"""Temporary public state; no game windows, sampling or chat sends."""
import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
import rouge.app as module

class SusuroModuleHealingViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])

    def setUp(self):
        temp=tempfile.TemporaryDirectory(prefix='public-susuro-');self.addCleanup(temp.cleanup);folder=Path(temp.name)
        for key,name in (('RUN_STATE','run.json'),('OPERATOR_STATE','account.json'),('SETTINGS','settings.json')):
            p=patch.object(module,key,folder/name);p.start();self.addCleanup(p.stop)
        backend=module.DesktopBackend
        p=patch.object(module,'DesktopBackend',lambda _path,callback:backend(folder/'chat',callback));p.start();self.addCleanup(p.stop)
        p=patch.object(module,'list_game_windows',return_value=[]);p.start();self.addCleanup(p.stop)
        self.window=module.MainWindow();self.addCleanup(self.window.close)
        self.assertFalse(self.window.auto.isChecked())
        self.cultivation={'elite':2,'level':70,'potential':1,'trust':100,'module_id':'uniequip_002_susuro','module_level':3}
        p=patch.object(self.window,'training_conditions',side_effect=lambda:dict(self.cultivation));p.start();self.addCleanup(p.stop)
        self.window.select_operator('char_298_susuro')
        self.widget=next(w for op,key,skills,w in self.window.model_option_widgets if key=='healing_target_hp_ratio')

    def test_only_selected_qualified_susuro_has_recipient_ratio_and_unknown_default(self):
        self.assertTrue(self.window.damage_form.isRowVisible(self.widget))
        self.assertIsNone(self.widget.value())
        self.assertFalse(self.widget.ratio.isEnabled())
        self.window.calculate();self.assertIsNone(self.window.damage_result['scenario']['healing_target_hp_ratio'])
        self.assertIsNone(self.window.damage_result['result']['susuro_module_healing_reference']['qualified'])
        self.widget.setValue(.500005);self.window.calculate()
        self.assertTrue(self.widget.ratio.isEnabled())
        self.assertEqual(self.window.damage_result['scenario']['healing_target_hp_ratio'],.500005)
        self.assertIs(self.window.damage_result['result']['susuro_module_healing_reference']['qualified'],True)
        self.cultivation['level']=39;self.window.update_skill_options()
        self.assertFalse(self.window.damage_form.isRowVisible(self.widget))
        self.cultivation.update(module_id=None,module_level=0,level=70)
        self.window.select_operator('char_196_sunbr')
        self.assertFalse(self.window.damage_form.isRowVisible(self.widget))
        self.window.calculate()
        self.assertNotIn('healing_target_hp_ratio',self.window.damage_result['scenario'])
        self.assertNotIn('susuro_module_healing_reference',self.window.damage_result['result'])

if __name__=='__main__':unittest.main()
