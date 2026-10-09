# Çalışma mantığı ve dosya akışı

## 1. İstenen işi seç

| İstek | Yapılacak çalışma | Çıktı |
| --- | --- | --- |
| Belirli hukuki soru | İlgili olgu, madde ve kararları incele | Kısa cevap, dayanak, belirleyici belirsizlik |
| Dosya değerlendirmesi | Belgeleri ve zaman çizelgesini kur; lehe/aleyhe dayanakları karşılaştır | Gerekçeli değerlendirme ve delil ihtiyaçları |
| Dava dilekçesi | Talebi, dayanak vakıaları, delilleri ve istenen dönemi eşleştir | Somut dosyaya uyarlanmış taslak |
| Cevap dilekçesi | Dava dilekçesindeki iddiaları ve talepleri ayrı ayrı karşıla | Usul/esas savunmaları ve karşı deliller |
| Bilirkişi raporuna itiraz | Raporun verilerini, yöntemini ve dosyadaki karşılıklarını incele | Raporun ilgili bölümüne bağlı somut itirazlar |
| Yeni belge veya düzeltme | Önceki değerlendirmede hangi olgu ve sonuçların değiştiğini belirle | Etkilenen kısımların güncellenmesi |

Kullanıcının istemediği ayrı bir dilekçe veya hukuki işlem üretme. Kısa bir soruyu tam dosya kabulüne dönüştürme.

## 2. Olguları ve zaman çizelgesini kur

Eksik bilgi için [soru akışındaki](soru-akisi.md) ilgili başlığı kullan. İlk turda sonucu etkileyen en fazla 3–5 kısa soru seç; mevcut belgelerde cevaplananları çıkar. Yeni cevap geldikçe yalnız etkilenen meseleleri ve kalan belirleyici eksikleri ele al.

Her belirleyici bilgiyi şu ayrımla ele al: **belgede görülen**, **kullanıcının beyanı**, **karşı tarafın iddiası**, **henüz bilinmeyen**. Belgede yazması, çekişmeli bir iddianın ispatlandığı anlamına gelmez. Çelişen tarih veya bedelleri sessizce birleştirme.

İhtiyaç varsa kısa bir çalışma tablosu tut: `olgu | değer/tarih | belge ve sayfa | çekişme/eksik`. Sözleşme başlangıcı, hedef kira dönemi, ihtar-tebliğ, arabuluculuk ve dava tarihlerini birbirinden ayrı yerleştir. Aylık/yıllık ve net/brüt bedelleri aynı temele getirmeden karşılaştırma.

Sonucu etkileyen bilgi yoksa onu sor; yanıt gelene kadar bağımsız kaynak araştırmasını sürdürebilirsin. Varsayımsal hesapta varsayımı açıkça yaz ve gerçek dosya olgusu gibi taslağa aktarma.

Süre hesabında [formül rehberini](sure-hesaplama.md) kullan. Başlangıç olayı ile belge tarihini, ham takvim sonucu ile hukuken uygulanacak son günü ayrı kaydet; hesap aracının yapmadığı tatil ve arabuluculuk düzeltmelerini uygulanmış gibi gösterme.

## 3. Dosyayı araştırılabilir meselelere ayır

Somut ihtiyaca göre aşağıdaki araştırma alanlarından ilgili olanları seç; bu liste hukuki sonuç veya otomatik uygulanacak kural değildir:

- Talebin kira tespiti niteliği, kira türü ve taraf sıfatları.
- Görev, yetki, dava şartları ve arabuluculuk belgeleri.
- Sözleşme süresi, yenilemeler, artış şartı ve TBK 344 kapsamında incelenecek dönem.
- Hedef döneme etki, dava/ihtar/tebliğ tarihleri ve TBK 345 bağlantısı.
- Emsal kiralar, kiralananın özellikleri, bilirkişi yöntemi ve eski kiracı değerlendirmesi.
- Talep sonucu, bedelin niteliği, talep değişiklikleri, önceki kararlar ve varsa kanun yolu aşaması.

Her mesele için önce hangi olgunun sonucu değiştirdiğini belirle. Bir dosyada gündeme gelmeyen bütün usul ihtimallerini sıralama.

## 4. Kaynağı bul, sonra doğrula

Skill kökünde `python scripts/pool.py stats` ve `python scripts/tbk.py` ile paket erişimini kontrol et. Komutları başka dizinden çalıştırıyorsan betiklerin mutlak yolunu kullan. Karar aramasının sözcük eşleştirmesi yaptığını, anlamsal arama veya hukukî ağırlık ölçümü olmadığını dikkate al.

Örneğin hedef döneme etki araştırmasında önce `python scripts/tbk.py 345` ile maddeyi oku; ardından `python scripts/pool.py search ihtar --limit 8`, `search "artış şartı" --limit 8` gibi ayrı sorgular kur. Esas gerekçesi filtresini gerektiğinde kullan; sonuç azsa filtresiz de ara. Adayın `document_id` değerini `get` komutuna vererek tam metni oku; kullanacağın birebir alıntıyı `quote` ile kontrol et. Komut ayrıntıları [havuz rehberindedir](havuz.md).

