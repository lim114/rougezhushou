from copy import deepcopy
import json
import time
import unittest
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QApplication
from rouge.route_continuation_view import RouteContinuationPanel, public_continuation_presets


class RouteContinuationViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.qt = QApplication.instance() or QApplication([])
    def setUp(self):
        self.p = RouteContinuationPanel(); self.p.resize(1300, 970); self.p.show(); self.qt.processEvents()
    def tearDown(self): self.p.close(); self.p.deleteLater(); self.qt.processEvents()
    def execute(self):
        self.p.run_button.click(); end = time.monotonic() + 8
        while self.p._workers and time.monotonic() < end: self.qt.processEvents(); time.sleep(.005)
        self.assertFalse(self.p._workers); self.assertIsNotNone(self.p.result_snapshot(), self.p.status.text())

    def test_all_presets_show_differences_progress_scope_and_unknowns_in_chinese(self):
        for preset in public_continuation_presets():
            self.p.preset.setCurrentIndex(self.p.preset.findData(preset['id'])); self.p.load_example.click(); before = self.p.editor.toPlainText()
            self.execute(); text = self.p.result_view.toPlainText(); self.assertEqual(self.p.editor.toPlainText(), before)
            self.assertIn('路线续接与变化诊断', text); self.assertIn('实际目标完成、收益和最优路线：未知', text)
            self.assertNotIn('planned_walking_edge_removed', text)
            if preset['id'] == 'fresh': self.assertIn('差值：-1', text)
            elif preset['id'] == 'edge': self.assertIn('这一条步行连线', text)
            elif preset['id'] == 'missing': self.assertIn('缺少计划加工品实例', text)
            elif preset['id'] == 'failed': self.assertIn('失败后继续资格未知', text)
            elif preset['id'] == 'unknown': self.assertIn('移动完成未知', text)
            elif preset['id'] == 'scope': self.assertIn('独立新图目标与完整人工要求', text)

    def test_progress_controls_never_update_fresh_ap_stock_completion_or_current_position(self):
        payload = json.loads(self.p.editor.toPlainText()); payload['progress'] = []; self.p.editor.setPlainText(json.dumps(payload, ensure_ascii=False))
        original = deepcopy(payload['after']); self.p.step_select.setCurrentIndex(1); self.p.move_match.setCurrentIndex(0); self.p.battle_result.setCurrentIndex(1)
        self.p.set_progress.click(); after = json.loads(self.p.editor.toPlainText())
        self.assertEqual(after['after'], original)
        self.assertIsNone(after['progress'][0]['movement_completed_declared'])
        self.assertTrue(after['progress'][1]['movement_completed_declared']); self.assertEqual(after['progress'][1]['battle_result_declared'], 'won')
        self.p.graph_node.setCurrentIndex(self.p.graph_node.findData('g')); self.p.set_current_after.click()
        current = json.loads(self.p.editor.toPlainText()); self.assertEqual(current['after']['graph']['current_node'], 'g')
        self.assertEqual(current['after']['action_points'], original['action_points']); self.assertEqual(current['after']['inventory'], original['inventory'])

    def test_failure_continue_control_is_independent_and_result_can_be_recomputed(self):
        self.p.preset.setCurrentIndex(self.p.preset.findData('failed')); self.p.load_example.click(); self.execute()
        self.assertIsNone(self.p.result_snapshot()['alternatives'])
        self.p.failure_match.setCurrentIndex(1); self.p.set_failure.click(); self.execute()
        self.assertTrue(self.p.result_snapshot()['alternatives']['plans'])

    def test_after_graph_import_preserves_before_progress_and_resources_and_epoch_links_expire(self):
        payload = json.loads(self.p.editor.toPlainText()); graph = payload['after']['graph']
        self.p.set_graph(graph, epoch=600); self.p.import_graph.click(); imported = json.loads(self.p.editor.toPlainText())
        self.assertEqual(imported['before'], payload['before']); self.assertEqual(imported['progress'], payload['progress'])
        self.assertEqual(imported['after']['action_points'], payload['after']['action_points']); self.execute()
        calls = []; self.p.mapNodeSelected.connect(lambda key, binding: calls.append((key, binding)))
        self.p.result_view.anchorClicked.emit(QUrl('rouge-map-node:a')); self.assertEqual(calls[0][1]['epoch'], 600)
        before = (self.p.editor.toPlainText(), self.p.result_snapshot(), self.p.graph_node.currentData(), self.p.result_view.toHtml())
        self.p.set_graph(graph, epoch=601); self.qt.processEvents()
        self.assertEqual(before, (self.p.editor.toPlainText(), self.p.result_snapshot(), self.p.graph_node.currentData(), self.p.result_view.toHtml()))
        self.p.result_view.anchorClicked.emit(QUrl('rouge-map-node:a')); self.assertEqual(len(calls), 1); self.assertIn('链接已过期', self.p.status.text())

    def test_edits_during_worker_and_invalid_input_retain_exact_prior_result_with_warning(self):
        self.execute(); payload = json.loads(self.p.editor.toPlainText()); payload['after']['action_points'] = 5
        self.p.editor.setPlainText(json.dumps(payload, ensure_ascii=False)); self.assertIn('结果对应此前输入', self.p.status.text())
        self.p.run_button.click(); payload['after']['action_points'] = 6; self.p.editor.setPlainText(json.dumps(payload, ensure_ascii=False))
        end = time.monotonic() + 8
        while self.p._workers and time.monotonic() < end: self.qt.processEvents(); time.sleep(.005)
        self.assertIn('结果对应此前输入', self.p.status.text()); before = self.p.result_snapshot()
        self.assertEqual(before['after_snapshot']['action_points'], 5)
        self.p.editor.setPlainText('{ invalid'); self.p.run_button.click(); self.assertIn('未运行', self.p.status.text()); self.assertEqual(before, self.p.result_snapshot())


if __name__ == '__main__': unittest.main()
