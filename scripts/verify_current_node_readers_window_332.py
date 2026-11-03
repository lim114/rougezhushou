"""Actual native MainWindow update-reader exercise with temporary empty state."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
from tempfile import TemporaryDirectory
from contextlib import ExitStack
from unittest.mock import patch
from copy import deepcopy
import argparse,json,os,sys,traceback
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))

def bound_files():
    names={p.relative_to(ROOT).as_posix()for p in(ROOT/'rouge').glob('*.py')}
    for pack in ('p3-expansion-313','p3-current-battle-314','p3-ending-events-316','p3-document-flows-321','p3-box-event-322','p3-current-node-readers-332'):
        names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'research'/pack).rglob('*')if p.is_file())
    manifest=json.loads((ROOT/'research/p3-current-node-readers-332/runtime-manifest.json').read_bytes());names.update(manifest['files'])
    names.update(['scripts/build_current_node_readers_332.py','scripts/verify_current_node_readers_window_332.py','scripts/verify_full_available.py','tests/test_current_node_readers_332.py','tests/test_current_node_readers_view_332.py'])
    return{n:sha256((ROOT/n).read_bytes()).hexdigest()for n in sorted(names)}


def main():
    p=argparse.ArgumentParser();p.add_argument('--receipt',type=Path,required=True);p.add_argument('--visible-ms',type=int,default=60000);args=p.parse_args();dest=args.receipt.resolve();assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True)
    before=bound_files();checks=[];images=[];observations=[];refreshes=[];calls={k:0 for k in('game_connect','capture','next_frame','desktop_start','desktop_request','provider_chat','credential_read')};failure=None;window=None;gui=None;exitcode=None;done=False
    def require(value,name):
        if not value:raise AssertionError(name)
        if name not in checks:checks.append(name)
    def forbidden(name):
        def fail(*a,**kw):calls[name]+=1;raise AssertionError('Forbidden real operation: '+name)
        return fail
    try:
        if sys.platform!='win32':raise RuntimeError('Actual Windows required')
        import win32gui,win32process
        from PySide6.QtCore import Qt,QTimer
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QApplication
        from PySide6.QtTest import QTest
        from rouge import app as app_module,current_node_readers as model
        gui=QApplication([]);require(gui.platformName()=='windows','actual_windows_QPA')
        with TemporaryDirectory(prefix='rouge332-public-')as folder,ExitStack()as stack:
            temporary=Path(folder)
            for name,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,name,value))
            backend=app_module.DesktopBackend
            stack.enter_context(patch.object(app_module,'DesktopBackend',lambda _path,callback:backend(temporary/'chat',callback)))
            stack.enter_context(patch.object(app_module,'list_game_windows',return_value=[]))
            for name,key in(('connect','game_connect'),('capture','capture'),('next_frame','next_frame')):stack.enter_context(patch.object(app_module.GameCapture,name,side_effect=forbidden(key)))
            for name,key in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(backend,name,side_effect=forbidden(key)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=app_module.MainWindow();window.resize(1220,850);window.setWindowTitle('第332节 · 更新事件条件（公开隔离验收）');window.show();gui.processEvents()
            tabs=window.centralWidget();panel=window.node_catalog;state=deepcopy(window.run.state);context=deepcopy(window.battle_preview.context)
            def native(widget=None):
                widget=window if widget is None else widget
                hwnd=int(widget.winId());pid=win32process.GetWindowThreadProcessId(hwnd)[1]
                require(win32gui.IsWindowVisible(hwnd)and not win32gui.IsIconic(hwnd)and pid==os.getpid(),'visible_owned_native_MainWindow_HWND_PID')
                return{'hwnd':hwnd,'pid':pid,'size':[widget.width(),widget.height()]}
            def shot(label):
                gui.processEvents();file=dest.with_name('window-'+label+'.png');assert not file.exists();require(panel.grab().save(str(file),'PNG'),'actual_widget_screenshot_saved')
                images.append({'name':label,'path':str(file),'sha256':sha256(file.read_bytes()).hexdigest(),'native':native()})
            def reading(widget):
                c=widget.textCursor();return{'anchor':c.anchor(),'position':c.position(),'selection':c.selectedText(),'scroll':widget.verticalScrollBar().value()}
            def exercise():
                nonlocal done,failure,panel
                dialog=None
                try:
                    bar=tabs.tabBar();idx=tabs.indexOf(panel);QTest.mouseClick(bar,Qt.MouseButton.LeftButton,pos=bar.tabRect(idx).center());gui.processEvents();require(tabs.currentWidget()is panel,'actual_MainWindow_node_catalogue_tab_opened')
                    main_panel=panel
                    def choose(combo,value):
                        index=combo.findData(value);require(index>=0,'exact_control_value_available');combo.setFocus();combo.setCurrentIndex(index);QTest.keyClick(combo,Qt.Key.Key_Return);gui.processEvents();require(combo.currentData()==value,'direct_exact_selection_no_long_prefix_traversal')
                    def select(widget,key):
                        index=next(i for i in range(widget.count())if widget.item(i).data(Qt.ItemDataRole.UserRole)==key);item=widget.item(index);widget.scrollToItem(item);gui.processEvents();QTest.mouseClick(widget.viewport(),Qt.MouseButton.LeftButton,pos=widget.visualItemRect(item).center());gui.processEvents();require(widget.currentItem().data(Qt.ItemDataRole.UserRole)==key,'actual_mouse_selects_exact_item_or_document_group')
                    def entry(category,key):
                        choose(main_panel.scope,False);choose(main_panel.category,category);select(main_panel.entries,key);require(main_panel.flow_button.isVisible(),'real_update_entry_exposes_current_event_battles');QTest.mouseClick(main_panel.flow_button,Qt.MouseButton.LeftButton);gui.processEvents();return main_panel.flow_dialog
                    def flow_entry(category,key):
                        choose(main_panel.scope,False);choose(main_panel.category,category);select(main_panel.entries,key);require(main_panel.flow_button.isVisible(),'real_update_entry_exposes_whole_encounter');QTest.mouseClick(main_panel.flow_button,Qt.MouseButton.LeftButton);gui.processEvents();return main_panel.flow_dialog
                    from tests.test_current_node_readers_332 import clone
                    data=model.packet()['data'];main_panel.runtime_context={'gold':100,'has_fossil':True,'has_controller':True}
                    def catalogue(event_id):
                        index=next(i for i,e in enumerate(main_panel.entries)if e['key']=='event:'+event_id);main_panel.list.setCurrentRow(index);gui.processEvents();require(main_panel.current_reference_button.isVisible(),'catalogue_current_reference_button_visible');QTest.mouseClick(main_panel.current_reference_button,Qt.MouseButton.LeftButton);gui.processEvents();require(main_panel.current_reference_window is not None,'actual_catalogue_button_opens_owned_reader');return main_panel.current_reference_window
                    for event_id,row in data['bindings'].items():
                        dialog=catalogue(event_id);panel=dialog.panel;native(dialog);require(panel.event_id==row['current_event_id']and panel.choice_id is None,'all25_groups_open_exact_existing_event_overview');require(panel.result['actual_eligible']is None and not dialog.node_reference_binding['actual_node_version_confirmed'],'no_actual_version_phase_or_eligibility_inferred');require('请核对实际游戏版本' in dialog.node_reference_banner.text(),'plain_chinese_version_reference_notice')
                        if hasattr(panel,'gold'):require(panel.gold.value()==-1,'run_gold_not_auto_applied')
                        for name in('controller','fossil','covenant'):
                            if hasattr(panel,name):require(getattr(panel,name).currentData()is None,'run_special_conditions_not_auto_applied')
                        observations.append({'legacy_event':event_id,'current_event':panel.event_id,'reader':row['reader'],'scene':panel.scene_id,'choice':panel.choice_id,'reference_only':True})
                        if row['reader']in('rest','shop','sand','ritual','box')and not any(v['name']=='catalogue-'+row['reader']for v in images):shot('catalogue-'+row['reader'])
                        dialog.close();panel=main_panel
                    dialog=catalogue('community_group_008');panel=dialog.panel;choose(panel.controller,True);select(panel.choices,next(c['id']for c in panel.result['choices'].values()if 'choice_ro6_normal2_2'in c['variant_ids']));require(panel.open_battle(),'exact_choice_opens_battle_configuration_reader');config=panel.battle_dialog;choose(config.panel.stages,'ro6_t_13');require(config.panel.open_battle(),'manual_exact_configuration_opens_fixed_map');battle=config.panel.battle_dialog;require(battle.isVisible(),'nested_fixed_map_visible');shot('encounter-choice');dialog.resize(850,440);gui.processEvents()
                    for reader in(panel.player,panel.technical):
                        panel.tabs.setCurrentWidget(reader);gui.processEvents();cursor=reader.textCursor();cursor.setPosition(3);cursor.setPosition(16,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor);bar=reader.verticalScrollBar();require(bar.maximum()>0,'real_reader_nonzero_scroll');bar.setValue(min(4,bar.maximum()));prior=reading(reader);tab=panel.tabs.currentIndex();main_panel.refresh();gui.processEvents();require(reading(reader)==prior and panel.tabs.currentIndex()==tab and panel.controller.currentData()is True and config.panel.stages.currentData()=='ro6_t_13','same_origin_refresh_keeps_two_real_readers_local_condition_configuration');require(dialog.isVisible()and config.isVisible()and battle.isVisible(),'same_origin_refresh_keeps_nested_map_tree');refreshes.append({'reader':'player'if reader is panel.player else'technical','before':prior,'after':reading(reader),'configuration':'ro6_t_13'})
                    main_panel.open_current_event_reference();require(not dialog.isVisible()and not config.isVisible()and not battle.isVisible(),'repeated_open_closes_entire_previous_reader_tree');dialog=main_panel.current_reference_window;panel=dialog.panel;catalogue('community_group_001');require(not dialog.isVisible(),'changed_catalogue_selection_closes_previous_reader');dialog=main_panel.current_reference_window;main_panel.list.setCurrentRow(next(i for i,e in enumerate(main_panel.entries)if e['kind']=='function'));gui.processEvents();require(not dialog.isVisible()and not main_panel.current_reference_button.isVisible()and not main_panel.open_current_event_reference(),'unrelated_node_type_has_no_event_reader')
                    graph={'zone_id':'zone_1','template_id':'t','nodes':[{'id':'a','row':1,'col':2,'observed_type':'林间空地','remembered_type':'不期而遇','remembered_content':{'kind':'event','title':'桑尼的邀请'}}]};original=deepcopy(graph);main_panel.set_map_context(graph,{'floor':1},epoch='first',historical=True);main_panel.set_node(graph,'a',floor=1);main_panel.bind_current_node();main_panel.list.setCurrentRow(next(i for i,e in enumerate(main_panel.entries)if e['kind']=='event'and e['title']=='桑尼的邀请'));gui.processEvents();require(main_panel.open_current_event_reference(),'historical_node_reference_available');dialog=main_panel.current_reference_window;panel=dialog.panel;require('历史节点'in dialog.node_reference_banner.text()and panel.result['actual_eligible']is None,'history_reference_not_actual_current_event');shot('historical-node');main_panel.refresh();require(dialog.isVisible(),'unchanged_history_refresh_keeps_reader');main_panel.set_map_context(graph,{'floor':1},epoch='second',historical=True);require(not dialog.isVisible()and graph==original,'changed_run_epoch_closes_history_without_mutating_map')
                    main_panel.show_directory();dialog=catalogue('community_group_016');panel=dialog.panel;prior=main_panel.player_detail.toPlainText()
                    with patch('rouge.current_lake.reference',return_value=None):
                        main_panel.show_selected();require(not dialog.isVisible()and not main_panel.current_reference_button.isVisible(),'optional_current_reader_source_failure_closes_old_window');require(main_panel.player_detail.toPlainText()==prior,'old_catalogue_text_remains_available_when_optional_reader_fails')
                    main_panel.show_selected();require(main_panel.open_current_event_reference(),'source_recovery_allows_manual_open');dialog=main_panel.current_reference_window;panel=dialog.panel;shot('lake-overview')
                    damaged=temporary/'public';clone(damaged);file=damaged/model.DATA;raw=file.read_bytes()
                    with patch.object(model,'ROOT',damaged):
                        file.write_bytes(raw+b' ');main_panel.show_selected();require(not dialog.isVisible()and not main_panel.open_current_event_reference(),'actual_bridge_bytes_damage_detected_and_old_window_closed');require(main_panel.player_detail.toPlainText()==prior,'actual_bridge_damage_keeps_legacy_information');panel=main_panel;shot('bridge-source-loss');file.write_bytes(raw);main_panel.show_selected();require(main_panel.current_reference_window is None,'source_recovery_never_reopens_or_reselects_automatically');require(main_panel.open_current_event_reference(),'manual_recovery_open_validated_current_reader');main_panel.current_reference_window.close()
                    dialog=catalogue('community_group_008');panel=dialog.panel;select(panel.choices,next(c['id']for c in panel.result['choices'].values()if 'choice_ro6_normal2_2'in c['variant_ids']));require(panel.open_battle(),'main_close_fixture_config_open');config=panel.battle_dialog;choose(config.panel.stages,'ro6_t_13');require(config.panel.open_battle(),'main_close_fixture_map_open');battle=config.panel.battle_dialog;require(dialog.isVisible()and config.isVisible()and battle.isVisible(),'main_close_fixture_owned_tree_visible');panel=main_panel;require(window.run.state==state and window.battle_preview.context==context,'temporary_run_resources_and_legacy_context_unchanged');require(all(v==0 for v in calls.values())and not window.auto.isChecked(),'all_seven_real_game_chat_credential_operations_zero');native();window.close();gui.processEvents();require(not dialog.isVisible()and not config.isVisible()and not battle.isVisible(),'actual_MainWindow_close_closes_owned_current_reader_and_nested_map');done=True;gui.exit(0)
                except BaseException as error:
                    failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
                    if dialog is not None:dialog.close()
                    window.close();gui.exit(1)
            QTimer.singleShot(250,exercise)
            QTimer.singleShot(args.visible_ms,lambda:gui.exit(2)if not done else None)
            exitcode=gui.exec()
            require(exitcode==0 and done and not window.isVisible(),'actual_Qt_success_and_owned_MainWindow_closed')
    except BaseException as error:
        if failure is None:failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
    finally:
        if window is not None:window.close()
    after=bound_files();result={'section':332,'passed':done and failure is None and exitcode==0 and before==after,'failure':failure,'process_id':os.getpid(),'qpa':gui.platformName()if gui else None,'qt_exit_code':exitcode,'verification_window_closed':window is not None and not window.isVisible(),'unique_checks':len(checks),'checks':checks,'actual_readings':observations,'same_identity_refresh_observations':refreshes,'screenshots':images,'source_sha256_before':before,'source_sha256_after':after,'source_scope_selected_not_all_transitive_dependencies':True,'external_operation_attempts':calls,'temporary_state':True,'private_contents_read_copied_or_restored':False,'game_operated':False,'chat_sent':False,'current_server_or_original_runtime_validated':False,'at_utc':datetime.now(timezone.utc).isoformat()}
    dest.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'));print(json.dumps({'passed':result['passed'],'checks':len(checks),'failure':failure},ensure_ascii=False));return 0 if result['passed']else 1

if __name__=='__main__':raise SystemExit(main())
