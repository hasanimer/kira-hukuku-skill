# Karar kartları ve dosya sınaması

Bu sürümde **58 özgün kurgu sınama dosyası (B01–B58)**, her biri için üç ölçüt ve **10 yapılandırılmış karar kartı** vardır. Sınama dosyaları gerçek müvekkil dosyaları değildir; [kiracı senaryoları (K1–K10)](kiraci-senaryolari.md) bundan ayrı bir settir. Ölçütler mevcut kaynaklı rehberlerden türetilmiş yazar taslağıdır; bağımsız hukukçu değerlendirmesi yapılmış bir altın standart değildir. Paket testinin geçmesi asistanın hukuki cevaplarının başarılı olduğunu göstermez.

Komutları skill kökünde çalıştır; `python` bulunmazsa `python3`, Windows'ta gerekirse `py -3` kullan.

## Kararı somut dosyaya bağla

**Cevaplı örnekler:** [On karardan soru–yanıt rehberi](kararlardan-soru-yanit.md). Kaynaklı editoryal yanıtlar canlı model sonucu değildir. Q01–Q06'nın olayları sırasıyla B06, B07, B33, B31, B12 ve B16 sınama dosyalarıyla örtüşür (Q03'teki karşıoy ayrımı B34'ü de kapsar). Bu dosyaların hukuki ayrımı aynı zamanda [tahliye ve uyarlama kaynak kontrolünde](tahliye-ve-uyarlama-kontrol.md) ve ilgili karar kartlarında yer aldığından sınama açık kaynaklıdır; bu dosyaların sonucunu ayrı alt toplam olarak raporla, bağımsız olgu sınaması gibi sunma. `score` çıktısındaki `linked_cards` alanı her dosyanın bağlı olduğu karar kartlarını gösterir. `python scripts/decision_qa.py export` yalnız on soruyu verir; `python scripts/decision_qa.py show Q01` yanıtı ve kaynağı da gösterir. Kör sınamada cevaplı rehberi veya kaynak kartlarını önceden açmak sonucu etkileyebilir; bu setin açık kaynak olduğunu raporla.

[Karar kartları](karar-kartlari.json) olay, belirleyici delil, mesele, gerekçe, hüküm, karşıoy, uygulanamayacağı durum ve kaynak izini ayrı alanlarda tutar. Kaynak kimliği/künye/hash [araştırma kaydıyla](egitim-kaynak-kaydi.json) eşleşir. Hash özgünlük veya hukuki doğruluk sertifikası değildir. Kartlar on yeni tam metin değildir; daha önce incelenmiş kararların yapılandırılmış özetleridir. Asıl metni okumadan dilekçeye birebir alıntı taşıma.

```sh
python scripts/quality.py cards
python scripts/quality.py cards "2025/3540"
python scripts/quality.py cards "Yargıtay 3. HD" "E. 2025/1495"
python scripts/quality.py cards tahliye depozito
```

