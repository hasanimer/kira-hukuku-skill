"""Runs the documented helper commands as subprocesses, as an agent or user would.

The Windows CI job has no global PYTHONUTF8/PYTHONIOENCODING setting, so these tests
see the real default console encoding there; the cp125x cases below reproduce it on Linux.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import quality


def legacy_env(encoding):
    env = {**os.environ, 'PYTHONIOENCODING': encoding}
    env.pop('PYTHONUTF8', None)
    return env


def run(script, *args, expected=0, env=None, flags=()):
    proc = subprocess.run([sys.executable, *flags, str(ROOT / 'scripts' / script), *args],
                          cwd=ROOT, capture_output=True, env=env)
    stderr = proc.stderr.decode('utf-8', errors='backslashreplace')
    if proc.returncode != expected:
        raise AssertionError(f'{script} {args}: rc={proc.returncode} {stderr}')
    proc.out = proc.stdout.decode('utf-8')
    proc.err = proc.stderr.decode('utf-8')
    return proc


class EncodingTests(unittest.TestCase):
    def test_json_commands_under_cp1252(self):
        env = legacy_env('cp1252')
        with tempfile.TemporaryDirectory(prefix='kira-cli-') as tmp:
            sample = Path(tmp) / 'girdi.json'
            sample.write_text(json.dumps({'query': 'Tahliye taahhüdü ve kısa süreli kira',
                                          'candidates': []}, ensure_ascii=False), encoding='utf-8')
            commands = [('pool.py', 'stats'), ('tbk.py', '344'), ('scenarios.py', 'list'),
                        ('quality.py', 'validate'), ('decision_qa.py', 'validate'),
                        ('triage.py', str(sample), '--dry-run')]
            for script, *args in commands:
                with self.subTest(script=script):
                    proc = run(script, *args, env=env)
                    self.assertIsInstance(json.loads(proc.out), dict)
        self.assertIn('TYPESAFE_API_KEY', run('triage.py', '--help', env=env).out)

    def test_turkish_error_message_survives_cp1254(self):
        proc = run('scenarios.py', 'show', 'kısa', expected=2, env=legacy_env('cp1254'))
        self.assertEqual(proc.stdout, b'')
        self.assertTrue(proc.err.startswith('HATA: '), proc.err)
        self.assertIn('kısa', proc.err)

    def test_isolated_mode_finds_sibling_modules(self):
        # -I (3.11+'da -P içerir) betik klasörünü sys.path'e eklemez; betikler kendisi ekler.
        for script in ('quality.py', 'scenarios.py', 'decision_qa.py', 'triage.py'):
            with self.subTest(script=script):
                run(script, '--help', flags=('-I',))


class QualityCliTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.suite, cls.catalog = quality.load()

    def test_documented_round_trip(self):
        total = len(self.suite['cases'])
        with tempfile.TemporaryDirectory(prefix='kira-cli-') as tmp:
            out = Path(tmp) / 'research-private'
            out.mkdir()
            run('quality.py', '--output', str(out / 'prompts.json'), 'export')
            prompts = json.loads((out / 'prompts.json').read_text(encoding='utf-8'))
            self.assertEqual(len(prompts['cases']), total)
            self.assertTrue(all(set(c) == {'id', 'prompt'} for c in prompts['cases']))
            # --output never overwrites (documented in kalite-sinama.md)
            self.assertIn('HATA', run('quality.py', '--output', str(out / 'prompts.json'),
                                      'export', expected=2).err)
            (out / 'answers.json').write_text(json.dumps({
                'suite_hash': prompts['suite_hash'], 'run': 'cli-fixture',
                'answers': [{'id': 'B06', 'response': 'Sentetik yanıt.'}]},
                ensure_ascii=False), encoding='utf-8-sig')
            run('quality.py', '--output', str(out / 'review.json'), 'review-template',
                str(out / 'answers.json'))
            review = json.loads((out / 'review.json').read_text(encoding='utf-8'))
            self.assertIn('Missing reviewer',
                          run('quality.py', 'score', str(out / 'review.json'), expected=2).err)
            review.update(reviewer='test-fixture', reviewed_on='2026-10-09')
            for check in review['reviews'][0]['checks']:
                check.update(met=True, evidence='Sentetik yanıt.', rationale='Fixture.')
            (out / 'review.json').write_text(json.dumps(review, ensure_ascii=False), encoding='utf-8')
            result = json.loads(run('quality.py', 'score', str(out / 'review.json')).out)
            self.assertEqual((result['reviewed'], result['total'], result['suite_passed']),
                             (1, total, False))
            self.assertIn('linked_cards', result['details'][0])
            review['reviewed_on'] = '09.10.2026'
            (out / 'review.json').write_text(json.dumps(review, ensure_ascii=False), encoding='utf-8')
            self.assertIn('reviewed_on',
                          run('quality.py', 'score', str(out / 'review.json'), expected=2).err)

    def test_case_and_cards(self):
        self.assertEqual(json.loads(run('quality.py', 'case', 'b06').out)['id'], 'B06')
        self.assertTrue(run('quality.py', 'case', 'ZZZ', expected=2).err.startswith('HATA: '))
        self.assertEqual(len(json.loads(run('quality.py', 'cards').out)), len(self.catalog['cards']))
        hits = json.loads(run('quality.py', 'cards', '2025/3540').out)
        self.assertTrue(hits and all('2025/3540' in json.dumps(c, ensure_ascii=False) for c in hits))
        hits = json.loads(run('quality.py', 'cards', 'ihtiyaç', '3. HD').out)
        self.assertTrue(hits)
        for card in hits:
            self.assertTrue(card['kunye'].startswith('Yargıtay 3. HD, E. '))

    def test_trigger_commands(self):
        summary = json.loads(run('quality.py', 'triggers').out)
        self.assertEqual((summary['structural_validation'], summary['trigger_performance']),
                         ('pass', 'not_measured'))
        exported = json.loads(run('quality.py', 'trigger-export').out)
        self.assertEqual(len(exported), summary['positives'] + summary['negatives'])
        self.assertTrue(all(set(row) == {'query', 'should_trigger'} for row in exported))


class DecisionQaCliTests(unittest.TestCase):
    def test_export_show_render(self):
        exported = json.loads(run('decision_qa.py', 'export').out)
        self.assertTrue(all(set(q) == {'id', 'question'} for q in exported['questions']))
        shown = json.loads(run('decision_qa.py', 'show', 'q01').out)
        self.assertEqual(shown['id'], 'Q01')
        self.assertTrue(shown['source']['url'])
        run('decision_qa.py', 'show', expected=2)
        run('decision_qa.py', 'export', 'Q01', expected=2)
        self.assertIn('Bilinmeyen soru kimliği: Q99',
                      run('decision_qa.py', 'show', 'Q99', expected=2).err)
        page = (ROOT / 'references/kararlardan-soru-yanit.md').read_bytes()
        self.assertEqual(run('decision_qa.py', 'render').stdout.replace(b'\r\n', b'\n'),
                         page.replace(b'\r\n', b'\n'))


if __name__ == '__main__':
    unittest.main()
