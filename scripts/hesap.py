"""Süre ve dava takvimi hesaplayıcı: TBK 344, 345 ve 347 süre denetimleri.

Yerel, standart kütüphane dışında harici bağımlılık gerektirmeyen araç.
Tarih girdileri GG.AA.YYYY, YYYY-AA-GG veya GG/AA/YYYY; çıktı GG.AA.YYYY.
"""
from __future__ import annotations

import argparse
from datetime import date, timedelta
import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Tuple

_HERE = str(Path(__file__).resolve().parent)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from deadlines import add_months, calculate, parse_date  # noqa: E402  (parse_date yeniden dışa aktarılır)

HUAK_18B_YURURLUK = date(2023, 9, 1)
VARSAYILAN_ILK_SURE_AY = 12

REJIM_ILK_BES_YIL = "Artış rejimi ayrıca incelenmeli (ilk beş yıl)"
REJIM_DONGU = ("TBK 344/3 (Hak ve Nesafet inceleme adayı; başlangıca göre beş yıllık takvim döngüsü — "
               "arada 344/3 belirlemesi veya rayici yansıttığı tartışılan yeni sözleşme varsa döngü ondan itibaren ayrıca hesaplanır)")
REJIM_KOSULLU = ("TBK 344/3 koşullu aday: beşinci yıldan sonra henüz 344/3 belirlemesi yapılmamışsa bu yıl da istenebilir "
                 "(Yargıtay 3. HD, E. 2017/4515, K. 2018/11754); yapılmışsa son belirlemeden itibaren beş yıl dolana kadar TBK 344/1-2")


def format_date(d: date) -> str:
    """Tarihi GG.AA.YYYY biçiminde döner."""
    return d.strftime("%d.%m.%Y")


def format_iso(d: date) -> str:
    """Tarihi YYYY-MM-DD biçiminde döner."""
    return d.isoformat()


def add_years(d: date, years: int) -> date:
    """Tarihe belirtilen yıl kadar ekler, 29 Şubat durumunu güvenle yönetir."""
    return add_months(d, years * 12)


def sub_months(d: date, months: int) -> date:
    """Tarihten belirtilen ay kadar çıkarır, ay sonu sınırlarını korur."""
    return add_months(d, -months)


def get_lease_year(start_date: date, year_index: int) -> Tuple[date, date]:
    """Belirtilen kira yılının (1-indexed) başlangıç ve bitiş tarihlerini döner."""
    if year_index < 1:
        raise ValueError("Kira yılı 1 veya daha büyük olmalıdır")
    p_start = add_years(start_date, year_index - 1)
    p_end = add_years(start_date, year_index) - timedelta(days=1)
    return p_start, p_end


def classify_lease_year(year_index: int) -> Tuple[bool, bool, str]:
    """Kira yılı için (beş yıl doldu mu, beş yıllık döngü adayı mı, rejim metni) döner."""
    bes_yil_doldu = year_index >= 6
    dongu = bes_yil_doldu and (year_index - 6) % 5 == 0
    if not bes_yil_doldu:
        regime = REJIM_ILK_BES_YIL
    elif dongu:
        regime = REJIM_DONGU
    else:
        regime = REJIM_KOSULLU
    return bes_yil_doldu, dongu, regime


def compute_periods(start_date: date, count: int = 12) -> List[Dict[str, Any]]:
    """Başlangıçtan itibaren kira dönemleri çizelgesini oluşturur."""
    if not 1 <= count <= 120:
        raise ValueError("Dönem sayısı 1–120 arasında olmalı")
    periods = []
    for i in range(1, count + 1):
        p_start, p_end = get_lease_year(start_date, i)
        bes_yil_doldu, dongu, regime = classify_lease_year(i)
        periods.append({
            "kira_yili": i,
            "baslangic": format_date(p_start),
            "bitis": format_date(p_end),
            "baslangic_iso": format_iso(p_start),
            "bitis_iso": format_iso(p_end),
            "rejim": regime,
            "bes_yillik_dongu_adayi": dongu,
            "bes_yil_doldu_mu": bes_yil_doldu,
            "tbk344_3_kosullu_aday": bes_yil_doldu and not dongu,
            "hak_nesafet_yili": dongu,  # eski alan adı; yalnız takvim döngüsünü gösterir, uygulanabilirliği belirlemez
            "tbk347_uzama_yili": None,
            "status": "takvim_adayi_hukuki_kontrol_gerekli"
        })
    return periods


