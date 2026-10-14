"""Kira kararları havuzuna salt okunur, hash denetimli erişim (yalnız standart kütüphane).

Her okumada kayıt metinlerinin SHA-256 değeri denetlenir; data/manifest.json varsa
karar dosyalarının SHA-256 değerleri de manifestle karşılaştırılır.
Komutlar: stats, search, get, quote.
"""
import argparse
import bisect
import collections
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import unicodedata

# Ana havuzdaki document_id UYAP Mevzuat ve İçtihat (Bedesten) belge kimliğidir; resmî
# adres bu desenle türetilir. Kayıtta yazılı source_url varsa ona dokunulmaz.
BEDESTEN_URL = 'https://mevzuat.adalet.gov.tr/ictihat/{}'
# Okunan havuz dosyaları; ilki zorunlu ana havuzdur, seçkiler varsa eklenir.
POOL_FILES = ('topic-rescan-assistant-adjusted.jsonl', 'bam-selected.jsonl',
              'yargitay-selected.jsonl', 'derleme-v5-selected.jsonl')
MAIN_POOL = POOL_FILES[0]
# Ana havuzla birlikte okunan seçkiler; kayıt hangi dosyadan geldiyse collection alanı onu gösterir.
SELECTIONS = POOL_FILES[1:]
EXIT_OK, EXIT_DATA, EXIT_USAGE, EXIT_NOT_FOUND = 0, 1, 2, 3
EPILOG = (
    'Çıkış kodları: 0 başarılı; 1 veri/bütünlük hatası (hash veya manifest uyuşmazlığı, tekrarlanan kimlik,\n'
    'okunamayan dosya; stderr "HATA (veri bütünlüğü)" ile başlar) ya da çıktıyı okuyan sürecin erken kapanması (ör. | head;\n'
    'Linux/macOS\'ta stderr boş kalır; Windows\'ta "[Errno 22] Invalid argument" içeren bir HATA iletisi\n'
    'görünebilir; ikisi de veri hatası değildir); 2 kullanım hatası; 3 bulunamadı (quote: alıntı\n'
    'belgede yok — --ignore-space ile boşluk farkı yok sayılarak da bulunamadı —, JSON yine basılır ve\n'
    'exact_match false olur; get/quote: kimlik havuzda yok, stdout boş kalır).\n'
    '"-" ile başlayan alıntı için: python scripts/pool.py quote KARAR_KIMLIGI -- "-alıntı"')
# Arama sıralaması: konu dışı kayıt en sona; sonra içerik türü, kapsam belirsizliği, sözcük geçişi.
KIND_ORDER = {'esas_gerekcesi': 0, 'usul_gerekcesi': 1, 'sinirda': 2, 'kisa_karar': 3}
ISO_DATE = re.compile(r'\d{4}-\d{2}-\d{2}')
# Yeniden taramada hariç olasılığı bu eşiği aşan incelenmemiş kayıt konu bakımından sınırdadır.
SCOPE_HARIC_THRESHOLD = 0.30
# Tam metinle konu dışı görülen kayıtlar; veri baytları değişmeden okuma sırasında işaretlenir.
SCOPE_CAUTIONS = {
    ('1018247800', '144a842b557ad46f06ebd18de8b0b419adfe739921f9ca1f36ab29904057ebdd'): {
        'outcome': 'Ticaret mahkemesi kararı oybirliğiyle onanmıştır; Yargıtay gerekçesi kısa onamadır.',
        'cautions': [('TCDD liman hizmetleri tarifesine dayalı yüzer vinç kirası; TBK 344 kira '
                      'tespiti veya konut/çatılı işyeri kirası emsali değildir.')]},
    ('504158200', 'ee67ea4dd909a2a898a1316dc5c02a2dcc980fd3401690a67291aba02c188f79'): {
        'outcome': 'Ticaret mahkemesi kararı oy çokluğuyla onanmıştır; çoğunluk gerekçesi kısa '
                   'onamadır.',
        'cautions': [('Fokker 100 uçak kirası; TBK 344 kira tespiti veya konut/çatılı işyeri '
                      'kirası emsali değildir.'),
                     ('Kira bedeli, depozito ve yedek parça değerlendirmesi yalnız karşıoydadır; '
                      'çoğunluk görüşü sayılmaz.')]},
}
COURT_SHORT = (
    (re.compile(r'Bölge Adliye Mahkemesi'), 'BAM'),
    (re.compile(r'Hukuk Genel Kurulu'), 'HGK'),
    (re.compile(r'Hukuk Daireleri Başkanlar Kurulu'), 'HDBK'),
    (re.compile(r'Ceza Genel Kurulu'), 'CGK'),
    (re.compile(r'(\d+)\. Hukuk Dairesi'), r'\1. HD'),
    (re.compile(r'(\d+)\. Ceza Dairesi'), r'\1. CD'),
)
QUOTE_MAX_OCCURRENCES = 20
QUOTE_MIN_LENGTH = 20
SNIPPET_WIDTH = 1400
# Kesme, tırnak ve tire biçimleri tek biçime indirilir; yumuşak tire atılır.
_PUNCT = str.maketrans({'’': "'", '‘': "'", 'ʼ': "'", '´': "'",
                        '`': "'", '“': '"', '”': '"', '–': '-',
                        '—': '-', '­': None})
