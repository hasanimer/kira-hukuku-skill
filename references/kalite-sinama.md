# Karar kartları ve dosya sınaması

Bu sürümde **49 özgün kurgu senaryo**, her biri için üç ölçüt ve **10 yapılandırılmış karar kartı** vardır. Senaryolar gerçek müvekkil dosyaları değildir. Ölçütler mevcut kaynaklı rehberlerden türetilmiş yazar taslağıdır; bağımsız hukukçu değerlendirmesi yapılmış bir altın standart değildir. Paket testinin geçmesi asistanın hukuki cevaplarının başarılı olduğunu göstermez.

## Kararı somut dosyaya bağla

**Cevaplı örnekler:** [On karardan soru–yanıt rehberi](kararlardan-soru-yanit.md). Kaynaklı editoryal yanıtlar 49 senaryonun yanıt anahtarı veya canlı model sonucu değildir. `python scripts/decision_qa.py export` yalnız on soruyu verir; `show Q01` yanıtı ve kaynağı da gösterir. Kör sınamada cevaplı rehberi veya kaynak kartlarını önceden açmak sonucu etkileyebilir; bu setin açık kaynak olduğunu raporla.

[Karar kartları](karar-kartlari.json) olay, belirleyici delil, mesele, gerekçe, hüküm, karşıoy, uygulanamayacağı durum ve kaynak izini ayrı alanlarda tutar. Kaynak kimliği/künye/hash [araştırma kaydıyla](egitim-kaynak-kaydi.json) eşleşir. Hash özgünlük veya hukuki doğruluk sertifikası değildir. Kartlar on yeni tam metin değildir; daha önce incelenmiş kararların yapılandırılmış özetleridir. Asıl metni okumadan dilekçeye birebir alıntı taşıma.

```sh
python scripts/quality.py cards
python scripts/quality.py cards "2025/3540"
```

Yeni kartta aynı alanları doldur; çoğunluk ile karşıoyu, bozma ile esas kabulünü birleştirme. Kartın senaryo bağlantısı o kararı bütün o olaylara doğrudan uygulama izni değildir. Somut olgu farklarını ve sonraki içtihadı yeniden araştır.

## Sınama akışı

1. [Senaryo setini](../evals/cases.json) doğrula. Setin sürümü ve içerik hash'i değerlendirmeye bağlanır.
2. Cevap üretecek oturuma yalnız `export` çıktısını ve skill kaynaklarını ver. Ölçüt dosyasını/`case` çıktısını cevap üretmeden önce okutma. Açık repo içindeki set gerçek gizli sınav değildir; bu yöntem yalnız doğrudan cevap anahtarı sızıntısını azaltır.
3. Her yanıtı değiştirmeden kaydet. Model/sürüm, tarih, kullanılan skill commit'i ve araç erişimini `run` açıklamasına yaz. Gerekirse her soruyu ayrı bağlamda çalıştır.
4. `review-template` ile inceleme taslağı çıkar. İnceleyici her ölçütte `met` alanını gerçek JSON boolean olarak işaretler; kısa gerekçe ve olumlu değerlendirmede yanıt içinden birebir kanıt girer. Eksik hususta olumsuz işaret ve neden gerekir. Sırf sorunun sözcüklerini tekrar etmek karşılanma sayılmaz. Zaten verilmiş bilgiyi tekrar sormak da soru ölçütünü karşılamaz.
5. `score` ile kapsamı, eksikleri ve kritik hataları raporla. Aynı set ve araç koşullarında önceki sürümle karşılaştır; mümkünse yanıt üreticisinden farklı bir hukukçu incelesin.

```sh
python scripts/quality.py validate
python scripts/quality.py --output research-private/prompts.json export
python scripts/quality.py case B06
python scripts/quality.py --output research-private/review.json review-template research-private/answers.json
python scripts/quality.py score research-private/review.json
```

Çıktı yolu mevcutsa araç üzerine yazmaz; yeni dosya adı seç. `research-private` yoksa önce oluştur. `case` yalnız inceleyici içindir.

`answers.json` biçimi (aşağıdaki yer tutucular gerçek sonuç değildir):

```json
{
  "suite_hash": "export çıktısındaki suite_hash",
  "run": "model, tarih, skill commit, araçlar",
  "answers": [{"id": "B06", "response": "Değiştirilmemiş gerçek yanıt"}]
}
```

İnceleme dosyasında `reviewer` ve `reviewed_on` doldurulur. Yanıt hash'i değişirse veya ölçütler güncellenirse yeniden inceleme gerekir. İfadelerin hukuki doğruluğunu Python ölçmez; alıntı eşleşmesi yalnız değerlendirme izini denetler. İnceleyicinin yanlış işaretlemesi otomatik saptanamaz.

## Ölçümün anlamı

Her dosyada hukuki ayrım (`analysis`), gerekli soru/belge (`questions`) ve yanlış genellemeden kaçınma (`avoid`) değerlendirilir. Bir dosya üçü de karşılandığında geçer. Hukuki ayrım ve yanlış sonuç ölçütündeki başarısızlık ayrıca kritik hata sayılır; yüksek toplam puan bunu gizlemez. Yalnız incelenen örneklerdeki oran, bütün set başarısı değildir; eksik dosya varken `suite_passed` false kalır. Henüz bu 49 soruyla canlı model performansı ölçülmedi. B46–B49 Legaluga entegrasyonundaki hata türlerini sınar; araç çıktısı soruda verildiği için canlı bağlantı gerektirmez. Bunlarda `run` açıklamasına Legaluga erişimini de yaz.

Yeni eklenen kaynakların konu/kapsam kontrolü [eğitim materyali kaydındadır](egitim-materyalleri.md). Ham eğitim metinleri ve gerçek dosya yanıtlarını kamuya açık depoya ekleme; yalnız anonimleştirilmiş ve paylaşılması uygun değerlendirmeleri ayrıca seç.