def _transitional_notes(target_start: date) -> List[str]:
    """Hedef dönem başlangıcına göre geçiş hükmü uyarılarını döner."""
    notes = []
    if date(2022, 6, 11) <= target_start <= date(2023, 7, 1):
        notes.append("Konut kirasıysa hedef dönem TBK geçici 1 kapsamında (11.06.2022–01.07.2023, son gün dahil) yenilenmiştir: "
                     "yüzde 25 sınırı veya daha düşükse TÜFE on iki aylık ortalama değişimi, 344/2 uyarınca verilecek hâkim "
                     "kararına da uygulanır; işyerine ve 344/3 rayiç tespitine otomatik uygulanmaz.")
    elif date(2023, 7, 2) <= target_start <= date(2024, 7, 1):
        notes.append("Konut kirasıysa hedef dönem TBK geçici 2 kapsamında (02.07.2023–01.07.2024, iki uç dahil) yenilenmiştir: "
                     "yüzde 25 sınırı veya daha düşükse TÜFE on iki aylık ortalama değişimi, 344/2 uyarınca verilecek hâkim "
                     "kararına da uygulanır; işyerine ve 344/3 rayiç tespitine otomatik uygulanmaz.")
    if date(2012, 7, 1) <= target_start <= date(2020, 7, 1):
        notes.append("Kiracı tacir veya özel/kamu hukuku tüzel kişisi olan işyeri kirasıysa 6217 s.K. geçici 2 (6353 değişikliği) "
                     "uyarınca TBK 344, 01.07.2012'den itibaren 8 yıl uygulanmamış olabilir (TBK 345 bu listede yoktur); "
                     "sözleşme hükümleri ve mülga 818 s. BK incelenir, 01.07.2020 sınır günü ayrıca değerlendirilir.")
    elif target_start < date(2012, 7, 1):
        notes.append("Hedef dönem 01.07.2012 öncesinde başlıyor; mülga 818 s. BK ve 6101 s. Yürürlük Kanunu geçiş hükümleri incelenir.")
    return notes


