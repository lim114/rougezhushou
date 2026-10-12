import copy,time,unittest
from tests import test_batch185_mainwindow as setup_module

class MeiModuleStaticReferenceWindowTests(unittest.TestCase):
    setUpClass=classmethod(setup_module.Batch185WindowTests.setUpClass.__func__)
    setUp=setup_module.Batch185WindowTests.setUp
    def training(self,level=40,module='uniequip_002_mm',stage=1):
        self.window.apply_operator_observation({'id':'char_133_mm','scope':'account',
            'fields':{'elite':2,'level':level,'trust':100,'potential':1,'module_id':module,'module_level':stage},
            'skill_ranks':{'1':7,'2':7}},time.time());self.qt.processEvents()
    def control(self):
        return next(w for owner,key,skills,w in self.window.model_option_widgets if owner=='char_133_mm' and key=='mei_module_static_reference')

    def test_manual_condition_real_calculation_default_cancel_and_no_records_write(self):
        self.window.use_run_training.setChecked(False);self.window.select_operator('char_133_mm');self.training(stage=3)
        control=self.control();self.assertFalse(control.isChecked());self.assertFalse(control.isHidden())
        self.assertNotIn('mei_module_static_reference',self.window.damage_result['result'])
        account=copy.deepcopy(self.window.account_cache.records);run=copy.deepcopy(self.window.run.state)
        control.setChecked(True);self.qt.processEvents()
        self.assertFalse(self.window.relic_context.isHidden())
        self.assertIn('mei_target_motion',self.window.relic_context.placeholderText())
        self.assertIsNone(self.window.damage_result['result']['mei_module_static_reference']['target_motion_declaration'])
        self.window.relic_context.setPlainText('{"mei_target_motion":"fly"}');self.qt.processEvents()
        self.window.calculate();self.qt.processEvents()
        r=self.window.damage_result['result'];ref=r['mei_module_static_reference']
        self.assertEqual(ref['target_motion_declaration'],'fly')
        self.assertEqual(ref['condition_source'],'manual_offline_preview')
        self.assertEqual(r['per_hit'],ref['packets'][1]['per_hit_reference'])
        self.assertIsNone(r['total_damage']);self.assertIn('明确选择的静态单包条件',self.window.damage_text.toPlainText())
        control.setChecked(False);self.qt.processEvents();self.window.calculate()
        self.assertNotIn('mei_module_static_reference',self.window.damage_result['result'])
        self.assertEqual(self.window.account_cache.records,account);self.assertEqual(self.window.run.state,run)
        self.assertTrue(self.window.isVisible());self.assertFalse(self.window.auto.isChecked())

    def test_unlock_skill_operator_switch_and_automatic_resources_do_not_supply_motion(self):
        self.window.use_run_training.setChecked(False);self.window.select_operator('char_133_mm');self.training(level=39)
        control=self.control();self.assertTrue(control.isHidden())
        self.training(level=40);control.setChecked(True);self.qt.processEvents()
        self.window.run.calculation_resources=lambda:{'mei_target_motion':{'value':'fly'}}
        self.window.relic_context.clear();self.window.calculate()
        self.assertIsNone(self.window.damage_result['result']['mei_module_static_reference']['target_motion_declaration'])
        self.window.relic_context.setPlainText('{"mei_target_motion":"not_fly"}');self.qt.processEvents()
        self.window.skill.setCurrentIndex(self.window.skill.findData(2));self.qt.processEvents()
        self.assertFalse(control.isHidden());self.window.calculate()
        self.assertIn('mei_module_static_reference',self.window.damage_result['result'])
        self.window.select_operator('silverash');self.qt.processEvents();self.window.calculate()
        self.assertTrue(control.isHidden());self.assertNotIn('mei_module_static_reference',self.window.damage_result['scenario'])
        self.assertNotIn('mei_module_static_reference',self.window.damage_result['result'])

if __name__=='__main__':unittest.main()
