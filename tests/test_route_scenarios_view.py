from copy import deepcopy
import json
import time
import unittest

from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QApplication

from rouge.route_scenarios_view import RouteScenarioMatrixPanel, public_scenario_presets


class RouteScenarioMatrixViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        self.p = RouteScenarioMatrixPanel(); self.p.resize(1280, 1000); self.p.show(); self.qt.processEvents()

    def tearDown(self): self.p.close(); self.p.deleteLater(); self.qt.processEvents()

    def complete(self):
        end = time.monotonic() + 12
        while self.p._workers and time.monotonic() < end: self.qt.processEvents(); time.sleep(.005)
        self.assertFalse(self.p._workers)

    def execute(self):
        self.p.run_button.click(); self.complete(); self.assertIsNotNone(self.p.result_snapshot(), self.p.status.text())

    def test_all_public_presets_display_cases_inputs_source_quantities_and_unknown_envelopes(self):
        for preset in public_scenario_presets():
            with self.subTest(preset=preset['id']):
                self.p.preset.setCurrentIndex(self.p.preset.findData(preset['id'])); self.p.load_example.click()
                before = self.p.editor.toPlainText(); self.execute(); text = self.p.result_view.toPlainText()
                self.assertEqual(before, self.p.editor.toPlainText()); self.assertIn('有限声明情景的路线矩阵', text)
                self.assertIn('实际最优路线、完整收益和情景概率：未知', text); self.assertIn('希望授予', text)
                self.assertIn('路线资源授予与出口账本', text); self.assertIn('结论变化见证', text)
                self.assertNotIn('compound_case_quantities_not_closed', text); self.assertNotIn('changed_fields', text)
                self.assertEqual(len(self.p.result_snapshot()['cases']), len(preset['payload']['scenarios']))
                if preset['id'] == 'compound':
                    self.assertIn('库存与概念体快照未知', text); self.assertIn('未知（不是空列表）', text)
                    self.assertIn('明确库存缺少计划实例', text); self.assertIn('触须余次数0', text)
                    self.assertIn('仅到缺实例之前的2步已知前缀，不是完整路线', text)
                    partial = next(row for row in self.p.result_snapshot()['cases'] if row['scenario_id'] == 'missing-tail')['routes'][0]
                    self.assertTrue(partial['resource_reference']['prefix_only']); self.assertFalse(partial['quantity_conditions_closed'])
                    self.assertTrue(all(row['closed_quantity_envelope'] is None for row in self.p.result_snapshot()['route_summaries']))
                elif preset['id'] == 'closed':
                    self.assertTrue(all(row['closed_quantity_envelope'] is not None for row in self.p.result_snapshot()['route_summaries']))
                else: self.assertIsNone(self.p.result_snapshot()['route_summaries'][0]['closed_quantity_envelope'])

    def test_selected_scenario_controls_keep_other_cases_and_unknown_distinct_from_empty(self):
        before = json.loads(self.p.editor.toPlainText()); self.p.scenario_select.setCurrentIndex(self.p.scenario_select.findData('ap2'))
        self.p.scenario_ap.setText('未知'); self.p.set_scenario_ap.click(); after = json.loads(self.p.editor.toPlainText())
        self.assertIsNone(after['scenarios'][1]['action_points']); self.assertEqual(before['scenarios'][0], after['scenarios'][0])
        self.p.snapshot_item.setCurrentIndex(self.p.snapshot_item.findData('gold')); self.p.snapshot_uses.setText('0'); self.p.set_snapshot_uses.click()
        after = json.loads(self.p.editor.toPlainText()); self.assertEqual(after['scenarios'][1]['inventory'][0]['remaining_uses'], 0)
        self.assertEqual(after['scenarios'][0], before['scenarios'][0])
        self.p.snapshot_uses.setText('3'); old = self.p.editor.toPlainText(); self.p.set_snapshot_uses.click()
        self.assertEqual(old, self.p.editor.toPlainText()); self.assertIn('超过', self.p.status.text())
        self.p.scenario_select.setCurrentIndex(self.p.scenario_select.findData('unknown-snapshots'))
        self.assertFalse(self.p.set_snapshot_uses.isEnabled()); self.assertIn('未知', self.p.snapshot_item.currentText())
        payload = json.loads(self.p.editor.toPlainText()); payload['scenarios'][4]['inventory'] = []; self.p._write(payload)
        self.assertEqual(self.p.scenario_select.currentData(), 'unknown-snapshots'); self.assertIn('明确空', self.p.snapshot_item.currentText())
        self.assertEqual(json.loads(self.p.editor.toPlainText())['scenarios'][4]['inventory'], [])
        self.assertFalse(self.p.add_resident.isVisible()); self.assertFalse(self.p.declare_victory.isVisible())

    def test_map_epoch_refresh_retention_and_running_input_snapshot_remain_independent(self):
        graph = public_scenario_presets()[0]['payload']['graph']; self.p.set_graph(graph, epoch=410); self.p.import_graph.click(); self.execute()
        calls = []; self.p.mapNodeSelected.connect(lambda identity, binding: calls.append((identity, binding)))
        self.p.result_view.anchorClicked.emit(QUrl('rouge-map-node:a')); self.assertEqual(calls[0][1]['epoch'], 410)
        self.p.scenario_select.setCurrentIndex(self.p.scenario_select.findData('ap2')); self.p.graph_node.setCurrentIndex(self.p.graph_node.findData('g'))
        self.p.result_view.verticalScrollBar().setValue(self.p.result_view.verticalScrollBar().maximum())
        before = (self.p.editor.toPlainText(), self.p.result_snapshot(), self.p.scenario_select.currentData(), self.p.graph_node.currentData(), self.p.result_view.toHtml(), self.p.result_view.verticalScrollBar().value())
        self.p.set_graph(graph, epoch=411); self.qt.processEvents()
        after = (self.p.editor.toPlainText(), self.p.result_snapshot(), self.p.scenario_select.currentData(), self.p.graph_node.currentData(), self.p.result_view.toHtml(), self.p.result_view.verticalScrollBar().value())
        self.assertEqual(before, after); self.p.result_view.anchorClicked.emit(QUrl('rouge-map-node:a')); self.assertEqual(len(calls), 1)
        self.p.run_button.click(); payload = json.loads(self.p.editor.toPlainText()); payload['scenarios'][0]['action_points'] = 9; self.p._write(payload); self.complete()
        self.assertIn('结果对应此前输入', self.p.status.text()); self.assertEqual(self.p.result_snapshot()['cases'][0]['scenario_input']['action_points'], 8)

    def test_invalid_case_preserves_previous_matrix_and_results_are_isolated_snapshots(self):
        self.execute(); before = deepcopy(self.p.result_snapshot()); isolated = self.p.result_snapshot(); isolated['cases'].clear()
        self.assertEqual(before, self.p.result_snapshot())
        payload = json.loads(self.p.editor.toPlainText()); payload['scenarios'][1]['id'] = payload['scenarios'][0]['id']; self.p._write(payload)
        self.p.run_button.click(); self.complete(); self.assertIn('未生成新结果', self.p.status.text()); self.assertEqual(before, self.p.result_snapshot())


if __name__ == '__main__': unittest.main()
