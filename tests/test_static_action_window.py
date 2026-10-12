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

    def test_declared_three_part_wait_budget_reaches_actual_window_result_and_text(self):
        self.window.use_run_training.setChecked(False);self.window.select_operator('kaltsit')
        self.window.skill.setCurrentIndex(self.window.skill.findData(1));self.qt.processEvents()
        self.window.frame_timing.setChecked(True)
        self.window.skill_animation_reference.setCurrentIndex(1)
        self.window.timing_scenario.setPlainText('{"interrupt_windows":[[0.5,0.8]],"movement_windows":[[0.8,1.0]]}')
        self.window.calculate();self.qt.processEvents();self.assertIsNotNone(self.window.damage_result)
        result=self.window.damage_result['result']
        stream=next(s for s in result['timing']['streams'] if s.get('three_part_reference',{}).get('wait_budget'))
        budget=stream['three_part_reference']['wait_budget']
        for case in budget['conditional_budgets']:
            self.assertEqual(case['declared_interruption_frame'],15)
            self.assertEqual(case['reference_resume_candidate_frame'],30)
            self.assertEqual(case['pending_wait_ticks_at_window_end'],0)
            self.assertGreater(case['discarded_wait_ticks_due_to_declared_interruption'],0)
            self.assertIsNone(case['restart_first_attack_gate_actual'])
        text=self.window.damage_text.toPlainText()
        self.assertIn('三段等待与声明窗口预算',text)
        self.assertIn('客户端实际步长',text)
        self.assertIn('移动/目标空窗均不清除等待',text)
        self.assertTrue(self.window.isVisible())