# Kapanış cümlesi: "GG.AA.YYYY tarihinde/gününde/günü ... karar verildi". Noktadan sonra boşluklu
# yazımı kabul eder; karartılmış tarih ("....01.2013") eşleşmez ve önceki bir tarihe geri düşülmez.
CLOSING_DATE = re.compile(
    r'(\d{1,2})\s*[./]\s*(\d{1,2})\s*[./]\s*(\d{4})\s*(?:tarihinde|gününde|günü)\b[^.]{0,80}?'
    r'karar\s+verildi')


def fold(text):
    """normalize() katlaması, boşluklar daraltılmadan (karakter ofseti eşlemesi için)."""
    # translate NFKD'den önce çalışmalı; yoksa ´ işareti boşluğa dönüşür.
    text = text.translate(_PUNCT).replace('ı', 'i').replace('İ', 'i').casefold()
    return ''.join(c for c in unicodedata.normalize('NFKD', text)
                   if not unicodedata.combining(c))


def normalize(text):
    """Büyük/küçük harf, aksan, kesme/tırnak/tire biçimi ve fazla boşluk farkını giderir."""
    return ' '.join(fold(text).split())


def term_pattern(term, substring=False):
    """term normalize() edilmiş olmalı. Varsayılan: sözcük başından eşleşir; rakamla biten
    terim daha uzun sayının parçası olarak eşleşmez. '/' sınır sayılmaz: '344' terimi '344/3'
    atfını bulur."""
    body = re.escape(term)
    if substring:
        return re.compile(body)
    start = r'(?<!\w)' if re.match(r'\w', term) else ''
    end = r'(?!\d)' if term[-1].isdigit() else ''
    return re.compile(start + body + end)


def snippet_of(paragraph, patterns, width=SNIPPET_WIDTH):
    """Uzun paragrafı ilk eşleşmenin çevresinden keser; normalize ofsetini özgün metne eşler."""
    if len(paragraph) <= width:
        return paragraph
    starts, pieces, length, after_space = [], [], 0, True
    for char in paragraph:
        starts.append(length)
        piece = []
        for c in fold(char):  # karakter bazında katlama + boşluk daraltma = normalize()
            if c.isspace():
                if after_space:
                    continue
                c, after_space = ' ', True
            else:
                after_space = False
            piece.append(c)
        pieces.append(''.join(piece))
        length += len(pieces[-1])
    flat = ''.join(pieces)
    hits = [m.start() for m in (p.search(flat) for p in patterns) if m]
    if not hits:
        return paragraph[:width]
    hit = bisect.bisect_right(starts, min(hits)) - 1
    begin = max(0, min(hit - width // 3, len(paragraph) - width))
    end = begin + width
    return ('…' if begin else '') + paragraph[begin:end] + ('…' if end < len(paragraph) else '')


def read_rows(path, bedesten_ids=None):
    """Kayıtları biçim, tekrar ve metin hash'i denetimiyle okur.
    Bedesten adresi varsayılan olarak yalnız ana havuz dosyasındaki kayıtlar için türetilir."""
    if bedesten_ids is None:
        bedesten_ids = path.name == MAIN_POOL
    seen = set()
    with path.open(encoding='utf-8-sig') as stream:
        for line_no, line in enumerate(stream, 1):
            if not line.strip():
                continue
            where = f'{path.name}:{line_no}'
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f'Invalid JSON ({where}): {exc.msg}, column {exc.colno}') from None
            if not isinstance(row, dict):
                raise ValueError(f'Record is not a JSON object ({where})')
            for field in ('document_id', 'text', 'text_sha256'):
                if field not in row:
                    raise ValueError(f'Missing field {field!r} ({where})')
            if not isinstance(row['text'], str) or not isinstance(row['text_sha256'], str):
                raise ValueError(f'text and text_sha256 must be strings ({where})')
            assessment = row.get('value_assessment')
            if assessment is not None and not isinstance(assessment, dict):
                raise ValueError(f'value_assessment must be an object ({where})')
            date = row.get('karar_tarihi')
            if date not in (None, '') and not (isinstance(date, str) and ISO_DATE.fullmatch(date)):
                raise ValueError(f'karar_tarihi must be YYYY-MM-DD ({where}): {date!r}')
            key = str(row['document_id'])
            if key in seen:
                raise ValueError(f'Duplicate document_id: {key} ({where})')
            seen.add(key)
            actual = hashlib.sha256(row['text'].encode('utf-8')).hexdigest()
            if actual != row['text_sha256']:
                raise ValueError(f'Text hash mismatch: {key} ({where})')
            if not str(row.get('court') or '').strip():
                raise ValueError(f'Missing court: {key} ({where})')
            row['collection'] = path.name
            yield enrich(row, bedesten_ids=bedesten_ids)


def read_manifest(root):
    path = Path(root) / 'manifest.json'
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding='utf-8'))


