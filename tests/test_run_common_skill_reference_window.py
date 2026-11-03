"""MainWindow class with public views and temporary storage, no native capture."""
from copy import deepcopy
from unittest.mock import patch
import unittest

from tests import test_batch185_mainwindow as setup_module

OP='char_298_susuro'


class RunCommonSkillWindowTests(unittest.TestCase):
    setUpClass=classmethod(setup_module.Batch185WindowTests.setUpClass.__func__)
    setUp=setup_module.Batch185WindowTests.setUp

    def run_view(self,ranks=None):
        state={'id':OP,'scope':'run','fields':{'elite':1,'level':40,'trust':0,'potential':1,
                  'module_id':None,'module_level':0},'skill_ranks':ranks or {'1':3},
               'run_confirmed_fields':['elite','level','trust','potential','module_id','module_level']}
        original=self.window.current_operator_state
        mocked=patch.object(self.window,'current_operator_state',
            lambda **kwargs:deepcopy(state) if self.window.operator.currentData()==OP else original(**kwargs))
        mocked.start();self.addCleanup(mocked.stop)
        self.window.use_run_training.setChecked(False);self.window.select_operator(OP)
        self.window.skill.setCurrentIndex(self.window.skill.findData(2));self.qt.processEvents()
        return state

    def test_select_calculates_changed_rank_and_cancel_restores_without_record_write(self):
        state=self.run_view();before=deepcopy(state)
        account_before=deepcopy(self.window.account_cache.records)
        run_before=deepcopy(self.window.run.state)
        checkbox=self.window.run_common_skill_reference
        self.assertFalse(checkbox.isChecked());self.assertTrue(checkbox.isEnabled())
        self.assertFalse(checkbox.isHidden())
        plain=deepcopy(self.window.damage_result)
        self.assertEqual(plain['scenario']['skill_rank'],7)
        checkbox.setChecked(True);self.qt.processEvents()
        selected=self.window.damage_result
        self.assertEqual(selected['scenario']['skill_rank'],3)
        self.assertNotEqual(selected['result']['components'],plain['result']['components'])
        self.assertIn('公共等级来源参考',self.window.rank.text())
        self.assertIn('S2',self.window.skill_cultivation_explanation.text())
        self.assertIn('未直接读取',self.window.damage_text.toPlainText())
        checkbox.setChecked(False);self.qt.processEvents()
        self.assertEqual(self.window.damage_result,plain)
        self.assertEqual(state,before);self.assertEqual(self.window.run.state,run_before)
        self.assertEqual(self.window.account_cache.records,account_before)
        self.assertFalse(self.window.auto.isChecked())

    def test_switch_skill_and_operator_clear_manual_reference(self):
        self.run_view();self.window.run_common_skill_reference.setChecked(True);self.qt.processEvents()
        self.assertEqual(self.window.skill_rank_value(),3)
        self.window.skill.setCurrentIndex(self.window.skill.findData(1));self.qt.processEvents()
        self.assertFalse(self.window.run_common_skill_reference.isChecked())
        self.assertTrue(self.window.run_common_skill_reference.isHidden())
        self.assertEqual(self.window.rank.text(),'等级 3（读取）')
        self.window.select_operator('mechanist');self.qt.processEvents()
        self.assertFalse(self.window.run_common_skill_reference.isChecked())
        self.assertNotEqual(self.window.skill_rank_selection()['source'],'manual_run_common_reference')


if __name__=='__main__':unittest.main()
