"""Fixed-map fit, one coherent refresh, and unchanged reward/source semantics."""
import unittest
from unittest.mock import patch
from PySide6.QtCore import QByteArray, QBuffer, QIODevice, Qt
from PySide6.QtGui import QImage, QColor, QPainter
from PySide6.QtWidgets import QApplication
from rouge.reference_image import ReferenceImage
from rouge.current_battle_view import CurrentBattlePanel


def image_bytes():
    image = QImage(1200, 400, QImage.Format.Format_RGB32)
    image.fill(QColor('red'))
    painter = QPainter(image)
    painter.fillRect(600, 0, 600, 400, QColor('blue'))
    painter.end()
    data = QByteArray(); buffer = QBuffer(data)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    assert image.save(buffer, 'PNG')
    return bytes(data)


class CountingBattle(CurrentBattlePanel):
    def __init__(self, *args, **kwargs):
        self.rebuilds = 0
        super().__init__(*args, **kwargs)

    def _actions_changed(self, *args, **kwargs):
        self.rebuilds += 1
        return super()._actions_changed(*args, **kwargs)


class ReaderReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def panel(self):
        panel = CountingBattle('ro6_b_7')
        self.addCleanup(panel.close)
        return panel

    def test_full_map_edges_and_aspect_survive_narrow_then_wide_resize(self):
        label = ReferenceImage(); self.addCleanup(label.close)
        label.set_data(image_bytes(), '未取得原图'); label.show()
        original = label.original.cacheKey()
        for width, height in ((90, 100), (700, 180), (160, 300), (1200, 400)):
            label.resize(width, height); self.qt.processEvents()
            pix = label.pixmap()
            self.assertFalse(pix.isNull())
            self.assertLessEqual(pix.width(), label.contentsRect().width())
            self.assertLessEqual(pix.height(), label.contentsRect().height())
            self.assertAlmostEqual(pix.width()/pix.height(), 3, delta=.06)
            image = pix.toImage()
            self.assertEqual(image.pixelColor(0, image.height()//2), QColor('red'))
            self.assertEqual(image.pixelColor(image.width()-1, image.height()//2), QColor('blue'))
            self.assertEqual(label.original.cacheKey(), original)

    def test_source_loss_or_invalid_image_does_not_return_after_resize(self):
        label = ReferenceImage(); self.addCleanup(label.close); label.show()
        for raw in (None, b'not a PNG'):
            label.set_data(image_bytes(), '未取得原图')
            self.assertFalse(label.set_data(raw, '本图无法核对'))
            label.resize(label.width()+20, 180); self.qt.processEvents()
            self.assertTrue(label.pixmap() is None or label.pixmap().isNull())
            self.assertEqual(label.text(), '本图无法核对')
        label.set_data(image_bytes(), '未取得原图'); label.clear(); label.resize(400, 200)
        self.qt.processEvents(); self.assertTrue(label.pixmap() is None or label.pixmap().isNull())

    def test_children_read_once_and_match_standalone_complete_results(self):
        from rouge import current_reward_reference as rewards, current_settlement_modes_reference as settlement
        from rouge.current_reward_view import CurrentRewardPanel
        from rouge.current_settlement_modes_view import CurrentSettlementModesPanel
        with patch.object(rewards, 'stage_rewards', wraps=rewards.stage_rewards) as r, \
             patch.object(settlement, 'stage_reference', wraps=settlement.stage_reference) as s:
            panel = self.panel()
            self.assertEqual((r.call_count, s.call_count), (1, 1))
        for cls, child in ((CurrentRewardPanel, panel.rewards), (CurrentSettlementModesPanel, panel.settlement)):
            standalone = cls(panel.stage_id); self.addCleanup(standalone.close)
            self.assertEqual(child.result, standalone.result)
            self.assertEqual(child.player.toPlainText(), standalone.player.toPlainText())
            self.assertEqual(child.technical.toPlainText(), standalone.technical.toPlainText())

    def test_focus_across_queue_types_rebuilds_once_and_selects_exact_action(self):
        panel = self.panel()
        target = next(a for a in panel.result['actions'] if a['queue']['kind'] == 'branch')
        panel.queue_kind.setCurrentIndex(panel.queue_kind.findData('main'))
        panel.rebuilds = 0
        self.assertTrue(panel.focus_action(target))
        self.assertEqual(panel.rebuilds, 1)
        self.assertEqual(panel.action_key, target['key'])
        self.assertEqual(panel.queue_kind.currentData(), 'branch')
        self.assertEqual(panel.tabs.currentIndex(), 2)

    def test_filtered_refresh_rebuilds_once_without_resetting_action_or_enemy(self):
        panel = self.panel(); enemy = panel.result['enemies'][0]
        panel.enemy_choices.select_value(enemy['key'])
        panel.action_focus.setCurrentIndex(panel.action_focus.findData('enemy'))
        panel.actions.setCurrentRow(0); selected = panel.action_key
        panel.rebuilds = 0
        self.assertTrue(panel.refresh_reference())
        self.assertEqual(panel.rebuilds, 1)
        self.assertEqual(panel.enemy_key, enemy['key'])
        self.assertEqual(panel.action_key, selected)
        self.assertEqual(panel.action_focus.currentData(), 'enemy')

    def test_panel_and_dialog_close_clear_their_owned_reader_results(self):
        from rouge.current_battle_view import CurrentBattleDialog
        for cls in (CurrentBattlePanel, CurrentBattleDialog):
            owner = cls('ro6_n_1_2'); self.addCleanup(owner.close)
            panel = owner.panel if cls is CurrentBattleDialog else owner
            owner.show(); self.qt.processEvents()
            self.assertTrue(panel.open_stage_objects())
            child = panel.stage_objects_dialog
            self.assertIsNotNone(child.panel.result)
            owner.close(); self.qt.processEvents()
            self.assertFalse(child.isVisible())
            self.assertIsNone(child.panel.result)


if __name__ == '__main__':
    unittest.main()
