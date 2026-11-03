import unittest
from unittest.mock import patch
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_battle_reference as model
from rouge.current_battle_view import CurrentBattlePanel


class CurrentEnemyTraitsView351Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def panel(self, sid='ro6_b_7'):
        panel = CurrentBattlePanel(sid)
        panel.resize(950, 510)
        panel.show()
        self.addCleanup(panel.close)
        self.app.processEvents()
        return panel

    def test_real_enemy_selection_shows_traits_in_existing_player_branch(self):
        panel = self.panel('ro6_b_2')
        self.assertIsNone(panel.enemy_combo.currentData())
        enemy = next(e for e in panel.result['enemies'] if e['id'] == 'enemy_2142_shsggd')
        panel.enemy_choices.select_value(enemy['key'])
        panel.tabs.setCurrentIndex(1)
        self.app.processEvents()
        text = panel.enemy_player.toPlainText()
        self.assertIn('行动与攻击方式', text)
        self.assertIn('仍可能有技能或特殊行为', text)
        self.assertIn('明确设有免疫', text)
        self.assertNotIn('stunImmune', text)

    def test_parent_refresh_preserves_nonzero_enemy_reading_and_chosen_identity(self):
        panel = self.panel()
        panel.tabs.setCurrentIndex(1)
        panel.enemy_choices.select_value(panel.result['enemies'][0]['key'])
        self.app.processEvents()
        reader = panel.enemy_player
        cursor = reader.textCursor()
        cursor.setPosition(3)
        cursor.setPosition(12, QTextCursor.MoveMode.KeepAnchor)
        reader.setTextCursor(cursor)
        self.assertGreater(reader.verticalScrollBar().maximum(), 0)
        reader.verticalScrollBar().setValue(3)
        expected = (panel.enemy_key, reader.textCursor().selectedText(), reader.verticalScrollBar().value(), panel.tabs.currentIndex())
        self.assertTrue(panel.refresh_reference())
        self.app.processEvents()
        self.assertEqual(expected, (panel.enemy_key, reader.textCursor().selectedText(), reader.verticalScrollBar().value(), panel.tabs.currentIndex()))

    def test_source_loss_clears_new_traits_and_recovery_requires_selection(self):
        panel = self.panel()
        panel.enemy_choices.select_value(panel.result['enemies'][0]['key'])
        with patch.object(model, 'packet', return_value=None):
            self.assertFalse(panel.refresh_reference())
            self.assertEqual(panel.enemy_player.toPlainText(), '')
            self.assertIsNone(panel.result)
        self.assertTrue(panel.refresh_reference())
        self.assertIsNone(panel.enemy_combo.currentData())
        self.assertEqual(panel.enemy_player.toPlainText(), '请选择敌人或关联实体。')


if __name__ == '__main__':
    unittest.main()
