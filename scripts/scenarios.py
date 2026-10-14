"""Find fictional tenant scenarios and resolve their real, hash-checked sources."""
import argparse
import json
import math
from pathlib import Path
import re
import sys

# Kardeş modül içe aktarımı PYTHONSAFEPATH / python -I altında da çalışsın.
_HERE = str(Path(__file__).resolve().parent)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from pool import load_pool, metadata, normalize  # noqa: E402
from triage import MODULES  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
STRING_FIELDS = ('title', 'story', 'coverage')
LIST_FIELDS = ('keywords', 'modules', 'documents', 'decisive_questions',
               'search_queries', 'decision_ids', 'counterfacts')
SUMMARY_KEYS = ('id', 'title', 'fictional', 'modules', 'coverage')
NEXT_STEP = ('Belgeler, belirleyici sorular, karşı olgular ve kaynak kayıtları için: '
             'python scripts/scenarios.py show <id>')
STOP_WORDS = frozenset(normalize(w) for w in (
    'acaba ama ancak bana ben beni benim bir biz bu çok da daha de diye en gibi göre hem '
    'her hiç için ile ise kadar ki mi mı mu mü ne o olan olarak onlar sen siz sonra şu '
    've veya var ya yok').split())


def load_catalog(root):
    catalog = json.loads((root / 'references/kiraci-senaryolari.json').read_text(encoding='utf-8-sig'))
    if (not isinstance(catalog, dict) or catalog.get('schema_version') != 1
            or catalog.get('fictional') is not True):
        raise ValueError('Unsupported catalog or missing fiction label')
    scenarios = catalog.get('scenarios')
    if not isinstance(scenarios, list) or not scenarios:
        raise ValueError('Scenario list missing or empty')
    seen = set()
    for row in scenarios:
        if not isinstance(row, dict):
            raise ValueError('Scenario entry must be an object')
        sid = row.get('id')
        if not isinstance(sid, str) or not re.fullmatch(r'K[1-9]\d*', sid):
            raise ValueError(f'Invalid scenario ID: {sid!r}')
        if sid in seen:
            raise ValueError(f'Duplicate scenario ID: {sid}')
        seen.add(sid)
        for field in STRING_FIELDS:
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f'Missing scenario field: {field}')
        for field in LIST_FIELDS:
            if not isinstance(row.get(field), list) or not row[field] or not all(
                    isinstance(item, str) and item.strip() for item in row[field]):
                raise ValueError(f'Invalid scenario field: {field}')
        unknown = set(row['modules']) - MODULES.keys()
        if unknown:
            raise ValueError(f'Unknown module in {sid}: {sorted(unknown)}')
    return scenarios


def resolve(rows, root):
    # pool.py ile aynı yükleyici: isteğe bağlı seçki dosyaları, manifest ve hash denetimi.
    pool_rows, _ = load_pool(root / 'data')
    sources = {str(d['document_id']): d for d in pool_rows}
    result = []
    for row in rows:
        absent = set(row['decision_ids']) - sources.keys()
        if absent:
            raise ValueError(f'Missing source for {row["id"]}: {sorted(absent)}')
        result.append({**row, 'fictional': True,
                       'decisions': [metadata(sources[key]) for key in row['decision_ids']]})
    return result


def _tokens(text):
    # Yalnız sözcük karakterleri; 'küf' gibi üç harfli hukuki sözcükler korunur.
    return [t for t in re.findall(r'\w+', normalize(text))
            if len(t) >= 3 and t not in STOP_WORDS]


def search(rows, query):
    # OR across words: a mixed dispute must not lose one issue to an AND filter.
    # 5-letter stems absorb Turkish suffixes (depozitomu -> depoz).
    stems = {}
    for token in _tokens(query):
        stems.setdefault(token[:5], set()).add(token)
    terms = sorted(stems)
    if not terms:
        raise ValueError('Search query has no searchable words')
    docs = [set(_tokens(' '.join([row['title'], row['story'], *row['keywords']])))
            for row in rows]

    def hit(term, doc):
        return any(word.startswith(term) for word in doc)

    # Nadir sözcük daha ağır basar; sıralama yine de yalnız sözcükseldir.
    weight = {term: math.log((len(rows) + 1) / (1 + sum(hit(term, d) for d in docs))) + 1
              for term in terms}
    found = []
    for index, (row, doc) in enumerate(zip(rows, docs)):
        matches = [term for term in terms if hit(term, doc)]
        if matches:
            words = sorted(set().union(*(stems[term] for term in matches)))
            found.append((-sum(weight[t] for t in matches), index,
                          {**row, 'matched_terms': words}))
    return [row for _, _, row in sorted(found, key=lambda item: item[:2])]


def main():
    for stream, errors in ((sys.stdout, 'strict'), (sys.stderr, 'backslashreplace')):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors=errors)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('list')
    show = commands.add_parser('show')
    show.add_argument('id')
    find = commands.add_parser('search')
    find.add_argument('query', nargs='+')
    args = parser.parse_args()
    rows = load_catalog(args.root)
    if args.command == 'show':
        rows = [row for row in rows if row['id'] == args.id.upper()]
        if not rows:
            raise ValueError(f'Unknown scenario: {args.id}')
    elif args.command == 'search':
        rows = search(rows, ' '.join(args.query))
    # Resolve before printing; broken citations must fail, not silently disappear.
    rows = resolve(rows, args.root)
    if args.command in ('list', 'search'):
        # Arama sonucu özet verir; tam kayıt için show kullanılır. Sonuç sayısı sınırlanmaz.
        keys = SUMMARY_KEYS
        if args.command == 'search':
            keys += ('matched_terms', 'decision_ids')
        rows = [{key: row[key] for key in keys} for row in rows]
    result = {
        'fictional': True,
        'matching': 'Lexical discovery only; order is not legal relevance or win probability.',
        'total': len(rows), 'scenarios': rows,
    }
    if args.command == 'search':
        result['next'] = NEXT_STEP
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f'HATA: {exc}', file=sys.stderr)
        sys.exit(2)
