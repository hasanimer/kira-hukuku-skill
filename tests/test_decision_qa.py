import copy
import shutil
import sys
import tempfile
from pathlib import Path
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import decision_qa as qa


class AnswerTests(unittest.TestCase):
    def test_blind_questions_have_no_answer_or_source_fields(self):
        data, _ = qa.load_qa()
        out = qa.questions(data)
        self.assertEqual(len(out['questions']), len(data['examples']))
        self.assertTrue(all(set(r) == {'id', 'question'} for r in out['questions']))

    def test_readable_answers_match_data_and_include_every_source(self):
        data, cards = qa.load_qa()
        rendered = qa.render(data, cards, qa.suite_case_count())
        self.assertEqual(rendered, qa.PAGE.read_text(encoding='utf-8'))
        for card in cards.values():
            self.assertIn(card['source']['url'], rendered)

    def test_render_uses_suite_count_dotted_date_and_court_name(self):
        data, cards = qa.load_qa()
        count = len(qa.load()[0]['cases'])
        self.assertEqual(qa.suite_case_count(), count)
        rendered = qa.render(data, cards, count)
        year, month, day = data['checked_on'].split('-')
        self.assertIn(f'Kontrol: {day}.{month}.{year}. Mevcut {count} kurgu sınama dosyasının (B01–B{count:02d})', rendered)
        self.assertIn(f'Mevcut {count + 2} kurgu', qa.render(data, cards, count + 2))
        self.assertNotIn('Yargıtay Yargıtay', rendered)
        # BAM kaynağı 'Yargıtay' önekiyle yazılmamalı.
        bam = copy.deepcopy(cards)
        first = data['examples'][0]['card_id']
        bam[first]['source']['court'] = 'İstanbul Bölge Adliye Mahkemesi 35. Hukuk Dairesi'
        text = qa.render(data, bam, count)
        self.assertIn('[İstanbul Bölge Adliye Mahkemesi 35. Hukuk Dairesi, E.', text)
        self.assertNotIn('Yargıtay İstanbul', text)

    def test_disposition_mismatch_is_rejected(self):
        data = qa.read(qa.ROOT / 'evals/decision-qa.json')
        bad = copy.deepcopy(data)
        bad['examples'][0]['outcome'] = 'onama' if bad['examples'][0]['outcome'] != 'onama' else 'bozma'
        with mock.patch.object(qa, 'read', return_value=bad):
            with self.assertRaisesRegex(ValueError, 'Disposition mismatch'):
                qa.load_qa()

    def test_write_page_is_utf8_lf(self):
        data, cards = qa.load_qa()
        rendered = qa.render(data, cards, qa.suite_case_count())
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'sayfa.md'
            qa.write_page(rendered, path)
            raw = path.read_bytes()
        self.assertEqual(raw, rendered.encode('utf-8'))
        self.assertNotIn(b'\r', raw)

    def test_answers_load_without_rubric_file(self):
        # Kör sınama kopyasında yalnız evals/cases.json silinir; export/show çalışmalıdır.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for rel in ('references/karar-kartlari.json', 'references/egitim-kaynak-kaydi.json',
                        'evals/decision-qa.json'):
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(qa.ROOT / rel, root / rel)
            data, cards = qa.load_qa(root)
            self.assertEqual(len(qa.questions(data)['questions']), len(cards))
            with self.assertRaises(OSError):
                qa.suite_case_count(root)


if __name__ == '__main__':
    unittest.main()
