# Dosyaya göre soru seçimi

Bu liste kullanıcıya topluca gönderilecek bir form değildir. Önce konuşma ve belgelerden cevapları çıkar; yalnız ilgili uyuşmazlığın sonucunu veya süre hesabını değiştiren eksikleri sor.

## Seçim ve takip

- İlk turda ihtiyaç varsa yalnız sonucu veya süreyi etkileyen 3–5 kısa soru seç; daha azı yeterliyse listeyi doldurma. Basit soruya tam dosya görüşmesi uygulama.
- Öncelik: devam eden işlem ve tebliğ tarihi → kullanıcının amacı ve sıfatı → sonucu değiştiren sözleşme/ödeme/teslim olgusu. Sadece varsayımsal risk nedeniyle ek soru üretme.
- Cevabı belgede bulunan soruyu tekrarlama. Belgeler çelişiyorsa çelişen iki bilgiyi gösterip hangisinin doğru olduğunu sor; yeni cevap önceki belgeyi kendiliğinden hükümsüz kılmaz.
- “Bilmiyorum” cevabını “yok” sayma. Hangi belgenin açıklığa kavuşturabileceğini belirt. Eksiklik bağımsız araştırmayı engellemiyorsa araştırmaya devam et.
- Kullanıcının ifadesini ispatlanmış olguya dönüştürme. Gerektiğinde `soru | cevap | belge/sayfa veya beyan | eksik/çelişki | etkilediği mesele` kaydı tut.
- Sonraki turda yalnız yeni cevabın açtığı belirleyici eksikleri sor. Yanıt veya taslak üretmek için yeterli bilgi oluştuğunda soru toplamayı bırak; açık kalan noktaları koşullu göster.

## Temel sorular

1. İhtar, icra takibi, arabuluculuk veya dava var mı? Hangi belge hangi yolla (UETS/e-Devlet e-Tebligat, PTT/posta, noter, elden) ve ne zaman tebliğ edildi? Söylediğiniz tarih belgedeki tebliğ/ulaşma tarihi mi, yoksa okuma, SMS veya öğrenme tarihi mi?
2. Sorun nedir; hangi sonucu veya çıktıyı istiyorsunuz?
3. Kiracı mısınız, kiraya veren misiniz; uyuşmazlıkta hangi sıfatla yer alıyorsunuz?
4. Taşınmaz konut, çatılı işyeri veya başka türde mi?
5. Sözleşmenin başlangıcı ve süresi nedir? Sonradan yeni sözleşme veya protokol yapıldı mı?

Tebliğ tarihini kullanıcının söylediği tarihten doğrudan alma. Elektronik tebligatta UETS'ye ulaşma tarihini okuma/SMS/e-posta tarihinden ayır; kanunen tebliğ, ulaşmayı izleyen beşinci günün sonunda yapılmış sayılır (7201 s.K. m.7/a; `python scripts/deadlines.py uets YYYY-AA-GG` komutuna ulaşma tarihini ver). Posta, noter veya adrese dayalı tebligatta tebliğ mazbatasındaki tarih ve şerhi iste; usulsüz tebligat şüphesinde öğrenme tarihini ayrıca sor. Ayrıntı: [süre rehberi](sure-hesaplama.md).

## Rejim ve taraflar

Rejim veya taraf sıfatı belirsizse [ön inceleme rehberine](kira-rejimi-ve-taraflar.md) göre yalnız ilgili soruları seç: Açık/kapalı alan ve fiilî kullanım nedir? Ruhsat, demirbaş ve işletme hakkı kime aittir; hangi unsurlar teslim edilmiştir? Sözleşmeyi kim, hangi yetkiyle imzaladı? Mülkiyet paylı mı elbirliği mi; pay oranları ve rıza belgeleri nedir? Kamu kiralaması varsa kurum, ihale ve sözleşme dayanağı nedir? Cevapları sözleşme, tapu, ruhsat ve yetki belgesinden çıkar; kullanıcıdan tekrar isteme.

## Kira bedeli ve ödeme

- Mevcut kira ile istenen bedel ne kadar; aylık mı, yıllık mı, net mi, brüt mü?
- Sözleşmedeki artış maddesi tam olarak ne diyor?
- Hangi dönemler çekişmeli? Ödemelerin tarihleri, tutarları ve dekont açıklamaları neler?
- Önceden kira tespit kararı veya bedel konusunda anlaşma var mı?
- Tespit isteniyorsa hangi kira döneminin başlangıcından itibaren yeni bedel talep ediliyor?

