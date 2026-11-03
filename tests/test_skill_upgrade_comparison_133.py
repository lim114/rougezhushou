import unittest
from copy import deepcopy
from rouge.skill_upgrade_comparison import compare_skill_upgrades, format_skill_upgrades
from rouge.damage import calculate_damage

class SkillUpgradeTests(unittest.TestCase):
    def test_same_scenario_baseline_and_differences(self):
        scenario={'operator':'mechanist','skill':3,'base_attack':1000,'skill_rank':7,'window_seconds':10,'enemy_resistance':50}
        before=deepcopy(scenario);result=compare_skill_upgrades(scenario,{'ranks':[7,10]})
        base,upgrade=result['rows'];self.assertEqual(base['delta_window_damage'],0)
        self.assertGreater(upgrade['delta_window_damage'],0);self.assertEqual(scenario,before)
        self.assertEqual(upgrade['duration_parameter'],40);self.assertEqual(upgrade['sp_cost_parameter'],35)
        self.assertEqual(upgrade['window_damage'],calculate_damage({**scenario,'skill_rank':10})['estimate']['skill']['window_damage'])

    def test_e1_mastery_unavailable_and_training_reference(self):
        result=compare_skill_upgrades({'operator':'mechanist','skill':2,'elite':1,'skill_rank':7},{'ranks':[1,7,8,10]})
        self.assertEqual([r['status'] for r in result['rows'][2:]],['不可测算','不可测算'])
        for row in result['rows'][2:]:
            self.assertIn('未开放',row['error']);self.assertIsNone(row['delta_window_damage'])
        self.assertEqual(result['rows'][2]['original_training_reference']['training_requirement']['kind'],'mastery_upgrade')
        self.assertIn('原表',format_skill_upgrades(result))

    def test_unknown_healing_is_not_zero_difference(self):
        result=compare_skill_upgrades({'operator':'char_2025_shu','skill':1,'skill_rank':7},{'ranks':[7,10]})
        for row in result['rows']:
            self.assertIsNone(row['window_healing']);self.assertIsNone(row['delta_window_healing'])
            self.assertEqual(row['known_window_healing'],0)
        self.assertIn('未知整体输出不当零',format_skill_upgrades(result))

    def test_e0_use_and_nonfixed_end_not_authorized(self):
        result=compare_skill_upgrades({'operator':'char_196_sunbr','skill':1,'elite':0,'skill_rank':7},{'ranks':[7]})
        row=result['rows'][0];self.assertIsNone(row['original_training_reference']['e0_common_use_verified'])
        self.assertEqual(row['duration_parameter'],0);self.assertEqual(row['raw_duration_parameter'],0)
        self.assertIsNone(row['original_training_reference']['actual_activation_verified'])

    def test_invalid_ranks(self):
        for ranks in ([],[True],[1.0],[0],[11],[7,7],list(range(11))):
            with self.assertRaises(ValueError):compare_skill_upgrades({'operator':'mechanist','skill':3},{'ranks':ranks})
