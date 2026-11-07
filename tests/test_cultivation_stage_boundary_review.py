from unittest.mock import patch
import unittest

from rouge import cultivation_comparison as comparison
from tests.test_cultivation_comparison_140 import proposal


class CultivationStageBoundaryReviewTests(unittest.TestCase):
    def test_player_proposal_uses_frozen_operator_and_only_defaults_missing_level(self):
        from PySide6.QtWidgets import QApplication, QComboBox, QWidget
        from rouge.app import MainWindow
        qt = QApplication.instance() or QApplication([])
        owner = QWidget()
        self.addCleanup(owner.close)
        owner.operator = QComboBox(owner)
        owner.operator.addItem('玫兰莎', 'char_208_melan')
        scenario = {'operator':'mechanist','elite':2,'skill':1,'skill_rank':7}
        owner.damage_result = {'scenario':scenario}
        MainWindow.show_cultivation_comparison(owner)
        dialog = owner.cultivation_comparison_dialog
        maximum = comparison.operator_profiles()['mechanist']['phases'][2]['max_level']
        self.assertEqual(dialog.result['rows'][0]['proposal']['level'], maximum)
        with patch.object(comparison, '_calculate_prepared', side_effect=ValueError('internal calculation')):
            with self.assertRaisesRegex(ValueError, 'internal calculation'):
                dialog.calculate()
        for invalid in (0, False, ''):
            with self.subTest(level=invalid):
                scenario['level'] = invalid
                MainWindow.show_cultivation_comparison(owner)
                dialog = owner.cultivation_comparison_dialog
                self.assertIsNone(dialog.result)
                self.assertIn('基准培养方案不可测算', dialog.notice.toPlainText())
        qt.processEvents()

    def test_supplemental_skill_uses_the_computed_proposal_attributes(self):
        from rouge import supplemental_skills as skills
        profiles = comparison.operator_profiles()
        for identity in skills.supplemental_profiles()['operators']:
            with self.subTest(identity=identity):
                self.assertEqual(profiles[identity]['modules'], [])
                scenario = skills.defaults(identity)
                choices = {'proposals': [proposal('基准', level=50), proposal('升级', level=55)]}
                with patch.object(skills, '_attribute_values', wraps=skills._attribute_values) as duplicate:
                    rows = comparison.compare_cultivation(scenario, choices)['rows']
                duplicate.assert_not_called()
                for row in rows:
                    standalone = {**scenario, 'level': row['proposal']['level'], 'count': 1, 'missing_hp': 0}
                    self.assertEqual(row['skill_reference'], skills.skill_reference(standalone))

    def test_supplemental_skill_still_requires_an_explicit_integer_level(self):
        from rouge import supplemental_skills as skills
        scenario = skills.defaults()
        choices = {'proposals': [proposal('默认满级', level=None)]}
        row = comparison.compare_cultivation(scenario, choices)['rows'][0]
        self.assertIsNotNone(row['attributes'])
        self.assertIsNone(row['skill_reference'])
        self.assertIn('level需要整数', row['error'])

    def test_trust_parser_internal_error_propagates(self):
        with patch.object(comparison, '_amount', side_effect=ValueError('internal amount error')):
            with self.assertRaisesRegex(ValueError, 'internal amount error'):
                comparison.compare_cultivation({'operator': 'mechanist'}, {'proposals': [proposal('基准')]})

    def test_equipped_stage_errors_are_owned_by_attribute_entry(self):
        for stage in (True, False, 1.0, '1', None, [], {}, 0, 4):
            with self.subTest(stage=stage):
                preview = {'proposals': [proposal('基准', elite=2, level=70),
                    proposal('模组方案', elite=2, level=70,
                             module_id='uniequip_002_nights', module_level=stage)]}
                with patch.object(comparison, '_attribute_values',
                                  wraps=comparison._attribute_values) as attributes:
                    result = comparison.compare_cultivation({'operator': 'char_141_nights'}, preview)
                self.assertEqual(attributes.call_count, 2)
                self.assertEqual(result['rows'][1]['status'], '不可测算')
                self.assertIsNone(result['rows'][1]['attributes'])

    def test_no_module_pair_is_validated_before_attribute_entry(self):
        for stage in (True, 1, 0.0, None):
            with self.subTest(stage=stage):
                preview = {'proposals': [proposal('基准', elite=2, level=70),
                    proposal('无模组', elite=2, level=70, module_level=stage)]}
                with patch.object(comparison, '_attribute_values',
                                  wraps=comparison._attribute_values) as attributes:
                    result = comparison.compare_cultivation({'operator': 'char_141_nights'}, preview)
                self.assertEqual(attributes.call_count, 1)
                self.assertEqual(result['rows'][1]['status'], '不可测算')
