"""Cache candidate: six ritual references and a manually opened fixed battle.
The root owns promotion and actual native execution. No actual weakening is inferred.
"""
import argparse
from contextlib import ExitStack
from copy import deepcopy
from datetime import datetime, timezone
from html import unescape
import hashlib, json, os, re
from pathlib import Path
import sys, tempfile, traceback
from unittest.mock import patch

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'rouge/app.py').is_file())
sys.path.insert(0, str(ROOT))
CANONICAL = 'scripts/verify_ritual_weakening_window_302.py'
PACKET = 'research/p3-ritual-weakening-302'
MANIFEST = PACKET + '/source-manifest.json'
DATA = 'rouge/data/ritual-weakening.json'
# Filled from the author's final actual HANDOFF before READY, never from a guessed result.
EXPECTED_SOURCE_PINS = {'research/p3-ritual-weakening-302/source-manifest.json': 'bb1ab31f0e41e7015d303368292d28a752f539e78f7b80be90329adb24f97182', 'rouge/data/ritual-weakening.json': '3e0533e212927bd9b50dd8f4f183ca97c5c02187f396a20718b049d7b7951138', 'rouge/ritual_weakening.py': '6467e17c40391f9197c9397cdd98c5fb066ae2a7cdf1c42f33098cc45b9b6752', 'rouge/data/battle-maps/ro6_b_6.png': '153423edbb0bb0eeadc9c5027da85639dc04f2926ddc7c244c1e5e811d7d8620', 'rouge/data/portraits/enemy_2150_shchmr.png': '4f7ce74fa8a5dc88161bf05ba5830d1b0dc7e770bff184b993f99261fcf42103'}
SIZE = (1050, 720)
DIALOG_SIZE = (900, 680)
BATTLE_SIZE = (1180, 850)
EVENT = 'community_group_032'
OTHER = 'community_group_001'
CASES = ((2, 0, 'choice_ro6_end3_3', 'rogue_6_chimera_weaken_1'),
         (2, 1, 'choice_ro6_end3_4', 'rogue_6_chimera_weaken_1'),
         (3, 0, 'choice_ro6_end3_6', 'rogue_6_chimera_weaken_3'),
         (3, 1, 'choice_ro6_end3_7', 'rogue_6_chimera_weaken_3'),
         (4, 0, 'choice_ro6_end3_9', 'rogue_6_chimera_weaken_2'),
         (4, 1, 'choice_ro6_end3_10', 'rogue_6_chimera_weaken_2'))
ACTUAL = ('actual_choice', 'actual_weakening', 'actual_attached', 'actual_inventory',
          'actual_consumed', 'actual_effect', 'actual_numeric_result', 'actual_eligible')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def text_sha(value):
    return hashlib.sha256(value.encode('utf8')).hexdigest()


def plain(value):
    value = unescape(value or '')
    value = re.sub(r'<br\s*/?>', '\n', value, flags=re.I)
    return re.sub(r'</?[A-Za-z][^<>]*>|<[@$][^<>]*>|</>', '', value).strip()


def identity(case):
    scene = EVENT + ':scene:' + str(case[0])
    return EVENT, scene, scene + ':choice:' + str(case[1])