Her terim ayrı aranır ve kartta hepsi geçmelidir; büyük/küçük harf ve Türkçe karakter farkı gözetilmez ve terim `pool.py search` gibi sözcük başından eşleşir; rakamla biten terim daha uzun sayının parçası olarak eşleşmez (`K. 2025/304`, `K. 2025/3048`'i bulmaz). Çıktıdaki `kunye` alanı `pool.py` künye biçimindedir. Kart araması ölçüt dosyası olmadan da çalışır.

Yeni kartta aynı alanları doldur; çoğunluk ile karşıoyu, bozma ile esas kabulünü birleştirme. Kartın sınama dosyası bağlantısı (`scenario_ids`) o kararı bütün o olaylara doğrudan uygulama izni değildir. Somut olgu farklarını ve sonraki içtihadı yeniden araştır.

## Sınama akışı

Her sınama dosyasında `modules` alanı [modüller](moduller.md) tablosundaki altı anahtardan (tespit, uyarlama, tahliye, alacak, guvence, sozlesme) birini veya birkaçını, `topic` alanı alt konuyu (ör. ihtiyac, taahhut, iki_hakli_ihtar) gösterir; `quality.py validate` bilinmeyen modülü reddeder. `reference` alanı ölçütlerin dayandığı rehberi, varsa `anchor` alanı o rehberde birebir geçmesi gereken dayanak metni gösterir; metin bulunamazsa `validate` hata verir.

1. [Sınama dosyası setini](../evals/cases.json) doğrula. Setin sürümü ve içerik hash'i değerlendirmeye bağlanır.
2. Cevap üretecek oturuma yalnız `export` çıktısını ve skill kaynaklarını ver. Ölçüt dosyası (`evals/cases.json`) kurulu skill klasöründe bulunduğundan `export` çıktısını asıl kopyada al; cevapları bu dosyanın silindiği ayrı bir kopyada üret ve `run` açıklamasına bunu yaz. O kopyada `quality.py cards` ile `decision_qa.py export` ve `show` ölçüt dosyası olmadan çalışır. Ölçüt dosyasını/`case` çıktısını cevap üretmeden önce okutma. Süreye bağlı sınama dosyalarında değerlendirme tarihi soru metninde "Bugünün tarihi …" olarak verilir; cevap üreten oturum kendi takvim tarihini değil bu tarihi esas almalıdır. Tarih verilmeyen dosyalarda süre sonucu cevabın üretildiği tarihe değil, verilen olgulara dayanır. Açık repo içindeki set gerçek gizli sınav değildir; bu yöntem yalnız doğrudan cevap anahtarı sızıntısını azaltır.
3. Her yanıtı değiştirmeden kaydet. Model/sürüm, tarih, kullanılan skill commit'i ve araç erişimini `run` açıklamasına yaz. Gerekirse her soruyu ayrı bağlamda çalıştır.
4. `review-template` ile inceleme taslağı çıkar. İnceleyici her ölçütte `met` alanını gerçek JSON boolean olarak işaretler; kısa gerekçe ve olumlu değerlendirmede yanıt içinden birebir kanıt girer. Eksik hususta olumsuz işaret ve neden gerekir. Sırf sorunun sözcüklerini tekrar etmek karşılanma sayılmaz. Zaten verilmiş bilgiyi tekrar sormak da soru ölçütünü karşılamaz.
5. `score` ile kapsamı, eksikleri ve kritik hataları raporla. Aynı set ve araç koşullarında önceki sürümle karşılaştır; mümkünse yanıt üreticisinden farklı bir hukukçu incelesin.

```sh
python scripts/quality.py validate
mkdir -p research-private
python scripts/quality.py --output research-private/prompts.json export
python scripts/quality.py case B06
python scripts/quality.py --output research-private/review.json review-template research-private/answers.json
python scripts/quality.py score research-private/review.json
```

Çıktı yolu mevcutsa araç üzerine yazmaz; yeni dosya adı seç. `research-private` klasörü git'e girmez (.gitignore); Windows'ta (cmd veya PowerShell) klasörü `mkdir research-private` ile oluştur. `review-template` çalıştırılmadan önce `research-private/answers.json` aşağıdaki biçimde elle hazırlanmalıdır. Dosya UTF-8 (BOM'lu veya BOM'suz) ya da UTF-16 (Windows PowerShell 5.1'de `>`/`Out-File` varsayılanı) olabilir; ANSI/cp1254 kabul edilmez. `case` yalnız inceleyici içindir.

`answers.json` biçimi (aşağıdaki yer tutucular gerçek sonuç değildir):

```json
{
  "suite_hash": "export çıktısındaki suite_hash",
  "run": "model, tarih, skill commit, araçlar",
  "answers": [{"id": "B06", "response": "Değiştirilmemiş gerçek yanıt"}]
}
```

İnceleme dosyasında `reviewer` ve `reviewed_on` (YYYY-AA-GG biçiminde inceleme tarihi, ör. 2026-10-08) doldurulur. Yanıt hash'i değişirse veya ölçütler güncellenirse yeniden inceleme gerekir. İfadelerin hukuki doğruluğunu Python ölçmez; alıntı eşleşmesi yalnız değerlendirme izini denetler. İnceleyicinin yanlış işaretlemesi otomatik saptanamaz.

## Tetiklenme sınaması

[Tetiklenme kümesi](../evals/trigger-cases.json), skill açıklamasının kira sorularında devreye girip girmediğini ve tapu harcı, kira geliri vergisi, finansal kiralama veya kat mülkiyeti aidatı gibi yakın ama kapsam dışı sorularda devre dışı kalıp kalmadığını sınamak için olumlu ve olumsuz sorgular içerir; her kutupta en az on sorgu bulunur. Olumlu sorgularda `module` alt konu etiketini, `modules` altı modül anahtarını gösterir; olumsuz sorgularda ikisi de boştur.

`python scripts/quality.py triggers` yalnız yapıyı doğrular; tetiklenme oranı ölçülmüş değildir. Ölçüm için `python scripts/quality.py --output research-private/trigger-set.json trigger-export` çıktısını canlı Codex/Claude oturumlarında (ör. skill-creator `run_eval.py --eval-set`) her sorgu için en az üç kez çalıştır; sonucu küme sürümü ve tarihle raporla.

## Ölçümün anlamı

Her dosyada hukuki ayrım (`analysis`), gerekli soru/belge (`questions`) ve yanlış genellemeden kaçınma (`avoid`) değerlendirilir. Bir dosya üçü de karşılandığında geçer. Hukuki ayrım ve yanlış sonuç ölçütündeki başarısızlık ayrıca kritik hata sayılır; yüksek toplam puan bunu gizlemez. Yalnız incelenen örneklerdeki oran, bütün set başarısı değildir; eksik dosya varken `suite_passed` false kalır. Henüz bu 58 soruyla canlı model performansı ölçülmedi.

Yeni eklenen kaynakların konu/kapsam kontrolü [eğitim materyali kaydındadır](egitim-materyalleri.md). Ham eğitim metinleri ve gerçek dosya yanıtlarını kamuya açık depoya ekleme; yalnız anonimleştirilmiş ve paylaşılması uygun değerlendirmeleri ayrıca seç.
