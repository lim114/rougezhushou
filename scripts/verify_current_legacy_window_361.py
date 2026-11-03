"""Actual Windows MainWindow legacy-reader acceptance; install/review before run."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
from tempfile import TemporaryDirectory
from contextlib import ExitStack
from unittest.mock import patch
from copy import deepcopy
import argparse, json, os, sys, traceback
ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'rouge/app.py').is_file())
sys.path.insert(0, str(ROOT))
CANONICAL = 'scripts/verify_current_legacy_window_361.py'


def bound_files():
    names = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'rouge').glob('*.py')}
    from rouge import current_legacy as model, current_startup as startup, expansion_reference as version
    from rouge import seed_cultivation_planning as seed, duel_reward_planning as parts
    for provider in (model, startup, version):
        names.add(provider.MANIFEST)
        manifest = json.loads((ROOT / provider.MANIFEST).read_bytes()); names.update(manifest['files'])
    names.update(('rouge/data/seed-cultivation-reference.json', 'rouge/data/duel-reward-reference.json',
                  'rouge/data/original-entry-reference.json'))
    names.update('rouge/data/' + name for name in parts.reference_data()['runtime_source_sha256'])
    names.update((CANONICAL, 'scripts/verify_full_available.py',
                  'tests/test_current_legacy_361.py', 'tests/test_current_legacy_view_361.py'))
    for name in ('scripts/build_current_legacy_361.py', 'verification/sections/361-preparation/scope.json'):
        if (ROOT / name).is_file(): names.add(name)
    result = {}
    for name in sorted(names):
        path = ROOT / name
        if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()):
            raise ValueError('Exact regular installed public source required: ' + name)
        result[name] = sha256(path.read_bytes()).hexdigest()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', type=Path, required=True)
    parser.add_argument('--visible-ms', type=int, default=120000)
    args = parser.parse_args(); dest = args.receipt.resolve()
    assert not dest.exists(); dest.parent.mkdir(parents=True, exist_ok=True)
    before = bound_files(); checks = []; images = []; observations = []; refreshes = []
    calls = {k: 0 for k in ('game_connect', 'capture', 'next_frame', 'desktop_start',
                            'desktop_request', 'provider_chat', 'credential_read')}
    failure = None; window = None; gui = None; exitcode = None; done = False
    def require(value, name):
        if not value: raise AssertionError(name)
        if name not in checks: checks.append(name)
    def forbidden(name):
        def fail(*a, **kw): calls[name] += 1; raise AssertionError('Forbidden real operation: ' + name)
        return fail
    try:
        if sys.platform != 'win32': raise RuntimeError('Actual Windows required')
        import win32gui, win32process
        from PySide6.QtCore import Qt, QTimer
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QApplication, QTabWidget, QPlainTextEdit
        from PySide6.QtTest import QTest
        from rouge import app as app_module, current_legacy as model, current_startup as startup
        gui = QApplication([]); require(gui.platformName() == 'windows', 'actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge361-public-') as folder, ExitStack() as stack:
            temporary = Path(folder)
            for name, value in {'ROOT': temporary, 'SETTINGS': temporary / 'settings.json',
                    'OPERATOR_STATE': temporary / 'operators.json', 'RUN_STATE': temporary / 'run.json'}.items():
                stack.enter_context(patch.object(app_module, name, value))
            backend = app_module.DesktopBackend
            stack.enter_context(patch.object(app_module, 'DesktopBackend', lambda _path, callback: backend(temporary / 'chat', callback)))
            stack.enter_context(patch.object(app_module, 'list_game_windows', return_value=[]))
            for name, key in (('connect', 'game_connect'), ('capture', 'capture'), ('next_frame', 'next_frame')):
                stack.enter_context(patch.object(app_module.GameCapture, name, side_effect=forbidden(key)))
            for name, key in (('start', 'desktop_start'), ('request', 'desktop_request')):
                stack.enter_context(patch.object(backend, name, side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module, 'stream_chat', side_effect=forbidden('provider_chat')))
            stack.enter_context(patch.object(app_module, 'read_key', side_effect=forbidden('credential_read')))
            window = app_module.MainWindow(); window.resize(1220, 850)
            window.setWindowTitle('第361节 · 跨局助力与失败／下次开始条件（公开隔离验收）')
            window.show(); gui.processEvents(); tabs = window.centralWidget()
            main_panel = window.reference_panel('relics'); panel = main_panel
            state = deepcopy(window.run.state); context = deepcopy(window.battle_preview.context)
            def native(widget=None):
                widget = window if widget is None else widget; hwnd = int(widget.winId())
                pid = win32process.GetWindowThreadProcessId(hwnd)[1]
                require(win32gui.IsWindowVisible(hwnd) and not win32gui.IsIconic(hwnd) and pid == os.getpid(),
                        'visible_owned_native_MainWindow_HWND_PID')
                return {'hwnd': hwnd, 'pid': pid, 'size': [widget.width(), widget.height()]}
            def shot(label, widget=None):
                gui.processEvents(); widget = panel if widget is None else widget
                file = dest.with_name('window-' + label + '.png'); assert not file.exists()
                require(widget.grab().save(str(file), 'PNG'), 'actual_widget_screenshot_saved')
                images.append({'name': label, 'path': str(file), 'sha256': sha256(file.read_bytes()).hexdigest(),
                               'native': native(widget.window())})
            def choose(combo, key):
                index = combo.findData(key); require(index >= 0, 'exact_legacy_branch_or_condition_value')
                combo.setCurrentIndex(index); gui.processEvents()
            def select_list(widget, key):
                item = next(widget.item(i) for i in range(widget.count())
                            if widget.item(i).data(Qt.ItemDataRole.UserRole) == key)
                widget.scrollToItem(item); gui.processEvents()
                QTest.mouseClick(widget.viewport(), Qt.MouseButton.LeftButton, pos=widget.visualItemRect(item).center())
                gui.processEvents(); require(widget.currentItem().data(Qt.ItemDataRole.UserRole) == key,
                                             'actual_exact_legacy_or_parent_original_mouse_selection')
            def declared():
                return {name: getattr(panel, name).currentData() for name in ('origin_mode', 'origin_grade',
                    'origin_failed', 'next_mode', 'next_grade', 'next_started', 'prior_claim_consumed')}
            def condition():
                return json.loads(panel.technical.toPlainText())['condition']
            def reading(widget):
                cursor = widget.textCursor()
                return {'anchor': cursor.anchor(), 'position': cursor.position(), 'selection': cursor.selectedText(),
                        'scroll': widget.verticalScrollBar().value()}
            def source(kind, key):
                request = next(panel.source_combo.itemData(i) for i in range(panel.source_combo.count())
                    if panel.source_combo.itemData(i) and panel.source_combo.itemData(i)['kind'] == kind
                    and panel.source_combo.itemData(i)['key'] == key)
                choose(panel.source_combo, request)
                require(panel.source_button.isVisible() and panel.source_button.isEnabled(), 'accurate_source_button_visible')
                QTest.mouseClick(panel.source_button, Qt.MouseButton.LeftButton); gui.processEvents()
                child = panel.link_dialog
                require(child is not None and child.isVisible(), 'actual_owned_exact_source_window_opened')
                return child
            def raw_source(child, expected):
                source_tabs = child.findChildren(QTabWidget)
                require(len(source_tabs) == 1 and source_tabs[0].count() == 2, 'raw_original_has_two_actual_reading_tabs')
                player, technical = source_tabs[0].widget(0), source_tabs[0].widget(1)
                require(isinstance(player, QPlainTextEdit) and isinstance(technical, QPlainTextEdit)
                        and player.isReadOnly() and technical.isReadOnly(), 'raw_original_readers_readonly')
                value = json.loads(technical.toPlainText())
                require(value['original'] == expected and value['actual_received'] is None
                        and not value['run_updated'] and not value['next_run_created'],
                        'actual_popup_complete_exact_original_and_unknown_receipt')
                return player.toPlainText()
            def reverse(category, key, item_kind=None):
                nonlocal main_panel, panel
                previous = getattr(main_panel, 'legacy_reference_dialog', None)
                main_panel = window.reference_panel(category); gui.processEvents()
                if category == 'relics': choose(main_panel.item_kind, item_kind)
                select_list(main_panel.entries, key)
                require(main_panel.legacy_reference_item_button.isVisible(), 'exact_selected_parent_original_reverse_button_visible')
                QTest.mouseClick(main_panel.legacy_reference_item_button, Qt.MouseButton.LeftButton); gui.processEvents()
                dialog = main_panel.legacy_reference_dialog; panel = dialog.panel
                require(dialog.isVisible() and panel.result is not None and
                        (previous is None or previous is not dialog and not previous.isVisible()),
                        'reverse_entry_uses_new_owned_source_not_stale_dialog')
                target_category = 'items' if category == 'relics' else category
                expected = model.locate(target_category, key)
                # locate also accepts relics; use the same exact source category
                # chosen by the final root integration rather than inventing it.
                require(panel.target == expected or category == 'relics' and panel.target == model.locate('relics', key),
                        'reverse_target_is_fresh_exact_model_locate_result')
                return dialog
            def exercise():
                nonlocal done, failure, main_panel, panel
                dialog = None; child = None
                try:
                    bar = tabs.tabBar(); index = tabs.indexOf(main_panel)
                    QTest.mouseClick(bar, Qt.MouseButton.LeftButton, pos=bar.tabRect(index).center()); gui.processEvents()
                    require(tabs.currentWidget() is main_panel, 'actual_MainWindow_common_item_page_opened')
                    require(main_panel.legacy_reference_button.isVisible(), 'ordinary_cross_run_reference_entry_visible')
                    QTest.mouseClick(main_panel.legacy_reference_button, Qt.MouseButton.LeftButton); gui.processEvents()
                    dialog = main_panel.legacy_reference_dialog; panel = dialog.panel
                    require(dialog.isVisible() and panel.entries.count() == 14 and panel.selected_key is None,
                            'actual_all14_manual_legacy_directory')
                    require(panel.conditions.isHidden() and all(v is None for v in declared().values()),
                            'overview_has_no_foreign_specific_conditions_or_automatic_run_declaration')
                    require(all(row['source_unchanged_from_previous_fixed_snapshot'] for row in model.rows(panel.result)),
                            '14_unchanged_records_not_presented_as_new_version_inheritance_mechanics')
                    shot('legacy-directory')
                    for group, count in (('cat', 3), ('dog', 3), ('cerberus', 1), ('feather', 6), ('hidden', 1)):
                        choose(panel.group, group)
                        require(panel.entries.count() == count and panel.selected_key is None,
                                'five_actual_group_counts_and_no_auto_selection')
                    choose(panel.group, 'all')
                    seed_count = 0; blue_count = 0; documented_seed_count = 0
                    for key, row in panel.result['data']['rows'].items():
                        select_list(panel.entries, key); raw = json.loads(panel.technical.toPlainText())
                        require(raw['row'] == row and model.version._plain(row['item']['usage']) in panel.player.toPlainText(),
                                'every_exact_legacy_complete_record_and_own_usage_displayed')
                        require(panel.conditions.isVisible() == (key == model.HIDDEN),
                                'only_hidden_failure_aid_has_two_run_inputs')
                        require(panel.result['actual_held'] is None and panel.result['actual_inherited'] is None
                                and panel.result['actual_claim_consumed'] is None and panel.result['actual_next_received'] is None
                                and not panel.result['run_updated'] and not panel.result['next_run_created']
                                and not panel.result['calculation_applied'], 'directory_never_creates_or_grants_a_run')
                        observations.append({'kind': 'legacy', 'id': key, 'group': row['group'], 'row': row,
                                             'actual_held': panel.result['actual_held']})
                        if key == model.HIDDEN:
                            kinds = {panel.source_combo.itemData(i)['kind'] for i in range(panel.source_combo.count())
                                     if panel.source_combo.itemData(i)}
                            require('seed' not in kinds and 'startup' not in kinds and row['hidden_in_original'] is True,
                                    'hidden_legacy_is_neither_fifth_seed_family_nor_seventh_blue_choice')
                            continue
                        child = source('seed', key); seed_count += 1
                        require(child.selected_id() == key, 'all13_old_seed_readers_select_exact_original_not_same_name')
                        old = next(r for r in child.result['rows'] if r['item_id'] == key)
                        require(old['item'] == row['item'] and old['legacy_group_id'] == row['legacy_group_id']
                                and old['documented_source_id'] is row['seed_source_reference']['documented_source_id'],
                                'current_legacy_to_old_seed_complete_identity_and_source_qualification_match')
                        documented_seed_count += int(old['documented_source_id'])
                        require(old['actual_received'] is None and old['actual_future_grant'] is None
                                and child.result['actual_result_item_id'] is None,
                                'old_seed_link_does_not_grant_current_or_next_item')
                        if key == 'rogue_6_legacy_01_1':
                            require(old['documented_source_id'] is False, 'same_named_cat_variant_source_stays_unproven')
                            shot('seed-original-variant', child)
                        child.close(); pointer = row['startup_pointer']
                        if pointer:
                            child = source('startup', pointer['choice_id']); blue_count += 1
                            require(child.panel.scene_id == pointer['scene_id'] and child.panel.choice_id == pointer['choice_id'],
                                    'all6_feather_sources_open_distinct_exact_startup_choice')
                            original = child.panel.result['choices'][pointer['choice_id']]
                            require(original['legacy_id'] == key and original['item_id'] == pointer['reward_item_id']
                                    and child.panel.result['actual_eligible'] is None and child.panel.result['actual_received'] is None
                                    and child.panel.result['actual_displayed_choice_ids'] is None,
                                    'six_blue_support_mappings_not_menu_or_actual_inheritance')
                            require(child.panel.inherited.currentData() is None, 'opening_blue_source_does_not_declare_inheritance')
                            observations.append({'kind': 'blue', 'legacy': key, 'pointer': pointer,
                                                 'actual_received': child.panel.result['actual_received']})
                            if key == 'rogue_6_legacy_09': shot('distinct-blue-support', child)
                            child.close()
                    require(seed_count == 13 and blue_count == 6 and documented_seed_count == 4,
                            'all13_seed_links_and6_blue_links_with_only4_explicit_seed_IDs_exercised')
                    select_list(panel.entries, model.HIDDEN)
                    choose(panel.origin_grade, 3); child = source('item', model.TARGET)
                    old_child = child; select_list(panel.entries, 'rogue_6_legacy_01')
                    require(not old_child.isVisible() and panel.conditions.isHidden()
                            and all(v is None for v in declared().values()),
                            'changing_selected_legacy_closes_source_and_clears_hidden_only_conditions')
                    select_list(panel.entries, model.HIDDEN)
                    choose(panel.origin_mode, 'NORMAL'); choose(panel.origin_failed, True)
                    choose(panel.next_mode, 'NORMAL'); choose(panel.next_started, True); choose(panel.prior_claim_consumed, False)
                    for origin in range(5):
                        for receipt in range(5):
                            choose(panel.origin_grade, origin); choose(panel.next_grade, receipt); value = condition()
                            require(value['listed_origin_match'] is (origin < 4) and value['listed_receipt_match'] is (receipt < 4),
                                    'all25_two_run_grade_pairs_check0_to3_and4_independently')
                            require(all(value[k] is None for k in ('actual_server_eligible', 'actual_claim_exists',
                                    'actual_claim_consumed', 'actual_received')) and not value['next_run_created'],
                                    'matching_or_failed_declarations_never_become_actual_receipt')
                            observations.append({'kind': 'grade_pair', 'origin_grade': origin, 'next_grade': receipt,
                                                 'comparison': value})
                    choose(panel.origin_grade, 3); choose(panel.next_grade, 4)
                    require(condition()['status'] == 'documented_check_consumption_risk'
                            and '没有确认实际消耗或发放' in panel.player.toPlainText()
                            and '主动放弃' in panel.player.toPlainText(),
                            'wrong_next_started_grade_warns_without_claiming_consumption_or_equating_abandonment')
                    shot('failure-grade-boundary')
                    choose(panel.next_grade, 3); require(condition()['status'] == 'listed_conditions_match_only',
                                                         'both_qualified_grades_only_match_listed_conditions')
                    choose(panel.origin_failed, False); require(condition()['status'] == 'failure_not_declared',
                                                               'no_failure_does_not_create_hidden_aid')
                    choose(panel.origin_failed, True); choose(panel.prior_claim_consumed, True)
                    require(condition()['status'] == 'claim_already_declared_consumed', 'already_consumed_check_not_reissued')
                    choose(panel.prior_claim_consumed, False); choose(panel.next_mode, 'OTHER')
                    require(panel.next_grade.isHidden() and panel.next_grade.currentData() is None
                            and panel.origin_grade.currentData() == 3, 'other_next_mode_hides_only_own_grade_and_preserves_origin')
                    choose(panel.next_mode, 'NORMAL'); choose(panel.next_grade, 4)
                    dialog.resize(740, 470); gui.processEvents()
                    for reader in (panel.player, panel.technical):
                        panel.tabs.setCurrentWidget(reader); gui.processEvents(); cursor = reader.textCursor()
                        cursor.setPosition(3); cursor.setPosition(15, QTextCursor.MoveMode.KeepAnchor); reader.setTextCursor(cursor)
                        scroll = reader.verticalScrollBar(); require(scroll.maximum() > 0, 'both_legacy_readers_have_real_nonzero_range')
                        scroll.setValue(min(3, scroll.maximum())); previous = reading(reader); selected = panel.selected_key
                        branch = panel.group.currentData(); declaration = declared(); tab = panel.tabs.currentIndex()
                        require(previous['scroll'] > 0 and previous['position'] > previous['anchor'],
                                'both_readers_actual_nonzero_scroll_and_text_selection')
                        require(main_panel.refresh_reference(), 'actual_ordinary_parent_refresh'); gui.processEvents()
                        require(reading(reader) == previous and panel.selected_key == selected and panel.group.currentData() == branch
                                and declared() == declaration and panel.tabs.currentIndex() == tab,
                                'parent_refresh_preserves_two_nonzero_readers_legacy_conditions_branch_and_tab')
                        refreshes.append({'before': previous, 'after': reading(reader), 'declarations': declaration})
                    dialog.resize(1100, 840); gui.processEvents()
                    for grade in range(5):
                        child = source('difficulty', 'NORMAL|' + str(grade))
                        original = next(r for r in panel.result['data']['originals']['difficulties']
                                        if r['modeDifficulty'] == 'NORMAL' and r['grade'] == grade)
                        text = raw_source(child, original)
                        require('不把该档自动填为失败局或下次开始' in text and panel.origin_grade.currentData() == 3
                                and panel.next_grade.currentData() == 4, 'all5_original_difficulty_popups_do_not_assign_either_run')
                        child.close()
                    child = source('item', model.TARGET)
                    original = {'item': panel.result['data']['originals']['items'][model.TARGET],
                                'relic': panel.result['data']['originals']['relics'][model.TARGET]}
                    text = raw_source(child, original)
                    require('特勤任务影像' in text and '不代表已持有' in text, 'exact_special_film_original_not_current_buff')
                    shot('special-film-original', child)
                    damaged = temporary / 'damaged-public'; manifest = json.loads((ROOT / model.MANIFEST).read_bytes())
                    for name in (model.MANIFEST, *manifest['files']):
                        path = damaged / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes((ROOT / name).read_bytes())
                    bad = damaged / (model.PACK + '/reference-data.json'); original_bytes = bad.read_bytes()
                    original_file = model.version._file
                    def own_file(name):
                        return damaged / name if name == model.MANIFEST or name in manifest['files'] else original_file(name)
                    with patch.object(model.version, '_file', side_effect=own_file):
                        bad.write_bytes(original_bytes + b'x')
                        require(main_panel.refresh_reference(), 'ordinary_parent_version_source_stays_valid_on361_member_damage')
                        gui.processEvents()
                        require(panel.result is None and panel.entries.count() == 0 and panel.selected_key is None
                                and panel.player.toPlainText() == model.UNAVAILABLE and panel.technical.toPlainText() == ''
                                and not child.isVisible(), 'actual361_member_damage_clears_old_content_and_source_tree')
                        require(panel.conditions.isHidden() and all(v is None for v in declared().values())
                                and panel.source_combo.count() == 0 and not panel.source_button.isEnabled(),
                                'bad_source_clears_both_run_declarations_and_all_source_entries')
                        shot('source-loss'); bad.write_bytes(original_bytes)
                        require(main_panel.refresh_reference(), 'actual_parent_recovery_refresh'); gui.processEvents()
                        require(panel.result is not None and panel.selected_key is None and panel.entries.currentItem() is None
                                and all(v is None for v in declared().values()), 'restored_source_requires_manual_legacy_not_old_selection')
                    for key, row in panel.result['data']['rows'].items():
                        dialog = reverse('relics', key, 'LEGACY')
                        require(panel.selected_key == key and panel.group.currentData() == row['group']
                                and all(v is None for v in declared().values()), 'all14_ordinary_LEGACY_reverse_entries_exact_without_run_declarations')
                        observations.append({'kind': 'reverse_legacy', 'id': key, 'target': panel.target})
                    feathers = model.rows(panel.result, 'feather')
                    for row in feathers:
                        pointer = row['startup_pointer']
                        dialog = reverse('relics', pointer['reward_item_id'], 'RELIC')
                        require(panel.selected_key == row['id'], 'all6_blue_reward_reverse_entries_preserve_distinct_same_named_source')
                        dialog = reverse('choices', pointer['choice_id'])
                        require(panel.selected_key == row['id'], 'all6_choice_reverse_entries_preserve_exact_legacy_source')
                    for grade in range(5):
                        dialog = reverse('difficulty', 'NORMAL|' + str(grade))
                        require(panel.selected_key == model.HIDDEN and all(v is None for v in declared().values()),
                                'all5_NORMAL_reverse_entries_open_hidden_without_assigning_origin_or_next_grade')
                    dialog = reverse('scenes', 'scene_ro6_startbuff_enter')
                    require(panel.group.currentData() == 'feather' and panel.entries.count() == 6 and panel.selected_key is None,
                            'startup_scene_reverse_keeps_six_distinct_candidates_no_automatic_legacy')
                    dialog = reverse('relics', model.TARGET, 'RELIC')
                    require(panel.selected_key == model.HIDDEN and all(v is None for v in declared().values()),
                            'special_film_reverse_opens_hidden_without_inferring_claim_from_held_item')
                    shot('reverse-special-film')
                    child = source('item', model.TARGET); old_dialog = dialog
                    unrelated = next(main_panel.entries.item(i).data(Qt.ItemDataRole.UserRole)
                        for i in range(main_panel.entries.count()) if model.locate('items', main_panel.entries.item(i).data(Qt.ItemDataRole.UserRole)) is None)
                    select_list(main_panel.entries, unrelated)
                    require(main_panel.legacy_reference_item_button.isHidden() and not old_dialog.isVisible()
                            and not child.isVisible(), 'unrelated_parent_item_has_no_legacy_button_and_closes_owned_tree')
                    dialog = reverse('relics', model.HIDDEN, 'LEGACY'); child = source('item', model.TARGET)
                    old_dialog = dialog; old_child = child; window.reference_panel('stages'); gui.processEvents()
                    require(not old_dialog.isVisible() and not old_child.isVisible(), 'changing_common_page_closes_complete_legacy_tree')
                    dialog = reverse('relics', 'rogue_6_legacy_04', 'LEGACY')
                    pointer = panel.result['data']['rows']['rogue_6_legacy_04']['startup_pointer']
                    child = source('startup', pointer['choice_id'])
                    require(window.run.state == state and window.battle_preview.context == context,
                            'temporary_run_and_old_battle_context_unchanged')
                    require(all(v == 0 for v in calls.values()) and not window.auto.isChecked(),
                            'all_seven_real_external_operations_zero'); native()
                    window.close(); gui.processEvents()
                    require(not dialog.isVisible() and not child.isVisible(), 'actual_MainWindow_closes_legacy_and350_source_tree')
                    require(sum(r['kind'] == 'legacy' for r in observations) == 14
                            and sum(r['kind'] == 'blue' for r in observations) == 6
                            and sum(r['kind'] == 'grade_pair' for r in observations) == 25
                            and sum(r['kind'] == 'reverse_legacy' for r in observations) == 14,
                            'all_required_original_groups_and25_grade_pairs_actually_exercised')
                    require(len(images) == 7, 'only_seven_necessary_actual_screenshots')
                    done = True; gui.exit(0)
                except BaseException as error:
                    failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
                    if dialog is not None: dialog.close()
                    window.close(); gui.exit(1)
            QTimer.singleShot(250, exercise)
            QTimer.singleShot(args.visible_ms, lambda: gui.exit(2) if not done else None)
            exitcode = gui.exec()
            require(exitcode == 0 and done and not window.isVisible(), 'actual_Qt_success_and_owned_MainWindow_closed')
    except BaseException as error:
        if failure is None: failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
    finally:
        if window is not None: window.close()
    after = bound_files()
    result = {'section': 361, 'passed': done and failure is None and exitcode == 0 and before == after,
        'failure': failure, 'process_id': os.getpid(), 'qpa': gui.platformName() if gui else None,
        'qt_exit_code': exitcode, 'verification_window_closed': window is not None and not window.isVisible(),
        'unique_checks': len(checks), 'checks': checks, 'actual_readings': observations,
        'same_identity_refresh_observations': refreshes, 'screenshots': images,
        'source_sha256_before': before, 'source_sha256_after': after,
        'source_scope_selected_not_all_transitive_dependencies': True, 'external_operation_attempts': calls,
        'temporary_state': True, 'private_contents_read_copied_or_restored': False,
        'game_operated': False, 'chat_sent': False, 'current_server_or_original_runtime_validated': False,
        'at_utc': datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    print(json.dumps({'passed': result['passed'], 'checks': len(checks), 'failure': failure}, ensure_ascii=False))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
