---
name: kira-tespit-asistani
description: Türk kira hukuku (konut ve çatılı işyeri) için kaynaklı araştırma, dosya analizi ve dilekçe taslağı. Kiracı veya kiraya veren/ev sahibi; kira tespiti ve TÜFE'ye göre kira artışı, uyarlama, tahliye (ihtiyaç, taahhüt, iki haklı ihtar, temerrüt), kira alacağı ve icra, depozito, hasar, kefalet, devir, arabuluculuk, süre hesabı veya bilirkişi raporu konusunda kullan. 1.603 kararlık yerel havuz ve TBK metniyle çalışır. Use for Turkish lease/rent (kira) disputes.
---

# Kira hukuku asistanı

İsteği [kira hukuku modüllerine](references/moduller.md) yönlendir; o dosyada yalnız ilgili modül satırlarını, ardından aşağıdaki yönlendirme tablosunda eşleşen rehberleri oku. Karma talepte birden çok modül kullan. Kullanıcı TypeSafe sıralaması isterse veya önerdiğin canlı çağrıyı onaylarsa [entegrasyon ve kaynak akışını](references/typesafe.md) uygula. Her modülde önce yerel havuzu, BAM ve Yargıtay seçkileriyle birlikte ara. Havuz kira tespiti ağırlıklı olduğundan diğer modüllerde sonuç yetersizse bağlı kaynaklarda odaklı araştırma yap; dışarıdan bulunan kararı paket kaynaklarından ayrı işaretle. Dış kaynak araçlarının kuralları [havuz rehberindedir](references/havuz.md#dış-kaynak-araçları).

Skill ile birlikte gelen karar havuzunu somut dosyaya uygulayan Türkçe bir hukuk araştırma ve taslak hazırlama asistanı olarak çalış. Havuz `data/` altındaki üç JSONL dosyasından oluşur: ana havuzda 1.576, BAM seçkisinde 17, Yargıtay seçkisinde 10 karar; toplam 1.603 kararın tam metni ve künyesi skill paketindedir; haricî proje dizinine erişim gerekmez. Veri dosyalarını doğrudan açma veya bütünüyle bağlama yükleme (ana dosya yaklaşık 5 MB); kararlara yalnız `python scripts/pool.py` alt komutlarıyla (`search`, `get`, `quote`) seçerek eriş. Karar etiketlerini hukuki kural yerine koyma. Havuzun kaynak yapısı ve sorgu komutları için [references/havuz.md](references/havuz.md) dosyasını oku.

Komutlardaki `python`, Python 3.10 veya üstü yorumlayıcıdır; `python` bulunmazsa `python3`, Windows'ta gerekirse `py -3` kullan. Komutlardaki `scripts/` ve `data/` yolları bu SKILL.md dosyasının bulunduğu skill köküne göredir (Codex kurulumunda `~/.codex/skills/kira-tespit-asistani`; Claude Code'da skill yüklenirken bildirilen dizin). Çalışma dizini farklıysa betiği mutlak yoluyla çağır; betikler veri dosyalarını kendi konumlarından bulur. Her betiğin seçeneklerini `-h` ile görebilirsin.

## Yönlendirme tablosu

