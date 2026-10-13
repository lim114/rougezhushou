from copy import deepcopy
import json
import time
import unittest

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QApplication

from rouge.route_constraints_view import RouteConstraintsPanel, public_constraint_presets


class RouteConstraintsViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        self.panel = RouteConstraintsPanel(); self.panel.resize(1200, 850); self.panel.show(); self.qt.processEvents()

    def tearDown(self):
        self.panel.close(); self.panel.deleteLater(); self.qt.processEvents()

    def execute(self):
        self.panel.run_button.click(); end = time.monotonic() + 8
        while self.panel._workers and time.monotonic() < end:
            self.qt.processEvents(); time.sleep(.005)
        self.assertFalse(self.panel._workers)
        self.assertIsNotNone(self.panel.result_snapshot(), self.panel.status.text())

    def test_all_public_presets_use_chinese_results_and_preserve_editable_declarations(self):
        for preset in public_constraint_presets():
            self.panel.preset.setCurrentIndex(self.panel.preset.findData(preset['id'])); self.panel.load_example.click()
            before = self.panel.editor.toPlainText(); self.execute()
            result = self.panel.result_snapshot(); text = self.panel.result_view.toPlainText()
            self.assertEqual(before, self.panel.editor.toPlainText())
            self.assertIn('必经、避开与顺序路线规划', text)
            self.assertIn('实际终点可达性、完整收益、动态住民、失败概率与最优路线：未知', text)
            self.assertNotIn('declared_entry_qualification_unknown', text)
            self.assertNotIn('remaining_constraints_exceed_step_budget', text)
            if preset['id'] in ['required', 'ordered']:
                self.assertTrue(result['plans']); self.assertIn('移动方式：', text)
            elif preset['id'] == 'unknown':
                self.assertFalse(result['plans']); self.assertIn('准入条件未知', text)
                self.assertIn('此节点的入口资格尚未确认', text)
            elif preset['id'] == 'failed':
                self.assertFalse(result['plans']); self.assertIn('准入条件不符', text)
            else:
                self.assertFalse(result['plans']); self.assertIn('超出步数预算', text)

    def test_node_actions_build_ordered_and_qualification_declarations(self):
        self.panel.graph_node.setCurrentIndex(self.panel.graph_node.findData('c'))
        for field in ['required_nodes', 'checkpoints']:
            self.panel.node_action.setCurrentIndex(self.panel.node_action.findData(field)); self.panel.apply_node.click()
            self.assertIn('c', json.loads(self.panel.editor.toPlainText())[field])
        self.panel.node_action.setCurrentIndex(self.panel.node_action.findData('qualifications'))
        self.panel.qualification.setCurrentIndex(2); self.panel.qualification_reason.setText('入口尚未确认')
        self.panel.apply_node.click()
        payload = json.loads(self.panel.editor.toPlainText())
        self.assertEqual(payload['qualifications']['c'], {'matches': None, 'reason': '入口尚未确认'})
        self.panel.node_action.setCurrentIndex(self.panel.node_action.findData('goal')); self.panel.apply_node.click()
        self.assertEqual(json.loads(self.panel.editor.toPlainText())['goal'], 'c')
        self.assertFalse(self.panel.qualification.isVisible())

    def test_explicit_import_enables_guarded_node_links_and_refresh_invalidates_old_epoch(self):
        graph = public_constraint_presets()[0]['payload']['graph']
        self.panel.set_graph(graph, epoch=80); self.panel.import_graph.click(); self.execute()
        calls = []; self.panel.mapNodeSelected.connect(lambda node, binding: calls.append((node, binding)))
        self.panel.result_view.anchorClicked.emit(QUrl('rouge-map-node:b'))
        self.assertEqual(calls[0][0], 'b'); self.assertEqual(calls[0][1]['epoch'], 80)
        self.panel.set_graph(graph, epoch=81)
        self.panel.result_view.anchorClicked.emit(QUrl('rouge-map-node:b'))
        self.assertEqual(len(calls), 1); self.assertIn('链接已过期', self.panel.status.text())
        self.panel.import_graph.click(); self.execute()
        self.panel.result_view.anchorClicked.emit(QUrl('rouge-map-node:b'))
        self.assertEqual(calls[-1][1]['epoch'], 81)
        changed = deepcopy(graph); changed['nodes'][2]['row'] = 5
        self.panel.set_graph(changed, epoch=81)
        count = len(calls); self.panel.result_view.anchorClicked.emit(QUrl('rouge-map-node:b'))
        self.assertEqual(len(calls), count)

    def test_cache_refresh_preserves_editor_constraints_node_selection_results_and_scroll(self):
        self.panel.graph_node.setCurrentIndex(self.panel.graph_node.findData('g')); self.execute()
        self.panel.result_view.verticalScrollBar().setValue(self.panel.result_view.verticalScrollBar().maximum())
        before = (self.panel.editor.toPlainText(), deepcopy(self.panel.result_snapshot()), self.panel.graph_node.currentData(),
                  self.panel.result_view.toHtml(), self.panel.result_view.verticalScrollBar().value())
        graph = deepcopy(public_constraint_presets()[0]['payload']['graph']); graph['nodes'][0]['row'] = 5
        self.panel.set_graph(graph, epoch=90, historical=True); self.qt.processEvents()
        after = (self.panel.editor.toPlainText(), self.panel.result_snapshot(), self.panel.graph_node.currentData(),
                 self.panel.result_view.toHtml(), self.panel.result_view.verticalScrollBar().value())
        self.assertEqual(before, after)

    def test_invalid_declaration_preserves_old_result_and_does_not_create_map_links(self):
        self.execute(); before = self.panel.result_snapshot()
        payload = json.loads(self.panel.editor.toPlainText()); payload['avoid_nodes'] = ['s']
        self.panel.editor.setPlainText(json.dumps(payload, ensure_ascii=False)); self.panel.run_button.click()
        end = time.monotonic() + 8
        while self.panel._workers and time.monotonic() < end:
            self.qt.processEvents(); time.sleep(.005)
        self.assertIn('未生成新结果', self.panel.status.text())
        self.assertEqual(self.panel.result_snapshot(), before)
        self.assertFalse(self.panel._result_links)
        self.panel.editor.setPlainText('{ invalid')
        self.panel.run_button.click(); self.assertIn('未运行', self.panel.status.text())
        self.assertEqual(self.panel.result_snapshot(), before)

    def test_edits_after_or_during_calculation_mark_the_retained_result_as_prior_input(self):
        self.execute(); before = self.panel.result_snapshot()
        payload = json.loads(self.panel.editor.toPlainText()); payload['required_nodes'] = ['b', 'c']
        self.panel.editor.setPlainText(json.dumps(payload, ensure_ascii=False))
        self.assertIn('结果对应此前输入', self.panel.status.text())
        self.assertEqual(before, self.panel.result_snapshot())
        self.panel.run_button.click()
        payload['checkpoints'] = ['b', 'c']
        self.panel.editor.setPlainText(json.dumps(payload, ensure_ascii=False))
        self.assertIn('输入已修改', self.panel.status.text())
        end = time.monotonic() + 8
        while self.panel._workers and time.monotonic() < end:
            self.qt.processEvents(); time.sleep(.005)
        self.assertFalse(self.panel._workers)
        self.assertIn('结果对应此前输入', self.panel.status.text())
        self.assertEqual(self.panel.result_snapshot()['policy']['checkpoints'], [])
        self.assertEqual(json.loads(self.panel.editor.toPlainText())['checkpoints'], ['b', 'c'])


if __name__ == '__main__':
    unittest.main()
