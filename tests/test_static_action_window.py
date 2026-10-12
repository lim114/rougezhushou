"""Default-skin static choices in the real window class, public temporary state."""
import unittest
from tests import test_batch185_mainwindow as setup_module


class StaticActionWindowTests(unittest.TestCase):
    setUpClass=classmethod(setup_module.Batch185WindowTests.setUpClass.__func__)
    setUp=setup_module.Batch185WindowTests.setUp

    def test_mechanist_s2_combo_uses_bound_segments_and_default_stays_unselected(self):
        self.window.use_run_training.setChecked(False);self.window.select_operator('mechanist')
        self.window.skill.setCurrentIndex(self.window.skill.findData(2));self.qt.processEvents()
        combo=self.window.skill_animation_reference
        self.assertIsNone(combo.currentData());self.assertEqual(combo.count(),4)
        ids=[combo.itemData(i) for i in range(1,combo.count())]
        self.assertEqual(ids,['char_4230_mcnist:Front:Skill_2_Loop',
            'char_4230_mcnist:Front:Skill_Down_2_Loop','char_4230_mcnist:Back:Skill_2_Loop'])
        self.assertIn('静态动作选择已核验',combo.toolTip())
        combo.setCurrentIndex(1);self.window.calculate();self.qt.processEvents()
        self.assertIsNotNone(self.window.damage_result)
        self.assertEqual(self.window.damage_result['scenario']['timing']['animation_reference'],ids[0])
        self.assertTrue(self.window.isVisible())

    def test_kaltsit_s1_three_part_choices_enter_calculation_and_keep_first_release_unknown(self):
        self.window.use_run_training.setChecked(False);self.window.select_operator('kaltsit')
        self.window.skill.setCurrentIndex(self.window.skill.findData(1));self.qt.processEvents()
        skill=self.window.skill_animation_reference;normal=self.window.normal_animation_reference
        self.assertEqual((normal.count(),skill.count()),(4,4))
        self.assertIsNone(skill.currentData());self.assertIsNone(normal.currentData())
        self.assertIn('首击未知',skill.itemText(1));skill.setCurrentIndex(1)
        self.window.calculate();self.qt.processEvents();self.assertIsNotNone(self.window.damage_result)
        estimate=self.window.damage_result['result']
        stream=next(row for row in estimate['timing']['streams'] if 'three_part_reference' in row)
        self.assertIsNone(stream['actual_first_release_seconds'])
        self.assertIsNone(stream['three_part_reference']['first_attack_gate_actual'])
        self.assertEqual(len(stream['three_part_reference']['conditional_profiles']),2)
        self.assertFalse(stream['original_animation_reference']['runtime_binding_verified'])

    def test_silverash_normal_random_candidates_stay_explicit_and_enter_recharge_report(self):
        self.window.use_run_training.setChecked(False);self.window.select_operator('silverash')
        self.window.skill.setCurrentIndex(self.window.skill.findData(3));self.qt.processEvents()
        normal=self.window.normal_animation_reference
        self.assertEqual(normal.count(),7);self.assertIsNone(normal.currentData())
        normal.setCurrentIndex(1);self.window.calculate();self.qt.processEvents()
        self.assertIsNotNone(self.window.damage_result)
        estimate=self.window.damage_result['result']
        streams=[*estimate['timing'].get('streams',[]),*estimate['timing'].get('recharge_streams',[])]
        stream=next(row for row in streams if 'three_part_reference' in row)
        self.assertIsNone(stream['three_part_reference']['selection']['sequence'])
        self.assertIsNone(stream['three_part_reference']['selection']['probabilities'])
        self.assertIsNone(stream['actual_first_release_seconds'])
