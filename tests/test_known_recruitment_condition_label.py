"""Known pending recruitment source stays visible; unknown identifiers stay opaque."""
import copy
import unittest

from rouge.damage import calculate_damage
from rouge.reporting import format_report


def result(mode, kind):
    return calculate_damage({'operator': 'silverash', 'skill': 3, 'elite': 2,
                             'level': 90, 'potential': 1, 'trust': 100, 'module_id': None,
                             'module_level': 0, 'skill_rank': 10, 'base_attack': 1000,
                             'window_seconds': 3, 'timing_mode': mode,
                             'relic_ids': ['rogue_6_relic_cargo_10'], 'recruitment_kind': kind})


class KnownConditionLabelTests(unittest.TestCase):
    def test_pending_human_label_keeps_missing_and_no_assumption_meaning(self):
        for mode in ('frames', 'continuous'):
            for kind in (None, 'unknown'):
                r = result(mode, kind)
                before = copy.deepcopy(r)
                human = format_report(r)
                self.assertIn('同行者：条件缺失或机制未覆盖；缺 应急招募来源', human)
                self.assertIn('同行者：尚未确认条件 应急招募来源，未按0或满层套用。', human)
                self.assertNotIn('emergency_hire', human)
                self.assertEqual(r['relic_resolution']['records'][0]['missing_conditions'], ['emergency_hire'])
                self.assertFalse(r['relic_resolution']['complete'])
                self.assertEqual(r, before)

    def test_technical_text_and_known_source_human_output_are_unchanged(self):
        for mode in ('frames', 'continuous'):
            for kind in (None, 'unknown', 'non_emergency', 'emergency_hire'):
                r = result(mode, kind)
                if kind in (None, 'unknown'):
                    self.assertIn('emergency_hire', format_report(r, technical=True))
                else:
                    self.assertNotIn('应急招募来源', format_report(r))
                    self.assertEqual(r['relic_resolution']['records'][0]['missing_conditions'], [])

    def test_other_opaque_keys_and_namespaced_or_extended_keys_stay_opaque(self):
        for key in ('global_buff_normal:rogue_6_unknown[dark]', 'emergency_hire_unknown',
                    'global_buff_normal:emergency_hire', 'emergency_hire.amount'):
            r = result('frames', 'non_emergency')
            r['estimate']['warnings'].append('未核验来源 ' + key + '，未套用。')
            human = format_report(r)
            self.assertIn('未核验配置', human)
            self.assertNotIn('应急招募来源', human)
            self.assertIn(key, format_report(r, technical=True))


if __name__ == '__main__':
    unittest.main()
