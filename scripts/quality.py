"""Offline benchmark/catalog tools. Scores explicit human reviews, never legal truth."""
import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import sys

# Kardeş modül içe aktarımı PYTHONSAFEPATH / python -I altında da çalışsın.
_HERE = str(Path(__file__).resolve().parent)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from pool import full_court, kunye, normalize  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
# triage.py MODULES anahtarları ve references/moduller.md tablosuyla aynı olmalıdır.
MODULES = frozenset({'tespit', 'uyarlama', 'tahliye', 'alacak', 'guvence', 'sozlesme'})
OUTCOMES = frozenset({'bozma', 'onama', 'uyusmazligin_giderilmesi', 'karar_verilmesine_yer_olmadigi'})
CARD_SEARCH_FIELDS = ('id', 'source_id', 'title', 'facts', 'evidence', 'issue',
                      'reasoning', 'outcome', 'result', 'limits')
ISO_DAY = re.compile(r'\d{4}-\d{2}-\d{2}')
MIN_TRIGGER_CASES = 10  # her kutup (tetiklenmeli / tetiklenmemeli) için en az


def read(path):
    # utf-8-sig: PowerShell 5.1 veya "UTF-8 with BOM" ile kaydedilen inceleme dosyaları da okunur.
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode('utf-8')).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique(rows, label):
    require(isinstance(rows, list), f'{label}: expected list')
    require(all(isinstance(r, dict) for r in rows), f'{label}: expected objects')
    ids = [r['id'] for r in rows]
    require(len(ids) == len(set(ids)), f'{label}: duplicate ID')
    return {r['id']: r for r in rows}


def iso_day(value, message):
    """Yalnız YYYY-MM-DD; Python 3.11+ fromisoformat'ın kabul ettiği diğer ISO biçimleri değil."""
    value = value.strip() if isinstance(value, str) else ''
    require(ISO_DAY.fullmatch(value), message)
    try:
        date.fromisoformat(value)
    except ValueError:
        raise ValueError(message) from None
    return value


def load_catalog(root=ROOT):
    """Karar kartlarını ve kaynak kaydını doğrular; ölçüt dosyası (evals/cases.json) gerekmez."""
    catalog = read(root / 'references/karar-kartlari.json')
    require(isinstance(catalog, dict) and catalog.get('schema_version') == 1, 'Unsupported schema')
    cards = unique(catalog.get('cards'), 'cards')
    require(bool(cards), 'Empty catalog')
    audit = unique(read(root / 'references/egitim-kaynak-kaydi.json')['records'], 'audit')
    for card in cards.values():
        require(card['source_id'] in audit, 'Unknown decision source')
        require(card['source'] == audit[card['source_id']], 'Source provenance mismatch')
        require(card['full_text_in_card'] is False, 'Card is not a full-text record')
        require(card['outcome'] in OUTCOMES, 'Unknown disposition')
        for key in ('title', 'facts', 'evidence', 'issue', 'reasoning', 'result', 'limits',
                    'review_status', 'checked_on'):
            require(isinstance(card[key], str) and card[key].strip(), 'Empty card field: ' + key)
        iso_day(card['checked_on'], 'Invalid card checked_on (expected YYYY-MM-DD): ' + card['id'])
        require(isinstance(card['dissent'], list) and all(isinstance(x, str) and x.strip()
                for x in card['dissent']), 'Invalid dissent')
        require(isinstance(card['scenario_ids'], list) and card['scenario_ids']
                and all(isinstance(x, str) for x in card['scenario_ids']), 'Unknown scenario link')
    return catalog


def load(root=ROOT):
    catalog = load_catalog(root)
    suite = read(root / 'evals/cases.json')
    require(isinstance(suite, dict) and suite.get('schema_version') == 1, 'Unsupported schema')
    require(suite.get('fictional') is True, 'Missing fiction label')
    cases = unique(suite.get('cases'), 'cases')
    require(bool(cases), 'Empty catalog')
    for case in cases.values():
        require(case.get('fictional') is True, 'Missing case fiction label')
        empty = [k for k in ('id', 'prompt', 'topic', 'reference')
                 if not (isinstance(case.get(k), str) and case[k].strip())]
        require(not empty, f'Empty case field: {case.get("id")} {", ".join(empty)}')
        mods = case.get('modules')
        require(isinstance(mods, list) and mods and all(isinstance(m, str) for m in mods)
                and len(set(mods)) == len(mods) and set(mods) <= MODULES,
                'Unknown or empty modules: ' + case['id'])
        ref = (root / case['reference']).resolve()
        require(ref.is_relative_to(root.resolve()) and ref.is_file(), 'Missing/unsafe reference')
        anchor = case.get('anchor')
        if anchor is not None:
            require(isinstance(anchor, str) and anchor.strip()
                    and anchor in ref.read_text(encoding='utf-8'),
                    'Reference anchor not found: ' + case['id'])
        criteria = unique(case['criteria'], 'criteria')
        require(set(criteria) == {'analysis', 'questions', 'avoid'}, 'Incomplete rubric')
        for criterion in criteria.values():
            require(isinstance(criterion['description'], str) and criterion['description'].strip()
                    and type(criterion['critical']) is bool, 'Invalid criterion')
    for card in catalog['cards']:
        require(all(x in cases for x in card['scenario_ids']), 'Unknown scenario link')
    return suite, catalog


