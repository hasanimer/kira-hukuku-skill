"""Read decision-based reference answers or export questions without answers."""
import argparse
import json
from pathlib import Path
import sys
from quality import ROOT, load, read, require, unique, digest


def load_qa():
    _, catalog = load()
    cards = unique(catalog['cards'], 'cards')
    data = read(ROOT / 'evals/decision-qa.json')
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


def questions(data):
    return {'kind': 'decision_based_questions_only', 'set_hash': digest(data),
            'questions': [{k: row[k] for k in ('id', 'question')} for row in data['examples']]}


def render(data, cards):
    lines = ['# Kararlardan sorular ve kaynaklı örnek yanıtlar', '',
             f'{len(data["examples"])} kararın anonimleştirilmiş, sadeleştirilmiş olaylarından hazırlanan cevaplı çalışma. '
             'Sorular kararın sonucunu söylemez; yanıtlar aşağıda açılır. Bunlar editoryal örnek yanıtlardır, '
             'bağımsız bir modelin kör sınama çıktısı veya mahkeme metninden birebir alıntı değildir.', '',
             'Kontrol: ' + data['checked_on'] + '. Kurgu sınama senaryolarının yanıt anahtarı değildir. '
             'Kaynak kararın dönemini ve usulünü korur; güncel dosyada sonraki mevzuat/içtihat ayrıca araştırılır.', '',
             'Makine okunur sürüm: [soru–yanıt verisi](../evals/decision-qa.json). '
             'Yalnız soru çıktısı: `python scripts/decision_qa.py export`. '
             'Kaynak sayfaları giriş gerektirebilir.', '']
    for row in data['examples']:
        card = cards[row['card_id']]
        source = card['source']
        citation = f"Yargıtay {source['court']}, E. {source['case_no']}, K. {source['decision_no']}, {source['date']}"
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


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('export', 'show', 'render', 'validate'))
    parser.add_argument('id', nargs='?')
    args = parser.parse_args()
    data, cards = load_qa()
    if args.command == 'render':
        print(render(data, cards), end='')
        return
    if args.command == 'export':
        result = questions(data)
    elif args.command == 'show':
        found = [r for r in data['examples'] if r['id'] == (args.id or '').upper()]
        require(found, 'Unknown question ID')
        result = dict(found[0], source=cards[found[0]['card_id']]['source'])
    else:
        require((ROOT / 'references/kararlardan-soru-yanit.md').read_text(encoding='utf-8') ==
                render(data, cards), 'Readable answers differ from JSON')
        result = {'status': 'pass', 'examples': len(data['examples']),
                  'model_performance': 'not_measured'}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        sys.exit(2)
