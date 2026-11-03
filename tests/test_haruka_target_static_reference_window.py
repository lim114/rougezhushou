import copy,time,unittest
from tests import test_batch185_mainwindow as setup_module
from rouge.haruka_target_static_reference import FLAG,OP,MODULE

class HarukaTargetStaticReferenceWindowTests(unittest.TestCase):
    setUpClass=classmethod(setup_module.Batch185WindowTests.setUpClass.__func__)
    setUp=setup_module.Batch185WindowTests.setUp
    def training(self,level=60,stage=1):
        self.window.apply_operator_observation({'id':OP,'scope':'account',
            'fields':{'elite':2,'level':level,'trust':100,'potential':1,'module_id':MODULE,'module_level':stage},
            'skill_ranks':{'1':7,'2':7,'3':7}},time.time());self.qt.processEvents()
    def control(self):return next(w for owner,key,skills,w in self.window.model_option_widgets if owner==OP and key==FLAG)
    def test_real_window_selection_budget_cancel_and_no_private_writes(self):
        self.window.use_run_training.setChecked(False);self.window.select_operator(OP);self.training(stage=3)
        self.window.skill.setCurrentIndex(self.window.skill.findData(2));self.qt.processEvents()
        control=self.control();self.assertFalse(control.isChecked());self.assertFalse(control.isHidden())
        self.assertEqual(self.window.healing_targets.maximum(),3)
        self.window.healing_targets.setValue(3)
        account=copy.deepcopy(self.window.account_cache.records);run=copy.deepcopy(self.window.run.state)
        control.setChecked(True);self.qt.processEvents();self.window.calculate()
        r=self.window.damage_result['result'];self.assertEqual(r[FLAG]['modeled_potential_recipients'],3)
        self.assertIsNone(r['total_healing']);self.assertIn('普通治疗条件小计',self.window.damage_text.toPlainText())
        control.setChecked(False);self.qt.processEvents();self.window.calculate()
        self.assertNotIn(FLAG,self.window.damage_result['result'])
        self.assertEqual(self.window.account_cache.records,account);self.assertEqual(self.window.run.state,run)
        self.assertTrue(self.window.isVisible());self.assertFalse(self.window.auto.isChecked())
    def test_cultivation_and_operator_gates_skip_hidden_selection(self):
        self.window.use_run_training.setChecked(False);self.window.select_operator(OP);self.training(level=59)
        control=self.control();self.assertTrue(control.isHidden())
        self.training(level=60);control.setChecked(True);self.qt.processEvents()
        for skill,cap in ((1,2),(2,3),(3,2)):
            self.window.skill.setCurrentIndex(self.window.skill.findData(skill));self.qt.processEvents();self.window.calculate()
            self.assertFalse(control.isHidden());self.assertEqual(self.window.damage_result['result'][FLAG]['selector_limit_reference'],cap)
        self.window.select_operator('silverash');self.qt.processEvents();self.window.calculate()
        self.assertTrue(control.isHidden());self.assertNotIn(FLAG,self.window.damage_result['scenario'])
        self.assertNotIn(FLAG,self.window.damage_result['result'])

if __name__=='__main__':unittest.main()
