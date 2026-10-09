# Yerel havuz ve kaynak izi

Varsayılan kök: bu skill klasöründeki `data/`. Yardımcı yolu kendi konumundan çözer; skill klasörünün tamamı başka dizine taşınabilir. Ana havuzdaki 1.576 karar ile `bam-selected.jsonl` dosyasındaki 17 BAM kararı ve `yargitay-selected.jsonl` dosyasındaki 10 Yargıtay kararının toplam 1.603 tam metni pakete dahildir. BAM seçkisi için [kullanım notlarını](bam-kararlari.md) oku. Başka havuzu açıkça seçmek için `--root "..."` seçeneğini alt komuttan önce yaz: `python scripts/pool.py --root "..." stats` (sonda verilirse argparse "unrecognized arguments" hatası verir; `scenarios.py` için de aynı sıra geçerlidir, ancak orada `--root` `data/` klasörünü değil skill kökünü gösterir).

Bu paket 20.09.2026 tarihli sabit kopyadır; 09.10.2026'da BAM ve Yargıtay seçkilerindeki yedi kaydın `research_notes` alanı güncellendi ve İzmir BAM 27. HD E. 2025/805 kaydında (`9ccfc163-f9fc-4c50-95c4-5853bab1eea4`) vekil adı anonimleştirildi (`text_sha256` değişti; önceki metnin hash'i `source_text_sha256` alanındadır). Ana havuzdaki 1.576 kayıt değişmedi. Kaynak proje değişince otomatik güncellenmez. `data/manifest.json` kaynak ve paket dosyalarının hash değerlerini, kayıt sayısını ve etiket birleştirme yöntemini içerir. Hukuki içerik korunarak aktarılmıştır. Açık kişi adı çıkarılan kayıtlarda `redactions` anonimleştirmeyi, `source_text_sha256` kaynak metnini, `text_sha256` yerel metni izler.

## Sürümler

19.09.2026 tarihinde incelenen dosyalar:

- `topic-rescan-assistant-adjusted.jsonl`: varsayılan sıkı havuz, 1.576 kayıt; tarih aralığı 14.10.2004–21.01.2026. Yeniden tarama ve bilinen 13 dışlama birlikte uygulanmış.
- `value_assessment` etiketleri önceki 1.645 kayıtlık `verified-topic-pool.jsonl` havuzundan yalnız `(document_id, text_sha256)` eşleşmesiyle paket kayıtlarına eklenmiştir. Önceki havuza çalışma zamanında ihtiyaç yoktur; dışlanmış kararlar pakete geri eklenmemiştir.
- `data/verified-topic-report.md`, `data/topic-rescan-report.md`: seçim yöntemleri ve sınırlılıkları; yollar skill köküne göredir. Raporlarda adı geçen diğer ara dosyalar (önceki havuz dahil) pakette yoktur ve yardımcıların çalışması için gerekmez.

`verified` adı bağımsız hukukçu onayı anlamına gelmez. Aynı JEV modelinin yeniden değerlendirmesi bağımsız model testi değildir. `human_validated: false` kayıtlarını insan onaylı diye sunma.

## Salt okunur yardımcı

Python standart kütüphanesi yeterli. Skill kökünde çalıştırılacak komut örnekleri; PowerShell, Bash ve Zsh'te aynıdır. `python` (Python 3.10 veya üstü) bulunmazsa `python3`, Windows'ta gerekirse `py -3` kullan; başka çalışma dizininde betiğin mutlak yolunu kullan:

```sh
python scripts/pool.py stats
python scripts/pool.py search "eski kiracı" --kind esas_gerekcesi --limit 8
python scripts/pool.py search emsal bilirkişi --limit 8
python scripts/pool.py get KARAR_KIMLIGI
python scripts/pool.py quote KARAR_KIMLIGI "Dilekçede kullanılacak alıntının tamamı"
```