def card_kunye(card):
    s = card['source']
    return kunye({'court': s['court'], 'karar_tarihi': s['date'],
                  'esas_no': s['case_no'], 'karar_no': s['decision_no']})


def card_haystack(card):
    # Yalnız içerik alanları: JSON anahtarları, URL ve iç enum adları aramaya girmez.
    s = card['source']
    parts = [card[k] for k in CARD_SEARCH_FIELDS] + card['dissent'] + card['scenario_ids']
    parts += [full_court({'court': s['court']}), card_kunye(card), s.get('citation_warning', '')]
    return normalize(' '.join(parts))


def search_cards(catalog, terms):
    """Her terim bir ifadedir ve kartta hepsi geçmelidir (pool.py search gibi); büyük/küçük
    harf ve Türkçe karakter farkı gözetilmez. Künye pool.py biçimiyle aranabilir."""
    terms = [normalize(t.strip()) for t in terms if t.strip()]
    return [dict(c, kunye=card_kunye(c)) for c in catalog['cards']
            if all(t in card_haystack(c) for t in terms)]


def load_triggers(root=ROOT, suite=None):
    """Tetiklenme kümesinin yalnız yapısını doğrular; tetiklenme oranı ölçülmez."""
    if suite is None:
        suite, _ = load(root)
    data = read(root / 'evals/trigger-cases.json')
    require(isinstance(data, dict) and data.get('schema_version') == 1,
            'Unsupported trigger schema')
    require(data.get('fictional') is True, 'Missing trigger fiction label')
    require(data.get('status') == 'not_measured', 'Trigger set must stay labelled not_measured')
    require(isinstance(data.get('version'), str) and data['version'].strip(),
            'Missing trigger set version')
    cases = unique(data.get('cases'), 'trigger cases')
    labels = set(MODULES) | {c['topic'] for c in suite['cases']}
    seen = set()
    for key, case in cases.items():
        require(isinstance(case.get('query'), str) and case['query'].strip(),
                'Empty trigger query: ' + str(key))
        query = normalize(case['query'])
        require(query not in seen, 'Duplicate trigger query: ' + str(key))
        seen.add(query)
        require(type(case.get('should_trigger')) is bool, 'should_trigger must be true/false: ' + str(key))
        module, mods = case.get('module'), case.get('modules')
        if case['should_trigger']:
            require(module is not None or mods, 'Positive trigger case needs a module: ' + str(key))
            require(module is None or module in labels, 'Unknown trigger module: ' + str(key))
            require(mods is None or (isinstance(mods, list) and mods
                                     and all(isinstance(m, str) for m in mods)
                                     and set(mods) <= MODULES),
                    'Unknown trigger modules: ' + str(key))
        else:
            require(module is None and not mods, 'Negative trigger case must have no module: ' + str(key))
    positives = sum(c['should_trigger'] for c in cases.values())
    negatives = len(cases) - positives
    require(positives >= MIN_TRIGGER_CASES and negatives >= MIN_TRIGGER_CASES,
            f'Trigger set needs at least {MIN_TRIGGER_CASES} cases of each polarity')
    return data


def blind(suite):
    return {'suite_version': suite['version'], 'suite_hash': digest(suite),
            'fictional': True, 'cases': [
                {k: c[k] for k in ('id', 'prompt')} for c in suite['cases']]}


def template(suite, answers):
    cases = unique(suite['cases'], 'cases')
    rows = unique(answers['answers'], 'answers')
    require(rows and set(rows) <= set(cases), 'Empty or unknown answers')
    require(answers['suite_hash'] == digest(suite), 'Answers use a different suite')
    require(isinstance(answers.get('run'), str) and answers['run'].strip(), 'Missing run label')
    reviews = []
    for key, row in rows.items():
        require(isinstance(row['response'], str) and row['response'].strip(), 'Empty response')
        reviews.append({'id': key, 'response': row['response'],
                        'response_hash': digest(row['response']),
                        'checks': [{'id': c['id'], 'met': None, 'evidence': '', 'rationale': ''}
                                   for c in cases[key]['criteria']]})
    return {'suite_hash': digest(suite), 'run': answers['run'], 'reviewer': '',
            'reviewed_on': '', 'reviews': reviews}


