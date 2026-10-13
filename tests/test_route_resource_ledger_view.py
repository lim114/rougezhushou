from copy import deepcopy
import json
import time
import unittest
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QApplication
from rouge.route_resource_ledger_view import RouteResourceLedgerPanel, public_resource_presets


class RouteResourceLedgerViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.qt = QApplication.instance() or QApplication([])
    def setUp(self):
        self.p = RouteResourceLedgerPanel(); self.p.resize(1280, 950); self.p.show(); self.qt.processEvents()
    def tearDown(self): self.p.close(); self.p.deleteLater(); self.qt.processEvents()
    def execute(self):
        self.p.run_button.click(); end = time.monotonic() + 8
        while self.p._workers and time.monotonic() < end: self.qt.processEvents(); time.sleep(.005)
        self.assertFalse(self.p._workers); self.assertIsNotNone(self.p.result_snapshot(), self.p.status.text())

    def test_all_presets_show_source_quantities_unknowns_and_exit_phases_in_chinese(self):
        for preset in public_resource_presets():
            self.p.preset.setCurrentIndex(self.p.preset.findData(preset['id'])); self.p.load_example.click()
            before = self.p.editor.toPlainText(); self.execute(); text = self.p.result_view.toPlainText()
            self.assertEqual(before, self.p.editor.toPlainText()); self.assertIn('路线资源授予与出口账本', text)
            self.assertIn('实际最优、最终资源和完整收益：未知', text)
            self.assertNotIn('passive_activation_not_declared', text)
            if preset['id'] == 'grants': self.assertIn('希望授予 7', text); self.assertIn('重弹簧 [spring]', text)
            elif preset['id'] == 'unknown': self.assertIn('概念体激活未独立声明', text)
            elif preset['id'] == 'portal': self.assertIn('秘境例外条件保留：重弹簧', text)
            elif preset['id'] == 'battle': self.assertIn('随机收藏品数量 1', text)
            elif preset['id'] == 'zero': self.assertIn('移动依赖链未闭合', text)

    def test_phase_controls_update_independent_activation_battle_and_terminal_declarations(self):
        self.p.passive_select.setCurrentIndex(self.p.passive_select.findData('rogue_6_scrap_P_03'))
        self.p.phase_match.setCurrentIndex(1); self.p.set_activation.click()
        payload = json.loads(self.p.editor.toPlainText()); self.assertFalse(payload['activation_declarations']['grants']['1']['rogue_6_scrap_P_03'])
        self.p.phase_match.setCurrentIndex(0); self.p.set_after_battle.click()
        self.assertTrue(json.loads(self.p.editor.toPlainText())['after_battle_declarations']['grants']['1'])
        self.p.transition_select.setCurrentIndex(self.p.transition_select.findData('portal_return')); self.p.set_terminal.click()
        self.assertEqual(json.loads(self.p.editor.toPlainText())['terminals']['grants'], {'transition': 'portal_return', 'success_declared': True})
        self.assertFalse(self.p.add_resident.isVisible()); self.assertFalse(self.p.declare_victory.isVisible())

    def test_map_epoch_guard_refresh_retention_and_stale_input_snapshot_are_reused(self):
        graph = public_resource_presets()[0]['payload']['graph']; self.p.set_graph(graph, epoch=330); self.p.import_graph.click(); self.execute()
        calls = []; self.p.mapNodeSelected.connect(lambda key, binding: calls.append((key, binding)))
        self.p.result_view.anchorClicked.emit(QUrl('rouge-map-node:a')); self.assertEqual(calls[0][1]['epoch'], 330)
        self.p.graph_node.setCurrentIndex(self.p.graph_node.findData('g')); self.p.result_view.verticalScrollBar().setValue(self.p.result_view.verticalScrollBar().maximum())
        before = (self.p.editor.toPlainText(), self.p.result_snapshot(), self.p.graph_node.currentData(), self.p.result_view.toHtml(), self.p.result_view.verticalScrollBar().value())
        self.p.set_graph(graph, epoch=331); self.qt.processEvents()
        after = (self.p.editor.toPlainText(), self.p.result_snapshot(), self.p.graph_node.currentData(), self.p.result_view.toHtml(), self.p.result_view.verticalScrollBar().value())
        self.assertEqual(before, after); self.p.result_view.anchorClicked.emit(QUrl('rouge-map-node:a')); self.assertEqual(len(calls), 1)
        payload = json.loads(self.p.editor.toPlainText()); payload['action_points'] = 9; self.p.editor.setPlainText(json.dumps(payload, ensure_ascii=False))
        self.assertIn('结果对应此前输入', self.p.status.text()); self.assertEqual(self.p.result_snapshot(), before[1])
        self.p.run_button.click(); payload['action_points'] = 10; self.p.editor.setPlainText(json.dumps(payload, ensure_ascii=False))
        end = time.monotonic() + 8
        while self.p._workers and time.monotonic() < end: self.qt.processEvents(); time.sleep(.005)
        self.assertIn('结果对应此前输入', self.p.status.text())
        self.assertEqual(self.p.result_snapshot()['routes'][0]['known_source_grant_subtotal']['hope'], 8)

    def test_invalid_new_declaration_preserves_old_result(self):
        self.execute(); before = deepcopy(self.p.result_snapshot()); payload = json.loads(self.p.editor.toPlainText())
        payload['terminals']['grants']['exit_node_type'] = 'BATTLE_BOSS'; self.p.editor.setPlainText(json.dumps(payload, ensure_ascii=False)); self.p.run_button.click()
        end = time.monotonic() + 8
        while self.p._workers and time.monotonic() < end: self.qt.processEvents(); time.sleep(.005)
        self.assertIn('未生成新结果', self.p.status.text()); self.assertEqual(self.p.result_snapshot(), before)


if __name__ == '__main__': unittest.main()
