from unittest.mock import patch
import unittest

from rouge import supplemental_comparison as comparison
from rouge import supplemental_cultivation as cultivation
from rouge import supplemental_enemies as enemies
from rouge import supplemental_skills as skills
from rouge.supplemental_skills import defaults
from tests.test_supplemental_run_141 import environment


class SupplementalBaselineMetricsReviewTests(unittest.TestCase):
    def test_rank_variants_share_identical_cultivated_attributes(self):
        with patch.object(skills,'_attribute_values',wraps=skills._attribute_values) as attributes:
            result=comparison.compare_ranks(defaults(),environment(),{'ranks':list(range(1,8))})
        self.assertEqual(attributes.call_count,1)
        self.assertEqual(len(result['variants']),7)

    def test_ranks_extract_baseline_once(self):
        with patch.object(comparison, 'metrics', wraps=comparison.metrics) as metrics:
            result = comparison.compare_ranks(defaults(), environment(), {'ranks': list(range(1, 8))})
        self.assertEqual(sum(call.args[0] is result['baseline'] for call in metrics.call_args_list), 1)
        self.assertEqual(metrics.call_count, 8)

    def test_cultivation_shares_one_baseline_across_all_proposals(self):
        preview=defaults();env=environment()
        with patch.object(cultivation, 'metrics', wraps=comparison.metrics) as baseline_metrics, \
                patch.object(comparison, 'metrics', wraps=comparison.metrics) as row_metrics:
            result=cultivation.compare_cultivation(preview,env,cultivation.cultivation_defaults(preview,env))
        self.assertEqual(baseline_metrics.call_count,1)
        self.assertIs(baseline_metrics.call_args.args[0],result['baseline'])
        self.assertEqual(row_metrics.call_count,4)

    def test_enemies_keep_a_separate_baseline_for_each_identity(self):
        env=environment();preview=enemies.enemy_defaults(env)
        preview.update(enemies=preview['enemies'][:2],grades=[4,5,6])
        with patch.object(enemies, 'metrics', wraps=comparison.metrics) as baseline_metrics, \
                patch.object(comparison, 'metrics', wraps=comparison.metrics) as row_metrics:
            result=enemies.compare_fixed_enemies(defaults(),env,preview)
        self.assertEqual(baseline_metrics.call_count,2)
        self.assertEqual(row_metrics.call_count,6)
        for call,variant in zip(baseline_metrics.call_args_list,result['variants'][::3]):
            self.assertIs(call.args[0],variant['result'])

    def test_raw_and_prepared_rows_agree_without_mutating_baseline(self):
        result=comparison.compare_ranks(defaults(),environment(),{'ranks':[1,7]})
        baseline=result['baseline'];value=result['variants'][0]['result']
        previous={r['key']:r['value'] for r in comparison.metrics(baseline)};saved=dict(previous)
        self.assertEqual(comparison.comparison_rows(value,baseline),
                         comparison.comparison_rows(value,baseline,baseline_values=previous))
        self.assertEqual(previous,saved)
        missing=comparison.comparison_rows(value,None)
        self.assertTrue(all(row['base_value'] is None and row['delta'] is None for row in missing))
