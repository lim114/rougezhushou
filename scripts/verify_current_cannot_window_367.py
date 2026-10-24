"""Native shop/enemy/vault entry exercise; cache preparation is not execution."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
from tempfile import TemporaryDirectory
from contextlib import ExitStack
from unittest.mock import patch
from copy import deepcopy
import argparse, json, os, sys, traceback

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def bound_files():
    names = {p.relative_to(ROOT).as_posix() for p in (ROOT / 'rouge').glob('*.py')}
    from rouge import current_cannot_reference as model, expansion_reference as version
    from rouge import current_battle_reference as battle, current_reward_reference as rewards
    from rouge import current_map_position as positions
    for provider in (model, version, battle, rewards, positions):
        names.add(provider.MANIFEST)
        names.update(json.loads((ROOT / provider.MANIFEST).read_bytes())['files'])
    names.update(('scripts/verify_current_cannot_window_367.py',
                  'scripts/build_current_cannot_367.py', 'scripts/verify_full_available.py',
                  'tests/test_current_cannot_367.py', 'tests/test_current_cannot_view_367.py'))
    return {name: sha256((ROOT / name).read_bytes()).hexdigest() for name in sorted(names)}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--receipt', type=Path, required=True)
    parser.add_argument('--visible-ms', type=int, default=120000)
    args = parser.parse_args(); dest = args.receipt.resolve()
    if dest.exists(): raise FileExistsError('Never overwrite actual native evidence')
    dest.parent.mkdir(parents=True, exist_ok=True)
    checks, images, enemy_reads, vault_reads, branch_reads, links, refreshes, node_reads = [], [], [], [], [], [], [], []
    calls = {k: 0 for k in ('game_connect', 'capture', 'next_frame', 'desktop_start',
                            'desktop_request', 'provider_chat', 'credential_read')}
    before = {}; after = {}; failure = None; window = None; gui = None; exitcode = None; done = False

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
        from rouge import app as app_module, current_cannot_reference as model
        gui = QApplication([]); require(gui.platformName() == 'windows', 'actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge367-public-') as folder, ExitStack() as stack:
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
            window.setWindowTitle('第367节 · 坎诺特与保险柜（公开隔离验收）')
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

            def select(widget, identity):
                item = next((widget.item(i) for i in range(widget.count())
                             if widget.item(i).data(Qt.ItemDataRole.UserRole) == identity), None)
                require(item is not None, 'exact_original_id_list_item_exists')
                widget.scrollToItem(item); gui.processEvents()
                QTest.mouseClick(widget.viewport(), Qt.MouseButton.LeftButton, pos=widget.visualItemRect(item).center())
                gui.processEvents()
                require(widget.currentItem() is not None and widget.currentItem().data(Qt.ItemDataRole.UserRole) == identity,
                        'real_exact_item_mouse_selection')

            def click(button):
                require(button.isVisible() and button.isEnabled(), 'actual_usable_reference_button')
                QTest.mouseClick(button, Qt.MouseButton.LeftButton); gui.processEvents()

            def ordinary_battle(sid):
                common = window.reference_panel('stages'); gui.processEvents()
                require(tabs.currentWidget() is common and common.category.currentData() == 'stages',
                        'actual_ordinary_stage_page_opened')
                common.search.clear(); select(common.entries, sid); click(common.battle_button)
                battle = common.current_battle_dialog
                require(battle.isVisible() and battle.panel.stage_id == sid and battle.panel.result['id'] == sid,
                        'ordinary_exact_stage_native_preview')
                return common, battle, battle.panel

            def open_enemy(panel, key):
                panel.tabs.setCurrentIndex(1)
                require(panel.enemy_choices.select_value(key, emit=True), 'exact_original_enemy_branch_selected')
                gui.processEvents(); require(panel.enemy_key == key, 'enemy_source_key_not_name_or_index_alias')
                click(panel.shop_vault_button); dialog = panel.shop_vault_dialog
                require(dialog.isVisible(), 'ordinary_enemy_owned_mechanism_dialog_visible')
                return dialog, dialog.panel

            def open_vault(panel, key):
                panel.tabs.setCurrentWidget(panel.rewards)
                require(panel.rewards.choices.select_value(key, emit=True), 'exact_original_vault_reward_branch_selected')
                gui.processEvents(); require(panel.rewards.row_id == key, 'vault_original_source_selector_not_action_or_alias')
                click(panel.rewards.shop_vault_button); dialog = panel.rewards.shop_vault_dialog
                require(dialog.isVisible(), 'ordinary_reward_owned_mechanism_dialog_visible')
                return dialog, dialog.panel

            def actuals_unknown(panel):
                require(panel.result is not None and all(panel.result[k] is None for k in (
                        'actual_boss_present', 'actual_recovered_vaults', 'actual_opened_vaults', 'actual_free_slots',
                        'actual_goods', 'actual_gold_lost', 'actual_shop_eligible', 'actual_outcome', 'actual_initial_entry'))
                        and not panel.result['actual_server_verified'] and not panel.result['run_updated']
                        and not panel.result['numerical_combat_model_added'],
                        'actual_spawn_recovery_free_goods_gold_eligibility_unknown_no_execution_or_model')

            def open_related(panel, target):
                select(panel.related, target); click(panel.open_button); child = panel.battle_dialog
                require(child is not None and child.isVisible() and child.panel.stage_id == target['stage_id'],
                        'actual_owned_exact_current_battle_link')
                if target['enemy_key'] is not None:
                    require(child.panel.enemy_key == target['enemy_key'] and child.panel.tabs.currentIndex() == 1,
                            'related_current_battle_exact_enemy_selected')
                if target['reward_id'] is not None:
                    require(child.panel.rewards.row_id == target['reward_id'] and child.panel.tabs.currentWidget() is child.panel.rewards,
                            'related_current_battle_exact_original_vault_selected')
                links.append(deepcopy(target)); return child

            def node_entry(node_type):
                node = window.node_catalog; tabs.setCurrentWidget(node); node.show_directory()
                node.search.clear(); choose(node.kind, 'function'); choose(node.floor, None); choose(node.node_type, node_type)
                entry = next((e for e in node.entries if e['kind'] == 'function' and e['record']['node_type'] == node_type), None)
                require(entry is not None, 'actual_complete_node_function_entry_exists')
                index = next(i for i, e in enumerate(node.entries) if e['key'] == entry['key'])
                node.list.setCurrentRow(index); item = node.list.flat[index]; node.list.scrollToItem(item); gui.processEvents()
                QTest.mouseClick(node.list.viewport(), Qt.MouseButton.LeftButton, pos=node.list.visualItemRect(item).center()); gui.processEvents()
                require(node.list.selected_key() == entry['key'] and tabs.currentWidget() is node,
                        'ordinary_node_tree_complete_function_mouse_selected')
                return node, entry

            def exercise():
                nonlocal done, failure
                dialog = None
                try:
                    original = deepcopy(model.reference()['data'])
                    stages = original['stages']
                    require(set(stages) == set(model.STAGES) and [len(stages[s]['vaults']) for s in model.STAGES] == [7, 10],
                            'two_exact_stages_seventeen_predefined_records_not_actual_spawn_totals')
                    for sid in model.STAGES:
                        stage = stages[sid]; common, battle, bp = ordinary_battle(sid)
                        bp.tabs.setCurrentIndex(1); gui.processEvents()
                        require(bp.enemy_key is None and not bp.shop_vault_button.isVisible() and not bp.open_shop_vault(),
                                'enemy_overview_has_no_unqualified_mechanism_entry')
                        other = next((e['key'] for e in bp.result['enemies'] if e['key'] != stage['boss']['key']), None)
                        if other is not None:
                            require(bp.enemy_choices.select_value(other, emit=True), 'other_actual_enemy_selectable')
                            gui.processEvents(); require(not bp.shop_vault_button.isVisible() and not bp.open_shop_vault(),
                                                        'other_enemy_cannot_borrow_cannot_mechanism')
                        dialog, panel = open_enemy(bp, stage['boss']['key']); actuals_unknown(panel)
                        require(panel.target == {'kind': 'enemy', 'stage_id': sid, 'key': stage['boss']['key']}
                                and model.same(panel.result['selected'], stage['boss'])
                                and panel.result['stages'][0]['id'] == sid and not panel.floor_row.isVisible(),
                                'both_ordinary_enemy_entries_keep_exact_stage_reference_and_enabled_overrides')
                        text = panel.player.toPlainText()
                        require(stage['name'] in text and '不等于实际出现或成功领取数量' in text
                                and '60000' not in text and model.BOSS not in text and '$.predefines' not in text,
                                'ordinary_player_reading_has_chinese_scope_without_raw_health_or_keys')
                        enemy_reads.append({'stage_id': sid, 'enemy_key': stage['boss']['key'],
                                            'selected': deepcopy(panel.result['selected']), 'actual_panel_complete': False})
                        if sid == model.STAGES[0]:
                            shot('deadbox-exact-enemy', panel)
                            for branch in original['reading']:
                                choose(panel.topic, branch['id']); text = panel.player.toPlainText()
                                require(all(p in text for p in branch['paragraphs']), 'six_complete_documentary_branches_visible')
                                branch_reads.append({'topic': branch['id'], 'paragraph_count': len(branch['paragraphs'])})
                            choose(panel.topic, 'free'); text = panel.player.toPlainText()
                            require('数量和等级' in text and '每回收一个' in text and '最多5个' in text
                                    and '不能自动套到' in text and '具体商品仍未知' in text,
                                    'free_slot_documentary_scopes_separate_no_large_vault_boss_recovery_formula')
                            shot('free-paths-and-source-boundary', panel)
                        choose(panel.topic, None)
                        target = {'kind': 'battle', 'stage_id': sid, 'enemy_key': stage['boss']['key'], 'reward_id': None}
                        child = open_related(panel, target); previous = child
                        child = open_related(panel, target)
                        require(child is not previous and not previous.isVisible(), 'repeated_owned_current_preview_closes_previous')
                        choose(bp.enemy_combo, None)
                        require(not dialog.isVisible() and not child.isVisible() and not bp.shop_vault_button.isVisible(),
                                'ordinary_enemy_deselection_closes_mechanism_and_current_preview_tree')
                        bp.tabs.setCurrentWidget(bp.rewards); gui.processEvents()
                        require(bp.rewards.row_id is None and not bp.rewards.shop_vault_button.isVisible()
                                and not bp.rewards.open_shop_vault(), 'reward_overview_has_no_unqualified_mechanism_entry')
                        for vault in stage['vaults']:
                            dialog, panel = open_vault(bp, vault['key']); actuals_unknown(panel)
                            require(panel.target == {'kind': 'vault', 'stage_id': sid, 'key': vault['key']}
                                    and model.same(panel.result['selected'], vault)
                                    and panel.entries.currentData() == panel.target and not panel.floor_row.isVisible(),
                                    'all17_original_vault_records_grades_and_pickup_references_exact')
                            text = panel.player.toPlainText()
                            require(vault['label'] in text and f"对应{vault['pickup_free_slots_reference']}个零价格栏位" in text
                                    and '这不是实际已领取数量' in text and '不同路径、候选与说明不能相加为实收' in text,
                                    'all17_vault_pickup_references_not_actual_total_or_boss_recovery')
                            vault_reads.append({'stage_id': sid, 'reward_id': vault['key'], 'grade': vault['grade'],
                                                'pickup_free_slots_reference': vault['pickup_free_slots_reference'],
                                                'selected': deepcopy(panel.result['selected']), 'actual_free_slots': None})
                            representative = ((sid == model.STAGES[0] and vault['key'] in ('$.predefines.tokenInsts[0]', '$.predefines.tokenInsts[1]'))
                                              or (sid == model.STAGES[1] and vault['key'] == '$.predefines.tokenInsts[9]'))
                            if representative:
                                target = {'kind': 'battle', 'stage_id': sid, 'enemy_key': None, 'reward_id': vault['key']}
                                child = open_related(panel, target)
                                require(child.panel.rewards.row_id == vault['key'], 'three_representative_original_reward_round_trips')
                                choose(bp.rewards.combo, None)
                                require(not dialog.isVisible() and not child.isVisible()
                                        and not bp.rewards.shop_vault_button.isVisible() and not bp.rewards.open_shop_vault(),
                                        'ordinary_reward_deselection_closes_mechanism_and_current_preview_tree')
                                dialog, panel = open_vault(bp, vault['key'])
                                if sid == model.STAGES[0] and vault['grade'] == 2: shot('deadbox-large-vault', panel)
                                if sid == model.STAGES[1]: shot('livingwood-small-vault', panel)
                            dialog.close(); gui.processEvents()
                        battle.close(); gui.processEvents()
                    require(len(enemy_reads) == 2 and len(vault_reads) == 17 and len(branch_reads) == 6,
                            'all_current_exact_boss_vault_and_documentary_branches_exercised')

                    # Two nonzero readings and an owned preview through the real ordinary parent.
                    sid = model.STAGES[0]; vault = stages[sid]['vaults'][0]
                    common, battle, bp = ordinary_battle(sid); dialog, panel = open_vault(bp, vault['key'])
                    choose(panel.topic, 'free')
                    target = {'kind': 'battle', 'stage_id': sid, 'enemy_key': None, 'reward_id': vault['key']}
                    child = open_related(panel, target); dialog.resize(800, 500); gui.processEvents()
                    for reader in (panel.player, panel.technical):
                        panel.tabs.setCurrentWidget(reader); gui.processEvents(); cursor = reader.textCursor()
                        cursor.setPosition(4); cursor.setPosition(20, QTextCursor.MoveMode.KeepAnchor); reader.setTextCursor(cursor)
                        scroll = reader.verticalScrollBar(); require(scroll.maximum() > 0, 'two_actual_nonzero_reading_ranges')
                        scroll.setValue(min(4, scroll.maximum())); prior = reading(reader)
                        old_target, old_topic, old_tab = deepcopy(panel.target), panel.topic.currentData(), panel.tabs.currentIndex()
                        old_related = deepcopy(panel.related.currentItem().data(Qt.ItemDataRole.UserRole))
                        require(common.refresh_reference(), 'actual_ordinary_stage_parent_refresh'); gui.processEvents()
                        require(common.current_battle_dialog is battle and bp.rewards.shop_vault_dialog is dialog
                                and panel.target == old_target and panel.topic.currentData() == old_topic
                                and panel.tabs.currentIndex() == old_tab and reading(reader) == prior
                                and panel.related.currentItem().data(Qt.ItemDataRole.UserRole) == old_related
                                and child.isVisible() and child.panel.rewards.row_id == vault['key'],
                                'two_nonzero_readings_exact_target_branch_tab_link_and_child_survive_true_parent_refresh')
                        refreshes.append({'reader': 'player' if reader is panel.player else 'technical',
                                          'before': prior, 'after': reading(reader), 'target': old_target})
                    forged = dict(target, stage_id=model.STAGES[1])
                    require(not panel.open_link(forged) and panel.battle_dialog is child and child.isVisible(),
                            'forged_cross_stage_original_vault_link_refused_without_losing_valid_child')

                    damaged = temporary / 'damaged'; manifest = json.loads((model.ROOT / model.MANIFEST).read_bytes())
                    for name in (model.MANIFEST, *manifest['files']):
                        path = damaged / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_bytes((model.ROOT / name).read_bytes())
                    path = damaged / model.DATA; raw = path.read_bytes()
                    with patch.object(model, 'ROOT', damaged):
                        path.write_bytes(raw + b'x'); require(common.refresh_reference(), 'ordinary_stage_parent_survives_independent_source_loss')
                        gui.processEvents()
                        require(panel.result is None and panel.target == {'kind': 'shop', 'stage_id': None, 'key': None}
                                and panel.entries.count() == 0 and panel.related.count() == 0
                                and panel.player.toPlainText() == model.UNAVAILABLE and panel.technical.toPlainText() == ''
                                and not panel.open_button.isEnabled() and not child.isVisible()
                                and not bp.rewards.shop_vault_button.isVisible(),
                                'bad_source_clears_exact_target_readers_links_and_owned_preview')
                        shot('source-loss-cleared-ordinary-entry', bp)
                        path.write_bytes(raw)
                        require(panel.refresh_reference() and panel.target == {'kind': 'shop', 'stage_id': None, 'key': None}
                                and panel.result['selected'] is None and panel.entries.count() == 0 and panel.battle_dialog is None,
                                'explicit_source_recovery_returns_unselected_shop_not_old_vault')
                    dialog.close(); require(common.refresh_reference(), 'restored_ordinary_source_revalidated'); gui.processEvents()
                    require(not dialog.isVisible() and bp.rewards.shop_vault_button.isVisible(),
                            'source_recovery_keeps_closed_reader_closed_until_manual_reopen')
                    dialog, panel = open_vault(bp, vault['key'])
                    require(panel.result['selected'] == vault, 'manual_reopen_after_recovery_uses_current_exact_reward')
                    dialog.close(); battle.close(); gui.processEvents()

                    node, entry = node_entry('诡意行商')
                    require(model.shop_target(entry['record']) == {'kind': 'shop', 'stage_id': None, 'key': None},
                            'ordinary_complete_shop_function_original_admitted')
                    click(node.shop_vault_button); dialog = node.shop_vault_dialog; panel = dialog.panel
                    require(panel.target == {'kind': 'shop', 'stage_id': None, 'key': None} and panel.floor_row.isVisible()
                            and not panel.entries_row.isVisible(), 'actual_node_function_entry_opens_shop_scope')
                    for floor, expected in ((None, list(model.STAGES)), (3, [model.STAGES[0]]), (4, [model.STAGES[1]])):
                        choose(panel.floor, floor); actuals_unknown(panel)
                        require([s['id'] for s in panel.result['stages']] == expected and panel.result['floor_declared'] == floor,
                                'unknown_three_four_floor_documentary_candidates_not_server_eligibility')
                        node_reads.append({'node_key': entry['key'], 'floor': floor, 'stage_candidates': expected,
                                           'actual_eligible': None})
                    shot('shop-main-floor-four-boundary', panel)
                    choose(panel.floor, None); choose(panel.topic, 'entry')
                    text = panel.player.toPlainText()
                    require('最高投资额' in text and '累计投资' in text and '秘境行商' in text,
                            'shop_entry_investment_scope_and_secret_merchant_boundaries_retained')
                    node.refresh(); gui.processEvents()
                    require(node.shop_vault_dialog is dialog and panel.topic.currentData() == 'entry'
                            and panel.floor.currentData() is None, 'actual_node_parent_refresh_preserves_reader_manual_branch')
                    node, _ = node_entry('秘境行商')
                    require(not dialog.isVisible() and not node.shop_vault_button.isVisible() and not node.open_shop_vault(),
                            'secret_merchant_function_cannot_borrow_shop_challenge_and_closes_old_tree')

                    # Full owner chain, including a real current fixed-map child, closes from MainWindow.
                    node, entry = node_entry('诡意行商'); click(node.shop_vault_button)
                    dialog = node.shop_vault_dialog; panel = dialog.panel
                    target = {'kind': 'battle', 'stage_id': model.STAGES[1], 'enemy_key': None, 'reward_id': None}
                    child = open_related(panel, target)
                    click(child.panel.position_button); map_dialog = child.panel.position_dialog
                    require(map_dialog.isVisible(), 'actual_owned_current_fixed_map_child_opened')
                    shot('owned-current-fixed-map', map_dialog.panel)
                    require(window.run.state == state and window.battle_preview.context == context, 'temporary_run_and_old_calculation_context_unchanged')
                    require(all(v == 0 for v in calls.values()) and not window.auto.isChecked(), 'all_seven_real_external_operations_zero')
                    require(len(images) == 7, 'seven_actual_native_screenshots_recorded')
                    native(window); window.close(); gui.processEvents()
                    require(all(not d.isVisible() for d in (dialog, child, map_dialog)), 'actual_MainWindow_closes_node_reader_current_preview_map_tree')
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
    result = {'section': 367, 'passed': done and failure is None and exitcode == 0 and bool(before) and before == after,
              'failure': failure, 'process_id': os.getpid(), 'qpa': gui.platformName() if gui else None,
              'qt_exit_code': exitcode, 'configured_visible_ms': args.visible_ms,
              'verification_window_closed': window is not None and not window.isVisible(),
              'unique_checks': len(checks), 'checks': checks, 'exact_enemy_readings': enemy_reads,
              'all17_original_vault_readings': vault_reads, 'six_mechanism_branch_readings': branch_reads,
              'actual_current_preview_links': links, 'ordinary_shop_function_readings': node_reads,
              'same_identity_refresh_observations': refreshes, 'screenshots': images,
              'source_sha256_before': before, 'source_sha256_after': after,
              'source_scope_selected_not_all_transitive_dependencies': True,
              'external_operation_attempts': calls, 'temporary_state': True,
              'private_contents_read_copied_or_restored': False, 'game_operated': False, 'chat_sent': False,
              'current_server_or_original_runtime_validated': False,
              'original_predefined_records_not_actual_spawn_or_reward_totals': True,
              'unattended_shop_event_adapter_not_claimed': True,
              'at_utc': datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
    print(json.dumps({'passed': result['passed'], 'checks': len(checks), 'failure': failure}, ensure_ascii=False))
    return 0 if result['passed'] else 1


if __name__ == '__main__': raise SystemExit(main())
