"""Read-only, hash-checked access to the rent determination corpus."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata

# Ana havuzdaki document_id UYAP Mevzuat ve İçtihat (Bedesten) belge kimliğidir; resmî
# adres bu desenle türetilir. Kayıtta yazılı source_url varsa ona dokunulmaz.
BEDESTEN_URL = 'https://mevzuat.adalet.gov.tr/ictihat/{}'
# Arama sıralaması: önce içerik türü (esas gerekçesi en değerli), sonra sözcük geçişi.
KIND_ORDER = {'esas_gerekcesi': 0, 'usul_gerekcesi': 1, 'sinirda': 2, 'kisa_karar': 3}
COURT_SHORT = (
    (re.compile(r'Bölge Adliye Mahkemesi'), 'BAM'),
    (re.compile(r'Hukuk Genel Kurulu'), 'HGK'),
    (re.compile(r'Ceza Genel Kurulu'), 'CGK'),
    (re.compile(r'(\d+)\. Hukuk Dairesi'), r'\1. HD'),
    (re.compile(r'(\d+)\. Ceza Dairesi'), r'\1. CD'),
)


def normalize(text):
    text = text.replace('ı', 'i').replace('İ', 'i').casefold()
    return ''.join(c for c in unicodedata.normalize('NFKD', text)
                   if not unicodedata.combining(c))


def read_rows(path):
    seen = set()
    with path.open(encoding='utf-8-sig') as stream:
        for line_no, line in enumerate(stream, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            key = str(row['document_id'])
            if key in seen:
                raise ValueError(f'Duplicate document_id: {key} ({path}:{line_no})')
            seen.add(key)
            actual = hashlib.sha256(row['text'].encode('utf-8')).hexdigest()
            if actual != row['text_sha256']:
                raise ValueError(f'Text hash mismatch: {key} ({path}:{line_no})')
            yield enrich(row)


def kind_of(row):
    return (row.get('value_assessment') or {}).get('icerik_turu', {}).get('choice')


def full_court(row):
    """Ana havuzda 'court' yalnız daire adıdır; künyede mahkeme adı da bulunmalı."""
    court = row.get('court') or ''
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


def enrich(row):
    """Türetilebilir alanları tamamlar; yazılı değeri ezmez, metne dokunmaz."""
    doc = str(row.get('document_id', ''))
    if not row.get('source_url') and doc.isdigit():
        row['source_url'] = BEDESTEN_URL.format(doc)
        row['source_provider'] = row.get('source_provider') or 'Bedesten (kimlikten türetildi)'
    if not row.get('court_type') and ('Yargıtay' in full_court(row)):
        row['court_type'] = 'yargitay'
    row['kunye'] = kunye(row)
    return row


def metadata(row):
    keys = ('document_id', 'kunye', 'court', 'esas_no', 'karar_no', 'karar_tarihi',
            'text_sha256', 'human_validated', 'review_level', 'value_assessment',
            'court_type', 'source_url', 'source_provider', 'research_notes',
            'source_text_sha256', 'redactions')
    return {key: row.get(key) for key in keys}


def emit(value):
    print(json.dumps(value, ensure_ascii=False, indent=2))


def squash(text):
    """Boşlukları atar; kalan her karakterin özgün metindeki konumunu da döndürür."""
    kept = [i for i, c in enumerate(text) if not c.isspace()]
    return ''.join(text[i] for i in kept), kept


def find_ignoring_space(text, quotation):
    """Bedesten çıktısı ile yerel metin yalnız boşlukta ayrışır; konumlar özgün metne göredir."""
    squashed, kept = squash(text)
    needle = squash(quotation)[0]
    hits = []
    offset = 0
    while needle:
        at = squashed.find(needle, offset)
        if at < 0:
            break
        start, end = kept[at], kept[at + len(needle) - 1] + 1
        hits.append({'start': start, 'end': end, 'matched_text': text[start:end],
                     'context': text[max(0, start-200):end+200]})
        offset = at + 1
    return hits


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path,
                        default=Path(__file__).resolve().parents[1] / 'data')
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('stats')
    search = sub.add_parser('search')
    search.add_argument('terms', nargs='+')
    search.add_argument('--limit', type=int, default=8)
    search.add_argument('--court-type', choices=['bam', 'yargitay'])
    search.add_argument('--kind', choices=['esas_gerekcesi', 'usul_gerekcesi',
                                         'kisa_karar', 'sinirda'])
    get = sub.add_parser('get')
    get.add_argument('document_id')
    quote = sub.add_parser('quote')
    quote.add_argument('document_id')
    quote.add_argument('quotation')
    quote.add_argument('--ignore-space', action='store_true',
                       help='Birebir eşleşme yoksa boşluk farklarını yok sayarak ara')
    args = parser.parse_args()
    source = args.root / 'topic-rescan-assistant-adjusted.jsonl'
    rows = list(read_rows(source))
    sources = [source]
    bam = args.root / 'bam-selected.jsonl'
    if bam.exists():
        rows.extend(read_rows(bam))
        sources.append(bam)
    yargitay = args.root / 'yargitay-selected.jsonl'
    if yargitay.exists():
        rows.extend(read_rows(yargitay))
        sources.append(yargitay)
    ids = [str(row['document_id']) for row in rows]
    if len(ids) != len(set(ids)):
        raise ValueError('Duplicate document_id across pools')
    prior = args.root / 'verified-topic-pool.jsonl'
    if prior.exists():
        labels = {(str(r['document_id']), r['text_sha256']): r.get('value_assessment')
                  for r in read_rows(prior)}
        for row in rows:
            row['value_assessment'] = labels.get(
                (str(row['document_id']), row['text_sha256']), row.get('value_assessment'))
    envelope = {'source_file': str(source.resolve()), 'records': len(rows),
                'source_file_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                'source_files': {str(p.resolve()): hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in sources}}
    if args.command == 'stats':
        dates = sorted(r['karar_tarihi'] for r in rows if r.get('karar_tarihi'))
        kinds = collections.Counter((r.get('value_assessment') or {}).get(
            'icerik_turu', {}).get('choice', 'unknown') for r in rows)
        emit({**envelope, 'date_min': dates[0] if dates else None,
              'date_max': dates[-1] if dates else None, 'kinds': dict(kinds),
              'human_validated_records': sum(r.get('human_validated') is True for r in rows)})
    elif args.command == 'search':
        if not 1 <= args.limit <= 2000:
            parser.error('--limit must be between 1 and 2000')
        terms = [normalize(t.strip()) for t in args.terms]
        if not all(terms):
            parser.error('Search terms cannot be empty')
        found = []
        for row in rows:
            if args.court_type and row.get('court_type') != args.court_type:
                continue
            kind = kind_of(row)
            if args.kind and kind != args.kind:
                continue
            normalized = normalize(row['text'])
            if all(t in normalized for t in terms):
                score = sum(normalized.count(t) for t in terms)
                # Return an original-text paragraph rather than offsets into normalized text.
                paragraphs = row['text'].splitlines()
                relevant = sorted(enumerate(paragraphs), key=lambda p: (
                    -sum(t in normalize(p[1]) for t in terms), p[0]))
                snippet = relevant[0][1][:1400] if relevant else ''
                found.append((KIND_ORDER.get(kind, 4), score, str(row['document_id']),
                              {**metadata(row), 'lexical_score': score, 'snippet': snippet}))
        # Esas gerekçesi önce, sonra sözcük geçişi; kısa onama kararları listenin sonuna düşer.
        found.sort(key=lambda item: (item[0], -item[1], item[2]))
        emit({**envelope, 'total_matches': len(found),
              'results': [r[3] for r in found[:args.limit]]})
    else:
        row = next((r for r in rows if str(r['document_id']) == args.document_id), None)
        if row is None:
            raise ValueError(f'Document not found in strict pool: {args.document_id}')
        if args.command == 'get':
            emit({**envelope, **metadata(row), 'text': row['text']})
        else:
            if not args.quotation.strip():
                parser.error('Quotation cannot be empty')
            positions = []
            offset = 0
            while True:
                start = row['text'].find(args.quotation, offset)
                if start < 0:
                    break
                end = start + len(args.quotation)
                positions.append({'start': start, 'end': end, 'matched_text': args.quotation,
                                  'context': row['text'][max(0, start-200):end+200]})
                offset = start + 1
            mode = 'exact' if positions else None
            if not positions and args.ignore_space:
                positions = find_ignoring_space(row['text'], args.quotation)
                mode = 'ignore_space' if positions else None
            emit({**envelope, **metadata(row), 'exact_match': mode == 'exact',
                  'match_mode': mode, 'quotation': args.quotation, 'occurrences': positions})
            if not positions:
                return 2
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'Corpus error: {exc}', file=sys.stderr)
        sys.exit(1)
