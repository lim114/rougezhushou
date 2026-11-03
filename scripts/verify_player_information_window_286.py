"""Actual Windows MainWindow check using only public, isolated node information.

This verifies presentation, navigation and reading-state preservation. It does
not enumerate the game, capture its screen, read private state, or send chat.
Run this reviewed script only after the section's source has been frozen.
"""
import argparse
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

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'rouge/app.py').is_file())
sys.path.insert(0, str(ROOT))


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--receipt', required=True)
    parser.add_argument('--visible-ms', type=int, default=120000)
    args = parser.parse_args()
    destination = Path(args.receipt).resolve()
    if destination.exists():
        raise FileExistsError('Preserve the original actual receipt; choose a new path.')
    if args.visible_ms <= 0:
        raise ValueError('--visible-ms must be positive.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    screenshot_paths = [destination.with_name(destination.stem + suffix) for suffix in (
        '-01-node-player.png', '-02-node-evidence.png',
        '-03-battle-rewards.png', '-04-battle-technical.png',
    )]
    for path in screenshot_paths:
        if path.exists():
            raise FileExistsError('Preserve the original actual screenshot: ' + str(path))

    before = {}
    completed = []
    assertion_executions = 0
    stages = []
    observations = []
    report = None
    failure = None
    window_closed = False
    qpa = None
    started = datetime.now(timezone.utc).isoformat()

    def require(condition, name):
        nonlocal assertion_executions
        if not condition:
            raise AssertionError(name)
        assertion_executions += 1
        if name not in completed:
            completed.append(name)

    def write(data):
        # Exclusive creation preserves first-run failures and prevents a race
        # from replacing an earlier report with a later green result.
        with destination.open('xb') as stream:
            stream.write((json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf8'))

    try:
        if sys.platform != 'win32':
            raise RuntimeError('Original Windows is required; Wine/offscreen is not native validation.')
        if Path(__file__).resolve() != (ROOT / 'scripts/verify_player_information_window_286.py').resolve():
            raise RuntimeError('Run the canonical reviewed script in scripts/, not a cache substitute.')

        from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QTimer
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QApplication
        import win32gui
        import win32process
        from rouge import app as app_module
        from rouge import map_view as map_module
        from rouge.battle_reward_planning import reward_source_text
        from tests.test_route_information_scope import (
            public_information_graph, REMOVED_ATTRIBUTES, REMOVED_TABS,
        )

        files = (
            'rouge/app.py', 'rouge/ui_state.py', 'rouge/map_view.py', 'rouge/map_reporting.py',
            'rouge/node_catalog.py', 'rouge/node_catalog_view.py', 'rouge/player_node_information.py',
            'rouge/event_planning.py', 'rouge/original_destinations.py',
            'rouge/battle_preview.py', 'rouge/battle_view.py', 'rouge/battle_reward_planning.py',
            'rouge/base_settlement_planning.py', 'rouge/rare_reward_sources.py',
            'rouge/data/node-catalog.json', 'rouge/data/node-events.json',
            'rouge/data/original-entry-reference.json', 'rouge/data/battle-previews.json',
            'rouge/data/battle-reward-reference.json',
            'tests/test_route_information_scope.py',
            'tests/test_player_node_information_286.py',
            'tests/test_player_battle_information_286.py',
            'tests/test_player_information_view_286.py',
            'scripts/verify_player_information_window_286.py',
        )
        before = {name: _sha(ROOT / name) for name in files}
        gui = QApplication([])
        qpa = gui.platformName()
        require(qpa == 'windows', 'actual_windows_qpa')

        class PublicWindow(app_module.MainWindow):
            def refresh_windows(self):
                # This covers constructor enumeration as well as refreshes.
                self.windows.clear()

        def forbidden_enumeration(*_args, **_kwargs):
            raise AssertionError('Game enumeration is forbidden in this public fixture.')

        def forbidden_route(*_args, **_kwargs):
            raise AssertionError('Route recommendation calculation is forbidden in the product fixture.')

        with tempfile.TemporaryDirectory(prefix='rouge-286-player-information-') as state, \
                patch.object(app_module, 'list_game_windows', side_effect=forbidden_enumeration), \
                patch.object(map_module, 'route_reference', side_effect=forbidden_route):
            temp = Path(state)
            # All four paths are replaced before MainWindow construction. No
            # original JSON or chat binding is parsed, copied or restored.
            app_module.ROOT = temp
            app_module.SETTINGS = temp / 'settings.json'
            app_module.OPERATOR_STATE = temp / 'operators.json'
            app_module.RUN_STATE = temp / 'run.json'
            w = PublicWindow()
            w.setWindowTitle('第286节 · 玩家节点说明、资料与固定作战预览（公开隔离验收）')
            w.resize(1460, 1000)
            w.show()
            tabs = w.centralWidget()
            panel = w.node_catalog
            battle = w.battle_preview
            expected_graph = None
            saved = None
            done = False

            def isolated():
                require(not w.auto.isChecked(), 'automatic_game_sampling_disabled')
                require(not w.timer.isActive(), 'game_sampling_timer_inactive')
                require(w.capture.target is None, 'no_game_capture_target')
                require(w.desktop.process is None, 'desktop_chat_backend_not_started')

            def native_window():
                handle = int(w.winId())
                thread, process = win32process.GetWindowThreadProcessId(handle)
                require(bool(win32gui.IsWindow(handle)), 'actual_win32_hwnd_exists')
                require(bool(win32gui.IsWindowVisible(handle)) and w.isVisible(), 'actual_win32_hwnd_visible')
                require(process == os.getpid(), 'actual_win32_hwnd_owned_by_verification_process')
                require(not bool(win32gui.IsIconic(handle)), 'verification_window_not_minimized')
                return {'hwnd': handle, 'process_id': process, 'thread_id': thread,
                        'visible': True, 'minimized': False, 'caption': win32gui.GetWindowText(handle),
                        'rectangle': list(win32gui.GetWindowRect(handle)), 'qpa': qpa}

            def reading(widget):
                cursor = widget.textCursor()
                return {'text_sha256': hashlib.sha256(widget.toPlainText().encode('utf8')).hexdigest(),
                        'anchor': cursor.anchor(), 'position': cursor.position(),
                        'selected_text': cursor.selectedText(),
                        'vertical': widget.verticalScrollBar().value(),
                        'horizontal': widget.horizontalScrollBar().value()}

            def prime_reading(widget, label):
                # Use actual formatter text and the real viewport. Do not add
                # padding merely to manufacture a nonzero scroll assertion.
                text = widget.toPlainText()
                require(len(text) > 20, label + '_actual_text_available')
                cursor = widget.textCursor()
                cursor.setPosition(1)
                cursor.setPosition(8, QTextCursor.MoveMode.KeepAnchor)
                widget.setTextCursor(cursor)
                gui.processEvents()
                bar = widget.verticalScrollBar()
                require(bar.maximum() > 0, label + '_actual_scroll_range_nonzero')
                bar.setValue(max(1, bar.maximum() // 2))
                gui.processEvents()
                current = reading(widget)
                require(current['vertical'] > 0, label + '_actual_scroll_position_nonzero')
                require(current['anchor'] != current['position'] and bool(current['selected_text']),
                        label + '_actual_text_selection_nonempty')
                return current

            def node_snapshot():
                return {'main_tab': tabs.currentIndex(), 'reading_tab': panel.reading_tabs.currentIndex(),
                        'key': panel.detail_key, 'list_selection': panel.list.selected_key(),
                        'expanded_groups': sorted(panel.list.expanded_groups()),
                        'event_stage': panel.event_stage.currentData(),
                        'map_location': deepcopy(panel.map_location.currentData()),
                        'player': reading(panel.player_detail), 'evidence': reading(panel.detail)}

            def battle_snapshot():
                return {'main_tab': tabs.currentIndex(), 'stage': battle.current_stage,
                        'technical': battle.technical.isChecked(),
                        'detail_key': battle._detail_key,
                        'reward': deepcopy(battle.reward_combo.currentData()),
                        'wave': battle.wave_combo.currentData(),
                        'enemy': deepcopy(battle.enemy_combo.currentData()),
                        'spawn_detail': reading(battle.spawn_detail)}

            def graph_unchanged():
                require(w.run.state['maps']['zone_1'] == expected_graph, 'public_graph_unchanged')
                require(w.map_view.route()['status'] == 'information_only', 'map_is_information_only')
                require(w.map_view.route()['display_path'] == [], 'map_has_no_selected_or_recommended_route')

            def image(stage, filename, observed):
                isolated()
                native = native_window()
                pixmap = w.grab()
                require(not pixmap.isNull(), stage + '_actual_widget_pixels_available')
                image_bytes = QByteArray()
                buffer = QBuffer(image_bytes)
                require(buffer.open(QIODevice.OpenModeFlag.WriteOnly), stage + '_image_buffer_opened')
                require(bool(pixmap.save(buffer, 'PNG')), stage + '_actual_png_encoded')
                buffer.close()
                # PNGs, like receipts, are exclusive actual artifacts. Another
                # run using this path must fail rather than replace pixels.
                with filename.open('xb') as stream:
                    stream.write(bytes(image_bytes))
                require(filename.stat().st_size > 0, stage + '_actual_screenshot_saved')
                stages.append({'stage': stage, 'observed_at': datetime.now(timezone.utc).isoformat(),
                               'native_window': native, 'screenshot': str(filename),
                               'screenshot_sha256': _sha(filename),
                               'width': pixmap.width(), 'height': pixmap.height(),
                               'observed_reading_state': deepcopy(observed)})

            def fail(error):
                nonlocal failure, done
                if failure is None:
                    failure = {'type': type(error).__name__, 'message': str(error),
                               'traceback': traceback.format_exc()}
                done = True
                w.close()
                gui.exit(1)

            def guarded(callback):
                def execute():
                    try:
                        isolated()
                        callback()
                    except BaseException as error:
                        fail(error)
                return execute

            def later(callback, ms=300):
                QTimer.singleShot(ms, guarded(callback))

            def node_player():
                nonlocal expected_graph, saved
                labels = {tabs.tabText(i) for i in range(tabs.count())}
                require(not labels.intersection(REMOVED_TABS), 'removed_route_recommendation_tabs_absent')
                require(all(not hasattr(w, name) for name in REMOVED_ATTRIBUTES),
                        'removed_route_recommendation_instances_absent')
                expected_graph = public_information_graph()
                expected_graph['captured_at'] = w.run.state['started_at'] + 1
                w.run.state['maps']['zone_1'] = deepcopy(expected_graph)
                w.run.state['config']['zone'] = {'id': 'zone_1'}
                w.render_map()
                w.map_view.select_node('b')
                tabs.setCurrentWidget(panel)
                panel.bind_button.click()
                index = next(i for i, entry in enumerate(panel.entries)
                             if entry['kind'] == 'event' and entry['title'] == '思乡心切'
                             and entry.get('history_read'))
                panel.list.setCurrentRow(index)
                require(panel.reading_tabs.count() == 2, 'two_actual_node_reading_pages')
                require([panel.reading_tabs.tabText(i) for i in range(2)] == ['玩家说明', '资料与依据'],
                        'node_reading_pages_have_player_and_evidence_labels')
                panel.reading_tabs.setCurrentWidget(panel.player_detail)
                require(panel.event_stage.findData('ro6_t_1') >= 0, 'historical_event_fixed_battle_link_retained')
                panel.event_stage.setCurrentIndex(panel.event_stage.findData('ro6_t_1'))
                require(panel.battle_button.isEnabled() and panel.map_jump.isEnabled(),
                        'actual_fixed_battle_and_exact_map_return_buttons_enabled')
                text = panel.player_detail.toPlainText()
                require('思乡心切' in text and '历史' in text, 'player_page_identifies_historical_event')
                require('不使用当前' in text and '未知' in text, 'player_page_keeps_historical_resources_and_unknown_separate')
                require('对应作战' in text, 'player_page_explains_corresponding_battle_entry')
                require('https://' not in text and 'http://' not in text and 'ro6_t_1' not in text,
                        'player_page_omits_source_urls_and_raw_stage_identifier')
                require(text != panel.detail.toPlainText(), 'player_summary_and_complete_evidence_are_distinct')
                panel.expand_button.click()
                require(bool(panel.list.expanded_groups()), 'node_type_branches_really_expand')
                later(prime_player)

            def prime_player():
                nonlocal saved
                prime_reading(panel.player_detail, 'node_player')
                saved = node_snapshot()
                panel.refresh()
                w.render_map()
                later(check_player)

            def check_player():
                require(node_snapshot() == saved, 'node_player_refresh_preserves_tab_selection_nonzero_scroll_and_text_selection')
                graph_unchanged()
                image('node_player', screenshot_paths[0], saved)
                panel.reading_tabs.setCurrentWidget(panel.detail)
                panel.collapse_button.click()
                later(prime_evidence)

            def prime_evidence():
                nonlocal saved
                text = panel.detail.toPlainText()
                require('思乡心切' in text and ('https://' in text or 'http://' in text),
                        'evidence_page_retains_complete_source_links')
                require(not panel.list.expanded_groups(), 'node_type_branches_really_collapse')
                prime_reading(panel.detail, 'node_evidence')
                saved = node_snapshot()
                panel.refresh()
                w.render_map()
                later(check_evidence)

            def check_evidence():
                require(node_snapshot() == saved, 'node_evidence_refresh_preserves_tab_selection_nonzero_scroll_and_text_selection')
                graph_unchanged()
                image('node_evidence', screenshot_paths[1], saved)
                panel.battle_button.click()
                later(event_battle, 500)

            def event_battle():
                require(tabs.currentWidget() is battle, 'event_button_navigates_to_actual_battle_preview')
                require(w.target_stage.currentData() == battle.current_stage == 'ro6_t_1',
                        'event_button_loads_exact_fixed_battle')
                require(bool(battle.rows), 'event_battle_has_actual_fixed_spawn_rows')
                observations.append({'event': '思乡心切', 'historical_reference': True,
                                     'preview_stage': battle.current_stage,
                                     'actual_spawn_claimed': False, 'native_window': native_window()})
                tabs.setCurrentWidget(panel)
                panel.map_jump.click()
                later(map_return)

            def map_return():
                require(tabs.currentWidget() is w.exploration_map_tab and w.map_view.selected == 'b',
                        'event_returns_to_exact_public_map_node')
                graph_unchanged()
                require(panel.reading_tabs.currentWidget() is panel.detail,
                        'node_evidence_tab_survives_battle_navigation')
                w.show_catalog_battle('ro6_n_1_2')
                battle.technical.setChecked(False)
                battle.reward_summary.click()
                later(prime_rewards, 500)

            def prime_rewards():
                nonlocal saved
                require(tabs.currentWidget() is battle and battle.current_stage == 'ro6_n_1_2',
                        'reward_preview_uses_declared_fixed_stage')
                require(battle.reward_result is not None, 'fixed_reward_source_available')
                require(battle.reward_result['actual_reward_total'] is None,
                        'actual_reward_total_remains_unknown')
                require(battle.reward_result['probability'] is None,
                        'no_reward_generation_probability_invented')
                require(battle.reward_result['complete_settlement_pool_known'] is False,
                        'complete_settlement_pool_not_claimed')
                text = battle.spawn_detail.toPlainText()
                require(text == reward_source_text(battle.reward_result, technical=False),
                        'actual_reward_button_displays_current_player_formatter')
                require('本关实际奖励总量与完整结算池：未知' in text and '不同候选' in text,
                        'reward_page_keeps_conditions_and_unknown_total_visible')
                require('https://' not in text and '原关卡来源' not in text,
                        'player_reward_view_omits_technical_source_appendix')
                require(not battle.source_label.isVisible(), 'technical_source_label_initially_hidden')
                prime_reading(battle.spawn_detail, 'battle_rewards')
                saved = battle_snapshot()
                battle.render_rows()
                w.render_map()
                later(check_rewards)

            def check_rewards():
                require(battle_snapshot() == saved,
                        'reward_refresh_preserves_main_tab_stage_technical_flag_selection_and_nonzero_scroll')
                graph_unchanged()
                image('battle_rewards', screenshot_paths[2], saved)
                battle.technical.setChecked(True)
                later(prime_technical, 400)

            def prime_technical():
                nonlocal saved
                require(battle.technical.isChecked() and battle.source_label.isVisible(),
                        'technical_switch_reveals_actual_source_label')
                text = battle.spawn_detail.toPlainText()
                require(text == reward_source_text(battle.reward_result, technical=True),
                        'technical_switch_uses_technical_reward_formatter')
                require('原关卡来源' in text and ('https://' in text or 'http://' in text),
                        'technical_reward_view_preserves_public_source_appendix')
                require('本关实际奖励总量与完整结算池：未知' in text,
                        'technical_reward_view_does_not_promote_unknown_total')
                prime_reading(battle.spawn_detail, 'battle_technical')
                saved = battle_snapshot()
                battle.render_rows()
                w.render_map()
                later(check_technical)

            def check_technical():
                nonlocal done, report
                require(battle_snapshot() == saved,
                        'technical_reward_refresh_preserves_selected_mode_text_selection_and_nonzero_scroll')
                graph_unchanged()
                image('battle_technical', screenshot_paths[3], saved)
                require(len(stages) == 4, 'all_four_actual_visible_stage_screenshots_saved')
                require({name: _sha(ROOT / name) for name in files} == before,
                        'bound_public_source_unchanged_during_window_checks')
                done = True
                report = {'passed': True,
                          'actual_windows_mainwindow': True,
                          'four_stage_screenshots_are_own_public_window_only': True,
                          'game_enumeration_guard_installed_before_constructor': True,
                          'state_paths_replaced_before_constructor': ['ROOT', 'SETTINGS', 'OPERATOR_STATE', 'RUN_STATE'],
                          'public_graph_unchanged': True,
                          'player_and_evidence_pages_exercised': True,
                          'historical_event_fixed_battle_and_exact_map_return_exercised': True,
                          'reward_summary_and_technical_switch_exercised': True,
                          'refresh_checks_used_actual_nonzero_scroll_and_nonempty_selection': True}

            def close_at_deadline():
                nonlocal failure, done
                if not done:
                    failure = {'type': 'TimeoutError', 'message': 'Actual window checks did not finish before deadline.'}
                    done = True
                w.close()

            later(node_player, 600)
            QTimer.singleShot(max(10000, args.visible_ms), close_at_deadline)
            code = gui.exec()
            window_closed = not w.isVisible()
            if not window_closed and failure is None:
                failure = {'type': 'RuntimeError', 'message': 'Verification GUI returned while its window remained visible.'}
            if not done and failure is None:
                failure = {'type': 'RuntimeError', 'message': 'Window closed before all actual stages completed.'}
            if code != 0 and failure is None:
                failure = {'type': 'RuntimeError', 'message': 'Qt returned nonzero exit: ' + str(code)}
            after = {name: _sha(ROOT / name) for name in files}
            if after != before and failure is None:
                failure = {'type': 'AssertionError', 'message': 'Bound public source changed before process closure.'}
            if failure is None and report is None:
                failure = {'type': 'RuntimeError', 'message': 'No completed actual verification report.'}
            if report is None:
                report = {}
            report.update({'source_sha256_after': after, 'qt_exit_code': code})
    except BaseException as error:
        failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
        if report is None:
            report = {}

    if failure is not None:
        report['passed'] = False
        report['failure'] = failure
    report.update({
        'section': 286, 'kind': 'isolated_public_windows_mainwindow',
        'started_at': started, 'finished_at': datetime.now(timezone.utc).isoformat(),
        'qpa': qpa, 'process_id': os.getpid(), 'window_closed': window_closed,
        'completed_checks': completed, 'completed_check_count': len(completed),
        'successful_assertion_executions_including_repeated_safety_guards': assertion_executions,
        'visible_stages': stages, 'public_observations': observations,
        'loaded_source_sha256': before, 'private_state_read': False,
        'private_files_copied_or_restored': False, 'temporary_state_root': True,
        'game_operated': False, 'game_captures': 0, 'chat_sent': False,
        'original_project_test_window_restarted': False,
        'scope': 'Actual native Windows MainWindow, public declared graph and fixed node/battle references only. No current game screen, current run inventory, chat integration, server eligibility, actual reward or complete settlement is certified.',
    })
    write(report)
    return 0 if report.get('passed') is True else 1


if __name__ == '__main__':
    raise SystemExit(main())
