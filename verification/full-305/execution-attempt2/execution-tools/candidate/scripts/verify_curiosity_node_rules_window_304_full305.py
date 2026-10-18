"""Isolated native reading of five fate-node documents and manual fixed battle.

This cache candidate must be promoted before acceptance. It never operates the
game, changes a run, marks a node, or asserts a live transformation/revisit.
"""
import argparse
from contextlib import ExitStack
from copy import deepcopy
from datetime import datetime, timezone
from html import unescape
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import traceback
from unittest.mock import patch

ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'rouge/app.py').is_file())
sys.path.insert(0, str(ROOT))
CANONICAL = 'scripts/verify_curiosity_node_rules_window_304_full305.py'
PACKET = 'research/p3-curiosity-node-rules-304'
MANIFEST = PACKET + '/source-manifest.json'
DATA = 'rouge/data/curiosity-node-rules.json'
# Bound to actual frozen author/UI files before READY, never to guessed results.
EXPECTED_SOURCE_PINS = {'research/p3-curiosity-node-rules-304/README.md': '8248063c0ff7224b344422eb4f984dcf47ea9e13a1e7293bc16beba29b717001', 'research/p3-curiosity-node-rules-304/SOURCE_SCHEMA.md': '653bb998738f8fd731e8749a70ba26dfab866068b99518a5f524bbfee9039a67', 'research/p3-curiosity-node-rules-304/choice-rule-map.json': '209d821d1636ebdc6db298fbb97885b5004366542844fc9f42947d9be3d307e6', 'research/p3-curiosity-node-rules-304/selected-authority-records.json': '187ded7d38f6d8b926fbeebf9f8977d4d7ad2ad2370d5ac84d4fd71254a2cb62', 'research/p3-curiosity-node-rules-304/source-authority.json': '8ad4aa78d9848a7c74eef81bfedc9266001ec230b5cdd581d2681f637ac15bff', 'research/p3-curiosity-node-rules-304/source-manifest.json': '6e4bddeef0ba5913504725d2f235f5384e8f7d1b51c1e89d6de5b7d977304237', 'rouge/curiosity_node_rules.py': 'cc73fa8f2f30dd17a49a63de1aec931dc276fc22eeff91232e17d599e354ec01', 'rouge/curiosity_node_rules_view.py': '2636dd08ac1075ad651fecf42e64d81893225e83bc7a9b6b18fdae7190c9a5b7', 'rouge/data/battle-maps/ro6_b_5.png': '884031921d3ccbc68f8960e4184e5391461bf82ea063a55a98dbe84d39dd54b3', 'rouge/data/curiosity-node-rules.json': '62529af5ba7f4c30bc57c95a98b03c4457f7426cd6d5bb49efd3abaee325285a', 'rouge/node_catalog_view.py': '5811cae02b0e02231cfaed2fb7764e18eaf07eb3e75ac3a879b4c7057201e9ba', 'scripts/build_curiosity_node_rules_304.py': 'af12290c0019aefe81fe4d59f8952756c344a13c470b40e5a6aa7dfebeaa1413', 'tests/test_curiosity_node_rules_304.py': '2c7e8c8741d7ef1d420df63d1bba80099a0c7ca634a4fa178b89a9a2d141314d', 'tests/test_curiosity_node_rules_view_304.py': 'f8afc2414456fce787338f0a300920c5f8eb47bedc4b9d344f4dff2f5818a4cb'}
SIZE = (1280, 900)
DIALOG_SIZE = (1080, 900)
BATTLE_SIZE = (1180, 850)
A, B, OTHER = 'community_group_030', 'community_group_031', 'community_group_001'
STAGE = {'stage_id': 'ro6_b_5', 'title': '混沌源阶理论',
         'reference_only': True, 'immediate_transition': None}
CASES = (
    (A, 0, 0, ('choice_ro6_end1_1',), ('marker_purchase_reference',)),
    (A, 0, 1, ('choice_ro6_end1_2',), ('unnamed_relic_reward_reference',)),
    (B, 0, 0, ('choice_ro6_end2_1', 'choice_ro6_end2_4'),
     ('node_becomes_fixed_battle', 'cannot_leave_after_conversion', 'not_normal_battle_node_effect')),
    (B, 0, 1, ('choice_ro6_end2_2',), ('temporary_leave_completes_node', 'documented_revisit')),
    (B, 2, 0, ('choice_ro6_end2_3',), ('existing_battle_decision_reference',)),
)
ACTUAL = ('actual_choice', 'actual_node_id', 'actual_marker', 'actual_transformation',
          'actual_revisit', 'actual_consumed', 'actual_reward', 'actual_quantity', 'actual_eligible')
FLAGS = ('inventory_updated', 'calculation_applied', 'run_state_updated')


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
    scene = case[0] + ':scene:' + str(case[1])
    return case[0], scene, scene + ':choice:' + str(case[2])


