"""Read decision-based reference answers or export questions without answers."""
import argparse
import json
from pathlib import Path
import sys

# Kardeş modül içe aktarımı PYTHONSAFEPATH / python -I altında da çalışsın.
_HERE = str(Path(__file__).resolve().parent)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from pool import full_court  # noqa: E402
from quality import ROOT, digest, load, load_catalog, read, require, unique  # noqa: E402

PAGE_REL = 'references/kararlardan-soru-yanit.md'
PAGE = ROOT / PAGE_REL


def load_qa(root=ROOT):
    # Yalnız kart kataloğu gerekir; ölçüt dosyası (evals/cases.json) silinmiş kör sınama
    # kopyasında da export/show çalışır.
    cards = unique(load_catalog(root)['cards'], 'cards')
    data = read(root / 'evals/decision-qa.json')
    require(data['schema_version'] == 1 and data['status'] == 'editorial_not_blind_model_run',
            'Invalid answer set status')
    examples = unique(data['examples'], 'examples')
    require(len(examples) == len(cards), 'Expected one answer per card')
    require({x['card_id'] for x in examples.values()} == set(cards), 'Card coverage mismatch')
    for row in examples.values():
        require(row['outcome'] == cards[row['card_id']]['outcome'], 'Disposition mismatch')
        for key in ('question', 'short_answer', 'reasoning', 'disposition', 'limits', 'counterfactual'):
            require(isinstance(row[key], str) and row[key].strip(), 'Empty answer field: ' + key)
        for key in ('legal_basis', 'decisive_documents'):
            require(isinstance(row[key], list) and row[key] and
                    all(isinstance(x, str) and x.strip() for x in row[key]), 'Invalid ' + key)
    return data, cards


def suite_case_count(root=ROOT):
    """Sınama setindeki kurgu sınama dosyası sayısı (tam doğrulamayla); sayfadaki sayı buradan gelir."""
    suite, _ = load(root)
    return len(suite['cases'])


def questions(data):
    return {'kind': 'decision_based_questions_only', 'set_hash': digest(data),
            'questions': [{k: row[k] for k in ('id', 'question')} for row in data['examples']]}


def render(data, cards, case_count):
    checked_on = '.'.join(reversed(data['checked_on'].split('-')))  # GG.AA.YYYY
    lines = ['# Kararlardan sorular ve kaynaklı örnek yanıtlar', '',
             f'{len(data["examples"])} kararın anonimleştirilmiş, sadeleştirilmiş olaylarından hazırlanan cevaplı çalışma. '
             'Sorular kararın sonucunu söylemez; yanıtlar aşağıda açılır. Bunlar editoryal örnek yanıtlardır, '
             'bağımsız bir modelin kör sınama çıktısı veya mahkeme metninden birebir alıntı değildir.', '',
             'Kontrol: ' + checked_on + f'. Mevcut {case_count} kurgu sınama dosyasının (B01–B{case_count:02d}) tamamının yanıt anahtarı değildir. '
             'Kaynak kararın dönemini ve usulünü korur; güncel dosyada sonraki mevzuat/içtihat ayrıca araştırılır.', '',
             'Makine okunur sürüm: [soru–yanıt verisi](../evals/decision-qa.json). '
             'Yalnız soru çıktısı: `python scripts/decision_qa.py export`. '
             'Kaynak sayfaları giriş gerektirebilir.', '']
    for row in data['examples']:
        card = cards[row['card_id']]
        source = card['source']
        citation = f"{full_court(source)}, E. {source['case_no']}, K. {source['decision_no']}, {source['date']}"
        lines += ['## ' + row['id'], '', '**Soru:** ' + row['question'], '',
                  '<details>', '<summary>Kaynaklı örnek yanıtı aç</summary>', '',
                  '**Kısa yanıt:** ' + row['short_answer'], '',
                  '**Gerekçe:** ' + row['reasoning'], '',
                  '**Hukuki dayanak:** ' + '; '.join(row['legal_basis']) + '.', '',
                  '**Belirleyici belgeler:** ' + '; '.join(row['decisive_documents']) + '.', '',
                  '**Kararın sonucu:** ' + row['disposition'], '',
                  '**Uygulama sınırı:** ' + row['limits'], '',
                  '**Hangi olgu değişirse değerlendirme değişebilir?** ' + row['counterfactual'], '',
                  f"**Kaynak:** [{citation}]({source['url']}). Kart: {card['id']}. "
                  'Künye ve metin hash’i [kart kaydında](karar-kartlari.json).', '', '</details>', '']
    return '\n'.join(lines)


def write_page(text, path=None):
    # Kabuk yönlendirmesi (>) Windows'ta UTF-16/CRLF yazabilir; sayfa her yerde UTF-8 ve LF olur.
    with Path(path or PAGE).open('w', encoding='utf-8', newline='\n') as handle:
        handle.write(text)


def main():
    for stream, errors in ((sys.stdout, 'strict'), (sys.stderr, 'backslashreplace')):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors=errors)
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('export', help='Yalnız soru kimlikleri ve soruları verir')
    show = commands.add_parser('show', help='Tek sorunun kaynaklı yanıtını verir')
    show.add_argument('id', help='Soru kimliği, örn. Q01')
    page = commands.add_parser('render', help='Okunabilir soru-yanıt sayfasını üretir')
    page.add_argument('--write', action='store_true',
                      help=f'{PAGE_REL} dosyasına UTF-8 ve LF ile yazar')
    commands.add_parser('validate', help='Okunabilir sayfanın JSON ile aynı olduğunu denetler')
    args = parser.parse_args()
    data, cards = load_qa()
    if args.command == 'render':
        text = render(data, cards, suite_case_count())
        if args.write:
            write_page(text)
            print(json.dumps({'written': PAGE_REL}, ensure_ascii=False))
        else:
            print(text, end='')
        return
    if args.command == 'export':
        result = questions(data)
    elif args.command == 'show':
        found = [r for r in data['examples'] if r['id'] == args.id.upper()]
        require(found, f'Bilinmeyen soru kimliği: {args.id}')
        result = dict(found[0], source=cards[found[0]['card_id']]['source'])
    else:
        require(PAGE.read_text(encoding='utf-8') == render(data, cards, suite_case_count()),
                'Readable answers differ from JSON; run: python scripts/decision_qa.py render --write')
        result = {'status': 'pass', 'examples': len(data['examples']),
                  'model_performance': 'not_measured'}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f'HATA: {exc}', file=sys.stderr)
        sys.exit(2)
