# Kiracı sorunları: kurgu senaryolar ve gerçek emsaller

20.09.2026. Aşağıdaki olaylar araştırma ve skill denemesi için **üretilmiş kurgulardır**; kararların olay özeti veya gerçek müvekkil dosyası değildir. Her örnekte gerçek emsalin olguları ve sonucu ayrıca gösterilir. Güncel mevzuat ve karşı içtihat somut dosyada yeniden araştırılır.

## Sorundan belge ve emsale erişim

[On senaryoluk katalog](kiraci-senaryolari.json) her sorun için gerekli belgeleri, belirleyici soruları, dış araştırma sorgularını, gerçek karar kimliklerini ve karşı olguları içerir. Aşağıdaki dört ayrıntılı örneğe ek olarak K5 taahhüt, K6 depozito/tadilat, K7 emsal raporu, K8 yeni malik/yeni sözleşme, K9 ödeme hesabı ve K10 ihtiyaç nedeniyle tahliyeyi kapsar. Yeni altı senaryo mevcut havuzdaki kararları kullanır; yeni karar eklendiği anlamına gelmez.

```sh
python scripts/scenarios.py list
python scripts/scenarios.py search "rutubet depozito"
python scripts/scenarios.py show K6
```

Komut başka çalışma dizininden de betiğin mutlak yolu ile kullanılabilir; API anahtarı gerekmez. `search` sözcük eşleştirmesidir: ayrı sorunları kaybetmemek için sözcüklerden herhangi birini içeren senaryoları döndürür. Sıralama hukuki önem veya başarı ihtimali değildir. Boş sonuç, hukuki çözüm veya emsal bulunmadığı anlamına gelmez; ek sorguları bağlı kaynaklarda araştır. `search` yalnız kimlik, başlık, modül, kapsam, eşleşen sözcükler ve karar kimliklerini verir; belgeler, belirleyici sorular, karşı olgular ve çözülmüş kaynak kayıtları için `python scripts/scenarios.py show <kimlik>` kullan. "kira" gibi genel sözcükler bütün senaryolarla eşleşir; sorunu belirleyen sözcüklerle ara.

`show` çıktısındaki `decisions` gerçek havuz kayıtlarından çözülür; metin ve dosya (manifest) hash'leri kontrol edilir. Kaynak kaydı eksik veya bozuksa komut hata verir. `coverage` emsalin hangi meseleyi çözdüğünü ve nerede ek araştırma gerektiğini gösterir. Kaynakların `research_notes` sınırlarını oku; tam metin için `python scripts/pool.py get <kimlik>`, birebir alıntı denetimi için `python scripts/pool.py quote <kimlik> "<alıntı>"` kullan.

## Somut dosyaya uygulama

Tarih veya süre hesabı gereken senaryolarda [süre formüllerini](sure-hesaplama.md) kullan; araç bir takvim adayı üretir, eksik hukuki koşulları tamamlamaz.

1. Uyan senaryoları seç; karma uyuşmazlıkta birden çok senaryoyu koru. Kurgudaki tarihleri, ödemeleri ve iddiaları kullanıcının dosyasına taşıma.
2. `documents` listesini dosyayla karşılaştır. Yalnız sonucu etkileyen eksikleri sor; eldeki belgeleri yeniden isteme. `decisive_questions` sonuç üzerinde etkili ayrımları gösterir.
3. Gerekirse `olay | tarih/saat | belge/sayfa | kimin iddiası | belirsizlik` çizelgesi kur. İhtarda düzenleme, tebliğ ve öğrenme tarihlerini; ödemede işlem ve hesaba geçme kayıtlarını karıştırma. Kaynak ve uygulanacak kural doğrulanmadan otomatik son gün hesaplama.
4. Emsalin gerekçesi ve hükmünü dosyayla karşılaştır; `counterfacts` farklı sonucu araştırma başlangıcıdır, kesin ispat veya kabul değildir. Katalogdaki karar tek yönlüyse karşı yöndeki içtihadı dış araştırmada ara. Yalnız usulü çözen kararla alacağın esasını kabul etme.
5. Yanıtı ihtiyaca göre `sorun → belgedeki olgu → uygun emsal ve farkı → eksik delil → sonraki somut adım` bağlantısıyla yaz. Kısa soru için tüm katalog veya belge listesini dökme. İcra/tebliğ gibi devam eden süreç varsa ilgili tarih ve evrakın kontrolünü önceliklendir; doğrulanmamış süreyi kesin tarih olarak bildirme.

## K1 — İşyerinden çıkınca kalan bütün kiralar istendi

