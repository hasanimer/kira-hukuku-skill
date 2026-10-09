<div align="center">

# Kira Hukuku Asistanı

**Dosyadan içtihada, içtihattan gerekçeli taslağa.**

Kira tespiti, tahliye, uyarlama, alacak ve depozito dosyaları için kaynaklara dayalı araştırma ve dilekçe hazırlama becerisi.

[![Paket kontrolü](https://github.com/hasanimer/kira-hukuku-skill/actions/workflows/validate.yml/badge.svg)](https://github.com/hasanimer/kira-hukuku-skill/actions/workflows/validate.yml)
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square)
![Codex Skill](https://img.shields.io/badge/Codex-Skill-111827?style=flat-square)
![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-D97757?style=flat-square)

[Hızlı başlangıç](#hızlı-başlangıç) · [Kullanım örnekleri](#kullanım-örnekleri) · [Çalışma akışı](#çalışma-akışı) · [Rehberler](#rehberler)

</div>

---

| **1.603 karar** | **6098 sayılı Kanun** | **Taşınabilir paket** |
| :---: | :---: | :---: |
| Tam metin, künye ve kaynak izi | Türk Borçlar Kanunu tam metni | Yerel aramada API anahtarı gerekmez |

## Dosyanız için ne yapar?

<table>
<tr>
<td width="50%" valign="top">

<h3>01 · Dosya analizi</h3>
Olayları ve tarihleri düzenler; sonucu etkileyen eksik bilgi ve belgeleri belirler.

</td>
<td width="50%" valign="top">

<h3>02 · Emsal araştırması</h3>
Lehe ve aleyhe kararları bulur; tam metinleri inceler, birebir alıntıları doğrular.

</td>
</tr>
<tr>
<td width="50%" valign="top">

<h3>03 · Dilekçe taslağı</h3>
Dava ve cevap dilekçelerinde somut olay, delil, hukuki dayanak ve talep arasında bağ kurar.

</td>
<td width="50%" valign="top">

<h3>04 · Rapor incelemesi</h3>
Bilirkişi raporunun emsallerini ve hesap yöntemini inceleyerek somut itirazlar hazırlar.

</td>
</tr>
</table>

## Hızlı başlangıç

**Gerekenler:** Codex veya Claude Code, Git ve Python 3.10+. Yerel yardımcılar yalnız Python standart kütüphanesini kullanır.

### 1. Skill'i ekleyin

**Codex**

```sh
git clone https://github.com/hasanimer/kira-hukuku-skill.git "$HOME/.codex/skills/kira-tespit-asistani"
```

**Claude Code**

```sh
git clone https://github.com/hasanimer/kira-hukuku-skill.git "$HOME/.claude/skills/kira-tespit-asistani"
```

<details>
<summary>Kurulum yolu ve mevcut kurulum hakkında</summary>

Komutlar PowerShell, Bash ve Zsh ile kullanılabilir. Özel bir `CODEX_HOME` kullanıyorsanız hedef olarak onun `skills` dizinini seçin. Claude Code'da kişisel kurulum `~/.claude/skills/` (Windows'ta `%USERPROFILE%\.claude\skills\`), tek projeye özel kurulum proje kökündeki `.claude/skills/` altındadır; klasör adını `kira-tespit-asistani` olarak koruyun. Hedef klasörde mevcut bir kopya varsa üzerine yazmadan önce değişikliklerinizi koruyun.

</details>

### 2. Çağırın

```text
$kira-tespit-asistani kira tespit dosyamı incele;
eksik belgeleri ve lehe/aleyhe emsalleri göster.
```

Codex'te `$kira-tespit-asistani`, Claude Code'da `/kira-tespit-asistani` ile çağırın. Claude Code, kira hukuku isteklerinde skill'i açıklamasına göre kendiliğinden de yükleyebilir. Aşağıdaki örneklerde Codex biçimi kullanılmıştır.

### 3. Legaluga MCP'yi bağlayın (isteğe bağlı)

Güncel mevzuat metni, 2020 sonrası ve BAM içtihadı, künye ön denetimi ve imzasız UDF dilekçe taslağı için skill Legaluga MCP'yi varsayılan dış kaynak olarak kullanır. Legaluga'nın verdiği MCP adresini Claude Code'da `claude mcp add --transport http legaluga <MCP_ADRESI>` komutuyla ya da claude.ai'de özel bağlayıcı olarak, Codex'te MCP sunucu ayarlarınıza ekleyin. Adres ve erişim bilgisi için [legaluga.com](https://legaluga.com). Bağlantı yoksa skill yerel paketle çalışır ve güncel doğrulama yapılamadığını belirtir. [Kullanım kuralları →](references/legaluga.md)

### 4. Dosyanızla çalışın

İlgili sözleşmeyi, dilekçeyi veya raporu paylaşın; istediğiniz çıktıyı belirtin. Asistan önce belirleyici olguları çıkarır, ardından ilgili kaynakları araştırır.

[Yargıtay ek seçkisi ve kullanım notları →](references/yargitay-kararlari.md)

## Kullanım örnekleri

[Dosyaya göre sorulacak sorular →](references/soru-akisi.md) · Belgelerde cevaplananları tekrarlamadan, ilk turda yalnız belirleyici 3–5 eksik soru.

[Kiracı sorunları: 10 kurgu senaryo, belge listeleri ve gerçek emsaller →](references/kiraci-senaryolari.md)

Kiracının sorunundan ilgili karara ulaşmak için API anahtarı gerektirmeyen senaryo aracı:

```sh
python scripts/scenarios.py list
python scripts/scenarios.py search "rutubet depozito"
python scripts/scenarios.py show K6
```

Her senaryo gerekli belgeleri, sonucu değiştiren soruları ve emsalin sınırlarını gösterir. Kurgu olaylar gerçek karar metinlerinden ayrıdır; sıralama kazanma ihtimali değildir.

[Süre formülleri ve hesap rehberi →](references/sure-hesaplama.md)

```sh
python scripts/deadlines.py tbk345 2026-09-01
python scripts/deadlines.py takvim 2026-01-31 --count 1 --unit ay
```

Araç gün/ay/yıl ayrımını, ilgili kira sürelerini ve UETS hesabını gösterir. Sonuçlar takvim adayıdır; tatil, arabuluculuk ve somut dosyanın hukuki koşulları ayrıca kontrol edilir.

### Süre ve Dava Takvimi Hesaplayıcı

TBK 344/345 bildirim ve dava açma süreleri, 5 yıllık hak ve nesafet dönemi ile TBK 347 uyarınca 10 yıllık uzama tahliye takvimini yerel olarak hesaplayan araç:

```sh
# Kira tespiti süre ve hedef dönem analizi (artış şartı, ihtar ve dava denetimi)
python scripts/hesap.py tespit --baslangic 01.07.2018 --artis-sarti --dava-tarihi 15.05.2024 --hedef-donem 01.07.2024

# 10 yıllık uzama süresi sonu tahliye takvimi (yıldönümü ve bildirim adayları)
python scripts/hesap.py tahliye-10yil --baslangic 01.01.2015

# Kronolojik kira dönemleri ve hak-nesafet / ara yıl çizelgesi
python scripts/hesap.py donemler --baslangic 15.09.2017
```

**Dosyanın güçlü ve zayıf yönlerini görmek için**

> $kira-tespit-asistani sözleşmeyi ve olayları incele. Talep edilen dönem bakımından belirleyici konuları, eksik belgeleri ve karşı tarafın ileri sürebileceği itirazları göster.

**Cevap dilekçesi hazırlamak için**

> $kira-tespit-asistani sözleşme ve dava dilekçesine dayanarak cevap dilekçesi taslağı hazırla. Dayandığın kararları tam metinden doğrula.

**Bilirkişi raporunu değerlendirmek için**

> $kira-tespit-asistani bilirkişi raporundaki emsalleri ve hesap yöntemini incele; dosyadaki belgelere bağlı somut itirazları belirle.

## Çalışma akışı

| Aşama | Yapılan iş |
| :--- | :--- |
| **01 · Dosyayı anla** | Belgelerden olgu ve tarih çizelgesi çıkarılır. |
| **02 · Soruyu belirle** | Sonucu değiştiren hukuki meseleler ayrıştırılır. |
| **03 · Kaynağı araştır** | İlgili kanun hükümleri ve karar tam metinleri okunur. |
| **04 · Karşılaştır** | Lehe/aleyhe gerekçeler, olgusal farklar ve dönem incelenir. |
| **05 · Sonucu hazırla** | Kaynaklara bağlı değerlendirme veya taslak oluşturulur. |

Skill, ilgili kaynakları paket içinden seçerek okur; kararlarla yeniden eğitilmiş bir model değildir. [Ayrıntılı çalışma mantığı →](references/calisma-mantigi.md)

## Veri kapsamı

Yerel karar havuzu kira tespiti ağırlıklıdır. Diğer kira hukuku konuları [modüller](references/moduller.md) üzerinden bağlı karar ve mevzuat kaynaklarında araştırılır. İsteğe bağlı [TypeSafe entegrasyonu](references/typesafe.md), karma talepleri yönlendirir ve karar adaylarını sıralar; hukuki sonuç veya dava başarı oranı üretmez. TypeSafe kullanımı ayrıca API anahtarı ve ağ erişimi gerektirir. [Legaluga MCP](references/legaluga.md) bağlıysa güncel mevzuat ve içtihat varsayılan olarak oradan araştırılır; araç sonuçları paket verisini değiştirmez ve künye/alıntı ön denetimi hukuki doğrulama yerine geçmez. Mevcut `$kira-tespit-asistani` çağrısı korunmuştur.

| | |
| :--- | :--- |
| **Karar havuzu** | 1.603 karar · 14.10.2004–21.05.2026 |
| **İçerik türü** | 446 esas gerekçesi · 549 usul gerekçesi · 11 sınırda · 570 kısa karar (model etiketi, insan onaysız) |
| **Dağılım** | 1.024 karar 3. HD, 539 karar 6. HD; 1.212 karar 2010–2015, 71 karar 2020 ve sonrası |
| **Kaynak izi** | Ana havuzda Bedesten belge kimliği ve ondan türetilen resmî adres; seçkilerde kayıttaki adres |
| **Mevzuat** | 6098 sayılı Türk Borçlar Kanunu |
| **Kaynak kontrolü** | Künye, resmî adres, metin hash'i ve birebir alıntı doğrulaması |
| **Otomatik denetim** | Windows ve Linux üzerinde paket bütünlüğü kontrolleri |

> [!NOTE]
> Veri paketi sabit bir kopyadır; kendiliğinden güncellenmez. Karar etiketleri bağımsız hukukçu doğrulamasından geçmemiştir. Havuzun ağırlığı 2010–2015 dönemindedir; 2019 TÜFE sınırı ve 2023 geçici artış sınırı gibi güncel rejim için havuz incedir, güncel içtihat ayrıca araştırılır. Somut dosyada uygulanacak hükmün dönemi ve güncelliği ayrıca kontrol edilir. Güncel kaynak araştırması, asistanın internet ve araç erişimine bağlıdır.

## Komut satırı

Depo kökünde çalıştırın. Sisteminizde gerekirse `python` yerine `python3` kullanın.

```sh
# Havuzun kapsamını görün
python scripts/pool.py stats

# İlgili kararları arayın
python scripts/pool.py search "eski kiracı" --kind esas_gerekcesi --limit 8

# Kanun maddesini okuyun
python scripts/tbk.py 344

# Canlı metinden okunan pasajı boşluk farkı gözetmeden yerel kayıtta bulun
python scripts/pool.py quote KARAR_KIMLIGI "Pasaj" --ignore-space

# Legaluga'nın döndürdüğü imzasız UDF taslağını doğrulayıp kaydedin
python scripts/udf.py kaydet yanit.b64 --sha256 YANITTAKI_SHA256 --cikti dilekce.udf

# Paketin bütünlüğünü kontrol edin
python scripts/validate.py
```

<details>
<summary>Depo yapısı</summary>

```text
kira-tespit-asistani/
├── SKILL.md             Asistan yönergeleri
├── agents/              Codex görünüm bilgileri
├── data/                Karar havuzu, mevzuat ve kaynak kayıtları
├── references/          Çalışma akışı ve kullanım rehberleri
├── scripts/             Arama, madde erişimi ve doğrulama
└── .github/workflows/   Otomatik paket kontrolleri
```

</details>

## Rehberler

**[Kararlardan hazırlanmış 10 soru ve kaynaklı örnek yanıt →](references/kararlardan-soru-yanit.md)** Olay sorusu, gerekçe, hüküm, belirleyici belgeler ve uygulama sınırları; yanıtlar açılır bölümlerdedir.

[49 özgün dosyayla sınama ve 10 yapılandırılmış karar kartı](references/kalite-sinama.md): hukuki ayrım, gerekli sorular ve kritik yanlış sonuçlar için inceleme ölçütleri. Yanıtlar insan değerlendirmesiyle puanlanır; henüz canlı model başarı oranı ölçülmedi.

| Başlamak için | Ayrıntıya inmek için |
| :--- | :--- |
| [Skill yönergeleri](SKILL.md) | [Karar havuzu ve arama komutları](references/havuz.md) |
| [Çalışma mantığı](references/calisma-mantigi.md) | [Borçlar Kanunu erişimi](references/mevzuat.md) |
| [Kira tespiti ve hak ve nesafet](references/uygulama-rehberi.md) | [Fazla ödeme iadesi ve ispat](references/iade-ispat.md) |
| [Kira türü, usul ve taraflar](references/kira-rejimi-ve-taraflar.md) | [30 emsalin doğrulama durumu](references/emsal-listesi-dogrulama.md) |
| [Teslim, masraf, kefalet ve devir](references/teslim-masraf-kefalet.md) | [Karar kaynak kayıtları](references/egitim-kaynak-kaydi.json) |
| [Tahliye ve uyarlama kaynak kontrolü](references/tahliye-ve-uyarlama-kontrol.md) | Arabuluculuk zamanı, taahhüt, aile konutu, iki ihtar, yeniden kiralama ve tedbir |
| [Kira mevzuatı haritası](references/mevzuat-haritasi.md) | Maddi hukuk, usul, icra, kamu kiraları, aidat, döviz, dönüşüm ve vergi |
| [Legaluga MCP akışı](references/legaluga.md) | Güncel mevzuat, emsal araştırması, künye/alıntı ön denetimi ve UDF taslağı |
| [Rehber kaynak kontrolü](references/rehber-dogrulama.md) | [BAM kararları ve kullanım sınırları](references/bam-kararlari.md) |
| [Katkı rehberi](CONTRIBUTING.md) | [Veri kaynakları ve bütünlük](data/README.md) |

## Lisans

Betikler, rehberler, etiketler ve yönergeler [MIT lisansı](LICENSE) ile dağıtılır. Mahkeme kararları ve kanun metni resmî metinlerdir; 5846 sayılı Kanun'un 31. maddesi gereği serbestçe çoğaltılabilir, lisans bu metinler üzerinde hak iddia etmez.

---

<div align="center">

**Bir hata mı buldunuz, bir öneriniz mi var?**

[Issue açın](https://github.com/hasanimer/kira-hukuku-skill/issues) · [Katkı rehberini okuyun](CONTRIBUTING.md)

</div>