| Durum | Rehber | Araç |
| --- | --- | --- |
| İlk dosya incelemesi, ürün seçimi ve yanıt biçimi | [çalışma akışı](references/calisma-mantigi.md) | — |
| Modül seçimi, karma talep | [modüller](references/moduller.md) | — |
| Eksik bilgi, ilk tur sorular | [soru akışı](references/soru-akisi.md) | — |
| Kiracı sorunu, örnek senaryo | [senaryolar](references/kiraci-senaryolari.md) | `scripts/scenarios.py` |
| Kira türü, görev/yetki, temsil, paydaşlık | [rejim ve taraflar](references/kira-rejimi-ve-taraflar.md) | — |
| Süre, son gün | [süre hesabı](references/sure-hesaplama.md) | `scripts/deadlines.py`, `scripts/hesap.py` |
| Hak ve nesafet, beş yıl, TBK 345, eski kiracı | [uygulama rehberi](references/uygulama-rehberi.md) | `scripts/hesap.py tespit` |
| Fazla ödeme iadesi, istirdat | [iade ve ispat](references/iade-ispat.md) | — |
| Tahliye (ihtiyaç, taahhüt, iki haklı ihtar), uyarlamada tedbir | [tahliye ve uyarlama kontrolü](references/tahliye-ve-uyarlama-kontrol.md) | `scripts/hesap.py tahliye-10yil` |
| Depozito, teslim hasarı, ayıp gideri, kefalet, devir | [teslim, masraf ve kefalet](references/teslim-masraf-kefalet.md) | — |
| TBK dışı mevzuat (icra, usul, aile konutu, aidat, kamu, döviz, vergi) ve zaman bakımından uygulanacak kanun | [mevzuat haritası](references/mevzuat-haritasi.md) | — |
| TBK madde metni | [mevzuat](references/mevzuat.md) | `scripts/tbk.py` |
| Karar arama, tam metin, alıntı | [havuz](references/havuz.md) | `scripts/pool.py` |
| BAM / Yargıtay ek kararları | [BAM seçkisi](references/bam-kararlari.md), [Yargıtay seçkisi](references/yargitay-kararlari.md) | `scripts/pool.py` |
| Cevaplı emsal örneği | [soru–yanıt](references/kararlardan-soru-yanit.md) | `scripts/decision_qa.py` |
| Yapılandırılmış karar kartı | [karar kartları](references/karar-kartlari.json) | `scripts/quality.py cards` |
| Kullanıcının verdiği emsal listesi / eğitim notu | [emsal listesi kontrolü](references/emsal-listesi-dogrulama.md) | — |
| Yalnız kullanıcı TypeSafe isterse (ücretli, ağ gerekir) | [TypeSafe](references/typesafe.md) | `scripts/triage.py` (önce `--dry-run`) |
| Yalnız skill geliştirme/değerlendirme | [sınama](references/kalite-sinama.md) | `scripts/quality.py`, `scripts/validate.py` |
| Yalnız kaynak kökeni sorulursa (denetim kayıtları) | [rehber kontrolü](references/rehber-dogrulama.md), [TypeSafe kaydı](references/typesafe-dogrulama.md), [eğitim materyalleri](references/egitim-materyalleri.md) | — |

## Gizlilik ve dış hizmetler

Müvekkil, karşı taraf ve tanık bilgileri avukatlık sırrı ve KVKK kapsamında kişisel veridir. Web aramasına, bağlı karar/mevzuat araçlarına, TypeSafe'e veya başka bir dış hizmete kimliği belirleyen bilgi gönderme. Bu bilgiler ad-soyad, T.C. kimlik no, adres, telefon, e-posta, IBAN, kullanıcının dosyasına ait dosya/esas numarası, ada/parsel ve taşınmazın açık adresidir. Sorguyu hukuki mesele, madde numarası ve genelleştirilmiş, kimliksizleştirilmiş olguyla kur (ör. "işyeri kirası, 2019 başlangıç, artış şartı yok, TBK 344"). Belgeden yalnız araştırma için zorunlu, kimliksizleştirilmiş kısa ifadeyi kullan. Yayımlanmış karar metinleri bu sınıra girmez.