def compute_tespit(
    start_date: date,
    has_increase_clause: bool,
    notice_date: Optional[date] = None,
    action_date: Optional[date] = None,
    target_period_start: Optional[date] = None
) -> Dict[str, Any]:
    """TBK 344 ve 345 kapsamında kira tespiti süre ve hedef dönem analizini gerçekleştirir."""
    if target_period_start is None:
        raise ValueError("Hedef dönem açıkça belirtilmeli: --hedef-donem GG.AA.YYYY")
    target_year_idx = target_period_start.year - start_date.year + 1
    if target_year_idx < 1 or add_years(start_date, target_year_idx - 1) != target_period_start:
        raise ValueError("Hedef tarih kira yılı başlangıcıyla eşleşmiyor; sessizce sonraki döneme taşınmaz")
    if target_year_idx < 2:
        raise ValueError("Hedef dönem ilk kira yılı olamaz; TBK 345 yenilenen (en az 2.) kira dönemi için incelenir. "
                         "İlişki daha önce başladıysa --baslangic olarak ilk başlangıcı ver.")
    target_start, target_end = get_lease_year(start_date, target_year_idx)
    prev_start = add_years(start_date, target_year_idx - 2)
    prev_threshold = prev_start - timedelta(days=30)
    first = add_years(start_date, 5)
    deadline_notice = target_start - timedelta(days=30)

    notice_usable = notice_date is not None and prev_threshold < notice_date <= deadline_notice
    ihtar_suresinde = None if notice_date is None else notice_usable
    condition = None
    if action_date is not None:
        condition = prev_threshold < action_date <= target_end and (
            has_increase_clause or action_date <= deadline_notice or notice_usable)
    candidate = target_start if condition is True else None
    etki_son = target_end if (has_increase_clause or ihtar_suresinde) else deadline_notice
    arabuluculuk = (action_date >= HUAK_18B_YURURLUK) if action_date is not None else None
    bes_yil_doldu, rayic_cycle, regime = classify_lease_year(target_year_idx)

    notes = [
        "Yalnız tarih koşulu denetlenir; belge, sözleşme ve uygulanacak mevzuat ayrıca doğrulanır.",
        "Hedef dönem sonu genel dava açma son günü değildir; TBK 345 dönem etkisi bakımından incelenir.",
        "Tatil, arabuluculuk, önceki tespit ve yeni sözleşme etkileri hesaplanmadı.",
        "Dönem çizelgesi yıllık dönem varsayımıdır; mahkemenin hangi dönemden hüküm kuracağını belirlemez.",
    ]
    notes.extend(_transitional_notes(target_start))
    if notice_date is not None and notice_date <= prev_threshold:
        notes.append(f"İhtar tarihi {format_date(notice_date)}, önceki dönemin ({format_date(prev_start)}) 30 gün eşiğine "
                     f"({format_date(prev_threshold)}) kadar veya daha önce; önceki/eski bir dönem için yapılmış sayılabileceğinden "
                     "hedef dönem için TBK 345/2 bildirimi olarak hesaba katılmadı.")
    if action_date is not None and action_date <= prev_threshold:
        notes.append(f"Dava tarihi {format_date(action_date)}, önceki dönemin ({format_date(prev_start)}) 30 gün eşiğine "
                     f"({format_date(prev_threshold)}) kadar veya daha önce; dava önceki/eski bir dönemi etkileyeceğinden hedef "
                     "dönem tarih koşulu sağlanmış sayılmadı.")
    if action_date is not None and prev_threshold < action_date < target_start and (
            has_increase_clause or (notice_date is not None and notice_date <= prev_threshold)):
        notes.append(f"Dava hedef dönemden önce ({format_date(prev_start)} başlangıçlı önceki dönemin sonuna kadar) açılmış; artış "
                     "şartı veya önceki döneme süresinde yapılmış ihtar varsa dava TBK 345 uyarınca daha önceki bir dönemden "
                     "itibaren etki doğurabilir. Talep edilen dönemi dilekçeden doğrula.")
    if not has_increase_clause and not ihtar_suresinde:
        notes.append(f"Artış şartı ve süresinde yazılı bildirim yok/verilmedi: hükmün {format_date(target_start)} başlangıçlı "
                     f"dönemden etkili olması için dava en geç {format_date(deadline_notice)} tarihinde açılmış olmalı ya da bu "
                     "tarihe kadar yazılı artış bildirimi tebliğ edilmeli. Daha sonra açılan dava yine açılabilir; ancak hedef "
                     "döneme etki etmez, hangi dönemden etkili olacağı ayrıca incelenir.")
    if arabuluculuk is True:
        if has_increase_clause or ihtar_suresinde:
            route = "TBK 345/3 (artış şartı)" if has_increase_clause else "TBK 345/2 süresinde yazılı bildirim"
            notes.append("Dava tarihi 01.09.2023 veya sonrası: HUAK 18/B-1-a uyarınca arabulucuya başvurmuş olmak dava şartıdır "
                         f"(HUAK 18/B-2: üç hafta, zorunlu hâlde en fazla bir hafta uzatma). {route} yolunda son tutanak "
                         "düzenlenmiş ve dava hedef dönem sonuna kadar açılmış olmalıdır; araç arabuluculuk süresini hesaplamaz.")
        else:
            notes.append("Dava tarihi 01.09.2023 veya sonrası: HUAK 18/B-1-a uyarınca arabulucuya başvurmuş olmak dava şartıdır "
                         "(HUAK 18/B-2: üç hafta, zorunlu hâlde en fazla bir hafta uzatma). TBK 345/2'de ihtarsız yol için "
                         "arabuluculuk son tutanağı düzenlenmiş ve dava en geç " + format_date(deadline_notice) + " tarihinde "
                         "açılmış olmalıdır; arabuluculuk başvurusunun bu eşiği durdurduğu veya karşıladığı varsayılmaz. Daha "
                         "güvenli yol, artış bildiriminin bu tarihe kadar kiracıya yazılı olarak ulaşmasıdır; bu durumda "
                         "arabuluculuk tamamlanıp dava hedef dönem sonuna kadar açılabilir.")
    elif arabuluculuk is None:
        notes.append("Dava tarihi verilmedi: 01.09.2023 ve sonrasında açılacak kira tespiti davasında HUAK 18/B-1-a uyarınca "
                     "dava şartı arabuluculuk aranır; arabuluculuk süresini TBK 345 eşiğinden önce planla.")
    if condition is None:
        notes.append("Dava tarihi verilmedi; hedef döneme etki henüz doğrulanamaz.")
    elif condition:
        notes.append("Verilen tarihlerle hedef dönem için TBK 345 tarih koşulu aday olarak sağlanıyor.")
    else:
        notes.append("Verilen tarihler hedef döneme etkiyi desteklemiyor; sonraki dönem otomatik seçilmez, ayrıca araştırılır.")

    return {
        "status": "takvim_adayi_hukuki_kontrol_gerekli",
        "sozlesme_baslangic": format_date(start_date),
        "bes_yil_dolum_tarihi": format_date(first - timedelta(days=1)),
        "besinci_kira_yili_son_gunu": format_date(first - timedelta(days=1)),
        "bes_yil_yildonumu": format_date(first),
        "ilk_hak_nesafet_donemi": {
            "baslangic": format_date(first),
            "bitis": format_date(add_years(start_date, 6) - timedelta(days=1)), "kira_yili": 6},
        "hedef_donem": {
            "baslangic": format_date(target_start), "bitis": format_date(target_end),
            "kira_yili": target_year_idx, "hak_nesafet_uygulanabilir": None,
            "bes_yillik_dongu_adayi": rayic_cycle, "bes_yil_doldu_mu": bes_yil_doldu,
            "tbk344_3_kosullu_aday": bes_yil_doldu and not rayic_cycle,
            "rejim": "Hukuki inceleme gerekli; takvim döngüsü tek başına uygulanabilirliği belirlemez. " + regime},
        "sure_analizi": {
            "artis_sarti_var": has_increase_clause,
            "ihtar_tarihi": format_date(notice_date) if notice_date else None,
            "dava_tarihi": format_date(action_date) if action_date else None,
            "en_gec_ihtar_teblig_tarihi": format_date(deadline_notice),
            "onceki_donem_30_gun_esigi": format_date(prev_threshold),
            "ihtar_suresinde": ihtar_suresinde,
            "hedef_donem_ham_sonu": format_date(target_end),
            "hedef_doneme_etki_son_dava_adayi": format_date(etki_son),
            "etki_senaryolari": {
                "artis_sarti_veya_suresinde_yazili_bildirim_varsa": format_date(target_end),
                "artis_sarti_ve_suresinde_bildirim_yoksa": format_date(deadline_notice)},
            "uygulanan_kural": "TBK 345/3" if has_increase_clause else "TBK 345/2",
            "kararin_gecerlilik_tarihi": None,
            "aday_etki_tarihi": format_date(candidate) if candidate else None,
            "hedef_donem_tarih_kosulu": condition,
            "arabuluculuk_zorunlu": arabuluculuk},
        "alan_notu": ("hedef_doneme_etki_son_dava_adayi yalnız hükmün hedef dönem başlangıcından bağlayıcı olması için dava "
                      "tarihinin ham sınırıdır; TBK 345/1 uyarınca dava her zaman açılabilir, bu tarih hak düşürücü genel dava "
                      "son günü değildir. Tatil ve arabuluculuk düzeltmesi yapılmadı. bes_yil_dolum_tarihi eski alan adıdır ve "
                      "beşinci kira yılının son kullanım gününü gösterir; TBK 92/3 anlamında karşılık gelen gün bes_yil_yildonumu "
                      "alanındadır. arabuluculuk_zorunlu yalnız dava tarihi verildiğinde ve yalnız tarih ölçütüyle (01.09.2023) "
                      "doldurulur; arabuluculuk süresini veya durma etkisini hesaplamaz. Önceki dönemin 30 gün eşiğine "
                      "(onceki_donem_30_gun_esigi) kadar yapılan ihtar/dava hedef döneme sayılmaz."),
        "tespitler": notes,
    }


