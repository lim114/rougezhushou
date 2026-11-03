import copy
import unittest

from rouge.catalog import catalog, operator_attributes
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate

OP = 'char_1048_orchd2'
MODULE = 'uniequip_002_orchd2'


def evaluate(stage=0, **options):
    scenario = {'operator': OP, 'skill': 1, 'base_attack': 1000, **options}
    if stage:
        scenario.update(module_id=MODULE, module_level=stage)
    return calculate_damage(scenario)


class OrchidRedeployReferenceTests(unittest.TestCase):
    def test_direct_module_attribute_is_in_cultivated_panel(self):
        self.assertEqual(operator_attributes(OP)['redeploy_seconds'], 70)
        for stage in (1, 2, 3):
            self.assertEqual(operator_attributes(OP, module_id=MODULE,
                module_level=stage)['redeploy_seconds'], 45)

    def test_each_module_stage_keeps_its_talent_reduction_parameter(self):
        for stage, expected, delta in ((0, 55, -15), (1, 30, -15),
                (2, 28, -17), (3, 27, -18)):
            result = evaluate(stage)
            self.assertEqual(result['estimate']['base_stats']['redeploy_seconds'], expected)
            self.assertEqual(result['orchid_redeploy_reference']['talent_delta_seconds_parameter'], delta)

    def test_level_59_does_not_apply_module_attributes_or_upgrade(self):
        for stage in (1, 2, 3):
            result = evaluate(stage, elite=2, level=59)
            reference = result['orchid_redeploy_reference']
            self.assertEqual(result['estimate']['base_stats']['redeploy_seconds'], 55)
            self.assertFalse(reference['module_unlocked'])
            self.assertEqual(reference['module_attribute_delta_seconds_parameter'], 0)
            self.assertEqual(reference['talent_delta_seconds_parameter'], -15)

    def test_level_60_unlocks_all_three_stage_parameters(self):
        for stage, expected in ((1, 30), (2, 28), (3, 27)):
            result = evaluate(stage, elite=2, level=60)
            self.assertEqual(result['estimate']['base_stats']['redeploy_seconds'], expected)
            self.assertTrue(result['orchid_redeploy_reference']['module_unlocked'])

    def test_elite_one_cannot_apply_module_even_at_level_80(self):
        for stage in (0, 1, 2, 3):
            result = evaluate(stage, elite=1, level=80, skill_rank=7)
            self.assertEqual(result['estimate']['base_stats']['redeploy_seconds'], 55)
            self.assertFalse(result['orchid_redeploy_reference']['module_unlocked'])

    def test_elite_zero_has_no_locked_talent_reduction(self):
        for stage in (0, 1, 2, 3):
            result = evaluate(stage, elite=0, level=1, skill_rank=7)
            self.assertEqual(result['estimate']['base_stats']['redeploy_seconds'], 70)
            self.assertEqual(result['orchid_redeploy_reference']['talent_delta_seconds_parameter'], 0)

    def test_potential_three_direct_addition_precedes_module_and_talent(self):
        for potential in (3, 6):
            for stage, expected in ((0, 51), (1, 26), (2, 24), (3, 23)):
                result = evaluate(stage, potential=potential)
                self.assertEqual(result['estimate']['base_stats']['redeploy_seconds'], expected)
            self.assertEqual(operator_attributes(OP, potential=potential,
                module_id=MODULE, module_level=3)['redeploy_seconds'], 41)

    def test_skill_and_timing_mode_do_not_reapply_static_redeploy_sources(self):
        for skill in (1, 2, 3):
            for mode in ('frames', 'continuous'):
                for stage, expected in ((0, 55), (1, 30), (2, 28), (3, 27)):
                    result = evaluate(stage, skill=skill, timing_mode=mode)
                    self.assertEqual(result['estimate']['base_stats']['redeploy_seconds'], expected)

    def test_reference_does_not_create_actual_deployment_events(self):
        reference = evaluate(3)['orchid_redeploy_reference']
        self.assertEqual(reference['parameter_seconds'], 27)
        for key in ('actual_retreat_seconds', 'actual_defeat_seconds',
                'actual_next_deployment_seconds'):
            self.assertIsNone(reference[key])
        for key in ('events_scheduled', 'native_attachment_verified', 'live_state_verified'):
            self.assertFalse(reference[key])
        self.assertEqual(reference['original_talent_identity'],
            {'talent_index': 3, 'prefab_key': '3'})

    def test_existing_rune_layer_is_kept_as_separate_parameter_preview(self):
        for stage, expected in ((0, 20), (1, 7), (2, 5), (3, 4)):
            result = evaluate(stage, relic_ids=['rogue_6_relic_artifact_6'])
            reference = result['orchid_redeploy_reference']
            self.assertEqual(reference['parameter_seconds'], expected)
            self.assertEqual(reference['after_attribute_sources_seconds_reference'], 35 if stage==0 else 22)
            self.assertFalse(reference['native_attachment_verified'])

    def test_public_report_labels_the_parameter_and_unknown_actual_events(self):
        text = format_estimate(evaluate(3))
        self.assertIn('再部署', text)
        self.assertIn('参数参考', text)
        self.assertIn('实际撤退、倒下和再次部署的时刻', text)
        self.assertIn('未安排部署事件', text)

    def test_public_input_and_cached_catalog_are_not_mutated(self):
        scenario = {'operator': OP, 'skill': 1, 'module_id': MODULE,
            'module_level': 3, 'potential': 6, 'window_seconds': 0}
        original = copy.deepcopy(scenario)
        profile_before = copy.deepcopy(catalog()['operators'][OP])
        calculate_damage(scenario)
        self.assertEqual(scenario, original)
        self.assertEqual(catalog()['operators'][OP], profile_before)
        self.assertNotIn('orchid_redeploy_reference',
            calculate_damage({'operator': 'char_133_mm', 'skill': 2}))


if __name__ == '__main__':
    unittest.main()