Yerel kanun ve kararlar ilk araştırma kaynağıdır. Uygulanacak tarihteki hükmü ve sonraki değişiklikleri çevrimiçi doğrula. Bağlı mevzuat araçları kullanılabiliyorsa önce araç yönergelerini uygula; mevzuatı resmî numarasıyla bul, dönen kimlikle ilgili maddeyi getir. Yerel karar yetersizse odaklı dış araştırma yap ve dışarıdan bulunan kararı paket havuzundan gelenlerden ayır. Dış kaynağı kullanmak paketi otomatik değiştirmez. Legaluga MCP bağlıysa sıra şudur: paketteki madde ve kararlar → `mevzuat_madde_getir` ile güncel metin, değişiklik ve geçiş notları → `semantik_ictihat_ara` ve ayrı `karar_ara` sorguları → `karar_getir` ile tam metin. Araç kuralları ve uyarıların anlamı [Legaluga akışındadır](legaluga.md).

Aramada eşanlamlı ifadeyi veya daha kısa terimi denemek, ilk sonuç sayfasında bulamamaktan daha güçlü bir araştırmadır. Yine de boş sonuçtan “böyle bir içtihat yok” sonucu çıkarma. Karar sayısını doldurmak için ilgisiz emsal ekleme.

## 5. Kanun, karar ve olgu arasında bağ kur

Her belirleyici meselede şu zinciri görünür ve kısa biçimde kur:

**Dosyadaki olgu → ilgili tarihteki düzenleme → kararın kendi gerekçesi → olgusal benzerlik/fark → somut dosyaya ilişkin sonuç.**

Kararı okurken kimin görüşünün aktarıldığını ve nihai sonucu belirle. Bozulan yerel mahkeme gerekçesini yüksek mahkemenin kabulü gibi kullanma. Lehe kararla birlikte karşı görüşü veya uygulanmasını zayıflatan farklı olguyu da araştır. Yeni tarihli olması tek başına kararı üstün veya uygulanabilir yapmaz; daire, kurul, uyuşmazlık, düzenleme dönemi ve usul aşamasını birlikte değerlendir. Çelişki çözülmüyorsa bunu belirt, tek çizgi varmış gibi yazma.

Çalışma notu gerektiğinde `mesele | olgu kaynağı | madde ve sürüm | karar künyesi/kimliği | kaynak (yerel/Bedesten/Core) | doğrulanmış pasaj ve doğrulama durumu | benzerlik/fark | sonuç/eksik` alanlarını kullan. Kullanıcıya yalnız kararını değerlendirmesine yardımcı olacak kısmını göster; iç muhakeme dökümü üretme.

## 6. İstenen ürüne dönüştür

Analizde önce sorunun cevabını ve onu değiştiren eksik bilgiyi ver; ardından gerekli dayanakları açıkla. Dilekçede doğrulanmış vakıalar, deliller, hukuki açıklamalar ve talep sonucu birbiriyle uyumlu olsun. Dava veya cevap yönüne göre anlatımı uyarla; aleyhe kaynağı araştırma notunda değerlendir, karşı tarafın iddiasını müvekkilin kabulü gibi yazma. Dilekçeden önce `iddia | kaynak | doğrulama durumu` tablosu kur; kaynağı olmayan hukuki cümleyi metne alma.

Belge eksikliği taslağı tamamen engellemiyorsa ilgili yere açıklayıcı doldurma alanı koy. Bir süre veya bedel doğrulanamıyorsa kesin tarih/tutar yazmak yerine gerekli girdiyi belirt. Başarı ihtimaline yapay yüzde verme. Hesap gerekiyorsa veri kaynağı, dönem, birim ve formülü göster.

## 7. Bitirme ve güncelleme ölçütü

Teslimden önce sonucu değiştiren olguların kaynağı, atıf yapılan kararların tam metni, alıntıların doğruluğu, madde/sürüm ilişkisi ve taslağın talep tutarlılığını kontrol et. Açık kalan noktaları kısa bir eksik bilgi listesiyle göster. Bu kontroller tamamlanıp önemli belirsizlikler açıklandığında araştırmayı sonlandır; aynı sonucu veren sorguları süresiz tekrarlama. UDF istenmişse yalnız onaylanmış ve yer tutucusuz son metni paketle; kaydedilen dosyanın adını, boyutunu ve SHA-256 değerini kaynak notuna yaz, dosyayı imzasız taslak olarak sun.

Yeni belge geldiğinde yalnız etkilenen meseleleri yeniden aç; önceki sonucun neden değiştiğini belirt. Paket güncellemesi ayrıca istenirse yeni kayıtları kimlik ve metin hash'iyle denetle, kaynak/alınma bilgisi ile manifesti güncelle ve yardımcıları doğrula. Normal dosya incelemesi sırasında paket kararlarını veya kanun metnini değiştirme.
