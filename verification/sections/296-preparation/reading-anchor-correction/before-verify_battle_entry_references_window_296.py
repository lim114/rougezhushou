"""Draft: isolated actual Windows MainWindow/manual battle-entry reading.

Do not execute from cache. Root promotes, binds final sources, supervises the
actual Windows process and archives its real results. This selected-source
guard is not a claim about every transitive dependency or the live game.
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
CANONICAL = 'scripts/verify_battle_entry_references_window_296.py'
EVENT_MANIFEST = 'research/p3-battle-event-references-296/source-manifest.json'
CONFIG_MANIFEST = 'research/p3-stage-entry-configuration-296/manifest.json'
SIZE = (1050, 720)
DIALOG_SIZE = (900, 680)
# Literal documented identities, not whatever entries the current helper emits.
CASES = (
    ('ro6_t_1', 'community_group_012', 1, 0),
    ('ro6_t_2', 'community_group_013', 1, 0),
    ('ro6_t_3', 'community_group_014', 1, 0),
    ('ro6_t_4', 'community_group_015', 1, 0),
    ('ro6_t_5', 'community_group_016', 3, 0),
    ('ro6_e_t_3', 'community_group_014', 1, 0),
    ('ro6_e_t_3', 'community_group_014', 2, 0),
    ('ro6_e_t_4', 'community_group_015', 1, 0),
    ('ro6_e_t_4', 'community_group_015', 2, 0),
    ('ro6_e_t_5', 'community_group_016', 3, 0),
    ('ro6_e_t_5', 'community_group_016', 8, 0),
)
EXCLUDED = (('ro6_t_3', 'community_group_014', 2, 0),
            ('ro6_t_4', 'community_group_015', 2, 0),
            ('ro6_t_5', 'community_group_016', 8, 0))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_sha(text):
    return hashlib.sha256(text.encode('utf8')).hexdigest()


def bound_files():
    names = {CANONICAL, 'rouge/app.py', 'rouge/battle_view.py',
        'rouge/node_catalog_view.py', 'rouge/player_node_information.py',
        'rouge/battle_entry_reference_view.py', 'rouge/battle_event_references.py',
        'rouge/stage_entry_reference.py', 'rouge/battle_preview.py', 'rouge/ui_state.py',
        'rouge/node_catalog.py', 'rouge/event_planning.py', 'rouge/branch_choice.py',
        'rouge/stage_context.py', 'rouge/stage_floor_reference.py',
        'rouge/data/stage-context-reference.json', 'rouge/data/view-catalog.json',
        'scripts/build_stage_entry_configuration_296.py',
        'scripts/build_battle_event_references_296.py',
        'tests/test_stage_entry_configuration_296.py',
        'tests/test_battle_event_references_296.py',
        'tests/test_battle_entry_reference_view_296.py',
        'tests/test_battle_entry_integration_296.py',
        'research/p3-stage-context/community-main.html', EVENT_MANIFEST, CONFIG_MANIFEST}
    for manifest_name in (EVENT_MANIFEST, CONFIG_MANIFEST):
        manifest = json.loads((ROOT / manifest_name).read_bytes())
        names.update(manifest['files'])
        if 'data_file' in manifest:
            names.add(manifest['data_file'])
        names.update(p.relative_to(ROOT).as_posix()
            for p in (ROOT / Path(manifest_name).parent).rglob('*') if p.is_file())
    result = {}
    for name in sorted(names):
        path = ROOT / name
        if (not path.is_file() or path.is_symlink()
                or not path.resolve().is_relative_to(ROOT.resolve())):
            raise ValueError('Selected public source must be a regular project file: ' + name)
        result[name] = sha(path)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', required=True)
    parser.add_argument('--visible-ms', type=int, default=120000)
    args = parser.parse_args()
    destination = Path(args.receipt).resolve()
    if destination.exists():
        raise FileExistsError('Preserve the first actual receipt')
    if args.visible_ms <= 0:
        raise ValueError('Positive visible time required')
    destination.parent.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    before = {}; after = {}; checks = []; images = []; native_observations = []
    navigated = []; excluded_observations = []; source_negatives = []; refresh_observations = []; configuration_observations = []
    executions = 0; failure = None; done = False; closed = False; qt_exit = None; qpa = None
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
        from PySide6.QtTest import QTest
        import win32gui
        import win32process
        from rouge import app as app_module
        from rouge import battle_event_references as events
        from rouge import stage_entry_reference as configurations
        from rouge import stage_context
        before = bound_files()
        gui = QApplication([]); qpa = gui.platformName()
        require(qpa == 'windows', 'native_windows_QPA')

        class PublicWindow(app_module.MainWindow):
            def refresh_windows(self):
                self.windows.clear()

        with tempfile.TemporaryDirectory(prefix='rouge-296-battle-entry-window-') as folder, ExitStack() as stack:
            temporary = Path(folder)
            for key, value in {'ROOT': temporary, 'SETTINGS': temporary / 'settings.json',
                    'OPERATOR_STATE': temporary / 'operators.json', 'RUN_STATE': temporary / 'run.json'}.items():
                stack.enter_context(patch.object(app_module, key, value))
            stack.enter_context(patch.object(app_module, 'list_game_windows', side_effect=forbidden('game_enumeration')))
            for method, name in [('connect', 'game_connect'), ('capture', 'game_capture'), ('next_frame', 'game_next_frame')]:
                stack.enter_context(patch.object(app_module.GameCapture, method, side_effect=forbidden(name)))
            for method, name in [('start', 'desktop_start'), ('request', 'desktop_request')]:
                stack.enter_context(patch.object(app_module.DesktopBackend, method, side_effect=forbidden(name)))
            stack.enter_context(patch.object(app_module, 'stream_chat', side_effect=forbidden('provider_chat')))
            stack.enter_context(patch.object(app_module, 'read_key', side_effect=forbidden('credential_read')))
            window = PublicWindow()
            dialog = None
            try:
                window.setWindowTitle('第296节 · 固定战斗入口资料（公开隔离验收）')
                window.resize(*SIZE); window.show()
                battle = window.battle_preview; catalog = window.node_catalog; tabs = window.centralWidget()
                initial_run = deepcopy(window.run.state)
                old_floor_data = deepcopy(stage_context.context_data())
                emitted = []
                battle.entryEventSelected.connect(lambda token: emitted.append(deepcopy(token)))
                case_index = 0; current = None; saved_battle = None; prior_stage = None; pending_emissions = 0

                def isolated():
                    require(not window.auto.isChecked() and not window.timer.isActive(), 'automatic_sampling_and_timer_disabled')
                    require(window.capture.target is None and window.desktop.process is None, 'capture_target_and_desktop_backend_inactive')
                    require(all(value == 0 for value in attempts.values()), 'all_eight_external_operation_attempts_zero')

                def native(widget, kind):
                    hwnd = int(widget.winId()); thread, pid = win32process.GetWindowThreadProcessId(hwnd)
                    require(win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd) and widget.isVisible(), kind + '_actual_native_HWND_visible')
                    require(pid == os.getpid() and not win32gui.IsIconic(hwnd), kind + '_HWND_owned_by_fixture_and_not_minimized')
                    actual = [widget.width(), widget.height()]
                    expected = list(SIZE if kind == 'parent' else DIALOG_SIZE)
                    require(actual == expected, kind + '_actual_client_size_exact_' + 'x'.join(map(str, expected)))
                    return {'kind': kind, 'hwnd': hwnd, 'process_id': pid, 'thread_id': thread,
                            'qpa': qpa, 'client_size': actual}

                def choose(control, value):
                    index = control.findData(value)
                    require(index >= 0, 'requested_exact_complete_control_identity_exists')
                    control.setCurrentIndex(index)

                def click(button, owner, label):
                    gui.processEvents()
                    rect = QRect(button.mapTo(owner, QPoint(0, 0)), button.size())
                    require(button.isVisible() and button.isEnabled() and not button.visibleRegion().isEmpty()
                            and owner.rect().contains(rect), label + '_visible_enabled_inside_actual_client')
                    QTest.mouseClick(button, Qt.MouseButton.LeftButton, pos=button.rect().center())

                def reader(widget):
                    cursor = widget.textCursor()
                    return {'text_sha256': text_sha(widget.toPlainText()), 'anchor': cursor.anchor(),
                        'position': cursor.position(), 'selected': cursor.selectedText(),
                        'vertical': widget.verticalScrollBar().value(), 'horizontal': widget.horizontalScrollBar().value()}

                def prime(widget, need_scroll=False):
                    gui.processEvents()
                    require(widget.document().characterCount() > 18, 'real_existing_reader_has_selectable_text')
                    cursor = widget.textCursor(); cursor.setPosition(5)
                    cursor.setPosition(16, QTextCursor.MoveMode.KeepAnchor); widget.setTextCursor(cursor)
                    maximum = widget.verticalScrollBar().maximum()
                    if need_scroll:
                        require(maximum > 0, 'real_existing_reader_has_nonzero_scroll_range')
                    if maximum > 0:
                        widget.verticalScrollBar().setValue(max(1, maximum // 2))
                    require(bool(widget.textCursor().selectedText()), 'reader_has_real_nonempty_text_selection')
                    if need_scroll:
                        require(widget.verticalScrollBar().value() > 0, 'reader_has_real_nonzero_scroll_position')

                def battle_state():
                    item = battle.spawn_list.currentItem()
                    return {'stage_id': battle.current_stage, 'wave': battle.wave_combo.currentData(),
                        'enemy': deepcopy(battle.enemy_combo.currentData()),
                        'enemy_branch': deepcopy(battle.enemy_choices.branch.currentData()),
                        'list_item': deepcopy(item.data(Qt.ItemDataRole.UserRole)) if item else None,
                        'list_scroll': battle.spawn_list.verticalScrollBar().value(),
                        'map_selected': deepcopy(battle.grid.selected), 'map_cell': deepcopy(battle.grid.reference_cell),
                        'original_selected': deepcopy(battle.original.selected), 'original_cell': deepcopy(battle.original.reference_cell),
                        'ordinal': battle.occurrence.value(), 'tile': deepcopy(battle._tile_cell),
                        'detail_key': deepcopy(battle._detail_key), 'shown_enemy': deepcopy(battle._shown_enemy),
                        'context': deepcopy(battle.context), 'technical': battle.technical.isChecked(),
                        'spawn_reader': reader(battle.spawn_detail), 'enemy_reader': reader(battle.enemy_detail)}

                def dialog_state():
                    return {'stage_id': dialog.stage_id, 'choice': dialog.event_choice.currentData(),
                        'tab': dialog.reading_tabs.currentIndex(), 'view_key': deepcopy(dialog._view_key),
                        'reference_reader': reader(dialog.reference_text), 'source_reader': reader(dialog.source_text)}

                def catalog_state():
                    return {'key': catalog.list.selected_key(), 'scene': catalog.event_scene_filter.currentData(),
                        'choice': catalog.event_choice_filter.currentData(), 'search': catalog.search.text(),
                        'player': reader(catalog.player_detail), 'source': reader(catalog.detail),
                        'tab': catalog.reading_tabs.currentIndex()}

                def save_image(name, widget, kind):
                    isolated(); handle = native(widget, kind)
                    path = destination.with_name(destination.stem + '-' + name + '.png')
                    if path.exists():
                        raise FileExistsError('First actual PNG must not be overwritten')
                    pixels = widget.grab(); require(not pixels.isNull(), 'actual_own_window_pixels')
                    require(pixels.save(str(path), 'PNG'), 'actual_own_window_PNG_saved')
                    images.append({'name': name, 'path': str(path), 'sha256': sha(path), 'native_window': handle})

                def close_owned():
                    if dialog is not None:
                        dialog.close()
                    window.close()

                def fail(error):
                    nonlocal failure, done
                    if failure is None:
                        failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
                    done = False; close_owned(); gui.exit(1)

                def later(callback, delay=150):
                    def guarded():
                        try:
                            isolated(); callback()
                        except BaseException as error:
                            fail(error)
                    QTimer.singleShot(delay, guarded)

                def begin():
                    native_observations.append(native(window, 'parent'))
                    require(battle.entry_reference_window is None, 'entry_dialog_not_precreated_before_main_button')
                    require(old_floor_data['stages']['ro6_t_12']['conditions'] == []
                        and old_floor_data['source']['remaining_unknown_floor_count'] == 15,
                        'existing_autopsy_floor_qualification_not_upgraded_before_reference_reading')
                    later(open_next_case)

                def open_next_case():
                    nonlocal prior_stage
                    if case_index >= len(CASES):
                        later(check_exclusions); return
                    sid, event, scene, choice = CASES[case_index]
                    tabs.setCurrentWidget(battle); battle.set_stage(sid)
                    battle.set_context(deepcopy(window.run.state.get('config', {})))
                    if sid != prior_stage:
                        require(battle.wave_combo.count() > 1, 'covered_fixed_stage_has_actual_wave_control')
                        battle.wave_combo.setCurrentIndex(1)
                        require(battle.enemy_combo.count() > 0, 'covered_fixed_stage_has_actual_enemy_control')
                        if battle.enemy_combo.count() > 1:
                            battle.enemy_combo.setCurrentIndex(1)
                        battle.technical.setChecked(True)
                        require(battle.spawn_list.count() > 0, 'covered_fixed_stage_has_actual_spawn_rows')
                        battle.spawn_list.setCurrentRow(battle.spawn_list.count() - 1)
                        cell = battle.rows[-1]['route']['start']
                        point = battle.grid.cell_center(cell).toPoint()
                        require(battle.grid.rect().contains(point), 'source_spawn_cell_has_actual_visible_grid_position')
                        QTest.mouseClick(battle.grid, Qt.MouseButton.LeftButton, pos=point)
                        require((battle.grid.selected and battle.grid.selected['route']['start'] == cell)
                            or battle.grid.reference_cell == cell,
                            'actual_grid_click_keeps_the_requested_source_cell_selected')
                        prime(battle.enemy_detail, need_scroll=True)
                    require(battle.entry_reference_button.isVisible() and battle.entry_reference_button.isEnabled(),
                        'covered_stage_manual_entry_button_available')
                    click(battle.entry_reference_button, window, 'main_battle_entry_QTest_click')
                    later(select_current_case)

                def select_current_case():
                    nonlocal dialog, current, saved_battle, prior_stage, pending_emissions
                    sid, event, scene, choice = CASES[case_index]
                    dialog = battle.entry_reference_window
                    require(dialog is not None and dialog.parent() is battle, 'main_button_constructs_owned_entry_dialog')
                    dialog.resize(*DIALOG_SIZE); gui.processEvents()
                    native_observations.append(native(dialog, 'dialog'))
                    require(dialog.stage_id == sid and dialog.event_bar.isVisible(), 'dialog_has_exact_stage_and_event_controls')
                    if sid != prior_stage:
                        require(dialog.event_choice.currentData() is None and dialog.event_choice.currentIndex() == -1
                            and not dialog.open_event_button.isEnabled(), 'new_stage_default_does_not_choose_an_event')
                    packet = events.stage_event_references(sid)
                    require(packet and packet['status'] == 'documented_reference', 'current_stage_source_verifies_before_manual_selection')
                    expected_scene = event + ':scene:' + str(scene)
                    expected_choice = expected_scene + ':choice:' + str(choice)
                    current = next(r for r in packet['rows'] if r['event_id'] == event
                        and r['scene_key'] == expected_scene and r['choice_key'] == expected_choice)
                    require({dialog.event_choice.itemData(i) for i in range(dialog.event_choice.count())}
                        == {r['reference_id'] for r in packet['rows']}, 'actual_choice_control_contains_all_and_only_admitted_references')
                    choose(dialog.event_choice, current['reference_id'])
                    require(dialog.open_event_button.isEnabled() and current['choice_title'] in dialog.reference_text.toPlainText(),
                        'actual_selected_reference_has_readable_choice_and_manual_button')
                    require(all(current[key] is None for key in ('actual_stage_id', 'actual_choice_eligible', 'actual_entered')),
                        'event_reference_does_not_assert_actual_game_choice_or_entry')
                    saved_battle = battle_state()
                    if not navigated:
                        save_image('event-reference-selected', dialog, 'dialog')
                    pending_emissions = len(emitted)
                    click(dialog.open_event_button, dialog, 'each_admitted_event_option_QTest_click')
                    prior_stage = sid
                    later(check_current_navigation)

                def check_current_navigation():
                    nonlocal case_index
                    require(tabs.currentWidget() is catalog and not dialog.isVisible(), 'manual_reference_click_opens_node_catalog_and_hides_dialog')
                    selected = next((r for r in catalog.entries if r['key'] == catalog.list.selected_key()), None)
                    require(selected and selected['kind'] == 'event' and selected['record']['id'] == current['event_id'],
                        'manual_reference_selects_exact_event_identity')
                    require(catalog.event_scene_filter.currentData() == current['scene_key']
                        and catalog.event_choice_filter.currentData() == current['choice_key'],
                        'manual_reference_selects_complete_scene_and_choice_not_same_title')
                    require(len(emitted) == pending_emissions + 1 and emitted[-1] == current['token'],
                        'each_actual_manual_click_emits_exactly_one_full_revalidated_token')
                    require('不表示本局' in catalog.context_label.text(), 'node_catalog_context_explains_reference_not_actual_entry')
                    require(battle_state() == saved_battle, 'event_navigation_preserves_battle_wave_enemy_item_map_readers_scroll_and_context')
                    navigated.append({'stage_id': current['stage_id'], 'event_id': current['event_id'],
                        'scene_key': current['scene_key'], 'choice_key': current['choice_key'],
                        'reference_id': current['reference_id'], 'emitted_token': deepcopy(emitted[-1]),
                        'battle_state_sha256': text_sha(json.dumps(saved_battle, ensure_ascii=False, sort_keys=True))})
                    if len(navigated) == 1:
                        save_image('exact-event-option-opened', window, 'parent')
                    tabs.setCurrentWidget(battle); gui.processEvents()
                    require(battle_state() == saved_battle, 'manual_tab_return_preserves_existing_battle_reading')
                    case_index += 1; later(open_next_case)

                def check_exclusions():
                    for sid, event, scene, choice in EXCLUDED:
                        if dialog.isVisible():
                            dialog.hide()
                        tabs.setCurrentWidget(battle); battle.set_stage(sid)
                        click(battle.entry_reference_button, window, 'excluded_case_opens_only_valid_reference_list')
                        packet = events.stage_event_references(sid)
                        key = event + ':scene:' + str(scene) + ':choice:' + str(choice)
                        excluded = next(r for r in packet['excluded_rows'] if r['choice_key'] == key)
                        require(dialog.event_choice.findData(excluded['reference_id']) < 0,
                            'explicit_emergency_option_absent_from_ordinary_reference_control')
                        admitted = deepcopy(packet['rows'][0]['token'])
                        for name in ('reference_id', 'event_id', 'scene_key', 'choice_key', 'scene_number', 'choice_number', 'stage_page'):
                            admitted[name] = deepcopy(excluded[name])
                        admitted['stage_record'] = {k: deepcopy(v) for k, v in excluded['stage_reference'].items() if k != 'level_source'}
                        admitted['level_source'] = deepcopy(excluded['stage_reference']['level_source'])
                        old_catalog = catalog_state(); old_tab = tabs.currentWidget(); count = len(emitted)
                        require(window.show_battle_event_reference(admitted) is False
                            and catalog.open_battle_event_reference(sid, admitted) is False,
                            'fully_typed_excluded_choice_token_rejected_by_app_and_catalog_guards')
                        require(catalog_state() == old_catalog and tabs.currentWidget() is old_tab and len(emitted) == count,
                            'excluded_choice_never_changes_reading_or_emits_navigation')
                        excluded_observations.append({'stage_id': sid, 'choice_key': key,
                            'excluded_reference_id': excluded['reference_id'], 'manual_navigation': False})
                    later(check_same_scope_refresh)

                def check_same_scope_refresh():
                    if dialog.isVisible():
                        dialog.hide()
                    sid = 'ro6_e_t_5'; battle.set_stage(sid); tabs.setCurrentWidget(battle)
                    click(battle.entry_reference_button, window, 'same_scope_entry_reopen_QTest_click')
                    packet = events.stage_event_references(sid)
                    chosen = next(r for r in packet['rows'] if r['choice_key'] == 'community_group_016:scene:8:choice:0')
                    choose(dialog.event_choice, chosen['reference_id'])
                    prime(dialog.reference_text)
                    dialog.reading_tabs.setCurrentWidget(dialog.source_text); prime(dialog.source_text, need_scroll=True)
                    saved = dialog_state(); parent = battle_state()
                    for label, callback in [('dialog_refresh', dialog.refresh_reference),
                            ('same_stage_set', lambda: dialog.set_stage(sid)),
                            ('parent_reference_refresh', battle._refresh_entry_reference)]:
                        callback(); gui.processEvents()
                        require(dialog_state() == saved, 'same_scope_refresh_preserves_reference_choice_tabs_reading_and_nonzero_scroll')
                        require(battle_state() == parent, 'same_scope_entry_refresh_does_not_reset_battle_state')
                        refresh_observations.append({'path': label, 'stage_id': sid,
                            'choice': chosen['reference_id'], 'source_scroll': saved['source_reader']['vertical']})
                    later(check_event_source_failure)

                def damage_source(model, manifest_name, image_name, kind):
                    manifest = json.loads((ROOT / manifest_name).read_bytes())
                    names = set(manifest['files']) | {manifest_name}
                    if 'data_file' in manifest:
                        names.add(manifest['data_file'])
                    clone = temporary / ('source-negative-' + kind)
                    for name in names:
                        source = ROOT / name; target = clone / name
                        require(source.is_file() and not source.is_symlink() and source.resolve().is_relative_to(ROOT.resolve()),
                            'negative_fixture_copies_only_selected_regular_public_sources')
                        target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(source.read_bytes())
                    target = clone / manifest_name; raw = target.read_bytes()
                    with patch.object(model, 'ROOT', clone):
                        require(model.source_data() is not None, 'temporary_public_source_clone_valid_before_manifest_damage')
                        try:
                            target.write_bytes(raw + b' ')
                            dialog.refresh_reference(); battle._refresh_entry_reference(); gui.processEvents()
                            require(dialog.packet is None and dialog._view_key is None
                                and dialog.event_choice.count() == 0 and dialog.event_choice.currentData() is None
                                and not dialog.open_event_button.isEnabled() and not battle.entry_reference_button.isEnabled(),
                                kind + '_real_manifest_damage_clears_packet_tokens_choices_and_buttons')
                            require(all('已清除' in widget.toPlainText() and 'community_group_' not in widget.toPlainText()
                                and '光明之末' not in widget.toPlainText() for widget in (dialog.reference_text, dialog.source_text)),
                                kind + '_real_source_failure_clears_both_old_reading_pages')
                            save_image(image_name, dialog, 'dialog')
                        finally:
                            target.write_bytes(raw)
                        require(sha(target) == before[manifest_name], 'temporary_source_manifest_restored_from_true_original_bytes')
                        dialog.refresh_reference(); battle._refresh_entry_reference(); gui.processEvents()
                        require(dialog.packet is not None and dialog.event_choice.currentData() is None
                            and not dialog.open_event_button.isEnabled(), kind + '_source_restoration_leaves_event_choice_unselected')
                        if kind == 'event':
                            require(dialog.event_choice.count() > 0 and '请在上方选择' in dialog.reference_text.toPlainText(),
                                'event_source_recovery_does_not_restore_previous_event_reading')
                        else:
                            require(dialog.event_choice.count() == 0 and not dialog.event_bar.isVisible()
                                and '光明之末' in dialog.reference_text.toPlainText(),
                                'configuration_source_recovery_has_no_event_token_or_invented_event_controls')
                    source_negatives.append({'model': model.__name__, 'manifest': manifest_name,
                        'temporary_only': True, 'damaged_manifest_sha256': hashlib.sha256(raw + b' ').hexdigest(),
                        'restored_manifest_sha256': hashlib.sha256(raw).hexdigest()})

                def check_event_source_failure():
                    damage_source(events, EVENT_MANIFEST, 'event-source-invalidated', 'event')
                    later(check_configuration)

                def check_configuration():
                    if dialog.isVisible():
                        dialog.hide()
                    battle.set_stage('ro6_t_12'); tabs.setCurrentWidget(battle)
                    click(battle.entry_reference_button, window, 'autopsy_main_entry_QTest_click')
                    dialog.resize(*DIALOG_SIZE); dialog.reading_tabs.setCurrentWidget(dialog.reference_text); gui.processEvents()
                    require(dialog.stage_id == 'ro6_t_12' and dialog.packet['kind'] == 'configuration',
                        'autopsy_uses_its_own_configuration_reference_not_event_link')
                    require(not dialog.event_bar.isVisible() and dialog.event_choice.count() == 0
                        and not dialog.open_event_button.isEnabled(), 'autopsy_has_no_event_choices_or_navigation_button')
                    text = dialog.reference_text.toPlainText()
                    require(all(word in text for word in ('第3层普通作战', '第4层普通作战', '第5层普通作战',
                        '假层', '光明之末', '湮没', '未持有', '不保证每层', '不能据此归到第4层或秘境')),
                        'autopsy_default_chinese_separates_three_main_layers_fake_layer_marker_not_hold_and_unknown_actual')
                    result = dialog.packet['result']
                    require([r['main_floor_reference'] for r in result['rows']] == [3, 4, 5, None]
                        and all(result[k] is None for k in ('actual_eligibility', 'actual_node', 'actual_entry', 'actual_reward', 'actual_count'))
                        and result['floor_eligibility_evaluated'] is False,
                        'autopsy_configuration_neither_proves_current_entry_nor_changes_floor_eligibility')
                    configuration_observations.append({'stage_id': dialog.stage_id,
                        'main_floor_references': [r['main_floor_reference'] for r in result['rows']],
                        'row_labels': [r['label'] for r in result['rows']],
                        'event_controls_visible': dialog.event_bar.isVisible(),
                        'event_choice_count': dialog.event_choice.count(),
                        'default_reader_sha256': text_sha(text),
                        'actual_entry': result['actual_entry'], 'actual_node': result['actual_node'],
                        'actual_reward': result['actual_reward'], 'actual_count': result['actual_count'],
                        'floor_eligibility_evaluated': result['floor_eligibility_evaluated']})
                    save_image('autopsy-four-configurations', dialog, 'dialog')
                    damage_source(configurations, CONFIG_MANIFEST, 'configuration-source-invalidated', 'configuration')
                    later(check_cross_stage_clear)

                def check_cross_stage_clear():
                    if dialog.isVisible():
                        dialog.hide()
                    battle.set_stage('ro6_t_3'); tabs.setCurrentWidget(battle)
                    click(battle.entry_reference_button, window, 'cross_stage_event_reopen_QTest_click')
                    require(dialog.event_choice.currentData() is None and not dialog.open_event_button.isEnabled()
                        and '光明之末' not in dialog.reference_text.toPlainText(),
                        'configuration_to_event_change_clears_old_marker_text_and_event_selection')
                    packet = events.stage_event_references('ro6_t_3'); choose(dialog.event_choice, packet['rows'][0]['reference_id'])
                    old_token = deepcopy(packet['rows'][0]['token'])
                    battle.set_stage('ro6_t_6'); gui.processEvents()
                    require(not battle.entry_reference_button.isVisible() and dialog.packet is None
                        and dialog.event_choice.count() == 0 and not dialog.open_event_button.isEnabled(),
                        'unsupported_fixed_stage_clears_previous_entry_references')
                    require(window.show_battle_event_reference(old_token) is False, 'old_stage_token_cannot_navigate_after_stage_change')
                    if dialog.isVisible():
                        dialog.hide()
                    battle.set_stage('ro6_t_3')
                    click(battle.entry_reference_button, window, 'return_supported_stage_QTest_click')
                    require(dialog.event_choice.currentData() is None and dialog.event_choice.currentIndex() == -1,
                        'returning_to_supported_stage_does_not_reselect_stale_reference')
                    later(finish)

                def finish():
                    nonlocal done
                    expected = {(s, e, e + ':scene:' + str(sc), e + ':scene:' + str(sc) + ':choice:' + str(c)) for s, e, sc, c in CASES}
                    actual = {(r['stage_id'], r['event_id'], r['scene_key'], r['choice_key']) for r in navigated}
                    require(actual == expected and len(navigated) == len(expected), 'every_literal_documented_admitted_identity_really_navigated_once')
                    require(len(excluded_observations) == len(EXCLUDED), 'each_literal_explicit_emergency_exclusion_really_guarded')
                    require(window.run.state == initial_run, 'manual_reference_reading_never_changes_temporary_run_memory')
                    require(stage_context.context_data() == old_floor_data, 'existing_stage_floor_conditions_and_unknowns_unchanged')
                    require(bound_files() == before, 'selected_public_sources_stable_before_completion')
                    native_observations.extend([native(window, 'parent'), native(dialog, 'dialog')])
                    done = True

                def close_deadline():
                    nonlocal failure
                    if not done and failure is None:
                        failure = {'type': 'TimeoutError', 'message': 'New manual-entry checks not completed before deadline'}
                    close_owned()

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
            finally:
                # Close while all four state paths and all external guards are
                # still patched, including setup failures before gui.exec().
                if dialog is not None:
                    dialog.close()
                window.close()
                gui.processEvents()
                closed = not window.isVisible() and (dialog is None or not dialog.isVisible())
    except BaseException as error:
        failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
    report = {'section': 296, 'kind': 'isolated_native_windows_fixed_battle_entry_references',
        'passed': done and failure is None, 'failure': failure, 'started_at': started,
        'finished_at': datetime.now(timezone.utc).isoformat(), 'process_id': os.getpid(),
        'qpa': qpa, 'qt_exit_code': qt_exit, 'verification_window_closed': closed,
        'checks': checks, 'unique_checks': len(checks),
        'successful_assertion_executions_including_repeated_guards': executions,
        'requested_parent_client_size': list(SIZE), 'requested_dialog_client_size': list(DIALOG_SIZE),
        'native_observations': native_observations, 'screenshots': images, 'screenshot_count': len(images),
        'navigated_documented_entries': navigated,
        'actually_navigated_entry_count': len(navigated),
        'actually_navigated_stage_count': len({r['stage_id'] for r in navigated}),
        'explicit_exclusions': excluded_observations, 'source_negative_fixtures': source_negatives,
        'same_scope_refresh_observations': refresh_observations,
        'public_observations': [{'actually_navigated_stage_ids': sorted({r['stage_id'] for r in navigated}),
            'actual_manual_reference_clicks': len(navigated), 'guarded_explicit_exclusions': len(excluded_observations),
            'configuration_readings': configuration_observations,
            'completed_same_scope_refresh_paths': [r['path'] for r in refresh_observations],
            'damaged_temporary_source_models': [r['model'] for r in source_negatives],
            'actual_game_event_or_stage_entry': None, 'actual_generated_stage_floor_pool': None,
            'screenshots_are_representative_not_every_stage': True}],
        'source_sha256_before': before, 'source_sha256_after': after,
        'source_guard_is_selected_not_all_transitive_dependencies': True,
        'temporary_state_root': True, 'state_paths_replaced_before_constructor': ['ROOT', 'SETTINGS', 'OPERATOR_STATE', 'RUN_STATE'],
        'private_state_read_copied_or_restored': False, 'external_operation_attempts': attempts,
        'game_operated': False, 'game_captures': 0, 'chat_sent': False,
        'chat_attempted': bool(attempts['desktop_request'] or attempts['provider_chat']),
        'external_entrypoints_blocked_before_original_call': True,
        'original_project_window_operated_or_restarted': False,
        'actual_process_termination_verified_by_this_script': False,
        'owned_supervisor_exit_and_cleanup_required_separately': True,
        'launch_Popen_PID_must_be_recorded_separately_from_actual_fixture_PID': True,
        'scope': 'Actual new MainWindow button and every documented admitted event-option click, exact node scene/choice, battle reading preservation, autopsy separate configuration, temporary source-manifest damage/recovery and stale/cross-stage rejection. Representative screenshots only, no live game or complete floor/entry inference; no full rerun.'}
    with destination.open('x', encoding='utf8') as stream:
        stream.write(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
