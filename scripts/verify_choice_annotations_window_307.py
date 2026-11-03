"""Native public directory reading only; root promotes and executes this fixture."""
import argparse,json,os,sys,tempfile,traceback
from contextlib import ExitStack
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch

ROOT=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file())
sys.path.insert(0,str(ROOT))
CANONICAL='scripts/verify_choice_annotations_window_307.py'
PACK='research/p3-choice-annotations-307'
MANIFEST=PACK+'/source-manifest.json'
DATA='rouge/data/choice-annotations.json'

def sha(path):return sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_bytes())
def bound_files():
    names={CANONICAL,MANIFEST,DATA,'rouge/choice_annotations.py','rouge/node_catalog_view.py',
        'rouge/player_node_information.py','rouge/original_destinations.py','rouge/original_destinations_view.py',
        'rouge/node_catalog.py','rouge/event_planning.py','rouge/app.py','rouge/ui_state.py',
        'rouge/data/original-destinations.json','rouge/data/node-events.json','rouge/data/battle-previews.json',
        'rouge/resting_corner_view.py','rouge/curiosity_node_rules_view.py','rouge/branch_choice.py',
        'scripts/build_choice_annotations_307.py','tests/test_choice_annotations_307.py','tests/test_choice_annotation_view_307.py'}
    manifest=read(ROOT/MANIFEST)
    names.update(manifest['runtime_files']);names.update(manifest['source_build_files'])
    names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/PACK).iterdir()if p.is_file())
    result={}
    for name in sorted(names):
        path=ROOT/name
        if not path.is_file()or path.is_symlink()or not path.resolve().is_relative_to(ROOT):raise ValueError('Regular selected public source missing: '+name)
        result[name]=sha(path)
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--receipt',type=Path,required=True)
    parser.add_argument('--visible-ms',type=int,default=120000);args=parser.parse_args()
    destination=args.receipt.resolve()
    if destination.exists():raise FileExistsError('Keep the original actual receipt.')
    if args.visible_ms<15000:raise ValueError('Allow at least15000ms for actual staged reading.')
    destination.parent.mkdir(parents=True,exist_ok=True)
    started=datetime.now(timezone.utc).isoformat();before={};after={};checks=[];assertions=0
    readings=[];requirements=[];destinations=[];refreshes=[];images=[];handles=[];negative=None
    failure=None;done=False;closed=False;qt_exit=None;qpa=None;panel=None;gui=None
    attempts={k:0 for k in('game_enumeration','game_connect','game_capture','game_next_frame','desktop_start','desktop_request','provider_chat','credential_read')}
    def require(value,label):
        nonlocal assertions
        if not value:raise AssertionError(label)
        assertions+=1
        if label not in checks:checks.append(label)
    def forbidden(name):
        def blocked(*a,**k):attempts[name]+=1;raise AssertionError('Forbidden external entry: '+name)
        return blocked
    try:
        if sys.platform!='win32':raise RuntimeError('Native Windows required; offscreen/Wine is not acceptance.')
        if Path(__file__).resolve()!=(ROOT/CANONICAL).resolve():raise RuntimeError('Promote the canonical source before actual execution.')
        before=bound_files()
        from rouge import app as app_module,choice_annotations as model,event_planning
    except ImportError as error:
        # Preserve import errors as actual failures; no substitute/mocked module.
        failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
    except BaseException as error:failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
    if failure is None:
        try:
            from rouge import node_catalog as catalog
            from rouge.node_catalog_view import NodeCatalogPanel
            from PySide6.QtCore import Qt,QTimer
            from PySide6.QtGui import QTextCursor
            from PySide6.QtWidgets import QApplication
            from PySide6.QtTest import QTest
            import win32gui,win32process
            packet=model.source_data();require(packet is not None,'fresh_role_source_valid_before_Qt')
            identities=list(model.NEW_RESULT_IDENTITIES);events=list(dict.fromkeys(k[0]for k in identities))
            require(len(identities)==10 and len(events)==7,'ten_source_bound_results_across_seven_events')
            prior_rows=[r for r in packet['rows']if r['role']=='preselection_requirement']
            extra_events=[r['event_id']for r in prior_rows if r['event_id']not in events]
            visits=events+list(dict.fromkeys(extra_events))
            gui=QApplication([]);qpa=gui.platformName();require(qpa=='windows','actual_native_windows_QPA')
            with tempfile.TemporaryDirectory(prefix='rouge-307-public-native-')as folder,ExitStack()as stack:
                temp=Path(folder)
                for key,value in{'ROOT':temp,'SETTINGS':temp/'settings.json','OPERATOR_STATE':temp/'operators.json','RUN_STATE':temp/'run.json'}.items():stack.enter_context(patch.object(app_module,key,value))
                stack.enter_context(patch.object(app_module,'list_game_windows',side_effect=forbidden('game_enumeration')))
                for method,name in(('connect','game_connect'),('capture','game_capture'),('next_frame','game_next_frame')):stack.enter_context(patch.object(app_module.GameCapture,method,side_effect=forbidden(name)))
                for method,name in(('start','desktop_start'),('request','desktop_request')):stack.enter_context(patch.object(app_module.DesktopBackend,method,side_effect=forbidden(name)))
                stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')))
                stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
                panel=NodeCatalogPanel();panel.resize(1280,900);panel.setWindowTitle('第307节 · 条件与结果资料（公开隔离验收）');panel.show()
                runtime_before=deepcopy(panel.runtime_context);stage_requests=[];panel.stageSelected.connect(stage_requests.append)
                def native(widget,kind):
                    h=int(widget.winId());thread,pid=win32process.GetWindowThreadProcessId(h)
                    require(win32gui.IsWindow(h)and win32gui.IsWindowVisible(h)and pid==os.getpid()and not win32gui.IsIconic(h),'visible_owned_HWND_and_actual_fixture_PID')
                    result={'kind':kind,'hwnd':h,'process_id':pid,'thread_id':thread,'qpa':qpa,'client_size':[widget.width(),widget.height()]};handles.append(result);return result
                def select(event_id):
                    index=next(i for i,e in enumerate(panel.entries)if e['kind']=='event'and e['record']['id']==event_id)
                    item=panel.list.flat[index];item.parent().setExpanded(True);panel.list.scrollToItem(item);gui.processEvents()
                    rect=panel.list.visualItemRect(item)
                    if not rect.isValid()or rect.isEmpty():raise AssertionError('Actual target tree row not visible.')
                    QTest.mouseClick(panel.list.viewport(),Qt.MouseButton.LeftButton,pos=rect.center());gui.processEvents()
                    require(panel.list.selected_key()==panel.entries[index]['key'],'actual_QTest_tree_click_selects_exact_event')
                def shot(name):
                    path=destination.with_name('window-'+name+'.png')
                    if path.exists():raise FileExistsError('Preserve original actual image.')
                    panel.reading_tabs.setCurrentWidget(panel.player_detail);panel.repaint();gui.processEvents()
                    if not panel.grab().save(str(path)):raise RuntimeError('Actual screenshot save failed.')
                    images.append({'name':name,'path':str(path),'sha256':sha(path),'direct_player_text':True,'native_window':native(panel,name)})
                def close_all():
                    nonlocal closed
                    if panel.destination_window is not None:panel.destination_window.close()
                    panel.close();gui.processEvents();closed=not panel.isVisible()and(panel.destination_window is None or not panel.destination_window.isVisible())
                def fail(error):
                    nonlocal failure
                    if failure is None:failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
                    close_all();gui.exit(1)
                def later(function,delay=150):
                    def guarded():
                        try:function()
                        except BaseException as error:fail(error)
                    QTimer.singleShot(delay,guarded)
                def visit(index):
                    eid=visits[index];select(eid);player=panel.player_detail.toPlainText();technical=panel.detail.toPlainText()
                    chosen=[]
                    for identity in identities:
                        if identity[0]!=eid:continue
                        row=model.choice_reference(*identity)['reference']
                        require(row['label']+'（原文）：'in player and row['text']in technical
                            and'条件原文：'+row['text']not in player and'不作为选项出现条件'in player,'documented_result_label_not_misrepresented_as_preselection')
                        chosen.append({'identity':list(identity),'label':row['label'],'literal_text':row['text']})
                    for row in prior_rows:
                        if row['event_id']!=eid:continue
                        old=next(r for r in event_planning.choice_eligibility(eid,row['scene_key'])['rows']if r['choice_key']==row['choice_key'])
                        new=next(r for r in model.classified_choice_eligibility(eid,row['scene_key'])['rows']if r['choice_key']==row['choice_key'])
                        require('条件原文：'+row['text']in player and all(old[k]==new[k]for k in('status','checks','parsed_special_requirements')),'true_preselection_literal_and_original_qualification_unchanged')
                        requirements.append({'choice_key':row['choice_key'],'literal':row['text'],'original_status':old['status'],'actual_selectable':new['actual_selectable']})
                    if eid=='community_group_014':
                        scene=eid+':scene:2';choice=scene+':choice:0'
                        panel.event_scene_filter.setCurrentIndex(panel.event_scene_filter.findData(scene));gui.processEvents()
                        panel.event_choice_filter.setCurrentIndex(panel.event_choice_filter.findData(choice));gui.processEvents()
                        require([panel.event_stage.itemData(i)for i in range(panel.event_stage.count())]==['ro6_e_t_3'],'original_exact_emergency_battle_reference_retained')
                        panel.event_stage.setCurrentIndex(0);QTest.mouseClick(panel.battle_button,Qt.MouseButton.LeftButton);gui.processEvents()
                        require(stage_requests==['ro6_e_t_3'],'actual_existing_battle_button_emits_only_documented_fixed_preview')
                    if eid=='community_group_023':require(panel.resting_button.isVisible()and panel.resting_button.isEnabled()and'数量不一致'in player,'resting_result_reader_and_documentary_conflicts_remain_available')
                    if eid=='community_group_031':require(panel.curiosity_node_rules_button.isVisible()and panel.curiosity_node_rules_button.isEnabled(),'existing_revisit_rules_reader_entry_remains_available')
                    readings.append({'event_id':eid,'actual_new_result_references':chosen,'player_character_count':len(player),'technical_character_count':len(technical)})
                    if eid in('community_group_008','community_group_015','community_group_023','community_group_031'):shot(eid)
                    later(lambda:visit(index+1))if index+1<len(visits)else later(check_destinations)
                def check_destinations():
                    for eid,original,target,expected in(
                        ('community_group_014','choice_ro6_bat3_2','scene_ro6_bat3_2','选择后的战斗难度（原文）：升级为紧急作战'),
                        ('community_group_023','choice_ro6_surprise_2','scene_ro6_surprise_5','后续奖励分支说明（原文）：随机出现以下2种奖励中的1种')):
                        select(eid);index=panel.destination_choice.findData(original)
                        require(index>=0,'original_destination_choice_exact_ID_still_available')
                        panel.destination_choice.setCurrentIndex(index);QTest.mouseClick(panel.destination_button,Qt.MouseButton.LeftButton);gui.processEvents()
                        win=panel.destination_window
                        require(win.isVisible()and win.result['destination_scene_id']==target and expected in win.detail.toPlainText(),'actual_original_destination_reader_retains_exact_scene_and_annotation')
                        if eid=='community_group_023':
                            require([r['scene_key']for r in win.result['catalog_references']]==[eid+':scene:6',eid+':scene:9',eid+':scene:11'] and '数量不一致'in win.detail.toPlainText(),'original_destination_retains_all_three_documentary_candidates_and_conflicts')
                        destinations.append({'original_choice_id':original,'destination_scene_id':target,'exact_catalog_scene_keys':[r['scene_key']for r in win.result['catalog_references']],'stage_candidates':[win.stage.itemData(i)for i in range(win.stage.count())],'native_window':native(win,'original-destination')})
                        win.close();gui.processEvents()
                    later(check_refresh)
                def check_refresh():
                    select('community_group_023')
                    for widget in(panel.player_detail,panel.detail):
                        panel.reading_tabs.setCurrentWidget(widget);gui.processEvents()
                        cursor=widget.textCursor();cursor.setPosition(4);cursor.setPosition(18,QTextCursor.MoveMode.KeepAnchor);widget.setTextCursor(cursor)
                        bar=widget.verticalScrollBar();require(bar.maximum()>0,'unmodified_actual_reader_content_has_scroll')
                        bar.setValue(min(25,bar.maximum()));before_state=(cursor.anchor(),cursor.position(),cursor.selectedText(),bar.value());selected=panel.list.selected_key()
                        panel.refresh();gui.processEvents();c=widget.textCursor();after_state=(c.anchor(),c.position(),c.selectedText(),bar.value())
                        require(panel.list.selected_key()==selected and panel.reading_tabs.currentWidget()is widget and before_state==after_state,'same_event_preserves_real_scroll_nonempty_selection_and_player_technical_tab')
                        refreshes.append({'tab':panel.reading_tabs.indexOf(widget),'before':list(before_state),'after':list(after_state)})
                    later(check_negative)
                def check_negative():
                    nonlocal negative,done
                    select('community_group_008');identity=next(k for k in identities if k[0]=='community_group_008')
                    literal=model.choice_reference(*identity)['reference']['text'];clone=temp/'public-source-clone'
                    manifest=read(ROOT/MANIFEST);names=[MANIFEST,*manifest['runtime_files']]
                    for name in names:
                        dest=clone/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((ROOT/name).read_bytes())
                    with patch.object(model,'ROOT',clone):
                        require(model.choice_reference(*identity)['source_valid']is True,'manifest_and_five_runtime_members_warm_clone_valid')
                        path=clone/model.AUTHORITY;raw=path.read_bytes();path.write_bytes(raw+b' ')
                        try:
                            panel.refresh();gui.processEvents();text=panel.player_detail.toPlainText()
                            failed=model.choice_reference(*identity)
                            require(failed['role']is None and failed['reference']is None and'附注原文（类型待核对）：'+literal in text
                                and'选择后可能的战斗（原文）：'not in text and literal in panel.detail.toPlainText(),'real_bad_source_clears_old_role_but_preserves_literal_original_text')
                            shot('source-unavailable-raw-note-preserved')
                        finally:path.write_bytes(raw)
                        panel.refresh();gui.processEvents()
                        require('选择后可能的战斗（原文）：'in panel.player_detail.toPlainText(),'source_recovery_reads_fresh_role_and_preserves_original_event')
                        negative={'copied_exact_public_files':names,'damaged_source':model.AUTHORITY,'restored_exact_bytes':path.read_bytes()==raw,'preserved_literal':literal}
                    require(len([r for x in readings for r in x['actual_new_result_references']])==10 and len(requirements)==4,'all_ten_new_result_rows_and_four_true_requirements_read')
                    require(panel.runtime_context==runtime_before and all(v==0 for v in attempts.values()),'runtime_context_unchanged_and_eight_external_counters_zero')
                    done=True;close_all();gui.exit(0)
                def timeout():
                    if not done:fail(TimeoutError('The native reading fixture did not finish by its explicit deadline.'))
                try:
                    native(panel,'directory');later(lambda:visit(0),300);QTimer.singleShot(args.visible_ms,timeout)
                    qt_exit=gui.exec();require(qt_exit==0 and done and closed,'actual_Qt_exec_success_and_owned_readers_closed')
                finally:close_all()
            after=bound_files();require(before==after,'selected_public_sources_unchanged_after_actual_window_close')
        except BaseException as error:
            if failure is None:failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
    if panel is not None:
        try:
            if panel.destination_window is not None:panel.destination_window.close()
            panel.close()
            if gui is not None:gui.processEvents()
            closed=not panel.isVisible()and(panel.destination_window is None or not panel.destination_window.isVisible())
        except BaseException as error:
            if failure is None:failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
    if before and not after:
        try:after=bound_files()
        except BaseException:pass
    report={'section':307,'kind':'isolated_native_windows_choice_annotation_reading','passed':done and failure is None and qt_exit==0 and closed,
        'failure':failure,'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'qpa':qpa,'process_id':os.getpid(),
        'qt_exit_code':qt_exit,'verification_window_closed':closed,'checks':checks,'unique_checks':len(checks),
        'successful_assertion_executions_including_repeated_guards':assertions,'actual_event_readings':readings,
        'actual_true_requirement_readings':requirements,'actual_original_destination_readings':destinations,
        'same_event_refresh_observations':refreshes,'source_negative_fixture':negative,'screenshots':images,'screenshot_count':len(images),
        'native_observations':handles,'source_sha256_before':before,'source_sha256_after':after,
        'selected_sources_not_all_transitive_dependencies':True,'temporary_state_root':True,
        'state_paths_replaced_before_constructor':['ROOT','SETTINGS','OPERATOR_STATE','RUN_STATE'],
        'external_operation_attempts':attempts,'private_state_read_copied_or_restored':False,'game_operated':False,'game_captures':0,'chat_sent':False,
        'actual_game_option_eligibility_or_result_verified':False,'actual_full_MainWindow_or_process_descendant_closure_claimed':False,
        'scope':'Manual NodeCatalogPanel and OriginalDestinationPanel documentary reading only; unchanged source checks/status and current actual state are not inferred from result labels.'}
    with destination.open('x',encoding='utf8')as stream:stream.write(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    return 0 if report['passed']else 1

if __name__=='__main__':raise SystemExit(main())