def score(suite, review, catalog=None):
    cases = unique(suite['cases'], 'cases')
    require(review['suite_hash'] == digest(suite), 'Review uses a different suite')
    for field in ('run', 'reviewer', 'reviewed_on'):
        require(isinstance(review.get(field), str) and review[field].strip(), 'Missing ' + field)
    reviewed_on = iso_day(review['reviewed_on'], 'Invalid reviewed_on (expected YYYY-MM-DD)')
    rows = unique(review['reviews'], 'reviews')
    require(rows and set(rows) <= set(cases), 'Empty or unknown reviews')
    details = []
    for key, row in rows.items():
        response = row['response']
        require(isinstance(response, str) and response.strip(), 'Empty response')
        require(row['response_hash'] == digest(response), 'Response changed after template')
        checks = unique(row['checks'], 'checks')
        criteria = unique(cases[key]['criteria'], 'criteria')
        require(set(checks) == set(criteria), 'Missing or unknown review criteria')
        for check in checks.values():
            require(type(check['met']) is bool, 'Unreviewed criterion')
            require(isinstance(check['rationale'], str) and check['rationale'].strip(),
                    'Missing review rationale')
            evidence = check['evidence']
            require(isinstance(evidence, str), 'Invalid evidence')
            require(not check['met'] or evidence.strip(), 'Passing review needs response evidence')
            require(not evidence or evidence in response, 'Evidence is not in response')
        critical_failures = [k for k, c in criteria.items() if c['critical'] and not checks[k]['met']]
        met = sum(c['met'] for c in checks.values())
        detail = {'id': key, 'topic': cases[key]['topic'], 'modules': cases[key]['modules'],
                  'met': met, 'criteria': len(criteria), 'critical_failures': critical_failures,
                  'passed': met == len(criteria)}
        if catalog is not None:
            # Yayımlanmış karar kartı/soru-yanıtla örtüşen senaryolar açık kaynaklıdır; ayrı raporla.
            detail['linked_cards'] = sorted(c['id'] for c in catalog['cards']
                                            if key in c['scenario_ids'])
        details.append(detail)
    complete = len(rows) == len(cases)
    return {'assessment': 'human_review_not_automatic_legal_validation',
            'suite_hash': digest(suite), 'run': review['run'], 'reviewer': review['reviewer'],
            'reviewed_on': reviewed_on, 'complete': complete,
            'reviewed': len(rows), 'total': len(cases),
            'missing': sorted(set(cases) - set(rows)),
            'met_ratio_reviewed': sum(r['met'] for r in details) / sum(r['criteria'] for r in details),
            'suite_passed': complete and all(r['passed'] for r in details), 'details': details}


def main():
    for stream, errors in ((sys.stdout, 'strict'), (sys.stderr, 'backslashreplace')):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8', errors=errors)
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output', type=Path, help='Write UTF-8 JSON without shell encoding differences')
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('validate')
    sub.add_parser('export')
    show = sub.add_parser('case')
    show.add_argument('id')
    cards = sub.add_parser('cards', help='Karar kartlarında arama; her terim kartta geçmelidir')
    cards.add_argument('terms', nargs='*', help='Konu veya pool.py biçiminde künye, ör. "3. HD"')
    for name in ('review-template', 'score'):
        child = sub.add_parser(name)
        child.add_argument('file', type=Path)
    sub.add_parser('triggers', help='Tetiklenme kümesinin yapısını doğrular; oran ölçmez')
    sub.add_parser('trigger-export', help='[{"query", "should_trigger"}] listesi verir')
    args = p.parse_args()
    if args.command == 'cards':
        # Ölçüt dosyası olmadan da çalışır (kör sınama kopyası).
        result = search_cards(load_catalog(), args.terms)
    else:
        suite, catalog = load()
        if args.command == 'validate':
            result = {'structural_validation': 'pass', 'cases': len(suite['cases']),
                      'cards': len(catalog['cards']), 'suite_hash': digest(suite),
                      'legal_performance': 'not_measured'}
        elif args.command == 'export':
            result = blind(suite)
        elif args.command == 'case':
            found = [c for c in suite['cases'] if c['id'] == args.id.upper()]
            require(found, 'Unknown case ID')
            result = found[0]
        elif args.command == 'review-template':
            result = template(suite, read(args.file))
        elif args.command == 'score':
            result = score(suite, read(args.file), catalog)
        else:
            triggers = load_triggers(suite=suite)
            if args.command == 'triggers':
                positives = sum(c['should_trigger'] for c in triggers['cases'])
                result = {'structural_validation': 'pass', 'version': triggers['version'],
                          'positives': positives, 'negatives': len(triggers['cases']) - positives,
                          'trigger_performance': 'not_measured'}
            else:
                result = [{'query': c['query'], 'should_trigger': c['should_trigger']}
                          for c in triggers['cases']]
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        with args.output.open('x', encoding='utf-8') as handle:
            handle.write(rendered)
    else:
        print(rendered, end='')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(f'HATA: {exc}', file=sys.stderr)
        sys.exit(2)
