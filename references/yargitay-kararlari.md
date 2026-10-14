# Yargıtay ek seçkisi

On kararın tam metni `data/yargitay-selected.jsonl` dosyasındadır. Asistan tarafından incelenmiştir; bağımsız hukukçu doğrulaması yapılmamıştır. Kaynak metin hataları düzeltilmeden korunur, kullanım sınırları ayrı notlanır.

```sh
python scripts/pool.py search depozito --court-type yargitay
python scripts/pool.py get 3ed4fe74-ff6b-4f4e-891c-e355ee63f916
python scripts/pool.py quote 3ed4fe74-ff6b-4f4e-891c-e355ee63f916 "olağan kullanımdan mı yoksa hor kullanımdan mı kaynaklandığının araştırılması"
```

`--court-type yargitay` filtresi bu on kararlık seçkiyle birlikte ana havuzdaki kararların tamamını ve derleme seçkisindeki Yargıtay kararlarını da kapsar: yardımcı, ana havuz kayıtlarına `court_type: yargitay` etiketini okuma sırasında ekler (BAM seçkisi bu filtreye girmez). Sonuçların kaynağını kayıttaki `collection` alanından ayırt et: `yargitay-selected.jsonl` bu seçkidir (`source_provider: Dejure`, Dejure `source_url`); `topic-rescan-assistant-adjusted.jsonl` ana havuzdur (`source_provider: Bedesten (kimlikten türetildi)`); `derleme-v5-selected.jsonl` [derleme seçkisidir](derleme-v5.md) (`source_provider: Bedesten (Legaluga MCP karar_getir)`). Bu notlardaki inceleme yalnız bu seçki için geçerlidir. Birebir alıntıdan önce tam metni oku ve `quote` ile doğrula.

## Yargıtay 3. Hukuk Dairesi, E. 2017/4355, K. 2019/607, T. 04.02.2019