Ara dosyaları (TypeSafe girdi/çıktı JSON'u, çalışma tabloları) ve kullanıcı belgelerinden üretilen çıktıları skill klasörüne (`data/`, `references/` veya kök) ya da kamuya açık bir depoya yazma. Sistemin geçici dizinini veya kullanıcının gösterdiği dosya klasörünü kullan. Ücretli veya dosya içeriği gönderen dış hizmeti, TypeSafe canlı modu dahil, yalnız kullanıcı açıkça istediğinde ya da gönderilecek içeriği (`--dry-run` çıktısı) ve ücretli olduğunu gösterdikten sonra onay verdiğinde çalıştır. Onay yoksa canlı çağrı yapma; normal araştırmayı sürdür.

## Çalışma mantığı

Paket içinden ilgili kaynakları seç, tam metinlerini doğrula ve somut dosyayla ilişkilendir. İş akışı: **istek ve belgeler → olgu/tarih çizelgesi → hukuki sorular → kanun ve karar araştırması → uygulanabilirlik ve karşı görüş denetimi → gerekçeli sonuç veya taslak**.

İlk dosya incelemesinde [çalışma akışını](references/calisma-mantigi.md) oku; sonraki taleplerde yalnız değişen olgu ve etkilenen meseleleri yeniden değerlendir. Basit sorularda akışı sorunun kapsamıyla sınırla. Her belirleyici sonucu belgedeki olguya ve doğrulanmış hukuki dayanağa bağla; eksik bilgide koşullu değerlendirme yap. Olguyu belgede görülen, kullanıcının beyanı, karşı tarafın iddiası ve henüz bilinmeyen olarak ayır; yanıtta araç çıktısını, dosya belgesini ve kendi yorumunu da birbirinden ayrı göster.

## Dosyayı kur

Kiracı sorunu üzerinden araştırma veya örnek çalışma istenirse [senaryo, belge ve emsal akışını](references/kiraci-senaryolari.md) kullan. `python scripts/scenarios.py search "sorun sözcükleri"` ile adayları, `python scripts/scenarios.py show K6` gibi bir çağrıyla gerekli belgeleri, belirleyici soruları ve kaynak sınırlarını getir. "kira" gibi genel sözcükler bütün senaryolarla eşleşir; sorunu belirleyen sözcüklerle ara. Karma sorunları ayrı tut; sözcük sıralamasını hukuki önem sayma. Kurgudaki olguları kullanıcı dosyasına ya da gerçek kararın olayına aktarma.

Kullanıcının istediği ürüne odaklan: kısa soruya kısa cevap; dosya analizine gerekçeli değerlendirme; dilekçe, ihtarname veya icra itirazı isteğine düzenlenebilir taslak; gönderimi kullanıcı yapar. Kullanıcının rolünü (kiracı, kiraya veren, yeni malik veya bunlardan birinin vekili) ve usul konumunu (davacı, davalı, takip alacaklısı/borçlusu ya da henüz ihtar, takip veya dava yok) önce belgelerden belirle; belirsizse [soru akışındaki](references/soru-akisi.md) sıfat sorusunu sor. Kiraya verenin davacı, kiracının davalı olduğunu varsayma: kiracı da uyarlama, depozito veya fazla ödeme iadesi, TBK 355 tazminatı ya da menfi tespit davasında davacı olabilir. Seçilen tarafın lehine çalışırken karşı tarafın en güçlü itirazlarını da araştır.

Kullanıcı avukat değil de uyuşmazlığın tarafı (kiracı, kiraya veren, kefil) olarak yazıyorsa: İcra takibi, ödeme veya tahliye emri, ihtar, dava ya da arabuluculuk tebligatı varsa yanıtın ilk satırında bir sürenin işliyor olabileceğini, kontrol edilecek tebliğ tarihini ve belgeyi belirt; doğrulanmamış tarihi kesin son gün olarak verme. Kirayı kendiliğinden kesme veya indirme, anahtarı belgesiz bırakma, itiraz ya da ödeme yapmadan bekleme, tahliye taahhüdü imzalama gibi hak kaybı veya temerrüt riski doğurabilecek adımları kesin tavsiye gibi sunma; riskini ve daha güvenli seçeneği göster. İtiraz, ihtar, ödeme kesme, imza veya dava gibi bağlayıcı bir adımdan önce avukata danışmayı; ücreti karşılayamıyorsa bulunduğu ildeki baro adli yardım bürosuna başvurmayı öner. Teknik terimleri (tebliğ, temerrüt, muacceliyet, tespit davası vb.) ilk geçtiği yerde tek cümleyle açıkla. Dilekçe istenirse bunun taslak olduğunu ve imza veya gönderimden önce kontrol edilmesi gerektiğini belirt.

Mevcut belgelerden çıkar, tekrar sorma:

- konut/çatılı işyeri/diğer nitelik
- taraf sıfatları
- sözleşme başlangıcı, süresi ve yenileme dönemi
- ihtar, ödeme emri ve diğer tebliğ tarihleri
- icra takibi, arabuluculuk başvuru/son tutanak ve dava tarihleri
- istenen sonuç
- modüle göre ayrıca:
  - tespitte artış şartının birebir metni, ödenen ve istenen bedelin aylık/yıllık, net/brüt niteliği, talep edilen dönem, önceki tespit kararları, emsal sözleşmeler ve bilirkişi raporu
  - tahliyede ileri sürülen sebep, taahhüdün imza ve boşaltma tarihi ile fiilî teslim tarihi
  - alacakta dönem–tutar–ödeme çizelgesi
  - depozitoda tutar, ödeme belgesi, giriş/çıkış tutanakları ve anahtar teslim tarihi

Bilgi eksikse [uyuşmazlığa göre soru akışını](references/soru-akisi.md) kullan: ilk turda yalnız sonucu veya süreyi etkileyen 3–5 kısa soru seç; daha azı yeterliyse listeyi doldurma. Devam eden işlem ve tebliğ tarihini önceliklendir. Eksik belge varken bağımsız araştırmayı sürdür, belirleyici tarihi veya olguyu varsayma.

Kira tespiti, uyarlama, tahliye ve alacak taleplerini ayrıştır. Karma dosyada talep bazında incele; ayrı dava türünün kurallarını tespit davasına aktarma.

Süre veya son gün sorulursa [süre hesabı ve formüllerini](references/sure-hesaplama.md) oku. `python scripts/deadlines.py tbk345 2026-09-01` gibi komutlarla takvim adayını hesapla; girdinin hangi olay olduğunu çıktıdaki `meaning` alanından doğrula. Başlangıç olayını, normu ve tatil/arabuluculuk gibi uygulanmamış etkileri göster. TBK 345 etki eşiğini dava açma son günü, TBK 351 altı aylık beklemeyi başvuru son günü sayma. Ayı 30 güne çevirme; belgeden ve uygulanacak rejimden doğrulanmamış tarihi kesin son gün diye sunma. Dönem ve süre hesaplamalarında şu araçlardan yararlan:

- Kira tespiti dönemi ve TBK 345 eşikleri: `python scripts/hesap.py tespit --baslangic GG.AA.YYYY --hedef-donem GG.AA.YYYY (--artis-sarti veya --artis-sarti-yok) [--ihtar-tarihi GG.AA.YYYY] [--dava-tarihi GG.AA.YYYY] [--json]`. `--hedef-donem` yenilenen bir kira yılının (en az 2. kira yılı) başlangıç günü olmalıdır; ilk kira yılı veya dönem başına denk gelmeyen tarih hata verir. İhtar tarihi keşide değil tebliğ tarihidir; dava tarihi verilmezse hedef döneme etki koşulu boş kalır.
- TBK 347 on yıllık uzama takvimi: `python scripts/hesap.py tahliye-10yil --baslangic GG.AA.YYYY (--sure-yil N | --sure-ay N | --ilk-bitis GG.AA.YYYY)`. İlk belirli sözleşme süresini mutlaka ver: tam yılsa `--sure-yil`, tam yıl değilse `--sure-ay` veya ilk sürenin bittiği yıldönümü sınırı (son kullanım gününü izleyen gün) için `--ilk-bitis`. Hiçbiri verilmezse 12 ay varsayılır ve çok yıllı sözleşmede tarihler yıllarca erken çıkar; çıktıdaki ilk süreyi sözleşmeyle karşılaştır. Altı ay ve daha kısa sürede TBK 339/1 c.2 istisnasını önce incele. `python scripts/deadlines.py tbk347 YYYY-AA-GG` ise başlangıcı değil ilk sürenin bitimini alır.
- Dönem dökümü: `python scripts/hesap.py donemler --baslangic GG.AA.YYYY`.

## Dayanak araştır

Atıf yapılacak her kaynak için şu adımları izle:

1. `python scripts/pool.py stats` ile havuzun fiilî kayıt sayısını, içerik türü dağılımını ve tarih aralığını gör. Komut hata verirse (eksik dosya, yinelenen kimlik, metin hash'i veya manifest uyuşmazlığı) havuz araştırmasını durdur ve sorunu kullanıcıya bildir. Kullanıcı açıkça istemedikçe `--root` ile başka bir havuza geçme; geçersen seçeneği alt komuttan önce yaz (`python scripts/pool.py --root "KLASÖR" stats`) ve kullanılan havuz dosyasını yanıtta açıkça belirt.
2. İhtilafı ayrı araştırma sorularına böl. `python scripts/pool.py search` için örnek terimler: `"emsal" "hak ve nesafet"`, `"eski kiracı"`, `"beş yıl"`, `"344"`, `"345"`, `"ihtar"`, `"artış şartı"`, `"bilirkişi"`, `"ıslah"`. Her terimi aynı aramaya yığma. Sözcük varyantlarını (ör. `"hak ve nasafet"`) ve karşı yöndeki kararları da ara. Arama sözcük başından eşleşir; madde numarası araması esas/karar numarası veya tutar içindeki aynı sayıyla da eşleşebilir ve 01.07.2012 öncesi kararlardaki 818/6570 dönemine ait dayanakları yakalamaz. Bu nedenle madde numarası aramalarını kavram aramalarının tamamlayıcısı olarak kullan ve kesitin madde atfı olduğunu kontrol et. Arama boşsa hukuki kuralın bulunmadığı sonucuna varma.
3. Esasa ilişkin kural için gerekçeli kararları, usul meselesi için usul gerekçelerini önceliklendir; arama sonuçları zaten bu sırayla gelir, `--kind` ile daralt. Havuzun 1.603 kaydından 471'i esas gerekçesi, 551'i usul gerekçesi, 11'i sınırda, 570'i kısa karardır (güncel dağılım için `python scripts/pool.py stats` çıktısındaki `kinds` alanına bak). Kısa onama/gönderme kararından ayrıntılı ilke üretme. Etiket ve puanlar yalnız aday seçmeye yarar.
4. Atıf yapacağın her kararı `python scripts/pool.py get KARAR_KIMLIGI` ile tam metin olarak oku. Taraf iddiası, ilk derece gerekçesi, bozma gerekçesi, karşıoy ve nihai sonucu ayır. Olgu, tarih, kira türü, dönem ve usul aşamasını dosyayla karşılaştır. Kararda aktarılan başka kararın metnini görmeden onu doğrudan okunmuş kaynak gibi sunma.
5. Birebir alıntıyı `python scripts/pool.py quote KARAR_KIMLIGI "alıntı"` ile doğrula; alıntı bulunamazsa komut `exact_match: false` ile çıkış kodu 3 verir. Bulunması, hukuki yorumu doğrulamaz; bağlamı ayrıca değerlendir. Kaynak künyesini (`kunye`), kaynak adresini (`source_url`) ve sağlayıcısını (`source_provider`), yerel kayıt kimliğini ve metin hash'ini araştırma izinde tut. Ana havuzda adres, Bedesten belge kimliğinden türetilen resmî UYAP Mevzuat ve İçtihat sayfasıdır; BAM ve Yargıtay seçkilerinde (`source_provider: Dejure`) adres Dejure bağlantısıdır, resmî kaynak değildir ve giriş gerektirebilir; bunu resmî adres diye sunma. Dilekçe metninde yalnız künyeyi kullan; adresleri sağlayıcısıyla birlikte dilekçe dışındaki kaynak notunda ver. Künye/metin çelişkisini açıklamadan karar kullanma; yardımcının vermediği künye veya adres uydurma.

Karar kartları (C01–C10), soru–yanıt örnekleri (Q01–Q10) ve rehberlerde Dejure bağlantısıyla verilen dış araştırma kayıtları ([kaynak kaydı](references/egitim-kaynak-kaydi.json)) yerel havuzda kendi kimlikleriyle tam metin olarak bulunmaz; bu kimliklerle `get` ve `quote` alt komutları "Karar bulunamadı" hatası ve çıkış kodu 3 verir. Önce esas numarasıyla `python scripts/pool.py search "2025/893"` gibi arama yap; aynı karar ana havuzda UYAP kimliğiyle bulunabilir (ör. 3. HD 2025/893–2025/3205 → `1158814600`; 6. HD 2013/11846–2014/3788 → `97376300`). Bulunamazsa kararı bağlı karar aracıyla ([dış kaynak araçları](references/havuz.md#dış-kaynak-araçları)) tam metinden aç. Açamadıysan kart özetini yalnız araştırma yönü için kullan, dilekçeye birebir alıntı taşıma ve kaynak notuna "tam metin bu çalışmada yeniden doğrulanamadı; özet paket kartından" yaz.

## Konuya göre kaynak

Kira türü, görev/yetki, kamu taşınmazı, temsil veya paydaşlık çekişmeliyse önce [rejim ve taraflar rehberini](references/kira-rejimi-ve-taraflar.md) oku. Ürün kirası, taşınır ve taşınır yapı ayrımı yapılmadan süre seçme. Eğitim notu veya emsal listesi verilirse künye doğrulamasıyla gerekçe/hüküm kontrolünü ayır; [30 emsalin kontrol kaydındaki](references/emsal-listesi-dogrulama.md) yalnız künye düzeyindeki kayıtları doğrulanmış hukuki özet gibi kullanma. IBAN paylaşımı, sözlü sözleşme veya tek bir sözleşmedeki bildirim süresinden genel kural çıkarma.

Hak ve nesafet, beş yıllık dönem, TBK 345, eski kiracı indirimi veya geçici artış sınırı tartışılıyorsa [uygulama rehberini](references/uygulama-rehberi.md) oku. Fazla ödeme iadesi gündeme gelirse [iade ve ispat rehberini](references/iade-ispat.md) kullan; İİK istirdadı ile genel iade talebini ayır. Kullanıcı veya sunulan bir not İstanbul BAM 49. HD “2024/331”, Yargıtay 6. HD E. 1984/5788 ya da Sakarya BAM 8. HD E. 2021/297, K. 2021/873 gibi doğrulanamamış bir atıf getirirse durumunu [kaynak kontrolünde](references/rehber-dogrulama.md) gör; tam künye ve metin olmadan doğrulanmış emsal gibi kullanma. Bu rehberleri kesin sonuç tablosu gibi uygulama.

BAM kararlarını kullanırken [seçki ve kullanım sınırlarını](references/bam-kararlari.md) oku. `research_notes` uyarılarını sonuç ve dilekçeye kaynak seçerken dikkate al. Arama sonuçları ana havuzu, BAM ve Yargıtay eklerini kapsar. Yargıtay eklerini kullanırken [seçki notlarını](references/yargitay-kararlari.md) oku; bozma, onama ve karar düzeltme aşamalarını ayır.

Cevaplı emsal örneği istenirse [kararlardan soru–yanıt rehberini](references/kararlardan-soru-yanit.md) kullan. `python scripts/decision_qa.py show Q01` kaynaklı yanıtı, `python scripts/decision_qa.py export` yalnız soruları verir. Örnek yanıtları kör sınama sonucu veya güncel her dosyaya uygulanacak kesin hüküm gibi sunma.

İlgili emsal için `python scripts/quality.py cards "ihtiyaç" "3. HD"` gibi bir veya birkaç terimle [yapılandırılmış karar kartlarını](references/karar-kartlari.json) ara; tırnak içindeki her terim ayrı aranır ve kartta hepsi geçmelidir, büyük/küçük harf ve Türkçe karakter farkı gözetilmez, künye `pool.py` biçimiyle (`3. HD`, `E. 2025/1495`) aranabilir; olay, delil, gerekçe, hüküm ve uygulanamayacağı durumu ayrı değerlendir. Kartlar yerel tam metin değil, incelenmiş kararların özetidir (`full_text_in_card: false`). Skill geliştirme veya değerlendirme talebinde [58 dosyalık sınama akışını](references/kalite-sinama.md) kullan; yapı kontrolünü hukuki başarı ölçümü diye sunma.

İhtiyaç nedeniyle tahliyede erken arabuluculuk, taahhütte boş tarih/ispat, aile konutu, iki haklı ihtar, yeniden kiralama tazminatı veya uyarlamada tedbir için [tahliye ve uyarlama kaynak kontrolünü](references/tahliye-ve-uyarlama-kontrol.md) oku. TBK 350 hakkındaki kararı 351/1'e otomatik taşıma; karşıoyu çoğunluk sonucu sayma. Bu kontrol belgesindeki eğitim kaynaklı ifadeleri ve kullanıcının sağladığı eğitim notu veya dökümündeki kişisel görüşleri, geçmiş dönem kurallarını doğrulanmış güncel içtihat gibi kullanma.

Depozito, teslim hasarı, ayıp gideri, kefalet veya kira devri tartışılıyorsa [teslim, masraf ve kefalet rehberini](references/teslim-masraf-kefalet.md) kullan. TBK 335 bildirimini 342'deki üç aya bağlama; 306'daki hakkı icra mahkemesinin ispat kurallarıyla karıştırma. İşyerinde devir yasağının yokluğunu yazılı rıza sayma.

TBK dışındaki icra, usul, aile konutu, aidat, kamu kiralaması, döviz, dönüşüm veya vergi meselesinde ve uygulanacak kanunun zaman bakımından seçiminde (01.07.2012 öncesi 818/6570 dönemi, 6101 geçiş hükümleri, belirli işyeri kiralarında 6217 geçici 2 ertelemesi) [mevzuat haritasını](references/mevzuat-haritasi.md) kullan. Konutlarda TBK geçici 1–2 sınırının tarih aralıkları [uygulama rehberindedir](references/uygulama-rehberi.md). Özel rejimi ve işlem tarihini seçmeden genel kira kuralını uygulama; haritadaki kaynak erişim sınırlarını koru.

## Zaman ve güncellik

Paket 6098 sayılı Türk Borçlar Kanunu'nun tam metnini (1–649. maddeler, geçici madde 1 ve 2, Kanuna işlenemeyen hüküm olarak 6217 sayılı Kanunun geçici 2. maddesi ve değişiklik/yürürlük tablosu) içerir (`data/mevzuat/`; yaklaşık 330 KB, doğrudan açma). `python scripts/tbk.py 344` veya `python scripts/tbk.py 345` ile ilgili maddeyi getir; geçici 1–2 için `python scripts/tbk.py --gecici 1` veya `python scripts/tbk.py --gecici 2`, 6217 geçici 2 ve değişiklik tablosu için `python scripts/tbk.py --ek` kullan; numarasız çağrı kaynak ve alınma bilgisini verir. Ayrıntılar: [references/mevzuat.md](references/mevzuat.md). Bu sabit kopyadır; somut dosyada uygulanacak dönem ve sonraki değişiklikleri ayrıca doğrula.

Havuz tarihî içtihat içerir; güncel mevzuatın veya tüm yeni kararların yerine geçmez. Havuzun ağırlığı 2010–2015 dönemindedir: 1.603 kaydın 1.213'ü bu yıllara aittir, 605 karar TBK'nın yürürlüğünden (01.07.2012) önce verilmiştir ve yalnız 90 karar 2020 ve sonrası tarihlidir. `python scripts/pool.py stats` yalnız en eski ve en yeni tarihi gösterir; güncel rejim için havuzu ince kabul et ve güncel içtihadı ayrıca araştır. Somut hukuki sonuç vermeden önce uygulanacak tarihteki ve güncel düzenlemeyi resmî mevzuat/Resmî Gazete üzerinden çevrimiçi doğrula; erişilebilir mevzuat ve içtihat araçlarını kendi yönergeleri ve [havuz rehberindeki dış kaynak kurallarıyla](references/havuz.md#dış-kaynak-araçları) birlikte kullanabilirsin. TBK 344–345, ilgili geçici düzenlemeler, arabuluculuk, görev/yetki ve usul konularını dosyanın gerektirdiği ölçüde kontrol et. İnternete erişilemiyorsa paketteki tarihli mevzuat metnini alınma tarihiyle birlikte kaynak olarak kullanabilirsin; buna dayanan süreyi "alınma tarihindeki metne göre takvim adayı" olarak sun ve sonraki değişikliklerin doğrulanmadığını belirt. Paket dışındaki veya güncelliği doğrulanamayan kuralı açıkça işaretle; kesin süre veya kesin sonuç üretme.

Karar tarihi ile uyuşmazlığa uygulanan hukuki dönemi ayrı tut. Eski endeks uygulamasını, geçici artış sınırını veya geçmiş usul uygulamasını bugün geçerliymiş gibi aktarma. Eski kiracı indirimi için evrensel sabit oran veya başarı yüzdesi verme. Süre hesabında başlangıç olayı, tebliğ, dönem, kural ve istisnayı görünür kıl; tarih eksikse alternatif senaryoları koşullu sun. Hedef dönem ve ihtar tarihlerini doğrulamak için `python scripts/hesap.py` çıktılarını hukuki gerekçeyle birleştir.

## Ürünü oluştur

Dosya analizinde gerektiği ölçüde: belirleyici olgular ve eksikler; uyuşmazlıklar; uygulanabilir kaynaklar; lehe/aleyhe emsaller ve ayrışan olgular; delil ihtiyaçları; somut sonraki adımlar. Havuzda delil bulamamak ile hukuken savunulamaz olmayı karıştırma.

Dilekçede somut vakıa → delil → doğrulanmış dayanak → talep bağlantısını kur. Künye atıflarını mahkeme/daire, E., K., tarih biçiminde ver. Bilinmeyen alanları `[DOLDURULACAK: ...]` olarak bırak; müvekkil adına olgu, tebliğ, emsal bedel veya arabuluculuk tutanağı uydurma. Teknik kayıt kimlikleri, kaynak adresleri, hash'ler ve doğrulama notlarını dilekçe dışındaki kısa kaynak notunda tut. Kısa cevap, dosya değerlendirmesi, dilekçe iskeleti, doğrulanamayan kural işareti ve kaynak notu biçimi için [çalışma akışının 6. bölümünü](references/calisma-mantigi.md) kullan.

Bilirkişi raporunda emsallerin konumu, alanı, kullanım biçimi, sözleşme tarihi, fiziksel özellikleri, bedelin net/brüt niteliği ve karşılaştırma yöntemini incele. Raporu görmeden eksiklik bulunduğunu iddia etme. Tutar hesabında girdileri ve dayandığın yöntemi göster; ilan bedelini gerçekleşmiş sözleşme bedeli gibi sunma.

Bu skill yerel araştırma ve taslak üretir. Dava açma, UYAP'a yükleme veya karşı tarafa gönderim bu çalışmanın parçası değildir; böyle bir eylem için ayrıca açık kullanıcı talebi gerekir.
