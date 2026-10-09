"""Topic index of a lawyer-compiled precedent list, linked to verified full texts."""
import argparse
import json
from pathlib import Path
import sys

from pool import normalize

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / 'data/derleme-v5-index.json'
DATA = ROOT / 'data/derleme-v5-selected.jsonl'
PAGE = ROOT / 'references/derleme-v5.md'
STATUS = {
    'paket': 'tam metin pakette',
    'ana_havuz': 'tam metin ana havuzda',
    'secki': 'tam metin önceki seçkide',
    'bulunamadi': "Bedesten'de bulunamadı",
    'belirsiz': 'eşleşme belirsiz',
}
EXCERPT = {'tam': 'alıntı tam metinde geçiyor', 'kismi': 'alıntı kısmen geçiyor',
           'eslesmedi': 'alıntı tam metinde bulunamadı', 'alinti_yok': 'derlemede alıntı yok'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load(root=ROOT):
    index = json.loads((root / 'data/derleme-v5-index.json').read_text(encoding='utf-8'))
    rows = {}
    path = root / 'data/derleme-v5-selected.jsonl'
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.strip():
            row = json.loads(line)
            rows[row['document_id']] = row
    return index, rows


def counts(index):
    return {'citations': len(index['citations']),
            'status': {k: sum(c['status'] == k for c in index['citations']) for k in STATUS}}


def check(index, rows):
    require(index['schema_version'] == 1, 'Unsupported index schema')
    numbers = [c['n'] for c in index['citations']]
    require(numbers == list(range(1, len(numbers) + 1)), 'Citation numbers must be 1..N in order')
    used = set()
    for c in index['citations']:
        require(c['status'] in STATUS, f"Unknown status: {c['n']}")
        require(c['section'] and c['citation'], f"Empty citation: {c['n']}")
        if c['status'] == 'paket':
            require(c['document_id'] in rows, f"Missing packaged text: {c['n']}")
            used.add(c['document_id'])
        if c['status'] in ('paket', 'ana_havuz', 'secki'):
            require(c['document_id'] and c['kunye'] and c['source_url'], f"Incomplete source: {c['n']}")
        else:
            require(c['note'], f"Unresolved citation needs a note: {c['n']}")
    require(used == set(rows), 'Packaged texts and index citations differ')
    for row in rows.values():
        require(row['source_url'].endswith('/' + row['document_id']), 'Unexpected source address')
        require(row['human_validated'] is False, 'Packaged texts are not human validated')
    return {**counts(index), 'packaged_texts': len(rows)}


def line(c):
    if c['status'] in ('paket', 'ana_havuz', 'secki'):
        head = f"[{c['kunye']}]({c['source_url']})"
        parts = [STATUS[c['status']], EXCERPT.get(c['excerpt_check'], c['excerpt_check'])]
    else:
        head = f"{c['citation']} (derlemedeki atıf)"
        parts = [STATUS[c['status']]]
    if c.get('qualifier'):
        parts.append(c['qualifier'])
    if c.get('kira_disi'):
        parts.append('kira dışı uyuşmazlık')
    text = f"- {head} — {'; '.join(parts)}."
    if c.get('compiler_note'):
        text += f" Derleyen notu: {c['compiler_note']}"
    if c.get('note'):
        text += f" {c['note']}"
    return text


def render(index):
    src = index['source']
    summary = counts(index)
    lines = [f"# {src['title']} — konu dizini", '',
             f"{src['compiler']}, {src['edition']} ({src['date']}). {src['permission']} "
             'Başlıklar ve sınıflandırma derleyene aittir; hukuki kural veya güncel içtihat özeti değildir.', '',
             f"Kontrol: {index['checked_on']}. {index['method']}", '',
             f"Toplam {summary['citations']} atıf: " + ', '.join(
                 f"{n} {STATUS[k]}" for k, n in summary['status'].items() if n) + '. '
             'Tam metni pakette olan kararlar `python scripts/pool.py get KIMLIK` ile okunur; '
             'konu araması için `python scripts/derleme.py search "terim"` kullanılır. '
             'Atıf yapmadan önce kararın tam metnini, dönemini ve usul aşamasını ayrıca değerlendir.', '']
    previous = []
    for c in index['citations']:
        section = c['section']
        common = 0
        while common < min(len(previous), len(section)) and previous[common] == section[common]:
            common += 1
        for depth in range(common, len(section)):
            lines += [f"{'#' * min(depth + 2, 6)} {section[depth]}", '']
        if common == len(section) and section != previous:
            lines += [f"{'#' * min(len(section) + 1, 6)} {section[-1]}", '']
        lines.append(line(c))
        previous = section
        nxt = index['citations'][c['n']] if c['n'] < len(index['citations']) else None
        if nxt is None or nxt['section'] != section:
            lines.append('')
    return '\n'.join(lines).rstrip('\n') + '\n'


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('validate')
    sub.add_parser('render')
    find = sub.add_parser('search')
    find.add_argument('terms', nargs='+')
    find.add_argument('--limit', type=int, default=20)
    show = sub.add_parser('show')
    show.add_argument('n', type=int)
    args = parser.parse_args()
    index, rows = load()
    if args.command == 'validate':
        result = check(index, rows)
        require(PAGE.read_text(encoding='utf-8') == render(index), 'Readable index differs from JSON')
        print(json.dumps({**result, 'structural_validation': 'pass'}, ensure_ascii=False, indent=2))
    elif args.command == 'render':
        print(render(index), end='')
    elif args.command == 'show':
        found = [c for c in index['citations'] if c['n'] == args.n]
        require(found, 'Unknown citation number')
        print(json.dumps(found[0], ensure_ascii=False, indent=2))
    else:
        if not 1 <= args.limit <= 2000:
            parser.error('--limit must be between 1 and 2000')
        terms = [normalize(t.strip()) for t in args.terms]
        if not all(terms):
            parser.error('Search terms cannot be empty')
        # Derlemedeki atıf da aranır: hatalı numarayla arayan düzeltme notunu görür.
        fields = ('citation', 'kunye', 'qualifier', 'compiler_note', 'note')
        hits = [c for c in index['citations']
                if all(t in normalize(' '.join(c['section'] + [c.get(f) or '' for f in fields])) for t in terms)]
        print(json.dumps({'total_matches': len(hits), 'results': hits[:args.limit],
                          'note': 'Eşleşme derleme başlıkları, atıfları ve notlarında yapılır; hukuki önem sırası değildir.'},
                         ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError) as exc:
        print(f'Derleme error: {exc}', file=sys.stderr)
        sys.exit(1)