def compute_tahliye_10yil(
    start_date: date,
    initial_years: Optional[int] = None,
    initial_months: Optional[int] = None,
    first_end: Optional[date] = None,
) -> Dict[str, Any]:
    """TBK 347 uyarınca 10 yıllık uzama süresi sonunda fesih takvimini hesaplar.

    İlk süre tam yıl (initial_years), ay (initial_months) veya ilk sürenin bittiği yıldönümü
    sınırı (first_end) olarak verilir; hiçbiri verilmezse 12 ay varsayılır ve çıktıda uyarılır.
    """
    if sum(value is not None for value in (initial_years, initial_months, first_end)) > 1:
        raise ValueError("--sure-yil, --sure-ay ve --ilk-bitis birlikte verilemez")
    if initial_years is not None:
        if initial_years < 1:
            raise ValueError("İlk sözleşme süresi en az 1 yıl olmalıdır")
        initial_months = initial_years * 12
        source = "sure_yil"
    elif initial_months is not None:
        if initial_months < 1:
            raise ValueError("İlk sözleşme süresi en az 1 ay olmalıdır")
        source = "sure_ay"
    elif first_end is not None:
        if first_end <= start_date:
            raise ValueError("İlk sözleşme bitişi başlangıç tarihinden sonra olmalıdır")
        source = "ilk_bitis"
    else:
        initial_months = VARSAYILAN_ILK_SURE_AY
        source = "varsayilan_12_ay"

    if first_end is None:
        months = initial_months or VARSAYILAN_ILK_SURE_AY  # yukarıda en az 1 olduğu doğrulandı
        first_end = add_months(start_date, months)

        def boundary(years_after_first_end: int) -> date:
            # Ay/yıl işlemi başlangıçtan tek adımda yapılır; kırpılmış ara tarihten zincirleme ilerlenmez.
            return add_months(start_date, months + 12 * years_after_first_end)
    else:
        anchor = first_end
        # Girdi bitişi başlangıçtan tam ay sayısıyla elde ediliyorsa süreyi bilgi olarak göster; hesap yine girdiden yürür.
        month_diff = (first_end.year - start_date.year) * 12 + first_end.month - start_date.month
        if add_months(start_date, month_diff) == first_end:
            initial_months = month_diff

        def boundary(years_after_first_end: int) -> date:
            return add_months(anchor, 12 * years_after_first_end)

    whole_years = initial_months // 12 if initial_months is not None and initial_months % 12 == 0 else None
    calculation = calculate('tbk347', first_end)
    ten_year_end = boundary(10)
    target = boundary(11)
    notes: List[str] = []
    if source == "varsayilan_12_ay":
        notes.append("İlk sözleşme süresi verilmedi; 12 ay (1 yıl) varsayıldı. Sözleşmedeki ilk süreyi --sure-yil, --sure-ay "
                     "veya --ilk-bitis ile ver; çok yıllı sözleşmede bu varsayım tarihleri yıllarca erken gösterir.")
    if add_months(start_date, 6) >= first_end:
        notes.append("İlk süre altı ay veya daha kısa: taşınmaz niteliği gereği geçici kullanıma özgülenmişse TBK 339/1 c.2 "
                     "uyarınca konut ve çatılı işyeri hükümleri, dolayısıyla TBK 347 uygulanmaz; bu hesap ancak bu istisna "
                     "dışlandıktan sonra kullanılabilir.")

    def clamp_note(label: str, value: date, years_after_first_end: int) -> None:
        if source == "ilk_bitis":
            return
        chained = add_months(first_end, 12 * years_after_first_end)
        if chained != value:
            notes.append(f"Ay sonu kırpması (ör. 29 Şubat başlangıcı): {label} başlangıçtan tek adımda yıldönümü "
                         f"{format_date(value)}, kırpılmış ilk süre bitiminden ({format_date(first_end)}) zincirleme okumada "
                         f"{format_date(chained)} olur. İhtarı erken eşik olan "
                         f"{format_date(sub_months(chained - timedelta(days=1), 3))} tarihine kadar ulaştır (zincirleme okumada "
                         f"yıldönümü eşiği {format_date(sub_months(chained, 3))}); uygulanacak sınırı sözleşme ve belgelerle doğrula.")

    clamp_note("ilk hedef", target, 11)
    following = []
    for extra in range(1, 4):
        year_boundary = boundary(11 + extra)
        following.append({
            "uzama_yili": 11 + extra,
            "toplam_kira_yili": whole_years + 11 + extra if whole_years is not None else None,
            "donem_sonu": format_date(year_boundary),
            "en_gec_ihtar_tarihi": format_date(sub_months(year_boundary - timedelta(days=1), 3)),
            "yildonumu_ihtar_esigi": format_date(sub_months(year_boundary, 3)),
            "tahliye_dava_donemi": None})
        clamp_note(f"{11 + extra}. uzama yılı sonu", year_boundary, 11 + extra)

    # deadlines.py'nin kendi alan adlarına (uc_ay_once_*) dayanan uyarısı aşağıda bu çıktının alan adlarıyla verilir.
    notes.extend(check for check in calculation['pending_checks'] if not check.startswith('uc_ay_once_'))
    notes.extend([
        "Tarihler yıldönümü sınırlarıdır; bir önceki kullanım günüyle karıştırılmamalı (son kullanım günleri ayrı alanlarda verilir).",
        "İlk sözleşme süresi + 10 uzama yılı + izleyen 1 yıl esas alınır.",
        "en_gec_ihtar_teblig_tarihi temkinli okumadır (uzama yılı yıldönümünden bir önceki gün biter); yildonumu_ihtar_esigi "
        "kararlardaki 'yıldönümünden yıldönümüne' dönem anlatımına karşılık gelir. Daha önce tebliğ edilmiş bir ihtarı yalnız "
        "temkinli tarihe göre süresiz sayma.",
        "TBK 347 için otomatik bir aylık dava penceresi veya TBK 353 uzaması üretilmez.",
        "Dava yolu, arabuluculuk ve geçiş hükümleri somut dosyada incelenmelidir."])
    return {
        "status": calculation['status'],
        "sozlesme_baslangic": format_date(start_date),
        "ilk_sure_kaynagi": source,
        "ilk_sozlesme_suresi_ay": initial_months,
        "ilk_sozlesme_suresi_yil": whole_years,
        "ilk_sozlesme_bitis": format_date(first_end),
        "ilk_sozlesme_son_kullanim_gunu": format_date(first_end - timedelta(days=1)),
        "on_yillik_uzama_baslangic": format_date(first_end),
        "on_yillik_uzama_bitis": format_date(ten_year_end),
        "on_yillik_uzama_son_kullanim_gunu": format_date(ten_year_end - timedelta(days=1)),
        "toplam_yil": whole_years + 11 if whole_years is not None else None,
        "ilk_fesih_donem_sonu": format_date(target),
        "en_gec_ihtar_teblig_tarihi": format_date(sub_months(target - timedelta(days=1), 3)),
        "yildonumu_ihtar_esigi": format_date(sub_months(target, 3)),
        "tahliye_dava_acma_araligi": None,
        "izleyen_uzama_yillari": following,
        "tespitler": notes,
    }


