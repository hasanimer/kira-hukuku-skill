# Tahliye: sebepler, yollar ve süreler

İnceleme: 14.10.2026. Bu rehber konut ve çatılı işyeri kiralarında tahliye sebeplerini, bildirim ve süre koşullarını, dava ve ilamsız icra yollarını, dava şartı arabuluculuğu ve doğrulanmış yerel kararları sebep sebep toplar. Kaynaklar paketteki TBK kopyası (`python scripts/tbk.py <madde>`), yerel karar havuzu (`python scripts/pool.py get <id>`) ve havuzla doğrulanmış araştırma kartlarıdır; İİK, HMK, HUAK ve TMK metinleri pakette yoktur, bu kanunlara dayanan her cümleyi olay tarihindeki resmî güncel metinden doğrula. Süreler [süre rehberindeki](sure-hesaplama.md#takvim-işlemleri) `G(t,n)`, `A(t,n)`, `Y(t,n)` gösterimiyle yazılır; araç çıktıları ham takvim adayıdır, tatil, arabuluculuk durması ve TBK 353 uzaması ayrıca incelenir. Her sebebin rota kartı ve emsal listesi için `python scripts/tahliye.py yol <sebep>` ve `python scripts/tahliye.py emsal <sebep>` komutlarını kullan; sebep anahtarları: ortak_usul, temerrut, iki_hakli_ihtar, taahhut, ihtiyac, yeni_malik, on_yillik_uzama, akde_aykirilik, kiracinin_konutu_ve_diger, tahliye_sonrasi. Rehberi bütünüyle okuma: önce yol seçimi tablosunu, sonra yalnız ilgili sebebin bölümünü ve gerekirse ortak usulü aç.

## Yol seçimi tablosu

| Sebep | Kim ister | Ön koşul ve bildirim | Süre | Yol | Arabuluculuk | Araç |
| --- | --- | --- | --- | --- | --- | --- |
| [Ortak usul](#ortak-usul-arabuluculuk-görev-taraf-ve-tebligat) | Sözleşmedeki bütün kiraya verenler (malik olmayabilir); karşı taraf bütün kiracılar ve TMK 194/son bildirimi yapmış eş | Sebebin yazılı bildirimi; dava ≥ 01.09.2023 ise davadan önce arabuluculuk ve son tutanak; tam taraf teşkili; yıllık kira üzerinden harç | 350/1 başvurusu E < b ≤ A(E,1); 18/A/15 durması; son tutanak G(T,7); HMK 20/1 G(K,14); cevap ve kanun yolu G(T,14) | Sulh hukuk (HMK 4/1-a, basit yargılama); ilamsız tahliyede icra dairesi ve icra mahkemesi | Dava ≥ 01.09.2023: dava şartı; ilamsız icra yoluyla tahliye istisna; itirazın iptali ve tahliye tartışmalı | `python scripts/deadlines.py tbk350 <sure-sonu>`; `python scripts/deadlines.py uets <ulasma-tarihi>`; usul süreleri için `takvim` |
| [Temerrüt (TBK 315; İİK 269)](#temerrüt-tbk-315-ve-ilamsız-tahliye-takibi) | Kiraya veren (malik olması gerekmez); sözleşmedeki bütün kiraya verenler, bütün kiracılara ve taraf olmuş eşe karşı | Teslimden sonra muaccel kira veya yan gider; yazılı ihtar ya da 13 örnek: en az 30 (diğer 10, ürün 60) gün ve fesih uyarısı; sürede ödenmemesi | Tebliğ T → ödeme süresi G(T,30); 13 örnekte itiraz G(T,7); itiraz yoksa ödeme süresi sonu O → A(O,6); davada hak düşürücü süre yok | İlamsız tahliye takibi (13 örnek; icra mahkemesi) veya sulh hukukta fesih ve tahliye davası | İlamsız takip ve icra mahkemesi istisna; sulh hukuk davası dava şartı (dava ≥ 01.09.2023); itirazın iptali ve tahliye tartışmalı | `python scripts/deadlines.py tbk315 <teblig-tarihi>`; 13 örnek: `python scripts/deadlines.py iik269 <odeme-emri-teblig-tarihi>` |
| [İki haklı ihtar (TBK 352/2)](#kira-yılı-içinde-iki-haklı-ihtar-tbk-3522) | Kiraya veren (malik olması gerekmez); birden fazla kiraya veren birlikte; dava bütün kiracılara karşı | Aynı kira yılı veya kira süresi içinde, muaccel kira için ayrı ayrı iki yazılı ihtar; tebliğ anında kira ödenmemiş olmalı | Kira süresinin veya ihtarların yapıldığı kira yılının son günü E1 → en geç A(E1,1) (orta güven); bitimden önce açılan dava reddedilir | Yalnız sulh hukukta tahliye davası; ilamsız icra yolu yok | Dava şartı (dava ≥ 01.09.2023); başvuruyu kira yılı bittikten sonra ve bir ay içinde yap | `python scripts/deadlines.py takvim <kira-yili-son-gunu> --count 1 --unit ay` |
| [Tahliye taahhüdü (TBK 352/1)](#tahliye-taahhüdü-tbk-3521) | Yalnız kiraya veren (taahhüdün verildiği taraf); bütün kiraya verenler bütün kiracılara karşı | Teslimden sonra verilmiş yazılı, imzalı, belli tarihli taahhüt; ön ihtar gerekmez | Taahhüt edilen boşaltma tarihi B → bir ay: A(B,1) (hak düşürücü) | İİK 272 ilamsız takip (Örnek 14) veya sulh hukukta tahliye davası | Takipte istisna; doğrudan davada dava şartı; itirazın iptali davasında tartışmalı | `python scripts/deadlines.py tbk352 <bosaltma-tarihi>` |
| [Gereksinim ve yeniden inşa (TBK 350)](#gereksinim-ve-yeniden-inşa-tbk-350) | Kiraya veren (malik şart değil); kiraya veren olmayan malik de; ihtiyaçlı: kendisi, eşi, altsoy, üstsoy, bakmakla yükümlü olunan | Gerçek, samimi, zorunlu ve süren ihtiyaç; belirli sürelide ihtar şart değil, sözleşmesel ihbar kaydına ve belirsiz sürede TBK 328–329'a uy | Süre veya uzama yılı sonu E → bir ay: A(E,1) (temkinli A(G(E,-1),1)); TBK 353 bildirimiyle Y(E,1) | Yalnız sulh hukukta tahliye davası (ilamsız icra yok); 350/2 için aynı yol | Dava şartı (dava ≥ 01.09.2023); başvuru E'den sonra ve süre içinde (3. HD 2025/3048) | `python scripts/deadlines.py tbk350 <donem-sonu>` |
| [Yeni malik (TBK 351)](#yeni-malik-tbk-351) | Kiralananı sözleşmeden sonra edinen yeni malik (TBK 310); ihtiyaçlı: kendisi, eşi, altsoy, üstsoy, bakmakla yükümlü olunan | 351/1: edinmeden A(D,1) içinde tebliğ edilmiş yazılı bildirim (keşide yetmez); 351/2 ve 350: bildirim yok, sözleşmesel ihbar kaydına uy | 351/1: dava en erken G(A(D,6),1), dönem sonuna kadar (düşük güven); 351/2: dönem sonu L/N → G(N,1)–A(L,1) | Yalnız sulh hukukta tahliye davası (ilamsız icra yok); 351/1, 351/2 ve 350/1 terditli | Dava şartı (dava ≥ 01.09.2023); 351/1'de erken başvuru çözülmedi, G(A(D,6),1)'den sonra başvur | `python scripts/deadlines.py tbk351 <edinme-tarihi>` |
| [On yıllık uzama (TBK 347)](#on-yıllık-uzama-ve-belirsiz-süreli-kira-tbk-347) | Kiraya veren (malik şart değil); yeni malik TBK 310 ile; birden çok kiraya verende hepsi birlikte | Konut/çatılı işyeri; ilk süre + 10 uzama yılı (347/2: başlangıçtan on yıl); yazılı fesih bildirimi | F = Y(E,11); tebliğ Y(E,10) ile A(G(F,-1),-3) arasında; dava F günü veya sonrası; üst sınır kanunda yok | Sulh hukukta tahliye davası; İİK 272 ilamsız yolu 347 için doğrulanmadı | Dava şartı (dava ≥ 01.09.2023); başvuru F günü veya sonrasında (2025/3048 kıyası) | `python scripts/deadlines.py tbk347 <ilk-sure-bitimi>` |
| [Özen borcuna aykırılık (TBK 316)](#özen-ve-komşulara-saygı-borcuna-aykırılık-tbk-316) | Kiraya veren (malik şart değil); paylı mülkiyette pay ve paydaş çoğunluğu, elbirliğinde bütün ortaklar | Önemli, kullanımla ilgili aykırılık; konut/çatılı işyerinde en az 30 günlük yazılı giderim ihtarı ve süre sonunda devam | Giderim G(T,30) (T = tebliğ); en erken başvuru süre sonunun ertesi günü; kanuni dava süresi yok | Yalnız sulh hukukta tahliye davası; ilamsız icra yolu yok | Dava şartı (dava ≥ 01.09.2023), istisna yok; başvuruyu giderim süresi bittikten sonra yap | `python scripts/deadlines.py tbk316 <ihtar-teblig-tarihi>` |
| [Kiracının konutu (TBK 352/3), TBK 325 ve 331–333](#kiracının-konutu-tbk-3523-ve-diğer-sona-erme-halleri) | 352/3: kiraya veren; 331: iki taraf; 332: kiraya veren; 333: mirasçılar; kira yoksa malik veya paydaş | Kiracının veya eşinin aynı ilçede elverişli konutu ve kiraya verenin bilmemesi; ön ihtar yok | Sözleşme veya uzama yılı bitimi E → bir ay: A(E,1) (orta güven) | Yalnız sulh hukukta tahliye davası; ilamsız takip yok; kira yoksa asliyede el atma ve ecrimisil | Dava şartı (dava ≥ 01.09.2023); ilamsız istisna yok; el atma ve ecrimisil kira bendi dışında | `python scripts/deadlines.py takvim <sozlesme-sonu> --count 1 --unit ay` |
| [Tahliyeden sonra (icra, TBK 355)](#tahliye-kararından-sonra-icra-tehir-ve-tbk-355) | İcrayı lehine ilam bulunan kiraya veren ister; kiracı tehir, şikâyet, 355 tazminatı ve depozito iadesi ister | Eda hükümlü ilam veya şerhli ya da ortak imzalı anlaşma belgesi; 355 için gereksinim veya yeniden inşa boşaltması, üç yıl içinde başkasına kiralama | İcra emri T → G(T,7) (doğrula); istinaf G(T,14); boşaltma B → 355 yasağı Y(B,3); öncelik A(N,1); banka bildirimi A(S,3) | İlamlı icra (İİK 26) ve tehir (İİK 36); ilamsızda menfi tespit ve tedbir; 355, hasar, depozito için sulh hukuk davası | İcra takibi ve şikâyette yok (çıkarım); 355, depozito, hasar ve kira davasında dava ≥ 01.09.2023 ise dava şartı | `python scripts/deadlines.py takvim <bosaltma-tarihi> --count 3 --unit yil`; diğer süreler `takvim`; İİK 36 ve TBK 335 için araç yok |

Tablo yön bulmak içindir; koşulları, güven düzeyini ve emsalleri ilgili bölümden ve rota kartından oku. Güveni orta veya düşük süreleri kesin son gün gibi aktarma.

**Önce şunu belirle.**

- **Kira türü:** Kiralanan konut veya çatılı işyeri mi, ürün kirası, arsa veya açık alan mı? Karma kiralananda baskın vasfa bak. TBK 347 ve 350–352 yalnız konut ve çatılı işyerinde işler (TBK 339); diğerlerinde genel hükümler (TBK 327) uygulanır ([rejim kontrolü](kira-rejimi-ve-taraflar.md#önce-rejimi-belirle)).
- **Belirli veya belirsiz süre:** İlk süreyi, uzama yıllarını ve kira yılı sınırlarını `python scripts/hesap.py donemler --baslangic <S>` ile çıkar; son kullanım günü ile yıldönümünü ayır.
- **Sözleşme tarihi ve dönem:** Sözleşme, ihtar ve fesih 01.07.2012'den önce mi (818 BK, 6570), sonra mı? Geçişte 6101 m.1–3 ve geçici 2'yi resmî metinden doğrula.
- **Kiraya veren, malik, yeni malik:** Sıfatları ayır. Taahhüde yalnız kiraya veren, TBK 351'e yalnız kiralananı sonradan edinen yeni malik dayanır; edinme günü `D`'yi tapu kaydıyla belgele.
- **Paylı ve elbirliği mülkiyet:** TBK 350 davasında pay ve paydaş çoğunluğunu, elbirliğinde bütün ortakları ara. İlamsız takipte sözleşmedeki bütün kiraya verenler birlikte hareket eder (12. HD 2025/7823); davada da temkinli yol budur ([taraf ve paydaşlık](kira-rejimi-ve-taraflar.md#taraf-temsil-ve-paydaşlık)).
- **Aile konutu:** TMK 194/son bildirimi var mı, ne zaman yapıldı? Eş taraf olduysa ihtar ve fesih bildirimlerini ona ayrıca yap (TBK 349/3) ve onu takipte veya davada taraf göster.
- **Dava tarihi:** Dava 01.09.2023 veya sonrasında açılacaksa HUAK 18/B dava şartı arabuluculuk aranır; ilamsız icra yoluyla tahliye istisnadır ([ortak usul](#ortak-usul-arabuluculuk-görev-taraf-ve-tebligat)).
- **Tebliğ tarihleri:** Her ihtarın, bildirimin, ödeme emrinin ve kararın keşide değil tebliğ tarihini belgeden al; UETS'de `G(U,5)` (`python scripts/deadlines.py uets <U>`). Bilinmeyen tarihi [DOLDURULACAK: tebliğ tarihi] diye yaz, varsayma.

## Ortak usul: arabuluculuk, görev, taraf ve tebligat

**Dayanak ve kapsam.** HUAK 18/B/1-a (7445 s.K.): 01.09.2023 ve sonrasında açılan davalarda kira ilişkisinden kaynaklanan uyuşmazlıklarda arabulucuya başvuru dava şartıdır; taşınmazların İİK'ya göre “ilamsız icra yoluyla tahliyesine ilişkin hükümler” hariçtir (lafız 3. HD 2025/3048 aktarımından; resmî metinden doğrula). Ölçüt dava tarihidir. HMK 4/1-a: ilamsız tahliye dışındaki bütün kira uyuşmazlıklarında, değere ve tacir sıfatına bakılmaksızın sulh hukuk görevlidir (20. HD 2015/10565); basit yargılama uygulanır. Ön inceleme: [görev, yetki ve başvuru yolu](kira-rejimi-ve-taraflar.md#görev-yetki-ve-başvuru-yolu).

**Koşullar.** Yolu seç: sulh hukukta dava (TBK 347, 350–352; 315, 316, 331 feshine dayalı tahliye) ya da ilamsız icra (İİK 269, 272). TBK 352/2 yalnız davayla istenir; konut ve çatılı işyerinde salt süre bitimine dayalı 14 örnek yapma (TBK 347/1). Taraf teşkili: sözleşmedeki bütün kiraya verenler (elbirliğinde bütün mirasçılar) ile bütün kiracılar ve TMK 194/son bildirimi yapmış eş. Kiraya veren ile maliki ayır: taahhüt yolunu yalnız kiraya veren kullanır (3. HD 2025/4997 gerekçesi); TBK 350 davasını malik de açabilir (3. HD 2018/1605, HUMK dönemi). Dava yolunda bütün kiraya verenlerin birlikte hareketini yalnız İstanbul BAM 36. HD aramıştır (3. HD 2024/3125'te aktarılır).

**Bildirim.** TBK 315, 316/2, 347/1, 347/2, 351/1 ve 352/2 yazılı bildirim ister; TBK 353 bildirimi isteğe bağlıdır; 350, 352/1 ve 352/3 ön ihtar istemez. Arabuluculuk ihtar yerine, ihtar da arabuluculuk yerine geçmez. Fesih bildirimi yazılı ve imzalıdır (TBK 348, 14): noter, UETS veya güvenli e-imza kullan; WhatsApp, SMS ve imzasız e-postayı ihtiyaten yazılı sayma. Bütün kiraya verenler adına, bütün kiracılara, bildirim yapmış eşe ayrı ayrı (TBK 349/3) ve TBK 356 uyarınca sürdürenlere gönder. Belirleyici tarih tebliğdir: UETS'de `G(U,5)` (`python scripts/deadlines.py uets <U>`); okuma tarihi ve normal KEP yazışması esas alınmaz. Şablon: [arabuluculuk başvurusu notu](tahliye-sablonlari.md#arabuluculuk-başvurusu-notu).

**Süreler.**

| Süre | Başlangıç olayı | Hesap | Araç | Güven |
| --- | --- | --- | --- | --- |
| TBK 350/1 başvurusu (350/2 kıyasen) | Süre veya uzama yılı sonu `E` | `E < başvuru ≤ A(E,1)` | `python scripts/deadlines.py tbk350 <E>` | yüksek; sınır günleri orta ([gereksinim](#gereksinim-ve-yeniden-inşa-tbk-350)); 350/2: orta |
| TBK 351, 352 dava yolları başvurusu | Edinme `D`, bitim `E`, boşaltma tarihi `B` | 351/1 `≥ G(A(D,6),1)`; 351/2, 352/2-3 `≤ A(E,1)`; 352/1 `≤ A(B,1)`; hak doğduktan sonra | `python scripts/deadlines.py tbk351 <D>`; `python scripts/deadlines.py tbk352 <B>` | pencere: 351/1 ve 352/1 orta, diğerleri düşük; pencereden önce başvurunun yeterliliği düşük (Yargıtay kararı yok) |
| Dava süresi olmayan yollar (347, 315, 316, 331) | Sona erme günü `F` | 347/1'de dava `F` günü dahil (3. HD 2017/6383), temkinli başvuru `F`'den sonra; diğerlerinde sona ermeden sonra; kanuni üst sınır yok | `python scripts/deadlines.py tbk347 <ilk-sure-bitimi>` (yalnız 347/1) | orta |
| TBK 353 uzaması | Süre sonu `E`; bildirim en geç dava süresinin son günü ulaşmış | Son gün adayı `Y(E,1)` | `python scripts/deadlines.py takvim <E> --count 1 --unit yil` | orta |
| 18/A/15 kalan süre | Başvuru `b`, son tutanak `T` | `kalan = A(E,1) − b` gün; `G(T,kalan)` | araç yok | düşük |
| Arabuluculuğun azami süresi (HUAK 18/B; resmî metinden doğrula) | Görevlendirme `g` | `G(g,21)`; uzatmayla `G(g,28)` | `python scripts/deadlines.py takvim <g> --count 3 --unit hafta` | orta |
| Son tutanağı sunma (kesin) | İhtarlı davetiyenin tebliği `T` | `G(T,7)` | `python scripts/deadlines.py takvim <T> --count 1 --unit hafta` | yüksek |
| Görevsizlik sonrası gönderme (HMK 20/1) | Kesinleşme veya tebliğ `K` | `G(K,14)` | `python scripts/deadlines.py takvim <K> --count 2 --unit hafta` | yüksek |
| Cevap; istinaf ve temyiz | Dilekçenin veya kararın tebliği `T` | `G(T,14)`; cevapta ek süreyle en çok `G(T,28)` | `python scripts/deadlines.py takvim <T> --count 2 --unit hafta` | orta |

Araçlar 18/A/15 durmasını, TBK 353'ü ve tatili uygulamaz: [süre rehberi](sure-hesaplama.md#tatil-arabuluculuk-ve-tebligat-düzeltmeleri).

**Yol, görevli yer ve arabuluculuk.** (A) Sulh hukukta dava: yetkili yer davalının (davalılardan birinin) yerleşim yeri veya sözleşme kurulurken taşınmazın bulunduğu ifa yeridir (TBK 89). Kesin yetki yoktur (6. HD 2013/14529, HUMK dönemi); itiraz cevapta ilk itirazdır (HMK 19; resmî metinden doğrula). Başvuru hiç yoksa dava işlem yapılmaksızın usulden reddedilir; son tutanak eklenmemişse bir haftalık kesin süre verilir (18/A/2); dosya numarası yazmak yetmez (9. HD 2026/862'nin onadığı BAM görüşü, iş). Terditli sebeplerin süresini ayrı denetle. Üç aylık kira temyiz sınırını aşmıyorsa BAM kararı kesindir (HMK 362/1-b; resmî metinden doğrula). (B) İlamsız tahliye: icra dairesi ve icra mahkemesi; istisna. (C) İtirazın iptali ve tahliye: istisna çözülmedi; ihtiyaten başvur. (D) Taraflar, avukatları ve arabulucunun imzaladığı anlaşma belgesi şerhsiz ilam niteliğindedir (HUAK 18/4; resmî metinden doğrula); tahliye tarihini icraya elverişli yaz (12. HD 2025/7199).

**Deliller.** Sözleşme; tapu, mirasçılık belgesi, vekâletnameler; arabuluculuk dosyası (başvuru, görevlendirme, son tutanak aslı, e-imza zaman damgaları); ihtar ve tebliğ kaydı; eşin bildirimi; yıllık kira kayıtları.

**Kiracı savunmaları.** Arabuluculuk yok, erken ya da son tutanak süresinde sunulmadı; eksik taraf; taahhüt yolunda kiraya veren olmayan malik; görev ve süresinde yetki itirazı; TBK 350–352 süreleri kamu düzenindendir; imzasız bildirim (tartışmalı). Yargılamada anahtar teslimi davayı konusuz bırakır; giderler dava tarihindeki haklılığa göre yüklenir (HMK 331/1). Şablon: [kiracı cevap dilekçesi iskeleti](tahliye-sablonlari.md#kiracı-cevap-dilekçesi-iskeleti).

**Tuzaklar.** 3. HD 2025/3048'i 350/1 dışına kendiliğinden, İstanbul BAM 35. HD 2025/3212'yi 26.05.2025 ve sonrasında açılan davalara taşıma. 18/A/15'i otomatik uygulama: son tutanak tarihi son imza tarihi olabilir (9. HD 2025/5080, iş uyuşmazlığı); temkinli hesapta erken tarihi al. 3048'deki “6235” yazımını ve 6325 m.16/2 atfını aktarma; durmanın dayanağı HUAK 18/A/15'tir. Havuzda olmayan 3. HD 2025/5039 ve 2025/3540'ı emsal sayma ([kontrol notu](tahliye-ve-uyarlama-kontrol.md)). Harç bir yıllık kira üzerinden nispidir (492 m.17); aylık kiradan yatırma (3. HD 2024/3820).

**Doğrulanmış yerel kararlar.**

- **Yargıtay 3. HD, E. 2025/1495, K. 2025/3048, 26.05.2025**: BAM'lar arası uyuşmazlık giderildi; oybirliği, kesin (kiracı lehine usul itirazı). TBK 350/1'de başvurunun “tahliye davası açma hakkının doğumundan sonra diğer bir anlatımla dava açma süresi içerisinde yapılması gerektiğine” karar verdi. Sınır: hüküm fıkrası yalnız 350/1. `python scripts/pool.py get 1155987500`
- **İstanbul BAM 35. HD, E. 2025/5438, K. 2025/3212, 30.12.2025**: usulden ret kaldırıldı, tahliyeye karar verildi; kesin (kiraya veren lehine). 05.08.2024'te açılan davada erken başvuru nedeniyle ret “davacı için öngörülebilir nitelikte olmayıp” denerek şart yeterli sayıldı. Sınır: tek daire; E./K. üst veriden. `python scripts/pool.py get aa156eaa-5348-4eef-963a-75a3f84b14a7`
- **Yargıtay HGK, E. 2025/255, K. 2026/11, 21.01.2026**: direnme kararı oybirliğiyle bozuldu. Görevsizlikten sonra, dosya gönderilmeden tamamlanan arabuluculukta “görevli veya yetkili mahkemede davaya devam edildiğinde dava şartı tamdır”. Sınır: iş uyuşmazlığı; aksi: Ankara BAM 31. HD 2026/339 (ticari, `python scripts/pool.py get 1202171700`). `python scripts/pool.py get 1202391900`
- **Yargıtay 12. HD, E. 2025/6920, K. 2025/7823, 03.12.2025**: BAM kararı oybirliğiyle bozuldu (kiracı lehine). Üç kiraya verenden ikisinin başlattığı takipte “ilamsız tahliye takibinin tüm kiraya verenler tarafından tüm kiracıları taraf gösterilerek başlatılması gerekir”; tapudaki çoğunluk yetmez. Sınır: ilamsız takip; paylıya çevrilmiş terekede 12. HD 2025/7528. `python scripts/pool.py get 1201163600`
- **Yargıtay 8. HD, E. 2017/3527, K. 2017/9518, 21.06.2017**: tahliye kararı bozuldu (kiracı tarafı lehine). TMK 194 ihtarı gönderen eş şerh olmasa da kiracıdır: “Davanın açılmasındaki eksiklik sonradan giderilebilir ise de, icra takibindeki eksikliğin sonradan giderilmesi mümkün olmadığından”. Sınır: HUMK dönemi. `python scripts/pool.py get 353815800`
- **Yargıtay 3. HD, E. 2022/4537, K. 2022/7440, 06.10.2022**: tahliye ve bedel davasında temyiz miktardan reddedildi; oybirliği. Hüküm tarihindeki sınıra göre “üç aylık kira tutarı, bu sınırın altındadır”. Sınır: 7550 s.K. sonrası dava tarihi ölçütü doğrulanmadı. `python scripts/pool.py get 815297500`

**Açık noktalar.**

- TBK 350/2, 351 ve 352 yollarında erken arabuluculuk yeterli mi? Derleme atıfları havuzda yok.
- İtirazın iptali ve tahliye davası 18/B istisnasına girer mi; görevsiz mahkemeden sonra tamamlanan arabuluculuk kira davasında yeterli mi?
- Eksik tarafla veya farklı konuda yürütülen arabuluculuk şartı karşılar mı; başvuru TBK 353 bildirimi sayılır mı?
- HUAK 18/B süresi, geçiş hükmü, HMK 362/1-b ve Ek m.1 metinleri resmî kaynaktan doğrulanmadı.

Rota kartı: `python scripts/tahliye.py yol ortak_usul` · emsaller: `python scripts/tahliye.py emsal ortak_usul`

## Temerrüt (TBK 315) ve ilamsız tahliye takibi

**Dayanak ve kapsam.** TBK 315: teslimden sonra muaccel olan kira bedeli veya yan gider ödenmezse kiraya veren yazılı süre verir; sürede ödenmezse sözleşmeyi feshedeceğini bildirir. Süre konut ve çatılı işyerinde en az 30, diğer kiralarda en az 10 gündür; ürün kirasında TBK 362/2 en az 60 gün ister. Belirli ve belirsiz süreli kirada sözleşme sonu beklenmez. 01.07.2012'den önce gerçekleşen temerrüt mülga BK 260/288'e tabidir (6101 m.1; resmî metinden doğrula); 6217 geçici 2 TBK 315'i ertelemez. Rejim: [kira rejimi rehberi](kira-rejimi-ve-taraflar.md#önce-rejimi-belirle).

**Koşullar.** Kira veya yan gider teslimden sonra ve ihtar ya da takipten önce muaccel olmalı (sözleşmedeki ödeme günü, yoksa TBK 314 ay sonu; TBK 346'ya aykırı muacceliyet kaydına dayanma). İhtar veya ödeme emri tebliğ edilmiş, süre içinde borcun tamamı kayıtsız ödenmemiş olmalı. Alacaklı temerrüdü bulunmamalı (TBK 106–107). Bütün kiraya verenler, TMK 194/son bildirimiyle taraf olmuş eş dahil bütün kiracılara karşı hareket eder (8. HD 2017/9518). Yalnız faiz, icra gideri ve vekâlet ücretinin ödenmemesi tahliye sebebi değildir (6. HD 2016/1075).

**Bildirim.** Dava yolunda TBK 315'e uygun yazılı ihtar şarttır: ay ay dönemler ve tutarlar, ödeme yeri veya IBAN, en az 30 (10/60) gün, sürede ödenmezse feshedileceği ve tahliye davası açılacağı. Noter veya UETS kullan; WhatsApp, SMS ve imzasız e-postaya dayanma (TBK 14/2). Taraf olmuş eşe ayrıca bildir (TBK 349/3). İlamsız yolda ayrı ihtar gerekmez: takip talebinde açıkça tahliye istenir, 13 örnek ödeme emri ihtarı içerir (İİK 269; resmî metinden doğrula). HGK, itiraz edilen 13 örneğin sulh hukuk davasında ihtar yerine geçtiğini kabul eder; İİK 269/b lafzı daha dar okunabildiğinden (resmî metinden doğrula) inkâr dışı itirazda ihtiyaten ayrı ihtar gönder. Şablon: [temerrüt ihtarnamesi](tahliye-sablonlari.md#temerrüt-ihtarnamesi-tbk-315).

**Süreler.**

| Süre | Başlangıç olayı | Hesap | Araç | Güven |
| --- | --- | --- | --- | --- |
| TBK 315 ödeme süresi, konut ve çatılı işyeri | İhtarın tebliği `T` (UETS'de `T = G(U,5)`) | `G(T,30)` veya verilen daha uzun süre | `python scripts/deadlines.py tbk315 <T>` | yüksek |
| 13 örnek: itiraz | Ödeme emrinin tebliği `T` | `G(T,7)` | `python scripts/deadlines.py iik269 <T>` (`itiraz_suresi_ham_sonu`) | yüksek |
| 13 örnek: ödeme süresi | Ödeme emrinin tebliği `T` | `O = G(T,30)`; diğer kiralarda `G(T,10)`, ürün kirasında `G(T,60)` | `python scripts/deadlines.py iik269 <T>` (yalnız konut ve çatılı işyeri; `odeme_suresi_ham_sonu`) | yüksek |
| İtiraz yoksa tahliye talebi (İİK 269/a) | Ödeme süresinin bitimi `O` | `G(O,1)` – `A(O,6)`; altı ay `O`'dan sayılır | `python scripts/deadlines.py iik269 <T>`; 10/60 günde `python scripts/deadlines.py takvim <O> --count 6 --unit ay` | yüksek |
| İtirazın kaldırılması ve tahliye | İtirazın alacaklıya tebliği `I` | `O` geçtikten sonra, son `A(I,6)` (İİK 68/1; resmî metinden doğrula) | `python scripts/deadlines.py takvim <I> --count 6 --unit ay` | orta |
| Sulh hukukta tahliye davası | İhtar süresinin bitimi `O` | En erken `G(O,1)`; hak düşürücü süre yok | araç yok | orta |
| İtirazın iptali ve tahliye | İtirazın alacaklıya tebliği `I` | `Y(I,1)` (İİK 67/1; resmî metinden doğrula) | `python scripts/deadlines.py takvim <I> --count 1 --unit yil` | orta |

`iik269` yalnız konut ve çatılı işyerindeki 30 günlük ödeme süresi içindir; diğer kiralarda `G(T,10)`, ürün kirasında `G(T,60)` veya ödeme emrinde yazılı daha uzun süre için `python scripts/deadlines.py takvim <T> --count <n> --unit gun` kullan. Yedi gün ve 269/a altı ayı resmî metinden değil, Yargıtay kararlarında aktarılan madde metninden kontrol edildi; resmî metinden doğrula ([icra süreleri](sure-hesaplama.md#kira-icra-takiplerinde-süreler)). Eşe ayrı tebliğde temkinli `G(max(T1,T2),30)` yalnız çıkarımdır (düşük güven). Araçlar tatil düzeltmesi yapmaz ([süre rehberi](sure-hesaplama.md#kira-işlemleri-için-formüller)).

**Yol, görevli yer ve arabuluculuk.** (A) İlamsız tahliye takibi: icra dairesi, sonra takibin yapıldığı yerdeki icra mahkemesi; HUAK 18/B/1-a istisnası nedeniyle arabuluculuk aranmaz. İtirazda yalnız tahliye isteme, itirazın kaldırılmasını da iste. Sözleşme veya imza açıkça inkâr edilmiş ve noter senedi yoksa sulh hukukta dava gerekir (İİK 269/b; resmî metinden doğrula). (B) Sulh hukukta TBK 315 fesih ve tahliye davası (HMK 4/1-a): dava 01.09.2023 veya sonrasında açılıyorsa arabuluculuk dava şartıdır; başvuruyu ihtar süresi bittikten sonra yap (3. HD 2025/3048 kıyası). (C) İtirazın iptali ve tahliye davası: tahliye kısmının istisnaya girip girmediği tartışmalıdır; ihtiyaten arabulucuya başvur. Bkz. [ortak usul](#ortak-usul-arabuluculuk-görev-taraf-ve-tebligat).

**Deliller.** Sözleşme (ödeme günü, peşin kaydı, IBAN, yan gider oranı, noter onayı), teslim belgesi, ay ay borç-ödeme çizelgesi, ihtar ve tebliğ şerhi veya UETS kaydı, icra dosyasının tamamı, kiraya veren sıfatı belgeleri, eşin bildirimi, son tutanak.

**Kiracı savunmaları.** Kısa süre veya fesih uyarısı yokluğu; takip talebinde tahliye istenmemesi; hiç tebliğ yapılmaması (usulsüz tebliğde öğrenmeden itibaren yedi gün içinde şikâyet, İİK 16/1; resmî metinden doğrula); süre içinde tam ödeme; muacceliyet yokluğu; alacaklı temerrüdü ve ödeme yeri belirlenmesi (3. HD 2025/3047); eksik taraf; miktarı belirsiz yan gider (12. HD 2025/5902); sözleşmedeki kısa ihtar ve fesih kayıtlarının geçersizliği (3. HD 2024/217). Önceki ödemeyi itirazda 269/c belgesiyle bildir. Şablon: [itiraz notu](tahliye-sablonlari.md#tahliye-takibine-itiraz-notu).

**Tuzaklar.** TBK 315 ihtarını [iki haklı ihtarla](#kira-yılı-içinde-iki-haklı-ihtar-tbk-3522) karıştırma. Yedi günlük itiraz süresini ödeme süresi sanma. “Bakiye kira” gibi belirsiz kalem yazma. Havale masrafı düşülmüş ödeme eksiktir (HGK 2021/1302). Tebliğsizlik ile usulsüz tebliği ayır.

**Doğrulanmış yerel kararlar.**

- **Yargıtay HGK, E. 2017/1918, K. 2021/1707, 21.12.2021**: direnme kararı oy çokluğuyla bozuldu (kiraya veren lehine). Süresinde icra dosyasına yatırılıp menfi tespit tedbiriyle alacaklıya geçmesi engellenen para temerrüdü önlemez. “İhtar süresi içinde yapılan bu ödeme ile borçlu hakkında haciz uygulanmasına engel olup, temerrüdü engellemez.” Sınır: karşıoy var; tedbirli ödemeye özgü. `python scripts/pool.py get 746178000`
- **Yargıtay HGK, E. 2017/2340, K. 2021/261, 16.03.2021**: direnme kararı oy çokluğuyla bozuldu (kiraya veren lehine). Takipten önceki ödeme, itiraz edilmemişse icra mahkemesinde dinlenmez. “ödeme emrine itiraz etmeyen borçlu icra mahkemesinde sadece ihtar süresi içinde ödeme yaptığını ileri sürebilir.” Sınır: karşıoy var. `python scripts/pool.py get 685746400`
- **Yargıtay HGK, E. 2021/996, K. 2023/642, 21.06.2023**: BAM'ın itirazın kaldırılmasına ilişkin direnme kararı oy çokluğuyla, kesin olarak bozuldu (kiracı lehine). Bila tebliğ dönen ödeme emrinde haricen öğrenip itiraz etmek süre başlatmaz. “Ödeme emri ile ihtar tebliğ edilmediğinden kiracının temerrüdünden de söz edilemez.” Sınır: usulsüz tebliği çözmez. `python scripts/pool.py get 920523900`
- **Yargıtay HGK, E. 2017/1842, K. 2021/648, 01.06.2021**: tahliyeye ilişkin direnme kararı oybirliğiyle bozuldu (kiracı lehine). Takip talebinde açık tahliye istemi yoksa 13 örnek hak doğurmaz. “icra dairesince borçluya gönderilen ödeme emrinde tahliye ihtarının bulunması alacaklıya tahliye açısından bir hak vermez.” Sınır: somut talep metnine bağlı. `python scripts/pool.py get 686165600`
- **Yargıtay 12. HD, E. 2025/6920, K. 2025/7823, 03.12.2025**: şikâyeti reddeden BAM kararı oybirliğiyle bozuldu (kiracı lehine). Takibi sözleşmedeki bütün kiraya verenler yapar. “Bu eksikliğin icra mahkemesinde görülen tahliye incelemesinde de giderilmesi mümkün değildir.” Sınır: paylı mülkiyete geçişte 12. HD 2025/7528 farklı. `python scripts/pool.py get 1201163600`

**Açık noktalar.**

- İtirazın iptali ve tahliye davası HUAK 18/B istisnasına girer mi? Havuzda karar yok.
- İtirazsız kesinleşen ödeme emri sulh hukuk davasında ihtar sayılır mı? İİK 269/b son fıkrası belirsiz.
- Yalnız yan gidere dayalı ilamsız tahliyeyi 12. HD 2025/5902 ilke olarak kabul edip somut olayda reddetti; karşıoylar iki yönlü.
- İİK 67, 68/1, 269/b–d, 16 ve 65 metinleri resmî kaynaktan doğrulanmadı.

Rota kartı: `python scripts/tahliye.py yol temerrut` · emsaller: `python scripts/tahliye.py emsal temerrut`

## Kira yılı içinde iki haklı ihtar (TBK 352/2)

**Dayanak ve kapsam.** TBK 352/2: bir yıldan kısa sözleşmede kira süresi, bir yıl ve daha uzun sözleşmede bir kira yılı içinde kira bedeli için iki yazılı haklı ihtara sebep olan kiracıya karşı kiraya veren, kira süresinin veya ihtarların yapıldığı kira yılının bitiminden başlayarak bir ay içinde yalnız dava yoluyla sözleşmeyi sona erdirebilir. İcra yolu yoktur; ihtarda süre veya fesih uyarısı lafzen aranmaz. Yalnız konut ve çatılı işyerinde uygulanır (TBK 339); karma kiralananda galip vasfa bak (3. HD 2019/4831). Süresiz sözleşmede ve yıllık ödemede iki haklı ihtarın oluşmayacağı Yargıtay'ın kalıp gerekçesidir ve havuzda hükmü tek başına taşımamıştır; riski bildir. 01.07.2012 öncesi olaylarda 6570 m.7/e uygulanır. Sözleşmedeki geç ödemede fesih kaydı bu sebebin yerine geçmez (3. HD 2024/217).

**Koşullar.**

- Farklı dönemler için ayrı ayrı yapılmış iki yazılı ihtar; ardışık aylar için tek ihtar tek sayılır (HGK 2021/1314).
- Her ihtar, kira sözleşmedeki ödeme gününe (yoksa TBK 314 ay sonuna) göre muaccel olduktan sonra keşide edilir; “peşin” kaydı bağlar (3. HD 2021/10994).
- İlk ihtar anında muaccel olan aylar ikinci ihtara saklanmaz (3. HD 2018/5354).
- İki ihtar aynı kira süresi veya kira yılına ilişkin olur ve o yıl içinde tebliğ edilir; bir yıllık sözleşmede TBK 347/1 uzama yılları ayrı kira yılıdır.
- Tebliğ anında borç ödenmemiş olmalı; tebliğden sonraki ödeme haklılığı kaldırmaz.
- Borç kira bedeli olmalı; aidat ve yan gider için haklılığı varsayma.
- Temkinli yol: bütün kiraya verenler ihtar eder ve dava açar, bütün kiracılar davalıdır (12. HD 2025/7823, icra bağlamında kıyas).

**Bildirim.** Noter ihtarnamesi veya kira alacağı için gönderilen icra ödeme emri ihtar sayılabilir. WhatsApp, SMS, imzasız e-posta ve telefon yetmez. Ay ay dönem, tutar ve ödeme yeri yazılır. 3. HD 2017/15623 30 günlük süre aramaz; HGK 2021/1314 ise koşul listesinde 30 gün ve tahliye davası uyarısını sayar. Temkinli metin ikisini de içerir; fesih uyarısı da taşıyan ihtar [TBK 315 yolunu](#temerrüt-tbk-315-ve-ilamsız-tahliye-takibi) açık tutar. Taraf olmuş eşe ihtiyaten ayrıca gönder (TBK 349/3'ün uygulanıp uygulanmadığı açık). İhtar sözleşmeyi sona erdirmez; kiraya verenin tek yanlı feshi ve kiralanana el koyması sözleşme ihlalidir (Yargıtay 3. HD, E. 2022/5351, K. 2022/7594, 11.10.2022).

**Süreler.**

| Süre | Başlangıç olayı | Hesap | Araç | Güven |
| --- | --- | --- | --- | --- |
| Muacceliyet eşiği | Ödeme günü veya ödeme aralığının son günü `D` (yoksa ay sonu) | En erken keşide `G(D,1)` | araç yok | yüksek |
| Kira yılları ve tebliğ penceresi | Başlangıç `S`; yıl `k` için `E1 = G(Y(S,k),-1)`, `E2 = Y(S,k)` | `D_i < keşide_i ≤ T_i`, `S_k ≤ T_i ≤ E1` | `python scripts/hesap.py donemler --baslangic <S>` | orta |
| UETS tebliğ anı | Ulaşma `U` | `T = G(U,5)` gün sonu; haklılık için ödeme `G(U,6)` veya sonra | `python scripts/deadlines.py uets <U>` | orta |
| Dava süresi | Kira süresinin veya ihtarların yapıldığı kira yılının son günü `E1` | `E2 = G(E1,1)`; `G(E2,1)` – `A(E1,1)`; ikinci ihtara ay eklenmez | `python scripts/deadlines.py takvim <E1> --count 1 --unit ay` | orta |
| Arabuluculuk başvurusu | Dava hakkının doğumu | `G(E2,1) ≤ B ≤ A(E1,1)`; başvurudan son tutanağa süre işlemez | araç yok | düşük |

`deadlines.py tbk352` TBK 352/1 içindir; burada kullanma. Peşin veya taksitli ödemede iki pencere hesapla: ihtar yılına göre W1 (kanun lafzı), kiranın ait olduğu yıla göre W2 (3. HD 2025/3118); pencereler çakışmayabilir. Adli tatilin bu süreyi uzatacağını varsayma ([süre rehberi](sure-hesaplama.md#kira-işlemleri-için-formüller)).

**Yol, görevli yer ve arabuluculuk.** Tek yol sulh hukukta tahliye davasıdır (HMK 4/1-a; basit yargılama ve yetkiyi resmî metinden doğrula). İlamsız icra yolu olmadığından HUAK 18/B/1-a istisnası uygulanmaz: dava 01.09.2023 veya sonrasında açılıyorsa arabuluculuk dava şartıdır; başvurusuz dava usulden reddedilir (18/A/2). Başvuruyu kira yılı veya süresi bittikten sonra, bir aylık süre içinde yap: 3. HD 2025/3048 TBK 350'de erken başvuruyu yetersiz saymıştır; kıyas riski yüksektir. Derlemedeki aksi yönlü 3. HD 2026/3805 K. havuzda yok. Kiralanan dava sırasında boşaltılırsa giderler dava tarihindeki haklılığa göre yüklenir. [Ortak usul](#ortak-usul-arabuluculuk-görev-taraf-ve-tebligat).

**Deliller.** Sözleşme (başlangıç, süre, ödeme günü, peşin kaydı, kiralananın niteliği), kira yılı çizelgesi, her ihtarın keşide ve tebliğ tarihi ile saati, icra dosyası ve itiraz tarama saati, banka dekontları, arabuluculuk tutanakları.

**Kiracı savunmaları.** Tebliğden önce ödeme (6. HD 2013/5989); aynı gün tebliğ ve ödemede sıralamanın ispatlanamaması (3. HD 2018/9394); muacceliyetten önce ihtar; bölünmüş ikinci ihtar; ayların belirtilmemesi; süre dışı dava; arabuluculuk yokluğu ya da erken başvuru; alacaklı temerrüdü ve ödeme yeri belirlenmesi (3. HD 2025/3047). Şablon: [kiracı cevabı](tahliye-sablonlari.md#kiracı-cevap-dilekçesi-iskeleti).

**Tuzaklar.** Uzun sözleşmede sözleşme sonunu değil kira yılı sonunu esas al. 3. HD 2025/3118'deki “bir yıl içinde” ifadesi “bir ay” yerine yazım hatası görünümündedir. [Eğitim notu kontrolünde](tahliye-ve-uyarlama-kontrol.md) anılan 6. HD 2014/9995 yerel havuzda yoktur; doğrulamadan alıntılama.

**Doğrulanmış yerel kararlar.**

- **Yargıtay HGK, E. 2017/1289, K. 2021/1314, 02.11.2021**: direnme kararı oybirliğiyle uygun bulundu; dosya sair itirazlar için 3. HD'ye gönderildi. Kurucu unsurlar sayıldı, somut ihtarlar haklı bulundu. “İhtar kiracıya tebliğ edildikten sonra ödeme yapılması kiraya verenin haklılığını ortadan kaldırmaz”. Sınır: nihai sonuç metinde yok; koşul listesi doktrine dayanır. `python scripts/pool.py get 720126200`
- **Yargıtay 3. HD, E. 2024/2951, K. 2025/3118, 28.05.2025**: BAM'ın ret kararı gerekçe değiştirilerek onandı (kiraya veren aleyhine). Peşin taksitli kirada kiranın ait olduğu kira yılı esas alındı; dava erken sayıldı. “26.01.2022 tarihinde açılan dava süresinde değildir.” Sınır: kanun lafzından ayrılan tek karar. `python scripts/pool.py get 1159454200`
- **Yargıtay 3. HD, E. 2017/6324, K. 2017/15623, 09.11.2017**: ret hükmü değiştirilen gerekçeyle düzeltilerek onandı (kiraya veren aleyhine). 30 gün gerekmez; muaccel olmadan keşide edilen ihtar haklı değildir. “30 günlük ödeme süresi verilmesine gerek olmayıp”. Sınır: HGK 2021/1314 ile gerilim. `python scripts/pool.py get 385800700`
- **Yargıtay 3. HD, E. 2017/11179, K. 2018/5354, 16.05.2018**: tahliye hükmü bozuldu (kiracı lehine). İkinci takip, ilk takipte istenebilecek kiraya ilişkindi. “bölünerek ayrı icra takibine konu edilemeyeceğinden bu ikinci ihtar haklı sayılamaz.” Sınır: dava 6570 döneminde açıldı. `python scripts/pool.py get 427128300`
- **İstanbul BAM 36. HD, E. 2019/3134, K. 2021/1779, 22.09.2021**: kiraya verenin istinafı kabul edildi; konusuz davada giderler kiracıya yüklendi, kesin. Kiracı ödeme emirlerine önce itiraz edip sonra ödediğinden usulsüz tebliğe rağmen emirler öğrenilmiş sayıldı. “her iki ödeme emrinin davalı tarafından öğrenildiğinin kabulü gerektiği”. Sınır: BAM kararı; bölünme yasağını tartışmadı. `python scripts/pool.py get fa461f44-de8b-43e1-aaa4-60c85a683530`

**Açık noktalar.**

- Peşin veya taksitli ödemede W1 mi W2 mi? Seçimi ve riski müvekkile yazılı bildir.
- İhtarda 30 gün ve dava uyarısı şart mı? 3. HD ile HGK arasında gerilim var.
- Kira yılı bitmeden arabuluculuk başvurusu yeterli mi, TBK 353 uzaması uygulanır mı? Havuzda karar yok.
- Yan gider ihtarı, eşe ayrı ihtar ve paydaş çoğunluğunun yeterliliği çözülmedi.

Rota kartı: `python scripts/tahliye.py yol iki_hakli_ihtar` · emsaller: `python scripts/tahliye.py emsal iki_hakli_ihtar`

## Tahliye taahhüdü (TBK 352/1)

**Dayanak ve kapsam.** TBK 352/1: kiracı, kiralananın tesliminden sonra kiraya verene karşı belli bir tarihte boşaltmayı yazılı olarak üstlenmiş ve boşaltmamışsa kiraya veren, bu tarihten başlayarak bir ay içinde icraya başvurarak veya dava açarak sözleşmeyi sona erdirebilir (`python scripts/tbk.py 352`). Hüküm konut ve çatılı işyerine özgüdür (TBK 339); belirli ve belirsiz süreli kirada uygulanır. Talep hakkı yalnız kiraya verenindir; kiraya veren olmayan malik veya paydaş taahhüde dayanamaz. Sona erme 01.07.2012'den sonraysa TBK uygulanır; taahhüdün geçerliliğini düzenlendiği tarihin hukukuna göre incele (6101 m.3, resmî metinden doğrula).

**Koşullar.** Taahhüdü kiracı veya yetkili temsilcisi el yazısı ya da güvenli elektronik imzayla imzalamalıdır (TBK 14–15); noter onayı geçerlilik şartı değildir. Birlikte kiracılıkta bütün kiracıların imzasını ara. Belli bir boşaltma tarihi `B` bulunmalı; şartlı veya tarihsiz taahhüt için doğrulanmış karar yok. Ölçüt sözleşme tarihi değil teslimdir; sözleşmeyle aynı gün veya önce alınan taahhüt geçersizdir (BAM 2026/377). Taahhütten sonra yeni kira ilişkisi kurulmuşsa taahhüt hükümsüz kalabilir ([kontrol notu](tahliye-ve-uyarlama-kontrol.md#taahhüt-teslim-tarih-ve-ispat)). Aile konutunda eşin TMK 194/son bildirimi taahhütten sonraysa taahhüdü etkilemez; önceyse iki eşin imzası veya açık rıza aranır (2025/4997, ikincisi obiter; TMK metnini resmî kaynaktan doğrula). Takibi bütün kiraya verenler adına bütün kiracılara, takipten önce bildirim yapmış eş dahil, yönelt; takipteki eksiklik icra mahkemesinde giderilemez.

**Bildirim.** Kanun ön ihtar aramaz. TBK 353 yalnız “dava açma süresi”nden söz eder; 352/1'e, özellikle takibe uygulanması tartışmalıdır: uzamaya güvenme. Bildirim yapılacaksa `A(B,1)` dolmadan kiracıya, taraf olmuş eşe ayrıca ulaştır. İrade sakatlığına dayanan kiracı bir yıl içinde bildirim yapmalıdır (TBK 39).

**Süreler.**

| Süre | Başlangıç olayı | Hesap | Araç | Güven |
| --- | --- | --- | --- | --- |
| Takip veya dava (TBK 352/1) | Taahhüt edilen boşaltma tarihi `B` | `A(B,1)`; başvuruyu `B`'den sonra yap | `python scripts/deadlines.py tbk352 <B>` | yüksek |
| Dava yolunda arabuluculuk | `B`; başvuru `R` | `B` < `R` ≤ `A(B,1)`; tutanağa kadar durma | araç yok | orta |
| Tahliye emrine itiraz (İİK 274) | Emrin tebliği `T` (UETS'de `G(U,5)`) | `G(T,7)` | `python scripts/deadlines.py takvim <T> --count 7 --unit gun` | orta |
| Boşaltma süresi (İİK 272) | `T` | `G(T,15)` | `python scripts/deadlines.py takvim <T> --count 15 --unit gun` | orta |
| İcra mahkemesine başvuru (İİK 275; 68 kıyası) | İtirazın alacaklıya tebliği `I` | `A(I,6)` | `python scripts/deadlines.py takvim <I> --count 6 --unit ay` | düşük |
| İtirazın iptali davası (İİK 67/1 kıyası) | `I` | `Y(I,1)` | `python scripts/deadlines.py takvim <I> --count 1 --unit yil` | düşük |

Araç tatil, durma ve TBK 353 düzeltmesi yapmaz; İİK sürelerini resmî metinden doğrula ([süre rehberi](sure-hesaplama.md#kira-işlemleri-için-formüller)).

**Yol, görevli yer ve arabuluculuk.** İİK 272 takibi (Örnek 14) icra dairesinde yapılır; HUAK 18/B/1 istisnası nedeniyle arabuluculuk gerekmez (resmî metinden doğrula). İtiraz üzerine icra mahkemesinde itirazın kaldırılması ve tahliye (İİK 275/1, doğrula) yalnız noterce düzenlenmiş, onaylanmış veya imzası ve tarihi ikrar edilmiş taahhütle istenebilir; adi belgede imza veya tarih inkârı bu yolu kapatır. Sulh hukukta itirazın iptali ve tahliye davasında arabuluculuk tartışmalıdır; dava 01.09.2023 veya sonrasında açılacaksa ihtiyaten başvur. Doğrudan tahliye davası sulh hukukta görülür (HMK 4/1-a, doğrula) ve 01.09.2023'ten itibaren dava şartına tabidir; başvurmadan açılan dava usulden reddedilir, bu arada süre dolabilir. [Ortak usul](#ortak-usul-arabuluculuk-görev-taraf-ve-tebligat); [dava iskeleti](tahliye-sablonlari.md#tahliye-dava-dilekçesi-iskeleti).

**Deliller.** Taahhüdün aslı; teslim tutanağı ve ilk ödeme kaydı; mukayese imzaları; tebliğ belgeleri; son tutanak; sonraki sözleşme ve ödemeler; TMK 194 bildirimi; tapu kaydı.

**Kiracı savunmaları.** Tahliye emrine yedi gün içinde itiraz et; edilmezse takip kesinleşir ([itiraz notu](tahliye-sablonlari.md#tahliye-takibine-itiraz-notu)). Teslimden önce verilme ve açığa imzanın aykırı doldurulması yazılı delille, yoksa süresinde dayanılmış yeminle ispatlanır; hileyle habersiz imzalatma sahtelik iddiasıdır; adi belgede imza veya tarih inkârı icra mahkemesi yolunu kapatır. Ayrıca süre aşımı, erken takip, yenilenmiş ilişki, aile konutu bildirimi, taraf eksikliği ve geç tahliye cezasını (TBK 346, 334/2, 182/3) incele.

**Tuzaklar.** İcra mahkemesinde belge ölçütünü İİK 68'e göre kurma; ölçüt 275/1'dir. 2025/4997 içinde aktarılan Başkanlar Kurulu ve BAM gerekçelerini Yargıtay görüşü gibi sunma. İki eşe yöneltmeyi TBK 349/3'e değil TMK 194/son ve zorunlu takip arkadaşlığına dayandır.

**Doğrulanmış yerel kararlar.**

- **Yargıtay 3. HD, E. 2025/3374, K. 2025/4997, 20.10.2025**: BAM'lar arası uyuşmazlık kiraya veren lehine giderildi (5235 s.K. 35/3; oybirliği). Eşin TMK 194 bildirimi yalnız sonrası için sonuç doğurur; bildirim öncesinde verilen taahhüt geçerli kalır: “kiracı eş tarafından bu bildirim öncesinde verilen yazılı tahliye tahhütnamesinin geçerliliğine bir etkisinin bulunmadığına”. Sınır: Yargıtay gerekçesi yalnız IV. bölümdür; bağlayıcılığı doğrula; takipten önceki bildirime rağmen tek eşe yöneltilen takibi çözmez. `python scripts/pool.py get 1187870600`
- **İstanbul BAM 36. HD, E. 2024/5083, K. 2026/377, 04.02.2026**: kiracının istinafı esastan reddedildi (kesin). İmzayı kabul eden kiracının boş imza savunması yazılı delil olmadığından reddedildi: “tahliye taahhüdünü boş olarak verdiği ve üzerinin sonradan doldurulduğu iddiası dinlenemez.” Sınır: BAM kararı; HGK'nın yemin ayrımı karşısında mutlak sayma. `python scripts/pool.py get 191fe3e9-f690-420c-ad33-23cfeb89e8ad`
- **Yargıtay 3. HD, E. 2022/8307, K. 2023/168, 21.02.2023**: onama, tahliye korundu. Onanan BAM gerekçesine göre “içinde kiracı olarak bulunduğum” ibaresi sonradan düzenlenmeyi gösterir: “ibaresinin yazılması nedeni ile kira sözleşmesinden daha sonra düzenlendiği anlaşılan tahliye taahhüdünün geçerli olduğu”. Sınır: alıntı BAM'ındır; işyeri; ibare teslim için yalnız karinedir. `python scripts/pool.py get 979779900`
- **Yargıtay HGK, E. 2008/369, K. 2008/394, 28.05.2008**: direnme kararı oy çokluğuyla, kiraya veren yararına bozuldu. Anlaşmaya aykırı doldurma tanıkla ispatlanamaz, “yazılı delil de yoksa dayanılmış olması koşuluyla yemin delilinin söz konusu olabileceğinde” uyuşmazlık yoktur; hileyle imzalatma sahteliktir. Sınır: 818/HUMK dönemi; HMK karşılığını doğrula. `python scripts/pool.py get 202209-1215-0532-2008369-2008394-0adafbc2-c10f-47aa-94f6-c2327d600cce`
- **Yargıtay 8. HD, E. 2017/3527, K. 2017/9518, 21.06.2017**: icra mahkemesinin tahliye kararı kiraya veren aleyhine bozuldu. Takipten önce bildirim yapan eş kiracıdır; “icra takibindeki eksikliğin sonradan giderilmesi mümkün olmadığından” talep reddedilmeliydi. Sınır: temerrüt takibi; taahhüde kıyasen. `python scripts/pool.py get 353815800`

**Açık noktalar.**

- İtirazın iptali ve tahliye davası HUAK 18/B istisnasına girer mi; `B`'den önceki arabuluculuk başvurusu yeter mi?
- Takip `B` günü yapılabilir mi, yoksa erken mi sayılır?
- Yeni sözleşmenin etkisi: kontrol notundaki Yargıtay 3. HD, E. 2026/2877, K. 2026/2766 kanun yararına bozması havuzda yok; Resmî Gazete metninden doğrula.
- Yeni malik önceki malike verilmiş taahhüde dayanabilir mi; geç tahliye cezası TBK 346 ve 334/2 karşısında geçerli mi?

Rota kartı: `python scripts/tahliye.py yol taahhut` · emsaller: `python scripts/tahliye.py emsal taahhut`

## Gereksinim ve yeniden inşa (TBK 350)

**Dayanak ve kapsam.** Kiraya veren, kiralananı kendisi, eşi, altsoyu, üstsoyu veya kanunen bakmakla yükümlü olduğu kişiler için konut ya da işyeri gereksinimiyle kullanma zorunluluğu varsa (TBK 350/1) ya da yeniden inşa veya imar amacıyla esaslı onarım, genişletme veya değiştirme gerekli ve bu sırada kullanım imkânsızsa (350/2) sözleşmeyi dava ile sona erdirir (`python scripts/tbk.py 350`). Yalnız konut ve çatılı işyeri (TBK 339); arsa ve açık alan genel hükümlere tabidir (3. HD 2017/15002). İlamsız icra yolu yoktur; edinen için [yeni malik](#yeni-malik-tbk-351). İşlemler 01.07.2012'den önceyse 6570 uygulanabilir (HGK 2021/878; 6101'i resmî metinden doğrula).

**Koşullar.** Davacı kiraya verendir; kiraya veren olmayan malik de içtihaden dava açabilir. Malikler davacıysa paylı mülkiyette pay ve paydaş çoğunluğu, elbirliğinde bütün ortaklar aranır, resen gözetilir; eksiklikte önce muvafakat için süre verilir (3. HD 2018/1605; 6. HD 2013/4227). Liste sınırlıdır: gerçek kişi şirketinin, tüzel kişi ortağının ihtiyacı için dava açamaz (3. HD 2021/4476; 6. HD 2015/9922). İhtiyaç gerçek, samimi, zorunlu olmalı; geçici veya henüz doğmamış ihtiyaç yetmez; dava tarihinde bulunup yargılama boyunca sürmeli (HGK 2021/878). İşyerinde işe uygunluğu denetlenebilir bilirkişi raporuyla araştır. 350/2'de ispat yükü kiraya verendedir (proje, ruhsat, bilirkişi); havuzda esastan Yargıtay gerekçesi yok.

**Bildirim.** Belirli sürelide kanun ihtar aramaz (6. HD 2015/9532). İstisnalar: sözleşmede kiraya vereni de bağlayan, süre bitiminden önce yazılı ihtar yapılmazsa sözleşmenin yenilenmiş sayılacağı kaydı varsa ihbar süresinde ulaşmalı, yoksa sözleşme bir yıl uzar (3. HD 2025/1440); belirsiz sürelide TBK 328–329 dönemine en az üç ay önce yazılı bildirim yap (TBK 348). TBK 353 uzaması için “dava açacağım” diyen yazılı bildirim en geç dava süresi içinde ulaşmalı; her ihtar 353 bildirimi değildir. İçerik: ihtiyaçlı ve yakınlığı, konut veya işyeri, dönem bitimi, dava beyanı. Bütün kiracılara, taraf olmuş eşe (TMK 194) ihtiyaten ayrıca gönder; WhatsApp ve SMS'e dayanma. [Bildirim şablonu](tahliye-sablonlari.md#gereksinim-veya-dava-bildirimi-tbk-350-ve-353).

**Süreler.**

| Süre | Başlangıç olayı | Hesap | Araç | Güven |
| --- | --- | --- | --- | --- |
| Dava ve arabuluculuk penceresi | Sözleşme süresinin veya uzama yılının bitimi `E` | Başvuru en erken `G(E,1)`; ham son `A(E,1)`, temkinli son `A(G(E,-1),1)` | `python scripts/deadlines.py tbk350 <E>` | orta |
| Belirsiz süre: bildirim eşiği | Seçilen altı aylık dönem sonu `F = A(S,6k)` | Ulaşma `A(F,-3)`, temkinli `A(G(F,-1),-3)`; dava `A(F,1)` | `python scripts/deadlines.py takvim <F> --count 3 --unit ay --geri` | orta |
| Sözleşmesel ihbar | `E` ve sözleşmedeki süre `n` | Temkinli `A(G(E,-1),-n)`; UETS'de `G(U,5)` ≤ eşik | `python scripts/deadlines.py takvim <G(E,-1)> --count <n> --unit ay --geri` | orta |
| TBK 353 uzaması | Bildirimin en geç dava süresi içinde ulaşması | Ham `Y(E,1)`, temkinli `Y(G(E,-1),1)`; “bildirim + 365” değil | `python scripts/deadlines.py takvim <E> --count 1 --unit yil` | orta |
| HUAK 18/A/15 durması | Başvuru `B`, son tutanak `T` | Kalan süre `T`'den sonra işler; ayı 30 güne çevirme | araç yok | orta |

Pencere kaçırılırsa hak düşmez; `Y(E,1)` yeni `E` olur. Araç tatil, durma ve 353 uzaması uygulamaz ([süre rehberi](sure-hesaplama.md#kira-işlemleri-için-formüller)).

**Yol, görevli yer ve arabuluculuk.** Sulh hukuk, basit yargılama (HMK 4/1-a, 316/1-a; resmî metinden doğrula); kesin yetki yok. Dava 01.09.2023 veya sonrasında açılıyorsa arabuluculuk dava şartıdır; ilamsız tahliye olmadığından HUAK 18/B istisnası uygulanmaz (HUAK'ı resmî metinden doğrula). Başvuru hak doğduktan sonra ve süre içinde yapılır (3. HD 2025/3048); erken başvuruda dava usulden reddedilir, bu arada pencere kapanabilir. Hüküm 350/1 içindir; 350/2'de aynı zamanlamayı ihtiyaten uygula. Terditli davada her sebebin penceresini ayrı hesapla (3. HD 2017/17142). Yargılamada tahliyede giderlere dava tarihindeki haklılık esas alınır (HMK 331/1). [Ortak usul](#ortak-usul-arabuluculuk-görev-taraf-ve-tebligat); [dava iskeleti](tahliye-sablonlari.md#tahliye-dava-dilekçesi-iskeleti).

**Deliller.** Sözleşme ve özel şartlar; tapu, muvafakatler, nüfus kaydı; ihtiyaçlının kira sözleşmesi, dekont, tanık; diploma, ticaret sicili; tapu sorgusu; ihtar ve UETS kaydı; 350/2'de proje, ruhsat, keşif.

**Kiracı savunmaları.** Erken veya hiç arabuluculuk; erken ya da geç dava; ihbar kaydına uyulmaması; liste dışı ihtiyaçlı veya şirket ihtiyacı; geçici ya da sona ermiş ihtiyaç; boş ve elverişli başka taşınmaz (ispat kiracıda, 6. HD 2015/9532); paydaş çoğunluğu eksikliği. Kira artışı veya tespit davası tek başına samimiyetsizlik değildir (3. HD 2018/1605). Arsa savunması süre sonu tahliyesini açabilir (TBK 327). [Cevap iskeleti](tahliye-sablonlari.md#kiracı-cevap-dilekçesi-iskeleti).

**Tuzaklar.** İstanbul BAM 35. HD 2025/3212 istisnasını 26.05.2025 ve sonrasında açılan davalara taşıma. Davacının oturduğu yer için verdiği tahliye taahhüdünü kesin delil sayma (3. HD 2017/17142). 350/2'yi 6306 idari süreciyle karıştırma. 2025/3048'deki yazım ve atıf hatalarını aktarma ([ortak usul](#ortak-usul-arabuluculuk-görev-taraf-ve-tebligat)). İhtar üzerine kendiliğinden çıkan kiracı TBK 355 tazminatını kaybedebilir (3. HD 2019/871; [kontrol notu](tahliye-ve-uyarlama-kontrol.md#yeniden-kiralama-yasağı-çoğunluk-ve-karşıoy)).

**Doğrulanmış yerel kararlar.**

- **Yargıtay 3. HD, E. 2025/1495, K. 2025/3048, 26.05.2025**: uyuşmazlık Bursa BAM 4. HD görüşüyle giderildi (kesin). Başvurunun “tahliye davası açma hakkının doğumundan sonra diğer bir anlatımla dava açma süresi içerisinde yapılması gerektiğine” hükmetti. Sınır: 350/1; 351–352'ye otomatik taşıma. `python scripts/pool.py get 1155987500`
- **İstanbul BAM 35. HD, E. 2025/5438, K. 2025/3212, 30.12.2025**: usulden ret kaldırıldı, tahliyeye hükmedildi (kesin). “26.05.2025 tarihinden önce açılan davalar bakımından” erken başvuru nedeniyle ret öngörülemez sayıldı (dava 05.08.2024). Sınır: tek BAM dairesi; E./K. Dejure üst verisi. `python scripts/pool.py get aa156eaa-5348-4eef-963a-75a3f84b14a7`
- **Yargıtay 3. HD, E. 2024/2446, K. 2025/1440, 10.03.2025**: uyuşmazlık 36. HD görüşüyle giderildi. Sözleşmesel ihbar kiracı lehine geçerlidir; uyulmazsa “süre bitiminde kira sözleşmesinin bir yıl için uzamış olacağına” hükmetti. Sınır: kapsam sözleşme yorumudur. `python scripts/pool.py get 1163474000`
- **Yargıtay 3. HD, E. 2021/2159, K. 2021/4476, 21.04.2021**: tahliye kiracı yararına bozuldu. Şirket kuran davacıya: “gerçek kişi, şirketin ihtiyacı nedeniyle tahliye isteminde bulunamaz.” Sınır: yeni malik davası, HUMK temyizi. `python scripts/pool.py get 682264200`
- **Yargıtay 6. HD, E. 2015/6245, K. 2015/9532, 05.11.2015**: ret kiraya veren lehine bozuldu. Dönem sonundan sonraki dava süresinde; “annesiyle birlikte oturuyor olması başlı başına ihtiyacın varlığı için yeterlidir.” Sınır: kapatılan 6. HD. `python scripts/pool.py get 149048900`
- **Yargıtay HGK, E. 2017/1540, K. 2021/878, 29.06.2021**: direnme bozuldu; karşıoy yalnız usul ön sorununda. Dava tarihi yetmez, “bu ihtiyacın yargılama sırasında da devam etmesi gerekir.” Sınır: 6570 dönemi, yeni malik dosyası. `python scripts/pool.py get 686798500`

**Açık noktalar.**

- Pencerenin ilk ve son günü (`E` veya `G(E,1)`; `A(E,1)` veya `A(G(E,-1),1)`): mahkemeler farklı okudu.
- Arabuluculuk başvurusu TBK 353 bildirimi sayılır mı? İstanbul BAM 49. HD 2025/1002 bulunamadı.
- 26.05.2025 öncesi davalarda diğer BAM'lar ne diyor? Derlemedeki 3. HD 2026/3805 bulunamadı.
- 350/2 koşulları; belirsiz sürelide fesih bildirimi kurucu mu?

Rota kartı: `python scripts/tahliye.py yol ihtiyac` · emsaller: `python scripts/tahliye.py emsal ihtiyac`

## Yeni malik (TBK 351)

**Dayanak ve kapsam.** Sözleşmenin kurulmasından sonra kiralanan el değiştirirse yeni malik sözleşmenin tarafı olur (TBK 310); satış tahliye sebebi değildir, sözleşme aynı nitelikle sürer (3. HD 2022/1103). Gereksinimde (kişi çevresi 350 ile aynı) iki özel yol vardır: edinmeden başlayarak bir ay içinde yazılı bildirim ve altı ay sonra dava (351/1) ya da sözleşme süresinin bitiminden başlayarak bir ay içinde dava (351/2) (`python scripts/tbk.py 351`). Kiraya veren sıfatıyla TBK 350 de açıktır; yararına olanı seçer (HGK 2021/878). Yalnız konut ve çatılı işyeri (TBK 339); arsada 351'e dayanılamaz (3. HD 2017/15002). Edinme ve bildirim 01.07.2012'den önceyse kişi çevresi daha dar olan mülga 6570 m.7/d gündeme gelir (6101'i resmî metinden doğrula).

**Koşullar.** Sözleşme edinmeden önce kurulmuş olmalı; yeni malik kiracıyla yeni sözleşme yaptıysa 350'yi değerlendir (çıkarım). Edinme günü `D`'yi belgeyle sapta: satışta tapu tescili; miras, ihale ve mahkeme kararında mülkiyetin geçtiği gün (TMK 705/2; resmî metinden doğrula). Gereksinim gerçek, samimi, zorunlu olmalı ve yargılama boyunca sürmeli (HGK 2021/878); gerçek kişinin şirketi kapsam dışıdır (3. HD 2021/4476; 6. HD 2015/9921). Kirada oturma ihtiyaç karinesidir (6. HD 2014/10948). Paylı ve elbirliği edinmede çoğunluk kuralı 350 dosyalarından kıyasla uygulanır ([gereksinim](#gereksinim-ve-yeniden-inşa-tbk-350)). Tüzel kişide ihtiyacın kendisine ait olduğunu göster; kısa gerekçeli 6. HD 2016/3567'den genelleme yapma.

**Bildirim.** 351/1'de kurucu şarttır: yazılı bildirim edinmeden bir ay içinde kiracıya tebliğ edilmiş olmalı; keşide yetmez, eksiklik sonradan giderilemez (3. HD 2017/12812). UETS'de tebliğ `G(U,5)`'tir. İçerik: tescil tarihi ve yevmiye, yeni malik sıfatı, ihtiyaçlı ve yakınlığı, konut veya işyeri, 351/1'e dayanıldığı ve altı ay sonra dava açılacağı. Her kiracıya, TMK 194 bildirimiyle taraf olmuş eşe ihtiyaten ayrıca gönder (çıkarım). Önceki malikin ihtarı yerine geçmez; WhatsApp, SMS ve e-postaya dayanma. 351/2 ve 350'de kanun bildirim aramaz, ama önceki malikle yapılmış sözleşmedeki kiraya veren aleyhine ihbar kaydı yeni maliki de bağlayabilir (3. HD 2025/1440 ve 2025/3576). [Bildirim şablonu](tahliye-sablonlari.md#yeni-malik-bildirimi-tbk-3511).

**Süreler.** `D` edinme; `L` dönemin son kullanım günü (`python scripts/hesap.py donemler --baslangic <S>` “bitiş”); `N = G(L,1)` yıldönümü.

| Süre | Başlangıç olayı | Hesap | Araç | Güven |
| --- | --- | --- | --- | --- |
| 351/1 bildirimin tebliği | `D` | Ham `A(D,1)`; “edinme günü de dahil” okumasıyla temkinli `G(A(D,1),-1)` | `python scripts/deadlines.py tbk351 <D>` | yüksek |
| 351/1 bekleme, en erken başvuru | `D` | Bekleme `A(D,6)` sonunda dolar; arabuluculuk ve dava en erken `G(A(D,6),1)` | `python scripts/deadlines.py tbk351 <D>` | orta |
| 351/1 son sınır | `G(A(D,6),1)` gününde yürüyen dönemin sonu `L` | `G(A(D,6),1)`–`L`; HGK obiteri nedeniyle gecikme | araç yok | düşük |
| 351/2 ve 350 dönem sonu | `L` ve `N` | En erken `G(N,1)`; temkinli son `A(L,1)` | `python scripts/deadlines.py takvim <L> --count 1 --unit ay` | orta |
| Sözleşmesel ihbar eşiği | `L` ve sözleşmedeki süre `n` | `A(L,-n)`; eşik `D`'den önceyse o dönem sonu kaybedilebilir | `python scripts/deadlines.py takvim <L> --count <n> --unit ay --geri` | orta |
| TBK 353 uzaması | 351/2'de `A(L,1)`'e kadar ulaşan yazılı dava bildirimi | Temkinli `Y(L,1)`; 351/1'e uygulanışı belirsiz | `python scripts/deadlines.py takvim <L> --count 1 --unit yil` | düşük |

Örnek: `D` = 16.05.2026 için bildirim ham 16.06.2026, temkinli 15.06.2026; en erken başvuru 17.11.2026. Arabuluculuk bildirim süresini ve altı aylık beklemeyi durdurmaz; araç tatil ve durma uygulamaz ([süre rehberi](sure-hesaplama.md#kira-işlemleri-için-formüller)).

**Yol, görevli yer ve arabuluculuk.** Yalnız dava: sulh hukuk, basit yargılama (HMK 4/1-a, 316/1-a; resmî metinden doğrula). İlamsız icra yolu yoktur, HUAK 18/B istisnası uygulanmaz; dava 01.09.2023 veya sonrasında açılıyorsa arabuluculuk dava şartıdır (HUAK'ı resmî metinden doğrula). 351/1'de erken başvuru Yargıtay'ca esastan çözülmedi; 2025/3048'i kıyasla uygula, başvuruyu `G(A(D,6),1)` veya sonrasında ve `L`'den önce yap. Önceki malikin başvurusuna güvenme; destekleyen karar bulunamadı. Terditli dava kurulabilir. [Ortak usul](#ortak-usul-arabuluculuk-görev-taraf-ve-tebligat).

**Deliller.** Tapu kaydı (tescil tarihi, yevmiye, paylar); önceki sözleşme ve özel şartları; ihtarname ve tebliğ şerhi veya UETS kaydı; son tutanak; ihtiyaçlının kira sözleşmesi ve dekontları; ticaret sicili; keşif.

**Kiracı savunmaları.** Bildirim süresinde tebliğ edilmedi (resen denetlenir); başvuru veya dava `A(D,6)` dolmadan yapıldı; 351/2'de süre geçti ya da ihbar kaydına uyulmadı; ihtiyaç samimi değil veya kişi çevresi dışında; paydaş çoğunluğu eksik. Muvazaa savunması dinlenmez (6. HD 2014/10948); ihtiyacın samimiyetine yönel. Tarihsiz ilan fotoğrafı karineyi çürütmez (Gaziantep BAM 2017/286). Arsa savunması süre sonu tahliyesine kapı açar (TBK 327; 3. HD 2022/1103). [Cevap iskeleti](tahliye-sablonlari.md#kiracı-cevap-dilekçesi-iskeleti).

**Tuzaklar.** Keşideyi tebliğ, altı ayı son başvuru süresi sanma. `L` ile `N`'yi karıştırma: `hesap.py` “bitiş” `L`'yi, `deadlines.py tbk350` ve `takvim` yıldönümünü işler. İlk dönem sonu `A(D,6)`'dan önceyse 351/2 penceresini kaçırma. 350 kararlarını (2025/3048, 2025/1440) kıyas olduğunu yazmadan aktarma.

**Doğrulanmış yerel kararlar.**

- **Yargıtay 3. HD, E. 2017/4691, K. 2017/12812, 27.09.2017**: tahliye kiracı lehine bozuldu. 16.05.2014 edinme, 19.06.2014 tebliğ: “edinmeyi izleyen bir ay içerisinde bildirimin tebliği zorunlu olup bunun sonradan giderilmesi mümkün değildir.” Sınır: arabuluculuk öncesi; dönem sonu yolunu kapatmaz. `python scripts/pool.py get 371154500`
- **Yargıtay HGK, E. 2017/1540, K. 2021/878, 29.06.2021**: direnme yeni malik lehine (giderler yönünden) bozuldu; karşıoy yalnız usul ön sorununda. “Yeni malikin bu seçeneklerden hangisi yararına ise onu tercih etme hakkı vardır.” Sınır: 6570 dönemi; par. 18'deki “takip eden altı ay” obiterdir. `python scripts/pool.py get 686798500`
- **Gaziantep BAM 3. HD, E. 2017/288, K. 2017/286, 21.03.2017**: kiracının istinafı esastan reddedildi (kesin). 351/1 bildirimi geçmişti; TBK 350'ye dayanan dönem sonu davası için “süresinde olduğunun kabulü gerekecektir” dedi. Sınır: künye Dejure üst verisi; keşide de süre dışındaydı. `python scripts/pool.py get 9ca8de68-9bcb-444d-9c07-3257427162e2`
- **Yargıtay 3. HD, E. 2024/2446, K. 2025/1440, 10.03.2025**: uyuşmazlık 36. HD görüşüyle giderildi. Kiraya veren tarafından “sözleşmede kararlaştırılmışsa fesih ihbar şartına uyulması gerektiği” kabul edildi. Sınır: 350 kararı; benimsenen dosya yeni malik dosyası değil, 2025/3576 yeni malik dosyasında ayrılmadı. `python scripts/pool.py get 1163474000`
- **Yargıtay 6. HD, E. 2014/9523, K. 2014/10948, 13.10.2014**: ret yeni malik lehine bozuldu: “iktisabın muvazaalı olduğu savunması bu dava içerisinde dinlenemez.” Sınır: kapatılan 6. HD; süre tartışılmadı. `python scripts/pool.py get 97355400`

**Açık noktalar.**

- 351/1'de `A(D,6)` dolmadan arabuluculuk yeterli mi? [Kontrol notundaki](tahliye-ve-uyarlama-kontrol.md) 3. HD 2025/3292–5039 havuzda yok.
- Son sınır “sözleşme sonuna kadar” mı, HGK'nın “takip eden altı ay”ı mı; HUAK 18/A/15 bu sınırı uzatır mı?
- Miras ve ihaleyle edinme; önceki malike yapılmış aile konutu bildiriminin yeni malike etkisi.

Rota kartı: `python scripts/tahliye.py yol yeni_malik` · emsaller: `python scripts/tahliye.py emsal yeni_malik`

## On yıllık uzama ve belirsiz süreli kira (TBK 347)

**Dayanak ve kapsam.** TBK 347/1 c.3: belirli süreli konut ve çatılı işyeri kirasında kiraya veren, on yıllık uzama süresi sonunda, bu süreyi izleyen her uzama yılının bitiminden en az üç ay önce bildirimde bulunarak sebep göstermeden sözleşmeye son verebilir. 347/2: belirsiz süreli kirada kiraya veren, kiranın başlangıcından on yıl geçtikten sonra genel hükümlere (TBK 328–329) göre fesih bildirimi yapar (`python scripts/tbk.py 347`). Karma kiralananda baskın vasfı tahsis amacına göre belirle; açık alanda TBK 327 uygulanır ([rejim kontrolü](kira-rejimi-ve-taraflar.md#önce-rejimi-belirle)). Ürün kirası ve 2886/75 idare kirası dışarıdadır; 6217 geçici 2 ertelemesi 347'yi kapsamaz. 01.07.2012 öncesi belirli süreli sözleşmede 6101 geçici 2 eşiklerini (01.07.2014, 01.07.2017) uygula (HGK aktarımı; resmî metinden doğrula). Yeni malik hakkı TBK 310 ile kullanır; salt el değiştirme süreyi yeniden başlatmaz (3. HD 2022/1103 kıyası).

**Koşullar.**

- İlk süre `E`'de bitmiş, yeni sözleşme yapılmadan on kez birer yıl uzamış olmalı. Yeni süre ve bedelle yapılan sözleşme süreyi yeniden başlatır (HGK 2021/614 çoğunluk); yalnız bedel güncelleyen protokolü yeni sözleşme varsayma.
- Fesih, on yıllık uzamayı izleyen bir uzama yılının sonu `F = Y(E,11)` (sonra `Y(E,11+k)`) için yapılır; yazılı bildirim hedef yıl içinde, `F`'den en az üç ay önce ulaşır. “Başlangıç + 10 yıl” yanlıştır.
- Belirsiz sürelide `Y(S,10)` geçmiş, bildirim yerel âdet yoksa başlangıçtan sayılan altı aylık dönem sonu `P`'den üç ay önce ulaşmış olmalı; geç bildirim sonraki döneme kayar (TBK 328/2).
- Bildirim ve dava bütün kiraya verenlerce bütün kiracılara yöneltilir (12. HD 2025/7823, icra bağlamından kıyas); TBK 349/3 ile taraf olmuş eşe ayrıca.

**Bildirim.** Yazılı ve imzalı yap (TBK 348, 14); noter ihtarnamesi kullan. WhatsApp, SMS veya imzasız e-postaya güvenme. İçerik: TBK 347'ye dayanıldığı, sona erme tarihi `F`, tahliye ve teslim talebi; sebep gerekmez. Başka sebebe (TBK 350) de dayanılacaksa onun koşullarını ayrıca karşıla. Keşide değil ulaşma esastır; UETS'de `G(U,5)` (`python scripts/deadlines.py uets <U>`). Vekaletnamede fesih ve ihtar yetkisini ara. [Şablon](tahliye-sablonlari.md#on-yıllık-uzama-sonunda-fesih-bildirimi-tbk-3471).

**Süreler.**

| Süre | Başlangıç olayı | Hesap | Araç | Güven |
| --- | --- | --- | --- | --- |
| Kiraya verenin bildirimi (347/1) | İlk süre bitimi `E` | `F = Y(E,11)`; `Y(E,10)` ≤ tebliğ ≤ `A(G(F,-1),-3)` | `python scripts/deadlines.py tbk347 <E>` veya `python scripts/hesap.py tahliye-10yil --baslangic <S> --sure-yil <n>` | yüksek |
| 6101 geçici 2 geçişi | Eşik `T` (01.07.2014 veya 01.07.2017) | İlk `Y(E,k)` ≥ `T` (k ≥ 11) = `F*`; tebliğ ≤ `A(F*,-3)`, `T`'den önce olabilir | `python scripts/deadlines.py takvim <F*> --count 3 --unit ay --geri` | orta |
| En erken dava ve arabuluculuk | Uzama yılı sonu `F` | `F` günü dahil sonrası | araç yok | yüksek |
| Dava üst sınırı | `F` | Kanunda yok; ihtiyaten `A(G(F,-1),1)` | `python scripts/deadlines.py takvim <G(F,-1)> --count 1 --unit ay` | düşük |
| Belirsiz süreli fesih (347/2) | Kira başlangıcı `S` | Tebliğ ≥ `Y(S,10)`; `P = A(S,6k)`; tebliğ ≤ `A(P,-3)` | `python scripts/deadlines.py takvim <P> --count 3 --unit ay --geri` | orta |
| Kiracının bildirimi | Süre veya uzama yılı sonu `E` | `G(E,-15)`; `E` yıldönümüyse temkinli `G(G(E,-1),-15)` | `python scripts/deadlines.py takvim <E> --count 15 --unit gun --geri` | yüksek |

Araçlar geçişi, yeni sözleşmeyi, tatili ve arabuluculuk durmasını uygulamaz; `hesap.py` ilk süre verilmezse 12 ay varsayar ([süre rehberi](sure-hesaplama.md#kira-işlemleri-için-formüller)). TBK 353 “dava yoluyla” bölümündedir; 347 davasına uzama olarak uygulama.

**Yol, görevli yer ve arabuluculuk.** Sulh hukukta tahliye davası (HMK 4/1-a, basit yargılama; resmî metinden doğrula). Dava 01.09.2023 veya sonrasında açılıyorsa arabuluculuk dava şartıdır (HUAK 18/B/1-a, resmî metinden doğrula). Başvuruyu `F` günü veya sonrasında yap: 3. HD 2025/3048 erken başvuruyu TBK 350 için yetersiz saymıştır; 347 için karar yok. İİK 272 ilamsız yolunun 347 feshine uygulanabildiği doğrulanmadı; ona güvenip arabuluculuğu atlama. Çatılı işyeri süre bitiminde kendiliğinden boşalmaz; ilamsız yıkım tazminat doğurur (3. HD 2025/4234). [Ortak usul](#ortak-usul-arabuluculuk-görev-taraf-ve-tebligat).

**Deliller.** Bütün sözleşme ve protokoller; tapu, edinme tarihi, mirasçılık belgesi; ihtarname ve tebliğ kaydı; vekaletname; aile konutu bildirimi; `F`'den sonraki ödemelerin çekinceli tahsil kaydı; son tutanak; gerekirse keşif; geçiş hesabı.

**Kiracı savunmaları.** Süre hesabı (ilk süre, yeni sözleşme); bildirimin zamanı, şekli ve yetkisi; erken dava; eksik kiraya veren veya eş; arabuluculuk. Geçiş savunması yalnız hedef yıl sonu eşikten önceyse işe yarar (HGK 2021/1517). Daha uzun sözleşmesel ihbar şartını kıyasen ileri sür (3. HD 2025/1440, TBK 350); TMK 2 zayıftır.

**Tuzaklar.** Bildirimi `Y(E,10)`'dan önce gönderme; hedef yıldan önceki bildirimi geçerli sayan karar yok. `F`'den sonra koşulsuz “kira” tahsil etme; çekinceyle al (zımni yenileme riski, doğrulanmadı). [Derlemedeki](derleme-v5.md) “dava açma süresi” başlığını kesin bir aylık süre sayma; atfedilen iki BAM kararı havuzda yok.

**Doğrulanmış yerel kararlar.**

- **Yargıtay HGK, E. 2017/1546, K. 2021/1517, 30.11.2021**: direnme bozuldu, kiraya veren lehine (oybirliği). Geçiş ertelemesi bildirimi ertelemez; 14.03.2014'te tebliğ edilip 01.07.2014'ü hedefleyen bildirim süresindedir: “bildirim tarihinin de 01.07.2014 tarihine kadar ertelendiği anlamı çıkarılamamalıdır”. Sınır: HUMK dönemi. `python scripts/pool.py get 724738400`
- **Yargıtay HGK, E. 2017/458, K. 2021/614, 25.05.2021**: direnme bozuldu, kiracı lehine (oy çokluğu, iki karşıoy). Çoğunluk: “her dönemde yapılan yenileme sözleşmesi on yıllık süreyi yeniden başlatır”. Sınır: karşıoylar farklı ayrımlar yapar; bedel protokolünü çözmez. `python scripts/pool.py get 686728500`
- **Yargıtay 3. HD, E. 2017/3032, K. 2017/6383, 02.05.2017**: tahliye hükmü kiracı lehine bozuldu. 31.07.2015 davası erkendir: “Davanın en erken dönem sonu olan 01.08.2015 tarihinden sonra (bu tarih dahil) açılması gerekir.” Sınır: üst sınırı çözmez. `python scripts/pool.py get 361252700`
- **İstanbul BAM 36. HD, E. 2021/1010, K. 2023/2382, 19.10.2023**: kiraya verenin istinafı esastan reddedildi (kesin). 1+10+1 hesabı; ihtar “bu tarihten sonra 01.11.2021 kira süresinin dolmasından 3 ay öncesinde tahliye ihtarnamesinin tebliğ edilerek” yapılmalıydı; 03.11.2020 davası erken. Sınır: BAM kararı; künye Dejure üst verisi; 04.06.2020 ihtarının erkenliği ilk derece gerekçesidir. `python scripts/pool.py get bb12b6b8-f33f-43ff-aded-6c9a2d166985`
- **Yargıtay 3. HD, E. 2017/7129, K. 2017/17713, 14.12.2017**: süre yönünden ret kiraya veren lehine bozuldu. Belirsiz sürelide geç ihtar düşmez: “TBK' nun 328/son maddesi uyarınca bir sonraki fesih dönemi için geçerli olacağından”. Sınır: hedef dönem kararda adıyla geçmez. `python scripts/pool.py get 389655600`
- **Yargıtay 3. HD, E. 2022/202, K. 2022/1103, 15.02.2022**: BAM kararı kiracı lehine bozuldu. “Bu durumda kiraya verenin değişmesi akdi ve akdin niteliğini ortadan kaldırmaz.” Sınır: 347 hakkında değil, kıyasla kullan; kiralanan açık alan sayıldı. `python scripts/pool.py get 748198200`

**Açık noktalar.**

- Dava açmanın üst sınırı: bir aylık süre (TBK 350, 352 kıyası) mı, zımni yenileme mi?
- 2025/3048'in arabuluculuk zamanlaması 347'ye taşınır mı; İİK 272 yolu 347 feshine uygulanır mı?
- Hedef yıldan önce veya on yıl dolmadan yapılan bildirim (347/1, 347/2) sonraki uygun dönem için geçerli olur mu?
- 6101 geçici 2 resmî metni ve AYM E.2015/102, K.2016/151 incelemesinin sonucu doğrulanmadı.

Rota kartı: `python scripts/tahliye.py yol on_yillik_uzama` · emsaller: `python scripts/tahliye.py emsal on_yillik_uzama`

## Özen ve komşulara saygı borcuna aykırılık (TBK 316)

**Dayanak ve kapsam.** TBK 316/1: kiracı kiralananı sözleşmeye uygun ve özenle kullanır, aynı taşınmazda oturanlara ve komşulara saygı gösterir. 316/2: konut ve çatılı işyerinde kiraya veren en az otuz gün süre vererek aykırılığın giderilmesini, aksi hâlde sözleşmeyi feshedeceğini yazılı olarak ihtar eder; diğer kiralarda ihtarsız yazılı bildirimle hemen fesheder (ürün kirasında TBK 358 atfıyla). 316/3: kasten ağır zarar, sürenin yararsızlığı veya çekilmezlik hâlinde konut ve çatılı işyerinde de yazılı bildirimle derhal fesih (`python scripts/tbk.py 316`). Tipik hâller: amaç dışı kullanım, izinsiz tadilat (TBK 321), yazılı rızasız alt kira veya devir (322/2), komşuları rahatsız etme. Rejimi baskın vasıf belirler ([rejim kontrolü](kira-rejimi-ve-taraflar.md#önce-rejimi-belirle)). İhtar ve fesih 01.07.2012'den önce tamamlanmışsa 818 BK 256 uygulanır; orada asgari 30 gün yoktur. 316 ve 322, 6217 geçici 2 ile ertelenmemiştir.

**Koşullar.**

- Davacı kiraya verendir; paylı mülkiyette pay ve paydaş çoğunluğu, elbirliğinde bütün ortaklar aranır (6. HD 2013/4227 kıyası; TMK'yi resmî metinden doğrula).
- Aykırılık önemli, doğrudan kiralananın kullanımıyla ilgili ve kiralananın içinde olmalı; rızaya aykırı kullanımda ayrıca zarar aranmaz (3. HD 2018/11200). Sözleşme dışı alanda tahliye değil, el atmanın önlenmesi ve ecrimisil istenir.
- İhtar tebliğ edilmiş, süre dolmuş, aykırılık süreden sonra da sürüyor olmalı.
- Kiraya veren yazılı veya zımni rıza göstermemiş olmalı; alt kirada rıza yazılıdır. Rıza verilen değişiklikte yazılı anlaşma yoksa eski hâle getirme istenemez (321/2).
- Sözleşmeye konulan tahliye şartı tek başına sebep değildir (3. HD 2024/217).

**Bildirim.** Yazılı ve imzalı yap (TBK 14–15), noter kullan; imzasız WhatsApp, SMS veya e-postaya güvenme. İçerik: aykırılığın somut tanımı (eylem, sözleşme maddesi, alan), istenen giderim, en az 30 gün süre, giderilmezse sözleşmenin feshedileceği uyarısı. 3. HD 2026/1193 “tahliye davası açılacağı” uyarısını yeterli saydı; yine de kanundaki fesih ifadesini yaz. Giderim istemeyip yalnız tahliye isteyen ihtar yetmez (HGK 2014/83). Muhatap: bütün kiracılar; ihtiyaten alt kiracı ve kullanıcı (TBK 322/3); taraf olmuş eşe fesih bildirimi ayrıca (TBK 349/3), giderim ihtarı ihtiyaten. [Şablon](tahliye-sablonlari.md#özen-borcuna-aykırılık-ihtarnamesi-tbk-316).

**Süreler.**

| Süre | Başlangıç olayı | Hesap | Araç | Güven |
| --- | --- | --- | --- | --- |
| Giderim süresi (316/2) | İhtarın tebliği `T`; UETS'de `T = G(U,5)` | `G(T,30)`; daha uzun süre verildiyse `G(T,n)` | `python scripts/deadlines.py tbk316 <T>` (`otuzuncu_gun`); `n` gün için `python scripts/deadlines.py takvim <T> --count <n> --unit gun` | yüksek |
| En erken fesih, arabuluculuk, dava | Süre sonu `S`; tatildeyse izleyen iş günü `S'` (TBK 93) | `G(S',1)`; kanuni üst sınır yok | `python scripts/deadlines.py tbk316 <T>`, tatili ve `+1` günü elle uygula | orta |
| Derhal fesih (316/3; diğer kiralar) | Yazılı bildirimin ulaşması | Bekleme yok; UETS'de `G(U,5)` | `python scripts/deadlines.py uets <U>` | orta |
| Olağanüstü fesih (TBK 331, 347/3) | Bildirimin ulaşması `B` | `A(B,3)` | `python scripts/deadlines.py takvim <B> --count 3 --unit ay` | orta |
| Arabuluculuk süreci (HUAK 18/B) | Görevlendirme `g` | `G(g,21)`; uzatmayla `G(g,28)` | `python scripts/deadlines.py takvim <g> --count 3 --unit hafta` | orta |

`G(T,31)` kısayolunu kullanma; tatil son günü kaydırabilir. `tbk315` ön ayarı aynı ham tarihi verse de temerrüt içindir; 316 ihtarında `tbk316` kullan. HUAK sürelerini resmî metinden doğrula ([süre rehberi](sure-hesaplama.md#tatil-arabuluculuk-ve-tebligat-düzeltmeleri)).

**Yol, görevli yer ve arabuluculuk.** Tek yol sulh hukukta tahliye davasıdır (HMK 4/1-a, basit yargılama; yetkiyi resmî metinden doğrula). İlamsız yol (İİK 269, 272) ve HUAK 18/B/1-a istisnası yoktur: dava 01.09.2023 veya sonrasında açılıyorsa arabuluculuk dava şartıdır (resmî metinden doğrula). Başvuruyu giderim süresi bittikten veya derhal fesih bildirimi ulaştıktan sonra yap (316 için karar yok; 2025/3048 kıyası). Fesih tahliye sağlamaz; tek yanlı el koyma, su veya elektrik kesme ve yıkım sözleşme ihlalidir (3. HD 2022/7594; 3. HD 2025/4234). Alt kirada kullananı da davalı göster. Kira borcu da varsa [temerrüt yolunu](#temerrüt-tbk-315-ve-ilamsız-tahliye-takibi) ayrı değerlendir. [Ortak usul](#ortak-usul-arabuluculuk-görev-taraf-ve-tebligat).

**Deliller.** Sözleşme (amaç, alt kira, tadilat izni, kroki, teslim tutanağı); ihtar ve tebliğ belgesi; ihtardan önce ve süre sonunda iki delil tespiti (HMK 400 vd., doğrula); uzman bilirkişi (sektör, statik, fen); tanık, yönetim ve kolluk tutanakları; ruhsat, sicil ve SGK kayıtları; tapu; son tutanak.

**Kiracı savunmaları.** İhtarın şekli, süresi ve içeriği; süre içinde giderim; önemsiz, kullanımla ilgisiz veya kiralanan dışındaki aykırılık; yazılı izin veya zımni rıza (alt kirada zayıf); teslimdeki ayıp (TBK 318); 316/3 koşullarının ispatsızlığı; baskın vasıf nedeniyle ihtarsız feshin geçersizliği; arabuluculuk veya taraf eksikliği. [Cevap iskeleti](tahliye-sablonlari.md#kiracı-cevap-dilekçesi-iskeleti).

**Tuzaklar.** HGK 2013/859'daki bir günlük giderim süresi tartışılmamıştır; o kararı (818 dönemi, oy çokluğu, fişsiz satışta tahliye) karşıoyunu ve sonraki doğrudan kullanım ölçütünü belirtmeden aktarma. Ayıp bildirimi TBK 318'dedir (317 değil); yaptırımı tazminattır, tahliye değil. Bozmaları tahliye hükmü gibi sunma. Derlemedeki Antalya BAM 6. HD 2019/1061 K. ve Bursa BAM 4. HD 2025/74 K. havuzda yok; atıf yapma.

**Doğrulanmış yerel kararlar.**

- **Yargıtay 3. HD, E. 2025/4165, K. 2026/1193, 04.03.2026**: onama; tahliye kiraya veren lehine kesinleşti. İzinsiz taşıyıcı sistem müdahalesinde ihtar yeterli: “30 günlük süre verildiğinin ve bu sürede aykırılık giderilmediğinde tahliye davası açılacağının usulünce bildirildiğinin”. Sınır: HUAK öncesi; tacir kiracı. `python scripts/pool.py get 1216459800`
- **Yargıtay 3. HD, E. 2018/6432, K. 2018/11200, 07.11.2018**: ret kiraya veren lehine bozuldu. Kafeterya yerine lokanta: “onun rızasına aykırı her kullanma, akde aykırı bir kullanmadır”; aykırılık süreden sonra da sürmeli, sektör uzmanı dinlenmeli. Sınır: bozma. `python scripts/pool.py get 454723600`
- **Yargıtay 3. HD, E. 2018/2258, K. 2018/6300, 04.06.2018**: ret kiraya veren lehine bozuldu. Franchise savunmasında 322/2 yazılı rızası aranır; “davalının yazılı muvafakate ilişkin varsa delillerinin ibrazı sağlanıp” karar verilmeli. Sınır: bozma; zımni rıza tartışılmadı; künyeyi doğrula. `python scripts/pool.py get 020e7adb-ba73-49cc-8228-2aa4bdf70f18`
- **Yargıtay HGK, E. 2013/378, K. 2014/83, 05.02.2014**: direnme bozuldu, kiracı lehine (oybirliği). Giderim süreli ihtar yoktu; ortak otopark işgali için: “Sözleşme kapsamı dışında kalan taşınmaz kısmı hakkında akde aykırılık veya pek fena kullanım nedeniyle taşınmazın tahliyesi istenemez.” Sınır: 818 BK 256 dönemi. `python scripts/pool.py get 84014200`
- **Yargıtay 3. HD, E. 2017/4483, K. 2019/189, 16.01.2019**: fesih hükmü kiracı lehine bozuldu. Kötü söz ispatlanamadı; hurdacılığın kiralananda yapılıp yapılmadığı araştırılmalı: “Sözleşme dışında kalan taşınmaz kısmı hakkında akde aykırı davranış nedenine dayanarak kira sözleşmesinin feshinin istenemeyeceği kuşkusuzdur.” Sınır: bozma. `python scripts/pool.py get 477596700`
- **Yargıtay 3. HD, E. 2022/5351, K. 2022/7594, 11.10.2022**: BAM kararı kaldırıldı, ret kiracı lehine bozuldu. Zorla boşaltma sözleşme ihlalidir: “mahkeme kararı ile tahliye ilamı alınmadığı sürece akdin sona erdiğinden söz edilemez.” Sınır: fesih temerrüde ve sözleşme hükmüne dayanıyordu. `python scripts/pool.py get 838265700`

**Açık noktalar.**

- Giderim süresi dolmadan yapılan arabuluculuk başvurusu yeter mi?
- Süre sonunda ayrı fesih bildirimi gerekir mi; sonradan giderimin etkisi ne?
- Kullanımla ilgisiz ihlaller (fişsiz satış, ciro) TBK döneminde tahliye sebebi mi?
- Alt kirada zımni rıza; konutun ofis veya turizm amaçlı (7464 s.K.) kullanımı.

Rota kartı: `python scripts/tahliye.py yol akde_aykirilik` · emsaller: `python scripts/tahliye.py emsal akde_aykirilik`

## Kiracının konutu (TBK 352/3) ve diğer sona erme halleri

**Dayanak ve kapsam.** TBK 352/3: kiracının veya birlikte yaşadığı eşinin aynı ilçe veya belde belediye sınırları içinde oturmaya elverişli bir konutu varsa ve kiraya veren bunu sözleşmenin kurulması sırasında bilmiyorsa, sözleşmenin bitiminden başlayarak bir ay içinde sözleşmeyi dava yoluyla sona erdirebilir (`python scripts/tbk.py 352`). İhtiyaç ve ön ihtar aranmaz; ilamsız takip yolu yoktur. Diğer haller: önemli sebeple fesih (TBK 331), kiracının iflası (332), ölümü (333, 356) ve erken geri verme (325); ürün kirasında 369–371 önce gelir (TBK 358).

**Koşullar.** 352/3 için süren kira ilişkisi, kiracıya veya birlikte yaşadığı eşine ait konut (çocuğun veya anne-babanın konutu girmez), aynı ilçe veya belde sınırı, oturmaya elverişlilik ve kiraya verenin sözleşme kurulurken bilmemesi gerekir. Elverişlilikte konutun varlığı ile davalının sosyal durumu ve aile nüfusu birlikte aranır. Birden çok kiraya verende pay ve paydaş çoğunluğunu, elbirliğinde bütün ortakları ara (350 kararından kıyasen). Bütün kiracıları ve TMK 194 bildirimi yapmış eşi davalı göster (8. HD 2017/9518). 331'de çekilmezlik yaratan önemli sebep, yazılı bildirim (TBK 348) ve üç aylık süre (TBK 329) gerekir; kullanım aykırılığı TBK 316 rejimindedir. 332'de kiracı ve iflas masasına yazılı uygun süre verilir. 333'te feshi mirasçılar birlikte yapar; kiraya verenin ölüme dayalı fesih hakkı yoktur, birlikte oturanlar sözleşmeyi sürdürebilir (356).

**Bildirim.** TBK 353 uzaması için “dava açacağım” içerikli yazılı bildirimi `A(E,1)` dolmadan kiracıya, taraf olmuş eşe ayrıca ulaştır; sebebi ve konutun adresini yaz ([bildirim şablonu](tahliye-sablonlari.md#gereksinim-veya-dava-bildirimi-tbk-350-ve-353)). 353'ün 352/3'e uygulanması sistematik yorumdur. 331 ve 333 fesih bildirimleri yazılı değilse geçersizdir (TBK 348); aile konutunda kiracı feshi için eşin açık rızasını al (TBK 349/1).

**Süreler.**

| Süre | Başlangıç olayı | Hesap | Araç | Güven |
| --- | --- | --- | --- | --- |
| 352/3 dava süresi | Sözleşme veya uzama yılı bitimi `E` | `A(E,1)` | `python scripts/deadlines.py takvim <E> --count 1 --unit ay` | orta |
| 352/3 arabuluculuk | `E` | `E` < başvuru ≤ `A(E,1)`; tutanağa kadar durma | araç yok | düşük |
| TBK 353 uzaması | Bildirimin ulaşması ≤ `A(E,1)` | Aday `Y(E,1)` | `python scripts/deadlines.py takvim <E> --count 1 --unit yil` | orta |
| 331 fesih | Yazılı bildirimin ulaşması `T` | En erken `A(T,3)` | `python scripts/deadlines.py takvim <T> --count 3 --unit ay` | düşük |
| 333 mirasçı feshi | En yakın fesih dönemi sonu `F` | Ulaşma ≤ `A(F,-3)` | `python scripts/deadlines.py takvim <F> --count 3 --unit ay --geri` | orta |
| 347/1 kiracı bildirimi | Belirli sürenin bitimi `E` | `G(E,-15)`; `E` yıldönümüyse temkinli `G(G(E,-1),-15)` | `python scripts/deadlines.py takvim <E> --count 15 --unit gun --geri` | yüksek |

`tbk352` yalnız 352/1 içindir. 325'teki makul süreyi uzman bilirkişi belirler; araç yok. Tatil ve durma: [süre rehberi](sure-hesaplama.md#kira-işlemleri-için-formüller).

**Yol, görevli yer ve arabuluculuk.** 352/3, 331, 332 ve 325 kaynaklı davalar sulh hukukta basit yargılamayla görülür (HMK 4/1-a, 316; doğrula). 01.09.2023 ve sonrasında açılan davada dava şartı arabuluculuk aranır; ilamsız tahliye istisnası uygulanmaz (HUAK 18/B/1-a, resmî metinden doğrula). 325 alacağında ilamsız takip arabuluculuk gerektirmez, itirazın iptali davası gerektirir. Kira ilişkisi yoksa el atmanın önlenmesi ve ecrimisil asliye hukukta görülür (doğrula); kira varken bu yolu seçme. Kiracı dava sırasında çıkarsa giderler dava tarihindeki haklılığa göre belirlenir (HMK 331/1). İcra için [kararın icrası](#tahliye-kararından-sonra-icra-tehir-ve-tbk-355).

**Deliller.** TAKBİS kaydı; sınır yazısı; yapı kullanma izni ve keşif raporu; MERNİS ve aile kaydı; sözleşmedeki adres beyanı; son tutanak ve 353 bildiriminin tebliğ şerhi; fesih, iflas ve mirasçılık belgeleri; anahtar teslim tutanağı veya tevdi mahalli kararı.

**Kiracı savunmaları.** Kiraya veren konutu biliyordu; konut elverişsiz, başka ilçede veya kiracıya ya da eşine ait değil; süre, arabuluculuk veya taraf teşkili eksik; ek tahliye kaydı geçersiz (TBK 354). Keşif avansını kesin sürede yatır (HMK 324; doğrula). Kilit değiştirme veya yıkım gibi kendiliğinden tahliye sözleşme ihlalidir. 331'e karşı 316 ihtarının atlandığını, 325'e karşı haklı feshi, sözleşmesel çıkış hakkını, yeni kiracı önerisini ve depozito mahsubunu ileri sür ([cevap iskeleti](tahliye-sablonlari.md#kiracı-cevap-dilekçesi-iskeleti)).

**Tuzaklar.** 352/3'ü 350 ile karıştırma; 2025/1495–3048'in erken arabuluculuk kuralı kendiliğinden taşınmaz. Yargıtay HGK, E. 2013/6-96, K. 2013/859'daki 352 sayımını HGK görüşü sayma; karşıoy yazısındadır. TBK 334'ü erken teslim sanma; erken geri verme 325'tir. Kiracıya “fuzuli şagil” diyerek el atma davası açma.

**Doğrulanmış yerel kararlar.**

- **Yargıtay 3. HD, E. 2017/4366, K. 2017/12337, 20.09.2017**: kiraya veren yararına bozma; havuzda 352/3'ü inceleyen tek karar. Konut ve elverişlilik için “Bu iki koşulun bir arada bulunması zorunludur.”; elverişlilik keşifle araştırılmalıydı. Sınır: gider bozmasıdır; bilmeme koşulu tartışılmadı. `python scripts/pool.py get 367438100`
- **Yargıtay 3. HD, E. 2023/2475, K. 2024/217, 17.01.2024**: onama; kiraya verenin istemi reddedildi: “emredici hukuk kurallarına aykırı olarak düzenlenen tahliye şartı geçersiz olduğu gibi, bu şarta bağlı olarak öngörülen cezai şartın da geçersiz olacağı”. Sınır: tacir işyeri; konuta evleviyetle taşınır. `python scripts/pool.py get 998664800`
- **Yargıtay 3. HD, E. 2024/3898, K. 2025/4234, 23.09.2025**: kiracılar yararına bozma; kiraya veren “usulüne uygun tahliye davası açarak kiracıları tahliye etmeden, kiralanan iş yerlerini yıkarak haksız şekilde kira ilişkisinin sona ermesine neden olmuştur.”; kazanç kaybı incelenmeli. Sınır: el atma yolunun kapalılığı aktarılan kesinleşmiş kararlara aittir. `python scripts/pool.py get 1182772600`
- **Yargıtay 3. HD, E. 2017/4483, K. 2019/189, 16.01.2019**: kiracı lehine bozma; çekilmezlik iddiası TBK 316/3 ile incelenmeli, “hurdacılık faaliyetinin kiralanan alanda yapılıp yapılmadığının tespiti ile sonucuna göre karar verilmesi gerekirken”. Sınır: 331'i anmaz. `python scripts/pool.py get 477596700`
- **Yargıtay 3. HD, E. 2023/2841, K. 2024/1036, 06.03.2024**: kiraya veren yararına bozma; süre vermeyen, bildirdiği tarihte çıkmayan kiracı için “bu durumda ayıba dayalı haklı fesihten söz edilemeyeceğinin kabulü gerekir.” Sınır: tacir işyeri. `python scripts/pool.py get e5c8048b-4685-4456-8ad1-39133abef50f`
- **Yargıtay 3. HD, E. 2020/10233, K. 2020/7199, 30.11.2020**: kiracı yararına kısmi bozma; makul süreyi uzman bilirkişi belirler: “Yasal anahtar teslimi bizzat anahtarı kiraya verene teslim etmek suretiyle veya notere ya da mahkemeye tevdi mahalli tayini suretiyle yapılır.” Sınır: HUMK dönemi. `python scripts/pool.py get 627898900`

**Açık noktalar.**

- 352/3 işyeri kiracısına uygulanır mı; kiraya veren olmayan malik dava açabilir mi?
- “Bilmeme” koşulunda ispat yükü kimdedir; yenilenen sözleşmede hangi tarih esastır?
- Belirsiz süreli sözleşmede `E` nasıl belirlenir; TBK 353 ve erken arabuluculuk 352/3'e uygulanır mı?
- 325'te makul süre kalan sözleşme süresiyle sınırlı mı?

Rota kartı: `python scripts/tahliye.py yol kiracinin_konutu_ve_diger` · emsaller: `python scripts/tahliye.py emsal kiracinin_konutu_ve_diger`

## Tahliye kararından sonra: icra, tehir ve TBK 355

**Dayanak ve kapsam.** İlamlı tahliye İİK 24–26, geri bırakma İİK 33 ve 36, şikâyet İİK 16, üçüncü kişi İİK 276 kapsamındadır; İİK metinleri paketlenmedi, resmî metinden doğrula. İlamsız tahliye kararında eski hâle iade İİK 72/5'e dayanır (HGK 2021/1707). TBK 355 yalnız gereksinim (350/1; metne uygun okumayla 351) ve yeniden inşa (350/2) boşaltmalarında işler; 315, 316, 347 ve 352 tahliyelerinde işlemez. Tahliye ilamı kesinleşmeden icra edilir; kanun yolu icrayı kendiliğinden durdurmaz (resmî metinden doğrula). 01.07.2012 öncesi boşaltmada 6570 rejimini araştır.

**Koşullar.** İlamlı icra eda hükmü ister; kira tespiti ilamı icra edilmez (12. HD 2019/3733). Arabuluculuk anlaşma belgesi şerhle veya taraflar, avukatları ve arabulucunun ortak imzasıyla ilam niteliği kazanır ve tarihi belli bir teslim edimi taşımalıdır (HUAK 18/4, resmî metinden doğrula; 12. HD 2025/7199). TBK 355 tazminatı için boşaltma gereksinim veya yeniden inşa amacıyla sağlanmış, üç yıl dolmadan eski kiracıdan başkasına kiralanmış ve haklı sebep bulunmamalıdır. Tazminat son kira yılında ödenen bir yıllık kiradan az olamaz; fazlası ispatla istenir. Kira veya ecrimisil, anahtar teslimi kiraya verene bildirilene kadar işler.

**Bildirim.** İcra için ihtar gerekmez; icra emrini icra dairesi tebliğ eder. Yeniden inşadan sonra kiraya veren yeni durumu ve bedeli yazılı bildirir (TBK 355/2). Hasarı geri verme sırasında hemen ve yazılı bildir (TBK 335). Dava veya takibi sona ermeyi izleyen üç ay içinde bankaya bildir (TBK 342/3). Anahtarı almayan kiraya verene yazılı davet gönder, sonra anahtarı tevdi mahalline, notere veya icra dosyasına teslim edip bildir (8. HD 2019/4523). Kiraya veren ilamdan sonraki ödemeyi ilam saklı kalmak kaydıyla alsın, kiracı gönüllü teslimde 355 hakkını saklı tutsun; etkileri doğrulanmadı.

**Süreler.**

| Süre | Başlangıç olayı | Hesap | Araç | Güven |
| --- | --- | --- | --- | --- |
| İcra emri: tahliye (İİK 26; resmî metinden doğrula) | İcra emrinin tebliği `T` (UETS'de `G(U,5)`) | `G(T,7)` | `python scripts/deadlines.py takvim <T> --count 7 --unit gun` | orta |
| İİK 16 şikâyet | Öğrenme `Ö` | `G(Ö,7)` | `python scripts/deadlines.py takvim <Ö> --count 7 --unit gun` | orta |
| İİK 36 mehil | Kanun yolunun belgelenmesi | İcra müdürünün verdiği süre | araç yok | düşük |
| İstinaf (sulh hukuk; 01.06.2024 sonrası icra mahkemesi kararı) | Kararın tebliği `T` | `G(T,14)` | `python scripts/deadlines.py takvim <T> --count 2 --unit hafta` | yüksek (icra mahkemesi: orta) |
| TBK 355 yasak süresi | Boşaltma `B` (tahliye tutanağı, anahtar teslimi veya tevdiin bildirimi) | `Y(B,3)`; temkinle bu günden sonra kirala | `python scripts/deadlines.py takvim <B> --count 3 --unit yil` | orta |
| TBK 355/2 öncelik hakkı | Bildirimin ulaşması `N` | `A(N,1)` | `python scripts/deadlines.py takvim <N> --count 1 --unit ay` | yüksek |
| TBK 342/3 banka bildirimi | Sona erme `S` (tartışmalı) | `A(S,3)` | `python scripts/deadlines.py takvim <S> --count 3 --unit ay` | orta |
| TBK 335 hasar bildirimi | Geri verme | Hemen; sabit gün yok | araç yok | yüksek |

İİK 33 ve 276 süreleri ile 355 zamanaşımı düşük güvenlidir. İcra sürelerine adli tatil uygulanmaz (rehber görüşü; resmî metinden doğrula); son gün resmî tatile rastlarsa İİK 19'u ayrıca incele, araç tatil kaydırması yapmaz ([süre rehberi](sure-hesaplama.md#tatil-arabuluculuk-ve-tebligat-düzeltmeleri)).

**Yol, görevli yer ve arabuluculuk.** İlamlı tahliye icra dairesinde yürür. Kiracı istinaf eder, teminatla mehil alıp geri bırakma kararı getirir; kararı 7343 s.K. sonrası icra mahkemesi verir (ikincil kaynak; AYM E.2025/92, K.2025/127 sonucu doğrulanmadı). İlam kaldırılır veya bozulursa icra durur; eski hâle iade yeni hükmün kesinleşmesiyle olur (İİK 40; resmî metinden doğrula). Üçüncü kişi itirazına icra mahkemesi bakar; kiracının eşi ve ona bağlı oturanlar üçüncü kişi değildir. İcra takibinde arabuluculuk aranmaz (çıkarım); 01.09.2023 ve sonrasında sulh hukukta açılan 355, depozito, hasar ve kira davalarında dava şartıdır ([ortak usul](#ortak-usul-arabuluculuk-görev-taraf-ve-tebligat)).

**Deliller.** İlam ve tebliğ şerhi; icra emri, mehil ve teminat belgeleri; tahliye, teslim veya tevdi tutanakları; giriş-çıkış tutanakları, fotoğraf, keşif raporu; 355 için yeni kira sözleşmesi, ilan, abonelik kayıtları, son kira yılı dekontları.

**Kiracı savunmaları.** İstinaf ve İİK 36; ilamdan sonra yeni yazılı sözleşme veya süre verilmişse İİK 33; eda hükmü olmayan ilam veya usulsüz tebliğde şikâyet; arabuluculuk zamanlaması (3. HD 2025/3048); 355 tazminatı; hasarda bildirim yokluğu ve yıpranma payı; depozito mahsubu; anahtar teslimi (3. HD 2021/5531; olaya özgü).

**Tuzaklar.** Tahliyenin kesinleşmeyi beklediğini varsayma. Anlaşmalı fesih ve teslim metniyle çıkış 355'i düşürebilir; yine de cebri tahliyeyi beklemeyi masraf riskini tartmadan önerme. Havuz dışı 3. HD 2025/3540'ı doğrulamadan kullanma ([kontrol notu](tahliye-ve-uyarlama-kontrol.md#yeniden-kiralama-yasağı-çoğunluk-ve-karşıoy)). 355'i bir yıllık kiraya eşitleme; 353/3 değil 355/3 yaz. TBK 342/3 üç ayını hasar süresi sanma. Fiilî boşaltma teslim değildir (6. HD 2015/7513). Hasarı yalnız delil tespitiyle ispatlama (İstanbul BAM 55. HD 2024/2656).

**Doğrulanmış yerel kararlar.**

- **İstanbul BAM 35. HD, E. 2017/1061, K. 2018/40, 10.01.2018**: kiracının istinafı esastan reddedildi; kesin (kiraya veren lehine). İlamdan sonra fesih ve teslim belgesi düzenlenmiş, ilam icraya konmamıştı: “sözleşmenin sona ermesinin ve tahliyenin fiilen vaki olmadığı”; 355 reddi doğru bulundu. Sınır: tek daire; ihtirazi kayıtlı teslimi çözmez. `python scripts/pool.py get 22c1c746-82ef-49f2-9db7-66b4e2326652`
- **Yargıtay 3. HD, E. 2017/4956, K. 2019/871, 07.02.2019**: tazminat hükmü bozuldu (kiraya veren lehine). İhtar üzerine dava açılmadan çıkışta 355 doğmaz: “davacı kiracı taşınmazı bir yargı kararı veya icra marifetiyle tahliye etmemiştir”. Sınır: ilam sonrası çıkışı çözmez. `python scripts/pool.py get 485159800`
- **Yargıtay 3. HD, E. 2023/4785, K. 2025/230, 14.01.2025**: kiracının temyizi reddedildi, BAM kararı onandı. Bir yıllık kira tazminatı korundu; kiracı “bir yıllık kira bedelinden fazla zararı olduğunu” ispatlayamadı. Sınır: yalnız kiracı temyiz etti; icra yoluyla tahliye davacı anlatımı. `python scripts/pool.py get b5ba4a69-f80a-4b47-891c-2229d452eb5d`
- **Yargıtay HGK, E. 2017/1918, K. 2021/1707, 21.12.2021**: direnme kararı oy çokluğuyla bozuldu (kiraya veren lehine). Gerekçeye göre ilamsız tahliyede kiracı menfi tespit açıp “teminat karşılığında tahliye kararının icrasının durdurulması için ihtiyatî tedbir kararı verilmesini isteyebilir”; lehine kesinleşirse taşınmaz geri teslim edilir. Sınır: doktrine dayanan açıklama; karşıoy var. `python scripts/pool.py get 746178000`
- **Yargıtay 12. HD, E. 2022/9584, K. 2023/2309, 04.04.2023**: üçüncü kişinin temyizi reddedildi (kiracı tarafı aleyhine). Aile konutu ve muvazaa iddiası şerh ve tedbir yokken tahliyeyi durdurmadı; onanan BAM'a göre “bir başka dava dosyasının bekletici mesele yapılamayacağı”. Sınır: alıntı BAM'ın. `python scripts/pool.py get 890028300`
- **Yargıtay 3. HD, E. 2020/10233, K. 2020/7199, 30.11.2020**: hüküm kiracı yararına bozuldu. Hor kullanım sorumluluğu, hasarın “makul süre (kanun icabı yenilenen kira süresi bitmeden) içinde kiracıya yazılı olarak bildirilmesi koşuluna bağlanmıştır”; depozito mahsup edilir. Sınır: erken boşaltma; 2019/1657 24 günü makul saydı. `python scripts/pool.py get 627898900`

**Açık noktalar.**

- İhtirazi kayıtlı teslim veya icra emrinden sonra çıkış 355'i korur mu?
- 355 TBK 351'e uygulanır mı; haklı sebep, zamanaşımı ve feragat?
- İİK 36'da AYM kararının sonucu ve teminat ölçüsü.
- Tahliye kararı sözleşmeyi hangi tarihte sona erdirir; kira mı ecrimisil mi?

Rota kartı: `python scripts/tahliye.py yol tahliye_sonrasi` · emsaller: `python scripts/tahliye.py emsal tahliye_sonrasi`

## Kiracı savunmaları kontrol listesi

Her maddeyi dosyadaki belgeyle eşleştir; ayrıntı, karar ve sınırlar ilgili bölümdedir. Savunmayı yalnız usul itirazına dayandırma. Kurgu örnekler: [kiracı senaryoları K11–K16](kiraci-senaryolari.md). Şablon: [kiracı cevap dilekçesi iskeleti](tahliye-sablonlari.md#kiracı-cevap-dilekçesi-iskeleti); takibe itiraz için [itiraz notu](tahliye-sablonlari.md#tahliye-takibine-itiraz-notu).

**Usul.**

- Dava 01.09.2023 veya sonrasında açıldıysa dava şartı arabuluculuk yapılmış mı, son tutanak süresinde sunulmuş mu (HUAK 18/A/2)? TBK 350/1'de başvuru dava hakkı doğmadan yapıldıysa erken başvuru itirazını ileri sür (3. HD 2025/3048); diğer yollarda bu kararın kıyasla uygulanma riskini tart.
- Taraf teşkili tam mı: sözleşmedeki bütün kiraya verenler, bütün kiracılar ve TMK 194/son bildirimiyle taraf olmuş eş? Takipteki eksiklik icra mahkemesinde giderilemez (12. HD 2025/7823; 8. HD 2017/9518).
- Sıfat: taahhüde dayalı yolda kiraya veren olmayan malik (3. HD 2025/4997 gerekçesi); TBK 350'de pay ve paydaş çoğunluğu veya elbirliğinde bütün ortaklar; TBK 351'de edinme ve yeni malik sıfatı.
- Görev itirazı her aşamada, yetki itirazı cevapta ilk itiraz olarak ileri sürülür; tahliyede kesin yetki yoktur (6. HD 2013/14529).
- Yol: TBK 316, 350, 351, 352/2 ve 352/3 için ilamsız icra yolu yoktur; takip talebinde açık tahliye istemi yoksa 13 örnek hak doğurmaz (HGK 2021/648).
- Tebliğ: ödeme emri hiç tebliğ edilmemişse süre başlamaz (HGK 2023/642); usulsüz tebliğde öğrenmeden itibaren yedi gün içinde şikâyet et (İİK 16/1; resmî metinden doğrula).
- İcra aşaması: istinaf ve İİK 36 ile teminatlı tehir; ilamdan sonra yeni yazılı sözleşme veya süre verilmişse İİK 33; eda hükmü olmayan ilamda şikâyet (12. HD 2019/3733).

**Bildirim ve süre.**

- TBK 315 ihtarı veya 13 örnek ödeme emri 30 günden kısa süre veriyor ya da fesih ve tahliye uyarısı içermiyor mu (HGK 2021/1707; HGK 2021/648)?
- TBK 316/2 ihtarı yazılı mı, en az 30 gün veriyor mu, giderim istiyor mu (HGK 2014/83); aykırılık süre içinde giderildi mi?
- İki haklı ihtar: ihtar muacceliyetten önce keşide edilmiş, muaccel kira bölünmüş, ihtarlar farklı kira yıllarına ait ya da kira tebliğden önce ödenmiş mi (3. HD 2017/15623; 3. HD 2018/5354; HGK 2021/1314; 6. HD 2013/5989)?
- TBK 351/1 bildirimi edinmeden bir ay içinde kiracıya tebliğ edilmiş mi; keşide yetmez (3. HD 2017/12812).
- TBK 347: süre ilk süre + 10 + 1 hesabıyla dolmuş mu; sonradan yeni süre ve bedelle sözleşme yapılmış mı (HGK 2021/614); bildirim hedef yıl sonundan en az üç ay önce ulaşmış mı?
- Sözleşmedeki kiraya veren aleyhine ihbar kaydına uyulmuş mu (3. HD 2025/1440)?
- Dava erken mi: kira yılı veya süre bitmeden (3. HD 2018/5110; 3. HD 2025/3118), TBK 347'de uzama yılı sonundan önce (3. HD 2017/6383), TBK 351/1'de altı ay dolmadan? Ya da TBK 350, 351/2 ve 352'deki bir aylık süreden sonra mı açıldı? Taahhütte takip `B`'den önce mi yapıldı?

**Esas.**

- Temerrüt: asıl borç süre içinde tam ödendi mi; yalnız faiz ve giderlerin ödenmemesi tahliye sebebi değildir (6. HD 2016/1075). Alacaklı temerrüdünde tevdi ve ödeme yeri belirlenmesine dayan (3. HD 2025/3047); yan gider miktarı belirsiz mi (12. HD 2025/5902)?
- Taahhüt: teslimden önce veya sözleşmeyle birlikte mi alındı; açığa imza aykırı mı dolduruldu (yazılı delil, yoksa yemin: HGK 2008/394); imza veya tarih inkârı icra mahkemesi yolunu kapatır; taahhütten sonra yeni kira ilişkisi kuruldu mu; aile konutu bildirimi taahhütten önce mi yapıldı?
- Gereksinim: ihtiyaçlı yasal kişi çevresinde mi, yoksa şirkete mi ait (3. HD 2021/4476); ihtiyaç gerçek, samimi ve yargılama boyunca süren nitelikte mi (HGK 2021/878)? Yeni malikte muvazaa savunması dinlenmez; ihtiyacın samimiyetine yönel (6. HD 2014/10948).
- TBK 316: aykırılık önemli, kullanımla ilgili ve kiralananın içinde mi (HGK 2014/83; 3. HD 2019/189); yazılı izin veya zımni rıza var mı, alt kirada yazılı rıza aranır (3. HD 2018/6300)?
- TBK 352/3: kiraya veren konutu sözleşme kurulurken biliyor muydu; konut aynı ilçede, elverişli ve kiracıya ya da birlikte yaşadığı eşine mi ait (3. HD 2017/12337)?
- Sözleşmedeki ek tahliye kaydı ve ona bağlı ceza koşulu geçersizdir (TBK 354; 3. HD 2024/217). Kilit değiştirme, el koyma veya yıkım gibi kendiliğinden tahliye sözleşme ihlalidir (3. HD 2022/7594; 3. HD 2025/4234).
- Kiralanan konut veya çatılı işyeri değilse TBK 347 ve 350–352 uygulanmaz; ancak bu savunma TBK 327 nedeniyle süre sonu tahliyesine kapı açar, riski tart (3. HD 2017/15002; 3. HD 2022/1103).
- Tahliyeden sonra: üç yıl içinde başkasına kiralamada TBK 355 tazminatı, alt sınır bir yıllık kira (3. HD 2025/230); hasarda TBK 335 bildirimi yokluğu, yıpranma payı ve depozito mahsubu (3. HD 2020/7199); anahtar teslimini yazılı delille ispatla.

## Açık sorular ve sınırlar

Aşağıdaki noktalar yerel havuzda ve doğrulanmış kaynaklarda çözülmemiştir. Dosyada bu noktaya dayanırken seçimi, gerekçesini ve riskini müvekkile yazılı bildir; güncel Yargıtay ve BAM uygulamasını ayrıca araştır.

- **Arabuluculuk kapsamı:** Sulh hukukta itirazın iptali ve tahliye davası HUAK 18/B istisnasına girer mi? Yerel havuzda karar yok; ihtiyaten başvur.
- **Erken arabuluculuk:** 3. HD 2025/3048'in zamanlama kuralı TBK 350/2, 351, 352/1–3, 347 ve 316'ya taşınır mı? 26.05.2025'ten önce açılan davalarda yalnız İstanbul BAM 35. HD 2025/3212 incelendi.
- **Görevsiz mahkemeden sonra arabuluculuk:** Dosya gönderilmeden tamamlanan arabuluculuk kira davasında yeterli mi? HGK 2026/11 iş uyuşmazlığında yeterli saydı; Ankara BAM 31. HD 2026/339 ticari davada aksi yönde karar verdi.
- **TBK 353:** Arabuluculuk başvurusu dava bildirimi sayılır mı; uzama 352/1'e (özellikle takibe), 352/2'ye ve 352/3'e uygulanır mı?
- **Pencere sınırları:** TBK 350 ve 351/2'de ilk ve son gün `E` mi `G(E,1)` mi, `A(E,1)` mi `A(G(E,-1),1)` mi? TBK 351/1 davasının son sınırı sözleşme sonu mu, HGK 2021/878'deki “takip eden altı ay” mı? 351/1 bildiriminde edinme günü sayılır mı? TBK 347 davasının üst sınırı bir ay mı, zımni yenileme mi?
- **İki haklı ihtar:** Peşin veya taksitli ödemede ihtar yılı mı (W1), kiranın ait olduğu yıl mı (W2; 3. HD 2025/3118) esas alınır? İhtarda 30 gün ve dava uyarısı şart mı (3. HD 2017/15623 ile HGK 2021/1314 arasında gerilim)?
- **Temerrüt ve ilamsız takip:** İtirazsız kesinleşen 13 örnek sulh hukuk davasında ihtar sayılır mı (İİK 269/b son fıkra)? Yalnız yan gidere dayalı ilamsız tahliyenin sınırı nedir (12. HD 2025/5902, iki yönlü karşıoy)?
- **Taahhüt:** Taahhütten sonra yapılan yeni sözleşmenin etkisi (Yargıtay 3. HD, E. 2026/2877, K. 2026/2766 kanun yararına bozması havuzda yok; Resmî Gazete metninden doğrula). Yeni malik önceki malike verilen taahhüde dayanabilir mi; takip `B` günü yapılabilir mi?
- **Yeni malik:** Altı ay dolmadan yapılan arabuluculuk yeterli mi? Önceki malikin başvurusu ve önceki malike yapılan aile konutu bildirimi yeni malike karşı etkili mi?
- **TBK 347:** İİK 272 ilamsız yolu 347 feshine uygulanır mı? Hedef yıldan önce veya on yıl dolmadan yapılan bildirim sonraki uygun dönem için geçerli olur mu?
- **TBK 316:** Süre sonunda ayrı yazılı fesih bildirimi gerekir mi? Kullanımla ilgisiz ihlaller TBK döneminde tahliye sebebi mi? Alt kirada zımni rıza yeterli mi?
- **TBK 350/2 ve 352/3:** Yeniden inşa koşullarında havuzda esastan Yargıtay gerekçesi yok. 352/3 çatılı işyeri kiracısına uygulanır mı; kiraya veren olmayan malik dava açabilir mi; “bilmeme” koşulunda ispat yükü kimdedir; belirsiz süreli sözleşmede bitim nasıl belirlenir? TBK 325'te makul süre kalan sözleşme süresiyle sınırlı mı?
- **Tahliyeden sonra:** İhtirazi kayıtlı gönüllü teslim veya icra emrinden sonra çıkış TBK 355'i korur mu; 355 TBK 351 tahliyelerine uygulanır mı; zamanaşımı ve feragat nasıl işler? Tahliye kararı sözleşmeyi hangi tarihte sona erdirir; bu tarihten sonra kira mı ecrimisil mi istenir? İİK 36'da AYM E.2025/92, K.2025/127 kararının sonucu ve teminat ölçüsü doğrulanmadı.

Kaynak sınırı: İİK, HMK, HUAK, TMK ve 6101 hükümleri yalnız karar aktarımlarından veya ikincil kaynaktan kontrol edildi; HUAK 18/B süresi ve geçiş hükmü, HMK 362/1-b ve Ek m.1 parasal sınırları, İİK 24–26, 33, 36, 269–276 metinleri resmî konsolide metinden doğrulanmadı. Havuzda bulunmayan kararlar (3. HD 2025/3292–5039, 3. HD 2024/3099–2025/3540, 3. HD 2026/3805 K., İstanbul BAM 49. HD 2025/1002 K., 6. HD 2014/8939–9995 ve derlemedeki bazı BAM kararları) bu rehberde yalnız uyarı olarak anılır; doğrulamadan emsal olarak kullanma ([kontrol notu](tahliye-ve-uyarlama-kontrol.md), [derleme](derleme-v5.md)). Doğrulanmış kararlar havuzun seçkisidir, içtihat taraması yerine geçmez: tam metni `python scripts/pool.py get <id>` ile oku, alıntıyı `python scripts/pool.py quote -- <id> "<metin>"` ile birebir doğrula. Bu rehber hukuki görüş değildir; bilinmeyen olguyu [DOLDURULACAK: …] diye işaretle, varsayma.
