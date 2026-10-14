import copy
import json
import subprocess
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import derleme  # noqa: E402


class DerlemeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index, cls.rows = derleme.load()

    def test_readable_index_matches_json(self):
        self.assertEqual(derleme.render(self.index), derleme.PAGE.read_text(encoding='utf-8'))

    def test_every_packaged_text_is_cited_and_official(self):
        result = derleme.check(self.index, self.rows)
        self.assertEqual(result['packaged_texts'], len(self.rows))
        self.assertEqual(sum(result['status'].values()), len(self.index['citations']))
        for row in self.rows.values():
            self.assertTrue(row['source_url'].startswith('https://mevzuat.adalet.gov.tr/ictihat/'))
            self.assertTrue(row['research_notes']['derleme_atiflari'])

    def test_missing_packaged_text_is_rejected(self):
        index = copy.deepcopy(self.index)
        cited = next(c for c in index['citations'] if c['status'] == 'paket')
        rows = {k: v for k, v in self.rows.items() if k != cited['document_id']}
        with self.assertRaises(ValueError):
            derleme.check(index, rows)

    def test_unresolved_citation_needs_note(self):
        index = copy.deepcopy(self.index)
        cited = next(c for c in index['citations'] if c['status'] == 'paket')
        cited.update(status='bulunamadi', note=None)
        with self.assertRaises(ValueError):
            derleme.check(index, self.rows)

    def test_packaged_decision_is_readable_from_pool(self):
        document_id = next(iter(self.rows))
        out = subprocess.run([sys.executable, str(ROOT / 'scripts/pool.py'), 'get', document_id],
                             capture_output=True, text=True, encoding='utf-8', check=True)
        row = json.loads(out.stdout)
        self.assertEqual(row['collection'], 'derleme-v5-selected.jsonl')
        self.assertEqual(row['text'], self.rows[document_id]['text'])

    def search(self, *terms):
        out = subprocess.run([sys.executable, str(ROOT / 'scripts/derleme.py'), 'search', *terms],
                             capture_output=True, text=True, encoding='utf-8', check=True)
        return json.loads(out.stdout)

    def test_search_ignores_accents_and_finds_compiler_numbers(self):
        self.assertEqual(self.search('taahhutname')['total_matches'], self.search('taahhütnâme')['total_matches'])
        # Derlemedeki hatalı numara da bulunur; düzeltme notu sonuçla birlikte döner.
        corrected = [c for c in self.index['citations']
                     if c['status'] == 'paket' and c['citation'].split()[-2] not in (c['kunye'] or '')]
        for c in corrected:
            hits = self.search(c['citation'].split()[-2])['results']
            self.assertIn(c['n'], [h['n'] for h in hits])
            self.assertTrue(c['note'])

    def test_redacted_texts_keep_provenance(self):
        for row in self.rows.values():
            if row.get('redactions'):
                self.assertEqual(row['text'].count('[KİŞİ ADI ANONİMLEŞTİRİLDİ]'),
                                 row['redactions']['replacement_count'])
                self.assertNotEqual(row['source_text_sha256'], row['text_sha256'])

    def test_search_uses_headings_without_ranking_claim(self):
        out = subprocess.run([sys.executable, str(ROOT / 'scripts/derleme.py'), 'search', 'arabuluculuk'],
                             capture_output=True, text=True, encoding='utf-8', check=True)
        result = json.loads(out.stdout)
        self.assertGreater(result['total_matches'], 0)
        self.assertIn('hukuki önem', result['note'])


if __name__ == '__main__':
    unittest.main()
