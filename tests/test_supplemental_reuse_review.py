from collections import Counter
from contextlib import ExitStack
from copy import deepcopy
import unittest
from unittest.mock import patch

from rouge import supplemental_run as run, supplemental_comparison as comparison
from rouge.supplemental_skills import defaults
from tests.test_supplemental_run_141 import environment


class SupplementalReuseReviewTests(unittest.TestCase):
    def test_current_rank_reuses_baseline_but_returned_variant_is_independent(self):
        preview = defaults('char_123_fang')
        env = environment(['rogue_6_relic_book_1'])
        original = deepcopy((preview, env))
        with patch.object(comparison, '_calculate_run_skill', wraps=comparison._calculate_run_skill) as calculate:
            report = comparison.compare_ranks(preview, env, {'ranks': [7, 1]})
        self.assertEqual(calculate.call_count, 2)
        self.assertEqual(report['baseline'], report['variants'][0]['result'])
        original_value = report['baseline']['rows'][0]['value']
        report['variants'][0]['result']['rows'][0]['value'] = 'changed'
        self.assertEqual(report['baseline']['rows'][0]['value'], original_value)
        self.assertEqual((preview, env), original)

    def test_each_effect_is_classified_once_per_family(self):
        names = ('is_attribute_rune', 'cost_layer',
                 'supported_sp', 'supported_healing', 'supported_damage')
        with ExitStack() as stack:
            checks = {name: stack.enter_context(patch.object(run, name, wraps=getattr(run, name))) for name in names}
            result = run.run_skill_reference(defaults(), environment(['rogue_6_relic_legacy_27', 'rogue_6_relic_book_1']))
        self.assertTrue(result['attribute_resolution']['runes'])
        for name, check in checks.items():
            with self.subTest(family=name):
                counts = Counter(id(call.args[0]) for call in check.call_args_list)
                self.assertTrue(counts)
                self.assertTrue(all(count == 1 for count in counts.values()), counts)
