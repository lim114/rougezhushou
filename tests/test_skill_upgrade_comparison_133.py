import unittest
from copy import deepcopy
from rouge.skill_upgrade_comparison import compare_skill_upgrades, format_skill_upgrades
from rouge.damage import calculate_damage

class SkillUpgradeTests(unittest.TestCase):
    def test_baseline_and_training_source_are_each_resolved_once(self):
        from unittest.mock import patch
        from rouge import skill_upgrade_comparison as model
        for scenario in ({'operator':'mechanist','skill':3,'skill_rank':7},
                         {'operator':'mechanist','skill':3}):
            with self.subTest(scenario=scenario), patch.object(
                    model, 'calculate_damage', wraps=calculate_damage) as calculate, patch.object(
                    model, '_training_source', wraps=model._training_source) as source:
                comparison = compare_skill_upgrades(scenario, {'ranks':[10, 7, 1]})
                base_rank = scenario.get('skill_rank', 10)
                self.assertEqual(sorted(call.args[0].get('skill_rank', 10) for call in calculate.call_args_list),
                                 [1, 7, 10])
                source.assert_called_once()
                self.assertEqual([row['rank'] for row in comparison['rows']], [10, 7, 1])
                baseline = next(row for row in comparison['rows'] if row['rank'] == base_rank)
                self.assertEqual(baseline['delta_window_damage'], 0)

    def test_player_dialog_reports_rank_input_and_propagates_internal_row_errors(self):
        import json
        from unittest.mock import patch
        from PySide6.QtWidgets import QApplication, QWidget
        from rouge import skill_upgrade_comparison as model
        from rouge.app import MainWindow
        qt = QApplication.instance() or QApplication([])
        owner = QWidget()
        self.addCleanup(owner.close)
        owner.damage_result = {'scenario': {'operator':'mechanist','skill':2,'elite':1,'skill_rank':7}}
        MainWindow.show_skill_upgrades(owner)
        dialog = owner.skill_upgrade_dialog
        self.assertIn('未开放', dialog.result['rows'][-1]['error'])
        dialog.editor.setPlainText(json.dumps({'ranks':[True]}))
        dialog.calculate()
        self.assertIsNone(dialog.result)
        self.assertIn('整数等级', dialog.notice.toPlainText())
        dialog.editor.setPlainText(json.dumps({'ranks':[7, 6]}))
        def broken_row(scenario):
            if scenario['skill_rank'] == 6: raise ValueError('internal row failure')
            return calculate_damage(scenario)
        with patch.object(model, 'calculate_damage', side_effect=broken_row):
            with self.assertRaisesRegex(ValueError, 'internal row failure'):
                dialog.calculate()
        qt.processEvents()

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
