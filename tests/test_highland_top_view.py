"""Actual highland dialog controls preserve source identity and unknown cells."""
import copy
import unittest

from PySide6.QtWidgets import QApplication
from rouge.battle_preview import DATA, battle_data
from rouge.fixed_landmark_mapping import landmark_data
from rouge.highland_top_mapping import highland_top_data
from rouge.highland_top_view import HighlandTopDialog


class HighlandTopViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.dialog = HighlandTopDialog(); self.dialog.show(); self.app.processEvents()

    def tearDown(self):
        self.dialog.close(); self.dialog.deleteLater(); self.app.processEvents()

    def select(self, cell):
        combo = self.dialog.panel.cell_combo
        index = next(i for i in range(combo.count()) if combo.itemData(i) == cell)
        combo.setCurrentIndex(index); self.app.processEvents()

    def test_complete_normal_emergency_highland_selection_unknown_and_refresh_flow(self):
        panel = self.dialog.panel; old_ground = copy.deepcopy(landmark_data())
        self.assertEqual(panel.stage_combo.count(), 2)
        self.assertEqual(panel.cell_combo.count(), 10)
        self.select({'row': 1, 'col': 3})
        self.assertEqual(panel.canvas.reference.top_center(panel.canvas.selected_cell), (185, 65))
        self.assertIn('菱形表面参考', panel.status.text())
        self.select({'row': 3, 'col': 3})
        self.assertIsNone(panel.canvas.reference.top_center(panel.canvas.selected_cell))
        self.assertIn('位置未知', panel.status.text())
        self.dialog.set_stage('ro6_n_4_1'); self.app.processEvents()
        self.assertEqual(panel.canvas.selected_cell, {'row': 3, 'col': 3})
        panel.stage_combo.setCurrentIndex(panel.stage_combo.findData('ro6_e_4_1')); self.app.processEvents()
        self.assertEqual(panel.stage['id'], 'ro6_e_4_1')
        self.assertEqual(panel.canvas.selected_cell, {'row': 3, 'col': 3})
        self.assertIsNone(panel.canvas.reference.top_center(panel.canvas.selected_cell))
        self.select({'row': 2, 'col': 8})
        self.assertEqual(panel.canvas.reference.top_center(panel.canvas.selected_cell), (367, 93))
        self.dialog.set_stage('ro6_e_4_1'); self.app.processEvents()
        self.assertEqual(panel.canvas.selected_cell, {'row': 2, 'col': 8})
        self.assertEqual(landmark_data(), old_ground)

    def test_unmapped_real_wooden_variant_keeps_all_cells_unknown_without_using_lowland_points(self):
        panel = self.dialog.panel
        for sid in ('ro6_n_2_4', 'ro6_e_2_4'):
            self.dialog.set_stage(sid); self.app.processEvents()
            self.assertEqual(panel.cell_combo.count(), 8)
            self.assertIsNone(panel.canvas.reference)
            for index in range(panel.cell_combo.count()):
                panel.cell_combo.setCurrentIndex(index); self.app.processEvents()
                self.assertIn('表面位置未知', panel.cell_combo.currentText())
                self.assertIn('位置未知', panel.status.text())
            selected = copy.deepcopy(panel.canvas.selected_cell)
            self.dialog.set_stage(sid); self.app.processEvents()
            self.assertEqual(panel.canvas.selected_cell, selected)

    def test_source_center_survives_three_ratios_and_mismatched_file_clears_reference(self):
        panel = self.dialog.panel; self.select({'row': 2, 'col': 3})
        for width, height in ((1050, 720), (680, 900), (1300, 480)):
            self.dialog.resize(width, height); self.app.processEvents()
            self.assertFalse(self.dialog.grab().isNull())
            self.assertEqual(panel.canvas.reference.top_center(panel.canvas.selected_cell), (184, 93))
        stage = battle_data()['stages']['ro6_n_4_1']
        panel.canvas.set_source(stage, DATA / 'battle-maps/ro6_n_2_4.png', highland_top_data())
        self.assertIsNone(panel.canvas.reference)
        self.assertIn('未直接核对', panel.canvas.caption())
        self.assertFalse(self.dialog.grab().isNull())


if __name__ == '__main__':
    unittest.main()


class HighlandTopEntryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])
    def test_actual_battle_entry_retains_unknown_cell_and_separate_lowland_data(self):
        from rouge.battle_view import BattlePreviewPanel
        before=copy.deepcopy(landmark_data())
        panel=BattlePreviewPanel();panel.show();panel.set_stage('ro6_n_4_1')
        self.assertTrue(panel.highland_top_button.isEnabled());panel.highland_top_button.click()
        dialog=panel.highland_top_dialog;combo=dialog.panel.cell_combo
        index=next(i for i in range(combo.count()) if combo.itemData(i)=={'row':3,'col':3})
        combo.setCurrentIndex(index);self.app.processEvents()
        self.assertIsNone(dialog.panel.canvas.reference.top_center(combo.currentData()))
        dialog.close();panel.highland_top_button.click();self.app.processEvents()
        self.assertEqual(combo.currentData(),{'row':3,'col':3})
        self.assertEqual(landmark_data(),before)
        panel.close();dialog.close();panel.deleteLater();self.app.processEvents()
