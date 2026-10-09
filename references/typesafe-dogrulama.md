# TypeSafe doğrulama kaydı

20.09.2026; canlı API'nin bildirdiği model: `jev-1.13.0`. Küçük örnek kümesiyle entegrasyon ve davranış kontrolüdür; Türk kira hukukunda doğruluk oranı veya karşılaştırmalı başarı çalışması değildir.

## Gözlemler ve düzeltme

İlk canlı denemede altıncı yıl kira tespiti talebine uyarlama sinyali 0,88; boş imza/aile konutu savunmasına parasal güvence sinyali 0,67 döndü. Tanımlar somut kapsam ve dışlamalarla netleştirildi. Sonraki çağrıda aynı iki talepte bu sinyaller sırasıyla 0,15 ve 0,18 oldu; tespit 0,90, tahliye 0,76 kaldı. Bunlar tekil model yanıtlarıdır, genel hata oranı değildir.

Depozito, hasar ve ödenmeyen kira içeren karma örnekte güvence 0,94 ve alacak 0,85 çıktı. Kira ilişkisi bulunmadığı açıkça belirtilen fazla mesai örneğinde kapsam dışı sinyali 0,86 oldu. Bu iki örnek tanım düzeltmesinden önce çalıştırıldı; güncel sürüm için geniş regresyon değerlendirmesi yerine geçmez.

Tam metni okunmuş İstanbul BAM 36. HD E. 2024/5083, K. 2026/377 ile ilgisiz temsili ceza pasajı birlikte verildiğinde, ilgili karar 0,90; ilgisiz pasaj 0,02 sıralama sinyali aldı. Kaynak kimliği korundu ve eksik pasaj tam metin olarak işaretlenmedi. Bu deneme hukuki yorumun doğrulandığı anlamına gelmez. Karar bağlantısı [modül rehberindedir](moduller.md).

## Erişim durumu

- DeJure üzerinden arama ve tam metin alma çalıştı.
- Bağlı içtihat aracı üzerinden depozito kararı arandı ve tam metni alındı.
- Legaluga MCP arama ve karar getirme çağrıları hata verdi. Yerel köprü üzerinden yapılan denemede sunucu HTTP 500 döndürdü. Bu çalışmada Legaluga havuzundan başarılı veri alındığı veya 9 milyon kayıt sayısının doğrulandığı iddia edilmez. Skill, erişim yeniden sağlandığında kaynak kimliklerini koruyarak bu araçları kullanabilir.

API anahtarı kullanıcı tarafından belirtilen yerel env dosyasından okundu; anahtar ve özel env yolu public dosyalara eklenmedi. Canlı isteklerde müvekkil belgesi kullanılmadı.

## Yerel kontroller

`python -m unittest discover -s tests -v`: kaynak kimliklerinin korunması, sıralamada düşük puanlı adayların kaybolmaması, eksik yanıt ve geçersiz olasılıkların reddi, yinelenen kaynak ve belirsiz tam metin durumunun reddi.

`python scripts/validate.py`: 1.580 mevcut kararın ve mevzuatın bütünlüğü, yerel bağlantılar ve yardımcı komutlar. Skill şema kontrolü ayrıca çalıştırılır. Bu denetimler canlı servislerin her zaman erişilebilirliğini veya hukuki sonuçların doğruluğunu garanti etmez.

## 20.09.2026 — ek karar elemesi

Legaluga arama aracı hata verdi; aynı yetkili API yoluyla doğrudan denemede HTTP 500 alındı. Bu turda büyük Legaluga havuzundan kayıt alınmadı. Alternatif DeJure kaynağından uyarlama, alt kira ve zamanaşımı için 9 aday toplandı. Güncel TypeSafe doküman uçlarına erişilemedi; mevcut entegrasyon ve daha önce okunmuş API belgeleri kullanıldı.

Canlı TypeSafe çağrısı `jev-1.13.0` döndürdü: 10.061 girdi ve 487 çıktı tokenı. Adayların hiçbiri puan eşiğiyle otomatik elenmedi. İlk iki sıradaki kararlar dahil 5 tam metin okundu: 3 yeni karar eklendi; E.2014/7121 K.2014/8734 mevcut havuzla mükerrerdi. E.2017/4223 K.2019/175 hedeflenen zamanaşımı süresini esastan çözmediği ve ret gerekçelerinin birlikte kullanılması nedeniyle bozma içerdiği için seçilmedi. Kalan 4 adayın tam metni bu turda incelenmedi.

Eklenenler: E.2024/2523 K.2025/1572 (uyarlamanın reddi); E.2018/2258 K.2018/6300 (alt kira ve yazılı muvafakat araştırması); E.2014/10567 K.2015/10451 (hasılat kirasında alacak türü/ıslah/zamanaşımı). Kaynaklar ve sınırlar [Yargıtay seçkisinde](yargitay-kararlari.md). Ham araştırma ve API dosyaları public pakete eklenmedi. Bu çalışma 9 milyon kaydın taranması veya model puanlarının hukuken doğrulanması değildir.

## 09.10.2026 — Legaluga erişimi

Legaluga MCP bu tarihte çalıştı; 20.09.2026 kaydındaki HTTP 500 durumu tarihî kayıt olarak korunur. Salt okuma sınamaları:

- `karar_getir` ana havuzdaki 1205946900 kimliğiyle aynı Yargıtay 3. HD, E. 2025/2321, K. 2025/5468 kararını döndürdü. Metinler yalnız boşluk ve satır sonlarında ayrıştı; bu nedenle `pool.py quote --ignore-space` eklendi.
- `kunye_dogrula` ana havuzdaki iki Yargıtay künyesi için `tarih_tuttu`, İstanbul BAM 55. HD E. 2024/3413, K. 2026/257 için `denetlenemedi` döndürdü (BAM kapsamı yetersiz). Bunlar parmak izi ön denetimidir; kararların varlığı tam metinden ayrıca doğrulanır.
- `mevzuat_madde_getir` TBK 344 için paketteki kopyayla aynı lafzı ve 7161 ile 6217 dipnotlarını verdi; TBK geçici 1–2 647. maddenin `ek_hukumler` alanında geldi.
- `udf_dilekce_olustur` kurgu bir girdiyle imzasız UDF döndürdü; `scripts/udf.py kaydet` SHA-256 ve zip denetimini geçti. Gerçek müvekkil verisi gönderilmedi.

Bu sınamalar entegrasyon davranışını gösterir; Legaluga havuzunun kapsamı, güncelliği veya hukuki sonuçların doğruluğu hakkında ölçüm değildir. Kullanım kuralları [Legaluga akışındadır](legaluga.md).
