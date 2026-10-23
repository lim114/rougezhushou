"""Actual Windows initial-recruitment directory and exact two-way associations."""
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
CANONICAL = 'scripts/verify_current_initial_recruit_window_364.py'


def bound_files():
    from rouge import current_initial_recruit as model, expansion_reference as version
    names = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'rouge').glob('*.py')}
    for provider in (model, version):
        names.add(provider.MANIFEST)
        manifest = json.loads((ROOT / provider.MANIFEST).read_bytes()); names.update(manifest['files'])
    names.update((CANONICAL, 'scripts/verify_full_available.py',
                  'tests/test_current_initial_recruit_364.py', 'tests/test_current_initial_recruit_view_364.py'))
    for name in ('scripts/build_current_initial_recruit_364.py', 'verification/sections/364-preparation/scope.json'):
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
        from PySide6.QtWidgets import QApplication
        from PySide6.QtTest import QTest
        from rouge import app as app_module, current_initial_recruit as model
        gui = QApplication([]); require(gui.platformName() == 'windows', 'actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge364-public-') as folder, ExitStack() as stack:
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
            window.setWindowTitle('第364节 · 开局招募组合与准确配置（公开隔离验收）')
            window.show(); gui.processEvents(); tabs = window.centralWidget()
            main_panel = window.reference_panel('initial'); panel = main_panel
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
                index = combo.findData(key); require(index >= 0, 'exact_recruit_branch_scope_or_declaration_value')
                combo.setCurrentIndex(index); gui.processEvents()
            def select_list(widget, key):
                item = next(widget.item(i) for i in range(widget.count())
                            if widget.item(i).data(Qt.ItemDataRole.UserRole) == key)
                widget.scrollToItem(item); gui.processEvents()
                QTest.mouseClick(widget.viewport(), Qt.MouseButton.LeftButton, pos=widget.visualItemRect(item).center())
                gui.processEvents(); require(widget.currentItem().data(Qt.ItemDataRole.UserRole) == key,
                                             'actual_exact_initial_group_or_related_mouse_selection')
            def unknowns(value):
                require(all(value[k] is None for k in ('actual_unlocked', 'actual_eligible', 'actual_menu', 'actual_recruits')),
                        'source_or_declaration_never_becomes_account_unlock_menu_or_recruit')
                require(value['data']['actual_account_unlocks'] is None and value['data']['actual_random_candidates'] is None
                        and not value['data']['run_updated'], 'reference_does_not_modify_account_or_run')
            def reading(widget):
                cursor = widget.textCursor()
                return {'anchor': cursor.anchor(), 'position': cursor.position(), 'selection': cursor.selectedText(),
                        'scroll': widget.verticalScrollBar().value()}
            def selected_related():
                item = panel.related.currentItem()
                return None if item is None else item.data(Qt.ItemDataRole.UserRole)
            def declared_view():
                return {'kind': panel.kind.currentData(), 'scope': panel.scope.currentData(),
                        'query': panel.search.text(), 'target': panel.selected_target(),
                        'declaration': panel.other_exploration.currentData(), 'related': selected_related(),
                        'related_scroll': panel.related.verticalScrollBar().value()}
            def open_related(target):
                select_list(panel.related, target)
                require(panel.open_related_button.isEnabled() and panel.open_related_button.isVisible(),
                        'actual_related_link_button_enabled_for_explicit_relation')
                QTest.mouseClick(panel.open_related_button, Qt.MouseButton.LeftButton); gui.processEvents()
                require(panel.selected_target() == target and panel.selected_result['target'] == target,
                        'actual_related_click_navigates_exact_target_without_new_window')
                unknowns(panel.selected_result)
            def reverse(key):
                nonlocal main_panel, panel
                previous = getattr(main_panel, 'initial_recruits_dialog', None)
                main_panel = window.reference_panel('initial'); gui.processEvents()
                select_list(main_panel.entries, key)
                require(main_panel.flow_button.isHidden() and main_panel.open_documented_flow() is False,
                        'original_event_flow_guard_still_rejects_initial_configuration')
                require(main_panel.initial_recruits_item_button.isVisible(), 'exact_initial_parent_reverse_button_visible')
                QTest.mouseClick(main_panel.initial_recruits_item_button, Qt.MouseButton.LeftButton); gui.processEvents()
                dialog = main_panel.initial_recruits_dialog; panel = dialog.panel
                require(dialog.isVisible() and panel.result is not None and
                        (previous is None or previous is not dialog and not previous.isVisible()),
                        'ordinary_reverse_entry_uses_new_owned_dialog_not_stale_target')
                expected = model.locate('initial', key)
                require(expected is not None and panel.selected_target() == expected and panel.selected_result['target'] == expected,
                        'ordinary_initial_reverse_uses_all_four_original_identity_fields')
                unknowns(panel.selected_result); return dialog
            def exercise():
                nonlocal done, failure, main_panel, panel
                dialog = None
                try:
                    bar = tabs.tabBar(); index = tabs.indexOf(main_panel)
                    QTest.mouseClick(bar, Qt.MouseButton.LeftButton, pos=bar.tabRect(index).center()); gui.processEvents()
                    require(tabs.currentWidget() is main_panel, 'actual_MainWindow_common_exploration_settings_opened')
                    require(main_panel.initial_recruits_button.isVisible(), 'ordinary_initial_recruit_directory_button_visible')
                    QTest.mouseClick(main_panel.initial_recruits_button, Qt.MouseButton.LeftButton); gui.processEvents()
                    dialog = main_panel.initial_recruits_dialog; panel = dialog.panel
                    require(dialog.isVisible() and panel.entries.count() == 21 and panel.selected_target() is None,
                            'actual_all21_initial_directory_default_unselected')
                    require(panel.scope.findData('unlinked') == -1 and panel.declaration_row.isHidden()
                            and panel.related.count() == 0, 'initial_overview_has_no_unlinked_filter_or_random_specific_input')
                    data = deepcopy(panel.result['data']); initial = data['initial']; groups = data['groups']
                    require(len(initial) == 21 and len(groups) == 14 and data['explicit_association_count'] == 106
                            and data['raw_group_definitions_equal_previous_baseline'] is True,
                            '21configs14groups106relations_not_new14_combinations')
                    require(len({r['id'] for r in initial}) == 21, 'all21_four_part_configuration_keys_are_unique')
                    shot('initial-directory')
                    for scope, count in (('normal', 17), ('monthly', 4), ('all', 21)):
                        choose(panel.scope, scope)
                        require(panel.entries.count() == count and panel.selected_target() is None,
                                'initial_scope_counts17normal4monthly21all_without_auto_selection')
                    for config in initial:
                        select_list(panel.entries, config['id']); value = panel.selected_result
                        require(value['row'] == config and value['kind'] == 'initial', 'every_initial_complete_original_displayed')
                        original = config['original']
                        require(json.loads(config['id']) == [original['modeId'], original['modeGrade'], original['predefinedId'], original['predefinedStyle']],
                                'exact_identity_is_mode_grade_predefined_and_style_not_name_or_level')
                        expected = [{'kind': 'group', 'key': gid} for gid in config['group_ids']]
                        actual = [panel.related.item(i).data(Qt.ItemDataRole.UserRole) for i in range(panel.related.count())]
                        require(actual == expected and len(actual) == (6 if config['scope'] == 'normal' else 1),
                                'every_initial_related_list_matches_only_its_explicit_group_pointers')
                        require(panel.declaration_row.isHidden(), 'all_initial_configs_hide_random_group_declaration')
                        unknowns(value); observations.append({'kind': 'initial', 'id': config['id'], 'original': original, 'related': actual})
                        source_target = {'kind': 'initial', 'key': config['id']}
                        for target in expected:
                            open_related(target)
                            require(source_target in [panel.related.item(i).data(Qt.ItemDataRole.UserRole)
                                    for i in range(panel.related.count())], 'reverse_association_explicitly_contains_original_four_field_configuration')
                            group_id = panel.selected_result['row']['id']; open_related(source_target)
                            require(panel.selected_result['row'] == config, 'every_relation_round_trip_returns_complete_original_configuration')
                            observations.append({'kind': 'association_round_trip', 'initial': config['id'], 'group': group_id,
                                                 'actual_menu': panel.selected_result['actual_menu']})
                    choose(panel.kind, 'group')
                    require(panel.entries.count() == 14 and panel.scope.findData('unlinked') >= 0,
                            'group_branch_has14_exact_definitions_and_own_unlinked_filter')
                    for scope, count in (('normal', 6), ('monthly', 4), ('unlinked', 4), ('all', 14)):
                        choose(panel.scope, scope)
                        require(panel.entries.count() == count and panel.selected_target() is None,
                                'group_scope_counts6normal4monthly4unlinked14all_without_auto_selection')
                    for group in groups:
                        select_list(panel.entries, group['id']); value = panel.selected_result; text = panel.player.toPlainText()
                        require(value['row'] == group and group['original']['desc'] in text,
                                'every_group_complete_record_and_original_description_displayed')
                        require(panel.declaration_row.isVisible() == group['random_choice'],
                                'only_random_group_has_optional_other_exploration_input')
                        require(panel.related.count() == len(group['initial_ids']), 'every_group_reverse_count_matches_exact_sources')
                        unknowns(value); observations.append({'kind': 'group', 'id': group['id'], 'row': group,
                                                             'actual_unlocked': value['actual_unlocked']})
                        if group['id'] in model.FIXED:
                            professions = model.FIXED[group['id']][1]
                            require(all(p + '招募券×1' in text for p in professions)
                                    and '未把列示先后当实际出券顺序' in text,
                                    'all5_fixed_group_professions_are_composition_not_ticket_order')
                            if group['id'] == 'recruit_group_1': shot('fixed-professions')
                        elif group['random_choice']:
                            choose(panel.other_exploration, True); value = panel.selected_result; unknowns(value)
                            require(value['listed_unlock_description_matches'] is True and '进行一次探索' in panel.player.toPlainText()
                                    and '不会三张同职业' in text and '不等于“三张职业都不同”' in text,
                                    'random_unlock_statement_does_not_require_clear_or_imply_three_distinct_professions')
                            require(value['row']['guaranteed_temporary_rarity_reference'] == 5
                                    and value['row']['slots_reference'][0]['professions'] is None
                                    and value['data']['source_scope']['generic_four_star_applied_to_current_theme'] is False
                                    and '通用' in text and '4星' in text and '5星' in text,
                                    'current_five_star_and_separate_generic_four_star_sources_not_mixed')
                            shot('random-guarantee')
                            choose(panel.other_exploration, False)
                            require(panel.selected_result['listed_unlock_description_matches'] is False
                                    and panel.selected_result['actual_unlocked'] is None,
                                    'false_manual_unlock_statement_is_not_actual_account_state')
                            choose(panel.other_exploration, None)
                        else:
                            require(group['ticket_count_reference'] == 2 and group['guaranteed_temporary_rarity_reference'] is None
                                    and group['slots_reference'] == [] and '不能套入5星保证' in text,
                                    'all8_support_definitions_do_not_inherit_normal_random_guarantees')
                            if group['scope'] == 'unlinked':
                                require(group['initial_ids'] == [] and panel.related.count() == 0
                                        and not panel.open_related_button.isEnabled() and '不按编号补成未来月份' in text,
                                        'all4_unlinked_definitions_have_no_guessed_future_month_or_menu')
                    choose(panel.scope, 'unlinked'); select_list(panel.entries, next(r['id'] for r in groups if r['scope'] == 'unlinked'))
                    shot('unlinked-definition'); choose(panel.scope, 'all')
                    panel.search.setText('随心所欲'); gui.processEvents(); require(panel.entries.count() == 1,
                                                                                'actual_group_search_filters_exact_named_combination')
                    select_list(panel.entries, model.RANDOM); choose(panel.other_exploration, True)
                    source_target = panel.selected_target(); previous = deepcopy(panel.selected_result)
                    require(panel.open_related({'kind': 'group', 'key': 'recruit_group_1'}) is False
                            and panel.selected_result == previous and panel.selected_target() == source_target,
                            'forged_non_associated_group_link_does_not_navigate_or_erase_valid_document')
                    related_key = panel.related.item(8).data(Qt.ItemDataRole.UserRole); select_list(panel.related, related_key)
                    require(panel.related.verticalScrollBar().value() > 0, 'actual_related_selection_has_nonzero_list_scroll')
                    dialog.resize(740, 470); gui.processEvents()
                    for reader in (panel.player, panel.technical):
                        panel.tabs.setCurrentWidget(reader); gui.processEvents(); cursor = reader.textCursor()
                        cursor.setPosition(3); cursor.setPosition(15, QTextCursor.MoveMode.KeepAnchor); reader.setTextCursor(cursor)
                        scroll = reader.verticalScrollBar(); require(scroll.maximum() > 0, 'both_recruit_readers_have_real_nonzero_range')
                        scroll.setValue(min(3, scroll.maximum())); prior = reading(reader); view = declared_view(); tab = panel.tabs.currentIndex()
                        require(prior['scroll'] > 0 and prior['position'] > prior['anchor'],
                                'both_readers_actual_nonzero_scroll_and_text_selection')
                        require(main_panel.refresh_reference(), 'actual_ordinary_parent_refresh'); gui.processEvents()
                        require(reading(reader) == prior and declared_view() == view and panel.tabs.currentIndex() == tab,
                                'parent_refresh_preserves_both_nonzero_readers_filter_target_declaration_related_and_tab')
                        refreshes.append({'before': prior, 'after': reading(reader), 'view': view})
                    dialog.resize(1080, 880); gui.processEvents(); panel.search.clear(); gui.processEvents()
                    select_list(panel.entries, 'recruit_group_1')
                    require(panel.declaration_row.isHidden() and panel.other_exploration.currentData() is None,
                            'changing_group_clears_and_hides_foreign_random_only_declaration')
                    normal = next(r for r in initial if r['scope'] == 'normal' and r['original']['modeGrade'] == 0)
                    monthly = [r for r in initial if r['scope'] == 'monthly']
                    require(len(monthly) == 4 and all(r['original']['modeGrade'] == 0 for r in monthly)
                            and len({r['original']['predefinedId'] for r in monthly}) == 4,
                            'all4_same_grade_zero_monthly_configurations_keep_distinct_original_predefined_IDs')
                    for number, config in enumerate((normal, monthly[0], monthly[1])):
                        dialog = reverse(config['id'])
                        require(panel.selected_result['row'] == config and panel.related.count() == (6 if number == 0 else 1),
                                'ordinary_normal_and_two_monthly_entries_show_only_their_exact_combinations')
                        require(panel.declaration_row.isHidden() and panel.other_exploration.currentData() is None,
                                'reverse_initial_does_not_assign_random_unlock_declaration')
                        observations.append({'kind': 'ordinary_reverse', 'original_key': config['id'], 'selected': panel.selected_target()})
                        if number: shot('monthly-' + str(number))
                        target = panel.related.item(0).data(Qt.ItemDataRole.UserRole)
                        open_related(target); open_related({'kind': 'initial', 'key': config['id']})
                    damaged = temporary / 'damaged-public'; manifest = json.loads((ROOT / model.MANIFEST).read_bytes())
                    for name in (model.MANIFEST, *manifest['files']):
                        path = damaged / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes((ROOT / name).read_bytes())
                    bad = damaged / model.DATA; original_bytes = bad.read_bytes(); original_file = model._file
                    def own_file(name):
                        return damaged / name if name == model.MANIFEST or name in manifest['files'] else original_file(name)
                    with patch.object(model, '_file', side_effect=own_file):
                        bad.write_bytes(original_bytes + b'x')
                        require(main_panel.refresh_reference(), 'ordinary_parent_version_remains_valid_on364_own_data_damage')
                        gui.processEvents()
                        require(panel.result is None and panel.selected_result is None and panel.entries.count() == 0
                                and panel.related.count() == 0 and panel.player.toPlainText() == model.UNAVAILABLE
                                and panel.technical.toPlainText() == '', 'actual364_member_damage_clears_all_old_entries_details_and_relations')
                        require(panel.declaration_row.isHidden() and panel.other_exploration.currentData() is None
                                and not panel.open_related_button.isEnabled(), 'bad_source_removes_specific_declarations_and_stale_navigation')
                        shot('source-loss'); bad.write_bytes(original_bytes)
                        require(main_panel.refresh_reference(), 'actual_parent_recovery_refresh'); gui.processEvents()
                        require(panel.result is not None and panel.selected_result is None and panel.selected_target() is None
                                and panel.other_exploration.currentData() is None, 'restored_source_requires_manual_initial_or_group_selection')
                    old_dialog = dialog; old_panel = panel
                    select_list(main_panel.entries, normal['id'])
                    require(not old_dialog.isVisible() and old_panel.result is None and old_panel.entries.count() == 0,
                            'changing_parent_initial_original_closes_and_clears_owned_recruit_tree')
                    dialog = reverse(normal['id']); old_dialog = dialog; old_panel = panel
                    main_panel.entries.setCurrentRow(-1); gui.processEvents()
                    require(main_panel.initial_recruits_item_button.isHidden() and not old_dialog.isVisible()
                            and old_panel.result is None, 'parent_deselection_hides_specific_entry_and_clears_owned_dialog')
                    dialog = reverse(normal['id']); old_dialog = dialog; old_panel = panel
                    window.reference_panel('stages'); gui.processEvents()
                    require(not old_dialog.isVisible() and old_panel.result is None and old_panel.related.count() == 0,
                            'changing_common_page_closes_and_clears_recruitment_subtree')
                    dialog = reverse(monthly[1]['id']); final_panel = panel
                    require(window.run.state == state and window.battle_preview.context == context,
                            'temporary_run_and_old_battle_context_unchanged')
                    require(all(v == 0 for v in calls.values()) and not window.auto.isChecked(),
                            'all_seven_real_external_operations_zero'); native()
                    window.close(); gui.processEvents()
                    require(not dialog.isVisible() and final_panel.result is None and final_panel.entries.count() == 0
                            and final_panel.related.count() == 0, 'actual_MainWindow_closes_and_clears_complete_recruitment_tree')
                    require(sum(r['kind'] == 'initial' for r in observations) == 21
                            and sum(r['kind'] == 'group' for r in observations) == 14
                            and sum(r['kind'] == 'association_round_trip' for r in observations) == 106
                            and sum(r['kind'] == 'ordinary_reverse' for r in observations) == 3,
                            'all21configs14groups106_roundtrips_and3ordinary_reverse_entries_actually_exercised')
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
    result = {'section': 364, 'passed': done and failure is None and exitcode == 0 and before == after,
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
