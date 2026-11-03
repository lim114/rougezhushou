"""Unexecuted native292 UI-only acceptance draft; root owns actual execution.

Canonical scripts/ promotion is mandatory. Uses public temporary state, no game,
chat or private state. Selected source guard is not a full dependency freeze.
"""
import argparse
from contextlib import ExitStack
from copy import deepcopy
from datetime import datetime,timezone
import hashlib,json,os
from pathlib import Path
import sys,tempfile,traceback
from unittest.mock import patch

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'rouge/app.py').is_file())
sys.path.insert(0,str(ROOT))
CANONICAL='scripts/verify_event_preview_filters_window_292.py'
SIZE=(1050,720)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def bound_files():
    names={CANONICAL,'rouge/app.py','rouge/node_catalog_view.py','rouge/node_catalog.py',
        'rouge/event_planning.py','rouge/player_node_information.py','rouge/ui_state.py',
        'rouge/battle_preview.py','rouge/battle_view.py','rouge/node_rewards.py',
        'rouge/event_named_reward_links.py','rouge/data/node-catalog.json',
        'rouge/data/event-planning-reference.json','rouge/data/event-current-observation.json',
        'rouge/data/battle-previews.json','rouge/data/battle-node-pools.json',
        'rouge/data/node-reward-reference.json','rouge/data/view-catalog.json',
        'tests/test_event_preview_filters_292.py'}
    stage=json.loads((ROOT/'rouge/data/battle-previews.json').read_bytes())['stages']['ro6_e_t_3']
    names.add('rouge/data/'+stage['image']['file'])
    result={}
    for name in sorted(names):
        path=ROOT/name
        if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(ROOT):
            raise ValueError('Selected public source must be a regular project file: '+name)
        result[name]=sha(path)
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt',required=True)
    parser.add_argument('--visible-ms',type=int,default=30000)
    args=parser.parse_args();destination=Path(args.receipt).resolve()
    if destination.exists():raise FileExistsError('Preserve the first actual receipt')
    if args.visible_ms<=0:raise ValueError('Positive --visible-ms required')
    destination.parent.mkdir(parents=True,exist_ok=True)
    started=datetime.now(timezone.utc).isoformat()
    before={};after={};checks=[];images=[];observations=[];native_observations=[]
    attempts={name:0 for name in ('game_enumeration','game_connect','game_capture','game_next_frame',
        'desktop_start','desktop_request','provider_chat','credential_read')}
    executions=0;failure=None;done=False;closed=False;qpa=None;qt_exit=None
    def require(value,label):
        nonlocal executions
        if not value:raise AssertionError(label)
        executions+=1
        if label not in checks:checks.append(label)
    def forbidden(name):
        def blocked(*_,**__):attempts[name]+=1;raise AssertionError('Forbidden original external entry: '+name)
        return blocked
    try:
        if sys.platform!='win32':raise RuntimeError('Actual native Windows required')
        if Path(__file__).resolve()!=(ROOT/CANONICAL).resolve():raise RuntimeError('Cache draft is not executable acceptance; promote canonical script first')
        from PySide6.QtCore import Qt,QRect,QPoint,QTimer
        from PySide6.QtGui import QTextCursor
        from PySide6.QtWidgets import QApplication
        import win32gui,win32process
        from rouge import app as app_module
        from rouge import node_catalog as catalog
        before=bound_files();gui=QApplication([]);qpa=gui.platformName()
        require(qpa=='windows','native_windows_QPA')
        class PublicWindow(app_module.MainWindow):
            def refresh_windows(self):self.windows.clear()
        with tempfile.TemporaryDirectory(prefix='rouge-292-filter-window-') as folder,ExitStack() as stack:
            temporary=Path(folder)
            for key,value in {'ROOT':temporary,'SETTINGS':temporary/'settings.json',
                    'OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():
                stack.enter_context(patch.object(app_module,key,value))
            stack.enter_context(patch.object(app_module,'list_game_windows',side_effect=forbidden('game_enumeration')))
            for method,name in [('connect','game_connect'),('capture','game_capture'),('next_frame','game_next_frame')]:
                stack.enter_context(patch.object(app_module.GameCapture,method,side_effect=forbidden(name)))
            for method,name in [('start','desktop_start'),('request','desktop_request')]:
                stack.enter_context(patch.object(app_module.DesktopBackend,method,side_effect=forbidden(name)))
            stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')))
            stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
            window=PublicWindow();window.setWindowTitle('第292节 · 场景与选项作战资料筛选（公开隔离验收）')
            window.resize(*SIZE);window.show()
            panel=window.node_catalog;tabs=window.centralWidget();role=Qt.ItemDataRole.UserRole+1
            initial_run=deepcopy(window.run.state);emitted=[];panel.stageSelected.connect(emitted.append)
            saved=None
            def isolated():
                require(not window.auto.isChecked() and not window.timer.isActive(),'automatic_sampling_and_timer_disabled')
                require(window.capture.target is None and window.desktop.process is None,'capture_target_and_desktop_backend_inactive')
                require(all(value==0 for value in attempts.values()),'all_eight_external_operation_attempts_zero')
            def native():
                hwnd=int(window.winId());thread,pid=win32process.GetWindowThreadProcessId(hwnd)
                require(win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd) and window.isVisible(), 'actual_native_HWND_visible')
                require(pid==os.getpid() and not win32gui.IsIconic(hwnd),'actual_HWND_owned_by_fixture_and_not_minimized')
                require([window.width(),window.height()]==list(SIZE),'actual_client_size_exact_1050x720')
                return {'hwnd':hwnd,'process_id':pid,'thread_id':thread,'qpa':qpa,'client_size':[window.width(),window.height()]}
            def choose(combo,value):
                index=combo.findData(value);require(index>=0,'requested_complete_filter_key_exists');combo.setCurrentIndex(index)
            def event(identity):
                panel.show_directory();choose(panel.kind,'event');choose(panel.floor,None);choose(panel.node_type,None)
                panel.search.setText(catalog._event(identity)['title'])
                index=next(i for i,e in enumerate(panel.entries) if e['kind']=='event' and e['record']['id']==identity)
                panel.list.setCurrentRow(index);tabs.setCurrentWidget(panel)
                require(panel.entries[index]['record']['id']==identity,'exact_event_identity_selected')
            def tokens():return [deepcopy(panel.event_stage.itemData(i,role)) for i in range(panel.event_stage.count())]
            def reading():
                result={}
                for name,widget in [('player',panel.player_detail),('evidence',panel.detail)]:
                    cursor=widget.textCursor();result[name]={'text':sha256text(widget.toPlainText()),'anchor':cursor.anchor(),
                        'position':cursor.position(),'selected':cursor.selectedText(),'vertical':widget.verticalScrollBar().value(),
                        'horizontal':widget.horizontalScrollBar().value()}
                return {'key':panel.list.selected_key(),'reading_tab':panel.reading_tabs.currentIndex(),'readers':result,
                    'search':panel.search.text(),'search_cursor':panel.search.cursorPosition(),
                    'search_selection_start':panel.search.selectionStart(),'search_selection':panel.search.selectedText()}
            def snapshot():
                return {'reading':reading(),'scene':panel.event_scene_filter.currentData(),'choice':panel.event_choice_filter.currentData(),
                    'stage_token':deepcopy(panel.event_stage.currentData(role)),'stage_id':panel.event_stage.currentData()}
            def prime():
                panel.reading_tabs.setCurrentWidget(panel.detail);gui.processEvents();widget=panel.detail
                require(widget.verticalScrollBar().maximum()>0 and len(widget.toPlainText())>16,'real_existing_document_has_nonzero_scroll_range')
                cursor=widget.textCursor();cursor.setPosition(5);cursor.setPosition(16,QTextCursor.MoveMode.KeepAnchor)
                widget.setTextCursor(cursor);widget.verticalScrollBar().setValue(max(1,widget.verticalScrollBar().maximum()//2))
                panel.search.setSelection(0,2);gui.processEvents()
                require(widget.verticalScrollBar().value()>0 and bool(widget.textCursor().selectedText()) and bool(panel.search.selectedText()),
                    'real_nonzero_scroll_and_document_search_selections')
            def save_image(name):
                isolated();handle=native();path=destination.with_name(destination.stem+'-'+name+'.png')
                if path.exists():raise FileExistsError('First image must not be overwritten')
                pixels=window.grab();require(not pixels.isNull(),'actual_own_window_pixels')
                require(pixels.save(str(path),'PNG'),'actual_own_window_PNG_saved')
                images.append({'name':name,'path':str(path),'sha256':sha(path),'native_window':handle})
            def fail(error):
                nonlocal failure,done
                if failure is None:failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
                done=False;window.close();gui.exit(1)
            def later(callback,delay=250):
                def guarded():
                    try:isolated();callback()
                    except BaseException as error:fail(error)
                QTimer.singleShot(delay,guarded)
            def begin():
                event('community_group_016');later(check_duplicate_options)
            def check_duplicate_options():
                nonlocal saved
                native_observations.append(native())
                for widget in (panel.event_scene_filter,panel.event_choice_filter):
                    rect=QRect(widget.mapTo(window,QPoint(0,0)),widget.size())
                    require(widget.isVisible() and not widget.visibleRegion().isEmpty() and window.rect().contains(rect), 'new_filter_visible_inside_1050x720')
                a=panel.event_scene_filter.mapTo(window,QPoint(0,0));b=panel.event_choice_filter.mapTo(window,QPoint(0,0))
                require(a.y()==b.y() and b.x()>a.x(),'new_scene_and_choice_filters_share_one_horizontal_row')
                expected={'community_group_016:scene:'+str(i)+':choice:1' for i in (2,5,6)}
                found={panel.event_choice_filter.itemData(i) for i in range(panel.event_choice_filter.count()) if '休想骗我' in panel.event_choice_filter.itemText(i)}
                require(found==expected,'same_title_options_remain_three_distinct_complete_keys')
                for key in sorted(expected):
                    choose(panel.event_choice_filter,key)
                    require(panel.event_choice_filter.currentData()==key and panel.event_scene_filter.currentData() is None,'same_title_key_does_not_infer_another_scene')
                    require(panel.event_stage.count()==0 and not panel.battle_button.isEnabled(),'same_title_nonbattle_options_have_no_borrowed_preview')
                choose(panel.event_scene_filter,'community_group_016:scene:8');choose(panel.event_choice_filter,'community_group_016:scene:8:choice:0')
                require(tokens()==[['community_group_016:scene:8','community_group_016:scene:8:choice:0','ro6_e_t_5']], 'exact_016_filtered_scene_choice_stage_token')
                panel.event_stage.setCurrentIndex(0);prime();saved=snapshot();panel.refresh();later(check_refresh)
            def check_refresh():
                require(snapshot()==saved,'same_event_refresh_retains_filters_full_stage_token_readers_search_scroll_and_selection')
                save_image('same-event-retained');event('community_group_014');later(check_dual)
            def check_dual():
                nonlocal saved
                require(panel.event_scene_filter.currentData() is None and panel.event_choice_filter.currentData() is None,'different_event_resets_filters')
                choose(panel.event_scene_filter,'community_group_014:scene:1');choose(panel.event_choice_filter,'community_group_014:scene:1:choice:0')
                require(tokens()==[['community_group_014:scene:1','community_group_014:scene:1:choice:0',s] for s in ('ro6_t_3','ro6_e_t_3')], 'ordinary_option_preserves_ordinary_and_emergency_alternatives')
                panel.event_stage.setCurrentIndex(1);prime();saved=snapshot();save_image('ordinary-dual-reference')
                count=len(emitted);panel.battle_button.click()
                require(emitted[count:]==['ro6_e_t_3'],'actual_button_emits_exact_manual_fixed_stage_once')
                require(tabs.currentWidget() is window.battle_preview and window.battle_preview.current_stage=='ro6_e_t_3'
                    and bool(window.battle_preview.grid.stage['map']),'actual_button_opens_correct_fixed_battle_preview')
                later(check_return)
            def check_return():
                save_image('fixed-preview-opened');tabs.setCurrentWidget(panel)
                require(snapshot()==saved,'return_from_fixed_preview_preserves_event_filter_and_reading_state')
                choose(panel.event_scene_filter,'community_group_014:scene:2');choose(panel.event_choice_filter,'community_group_014:scene:2:choice:0')
                require(tokens()==[['community_group_014:scene:2','community_group_014:scene:2:choice:0','ro6_e_t_3']], 'emergency_only_option_never_includes_ordinary_variant')
                panel.event_stage.setCurrentIndex(0);previous=len(emitted)
                panel.event_stage.setItemData(0,['community_group_014:scene:1','community_group_014:scene:1:choice:0','ro6_e_t_3'],role)
                panel.battle_button.click()
                require(len(emitted)==previous and panel.event_stage.currentData() is None and not panel.battle_button.isEnabled(),
                    'stale_complete_origin_token_revalidated_before_click_without_emission')
                choose(panel.event_scene_filter,'community_group_014:scene:0');choose(panel.event_choice_filter,'community_group_014:scene:0:choice:2')
                require(panel.event_stage.count()==0 and not panel.battle_button.isEnabled(),'nonbattle_option_empty_and_disabled_not_event_fallback')
                panel.select_stage();require(len(emitted)==previous,'nonbattle_programmatic_click_does_not_emit')
                save_image('nonbattle-option-empty');event('community_group_015');later(finish)
            def finish():
                nonlocal done
                require(panel.event_scene_filter.currentData() is None and panel.event_choice_filter.currentData() is None,'final_event_change_resets_both_filters')
                require(all(token[0].startswith('community_group_015:') for token in tokens()),'final_event_never_borrows_prior_choice_origin')
                require(window.run.state==initial_run,'manual_UI_preview_never_changes_temporary_run_memory')
                require(bound_files()==before,'selected_public_sources_stable_before_completion')
                observations.append({'same_title_keys':sorted(expected for expected in ('community_group_016:scene:2:choice:1',
                    'community_group_016:scene:5:choice:1','community_group_016:scene:6:choice:1')),
                    'manual_stage_requests':emitted,'actual_game_transition':None,'actual_choice_executed':None,
                    'stale_control_data_is_an_explicit_negative_fixture':True})
                done=True
            def close_deadline():
                nonlocal failure
                if not done and failure is None:failure={'type':'TimeoutError','message':'New UI checks not completed before deadline'}
                window.close()
            later(begin,500);QTimer.singleShot(max(12000,args.visible_ms),close_deadline)
            qt_exit=gui.exec();closed=not window.isVisible()
            if qt_exit!=0 or not closed or not done:
                if failure is None:failure={'type':'RuntimeError','message':'Fixture checks/Qt/window close not complete'}
            if failure is None:isolated()
            after=bound_files()
            if before!=after and failure is None:failure={'type':'AssertionError','message':'Selected public sources changed through actual closure'}
    except BaseException as error:
        failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
    report={'section':292,'kind':'isolated_native_windows_event_preview_filters','passed':done and failure is None,
        'failure':failure,'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'process_id':os.getpid(),
        'qpa':qpa,'qt_exit_code':qt_exit,'verification_window_closed':closed,'checks':checks,'unique_checks':len(checks),
        'successful_assertion_executions_including_repeated_guards':executions,'requested_client_size':list(SIZE),
        'native_observations':native_observations,'screenshots':images,'screenshot_count':len(images),'public_observations':observations,
        'source_sha256_before':before,'source_sha256_after':after,'source_guard_is_selected_not_all_transitive_dependencies':True,
        'temporary_state_root':True,'state_paths_replaced_before_constructor':['ROOT','SETTINGS','OPERATOR_STATE','RUN_STATE'],
        'private_state_read_copied_or_restored':False,'external_operation_attempts':attempts,'game_operated':False,
        'game_captures':0,'chat_sent':False,'chat_attempted':bool(attempts['desktop_request'] or attempts['provider_chat']),
        'external_entrypoints_blocked_before_original_call':True,'original_project_window_operated_or_restarted':False,
        'actual_process_termination_verified_by_this_script':False,'owned_supervisor_exit_and_cleanup_required_separately':True,
        'scope':'New manual scene/choice preview filtering only; 1050x720 UI, reading retention, exact stage token and real fixed preview, stale/empty rejection. No full mechanism/domain rerun or actual game state inferred.'}
    with destination.open('x',encoding='utf-8') as stream:stream.write(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    return 0 if report['passed'] else 1

def sha256text(value):return hashlib.sha256(value.encode('utf-8')).hexdigest()
if __name__=='__main__':raise SystemExit(main())
