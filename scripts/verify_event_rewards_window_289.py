"""Native isolated MainWindow: two documented named rewards, never grants.

No real game, private state, chat or inventory is read. Run only the canonical
reviewed script after the section's source and necessary tests are frozen.
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
PACKET = ROOT / 'research/p3-event-named-rewards-289'
TARGET = 'community_group_007'
SCENE = TARGET + ':scene:0'
CHOICES = (SCENE + ':choice:0', SCENE + ':choice:1')
TITLES = ('清理门上的人形藤蔓', '试图和人形藤蔓交流')
ORIGINAL_IDS = ('choice_ro6_normal1_1', 'choice_ro6_normal1_2')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--receipt', required=True)
    parser.add_argument('--visible-ms', type=int, default=120000)
    args = parser.parse_args()
    destination = Path(args.receipt).resolve()
    if destination.exists():
        raise FileExistsError('Preserve the first actual receipt; use a new path.')
    if args.visible_ms <= 0:
        raise ValueError('--visible-ms must be positive.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    screenshots = [destination.with_name(destination.stem + suffix)
                   for suffix in ('-01-player.png', '-02-evidence.png')]
    for image in screenshots:
        if image.exists():
            raise FileExistsError('Preserve the first actual screenshot: ' + str(image))
    checks, stages, observations = [], [], []
    executions = 0
    before, after = {}, {}
    qpa, failure, qt_exit = None, None, None
    done, closed = False, False
    started = datetime.now(timezone.utc).isoformat()

    def require(condition, name):
        nonlocal executions
        if not condition:
            raise AssertionError(name)
        executions += 1
        if name not in checks:
            checks.append(name)

    def bound_files():
        files = {
            'rouge/app.py', 'rouge/ui_state.py', 'rouge/node_catalog.py',
            'rouge/node_catalog_view.py', 'rouge/player_node_information.py',
            'rouge/event_planning.py', 'rouge/node_rewards.py',
            'rouge/event_named_reward_links.py',
            'rouge/data/event-named-reward-links.json',
            'rouge/data/node-catalog.json', 'rouge/data/node-reward-reference.json',
            'rouge/data/node-events.json', 'rouge/data/original-entry-reference.json',
            'scripts/build_event_named_reward_links_289.py',
            'scripts/verify_event_rewards_window_289.py',
        }
        if not PACKET.is_dir():
            raise FileNotFoundError('The reviewed public source packet has not been promoted.')
        for path in PACKET.rglob('*'):
            if path.is_symlink():
                raise ValueError('The public source packet must contain regular original files.')
            if path.is_file():
                files.add(path.relative_to(ROOT).as_posix())
        tests = sorted((ROOT / 'tests').glob('test_*289*.py'))
        if not tests:
            raise FileNotFoundError('Section289 necessary tests must be present before this window check.')
        files.update(path.relative_to(ROOT).as_posix() for path in tests)
        return {name: sha(ROOT / name) for name in sorted(files)}

    try:
        if sys.platform != 'win32':
            raise RuntimeError('Original Windows is required; Wine/offscreen is not native validation.')
        if Path(__file__).resolve() != (ROOT / 'scripts/verify_event_rewards_window_289.py').resolve():
            raise RuntimeError('Use the canonical reviewed script in scripts/.')
        from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QTimer
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QApplication
        import win32gui
        import win32process
        from rouge import app as app_module
        from rouge import node_catalog as catalog
        from rouge import event_planning
        from rouge.event_named_reward_links import source_data

        before = bound_files()
        require(source_data() is not None, 'fresh_supplemental_source_packet_valid')
        original_event = deepcopy(catalog._event(TARGET))
        original_choices = original_event['scenes'][0]['choices'][:2]
        require([row['key'] for row in original_choices] == list(CHOICES), 'two_exact_community_choices')
        require(all(row['game_choice_ids'] == [] for row in original_choices),
                'original_two_game_choice_id_lists_are_empty')
        gui = QApplication([])
        qpa = gui.platformName()
        require(qpa == 'windows', 'actual_native_windows_qpa')

        class PublicWindow(app_module.MainWindow):
            def refresh_windows(self):
                self.windows.clear()

        def forbidden(*_args, **_kwargs):
            raise AssertionError('Game enumeration is forbidden in this public fixture.')

        with tempfile.TemporaryDirectory(prefix='rouge-289-event-rewards-') as directory, \
                patch.object(app_module, 'list_game_windows', side_effect=forbidden):
            temporary = Path(directory)
            app_module.ROOT = temporary
            app_module.SETTINGS = temporary / 'settings.json'
            app_module.OPERATOR_STATE = temporary / 'operators.json'
            app_module.RUN_STATE = temporary / 'run.json'
            window = PublicWindow()
            window.setWindowTitle('第289节 · 沉寂之屋两项奖励与独立费用（公开隔离验收）')
            window.resize(1440, 930)
            window.show()
            panel, tabs = window.node_catalog, window.centralWidget()
            saved = None
            baseline_qualifications = None
            isolated_run = deepcopy(window.run.state)

            def isolated():
                require(not window.auto.isChecked(), 'automatic_game_sampling_disabled')
                require(not window.timer.isActive(), 'game_sampling_timer_inactive')
                require(window.capture.target is None, 'no_game_capture_target')
                require(window.desktop.process is None, 'desktop_chat_backend_not_started')

            def native_window():
                handle = int(window.winId())
                thread, process = win32process.GetWindowThreadProcessId(handle)
                require(bool(win32gui.IsWindow(handle)), 'actual_win32_hwnd_exists')
                require(bool(win32gui.IsWindowVisible(handle)) and window.isVisible(), 'actual_win32_hwnd_visible')
                require(process == os.getpid(), 'actual_win32_hwnd_owned_by_fixture_process')
                require(not bool(win32gui.IsIconic(handle)), 'verification_window_not_minimized')
                return {'hwnd': handle, 'process_id': process, 'thread_id': thread,
                        'visible': True, 'caption': win32gui.GetWindowText(handle),
                        'rectangle': list(win32gui.GetWindowRect(handle)), 'qpa': qpa}

            def reading(widget):
                cursor = widget.textCursor()
                return {'text_sha256': hashlib.sha256(widget.toPlainText().encode('utf8')).hexdigest(),
                        'anchor': cursor.anchor(), 'position': cursor.position(),
                        'selected_text': cursor.selectedText(),
                        'vertical': widget.verticalScrollBar().value(),
                        'horizontal': widget.horizontalScrollBar().value()}

            def filters_and_selection():
                return {'main_tab': tabs.currentIndex(), 'reading_tab': panel.reading_tabs.currentIndex(),
                        'kind': panel.kind.currentData(), 'node_type': panel.node_type.currentData(),
                        'floor': panel.floor.currentData(), 'search_text': panel.search.text(),
                        'search_cursor': panel.search.cursorPosition(),
                        'search_selection_start': panel.search.selectionStart(),
                        'search_selected_text': panel.search.selectedText(),
                        'selected_key': panel.list.selected_key(), 'detail_key': panel.detail_key,
                        'expanded_groups': sorted(panel.list.expanded_groups()),
                        'tree_scroll': panel.list.verticalScrollBar().value()}

            def snapshot():
                return {**filters_and_selection(), 'player': reading(panel.player_detail),
                        'evidence': reading(panel.detail),
                        'runtime_context': deepcopy(panel.runtime_context)}

            def prime(widget, label):
                require(widget.document().characterCount() > 30, label + '_real_formatter_text_available')
                cursor = widget.textCursor()
                cursor.setPosition(1)
                cursor.setPosition(8, QTextCursor.MoveMode.KeepAnchor)
                widget.setTextCursor(cursor)
                panel.search.setSelection(0, 2)
                gui.processEvents()
                bar = widget.verticalScrollBar()
                require(bar.maximum() > 0, label + '_actual_scroll_range_nonzero')
                bar.setValue(max(1, bar.maximum() // 2))
                gui.processEvents()
                require(bar.value() > 0 and bool(widget.textCursor().selectedText()),
                        label + '_actual_nonzero_scroll_and_nonempty_text_selection')
                require(bool(panel.search.selectedText()), label + '_actual_search_text_selection')

            def selected_entry():
                entry = next(row for row in panel.entries if row['key'] == panel.list.selected_key())
                require(entry['kind'] == 'event' and entry['record']['id'] == TARGET,
                        'actual_directory_selection_is_exact_event_group')
                return entry

            def reward_contract():
                result = catalog.event_reward_options(TARGET)
                require(result['supplemental_reward_reference']['status'] == 'documented_reference',
                        'actual_catalog_uses_documented_supplemental_links')
                require(result['inventory_updated'] is False and result['full_reward_pool_known'] is False,
                        'named_references_do_not_update_inventory_or_claim_complete_pool')
                rows = {row['choice_id']: row for row in result['rows']}
                for index, key in enumerate(CHOICES):
                    row = rows[key]
                    require(len(row['rewards']) == 1, 'each_independent_option_has_one_named_reference')
                    reference = row['rewards'][0]
                    require(reference['choice_id'] == ORIGINAL_IDS[index]
                            and reference['reference_kind'] == 'documented_choice_content_link',
                            'reward_is_exact_document_content_reference')
                    require(reference['reward']['name'] == '笼控器'
                            and reference['reward']['type'] == 'SCRAP'
                            and reference['reward']['quantity'] is None,
                            'named_scrap_identity_is_known_but_quantity_unknown')
                    require(reference['actual_claim_eligible'] is None and reference['actual_reward'] is None
                            and reference['source_scene_link_verified'] is False,
                            'actual_claim_and_original_source_scene_remain_unverified')
                    cost = reference['documented_cost_reference']
                    require((cost['resource'], cost['quantity']) == (('hp', 2) if index == 0 else ('gold', 8))
                            and cost['actual_payment'] is None,
                            'documented_costs_belong_to_separate_options')
                    require(reference['source_reference']['original_item_pointer'] ==
                            '$.details.rogue_6.choices.' + ORIGINAL_IDS[index] + '.displayData.itemId',
                            'documented_item_pointer_is_exact')
                require(catalog._event(TARGET) == original_event, 'original_catalog_and_empty_choice_ids_unchanged')
                return result

            def player_contract():
                text = panel.player_detail.toPlainText()
                markers = ('选项 1：' + TITLES[0], '选项 2：' + TITLES[1], '选项 3：离开')
                require(all(marker in text for marker in markers), 'player_page_retains_three_independent_choices')
                first = text.split(markers[0], 1)[1].split(markers[1], 1)[0]
                second = text.split(markers[1], 1)[1].split(markers[2], 1)[0]
                require('费用：2目标生命值（原文明示数量）' in first
                        and '费用：8源石锭（原文明示数量）' not in first,
                        'first_option_has_only_its_own_hp_cost')
                require('费用：8源石锭（原文明示数量）' in second
                        and '费用：2目标生命值（原文明示数量）' not in second,
                        'second_option_has_only_its_own_gold_cost')
                reward = '具名奖励（零件）：笼控器；数量未确认；实际领取未知。'
                require(first.count(reward) == second.count(reward) == 1,
                        'each_option_shows_scrap_type_unknown_quantity_and_unknown_receipt')
                require('入场费' not in text, 'independent_costs_are_not_presented_as_combined_entry_fee')
                require(not any(value in text for value in
                        ('http://', 'https://', 'choice_ro6_', 'scene_ro6_', 'rogue_6_scrap_G_12', 'community_group_')),
                        'player_page_hides_raw_ids_and_document_urls')
                require('实际可选仍未知' in first and '实际可选仍未知' in second,
                        'documented_reward_does_not_upgrade_actual_option_availability')
                return text

            def image(name, path):
                isolated()
                native = native_window()
                pixels = window.grab()
                require(not pixels.isNull(), name + '_actual_own_window_pixels_available')
                data = QByteArray()
                buffer = QBuffer(data)
                require(buffer.open(QIODevice.OpenModeFlag.WriteOnly), name + '_png_buffer_open')
                require(bool(pixels.save(buffer, 'PNG')), name + '_actual_png_encoded')
                buffer.close()
                with path.open('xb') as stream:
                    stream.write(bytes(data))
                stages.append({'name': name, 'native_window': native, 'screenshot': str(path),
                               'screenshot_sha256': sha(path), 'reading_state': snapshot()})

            def fail(error):
                nonlocal failure, done
                if failure is None:
                    failure = {'type': type(error).__name__, 'message': str(error),
                               'traceback': traceback.format_exc()}
                done = True
                window.close()
                gui.exit(1)

            def later(callback, delay=350):
                def guarded():
                    try:
                        isolated()
                        callback()
                    except BaseException as error:
                        fail(error)
                QTimer.singleShot(delay, guarded)

            def begin():
                nonlocal baseline_qualifications
                tabs.setCurrentWidget(panel)
                panel.set_map_context(None, runtime_context={'resources': {'hp': 2, 'gold': 8}})
                panel.kind.setCurrentIndex(panel.kind.findData('event'))
                panel.node_type.setCurrentIndex(panel.node_type.findData('不期而遇'))
                panel.floor.setCurrentIndex(panel.floor.findData(1))
                panel.search.setText('沉寂之屋')
                index = next(i for i, entry in enumerate(panel.entries)
                             if entry['kind'] == 'event' and entry['record']['id'] == TARGET)
                panel.list.setCurrentRow(index)
                panel.reading_tabs.setCurrentWidget(panel.player_detail)
                entry = selected_entry()
                resource_rows = event_planning.choice_resources(TARGET, SCENE, panel._event_context(entry['record']))['rows']
                baseline_qualifications = {row['choice_key']: deepcopy(row['choice_eligibility']) for row in resource_rows}
                reward_contract()
                player_contract()
                later(prime_player)

            def prime_player():
                nonlocal saved
                prime(panel.player_detail, 'player_page')
                saved = snapshot()
                panel.refresh()
                later(check_player)

            def check_player():
                require(snapshot() == saved, 'player_refresh_preserves_filters_selection_tab_text_selection_and_nonzero_scroll')
                reward_contract()
                player_contract()
                image('player', screenshots[0])
                panel.reading_tabs.setCurrentWidget(panel.detail)
                later(prime_evidence)

            def prime_evidence():
                nonlocal saved
                text = panel.detail.toPlainText()
                require('完整选项文字和物品指针相符' in text and 'displayData.itemId' in text,
                        'evidence_page_exposes_full_content_link_and_original_item_pointer')
                require('https://wiki.biligame.com/arknights/' in text and '349818' in text and '427904' in text,
                        'evidence_page_exposes_attributed_document_and_fixed_revisions')
                require(all(value in text for value in ORIGINAL_IDS), 'evidence_page_keeps_two_distinct_original_references')
                prime(panel.detail, 'evidence_page')
                saved = snapshot()
                panel.refresh()
                later(check_evidence)

            def check_evidence():
                require(snapshot() == saved, 'evidence_refresh_preserves_filters_selection_tab_text_selection_and_nonzero_scroll')
                reward_contract()
                image('evidence', screenshots[1])
                panel.set_map_context(None, runtime_context={'resources': {'hp': 0, 'gold': 0}})
                later(check_low_resources)

            def check_low_resources():
                nonlocal done
                entry = selected_entry()
                require(panel.reading_tabs.currentWidget() is panel.detail
                        and panel.kind.currentData() == 'event' and panel.node_type.currentData() == '不期而遇'
                        and panel.floor.currentData() == 1 and panel.search.text() == '沉寂之屋',
                        'resource_update_keeps_actual_directory_filters_and_selected_page')
                resource_rows = event_planning.choice_resources(TARGET, SCENE, panel._event_context(entry['record']))['rows']
                actual_qualifications = {row['choice_key']: row['choice_eligibility'] for row in resource_rows}
                require(actual_qualifications == baseline_qualifications,
                        'insufficient_budget_does_not_upgrade_or_exclude_choice_qualification')
                costs = {row['choice_key']: row['resource_references'] for row in resource_rows}
                for key in CHOICES:
                    require(len(costs[key]) == 1 and costs[key][0]['kind'] == 'nominal_cost'
                            and costs[key][0]['nominal_budget_covers'] is False
                            and costs[key][0]['actual_changed'] is None,
                            'insufficient_budget_remains_separate_from_actual_payment')
                reward_contract()
                text = player_contract()
                require(text.count('已知资源不足这项费用') == 2,
                        'actual_player_text_keeps_both_reward_references_when_resources_are_insufficient')
                require(window.run.state == isolated_run, 'declared_directory_resources_do_not_mutate_run_memory')
                require(source_data() is not None, 'source_packet_remains_freshly_valid_at_completion')
                require(bound_files() == before, 'bound_source_unchanged_during_both_actual_pages')
                require(len(stages) == 2, 'both_actual_native_page_screenshots_saved')
                observations.append({'low_resource_context': {'hp': 0, 'gold': 0},
                    'documented_reward_references_retained': 2, 'quantity_inferred': False,
                    'choice_qualifications_changed': False, 'inventory_updated': False,
                    'game_choice_ids_filled': False, 'actual_receipt_certified': False})
                done = True

            def close_at_deadline():
                nonlocal failure
                if not done:
                    failure = {'type': 'TimeoutError', 'message': 'Both actual event reward pages did not complete.'}
                window.close()

            later(begin, 650)
            QTimer.singleShot(max(12000, args.visible_ms), close_at_deadline)
            qt_exit = gui.exec()
            closed = not window.isVisible()
            if not done and failure is None:
                failure = {'type': 'RuntimeError', 'message': 'Window closed before all event checks completed.'}
            if (qt_exit != 0 or not closed) and failure is None:
                failure = {'type': 'RuntimeError', 'message': 'The actual verification window did not close normally.'}
            after = bound_files()
            if after != before and failure is None:
                failure = {'type': 'AssertionError', 'message': 'Bound public source changed before window closure.'}
    except BaseException as error:
        failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}

    report = {'section': 289, 'kind': 'isolated_native_windows_documented_event_rewards',
              'passed': done and failure is None, 'failure': failure,
              'started_at': started, 'finished_at': datetime.now(timezone.utc).isoformat(),
              'qpa': qpa, 'process_id': os.getpid(), 'qt_exit_code': qt_exit,
              'verification_window_closed': closed,
              'checks': checks, 'unique_checks': len(checks),
              'successful_assertion_executions_including_repeated_guards': executions,
              'visible_stages': stages, 'public_observations': observations,
              'source_sha256_before': before, 'source_sha256_after': after,
              'state_paths_replaced_before_constructor': ['ROOT', 'SETTINGS', 'OPERATOR_STATE', 'RUN_STATE'],
              'private_state_read_or_copied': False, 'temporary_state_root': True,
              'game_operated': False, 'game_captures': 0, 'chat_sent': False,
              'original_project_window_operated_or_restarted': False,
              'scope': 'Two actual native MainWindow directory pages with public declared resources. Full document-content reward corroboration only; no original source-scene link, server option availability, actual payment, reward quantity or received item is certified.'}
    with destination.open('x', encoding='utf8', newline='\n') as stream:
        stream.write(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