def verify_manifest(root, digests):
    """root/manifest.json varsa, verilen dosya hash'lerini manifestle karşılaştırır.
    digests: {Path: sha256_hex}. Manifest yoksa False döner (ör. --root ile test havuzu)."""
    manifest = read_manifest(root)
    if manifest is None:
        return False
    pinned = manifest.get('files', {})
    for path, digest in digests.items():
        name = Path(path).resolve().relative_to(Path(root).resolve()).as_posix()
        if name not in pinned:
            raise ValueError(f'File not pinned in manifest: {name}')
        if digest != pinned[name]:
            raise ValueError(f'File hash mismatch vs manifest: {name}')
    return True


def load_pool(data_root):
    """Havuz dosyalarını okur; (kayıtlar, çıktı zarfı) döner.
    Zarf yerel mutlak yol içermez: dosya adları ve SHA-256 değerleri `pool_files` alanındadır."""
    data_root = Path(data_root)
    sources = [data_root / MAIN_POOL] + [data_root / name for name in POOL_FILES[1:]
                                         if (data_root / name).exists()]
    digests = {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in sources}
    verified = verify_manifest(data_root, digests)
    if verified:
        pinned = read_manifest(data_root).get('files', {})
        missing = [name for name in POOL_FILES if name in pinned and not (data_root / name).exists()]
        if missing:
            raise ValueError(f'Pool file pinned in manifest is missing: {", ".join(missing)}')
    rows = []
    for path in sources:
        rows.extend(read_rows(path))
    ids = [str(row['document_id']) for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate document_id across pools')
    envelope = {'records': len(rows), 'pool_files': {p.name: d for p, d in digests.items()},
                'manifest_verified': verified}
    return rows, envelope


def kind_of(row):
    assessment = row.get('value_assessment')
    kind = assessment.get('icerik_turu') if isinstance(assessment, dict) else None
    return kind.get('choice') if isinstance(kind, dict) else None


def full_court(row):
    """Ana havuzda 'court' yalnız daire adıdır; künyede mahkeme adı da bulunmalı."""
    court = (row.get('court') or '').strip()
    if not court:
        raise ValueError(f"court alanı boş: {row.get('document_id')}")
    if 'Yargıtay' in court or 'Mahkemesi' in court:
        return court
    return f'Yargıtay {court}'


def kunye(row):
    """Dilekçe biçimi: mahkeme/daire, E., K., T. GG.AA.YYYY."""
    court = full_court(row)
    for pattern, short in COURT_SHORT:
        court = pattern.sub(short, court)
    date = row.get('karar_tarihi') or ''
    if re.fullmatch(r'\d{4}-\d{2}-\d{2}', date):
        date = '.'.join(reversed(date.split('-')))
    return f"{court}, E. {row.get('esas_no')}, K. {row.get('karar_no')}, T. {date}"


def enrich(row, bedesten_ids=False):
    """Türetilebilir alanları tamamlar; yazılı source_url/source_provider/court_type değerini
    ezmez, metne dokunmaz. `kunye` her çağrıda yapısal alanlardan (court, esas_no, karar_no,
    karar_tarihi) yeniden üretilir; böylece E./K./T. bilgisinden sapamaz.
    Bedesten adresi yalnız ana havuz kayıtları için (bedesten_ids=True) türetilir."""
    doc = str(row.get('document_id', ''))
    if bedesten_ids and not row.get('source_url') and doc.isdigit():
        row['source_url'] = BEDESTEN_URL.format(doc)
        row['source_provider'] = row.get('source_provider') or 'Bedesten (kimlikten türetildi)'
    if not row.get('court_type') and ('Yargıtay' in full_court(row)):
        row['court_type'] = 'yargitay'
    rescan = row.get('rescan_assessment')
    verdict = rescan.get('korpus_karari') if isinstance(rescan, dict) else None
    probabilities = verdict.get('probabilities') if isinstance(verdict, dict) else None
    if not isinstance(probabilities, dict):
        probabilities = {}
    haric = probabilities.get('haric')
    row['scope_haric_probability'] = haric
    caution = SCOPE_CAUTIONS.get((doc, row.get('text_sha256')))
    row['out_of_scope'] = caution is not None
    if caution and not row.get('research_notes'):
        row['research_notes'] = caution
    row['scope_uncertain'] = row['out_of_scope'] or (
        row.get('review_level') == 'not_reviewed' and
        isinstance(haric, (int, float)) and haric >= SCOPE_HARIC_THRESHOLD)
    row['kunye'] = kunye(row)
    return row


def text_decision_date(row):
    """Metnin kapanış cümlesindeki karar günü (YYYY-AA-GG) ya da None."""
    found = CLOSING_DATE.findall((row.get('text') or '')[-700:])
    if not found:
        return None
    day, month, year = found[-1]
    try:
        return datetime.date(int(year), int(month), int(day)).isoformat()
    except ValueError:
        return None


def metadata(row):
    keys = ('document_id', 'collection', 'kunye', 'court', 'esas_no', 'karar_no', 'karar_tarihi',
            'text_sha256', 'raw_sha256', 'human_validated', 'review_level', 'value_assessment',
            'court_type', 'source_url', 'source_provider', 'research_notes',
            'source_text_sha256', 'redactions', 'needs_scope_review', 'scope_uncertain',
            'scope_haric_probability', 'out_of_scope')
    meta = {key: row.get(key) for key in keys}
    closing = text_decision_date(row)
    if closing and row.get('karar_tarihi') and closing != row['karar_tarihi']:
        shown = '.'.join(reversed(closing.split('-')))
        provider = row.get('source_provider') or ''
        if row.get('collection') == MAIN_POOL or provider.startswith('Bedesten'):
            origin = ('Künye tarihi Bedesten üst verisidir; kapanış cümlesini alıntılarken farkı '
                      'belirt ve resmî sayfadan (source_url) kontrol et.')
        else:
            # Seçki kayıtlarının künyesi Dejure üst verisidir; source_url resmî sayfa değildir.
            origin = (f'Künye tarihi {provider or "kaynak"} üst verisidir; source_url resmî sayfa değildir. '
                      'Kapanış cümlesini alıntılarken farkı belirt ve tarihi resmî kayıttan '
                      '(UYAP Emsal / Yargıtay Karar Arama) doğrula.')
        meta['date_warning'] = (
            f'Metnin kapanış cümlesindeki karar günü {shown}, künye tarihinden farklı. ' + origin)
    return meta


def best_paragraph(text, patterns):
    """En çok farklı terimin geçtiği ilk paragraf."""
    best, best_hits = '', -1
    for paragraph in text.splitlines():
        folded = normalize(paragraph)
        hits = sum(bool(p.search(folded)) for p in patterns)
        if hits > best_hits:
            best, best_hits = paragraph, hits
    return best


def search_rows(rows, terms, court_type=None, kind=None, substring=False, limit=None):
    """terms normalize() edilmiş olmalı. (toplam eşleşme sayısı, sıralı ilk `limit` sonuç) döner;
    her sonuç metadata + lexical_score + snippet içerir. Kesit ve üst veri yalnız döndürülen
    sonuçlar için üretilir (limit=None: hepsi)."""
    patterns = [term_pattern(t, substring) for t in terms]
    found = []
    for row in rows:
        if court_type and row.get('court_type') != court_type:
            continue
        row_kind = kind_of(row)
        if kind and row_kind != kind:
            continue
        normalized = normalize(row['text'])  # kayıt başına bir kez, terim başına değil
        counts = [len(p.findall(normalized)) for p in patterns]
        if all(counts):
            score = sum(counts)
            # Konu dışı kayıt en sona; konu bakımından sınırdaki kayıt kendi türünün sonuna düşer.
            rank = (row['out_of_scope'], KIND_ORDER.get(row_kind, 4), row['scope_uncertain'])
            found.append((rank, -score, str(row['document_id']), row, score))
    # Esas gerekçesi önce, sonra sözcük geçişi; kısa onama kararları listenin sonuna düşer.
    # document_id tekil olduğundan sıralama kayıt sözlüklerini hiç karşılaştırmaz.
    found.sort(key=lambda item: item[:3])
    # Normalize metindeki ofset yerine özgün metinden paragraf kesiti döner.
    return len(found), [{**metadata(row), 'lexical_score': score,
                         'snippet': snippet_of(best_paragraph(row['text'], patterns), patterns)}
                        for *_, row, score in found[:limit]]


def find_quotes(text, quotation):
    """(toplam eşleşme sayısı, bağlamıyla en çok ilk QUOTE_MAX_OCCURRENCES eşleşme)."""
    positions, count, offset = [], 0, 0
    while True:
        start = text.find(quotation, offset)
        if start < 0:
            break
        count += 1
        if len(positions) < QUOTE_MAX_OCCURRENCES:
            end = start + len(quotation)
            positions.append({'start': start, 'end': end, 'matched_text': quotation,
                              'context': text[max(0, start - 200):end + 200]})
        offset = start + 1
    return count, positions


def squash(text):
    """Boşlukları atar; kalan her karakterin özgün metindeki konumunu da döndürür."""
    kept = [i for i, c in enumerate(text) if not c.isspace()]
    return ''.join(text[i] for i in kept), kept


def find_ignoring_space(text, quotation):
    """Bedesten çıktısı ile yerel metin yalnız boşlukta ayrışabilir; konumlar özgün metne göredir.
    (toplam eşleşme sayısı, bağlamıyla en çok ilk QUOTE_MAX_OCCURRENCES eşleşme) döner."""
    squashed, kept = squash(text)
    needle = squash(quotation)[0]
    positions, count, offset = [], 0, 0
    while needle:
        at = squashed.find(needle, offset)
        if at < 0:
            break
        count += 1
        if len(positions) < QUOTE_MAX_OCCURRENCES:
            start, end = kept[at], kept[at + len(needle) - 1] + 1
            positions.append({'start': start, 'end': end, 'matched_text': text[start:end],
                              'context': text[max(0, start - 200):end + 200]})
        offset = at + 1
    return count, positions


def emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


def limit_type(value):
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f'tam sayı olmalı: {value!r}') from None
    if not 1 <= number <= 2000:
        raise argparse.ArgumentTypeError('1 ile 2000 arasında olmalı')
    return number


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__, epilog=EPILOG,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--root', type=Path,
                        default=Path(__file__).resolve().parents[1] / 'data',
                        help='Havuz klasörü (varsayılan: skill kökündeki data/)')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('stats', help='Havuz özeti: kayıt sayısı, tarih aralığı, içerik türleri')
    search = sub.add_parser('search', help='Bütün terimleri içeren kararları sözcük eşleştirmesiyle arar')
    search.add_argument('terms', nargs='+',
                        help='Aranacak terimler; hepsi geçmeli. Sözcük başından eşleşir; büyük/küçük '
                             'harf, aksan, kesme/tırnak ve tire biçimi farkı yok sayılır. Rakamla biten '
                             'terimden hemen sonra rakam gelemez ("344" "13443" içinde eşleşmez, '
                             '"344/3" ve "344.000" içinde eşleşir). Tırnaklı ifade tek terimdir; '
                             'sözcükler aynı sırayla bitişik geçmeli')
    search.add_argument('--limit', type=limit_type, default=8,
                        help='Döndürülecek en çok sonuç (1-2000, varsayılan 8)')
    search.add_argument('--court-type', choices=['bam', 'yargitay'],
                        help='Yalnız bu mahkeme türü')
    search.add_argument('--kind', choices=['esas_gerekcesi', 'usul_gerekcesi',
                                           'kisa_karar', 'sinirda'],
                        help='Yalnız bu içerik türü (value_assessment.icerik_turu)')
    search.add_argument('--substring', action='store_true',
                        help='Sözcük başı ve sayı sınırı kuralını kaldırır; terim sözcük veya sayı '
                             'içinde de eşleşir (ör. "artış" "tartışılması", "344" "13443" içinde '
                             'bulunur). Varsayılan: yalnız sözcük başı')
    get = sub.add_parser('get', help='Kararın tam metnini ve künyesini getirir')
    get.add_argument('document_id', help='Aramada dönen document_id')
    quote = sub.add_parser('quote', help='Birebir alıntıyı tam metinde arar; bulunamazsa çıkış kodu 3')
    quote.add_argument('document_id', help='Aramada dönen document_id')
    quote.add_argument('quotation', help='Harfi harfine alıntı; "-" ile başlıyorsa önüne -- koy')
    quote.add_argument('--ignore-space', action='store_true',
                       help='Birebir eşleşme yoksa boşluk farklarını yok sayarak ara (ör. Bedesten/'
                            'Legaluga çıktısından alınan pasaj); sonuç match_mode: ignore_space')
    return parser, search, quote