def bound_files():
    names = {CANONICAL, MANIFEST, DATA, 'rouge/app.py', 'rouge/node_catalog_view.py',
             'rouge/node_catalog.py', 'rouge/event_planning.py', 'rouge/player_node_information.py',
             'rouge/ui_state.py', 'rouge/branch_choice.py', 'rouge/view_catalog.py',
             'rouge/curiosity_node_rules.py', 'rouge/curiosity_node_rules_view.py',
             'rouge/battle_view.py', 'rouge/battle_preview.py', 'rouge/spawn_reference.py',
             'rouge/map_projection.py', 'rouge/fixed_landmark_mapping.py',
             'rouge/player_tile_information.py', 'rouge/data/battle-previews.json',
             'rouge/data/battle-map-projections.json', 'rouge/data/fixed-landmark-references.json',
             'scripts/build_curiosity_node_rules_304.py'}
    manifest = read(ROOT / MANIFEST)
    # Complete build authority is checked before/after this fixture, not on each
    # UI refresh. The actual model keeps the smaller runtime selected records.
    names.update(manifest['files'])
    names.update(p.relative_to(ROOT).as_posix() for p in (ROOT / PACKET).rglob('*') if p.is_file())
    names.update(p.relative_to(ROOT).as_posix() for p in (ROOT / 'tests').glob('test_curiosity*304.py'))
    stage = read(ROOT / 'rouge/data/battle-previews.json')['stages'][STAGE['stage_id']]
    names.add('rouge/data/' + stage['image']['file'])
    names.update(EXPECTED_SOURCE_PINS)
    result = {}
    for name in sorted(names):
        path = ROOT / name
        if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()):
            raise ValueError('Regular selected public source required: ' + name)
        result[name] = sha(path)
    return result


