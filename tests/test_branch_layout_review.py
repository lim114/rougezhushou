"""Readable category labels and narrow-window reflow without changing choices."""
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QStyleOptionComboBox, QStyle
import unittest
from rouge.branch_choice import BranchChoice


class BranchLayoutReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def panel(self, width=900):
        parent = QWidget()
        layout = QVBoxLayout(parent)
        combo = QComboBox()
        groups = [('宝箱与装置', [('箱型恶笼草 · 候选1' * 12, 'box', QIcon())]),
                  ('移动恶笼草', [('移动奖励', 'moving', QIcon())])]
        control = BranchChoice(combo, groups, overview_label='总览（本关奖励来源）', placeholder='请选择奖励目标')
        layout.addWidget(control)
        layout.addStretch()
        parent.resize(width, 200)
        parent.show()
        self.qt.processEvents()
        self.addCleanup(parent.close)
        return parent, control

    def readable_label(self, control):
        option = QStyleOptionComboBox()
        control.branch.initStyleOption(option)
        box = control.branch.style().subControlRect(QStyle.ComplexControl.CC_ComboBox, option,
                                                   QStyle.SubControl.SC_ComboBoxEditField, control.branch)
        icon_width = control.branch.iconSize().width() + 4 if not option.currentIcon.isNull() else 0
        self.assertGreaterEqual(box.width() - icon_width - 4, control.branch.fontMetrics().horizontalAdvance(control.branch.currentText()))

    def test_wide_category_text_is_fully_readable_next_to_target(self):
        parent, control = self.panel()
        self.readable_label(control)
        self.assertEqual(control.branch.y(), control.combo.y())
        self.assertEqual(control.branch.height(), control.combo.height())
        self.assertGreater(control.combo.width(), control.branch.width())

    def test_narrow_window_wraps_controls_instead_of_forcing_long_item_width(self):
        parent, control = self.panel()
        width = parent.minimumSizeHint().width()
        parent.resize(width, 200)
        self.qt.processEvents()
        self.assertLessEqual(parent.width(), width)
        self.readable_label(control)
        self.assertGreater(control.combo.y(), control.branch.geometry().bottom())
        self.assertTrue(control.rect().contains(control.branch.geometry()))
        self.assertTrue(control.rect().contains(control.combo.geometry()))

    def test_wide_narrow_wide_roundtrip_preserves_selection_and_does_not_emit(self):
        parent, control = self.panel()
        control.select_branch('移动恶笼草')
        control.select_value('moving')
        events = []
        control.combo.currentIndexChanged.connect(lambda _: events.append(control.combo.currentData()))
        for width in [350, 900, 350, 900]:
            parent.resize(width, 200)
            self.qt.processEvents()
            self.assertEqual(control.branch.currentData(), '移动恶笼草')
            self.assertEqual(control.combo.currentData(), 'moving')
        self.assertEqual(events, [])

    def test_larger_font_uses_current_metrics_and_still_shows_complete_category(self):
        parent, control = self.panel(460)
        font = QFont(parent.font())
        font.setPointSize(18)
        parent.setFont(font)
        self.qt.processEvents()
        self.readable_label(control)
        self.assertLessEqual(parent.width(), 460)
        self.assertGreater(control.combo.y(), control.branch.geometry().bottom())

    def test_refresh_after_reflow_preserves_branch_and_accurate_target(self):
        parent, control = self.panel(350)
        control.select_branch('宝箱与装置')
        control.select_value('box')
        control.set_groups(control.groups)
        self.qt.processEvents()
        self.assertEqual(control.branch.currentData(), '宝箱与装置')
        self.assertEqual(control.combo.currentData(), 'box')
        self.readable_label(control)

    def test_styled_category_keeps_its_icon_and_full_name_at_larger_font(self):
        parent, control = self.panel(460)
        label = '特殊分类名称（带图标）'
        control.branch_icons[label] = parent.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        control.set_groups([(label, [('准确条目', 'special', QIcon())])])
        control.select_branch(label)
        control.select_value('special')
        parent.setStyleSheet('QComboBox{padding:5px;border:1px solid #bbc6c1;border-radius:7px;}')
        font = QFont(parent.font())
        font.setPointSize(18)
        parent.setFont(font)
        self.qt.processEvents()
        self.assertFalse(control.branch.itemIcon(control.branch.currentIndex()).isNull())
        self.assertEqual(control.combo.currentData(), 'special')
        self.readable_label(control)

    def test_real_player_battle_reader_retains_reward_source_across_resizing(self):
        from rouge.player_map_reader import make_reader
        dialog = make_reader('battle', {'id': 'ro6_n_2_6', 'title': '公开固定作战'}, None)
        self.assertIsNotNone(dialog)
        self.addCleanup(dialog.close)
        panel = dialog.panel
        rewards = panel.rewards
        dialog.resize(920, 720)
        dialog.show()
        panel.tabs.setCurrentWidget(rewards)
        row = next(r for r in rewards.result['rows'] if r['source_action_keys'])
        rewards.choices.select_value(row['id'])
        rewards.source_combo.setCurrentIndex(1)
        before = rewards.combo.currentData(), rewards.source_combo.currentData()
        for width in [720, 1000]:
            dialog.resize(width, 720)
            self.qt.processEvents()
            self.readable_label(rewards.choices)
            self.assertEqual(rewards.choices.branch.height(), rewards.combo.height())
            self.assertEqual((rewards.combo.currentData(), rewards.source_combo.currentData()), before)
        self.assertTrue(panel.refresh_reference())
        self.assertEqual((rewards.combo.currentData(), rewards.source_combo.currentData()), before)
        self.assertTrue(rewards.follow_action())
        self.assertEqual(panel.action_key, before[1])


if __name__ == '__main__':
    unittest.main()
