import copy
import unittest

from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.haruka_healing_reference import conditional_input_limit, reference

OP = 'char_4202_haruka'
MODULE = 'uniequip_002_haruka'
EXTRA_HEAL = '护佑者额外目标治疗（组合待核验）'
EXTRA_DAMAGE = '额外目标治疗衍生伤害（组合待核验）'


def evaluate(skill=1, **extra):
    return calculate_damage({'operator': OP, 'skill': skill, 'base_attack': 1000,
        'elite': 2, 'level': 60, 'skill_rank': 10, 'module_id': MODULE,
        'module_level': 1, 'window_seconds': 10, **extra})


def component(result, name):
    return next(c for c in result['components'] if c['name'] == name)


class HarukaHealingTargetsTests(unittest.TestCase):
    def test_all_module_stages_double_s1_and_s3_potential_reference(self):
        for stage in (1, 2, 3):
            for skill, expected in ((1, 13500), (3, 20925)):
                for mode in ('frames', 'continuous'):
                    one = evaluate(skill, module_level=stage, healing_targets=1, timing_mode=mode)
                    two = evaluate(skill, module_level=stage, healing_targets=2, timing_mode=mode)
                    self.assertEqual(two['total_healing'], 2 * one['total_healing'])
                    if mode == 'frames': self.assertEqual(two['total_healing'], expected)
                    self.assertEqual(two['haruka_healing_reference']['selected_trait_target_limit_parameter'], 2)

    def test_unlock_boundary_and_absent_module_do_not_apply_trait_two(self):
        for extra in ({'level': 59}, {'elite': 1, 'level': 80, 'skill_rank': 7},
                      {'elite': 0, 'level': 50, 'skill_rank': 7},
                      {'module_id': None, 'module_level': 0}):
            one = evaluate(healing_targets=1, **extra)
            two = evaluate(healing_targets=2, **extra)
            self.assertEqual(one['total_healing'], two['total_healing'])
            self.assertFalse(two['haruka_healing_reference']['module_unlocked'])
            self.assertEqual(two['haruka_healing_reference']['selected_trait_target_limit_parameter'], 1)

    def test_s2_all_ranks_follow_actual_add_parameter_without_module(self):
        for rank in range(1, 11):
            one = evaluate(2, module_id=None, module_level=0, skill_rank=rank, healing_targets=1)
            two = evaluate(2, module_id=None, module_level=0, skill_rank=rank, healing_targets=2)
            extra = int(rank >= 7)
            self.assertEqual(two['haruka_healing_reference']['skill_target_add_parameter'], extra)
            self.assertEqual(two['total_healing'], one['total_healing'] * (1 + extra))
            self.assertEqual(two['total_damage'], one['total_damage'] * (1 + extra))

    def test_s2_module_base_and_rank_add_remain_separate_sources(self):
        for rank in range(1, 11):
            r = evaluate(2, skill_rank=rank, healing_targets=2)
            ref = r['haruka_healing_reference']
            self.assertEqual(ref['selected_trait_target_limit_parameter'], 2)
            self.assertEqual(ref['skill_target_add_parameter'], int(rank >= 7))
            self.assertEqual(ref['modeled_target_limit_reference'], 2)
            self.assertEqual(ref['conditional_target_limit_reference'], 2 + int(rank >= 7))
            self.assertIsInstance(r['total_healing'], (int, float))

    def test_third_recipient_is_unplaced_and_keeps_two_recipient_subtotals(self):
        for mode in ('frames', 'continuous'):
            two = evaluate(2, healing_targets=2, timing_mode=mode)
            three = evaluate(2, healing_targets=3, timing_mode=mode)
            self.assertIsNone(three['total_healing'])
            self.assertIsNone(three['total_damage'])
            self.assertEqual(three['known_healing_subtotals']['window_healing'], two['total_healing'])
            self.assertEqual(three['known_damage_subtotals']['window_damage'], two['total_damage'])
            for name, quantity in ((EXTRA_HEAL, two['total_healing']), (EXTRA_DAMAGE, two['total_damage'])):
                c = component(three, name)
                self.assertEqual(c['total'], quantity / 2)
                self.assertNotIn('times_seconds', c)
                self.assertIsNone(c['actual_total'])
            for key in ('total_healing', 'window_healing', 'window_hps', 'cycle_healing', 'cycle_hps'):
                self.assertIsNone(three['estimate']['skill'][key])

    def test_zero_declaration_and_zero_window_keep_zero_output(self):
        for skill in (1, 2, 3):
            for mode in ('frames', 'continuous'):
                for extra in ({'healing_targets': 0}, {'healing_targets': 3, 'window_seconds': 0}):
                    r = evaluate(skill, timing_mode=mode, **extra)
                    self.assertEqual(r['total_healing'], 0)
                    self.assertEqual(r['total_damage'], 0)
                    self.assertEqual(r['estimate']['skill']['window_healing'], 0)
                    if 'known_healing_subtotals' in r:
                        self.assertEqual(r['known_healing_subtotals']['window_healing'], 0)

    def test_empty_enemy_does_not_cancel_independent_third_healing_source(self):
        r = evaluate(2, healing_targets=3, timing={'target_disappears_seconds': 0})
        self.assertIsNone(r['total_healing'])
        self.assertEqual(r['total_damage'], 0)
        self.assertGreater(component(r, EXTRA_HEAL)['total'], 0)
        self.assertEqual(component(r, EXTRA_DAMAGE)['total'], 0)

    def test_owner_empty_range_does_not_prove_extra_friend_acquisition_absent(self):
        for timing in ({'target_windows': []}, {'interruptions': [[0, 60]]}):
            r = evaluate(2, healing_targets=3, timing=timing)
            self.assertIsNone(r['total_healing'])
            self.assertIsNone(component(r, EXTRA_HEAL)['actual_total'])
            self.assertNotIn('times_seconds', component(r, EXTRA_HEAL))

    def test_healing_factor_applies_once_to_known_two_reference(self):
        base = evaluate(2, healing_targets=3)
        scaled = evaluate(2, healing_targets=3, relic_ids=['rogue_6_relic_legacy_81'])
        self.assertEqual(scaled['known_healing_subtotals']['window_healing'], 10800)
        self.assertEqual(component(scaled, '护佑者普通治疗')['total'], 10800)
        self.assertEqual(scaled['known_healing_subtotals']['window_healing'], base['known_healing_subtotals']['window_healing'] * 1.2)
        self.assertIsNone(scaled['total_healing'])
        # Independent amounts remain before the final recipient factor.
        self.assertEqual(scaled['external_event_reference']['window_reference']['conditional_components'][0]['total'], 4500)

    def test_bubble_and_levitate_references_preserve_independent_parameters(self):
        for potential in (1, 6):
            for skill in (1, 2, 3):
                one = evaluate(skill, healing_targets=1, potential=potential, bubble_bursts=2, levitate_triggers=1)
                two = evaluate(skill, healing_targets=2, potential=potential, bubble_bursts=2, levitate_triggers=1)
                for name in ('扶摇花火', '浮泡治疗衍生伤害', '浮泡浮空持续伤害'):
                    matches = [c for c in one['external_event_reference']['conditional_components'] if c['name'] == name]
                    if matches:
                        target = next(c for c in two['external_event_reference']['conditional_components'] if c['name'] == name)
                        self.assertEqual(matches[0], target)

    def test_repeat_third_source_keeps_full_cast_and_cycle_unknown(self):
        r = evaluate(2, healing_targets=3, haruka_repeat=True)
        self.assertIsNone(r['total_healing'])
        self.assertIsNone(r['known_healing_subtotals']['total_healing'])
        self.assertIsNone(r['known_damage_subtotals']['total_damage'])
        self.assertIsNone(r['estimate']['skill']['cycle_healing'])
        self.assertGreater(r['known_healing_subtotals']['window_healing'], 0)

    def test_shared_reference_input_limit_obeys_skill_rank_and_module_gate(self):
        p = catalog()['operators'][OP]
        before = copy.deepcopy(p)
        for rank in range(1, 11):
            for elite, level, stage in ((0, 50, 1), (1, 80, 3), (2, 59, 2), (2, 60, 0), (2, 60, 1), (2, 90, 3)):
                s = {'elite': elite, 'level': level, 'module_id': MODULE, 'module_level': stage, 'skill_rank': rank}
                for index in range(3):
                    skill = p['skills'][index]['levels'][rank - 1]
                    base = 2 if elite == 2 and level >= 60 and stage else 1
                    added = int(index == 1 and rank >= 7)
                    self.assertEqual(conditional_input_limit(p, s, skill), base + added)
        self.assertIsNone(reference(catalog()['operators']['char_2025_shu'], {}, p['skills'][0]['levels'][0]))
        self.assertEqual(p, before)

    def test_metadata_and_report_keep_native_acquisition_unknown(self):
        r = evaluate(2, healing_targets=3)
        ref = r['haruka_healing_reference']
        for key in ('actual_target_limit', 'actual_target_count', 'actual_acquisition_times_seconds'):
            self.assertIsNone(ref[key])
        for key in ('native_composition_verified', 'native_attachment_verified', 'live_state_verified'):
            self.assertFalse(ref[key])
        text = format_estimate(r)
        self.assertIn('当前特性治疗人数参数：2 名', text)
        self.assertIn('当前技能增加人数参数：1 名', text)
        self.assertIn('人数相加条件参考：3 名', text)
        self.assertIn('实际同时受疗人数：未知', text)
        self.assertIn('观察窗口已计治疗小计：9,000', text)
        self.assertIn('观察窗口治疗：未知', text)


if __name__ == '__main__':
    unittest.main()
