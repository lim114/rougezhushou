"""Visible current-product node-information MainWindow; isolated public state."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--receipt', required=True)
    parser.add_argument('--visible-ms', type=int, default=120000)
    args = parser.parse_args()
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    from rouge import app as app_module
    from rouge import map_view as map_module
    from rouge.offline_tools_view import PRODUCT_QUERIES, QUERIES, public_payload, run_offline_query
    from tests.test_route_information_scope import (
        PublicInformationWindow, public_information_graph, REMOVED_TABS,
        REMOVED_ATTRIBUTES, REMOVED_COMMANDS,
    )
    from unittest.mock import patch
    files = (
        'rouge/app.py', 'rouge/map_view.py', 'rouge/map_reporting.py',
        'rouge/offline_tools_view.py', 'rouge/exploration_planning.py',
        'rouge/information_scope.py',
        'scripts/exploration_planning_cli.py', 'tests/test_route_information_scope.py',
        'scripts/verify_route_information_window_270.py',
    )
    loaded = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in files}
    gui = QApplication([])
    with tempfile.TemporaryDirectory(prefix='rouge-270-public-window-') as state:
        temp = Path(state)
        app_module.ROOT = temp; app_module.SETTINGS = temp / 'settings.json'
        app_module.OPERATOR_STATE = temp / 'operators.json'; app_module.RUN_STATE = temp / 'run.json'
        window = PublicInformationWindow()
        window.setWindowTitle('第270节 · 路线节点信息（隔离公开资料，不提供选路）')
        window.resize(1550, 1100); window.show()

        def check():
            try:
                assert window.isVisible()
                assert not window.auto.isChecked() and window.capture.target is None
                assert window.desktop.process is None
                tabs = window.centralWidget()
                labels = {tabs.tabText(i) for i in range(tabs.count())}
                assert not labels.intersection(REMOVED_TABS)
                assert all(not hasattr(window, name) for name in REMOVED_ATTRIBUTES)
                graph = public_information_graph()
                graph['captured_at'] = window.run.state['started_at'] + 1
                window.run.state['maps']['zone_1'] = deepcopy(graph)
                window.run.state['config']['zone'] = {'id': 'zone_1'}
                window.render_map()
                tabs.setCurrentWidget(window.exploration_map_tab)
                with patch.object(map_module, 'route_reference', side_effect=AssertionError('route calculation forbidden')):
                    window.map_view.select_node('a'); gui.processEvents()
                    assert not window.map_view.grab().isNull()
                    assert window.map_view.route()['status'] == 'information_only'
                    assert window.map_view.route()['display_path'] == []
                assert '思乡心切' in window.map_detail.toPlainText()
                assert '【路线参考】' not in window.map_detail.toPlainText()
                panel = window.node_catalog
                panel.map_button.click()
                assert {'不期而遇', '林间空地', '未知的命运', '作战'} <= set(panel.list.groups)
                window.map_view.select_node('b'); panel.bind_button.click()
                index = next(i for i, entry in enumerate(panel.entries)
                             if entry['title'] == '思乡心切' and entry.get('history_read'))
                panel.list.setCurrentRow(index)
                assert panel.event_stage.currentData() == 'ro6_t_1'
                assert panel.battle_button.isEnabled() and panel.map_jump.isEnabled()
                key = panel.detail_key; panel.collapse_button.click(); panel.refresh()
                assert panel.detail_key == key and not panel.list.expanded_groups()
                panel.battle_button.click(); gui.processEvents()
                assert tabs.currentWidget() is window.battle_preview
                assert window.target_stage.currentData() == 'ro6_t_1'
                tabs.setCurrentWidget(panel); panel.map_jump.click(); gui.processEvents()
                assert tabs.currentWidget() is window.exploration_map_tab and window.map_view.selected == 'b'
                window.render_map(); gui.processEvents()
                assert window.map_view.selected == 'b' and panel.detail_key == key
                assert window.run.state['maps']['zone_1'] == graph
                tools = window.offline_tools; tools.select_query('exploration', 'targets')
                assert tools.query.count() == len(PRODUCT_QUERIES['exploration']) == 9
                assert len(QUERIES['exploration']) == 13
                for command in REMOVED_COMMANDS:
                    try:
                        tools.select_query('exploration', command)
                    except ValueError:
                        pass
                    else:
                        raise AssertionError('removed menu command accepted: ' + command)
                    try:
                        run_offline_query('exploration', command, public_payload('exploration', command))
                    except ValueError:
                        pass
                    else:
                        raise AssertionError('removed backend command accepted: ' + command)
                # Leave the changed map interface visible for visual inspection.
                window.map_view.select_node('a'); tabs.setCurrentWidget(window.exploration_map_tab)
                gui.processEvents()
                assert not window.auto.isChecked() and window.capture.target is None
                assert window.desktop.process is None
                after = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in files}
                assert after == loaded, 'source changed during window validation'
                report = {
                    'passed': True, 'qpa': gui.platformName(), 'visible': window.isVisible(),
                    'current_product_route_planning_pages_absent': True,
                    'current_product_route_instances_absent': True,
                    'route_calculation_not_called_for_map_paint': True,
                    'no_automatically_selected_route_highlight': True,
                    'current_product_exploration_query_count': 9,
                    'historical_catalog_exploration_query_count': 13,
                    'all_four_removed_menu_and_backend_commands_rejected': True,
                    'node_type_branches_and_collapse_retained': True,
                    'history_event_fixed_battle_preview_and_exact_map_return': True,
                    'refresh_preserved_selected_node_and_historical_event': True,
                    'public_graph_unchanged': True,
                    'loaded_source_sha256': loaded, 'source_sha256_after': after,
                    'private_state_read': False, 'temporary_state_root': True,
                    'game_operated': False, 'game_captures': 0, 'chat_sent': False,
                    'scope': 'Actual changed MainWindow using public graph only; not original game/private/native-history validation',
                }
            except BaseException as error:
                report = {'passed': False, 'failure': {'type': type(error).__name__, 'message': str(error)},
                          'loaded_source_sha256': loaded, 'private_state_read': False,
                          'temporary_state_root': True, 'game_operated': False, 'chat_sent': False}
                gui.exit(1)
            path = Path(args.receipt); path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((json.dumps(report, ensure_ascii=False, indent=2) + '\n').encode('utf8'))

        QTimer.singleShot(500, check)
        QTimer.singleShot(args.visible_ms, window.close)
        return gui.exec()


if __name__ == '__main__':
    raise SystemExit(main())
