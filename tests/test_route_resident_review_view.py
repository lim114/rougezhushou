from copy import deepcopy
import json
import time
import unittest

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QApplication

from rouge.route_resident_review_view import ResidentRouteReviewPanel, public_resident_review_presets


class ResidentRouteReviewViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.qt = QApplication.instance() or QApplication([])
    def setUp(self):
        self.panel = ResidentRouteReviewPanel(); self.panel.resize(1250, 900); self.panel.show(); self.qt.processEvents()
    def tearDown(self): self.panel.close(); self.panel.deleteLater(); self.qt.processEvents()
    def execute(self):
        self.panel.run_button.click(); end = time.monotonic() + 8
        while self.panel._workers and time.monotonic() < end:
            self.qt.processEvents(); time.sleep(.005)
        self.assertFalse(self.panel._workers); self.assertIsNotNone(self.panel.result_snapshot(), self.panel.status.text())

    def test_all_presets_keep_phases_unknowns_and_conditional_eviction_readable_in_chinese(self):
        for preset in public_resident_review_presets():
            self.panel.preset.setCurrentIndex(self.panel.preset.findData(preset['id'])); self.panel.load_example.click()
            before = self.panel.editor.toPlainText(); self.execute(); text = self.panel.result_view.toPlainText()
            self.assertEqual(before, self.panel.editor.toPlainText())
            self.assertIn('进入前：', text); self.assertIn('移动后（假设该次移动成功）', text)
            self.assertIn('实际安全、失败概率', text)
            self.assertNotIn('navigation_position_unknown', text)
            if preset['id'] == 'fallback': self.assertIn('未知继续保留', text)
            elif preset['id'] == 'victory': self.assertIn('独立声明据点获胜后', text)
            elif preset['id'] == 'zero': self.assertIn('居民尾链未评估', text)
            elif preset['id'] == 'conservative': self.assertEqual(self.panel.result_snapshot()['policy_excluded_route_ids'], ['a-route'])

    def test_victory_control_requires_exact_post_type_and_independent_declared_step(self):
        self.assertFalse(self.panel.declare_victory.isEnabled())
        preset = next(row for row in public_resident_review_presets() if row['id'] == 'victory')
        payload = deepcopy(preset['payload']); payload['resident_post_victories'] = {}
        self.panel.editor.setPlainText(json.dumps(payload, ensure_ascii=False)); self.qt.processEvents()
        self.assertTrue(self.panel.declare_victory.isEnabled()); self.panel.declare_victory.click()
        self.assertEqual(json.loads(self.panel.editor.toPlainText())['resident_post_victories'], {'post': [1]})
        self.execute(); self.assertEqual(self.panel.result_snapshot()['routes'][0]['conditional_post_eviction_steps'], [1])
        self.panel.step_select.setCurrentIndex(1); self.assertFalse(self.panel.declare_victory.isEnabled())

    def test_append_snapshot_respects_implicit_identity_and_three_resident_limit(self):
        payload = json.loads(self.panel.editor.toPlainText()); payload['residents'] = [{'node_id': 'r'}]
        self.panel.editor.setPlainText(json.dumps(payload, ensure_ascii=False))
        self.panel.graph_node.setCurrentIndex(self.panel.graph_node.findData('a')); self.panel.add_resident.click()
        residents = json.loads(self.panel.editor.toPlainText())['residents']
        self.assertEqual(residents[1], {'id': 'resident:2', 'node_id': 'a'})
        self.panel.add_resident.click(); before = self.panel.editor.toPlainText(); self.panel.add_resident.click()
        self.assertEqual(self.panel.editor.toPlainText(), before); self.assertIn('未追加', self.panel.status.text())
        self.execute(); self.assertEqual(len(self.panel.result_snapshot()['residents_snapshot_declaration']), 3)

    def test_map_import_and_epoch_layout_guard_use_existing_map_binding_contract(self):
        graph = public_resident_review_presets()[0]['payload']['graph']
        self.panel.set_graph(graph, epoch=220); self.panel.import_graph.click(); self.execute()
        calls = []; self.panel.mapNodeSelected.connect(lambda key, binding: calls.append((key, binding)))
        self.panel.result_view.anchorClicked.emit(QUrl('rouge-map-node:r'))
        self.assertEqual(calls[0][0], 'r'); self.assertEqual(calls[0][1]['epoch'], 220)
        self.panel.set_graph(graph, epoch=221); self.panel.result_view.anchorClicked.emit(QUrl('rouge-map-node:r'))
        self.assertEqual(len(calls), 1); self.assertIn('链接已过期', self.panel.status.text())
        self.panel.import_graph.click(); self.execute(); self.panel.result_view.anchorClicked.emit(QUrl('rouge-map-node:r'))
        self.assertEqual(calls[-1][1]['epoch'], 221)
        changed = deepcopy(graph); changed['nodes'][4]['col'] = 8; self.panel.set_graph(changed, epoch=221)
        count = len(calls); self.panel.result_view.anchorClicked.emit(QUrl('rouge-map-node:r')); self.assertEqual(len(calls), count)

    def test_cache_refresh_preserves_routes_snapshot_selection_result_and_scroll(self):
        self.panel.graph_node.setCurrentIndex(self.panel.graph_node.findData('p')); self.panel.route_select.setCurrentIndex(1)
        self.execute(); self.panel.result_view.verticalScrollBar().setValue(self.panel.result_view.verticalScrollBar().maximum())
        before = (self.panel.editor.toPlainText(), self.panel.result_snapshot(), self.panel.graph_node.currentData(), self.panel.route_select.currentData(),
                  self.panel.result_view.toHtml(), self.panel.result_view.verticalScrollBar().value())
        self.panel.set_graph(public_resident_review_presets()[0]['payload']['graph'], epoch=240, historical=True); self.qt.processEvents()
        after = (self.panel.editor.toPlainText(), self.panel.result_snapshot(), self.panel.graph_node.currentData(), self.panel.route_select.currentData(),
                 self.panel.result_view.toHtml(), self.panel.result_view.verticalScrollBar().value())
        self.assertEqual(before, after)

    def test_edits_and_invalid_input_preserve_exact_prior_computed_snapshot_with_warning(self):
        self.execute(); before = self.panel.result_snapshot(); payload = json.loads(self.panel.editor.toPlainText())
        payload['risk_policy'] = 'avoid_candidate_overlap'; self.panel.editor.setPlainText(json.dumps(payload, ensure_ascii=False))
        self.assertIn('结果对应此前输入', self.panel.status.text()); self.assertEqual(self.panel.result_snapshot(), before)
        self.panel.run_button.click(); payload['action_points'] = 1; self.panel.editor.setPlainText(json.dumps(payload, ensure_ascii=False))
        end = time.monotonic() + 8
        while self.panel._workers and time.monotonic() < end: self.qt.processEvents(); time.sleep(.005)
        self.assertIn('结果对应此前输入', self.panel.status.text())
        current = self.panel.result_snapshot(); self.assertIsNone(current['routes'][0]['movement_stop_step'])
        self.panel.editor.setPlainText('{ invalid'); self.panel.run_button.click()
        self.assertIn('未运行', self.panel.status.text()); self.assertEqual(self.panel.result_snapshot(), current)


if __name__ == '__main__': unittest.main()
