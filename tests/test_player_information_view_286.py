"""Player-first information keeps the original references and reader state."""
from copy import deepcopy
import unittest

from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication

from rouge.node_catalog_view import NodeCatalogPanel
from rouge.battle_view import BattlePreviewPanel
from tests.test_node_map_navigation import graph


class PlayerInformationView286Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        self.panel = NodeCatalogPanel()
        self.panel.resize(1120, 800)
        self.panel.show()
        self.addCleanup(self.panel.close)
        self.qt.processEvents()

    def select(self, title):
        self.panel.list.setCurrentRow(next(i for i, e in enumerate(self.panel.entries)
                                          if e['title'] == title))
        self.qt.processEvents()

    def test_player_page_is_default_and_original_reference_stays_available(self):
        self.select('思乡心切')
        self.assertIs(self.panel.reading_tabs.currentWidget(), self.panel.player_detail)
        player = self.panel.player_detail.toPlainText()
        self.assertIn('思乡心切', player)
        self.assertIn('强行驱赶', player)
        self.assertNotIn('https://', player)
        self.assertNotIn('ro6_t_1', player)
        self.panel.reading_tabs.setCurrentWidget(self.panel.detail)
        self.assertIn('流程来源', self.panel.detail.toPlainText())
        self.assertTrue(self.panel.battle_button.isEnabled())

    def test_event_battle_button_opens_the_same_fixed_stage_from_player_page(self):
        battle = BattlePreviewPanel()
        self.addCleanup(battle.close)
        stages = []
        self.panel.stageSelected.connect(stages.append)
        self.panel.stageSelected.connect(battle.set_stage)
        self.select('思乡心切')
        self.assertIs(self.panel.reading_tabs.currentWidget(), self.panel.player_detail)
        self.panel.battle_button.click()
        self.qt.processEvents()
        self.assertEqual(stages, ['ro6_t_1'])
        self.assertEqual(battle.current_stage, 'ro6_t_1')
        self.assertGreater(len(battle.rows), 0)
        self.assertIn('不是开战倒计时', battle.summary.text())

    def test_refresh_preserves_selected_tab_and_both_text_reading_states(self):
        self.select('安眠一隅')
        for widget in (self.panel.player_detail, self.panel.detail):
            self.panel.reading_tabs.setCurrentWidget(widget)
            self.qt.processEvents()
            cursor = widget.textCursor()
            cursor.setPosition(3)
            cursor.setPosition(12, QTextCursor.MoveMode.KeepAnchor)
            widget.setTextCursor(cursor)
            bar = widget.verticalScrollBar()
            self.assertGreater(bar.maximum(), 0)
            bar.setValue(min(25, bar.maximum()))
            selected, scroll = widget.textCursor().selectedText(), bar.value()
            key = self.panel.detail_key
            self.panel.refresh()
            self.qt.processEvents()
            self.assertEqual(self.panel.detail_key, key)
            self.assertIs(self.panel.reading_tabs.currentWidget(), widget)
            self.assertEqual(widget.textCursor().selectedText(), selected)
            self.assertEqual(bar.value(), scroll)

    def test_map_current_and_previous_content_are_distinct_and_state_is_read_only(self):
        data = graph()
        original = deepcopy(data)
        self.panel.set_map_context(data, {'floor': 1}, epoch=7, historical=True)
        self.panel.show_map_nodes()
        self.panel.list.setCurrentRow(next(i for i, e in enumerate(self.panel.entries)
            if e['kind'] == 'map' and e['record']['id'] == 'b'))
        text = self.panel.player_detail.toPlainText()
        self.assertIn('林间空地', text)
        self.assertIn('呼吸的红苔', text)
        self.assertIn('过去', text)
        self.assertTrue(self.panel.map_jump.isEnabled())
        self.assertEqual(data, original)

    def test_unclassified_list_uses_readable_labels_but_keeps_stable_identity(self):
        entries = [e for e in self.panel.entries if e['kind'] == 'original']
        self.assertEqual(len(entries), 108)
        for entry in entries:
            self.assertNotIn(entry['record']['record']['record_id'], entry['title'])
            self.assertTrue(entry['key'].startswith('original:'))

    def test_bound_historical_map_does_not_borrow_today_resources_but_directory_does(self):
        data = graph()
        data['nodes'][0]['content'] = {'kind': 'event', 'title': '货从口出'}
        original = deepcopy(data)
        self.panel.set_map_context(data, {'floor': 1}, epoch=8, historical=True,
                                   runtime_context={'gold': 999})
        self.panel.set_node(data, 'a', floor=1)
        self.panel.bind_current_node()
        self.select('货从口出')
        historical = self.panel.player_detail.toPlainText()
        self.assertIn('历史节点的资料参考', historical)
        self.assertIn('能否付清这项费用：未知', historical)
        self.assertNotIn('已知资源够付这项费用', historical)
        self.assertEqual(data, original)
        self.panel.show_directory()
        self.select('货从口出')
        self.assertNotIn('历史节点的资料参考', self.panel.player_detail.toPlainText())
        self.assertIn('已知资源够付这项费用', self.panel.player_detail.toPlainText())

    def test_battle_mode_and_selected_enemy_survive_same_stage_refresh(self):
        battle = BattlePreviewPanel()
        self.addCleanup(battle.close)
        battle.set_stage('ro6_n_1_2')
        battle.spawn_list.setCurrentRow(1)
        before = deepcopy(battle.spawn_list.currentItem().data(Qt.ItemDataRole.UserRole))
        battle.technical.setChecked(True)
        battle.render_rows()
        self.assertTrue(battle.technical.isChecked())
        self.assertEqual(battle.spawn_list.currentItem().data(Qt.ItemDataRole.UserRole), before)
        self.assertIn('关卡标识', battle.spawn_detail.toPlainText())
        battle.technical.setChecked(False)
        self.assertNotIn('原始生成动作', battle.spawn_detail.toPlainText())
        self.assertIn('不是开战倒计时', battle.summary.text())


if __name__ == '__main__':
    unittest.main()