`stats` kayıt sayısını, içerik türü dağılımını (`kinds`), dosya başına kayıt sayısını (`collections`), en eski/en yeni karar tarihini ve insan onaylı kayıt sayısını (`human_validated_records`) verir. `KARAR_KIMLIGI` yerine aramada dönen `document_id` kullan. Arama bütün terimlerin bulunmasını ister (VE); büyük/küçük harf ve Türkçe karakter/aksan farkını (ı–i, ş–s, ü–u gibi), düz ve kıvrık kesme/tırnak işaretlerini (' ’ “ ”), tire biçimlerini ve fazla boşlukları yok sayarak sözcük başından eşleştirir: `kira` terimi `kiracı`, `kiraya` gibi ekli biçimleri, `ihtar` terimi `ihtarname`, `ihtarın` geçişlerini bulur; `artış` terimi `tartışılması`, `ÜFE` terimi `TÜFE` içinde eşleşmez. Rakamla biten terim daha uzun bir sayının parçası olarak eşleşmez: `344` terimi `TBK 344/3` atfını bulur, `2017/13443` esas numarasını bulmaz; esas/karar numarası veya tutar içinde geçen aynı sayı yine eşleşebileceğinden kesiti kontrol et. Sözcük içi eşleşme gerekirse `--substring` ekle. Tırnaksız `eski kiracı` iki ayrı terimdir; sözcükler metnin herhangi bir yerinde bulunabilir. Tırnaklı `"eski kiracı"` tek terimdir; sözcüklerin aynı sırayla bitişik geçmesini ister (satır sonu ve fazla boşluk tek boşluk sayılır).

Sıralama önce içerik türüne (esas gerekçesi, usul gerekçesi, sınırda, kısa karar), sonra sözcük geçişine göredir; kısa onama kararları listenin sonuna düşer. Bu sıra hukuki önem veya emsal gücü puanı değildir. Arama kesiti, aranan terimlerden en çoğunu içeren ilk paragraftan alınır (tek terimde terimin ilk geçtiği paragraf); uzun paragraf ilk eşleşmenin çevresinden kırpılır, kırpılan uçlar `…` ile gösterilir ve kesit tam metin yerine geçmez. Satır sonuna bölünmüş tırnaklı ifadede kesit terimi içermeyebilir. Varsayılan olarak en çok 8 sonuç döner; `total_matches` alanını `results` sayısıyla karşılaştır, gerekirse sorguyu daralt veya limiti artır (`--limit` 1–2000).

Arama eşanlamlı veya farklı yazılmış ifadeyi kendiliğinden bulmaz. Aynı kavram için aşağıdaki varyantları ayrı aramalarla dene ve `total_matches` değerlerini karşılaştır.

| Kavram | Ayrı ayrı aranacak varyantlar |
| --- | --- |
| Kira tespiti | `"kira bedelinin tespit"`, `"kira parasının tespit"`, `"kira tespit"`, `"kira bedelinin belirlen"`, `"kira bedeli tespit"`. Yalnız `"kira tespit"` bu kararların yaklaşık beşte birini verir; tırnaksız `kira tespit` ise "tespit" geçen her kararı getirir. |
| İhtiyaç | `"ihtiyaç"`, `"gereksinim"` |
| Ürün kirası | `"ürün kira"`, `"hasılat kira"` (818 sayılı BK'daki adı; kararlarda hâlâ kullanılır) |
| Hak ve nesafet | `"hak ve nesafet"`, `"hak ve nasafet"` (yazım varyantı), `"hakkaniyet"` |
| Taahhüt | `"taahh"` (taahhüt ve taahhüdü biçimlerini birlikte bulur) |

Kayıtta `date_warning` varsa metnin kapanış cümlesindeki karar günü künye tarihinden farklıdır; alıntılarken farkı belirt ve tarihi kaynak sayfasından kontrol et. `out_of_scope: true` kayıt tam metin incelemesinde konu dışı bulunmuştur ve listenin sonuna düşer; `scope_uncertain: true` kayıt konu bakımından sınırdadır ve kendi içerik türünün sonuna düşer. `scope_haric_probability` yeniden taramadaki kapsam dışı olasılığıdır; eşik yalnız tam metin incelemesi yapılmamış (`review_level: not_reviewed`) kayıtlarda uygulanır ve 0,30 ve üstü değer `scope_uncertain` işaretini doğurur; asistan tam metin incelemesinden geçmiş (`assistant_full_text`, `assistant_full_text_review`) kayıtlarda bu eşik uygulanmaz. Hiçbir kayıt insan onaylı değildir (`human_validated: false`). `needs_scope_review` yalnız kaynak veride bu işaret bulunan kayıtlarda doludur, diğerlerinde `null` döner. Bu kayıtları kullanmadan önce varsa `research_notes` uyarılarını ve tam metindeki kira ilişkisini kontrol et.

Yardımcı her okumada kayıt metni SHA-256 değerini kontrol eder; `data/manifest.json` varsa karar dosyalarının SHA-256 değerlerini de manifestle karşılaştırır ve sonucu `manifest_verified` alanında bildirir (manifest yoksa, ör. `--root` ile seçilen deneme havuzunda, değer `false` olur). Uyuşmazlıkta durur. Hash yalnız paket içi bütünlüğü doğrular, resmî kaynağın doğruluğunu veya eksiksizliğini kanıtlamaz. `quote` büyük/küçük harf, noktalama ve boşlukları değiştirmeden arar; girdiyi yalnız Unicode NFC biçimine getirir (ayrık kodlanmış Türkçe harf birleşik biçime çevrilirse `input_normalized: true` olur). Konumlar Python Unicode karakter dizisinde sıfır tabanlı, bitiş hariçtir. Dilekçede kullanacağın alıntının tamamını sorgula; parçasını değil. 20 karakterden kısa sorguda çıktı `warning` alanı taşır. Toplam eşleşme sayısı `occurrence_count` alanındadır; `occurrences` en çok ilk 20 eşleşmeyi bağlamıyla verir, fazlası varsa `occurrences_truncated: true` olur. Bulunamayan alıntıyı yaklaşık eşleşmiş diye doğrulama.

Çıkış kodları (`pool.py`): `0` başarılı; `1` veri/bütünlük hatası (hash veya manifest uyuşmazlığı, tekrarlanan kimlik, okunamayan dosya; stderr `HATA (veri bütünlüğü)` ile başlar) ya da çıktıyı okuyan sürecin erken kapanması (ör. `| head`; Linux/macOS'ta stderr boş kalır, veri hatası değildir; Windows'ta kapalı boru `[Errno 22] Invalid argument` içeren bir HATA iletisi olarak görünebilir, bu da veri hatası değildir); `2` kullanım hatası (eksik veya boş bağımsız değişken, geçersiz `--limit`); `3` bulunamadı — `quote` alıntıyı bulamadıysa JSON yine basılır ve `exact_match: false` olur, kimlik havuzda yoksa stdout boştur. Veri hatalarında ve kimlik havuzda bulunmadığında stderr iletisi `HATA` ile başlar; `quote` alıntıyı bulamadığında stderr boş kalır, sonuç stdout'taki JSON'dadır (`exact_match: false`, çıkış kodu `3`). Kısa çizgiyle başlayan alıntılarda alıntıdan önce `--` kullan: `python scripts/pool.py quote KARAR_KIMLIGI -- "-alıntı"`.

Araştırma izinde: havuz dosyası (kayıttaki `pool_file`), document_id, `kunye`, `source_url`, text_sha256, alıntı ve konumu, dosyaya uygulanabilirlik gerekçesi. Çıktı zarfındaki `pool_files` alanı okunan her havuz dosyasının adını ve SHA-256 değerini verir; yerel mutlak yol yazdırılmaz. Ana havuzdaki `document_id` UYAP Mevzuat ve İçtihat (Bedesten) belge kimliğidir; yardımcı `source_url` alanını `https://mevzuat.adalet.gov.tr/ictihat/<document_id>` deseniyle türetir ve `source_provider` alanında "kimlikten türetildi" diye işaretler. Bu adres kararın resmî sayfasıdır; araştırma notunda künyeyle birlikte verilir, dilekçe metninde yalnız künye kullanılır. Kayıtta yazılı başka bir adres varsa ona dokunulmaz. Seçki kayıtları (BAM ve Yargıtay seçkileri; kimlikleri sayısal değildir) için adres türetilmez; yalnız kayıttaki `source_url` kullanılır. Bu adresler Dejure bağlantısıdır (`source_provider: Dejure`), resmî sayfa değildir ve giriş gerektirebilir; okuyucuya bu şekilde tanımlanır. Bunların dışında adres uydurma.

`kunye` alanı dilekçe biçiminde hazır gelir: "Yargıtay 3. HD, E. 2017/8082, K. 2019/5082, T. 28.05.2019". Ana havuzda `court` yalnız daire adıdır; mahkeme adını yardımcı ekler.

Yalnız BAM kararları için `python scripts/pool.py search ihtar --court-type bam --limit 20` kullan; BAM seçkisi 17 karar olduğundan `--limit 20` bütün eşleşmeleri gösterir. BAM kaynak adresleri `source_url`, kullanım sınırları `research_notes` alanında döner. BAM ve Yargıtay seçkilerindeki Dejure bağlantıları giriş gerektirebilir; yerel tam metin erişimi çevrimdışı çalışır.

Yargıtay ekleri için [seçki ve kullanım sınırlarını](yargitay-kararlari.md) oku. Ana havuz kayıtlarına yardımcı `court_type: yargitay` etiketini okuma sırasında ekler; `--court-type yargitay` ana havuzu ve Yargıtay seçkisini birlikte, `--court-type bam` yalnız BAM seçkisini verir.

## Dış kaynak araçları

Yerel havuz kira tespiti ağırlıklıdır; bütün kira hukuku modüllerini kapsadığı iddia edilmez. Önce yerel havuzu, BAM ve Yargıtay seçkileriyle birlikte ara; yetersizse aşağıdaki araçlarla odaklı dış araştırma yap ve dış kararları paket kaynaklarından ayrı işaretle. Dış araçlara gönderilen sorguya müvekkil veya karşı tarafı tanıtan bilgi yazma; SKILL.md'deki gizlilik kuralı bütün dış araçlar için geçerlidir.

- DeJure: `search_decisions` ile aday, `lookup_decisions` ile künye, `get_decision` ile metin. Kesilme varsa `next_offset` üzerinden devam et.
- Legaluga: `search_cases` → `get_case` → gerektiğinde `verify_quotation`. `source_ref`, `passage_id`, görüş sahibi ve kesilme alanlarını koru. `get_case` yalnız kesit döndürebilir; `full_text_truncated` doğruysa tam metin sayma. Büyük havuzun tamamının yerel pakete eklendiğini veya her sorguda tarandığını iddia etme.
- Bağlı mevzuat/içtihat aracı: kendi başlangıç yönergesini uygula; maddeyi veya kararı dönen kimlikle getir. Arama sözdizimini sağlayıcıya göre kullan; boşlukların AND olduğu varsayımında bulunma.

Kaynak araç hatası, sıfır sonuç değildir. Bir kaynak erişilemiyorsa bunu araştırma izine yaz, diğerlerinde devam et. Aynı karar farklı kaynaklardan gelirse künyeyi karşılaştır; farklı kaynak kimliklerini sakla. Eşleşmeyen metinleri sessizce birleştirme.
