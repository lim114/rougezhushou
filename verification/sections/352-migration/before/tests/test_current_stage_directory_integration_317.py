from copy import deepcopy
from tests import test_batch185_mainwindow as setup_module
import unittest

class CurrentStageDirectoryIntegration317Tests(unittest.TestCase):
    setUpClass=classmethod(setup_module.Batch185WindowTests.setUpClass.__func__)
    setUp=setup_module.Batch185WindowTests.setUp
    def test_MainWindow_filters_preview_and_sources_preserve_run_and_legacy_calculation(self):
        p=self.window.expansion_update;before=deepcopy(self.window.run.state);context=deepcopy(self.window.battle_preview.context);self.window.centralWidget().setCurrentWidget(p);p.scope.setCurrentIndex(p.scope.findData(False));p.stage_floor.setCurrentIndex(p.stage_floor.findData('floor6'));p.stage_kind.setCurrentIndex(p.stage_kind.findData('boss'))
        for sid in ('ro6_b_7','ro6_b_7_b'):
            from PySide6.QtCore import Qt
            i=next(i for i in range(p.entries.count())if p.entries.item(i).data(Qt.ItemDataRole.UserRole)==sid);p.entries.setCurrentRow(i);self.assertTrue(p.open_current_battle());self.assertEqual(p.current_battle_dialog.panel.stage_id,sid);self.assertFalse(p.current_battle_dialog.panel.map_image.pixmap().isNull());p.current_battle_dialog.close()
        self.assertEqual(self.window.run.state,before);self.assertEqual(self.window.battle_preview.context,context);self.assertFalse(self.window.auto.isChecked())

if __name__=='__main__':unittest.main()
