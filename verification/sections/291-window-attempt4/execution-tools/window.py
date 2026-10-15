"""UNEXECUTED CACHE DRAFT: native isolated resident-position/reference acceptance.

Root must promote reviewed291 sources (including the bound-reading signal fix)
and this canonical scripts/ file before running. This file was prepared with AST
checks only. No result, count or native-window PASS is claimed by preparation.
"""
import argparse
import ast
from contextlib import ExitStack, contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import traceback
from unittest.mock import patch

ROOT = next(path for path in Path(__file__).resolve().parents if (path / 'rouge/app.py').is_file())
sys.path.insert(0, str(ROOT))
CANONICAL = 'scripts/verify_peace_guardian_window_291.py'
PACKET = 'research/p3-peace-guardian-results-291'
TARGET = 'community_group_019'
SCENE = TARGET + ':scene:1'
MOVE = SCENE + ':choice:0'
VISION = SCENE + ':choice:1'
FIXTURE_SOURCE = 'tests/test_readable_map_047.py'
FIXTURE_SOURCE_SHA = 'aa17def537d729dff08ed10176a3b4249a08670297ddea815d6c2d6f104d73f0'
SIZES = ((1050, 720), (1280, 800), (1440, 930))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def public_seed_graph():
    """Extract an existing literal without importing a test module or setting QPA."""
    path = ROOT / FIXTURE_SOURCE
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != FIXTURE_SOURCE_SHA:
        raise AssertionError('The public graph schema fixture changed; review before adapting.')
    function = next(node for node in ast.parse(raw).body if isinstance(node, ast.FunctionDef) and node.name == 'graph')
    result = ast.literal_eval(next(node for node in function.body if isinstance(node, ast.Return)).value)
    # Explicit synthetic type/content changes; never actual game observations.
    result['nodes'][0].update(observed_type='“居民”据点', remembered_type='“居民”据点')
    result['nodes'][0].pop('content', None)
    result['nodes'][0].pop('prediction', None)
    result['nodes'][1]['remembered_type'] = '“居民”据点'
    result['nodes'][2].update(observed_type='不期而遇', content={'kind': 'event', 'title': '和平守卫者'})
    result['nodes'][2].pop('prediction', None)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--receipt', required=True)
    parser.add_argument('--visible-ms', type=int, default=120000)
    args = parser.parse_args()
    destination = Path(args.receipt).resolve()
    if destination.exists():
        raise FileExistsError('Do not overwrite the first actual receipt.')
    if args.visible_ms <= 0:
        raise ValueError('--visible-ms must be positive.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    checks, observations, images, geometry = [], [], [], []
    successful_executions = 0
    attempts = {name: 0 for name in ('game_enumeration', 'game_connect', 'game_capture',
                                    'game_next_frame', 'desktop_start', 'desktop_request',
                                    'provider_chat', 'credential_read')}
    before, after = {}, {}
    done = False
    failure = None
    qpa = None
    qt_exit = None
    closed = False
    gui = None
    window = None

    def require(condition, name):
        nonlocal successful_executions
        if not condition:
            raise AssertionError(name)
        successful_executions += 1
        if name not in checks:
            checks.append(name)

    def forbidden(name):
        def blocked(*_args, **_kwargs):
            attempts[name] += 1
            raise AssertionError('Forbidden external operation: ' + name)
        return blocked

    def bound_files():
        paths = {'rouge/app.py', 'rouge/map_view.py', 'rouge/map_reporting.py',
                 'rouge/node_catalog.py', 'rouge/node_catalog_view.py', 'rouge/ui_state.py',
                 'rouge/player_node_information.py', 'rouge/event_planning.py',
                 'rouge/peace_guardian_results.py', 'rouge/resident_location_references.py',
                 'rouge/choice_recruitment_results.py', 'rouge/data/node-catalog.json',
                 'rouge/data/battle-node-pools.json', 'rouge/data/peace-guardian-results.json',
                 'scripts/build_peace_guardian_results_291.py', CANONICAL, FIXTURE_SOURCE}
        packet = ROOT / PACKET
        if not packet.is_dir():
            raise FileNotFoundError('Promote the reviewed291 source packet before actual window verification.')
        for path in packet.rglob('*'):
            if path.is_symlink():
                raise ValueError('Source packet requires regular public files.')
            if path.is_file():
                paths.add(path.relative_to(ROOT).as_posix())
        manifest = json.loads((packet / 'source-manifest.json').read_bytes())
        paths.update(manifest['files'])
        tests = sorted((ROOT / 'tests').glob('test_*291*.py'))
        if not tests:
            raise FileNotFoundError('Actual291 necessary test sources must be promoted before this verification.')
        paths.update(path.relative_to(ROOT).as_posix() for path in tests)
        result = {}
        for name in sorted(paths):
            path = ROOT / name
            if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()):
                raise ValueError('Bound source must be a regular public project file: ' + name)
            result[name] = sha(path)
        return result

    try:
        if sys.platform != 'win32':
            raise RuntimeError('Native original Windows is required, not Wine/offscreen.')
        if Path(__file__).resolve() != (ROOT / CANONICAL).resolve():
            raise RuntimeError('Cache draft is not runnable acceptance. Use the reviewed canonical scripts/ file.')
        from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QPoint, QRect, QTimer
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QApplication, QScrollArea, QLabel
        import win32gui
        import win32process
        from rouge import app as app_module, event_planning
        from rouge import node_catalog as catalog
        from rouge import peace_guardian_results

        before = bound_files()
        require(peace_guardian_results.source_data() is not None, 'fresh_MOVE_source_packet_valid')
        original_event = deepcopy(catalog._event(TARGET))
        original_scene = deepcopy(catalog._scene(TARGET, SCENE))
        source = public_seed_graph()
        original_source = deepcopy(source)
        gui = QApplication([])
        qpa = gui.platformName()
        require(qpa == 'windows', 'native_windows_QPA')

        class PublicWindow(app_module.MainWindow):
            def refresh_windows(self):
                self.windows.clear()

        with tempfile.TemporaryDirectory(prefix='rouge-291-resident-window-') as directory, ExitStack() as stack:
            temporary = Path(directory)
            for key, value in {'ROOT': temporary, 'SETTINGS': temporary / 'settings.json',
                               'OPERATOR_STATE': temporary / 'operators.json', 'RUN_STATE': temporary / 'run.json'}.items():
                stack.enter_context(patch.object(app_module, key, value))
            stack.enter_context(patch.object(app_module, 'list_game_windows', side_effect=forbidden('game_enumeration')))
            for method, name in (('connect', 'game_connect'), ('capture', 'game_capture'), ('next_frame', 'game_next_frame')):
                stack.enter_context(patch.object(app_module.GameCapture, method, side_effect=forbidden(name)))
            for method, name in (('start', 'desktop_start'), ('request', 'desktop_request')):
                stack.enter_context(patch.object(app_module.DesktopBackend, method, side_effect=forbidden(name)))
            stack.enter_context(patch.object(app_module, 'stream_chat', side_effect=forbidden('provider_chat')))
            stack.enter_context(patch.object(app_module, 'read_key', side_effect=forbidden('credential_read')))
            window = PublicWindow()
            window.setWindowTitle('第291节 · 据点位置与固定作战资料（公开隔离验收）')
            window.resize(*SIZES[-1])
            window.show()
            panel, tabs = window.node_catalog, window.centralWidget()
            epoch = window.run.state['id']
            initial_run = deepcopy(window.run.state)
            map_signals, position_signals, stage_signals = [], [], []
            window.map_view.nodeSelected.connect(map_signals.append)
            panel.mapNodeSelected.connect(lambda key, binding: position_signals.append((key, deepcopy(binding))))
            panel.stageSelected.connect(stage_signals.append)
            saved = None
            size_index = 0

            def isolated():
                require(not window.auto.isChecked(), 'automatic_sampling_disabled')
                require(not window.timer.isActive(), 'sampling_timer_inactive')
                require(window.capture.target is None, 'no_capture_target')
                require(window.desktop.process is None, 'desktop_backend_not_started')
                require(all(value == 0 for value in attempts.values()), 'all_external_operation_attempt_counts_zero')

            def native():
                hwnd = int(window.winId())
                thread, process = win32process.GetWindowThreadProcessId(hwnd)
                require(bool(win32gui.IsWindow(hwnd)), 'actual_HWND_exists')
                require(bool(win32gui.IsWindowVisible(hwnd)) and window.isVisible(), 'actual_HWND_visible')
                require(process == os.getpid(), 'actual_HWND_owned_by_fixture_process')
                require(not bool(win32gui.IsIconic(hwnd)), 'actual_window_not_minimized')
                return {'hwnd': hwnd, 'thread_id': thread, 'process_id': process,
                        'rectangle': list(win32gui.GetWindowRect(hwnd)), 'qpa': qpa}

            def selected_entry():
                entry = next(row for row in panel.entries if row['key'] == panel.list.selected_key())
                require(entry['kind'] == 'event' and entry['record']['id'] == TARGET, 'exact_guardian_event_still_selected')
                return entry

            def choose_event():
                panel.list.setCurrentRow(next(index for index, entry in enumerate(panel.entries)
                    if entry['kind'] == 'event' and entry['record']['id'] == TARGET))

            def install(historical=False, bound=False, conditions=None):
                # Populate the public-fixture map selector as render_map does,
                # without installing a real run observation or triggering capture.
                from rouge.map_reporting import location
                window.map_nodes.blockSignals(True)
                window.map_nodes.clear();window.map_nodes.addItem('请选择地图上的节点',None)
                for node in sorted(source['nodes'],key=lambda item:(item['row'],item['col'])):
                    window.map_nodes.addItem(location(node,source['grid']['rows']),node['id'])
                window.map_nodes.blockSignals(False)
                window.map_view.set_map(deepcopy(source), historical=historical)
                panel.show_directory()
                panel.set_map_context(source, {'floor': 4} if conditions is None else conditions,
                    epoch=epoch, historical=historical)
                panel.kind.setCurrentIndex(panel.kind.findData('event'))
                panel.floor.setCurrentIndex(0)
                panel.node_type.setCurrentIndex(0)
                panel.search.setText('和平守卫者')
                if bound:
                    panel.set_node(source, '2,3', floor=4, difficulty=3)
                    panel.bind_current_node()
                    require(panel.dossier is not None and panel.dossier['position']['node_id'] == '2,3',
                            'actual_event_dossier_bound_before_reference_navigation')
                choose_event()
                tabs.setCurrentWidget(panel)
                panel.reading_tabs.setCurrentWidget(panel.player_detail)

            def reading(widget):
                cursor = widget.textCursor()
                return {'text_sha256': hashlib.sha256(widget.toPlainText().encode('utf8')).hexdigest(),
                        'anchor': cursor.anchor(), 'position': cursor.position(), 'selected_text': cursor.selectedText(),
                        'vertical': widget.verticalScrollBar().value(), 'horizontal': widget.horizontalScrollBar().value()}

            def snapshot():
                return {'selected_key': panel.list.selected_key(), 'detail_key': panel.detail_key,
                        'search_text': panel.search.text(), 'search_cursor': panel.search.cursorPosition(),
                        'search_selection_start': panel.search.selectionStart(), 'search_selected_text': panel.search.selectedText(),
                        'reading_tab': panel.reading_tabs.currentIndex(), 'player': reading(panel.player_detail),
                        'evidence': reading(panel.detail), 'dossier': deepcopy(panel.dossier),
                        'node_context': deepcopy(panel.node_context), 'position': deepcopy(panel.resident_location.currentData()),
                        'stage': panel.resident_stage.currentData(), 'expanded_groups': sorted(panel.list.expanded_groups()),
                        'tree_scroll': panel.list.verticalScrollBar().value()}

            def prime(widget):
                cursor = widget.textCursor(); cursor.setPosition(2)
                cursor.setPosition(12, QTextCursor.MoveMode.KeepAnchor); widget.setTextCursor(cursor)
                panel.search.setSelection(0, 2)
                gui.processEvents()
                bar = widget.verticalScrollBar()
                require(bar.maximum() > 0, 'real_reading_scroll_range_nonzero')
                bar.setValue(max(1, bar.maximum() // 2))
                gui.processEvents()
                require(bar.value() > 0 and bool(widget.textCursor().selectedText()), 'real_nonzero_scroll_and_text_selection')
                require(bool(panel.search.selectedText()), 'real_search_selection_nonempty')

            def contract():
                entry = selected_entry()
                rows = event_planning.choice_eligibility(TARGET, SCENE, panel._event_context(entry['record']))['rows']
                move = next(row for row in rows if row['choice_key'] == MOVE)
                vision = next(row for row in rows if row['choice_key'] == VISION)
                reference = move['movement_result_reference']
                require(reference['status'] == 'documented_reference' and reference['annotation_role'] == 'selection_result',
                        'exact_MOVE_documented_result_role')
                require(reference['source_scene_link_verified'] is False
                        and reference['completion_exception_reference']['negation_implies_successful_movement_verified'] is False,
                        'one_way_documentation_not_sourceScene_or_converse_proof')
                require(all(reference[name] is None for name in ('actual_current_floor_completion', 'actual_target_node_id',
                        'actual_moved', 'actual_battle_triggered', 'actual_position_after')), 'all_actual_MOVE_outcomes_unknown')
                require('movement_result_reference' not in vision, 'VISION_does_not_inherit_MOVE_exception')
                require(move['conditional_text'] == original_scene['choices'][0]['conditional']
                        and move['unparsed_condition_text'] is None
                        and move['game_choice_ids'] == original_scene['choices'][0]['game_choice_ids'] == ['choice_ro6_task1_3'],
                        'exact_raw_MOVE_annotation_and_original_IDs_preserved')
                text = panel.player_detail.toPlainText()
                require('资料记载：若已完成当前层的【“居民”据点】作战则不会移动。' in text,
                        'player_retains_exact_original_one_way_condition')
                require('未完成不代表一定移动' in text and '本层是否已完成、实际目的地和是否移动：尚未确认' in text,
                        'player_keeps_completion_target_and_movement_unknown')
                require('http://' not in text and 'https://' not in text and 'community_group_' not in text,
                        'player_no_raw_URL_or_community_ID')
                require(catalog._event(TARGET) == original_event, 'original_event_catalog_unmodified')
                require(event_planning.event_battle_links(TARGET)['rows'] == [], 'fixed_battle_references_not_added_as_MOVE_outcomes')

            def defaults():
                require(panel.resident_location.count() == 3 and panel.resident_stage.count() == 3,
                        'two_explicit_positions_and_two_fixed_stages_with_placeholders')
                require(panel.resident_location.currentData() is None and panel.resident_stage.currentData() is None,
                        'position_and_fixed_stage_default_unselected')
                require(not panel.resident_map_button.isEnabled() and not panel.resident_stage_button.isEnabled(),
                        'reference_buttons_disabled_without_manual_selection')
                require({panel.resident_stage.itemData(index) for index in range(1, panel.resident_stage.count())}
                        == {'ro6_t_10', 'ro6_t_11'}, 'exact_two_resident_fixed_battle_choices')

            def save_image(name):
                isolated(); handle = native()
                path = destination.with_name(destination.stem + '-' + name + '.png')
                if path.exists():
                    raise FileExistsError('Preserve first actual screenshot: ' + str(path))
                pixels = window.grab(); require(not pixels.isNull(), name + '_actual_own_window_pixels')
                data = QByteArray(); buffer = QBuffer(data)
                require(buffer.open(QIODevice.OpenModeFlag.WriteOnly), name + '_PNG_buffer_open')
                require(bool(pixels.save(buffer, 'PNG')), name + '_actual_PNG_encoded'); buffer.close()
                with path.open('xb') as stream:
                    stream.write(bytes(data))
                images.append({'name': name, 'path': str(path), 'sha256': sha(path), 'native_window': handle,
                               'reading_state': snapshot()})

            def fail(error):
                nonlocal failure, done
                if failure is None:
                    failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
                done = False
                window.close(); gui.exit(1)

            def later(callback, delay=400):
                def guarded():
                    try:
                        isolated(); callback()
                    except BaseException as error:
                        fail(error)
                QTimer.singleShot(delay, guarded)

            def begin():
                install(); defaults(); contract()
                require(panel.node_context is None and panel.dossier is None,
                        'initial_public_directory_has_no_node_context_or_bound_dossier')
                require(not panel.bind_button.isEnabled(),
                        'initial_view_selected_map_node_button_disabled_without_selection')
                before_reference = snapshot()
                panel.resident_location.setCurrentIndex(1)
                binding = deepcopy(panel.resident_location.currentData())
                selected_reading = snapshot()
                panel.resident_map_button.click()
                require(tabs.currentWidget() is window.exploration_map_tab
                        and window.map_view.selected == binding['node_id'],
                        'first_unbound_reference_click_reaches_latest_MapView_selection')
                require(panel.bind_button.isEnabled(),
                        'first_unbound_reference_click_enables_explicit_view_selected_node_button')
                require(panel.node_context is None and panel.dossier is None,
                        'first_unbound_reference_click_does_not_create_or_replace_reading_binding')
                require(snapshot() == selected_reading,
                        'first_unbound_reference_click_preserves_selected_event_reading')
                tabs.setCurrentWidget(panel)
                window.map_view.clear_reference_selection()
                window.map_node_selected('',update_catalog=False)
                panel.resident_location.setCurrentIndex(0)
                require(window.map_view.selected is None and window.map_view.reference_binding is None,
                        'first_unbound_probe_clears_only_UI_reference_selection')
                require(not panel.bind_button.isEnabled(),
                        'first_unbound_probe_reset_disables_explicit_view_without_selection')
                require(snapshot() == before_reference,
                        'first_unbound_probe_restores_original_directory_reading_and_placeholders')
                defaults(); contract()
                window.resize(*SIZES[0]); later(check_layout)

            def check_layout():
                nonlocal size_index
                native_info = native()
                require(tabs.currentWidget() is panel, 'actual_node_panel_is_visible_for_layout')
                require(panel.player_detail.width() >= 260 and panel.player_detail.height() >= 120,
                        'player_reading_area_at_least_260_by_120_operational_threshold')
                controls = {}
                for name in ('resident_reference_label', 'resident_location', 'resident_map_button',
                             'resident_stage', 'resident_stage_button'):
                    widget = getattr(panel, name)
                    rect = QRect(widget.mapTo(window, QPoint(0, 0)), widget.size())
                    parent_rect = QRect(widget.mapTo(widget.parentWidget(), QPoint(0, 0)), widget.size())
                    require(widget.isVisible() and not widget.visibleRegion().isEmpty(), 'layout_' + name + '_visible')
                    require(window.rect().contains(rect) and widget.parentWidget().rect().contains(parent_rect),
                            'layout_' + name + '_fully_inside_window_and_parent')
                    controls[name] = [rect.x(), rect.y(), rect.width(), rect.height()]
                geometry.append({'requested_size': list(SIZES[size_index]), 'actual_size': [window.width(), window.height()],
                    'player_size': [panel.player_detail.width(), panel.player_detail.height()], 'controls': controls,
                    'native_window': native_info, 'threshold_is_operational_not_general_usability_claim': True})
                require([window.width(),window.height()]==list(SIZES[size_index]),
                        'actual_window_client_size_matches_requested_layout_size')
                if size_index==0:
                    saved_reading=snapshot();capture_page=tabs.widget(0)
                    tabs.setCurrentWidget(capture_page);gui.processEvents()
                    require(isinstance(capture_page,QScrollArea), 'sampling_page_can_scroll_without_forcing_other_tabs_taller')
                    bar=capture_page.verticalScrollBar();old_value=bar.value()
                    require(bar.maximum()>0, 'sampling_page_has_real_scroll_range_at_720_height')
                    bar.setValue(bar.maximum());gui.processEvents()
                    notice=next(label for label in capture_page.findChildren(QLabel)
                                if label.text().startswith('地图预测页提供模板匹配'))
                    notice_rect=QRect(notice.mapTo(capture_page.viewport(),QPoint(0,0)),notice.size())
                    require(capture_page.viewport().rect().contains(notice_rect),
                            'sampling_page_bottom_information_fully_reachable_without_clipping')
                    bar.setValue(old_value);tabs.setCurrentWidget(panel);gui.processEvents()
                    require(snapshot()==saved_reading, 'sampling_page_scroll_test_preserves_node_reading')
                save_image('layout-' + str(size_index + 1))
                size_index += 1
                if size_index < len(SIZES):
                    window.resize(*SIZES[size_index]); later(check_layout)
                else:
                    later(prepare_bound_reading)

            def prepare_bound_reading():
                nonlocal saved
                install(bound=True)
                panel.resident_location.setCurrentIndex(1); panel.resident_stage.setCurrentIndex(2)
                prime(panel.player_detail); saved = snapshot()
                panel.refresh(); later(check_bound_refresh_and_click)

            def check_bound_refresh_and_click():
                require(snapshot() == saved, 'bound_event_refresh_keeps_dossier_key_search_tab_scroll_and_selection')
                binding = deepcopy(panel.resident_location.currentData())
                panel.resident_map_button.click()
                require(tabs.currentWidget() is window.exploration_map_tab and window.map_view.selected == binding['node_id'],
                        'reference_click_reaches_actual_MapView_selected_position')
                require(window.map_nodes.currentData() == binding['node_id'] and bool(window.map_detail.toPlainText()),
                        'map_details_and_position_combo_update_on_reference_navigation')
                require(snapshot() == saved, 'real_signal_chain_preserves_bound_event_reading_after_reference_navigation')
                tabs.setCurrentWidget(panel)
                require(snapshot() == saved, 'return_to_event_preserves_bound_key_search_tab_nonzero_scroll_and_selection')
                window.map_view.set_map(deepcopy(source), historical=False)
                require(snapshot() == saved and window.map_view.selected == binding['node_id'],
                        'set_map_refresh_preserves_reference_origin_and_bound_event_reading')
                require(window.map_view.reference_binding == binding,
                        'reference_origin_retains_full_typed_binding_after_map_refresh')
                technical_before = window.map_technical.isChecked()
                tabs.setCurrentWidget(window.exploration_map_tab)
                window.map_technical.setChecked(not technical_before)
                require(snapshot() == saved, 'reference_map_technical_toggle_keeps_bound_event_reading')
                window.map_technical.setChecked(technical_before)
                tabs.setCurrentWidget(panel)
                require(snapshot() == saved, 'return_from_technical_map_keeps_bound_event_reading')
                contract(); save_image('bound-current')
                # Explicit viewing has the opposite intent: bind the latest map selection.
                panel.bind_button.click()
                require(panel.node_context[1] == binding['node_id']
                        and panel.dossier['position']['node_id'] == binding['node_id'],
                        'explicit_view_selected_map_node_uses_latest_selection_not_old_event_context')
                require(panel.list.selected_key() != saved['selected_key'],
                        'explicit_selected_node_view_replaces_reading_only_after_user_intent')
                install(bound=True)
                # Ordinary map selection must retain the old automatic dossier follow.
                old_signals = len(map_signals)
                window.map_view.select_node('1,1')
                require(len(map_signals) == old_signals + 1, 'ordinary_MapView_selection_still_emits_original_signal_once')
                require(panel.node_context[1] == '1,1' and panel.dossier['position']['node_id'] == '1,1',
                        'ordinary_MapView_selection_still_follows_original_bound_dossier_flow')
                require(window.map_view.reference_binding is None, 'ordinary_selection_clears_UI_reference_origin')
                later(check_history)

            def check_history():
                nonlocal saved
                install(historical=True, bound=True, conditions={})
                defaults()
                require('记录时读到的据点' in panel.resident_location.itemText(1)
                        and '历史地图记录' in panel.resident_location.itemText(1)
                        and '以前读到的据点' in panel.resident_location.itemText(2), 'history_labels_separate_recorded_and_past_type_evidence')
                require('地图层数尚未确认' in panel.resident_reference_label.text(), 'unknown_map_floor_not_taken_from_directory_filter')
                panel.resident_location.setCurrentIndex(2); panel.resident_stage.setCurrentIndex(1)
                prime(panel.player_detail); saved = snapshot()
                panel.resident_map_button.click()
                require(window.map_view.selected == '1,1' and snapshot() == saved,
                        'historical_reference_reaches_same_position_without_replacing_bound_event')
                window.map_view.set_map(deepcopy(source), historical=True)
                require(window.map_view.selected == '1,1' and snapshot() == saved,
                        'historical_set_map_refresh_preserves_bound_event_and_reference_position')
                tabs.setCurrentWidget(panel); contract(); save_image('bound-history')
                later(check_stale_guards)

            def check_stale_guards():
                install(bound=True)
                panel.resident_location.setCurrentIndex(1)
                previous_calls = len(position_signals)
                stale = deepcopy(source); stale['nodes'][0]['col'] = 4
                panel.map_context = (stale, {'floor': 4}, epoch, False)
                panel.resident_map_button.click()
                require(len(position_signals) == previous_calls and panel.resident_location.currentData() is None,
                        'latest_panel_context_rejects_stale_position_before_signal')
                install(bound=True); panel.resident_location.setCurrentIndex(1)
                selected = window.map_view.selected
                stale = deepcopy(source); stale['nodes'][2]['id'] = source['nodes'][0]['id']
                window.map_view.graph = stale
                panel.resident_map_button.click()
                require(tabs.currentWidget() is panel and window.map_view.selected == selected,
                        'latest_App_graph_duplicate_rejects_before_MapView_navigation')
                require('据点位置链接已过期' in panel.status.text(), 'latest_App_guard_reports_expired_reference')
                window.map_view.graph = deepcopy(source)
                install(bound=True); later(check_reference_origin_expiry)

            def check_reference_origin_expiry():
                variants = []
                value = deepcopy(source); value['nodes'][0]['col'] = 4; variants.append(('same_ID_changed_position', value, False))
                value = deepcopy(source); value['nodes'][0]['observed_type'] = '林间空地'; variants.append(('same_ID_changed_type_evidence', value, False))
                value = deepcopy(source); value['template_id'] = 'different-public-template'; variants.append(('changed_template', value, False))
                variants.append(('changed_history_context', deepcopy(source), True))
                for label, value, historical in variants:
                    install(bound=True); panel.resident_location.setCurrentIndex(1); panel.resident_map_button.click()
                    saved_reading = snapshot()
                    tabs.setCurrentWidget(panel)
                    window.map_view.set_map(value, historical=historical)
                    require(window.map_view.reference_binding is None and window.map_view.selected is None,
                            label + '_clears_expired_reference_origin_without_rebinding')
                    require(snapshot() == saved_reading, label + '_expired_reference_does_not_replace_event_reading')
                    panel.bind_button.click()
                    require(snapshot() == saved_reading and '地图当前没有可查看' in panel.status.text(),
                            label + '_explicit_button_does_not_fallback_to_old_node_context')
                install(bound=True); panel.resident_location.setCurrentIndex(1); panel.resident_map_button.click()
                saved_reading = snapshot(); tabs.setCurrentWidget(panel)
                old_epoch = window.run.state['id']
                try:
                    window.run.state['id'] = 'public-different-run-with-same-map-IDs'
                    window.map_view.set_map(deepcopy(source), historical=False)
                    require(window.map_view.reference_binding is None and window.map_view.selected is None,
                            'new_run_same_map_IDs_cannot_reuse_reference_origin')
                    require(snapshot() == saved_reading, 'new_run_reference_expiry_does_not_auto_rebind_old_reading')
                finally:
                    window.run.state['id'] = old_epoch
                install(bound=True); later(check_fixed_stages)

            def check_fixed_stages():
                old_links = deepcopy(event_planning.event_battle_links(TARGET))
                for identity in ('ro6_t_10', 'ro6_t_11'):
                    tabs.setCurrentWidget(panel)
                    panel.resident_stage.setCurrentIndex(panel.resident_stage.findData(identity))
                    saved_reading = snapshot(); selected_position = window.map_view.selected
                    panel.resident_stage_button.click()
                    require(tabs.currentWidget() is window.battle_preview and window.battle_preview.current_stage == identity,
                            identity + '_manual_button_opens_actual_fixed_battle_preview')
                    require(window.battle_preview.grid.stage is not None and bool(window.battle_preview.grid.stage['map']),
                            identity + '_actual_fixed_battle_grid_loaded')
                    require(window.map_view.selected == selected_position and snapshot() == saved_reading,
                            identity + '_fixed_preview_does_not_change_map_position_or_event_reading')
                    save_image('fixed-' + identity)
                require(event_planning.event_battle_links(TARGET) == old_links, 'two_manual_fixed_previews_never_become_event_outcomes')
                tabs.setCurrentWidget(panel); later(check_source_failure)

            @contextmanager
            def cloned_public_source():
                manifest = json.loads((ROOT / peace_guardian_results.MANIFEST).read_bytes())
                with tempfile.TemporaryDirectory(prefix='rouge-291-public-source-') as folder:
                    clone = Path(folder)
                    for name in (peace_guardian_results.MANIFEST, *manifest['files']):
                        output = clone / name; output.parent.mkdir(parents=True, exist_ok=True)
                        output.write_bytes((ROOT / name).read_bytes())
                    html = clone / next(name for name in manifest['files'] if name.endswith('440271.html'))
                    with patch.object(peace_guardian_results, 'ROOT', clone):
                        yield html

            def check_source_failure():
                with cloned_public_source() as html:
                    raw = html.read_bytes(); panel.refresh()
                    require(peace_guardian_results.source_data() is not None, 'cloned_public_source_initially_valid')
                    panel.resident_location.setCurrentIndex(1); panel.resident_stage.setCurrentIndex(1)
                    html.write_bytes(raw + b' '); panel.refresh()
                    for name in ('resident_reference_label', 'resident_location', 'resident_map_button',
                                 'resident_stage', 'resident_stage_button'):
                        require(getattr(panel, name).isHidden(), 'invalid_source_' + name + '_hidden')
                    require(panel.resident_location.count() == 0 and panel.resident_stage.count() == 0
                            and panel.resident_reference_label.text() == '', 'invalid_source_clears_all_old_reference_data')
                    require(not panel.resident_map_button.isEnabled() and not panel.resident_stage_button.isEnabled(),
                            'invalid_source_disables_both_reference_buttons')
                    require('补充移动资料暂时无法核对' in panel.player_detail.toPlainText()
                            and original_scene['choices'][0]['conditional'] in panel.player_detail.toPlainText(),
                            'invalid_source_retains_raw_condition_and_explicit_unknown')
                    html.write_bytes(raw); panel.refresh(); defaults()
                panel.refresh(); contract()
                later(finish)

            def finish():
                nonlocal done
                isolated()
                require(source == original_source, 'public_seed_graph_not_mutated_by_reference_UI')
                require(window.run.state == initial_run, 'all_reference_interactions_leave_temporary_run_memory_unchanged')
                require(bound_files() == before, 'all_bound_public_sources_unchanged')
                observations.append({'event_id': TARGET, 'scene_key': SCENE, 'MOVE_choice': MOVE, 'VISION_choice': VISION,
                    'reference_positions': [row[0] for row in position_signals], 'manual_fixed_stage_requests': list(stage_signals),
                    'original_MapView_signal_values': list(map_signals), 'actual_current_floor_completion': None,
                    'actual_target': None, 'actual_movement': None, 'actual_battle': None,
                    'reference_positions_are_not_route_or_destination_choices': True})
                done = True

            def close_at_deadline():
                nonlocal failure
                if not done and failure is None:
                    failure = {'type': 'TimeoutError', 'message': 'Actual reference/window checks did not complete.'}
                window.close()

            later(begin, 650)
            QTimer.singleShot(max(12000, args.visible_ms), close_at_deadline)
            qt_exit = gui.exec(); closed = not window.isVisible()
            if (qt_exit != 0 or not closed or not done) and failure is None:
                failure = {'type': 'RuntimeError', 'message': 'Verification did not finish and close normally.'}
            if failure is None:
                require(all(value == 0 for value in attempts.values()),
                        'all_external_operation_attempt_counts_zero_at_actual_closure')
            after = bound_files()
            if after != before and failure is None:
                failure = {'type': 'AssertionError', 'message': 'Bound sources changed before actual window closure.'}
    except BaseException as error:
        failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}

    report = {'section': 291, 'kind': 'isolated_native_windows_resident_position_and_fixed_battle_references',
        'passed': done and failure is None, 'failure': failure, 'started_at': started,
        'finished_at': datetime.now(timezone.utc).isoformat(), 'process_id': os.getpid(), 'qpa': qpa,
        'qt_exit_code': qt_exit, 'verification_window_closed': closed,
        'checks': checks, 'unique_checks': len(checks),
        'successful_assertion_executions_including_repeated_guards': successful_executions,
        'geometry_observations': geometry, 'geometry_stages_observed': len(geometry),
        'screenshots': images, 'screenshot_count': len(images), 'public_observations': observations,
        'source_sha256_before': before, 'source_sha256_after': after,
        'state_paths_replaced_before_constructor': ['ROOT', 'SETTINGS', 'OPERATOR_STATE', 'RUN_STATE'],
        'temporary_state_root': True, 'private_state_read_copied_or_restored': False,
        'external_operation_attempts': attempts, 'game_capture_attempts': attempts['game_capture'],
        'game_captures': 0, 'game_operated': False, 'chat_sent': False,
        'chat_attempted': bool(attempts['desktop_request'] or attempts['provider_chat']),
        'external_entrypoints_blocked_before_original_call': True,
        'original_project_window_operated_or_restarted': False,
        'scope': 'Actual native HWND, three requested sizes, current/history positions, real bound-event signal path, nonzero reading-state refresh, latest-context/App stale rejection, two independent fixed battle previews and warm public-source failure. No actual MOVE target/completion or route is inferred.'}
    with destination.open('x', encoding='utf8', newline='\n') as stream:
        stream.write(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
