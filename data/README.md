# Veri paketi

Karar havuzu 1.603 kayıt içerir; kararların hukuki içeriği korunur. Açık kişi adı çıkarılan kayıtlarda anonimleştirme `redactions` alanında belirtilir; `source_text_sha256` kaynak metnini, `text_sha256` dağıtılan metni izler. Seçim ve etiketleme yöntemleri [havuz rehberinde](../references/havuz.md) açıklanır. Bu paket tüm kira uyuşmazlıklarını veya güncel içtihadın tamamını kapsadığı iddiasını taşımaz.

| Dosya | Amaç |
| --- | --- |
| `yargitay-selected.jsonl` | On Yargıtay kararının tam metni, kaynak bağlantısı ve inceleme notları |
| `bam-selected.jsonl` | On yedi BAM kararının tam metni, kaynak bağlantısı ve asistan inceleme notları |
| `topic-rescan-assistant-adjusted.jsonl` | Karar künyesi, tam metin, metin hash'i ve değerlendirme etiketleri |
| `topic-rescan-report.md` | Sıkı havuz seçiminin yöntemi |
| `verified-topic-report.md` | Önceki seçim aşamasının raporu |
| `mevzuat/6098-source.json` | Kanunun kaynak bölümleri ve alınma bilgisi |
| `mevzuat/6098-turk-borclar-kanunu.md` | Kanunun okunabilir tam metni |
| `manifest.json` | Paket dosyalarının SHA-256 değerleri ve kaynak sürüm izleri |

`verified` dosya adı insan doğrulaması anlamına gelmez. Etiketler aday karar seçimini destekler; kararı okumadan hukuki sonuca dönüşmez.

Rapor dosyalarında adı geçen ara çıktılar (`topic-rescan-keep.jsonl`, `topic-rescan-exclude.jsonl`, `topic-rescan-review.jsonl`, `topic-rescan-new-exclusions.jsonl`, `verified-topic-pool.jsonl`, `quality-excluded.jsonl`, `assistant-quality-audit.json`, `quality-human-queue.tsv`) kaynak projede kalmıştır; bu pakete dahil değildir ve yardımcıların çalışması için gerekmez. Veri dizininde bu açıklama dosyası ile yukarıdaki tabloda listelenen dosyalar bulunur.

Kanunun resmî adresi kaynak JSON dosyasındadır. Kararlarda `document_id`, künye ve `text_sha256` izleri korunur. `raw_sha256` yalnız ana havuzdaki 1.576 kayıtta bulunur. `source_text_sha256` Yargıtay seçkisinin 10 kaydında ve BAM seçkisinin 9 kaydında yer alır; kalan 8 BAM kaydında yalnız `text_sha256` vardır. Ana havuzdaki `document_id` UYAP Mevzuat ve İçtihat (Bedesten) belge kimliğidir; `scripts/pool.py` resmî adresi `https://mevzuat.adalet.gov.tr/ictihat/<document_id>` olarak türetir ve `source_provider` alanında işaretler. Veri dosyasına adres yazılmaz; dosya baytları ve hash'ler değişmez. Metin hash'i yerel bütünlüğü gösterir; tek başına resmî doğrulama değildir. Çalıştırma ortamı ve anahtar yuvası gibi iç operasyon alanları pakete dahil edilmez.

`yargitay-selected.jsonl` ve `bam-selected.jsonl` dosyalarındaki 27 kararın tam metni Dejure (app.dejure.ai) üzerinden alınmıştır; kayıtlardaki `source_provider` ve `source_url` alanları bu kaynağı gösterir. Bu bağlantılar üyelik girişi gerektirebilir. Metinler mahkeme kararıdır; Dejure kullanım koşullarının yeniden dağıtıma etkisi ayrıca kontrol edilmelidir. Dilekçede kaynak gösterirken künyeyi resmî kayıttan (UYAP Emsal / Yargıtay Karar Arama) doğrulayın. Mahkeme kararları ve kanun metninin lisans durumu için [README'nin Lisans bölümüne](../README.md#lisans) bakın.

`python scripts/validate.py` kayıt sayısını, dosya/metin hash'lerini, kanun bütünlüğünü ve yardımcıların temel davranışlarını doğrular. `.gitattributes` veri baytlarının işletim sistemine göre değiştirilmesini önler. Depodaki diğer metin dosyaları tüm platformlarda LF satır sonuyla çıkarılır.

Kaynak metin düzeltmesi öneriyorsanız kayıt kimliğini, kaynağı ve değişikliğin gerekçesini belirtin; metni sessizce değiştirmeyin. Müvekkil dosyalarını bu veri dizinine eklemeyin.