**Kurgu:** Beş yıllık işyeri sözleşmesinin üçüncü yılından sonra başka şehre taşınacak kiracı, sözleşmedeki altı ay önceden bildirim hakkını kullanıyor. Bildirim süresi kiralarını ödüyor ve imzalı anahtar teslim tutanağı alıyor. Kiraya veren yine de yıllık kiranın tamamını takibe koyuyor.

**İnceleme:** Özel çıkış hükmünün tam metni, bildirimin ulaşma tarihi, ödeme/iade/tevdi belgeleri ve anahtar teslimi. Gerçek erken tahliye ile sözleşmesel çıkış hakkının kullanımını ayır. Gerçek erken tahliyede sorumluluk TBK 325'e göre ayrıca incelenir. Sırf taşınmak veya anahtarı kiraya verenin yetkilendirmediği bir emlakçıya, kapıcıya ya da komşuya bırakmak kural olarak kiraya verene teslim sayılmaz. Anahtarı alan kişinin kiraya veren adına teslim almaya yetkili olduğunu veya kiraya verenin bildirilen teslim tarihine itiraz etmediğini gösteren belge ara. Yargıtay 3. HD, E. 2017/13231, K. 2019/1657 kararında anahtarın güvenlik görevlisine bırakılması, ihtarla bildirilen tarihe kiraya veren karşı çıkmadığı için o somut olayda tahliye tarihi kabul edilmiştir; bunu genel kural yapma. Kiraya veren anahtarı almaktan kaçınıyorsa TBK 106–107 uyarınca ifa yerindeki sulh hukuk hâkiminden tevdi yeri belirlenmesini değerlendir; noter aracılığıyla bırakma ve bildirimin teslim tarihine etkisini güncel içtihatla ayrıca araştır.