def main(argv=None):
    for stream, errors in ((sys.stdout, 'strict'), (sys.stderr, 'backslashreplace')):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors=errors)
    parser, search, quote = build_parser()
    args = parser.parse_args(argv)
    # Girdi hataları havuz okunmadan bildirilir.
    if args.command == 'search':
        args.terms = [normalize(t.strip()) for t in args.terms]
        if not all(args.terms):
            search.error('Arama terimleri boş olamaz')
    if args.command == 'quote':
        args.raw_quotation = args.quotation
        # Yalnız Unicode NFC: ayrık kodlanmış ç/ş/ğ/ü/ö/İ birleşik biçime getirilir; NFKC kullanılmaz.
        args.quotation = unicodedata.normalize('NFC', args.quotation)
        if not args.quotation.strip():
            quote.error('Alıntı boş olamaz')
    rows, envelope = load_pool(args.root)
    if args.command == 'stats':
        dates = sorted(r['karar_tarihi'] for r in rows if r.get('karar_tarihi'))
        kinds = collections.Counter(kind_of(r) or 'unknown' for r in rows)
        emit({**envelope, 'date_min': dates[0] if dates else None,
              'date_max': dates[-1] if dates else None, 'kinds': dict(kinds),
              'collections': dict(collections.Counter(r['collection'] for r in rows)),
              'human_validated_records': sum(r.get('human_validated') is True for r in rows)})
        return EXIT_OK
    if args.command == 'search':
        total, results = search_rows(rows, args.terms, args.court_type, args.kind, args.substring,
                                     args.limit)
        emit({**envelope, 'total_matches': total, 'results': results})
        return EXIT_OK
    row = next((r for r in rows if str(r['document_id']) == args.document_id), None)
    if row is None:
        print(f'HATA: Karar bulunamadı: {args.document_id}', file=sys.stderr)
        return EXIT_NOT_FOUND
    if args.command == 'get':
        emit({**envelope, **metadata(row), 'text': row['text']})
        return EXIT_OK
    count, positions = find_quotes(row['text'], args.quotation)
    mode = 'exact' if count else None
    if not count and args.ignore_space:
        count, positions = find_ignoring_space(row['text'], args.quotation)
        mode = 'ignore_space' if count else None
    result = {**envelope, **metadata(row), 'exact_match': mode == 'exact', 'match_mode': mode,
              'quotation': args.quotation,
              'input_normalized': args.quotation != args.raw_quotation,
              'occurrence_count': count, 'occurrences_truncated': count > len(positions),
              'occurrences': positions}
    if len(args.quotation.strip()) < QUOTE_MIN_LENGTH:
        result['warning'] = (f'Alıntı {QUOTE_MIN_LENGTH} karakterden kısa; eşleşme, dilekçede '
                             'kullanılacak daha uzun alıntıyı doğrulamaz. Kullanacağın tam cümleyi '
                             'sorgula.')
    emit(result)
    return EXIT_OK if count else EXIT_NOT_FOUND


if __name__ == '__main__':
    try:
        code = main()
        sys.stdout.flush()
    except BrokenPipeError:
        # Çıktıyı okuyan süreç (ör. `| head`) erken kapandı; veri/bütünlük hatası değildir.
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(EXIT_DATA)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'HATA (veri bütünlüğü): {exc}', file=sys.stderr)
        sys.exit(EXIT_DATA)
    sys.exit(code)
