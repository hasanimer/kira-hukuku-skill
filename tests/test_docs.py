"""Belgelerdeki havuz sayıları veriden sapmamalı; validate.py yardımcıları doğru çalışmalı."""
import collections
import inspect
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import validate  # noqa: E402
from pool import full_court, kind_of, load_pool  # noqa: E402


def tr(number):
    """Türkçe binlik ayırıcı: 1576 -> '1.576'."""
    return f'{number:,}'.replace(',', '.')


class CorpusFigureTests(unittest.TestCase):
    def assertPhrase(self, phrase, text, name):
        # Uzun belgeyi hata iletisine dökmeden yalnız eksik ifadeyi bildirir.
        self.assertTrue(phrase in text, f'{name} şu ifadeyi içermiyor: {phrase}')

    @classmethod
    def setUpClass(cls):
        cls.rows, cls.envelope = load_pool(ROOT / 'data')
        cls.kinds = collections.Counter(kind_of(r) or 'unknown' for r in cls.rows)
        cls.readme = (ROOT / 'README.md').read_text(encoding='utf-8')
        cls.skill = (ROOT / 'SKILL.md').read_text(encoding='utf-8')

    def test_manifest_kinds_match_data(self):
        manifest = json.loads((ROOT / 'data/manifest.json').read_text(encoding='utf-8'))
        if 'kinds' in manifest:
            self.assertEqual(manifest['kinds'], dict(self.kinds))
        self.assertEqual(manifest['records'], len(self.rows))

    def test_readme_kind_counts_cover_whole_pool(self):
        k = self.kinds
        self.assertPhrase(f"{k['esas_gerekcesi']} esas gerekçesi · {k['usul_gerekcesi']} usul gerekçesi · "
                          f"{k['sinirda']} sınırda · {k['kisa_karar']} kısa karar", self.readme, 'README.md')

    def test_skill_kind_counts_cover_whole_pool(self):
        for count, label in ((self.kinds['esas_gerekcesi'], 'esas gerekçesi'),
                             (self.kinds['kisa_karar'], 'kısa karar')):
            self.assertTrue(re.search(rf"{count}'[a-zçğıöşü]+ {label}", self.skill),
                            f"SKILL.md şu sayıyı içermiyor: {count}'… {label}")

    def test_stale_main_pool_only_figures_are_gone(self):
        for name, text in (('README.md', self.readme), ('SKILL.md', self.skill)):
            for stale in ('446 esas', "446'sı esas"):
                self.assertFalse(stale in text, f'{name} eski ana havuz sayısını içeriyor: {stale}')

    def test_readme_record_count_and_date_range_match_data(self):
        dates = sorted(r['karar_tarihi'] for r in self.rows)
        shown = ['.'.join(reversed(d.split('-'))) for d in (dates[0], dates[-1])]
        self.assertPhrase(f'{tr(len(self.rows))} karar · {shown[0]}–{shown[1]}', self.readme,
                          'README.md')

    def test_readme_distribution_matches_data(self):
        files = collections.Counter(r['collection'] for r in self.rows)
        courts = collections.Counter(full_court(r) for r in self.rows)
        years = collections.Counter(int(r['karar_tarihi'][:4]) for r in self.rows)
        expected = [
            f"{tr(files['topic-rescan-assistant-adjusted.jsonl'])} ana havuz",
            f"{tr(files['bam-selected.jsonl'])} BAM seçkisi",
            f"{tr(files['yargitay-selected.jsonl'])} Yargıtay seçkisi",
            f"{tr(files['derleme-v5-selected.jsonl'])} derleme seçkisi",
            f"{tr(courts['Yargıtay 3. Hukuk Dairesi'])} karar Yargıtay 3. HD",
            f"{tr(courts['Yargıtay 6. Hukuk Dairesi'])} karar Yargıtay 6. HD",
            f"{tr(sum(v for y, v in years.items() if 2010 <= y <= 2015))} karar 2010–2015",
            f"{tr(sum(v for y, v in years.items() if y >= 2020))} karar 2020 ve sonrası",
        ]
        for phrase in expected:
            self.assertPhrase(phrase, self.readme, 'README.md')

    def test_skill_collection_figures_match_data(self):
        files = collections.Counter(r['collection'] for r in self.rows)
        self.assertPhrase(
            f"{tr(len(self.rows))} kararın (ana havuz {tr(files['topic-rescan-assistant-adjusted.jsonl'])}, "
            f"BAM seçkisi {tr(files['bam-selected.jsonl'])}, Yargıtay seçkisi {tr(files['yargitay-selected.jsonl'])}, "
            f"derleme seçkisi {tr(files['derleme-v5-selected.jsonl'])})",
            self.skill, 'SKILL.md')

    def test_skill_period_figures_match_data(self):
        # SKILL.md ajana havuzun yaş dağılımını verir; veri değişirse bu sayılar da güncellenmeli.
        years = collections.Counter(int(r['karar_tarihi'][:4]) for r in self.rows)
        n1015 = sum(v for y, v in years.items() if 2010 <= y <= 2015)
        n2020 = sum(v for y, v in years.items() if y >= 2020)
        pre_tbk = sum(r['karar_tarihi'] < '2012-07-01' for r in self.rows)  # TBK: 01.07.2012
        for phrase in (f"{tr(len(self.rows))} kaydın {tr(n1015)}'",
                       f"{tr(pre_tbk)} karar TBK'nın yürürlüğünden",
                       f"yalnız {tr(n2020)} karar 2020 ve sonrası"):
            self.assertPhrase(phrase, self.skill, 'SKILL.md')


