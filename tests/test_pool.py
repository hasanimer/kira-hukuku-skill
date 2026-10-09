import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from pool import BEDESTEN_URL, enrich, find_ignoring_space, kunye, squash  # noqa: E402


def row(document_id, text, kind, **extra):
    base = {'document_id': document_id, 'court': '3. Hukuk Dairesi', 'esas_no': '2017/1',
            'karar_no': '2019/2', 'karar_tarihi': '2019-05-28',
            'text': text, 'text_sha256': hashlib.sha256(text.encode('utf-8')).hexdigest(),
            'value_assessment': {'icerik_turu': {'choice': kind}}}
    base.update(extra)
    return base


class PoolTests(unittest.TestCase):
    def test_bedesten_url_is_derived_only_for_numeric_ids(self):
        main = enrich(row('525578700', 'metin', 'esas_gerekcesi'))
        self.assertEqual(main['source_url'], BEDESTEN_URL.format('525578700'))
        self.assertEqual(main['source_provider'], 'Bedesten (kimlikten türetildi)')
        self.assertEqual(main['court_type'], 'yargitay')
        uuid = enrich(row('615160e1-265c', 'metin', 'esas_gerekcesi',
                          court='Denizli Bölge Adliye Mahkemesi 6. Hukuk Dairesi'))
        self.assertIsNone(uuid.get('source_url'))
        self.assertIsNone(uuid.get('court_type'))

    def test_written_source_url_is_not_overwritten(self):
        given = enrich(row('123', 'metin', 'esas_gerekcesi', source_url='https://example.org/x',
                           source_provider='Dejure', court_type='bam'))
        self.assertEqual(given['source_url'], 'https://example.org/x')
        self.assertEqual(given['source_provider'], 'Dejure')
        self.assertEqual(given['court_type'], 'bam')

    def test_kunye_uses_court_name_and_petition_format(self):
        self.assertEqual(kunye(row('1', 'm', 'kisa_karar')),
                         'Yargıtay 3. HD, E. 2017/1, K. 2019/2, T. 28.05.2019')
        self.assertEqual(kunye(row('2', 'm', 'kisa_karar', court='Hukuk Genel Kurulu')),
                         'Yargıtay HGK, E. 2017/1, K. 2019/2, T. 28.05.2019')
        self.assertEqual(kunye(row('3', 'm', 'kisa_karar',
                                   court='Denizli Bölge Adliye Mahkemesi 6. Hukuk Dairesi')),
                         'Denizli BAM 6. HD, E. 2017/1, K. 2019/2, T. 28.05.2019')

    def test_search_ranks_reasoned_decisions_before_short_ones(self):
        rows = [row('1', 'kira kira kira onama', 'kisa_karar'),
                row('2', 'kira bedeli hak ve nesafet gerekçesi', 'esas_gerekcesi'),
                row('3', 'kira usul', 'usul_gerekcesi')]
        with tempfile.TemporaryDirectory(prefix='kira-pool-') as directory:
            path = Path(directory) / 'topic-rescan-assistant-adjusted.jsonl'
            path.write_text('\n'.join(json.dumps(r, ensure_ascii=False) for r in rows) + '\n',
                            encoding='utf-8')
            out = subprocess.run([sys.executable, str(ROOT / 'scripts/pool.py'), '--root', directory,
                                  'search', 'kira'], capture_output=True, text=True,
                                 encoding='utf-8', check=True)
        result = json.loads(out.stdout)
        self.assertEqual([r['document_id'] for r in result['results']], ['2', '3', '1'])
        self.assertEqual(result['results'][0]['kunye'],
                         'Yargıtay 3. HD, E. 2017/1, K. 2019/2, T. 28.05.2019')
        self.assertEqual(result['results'][0]['source_url'], BEDESTEN_URL.format('2'))

    def test_squash_keeps_original_positions(self):
        text = 'Kira  bedeli\n\n tespit'
        squashed, kept = squash(text)
        self.assertEqual(squashed, 'Kirabedelitespit')
        self.assertEqual([text[i] for i in kept], list(squashed))
        hit = find_ignoring_space(text, 'bedeli tespit')[0]
        self.assertEqual(hit['matched_text'], 'bedeli\n\n tespit')
        self.assertEqual(text[hit['start']:hit['end']], hit['matched_text'])
        self.assertEqual(find_ignoring_space(text, 'bedel  yok'), [])

    def test_quote_ignore_space_is_opt_in_and_keeps_exact_meaning(self):
        text = 'Birinci  satır\n\nikinci satır'
        with tempfile.TemporaryDirectory(prefix='kira-pool-') as directory:
            path = Path(directory) / 'topic-rescan-assistant-adjusted.jsonl'
            path.write_text(json.dumps(row('9', text, 'esas_gerekcesi'), ensure_ascii=False) + '\n',
                            encoding='utf-8')

            def quote(quotation, *flags):
                out = subprocess.run([sys.executable, str(ROOT / 'scripts/pool.py'), '--root',
                                      directory, 'quote', '9', quotation, *flags],
                                     capture_output=True, text=True, encoding='utf-8')
                return out.returncode, json.loads(out.stdout)

            code, plain = quote('Birinci satır\nikinci')
            self.assertEqual((code, plain['exact_match'], plain['match_mode']), (2, False, None))
            code, loose = quote('Birinci satır\nikinci', '--ignore-space')
            self.assertEqual((code, loose['exact_match'], loose['match_mode']),
                             (0, False, 'ignore_space'))
            self.assertEqual(loose['occurrences'][0]['start'], 0)
            self.assertEqual(loose['occurrences'][0]['matched_text'], 'Birinci  satır\n\nikinci')
            code, exact = quote('ikinci satır', '--ignore-space')
            self.assertEqual((code, exact['exact_match'], exact['match_mode']), (0, True, 'exact'))
            self.assertEqual(exact['occurrences'][0]['matched_text'], 'ikinci satır')


if __name__ == '__main__':
    unittest.main()