def _row(label: str, value: str, width: int = 28) -> str:
    return f"{label:<{width}}: {value}"


def render_text_tespit(res: Dict[str, Any]) -> str:
    sa = res['sure_analizi']
    hd = res['hedef_donem']
    ilk = res['ilk_hak_nesafet_donemi']
    lines = ["=== KİRA TESPİTİ SÜRE VE HEDEF DÖNEM ANALİZİ (TBK 344 / 345) ==="]
    lines.append(_row("Sözleşme Başlangıcı", res['sozlesme_baslangic']))
    lines.append(_row("5. Kira Yılının Son Günü", res['besinci_kira_yili_son_gunu']))
    lines.append(_row("Beş Yıl Yıldönümü (TBK 92/3)", f"{res['bes_yil_yildonumu']} (6. kira yılı başlangıcı)"))
    lines.append(_row("İlk Hak ve Nesafet Dönemi", f"{ilk['baslangic']} - {ilk['bitis']} (6. Kira Yılı)"))
    lines.append("")
    lines.append(f"--- İncelenen Hedef Dönem: {hd['baslangic']} - {hd['bitis']} ({hd['kira_yili']}. Kira Yılı) ---")
    lines.append(_row("İncelenecek Hukuki Rejim", hd['rejim']))
    if hd['bes_yillik_dongu_adayi']:
        cycle = "Evet (yalnız takvim adayı)"
    elif hd['tbk344_3_kosullu_aday']:
        cycle = "Hayır; TBK 344/3 koşullu aday (önceki 344/3 belirlemesine bağlı)"
    else:
        cycle = "Hayır (ilk beş yıl)"
    lines.append(_row("5 Yıllık Döngü Adayı", cycle))
    if sa['artis_sarti_var']:
        lines.append(_row("Artış Şartı Durumu", "Var (TBK 345/3)"))
        lines.append(_row("TBK 345/2 30 Gün Eşiği",
                          f"{sa['en_gec_ihtar_teblig_tarihi']} (bilgi: 345/3'te ihtar şart değil; artış hükmü yeterli sayılmazsa 345/2 için)"))
    else:
        lines.append(_row("Artış Şartı Durumu", "Yok (TBK 345/2)"))
        lines.append(_row("30 Gün Eşiği (İhtar/Dava)",
                          f"{sa['en_gec_ihtar_teblig_tarihi']} (yazılı bildirimin kiracıya ulaşması veya davanın açılması için)"))
    lines.append(_row("Hedef Dönem Ham Sonu", f"{sa['hedef_donem_ham_sonu']} (dönem sonu; genel dava son günü değil)"))
    lines.append(_row("Hedef Döneme Etki İçin Dava",
                      f"en geç {sa['hedef_doneme_etki_son_dava_adayi']} (aday; artış şartı/süresinde bildirim varsa dönem sonu, "
                      "yoksa 30 gün önce eşiği — genel dava son günü değildir)"))
    if sa['ihtar_tarihi']:
        timely = "hedef dönem için süresinde" if sa['ihtar_suresinde'] else "hedef dönem için süresinde değil"
        lines.append(_row("Bildirilen İhtar Tarihi", f"{sa['ihtar_tarihi']} ({timely})"))
    if sa['dava_tarihi']:
        lines.append(_row("Bildirilen Dava Tarihi", sa['dava_tarihi']))
    arb = sa['arabuluculuk_zorunlu']
    lines.append(_row("Dava Şartı Arabuluculuk",
                      "Aranır (HUAK 18/B-1-a)" if arb is True else
                      "Aranmaz (dava 01.09.2023 öncesi)" if arb is False else
                      "Dava tarihi verilmedi; 01.09.2023 sonrası davalarda aranır"))
    kosul = sa['hedef_donem_tarih_kosulu']
    lines.append(_row("Hedef Dönem Tarih Koşulu",
                      "Dava tarihi verilmedi" if kosul is None else ("Sağlanıyor (aday)" if kosul else "Sağlanmıyor")))
    if sa['aday_etki_tarihi']:
        lines.append(_row("Aday Dönem Etkisi", f"{sa['aday_etki_tarihi']} (hukuki kontrol gerekli)"))
    lines.append("")
    lines.append("Hukuki Değerlendirmeler:")
    for note in res['tespitler']:
        lines.append(f"  • {note}")
    return "\n".join(lines)