Ödeme hesabında her ay için aynı bilgileri ayrı sorularla tekrarlamak yerine dönem–tutar–ödeme çizelgesi kullan. Net/brüt niteliğini tutardan tahmin etme.

## Uyarlama

Önce talebin TBK 344 kapsamında tespit, sözleşmedeki artış şartının yorumu veya TBK 138 kapsamında uyarlama olup olmadığını ayır. Tespit sorularını uyarlamaya, uyarlama koşullarını tespite taşıma. Yalnız ileri sürülen değişikliğe ilişkin soruları seç. [Kaynaklar ve yorum sınırları](tahliye-ve-uyarlama-kontrol.md).

- Sözleşme ne zaman yapıldı? Kira bedeli Türk lirası olarak mı, yabancı para olarak mı kararlaştırıldı? Yabancı paraysa TBK 344/4'teki beş yıllık süre doldu mu?
- Sözleşmeden sonra hangi olağanüstü değişiklik, ne zaman ortaya çıktı? Bu değişiklik sözleşme yapılırken öngörülebilir miydi? Uyarlama isteyen taraftan kaynaklanıyor mu?
- Değişiklik edimler arasındaki dengeyi nasıl ve ne ölçüde bozdu? Bunu gösteren kapanma/kısıtlama kararı, ciro, kur veya ödeme kayıtları neler?
- Uyarlama istenen dönemin kiraları ödendi mi? Ödendiyse haklar saklı tutularak mı ödendi; çekince hangi belgede yer alıyor?
- Daha önce tespit, uyarlama veya tahliye davası açıldı mı, tedbir kararı verildi mi?

Değişikliğin varlığı, öngörülemezliği ve edim dengesine etkisi ayrı meselelerdir; tek bir “ekonomik kriz oldu” beyanıyla hepsini çözülmüş sayma.

## Tahliye

İhtiyaçta önce 350/351 yolunu, dava hakkının doğumunu ve arabuluculuk tarihlerini belirle. Taahhütte fiilî teslim, belgenin düzenlenmesi, imza/tarih itirazı, taahhütten sonra yapılan yeni sözleşme/yenileme ve dayanak delili ayır. Aile konutunda eş bildiriminin tarihi ve muhatabını; TBK 355'te ilam, takip ve fiilî tahliye belgelerini sor. Belgelerde mevcut bilgiyi tekrar isteme. [Kaynaklar ve yorum sınırları](tahliye-ve-uyarlama-kontrol.md).

- İleri sürülen neden ne: kiraya verenin ihtiyacı (TBK 350/1), yeniden inşa veya imar amacıyla esaslı onarım, genişletme ya da değiştirme (TBK 350/2), yeni malikin ihtiyacı (TBK 351/1–2), yazılı tahliye taahhüdü (TBK 352/1), iki haklı ihtar (TBK 352/2), kiracının veya birlikte yaşadığı eşinin aynı ilçe/belde belediye sınırları içinde oturmaya elverişli konutu (TBK 352/3), kira bedelinde temerrüt (TBK 315), özenle kullanma ve komşulara saygı borcuna aykırılık (TBK 316), önemli sebeple olağanüstü fesih (TBK 331) veya on yıllık uzama süresinin dolması (TBK 347)?
- Taahhüt varsa ne zaman imzalandı, hangi boşaltma tarihini içeriyor? Aslı mevcut mu; imza veya tarih çekişmeli mi? Taahhütten sonra yeni kira sözleşmesi, yenileme veya ek protokol yapıldı mı; yapıldıysa tarihi ve içeriği ne?
- Taşınmaz fiilen ne zaman teslim edildi? Bu tarih hangi belgede yer alıyor?
- İhtarlar hangi yolla (UETS/e-Devlet, PTT, noter, elden) ve hangi tarihte tebliğ edildi; ödemelerin tarihleri, gerektiğinde saatleri neler?
- Taşınmaz satıldı mı? Yeni malikin edinme ve bildirim tarihleri nedir?
- İhtiyaç ileri sürülüyorsa kimin ihtiyacı anlatılıyor; bunu destekleyen veya çürüten somut belgeler neler?
- Yeniden inşa/imar ileri sürülüyorsa: proje, yapı ruhsatı veya ruhsat başvurusu var mı; yapılacak iş esaslı mı ve iş sırasında kiralananın kullanımı imkânsız mı? Ayrıca 6306 sayılı Kanun kapsamında riskli yapı süreci yürüyor mu?
- Kiracının veya birlikte yaşadığı eşinin konutu ileri sürülüyorsa: konut kimin adına, ne zamandan beri kayıtlı, aynı ilçe/belde belediye sınırları içinde ve oturmaya elverişli mi; kiraya veren sözleşme kurulurken bunu biliyor muydu?
- Özen veya komşulara saygı borcuna aykırılık ileri sürülüyorsa: konut/çatılı işyerinde en az otuz gün süre veren yazılı ihtar ne zaman tebliğ edildi ve süre içinde aykırılık giderildi mi? Yoksa TBK 316/3 kapsamında ihtarsız derhal fesih mi iddia ediliyor?
- Önemli sebeple olağanüstü fesih ileri sürülüyorsa: sebep nedir, fesih bildirimi ne zaman yapıldı ve yasal fesih bildirim süresine (TBK 328–330) uyuldu mu?