def bound_files():
    names = {CANONICAL, MANIFEST, DATA, 'rouge/app.py', 'rouge/node_catalog_view.py',
             'rouge/node_catalog.py', 'rouge/event_planning.py', 'rouge/player_node_information.py',
             'rouge/ui_state.py', 'rouge/branch_choice.py', 'rouge/view_catalog.py',
             'rouge/ritual_weakening.py', 'rouge/ritual_weakening_view.py',
             'rouge/battle_view.py', 'rouge/battle_preview.py', 'rouge/spawn_reference.py',
             'rouge/map_projection.py', 'rouge/player_tile_information.py',
             'rouge/enemy_panel.py', 'rouge/enemy_skills.py',
             'rouge/data/battle-previews.json', 'rouge/data/battle-map-projections.json',
             'rouge/data/fixed-landmark-references.json', 'rouge/data/view-catalog.json',
             'scripts/build_ritual_weakening_302.py',
             'tests/test_ritual_weakening_302.py', 'tests/test_ritual_weakening_view_302.py',
             'tests/test_ritual_weakening_integration_302.py'}
    names.update(read(ROOT / MANIFEST)['files'])
    names.update(p.relative_to(ROOT).as_posix() for p in (ROOT / PACKET).rglob('*') if p.is_file())
    battle = read(ROOT / 'rouge/data/battle-previews.json')['stages']['ro6_b_6']
    names.add('rouge/data/' + battle['image']['file'])
    # The pictured fixed enemy is selected by its exact ID, never by a similar icon.
    assets = read(ROOT / 'rouge/data/view-catalog.json')
    portrait = assets['enemies']['enemy_2150_shchmr'].get('portrait')
    if portrait is not None:
        names.add('rouge/data/' + assets['images'][portrait]['file'])
    names.update(EXPECTED_SOURCE_PINS)
    result = {}
    for name in sorted(names):
        p = ROOT / name
        if not p.is_file() or p.is_symlink() or not p.resolve().is_relative_to(ROOT.resolve()):
            raise ValueError('Regular selected public source required: ' + name)
        result[name] = sha(p)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', required=True)
    parser.add_argument('--visible-ms', type=int, default=120000)
    args = parser.parse_args()
    destination = Path(args.receipt).resolve()
    if destination.exists():
        raise FileExistsError('Preserve the first actual receipt.')
    if args.visible_ms <= 0:
        raise ValueError('Positive visible interval required.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    before, after = {}, {}
    checks, images, handles, readings, refreshes, negatives, battle_readings = [], [], [], [], [], [], []
    executions = 0
    failure, done, closed, qpa, qt_exit = None, False, False, None, None
    attempts = {k: 0 for k in ('game_enumeration', 'game_connect', 'game_capture', 'game_next_frame',
                               'desktop_start', 'desktop_request', 'provider_chat', 'credential_read')}

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
            raise RuntimeError('Actual native Windows required.')
        if Path(__file__).resolve() != (ROOT / CANONICAL).resolve():
            raise RuntimeError('A cache script is not acceptance.')
        require(bool(EXPECTED_SOURCE_PINS) and MANIFEST in EXPECTED_SOURCE_PINS and DATA in EXPECTED_SOURCE_PINS
                and all(sha(ROOT / n) == digest for n, digest in EXPECTED_SOURCE_PINS.items()),
                'final_ritual_authority_data_and_selected_assets_exact_before_window')
        before = bound_files()
        from rouge import ritual_weakening as model, node_catalog as catalog
        from rouge.battle_preview import battle_data, enemy_preview
        require(model.event_reference(EVENT)['source_valid'] is True,
                'actual_ritual_fixed_reference_valid_before_Qt')
        fixed_stage = deepcopy(battle_data()['stages']['ro6_b_6'])
        fixed_enemy = deepcopy(enemy_preview('ro6_b_6', 'enemy_2150_shchmr', 0))
        from PySide6.QtCore import Qt, QPoint, QRect, QTimer
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QApplication
        from PySide6.QtTest import QTest
        import win32gui, win32process
        from rouge import app as app_module
        gui = QApplication([])
        qpa = gui.platformName()
        require(qpa == 'windows', 'actual_windows_QPA')

        class PublicWindow(app_module.MainWindow):
            def refresh_windows(self):
                self.windows.clear()

        with tempfile.TemporaryDirectory(prefix='rouge-302-ritual-') as folder, ExitStack() as stack:
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
                window.setWindowTitle('第302节 · 调谐仪式与相关作战资料（公开隔离验收）')
                window.resize(*SIZE)
                window.show()
                panel = window.node_catalog
                tabs = window.centralWidget()
                initial_run = deepcopy(window.run.state)
                calculation_before = tuple((window.relic_list.item(i).data(Qt.ItemDataRole.UserRole),
                                            window.relic_list.item(i).checkState().value)
                                           for i in range(window.relic_list.count()))
                parent_saved = dialog_saved = battle_saved = None
                initial_battle_object = None
                main_battle_saved = None

                def isolated():
                    require(not window.auto.isChecked() and not window.timer.isActive(),
                            'automatic_sampling_and_timer_disabled')
                    require(window.capture.target is None and window.desktop.process is None,
                            'capture_and_desktop_backend_inactive')
                    require(all(v == 0 for v in attempts.values()), 'all_eight_external_original_entry_attempts_zero')

                def native(widget, kind):
                    hwnd = int(widget.winId())
                    thread, pid = win32process.GetWindowThreadProcessId(hwnd)
                    size = {'parent': SIZE, 'dialog': DIALOG_SIZE, 'battle': BATTLE_SIZE}[kind]
                    require(win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd) and widget.isVisible(),
                            kind + '_actual_owned_visible_HWND')
                    require(pid == os.getpid() and not win32gui.IsIconic(hwnd), kind + '_actual_fixture_PID_not_minimized')
                    require([widget.width(), widget.height()] == list(size), kind + '_actual_client_size_exact')
                    return {'kind': kind, 'hwnd': hwnd, 'process_id': pid, 'thread_id': thread,
                            'qpa': qpa, 'client_size': [widget.width(), widget.height()]}

                def choose(control, value):
                    at = control.findData(value)
                    require(at >= 0, 'exact_complete_reference_control_identity_present')
                    control.setCurrentIndex(at)
                    gui.processEvents()

                def event(event_id):
                    panel.show_directory()
                    panel.set_map_context(None)
                    choose(panel.kind, 'event')
                    choose(panel.floor, None)
                    choose(panel.node_type, None)
                    panel.search.setText(catalog._event(event_id)['title'])
                    tabs.setCurrentWidget(panel)
                    at = next(i for i, e in enumerate(panel.entries)
                              if e['kind'] == 'event' and e['record']['id'] == event_id)
                    item = panel.list.flat[at]
                    item.parent().setExpanded(True)
                    panel.list.scrollToItem(item)
                    gui.processEvents()
                    rect = panel.list.visualItemRect(item)
                    require(not rect.isEmpty() and panel.list.viewport().rect().contains(rect.center()),
                            'actual_exact_directory_event_item_visible')
                    QTest.mouseClick(panel.list.viewport(), Qt.MouseButton.LeftButton, pos=rect.center())
                    gui.processEvents()
                    require(panel.list.selected_key() == panel.entries[at]['key'],
                            'actual_QTest_selected_complete_event_identity_not_same_title')

                def click(button, owner, label):
                    gui.processEvents()
                    rect = QRect(button.mapTo(owner, QPoint(0, 0)), button.size())
                    require(button.isVisible() and button.isEnabled() and not button.visibleRegion().isEmpty()
                            and owner.rect().contains(rect), label + '_visible_enabled_inside_actual_client')
                    QTest.mouseClick(button, Qt.MouseButton.LeftButton, pos=button.rect().center())
                    gui.processEvents()

                def reader(widget):
                    cursor = widget.textCursor()
                    return {'text_sha256': text_sha(widget.toPlainText()), 'anchor': cursor.anchor(),
                            'position': cursor.position(), 'selected': cursor.selectedText(),
                            'vertical': widget.verticalScrollBar().value(), 'horizontal': widget.horizontalScrollBar().value()}

                def parent_state():
                    return {'key': panel.list.selected_key(), 'tab': panel.reading_tabs.currentIndex(),
                            'scene': panel.event_scene_filter.currentData(), 'choice': panel.event_choice_filter.currentData(),
                            'stage': panel.event_stage.currentData(), 'search': panel.search.text(),
                            'search_cursor': panel.search.cursorPosition(), 'search_selection': panel.search.selectedText(),
                            'player': reader(panel.player_detail), 'source': reader(panel.detail)}

                def dialog_state():
                    return {'event': dialog.event_id, 'scope': deepcopy(dialog.scope_key),
                            'choice': dialog.choice.currentData(), 'tab': dialog.reading_tabs.currentIndex(),
                            'view_key': deepcopy(dialog._view_key), 'reading_key': deepcopy(dialog._reading_key),
                            'player': reader(dialog.player_text), 'source': reader(dialog.source_text)}

                def battle_state(battle=None):
                    battle = dialog.battle_preview if battle is None else battle
                    if battle is None:
                        return None
                    selected = battle.spawn_list.currentItem()
                    return {'stage': battle.current_stage, 'context': deepcopy(battle.context),
                            'wave': battle.wave_combo.currentData(), 'enemy_branch': battle.enemy_choices.branch.currentData(),
                            'enemy': deepcopy(battle.enemy_combo.currentData()), 'branches': battle.include_branches.isChecked(),
                            'technical': battle.technical.isChecked(), 'reward': deepcopy(battle.reward_combo.currentData()),
                            'row': None if selected is None else selected.data(Qt.ItemDataRole.UserRole)['id'],
                            'occurrence': battle.occurrence.value(), 'list_scroll': battle.spawn_list.verticalScrollBar().value(),
                            'tile': deepcopy(battle._tile_cell), 'grid_cell': deepcopy(battle.grid.reference_cell),
                            'image_cell': deepcopy(battle.original.reference_cell),
                            'image_selected': deepcopy(battle.original.selected),
                            'spawn_reader': reader(battle.spawn_detail), 'enemy_reader': reader(battle.enemy_detail)}

                def prime(widget, scroll=False):
                    gui.processEvents()
                    require(widget.document().characterCount() > 30, 'actual_existing_reader_text_can_be_selected')
                    cursor = widget.textCursor()
                    cursor.setPosition(5)
                    cursor.setPosition(25, QTextCursor.MoveMode.KeepAnchor)
                    widget.setTextCursor(cursor)
                    if scroll:
                        bar = widget.verticalScrollBar()
                        require(bar.maximum() > 0, 'actual_existing_reader_has_real_scroll_range')
                        bar.setValue(max(1, bar.maximum() // 2))
                        require(bar.value() > 0, 'actual_existing_reader_nonzero_scroll_set')
                    require(bool(widget.textCursor().selectedText()), 'actual_existing_reader_nonempty_selection')

                def actual_unknown(value):
                    return all(k in value and value[k] is None for k in ACTUAL)

                def select_case(case):
                    event_id, scene_key, choice_key = identity(case)
                    expected = next(row for row in dialog.packet['choices']
                                    if row['scene_key'] == scene_key and row['choice_key'] == choice_key)
                    previous_battle = dialog.battle_window
                    choose(dialog.choice, expected['reference_id'])
                    details = model.weakening_details(event_id, scene_key, choice_key)
                    require(details['status'] == 'documented_reference' and details['source_valid'] is True
                            and details['reference'] == expected, 'fresh_details_exact_complete_six_tuple_not_title_matching')
                    require(expected['original_choice_id'] == case[2] and expected['weakening_id'] == case[3],
                            'actual_primary_choice_order_maps_to_weakening_one_three_two')
                    require(actual_unknown(details) and actual_unknown(expected) and actual_unknown(dialog.packet)
                            and details['calculation_applied'] is False and details['run_state_updated'] is False,
                            'all_eight_actual_outcomes_unknown_no_weakening_calculation_or_run_write')
                    related = details['related_stage_reference']
                    require(related == expected['related_stage_reference'] and related['stage_id'] == 'ro6_b_6'
                            and related['title'] == '畸症' and related['reference_only'] is True
                            and related['immediate_transition'] is None
                            and related['enemy_selector'] == 'enemy_2150_shchmr'
                            and related['enemy_level_reference'] is None,
                            'explicit_related_fixed_battle_and_enemy_selector_do_not_assert_a_FEATURE_level_or_immediate_transition')
                    require(dialog.battle_window is previous_battle,
                            'manual_choice_reads_only_and_never_automatically_creates_related_battle')
                    dialog.reading_tabs.setCurrentWidget(dialog.player_text)
                    gui.processEvents()
                    text = dialog.player_text.toPlainText()
                    require(plain(expected['effect_text']) in text and plain(expected['choice_title']) in text
                            and all(t in text for t in ('【交付方式与条件资料】', '【同一效果的另一种方式】',
                                                       '【资料所述弱化效果】', '【选项叙述原文】',
                                                       '不默认1件', '不表示一次替代全部三个步骤',
                                                       '尚未确认', '不会', '立即进入')),
                            'actual_player_page_contains_exact_exchange_effect_alternative_and_actual_unknown_boundary')
                    require(plain(expected['choice_description']) in text,
                            'complete_option_narrative_is_retained_separate_from_verified_effect')
                    if case[3] == 'rogue_6_chimera_weaken_1':
                        require('首次释放' in plain(expected['effect_text']), 'no_destruction_reference_keeps_first_release_limit')
                    if case[3] == 'rogue_6_chimera_weaken_2':
                        require('不能当作无伤或不再扣血' in text and '0.5' not in text,
                                'damage_reduction_not_promoted_to_immunity_or_actual_numeric_result')
                    if expected['condition_text']:
                        require(plain(expected['condition_text']) in text, 'each_private_key_retains_its_own_complete_condition')
                    require(not any(t in text for t in ('community_group_', 'choice_ro6_', 'enemy_2150_', 'https://')),
                            'default_ritual_player_text_has_no_raw_IDs_or_URLs')
                    technical = json.loads(dialog.source_text.toPlainText())
                    require(technical['selected_weakening_details'] == details,
                            'technical_reader_retains_complete_selected_details_and_original_identity')
                    return details

                def screenshot(name, kind='dialog'):
                    isolated()
                    widget = dialog if kind == 'dialog' else dialog.battle_window
                    shown_effect = None
                    if kind == 'dialog':
                        require(dialog.reading_tabs.currentWidget() is dialog.player_text,
                                'representative_ritual_PNG_directly_shows_player_body')
                        if name.startswith('player-effect-'):
                            shown_effect = plain(readings[-1]['effect_text'])
                            cursor = dialog.player_text.document().find(shown_effect)
                            require(not cursor.isNull(), 'representative_PNG_effect_exists_in_actual_player_document')
                            dialog.player_text.setTextCursor(cursor)
                            dialog.player_text.ensureCursorVisible()
                            gui.processEvents()
                            require(dialog.player_text.viewport().rect().contains(dialog.player_text.cursorRect().center()),
                                    'representative_PNG_exact_effect_is_anchored_in_real_player_viewport')
                    observation = native(widget, kind)
                    path = destination.with_name(destination.stem + '-' + name + '.png')
                    if path.exists():
                        raise FileExistsError('Preserve first actual PNG.')
                    pixels = widget.grab()
                    require(not pixels.isNull() and pixels.save(str(path), 'PNG'), 'actual_owned_native_PNG_saved')
                    images.append({'name': name, 'path': str(path), 'sha256': sha(path), 'native_window': observation,
                                   'direct_player_text': kind == 'dialog', 'related_fixed_map': kind == 'battle',
                                   'effect_text_anchored_in_player_viewport': shown_effect})

                def close_owned():
                    if dialog is not None:
                        if dialog.battle_window is not None:
                            dialog.battle_window.close()
                        dialog.close()
                    window.close()

                def later(callback, delay=150):
                    def guarded():
                        nonlocal failure, done
                        try:
                            isolated()
                            callback()
                        except BaseException as error:
                            failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
                            done = False
                            close_owned()
                            gui.exit(1)
                    QTimer.singleShot(delay, guarded)

                def begin():
                    nonlocal parent_saved, main_battle_saved
                    # Give the existing main battle page a real manual public map selection
                    # before opening the new event reader, so parent-map preservation is useful.
                    main_battle = window.battle_preview
                    main_battle.set_stage('ro6_b_6')
                    tabs.setCurrentWidget(main_battle)
                    gui.processEvents()
                    row = next(r for r in main_battle.rows if r['action']['key'] == 'enemy_2150_shchmr'
                               and r['route']['start'] is not None)
                    QTest.mouseClick(main_battle.grid, Qt.MouseButton.LeftButton,
                                     pos=main_battle.grid.cell_center(row['route']['start']).toPoint())
                    gui.processEvents()
                    require(main_battle.grid.selected is not None, 'existing_parent_fixed_map_has_real_manual_selection_before_new_reader')
                    main_battle_saved = battle_state(main_battle)
                    event(EVENT)
                    panel.reading_tabs.setCurrentWidget(panel.detail)
                    prime(panel.detail, True)
                    panel.search.setSelection(0, 2)
                    parent_saved = parent_state()
                    require(panel.ritual_weakening_window is None and panel.ritual_weakening_button.isVisible()
                            and panel.ritual_weakening_button.isEnabled(), 'real_MainWindow_entry_is_manual_not_precreated')
                    handles.append(native(window, 'parent'))
                    click(panel.ritual_weakening_button, window, 'actual_MainWindow_ritual_entry_QTest_click')
                    later(opened)

                def opened():
                    nonlocal dialog, dialog_saved
                    dialog = panel.ritual_weakening_window
                    require(dialog is not None and dialog.parent() is panel, 'actual_parent_button_created_owned_ritual_reader')
                    dialog.resize(*DIALOG_SIZE)
                    gui.processEvents()
                    handles.append(native(dialog, 'dialog'))
                    require(dialog.choice.count() == len(CASES) and dialog.choice.currentIndex() == -1
                            and dialog._view_key is None and dialog.battle_window is None and not dialog.open_stage_button.isEnabled(),
                            'six_choices_default_unselected_without_automatic_battle_or_effect')
                    require(parent_state() == parent_saved, 'opening_ritual_preserves_parent_filters_tabs_scroll_and_text_selection')
                    dialog.reading_tabs.setCurrentWidget(dialog.source_text)
                    prime(dialog.source_text, True)
                    dialog_saved = dialog_state()
                    later(unselected_refresh)

                def unselected_refresh():
                    panel.refresh()
                    gui.processEvents()
                    require(dialog_state() == dialog_saved and parent_state() == parent_saved and dialog.battle_window is None,
                            'unselected_same_scope_parent_refresh_preserves_real_source_scroll_and_selection')
                    refreshes.append({'path': 'unselected_parent', 'selected': None,
                                      'nonzero_scroll': dialog.source_text.verticalScrollBar().value(),
                                      'selection': dialog.source_text.textCursor().selectedText(), 'parent_unchanged': True})
                    later(read_next)

                def read_next():
                    case = CASES[len(readings)]
                    parent_before = parent_state()
                    details = select_case(case)
                    require(parent_state() == parent_before, 'manual_full_tuple_selection_leaves_parent_reading_unchanged')
                    row = details['reference']
                    readings.append({'event_id': EVENT, 'scene_key': row['scene_key'], 'choice_key': row['choice_key'],
                                     'reference_id': row['reference_id'], 'original_choice_id': row['original_choice_id'],
                                     'weakening_id': row['weakening_id'], 'choice_title': row['choice_title'],
                                     'condition_text': row['condition_text'], 'effect_text': row['effect_text'],
                                     'related_stage_id': details['related_stage_reference']['stage_id'],
                                     'actual_effect': None, 'calculation_applied': False})
                    if case[1] == 0:
                        screenshot('player-effect-' + case[3])
                    if len(readings) < len(CASES):
                        later(read_next)
                    else:
                        later(open_battle)

                def open_battle():
                    nonlocal initial_battle_object
                    require(dialog.battle_window is None, 'all_six_manual_choices_created_no_battle_before_explicit_button')
                    previous = parent_state()
                    click(dialog.open_stage_button, dialog, 'actual_manual_related_fixed_stage_QTest_click')
                    require(parent_state() == previous, 'manual_related_preview_does_not_change_parent_event_reading')
                    require(dialog.battle_window is not None and dialog.battle_preview is not None,
                            'explicit_related_button_opens_separate_owned_fixed_battle')
                    initial_battle_object = dialog.battle_preview
                    dialog.battle_window.resize(*BATTLE_SIZE)
                    gui.processEvents()
                    handles.append(native(dialog.battle_window, 'battle'))
                    later(configure_battle)

                def configure_battle():
                    nonlocal parent_saved, dialog_saved, battle_saved
                    battle = dialog.battle_preview
                    require(battle.current_stage == 'ro6_b_6' and battle.context == {}
                            and battle.grid.stage == fixed_stage and battle.original.stage == fixed_stage,
                            'related_preview_uses_exact_fixed_stage_unmodified_by_ritual_effect')
                    enemy = ('enemy_2150_shchmr', 0)
                    require(sum(e['id'] == enemy[0] and e['level'] == enemy[1] for e in fixed_stage['enemies']) == 1,
                            'related_fixed_enemy_identity_and_original_reference_level_unique')
                    battle.enemy_choices.select_value(enemy)
                    gui.processEvents()
                    require(battle.enemy_combo.currentData() == enemy and battle._shown_enemy == ('ro6_b_6', *enemy)
                            and battle.rows and all(r['action']['key'] == enemy[0] for r in battle.rows),
                            'actual_fixed_enemy_selection_and_its_main_route_rows_match_related_identity')
                    require(enemy_preview('ro6_b_6', *enemy) == fixed_enemy,
                            'reading_ritual_does_not_change_fixed_enemy_panel_or_skills')
                    row = next((r for r in battle.rows if r['route']['start'] is not None), None)
                    require(row is not None, 'fixed_enemy_has_actual_source_route_start_for_readonly_map_selection')
                    cell = row['route']['start']
                    QTest.mouseClick(battle.grid, Qt.MouseButton.LeftButton, pos=battle.grid.cell_center(cell).toPoint())
                    gui.processEvents()
                    require(battle.grid.selected is not None and battle.grid.selected['action']['key'] == enemy[0],
                            'actual_grid_click_selects_related_fixed_enemy_source_row')
                    battle.technical.setChecked(False)
                    gui.processEvents()
                    require(not battle.original.pixmap.isNull() and '畸症' in battle.summary.text(),
                            'related_fixed_map_image_decodable_and_player_stage_name_visible')
                    screenshot('related-fixed-map-player', 'battle')
                    prime(battle.enemy_detail, True)
                    prime(battle.spawn_detail)
                    parent_saved = parent_state()
                    dialog.reading_tabs.setCurrentWidget(dialog.source_text)
                    prime(dialog.source_text, True)
                    dialog_saved = dialog_state()
                    battle_saved = battle_state()
                    battle_readings.append({'stage_id': 'ro6_b_6', 'enemy_id': enemy[0], 'original_reference_level': enemy[1],
                                            'selected_row': battle_saved['row'], 'selected_source_cell': cell,
                                            'context': deepcopy(battle.context), 'actual_effect': None,
                                            'actual_transition': None, 'fixed_enemy_unmodified': True})
                    later(selected_refresh)

                def selected_refresh():
                    selected = [r for r in refreshes if r['selected'] is not None]
                    callbacks = [dialog.refresh_reference, panel.refresh,
                                 lambda: dialog.set_reference(EVENT, scope_key=deepcopy(panel.list.selected_key()))]
                    callbacks[len(selected)]()
                    gui.processEvents()
                    require(dialog_state() == dialog_saved and parent_state() == parent_saved
                            and dialog.battle_preview is initial_battle_object and battle_state() == battle_saved,
                            'same_scope_refresh_preserves_choice_readers_and_existing_battle_filters_map_context_scroll')
                    refreshes.append({'path': ['selected_dialog', 'selected_parent', 'selected_same_reference'][len(selected)],
                                      'selected': dialog.choice.currentData(), 'nonzero_scroll': dialog.source_text.verticalScrollBar().value(),
                                      'selection': dialog.source_text.textCursor().selectedText(), 'parent_unchanged': True,
                                      'battle_unchanged': True})
                    if len(selected) < 2:
                        later(selected_refresh)
                    else:
                        later(source_failure)

                def source_failure():
                    manifest = read(ROOT / MANIFEST)
                    clone = temporary / 'public-source-negative'
                    for name in set(manifest['runtime_files']) | {MANIFEST}:
                        source = ROOT / name
                        require(source.is_file() and not source.is_symlink()
                                and source.resolve().is_relative_to(ROOT.resolve()), 'negative_fixture_copies_only_regular_public_sources')
                        target = clone / name
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(source.read_bytes())
                    target = clone / MANIFEST
                    raw = target.read_bytes()
                    previous_battle = dialog.battle_preview
                    previous_window = dialog.battle_window
                    previous_hwnd = int(previous_window.winId())
                    with patch.object(model, 'ROOT', clone):
                        require(model.weakening_details(*identity(CASES[-1]))['source_valid'] is True,
                                'complete_public_runtime_clone_warmed_valid_before_real_manifest_damage')
                        try:
                            target.write_bytes(raw + b' ')
                            dialog.refresh_reference()
                            panel.refresh()
                            gui.processEvents()
                            failed_details = model.weakening_details(*identity(CASES[-1]))
                            failed_packet = model.event_reference(EVENT)
                            require(failed_details['source_valid'] is False and failed_details['reference'] is None
                                    and failed_packet['choices'] == [] and failed_packet['weakening_references'] == [],
                                    'fresh_damaged_authority_returns_unknown_without_old_effect_or_choices')
                            require(dialog.packet is None and dialog.choice.currentIndex() == -1
                                    and dialog._view_key is None and not dialog.open_stage_button.isEnabled()
                                    and not panel.ritual_weakening_button.isEnabled(),
                                    'source_failure_clears_choice_and_both_manual_entry_eligibilities')
                            require(dialog.battle_preview is None and dialog.battle_window is None
                                    and previous_battle.current_stage is None
                                    and not win32gui.IsWindowVisible(previous_hwnd),
                                    'source_failure_clears_old_related_stage_and_owned_child_reference')
                            require(all('已清除' in w.toPlainText() for w in (dialog.player_text, dialog.source_text)),
                                    'source_failure_clears_both_old_weakening_and_evidence_readers')
                            screenshot('player-source-unavailable')
                        finally:
                            target.write_bytes(raw)
                        require(sha(target) == EXPECTED_SOURCE_PINS[MANIFEST], 'temporary_damaged_source_restored_exact_bytes')
                        dialog.refresh_reference()
                        panel.refresh()
                        gui.processEvents()
                        require(dialog.packet is not None and dialog.choice.currentIndex() == -1
                                and dialog._view_key is None and dialog.battle_window is None
                                and not dialog.open_stage_button.isEnabled() and panel.ritual_weakening_button.isEnabled(),
                                'source_recovery_requires_manual_reselection_and_manual_related_battle_reopen')
                    negatives.append({'kind': 'warm_complete_runtime_clone_manifest_bytes', 'member': MANIFEST,
                                      'old_child_stage_cleared': True, 'actual_effect': None,
                                      'restore_sha256': sha(target), 'restored_unselected': True})
                    later(reopen_and_switch)

                def reopen_and_switch():
                    select_case(CASES[0])
                    click(dialog.open_stage_button, dialog, 'actual_manual_related_stage_after_source_restore')
                    require(dialog.battle_preview is not None and dialog.battle_preview.current_stage == 'ro6_b_6',
                            'only_explicit_new_manual_action_reopens_restored_fixed_battle')
                    previous = dialog.battle_preview
                    event(OTHER)
                    gui.processEvents()
                    require(not panel.ritual_weakening_button.isVisible() and dialog.packet is None
                            and dialog.choice.currentIndex() == -1 and dialog.battle_window is None
                            and dialog.battle_preview is None and previous.current_stage is None
                            and all('已清除' in w.toPlainText() for w in (dialog.player_text, dialog.source_text)),
                            'non_target_scope_clears_all_old_ritual_and_related_fixed_stage_content')
                    later(finish)

                def finish():
                    nonlocal done
                    require(len(readings) == len(CASES)
                            and {(r['scene_key'], r['choice_key'], r['original_choice_id'], r['weakening_id']) for r in readings}
                            == {(identity(c)[1], identity(c)[2], c[2], c[3]) for c in CASES},
                            'all_six_exact_choices_and_one_three_two_mapping_actually_read')
                    private = [r for r in readings if r['choice_key'].endswith(':choice:1')]
                    require(len(private) == 3 and len({r['choice_title'] for r in private}) == 1
                            and len({r['reference_id'] for r in private}) == 3
                            and len({r['weakening_id'] for r in private}) == 3,
                            'three_same_title_private_key_options_keep_distinct_complete_identity_and_effect')
                    require(len(images) == 5 and sum(r['direct_player_text'] for r in images) == 4
                            and sum(r['related_fixed_map'] for r in images) == 1,
                            'five_actual_images_include_three_effect_bodies_source_failure_and_manual_fixed_map')
                    require(len(refreshes) == 4 and all(r['nonzero_scroll'] > 0 and r['selection']
                                                      and r['parent_unchanged'] for r in refreshes),
                            'selected_and_unselected_refreshes_preserve_actual_nonzero_reading')
                    calculation_after = tuple((window.relic_list.item(i).data(Qt.ItemDataRole.UserRole),
                                               window.relic_list.item(i).checkState().value)
                                              for i in range(window.relic_list.count()))
                    require(window.run.state == initial_run and calculation_after == calculation_before,
                            'ritual_and_manual_fixed_battle_reading_does_not_change_run_or_calculation_relics')
                    require(battle_state(window.battle_preview) == main_battle_saved,
                            'existing_MainWindow_battle_filters_selected_map_and_readers_not_changed_by_new_dialog')
                    require(bound_files() == before, 'selected_public_sources_unchanged_before_completion')
                    handles.append(native(window, 'parent'))
                    done = True

                def deadline():
                    nonlocal failure
                    if not done and failure is None:
                        failure = {'type': 'TimeoutError', 'message': 'Actual ritual reading checks incomplete.'}
                    close_owned()

                later(begin, 500)
                QTimer.singleShot(max(30000, args.visible_ms), deadline)
                qt_exit = gui.exec()
                closed = (not window.isVisible() and not (dialog and dialog.isVisible())
                          and not (dialog and dialog.battle_window and dialog.battle_window.isVisible()))
                if qt_exit != 0 or not closed or not done:
                    if failure is None:
                        failure = {'type': 'RuntimeError', 'message': 'Actual checks, Qt or owned-window closure incomplete.'}
                if failure is None:
                    isolated()
                after = bound_files()
                if before != after and failure is None:
                    failure = {'type': 'AssertionError', 'message': 'Selected sources changed before closure.'}
            finally:
                close_owned()
                gui.processEvents()
                closed = (not window.isVisible() and not (dialog and dialog.isVisible())
                          and not (dialog and dialog.battle_window and dialog.battle_window.isVisible()))
    except BaseException as error:
        failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
    report = {'section': 302, 'kind': 'isolated_native_windows_ritual_weakening_reader',
              'passed': done and failure is None, 'failure': failure, 'started_at': started,
              'finished_at': datetime.now(timezone.utc).isoformat(), 'process_id': os.getpid(), 'qpa': qpa,
              'qt_exit_code': qt_exit, 'verification_window_closed': closed, 'checks': checks,
              'unique_checks': len(checks), 'successful_assertion_executions_including_repeated_guards': executions,
              'requested_parent_client_size': list(SIZE), 'requested_dialog_client_size': list(DIALOG_SIZE),
              'requested_related_battle_client_size': list(BATTLE_SIZE), 'native_observations': handles,
              'screenshots': images, 'screenshot_count': len(images), 'actual_choice_readings': readings,
              'related_fixed_battle_readings': battle_readings, 'same_scope_refresh_observations': refreshes,
              'source_negative_fixtures': negatives, 'source_sha256_before': before, 'source_sha256_after': after,
              'source_guard_is_selected_not_all_transitive_dependencies': True, 'temporary_state_root': True,
              'state_paths_replaced_before_constructor': ['ROOT', 'SETTINGS', 'OPERATOR_STATE', 'RUN_STATE'],
              'private_state_read_copied_or_restored': False, 'external_operation_attempts': attempts,
              'external_entrypoints_blocked_before_original_call': True, 'game_operated': False,
              'game_captures': 0, 'chat_sent': False,
              'chat_attempted': bool(attempts['desktop_request'] or attempts['provider_chat']),
              'original_project_window_operated_or_restarted': False,
              'actual_process_termination_verified_by_this_script': False,
              'owned_supervisor_exit_and_cleanup_required_separately': True,
              'launch_Popen_PID_must_be_recorded_separately_from_actual_fixture_PID': True,
              'actual_weakening_activation_or_numeric_result_verified': False,
              'scope': 'Six exact submission references, three distinct conditional weakening descriptions, manually opened related fixed battle; no actual submission, activation or calculation.'}
    with destination.open('x', encoding='utf8') as stream:
        stream.write(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
