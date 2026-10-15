"""Cache draft: manual one-hop resting-corner reading in an isolated native UI.

Not executable acceptance until promoted to the canonical scripts/ path.  Root
owns the actual process supervisor, final source binding, launch and closeout.
Selected-source guards do not claim the whole transitive dependency graph.
"""
import argparse
from contextlib import ExitStack
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
CANONICAL = 'scripts/verify_resting_corner_window_293.py'
MANIFEST = 'research/p3-resting-results-293/source-manifest.json'
DATA = 'rouge/data/resting-corner-results.json'
EVENT = 'community_group_023'
SIZE = (1050, 720)
# Literal community-local navigation, not an inferred original-game pool.
CARDS = (
    (EVENT + ':scene:1:choice:0', 3, 3, (('小狗', 2), ('捕梦网', 4), ('松鼠', 5))),
    (EVENT + ':scene:6:choice:0', 2, 2, (('果园', 7), ('竞速比赛', 3))),
    (EVENT + ':scene:9:choice:1', 2, 1, (('动物泥偶', 10),)),
    (EVENT + ':scene:11:choice:0', 2, 3, (('果园', 7), ('竞速比赛', 3), ('动物泥偶', 10))),
)
SCENE_WORDS = {
    2: ('熟睡小狗', '抚摸小狗的脑袋', '获得20希望'),
    4: ('捕梦网', '闭眼感受', '获得15护盾'),
    5: ('松鼠', '拾起松鼠落下的橡实', '获得1件珍贵的加工品'),
    7: ('番石榴', '帮忙采摘', '获得15护盾'),
    3: ('竞速比赛', '目送豹子们远去', '获得1件珍贵的加工品'),
    10: ('动物泥偶', '进入神秘空间', '获得99源石锭'),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def bound_files():
    names = {CANONICAL, 'rouge/app.py', 'rouge/node_catalog_view.py',
        'rouge/resting_corner_view.py', 'rouge/resting_corner_results.py',
        'rouge/node_catalog.py', 'rouge/event_planning.py',
        'rouge/player_node_information.py', 'rouge/ui_state.py',
        'rouge/data/node-catalog.json', 'rouge/data/event-planning-reference.json',
        'tests/test_resting_corner_results_293.py',
        'tests/test_resting_corner_view_293.py', MANIFEST}
    manifest = json.loads((ROOT / MANIFEST).read_bytes())
    names.update(manifest['files'])
    result = {}
    for name in sorted(names):
        path = ROOT / name
        if (not path.is_file() or path.is_symlink()
                or not path.resolve().is_relative_to(ROOT)):
            raise ValueError('Selected public source must be a regular project file: ' + name)
        result[name] = sha(path)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', required=True)
    parser.add_argument('--visible-ms', type=int, default=30000)
    args = parser.parse_args()
    destination = Path(args.receipt).resolve()
    if destination.exists():
        raise FileExistsError('Preserve the first actual receipt')
    if args.visible_ms <= 0:
        raise ValueError('Positive --visible-ms required')
    destination.parent.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    before = {}; after = {}; checks = []; images = []; native_observations = []
    observations = []; executions = 0; failure = None; done = False
    closed = False; qpa = None; qt_exit = None
    attempts = {name: 0 for name in ('game_enumeration', 'game_connect', 'game_capture',
        'game_next_frame', 'desktop_start', 'desktop_request', 'provider_chat', 'credential_read')}

    def require(value, label):
        nonlocal executions
        if not value:
            raise AssertionError(label)
        executions += 1
        if label not in checks:
            checks.append(label)

    def forbidden(name):
        def blocked(*_, **__):
            attempts[name] += 1
            raise AssertionError('Forbidden original external entry: ' + name)
        return blocked

    try:
        if sys.platform != 'win32':
            raise RuntimeError('Actual native Windows required')
        if Path(__file__).resolve() != (ROOT / CANONICAL).resolve():
            raise RuntimeError('Cache draft is not executable acceptance; promote canonical script first')
        from PySide6.QtCore import Qt, QPoint, QRect, QTimer
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QApplication
        import win32gui
        import win32process
        from rouge import app as app_module
        from rouge import node_catalog as catalog
        from rouge import resting_corner_results as results
        before = bound_files()
        gui = QApplication([]); qpa = gui.platformName()
        require(qpa == 'windows', 'native_windows_QPA')

        class PublicWindow(app_module.MainWindow):
            def refresh_windows(self):
                self.windows.clear()

        with tempfile.TemporaryDirectory(prefix='rouge-293-resting-window-') as folder, ExitStack() as stack:
            temporary = Path(folder)
            for key, value in {'ROOT': temporary, 'SETTINGS': temporary / 'settings.json',
                    'OPERATOR_STATE': temporary / 'operators.json',
                    'RUN_STATE': temporary / 'run.json'}.items():
                stack.enter_context(patch.object(app_module, key, value))
            stack.enter_context(patch.object(app_module, 'list_game_windows',
                side_effect=forbidden('game_enumeration')))
            for method, name in [('connect', 'game_connect'), ('capture', 'game_capture'),
                    ('next_frame', 'game_next_frame')]:
                stack.enter_context(patch.object(app_module.GameCapture, method, side_effect=forbidden(name)))
            for method, name in [('start', 'desktop_start'), ('request', 'desktop_request')]:
                stack.enter_context(patch.object(app_module.DesktopBackend, method, side_effect=forbidden(name)))
            stack.enter_context(patch.object(app_module, 'stream_chat', side_effect=forbidden('provider_chat')))
            stack.enter_context(patch.object(app_module, 'read_key', side_effect=forbidden('credential_read')))
            window = PublicWindow()
            window.setWindowTitle('第293节 · 安眠一隅后续资料（公开隔离验收）')
            window.resize(*SIZE); window.show()
            panel = window.node_catalog; tabs = window.centralWidget()
            initial_run = deepcopy(window.run.state)
            dialog = None; parent_saved = None; reading_saved = None
            visited = []; card_observations = []; navigation = []
            role = Qt.ItemDataRole.UserRole + 1

            def isolated():
                require(not window.auto.isChecked() and not window.timer.isActive(),
                    'automatic_sampling_and_timer_disabled')
                require(window.capture.target is None and window.desktop.process is None,
                    'capture_target_and_desktop_backend_inactive')
                require(all(value == 0 for value in attempts.values()),
                    'all_eight_external_operation_attempts_zero')

            def native(widget, kind):
                hwnd = int(widget.winId())
                thread, pid = win32process.GetWindowThreadProcessId(hwnd)
                require(win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd) and widget.isVisible(),
                    kind + '_actual_native_HWND_visible')
                require(pid == os.getpid() and not win32gui.IsIconic(hwnd),
                    kind + '_HWND_owned_by_fixture_and_not_minimized')
                actual = [widget.width(), widget.height()]
                if kind == 'parent':
                    require(actual == list(SIZE), 'parent_actual_client_size_exact_1050x720')
                else:
                    require(actual[0] >= 900 and actual[1] >= 660,
                        'dialog_actual_client_size_at_least_900x660')
                return {'kind': kind, 'hwnd': hwnd, 'process_id': pid,
                    'thread_id': thread, 'qpa': qpa, 'client_size': actual}

            def choose(control, key):
                index = control.findData(key)
                require(index >= 0, 'requested_complete_reference_key_exists')
                control.setCurrentIndex(index)

            def event(identity):
                panel.show_directory(); choose(panel.kind, 'event')
                choose(panel.floor, None); choose(panel.node_type, None)
                panel.search.setText(catalog._event(identity)['title'])
                index = next(i for i, entry in enumerate(panel.entries)
                    if entry['kind'] == 'event' and entry['record']['id'] == identity)
                panel.list.setCurrentRow(index); tabs.setCurrentWidget(panel)
                require(panel.entries[index]['record']['id'] == identity, 'exact_event_identity_selected')

            def reader(widget):
                cursor = widget.textCursor()
                return {'text': text_sha(widget.toPlainText()), 'anchor': cursor.anchor(),
                    'position': cursor.position(), 'selected': cursor.selectedText(),
                    'vertical': widget.verticalScrollBar().value(),
                    'horizontal': widget.horizontalScrollBar().value()}

            def parent_state():
                return {'key': panel.list.selected_key(), 'tab': panel.reading_tabs.currentIndex(),
                    'scene_filter': panel.event_scene_filter.currentData(),
                    'choice_filter': panel.event_choice_filter.currentData(),
                    'stage_id': panel.event_stage.currentData(),
                    'stage_token': deepcopy(panel.event_stage.currentData(role)),
                    'search': panel.search.text(), 'search_cursor': panel.search.cursorPosition(),
                    'search_selection_start': panel.search.selectionStart(),
                    'search_selection': panel.search.selectedText(),
                    'player': reader(panel.player_detail), 'technical': reader(panel.detail)}

            def dialog_state():
                return {'event_id': dialog.event_id, 'scope_key': dialog.scope_key,
                    'choice_key': dialog.choice.currentData(), 'branch_id': dialog.branch.currentData(),
                    'tab': dialog.reading_tabs.currentIndex(),
                    'scene_identity': deepcopy(dialog._scene_identity),
                    'result': reader(dialog.result_text), 'scene': reader(dialog.scene_text),
                    'source': reader(dialog.source_text)}

            def prime(widget):
                gui.processEvents()
                require(widget.verticalScrollBar().maximum() > 0 and len(widget.toPlainText()) > 16,
                    'real_existing_document_has_nonzero_scroll_range')
                cursor = widget.textCursor(); cursor.setPosition(5)
                cursor.setPosition(16, QTextCursor.MoveMode.KeepAnchor); widget.setTextCursor(cursor)
                widget.verticalScrollBar().setValue(max(1, widget.verticalScrollBar().maximum() // 2))
                require(widget.verticalScrollBar().value() > 0 and bool(widget.textCursor().selectedText()),
                    'real_nonzero_scroll_and_nonempty_document_selection')

            def save_image(name, widget, kind):
                isolated(); handle = native(widget, kind)
                path = destination.with_name(destination.stem + '-' + name + '.png')
                if path.exists():
                    raise FileExistsError('First image must not be overwritten')
                pixels = widget.grab(); require(not pixels.isNull(), 'actual_own_window_pixels')
                require(pixels.save(str(path), 'PNG'), 'actual_own_window_PNG_saved')
                images.append({'name': name, 'path': str(path), 'sha256': sha(path), 'native_window': handle})

            def close_owned_windows():
                if dialog is not None:
                    dialog.close()
                window.close()

            def fail(error):
                nonlocal failure, done
                if failure is None:
                    failure = {'type': type(error).__name__, 'message': str(error),
                        'traceback': traceback.format_exc()}
                done = False; close_owned_windows(); gui.exit(1)

            def later(callback, delay=200):
                def guarded():
                    try:
                        isolated(); callback()
                    except BaseException as error:
                        fail(error)
                QTimer.singleShot(delay, guarded)

            def begin():
                nonlocal parent_saved
                event(EVENT); panel.reading_tabs.setCurrentWidget(panel.detail)
                gui.processEvents(); prime(panel.detail); panel.search.setSelection(0, 2)
                parent_saved = parent_state()
                require(panel.event_choice_filter.currentData() is None,
                    'parent_default_all_choices_has_no_implicit_resting_card')
                require(panel.resting_window is None, 'new_resting_window_not_precreated')
                rect = QRect(panel.resting_button.mapTo(window, QPoint(0, 0)), panel.resting_button.size())
                require(panel.resting_button.isVisible() and not panel.resting_button.visibleRegion().isEmpty()
                    and window.rect().contains(rect), 'dedicated_resting_button_visible_inside_parent_1050x720')
                save_image('parent-entry', window, 'parent')
                panel.resting_button.click(); later(check_opened)

            def check_opened():
                nonlocal dialog
                dialog = panel.resting_window
                require(dialog is not None and dialog.parent() is panel,
                    'actual_parent_button_constructed_and_retained_owned_dialog')
                parent_handle = native(window, 'parent'); dialog_handle = native(dialog, 'dialog')
                require(parent_handle['hwnd'] != dialog_handle['hwnd'], 'parent_and_dialog_have_distinct_owned_HWNDs')
                native_observations.extend([parent_handle, dialog_handle])
                require(dialog.choice.currentData() is None and dialog.branch.currentData() is None
                    and not dialog.open_scene_button.isEnabled() and dialog._scene_identity is None,
                    'dialog_default_does_not_choose_card_branch_or_open_scene')
                require([dialog.choice.itemData(i) for i in range(dialog.choice.count())]
                    == [row[0] for row in CARDS], 'four_cards_keep_exact_complete_choice_keys')
                require(parent_state() == parent_saved, 'opening_child_preserves_parent_reading_state')
                later(lambda: read_card(0))

            def read_card(number):
                key, annotation, listed, branches = CARDS[number]
                choose(dialog.choice, key)
                card = next(row for row in dialog.packet['cards'] if row['choice_key'] == key)
                require(card['documented_count'] == annotation and card['listed_branch_count'] == listed,
                    'literal_annotation_and_listed_branch_counts_3_2_1_3_preserved')
                require([(row['label'], row['target_scene_key']) for row in card['branches']]
                    == [(label, EVENT + ':scene:' + str(target)) for label, target in branches],
                    'literal_branches_and_destinations_not_repaired_or_invented')
                expected_ids = [key + ':sub:' + str(i) for i in range(listed)]
                require([dialog.branch.itemData(i) for i in range(dialog.branch.count())] == expected_ids,
                    'branch_controls_use_complete_origin_specific_reference_ids')
                text = dialog.result_text.toPlainText()
                require('后续' in text and '本局' in text and '未确认' in text and '不能把各项相加' in text,
                    'player_reference_states_future_buttons_and_actual_unknown_without_sum')
                require(not any(value in text for value in ('community_group_', 'choice_ro6_', 'https://')),
                    'player_result_uses_chinese_without_raw_identifiers_or_source_urls')
                if annotation != listed:
                    require('资料数量对不上' in text and f'原注写{annotation}种' in text
                        and f'{listed}项' in text, 'both_count_conflicts_visible_in_player_result')
                else:
                    require('资料数量对不上' not in text, 'matching_counts_not_falsely_marked_conflicting')
                require(card['actual_selected_branch'] is None and card['actual_reward'] is None
                    and card['actual_selectable'] is None and card['full_actual_pool_known'] is False,
                    'reading_cards_does_not_confirm_actual_result_pool_or_eligibility')
                card_observations.append({'choice_key': key, 'documented_count': annotation,
                    'listed_branch_count': listed, 'branch_ids': expected_ids})
                if number == 0:
                    save_image('first-three-branches', dialog, 'dialog')
                later(lambda: read_branch(number, 0))

            def read_branch(card_number, branch_number):
                key, _, listed, branches = CARDS[card_number]
                label, target = branches[branch_number]; branch_id = key + ':sub:' + str(branch_number)
                choose(dialog.branch, branch_id)
                require(dialog.open_scene_button.isEnabled(), 'explicit_branch_enables_manual_scene_reading')
                require('尚未手动打开' in dialog.scene_text.toPlainText(),
                    'selecting_branch_alone_does_not_automatically_open_scene')
                dialog.open_scene_button.click()
                require(dialog.reading_tabs.currentWidget() is dialog.scene_text
                    and dialog._scene_identity[-1] == EVENT + ':scene:' + str(target),
                    'real_manual_button_opens_exact_community_destination_scene')
                text = dialog.scene_text.toPlainText()
                require(all(word in text for word in SCENE_WORDS[target]),
                    'manual_destination_contains_its_distinct_scene_and_future_button_text')
                require('不表示已进入游戏' in text and '是否出现' in text and '实际领取仍未知' in text,
                    'scene_reading_never_claims_game_transition_or_reward')
                visited.append(EVENT + ':scene:' + str(target))
                navigation.append({'choice_key': key, 'branch_id': branch_id,
                    'label': label, 'target_scene_key': visited[-1]})
                if target == 10:
                    result_text = dialog.result_text.toPlainText()
                    require('99源石锭' in result_text and '尚未与原游戏入口对应' in result_text,
                        'ninety_nine_gold_destination_mismatch_visible_in_player_result')
                if branch_number + 1 < listed:
                    later(lambda: read_branch(card_number, branch_number + 1))
                elif card_number + 1 < len(CARDS):
                    later(lambda: read_card(card_number + 1))
                else:
                    save_image('conflict-and-ninety-nine-scene', dialog, 'dialog')
                    later(prime_refresh)

            def prime_refresh():
                nonlocal reading_saved
                require(set(visited) == {EVENT + ':scene:' + str(n) for n in SCENE_WORDS},
                    'all_six_distinct_destinations_manually_read_without_pool_inference')
                require(len(navigation) == 9, 'all_nine_origin_specific_branches_remain_distinct')
                dialog.reading_tabs.setCurrentWidget(dialog.source_text); prime(dialog.source_text)
                reading_saved = dialog_state(); panel.refresh(); dialog.refresh_reference()
                later(check_refresh)

            def check_refresh():
                require(dialog_state() == reading_saved,
                    'same_scope_refresh_retains_card_branch_scene_tab_text_cursor_selection_and_real_scroll')
                require(parent_state() == parent_saved,
                    'child_navigation_and_parent_refresh_preserve_parent_reading_state')
                save_image('source-reading-retained', dialog, 'dialog')
                later(check_source_failure)

            def check_source_failure():
                source_root = temporary / 'public-source-clone'
                manifest_raw = (ROOT / MANIFEST).read_bytes(); manifest = json.loads(manifest_raw)
                for relative in [MANIFEST, *manifest['files']]:
                    source = ROOT / relative; target = source_root / relative
                    target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(source.read_bytes())
                cloned_data = source_root / DATA; original = cloned_data.read_bytes()
                require(sha(cloned_data) == before[DATA], 'temporary_source_clone_starts_with_exact_public_bytes')
                with patch.object(results, 'ROOT', source_root):
                    require(results.source_data() is not None, 'temporary_complete_public_source_clone_validates_before_damage')
                    cloned_data.write_bytes(original + b' ')
                    dialog.refresh_reference()
                    require(dialog.choice.count() == 0 and dialog.branch.count() == 0
                        and not dialog.open_scene_button.isEnabled() and dialog.packet is None
                        and dialog._scene_identity is None, 'source_failure_clears_all_reference_controls_and_old_identity')
                    require(all('尚未通过核对' in widget.toPlainText()
                        for widget in (dialog.result_text, dialog.scene_text, dialog.source_text)),
                        'source_failure_clears_all_three_old_reading_pages')
                    save_image('source-invalidated', dialog, 'dialog')
                    cloned_data.write_bytes(original)
                    require(sha(cloned_data) == before[DATA], 'temporary_source_restored_from_true_original_bytes')
                    dialog.refresh_reference()
                    require(dialog.choice.count() == 4 and dialog.choice.currentData() is None
                        and dialog.branch.currentData() is None and dialog.branch.count() == 0
                        and not dialog.open_scene_button.isEnabled() and dialog._scene_identity is None,
                        'source_recovery_does_not_automatically_restore_choice_branch_or_scene')
                    require('尚未手动打开' in dialog.scene_text.toPlainText(),
                        'source_recovery_does_not_reopen_stale_scene_text')
                later(check_changed_event)

            def check_changed_event():
                choose(dialog.choice, CARDS[0][0]); choose(dialog.branch, CARDS[0][0] + ':sub:0')
                dialog.open_scene_button.click()
                event('community_group_014')
                require(not panel.resting_button.isVisible() and dialog.event_id is None
                    and dialog.scope_key is None and dialog.choice.count() == 0 and dialog.branch.count() == 0
                    and dialog._scene_identity is None and not dialog.open_scene_button.isEnabled(),
                    'different_parent_event_invalidates_resting_scope_and_all_old_selections')
                require(all('当前未查阅安眠一隅' in widget.toPlainText()
                    for widget in (dialog.result_text, dialog.scene_text, dialog.source_text)),
                    'different_event_clears_all_three_dialog_pages')
                event(EVENT); panel.resting_button.click()
                require(panel.resting_window is dialog and dialog.choice.currentData() is None
                    and dialog.branch.currentData() is None and dialog._scene_identity is None,
                    'return_to_event_reuses_dialog_without_restoring_old_scope_selection')
                save_image('restored-unselected', dialog, 'dialog'); later(finish)

            def finish():
                nonlocal done
                native_observations.extend([native(window, 'parent'), native(dialog, 'dialog')])
                require(window.run.state == initial_run, 'manual_reading_never_changes_temporary_run_memory')
                require(bound_files() == before, 'selected_public_sources_stable_before_completion')
                observations.append({'card_count_references': card_observations,
                    'manual_one_hop_reading': navigation, 'distinct_scene_keys': sorted(set(visited)),
                    'default_choice': None, 'actual_game_transition': None, 'actual_choice_executed': None,
                    'actual_rewards_granted': None, 'complete_actual_pool': None,
                    'source_failure_is_only_an_explicit_temporary_public_clone_negative_fixture': True})
                done = True

            def close_deadline():
                nonlocal failure
                if not done and failure is None:
                    failure = {'type': 'TimeoutError', 'message': 'New UI checks not completed before deadline'}
                close_owned_windows()

            later(begin, 500); QTimer.singleShot(max(30000, args.visible_ms), close_deadline)
            qt_exit = gui.exec()
            closed = not window.isVisible() and (dialog is None or not dialog.isVisible())
            if qt_exit != 0 or not closed or not done:
                if failure is None:
                    failure = {'type': 'RuntimeError', 'message': 'Fixture checks/Qt/owned windows not closed'}
            if failure is None:
                isolated()
            after = bound_files()
            if before != after and failure is None:
                failure = {'type': 'AssertionError', 'message': 'Selected public sources changed through actual closure'}
    except BaseException as error:
        failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
    report = {'section': 293, 'kind': 'isolated_native_windows_resting_corner_reading',
        'passed': done and failure is None, 'failure': failure, 'started_at': started,
        'finished_at': datetime.now(timezone.utc).isoformat(), 'process_id': os.getpid(),
        'qpa': qpa, 'qt_exit_code': qt_exit, 'verification_window_closed': closed,
        'checks': checks, 'unique_checks': len(checks),
        'successful_assertion_executions_including_repeated_guards': executions,
        'requested_parent_client_size': list(SIZE), 'minimum_dialog_client_size': [900, 660],
        'native_observations': native_observations, 'screenshots': images, 'screenshot_count': len(images),
        'public_observations': observations, 'source_sha256_before': before, 'source_sha256_after': after,
        'source_guard_is_selected_not_all_transitive_dependencies': True, 'temporary_state_root': True,
        'state_paths_replaced_before_constructor': ['ROOT', 'SETTINGS', 'OPERATOR_STATE', 'RUN_STATE'],
        'private_state_read_copied_or_restored': False, 'external_operation_attempts': attempts,
        'game_operated': False, 'game_captures': 0, 'chat_sent': False,
        'chat_attempted': bool(attempts['desktop_request'] or attempts['provider_chat']),
        'external_entrypoints_blocked_before_original_call': True,
        'original_project_window_operated_or_restarted': False,
        'actual_process_termination_verified_by_this_script': False,
        'owned_supervisor_exit_and_cleanup_required_separately': True,
        'launch_Popen_PID_must_be_recorded_separately_from_actual_fixture_PID': True,
        'scope': 'New manual resting-corner one-hop reading only: four exact cards, nine branches, six local scenes, two document count conflicts, destination mismatch, real reader retention and source invalidation. No pool/qualification/game-state inference; no full rerun.'}
    with destination.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
