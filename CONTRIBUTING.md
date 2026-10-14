# Katkıda bulunma

Önce mevcut issue ve pull request'leri kontrol edin. Küçük ve tek amaçlı değişiklikler incelemeyi kolaylaştırır.

## Hata bildirimi

Kullandığınız komutu, Python sürümünü, beklenen sonucu ve gerçekleşen sonucu yazın. Karar hatalarında `document_id` ve ilgili künyeyi; mevzuat hatalarında madde numarasını ve kaynak adresini ekleyin. Herkese açık issue veya pull request'e müvekkil belgesi, kişisel iletişim bilgisi, parola veya erişim anahtarı koymayın.

## Yerel kontrol

```sh
python scripts/validate.py
python -m unittest discover -s tests -v
```

Komutları depo kökünde çalıştırın; `python` komutu yoksa `python3`, Windows'ta gerekirse `py -3` kullanın.

Standart kütüphane yeterlidir. GitHub Actions aynı denetimi Windows, macOS ve Linux üzerinde Python 3.10 ve 3.14 ile çalıştırır. CI, kodlama belirtilmeden açılan metin dosyalarını ve alt süreç çıktılarını (`EncodingWarning`) hata sayar; dosya okurken ve yazarken `encoding='utf-8'` belirtin. Aynı denetimi yerelde `PYTHONWARNDEFAULTENCODING=1` ve `PYTHONWARNINGS=error::EncodingWarning` ortam değişkenleriyle çalıştırabilirsiniz. Linux işinde ayrıca yalnız CI'da kurulan `pyflakes` çalışır; paket betikleri standart kütüphane dışında bağımlılık almaz.

## Değişiklik kuralları

- Yönerge değişikliklerinde `SKILL.md` ile ilgili rehberlerin tutarlı kalmasını sağlayın.
- `SKILL.md` ön bilgisindeki `description` tek satır kalmalı ve 500 UTF-8 baytı aşmamalıdır (Codex için temkinli sınır; `validate.py` denetler).
- Kaynak metinlerde yapılan değişikliği gerekçesi ve kaynağıyla açıklayın; etiket ile tam metni birbirinden ayırın.
- `data/` altındaki her dosya (`data/README.md` ve rapor `.md` dosyaları dahil) `data/manifest.json` içindeki `files` alanında SHA-256 ile sabitlenmiştir. Bu dosyalardan birini yalnız yazım düzeltmesi için bile değiştirirseniz yeni hash'i `files` alanına yazın. Karar metni değişirse kaydın `text_sha256` alanını da güncelleyin. Karar metni veya `research_notes` değişirse `references/havuz.md`'deki paket tarihi notunu da güncelleyin. Başarısız kontrolü geçirmek için doğrulanmamış bir kaynağın hash'ini değiştirmeyin.
- Karar eklenir, çıkarılır veya yeniden sınıflandırılırsa `data/manifest.json` içindeki `records`, `collections`, `snapshot_date` ve varsa `kinds` alanlarını güncelleyin.
- Ardından `python scripts/pool.py stats` çıktısındaki `records`, `kinds`, `date_min` ve `date_max` değerlerini belgelerde elle yazılmış sayılarla karşılaştırın. Bu sayılar şu dosyalardadır: `README.md` (üst tablo, veri tablosu ve emsal derlemesi satırı), `SKILL.md`, `data/README.md` ve `references/havuz.md`. `references/derleme-v5.md` `python scripts/derleme.py render --write` ile üretilir ve `derleme.py validate` ile denetlenir. Daire ve yıl dağılımı ile 01.07.2012 öncesi karar sayısı `stats` çıktısında yoktur. `tests/test_docs.py` README'deki kayıt sayısını, tarih aralığını, içerik türü, dosya, daire ve yıl dağılımını; SKILL.md'deki toplam ve dosya başına kayıt sayılarını, esas gerekçesi ve kısa karar sayılarını ve "Zaman ve güncellik" bölümündeki toplam kayıt, 2010–2015, 01.07.2012 öncesi ve 2020 sonrası sayılarını veriden hesaplayarak denetler. `validate.py` sınama, karar kartı ve senaryo sayılarını denetler; diğer belgelerdeki sayılar otomatik denetlenmez. Eski değerleri aramak için değişen sayıları ve tarihleri desene yazın; bugünkü değerlerle örnek: `grep -rnwE '1\.?738|1\.?576|1\.?229|1\.?105|578|572|574|557|607|152|135|14\.10\.2004|21\.0[15]\.2026' README.md SKILL.md data/README.md references` (birkaç ilgisiz `607`, `21.01.2026` ve `21.05.2026` eşleşmesi çıkar).
- Kanun sürümü değişirse bütün bölümleri, alınma bilgisini ve okunabilir metni birlikte güncelleyin.
- Yeni sürümde dosya adlarını veya komut davranışını değiştiriyorsanız kullanıcı belgelerini de güncelleyin.
- `evals/decision-qa.json`, `evals/cases.json` veya karar kartları değişirse `references/kararlardan-soru-yanit.md` sayfasını elle düzenlemeyin; `python scripts/decision_qa.py render --write` ile yeniden üretip `python scripts/validate.py` çalıştırın. Çıktıyı kabuk yönlendirmesiyle (`>`) dosyaya yazmayın; Windows PowerShell dosyayı UTF-16 veya farklı kod sayfasıyla kaydedebilir.
- `data/derleme-v5-index.json` veya `data/derleme-v5-selected.jsonl` değişirse `references/derleme-v5.md` sayfasını elle düzenlemeyin; `python scripts/derleme.py render --write` ile yeniden üretin, değişen veri dosyalarının hash'ini `data/manifest.json` `files` alanına yazın ve `python scripts/validate.py` çalıştırın. Çıktıyı `>` ile yazmayın.
- Legaluga veya TypeSafe araştırma dökümlerini, araç yanıtlarını ve UDF dosyalarını public depoya eklemeyin; yalnız anonim ve paylaşılması uygun doğrulama özetlerini ekleyin.

Bir veri kaydının yayımlanmaması gerektiğini düşünüyorsanız hassas içeriği tekrar yayımlamadan yalnız kayıt kimliğini ve gerekçeyi belirtin.
