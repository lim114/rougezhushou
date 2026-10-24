"""Native ordinary-page enemy reverse index exercise; preparation is not execution."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
from tempfile import TemporaryDirectory
from contextlib import ExitStack
from unittest.mock import patch
from copy import deepcopy
from collections import Counter
import argparse, json, os, sys, traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def digest(value):
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf8')).hexdigest()


def bound_files():
    names = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'rouge').glob('*.py')}
    from rouge import current_enemy_stage_index as model, expansion_reference as version
    from rouge import current_battle_reference as battle, current_stage_directory as directory
    from rouge import current_map_position as positions
    for provider in (model, version, battle, directory, positions):
        names.add(provider.MANIFEST)
        names.update(json.loads((ROOT / provider.MANIFEST).read_bytes())['files'])
    data = json.loads((ROOT / model.DATA).read_bytes())
    names.update(r['portrait']['file'] for r in data['rows'] if r['portrait'] is not None)
    maps = json.loads((ROOT / 'research/p3-expansion-313/map-images.json').read_bytes())['images']
    names.update(maps[sid]['file'] for sid in ('ro6_duel_1', 'ro6_duel_2', 'ro6_n_2_3', 'ro6_b_4_b', 'ro6_t_6', 'ro6_t_7'))
    names.update(('scripts/verify_current_enemy_stage_index_window_370.py',
                  'scripts/build_current_enemy_stage_index_370.py', 'scripts/verify_full_available.py',
                  'tests/test_current_enemy_stage_index_370.py', 'tests/test_current_enemy_stage_index_view_370.py'))
    return {name: sha256((ROOT / name).read_bytes()).hexdigest() for name in sorted(names)}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--receipt', type=Path, required=True)
    parser.add_argument('--visible-ms', type=int, default=120000)
    args = parser.parse_args(); dest = args.receipt.resolve()
    if dest.exists(): raise FileExistsError('Never overwrite actual native evidence')
    dest.parent.mkdir(parents=True, exist_ok=True)
    checks, images, filters, jumps, refreshes, original_counts = [], [], [], [], [], []
    calls = {k: 0 for k in ('game_connect', 'capture', 'next_frame', 'desktop_start',
                            'desktop_request', 'provider_chat', 'credential_read')}
    before = {}; after = {}; failure = None; window = None; gui = None; exitcode = None; done = False
    full_scope = {}

    def require(value, name):
        if not value: raise AssertionError(name)
        if name not in checks: checks.append(name)

    def forbidden(name):
        def fail(*args, **kwargs):
            calls[name] += 1; raise AssertionError('Forbidden real operation: ' + name)
        return fail

    try:
        before = bound_files()
        if sys.platform != 'win32': raise RuntimeError('Actual Windows required')
        import win32gui, win32process
        from PySide6.QtCore import Qt, QTimer
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QApplication
        from PySide6.QtTest import QTest
        from rouge import app as app_module, current_enemy_stage_index as model
        from rouge import current_battle_reference as battle_model
        gui = QApplication([]); require(gui.platformName() == 'windows', 'actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge370-public-') as folder, ExitStack() as stack:
            temporary = Path(folder)
            for name, value in {'ROOT': temporary, 'SETTINGS': temporary / 'settings.json',
                                'OPERATOR_STATE': temporary / 'operators.json', 'RUN_STATE': temporary / 'run.json'}.items():
                stack.enter_context(patch.object(app_module, name, value))
            backend = app_module.DesktopBackend
            stack.enter_context(patch.object(app_module, 'DesktopBackend',
                lambda _path, callback: backend(temporary / 'chat', callback)))
            stack.enter_context(patch.object(app_module, 'list_game_windows', return_value=[]))
            for name, key in (('connect', 'game_connect'), ('capture', 'capture'), ('next_frame', 'next_frame')):
                stack.enter_context(patch.object(app_module.GameCapture, name, side_effect=forbidden(key)))
            for name, key in (('start', 'desktop_start'), ('request', 'desktop_request')):
                stack.enter_context(patch.object(backend, name, side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module, 'stream_chat', side_effect=forbidden('provider_chat')))
            stack.enter_context(patch.object(app_module, 'read_key', side_effect=forbidden('credential_read')))
            window = app_module.MainWindow(); window.resize(1240, 880)
            window.setWindowTitle('第370节 · 按敌人查找关卡（公开隔离验收）')
            window.show(); gui.processEvents(); tabs = window.centralWidget()
            state = deepcopy(window.run.state); context = deepcopy(window.battle_preview.context)

            def native(widget):
                owner = widget.window(); hwnd = int(owner.winId()); pid = win32process.GetWindowThreadProcessId(hwnd)[1]
                require(win32gui.IsWindowVisible(hwnd) and not win32gui.IsIconic(hwnd) and pid == os.getpid(),
                        'visible_owned_native_HWND_PID')
                return {'hwnd': hwnd, 'pid': pid, 'size': [owner.width(), owner.height()]}

            def shot(label, widget):
                gui.processEvents(); path = dest.with_name('window-' + label + '.png')
                if path.exists(): raise FileExistsError('Never overwrite a native screenshot')
                require(widget.grab().save(str(path), 'PNG'), 'actual_widget_screenshot_saved')
                images.append({'name': label, 'path': str(path), 'sha256': sha256(path.read_bytes()).hexdigest(), 'native': native(widget)})

            def reading(widget):
                c = widget.textCursor()
                return {'anchor': c.anchor(), 'position': c.position(), 'selection': c.selectedText(),
                        'scroll': widget.verticalScrollBar().value()}

            def choose(combo, value):
                index = combo.findData(value); require(index >= 0, 'actual_filter_branch_value_exists')
                combo.setCurrentIndex(index); gui.processEvents()

            def click(button):
                require(button.isVisible() and button.isEnabled(), 'actual_usable_reference_button')
                QTest.mouseClick(button, Qt.MouseButton.LeftButton); gui.processEvents()

            def keys(panel):
                return [tuple(panel.entries.item(i).data(Qt.ItemDataRole.UserRole)) for i in range(panel.entries.count())]

            def select(panel, key):
                item = next((panel.entries.item(i) for i in range(panel.entries.count())
                             if tuple(panel.entries.item(i).data(Qt.ItemDataRole.UserRole)) == tuple(key)), None)
                require(item is not None, 'exact_original_stage_enemy_pair_exists_in_actual_list')
                panel.entries.scrollToItem(item); gui.processEvents()
                QTest.mouseClick(panel.entries.viewport(), Qt.MouseButton.LeftButton, pos=panel.entries.visualItemRect(item).center())
                gui.processEvents(); require(panel.selected_key == tuple(key), 'actual_mouse_selects_exact_stage_enemy_pair')

            def reset_filters(panel):
                panel.search.clear()
                for widget in (panel.tier, panel.scope, panel.floor, panel.kind): choose(widget, None)

            def lookup(panel, row):
                reset_filters(panel); panel.search.setText(row['name']); gui.processEvents()
                select(panel, (row['stage_id'], row['enemy_key']))
                require(model.same(panel.result['row'], row) and panel.result['actual_spawned'] is None
                        and panel.result['actual_count'] is None and panel.result['expected_stats'] is None
                        and not panel.result['run_updated'] and not panel.result['actual_server_verified'],
                        'representative_exact_row_keeps_actual_spawn_counts_and_final_stats_unknown')

            def open_exact(panel, row):
                click(panel.open_button); child = panel.battle_dialog
                require(child is not None and child.isVisible() and child.panel.stage_id == row['stage_id']
                        and child.panel.enemy_key == row['enemy_key'] and child.panel.tabs.currentIndex() == 1,
                        'actual_current_battle_opens_exact_stage_enemy_reference')
                selected = next(e for e in child.panel.result['enemies'] if e['key'] == row['enemy_key'])
                require(digest(selected['raw_binding']) == row['binding_sha256'] and selected['name'] == row['name']
                        and model.same(selected['portrait'], row['portrait']), 'opened_reference_binding_name_and_portrait_are_exact')
                require(row['name'] in child.panel.enemy_player.toPlainText(), 'actual_original_enemy_mechanism_page_visible')
                pix = child.panel.map_image.pixmap()
                require(pix is not None and not pix.isNull(), 'actual_exact_stage_fixed_map_image_loaded')
                jumps.append({'stage_id': row['stage_id'], 'enemy_key': row['enemy_key'], 'name': row['name'],
                              'binding_sha256': row['binding_sha256'], 'database_level': row['database_level'],
                              'tier': row['tier'], 'portrait_available': row['portrait'] is not None})
                return child

            def check_filter(panel, expected, label):
                actual = keys(panel); wanted = [(r['stage_id'], r['enemy_key']) for r in expected]
                require(actual == wanted, 'actual_filter_rows_match_exact_original_pairs_in_order')
                require(panel.result is None and panel.selected_key is None and not panel.open_button.isEnabled(),
                        'changed_filter_clears_old_selection_and_navigation')
                require('不是实际出场数量' in panel.count.text() and '不保证本局会出现' in panel.count.text(),
                        'filter_counts_explicitly_describe_references_not_actual_enemies')
                filters.append({'branch': label, 'rows': len(actual), 'stage_configurations': len({p[0] for p in actual}),
                                'exact_pair_order_sha256': digest(actual)})

            def ordinary():
                common = window.reference_panel('stages'); gui.processEvents()
                require(tabs.currentWidget() is common and common.category.currentData() == 'stages',
                        'actual_ordinary_current_stages_page_opened')
                click(common.enemy_directory_button); dialog = common.enemy_directory_dialog
                require(dialog.isVisible() and dialog.panel.reference is not None, 'ordinary_enemy_directory_owned_dialog_visible')
                return common, dialog, dialog.panel

            def exercise():
                nonlocal done, failure, full_scope
                dialog = None
                try:
                    common, dialog, panel = ordinary()
                    require(panel.entries.count() == 2060 and panel.result is None and panel.selected_key is None,
                            'ordinary_directory_all2060_unselected')
                    shot('ordinary-stage-entry', common)
                    previous = dialog; click(common.enemy_directory_button); dialog = common.enemy_directory_dialog; panel = dialog.panel
                    require(dialog is not previous and dialog.isVisible() and not previous.isVisible(),
                            'repeated_ordinary_entry_closes_previous_owned_directory')
                    reference = panel.reference; rows = deepcopy(reference['data']['rows']); stages = reference['data']['stages']
                    current = battle_model.packet(); expected = {}; expected_portraits = {}; checked_binding = []
                    for sid, stage in current['version']['current']['details']['stages'].items():
                        level = current['inputs']['levels']['levels/' + stage['levelId'].lower() + '.json']
                        original_counts.append({'stage_id': sid, 'original_enemyDbRefs': len(level['enemyDbRefs'])})
                        for index, raw in enumerate(level['enemyDbRefs']): expected[(sid, str(index))] = digest(raw)
                        for enemy in battle_model.enemy_records(level, current):
                            expected_portraits[(sid, enemy['key'])] = enemy['portrait']
                    require(len(stages) == len(original_counts) == 184 and len(rows) == len(expected) == 2060,
                            'actual_full184_original_configs_all2060_reference_records')
                    require(len(keys(panel)) == len(set(keys(panel))) and set(keys(panel)) == set(expected),
                            'actual_UI_list_complete_original_pair_bijection_no_name_merging')
                    for row in rows:
                        key = (row['stage_id'], row['enemy_key'])
                        require(row['binding_sha256'] == expected[key] and model.same(row['portrait'], expected_portraits[key]),
                                'all2060_exact_original_bindings_and_portrait_references_verified')
                        checked_binding.append([*key, row['binding_sha256']])
                    counts = Counter(r['tier'] or 'UNKNOWN' for r in rows)
                    require(counts == {'NORMAL': 508, 'ELITE': 1467, 'BOSS': 76, 'UNKNOWN': 9}, 'frozen_original_category_counts')
                    portrait_counts = Counter(r['portrait'] is not None for r in rows)
                    require(portrait_counts == {True: 2047, False: 13}, 'frozen_exact_portrait_available_missing_counts')
                    require(reference['actual_spawn_list'] is None and reference['actual_enemy_count'] is None
                            and not reference['actual_server_verified'] and not reference['run_updated'],
                            'directory_never_claims_actual_spawn_or_server_validation')
                    full_scope = {'stage_configurations': len(stages), 'reference_records': len(rows),
                                  'all_original_binding_pairs_sha256': digest(sorted(checked_binding)),
                                  'category_counts': dict(counts), 'exact_portraits': portrait_counts[True],
                                  'missing_portraits': portrait_counts[False], 'actual_enemy_count': None}
                    for tier, _ in model.TIERS[1:]:
                        choose(panel.tier, tier); check_filter(panel, [r for r in rows if (r['tier'] or 'UNKNOWN') == tier], 'tier:' + tier)
                    choose(panel.tier, None)
                    for floor, _ in model.directory.FLOORS[1:]:
                        choose(panel.floor, floor); check_filter(panel, [r for r in rows if stages[r['stage_id']]['floor'] == floor], 'floor:' + floor)
                    choose(panel.floor, None)
                    for kind, _ in model.directory.KINDS[1:]:
                        choose(panel.kind, kind); check_filter(panel, [r for r in rows if stages[r['stage_id']]['play_kind'] == kind], 'kind:' + kind)
                    choose(panel.kind, None)
                    choose(panel.scope, 'not_counted'); not_counted = [r for r in rows if r['not_counted'] is True]
                    check_filter(panel, not_counted, 'scope:not_counted')
                    independent = [r for r in rows if r['use_db'] is False]
                    require(len(not_counted) == 10 and {r['tier'] for r in not_counted} == {'NORMAL', 'ELITE'}
                            and len(independent) == 95 and any(r['tier'] == 'BOSS' for r in independent)
                            and not {(r['stage_id'], r['enemy_key']) for r in independent}.intersection(keys(panel)),
                            'not_counted_flag_not_useDb_false_or_invented_auxiliary_class')
                    sample_flag = next(r for r in not_counted if r['tier'] == 'ELITE')
                    select(panel, (sample_flag['stage_id'], sample_flag['enemy_key']))
                    require('不计入总敌人数' in panel.player.toPlainText() and '不证明它一定是辅助单位' in panel.player.toPlainText(),
                            'not_counted_keeps_elite_category_and_uncertain_entity_role')
                    shot('not-counted-original-tier', panel)
                    reset_filters(panel); panel.search.setText('  鸭爵  '); choose(panel.tier, 'ELITE')
                    choose(panel.floor, 'floor1'); choose(panel.kind, 'normal')
                    expected_search = [r for r in rows if '鸭爵' in r['name'] and r['tier'] == 'ELITE'
                                       and stages[r['stage_id']]['floor'] == 'floor1' and stages[r['stage_id']]['play_kind'] == 'normal']
                    check_filter(panel, expected_search, 'chinese:duck+elite+floor1+normal')
                    require(bool(expected_search), 'source_backed_chinese_intersection_nonempty')
                    select(panel, (expected_search[0]['stage_id'], expected_search[0]['enemy_key']))
                    pix = panel.portrait.pixmap(); require(pix is not None and not pix.isNull(), 'exact_portrait_actually_decoded_and_visible')
                    shot('chinese-intersecting-filters', panel)

                    # Representative real windows: same name/different database grade and same-stage independent references.
                    ducks = [r for r in rows if r['name'] == '鸭爵']; first = ducks[0]
                    second = next(r for r in ducks if r['database_level'] != first['database_level'])
                    for row in (first, second):
                        lookup(panel, row); require('不合并等级' in panel.player.toPlainText(), 'same_name_grades_not_merged_in_player_reading')
                        child = open_exact(panel, row); child.close(); gui.processEvents()
                    plants = [r for r in rows if r['stage_id'] == 'ro6_n_2_3' and r['name'] == '空植体']
                    require(len(plants) == 4 and len({r['binding_sha256'] for r in plants}) == 4, 'four_same_stage_same_name_originals_stay_distinct')
                    for row in plants[:2]:
                        lookup(panel, row); choose(panel.tier, 'UNKNOWN'); select(panel, (row['stage_id'], row['enemy_key']))
                        require('本关也有多个同名记录' in panel.player.toPlainText() and '本关独立配置' in panel.player.toPlainText()
                                and '尚未确认，不按普通敌人归类' in panel.player.toPlainText(),
                                'unknown_same_stage_independent_config_reading_not_forced_normal')
                        child = open_exact(panel, row); child.close(); gui.processEvents()
                    shot('same-name-unknown-exact-reference', panel)
                    missing = next(r for r in rows if r['name'] == '净浊之焰' and r['portrait'] is None)
                    lookup(panel, missing); require(panel.portrait.text() == '此精确引用未取得可核对的图片。'
                                                  and '不借用同名图' in panel.player.toPlainText(), 'missing_exact_image_stays_empty_without_alias_substitution')
                    shot('missing-exact-image', panel)
                    child = open_exact(panel, missing)
                    pix = child.panel.enemy_portrait.pixmap()
                    require(pix is None or pix.isNull(), 'actual_current_enemy_page_does_not_invent_missing_portrait')
                    child.close(); gui.processEvents()
                    bosses = [next(r for r in rows if (r['stage_id'], r['enemy_key']) == (sid, '0')) for sid in ('ro6_t_6', 'ro6_t_7')]
                    require('attributes.maxHp' in bosses[0]['enabled_override_paths'] and 'attributes.maxHp' not in bosses[1]['enabled_override_paths']
                            and bosses[0]['binding_sha256'] != bosses[1]['binding_sha256'], 'same_name_stage_override_binding_not_borrowed')
                    for row in bosses:
                        lookup(panel, row); require('60000' not in panel.player.toPlainText() and 'enemy_2153' not in panel.player.toPlainText(),
                                                   'player_output_keeps_raw_health_and_code_in_technical_details')
                        child = open_exact(panel, row); child.close(); gui.processEvents()

                    # Real ordinary-parent refresh, including a live exact child and two nonzero readings.
                    row = bosses[0]; lookup(panel, row); child = open_exact(panel, row)
                    previous = child; child = open_exact(panel, row)
                    require(child is not previous and not previous.isVisible(), 'repeated_exact_target_open_closes_old_current_preview')
                    dialog.resize(890, 475); gui.processEvents()
                    for reader in (panel.player, panel.technical):
                        panel.tabs.setCurrentWidget(reader); gui.processEvents(); cursor = reader.textCursor()
                        cursor.setPosition(4); cursor.setPosition(20, QTextCursor.MoveMode.KeepAnchor); reader.setTextCursor(cursor)
                        scroll = reader.verticalScrollBar(); require(scroll.maximum() > 0, 'two_actual_nonzero_reading_ranges')
                        scroll.setValue(min(3, scroll.maximum())); prior = reading(reader)
                        selected, tab = panel.selected_key, panel.tabs.currentIndex()
                        current_filters = (panel.search.text(), panel.tier.currentData(), panel.scope.currentData(), panel.floor.currentData(), panel.kind.currentData())
                        require(common.refresh_reference(), 'actual_ordinary_stage_parent_refresh'); gui.processEvents()
                        require(common.enemy_directory_dialog is dialog and panel.battle_dialog is child and child.isVisible()
                                and panel.selected_key == selected and panel.tabs.currentIndex() == tab and reading(reader) == prior
                                and current_filters == (panel.search.text(), panel.tier.currentData(), panel.scope.currentData(), panel.floor.currentData(), panel.kind.currentData())
                                and child.panel.enemy_key == row['enemy_key'] and child.panel.tabs.currentIndex() == 1,
                                'two_nonzero_readings_exact_filters_selection_tab_and_live_child_preserved_by_true_parent')
                        refreshes.append({'reader': 'player' if reader is panel.player else 'technical', 'before': prior,
                                          'after': reading(reader), 'selected': selected, 'filters': current_filters})
                    child.panel.tabs.setCurrentIndex(0); gui.processEvents(); shot('actual-exact-stage-fixed-map', child.panel)
                    child.panel.tabs.setCurrentIndex(1)
                    panel.search.setText('不存在的测试敌人'); gui.processEvents()
                    require(not child.isVisible() and panel.entries.count() == 0 and panel.result is None and not panel.open_button.isEnabled(),
                            'actual_changed_search_clears_old_reference_and_closes_current_preview')
                    lookup(panel, row); panel.result['row']['stage_id'] = 'ro6_t_7'
                    require(not panel.open_battle() and panel.result is None and panel.battle_dialog is None and panel.entries.count() == 0,
                            'forged_same_name_cross_stage_selection_refused_and_cleared')
                    require(panel.refresh_reference() and panel.result is None, 'explicit_refetch_after_forgery_requires_manual_selection')
                    lookup(panel, row); child = open_exact(panel, row)
                    damaged = temporary / 'damaged'; manifest = json.loads((model.ROOT / model.MANIFEST).read_bytes())
                    for name in (model.MANIFEST, *manifest['files']):
                        path = damaged / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes((model.ROOT / name).read_bytes())
                    path = damaged / model.DATA; raw = path.read_bytes()
                    with patch.object(model, 'ROOT', damaged):
                        path.write_bytes(raw + b'x'); require(common.refresh_reference(), 'ordinary_stage_parent_survives_enemy_index_source_loss')
                        gui.processEvents()
                        require(panel.reference is None and panel.result is None and panel.selected_key is None and panel.source_identity is None
                                and panel.entries.count() == 0 and panel.technical.toPlainText() == ''
                                and panel.player.toPlainText() == model.UNAVAILABLE and not panel.open_button.isEnabled() and not child.isVisible(),
                                'actual_bad_source_clears_directory_both_readers_selection_image_and_preview')
                        pix = panel.portrait.pixmap(); require((pix is None or pix.isNull()) and panel.portrait.text() == '', 'source_loss_clears_old_portrait')
                        shot('source-loss', panel if dialog.isVisible() else common)
                        path.write_bytes(raw)
                        require(panel.refresh_reference() and panel.result is None and panel.selected_key is None
                                and panel.entries.currentItem() is None and not panel.open_button.isEnabled() and panel.battle_dialog is None,
                                'repaired_public_source_requires_manual_reselection_no_old_child_restore')
                    dialog.close(); require(common.refresh_reference(), 'ordinary_source_recovery_revalidated'); gui.processEvents()
                    click(common.enemy_directory_button); dialog = common.enemy_directory_dialog; panel = dialog.panel
                    lookup(panel, row); child = open_exact(panel, row)
                    window.reference_panel('squads'); gui.processEvents()
                    require(not dialog.isVisible() and not child.isVisible(), 'ordinary_page_switch_closes_reverse_directory_and_current_preview')
                    common, dialog, panel = ordinary(); lookup(panel, row); child = open_exact(panel, row)
                    child.panel.tabs.setCurrentIndex(0); click(child.panel.position_button); map_dialog = child.panel.position_dialog
                    require(map_dialog.isVisible(), 'actual_current_map_grids_owned_child_visible')
                    require(window.run.state == state and window.battle_preview.context == context, 'temporary_run_and_old_calculation_context_unchanged')
                    require(all(v == 0 for v in calls.values()) and not window.auto.isChecked(), 'all_seven_real_external_operations_zero')
                    require(len(images) == 7, 'seven_actual_native_screenshots_recorded')
                    native(window); window.close(); gui.processEvents()
                    require(all(not d.isVisible() for d in (dialog, child, map_dialog)), 'actual_MainWindow_closes_directory_current_preview_map_tree')
                    done = True; gui.exit(0)
                except BaseException as error:
                    failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
                    if dialog is not None: dialog.close()
                    window.close(); gui.exit(1)

            def timeout():
                nonlocal failure
                if not done:
                    failure = failure or {'type': 'TimeoutError', 'message': f'Native exercise did not finish within configured {args.visible_ms} ms', 'traceback': None}
                    window.close(); gui.exit(2)

            QTimer.singleShot(250, exercise); QTimer.singleShot(args.visible_ms, timeout); exitcode = gui.exec()
            require(exitcode == 0 and done and not window.isVisible(), 'actual_Qt_success_and_owned_MainWindow_closed')
    except BaseException as error:
        if failure is None: failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
    finally:
        if window is not None: window.close()
    try:
        after = bound_files()
    except BaseException as error:
        if failure is None: failure = {'type': type(error).__name__, 'message': str(error), 'traceback': traceback.format_exc()}
    result = {'section': 370, 'passed': done and failure is None and exitcode == 0 and bool(before) and before == after,
              'failure': failure, 'process_id': os.getpid(), 'qpa': gui.platformName() if gui else None,
              'qt_exit_code': exitcode, 'configured_visible_ms': args.visible_ms,
              'verification_window_closed': window is not None and not window.isVisible(),
              'unique_checks': len(checks), 'checks': checks, 'full_original_reference_scope': full_scope,
              'all184_original_stage_counts': original_counts, 'actual_filter_observations': filters,
              'representative_exact_window_jumps': jumps, 'all2060_windows_claimed_open': False,
              'same_identity_refresh_observations': refreshes, 'screenshots': images,
              'source_sha256_before': before, 'source_sha256_after': after,
              'source_scope_selected_not_all_transitive_dependencies': True,
              'external_operation_attempts': calls, 'temporary_state': True,
              'private_contents_read_copied_or_restored': False, 'game_operated': False, 'chat_sent': False,
              'current_server_or_original_runtime_validated': False,
              'feature_section_published_or_completed_by_this_script': False,
              'batch_pause_state_changed_by_this_script': False,
              'at_utc': datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
    print(json.dumps({'passed': result['passed'], 'checks': len(checks), 'failure': failure}, ensure_ascii=False))
    return 0 if result['passed'] else 1


if __name__ == '__main__': raise SystemExit(main())
