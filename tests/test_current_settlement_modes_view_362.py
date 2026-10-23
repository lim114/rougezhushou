from unittest.mock import patch
import unittest
from PySide6.QtWidgets import QApplication
from rouge import current_settlement_modes_reference as model
from rouge.current_settlement_modes_view import CurrentSettlementModesPanel


class CurrentSettlementModesView362Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def panel(self, sid='ro6_n_1_2'):
        panel = CurrentSettlementModesPanel(sid)
        panel.resize(900, 380)
        panel.show()
        self.addCleanup(panel.close)
        self.app.processEvents()
        return panel

    def test_default_and_two_modes_visible_without_account_technology_assumption(self):
        panel = self.panel()
        self.assertIsNone(panel.result['conditional_base_experience'])
        panel.entry.setCurrentIndex(panel.entry.findData('map'))
        self.assertEqual(panel.result['conditional_base_experience'], 10)
        self.assertEqual(panel.result['conditional_full_technology_experience'], 13)
        self.assertIsNone(panel.result['actual_player_technology'])
        self.assertIn('基础指挥经验：10 点', panel.player.toPlainText())
        self.assertIn('满级生命游戏的经验参考：13 点', panel.player.toPlainText())
        self.assertNotIn('1013', panel.player.toPlainText())
        self.assertNotIn('is-fulltech', panel.player.toPlainText())

    def test_two_readers_nonzero_scroll_and_context_survive_same_source_refresh(self):
        panel = self.panel('ro6_t_16')
        panel.entry.setCurrentIndex(panel.entry.findData('event'))
        for reader in (panel.player, panel.technical):
            panel.tabs.setCurrentWidget(reader)
            self.app.processEvents()
            reader.verticalScrollBar().setValue(5)
            position = reader.verticalScrollBar().value()
            self.assertGreater(position, 0)
            index = panel.tabs.currentIndex()
            self.assertTrue(panel.refresh_reference())
            self.assertEqual(reader.verticalScrollBar().value(), position)
            self.assertEqual(panel.tabs.currentIndex(), index)
            self.assertEqual(panel.entry.currentData(), 'event')
            self.assertEqual(panel.result['conditional_base_experience'], 30)

    def test_crystal_entry_region_and_source_changes_do_not_keep_stale_totals(self):
        panel = self.panel('ro6_c_9')
        for entry, base in (('event', 30), ('pursuit', 0), ('unknown', None)):
            panel.entry.setCurrentIndex(panel.entry.findData(entry))
            self.assertEqual(panel.result['conditional_base_experience'], base)
        panel.entry.setCurrentIndex(panel.entry.findData('event'))
        panel.region.setCurrentIndex(panel.region.findData('side_path'))
        self.assertIsNone(panel.result['conditional_base_experience'])
        self.assertIsNone(panel.result['conditional_full_technology_experience'])
        with patch.object(model, 'packet', return_value=None):
            self.assertFalse(panel.refresh_reference())
            self.assertIsNone(panel.result)
            self.assertEqual(panel.technical.toPlainText(), '')
            self.assertNotIn('39', panel.player.toPlainText())
        self.assertTrue(panel.refresh_reference())
        self.assertIsNone(panel.result['conditional_base_experience'])


if __name__ == '__main__':
    unittest.main()