**Gerçek emsal:** Adana BAM 5. HD, E. 2022/1189, K. 2024/1605, 14.11.2024. Sözleşmedeki hakkını bildirimle kullanan, altı aylık ödemeyi tevdi eden ve anahtar teslimini belgeleyen kiracının menfi tespit talebi kabul edilmiş; kiraya verenin istinafı reddedilmiştir. BAM olayın erken tahliye olmadığını belirtir. Aynı takipte açılan itirazın kaldırılması davasında, Adana BAM 10. HD kararıyla kesinleşen sonuçla kiracının itirazı 75.005,98 TL asıl alacak yönünden kaldırılmış, fazlası reddedilmiştir; 5. HD menfi tespit kabulünü buna rağmen korumuş, iki karar arasındaki ilişkiyi tartışmamıştır. [Kaynak](https://app.dejure.ai/dokuman/7ad0f708-0612-47c9-956d-f722f4fe55fe).

**Kiracı lehine kullanım:** Bildirim ve ödeme belgeleriyle sözleşmesel hakkın yerine getirildiğini tartışmak. **Sınır/karşı olgu:** Bildirim şartına uyulmaması veya teslimin ispatlanamaması sonucu değiştirir. Sözleşmeden aktarılan üç yıllık makul süreyi veya altı aylık tazminatı kanuni kural sayma. Kiracı icra hukuk aşamasını kısmen kaybetmiştir; bu kararı, itirazın kaldırılması kararının menfi tespit davasına etkisi hakkında genel kural gibi sunma. Takip dosyasının güncel durumunu, tahsilat ve mahsubu ayrıca incele.

## K2 — Rutubet var; kiracı kirayı kendiliğinden yarıya indirmek istiyor

**Kurgu:** Depo olarak kiralanan işyerinde su sızıntısı mallara zarar veriyor. Kiracı altı ay önce başlayan sorun için yeni ihtar gönderiyor ve geçmiş dönem dahil süresiz %50 indirim istiyor. İki uzman raporu zararı farklı hesaplıyor.

**İnceleme:** Sözleşmedeki kullanım amacı, ayıbın kaynağı, fotoğraf ve tespit raporları, kiraya verenin öğrendiği tarih, onarım ve giderilme tarihi, kiracının olası kusuru. Kiracının tek taraflı indirim yapmasını kesin hak gibi önermeden ödeme/temerrüt riskini değerlendir.

**Gerçek emsal:** İstanbul BAM 35. HD, E. 2017/1243, K. 2017/1468, 11.10.2017. Daire ve E./K. numaraları karar metninde yer almaz; künye Dejure üst verisidir, dilekçede kullanmadan önce doğrula. Su ve rutubet nedeniyle indirim davasında, 40.000 TL ve 200.000 TL tespitler arasındaki çelişki, öğrenme tarihi ve indirim süresi incelenmeden verilen karar kaldırılmıştır. [Kaynak](https://app.dejure.ai/dokuman/eb8af224-a46c-4101-867f-2d58b76a0aef).

**Kiracı lehine kullanım:** Ayıbın kullanıma etkisini ve gerekli teknik incelemeyi göstermek. **Sınır/karşı olgu:** Karar kiracının istediği oranı onaylamaz; geçmişe ve sözleşmenin tamamına yayılan indirimi eleştirir. Kaynaktaki TBK 350 atfı, aynı gerekçedeki TBK 307 anlatımıyla tutarsızdır; yanlış madde numarasını tekrarlama. İşyeri kararı konuta koşulsuz taşınmaz.

**Gerçek emsal — kiracı aleyhine:** Yargıtay 3. HD, E. 2023/2841, K. 2024/1036, 06.03.2024. Depo olarak kiralanan işyerindeki önemli ayıplar nedeniyle sözleşmeyi feshedip taşınan kiracının feshi haklı sayılmamıştır: ihtarnamelerde ayıpların giderilmesi için süre verilmemiş, bildirilen fesih tarihlerinde tahliye de yapılmamıştır. İlk derece ve BAM'ın haklı fesih kabulü kaldırılmış; kiracının anahtar teslimine kadar kira ve TBK 325 makul süre kirasından sorumluluğunun belirlenmesi için bozma kararı verilmiştir. [Kaynak](https://app.dejure.ai/dokuman/e5c8048b-4685-4456-8ad1-39133abef50f).

**Talepleri ayır:** TBK 306: kiraya verenden ayıbın uygun sürede giderilmesini isteme; süresinde giderilmezse kiraya veren hesabına gidertip doğan alacağı kiradan indirme; kullanıma elverişliliği ortadan kaldıran veya önemli ölçüde engelleyen ayıp verilen sürede giderilmezse fesih. TBK 307: kira indirimi yalnız ayıbın kiraya verence öğrenilmesinden giderilmesine kadar geçen süre için istenir. TBK 308: mallardaki zarar ayrı tazminat kalemidir; kiraya veren kusursuzluğunu ispat etmedikçe sorumludur. BAM kararındaki “öncelikle giderim talep yükümlülüğü” anlatımını TBK 307 indirimi için genel ön koşul gibi sunma. İndirimi tek taraflı eksik ödemeyle uygulamanın temerrüt/tahliye riskini; feshe yönelen kiracıda önceden süre verme ile fiilî tahliye ve anahtar teslimi koşullarını ayrıca değerlendir.

## K3 — “İhtarı aldığım gün ödedim; iki ihtar oluşmaz” savunması

**Kurgu:** Kiracı aynı kira yılı içinde iki ödeme emrine itiraz ediyor, ardından aynı gün bankadan ödeme yapıyor. Tahliye davası sırasında taşınıyor ve artık yargılama gideri ödemeyeceğini düşünüyor.

**İnceleme:** Her kira ayı için muacceliyet, tebliğ/öğrenme, itiraz ve ödeme tarih-saat çizelgesi. Temerrüt nedeniyle tahliye (TBK 315) ile iki haklı ihtarı (TBK 352/2) ayır. TBK 352/2 dava süresini kontrol et: kira süresinin, bir yıldan uzun süreli kiralarda ihtarların yapıldığı kira yılının bitiminden başlayarak bir ay; ikinci ihtarın tarihine bir ay eklenmez ([süre formülü](sure-hesaplama.md)). Dava 01.09.2023 veya sonrasında açılmışsa arabuluculuk dava şartını ve başvurunun süreye etkisini ayrıca incele. Kiralanan dava sırasında boşaltılıp dava konusuz kalırsa yargılama giderleri ve vekâlet ücreti HMK 331/1 uyarınca davanın açıldığı tarihteki haklılık durumuna göre belirlenir; taşınmak giderleri kendiliğinden kaldırmaz. Bu nedenle iki haklı ihtar koşullarının ve dava süresinin dava tarihi itibarıyla gerçekleşip gerçekleşmediğini incele.

**Gerçek emsal — kiracı aleyhine:** İstanbul BAM 36. HD, E. 2019/3134, K. 2021/1779, 22.09.2021. İtirazlar 11:36 ve 10:39'da, ilgili ödemeler aynı gün 13:19 ve 11:35'te yapılmıştır. BAM iki haklı ihtarı kabul etmiş; taşınmayla konusuz kalan davada giderleri ve vekalet ücretini kiracıya yüklemiştir. [Kaynak](https://app.dejure.ai/dokuman/fa461f44-de8b-43e1-aaa4-60c85a683530).

**Sınır/karşı olgu:** Ödemenin tebliğ/öğrenmeden önce yapıldığı, ihtarın muaccel borca dayanmadığı veya dönemlerin farklı olduğu dosya ayrıca değerlendirilir. Usulsüz tebligatta öğrenme sonucu somut olayın itiraz kayıtlarına dayanır. Bu karar kiracı zaten çıktığı için yeni tahliye hükmü kurmamıştır. Dava, TBK 352/2'deki bir aylık süre geçtikten sonra açılmışsa veya dava tarihinde ikinci haklı ihtar henüz oluşmamışsa, konusuzlukta giderlerin kiraya verene yüklenmesi araştırılır. BAM kararı bir aylık dava süresini ayrıca tartışmamış, HMK 331'i madde numarasıyla anmamıştır; giderleri dava tarihindeki haklılığa göre yüklemiştir.

## K4 — Çıkışta bütün yenileme masrafı kiracıya yüklendi

**Kurgu:** Dört yıl kullanılan işyerinden çıkan kiracıdan boya, elektrik ve sökülen malzemeler için yeni ürün fiyatlarıyla tazminat isteniyor. Kiracı bazı malzemeleri kendisinin taktığını, diğer izlerin normal kullanım olduğunu savunuyor. Kiraya veren yalnız delil tespiti raporuna dayanıyor.

**İnceleme:** İlk teslim fotoğrafları, demirbaş listesi, tadilat izinleri, faturalar, son teslim tutanağı, ayıp bildirimi ve bilirkişi itirazları. Her kalemde olağan yıpranma/hor kullanım ayrımı, tahliye tarihindeki bedel ve amortisman ele alınmalı. Depozito kesintisi ileri sürülüyorsa mahsup koşulları ayrıca incelenmeli. Kiraya verenin TBK 335 uyarınca geri vermede hemen yazılı bildirim yapıp yapmadığı ayrıca sorulmalı: bildirim yoksa veya gecikmişse görülebilir hasarlar yönünden kiracı her türlü sorumluluktan kurtulma savunmasını ileri sürebilir. Delil tespiti talebinin veya raporunun bildirim yerine geçip geçmediğini kendiliğinden kabul ya da ret etme; tahliye tarihi, tespit tarihi, raporun kiracıya tebliğ tarihi, içeriğin somutluğu ve hasarın olağan incelemeyle görülebilir olup olmadığı birlikte değerlendirilmeli.

**Gerçek emsal:** İstanbul BAM 55. HD, E. 2023/2395, K. 2024/2656, 06.11.2024. Hasar talebinin kabulü kaldırılmış; keşif, hasar kalemleri ve yıpranma/yenileme payı değerlendirmesi için dosya iade edilmiştir. [Kaynak](https://app.dejure.ai/dokuman/880b0d47-5ca8-4e1a-9fab-41b5da8f1992).

**Kiracı lehine kullanım:** Toplu yenileme faturası yerine somut hasar incelemesi istemek. **Sınır/karşı olgu:** Karar kiracıyı tamamen borçsuz saymaz; kendi taktırdığı malzemeleri söktüğü savunmasını da kesin olgu olarak kabul etmez. Karar depozito iadesi değil hasar tazminatıdır. Kararda TBK 335 metni aktarılmış, ancak bildirim yokluğu nedeniyle sorumluluktan kurtulma tartışılmamıştır (istinaf sebepleri arasında yoktur; tespit raporu kiracıya 30.03.2022'de tebliğ edilmiştir). Kararı bu savunmanın kabulü veya reddi gibi sunma.

## Skill denemesinde beklenen davranış

- Katalogdaki modüller: K1 `alacak` + `sozlesme` (Alacak ve icra; Sözleşme ve kullanım); K2 `guvence` (Güvence ve masraf: ayıp ve kira indirimi); K3 `tahliye` + `alacak` (Tahliye; Alacak ve icra; yargılama giderleri ayrıca değerlendirilir); K4 `guvence` (Güvence ve masraf: hasar ve olağan yıpranma). Model puanı düşük çıksa da bu modüller silinmez.
- Kurguyu kararın olayıymış gibi anlatma. Gerçek emsalin sonucunu “kabul”, “ret”, “kaldırma/iade” ve “konusuzluk” ayrımıyla yaz.
- Lehe örneği kesin kazanma, aleyhe örneği savunmanın her durumda imkânsızlığı olarak sunma.
- İlgili kararı `python scripts/pool.py get <kimlik>` ile oku; birebir alıntıyı `python scripts/pool.py quote <kimlik> "<alıntı>"` ile denetle. Anonimleştirme alanı varsa yerel alıntının kaynak kopyasından farkını koru.

**Seçilmeyen aday:** Bursa BAM 4. HD E. 2024/3141, K. 2026/302 metninde 23.05.2024 ilk derece kararına rağmen 25.08.2024 dava tarihi anlatılıyor. Tarih çelişkisi nedeniyle senaryo emsali olarak eklenmedi; kararın yokluğu veya sonucu hakkında başka çıkarım yapılmadı.
