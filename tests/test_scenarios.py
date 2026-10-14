"""Regression checks for mixed issues, traceable sources and fiction boundaries."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CATALOG = 'references/kiraci-senaryolari.json'
sys.path.insert(0, str(ROOT / 'scripts'))
import scenarios


class ScenarioTests(unittest.TestCase):
    def test_all_references_resolve_with_limits(self):
        rows = scenarios.resolve(scenarios.load_catalog(ROOT), ROOT)
        for row in rows:
            self.assertTrue(row['fictional'])
            self.assertTrue(row['coverage'])
            self.assertEqual([str(d['document_id']) for d in row['decisions']], row['decision_ids'])
            for source in row['decisions']:
                self.assertTrue(source['text_sha256'])
                self.assertTrue(source['source_url'])
                self.assertTrue(source['research_notes'])

    def test_mixed_dispute_preserves_both_topics(self):
        rows = scenarios.search(scenarios.load_catalog(ROOT), 'RUTUBET DEPOZİTO')
        ids = {row['id'] for row in rows}
        self.assertTrue({'K2', 'K6'}.issubset(ids))

    def test_punctuation_and_suffixes(self):
        catalog = scenarios.load_catalog(ROOT)
        ids = {r['id'] for r in scenarios.search(catalog, 'rutubet, depozito')}
        self.assertTrue({'K2', 'K6'}.issubset(ids))
        self.assertIn('K6', {r['id'] for r in scenarios.search(catalog, 'depozitomu')})
        self.assertIn('K2', {r['id'] for r in scenarios.search(catalog, 'küf')})

    def test_stop_words_do_not_match_everything(self):
        catalog = scenarios.load_catalog(ROOT)
        for query in ('a', 'var', 've ama'):
            with self.assertRaises(ValueError):
                scenarios.search(catalog, query)
        self.assertEqual(scenarios.search(catalog, 'kira depozito iadesi')[0]['id'], 'K6')

    def test_no_match_does_not_invent_source(self):
        self.assertEqual(scenarios.search(scenarios.load_catalog(ROOT), 'xyz-nonexistent'), [])
        with self.assertRaises(ValueError):
            scenarios.search(scenarios.load_catalog(ROOT), '   ')

    def test_broken_reference_fails(self):
        rows = copy.deepcopy(scenarios.load_catalog(ROOT)[:1])
        rows[0]['decision_ids'] = ['missing-decision']
        with self.assertRaisesRegex(ValueError, 'Missing source'):
            scenarios.resolve(rows, ROOT)

    def test_cli_portable_and_unknown_id_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            proc = subprocess.run([sys.executable, str(ROOT / 'scripts/scenarios.py'),
                                   'show', 'k6'], cwd=directory, capture_output=True,
                                  encoding='utf-8')
            self.assertEqual(proc.returncode, 0, proc.stderr)
            result = json.loads(proc.stdout)
            self.assertTrue(result['fictional'])
            self.assertEqual(result['scenarios'][0]['id'], 'K6')
            proc = subprocess.run([sys.executable, str(ROOT / 'scripts/scenarios.py'),
                                   'show', 'K999'], cwd=directory, capture_output=True)
            self.assertEqual(proc.returncode, 2)
            self.assertEqual(proc.stdout, b'')
            self.assertTrue(proc.stderr.decode('utf-8').startswith('HATA: '))

    def test_cli_search_returns_summaries(self):
        proc = subprocess.run([sys.executable, str(ROOT / 'scripts/scenarios.py'),
                               'search', 'kira', 'depozito'], capture_output=True, encoding='utf-8')
        self.assertEqual(proc.returncode, 0, proc.stderr)
        result = json.loads(proc.stdout)
        self.assertEqual(result['total'], len(scenarios.load_catalog(ROOT)))
        self.assertEqual(result['total'], len(result['scenarios']))
        for row in result['scenarios']:
            self.assertFalse({'story', 'documents', 'decisions'} & set(row))
            self.assertTrue(row['decision_ids'])
        by_id = {row['id']: row for row in result['scenarios']}
        self.assertEqual(by_id['K6']['matched_terms'], ['depozito', 'kira'])
        self.assertIn('show', result['next'])
        # Satır başına bütçe: katalog büyüdükçe sınır da büyür; tam kayıt (~10 KB) sızarsa aşılır.
        self.assertLess(len(proc.stdout.encode('utf-8')), 500 + 1500 * result['total'])


class CatalogGuardTests(unittest.TestCase):
    """Negative tests: load_catalog must reject malformed or unsafe catalogs with ValueError."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / CATALOG).parent.mkdir(parents=True)
        shutil.copyfile(ROOT / CATALOG, self.root / CATALOG)

    def assert_rejects(self, change, message):
        path = self.root / CATALOG
        data = json.loads(path.read_text(encoding='utf-8'))
        data = change(data) or data
        path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, message):
            scenarios.load_catalog(self.root)

    def test_unmutated_copy_loads(self):
        self.assertEqual(len(scenarios.load_catalog(self.root)), len(scenarios.load_catalog(ROOT)))

    def test_fiction_label_required(self):
        self.assert_rejects(lambda d: d.update(fictional=False), 'fiction label')

    def test_top_level_list_rejected(self):
        self.assert_rejects(lambda d: [d], 'fiction label')

    def test_scenarios_must_be_a_non_empty_list(self):
        self.assert_rejects(lambda d: d.update(scenarios={'K1': d['scenarios'][0]}),
                            'Scenario list')

    def test_entry_must_be_object(self):
        self.assert_rejects(lambda d: d['scenarios'].append('K99'), 'must be an object')

    def test_invalid_id_rejected(self):
        for bad in (1, ['K1'], 'k1', 'B01', ''):
            with self.subTest(bad=bad):
                shutil.copyfile(ROOT / CATALOG, self.root / CATALOG)
                self.assert_rejects(lambda d: d['scenarios'][0].update(id=bad),
                                    'Invalid scenario ID')

    def test_duplicate_scenario_rejected(self):
        self.assert_rejects(lambda d: d['scenarios'].append(dict(d['scenarios'][0])),
                            'Duplicate scenario ID')

    def test_blank_story_rejected(self):
        self.assert_rejects(lambda d: d['scenarios'][0].update(story='   '),
                            'Missing scenario field: story')

    def test_empty_decision_ids_rejected(self):
        self.assert_rejects(lambda d: d['scenarios'][0].update(decision_ids=[]),
                            'Invalid scenario field: decision_ids')

    def test_unknown_module_rejected(self):
        self.assert_rejects(lambda d: d['scenarios'][0].update(modules=['yok']),
                            'Unknown module')


if __name__ == '__main__':
    unittest.main()
