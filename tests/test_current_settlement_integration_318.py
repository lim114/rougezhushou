from copy import deepcopy
from tests import test_batch185_mainwindow as setup_module
import unittest
from PySide6.QtCore import Qt
from rouge.current_settlement_modes_view import CurrentSettlementModesPanel

class CurrentSettlementIntegration318Tests(unittest.TestCase):
    setUpClass=classmethod(setup_module.Batch185WindowTests.setUpClass.__func__)
    setUp=setup_module.Batch185WindowTests.setUp
    def test_actual_MainWindow_stage_preview_exposes_reference_without_run_mutation(self):
        p=self.window.reference_panel('stages');before=deepcopy(self.window.run.state);old=deepcopy(self.window.battle_preview.context);self.assertIs(self.window.centralWidget().currentWidget(),p);self.assertFalse(p.scope.currentData());self.assertTrue(p.scope.isHidden());i=next(i for i in range(p.entries.count())if p.entries.item(i).data(Qt.ItemDataRole.UserRole)=='ro6_n_1_2');p.entries.setCurrentRow(i);self.assertTrue(p.open_current_battle());dialog=p.current_battle_dialog;self.addCleanup(dialog.close);child=dialog.panel.settlement
        dialog.panel.tabs.setCurrentWidget(dialog.panel.rewards);dialog.panel.rewards.sections.setCurrentWidget(child);self.qt.processEvents();self.assertTrue(child.isVisible())
        child.entry.setCurrentIndex(child.entry.findData('map'));self.assertEqual(child.result['conditional_base_gold'],{'minimum':1,'maximum':1});self.assertIsInstance(child,CurrentSettlementModesPanel);self.assertEqual(child.result['conditional_base_experience'],10);self.assertEqual(child.result['conditional_full_technology_experience'],13);self.assertIsNone(child.result['conditional_current_experience']);self.assertIsNone(child.result['actual_reward_total']);self.assertEqual(self.window.run.state,before);self.assertEqual(self.window.battle_preview.context,old);self.assertFalse(self.window.auto.isChecked())

if __name__=='__main__':unittest.main()