def render_text_tahliye(res: Dict[str, Any]) -> str:
    source = res['ilk_sure_kaynagi']
    if source == "ilk_bitis":
        term = f"ilk bitiş girdisi {res['ilk_sozlesme_bitis']}"
        if res['ilk_sozlesme_suresi_ay'] is not None:
            term += f"; {res['ilk_sozlesme_suresi_ay']} ay"
    elif res['ilk_sozlesme_suresi_yil'] is not None:
        term = f"{res['ilk_sozlesme_suresi_yil']} Yıl Süreli"
        if source == "varsayilan_12_ay":
            term += " — ilk süre verilmedi, 12 ay varsayıldı"
    else:
        term = f"{res['ilk_sozlesme_suresi_ay']} Ay Süreli"
    lines = ["=== 10 YILLIK UZAMA SÜRESİ SONU TAHLİYE TAKVİMİ (TBK 347) ==="]
    lines.append(_row("Sözleşme Başlangıcı", f"{res['sozlesme_baslangic']} ({term})", 27))
    lines.append(_row("İlk Sözleşme Süresi Dolumu",
                      f"{res['ilk_sozlesme_bitis']} yıldönümü (son kullanım günü {res['ilk_sozlesme_son_kullanim_gunu']})", 27))
    lines.append(_row("10 Yıllık Uzama",
                      f"{res['on_yillik_uzama_baslangic']} başlar, {res['on_yillik_uzama_bitis']} yıldönümünde dolar "
                      f"(son kullanım günü {res['on_yillik_uzama_son_kullanim_gunu']})", 27))
    total = f" (Toplam {res['toplam_yil']}. yıl sonu)" if res['toplam_yil'] is not None else ""
    lines.append(_row("İlk Hedef Yıldönümü", f"{res['ilk_fesih_donem_sonu']} takvim adayı{total}", 27))
    lines.append(_row("En Geç İhtar Tebliğ Tarihi",
                      f"{res['en_gec_ihtar_teblig_tarihi']} (temkinli; yıldönümü okumasında eşik {res['yildonumu_ihtar_esigi']})", 27))
    lines.append("Dava penceresi otomatik hesaplanmadı; hukuki inceleme gerekli.")
    lines.append("")
    lines.append("Takip Eden Uzama Yılları:")
    for sub in res['izleyen_uzama_yillari']:
        total = f" (Toplam {sub['toplam_kira_yili']}. yıl)" if sub['toplam_kira_yili'] is not None else ""
        lines.append(f"  • {sub['uzama_yili']}. Uzama Yılı{total}: Dönem sonu {sub['donem_sonu']}, "
                     f"en geç ihtar {sub['en_gec_ihtar_tarihi']} (yıldönümü eşiği {sub['yildonumu_ihtar_esigi']})")
    lines.append("")
    lines.append("Hukuki Tespitler:")
    for note in res['tespitler']:
        lines.append(f"  • {note}")
    return "\n".join(lines)


