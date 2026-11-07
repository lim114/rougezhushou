"""Prepared calculation inputs and grouped cells are reused at their owners."""
from copy import deepcopy
import unittest
from unittest.mock import patch
from rouge import calibration, damage
from rouge import branch_position_overview as positions


class PreparationReuseTests(unittest.TestCase):
    def test_panel_layers_prepares_the_scenario_once(self):
        scenario = {'operator': 'mechanist', 'skill': 3,
                    'relic_ids': ['rogue_6_relic_legacy_16']}
        before = deepcopy(scenario)
        with patch.object(damage, '_prepare_damage', wraps=damage._prepare_damage) as prepare, \
                patch.object(calibration, '_prepare_damage', prepare):
            result = calibration.panel_layers(scenario)
        self.assertEqual(prepare.call_count, 1)
        self.assertEqual(scenario, before)
        self.assertEqual(result['panels']['培养与模组']['attack'], 573)
        self.assertEqual(result['panels']['藏品与分队符文写回']['attack'], 716)
        self.assertAlmostEqual(result['panels']['技能期间参考']['attack'], 2720.8)

    def test_matching_window_reuses_skill_but_distinct_cast_conditions_recalculate(self):
        for scenario, expected in (
                ({'operator':'mechanist','skill':1}, 1),
                ({'operator':'mechanist','skill':1,'window_seconds':8}, 2),
                ({'operator':'mechanist','skill':3,'charge_count':1}, 2),
                ({'operator':'silverash','skill':2,'deployment_stacks':1,'companion_attack':500}, 2)):
            with self.subTest(scenario=scenario), patch.object(damage, '_skill_damage_base',
                                                              wraps=damage._skill_damage_base) as compute:
                damage.calculate_damage(scenario)
                self.assertEqual(compute.call_count, expected)

    def test_silverash_deployment_needs_companion_attack_only_for_positive_stacks(self):
        from rouge.condition_inputs import RunConditionError
        scenario = {'operator': 'silverash', 'skill': 2, 'deployment_stacks': 0}
        self.assertEqual(len(damage.calculate_damage(scenario)['components']), 1)
        scenario['deployment_stacks'] = 1
        with self.assertRaisesRegex(RunConditionError, '请提供受益干员攻击力'):
            damage.calculate_damage(scenario)
        scenario['companion_attack'] = 0
        self.assertEqual(damage.calculate_damage(scenario)['components'][1]['total'], 0)

    def test_overlapping_references_copy_the_group_cell_once(self):
        cell = {'row': 1, 'col': 2}
        references = [{'cell': cell, 'name': name, 'reference_id': name} for name in ('甲', '乙')]
        source = {'rows': [{'map_references': references}], 'stage_name': '测试关卡',
                  'source': {'sha256': 'fixed-public-source'}}
        with patch.object(positions, 'branch_reference', return_value=source), \
                patch.object(positions, 'deepcopy', wraps=deepcopy) as copied:
            result = positions.branch_position_overview('test-stage')
        self.assertEqual(sum(call.args[0] is cell for call in copied.call_args_list), 1)
        self.assertEqual(result['reference_count'], 2)
        self.assertEqual(result['cell_count'], 1)
        result['rows'][0]['cell']['row'] = 9
        result['rows'][0]['references'][0]['name'] = '修改'
        self.assertEqual(cell['row'], 1)
        self.assertEqual(references[0]['name'], '甲')


if __name__ == '__main__':
    unittest.main()
