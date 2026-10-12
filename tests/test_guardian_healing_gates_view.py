"""Real MainWindow class with temporary public data only, no game/chat actions."""
import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
import rouge.app as module
class GuardianHealingGateViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])
    def setUp(self):
        temp=tempfile.TemporaryDirectory(prefix='public-guardian-');self.addCleanup(temp.cleanup);folder=Path(temp.name)
        for key,name in [('RUN_STATE','run.json'),('OPERATOR_STATE','account.json'),('SETTINGS','settings.json')]:
            p=patch.object(module,key,folder/name);p.start();self.addCleanup(p.stop)
        backend=module.DesktopBackend
        p=patch.object(module,'DesktopBackend',lambda _path,callback:backend(folder/'chat',callback));p.start();self.addCleanup(p.stop)
        p=patch.object(module,'list_game_windows',return_value=[]);p.start();self.addCleanup(p.stop)
        self.window=module.MainWindow();self.addCleanup(self.window.close);self.assertFalse(self.window.auto.isChecked())
        self.cultivation={'elite':2,'level':70,'potential':1,'trust':100,'module_id':'uniequip_002_sunbr','module_level':3}
        p=patch.object(self.window,'training_conditions',side_effect=lambda:dict(self.cultivation));p.start();self.addCleanup(p.stop)
    def check_actor(self,op,module_id,equal_qualifies,gate):
        self.cultivation.update(module_id=module_id,level=70)
        self.window.select_operator(op)
        widget=next(w for owner,key,_,w in self.window.model_option_widgets if owner==op and key=='guardian_healing_target_hp_ratio')
        self.assertTrue(self.window.damage_form.isRowVisible(widget));self.assertIsNone(widget.value());self.assertFalse(widget.ratio.isEnabled())
        self.window.calculate();self.assertIsNone(self.window.damage_result['result']['guardian_module_healing_reference']['qualified'])
        widget.setValue(.5);self.window.calculate()
        self.assertIs(self.window.damage_result['result']['guardian_module_healing_reference']['qualified'],equal_qualifies)
        self.assertEqual(self.window.damage_result['scenario']['guardian_healing_target_hp_ratio'],.5)
        self.cultivation['level']=gate-1;self.window.update_skill_options();self.assertFalse(self.window.damage_form.isRowVisible(widget))
        self.cultivation.update(module_id=None,module_level=0,level=70);self.window.select_operator('char_298_susuro')
        self.assertFalse(self.window.damage_form.isRowVisible(widget));self.window.calculate()
        self.assertNotIn('guardian_healing_target_hp_ratio',self.window.damage_result['scenario'])
        self.assertNotIn('guardian_module_healing_reference',self.window.damage_result['result'])
    def test_gummy_own_lt_control(self):self.check_actor('char_196_sunbr','uniequip_002_sunbr',False,40)
    def test_shu_own_le_control(self):self.check_actor('char_2025_shu','uniequip_002_shu',True,60)
if __name__=='__main__':unittest.main()