def _fresh305_parent_pin():
    freeze=read(ROOT/'verification/full-305/source-freeze-attempt2.json')
    if freeze.get('section')!=305 or freeze.get('root_declared')is not True:
        raise ValueError('Actual305 declared source input required for this parent compatibility pin.')
    expected=freeze['source_sha256']['rouge/node_catalog_view.py']
    if sha(ROOT/'rouge/node_catalog_view.py')!=expected:
        raise ValueError('Fresh305 parent source differs from its declared pin.')
    return expected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', required=True)
    parser.add_argument('--visible-ms', type=int, default=90000)
    args = parser.parse_args()
    EXPECTED_SOURCE_PINS['rouge/node_catalog_view.py'] = _fresh305_parent_pin()
    destination = Path(args.receipt).resolve()
    if destination.exists():
        raise FileExistsError('Preserve first actual receipt.')
    if args.visible_ms <= 0:
        raise ValueError('Positive visible interval required.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    before, after = {}, {}
    checks, screenshots, handles, readings, refreshes, negatives, battles = [], [], [], [], [], [], []
    executions = 0
    refresh_diagnostics = []
    failure, done, closed, qpa, qt_exit = None, False, False, None, None
    attempts = {key: 0 for key in ('game_enumeration', 'game_connect', 'game_capture', 'game_next_frame',
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
        require(MANIFEST in EXPECTED_SOURCE_PINS and DATA in EXPECTED_SOURCE_PINS
                and all(sha(ROOT / name) == value for name, value in EXPECTED_SOURCE_PINS.items()),
                'frozen_authority_data_UI_and_parent_exact_before_window')
        before = bound_files()
        from rouge import curiosity_node_rules as model, node_catalog as catalog
        from rouge.battle_preview import battle_data
        require(all(model.event_reference(event)['source_valid'] is True for event in (A, B)),
                'both_complete_fixed_event_documents_valid_before_Qt')
        fixed_stage = deepcopy(battle_data()['stages'][STAGE['stage_id']])
        from PySide6.QtCore import Qt, QPoint, QRect, QTimer
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QApplication
        from PySide6.QtTest import QTest
        import win32gui
        import win32process
        from rouge import app as app_module
        gui = QApplication([])
        qpa = gui.platformName()
        require(qpa == 'windows', 'actual_windows_QPA')

        class PublicWindow(app_module.MainWindow):
            def refresh_windows(self):
                self.windows.clear()

        with tempfile.TemporaryDirectory(prefix='rouge-304-fate-node-') as folder, ExitStack() as stack:
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
                window.setWindowTitle('第304节 · 命运所指资料（公开隔离验收）')
                window.resize(*SIZE)
                window.show()
                panel, tabs = window.node_catalog, window.centralWidget()
                initial_run = deepcopy(window.run.state)
                calculation_before = tuple((window.relic_list.item(i).data(Qt.ItemDataRole.UserRole),
                                            window.relic_list.item(i).checkState().value)
                                           for i in range(window.relic_list.count()))
                parent_saved = dialog_saved = battle_saved = main_battle_saved = None
                preserved_battle = None

                def isolated():
                    require(not window.auto.isChecked() and not window.timer.isActive(),
                            'automatic_sampling_and_timer_disabled')
                    require(window.capture.target is None and window.desktop.process is None,
                            'capture_and_desktop_backend_inactive')
                    require(all(value == 0 for value in attempts.values()), 'all_eight_original_external_entry_attempts_zero')

                def native(widget, kind):
                    hwnd = int(widget.winId())
                    thread, pid = win32process.GetWindowThreadProcessId(hwnd)
                    expected = {'parent': SIZE, 'dialog': DIALOG_SIZE, 'battle': BATTLE_SIZE}[kind]
                    require(win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd) and widget.isVisible(),
                            kind + '_actual_owned_visible_HWND')
                    require(pid == os.getpid() and not win32gui.IsIconic(hwnd), kind + '_fixture_PID_not_minimized')
                    require([widget.width(), widget.height()] == list(expected), kind + '_exact_client_size')
                    return {'kind': kind, 'hwnd': hwnd, 'process_id': pid, 'thread_id': thread,
                            'qpa': qpa, 'client_size': [widget.width(), widget.height()]}

                def choose(control, value):
                    index = control.findData(value)
                    require(index >= 0, 'complete_control_identity_present')
                    control.setCurrentIndex(index)
                    gui.processEvents()

                def select_event(event_id):
                    panel.show_directory()
                    panel.set_map_context(None)
                    choose(panel.kind, 'event')
                    choose(panel.floor, None)
                    choose(panel.node_type, None)
                    panel.search.setText(catalog._event(event_id)['title'])
                    tabs.setCurrentWidget(panel)
                    index = next(i for i, entry in enumerate(panel.entries)
                                 if entry['kind'] == 'event' and entry['record']['id'] == event_id)
                    item = panel.list.flat[index]
                    item.parent().setExpanded(True)
                    panel.list.scrollToItem(item)
                    gui.processEvents()
                    rect = panel.list.visualItemRect(item)
                    require(not rect.isEmpty() and panel.list.viewport().rect().contains(rect.center()),
                            'exact_directory_event_item_visible')
                    QTest.mouseClick(panel.list.viewport(), Qt.MouseButton.LeftButton, pos=rect.center())
                    gui.processEvents()
                    require(panel.list.selected_key() == panel.entries[index]['key'],
                            'actual_QTest_selected_full_event_not_same_title')

                def click(button, owner, label):
                    gui.processEvents()
                    rect = QRect(button.mapTo(owner, QPoint(0, 0)), button.size())
                    require(button.isVisible() and button.isEnabled() and not button.visibleRegion().isEmpty()
                            and owner.rect().contains(rect), label + '_visible_enabled_inside_client')
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
                            'stage': deepcopy(panel.event_stage.currentData()), 'kind': panel.kind.currentData(),
                            'floor': panel.floor.currentData(), 'node_type': panel.node_type.currentData(),
                            'search': panel.search.text(), 'search_cursor': panel.search.cursorPosition(),
                            'search_selection': panel.search.selectedText(),
                            'player': reader(panel.player_detail), 'source': reader(panel.detail)}

                def dialog_state():
                    return {'event': dialog.event_id, 'scope': deepcopy(dialog.scope_key),
                            'choice': dialog.choice.currentData(), 'tab': dialog.reading_tabs.currentIndex(),
                            'reading_key': deepcopy(dialog._reading_key), 'source_scope': deepcopy(dialog._source_scope),
                            'player': reader(dialog.player_text), 'source': reader(dialog.source_text)}

                def battle_state(battle=None):
                    battle = dialog.battle_preview if battle is None else battle
                    if battle is None:
                        return None
                    item = battle.spawn_list.currentItem()
                    return {'stage': battle.current_stage, 'context': deepcopy(battle.context),
                            'wave': battle.wave_combo.currentData(), 'enemy_branch': battle.enemy_choices.branch.currentData(),
                            'enemy': deepcopy(battle.enemy_combo.currentData()), 'branches': battle.include_branches.isChecked(),
                            'technical': battle.technical.isChecked(), 'reward': deepcopy(battle.reward_combo.currentData()),
                            'row': None if item is None else item.data(Qt.ItemDataRole.UserRole)['id'],
                            'occurrence': battle.occurrence.value(), 'list_scroll': battle.spawn_list.verticalScrollBar().value(),
                            'tile': deepcopy(battle._tile_cell), 'grid_cell': deepcopy(battle.grid.reference_cell),
                            'image_cell': deepcopy(battle.original.reference_cell), 'image_selected': deepcopy(battle.original.selected),
                            'spawn_reader': reader(battle.spawn_detail), 'enemy_reader': reader(battle.enemy_detail)}

                def prime(widget, scroll=False):
                    gui.processEvents()
                    require(widget.document().characterCount() > 30, 'existing_reader_has_selectable_real_text')
                    cursor = widget.textCursor()
                    cursor.setPosition(5)
                    cursor.setPosition(25, QTextCursor.MoveMode.KeepAnchor)
                    widget.setTextCursor(cursor)
                    if scroll:
                        bar = widget.verticalScrollBar()
                        require(bar.maximum() > 0, 'existing_reader_has_actual_scroll_range')
                        bar.setValue(max(1, bar.maximum() // 2))
                        require(bar.value() > 0, 'existing_reader_actual_nonzero_scroll')
                    require(bool(widget.textCursor().selectedText()), 'existing_reader_actual_nonempty_selection')

                def unknown(value):
                    return (all(key in value and value[key] is None for key in ACTUAL)
                            and all(value.get(key) is False for key in FLAGS))

                def select_case(case):
                    event_id, scene_key, choice_key = identity(case)
                    expected = next(row for row in dialog.packet['choices'] if row['choice_key'] == choice_key)
                    parent_before = parent_state()
                    choose(dialog.choice, choice_key)
                    details = model.choice_reference(event_id, scene_key, choice_key)
                    require(details['source_valid'] is True and details['status'] == 'documented_reference'
                            and details['reference'] == expected, 'fresh_complete_selected_tuple_matches_displayed_row')
                    require(expected['reference_id'] == choice_key and expected['original_choice_ids'] == list(case[3])
                            and [rule['rule_id'] for rule in expected['documented_rules']] == list(case[4]),
                            'five_choices_keep_distinct_originals_and_only_their_documented_rules')
                    require(unknown(details) and unknown(expected) and unknown(dialog.packet),
                            'all_nine_actual_outcomes_unknown_and_all_three_update_flags_false')
                    require(parent_state() == parent_before and dialog.battle_window is None,
                            'manual_reading_does_not_change_parent_or_automatically_open_battle')
                    related = STAGE if case in (CASES[2], CASES[4]) else None
                    require(expected['related_stage_reference'] == related
                            and details['related_stage_reference'] == related
                            and dialog.open_stage_button.isEnabled() is bool(related),
                            'only_conversion_and_final_decision_have_manual_reference_only_fixed_stage')
                    dialog.reading_tabs.setCurrentWidget(dialog.player_text)
                    gui.processEvents()
                    text = dialog.player_text.toPlainText()
                    require(all(plain(rule['text']) in text and plain(rule['title']) in text
                                for rule in expected['documented_rules'])
                            and plain(expected['choice_title']) in text and plain(expected['choice_description']) in text,
                            'player_body_keeps_complete_selected_rules_and_original_choice_text')
                    require('第五层' in text and '本局尚未确认' in text
                            and not any(term in text for term in ('community_group_', 'choice_ro6_', 'rogue_6_', 'FEATURE', '本节新增')),
                            'player_body_explains_scope_and_unknowns_without_raw_ID_or_progress_terms')
                    require(json.loads(dialog.source_text.toPlainText())['selected_choice'] == details,
                            'technical_reader_keeps_complete_original_choice_and_source')
                    if case == CASES[2]:
                        originals = expected['original_choices']
                        require(originals['choice_ro6_end2_1']['displayData']['itemId'] == 'rogue_6_end_2_change'
                                and originals['choice_ro6_end2_4']['displayData']['itemId'] is None
                                and expected['original_choice_candidate_selection_unknown'] is True,
                                'same_title_protection_preserves_two_distinct_primary_candidates_not_one_live_choice')
                    if case == CASES[3]:
                        require(not any(rule['rule_id'] == 'cannot_leave_after_conversion' for rule in expected['documented_rules']),
                                'temporary_leave_is_not_the_conversion_cannot_leave_result')
                    return details

                def screenshot(name, kind='dialog', anchor=None):
                    isolated()
                    widget = {'parent': window, 'dialog': dialog, 'battle': None if dialog is None else dialog.battle_window}[kind]
                    if kind == 'dialog':
                        dialog.reading_tabs.setCurrentWidget(dialog.player_text)
                        gui.processEvents()
                        if anchor:
                            cursor = dialog.player_text.document().find(anchor)
                            require(not cursor.isNull(), 'PNG_rule_anchor_exists_in_actual_player_document')
                            dialog.player_text.setTextCursor(cursor)
                            dialog.player_text.ensureCursorVisible()
                            gui.processEvents()
                            require(dialog.player_text.viewport().rect().contains(dialog.player_text.cursorRect().center()),
                                    'PNG_rule_anchor_visible_in_player_viewport')
                    observation = native(widget, kind)
                    path = destination.with_name(destination.stem + '-' + name + '.png')
                    if path.exists():
                        raise FileExistsError('Preserve first actual PNG.')
                    pixmap = widget.grab()
                    require(not pixmap.isNull() and pixmap.save(str(path), 'PNG'), 'actual_owned_native_PNG_saved')
                    screenshots.append({'name': name, 'path': str(path), 'sha256': sha(path),
                                        'native_window': observation, 'direct_player_text': kind == 'dialog',
                                        'related_fixed_map': kind == 'battle', 'parent_entry': kind == 'parent',
                                        'player_rule_anchor': anchor})

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
                    main_battle = window.battle_preview
                    main_battle.set_stage(STAGE['stage_id'])
                    tabs.setCurrentWidget(main_battle)
                    gui.processEvents()
                    source_row = next(row for row in main_battle.rows if row['route']['start'] is not None)
                    QTest.mouseClick(main_battle.grid, Qt.MouseButton.LeftButton,
                                     pos=main_battle.grid.cell_center(source_row['route']['start']).toPoint())
                    gui.processEvents()
                    require(main_battle.grid.selected is not None, 'main_fixed_map_has_real_manual_selection_before_new_reader')
                    main_battle_saved = battle_state(main_battle)
                    select_event(A)
                    choose(panel.event_scene_filter, identity(CASES[0])[1])
                    choose(panel.event_choice_filter, identity(CASES[0])[2])
                    panel.reading_tabs.setCurrentWidget(panel.detail)
                    prime(panel.detail, True)
                    panel.search.setSelection(0, 2)
                    parent_saved = parent_state()
                    require(panel.curiosity_node_rules_window is None and panel.curiosity_node_rules_button.isVisible()
                            and panel.curiosity_node_rules_button.isEnabled(), 'real_MainWindow_entry_is_manual_not_precreated')
                    handles.append(native(window, 'parent'))
                    screenshot('parent-manual-entry', 'parent')
                    click(panel.curiosity_node_rules_button, window, 'MainWindow_fate_document_entry_QTest')
                    later(opened)

                def opened():
                    nonlocal dialog, dialog_saved
                    dialog = panel.curiosity_node_rules_window
                    require(dialog is not None and dialog.parent() is panel, 'actual_parent_button_created_owned_reader')
                    dialog.resize(*DIALOG_SIZE)
                    gui.processEvents()
                    handles.append(native(dialog, 'dialog'))
                    require(dialog.event_id == A and dialog.choice.count() == 2 and dialog.choice.currentIndex() == -1
                            and dialog.battle_window is None and not dialog.open_stage_button.isEnabled(),
                            '030_defaults_to_two_unselected_choices_without_battle')
                    require(parent_state() == parent_saved, 'opening_reader_keeps_parent_filters_scroll_and_selection')
                    dialog.reading_tabs.setCurrentWidget(dialog.source_text)
                    prime(dialog.source_text, True)
                    dialog_saved = dialog_state()
                    later(unselected_refresh)

                def unselected_refresh():
                    panel.refresh()
                    gui.processEvents()
                    require(dialog_state() == dialog_saved and parent_state() == parent_saved and dialog.battle_window is None,
                            'unselected_parent_refresh_keeps_real_source_scroll_and_selection')
                    refreshes.append({'path': 'unselected_parent', 'selected': None,
                                      'nonzero_scroll': dialog.source_text.verticalScrollBar().value(),
                                      'selection': dialog.source_text.textCursor().selectedText(), 'parent_unchanged': True})
                    later(read_next)

                def read_next():
                    nonlocal parent_saved
                    case = CASES[len(readings)]
                    if dialog.event_id != case[0]:
                        select_event(case[0])
                        gui.processEvents()
                        require(dialog.event_id == B and dialog.choice.count() == 3 and dialog.choice.currentIndex() == -1
                                and dialog.battle_window is None and not dialog.open_stage_button.isEnabled(),
                                '031_event_change_clears_previous_choice_and_defaults_to_three_unselected')
                        choose(panel.event_scene_filter, identity(CASES[3])[1])
                        choose(panel.event_choice_filter, identity(CASES[3])[2])
                        panel.reading_tabs.setCurrentWidget(panel.detail)
                        prime(panel.detail, True)
                        panel.search.setSelection(0, 2)
                        parent_saved = parent_state()
                    details = select_case(case)
                    row = details['reference']
                    readings.append({'event_id': row['event_id'], 'scene_key': row['scene_key'], 'choice_key': row['choice_key'],
                                     'reference_id': row['reference_id'], 'original_choice_ids': row['original_choice_ids'],
                                     'documented_rule_ids': [r['rule_id'] for r in row['documented_rules']],
                                     'related_stage_reference': row['related_stage_reference'],
                                     'all_actual_fields_unknown': unknown(details), 'run_state_updated': False})
                    if case == CASES[0]:
                        screenshot('player-fifty-ingots-marker', anchor=plain(row['documented_rules'][0]['text']))
                    elif case == CASES[2]:
                        screenshot('player-conversion-warning', anchor=plain(row['documented_rules'][1]['text']))
                        later(open_conversion_battle)
                        return
                    elif case == CASES[3]:
                        screenshot('player-temporary-leave', anchor=plain(row['documented_rules'][0]['text']))
                    later(read_next if len(readings) < len(CASES) else open_final_battle)

                def open_conversion_battle():
                    previous = parent_state()
                    click(dialog.open_stage_button, dialog, 'conversion_reference_manual_fixed_battle_QTest')
                    require(dialog.battle_preview is not None and dialog.battle_preview.current_stage == STAGE['stage_id']
                            and parent_state() == previous, 'protection_opens_only_separate_fixed_battle_and_keeps_parent')
                    dialog.battle_window.resize(*BATTLE_SIZE)
                    gui.processEvents()
                    handles.append(native(dialog.battle_window, 'battle'))
                    battles.append({'choice_key': identity(CASES[2])[2], 'stage_id': STAGE['stage_id'],
                                    'reference_only': True, 'immediate_transition': None})
                    previous_battle, hwnd = dialog.battle_preview, int(dialog.battle_window.winId())
                    # The next manual choice is temporary leave. It must remove
                    # the converted-node preview rather than inherit its result.
                    choose(dialog.choice, identity(CASES[3])[2])
                    require(dialog.battle_window is None and dialog.battle_preview is None
                            and previous_battle.current_stage is None and not win32gui.IsWindowVisible(hwnd),
                            'changing_from_conversion_to_leave_clears_old_independent_battle')
                    later(read_next)

                def open_final_battle():
                    nonlocal preserved_battle
                    require(dialog.battle_window is None, 'final_decision_read_did_not_automatically_open_battle')
                    previous = parent_state()
                    click(dialog.open_stage_button, dialog, 'final_decision_manual_fixed_battle_QTest')
                    require(dialog.battle_preview is not None and parent_state() == previous,
                            'decision_manual_fixed_battle_keeps_parent_reading')
                    preserved_battle = dialog.battle_preview
                    dialog.battle_window.resize(*BATTLE_SIZE)
                    gui.processEvents()
                    handles.append(native(dialog.battle_window, 'battle'))
                    later(configure_fixed_battle)

                def configure_fixed_battle():
                    nonlocal parent_saved, dialog_saved, battle_saved
                    battle = dialog.battle_preview
                    require(battle.current_stage == STAGE['stage_id'] and battle.context == {}
                            and battle.grid.stage == fixed_stage and battle.original.stage == fixed_stage,
                            'separate_battle_uses_exact_unmodified_fixed_stage_without_node_effect_context')
                    row = next(row for row in battle.rows if row['route']['start'] is not None)
                    QTest.mouseClick(battle.grid, Qt.MouseButton.LeftButton,
                                     pos=battle.grid.cell_center(row['route']['start']).toPoint())
                    gui.processEvents()
                    require(battle.grid.selected is not None and not battle.original.pixmap.isNull()
                            and STAGE['title'] in battle.summary.text(), 'actual_fixed_map_and_readonly_source_selection_visible')
                    battle.technical.setChecked(False)
                    gui.processEvents()
                    screenshot('related-fixed-battle-player', 'battle')
                    prime(battle.enemy_detail)
                    prime(battle.spawn_detail)
                    dialog.reading_tabs.setCurrentWidget(dialog.source_text)
                    prime(dialog.source_text, True)
                    parent_saved, dialog_saved, battle_saved = parent_state(), dialog_state(), battle_state()
                    battles.append({'choice_key': identity(CASES[4])[2], 'stage_id': STAGE['stage_id'],
                                    'reference_only': True, 'immediate_transition': None,
                                    'source_row_id': battle_saved['row'], 'source_cell': row['route']['start']})
                    later(selected_refresh)

                def differences(expected, actual, path=''):
                    if type(expected) is dict and type(actual) is dict:
                        rows = []
                        for key in sorted(set(expected) | set(actual)):
                            child = path + '.' + str(key) if path else str(key)
                            if key not in expected or key not in actual:
                                rows.append({'path': child, 'expected': expected.get(key), 'actual': actual.get(key)})
                            else:
                                rows += differences(expected[key], actual[key], child)
                        return rows
                    if expected != actual:
                        return [{'path': path, 'expected': expected, 'actual': actual}]
                    return []

                def selected_refresh():
                    selected_count = sum(row['selected'] is not None for row in refreshes)
                    callbacks = [dialog.refresh_reference, panel.refresh,
                                 lambda: dialog.set_reference(B, scope_key=deepcopy(panel.list.selected_key()))]
                    expected = {'dialog': dialog_saved, 'parent': parent_saved, 'battle': battle_saved,
                                'same_battle_object': True}
                    before_callback = {'dialog': dialog_state(), 'parent': parent_state(), 'battle': battle_state(),
                                       'same_battle_object': dialog.battle_preview is preserved_battle}
                    before_parent_text = {'source': panel.detail.toPlainText(), 'player': panel.player_detail.toPlainText()}
                    callbacks[selected_count]()
                    gui.processEvents()
                    after_callback = {'dialog': dialog_state(), 'parent': parent_state(), 'battle': battle_state(),
                                      'same_battle_object': dialog.battle_preview is preserved_battle}
                    after_parent_text = {'source': panel.detail.toPlainText(), 'player': panel.player_detail.toPlainText()}
                    refresh_diagnostics.append({'path': ['selected_dialog', 'selected_parent', 'selected_same_reference'][selected_count],
                                                'expected': deepcopy(expected), 'before_callback': before_callback,
                                                'after_callback': after_callback,
                                                'before_vs_expected': differences(expected, before_callback),
                                                'after_vs_expected': differences(expected, after_callback),
                                                'before_vs_after': differences(before_callback, after_callback),
                                                'parent_documents_before': before_parent_text,
                                                'parent_documents_after': after_parent_text})
                    require(dialog_state() == dialog_saved and parent_state() == parent_saved
                            and dialog.battle_preview is preserved_battle and battle_state() == battle_saved,
                            'same_scope_refresh_keeps_choice_readers_and_same_independent_battle_state')
                    refreshes.append({'path': ['selected_dialog', 'selected_parent', 'selected_same_reference'][selected_count],
                                      'selected': dialog.choice.currentData(),
                                      'nonzero_scroll': dialog.source_text.verticalScrollBar().value(),
                                      'selection': dialog.source_text.textCursor().selectedText(),
                                      'parent_unchanged': True, 'battle_unchanged': True})
                    later(selected_refresh if selected_count < 2 else source_failure)

                def source_failure():
                    manifest = read(ROOT / MANIFEST)
                    clone = temporary / 'public-source-negative'
                    for name in set(manifest['runtime_files']) | {MANIFEST}:
                        source = ROOT / name
                        require(source.is_file() and not source.is_symlink() and source.resolve().is_relative_to(ROOT.resolve()),
                                'source_negative_copies_only_explicit_regular_public_runtime_members')
                        target = clone / name
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(source.read_bytes())
                    target = clone / MANIFEST
                    raw = target.read_bytes()
                    previous_battle, hwnd = dialog.battle_preview, int(dialog.battle_window.winId())
                    with patch.object(model, 'ROOT', clone):
                        require(model.choice_reference(*identity(CASES[4]))['source_valid'] is True,
                                'complete_selected_runtime_clone_warmed_valid_before_real_byte_damage')
                        try:
                            target.write_bytes(raw + b' ')
                            dialog.refresh_reference()
                            panel.refresh()
                            gui.processEvents()
                            failed = model.choice_reference(*identity(CASES[4]))
                            packet = model.event_reference(B)
                            require(failed['source_valid'] is False and failed['reference'] is None
                                    and packet['choices'] == [] and packet['node_context_reference'] is None,
                                    'fresh_damaged_manifest_returns_empty_unknown_not_old_node_rules')
                            require(dialog.packet is None and dialog.choice.count() == 0 and dialog.choice.currentIndex() == -1
                                    and not dialog.open_stage_button.isEnabled() and not panel.curiosity_node_rules_button.isEnabled(),
                                    'source_failure_clears_selection_and_disables_both_manual_entries')
                            require(dialog.battle_preview is None and dialog.battle_window is None
                                    and previous_battle.current_stage is None and not win32gui.IsWindowVisible(hwnd),
                                    'source_failure_clears_old_independent_fixed_battle')
                            require(all('已清除' in widget.toPlainText() for widget in (dialog.player_text, dialog.source_text)),
                                    'source_failure_clears_both_player_and_technical_readers')
                        finally:
                            target.write_bytes(raw)
                        require(sha(target) == EXPECTED_SOURCE_PINS[MANIFEST], 'temporary_manifest_restored_to_exact_original_bytes')
                        dialog.refresh_reference()
                        panel.refresh()
                        gui.processEvents()
                        require(dialog.packet is not None and dialog.choice.count() == 3 and dialog.choice.currentIndex() == -1
                                and dialog.battle_window is None and not dialog.open_stage_button.isEnabled()
                                and panel.curiosity_node_rules_button.isEnabled(),
                                'recovery_restores_documents_without_reselecting_choice_or_reopening_battle')
                    negatives.append({'kind': 'complete_warm_runtime_clone_manifest_bytes', 'member': MANIFEST,
                                      'restored_sha256': sha(target), 'restored_unselected': True,
                                      'old_battle_cleared': True, 'actual_transformation': None})
                    later(reopen_then_change_scope)

                def reopen_then_change_scope():
                    select_case(CASES[2])
                    click(dialog.open_stage_button, dialog, 'source_recovery_requires_new_manual_battle_click')
                    require(dialog.battle_preview is not None and dialog.battle_preview.current_stage == STAGE['stage_id'],
                            'only_explicit_manual_reselection_reopens_restored_battle')
                    previous, hwnd = dialog.battle_preview, int(dialog.battle_window.winId())
                    select_event(OTHER)
                    gui.processEvents()
                    require(not panel.curiosity_node_rules_button.isVisible() and dialog.packet is None
                            and dialog.choice.count() == 0 and dialog.choice.currentIndex() == -1
                            and dialog.battle_window is None and dialog.battle_preview is None
                            and previous.current_stage is None and not win32gui.IsWindowVisible(hwnd),
                            'non_target_scope_clears_old_rules_and_battle_without_new_selection')
                    later(finish)

                def finish():
                    nonlocal done
                    require(len(readings) == 5 and {(r['event_id'], r['scene_key'], r['choice_key']) for r in readings}
                            == {identity(case) for case in CASES}, 'all_five_exact_choices_actually_read')
                    require(len(battles) == 2 and {r['choice_key'] for r in battles} == {identity(CASES[i])[2] for i in (2, 4)},
                            'both_documented_related_choices_manually_opened_without_adding_immediate_battle_links')
                    require(len(screenshots) == 5 and sum(r['direct_player_text'] for r in screenshots) == 3
                            and sum(r['related_fixed_map'] for r in screenshots) == 1
                            and sum(r['parent_entry'] for r in screenshots) == 1,
                            'five_actual_PNGs_cover_parent_fifty_ingots_conversion_leave_and_fixed_battle')
                    require(len(refreshes) == 4 and all(r['nonzero_scroll'] > 0 and r['selection']
                                                       and r['parent_unchanged'] for r in refreshes),
                            'unselected_and_three_selected_refreshes_kept_actual_nonzero_scroll_and_selection')
                    calculation_after = tuple((window.relic_list.item(i).data(Qt.ItemDataRole.UserRole),
                                               window.relic_list.item(i).checkState().value)
                                              for i in range(window.relic_list.count()))
                    require(window.run.state == initial_run and calculation_after == calculation_before,
                            'all_document_reading_preserves_temporary_run_and_calculation_relics')
                    require(battle_state(window.battle_preview) == main_battle_saved,
                            'existing_main_battle_selection_and_readers_unchanged_by_independent_dialog')
                    require(bound_files() == before, 'selected_public_sources_unchanged_before_completion')
                    handles.append(native(window, 'parent'))
                    done = True

                def deadline():
                    nonlocal failure
                    if not done and failure is None:
                        failure = {'type': 'TimeoutError', 'message': 'Actual fate-node document checks incomplete.'}
                    close_owned()

                later(begin, 500)
                QTimer.singleShot(max(30000, args.visible_ms), deadline)
                qt_exit = gui.exec()
                closed = (not window.isVisible() and not (dialog and dialog.isVisible())
                          and not (dialog and dialog.battle_window and dialog.battle_window.isVisible()))
                if qt_exit != 0 or not closed or not done:
                    if failure is None:
                        failure = {'type': 'RuntimeError', 'message': 'Checks, Qt or owned window closure incomplete.'}
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
    report = {'section': 304, 'kind': 'isolated_native_windows_curiosity_node_rules_reader',
              'passed': done and failure is None, 'failure': failure, 'started_at': started,
              'finished_at': datetime.now(timezone.utc).isoformat(), 'process_id': os.getpid(), 'qpa': qpa,
              'qt_exit_code': qt_exit, 'verification_window_closed': closed, 'checks': checks,
              'unique_checks': len(checks), 'successful_assertion_executions_including_repeated_guards': executions,
              'requested_parent_client_size': list(SIZE), 'requested_dialog_client_size': list(DIALOG_SIZE),
              'requested_related_battle_client_size': list(BATTLE_SIZE), 'native_observations': handles,
              'screenshots': screenshots, 'screenshot_count': len(screenshots), 'actual_choice_readings': readings,
              'related_fixed_battle_readings': battles, 'same_scope_refresh_observations': refreshes,
              'source_negative_fixtures': negatives, 'same_scope_refresh_diagnostics': refresh_diagnostics,
              'source_sha256_before': before, 'source_sha256_after': after,
              'source_guard_is_selected_not_all_transitive_dependencies': True, 'temporary_state_root': True,
              'state_paths_replaced_before_constructor': ['ROOT', 'SETTINGS', 'OPERATOR_STATE', 'RUN_STATE'],
              'private_state_read_copied_or_restored': False, 'external_operation_attempts': attempts,
              'external_entrypoints_blocked_before_original_call': True, 'game_operated': False, 'game_captures': 0,
              'chat_sent': False, 'chat_attempted': bool(attempts['desktop_request'] or attempts['provider_chat']),
              'original_project_window_operated_or_restarted': False,
              'actual_process_termination_verified_by_this_script': False,
              'owned_supervisor_exit_and_cleanup_required_separately': True,
              'launch_Popen_PID_must_be_recorded_separately_from_actual_fixture_PID': True,
              'actual_node_marker_transformation_revisit_or_inventory_verified': False,
              'scope': 'Five exact choice-specific documents, parent-preserving manual reading and two explicit fixed battle references; no actual node, marker, conversion, revisit, inventory, reward or calculation.'}
    with destination.open('x', encoding='utf8') as stream:
        stream.write(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
