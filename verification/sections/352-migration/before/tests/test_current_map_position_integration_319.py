from copy import deepcopy
from tests import test_batch185_mainwindow as setup_module
from PySide6.QtCore import Qt
import unittest

class CurrentMapPositionIntegration319Tests(unittest.TestCase):
    setUpClass=classmethod(setup_module.Batch185WindowTests.setUpClass.__func__)
    setUp=setup_module.Batch185WindowTests.setUp
    def test_MainWindow_current_stage_position_dialog_is_read_only_and_source_exact(self):
        p=self.window.expansion_update;before=deepcopy(self.window.run.state);old=deepcopy(self.window.battle_preview.context);p.scope.setCurrentIndex(p.scope.findData(False));i=next(i for i in range(p.entries.count())if p.entries.item(i).data(Qt.ItemDataRole.UserRole)=='ro6_n_3_2_dlc1');p.entries.setCurrentRow(i);self.assertTrue(p.open_current_battle());d=p.current_battle_dialog;self.addCleanup(d.close);self.assertTrue(d.panel.open_map_positions());child=d.panel.position_dialog.panel;child.combo.setCurrentIndex(1);self.assertEqual(child.result['stage_id'],'ro6_n_3_2_dlc1');self.assertTrue(child.result['points']);self.assertEqual(child.image_raw,__import__('rouge.current_map_position',fromlist=['battle']).battle.version.image_bytes(child.result['image']));self.assertEqual(self.window.run.state,before);self.assertEqual(self.window.battle_preview.context,old);self.assertFalse(self.window.auto.isChecked())

if __name__=='__main__':unittest.main()
