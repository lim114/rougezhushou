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
    names={p.relative_to(ROOT).as_posix()for p in(ROOT/'rouge').glob('*.py')}
    from rouge import current_route_itinerary as model,expansion_reference as version,current_battle_reference as battle,current_stage_directory as directory,current_enemy_stage_index as index,current_map_position as positions
    for provider in(model,version,battle,directory,index,positions):
        names.add(provider.MANIFEST);names.update(json.loads((ROOT/provider.MANIFEST).read_bytes())['files'])
    names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'rouge/data/battle-maps').glob('*.png'))
    for folder in('current-enemies','portraits'):names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'rouge/data'/folder).glob('*.png'))
    names.update(('scripts/verify_current_route_itinerary_window_375.py','scripts/build_current_route_itinerary_375.py','scripts/verify_full_available.py','tests/test_current_route_itinerary_375.py','tests/test_current_route_itinerary_view_375.py'))
    return {n:sha256((ROOT/n).read_bytes()).hexdigest()for n in sorted(names)}


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
        from rouge import app as app_module, current_route_itinerary as model
        from rouge import current_battle_reference as battle_model
        gui = QApplication([]); require(gui.platformName() == 'windows', 'actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge375-public-') as folder, ExitStack() as stack:
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
            window.setWindowTitle('第375节 · 完整敌人行程与等待条件（公开隔离验收）')
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


            def exercise():
                nonlocal done,failure,full_scope
                dialog=None
                try:
                    common=window.reference_panel('stages');gui.processEvents();click(common.enemy_directory_button);directory=common.enemy_directory_dialog;ip=directory.panel
                    def open_stage(sid):
                        row=next(r for r in ip.reference['data']['rows']if r['stage_id']==sid and r['enemy_key']=='0');ip.search.setText(row['name']);gui.processEvents();item=next(ip.entries.item(i)for i in range(ip.entries.count())if tuple(ip.entries.item(i).data(Qt.ItemDataRole.UserRole))==(sid,'0'));ip.entries.scrollToItem(item);gui.processEvents();QTest.mouseClick(ip.entries.viewport(),Qt.MouseButton.LeftButton,pos=ip.entries.visualItemRect(item).center());gui.processEvents();click(ip.open_button);child=ip.battle_dialog;parent=child.panel;parent.tabs.setCurrentIndex(2);gui.processEvents();require(parent.stage_id==sid,'ordinary_directory_opens_exact_stage_configuration');click(parent.route_itinerary_button);dialog=parent.route_itinerary_dialog;require(dialog.isVisible()and dialog.panel.result is not None,'ordinary_battle_opens_owned_complete_itinerary');return child,parent,dialog,dialog.panel
                    def route(panel,key):
                        idx=panel.entries.findData(key);require(idx>0,'exact_original_route_selector_exists');panel.entries.setCurrentIndex(idx);gui.processEvents();require(panel.selected_route()['key']==key,'actual_exact_original_route_selected')
                    def step(panel,kind):
                        selected=next(s for s in panel.selected_route()['steps']if s['kind']==kind);choose(panel.steps,selected['key']);require(panel.selected_step()['kind']==kind,'actual_exact_checkpoint_kind_selected');return selected
                    child,parent,dialog,panel=open_stage('ro6_n_1_3');require(panel.selected_route()is None and panel.selected_step()is None and not panel.action_button.isEnabled()and not panel.position_button.isEnabled(),'complete_itinerary_initial_scope_unselected');shot('ordinary-stage-itinerary-entry',parent)
                    route(panel,'$.routes[10]');selected=panel.selected_route();require(len(selected['steps'])==len(selected['raw']['checkpoints'])+2,'complete_selected_original_checkpoint_order_includes_birth_and_end');require([p['raw']for p in selected['steps'][1:-1]]==selected['raw']['checkpoints'],'every_selected_checkpoint_keeps_original_order_and_raw_data');require('不是实际采用条数'in panel.player.toPlainText()and'不按直线连接格子'in panel.player.toPlainText(),'default_player_distinguishes_original_itinerary_from_actual_path');shot('complete-original-itinerary',panel)
                    disappear=step(panel,'DISAPPEAR');require(not panel.position_button.isEnabled()and disappear['cell']is None,'disappear_placeholder_never_enables_map');require('占位坐标不画到地图'in panel.player.toPlainText(),'disappear_gap_has_readable_no_connection_boundary');shot('disappear-gap-not-a-route-line',panel)
                    appear=step(panel,'APPEAR_AT_POS');require(panel.position_button.isEnabled(),'explicit_reappearance_nominal_cell_has_map_entry');click(panel.position_button);map_dialog=panel.position_dialog;require(map_dialog.isVisible()and map_dialog.panel.result['route']['key']=='$.routes[10]'and map_dialog.panel.result['step']['key']==appear['key'],'map_uses_exact_selected_reappearance_step');require(map_dialog.panel.result['actual_path']is None and map_dialog.panel.result['actual_time']is None,'no_live_path_or_clock_in_map_reference');shot('exact-reappearance-step-map',map_dialog.panel)
                    wait=step(panel,'WAIT_FOR_SECONDS');require(not panel.position_button.isEnabled()and wait['cell']is None and not map_dialog.isVisible()and map_dialog.panel.result is None,'selecting_wait_clears_old_map_and_rejects_placeholder_point');require('不是开场后的时刻'in panel.player.toPlainText(),'wait_duration_not_displayed_as_absolute_time')
                    choose(panel.actions,'10');click(panel.action_button);require(parent.action_key=='10'and parent.queue_kind.currentData()=='main','bound_base_route_jumps_exact_original_main_spawn');jumps.append({'stage_id':parent.stage_id,'route_key':panel.entries.currentData(),'action_key':'10','association':'exact_main_base_route'})
                    dialog.resize(1100,560);panel.player.setMaximumHeight(140);panel.technical.setMaximumHeight(140);gui.processEvents()
                    for reader in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();c=reader.textCursor();c.setPosition(13);c.setPosition(36,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);gui.processEvents();require(reader.verticalScrollBar().maximum()>0,'actual_test_viewport_has_nonzero_reading_range');reader.verticalScrollBar().setValue(min(5,reader.verticalScrollBar().maximum()));prior=reading(reader);tab=panel.tabs.currentIndex();require(prior['scroll']>0 and prior['anchor']!=prior['position'],'actual_nonzero_reading_selection_recorded');require(parent.refresh_reference(),'true_parent_refresh_success');gui.processEvents();require(dialog.isVisible()and panel.entries.currentData()=='$.routes[10]'and panel.steps.currentData()==wait['key']and panel.actions.currentData()=='10'and panel.tabs.currentIndex()==tab and reading(reader)==prior,'true_parent_preserves_exact_route_step_action_filter_tab_two_readings');refreshes.append({'reader':'player'if reader is panel.player else'technical','before':prior,'after':reading(reader),'route_key':'$.routes[10]','step_key':wait['key'],'action_key':'10'})
                    old=dialog;oldpanel=panel;child,parent,dialog,panel=open_stage('ro6_n_1_4');require(not old.isVisible()and oldpanel.result is None,'exact_stage_change_closes_old_complete_itinerary');route(panel,'$.routes[10]');fragment=step(panel,'WAIT_CURRENT_FRAGMENT_TIME');require('15秒'in panel.player.toPlainText()and'不能与路程耗时或其它等待直接相加'in panel.player.toPlainText(),'fragment_wait_parameter_never_summed_with_travel_or_other_waits');require(not panel.position_button.isEnabled(),'fragment_wait_placeholder_cannot_open_map');shot('fragment-clock-wait-boundary',panel)
                    child,parent,dialog,panel=open_stage('ro6_n_1_3');choose(panel.scope,'extra');route(panel,'$.extraRoutes[0]');require(panel.selected_route()['actions']==[]and not panel.action_button.isEnabled(),'extra_route_does_not_borrow_equal_main_or_branch_index');require('没有按相同编号借用出怪记录'in panel.player.toPlainText(),'extra_route_actual_selection_boundary_readable');require(panel.unassigned.count()>1,'actual_unassigned_spawn_records_retained');panel.unassigned.setCurrentIndex(1);gui.processEvents();action=panel.selected_action();require(panel.selected_route()is None and panel.selected_step()is None and action is not None,'unassigned_spawn_does_not_leave_old_extra_route_selected');require('没有把它归到任何基础或额外路线'in panel.player.toPlainText()and not panel.position_button.isEnabled(),'unassigned_spawn_does_not_claim_route_or_map');shot('extra-route-and-unbound-spawn',panel);click(panel.action_button);require(parent.action_key==action['key'],'unassigned_spawn_can_still_jump_exact_original_record');jumps.append({'stage_id':parent.stage_id,'route_key':None,'action_key':action['key'],'association':'unassigned_no_route_claim'})
                    choose(panel.scope,None);route(panel,'$.routes[10]');step(panel,'START');click(panel.position_button);map_dialog=panel.position_dialog;original=battle_model.version._file;damaged=temporary/'damaged-route-manifest.json';raw=original(model.MANIFEST).read_bytes();damaged.write_bytes(raw+b'x')
                    with patch.object(battle_model.version,'_file',side_effect=lambda n:damaged if n==model.MANIFEST else original(n)):
                        require(parent.refresh_reference(),'ordinary_battle_survives_itinerary_source_loss');gui.processEvents();require(panel.result is None and panel.technical.toPlainText()==''and panel.player.toPlainText()==model.UNAVAILABLE and not panel.action_button.isEnabled()and not panel.position_button.isEnabled(),'actual_bad_source_clears_all_itinerary_readers_selections_jumps');require(not map_dialog.isVisible()and map_dialog.panel.result is None and map_dialog.panel.image_raw is None,'source_loss_clears_actual_owned_map_grid_and_image');shot('source-loss',panel);damaged.write_bytes(raw);require(panel.refresh_reference(),'repaired_public_source_refetches');require(panel.selected_route()is None and panel.selected_step()is None and panel.selected_action()is None and panel.position_dialog is None,'source_recovery_requires_manual_reselection')
                    route(panel,'$.routes[10]');step(panel,'START');panel.result['stage_name']='forged';require(not panel.open_position()and panel.result is None,'forged_same_stage_itinerary_cannot_open_map');require(panel.refresh_reference(),'refetch_after_forgery');route(panel,'$.routes[10]');step(panel,'START');click(panel.position_button);map_dialog=panel.position_dialog;QTest.keyClick(dialog,Qt.Key.Key_Escape);gui.processEvents();require(not dialog.isVisible()and panel.result is None and not map_dialog.isVisible()and map_dialog.panel.result is None,'Escape_clears_itinerary_and_map_actual_data')
                    parent.tabs.setCurrentIndex(2);click(parent.route_itinerary_button);dialog=parent.route_itinerary_dialog;panel=dialog.panel;route(panel,'$.routes[10]');step(panel,'START');click(panel.position_button);map_dialog=panel.position_dialog;dialog.close();gui.processEvents();require(panel.result is None and not map_dialog.isVisible()and map_dialog.panel.result is None,'direct_X_clears_itinerary_and_map_actual_data')
                    current=battle_model.packet();inventory=model.packet()['inventory'];total=0
                    for sid,entry in inventory['stages'].items():
                        level=current['inputs']['levels'][entry['level_key']];expected=[(f'$.{field}[{i}]',scope,len(r.get('checkpoints')or[]))for scope,field in(('base','routes'),('extra','extraRoutes'))for i,r in enumerate(level.get(field)or[])];require([(r['key'],r['scope'],r['checkpoint_count'])for r in entry['routes']]==expected,'all_original_base_extra_route_positions_and_checkpoint_counts_match');total+=len(expected)
                    counts=inventory['counts'];require(counts=={'base':8773,'checkpoints':40695,'main_bound_spawn_records':7042,'route_unassigned_spawn_records':654,'extra':667,'stages':184,'routes':9440,'steps':59575}and total==9440,'complete_current_route_and_action_partition_scope');full_scope={**counts,'checkpoint_types':inventory['checkpoint_types'],'all9440_windows_opened':False,'actual_route_selection_or_global_clock_verified':False}
                    parent.tabs.setCurrentIndex(2);click(parent.route_itinerary_button);dialog=parent.route_itinerary_dialog;panel=dialog.panel;route(panel,'$.routes[10]');step(panel,'START');click(panel.position_button);map_dialog=panel.position_dialog;window.reference_panel('squads');gui.processEvents();require(not dialog.isVisible()and panel.result is None and not map_dialog.isVisible()and map_dialog.panel.result is None,'ordinary_page_switch_clears_owned_itinerary_tree');common=window.reference_panel('stages');gui.processEvents();click(common.enemy_directory_button);directory=common.enemy_directory_dialog;ip=directory.panel;child,parent,dialog,panel=open_stage('ro6_n_1_3');route(panel,'$.routes[10]');step(panel,'START');click(panel.position_button);map_dialog=panel.position_dialog;require(window.run.state==state and window.battle_preview.context==context,'temporary_run_and_old_calculation_context_unchanged');require(all(v==0 for v in calls.values())and not window.auto.isChecked(),'all_seven_real_external_operations_zero');require(len(images)==7,'seven_actual_native_screenshots_recorded');native(window);window.close();gui.processEvents();require(not dialog.isVisible()and panel.result is None and not map_dialog.isVisible()and map_dialog.panel.result is None,'actual_MainWindow_close_clears_live_itinerary_and_map_tree');done=True;gui.exit(0)
                except BaseException as error:
                    failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
                    if dialog is not None:dialog.close()
                    window.close();gui.exit(1)

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
    result = {'section': 375, 'passed': done and failure is None and exitcode == 0 and bool(before) and before == after,
              'failure': failure, 'process_id': os.getpid(), 'qpa': gui.platformName() if gui else None,
              'qt_exit_code': exitcode, 'configured_visible_ms': args.visible_ms,
              'verification_window_closed': window is not None and not window.isVisible(),
              'unique_checks': len(checks), 'checks': checks, 'full_original_reference_scope': full_scope,
              'all184_original_stage_counts': original_counts, 'actual_filter_observations': filters,
              'representative_exact_window_jumps': jumps, 'all9440_windows_claimed_open': False,
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
