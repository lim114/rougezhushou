"""Real MainWindow class; public synthetic training in temporary storage."""
import time
import unittest
from tests import test_batch185_mainwindow as setup_module


class MechanistModuleReferenceWindowTests(unittest.TestCase):
    setUpClass=classmethod(setup_module.Batch185WindowTests.setUpClass.__func__)
    setUp=setup_module.Batch185WindowTests.setUp

    def training(self, stage):
        record={'id':'mechanist','scope':'account','fields':{'elite':2,'level':90,'trust':100,
                    'potential':1,'module_id':'uniequip_002_mcnist','module_level':stage},
                'skill_ranks':{'1':7,'2':7,'3':7}}
        self.window.apply_operator_observation(record,time.time())
        self.qt.processEvents()

    def control(self):
        return next(w for owner,key,skills,w in self.window.model_option_widgets
                    if owner=='mechanist' and key=='mechanist_module_static_reference')

    def test_selected_reference_uses_manual_blocker_and_preserves_unknown_total(self):
        self.window.use_run_training.setChecked(False);self.window.select_operator('mechanist')
        self.training(2);self.window.skill.setCurrentIndex(self.window.skill.findData(3));self.qt.processEvents()
        control=self.control();self.assertFalse(control.isChecked());self.assertFalse(control.isHidden())
        self.assertIsNotNone(self.window.damage_result)
        self.assertNotIn('mechanist_module_reference',self.window.damage_result['result'])
        control.setChecked(True);self.qt.processEvents()
        self.assertFalse(self.window.relic_context.isHidden())
        self.assertIn('mechanist_target_blocker',self.window.relic_context.placeholderText())
        unknown=self.window.damage_result['result']['mechanist_module_reference']
        self.assertIsNone(unknown['target_blocker_declaration'])
        self.window.relic_context.setPlainText('{"mechanist_target_blocker":"own_token"}');self.qt.processEvents()
        self.window.calculate();self.qt.processEvents()
        result=self.window.damage_result['result'];reference=result['mechanist_module_reference']
        self.assertEqual(reference['condition_source'],'manual_offline_preview')
        self.assertEqual(reference['target_blocker_declaration'],'own_token')
        self.assertTrue(all(row['module_attack_scale']==1.5 for row in reference['packets']))
        self.assertIsNone(result['total_damage'])
        self.assertIsNone(result['estimate']['skill']['total_damage'])
        self.assertIn('机械师模组',self.window.damage_text.toPlainText())
        self.assertTrue(self.window.isVisible())
        self.assertFalse(self.window.auto.isChecked())

    def test_first_stage_skill_gate_and_operator_switch_do_not_reuse_binding(self):
        self.window.use_run_training.setChecked(False);self.window.select_operator('mechanist')
        self.training(1);self.window.skill.setCurrentIndex(self.window.skill.findData(1));self.qt.processEvents()
        control=self.control();self.assertFalse(control.isHidden());control.setChecked(True)
        self.window.relic_context.setPlainText('{"mechanist_target_blocker":"self"}');self.qt.processEvents()
        self.window.calculate();self.qt.processEvents()
        self.assertIn('mechanist_module_reference',self.window.damage_result['result'])
        self.window.skill.setCurrentIndex(self.window.skill.findData(3));self.qt.processEvents()
        self.assertTrue(control.isHidden());self.window.calculate()
        self.assertNotIn('mechanist_module_static_reference',self.window.damage_result['scenario'])
        self.assertNotIn('mechanist_module_reference',self.window.damage_result['result'])
        self.window.select_operator('silverash');self.qt.processEvents();self.window.calculate()
        self.assertTrue(control.isHidden())
        self.assertNotIn('mechanist_module_reference',self.window.damage_result['result'])


if __name__=='__main__':unittest.main()
