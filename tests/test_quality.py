import copy
import json
import shutil
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import quality
import triage

CATALOGS = ['evals/cases.json', 'references/karar-kartlari.json',
            'references/egitim-kaynak-kaydi.json']


class QualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.suite, cls.cards = quality.load()

    def review(self, all_cases=False):
        # Synthetic transport fixture, not a model's legal answer or measured performance.
        rows = self.suite['cases'] if all_cases else self.suite['cases'][:1]
        answers = {'suite_hash': quality.digest(self.suite), 'run': 'synthetic-test',
                   'answers': [{'id': c['id'], 'response': 'Synthetic evidence.'} for c in rows]}
        review = quality.template(self.suite, answers)
        review.update(reviewer='test-fixture', reviewed_on='2026-09-20')
        for row in review['reviews']:
            for check in row['checks']:
                check.update(met=True, evidence='Synthetic evidence.', rationale='Fixture only.')
        return review

    def test_blind_export_contains_no_rubric_or_reference(self):
        exported = quality.blind(self.suite)
        self.assertTrue(all(set(c) == {'id', 'prompt'} for c in exported['cases']))
        self.assertEqual(len(exported['cases']), len(self.suite['cases']))

    def test_partial_perfect_review_is_not_suite_pass(self):
        result = quality.score(self.suite, self.review())
        self.assertEqual(result['met_ratio_reviewed'], 1)
        self.assertFalse(result['suite_passed'])
        self.assertEqual(len(result['missing']), len(self.suite['cases']) - 1)

    def test_critical_failure_survives_high_total(self):
        review = self.review(all_cases=True)
        review['reviews'][0]['checks'][0]['met'] = False
        result = quality.score(self.suite, review)
        self.assertFalse(result['suite_passed'])
        self.assertGreater(result['met_ratio_reviewed'], .98)
        self.assertEqual(result['details'][0]['critical_failures'], ['analysis'])

    def test_missing_review_does_not_mean_pass(self):
        review = self.review()
        review['reviews'][0]['checks'][0]['met'] = None
        with self.assertRaisesRegex(ValueError, 'Unreviewed'):
            quality.score(self.suite, review)

    def test_fabricated_evidence_rejected(self):
        review = self.review()
        review['reviews'][0]['checks'][0]['evidence'] = 'Absent quote'
        with self.assertRaisesRegex(ValueError, 'not in response'):
            quality.score(self.suite, review)

    def test_changed_answer_requires_new_review(self):
        review = self.review()
        review['reviews'][0]['response'] += ' Changed'
        with self.assertRaisesRegex(ValueError, 'Response changed'):
            quality.score(self.suite, review)

    def test_changed_suite_rejects_stale_review(self):
        suite = copy.deepcopy(self.suite)
        suite['cases'][0]['criteria'][0]['description'] += ' Changed'
        with self.assertRaisesRegex(ValueError, 'different suite'):
            quality.score(suite, self.review())

    def test_duplicate_review_rejected(self):
        review = self.review()
        review['reviews'].append(copy.deepcopy(review['reviews'][0]))
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            quality.score(self.suite, review)

    def test_unknown_criterion_rejected(self):
        review = self.review()
        review['reviews'][0]['checks'][0]['id'] = 'invented'
        with self.assertRaisesRegex(ValueError, 'criteria'):
            quality.score(self.suite, review)

    def test_invalid_review_date_rejected(self):
        for bad in ('x', '2026-13-45', '20260920', '2026-W38-7', '2026-9-20'):
            review = self.review()
            review['reviewed_on'] = bad
            with self.assertRaisesRegex(ValueError, 'reviewed_on'):
                quality.score(self.suite, review)
        review = self.review()
        review['reviewed_on'] = ' 2026-10-09 '
        self.assertEqual(quality.score(self.suite, review)['reviewed_on'], '2026-10-09')

    def test_bom_prefixed_review_file_is_accepted(self):
        review = self.review()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'review.json'
            path.write_text(json.dumps(review, ensure_ascii=False), encoding='utf-8-sig')
            self.assertEqual(quality.read(path), review)
            self.assertFalse(quality.score(self.suite, quality.read(path))['suite_passed'])

    def test_utf16_review_file_is_accepted(self):
        # Windows PowerShell 5.1'de `>` ve Out-File varsayılanı BOM'lu UTF-16LE'dir.
        review = self.review()
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'review.json'
            for encoding in ('utf-16', 'utf-16-le', 'utf-8'):
                with self.subTest(encoding=encoding):
                    path.write_text(json.dumps(review, ensure_ascii=False), encoding=encoding)
                    self.assertEqual(quality.read(path), review)

    def test_ansi_review_file_is_rejected_as_value_error(self):
        # cp1254 (ANSI) desteklenmez; hata ValueError olarak CLI'da HATA satırına dönüşür.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'review.json'
            path.write_bytes(json.dumps({'run': 'İhtiyaç'}, ensure_ascii=False).encode('cp1254'))
            with self.assertRaisesRegex(ValueError, 'UTF-8 veya UTF-16 değil'):
                quality.read(path)

    def test_score_reports_topic_modules_and_linked_cards(self):
        review = self.review()
        first = self.suite['cases'][0]
        detail = quality.score(self.suite, review, self.cards)['details'][0]
        self.assertEqual((detail['topic'], detail['modules']), (first['topic'], first['modules']))
        self.assertEqual(detail['linked_cards'], sorted(
            c['id'] for c in self.cards['cards'] if first['id'] in c['scenario_ids']))
        self.assertNotIn('linked_cards', quality.score(self.suite, review)['details'][0])

    def test_module_taxonomy_matches_triage(self):
        self.assertEqual(quality.MODULES, set(triage.MODULES))
        for case in self.suite['cases']:
            self.assertTrue(case['modules'] and set(case['modules']) <= quality.MODULES, case['id'])

    def test_deadline_cases_fix_scenario_date(self):
        # Süreye bağlı senaryolar değerlendirme tarihini soru metninde taşır.
        prompts = {c['id']: c['prompt'] for c in self.suite['cases']}
        for key in ('B06', 'B14', 'B54', 'B59'):
            self.assertRegex(prompts[key], r'^(Bugünün|Değerlendirme) tarihi \d{2}\.\d{2}\.\d{4}\b', key)

    def test_card_search_folds_turkish_and_citation_forms(self):
        ids = lambda *t: [c['id'] for c in quality.search_cards(self.cards, t)]
        for q in ('İhtiyaç', 'ihtiyaç', 'İHTİYAÇ', 'IHTIYAC'):
            self.assertEqual(ids(q), ['C01', 'C03'])
        self.assertEqual(ids('E. 2025/1495'), ['C01'])
        # pool.py search gibi sözcük başından eşleşir; sayı daha uzun sayının parçası olamaz.
        self.assertEqual(ids('K. 2025/304'), [])     # K. 2025/3048 değil
        self.assertEqual(ids('2025/36'), [])         # E. 2025/366 değil
        self.assertEqual(ids('6. HD', 'E. 2014/8939'), ['C06'])
        self.assertEqual(ids('tahliye', 'depozito'), ['C07', 'C10'])
        self.assertEqual(ids('artış'), [])            # 'tartışmalıdır' içinde eşleşmez
        self.assertEqual(ids('\u00ad'), ids())        # normalize sonrası boş terim yok sayılır
        for q in ('false', 'dejure', 'url'):
            self.assertEqual(ids(q), [])
        self.assertEqual(len(ids()), len(self.cards['cards']))
        self.assertEqual(ids('  ', ''), ids())
        hit = quality.search_cards(self.cards, ['E. 2025/1495'])[0]
        self.assertEqual(hit['kunye'], 'Yargıtay 3. HD, E. 2025/1495, K. 2025/3048, T. 26.05.2025')


class TriggerSetTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / 'evals').mkdir()
        shutil.copyfile(ROOT / 'evals/trigger-cases.json', self.root / 'evals/trigger-cases.json')
        self.suite, _ = quality.load()

    def mutate(self, change):
        path = self.root / 'evals/trigger-cases.json'
        data = json.loads(path.read_text(encoding='utf-8'))
        change(data)
        path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    def test_shipped_set_has_both_polarities(self):
        data = quality.load_triggers()
        polarities = [c['should_trigger'] for c in data['cases']]
        self.assertGreaterEqual(polarities.count(True), quality.MIN_TRIGGER_CASES)
        self.assertGreaterEqual(polarities.count(False), quality.MIN_TRIGGER_CASES)
        self.assertEqual(data['status'], 'not_measured')

    def test_mutated_sets_rejected(self):
        first_positive = lambda d: next(c for c in d['cases'] if c['should_trigger'])
        first_negative = lambda d: next(c for c in d['cases'] if not c['should_trigger'])
        mutations = {
            'should_trigger must be true/false': lambda d: d['cases'][0].update(should_trigger='true'),
            'not_measured': lambda d: d.update(status='measured'),
            'fiction label': lambda d: d.update(fictional=False),
            'Unknown trigger module': lambda d: first_positive(d).update(module='yok_boyle'),
            'needs a module': lambda d: [first_positive(d).pop(k, None) for k in ('module', 'modules')],
            'must have no module': lambda d: first_negative(d).update(module='tespit'),
            'Duplicate trigger query': lambda d: d['cases'][1].update(query=d['cases'][0]['query'].upper()),
            'Empty trigger query': lambda d: d['cases'][0].update(query='  '),
            'duplicate ID': lambda d: d['cases'][1].update(id=d['cases'][0]['id']),
            'at least': lambda d: d.update(cases=[c for c in d['cases'] if c['should_trigger']]),
        }
        for message, change in mutations.items():
            with self.subTest(message=message):
                shutil.copyfile(ROOT / 'evals/trigger-cases.json', self.root / 'evals/trigger-cases.json')
                quality.load_triggers(self.root, self.suite)
                self.mutate(change)
                with self.assertRaisesRegex(ValueError, message):
                    quality.load_triggers(self.root, self.suite)


