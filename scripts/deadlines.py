"""Kira hukuku süreleri için ham takvim adayı üretir; otomatik hukuki son gün görüşü değildir.

Yalnız standart kütüphane kullanır. Girdi tarihleri YYYY-AA-GG, GG.AA.YYYY veya GG/AA/YYYY; çıktı YYYY-AA-GG.
"""
import argparse
from calendar import monthrange
from datetime import date, datetime, timedelta
import json
import sys

TBK = 'https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6098&MevzuatTur=1&MevzuatTertip=5'
TEBLIGAT = 'https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=7201&MevzuatTur=1&MevzuatTertip=3'
IIK = 'https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=2004&MevzuatTur=1&MevzuatTertip=3'
DATE_FORMATS = ('%Y-%m-%d', '%d.%m.%Y', '%d/%m/%Y')
RULES = ['takvim', 'tbk344', 'tbk345', 'tbk315', 'tbk316', 'tbk350', 'tbk351', 'tbk352', 'tbk347', 'iik269', 'uets']


def parse_date(value):
    """YYYY-AA-GG, GG.AA.YYYY veya GG/AA/YYYY biçimindeki tarihi date nesnesine çevirir."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError('Tarih boş olamaz')
    cleaned = value.strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"Geçersiz tarih: '{value}'. Desteklenenler: YYYY-AA-GG, GG.AA.YYYY veya GG/AA/YYYY")


def _arg_date(value):
    try:
        return parse_date(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from None


def add_months(start, months):
    index = start.year * 12 + start.month - 1 + months
    year, month = divmod(index, 12)
    month += 1
    return date(year, month, min(start.day, monthrange(year, month)[1]))


def calculate(rule, start, *, count=None, unit=None, backward=False):
    dates = {}
    checks = [
        'Başlangıç olayı, belge ve uygulanacak tarihli mevzuat doğrulanmalı.',
        'Tatil/adli tatil, durma, uzama ve özel sözleşme koşulları uygulanmadı.',
    ]
    source = TBK
    if rule == 'takvim':
        if count is None or count < 1 or unit not in ('gun', 'hafta', 'ay', 'yil'):
            raise ValueError('takvim için pozitif --count ve --unit gerekir')
        sign = -1 if backward else 1
        if unit in ('gun', 'hafta'):
            result = start + timedelta(days=sign * count * (7 if unit == 'hafta' else 1))
        else:
            result = add_months(start, sign * count * (12 if unit == 'yil' else 1))
        dates['ham_geri_esik' if backward else 'ham_bitis'] = result
        basis = 'TBK 92 / HMK 92: hangi rejimin uygulanacağı ayrıca seçilir'
        if backward:
            meaning = ('Geri sayım: girdi hedef tarihtir (dönem/süre bitimi). Çıktı “en az … önce” bildirimin '
                       'en geç ulaşması gereken ham eşiktir; ay/yıl hesabında karşılık gelen gün, yoksa ayın son günü alınır. '
                       'Girdi bir dönem/süre bitimi olarak yıldönümü ise (ör. TBK 347 kiracı veya kiraya veren bildirimi), '
                       'son kullanım gününden de geri say ve erken çıkan tarihi esas al; girdi yeni dönem başlangıcıysa '
                       '(TBK 345/2 otuz gün eşiği) bu ek hesap yapılmaz.')
            checks.append('Geri sayılan eşiği tatil nedeniyle ileri taşıma; bildirimin bu tarihe kadar karşı tarafa '
                          'ulaşmasını ve hedef tarihin belgeden doğru seçildiğini doğrula.')
        else:
            meaning = 'Gün hesabında olay günü sayılmaz; ay/yıl hesabı karşılık gelen gündür.'
    else:
        if count is not None or unit is not None or backward:
            raise ValueError('--count/--unit/--geri yalnız takvim kuralında kullanılabilir')
        if rule == 'tbk344':
            dates['bes_yil_sonraki_yildonumu'] = add_months(start, 60)
            basis = 'TBK 344/3'
            meaning = 'Başlangıçtan beş yıl sonrası aday dönem sınırı; bedelin etkisi TBK 345 ile ayrıca incelenir.'
            checks.append('Yeni sözleşme, önceki tespit ve kira dönemi; yıldönümü tek başına hak veya hüküm oluşturmaz.')
        elif rule == 'tbk345':
            dates['otuz_gun_once_esigi'] = start - timedelta(days=30)
            basis = 'TBK 345/2–3'
            meaning = 'Girdi hedef dönem başlangıcıdır. Çıktı dava veya yazılı artış bildirimi için 30 gün önce eşiğidir; genel dava açma son günü değildir.'
            checks.append('Artış hükmü, bildirimin ulaşması ve hedef dönemin sonuna kadar dava koşulunu ayrı incele; geri sayılan eşiği tatil diye ileri taşıma.')
            checks.append('30 gün önce eşiği bildirimin kiracıya ulaşması (tebliği) içindir; keşide/postalama tarihi yetmez. '
                          'UETS ile tebliğde bildirim, UETS adresine ulaşmayı izleyen beşinci günün sonunda tebliğ edilmiş sayılır; '
                          "UETS'ye ulaşma en geç eşikten beş gün önce olmalıdır.")
        elif rule == 'tbk315':
            dates['otuzuncu_gun'] = start + timedelta(days=30)
            basis = 'TBK 315: yalnız konut ve çatılı işyeri, asgari 30 günlük süre'
            meaning = ('Girdi, yazılı bildirimin kiracıya ulaştığı (tebliğ edildiği) tarihtir; ihtarnamenin düzenleme/keşide '
                       'veya postaya verilme tarihi değildir. Elektronik tebligatta önce `uets` kuralıyla tebliğ edilmiş '
                       'sayılma gününü bul ve onu girdi yap. Ertesi gün birinci gündür; çıktı sürenin ham son günüdür, '
                       'tahliye tarihi değildir.')
            checks.append('İhtarda daha uzun süre varsa onu esas al; diğer kiralar veya İİK takipleri için bu ön ayarı kullanma. '
                          '13 örnek ödeme emri için iik269, TBK 316/2 giderim ihtarı için tbk316 kuralını kullan.')
        elif rule == 'tbk316':
            dates['otuzuncu_gun'] = start + timedelta(days=30)
            basis = 'TBK 316/2: yalnız konut ve çatılı işyeri, aykırılığın giderilmesi için asgari 30 günlük süre'
            meaning = ('Girdi, aykırılığın giderilmesini ve aksi hâlde sözleşmenin feshedileceğini bildiren yazılı ihtarın '
                       'kiracıya ulaştığı (tebliğ edildiği) tarihtir; ihtarnamenin düzenleme/keşide veya postaya verilme '
                       'tarihi, aykırılığın başladığı ya da öğrenildiği tarih değildir. Elektronik tebligatta önce `uets` '
                       "kuralıyla tebliğ edilmiş sayılma gününü bul ve onu girdi yap. TBK 316/2, TBK 315/2'deki “izleyen "
                       "günden” cümlesini içermez; aynı sonuç TBK 92/1'den çıkar: ertesi gün birinci gündür. Çıktı giderim "
                       'süresinin ham son günüdür; fesih, arabuluculuk, dava veya tahliye tarihi değildir.')
            checks.append('İhtarda daha uzun süre varsa onu esas al. İhtar aykırılığı, istenen giderimi ve süre içinde '
                          'giderilmezse sözleşmenin feshedileceğini açıkça içermeli; 30 günden kısa süre veren ihtarın yasal '
                          'süre sonunda sonuç doğuracağını varsayma.')
            checks.append('Diğer kiralarda (TBK 316/2 son cümle) ve TBK 316/3 hâllerinde süre verilmeden yazılı bildirimle '
                          'hemen fesih söz konusudur; bu ön ayarı kullanma. Kira bedeli/yan gider temerrüdü için tbk315 '
                          'kuralını kullan; bu sebebe İİK 269 ilamsız tahliye yolu uygulanmaz.')
            checks.append('Son gün tatile rastlarsa TBK 93 etkisini (aksine anlaşma dahil) ayrıca incele. Ayrı yazılı fesih '
                          'bildirimini (zorunluluğu açık soru, ihtiyatlıdır) ve dava şartı arabuluculuk başvurusunu '
                          '(HUAK 18/B; dava 01.09.2023 ve sonrası) süre, aykırılık giderilmeden dolduktan sonra yap; çıktıya '
                          'otomatik +1 gün ekleme. Kanunda dava açma süresi yoktur.')
            checks.append('30 gün tebliğden işler; keşide/postalama tarihi yetmez. UETS ile tebliğde bildirim, UETS adresine '
                          'ulaşmayı izleyen beşinci günün sonunda tebliğ edilmiş sayılır. Aile konutunda eş TBK 349/3 ile '
                          'taraf olmuşsa fesih bildirimini ona da ayrıca yap; giderim ihtarını da ihtiyaten ayrıca tebliğ et.')
        elif rule == 'tbk350':
            dates['bir_aylik_dava_ham_sonu'] = add_months(start, 1)
            basis = 'TBK 350: ihtiyaç veya yeniden inşa/imar nedeniyle tahliye'
            meaning = ('Girdi belirli süreli sözleşmede sürenin sonudur: ilk sözleşme süresinin veya sözleşme TBK 347/1 ile '
                       'uzamışsa içinde bulunulan uzama yılının bitimi (bir dönemde dava açılmaması hakkı düşürmez; izleyen '
                       'uzama yılının bitimi yeni girdidir). Belirsiz süreli sözleşmede girdi, genel hükümlere göre fesih '
                       'dönemi ve bildirim süresine uyularak belirlenen tarihtir. İhtar, arabuluculuk veya ilk kira '
                       'başlangıcı girdi değildir. Çıktı bir aylık dava süresinin ham sonudur. Bir ay 30 güne çevrilmez.')
            checks.append('Zorunlu arabuluculuk başvurusu dava hakkı doğduktan sonra yapılmalıdır (Yargıtay 3. HD 2025/1495 E., '
                          '2025/3048 K.); erken başvuru dava şartını sağlamış sayılmaz. Başvurudan son tutanağa kadarki '
                          'durma (HUAK 18/A/15) uygulanmadı.')
            checks.append('Girdi gününün kendisinde başvuru veya dava açılabilirliği ve sürenin sona erdiği an ayrıca '
                          'doğrulanır; otomatik ±1 gün uygulanmaz.')
            checks.append('En geç dava açma süresinin son gününe kadar kiracıya ulaşmış (daha önce, örneğin kira süresi '
                          'içinde de yapılabilen) yazılı TBK 353 bildirimi varsa dava süresinin bir kira yılı uzaması '
                          "hesaplanmadı. Yeni malik için tbk351 kuralını kullan; TBK 350 kararını 351/1'e otomatik taşıma.")
        elif rule == 'tbk351':
            dates['bir_aylik_bildirim_ham_sonu'] = add_months(start, 1)
            dates['alti_ayin_ham_dolum_tarihi'] = add_months(start, 6)
            dates['temkinli_en_erken_arabuluculuk_ve_dava_gunu'] = add_months(start, 6) + timedelta(days=1)
            basis = 'TBK 351/1'
            meaning = ('Girdi edinme tarihidir: satışta kural olarak tapu sicilindeki tescil tarihi; TMK 705/2 hallerinde '
                       '(ör. cebri icra, mahkeme kararı) mülkiyetin tescilden önce geçtiği tarih ayrıca belirlenir. '
                       'Bir ay bildirim penceresidir; altı ay bekleme süresidir, dava açma son günü değildir. '
                       'Altı ay, TBK 92 uyarınca karşılık gelen günün sonunda dolar; o gün yapılan başvuru/dava erken '
                       'sayılabilir. Temkinli en erken gün bu nedenle ertesi gündür. '
                       'Edinme gününü süreye dahil eden kararlar da bulunduğundan bildirimi ham sondan önce ulaştır.')
            checks.append('İhtiyaç, yazılı bildirimin süresinde ulaşması ve altı ayın dolması doğrulanmalı; TBK 351/2 dönem sonu yolu ayrı değerlendirilir.')
            checks.append('Dava şartı arabuluculuk başvurusunu da temkinli en erken günden önce yapma: TBK 350 için Yargıtay '
                          '3. HD 2025/1495 E., 2025/3048 K. başvuruyu dava açma hakkı doğduktan sonra arar; TBK 351/1 '
                          'yönünden 2025/3292 E., 2025/5039 K. uyuşmazlığı esastan çözmemiştir.')
        elif rule == 'tbk352':
            dates['bir_aylik_basvuru_ham_sonu'] = add_months(start, 1)
            basis = 'TBK 352/1: tahliye taahhüdü'
            meaning = 'Girdi taahhüt edilen boşaltma tarihidir; imza tarihi değildir. Bir ay 30 güne çevrilmez.'
            checks.append('Taahhüt geçerliliği, dava/icra yolu, arabuluculuk ve TBK 353 etkisi ayrıca incelenmeli; iki haklı ihtar için bu başlangıcı kullanma.')
            checks.append('TBK 352/1 “icraya başvurmak veya dava açmak” der: aynı ham sonuç İİK 272 ilamsız tahliye takibi '
                          '(14 örnek) için de kullanılır, ayrı kural yoktur. Tahliye emrine itiraz (7 gün) ve boşaltma '
                          '(15 gün) süreleri tahliye emrinin tebliğinden işler; bunları takvim kuralıyla ayrı hesapla. '
                          'İİK 272 vd. metni resmî metinden doğrulanmadı.')
            checks.append('Son gün tatile rastlarsa dava yolunda TBK 93, takip yolunda İİK 19 (resmî metinden doğrula) '
                          'etkisini ayrıca incele; araç tatil düzeltmesi yapmaz, başvuruyu son güne bırakma.')
        elif rule == 'tbk347':
            dates['on_yillik_uzama_ham_sonu'] = add_months(start, 120)
            target = add_months(start, 132)
            dates['izleyen_ilk_uzama_yili_ham_sonu'] = target
            dates['uc_ay_once_bildirim_esigi'] = add_months(target, -3)
            dates['uc_ay_once_temkinli_esik'] = add_months(target - timedelta(days=1), -3)
            basis = 'TBK 347/1: belirli süreli konut/çatılı işyeri'
            meaning = 'Girdi ilk sözleşme süresinin hukuken belirlenmiş bitimidir; ilk kira başlangıcı değildir. İlk hedef = ilk süre bitimi + 10 uzama yılı + 1 izleyen yıl.'
            checks.append('Geçiş hükümleri, yeni sözleşmeler, süre/bitiş gününün yorumu ve yazılı bildirimin ulaşması incelenmeli; belirsiz süreliye uygulanmaz.')
            checks.append('uc_ay_once_bildirim_esigi yıldönümü okumasıdır; uzama yılının son günü yıldönümünden bir önceki gün '
                          'sayılırsa eşik uc_ay_once_temkinli_esik olur. Tebliği temkinli eşikte veya daha önce sağla; iki tarih '
                          'arasındaki tebliğin süresinde olup olmadığı yoruma açıktır.')
            checks.append('Üç ay önce bildirim eşiği tebliğ içindir; UETS ile tebliğde ulaşmayı izleyen beşinci günün sonu '
                          "tebliğ günüdür, bu nedenle UETS'ye ulaşma en geç eşikten beş gün önce olmalıdır.")
        elif rule == 'iik269':
            payment_end = start + timedelta(days=30)
            dates['itiraz_suresi_ham_sonu'] = start + timedelta(days=7)
            dates['odeme_suresi_ham_sonu'] = payment_end
            dates['en_erken_tahliye_talebi_ham_gunu'] = payment_end + timedelta(days=1)
            dates['tahliye_talebi_alti_ay_ham_sonu'] = add_months(payment_end, 6)
            basis = ('İİK 269 ve 269/a (13 örnek ödeme emri; resmî metinden doğrula) ile TBK 315/2: yalnız konut ve '
                     'çatılı işyeri, 30 günlük ödeme süresi')
            source = IIK
            meaning = ('Girdi, tahliye ihtarlı (13 örnek) ödeme emrinin kiracıya tebliğ edildiği tarihtir (T); takip talebi, '
                       'ödeme emrinin düzenlenmesi, noter ihtarnamesinin tebliği veya kiranın vade günü değildir. Elektronik '
                       'tebligatta önce `uets` kuralıyla tebliğ edilmiş sayılma gününü bul ve onu girdi yap. Ertesi gün '
                       'birinci gündür. Çıktı yalnız konut ve çatılı işyeri içindir: itiraz süresinin ham sonu G(T,7); ödeme '
                       '(ihtar) süresinin ham sonu O = G(T,30); itiraz edilmemiş ve süresinde ödenmemişse en erken tahliye '
                       'talebi G(O,1) ve altı aylık talep süresinin ham sonu A(O,6). Altı ay O\'dan sayılır; tebliğden veya '
                       'itiraz süresinin bitiminden sayılmaz. Yedi günün geçmesi ödeme süresini kısaltmaz. Hiçbiri tahliye '
                       'tarihi değildir; tahliyeye icra mahkemesi karar verir.')
            checks.append('Yalnız konut ve çatılı işyerindeki 30 günlük ödeme süresi için ön ayardır. Diğer kiralarda 10 gün '
                          '(TBK 315/2), ürün kirasında 60 gün (TBK 362/2) veya ödeme emrinde daha uzun süre yazılıysa O '
                          'değerini takvim <T> --count <n> --unit gun ile, altı ayı takvim <O> --count 6 --unit ay ile '
                          'ayrı hesapla; bu kuralın tarihlerini kullanma.')
            checks.append('İİK metni resmî kaynaktan doğrulanmadı: yedi günlük itiraz süresi Yargıtay 12. HD 2025/7021 E., '
                          '2025/5902 K. çoğunluk gerekçesinde, 269/a altı ay kuralı aynı kararın karşıoy yazısında ve '
                          'Yargıtay HGK 2017/1918 E., 2021/1707 K. ile HGK 2017/2340 E., 2021/261 K. gerekçelerinde '
                          'aktarılmıştır. Takip tarihindeki İİK 269–269/a metnini resmî metinden doğrula.')
            checks.append('Ödeme süresi dolmadan icra mahkemesinden tahliye istenemez (HGK 2017/2340 E., 2021/261 K.). '
                          '“Bitim tarihini takip eden altı ay” ifadesi bir günlük okuma farkı doğurabilir; talebi ham sondan '
                          'önce yap. Altı ay talep içindir; kaçırılırsa bu takibe dayalı ilamsız tahliye istenemez, dava '
                          'yolunu (HUAK 18/B dava şartı arabuluculuk dahil) ayrıca incele.')
            checks.append('Kural yalnız ödeme emrine süresinde itiraz edilmeyen hâli kapsar. İtiraz varsa itirazın kaldırılması '
                          've tahliye (İİK 269/b–269/c; itirazın alacaklıya tebliğinden altı ay görüşü ikincil kaynaklıdır) '
                          'ayrı başlangıç olayına bağlıdır; bu tarihleri o yol için kullanma.')
            checks.append('Son gün tatile rastlarsa İİK 19 (resmî metinden doğrula) etkisini ayrıca incele; araç tatil '
                          'düzeltmesi yapmaz. O tatil nedeniyle uzarsa en erken talep günü de ileri kayar; altı ayı ham O\'dan '
                          'say ve erken planla. İcra işlerinde HMK adli tatil uzatmasını uygulama (rehber; resmî metinden '
                          'doğrula). İlamsız tahliye takibi HUAK 18/B istisnasındadır; arabuluculuk düzeltmesi yoktur.')
            checks.append('T ödeme emrinin usulüne uygun tebliğidir; UETS ile tebliğde ulaşmayı izleyen beşinci günün sonu '
                          'tebliğ günüdür. Tebliğ yapılmamış veya usulsüzse sürelerin başlangıcını ayrıca incele. Kiracı '
                          'olmayan eş TBK 349/3 ile taraf olmuşsa ödeme süresi ona da ayrı bildirilir; farklı tebliğ '
                          'tarihlerinde hangisinin esas alınacağı açık sorudur; temkinli olarak geç tebliğden hesapla.')
        elif rule == 'uets':
            dates['teblig_edilmis_sayilma_gunu'] = start + timedelta(days=5)
            basis = '7201 sayılı Kanun 7/a/4'
            source = TEBLIGAT
            meaning = 'Girdi UETS adresine ulaşma günüdür; izleyen beşinci günün sonunda tebliğ edilmiş sayılır. SMS/e-posta veya okuma tarihi değildir.'
            checks = ['UETS delil kaydını doğrula; beşinci günü iş gününe taşıma.',
                      'Bundan sonraki başvuru süresini ayrı hesapla; onun tatil ve diğer etkilerini ayrıca incele.']
        else:
            raise ValueError(f'Bilinmeyen kural: {rule}')
    return {
        'rule': rule, 'input_date': start.isoformat(), 'basis': basis,
        'source_url': source, 'status': 'takvim_adayi_hukuki_kontrol_gerekli',
        'raw_dates': {key: value.isoformat() for key, value in dates.items()},
        'meaning': meaning, 'pending_checks': checks,
        'holiday_adjustment_applied': False,
        'mediation_adjustment_applied': False,
    }


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('rule', choices=RULES, help='Süre kuralı; girdinin ve çıktının anlamı meaning alanında yazılıdır')
    parser.add_argument('date', type=_arg_date,
                        help='YYYY-AA-GG, GG.AA.YYYY veya GG/AA/YYYY; girdinin anlamı kurala göre değişir')
    parser.add_argument('--count', type=int, help='takvim: süre miktarı (pozitif tam sayı)')
    parser.add_argument('--unit', choices=['gun', 'hafta', 'ay', 'yil'], help='takvim: süre birimi')
    parser.add_argument('--geri', action='store_true',
                        help='takvim: hedef tarihten geriye say (en az … önce bildirim eşiği)')
    args = parser.parse_args()
    try:
        result = calculate(args.rule, args.date, count=args.count, unit=args.unit, backward=args.geri)
    except (ValueError, OverflowError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
