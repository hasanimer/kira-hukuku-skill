# Yerel havuz ve kaynak izi

Varsayılan kök: bu skill klasöründeki `data/`. Yardımcı yolu kendi konumundan çözer; skill klasörünün tamamı başka dizine taşınabilir. Ana havuzdaki 1.576 karar ile `bam-selected.jsonl` dosyasındaki 17 BAM kararı, `yargitay-selected.jsonl` dosyasındaki 10 Yargıtay kararı ve `derleme-v5-selected.jsonl` dosyasındaki 135 kararın toplam 1.738 tam metni pakete dahildir. Derleme seçkisinin konu dizini ve doğrulama yöntemi [derleme dizinindedir](derleme-v5.md); her kaydın `collection` alanı geldiği dosyayı gösterir. BAM seçkisi için [kullanım notlarını](bam-kararlari.md) oku. Başka havuzu açıkça seçmek için komuta `--root "..."` ekle.

Bu paket 20.09.2026 tarihinde güncellenmiş sabit kopyadır; kaynak proje değişince otomatik güncellenmez. `data/manifest.json` kaynak ve paket dosyalarının hash değerlerini, kayıt sayısını ve etiket birleştirme yöntemini içerir. Hukuki içerik korunarak aktarılmıştır. Açık kişi adı çıkarılan kayıtlarda `redactions` anonimleştirmeyi, `source_text_sha256` kaynak metnini, `text_sha256` yerel metni izler.

## Sürümler

19.09.2026 tarihinde incelenen dosyalar:

- `topic-rescan-assistant-adjusted.jsonl`: varsayılan sıkı havuz, 1.576 kayıt; tarih aralığı 14.10.2004–21.01.2026. Yeniden tarama ve bilinen 13 dışlama birlikte uygulanmış.
- `value_assessment` etiketleri önceki 1.645 kayıtlık `verified-topic-pool.jsonl` havuzundan yalnız `(document_id, text_sha256)` eşleşmesiyle paket kayıtlarına eklenmiştir. Önceki havuza çalışma zamanında ihtiyaç yoktur; dışlanmış kararlar pakete geri eklenmemiştir.
- `data/verified-topic-report.md`, `data/topic-rescan-report.md`: seçim yöntemleri ve sınırlılıkları; yollar skill köküne göredir.

`verified` adı bağımsız hukukçu onayı anlamına gelmez. Aynı JEV modelinin yeniden değerlendirmesi bağımsız model testi değildir. `human_validated: false` kayıtlarını insan onaylı diye sunma.

## Salt okunur yardımcı

Python standart kütüphanesi yeterli. Skill kökünde çalıştırılacak PowerShell örnekleri (başka çalışma dizininde betiğin mutlak yolunu kullan):

```powershell
python scripts/pool.py stats
python scripts/pool.py search "eski kiracı" --kind esas_gerekcesi --limit 8
python scripts/pool.py search emsal bilirkişi --limit 8
python scripts/pool.py get KARAR_KIMLIGI
python scripts/pool.py quote KARAR_KIMLIGI "Birebir kısa alıntı"
```

`KARAR_KIMLIGI` yerine aramada dönen `document_id` kullan. Arama bütün terimlerin bulunmasını ister; aksanları sadeleştirerek eşleştirir. Sıralama önce içerik türüne (esas gerekçesi, usul gerekçesi, sınırda, kısa karar), sonra sözcük geçişine göredir; kısa onama kararları listenin sonuna düşer. Bu sıra hukuki önem veya emsal gücü puanı değildir. Arama kesiti tam metin yerine geçmez. Sonuç sayısı sınırlı olduğu için `total_matches` alanını kontrol et, gerekirse sorguyu daralt veya limiti artır (`--limit` en çok 2000).

Yardımcı her okumada kayıt metni SHA-256 değerini kontrol eder; uyuşmazlıkta durur. Hash yalnız dosya içi bütünlüğü doğrular, resmî kaynağın doğruluğunu veya eksiksizliğini kanıtlamaz. `quote` büyük/küçük harf, noktalama ve boşlukları değiştirmeden arar; konumlar Python Unicode karakter dizisinde sıfır tabanlı, bitiş hariçtir. Bulunamayan alıntıyı yaklaşık eşleşmiş diye doğrulama.

Ana havuz kararının metni Bedesten'den (`karar_getir`) canlı alındıysa yerel metinden yalnız boşluk ve satır sonlarında ayrışabilir. Bu durumda `python scripts/pool.py quote KARAR_KIMLIGI "Pasaj" --ignore-space` kullan: birebir eşleşme yoksa boşluk farkları yok sayılır, `match_mode` alanı `ignore_space` olur ve `exact_match` false kalır. Harf, noktalama veya Unicode biçimi farkı yine eşleşmez. Her iki modda da dilekçeye canlı pasajı değil, dönen `matched_text` yerel parçasını birebir alıntı olarak taşı.

Araştırma izinde: havuz dosyası, document_id, `kunye`, `source_url`, text_sha256, alıntı ve konumu, dosyaya uygulanabilirlik gerekçesi. Ana havuzdaki `document_id` UYAP Mevzuat ve İçtihat (Bedesten) belge kimliğidir; yardımcı `source_url` alanını `https://mevzuat.adalet.gov.tr/ictihat/<document_id>` deseniyle türetir ve `source_provider` alanında "kimlikten türetildi" diye işaretler. Bu adres kararın resmî sayfasıdır; okuyucuya künyeyle birlikte verilir. Kayıtta yazılı başka bir adres varsa ona dokunulmaz. Kimliği sayısal olmayan kayıt (BAM ve Yargıtay seçkileri) için adres türetilmez; yalnız kayıttaki `source_url` kullanılır. Bunların dışında adres uydurma.

`kunye` alanı dilekçe biçiminde hazır gelir: "Yargıtay 3. HD, E. 2017/8082, K. 2019/5082, T. 28.05.2019". Ana havuzda `court` yalnız daire adıdır; mahkeme adını yardımcı ekler.

Yalnız BAM kararları için `python scripts/pool.py search ihtar --court-type bam` kullan. BAM kaynak adresleri `source_url`, kullanım sınırları `research_notes` alanında döner. Dejure bağlantıları giriş gerektirebilir ve resmî adres değildir; yerel tam metin erişimi çevrimdışı çalışır. Bu kararların resmî karşılığını E., K. ve tarihle bağlı kaynakta (Legaluga `karar_ara`) ara; bulunamazsa adres türetme.

Yargıtay ekleri için [seçki ve kullanım sınırlarını](yargitay-kararlari.md) oku. Ana havuz kayıtlarına yardımcı `court_type: yargitay` etiketini okuma sırasında ekler; `--court-type yargitay` ana havuzu ve Yargıtay seçkisini birlikte, `--court-type bam` yalnız BAM seçkisini verir.