class CatalogGuardTests(unittest.TestCase):
    """Negative tests: catalog loaders must reject mutated/unsafe catalogs."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        refs = {c['reference'] for c in quality.read(ROOT / 'evals/cases.json')['cases']}
        for rel in [*CATALOGS, *refs]:
            (self.root / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / rel, self.root / rel)

    def mutate(self, rel, change):
        path = self.root / rel
        data = json.loads(path.read_text(encoding='utf-8'))
        change(data)
        path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    def assert_rejects(self, rel, change, message):
        self.mutate(rel, change)
        with self.assertRaisesRegex(ValueError, message):
            quality.load(self.root)

    def test_unmutated_copy_loads(self):
        quality.load(self.root)

    def test_traversal_reference_rejected(self):
        self.assert_rejects('evals/cases.json', lambda d: d['cases'][0].update(
            reference='../../etc/passwd'), 'unsafe reference')

    def test_absolute_reference_outside_root_rejected(self):
        self.assert_rejects('evals/cases.json', lambda d: d['cases'][0].update(
            reference=str(ROOT / 'SKILL.md')), 'unsafe reference')

    def test_missing_anchor_text_rejected(self):
        self.assert_rejects('evals/cases.json', lambda d: d['cases'][0].update(
            anchor='YOK-BOYLE-METIN'), 'Reference anchor not found')
        self.assert_rejects('evals/cases.json', lambda d: d['cases'][0].update(
            anchor='  '), 'Reference anchor not found')

    def test_existing_anchor_accepted(self):
        def add_anchor(d):
            case = d['cases'][0]
            text = (self.root / case['reference']).read_text(encoding='utf-8')
            case['anchor'] = next(line for line in text.splitlines() if line.strip())
        self.mutate('evals/cases.json', add_anchor)
        quality.load(self.root)

    def test_suite_fiction_label_required(self):
        self.assert_rejects('evals/cases.json', lambda d: d.update(fictional=False),
                            'Missing fiction label')

    def test_case_fiction_label_required(self):
        self.assert_rejects('evals/cases.json', lambda d: d['cases'][0].update(
            fictional=False), 'case fiction label')

    def test_incomplete_rubric_rejected(self):
        self.assert_rejects('evals/cases.json', lambda d: d['cases'][0]['criteria'].pop(),
                            'Incomplete rubric')

    def test_unknown_or_empty_modules_rejected(self):
        for modules in (['temerrut'], [], 'tahliye', ['tahliye', 'tahliye'], None):
            with self.subTest(modules=modules):
                shutil.copyfile(ROOT / 'evals/cases.json', self.root / 'evals/cases.json')
                self.assert_rejects('evals/cases.json', lambda d: d['cases'][0].update(
                    modules=modules), 'Unknown or empty modules')

    def test_missing_topic_rejected(self):
        self.assert_rejects('evals/cases.json', lambda d: d['cases'][0].pop('topic'),
                            'Empty case field')

    def test_non_contiguous_case_ids_rejected(self):
        # Sayfa ve belgeler aralığı sayıdan türetir (B01–Bnn); boşluklu kimlik reddedilir.
        self.assert_rejects('evals/cases.json', lambda d: d['cases'][-1].update(id='B99'),
                            'contiguous')

    def test_unknown_outcome_rejected(self):
        self.assert_rejects('references/karar-kartlari.json', lambda d: d['cards'][0].update(
            outcome='kabul'), 'Unknown disposition')

    def test_invalid_card_date_rejected(self):
        self.assert_rejects('references/karar-kartlari.json', lambda d: d['cards'][0].update(
            checked_on='20.09.2026'), 'checked_on')

    def test_changed_source_url_rejected(self):
        self.assert_rejects('references/karar-kartlari.json',
                            lambda d: d['cards'][0]['source'].update(url='https://example.invalid/x'),
                            'provenance mismatch')

    def test_unknown_scenario_link_rejected(self):
        self.assert_rejects('references/karar-kartlari.json', lambda d: d['cards'][0].update(
            scenario_ids=['Z99']), 'Unknown scenario link')

    def test_cards_load_without_rubric_file(self):
        # Kör sınama kopyasında ölçüt dosyası silinir; kart araması yine çalışmalıdır.
        (self.root / 'evals/cases.json').unlink()
        catalog = quality.load_catalog(self.root)
        self.assertTrue(quality.search_cards(catalog, ['3. HD']))
        with self.assertRaises(OSError):
            quality.load(self.root)


if __name__ == '__main__':
    unittest.main()
