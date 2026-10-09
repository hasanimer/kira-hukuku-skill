import copy
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import quality


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


if __name__ == '__main__':
    unittest.main()
