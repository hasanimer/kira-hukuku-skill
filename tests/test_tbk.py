"""Regression checks for the bundled TBK reader (scripts/tbk.py)."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import tbk  # noqa: E402
from tbk import DATA_ROOT, HEADING, load_law, structure  # noqa: E402

SCRIPT = ROOT / 'scripts/tbk.py'


def run_tbk(*args, env=None):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True,
                          timeout=120, env=env)


def parsed(proc):
    return json.loads(proc.stdout.decode('utf-8'))


class TbkCliTests(unittest.TestCase):
    def test_source_mode_without_argument(self):
        proc = run_tbk()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        result = parsed(proc)
        self.assertEqual(result['article_count'], 649)
        self.assertEqual(len(result['snapshot_sha256']), 64)
        self.assertNotIn('markdown', result)

    def test_invalid_article_numbers_are_usage_errors(self):
        for value in ('0', '-1', '650'):
            with self.subTest(value):
                proc = run_tbk(value)
                self.assertEqual(proc.returncode, 2)
                self.assertIn('1 ile 649 arasında', proc.stderr.decode('utf-8'))
                self.assertEqual(proc.stdout, b'')
        self.assertEqual(run_tbk('abc').returncode, 2)
        self.assertEqual(run_tbk('344', '--ek').returncode, 2)
        self.assertEqual(run_tbk('--gecici', '3').returncode, 2)

    def test_article_starts_with_own_heading_and_carries_footnotes(self):
        a344 = parsed(run_tbk('344'))
        self.assertEqual(a344['requested_article'], 344)
        self.assertTrue(a344['markdown'].startswith('## II. Belirlenmesi'))
        self.assertNotIn('III. Dava açma süresi', a344['markdown'])
        self.assertEqual(sorted(a344['footnotes']), ['2', '3', '4'])
        self.assertIn('7161', a344['footnotes']['3'])
        self.assertIn('tacir', a344['temporary_provision'])
        a343 = parsed(run_tbk('343'))
        self.assertNotIn('Belirlenmesi', a343['markdown'])
        self.assertTrue(parsed(run_tbk('345'))['markdown'].startswith('## III. Dava açma süresi'))
        # TBK 8'in '## ...' biçimli ikinci fıkrası sonraki maddeye kaymaz.
        self.assertTrue(parsed(run_tbk('8'))['markdown'].rstrip().endswith('öneri sayılır.'))
        a347 = parsed(run_tbk('347'))
        self.assertEqual(a347['footnotes'], {})
        self.assertNotIn('temporary_provision', a347)

    def test_last_article_and_temporary_articles_are_separate(self):
        a649 = parsed(run_tbk('649'))
        self.assertTrue(a649['markdown'].startswith('**Yürütme**'))
        self.assertIn('MADDE 649', a649['markdown'])
        self.assertNotIn('İŞLENEMEYEN', a649['markdown'])
        self.assertNotIn('* * *', a649['markdown'])
        self.assertNotIn('GEÇİCİ MADDE', parsed(run_tbk('647'))['markdown'])
        g1 = parsed(run_tbk('--gecici', '1'))
        self.assertEqual(g1['requested'], 'geçici 1')
        self.assertIn('7409/4', g1['markdown'])
        self.assertNotIn('7456', g1['markdown'])
        g2 = parsed(run_tbk('--gecici', '2'))
        self.assertIn('7456/23', g2['markdown'])
        self.assertNotIn('6217', g2['markdown'])
        self.assertNotIn('Yürürlük', g2['markdown'])
        tail = parsed(run_tbk('--ek'))
        self.assertIn('6217', tail['markdown'])
        self.assertIn('6353/53', tail['markdown'])
        self.assertNotIn('* * *', tail['markdown'])
        self.assertEqual(sorted(tail['footnotes']), ['1', '2', '3', '4', '5'])

    def test_every_article_holds_exactly_its_own_heading(self):
        _, text, matches, _ = load_law(DATA_ROOT)
        parts = structure(text, matches)
        for number in range(1, 650):
            markdown = tbk.article_result(text, matches, parts, number)['markdown']
            self.assertEqual([int(n) for n in HEADING.findall(markdown)], [number])
            self.assertFalse(re.match(r'(?:#+\s*)?(?:\*\*)?MADDE', markdown), number)

    def test_legacy_console_encoding(self):
        env = {**os.environ, 'PYTHONIOENCODING': 'cp1252'}
        env.pop('PYTHONUTF8', None)
        proc = run_tbk('344', env=env)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn('Belirlenmesi', parsed(proc)['markdown'])
        bad = run_tbk('650', env={**env, 'PYTHONIOENCODING': 'cp1254'})
        self.assertEqual(bad.returncode, 2)
        self.assertIn('arasında', bad.stderr.decode('utf-8'))


class TbkIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix='kira-tbk-')
        self.root = Path(self.directory.name)
        (self.root / 'mevzuat').mkdir()
        shutil.copy(DATA_ROOT / 'manifest.json', self.root / 'manifest.json')
        self.source = self.root / 'mevzuat' / '6098-source.json'
        shutil.copy(DATA_ROOT / 'mevzuat' / '6098-source.json', self.source)

    def tearDown(self):
        self.directory.cleanup()

    def test_intact_copy_loads(self):
        _, _, matches, digest = load_law(self.root)
        self.assertEqual(len(matches), 649)
        self.assertEqual(len(digest), 64)

    def test_changed_byte_is_hash_error(self):
        raw = bytearray(self.source.read_bytes())
        index = raw.index(b'MADDE 344')
        raw[index] = ord('N')
        self.source.write_bytes(bytes(raw))
        with self.assertRaisesRegex(ValueError, 'hash'):
            load_law(self.root)

    def test_truncated_copy_is_hash_error_before_parsing(self):
        self.source.write_bytes(self.source.read_bytes()[:1000])
        with self.assertRaisesRegex(ValueError, 'hash'):
            load_law(self.root)

    def test_missing_copy_is_os_error(self):
        self.source.unlink()
        with self.assertRaises(OSError):
            load_law(self.root)

    def test_cli_reports_integrity_failure_with_exit_1(self):
        raw = self.source.read_bytes()
        self.source.write_bytes(raw[:-10] + b'          ')
        code = ('import sys; from pathlib import Path; sys.path.insert(0, sys.argv[1]); '
                'import tbk; sys.exit(tbk.cli(["344"], Path(sys.argv[2])))')
        proc = subprocess.run([sys.executable, '-c', code, str(ROOT / 'scripts'), str(self.root)],
                              capture_output=True, timeout=120)
        self.assertEqual(proc.returncode, 1)
        stderr = proc.stderr.decode('utf-8')
        self.assertTrue(stderr.startswith('HATA (mevzuat bütünlüğü):'), stderr)
        self.assertIn('hash', stderr)
        self.assertNotIn('Traceback', stderr)
        self.assertEqual(proc.stdout, b'')

    def test_structure_rejects_missing_tail_heading(self):
        _, text, matches, _ = load_law(self.root)
        broken = text.replace('6098 SAYILI KANUNA İŞLENEMEYEN HÜKÜMLER', 'EK HÜKÜMLER')
        with self.assertRaises(ValueError):
            structure(broken, matches)


if __name__ == '__main__':
    unittest.main()
