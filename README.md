<div align="center">

# Kira Hukuku Asistanı

**Dosyadan içtihada, içtihattan gerekçeli taslağa.**

Kira tespiti, tahliye, uyarlama, alacak ve depozito dosyaları için kaynaklara dayalı araştırma ve dilekçe hazırlama becerisi.

[![Paket kontrolü](https://github.com/hasanimer/kira-hukuku-skill/actions/workflows/validate.yml/badge.svg)](https://github.com/hasanimer/kira-hukuku-skill/actions/workflows/validate.yml)
![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square)
![Codex Skill](https://img.shields.io/badge/Codex-Skill-111827?style=flat-square)
![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-D97757?style=flat-square)

[Hızlı başlangıç](#hızlı-başlangıç) · [Kullanım örnekleri](#kullanım-örnekleri) · [Çalışma akışı](#çalışma-akışı) · [Veri kapsamı](#veri-kapsamı) · [Komut satırı](#komut-satırı) · [Rehberler](#rehberler)

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

> [!IMPORTANT]
> Bu skill'in çıktıları hukuki danışmanlık veya avukat mütalaası değildir. Değerlendirmeler ve dilekçeler taslaktır; süre hesapları takvim adayıdır. Tatil, arabuluculuk, tebligat tarihi ve uygulanacak mevzuat sürümü bir avukat tarafından doğrulanmadan dava açılmamalı, ihtar gönderilmemeli veya süreye dayalı işlem yapılmamalıdır. Sözleşme, dilekçe ve müvekkil belgelerini paylaşmadan önce kişisel veriler (KVKK) ve sır saklama yükümlülükleri bakımından değerlendirin.

## Hızlı başlangıç

**Gerekenler:** Codex veya Claude Code, Git ve Python 3.10+. Yerel yardımcılar yalnız Python standart kütüphanesini kullanır. `python scripts/...` komutlarını skill (depo) kökünde çalıştırın; sisteminizde `python` komutu yoksa `python3` (Windows'ta gerekirse `py -3`) kullanın.

### 1. Skill'i ekleyin

Hedef klasörün adı skill adıyla aynı olmalıdır: `kira-tespit-asistani`. Varsayılan `git clone` klasörü `kira-hukuku-skill` adıyla oluşturur; bu yüzden hedef yolu açıkça yazın.

**Codex**

```sh
git clone https://github.com/hasanimer/kira-hukuku-skill.git "$HOME/.codex/skills/kira-tespit-asistani"
```

**Claude Code — tüm projeleriniz için**

```sh
git clone https://github.com/hasanimer/kira-hukuku-skill.git "$HOME/.claude/skills/kira-tespit-asistani"
```

**Claude Code — yalnız bir proje için (proje kökünde çalıştırın)**

```sh
git clone https://github.com/hasanimer/kira-hukuku-skill.git ".claude/skills/kira-tespit-asistani"
```

<details>
<summary>Kurulum yolu ve mevcut kurulum hakkında</summary>

Komut PowerShell, Bash ve Zsh ile kullanılabilir. Özel bir `CODEX_HOME` kullanıyorsanız hedef olarak onun `skills` dizinini seçin. Hedef klasörde mevcut bir kopya varsa üzerine yazmadan önce değişikliklerinizi koruyun. Proje içi Claude Code kurulumunda iç içe bir Git deposu oluşur; klasörü projenin `.gitignore` dosyasına ekleyin veya `git submodule add` ile bağlayın.

</details>

**Güncelleme**

```sh
git -C "$HOME/.codex/skills/kira-tespit-asistani" pull --ff-only
python "$HOME/.codex/skills/kira-tespit-asistani/scripts/validate.py"
```

Claude Code kurulumunda yolu `$HOME/.claude/skills/kira-tespit-asistani` (veya `.claude/skills/kira-tespit-asistani`) olarak değiştirin. Doğrulama PASS vermezse dosyayla çalışmadan önce sorunu giderin.

### 2. Skill'i çağırın

Codex:

```text
$kira-tespit-asistani kira tespit dosyamı incele;
eksik belgeleri ve lehe/aleyhe emsalleri göster.
```

Claude Code:

```text
/kira-tespit-asistani kira tespit dosyamı incele;
eksik belgeleri ve lehe/aleyhe emsalleri göster.
```

Depo adı `kira-hukuku-skill` olsa da skill adı `kira-tespit-asistani` olarak korunmuştur: Codex'te `$kira-tespit-asistani`, Claude Code'da `/kira-tespit-asistani`. Claude Code, istek skill açıklamasıyla eşleştiğinde skill'i adı yazılmadan da yükleyebilir. Aşağıdaki örneklerdeki `$` öneki Codex içindir; Claude Code'da `/` kullanın.

### 3. Dosyanızla çalışın

İlgili sözleşmeyi, dilekçeyi veya raporu paylaşın; istediğiniz çıktıyı belirtin. Asistan önce belirleyici olguları çıkarır, ardından ilgili kaynakları araştırır.

[Yargıtay ek seçkisi ve kullanım notları →](references/yargitay-kararlari.md)

## Kullanım örnekleri

### Örnek istemler

**Dosyanın güçlü ve zayıf yönlerini görmek için**

> $kira-tespit-asistani sözleşmeyi ve olayları incele. Talep edilen dönem bakımından belirleyici konuları, eksik belgeleri ve karşı tarafın ileri sürebileceği itirazları göster.

**Cevap dilekçesi hazırlamak için**

> $kira-tespit-asistani sözleşme ve dava dilekçesine dayanarak cevap dilekçesi taslağı hazırla. Dayandığın kararları tam metinden doğrula.

**Bilirkişi raporunu değerlendirmek için**

> $kira-tespit-asistani bilirkişi raporundaki emsalleri ve hesap yöntemini incele; dosyadaki belgelere bağlı somut itirazları belirle.

[Dosyaya göre sorulacak sorular →](references/soru-akisi.md) · Belgelerde cevaplananları tekrarlamadan, ilk turda yalnız belirleyici 3–5 eksik soru.

### Kiracı senaryoları

[Kiracı sorunları: 10 kurgu senaryo, belge listeleri ve gerçek emsaller →](references/kiraci-senaryolari.md)

Kiracının sorunundan ilgili karara ulaşmak için API anahtarı gerektirmeyen senaryo aracı:

```sh
python scripts/scenarios.py list
python scripts/scenarios.py search "rutubet depozito"
python scripts/scenarios.py show K6
```

Her senaryo gerekli belgeleri, sonucu değiştiren soruları ve emsalin sınırlarını gösterir. Kurgu olaylar gerçek karar metinlerinden ayrıdır; sıralama kazanma ihtimali değildir.

### Süre ve kira dönemi hesapları

[Süre formülleri ve hesap rehberi →](references/sure-hesaplama.md)

```sh
python scripts/deadlines.py tbk345 2026-09-01
python scripts/deadlines.py tbk350 2026-01-31
python scripts/deadlines.py takvim 2026-01-31 --count 1 --unit ay
python scripts/deadlines.py takvim 2026-09-01 --count 15 --unit gun --geri
python scripts/deadlines.py uets 2026-09-01
```

Tarihler YYYY-AA-GG, GG.AA.YYYY veya GG/AA/YYYY biçiminde girilebilir; `deadlines.py` çıktıyı YYYY-AA-GG, `hesap.py` GG.AA.YYYY biçiminde verir. Tek bir sürenin ham hesabı için `deadlines.py`, kira dönemi çizelgesi ve TBK 345 hedef dönem koşulu için `hesap.py` kullanılır.

`deadlines.py` gün/ay/yıl ayrımını, ilgili kira sürelerini ve UETS hesabını gösterir. Sonuçlar takvim adayıdır; tatil, arabuluculuk ve somut dosyanın hukuki koşulları ayrıca kontrol edilir.

**Kira dönemi ve süre takvimi hesaplayıcı (`hesap.py`):** kira dönemi çizelgesini, beş yıllık dönem adaylarını (TBK 344/3), hedef dönem için TBK 345/2–3 tarih koşullarını (yeni dönemden en az otuz gün önce dava veya yazılı bildirim; dönem sonuna kadar dava) ve TBK 347 on yıllık uzama sonrası fesih bildirimi takvimini yerel olarak hesaplar. TBK 345/1 uyarınca tespit davası her zaman açılabilir; araç genel dava açma son günü vermez, yalnız kararın hangi dönemden etkili olabileceğine ilişkin takvim adayı üretir:

```sh
# Kira tespiti hedef dönem analizi (artış şartı, ihtar ve dava tarihi denetimi; geçiş hükmü uyarıları)
python scripts/hesap.py tespit --baslangic 01.07.2018 --artis-sarti --dava-tarihi 15.05.2024 --hedef-donem 01.07.2024

# 10 yıllık uzama süresi sonu tahliye takvimi (--sure-yil: ilk sözleşme süresi, yıl; tam yıl değilse --sure-ay
# veya --ilk-bitis; hiçbiri verilmezse 12 ay varsayılır ve çıktıda uyarılır)
python scripts/hesap.py tahliye-10yil --baslangic 01.01.2015 --sure-yil 1
python scripts/hesap.py tahliye-10yil --baslangic 01.01.2015 --sure-yil 3   # ilk hedef 01.01.2029; ihtar en geç 30.09.2028 (temkinli; yıldönümü eşiği 01.10.2028)
python scripts/hesap.py tahliye-10yil --baslangic 01.01.2015 --sure-ay 11   # ilk hedef 01.12.2026; ihtar en geç 30.08.2026 (temkinli)

# Kronolojik kira dönemleri, beş yıllık takvim döngüsü ve koşullu TBK 344/3 aday çizelgesi
python scripts/hesap.py donemler --baslangic 15.09.2017
```

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

Yerel karar havuzu kira tespiti ağırlıklıdır. Diğer kira hukuku konuları [modüller](references/moduller.md) üzerinden bağlı karar ve mevzuat kaynaklarında araştırılır. İsteğe bağlı [TypeSafe entegrasyonu](references/typesafe.md), karma talepleri yönlendirir ve karar adaylarını sıralar; hukuki sonuç veya dava başarı oranı üretmez. TypeSafe kullanımı ayrıca API anahtarı ve ağ erişimi gerektirir; ücretli canlı çağrı yalnız kullanıcı istediğinde veya onay verdiğinde yapılır.

| | |
| :--- | :--- |
| **Karar havuzu** | 1.603 karar · 14.10.2004–21.05.2026 |
| **İçerik türü** | 471 esas gerekçesi · 551 usul gerekçesi · 11 sınırda · 570 kısa karar (ana havuzda model etiketi, BAM/Yargıtay seçkilerinde asistan etiketi; insan onaysız) |
| **Dağılım** | 1.576 ana havuz · 17 BAM seçkisi · 10 Yargıtay seçkisi; 1.032 karar Yargıtay 3. HD, 540 karar Yargıtay 6. HD; 1.213 karar 2010–2015, 90 karar 2020 ve sonrası |
| **Kaynak izi** | Ana havuzda Bedesten belge kimliği ve ondan türetilen resmî adres; seçkilerde kayıttaki adres |
| **Mevzuat** | 6098 sayılı Türk Borçlar Kanunu |
| **Kaynak kontrolü** | Metin hash'i ve birebir alıntı doğrulaması; künye kayıttaki alanlardan, ana havuzda resmî adres belge kimliğinden türetilir (adres çevrimdışı açılıp doğrulanmaz) |
| **Otomatik denetim** | Windows, macOS ve Linux üzerinde, Python 3.10 ve 3.14 ile paket bütünlüğü kontrolleri ve birim testleri |

> [!NOTE]
> Veri paketi sabit bir kopyadır; kendiliğinden güncellenmez. Karar etiketleri bağımsız hukukçu doğrulamasından geçmemiştir. Havuzun ağırlığı 2010–2015 dönemindedir; 01.01.2019'dan itibaren geçerli TÜFE sınırı (7161 s.K.) ile konut kiralarında 11.06.2022–01.07.2024 (dahil) arasında yenilenen dönemlere uygulanan ve artık yeni dönemlere uygulanmayan geçici %25 sınırı (TBK geçici m. 1–2; 7409 ve 7456 s.K.) gibi yakın tarihli düzenlemeler için havuz incedir; bunlara ilişkin içtihat ayrıca araştırılır. Somut dosyada uygulanacak hükmün dönemi ve güncelliği ayrıca kontrol edilir. Güncel kaynak araştırması, asistanın internet ve araç erişimine bağlıdır.

## Komut satırı

Depo kökünde çalıştırın; başka bir dizinden çalışıyorsanız betiğin mutlak yolunu verin (`python`/`python3` notu için [Hızlı başlangıç](#hızlı-başlangıç)).

```sh
# Havuzun kapsamını görün
python scripts/pool.py stats

# İlgili kararları arayın
python scripts/pool.py search "eski kiracı" --kind esas_gerekcesi --limit 8

# Kanun maddesini okuyun
python scripts/tbk.py 344

# Paketin bütünlüğünü kontrol edin
python scripts/validate.py
```

<details>
<summary>Depo yapısı</summary>

```text
kira-tespit-asistani/
├── SKILL.md             Asistan yönergeleri
├── README.md            Tanıtım, kurulum ve komutlar
├── CONTRIBUTING.md      Katkı rehberi
├── LICENSE              MIT lisansı
├── agents/              Codex görünüm bilgileri (openai.yaml)
├── data/                Karar havuzu, TBK metni, kaynak kayıtları ve SHA-256 manifesti
├── references/          Çalışma akışı, modül rehberleri, senaryolar ve karar kartları
├── scripts/             Yerel yardımcılar (yalnız Python standart kütüphanesi)
│   ├── pool.py          Karar havuzunda arama, tam metin ve birebir alıntı doğrulama
│   ├── tbk.py           6098 sayılı TBK madde erişimi
│   ├── hesap.py         Kira dönemi çizelgesi, TBK 345 hedef dönem koşulu ve TBK 347 takvimi
│   ├── deadlines.py     Kira süreleri ve UETS için takvim adayları
│   ├── scenarios.py     Kiracı senaryoları ve bağlı gerçek emsaller
│   ├── triage.py        İsteğe bağlı TypeSafe yönlendirmesi ve aday sıralama
│   ├── quality.py       Sınama seti, karar kartları ve insan değerlendirmesi puanlama
│   ├── decision_qa.py   Kararlardan hazırlanmış soru–yanıt seti
│   └── validate.py      Paket bütünlüğü ve komut kontrolleri
├── evals/               Sınama dosyaları (cases.json), tetiklenme sorguları (trigger-cases.json) ve karar soru–yanıtları (decision-qa.json)
├── tests/               Birim testleri (python -m unittest discover -s tests -v)
└── .github/             Otomatik paket kontrolleri (workflows/) ve Dependabot ayarı
```

</details>

## Rehberler

**[Kararlardan hazırlanmış 10 soru ve kaynaklı örnek yanıt →](references/kararlardan-soru-yanit.md)** Olay sorusu, gerekçe, hüküm, belirleyici belgeler ve uygulama sınırları; yanıtlar açılır bölümlerdedir.

[58 özgün dosyayla sınama ve 10 yapılandırılmış karar kartı](references/kalite-sinama.md): hukuki ayrım, gerekli sorular ve kritik yanlış sonuçlar için inceleme ölçütleri. Yanıtlar insan değerlendirmesiyle puanlanır; henüz canlı model başarı oranı ölçülmedi.

| Başlamak için | Ayrıntıya inmek için |
| :--- | :--- |
| [Skill yönergeleri](SKILL.md) | [Karar havuzu ve arama komutları](references/havuz.md) |
| [Çalışma mantığı](references/calisma-mantigi.md) | [Borçlar Kanunu erişimi](references/mevzuat.md) |
| [Kira tespiti ve hak ve nesafet](references/uygulama-rehberi.md) | [Fazla ödeme iadesi ve ispat](references/iade-ispat.md) |
| [Kira türü, usul ve taraflar](references/kira-rejimi-ve-taraflar.md) | [30 emsalin doğrulama durumu](references/emsal-listesi-dogrulama.md) |
| [Teslim, masraf, kefalet ve devir](references/teslim-masraf-kefalet.md) | [Karar kaynak kayıtları](references/egitim-kaynak-kaydi.json) |
| [Tahliye ve uyarlama kaynak kontrolü](references/tahliye-ve-uyarlama-kontrol.md)<br><sub>Arabuluculuk zamanı, taahhüt, aile konutu, iki ihtar, yeniden kiralama ve tedbir</sub> | [Kira hukuku modülleri](references/moduller.md) |
| [Kira mevzuatı haritası](references/mevzuat-haritasi.md)<br><sub>Maddi hukuk, usul, icra, kamu kiraları, aidat, döviz, dönüşüm ve vergi</sub> | [Kira hukukunda süre hesabı](references/sure-hesaplama.md) |
| [Rehber kaynak kontrolü](references/rehber-dogrulama.md) | [BAM kararları ve kullanım sınırları](references/bam-kararlari.md) |
| [Katkı rehberi](CONTRIBUTING.md) | [Veri kaynakları ve bütünlük](data/README.md) |

## Lisans

Betikler, rehberler, etiketler, karar kartları ve yönergeler [MIT lisansı](LICENSE) ile dağıtılır. `data/` altındaki mahkeme kararları ve 6098 sayılı Türk Borçlar Kanunu metni resmî metinlerdir; 5846 sayılı Fikir ve Sanat Eserleri Kanunu'nun 31. maddesi uyarınca, resmen yayımlanmış veya ilan edilmiş olmak şartıyla çoğaltılabilir ve yayılabilir. MIT lisansı bu metinler üzerinde hak iddiası doğurmaz. Karar koleksiyonlarının kaynakları (ana havuz: UYAP Mevzuat ve İçtihat/Bedesten; Yargıtay ve BAM seçkileri: Dejure) ile bütünlük bilgileri [veri notunda](data/README.md) belirtilir; bu açıklama, metinlerin alındığı üçüncü taraf veri tabanlarının kullanım koşullarını kendiliğinden ortadan kaldırmaz.

---

<div align="center">

**Bir hata mı buldunuz, bir öneriniz mi var?**

[Issue açın](https://github.com/hasanimer/kira-hukuku-skill/issues) · [Katkı rehberini okuyun](CONTRIBUTING.md)

</div>