Yalnız ileri sürülen tahliye sebebine ilişkin soruları seç. Uzama hesabında ilk sözleşme süresini, taahhüt hesabında imza ile boşaltma tarihini birbirinin yerine kullanma. Tarih incelemesini [süre rehberine](sure-hesaplama.md) bağla.

## Depozito, hasar ve ayıp

- Depozito ne kadar, kime ve nasıl ödendi: bankada vadeli hesaba yatırıldı veya bankaya depo edildi mi, yoksa elden ya da kiraya verenin hesabına mı ödendi? Tutar üç aylık kirayı aşıyor mu?
- İlk ve son teslim tutanakları, fotoğraflar ve demirbaş listesi var mı?
- Hangi hasar veya kesinti ileri sürülüyor; tutarı ve belgeleri neler?
- Rutubet veya başka ayıp ne zaman başladı, kiraya verene ne zaman ve nasıl bildirildi?
- Onarım veya tadilat kimin izniyle ve masrafıyla yapıldı? Faturalar var mı?
- Anahtar ne zaman, kime ve hangi belgeyle teslim edildi?

Hasarın varlığı, sorumluluğu ve tutarı ayrı meselelerdir. “Ev zarar görmüş mü?” gibi tek soruyla hepsini çözülmüş sayma. Depozitonun tamamının iadesini veya kesintinin haklılığını cevaplardan otomatik çıkarma.

Hasar bildiriminde eksikliğin ne zaman fark edildiğini ve yazılı bildirimin ne zaman ulaştığını ayır. Kefalet tartışılıyorsa kefalet metni, el yazılı alanlar, tarih, azami tutar, kapsam ve gerekiyorsa eş rızası belgesini incele. Devirde yazılı rıza ve devredilen şeyin kira ilişkisi mi kullanım mı olduğunu belirle. Ayrıntılar: [teslim, masraf ve kefalet](teslim-masraf-kefalet.md).

## İlk tur seçimi örnekleri

**“İki ihtar geldi, ödedim.”** İhtar/ödeme emirlerinin tebliğ yolu ve tebliğ (UETS'de ulaşma) veya öğrenme tarihleri; hangi kira aylarına ilişkin oldukları; ödemelerin tarih-saatleri; takip veya davanın mevcut aşaması. Sözleşme başlangıcı belgede yoksa ve dönem ayrımını etkiliyorsa ekle. Depozito ve tadilat sorularını sorma.

**“Depozitomu vermiyor.”** Depozito tutarı ve ödeme belgesi; paranın bankada vadeli hesapta mı olduğu, yoksa elden ya da kiraya verenin hesabına mı ödendiği; sözleşmenin sona erme tarihi ile anahtar teslim tarihi ve belgesi; ileri sürülen kesinti nedeni; giriş/çıkış durumunu gösteren belgeler. Mevcut dosyada cevaplananları çıkar.

**“Kirayı artırmak istiyor.”** Önce bunun sözleşmesel artış talebi, tespit davası, uyarlama talebi veya başka bir talep olup olmadığını ayır; bilinmeyen başlangıç/hedef dönem, artış maddesi ve mevcut/istenen bedeli sor. Dava veya tebligat varsa onu önceliklendir.

[Senaryo kataloğundaki](kiraci-senaryolari.md) `documents` ve `decisive_questions` alanları ayrıntılı soru seçimini destekler. Kurgu olayları kullanıcıya aitmiş gibi soru öncülüne yerleştirme.
