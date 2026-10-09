# Türk Borçlar Kanunu

Diğer kanunların hangi meselede araştırılacağı ve sık karıştırılan dayanaklar için [kira mevzuat haritasını](mevzuat-haritasi.md) kullan. Harita tam metin kanun arşivi değildir.

- `data/mevzuat/6098-source.json`: tam metnin yedi kaynak bölümü; kaynak adresi, alınma zamanı ve bölüm bilgileri korunur.
- `data/mevzuat/6098-turk-borclar-kanunu.md`: bölümlerin aralarına iki satır sonu eklenerek birleştirilen aranabilir tam metin.
- `scripts/tbk.py`: madde numarasıyla, geçici maddeye ve kanuna işlenemeyen hükümlere seçenekle erişim. Kaynak hash'i, bölüm sırası, toplam bayt sayısı, 1–649 madde başlıkları, geçici 1–2 başlıklarının yeri ve dipnot atıfları denetlenir.

[Resmî kaynak: 6098 sayılı Türk Borçlar Kanunu](https://www.mevzuat.gov.tr/mevzuat?MevzuatNo=6098&MevzuatTur=1&MevzuatTertip=5).

Alınma zamanı kaynak JSON dosyasındadır. Paket sabit kopyadır; sonraki değişiklikleri ve geçmiş olayda uygulanacak sürümü ayrıca kontrol edin. Geçici hükmün metinde bulunması bugün uygulanacağı anlamına gelmez.

Depo kökünde:

```sh
python scripts/tbk.py
python scripts/tbk.py 344
python scripts/tbk.py 345
python scripts/tbk.py --gecici 1
python scripts/tbk.py --gecici 2
python scripts/tbk.py --ek
```

Numarasız çağrı kaynak bilgisini verir. Madde çıktısı maddenin kendi kenar başlıklarıyla başlar ve sonraki maddenin başlığından önce biter; değişiklik dipnotları `footnotes` alanında ayrıca verilir. Üst bölüm başlıkları veya dipnot atıfları metinde görünebilir; bunları istenen madde hükmünden ayırın. TBK geçici 1–2 (7409 ve 7456 sayılı Kanunlarla eklenen yüzde 25 sınırı) `--gecici 1` veya `--gecici 2` ile, 6217 sayılı Kanun geçici 2 ve değişiklik tablosu `--ek` ile ayrıca getirilir. 6217 geçici 2'nin ertelediği maddelerde (323, 325, 331, 340, 342, 343, 344, 346 ve 354) aynı hüküm madde çıktısının `temporary_provision` alanında da verilir; bu erteleme yalnız kiracısı tacir veya tüzel kişi olan işyeri kiralarında ve 01.07.2012'den itibaren sekiz yıl için geçerliydi (süre 01.07.2020'de doldu). 647. ve 649. madde çıktıları geçici maddeleri, kanuna işlenemeyen hükmü ve değişiklik tablosunu içermez; `--ek` çıktısının `footnotes` alanı kopyadaki bütün değişiklik dipnotlarını verir.

Çıkış kodları: 0 başarılı; 1 paket metni okunamadı veya bütünlük denetimi başarısız; 2 kullanım hatası (ör. 1–649 dışında madde numarası).
