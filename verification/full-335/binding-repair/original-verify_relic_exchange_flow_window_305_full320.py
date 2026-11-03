"""Isolated native fixed-relic offering and complete documentary exchange reader.

No real inventory, payment, exchange, reward grant, game or chat is exercised.
The root must promote the frozen candidate and own its actual native process.
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

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'rouge/app.py').is_file())
sys.path.insert(0, str(ROOT))
CANONICAL = 'scripts/verify_relic_exchange_flow_window_305_full320.py'
PACKET = 'research/p3-relic-exchange-305'
MANIFEST = PACKET+'/source-manifest.json'
DATA = 'rouge/data/relic-exchange-flow.json'
# Set only from frozen author and root UI bytes, never guessed future results.
EXPECTED_SOURCE_PINS = {'research/p3-relic-exchange-305/README.md': '3398da245d25d9a23fdbb6abb3c88188f053583b14102b897d15fb38f06740c9', 'research/p3-relic-exchange-305/SOURCE_SCHEMA.md': '4d71b7488afaf8a04036d2b62ce0c305b6c2d6567deaf663ff9c5ef54f39118c', 'research/p3-relic-exchange-305/backend-template.py': '3f3648301725acf63d645c93841bf0d15b1c7a525b6a4ecfe96a83a73acfef7a', 'research/p3-relic-exchange-305/build-receipt.json': '283507d3f6ecd19c2fd09e2ea998230f5773d8161e4be4fa2f0722046035e7c2', 'research/p3-relic-exchange-305/http-source-attempt1.json': 'cf3b2ce2ecbbf577f20825d83a4c1f0af8859d9ba2cd5e77ef0bcf28e7863886', 'research/p3-relic-exchange-305/http-source-records.json': '37c57cfdc5ba48c73399a6f298c1c1e651c52669bd2378c46306741f0d54cc16', 'research/p3-relic-exchange-305/notrade-corner-433235.html': '7b0002fd98b7c507f129b30c8f3241f0b2dd9d9e07d7fa9b89adde9f49f738f5', 'research/p3-relic-exchange-305/relic-index-current.html': 'e459f6713eca12108998f6c858d88f45007748a578d1fbca7a0e05bc98c39bd8', 'research/p3-relic-exchange-305/selected-authority-records.json': '8f2cc8c1448be40fafeaf418c7918d8e86a11f62ef599fd6248c81e763b61f23', 'research/p3-relic-exchange-305/source-manifest.json': 'acd83e3d1d94b888bf5e9b0b8fb54771341b5bcc2c446e2906cbee57b90e661d', 'rouge/data/relic-exchange-flow.json': '30335cce9fd13f1a00e9fffde109ce813f48fa6537632a8913ed452ec1536929', 'rouge/node_catalog_view.py': '6d1817136ec250d4500e49a00936e5e487ca94f0c30d36dbd8d65ae57003e359', 'rouge/relic_exchange_flow.py': '9ac3681bcb347aca9a7ce2c6a728502f136acee89c5d541a78207b978cf90399', 'rouge/relic_exchange_flow_view.py': '091c879b00643c8094ab0643b61fc89b2d895a7b27b200687163e5370a326340', 'scripts/build_relic_exchange_flow_305.py': '276c0e9887d2313b95095d47a9fedc678dd6c406592ed1cae9e44fe2208e139e', 'tests/test_relic_exchange_flow_305.py': 'e82f7a78678c4c09e2fc81032f10871982e5793f81eaa8dffcae83ba6fcb7099', 'tests/test_relic_exchange_flow_view_305.py': '3682e3c7006cf0c271c545c24430807562f7276588db1ca3702223d119b9b080'}
SIZE, DIALOG_SIZE = (1280, 900), (1080, 900)
EVENT, OTHER = 'community_group_025', 'community_group_001'
KETTLE, ALPHA = 'rogue_6_relic_legacy_1', 'rogue_6_relic_final_1'
STOP_KEYS = (EVENT+':scene:3:choice:1', EVENT+':scene:7:choice:1')
STOP_ORIGINALS = {'scene_ro6_sacrifice1_10', 'scene_ro6_sacrifice1_17',
                  'scene_ro6_sacrifice2_10', 'scene_ro6_sacrifice2_17'}
ACTUAL = ('actual_consumed', 'actual_reward_pool', 'actual_selectable', 'actual_eligible',
          'actual_offered_consumed', 'actual_reward', 'actual_quantity', 'actual_choice',
          'actual_scene', 'actual_transition', 'actual_inventory', 'quantity', 'reward_pool')
FLAGS = ('inventory_updated', 'calculation_applied', 'run_state_updated')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_bytes())


def text_sha(value):
    return hashlib.sha256(value.encode('utf8')).hexdigest()


def json_sha(value):
    return text_sha(json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False))


def plain(value):
    value = unescape(value or '')
    value = re.sub(r'<br\s*/?>', '\n', value, flags=re.I)
    return re.sub(r'</?[A-Za-z][^<>]*>|<[@$][^<>]*>|</>', '', value).strip()


def bound_files():
    names = {CANONICAL, MANIFEST, DATA, 'rouge/app.py', 'rouge/node_catalog_view.py',
             'rouge/node_catalog.py', 'rouge/event_planning.py', 'rouge/player_node_information.py',
             'rouge/ui_state.py', 'rouge/branch_choice.py', 'rouge/relic_exchange_flow.py',
             'rouge/relic_exchange_flow_view.py', 'rouge/scrap_exchange_planning.py',
             'rouge/scrap_exchange_view.py', 'rouge/duel_reward_planning.py',
             'rouge/data/scrap-exchange-reference.json', 'rouge/data/duel-reward-reference.json',
             'scripts/build_relic_exchange_flow_305.py'}
    manifest = read(ROOT/MANIFEST)
    names.update(manifest['runtime_files'])
    names.add(manifest['complete_primary_build_pin']['file'])
    names.update(row['file'] for row in manifest['build_source_documents'])
    names.update(p.relative_to(ROOT).as_posix() for p in (ROOT/PACKET).rglob('*') if p.is_file())
    names.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'tests').glob('test_relic_exchange*305.py'))
    names.update(EXPECTED_SOURCE_PINS)
    result = {}
    for name in sorted(names):
        path = ROOT/name
        if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()):
            raise ValueError('Regular selected public source required: '+name)
        result[name] = sha(path)
    return result


def differences(expected, actual, path=''):
    if type(expected) is dict and type(actual) is dict:
        rows = []
        for key in sorted(set(expected) | set(actual)):
            child = path+'.'+str(key) if path else str(key)
            if key not in expected or key not in actual:
                rows.append({'path': child, 'expected': expected.get(key), 'actual': actual.get(key)})
            else:
                rows += differences(expected[key], actual[key], child)
        return rows
    return [] if expected == actual else [{'path': path, 'expected': expected, 'actual': actual}]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', required=True)
    parser.add_argument('--visible-ms', type=int, default=90000)
    args = parser.parse_args()
    freeze=read(ROOT/'verification/full-320/source-freeze-attempt2.json')
    if freeze.get('section')!=320 or freeze.get('root_declared')is not True:
        raise ValueError('Current320 frozen parent source required.')
    parent_pin=freeze['source_sha256']['rouge/node_catalog_view.py']
    if sha(ROOT/'rouge/node_catalog_view.py')!=parent_pin:
        raise ValueError('Current320 declared parent differs from actual bytes.')
    # Only the evolved parent UI pin changes; all original data, scope and assertions remain.
    EXPECTED_SOURCE_PINS['rouge/node_catalog_view.py']=parent_pin
    destination = Path(args.receipt).resolve()
    if destination.exists():
        raise FileExistsError('Preserve first actual receipt.')
    if args.visible_ms <= 0:
        raise ValueError('Positive visible interval required.')
    destination.parent.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()
    before, after = {}, {}
    checks, images, handles, flow_readings, catalogue_reads, offer_reads = [], [], [], [], [], []
    refreshes, refresh_diagnostics, negatives, legacy_reads = [], [], [], []
    executions = 0
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
            raise AssertionError('Forbidden original external entry: '+name)
        return blocked

    try:
        if sys.platform != 'win32':
            raise RuntimeError('Actual native Windows required.')
        if Path(__file__).resolve() != (ROOT/CANONICAL).resolve():
            raise RuntimeError('A cache script is not acceptance.')
        require(MANIFEST in EXPECTED_SOURCE_PINS and DATA in EXPECTED_SOURCE_PINS
                and all(sha(ROOT/name) == value for name, value in EXPECTED_SOURCE_PINS.items()),
                'frozen_relic_flow_authority_data_UI_and_parent_exact_before_window')
        before = bound_files()
        from rouge import relic_exchange_flow as model, node_catalog as catalog
        from rouge import scrap_exchange_planning as old_scrap
        packet = model.event_reference(EVENT)
        require(packet['source_valid'] is True and len(packet['scenes']) == 11 and len(packet['choices']) == 19
                and len(packet['catalogue']) == 272, 'complete_fixed_event_11_scenes_19_rows_and_272_relics_before_Qt')
        fixed_rows = deepcopy(packet['choices'])
        fixed_items = deepcopy(packet['catalogue'])
        scrap_context = {'floor': 3, 'node_type': '失与得', 'entry_mode': 'natural'}
        scrap_arguments = [dict(vocal_cords_unlocked=True, owned_quantity=1),
                           dict(exchange_index=2, vocal_cords_unlocked=True, palm_unlocked=True,
                                first_exchange_item_type='SCRAP', owned_quantity=1)]
        old_scrap_before = [deepcopy(old_scrap.exchange_candidates('rogue_6_scrap_M_01', scrap_context, **args))
                            for args in scrap_arguments]
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

        with tempfile.TemporaryDirectory(prefix='rouge-305-relic-exchange-') as folder, ExitStack() as stack:
            temporary = Path(folder)
            for key, value in {'ROOT': temporary, 'SETTINGS': temporary/'settings.json',
                               'OPERATOR_STATE': temporary/'operators.json', 'RUN_STATE': temporary/'run.json'}.items():
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
                window.setWindowTitle('第305节 · 回滚文明资料（公开隔离验收）')
                window.resize(*SIZE)
                window.show()
                panel, tabs = window.node_catalog, window.centralWidget()
                initial_run = deepcopy(window.run.state)
                calculation_before = tuple((window.relic_list.item(i).data(Qt.ItemDataRole.UserRole),
                                            window.relic_list.item(i).checkState().value)
                                           for i in range(window.relic_list.count()))
                parent_saved = dialog_saved = None

                def isolated():
                    require(not window.auto.isChecked() and not window.timer.isActive(),
                            'automatic_sampling_and_timer_disabled')
                    require(window.capture.target is None and window.desktop.process is None,
                            'capture_and_desktop_backend_inactive')
                    require(all(value == 0 for value in attempts.values()), 'all_eight_original_external_entry_attempts_zero')

                def native(widget, kind):
                    hwnd = int(widget.winId())
                    thread, pid = win32process.GetWindowThreadProcessId(hwnd)
                    require(win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd) and widget.isVisible(),
                            kind+'_actual_owned_visible_HWND')
                    require(pid == os.getpid() and not win32gui.IsIconic(hwnd), kind+'_fixture_PID_not_minimized')
                    expected = SIZE if kind == 'parent' else DIALOG_SIZE
                    require([widget.width(), widget.height()] == list(expected), kind+'_exact_client_size')
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
                            'actual_QTest_selected_complete_event_identity')

                def click(button, label):
                    gui.processEvents()
                    rect = QRect(button.mapTo(window, QPoint(0, 0)), button.size())
                    require(button.isVisible() and button.isEnabled() and not button.visibleRegion().isEmpty()
                            and window.rect().contains(rect), label+'_visible_enabled_inside_actual_client')
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
                    return {'event': dialog.event_id, 'scope': deepcopy(dialog.scope_key), 'tab': dialog.tabs.currentIndex(),
                            'flow': dialog.flow.currentData(), 'relic': dialog.relic.currentData(),
                            'filter': dialog.membership.currentData(), 'search': dialog.search.text(),
                            'search_cursor': dialog.search.cursorPosition(), 'search_selection': dialog.search.selectedText(),
                            'exchange_index': dialog.exchange_index.currentData(), 'owned': dialog.owned.currentData(),
                            'palm': dialog.palm.currentData(), 'first_type': dialog.first_type.currentData(),
                            'source_scope': deepcopy(dialog._source_scope), 'flow_key': deepcopy(dialog._flow_key),
                            'offer_key': deepcopy(dialog._offer_key), 'count_text': dialog.catalogue_count.text(),
                            'flow_reader': reader(dialog.flow_reader), 'offer_reader': reader(dialog.offer_reader),
                            'source_reader': reader(dialog.source_reader)}

                def prime(widget, scroll=False):
                    gui.processEvents()
                    require(widget.document().characterCount() > 30, 'actual_reader_contains_selectable_existing_text')
                    cursor = widget.textCursor()
                    cursor.setPosition(5)
                    cursor.setPosition(25, QTextCursor.MoveMode.KeepAnchor)
                    widget.setTextCursor(cursor)
                    if scroll:
                        bar = widget.verticalScrollBar()
                        require(bar.maximum() > 0, 'actual_reader_has_real_scroll_range')
                        bar.setValue(max(1, bar.maximum()//2))
                        require(bar.value() > 0, 'actual_reader_nonzero_scroll')
                    require(bool(widget.textCursor().selectedText()), 'actual_reader_nonempty_selection')

                def unknown(value):
                    return all(key in value and value[key] is None for key in ACTUAL) and all(value.get(key) is False for key in FLAGS)

                def screenshot(name, reader_widget=None, anchor=None, parent=False):
                    isolated()
                    widget = window if parent else dialog
                    if reader_widget is not None and anchor:
                        cursor = reader_widget.document().find(anchor)
                        require(not cursor.isNull(), 'PNG_exact_player_text_exists_in_document')
                        reader_widget.setTextCursor(cursor)
                        reader_widget.ensureCursorVisible()
                        gui.processEvents()
                        require(reader_widget.isVisible() and reader_widget.viewport().rect().contains(reader_widget.cursorRect().center()),
                                'PNG_exact_player_text_anchored_in_actual_visible_viewport')
                    observation = native(widget, 'parent' if parent else 'dialog')
                    path = destination.with_name(destination.stem+'-'+name+'.png')
                    if path.exists():
                        raise FileExistsError('Preserve first actual PNG.')
                    pixmap = widget.grab()
                    require(not pixmap.isNull() and pixmap.save(str(path), 'PNG'), 'actual_owned_native_PNG_saved')
                    images.append({'name': name, 'path': str(path), 'sha256': sha(path), 'native_window': observation,
                                   'parent_entry': parent, 'direct_player_text': not parent,
                                   'player_text_anchor': anchor})

                def current_offer(label, expected_state):
                    source = json.loads(dialog.source_reader.toPlainText())
                    result = source['selected_offering']
                    require(result is not None and result['source_valid'] is True
                            and result['item_id'] == dialog.relic.currentData()
                            and result['documented_condition_status'] == expected_state, 'actual_UI_offer_matches_exact_source_and_declarations')
                    expected = model.relic_offer_reference(dialog.relic.currentData(), exchange_index=dialog.exchange_index.currentData(),
                        owned=dialog.owned.currentData(), palm_unlocked=dialog.palm.currentData() if dialog.exchange_index.currentData()==2 else None,
                        first_exchange_item_type=dialog.first_type.currentData() if dialog.exchange_index.currentData()==2 else None)
                    require(result == expected and unknown(result), 'all_thirteen_actual_values_unknown_and_three_update_flags_false')
                    require(result['documented_conditions_are_actual_selectability'] is False
                            and result['complete_reward_pool_known'] is False and result['reward_rarity_inferred'] is False
                            and result['offering_flag_used_for_reward_side'] is False,
                            'offering_flag_and_declarations_never_prove_reward_pool_rarity_or_actual_selectability')
                    require('不说明能否作为交换奖励得到' in dialog.offer_reader.toPlainText()
                            and '完整奖励池' in dialog.offer_reader.toPlainText(), 'player_reading_separates_offering_from_receiving')
                    require('旗标' not in dialog.offer_reader.toPlainText(),
                            'default_offer_player_text_uses_plain_language_without_flag_terms')
                    offer_reads.append({'label': label, 'item_id': result['item_id'], 'can_offer_reference': result['can_offer_reference'],
                                        'exchange_index': result['exchange_index'], 'owned_declared': result['owned_declared'],
                                        'palm_unlocked_declared': result['palm_unlocked_declared'],
                                        'first_exchange_item_type_declared': result['first_exchange_item_type_declared'],
                                        'documented_condition_status': result['documented_condition_status'],
                                        'actual_unknown': unknown(result), 'actual_reward': None})
                    return result

                def filtered_catalogue(flag):
                    dialog.search.clear()
                    choose(dialog.membership, flag)
                    expected = [row['item_id'] for row in fixed_items if flag is None or row['canSacrifice'] is flag]
                    actual = [dialog.relic.itemData(i) for i in range(dialog.relic.count())]
                    require(actual == expected and len(set(actual)) == len(actual), 'all_fixed_item_ids_and_true_false_filter_membership_exact')
                    require('272' in dialog.catalogue_count.text() and '251' in dialog.catalogue_count.text()
                            and '21' in dialog.catalogue_count.text(), 'actual_count_label_distinguishes_fixed_total_and_filter')
                    catalogue_reads.append({'flag': flag, 'count': len(actual), 'ordered_item_ids_sha256': json_sha(actual)})

                def close_owned():
                    if dialog is not None:
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
                    nonlocal parent_saved
                    select_event(EVENT)
                    choose(panel.event_scene_filter, EVENT+':scene:3')
                    choose(panel.event_choice_filter, STOP_KEYS[0])
                    panel.refresh()  # Complete deliberate filtering before recording the reading baseline.
                    panel.reading_tabs.setCurrentWidget(panel.detail)
                    prime(panel.detail, True)
                    panel.search.setSelection(0, 2)
                    parent_saved = parent_state()
                    require(panel.relic_exchange_flow_window is None and panel.relic_exchange_flow_button.isVisible()
                            and panel.relic_exchange_flow_button.isEnabled(), 'actual_MainWindow_manual_reader_entry_not_precreated')
                    handles.append(native(window, 'parent'))
                    screenshot('parent-manual-entry', parent=True)
                    click(panel.relic_exchange_flow_button, 'MainWindow_relic_exchange_entry_QTest')
                    later(opened)

                def opened():
                    nonlocal dialog, dialog_saved
                    dialog = panel.relic_exchange_flow_window
                    require(dialog is not None and dialog.parent() is panel, 'actual_parent_button_created_owned_exchange_reader')
                    dialog.resize(*DIALOG_SIZE)
                    gui.processEvents()
                    handles.append(native(dialog, 'dialog'))
                    require(dialog.flow.count() == 19 and dialog.flow.currentIndex() == -1
                            and dialog.relic.count() == 272 and dialog.relic.currentIndex() == -1,
                            'default_19_flow_rows_and_272_catalogue_items_both_unselected')
                    require(dialog.exchange_index.currentData()==1 and dialog.owned.currentData() is None
                            and dialog.palm.isHidden() and dialog.first_type.isHidden(), 'first_exchange_hides_second_only_declarations')
                    require(parent_state() == parent_saved, 'opening_new_reader_preserves_parent_filters_scroll_selection')
                    dialog.tabs.setCurrentWidget(dialog.source_reader)
                    prime(dialog.source_reader, dialog.source_reader.verticalScrollBar().maximum() > 0)
                    dialog_saved = dialog_state()
                    later(unselected_refresh)

                def unselected_refresh():
                    panel.refresh()
                    gui.processEvents()
                    require(dialog_state() == dialog_saved and parent_state() == parent_saved,
                            'unselected_same_scope_refresh_preserves_real_reading_without_autoselection')
                    refreshes.append({'path': 'unselected_parent', 'selected': None,
                                      'nonzero_scroll': dialog.source_reader.verticalScrollBar().value(),
                                      'selection': dialog.source_reader.textCursor().selectedText(), 'parent_unchanged': True})
                    later(read_flow)

                def read_flow():
                    index = len(flow_readings)
                    row = fixed_rows[index]
                    previous = parent_state()
                    choose(dialog.flow, row['reference_id'])
                    dialog.tabs.setCurrentIndex(0)
                    gui.processEvents()
                    detail = model.choice_details(EVENT, row['scene_key'], row['choice_key'])
                    source = json.loads(dialog.source_reader.toPlainText())
                    require(detail['source_valid'] is True and detail['reference'] == row and source['selected_flow'] == detail,
                            'all_19_UI_flow_selections_match_complete_scene_choice_and_fresh_details')
                    require(row['reference_id']==row['choice_key'] and row['related_stage_reference'] is None
                            and row['source_scene_link_verified'] is False and unknown(detail),
                            'documentary_navigation_does_not_become_proven_game_button_or_scene_transition')
                    text = dialog.flow_reader.toPlainText()
                    require('旗标' not in text,
                            'default_flow_player_text_uses_plain_game_language_without_flag_terms')
                    require(all(plain(rule['text']) in text for rule in row['documented_rules'])
                            and (not plain(row['choice_description']) or plain(row['choice_description']) in text),
                            'flow_player_text_retains_each_exact_result_and_its_rules')
                    role_label = {'display_option_reference':'选择参考', 'explanatory_text':'资料说明',
                                  'community_navigation_guide':'文献导航'}[row['presentation_role']]
                    require(role_label in dialog.flow.currentText(), 'flow_control_distinguishes_options_explanation_and_navigation')
                    require(parent_state() == previous and dialog.relic.currentIndex() == -1,
                            'manual_flow_selection_never_changes_parent_or_selects_an_offering')
                    if row['reference_id'] in STOP_KEYS:
                        require(row['choice_description']=='见好就收' and row['documented_result_text']
                                and plain(row['documented_result_text']) in text
                                and {r['id'] for r in row['original_scene_candidates']}==STOP_ORIGINALS
                                and row['current_actual_original_candidate'] is None
                                and row['original_choice_ids']==[], 'both_stop_results_keep_full_text_and_all_four_unresolved_original_candidates')
                        destinations = row['documented_destinations']
                        require(len(destinations)==1 and destinations[0]['scene_key']==EVENT+':scene:5'
                                and all(plain(d['description']) in text and d['actual_reached'] is None for d in destinations),
                                'both_stop_rows_retain_complete_PRTS_navigation_as_document_reference_not_actual_transition')
                        require('【PRTS流程导航记载的后续】' in text and '【文献补充的后续结果】' in text
                                and '【两份资料的后续不一致】' in text and '目前不能确定游戏实际会出现哪一种后续' in text,
                                'both_stop_rows_show_dual_original_text_conflict_and_actual_unknown_without_choosing_one')
                        if row['reference_id']==STOP_KEYS[-1]:
                            screenshot('player-complete-stop-result', dialog.flow_reader,
                                       '目前不能确定游戏实际会出现哪一种后续')
                    flow_readings.append({'reference_id': row['reference_id'], 'scene_key': row['scene_key'],
                                          'choice_key': row['choice_key'], 'role': row['presentation_role'],
                                          'stop_result': row['documented_result_text'],
                                          'original_candidate_ids': [r['id'] for r in row['original_scene_candidates']],
                                          'documented_navigation_destinations': deepcopy(row['documented_destinations']),
                                          'documented_conflict_visible': row['reference_id'] in STOP_KEYS,
                                          'actual_transition': None})
                    later(read_flow if len(flow_readings)<len(fixed_rows) else read_catalogue)

                def read_catalogue():
                    dialog.tabs.setCurrentIndex(1)
                    filtered_catalogue(None)
                    require(dialog.relic.currentIndex() == -1, 'full_catalogue_stays_unselected_before_manual_item_choice')
                    filtered_catalogue(False)
                    require(dialog.relic.count()==21, 'twenty_one_false_offering_flags_displayed_not_dropped')
                    choose(dialog.relic, ALPHA)
                    choose(dialog.owned, True)
                    false_result = current_offer('first-alpha-forbidden', 'excluded')
                    require(false_result['name']=='沙盘α' and false_result['can_offer_reference'] is False,
                            'exact_sandbox_alpha_false_flag_not_a_similar_item')
                    screenshot('player-alpha-cannot-offer', dialog.offer_reader, '不能作为提供物')
                    filtered_catalogue(True)
                    require(dialog.relic.count()==251 and dialog.relic.currentIndex()==-1,
                            'filter_change_clears_removed_false_selection_without_selecting_first_allowed_item')
                    dialog.search.setText('热水壶')
                    gui.processEvents()
                    require(dialog.relic.count()==1 and dialog.relic.itemData(0)==KETTLE and dialog.relic.currentIndex()==-1,
                            'search_intersects_flag_and_preserves_manual_selection_requirement')
                    choose(dialog.relic, KETTLE)
                    true_result = current_offer('first-kettle-allowed', 'matched')
                    require(true_result['name']=='热水壶' and true_result['can_offer_reference'] is True,
                            'exact_kettle_true_flag_is_only_offering_reference')
                    screenshot('player-kettle-can-offer', dialog.offer_reader, '不说明能否作为交换奖励得到')
                    later(second_exchange)

                def second_exchange():
                    choose(dialog.exchange_index, 2)
                    require(dialog.palm.isVisible() and dialog.first_type.isVisible(), 'second_exchange_actual_controls_visible')
                    current_offer('second-unknown-palm-and-type', 'unknown')
                    choose(dialog.palm, True)
                    choose(dialog.first_type, 'SCRAP')
                    current_offer('second-wrong-first-SCRAP', 'excluded')
                    choose(dialog.first_type, None)
                    current_offer('second-unknown-first-type', 'unknown')
                    choose(dialog.first_type, 'RELIC')
                    current_offer('second-same-first-RELIC', 'matched')
                    screenshot('player-second-exchange-conditions', dialog.offer_reader, '与首次同为收藏品')
                    choose(dialog.palm, False)
                    current_offer('second-palm-declared-false', 'excluded')
                    choose(dialog.palm, True)
                    choose(dialog.owned, False)
                    current_offer('second-owned-declared-false', 'excluded')
                    choose(dialog.owned, True)
                    choose(dialog.first_type, 'SCRAP')
                    choose(dialog.exchange_index, 1)
                    require(dialog.palm.isHidden() and dialog.first_type.isHidden(), 'returning_to_first_exchange_hides_stale_second_declarations')
                    first = current_offer('first-ignores-hidden-second-SCRAP', 'matched')
                    require(first['palm_unlocked_declared'] is None and first['first_exchange_item_type_declared'] is None,
                            'hidden_second_declarations_not_sent_as_first_exchange_history')
                    choose(dialog.exchange_index, 2)
                    choose(dialog.first_type, 'RELIC')
                    current_offer('second-final-same-type-state', 'matched')
                    later(prepare_selected_refresh)

                def prepare_selected_refresh():
                    nonlocal parent_saved, dialog_saved
                    choose(dialog.flow, STOP_KEYS[-1])
                    prime(dialog.flow_reader)
                    prime(dialog.offer_reader)
                    dialog.tabs.setCurrentWidget(dialog.source_reader)
                    prime(dialog.source_reader, True)
                    dialog.search.setSelection(0, 2)
                    parent_saved, dialog_saved = parent_state(), dialog_state()
                    later(selected_refresh)

                def selected_refresh():
                    number = sum(row['selected'] is not None for row in refreshes)
                    callbacks = [dialog.refresh_reference, panel.refresh,
                                 lambda: dialog.set_reference(EVENT, scope_key=deepcopy(panel.list.selected_key()))]
                    expected = {'parent': parent_saved, 'dialog': dialog_saved}
                    before_callback = {'parent': parent_state(), 'dialog': dialog_state()}
                    callbacks[number]()
                    gui.processEvents()
                    actual = {'parent': parent_state(), 'dialog': dialog_state()}
                    refresh_diagnostics.append({'path': ['selected_dialog','selected_parent','selected_same_reference'][number],
                                                'expected': deepcopy(expected), 'before_callback': before_callback,
                                                'after_callback': actual, 'before_vs_expected': differences(expected,before_callback),
                                                'after_vs_expected': differences(expected,actual)})
                    require(actual==expected, 'same_scope_refresh_keeps_all_flow_filters_declarations_readers_and_parent')
                    refreshes.append({'path': ['selected_dialog','selected_parent','selected_same_reference'][number],
                                      'selected': dialog.relic.currentData(), 'flow': dialog.flow.currentData(),
                                      'nonzero_scroll': dialog.source_reader.verticalScrollBar().value(),
                                      'selection': dialog.source_reader.textCursor().selectedText(), 'parent_unchanged': True})
                    later(selected_refresh if number<2 else source_failure)

                def source_failure():
                    manifest = read(ROOT/MANIFEST)
                    clone = temporary/'public-runtime-negative'
                    for name in set(manifest['runtime_files'])|{MANIFEST}:
                        source = ROOT/name
                        require(source.is_file() and not source.is_symlink() and source.resolve().is_relative_to(ROOT.resolve()),
                                'negative_fixture_copies_only_exact_regular_public_runtime_members')
                        target=clone/name
                        target.parent.mkdir(parents=True,exist_ok=True)
                        target.write_bytes(source.read_bytes())
                    target=clone/MANIFEST
                    raw=target.read_bytes()
                    with patch.object(model,'ROOT',clone):
                        require(model.event_reference(EVENT)['source_valid'] is True
                                and model.relic_offer_reference(KETTLE)['source_valid'] is True,
                                'complete_runtime_clone_warmed_valid_before_real_manifest_byte_damage')
                        try:
                            target.write_bytes(raw+b' ')
                            dialog.refresh_reference()
                            panel.refresh()
                            gui.processEvents()
                            failed=model.event_reference(EVENT)
                            require(failed['source_valid'] is False and failed['choices']==[] and failed['catalogue']==[],
                                    'fresh_source_failure_returns_no_old_flow_or_catalogue')
                            require(dialog.packet is None and dialog.flow.count()==0 and dialog.relic.count()==0
                                    and dialog.flow.currentIndex()==-1 and dialog.relic.currentIndex()==-1
                                    and not panel.relic_exchange_flow_button.isEnabled(), 'source_failure_clears_both_choices_and_disables_parent_entry')
                            require(all('已清除' in widget.toPlainText() for widget in (dialog.flow_reader,dialog.offer_reader,dialog.source_reader)),
                                    'source_failure_clears_all_three_reading_pages')
                        finally:
                            target.write_bytes(raw)
                        require(sha(target)==EXPECTED_SOURCE_PINS[MANIFEST], 'temporary_manifest_restored_exactly')
                        dialog.refresh_reference()
                        panel.refresh()
                        gui.processEvents()
                        require(dialog.packet is not None and dialog.flow.count()==19 and dialog.flow.currentIndex()==-1
                                and dialog.relic.currentIndex()==-1 and panel.relic_exchange_flow_button.isEnabled(),
                                'source_recovery_restores_reference_without_reselecting_flow_or_relic')
                    negatives.append({'kind':'complete_warm_runtime_clone_manifest_bytes','member':MANIFEST,
                                      'restored_sha256':sha(target),'restored_unselected':True,'actual_consumed':None})
                    later(switch_scope)

                def switch_scope():
                    choose(dialog.flow, STOP_KEYS[0])
                    choose(dialog.relic, KETTLE)
                    select_event(OTHER)
                    gui.processEvents()
                    require(not panel.relic_exchange_flow_button.isVisible() and dialog.packet is None
                            and dialog.flow.count()==0 and dialog.relic.count()==0
                            and dialog.flow.currentIndex()==-1 and dialog.relic.currentIndex()==-1,
                            'non_target_event_clears_all_old_flow_catalogue_and_results')
                    require(dialog.search.text()=='' and dialog.membership.currentData() is None
                            and dialog.exchange_index.currentData()==1 and dialog.owned.currentData() is None
                            and dialog.palm.currentData() is None and dialog.first_type.currentData() is None,
                            'scope_change_resets_only_reader_filters_and_declarations')
                    later(finish)

                def finish():
                    nonlocal done
                    require(len(flow_readings)==19 and [row['reference_id'] for row in flow_readings]==[row['reference_id'] for row in fixed_rows],
                            'all_nineteen_complete_flow_rows_actually_read_in_source_order')
                    stops=[row for row in flow_readings if row['reference_id'] in STOP_KEYS]
                    require(len(stops)==2 and all(set(row['original_candidate_ids'])==STOP_ORIGINALS for row in stops),
                            'both_complete_stop_readings_preserve_four_candidates_without_matching_by_number')
                    require([row['count'] for row in catalogue_reads]==[272,21,251], 'all_catalogue_and_both_flags_actually_browsed')
                    require(len(refreshes)==4 and all(row['selection'] and row['parent_unchanged'] for row in refreshes)
                            and all(row['nonzero_scroll']>0 for row in refreshes if row['selected'] is not None),
                            'default_reading_and_three_selected_refreshes_keep_actual_nonzero_selected_reading')
                    require(len(images)==5 and sum(row['parent_entry'] for row in images)==1
                            and sum(row['direct_player_text'] for row in images)==4,
                            'five_actual_PNGs_cover_manual_entry_full_exit_both_offering_flags_and_second_type')
                    calculation_after=tuple((window.relic_list.item(i).data(Qt.ItemDataRole.UserRole),window.relic_list.item(i).checkState().value)
                                            for i in range(window.relic_list.count()))
                    require(window.run.state==initial_run and calculation_after==calculation_before,
                            'reader_declarations_do_not_change_temporary_run_or_calculation_relic_selection')
                    for number,arguments in enumerate(scrap_arguments):
                        current=old_scrap.exchange_candidates('rogue_6_scrap_M_01',scrap_context,**arguments)
                        require(current==old_scrap_before[number], 'existing_scrap_exchange_API_complete_output_unchanged')
                        legacy_reads.append({'offered_item_id':'rogue_6_scrap_M_01','arguments':arguments,
                                             'before_sha256':json_sha(old_scrap_before[number]),'after_sha256':json_sha(current),
                                             'complete_output_equal':True,'actual_reward_quantity':current['actual_reward_quantity']})
                    require(bound_files()==before, 'selected_public_sources_unchanged_before_completion')
                    handles.append(native(window,'parent'))
                    done=True

                def deadline():
                    nonlocal failure
                    if not done and failure is None:
                        failure={'type':'TimeoutError','message':'Actual relic-flow reading checks incomplete.'}
                    close_owned()

                later(begin,500)
                QTimer.singleShot(max(30000,args.visible_ms),deadline)
                qt_exit=gui.exec()
                closed=not window.isVisible() and not(dialog and dialog.isVisible())
                if qt_exit!=0 or not closed or not done:
                    if failure is None:
                        failure={'type':'RuntimeError','message':'Checks, Qt or owned window closure incomplete.'}
                if failure is None:
                    isolated()
                after=bound_files()
                if before!=after and failure is None:
                    failure={'type':'AssertionError','message':'Selected sources changed before closure.'}
            finally:
                close_owned()
                gui.processEvents()
                closed=not window.isVisible() and not(dialog and dialog.isVisible())
    except BaseException as error:
        failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
    report={'section':305,'kind':'isolated_native_windows_relic_exchange_flow_reader','passed':done and failure is None,
            'failure':failure,'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),
            'process_id':os.getpid(),'qpa':qpa,'qt_exit_code':qt_exit,'verification_window_closed':closed,
            'checks':checks,'unique_checks':len(checks),'successful_assertion_executions_including_repeated_guards':executions,
            'requested_parent_client_size':list(SIZE),'requested_dialog_client_size':list(DIALOG_SIZE),
            'native_observations':handles,'screenshots':images,'screenshot_count':len(images),
            'actual_flow_readings':flow_readings,'catalogue_filter_observations':catalogue_reads,
            'offering_declaration_observations':offer_reads,'same_scope_refresh_observations':refreshes,
            'same_scope_refresh_diagnostics':refresh_diagnostics,'source_negative_fixtures':negatives,
            'legacy_scrap_API_comparisons':legacy_reads,'source_sha256_before':before,'source_sha256_after':after,
            'source_guard_is_selected_not_all_transitive_dependencies':True,'temporary_state_root':True,
            'state_paths_replaced_before_constructor':['ROOT','SETTINGS','OPERATOR_STATE','RUN_STATE'],
            'private_state_read_copied_or_restored':False,'external_operation_attempts':attempts,
            'external_entrypoints_blocked_before_original_call':True,'game_operated':False,'game_captures':0,
            'chat_sent':False,'chat_attempted':bool(attempts['desktop_request']or attempts['provider_chat']),
            'original_project_window_operated_or_restarted':False,
            'actual_process_termination_verified_by_this_script':False,
            'owned_supervisor_exit_and_cleanup_required_separately':True,
            'launch_Popen_PID_must_be_recorded_separately_from_actual_fixture_PID':True,
            'actual_exchange_inventory_consumption_or_reward_verified':False,
            'scope':'Fixed272-body catalogue offering flags,19 documentary flow rows and explicit offline declarations; no actual exchange, payment, consumption, reward pool, eligibility, inventory or game transition.'}
    with destination.open('x',encoding='utf8')as stream:
        stream.write(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    return 0 if report['passed']else 1


if __name__=='__main__':
    raise SystemExit(main())