[Kaynak](https://app.dejure.ai/dokuman/3ed4fe74-ff6b-4f4e-891c-e355ee63f916)

**Kullanım:** depozito iadesi, hasar mahsubu, teslim tutanağı.

Depozito iadesini kabul eden hüküm; hor kullanım, geç teslim ve aidat incelemesi eksikliği nedeniyle bozuldu.

Hasar iddiasının varlığı kesintiyi kendiliğinden haklı kılmaz; olağan kullanım ve hor kullanım ayrımı araştırılmalıdır.

2009 sözleşmesi ve 2013 fesih protokolü değerlendirilmiştir; cezai şart anlatımı güncel konut/çatılı işyeri kiralarına koşulsuz taşınamaz, TBK 346 ve geçiş hükümleri ayrıca incelenir.

Bozma kararıdır; belirli hasarın veya mahsup tutarının kesin kabulü değildir.

## Yargıtay 3. Hukuk Dairesi, E. 2023/5407, K. 2024/820, T. 28.02.2024

[Kaynak](https://app.dejure.ai/dokuman/cb724b08-d518-489f-bd0f-cce07b98ea89)

**Kullanım:** depozito, hasar ispatı, karar düzeltme, usuli kazanılmış hak.

Depozito davasındaki önceki düzelterek onama kararına yönelik tarafların karar düzeltme talepleri reddedildi.

2024 karar tarihi, 2005 sözleşmesi ve 2012 tahliyesini güncel sözleşme rejimine dönüştürmez.

İlk derece mahkemesinin icra inkâr tazminatı gerekçesini nihai kabul sayma: önceki temyiz kararı bu yönden düzelterek onamadır; düzeltmenin kapsamı bu metinde açık değildir.

Takip/ihtar tarihleri ve hesap kalemleri anlatımında tutarsızlıklar vardır; faiz başlangıcı veya kur hesabında bu metni doğrudan hesap girdisi yapma.

Önceki bozma ve onama kararları bu güncellemede bağımsız okunmadı; dosya geçmişi olarak aktarılmıştır.

## Yargıtay 3. Hukuk Dairesi, E. 2023/4785, K. 2025/230, T. 14.01.2025

[Kaynak](https://app.dejure.ai/dokuman/b5ba4a69-f80a-4b47-891c-2229d452eb5d)

**Kullanım:** yeniden kiralama, TBK 355, kazanç kaybı, zararın ispatı.

İlk derece mahkemesi davayı kısmen kabul ederek son kira yılında ödenen kira üzerinden hesaplanan bir yıllık kira bedeli 18.094,32 TL'ye (talep 18.165,00 TL; faiz dava tarihinden) hükmetti, kazanç kaybı ve manevi tazminat taleplerini reddetti; BAM istinafı esastan reddetti. Bir yıllık kira bedelini aşan zarar ispatlanamadığından davacının temyizi reddedilerek BAM kararı onandı.

Davacı ve ilk derece anlatımındaki 353/3 atfı, Yargıtay gerekçesindeki 355/3 ile karıştırılmamalıdır.

Bir yıllık kira bedeli tazminatın her durumda üst sınırı değildir; bu dosyada aşan zararın ispatı başarısızdır.

İcra yoluyla tahliye olgusu vardır; anlaşmalı teslimi konu alan BAM E.2017/1061 K.2018/40 ile aynı olgu seti gibi sunma.

Manevi tazminata ilişkin ilk derece anlatımını her ihtimale uygulanacak genel ret kuralı yapma.

## Yargıtay 3. Hukuk Dairesi, E. 2017/13231, K. 2019/1657, T. 27.02.2019

[Kaynak](https://app.dejure.ai/dokuman/4c8c9a72-a027-4670-a768-34a95067ccbb)

**Kullanım:** erken tahliye, yeniden kiralama, depozito mahsubu.

İki aylık makul süreye rağmen daha önce gerçekleşen yeniden kiralama dikkate alınmadığı ve depozito mahsubu incelenmediği için hüküm bozuldu.

Anahtarın güvenlik görevlisine bırakılması, kiraya veren bildirilen tahliye tarihine karşı çıkmadığı somut olayda kabul edilmiştir; her teslim bu şekilde geçerli sayılmaz.

İki ay evrensel makul süre değildir; fiilen yeniden kiralama 01.09.2012 tarihinde gerçekleşmiştir.

Dava dilekçesiyle hasar bildiriminin yeterli görülmesi somut tarih akışına özgüdür; TBK 335 için genel süre üretme.

Metindeki davacı/davalı kiracı sıfatı kaymalarını aynen hukuki sonuca taşıma; sözleşmesel cezalar için dönem ve geçiş rejimini ayrıca incele.

## Yargıtay 3. Hukuk Dairesi, E. 2023/2841, K. 2024/1036, T. 06.03.2024

[Kaynak](https://app.dejure.ai/dokuman/e5c8048b-4685-4456-8ad1-39133abef50f)

**Kullanım:** ayıplı kiralanan, haklı fesih, makul süre, TBK 325.

Kiracının haklı feshi kabul edilerek makul süre bedelinin reddedilmesi uygun bulunmadı; BAM kararı kaldırılıp ilk derece hükmü kiraya veren yararına bozuldu.

Ayıpların giderilmesi için süre verilmemesi ve bildirilen fesih tarihlerinde tahliye edilmemesi birlikte değerlendirilmiştir; her ayıpta aynı sonuç varsayılmaz.

İlk derece ve BAM'ın haklı fesih kabulünü Yargıtay sonucu gibi sunma.

2015 işyeri sözleşmesindeki muacceliyet kaydı, güncel konut/çatılı işyerleri için geçerli örnek değildir; 6217 geçici 2 atfı ve TBK 346 ayrıca incelenir.

Anahtarın notere bırakıldığı tarih ile tahliye tarihinin anlatımı farklıdır; buradan doğrulanmamış süre veya bakiye hesabı yapma.

## Yargıtay 3. Hukuk Dairesi, E. 2022/8302, K. 2023/167, T. 21.02.2023

[Kaynak](https://app.dejure.ai/dokuman/339cd8cf-0eab-47de-90ba-2f0b52a02c73)

**Kullanım:** tahliye taahhüdü, imza incelemesi, boş imza, ispat.

İmzanın şirket yetkilisine ait olduğu bilirkişiyle belirlenen ve savunmaların kesin delillerle ispatlanamadığı olayda tahliye ve itirazın iptali sonucu onandı.

Başlangıç tarihi ve taahhüdün düzenleme tarihi anlatımında farklı tarihler vardır; süre hesabında veya teslim-sonrası koşulunu tek başına doğrulamakta kullanma.

BAM'ın boş imza hakkındaki geniş ifadesini bütün savunmaları ortadan kaldıran kural sayma; Yargıtay gerekçesi somut ispat durumuna dayanır.

HGK E.2008/369 K.2008/394 bu güncellemede ayrıca tam metinden okunmuştur; anlaşmaya aykırı doldurma ile hile/sahtecilik ayrımını koru.

Şirketin işyeri uyuşmazlığı aile konutu itirazını çözmez.

## Yargıtay Hukuk Genel Kurulu, E. 2008/369, K. 2008/394, T. 28.05.2008

[Kaynak](https://app.dejure.ai/dokuman/202209-1215-0532-2008369-2008394-0adafbc2-c10f-47aa-94f6-c2327d600cce)

**Kullanım:** Hukuk Genel Kurulu, tahliye taahhüdü, hile, yemin.

Hileyle imzalatılma savunmasının usulünce ispatlanamadığı ve yemin teklifinin o olayda dinlenemediği gerekçesiyle ret yönündeki direnme kararı oyçokluğuyla bozuldu.

Anlaşarak boş imzalama ve anlaşmaya aykırı doldurma iddiası ile habersizce hileyle imzalatılma iddiası ayrı değerlendirilmiştir.

Yemin delili hiçbir boş imza uyuşmazlığında kullanılamaz sonucunu çıkarma; karar iki durumu açıkça ayırır.

2008 tarihli karar 1086 sayılı HUMK ve eski Borçlar Kanunu dönemindedir; güncel HMK/TBK delil ve süre rejimini ayrıca doğrula.

Araç künyesinde esas numarası 2008/369 olarak verilmiştir; araçla doğrulanmamış daire eki ekleme.

## Yargıtay 3. Hukuk Dairesi, E. 2024/2523, K. 2025/1572, T. 12.03.2025

[Kaynak](https://app.dejure.ai/dokuman/2741a64d-0a5f-4a40-8083-e40276bcfb1f)

**Kullanım:** uyarlama, uzun süreli kira, ekonomik değişiklik.

Uyarlama talebinin reddine ilişkin BAM kararı onandı.

Sırf beş yıl dolmadığı için uyarlama hiçbir zaman istenemez sonucu çıkarılmaz; somut dosyada koşullar oluşmamıştır.

Enflasyon hiçbir durumda uyarlamaya gerekçe olamaz şeklinde genelleme; Yargıtay gerekçesi kısa onamadır.

İşyeri uyuşmazlığındaki yüzde 25 göndermesi davacının temyiz iddiasıdır; uygulanmış sınır değildir.

## Yargıtay 3. Hukuk Dairesi, E. 2018/2258, K. 2018/6300, T. 04.06.2018

[Kaynak](https://app.dejure.ai/dokuman/020e7adb-ba73-49cc-8228-2aa4bdf70f18)

**Kullanım:** alt kira, franchise, yazılı muvafakat.

Şirket ilişkileri ve yazılı muvafakat araştırılmadan tahliye talebinin reddi nedeniyle karar bozuldu.

Franchise ilişkisinin varlığı otomatik alt kira izni değildir; unvan değişikliği ve şirket ilişkileri araştırılmalıdır.

Bozma doğrudan tahliye hükmü değildir.

TBK 316 ihtar anlatımını bütün aykırılık türlerinde istisnasız uygulama.

## Yargıtay 6. Hukuk Dairesi, E. 2014/10567, K. 2015/10451, T. 26.11.2015

[Kaynak](https://app.dejure.ai/dokuman/3d040a9a-72cd-42ce-b64a-72bf63459651)

**Kullanım:** zamanaşımı, kısmi dava, ıslah, ürün (hasılat) kirası.

Islah edilen alacaklar yönünden zamanaşımı ve alacak türü ayrımı değerlendirilmediğinden hüküm oyçokluğuyla bozuldu.

Otobüs işletmesine ilişkin hasılat kirasıdır (818 sayılı BK'daki ad; TBK 357'de ürün kirası); konut veya çatılı işyeri uyuşmazlığı değildir.

Dönemsel kira ile sözleşmeye dayalı ceza geri istemi ayrı değerlendirilmiştir; tüm yan alacaklara otomatik aynı süreyi uygulama.

Karşıoy onama yönündedir; çoğunluk gerekçesinden ayrı tut. Belirsiz alacak davası ve güncel ıslah rejimi ayrıca incelenmeli.