class ValidateHelperTests(unittest.TestCase):
    def test_heading_slugs_follow_github_rules(self):
        text = '# Hızlı başlangıç\n\n## Rehberler\n\n```bash\n# kod yorumu\n```\n\n## Rehberler\n'
        slugs = validate.heading_slugs(text)
        self.assertEqual(slugs, {'hızlı-başlangıç', 'rehberler', 'rehberler-1'})

    def test_read_jsonl_accepts_bom_and_blank_lines_and_locates_errors(self):
        with tempfile.TemporaryDirectory(prefix='kira-docs-') as directory:
            path = Path(directory) / 'ornek.jsonl'
            path.write_text('﻿{"a": 1}\n\n{"a": 2}\n', encoding='utf-8')
            self.assertEqual(validate.read_jsonl(path), [{'a': 1}, {'a': 2}])
            path.write_text('{"a": 1}\n{bozuk\n', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'ornek.jsonl:2'):
                validate.read_jsonl(path)

    def test_run_reports_command_exit_codes_and_empty_output(self):
        with self.assertRaisesRegex(ValueError, r'tbk.py 650: çıkış kodu 2 \(beklenen 0\)'):
            validate.run('tbk.py', '650')
        with self.assertRaisesRegex(ValueError, 'stdout boş'):
            validate.run('tbk.py', '650', expected=2)
        self.assertEqual(validate.run('tbk.py', '650', expected=2, parse=False), '')
        self.assertEqual(validate.run('tbk.py')['article_count'], 649)

    def test_skill_frontmatter_and_invocation_are_valid(self):
        validate.check_frontmatter()

    def test_eviction_catalog_check_runs_before_frontmatter(self):
        source = inspect.getsource(validate.main)
        self.assertIn('check_tahliye()', source)
        self.assertLess(source.index('check_tahliye()'), source.index('check_frontmatter()'))

    def test_eviction_catalog_check_passes(self):
        validate.check_tahliye()

    def test_bulk_data_link_pattern(self):
        for target in ('data/topic-rescan-assistant-adjusted.jsonl', './data/bam-selected.jsonl',
                       'data/mevzuat/6098-turk-borclar-kanunu.md'):
            self.assertTrue(validate.BULK_LINK.match(target), target)
        for target in ('references/havuz.md', 'data/README.md'):
            self.assertIsNone(validate.BULK_LINK.match(target), target)


if __name__ == '__main__':
    unittest.main()
