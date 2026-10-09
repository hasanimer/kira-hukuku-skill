# Katkıda bulunma

Önce mevcut issue ve pull request'leri kontrol edin. Küçük ve tek amaçlı değişiklikler incelemeyi kolaylaştırır.

## Hata bildirimi

Kullandığınız komutu, Python sürümünü, beklenen sonucu ve gerçekleşen sonucu yazın. Karar hatalarında `document_id` ve ilgili künyeyi; mevzuat hatalarında madde numarasını ve kaynak adresini ekleyin. Herkese açık issue veya pull request'e müvekkil belgesi, kişisel iletişim bilgisi, parola veya erişim anahtarı koymayın.

## Yerel kontrol

```sh
python scripts/validate.py
python -m unittest discover -s tests -v
```

Standart kütüphane yeterlidir. GitHub Actions aynı denetimi Windows ve Linux üzerinde çalıştırır.

## Değişiklik kuralları

- Yönerge değişikliklerinde `SKILL.md` ile ilgili rehberlerin tutarlı kalmasını sağlayın.
- Kaynak metinlerde yapılan değişikliği gerekçesi ve kaynağıyla açıklayın; etiket ile tam metni birbirinden ayırın.
- Veri değişirse ilgili `text_sha256` ve `data/manifest.json` dosya hash'lerini güncelleyin. Başarısız kontrolü geçirmek için doğrulanmamış bir kaynağın hash'ini değiştirmeyin.
- Kanun sürümü değişirse bütün bölümleri, alınma bilgisini ve okunabilir metni birlikte güncelleyin.
- Yeni sürümde dosya adlarını veya komut davranışını değiştiriyorsanız kullanıcı belgelerini de güncelleyin.
- Legaluga veya TypeSafe araştırma dökümlerini, araç yanıtlarını ve UDF dosyalarını public depoya eklemeyin; yalnız anonim ve paylaşılması uygun doğrulama özetlerini ekleyin.

Bir veri kaydının yayımlanmaması gerektiğini düşünüyorsanız hassas içeriği tekrar yayımlamadan yalnız kayıt kimliğini ve gerekçeyi belirtin.
