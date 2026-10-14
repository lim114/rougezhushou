"""Public route comparison through the actual temporary query widget."""
from copy import deepcopy
import json
import time
import unittest

from PySide6.QtCore import QUrl
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication

from rouge.offline_tools_view import (OfflineToolsPanel, public_payload,
    exploration_presets, run_offline_query, render_offline_result)


class RouteComparisonViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])
    def setUp(self):
        self.panel=OfflineToolsPanel(include_historical_route_diagnostics=True);self.panel.resize(1050,750);self.panel.show()
        self.panel.select_query('exploration','compare-routes');self.qt.processEvents()
    def tearDown(self):self.panel.close();self.panel.deleteLater();self.qt.processEvents()
    def execute(self):
        self.panel.run_button.click();end=time.monotonic()+8
        while self.panel._workers and time.monotonic()<end:self.qt.processEvents();time.sleep(.005)
        self.assertFalse(self.panel._workers);self.assertIsNotNone(self.panel.result_snapshot(),self.panel.status.text())

    def test_all_four_public_presets_run_in_real_widget_and_keep_unknown_totals(self):
        count=0
        for preset in exploration_presets('compare-routes'):
            self.panel.preset.setCurrentIndex(self.panel.preset.findData(preset['id']))
            self.panel.load_example.click();before=self.panel.editor.toPlainText();self.execute()
            self.assertEqual(self.panel.editor.toPlainText(),before)
            result=self.panel.result_snapshot();text=self.panel.result_view.toPlainText()
            self.assertIn('多路线费用与战斗收益比较',text)
            self.assertIn('第1行、第2列',text)
            self.assertIn('实际最佳路线',text);self.assertIn('未知',text)
            self.assertNotIn('arrival_chain_unresolved_or_blocked',text)
            self.assertNotIn('repeated_battle_reward_eligibility_unknown',text)
            self.assertIsNone(result['actual_best_route']);self.assertFalse(result['inventory_updated'])
            if preset['id']=='route-zero':
                self.assertEqual(result['routes'][0]['known_base_subtotal']['experience'],0)
                self.assertIsNone(result['routes'][0]['conditional_base_total'])
            if preset['id']=='route-repeat-reward':
                self.assertEqual(result['routes'][0]['known_base_subtotal']['experience'],10)
                self.assertIsNone(result['routes'][0]['conditional_base_total'])
            count+=1
        self.assertEqual(count,4)

    def test_refresh_query_switch_and_editor_selection_preserve_existing_work(self):
        self.execute();self.panel.technical.setChecked(True)
        cursor=self.panel.editor.textCursor();cursor.setPosition(17);cursor.setPosition(40,QTextCursor.MoveMode.KeepAnchor)
        self.panel.editor.setTextCursor(cursor);self.panel.result_view.verticalScrollBar().setValue(60)
        before=(self.panel.editor.toPlainText(),self.panel.result_snapshot(),
                cursor.anchor(),cursor.position(),self.panel.result_view.verticalScrollBar().value())
        graph=public_payload('exploration','compare-routes')['graph']
        self.panel.set_graph(graph,epoch=31);self.panel.set_graph(deepcopy(graph),epoch=31)
        self.panel.select_query('exploration','settlements');self.panel.select_query('exploration','compare-routes')
        self.qt.processEvents();cursor=self.panel.editor.textCursor()
        after=(self.panel.editor.toPlainText(),self.panel.result_snapshot(),
               cursor.anchor(),cursor.position(),self.panel.result_view.verticalScrollBar().value())
        self.assertEqual(before,after)

    def test_imported_route_nodes_bind_only_to_same_current_epoch_and_positions(self):
        graph=public_payload('exploration','compare-routes')['graph'];graph['template_id']='public-route-reference';graph['zone_id']='zone_1'
        self.panel.set_graph(graph,epoch=31);self.panel.import_graph.click();self.execute()
        self.assertEqual(set(self.panel._result_links),{'s','a','g','q'})
        calls=[];self.panel.mapNodeSelected.connect(lambda node,binding:calls.append((node,binding)))
        self.panel.result_view.anchorClicked.emit(QUrl('rouge-map-node:a'));self.assertEqual(calls[0][0],'a')
        self.assertEqual(calls[0][1]['epoch'],31)
        self.panel.set_graph(graph,epoch=32);self.panel.result_view.anchorClicked.emit(QUrl('rouge-map-node:a'))
        self.assertEqual(len(calls),1);self.assertIn('链接已过期',self.panel.status.text())

    def test_invalid_plan_does_not_leave_old_result_or_mutate_public_input(self):
        self.execute();payload=public_payload('exploration','compare-routes')
        payload['routes'][0]['steps'][0]['battle']['stage_id']='unlisted'
        self.panel.editor.setPlainText(json.dumps(payload,ensure_ascii=False));self.panel.run_button.click()
        end=time.monotonic()+8
        while self.panel._workers and time.monotonic()<end:self.qt.processEvents();time.sleep(.005)
        self.assertFalse(self.panel._workers);self.assertIsNone(self.panel.result_snapshot())
        self.assertIn('离线查询失败',self.panel.status.text())
        self.assertEqual(json.loads(self.panel.editor.toPlainText()),payload)

    def test_sync_render_retains_independent_battle_source_and_declared_interval(self):
        payload=public_payload('exploration','compare-routes');before=deepcopy(payload)
        for route in payload['routes']:
            battle=next(step['battle'] for step in route['steps'] if 'battle' in step)
            battle.update(stage_id='ro6_t_1',battle_floor=None,entry_context='event_battle')
        result=run_offline_query('exploration','compare-routes',payload,include_historical_route_diagnostics=True)
        text=render_offline_result('exploration','compare-routes',result,graph=payload['graph'])
        self.assertIn('2–3',text);self.assertIn('不取平均或赋概率',text)
        self.assertEqual(result['source']['base_rewards']['revision'],'433770')
        self.assertEqual(public_payload('exploration','compare-routes'),before)
