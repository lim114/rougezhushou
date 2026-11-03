"""Current node-information product scope and explicit historical diagnostics.

Only public graphs and temporary state are used. No game enumeration, capture,
chat request, or real user's run/configuration participates in these checks.
"""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication

from rouge import app as app_module
from rouge import map_view as map_module
from rouge.map_reporting import format_connections, format_node
from rouge.offline_tools_view import (
    OfflineToolsPanel, PRODUCT_QUERIES, QUERIES, public_payload,
    run_offline_query,
)


REMOVED_COMMANDS = ('options', 'itinerary', 'compare-routes', 'search-routes')
REMOVED_TABS = ('路线约束', '居民路线', '路线资源', '多情景路线', '路线续接')
REMOVED_ATTRIBUTES = (
    'route_constraints', 'resident_route_review', 'route_resource_ledger',
    'route_scenarios', 'route_continuation',
)
ROOT = Path(__file__).resolve().parents[1]


def public_information_graph():
    """An independently declared diamond, not a game observation."""
    return {
        'status': 'matched', 'zone_id': 'zone_1', 'template_id': 'public-node-information-270',
        'grid': {'rows': 3, 'cols': 4}, 'current_node': 'a',
        'source': {'url': 'https://example.invalid/public-node-information-fixture'},
        'edges': [['a', 'b'], ['a', 'c'], ['b', 'd'], ['c', 'd']],
        'nodes': [
            {'id': 'a', 'row': 1, 'col': 0, 'distance': 0, 'center': [.2, .5],
             'visible': True, 'observed_type': '不期而遇',
             'content': {'kind': 'event', 'title': '思乡心切'}},
            {'id': 'b', 'row': 0, 'col': 1, 'distance': 1, 'center': [.5, .25],
             'visible': True, 'observed_type': '林间空地', 'remembered_type': '不期而遇',
             'remembered_content': {'kind': 'event', 'title': '思乡心切'},
             'content_history': [{'kind': 'event', 'title': '鸭托邦'}]},
            {'id': 'c', 'row': 2, 'col': 1, 'distance': 1, 'center': [.5, .75],
             'visible': True, 'observed_type': '未知的命运',
             'prediction': {'candidates': ['不期而遇'], 'evidence': 'community_constraint',
                            'reason': '公开测试声明；不是游戏观测或概率'}},
            {'id': 'd', 'row': 1, 'col': 3, 'distance': 2, 'center': [.8, .5],
             'visible': True, 'observed_type': '作战',
             'content': {'kind': 'battle', 'title': '遗忘时间', 'variant_id': 'ro6_n_1_2'}},
        ],
    }


class PublicInformationWindow(app_module.MainWindow):
    def refresh_windows(self):
        # Override the constructor's enumeration as well as any later refresh.
        self.windows.clear()


class RouteInformationScopeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='rouge-270-public-test-')
        self.addCleanup(temp.cleanup)
        self.state_root = Path(temp.name)
        for key, value in (
            ('ROOT', self.state_root), ('RUN_STATE', self.state_root / 'run.json'),
            ('OPERATOR_STATE', self.state_root / 'operators.json'),
            ('SETTINGS', self.state_root / 'settings.json'),
        ):
            patched = patch.object(app_module, key, value)
            patched.start(); self.addCleanup(patched.stop)
        # Any accidentally reached real enumeration must fail this isolated test.
        patched = patch.object(app_module, 'list_game_windows', side_effect=AssertionError('game enumeration forbidden'))
        patched.start(); self.addCleanup(patched.stop)
        self.window = PublicInformationWindow()
        self.addCleanup(self.window.close)
        self.window.resize(1200, 850); self.window.show(); self.qt.processEvents()
        self.assertFalse(self.window.auto.isChecked())
        self.assertIsNone(self.window.capture.target)
        self.assertIsNone(self.window.desktop.process)

    def install_graph(self):
        graph = public_information_graph()
        graph['captured_at'] = self.window.run.state['started_at'] + 1
        self.window.run.state['maps']['zone_1'] = deepcopy(graph)
        self.window.run.state['config']['zone'] = {'id': 'zone_1'}
        self.window.render_map(); self.qt.processEvents()
        return graph

    def pick_event(self, title, *, historical=False):
        panel = self.window.node_catalog
        index = next(i for i, entry in enumerate(panel.entries)
                     if entry['kind'] == 'event' and entry['title'] == title
                     and bool(entry.get('history_read')) == historical)
        panel.list.setCurrentRow(index); self.qt.processEvents()
        return panel.entries[index]

    def wait_done(self, panel):
        end = time.monotonic() + 8
        while panel._workers and time.monotonic() < end:
            self.qt.processEvents(); time.sleep(.005)
        self.assertFalse(panel._workers, panel.status.text())
        self.qt.processEvents()

    def test_current_main_window_has_no_route_planning_pages_or_instances(self):
        tabs = self.window.centralWidget()
        labels = {tabs.tabText(i) for i in range(tabs.count())}
        self.assertEqual(labels,{'本局','地图与节点','干员计算','资料查询','聊天'})
        self.assertEqual(tabs.pages[self.window.common_reference_panels['battle']],('地图与节点','关卡与敌人'))
        self.assertEqual(tabs.pages[self.window.common_reference_panels['events']],('地图与节点','事件查询'))
        self.assertIs(tabs.aliases[self.window.exploration_map_tab],tabs.aliases[self.window.node_catalog])
        self.assertFalse(tabs.developer_tools);self.assertFalse(tabs.setCurrentWidget(self.window.offline_tools))
        self.assertFalse(tabs.developer_dialog.isVisible())
        self.assertFalse(labels.intersection(REMOVED_TABS))
        for name in REMOVED_ATTRIBUTES:
            self.assertFalse(hasattr(self.window, name), name)
        self.assertFalse((self.state_root / '.local' / 'desktop-chat').exists())

    def test_current_map_never_requests_an_automatically_selected_route(self):
        graph = self.install_graph()
        self.window.centralWidget().setCurrentWidget(self.window.exploration_map_tab)
        with patch.object(map_module, 'route_reference', side_effect=AssertionError('route calculation forbidden')):
            self.window.map_view.select_node('d'); self.qt.processEvents()
            self.assertFalse(self.window.map_view.grab().isNull())
            route = self.window.map_view.route()
        self.assertEqual(route['status'], 'information_only')
        self.assertEqual(route['display_path'], [])
        self.assertEqual(self.window.map_view.graph['edges'], graph['edges'])
        self.assertEqual(self.window.map_view.selected, 'd')

    def test_connections_report_all_adjacent_nodes_without_selecting_one_path(self):
        graph = public_information_graph(); before = deepcopy(graph)
        text = format_connections(graph, 'a')
        self.assertIn('上排 · 第2列', text)
        self.assertIn('下排 · 第2列', text)
        self.assertIn('模板', text)
        self.assertNotIn('最短', text)
        self.assertNotIn(' → ', text)
        report = format_node(graph, 'a')
        self.assertNotIn('【路线参考】', report)
        self.assertNotIn('从当前确认位置出发', report)
        self.assertIn('思乡心切', report)
        self.assertEqual(graph, before)
        graph['nodes'][2]['observed_type']='类型未确认'
        text=format_connections(graph,'a')
        self.assertNotIn('已读：类型未确认',text)
        self.assertIn('类型候选：不期而遇',text)
        history=format_connections(graph,'a',historical=True)
        self.assertIn('当时林间空地',history)
        self.assertNotIn('本帧林间空地',history)

    def test_chat_scope_prompts_keep_node_information_policy_without_sending(self):
        from rouge.information_scope import analysis_system_prompt,desktop_analysis_prompt,NODE_INFORMATION_POLICY
        context={'fixture':'公开声明','node':'类型未确认'};before=deepcopy(context)
        for supplied in (None,context):
            system=analysis_system_prompt(supplied);desktop=desktop_analysis_prompt('列出事件条件',supplied)
            self.assertIn(NODE_INFORMATION_POLICY,system);self.assertIn(NODE_INFORMATION_POLICY,desktop)
            self.assertIn('列出事件条件',desktop)
            if supplied is None:
                self.assertNotIn('公开声明',system);self.assertNotIn('公开声明',desktop)
            else:self.assertIn('公开声明',system);self.assertIn('公开声明',desktop)
        self.assertEqual(context,before)

    def test_product_query_menu_and_programmatic_selection_reject_removed_commands(self):
        self.assertEqual(len(QUERIES['exploration']), 13)
        self.assertEqual(len(PRODUCT_QUERIES['exploration']), 9)
        panel = self.window.offline_tools
        panel.select_query('exploration', 'targets')
        visible = {panel.query.itemData(i) for i in range(panel.query.count())}
        self.assertEqual(visible, set(dict(PRODUCT_QUERIES['exploration'])))
        before = (panel.current_query(), panel.editor.toPlainText())
        for command in REMOVED_COMMANDS:
            with self.subTest(command=command), self.assertRaises(ValueError):
                panel.select_query('exploration', command)
            self.assertEqual((panel.current_query(), panel.editor.toPlainText()), before)

    def test_default_backend_rejects_all_four_routes_before_running_historical_algorithms(self):
        from rouge import exploration_planning
        for command in REMOVED_COMMANDS:
            with self.subTest(command=command):
                with patch.dict(exploration_planning.COMMANDS, {command: lambda **_: self.fail('historical route executed')}):
                    with self.assertRaises(ValueError):
                        run_offline_query('exploration', command, public_payload('exploration', command))

    def test_injected_combo_entry_cannot_bypass_current_product_backend(self):
        from rouge import exploration_planning
        panel = self.window.offline_tools
        panel.select_query('exploration', 'targets')
        panel.query.blockSignals(True)
        panel.query.addItem('历史搜索旁路测试', 'search-routes')
        panel.query.setCurrentIndex(panel.query.count() - 1)
        panel.query.blockSignals(False)
        panel.editor.setPlainText(json.dumps(public_payload('exploration', 'search-routes'), ensure_ascii=False))
        with patch.dict(exploration_planning.COMMANDS, {'search-routes': lambda **_: self.fail('injected route executed')}):
            panel.run_button.click(); self.wait_done(panel)
        self.assertIsNone(panel.result_snapshot())

    def test_historical_route_diagnostics_require_explicit_opt_in(self):
        panel = OfflineToolsPanel(include_historical_route_diagnostics=True)
        self.addCleanup(panel.close)
        panel.select_query('exploration', 'search-routes')
        self.assertEqual(panel.query.count(), 13)
        result = run_offline_query('exploration', 'search-routes', public_payload('exploration', 'search-routes'),
                                   include_historical_route_diagnostics=True)
        self.assertTrue(result['plans'])
        self.assertIsNone(result['actual_best_route'])
        view = map_module.MapView(include_historical_route_diagnostics=True)
        self.addCleanup(view.close); view.set_map(public_information_graph()); view.select_node('d')
        self.assertTrue(view.route()['display_path'])

    def test_cli_default_rejects_route_commands_and_hidden_history_switch_remains_explicit(self):
        script = ROOT / 'scripts' / 'exploration_planning_cli.py'
        help_result = subprocess.run([sys.executable, '-X', 'utf8', str(script), '--help'], cwd=ROOT,
                                     capture_output=True, text=True, encoding='utf8')
        self.assertEqual(help_result.returncode, 0)
        self.assertNotIn('--historical-route-diagnostics', help_result.stdout)
        for command in REMOVED_COMMANDS:
            with self.subTest(command=command):
                result = subprocess.run([sys.executable, '-X', 'utf8', str(script), command], cwd=ROOT,
                                        capture_output=True, text=True, encoding='utf8')
                self.assertNotEqual(result.returncode, 0)
        payload_file = self.state_root / 'public-search-input.json'
        payload_file.write_text(json.dumps(public_payload('exploration', 'search-routes'), ensure_ascii=False), encoding='utf8')
        result = subprocess.run([sys.executable, '-X', 'utf8', str(script), '--historical-route-diagnostics', 'search-routes',
                                 '--input', str(payload_file)], cwd=ROOT, capture_output=True, text=True, encoding='utf8')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)['plans'])

    def test_node_type_branches_collapse_refresh_and_unknown_event_qualification_remain(self):
        self.install_graph(); panel = self.window.node_catalog
        panel.map_button.click()
        self.assertTrue({'不期而遇', '林间空地', '未知的命运', '作战'} <= set(panel.list.groups))
        self.window.map_view.select_node('c'); panel.bind_button.click()
        row = self.pick_event('思乡心切')
        self.assertNotEqual(row['qualification']['status'], 'excluded')
        self.assertIsNone(row['qualification']['actual_server_eligible'])
        self.assertIn('未知', panel.detail.toPlainText())
        key = panel.detail_key
        panel.collapse_button.click(); panel.refresh(); self.qt.processEvents()
        self.assertFalse(panel.list.expanded_groups()); self.assertEqual(panel.detail_key, key)
        panel.expand_button.click(); self.assertTrue(panel.list.expanded_groups())

    def test_historical_event_keeps_fixed_battle_and_return_to_its_exact_map_node(self):
        graph = self.install_graph(); self.window.map_view.select_node('b')
        panel = self.window.node_catalog; panel.bind_button.click()
        self.pick_event('思乡心切', historical=True)
        self.assertIn('历史已读取内容', panel.detail.toPlainText())
        self.assertTrue(panel.battle_button.isEnabled())
        self.assertEqual(panel.event_stage.currentData(), 'ro6_t_1')
        self.assertEqual(panel.map_location.currentData()['node_id'], 'b')
        key = panel.detail_key; panel.battle_button.click(); self.qt.processEvents()
        self.assertEqual(self.window.target_stage.currentData(), 'ro6_t_1')
        self.assertIs(self.window.centralWidget().currentWidget(), self.window.battle_preview)
        self.window.centralWidget().setCurrentWidget(panel); panel.map_jump.click(); self.qt.processEvents()
        self.assertIs(self.window.centralWidget().currentWidget(), self.window.exploration_map_tab)
        self.assertEqual(self.window.map_view.selected, 'b')
        self.assertEqual(panel.detail_key, key)
        self.assertEqual(self.window.run.state['maps']['zone_1'], graph)

    def test_current_refresh_preserves_node_and_active_query_inputs_results_and_reading(self):
        graph = self.install_graph(); self.window.map_view.select_node('a')
        panel = self.window.offline_tools; panel.select_query('exploration', 'targets')
        panel.import_graph.click(); panel.run_button.click(); self.wait_done(panel)
        self.assertIsNotNone(panel.result_snapshot(), panel.status.text())
        panel.show(); self.qt.processEvents()
        cursor = panel.editor.textCursor(); cursor.setPosition(7)
        cursor.setPosition(17, QTextCursor.MoveMode.KeepAnchor); panel.editor.setTextCursor(cursor)
        before = (panel.current_query(), panel.editor.toPlainText(), panel.result_snapshot(),
                  panel.result_view.toHtml(), cursor.anchor(), cursor.position(),
                  panel.result_view.verticalScrollBar().value())
        self.window.render_map(); self.qt.processEvents()
        cursor = panel.editor.textCursor()
        after = (panel.current_query(), panel.editor.toPlainText(), panel.result_snapshot(),
                 panel.result_view.toHtml(), cursor.anchor(), cursor.position(),
                 panel.result_view.verticalScrollBar().value())
        self.assertEqual(before, after)
        self.assertEqual(self.window.map_view.selected, 'a')
        self.assertEqual(self.window.run.state['maps']['zone_1'], graph)

    def test_fixed_enemy_path_sources_and_battle_preview_remain_available(self):
        from rouge.battle_preview import battle_data, route_reference
        from rouge.battle_planning import route_segments
        stage_id = 'ro6_n_1_2'; stage = battle_data()['stages'][stage_id]
        index = next(i for i, route in enumerate(stage['routes']) if route['motionMode'] in ('WALK', 'FLY'))
        result = route_reference(stage, index)
        self.assertIsNotNone(result['start']); self.assertTrue(result['points'])
        details = route_segments(stage_id, index)
        self.assertEqual(details['route_index'], index)
        self.window.show_catalog_battle(stage_id); self.qt.processEvents()
        self.assertIs(self.window.centralWidget().currentWidget(), self.window.battle_preview)
        self.assertTrue(self.window.battle_preview.rows)


if __name__ == '__main__':
    unittest.main()