def render_text_donemler(periods: List[Dict[str, Any]], start_str: str) -> str:
    lines = [f"=== KİRA DÖNEMLERİ ÇİZELGESİ (Başlangıç: {start_str}) ==="]
    lines.append(f"{'Kira Yılı':<10} {'Dönem Aralığı':<25} {'TBK 347 Durumu':<36} {'Rejim / Hak ve Nesafet'}")
    lines.append("-" * 104)
    status_347 = "İlk sözleşme süresi ayrıca gerekli"
    for p in periods:
        if p['bes_yillik_dongu_adayi']:
            label = "TBK 344/3 döngü adayı [A]"
        elif p['tbk344_3_kosullu_aday']:
            label = "TBK 344/3 koşullu aday [B]"
        else:
            label = "İlk beş yıl"
        lines.append(f"{p['kira_yili']:<10} {p['baslangic'] + ' - ' + p['bitis']:<25} {status_347:<36} {label}")
    lines.append("")
    lines.append("Rejim açıklamaları:")
    lines.append(f"  İlk beş yıl: {REJIM_ILK_BES_YIL}")
    if any(p['bes_yillik_dongu_adayi'] for p in periods):
        lines.append(f"  [A] {REJIM_DONGU}")
    if any(p['tbk344_3_kosullu_aday'] for p in periods):
        lines.append(f"  [B] {REJIM_KOSULLU}")
    lines.append("  Dönem bitiş tarihi son kullanım günüdür; TBK 92/3 anlamında karşılık gelen gün izleyen dönemin başlangıcıdır.")
    return "\n".join(lines)


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

    date_help = "(GG.AA.YYYY, YYYY-AA-GG veya GG/AA/YYYY)"
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    # Alt komut: tespit
    p_tespit = sub.add_parser("tespit", help="TBK 344/345 kira tespiti ve süre denetimi")
    p_tespit.add_argument("--baslangic", "-b", required=True, help=f"Kira ilişkisinin ilk başlangıç tarihi {date_help}")
    group = p_tespit.add_mutually_exclusive_group(required=True)
    group.add_argument("--artis-sarti", dest="artis_sarti", action="store_true", default=False,
                       help="Sözleşmede yeni dönem için artış şartı var (TBK 345/3)")
    group.add_argument("--artis-sarti-yok", dest="artis_sarti", action="store_false",
                       help="Sözleşmede artış şartı yok (TBK 345/2)")
    p_tespit.add_argument("--ihtar-tarihi", "-i",
                          help="İhtarnamenin kiracıya tebliğ (ulaşma) tarihi; keşide/postalama tarihi değil, "
                               "UETS'de ulaşmayı izleyen 5. gün (GG.AA.YYYY)")
    p_tespit.add_argument("--dava-tarihi", "-d", help=f"Açılmış veya planlanan dava tarihi {date_help}")
    p_tespit.add_argument("--hedef-donem", "-t", required=True,
                          help=f"Tespiti istenen kira döneminin başlangıcı; en az 2. kira yılı {date_help}")
    p_tespit.add_argument("--json", action="store_true", help="JSON formatında çıktı üret")

    # Alt komut: tahliye-10yil
    p_tahliye = sub.add_parser("tahliye-10yil", help="TBK 347 10 yıllık uzama süresi sonu tahliye takvimi")
    p_tahliye.add_argument("--baslangic", "-b", required=True, help=f"Kira sözleşmesi başlangıç tarihi {date_help}")
    term = p_tahliye.add_mutually_exclusive_group()
    term.add_argument("--sure-yil", "-s", type=int,
                      help="İlk sözleşme süresi (tam yıl). Hiçbiri verilmezse 12 ay esas alınır ve çıktıda uyarılır")
    term.add_argument("--sure-ay", type=int, help="İlk sözleşme süresi (ay), örn. 6, 11, 18, 30")
    term.add_argument("--ilk-bitis",
                      help="İlk sözleşme süresinin bittiği yıldönümü sınırı (GG.AA.YYYY); son kullanım günü değil, "
                           "onu izleyen gün: 01.01.2015–31.12.2015 sözleşmesi için 01.01.2016")
    p_tahliye.add_argument("--json", action="store_true", help="JSON formatında çıktı üret")

    # Alt komut: donemler
    p_donem = sub.add_parser("donemler", help="Kronolojik kira dönemleri ve hukuki rejim çizelgesi")
    p_donem.add_argument("--baslangic", "-b", required=True, help=f"Kira sözleşmesi başlangıç tarihi {date_help}")
    p_donem.add_argument("--yil", "-n", type=int, default=12, help="Gösterilecek kira yılı sayısı, 1–120 (varsayılan: 12)")
    p_donem.add_argument("--json", action="store_true", help="JSON formatında çıktı üret")

    args = parser.parse_args()

    try:
        start_d = parse_date(args.baslangic)

        if args.command == "tespit":
            notice_d = parse_date(args.ihtar_tarihi) if args.ihtar_tarihi else None
            action_d = parse_date(args.dava_tarihi) if args.dava_tarihi else None
            target_d = parse_date(args.hedef_donem) if args.hedef_donem else None
            res = compute_tespit(
                start_date=start_d,
                has_increase_clause=args.artis_sarti,
                notice_date=notice_d,
                action_date=action_d,
                target_period_start=target_d
            )
            if args.json:
                print(json.dumps(res, ensure_ascii=False, indent=2))
            else:
                print(render_text_tespit(res))

        elif args.command == "tahliye-10yil":
            res = compute_tahliye_10yil(
                start_d,
                initial_years=args.sure_yil,
                initial_months=args.sure_ay,
                first_end=parse_date(args.ilk_bitis) if args.ilk_bitis else None)
            if args.json:
                print(json.dumps(res, ensure_ascii=False, indent=2))
            else:
                print(render_text_tahliye(res))

        elif args.command == "donemler":
            periods = compute_periods(start_d, count=args.yil)
            if args.json:
                print(json.dumps({
                    "baslangic": format_date(start_d),
                    "yil_sayisi": args.yil,
                    "donemler": periods
                }, ensure_ascii=False, indent=2))
            else:
                print(render_text_donemler(periods, format_date(start_d)))

    except (ValueError, OSError, OverflowError) as exc:
        print(f"HATA: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
