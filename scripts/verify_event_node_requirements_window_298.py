"""Unexecuted native298 draft: fixed natural-main-floor conditions in real MainWindow.
Root owns promotion, final source freeze and the only supervised actual run.
No actual event generation, current-server qualification or game/chat validation.
"""
import argparse
from contextlib import ExitStack
from copy import deepcopy
from datetime import datetime,timezone
import hashlib,json,os
from pathlib import Path
import sys,tempfile,traceback
from unittest.mock import patch

ROOT=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file())
sys.path.insert(0,str(ROOT))
CANONICAL='scripts/verify_event_node_requirements_window_298.py'
PACKET='research/p3-event-node-requirements-298'
MANIFEST=PACKET+'/source-manifest.json';DATA='rouge/data/event-node-requirements.json'
MANIFEST_SHA='38638685b5b5084cbd3e81ff1c288a6d89c97c67cdc34fa72299a7997aa621ed'
DATA_SHA='f11c6d83a048ffdea14cbccdd1506ff02c3ef35a1cf94f107e30845b2d1deab3'
RULES={'community_group_024':[1,5,6],'community_group_025':[1,6],
 'community_group_027':[1,2,6],'community_group_028':[1,2,6],
 'community_group_029':[1,2,6],'community_group_037':[1]}
CHECK='documented_node_natural_main_floor';SIZE=(1050,720)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def read(path):return json.loads(path.read_bytes())
def text_sha(text):return hashlib.sha256(text.encode('utf8')).hexdigest()
def bound_files():
 names={CANONICAL,'rouge/app.py','rouge/node_catalog.py','rouge/event_planning.py',
  'rouge/node_catalog_view.py','rouge/player_node_information.py','rouge/ui_state.py','rouge/branch_choice.py',
  'rouge/event_node_requirements.py',DATA,MANIFEST,'rouge/data/node-catalog.json',
  'rouge/data/event-planning-reference.json','scripts/build_event_node_requirements_298.py',
  'tests/test_event_node_requirements_298.py','tests/test_event_node_requirements_integration_298.py',
  'tests/test_event_node_requirements_view_298.py'}
 names.update(read(ROOT/MANIFEST)['files'])
 names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/PACKET).rglob('*')if p.is_file())
 result={}
 for name in sorted(names):
  path=ROOT/name
  if not path.is_file()or path.is_symlink()or not path.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Regular selected public source required: '+name)
  result[name]=sha(path)
 return result

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--receipt',required=True)
 parser.add_argument('--visible-ms',type=int,default=120000);args=parser.parse_args()
 destination=Path(args.receipt).resolve()
 if destination.exists():raise FileExistsError('Preserve original actual receipt.')
 if args.visible_ms<=0:raise ValueError('Positive visible interval required.')
 destination.parent.mkdir(parents=True,exist_ok=True)
 started=datetime.now(timezone.utc).isoformat();before={};after={};checks=[];images=[];handles=[]
 matrix=[];contexts=[];negatives=[];refreshes=[];executions=0;failure=None;done=False;closed=False;qpa=None;qt_exit=None
 attempts={name:0 for name in('game_enumeration','game_connect','game_capture','game_next_frame',
  'desktop_start','desktop_request','provider_chat','credential_read')}
 def require(value,label):
  nonlocal executions
  if not value:raise AssertionError(label)
  executions+=1
  if label not in checks:checks.append(label)
 def forbidden(name):
  def blocked(*_,**__):attempts[name]+=1;raise AssertionError('Forbidden original external entry: '+name)
  return blocked
 try:
  if sys.platform!='win32':raise RuntimeError('Actual native Windows required.')
  if Path(__file__).resolve()!=(ROOT/CANONICAL).resolve():raise RuntimeError('Unpromoted cache draft cannot be acceptance.')
  require(sha(ROOT/MANIFEST)==MANIFEST_SHA and sha(ROOT/DATA)==DATA_SHA,'fixed_new_requirement_source_and_data_before_window')
  from rouge import event_node_requirements as model
  from rouge import node_catalog as catalog
  require(model.source_data()is not None,'actual_new_requirement_packet_valid_before_Qt')
  for identity,floors in RULES.items():
   ref=model.event_requirements(identity,floor=1,entry_mode='natural')
   require(ref['source_valid']is True and ref['documented_excluded_main_floors']==floors,'six_exact_source_identities_and_negative_lists')
  before=bound_files()
  from PySide6.QtCore import Qt,QTimer
  from PySide6.QtGui import QTextCursor
  from PySide6.QtWidgets import QApplication
  from PySide6.QtTest import QTest
  import win32gui,win32process
  from rouge import app as app_module
  gui=QApplication([]);qpa=gui.platformName();require(qpa=='windows','native_windows_QPA')
  class PublicWindow(app_module.MainWindow):
   def refresh_windows(self):self.windows.clear()
  with tempfile.TemporaryDirectory(prefix='rouge-298-floor-window-')as folder,ExitStack()as stack:
   temporary=Path(folder)
   for key,value in{'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():
    stack.enter_context(patch.object(app_module,key,value))
   stack.enter_context(patch.object(app_module,'list_game_windows',side_effect=forbidden('game_enumeration')))
   for method,name in[('connect','game_connect'),('capture','game_capture'),('next_frame','game_next_frame')]:
    stack.enter_context(patch.object(app_module.GameCapture,method,side_effect=forbidden(name)))
   for method,name in[('start','desktop_start'),('request','desktop_request')]:stack.enter_context(patch.object(app_module.DesktopBackend,method,side_effect=forbidden(name)))
   stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')))
   stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
   window=PublicWindow()
   try:
    window.setWindowTitle('第298节 · 节点自然主层条件（公开隔离验收）');window.resize(*SIZE);window.show()
    panel=window.node_catalog;tabs=window.centralWidget();initial_run=deepcopy(window.run.state)
    initial_selection=panel.list.selected_key();queue=[(identity,floor)for identity in RULES for floor in range(1,7)]
    index=0;saved=None
    def isolated():
     require(not window.auto.isChecked()and not window.timer.isActive(),'automatic_sampling_and_timer_disabled')
     require(window.capture.target is None and window.desktop.process is None,'capture_and_desktop_backend_inactive')
     require(all(n==0 for n in attempts.values()),'all_eight_external_entry_attempts_zero')
    def native():
     hwnd=int(window.winId());thread,pid=win32process.GetWindowThreadProcessId(hwnd)
     require(win32gui.IsWindow(hwnd)and win32gui.IsWindowVisible(hwnd)and window.isVisible(),'actual_owned_MainWindow_HWND_visible')
     require(pid==os.getpid()and not win32gui.IsIconic(hwnd),'actual_fixture_PID_owns_nonminimized_HWND')
     require([window.width(),window.height()]==list(SIZE),'actual_MainWindow_client_size_exact')
     return{'kind':'parent','hwnd':hwnd,'process_id':pid,'thread_id':thread,'qpa':qpa,'client_size':[window.width(),window.height()]}
    def choose(control,value):
     at=control.findData(value);require(at>=0,'exact_declared_control_value_present');control.setCurrentIndex(at)
    def event(identity):
     title=catalog._event(identity)['title'];panel.search.setText(title)
     selected=next(i for i,e in enumerate(panel.entries)if e['kind']=='event'and e['record']['id']==identity)
     tabs.setCurrentWidget(panel);item=panel.list.flat[selected];item.parent().setExpanded(True)
     panel.list.scrollToItem(item);gui.processEvents();rect=panel.list.visualItemRect(item)
     require(not rect.isEmpty()and panel.list.viewport().rect().contains(rect.center()),'actual_manual_tree_item_inside_visible_viewport')
     QTest.mouseClick(panel.list.viewport(),Qt.MouseButton.LeftButton,pos=rect.center());gui.processEvents()
     require(panel.entries[selected]['record']['id']==identity and panel.list.selected_key()==panel.entries[selected]['key'],'manual_exact_event_identity_selected_not_title_alias')
     return panel.entries[selected]
    def directory(identity,floor,context=None):
     panel.show_directory();panel.set_map_context(None,runtime_context=context or {})
     choose(panel.kind,'event');choose(panel.node_type,None);choose(panel.floor,floor)
     return event(identity)
    def new_checks(entry):return[r for r in entry['qualification']['checks']if r['key']==CHECK]
    def reader(widget):
     cursor=widget.textCursor();return{'sha256':text_sha(widget.toPlainText()),'anchor':cursor.anchor(),'position':cursor.position(),
      'selected':cursor.selectedText(),'vertical':widget.verticalScrollBar().value(),'horizontal':widget.horizontalScrollBar().value()}
    def state():
     return{'key':panel.list.selected_key(),'search':panel.search.text(),'search_cursor':panel.search.cursorPosition(),
      'search_selected':panel.search.selectedText(),'kind':panel.kind.currentData(),'floor':panel.floor.currentData(),
      'node_type':panel.node_type.currentData(),'scene':panel.event_scene_filter.currentData(),
      'choice':panel.event_choice_filter.currentData(),'stage':panel.event_stage.currentData(),
      'tab':panel.reading_tabs.currentIndex(),'player':reader(panel.player_detail),'technical':reader(panel.detail),
      'expanded':sorted(panel.list.expanded_groups()),'list_scroll':panel.list.verticalScrollBar().value()}
    def select_text(widget,scroll=False):
     cursor=widget.textCursor();require(widget.document().characterCount()>17,'real_existing_reader_text_available')
     cursor.setPosition(5);cursor.setPosition(16,QTextCursor.MoveMode.KeepAnchor);widget.setTextCursor(cursor)
     if scroll:
      bar=widget.verticalScrollBar();require(bar.maximum()>0,'real_existing_reader_has_nonzero_scroll_range')
      bar.setValue(max(1,bar.maximum()//2));require(bar.value()>0,'actual_reader_nonzero_scroll_set')
     require(bool(widget.textCursor().selectedText()),'actual_reader_nonempty_selection')
    def screenshot(name):
     isolated();handle=native();file=destination.with_name(destination.stem+'-'+name+'.png')
     if file.exists():raise FileExistsError('Preserve first actual PNG.')
     image=window.grab();require(not image.isNull()and image.save(str(file),'PNG'),'actual_owned_native_PNG_saved')
     images.append({'name':name,'path':str(file),'sha256':sha(file),'native_window':handle})
    def fail(error):
     nonlocal done,failure
     failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()};done=False;window.close();gui.exit(1)
    def later(callback,delay=100):
     def guarded():
      try:isolated();callback()
      except BaseException as error:fail(error)
     QTimer.singleShot(delay,guarded)
    def matrix_step():
     nonlocal index
     identity,floor=queue[index];entry=directory(identity,floor);rows=new_checks(entry);match=floor not in RULES[identity]
     require(len(rows)==1 and rows[0]['kind']=='source_node_floor_requirement'and rows[0]['matches']is match,
      'actual_directory_natural_main_floor_check_matches_exact_source_rule')
     require(entry['qualification']['actual_server_eligible']is None and entry['qualification']['all_server_conditions_known']is False,
      'permitted_by_one_rule_never_proves_actual_generation_or_all_conditions')
     if not match:require(entry['qualification']['status']=='excluded'and'已列条件不符'in entry['group'],
      'negative_rule_is_visible_in_manual_readable_excluded_group')
     text=panel.player_detail.toPlainText()
     require(catalog._event(identity)['title']in text and'【自然出现的已知条件】'in text,'default_player_reader_has_chinese_natural_condition_and_full_event')
     require(not any(token in text for token in('community_group_','documented_node_','https://')),'default_player_condition_has_no_code_identifiers_or_URLs')
     matrix.append({'event_id':identity,'floor':floor,'new_check_match':rows[0]['matches'],'overall_status':entry['qualification']['status'],
      'group':entry['group'],'actual_server_eligible':None})
     index+=1
     if index<len(queue):later(matrix_step,40)
     else:later(retention_prime)
    def retention_prime():
     nonlocal saved
     directory('community_group_024',1);panel.reading_tabs.setCurrentWidget(panel.detail);gui.processEvents()
     select_text(panel.player_detail);select_text(panel.detail,True);panel.search.setSelection(0,2);saved=state()
     screenshot('directory-excluded');later(retention_step)
    def retention_step():
     panel.refresh();gui.processEvents();require(state()==saved,'same_context_refresh_preserves_filters_full_identity_tab_selection_and_nonzero_scroll')
     refreshes.append({'iteration':len(refreshes)+1,'event_key':panel.list.selected_key(),'technical_scroll':panel.detail.verticalScrollBar().value(),
      'text_selection':panel.detail.textCursor().selectedText(),'same_state':True})
     if len(refreshes)<3:later(retention_step)
     else:later(nonapplicable)
    def nonapplicable():
     identity='community_group_024'
     for label,floor,context in[('unknown_floor',None,{}),('special_region',1,{'special_region':True})]:
      entry=directory(identity,floor,context)
      require(not new_checks(entry),'nonapplicable_context_does_not_add_natural_floor_negative_check')
      ref=model.event_requirements(identity,floor=floor,entry_mode='natural',special_region=bool(context.get('special_region')))
      require(ref['context_applicable']is False and ref['documented_floor_match']is None,'source_reference_does_not_apply_negative_rule_outside_main_floor_context')
      contexts.append({'kind':label,'event_id':identity,'natural_new_check_count':0,'actual_server_eligible':None})
     later(observed_current)
    def fixture_graph(past=False):
     identity='community_group_024';record=catalog._event(identity)
     content={'kind':'event','title':record['title'],'source':'same_frame_selected_node','identity_status':'visible_scene',
      'scene_candidates':deepcopy(record['scenes'][0]['game_scene_ids'])}
     node={'id':'public-reference-node','row':0,'col':0,'observed_type':'林间空地'if past else record['node_types'][0]}
     if past:node.update(remembered_type=record['node_types'][0],remembered_content=content)
     else:node['content']=content
     return{'zone_id':'zone_1','template_id':'public298-context','nodes':[node]}
    def observed_current():
     graph=fixture_graph();before_graph=deepcopy(graph)
     panel.search.clear();panel.set_map_context(graph,{'floor':1,'special_region':False},epoch='public298',historical=False)
     panel.set_node(graph,'public-reference-node',floor=1,special_region=False);panel.bind_current_node();entry=event('community_group_024')
     require(not new_checks(entry)and panel._event_context(entry['record'])['entry_mode']=='content',
      'actual_current_title_is_content_reference_not_rejected_natural_generation')
     require(graph==before_graph and catalog._event('community_group_024')['title']in panel.player_detail.toPlainText(),
      'observed_title_preserved_readable_and_input_graph_unchanged')
     contexts.append({'kind':'current_content','event_id':'community_group_024','natural_new_check_count':0,'title_retained':True})
     screenshot('current-title');later(observed_history)
    def observed_history():
     graph=fixture_graph(True);before_graph=deepcopy(graph)
     panel.search.clear();panel.set_map_context(graph,{'floor':1,'special_region':False},epoch='public298-history',historical=True)
     panel.set_node(graph,'public-reference-node',floor=1,special_region=False);panel.bind_current_node();entry=event('community_group_024')
     context=panel._event_context(entry['record'])
     require(entry.get('history_read')is True and context['entry_mode']=='content'and context['reference_context_scope']=='historical_title_reference_only'
      and not new_checks(entry),'remembered_title_is_separate_historical_read_not_erased_by_current_negative_floor')
     require(graph==before_graph and catalog._event('community_group_024')['title']in panel.player_detail.toPlainText(),
      'history_title_preserved_readable_and_input_graph_unchanged')
     contexts.append({'kind':'historical_title','event_id':'community_group_024','natural_new_check_count':0,'title_retained':True})
     screenshot('historical-title');later(source_failure)
    def source_failure():
     entry=directory('community_group_024',1);key=panel.list.selected_key();require(new_checks(entry)[0]['matches']is False,'source_negative_starts_from_real_warm_exclusion')
     manifest=read(ROOT/MANIFEST);clone=temporary/'public-source-negative'
     for name in set(manifest['files'])|{MANIFEST}:
      original=ROOT/name;require(original.is_file()and not original.is_symlink()and original.resolve().is_relative_to(ROOT.resolve()),'source_negative_copies_only_regular_public_members')
      target=clone/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(original.read_bytes())
     target=clone/MANIFEST;raw=target.read_bytes()
     with patch.object(model,'ROOT',clone):
      require(model.source_data()is not None and model.event_requirements('community_group_024',floor=1,entry_mode='natural')['documented_floor_match']is False,
       'complete_public_source_clone_valid_before_warm_damage')
      try:
       target.write_bytes(raw+b' ');panel.refresh();gui.processEvents();entry=next(e for e in panel.entries if e['key']==key);rows=new_checks(entry)
       require(len(rows)==1 and rows[0]['matches']is None and'不能据此排除'in rows[0]['source_text'],
        'warm_source_failure_clears_old_negative_rule_to_unknown_without_exclusion')
       text=panel.player_detail.toPlainText()
       require('暂时无法核对'in text and'资料记载：先行一步不会自然出现在'not in text and'已知开启途径：'not in text,
        'source_failure_player_clears_old_specific_natural_floor_list')
       require('已列条件不符'not in entry['group'],'source_failure_clears_prior_negative_group_not_only_reader_text')
       require(panel.list.selected_key()==key and entry['qualification']['actual_server_eligible']is None,
        'source_failure_keeps_manual_reference_identity_without_positive_eligibility')
       screenshot('source-unavailable')
      finally:target.write_bytes(raw)
      require(sha(target)==MANIFEST_SHA,'public_source_negative_restores_exact_original_bytes')
      panel.refresh();gui.processEvents();entry=next(e for e in panel.entries if e['key']==key)
      require(panel.list.selected_key()==key and new_checks(entry)[0]['matches']is False,'source_restore_revalidates_existing_manual_choice_not_another_event')
     negatives.append({'kind':'warm_manifest','manifest':MANIFEST,'damaged_member':MANIFEST,'public_clone_only':True,
      'restored_sha256':sha(target),'actual_server_eligible':None})
     screenshot('restored-reading');later(finish)
    def finish():
     nonlocal done
     require(len(matrix)==36 and{(r['event_id'],r['floor'])for r in matrix}==set(queue),'all_six_events_and_six_main_floors_actually_read')
     require({r['kind']for r in contexts}=={'unknown_floor','special_region','current_content','historical_title'},'all_nonapplicable_and_observed_contexts_exercised')
     require(len(refreshes)==3 and all(r['technical_scroll']>0 and r['text_selection']for r in refreshes),'actual_nonzero_scroll_and_selection_retained_across_three_refreshes')
     require(window.run.state==initial_run,'manual_condition_reference_never_changes_temporary_run_memory')
     require(bound_files()==before,'selected_public_sources_stable_before_completion');handles.append(native());done=True
    def deadline():
     nonlocal failure
     if not done and failure is None:failure={'type':'TimeoutError','message':'Natural-main-floor checks incomplete.'}
     window.close()
    later(matrix_step,500);QTimer.singleShot(max(30000,args.visible_ms),deadline)
    qt_exit=gui.exec();closed=not window.isVisible()
    if qt_exit!=0 or not closed or not done:
     if failure is None:failure={'type':'RuntimeError','message':'Actual checks/Qt/owned-window closure incomplete.'}
    if failure is None:isolated()
    after=bound_files()
    if before!=after and failure is None:failure={'type':'AssertionError','message':'Selected sources changed before closure.'}
   finally:window.close();gui.processEvents();closed=not window.isVisible()
 except BaseException as error:failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
 report={'section':298,'kind':'isolated_native_windows_event_node_requirements','passed':done and failure is None,
  'failure':failure,'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'process_id':os.getpid(),
  'qpa':qpa,'qt_exit_code':qt_exit,'verification_window_closed':closed,'checks':checks,'unique_checks':len(checks),
  'successful_assertion_executions_including_repeated_guards':executions,'requested_parent_client_size':list(SIZE),
  'native_observations':handles,'screenshots':images,'screenshot_count':len(images),'main_floor_observations':matrix,
  'nonapplicable_and_observed_contexts':contexts,'same_scope_refresh_observations':refreshes,'source_negative_fixtures':negatives,
  'initial_directory_selection':initial_selection if'initial_selection'in locals()else None,
  'new_forced_no_selection_policy_applied':False,
  'source_sha256_before':before,'source_sha256_after':after,'source_guard_is_selected_not_all_transitive_dependencies':True,
  'temporary_state_root':True,'state_paths_replaced_before_constructor':['ROOT','SETTINGS','OPERATOR_STATE','RUN_STATE'],
  'private_state_read_copied_or_restored':False,'external_operation_attempts':attempts,'external_entrypoints_blocked_before_original_call':True,
  'game_operated':False,'game_captures':0,'chat_sent':False,'chat_attempted':bool(attempts['desktop_request']or attempts['provider_chat']),
  'original_project_window_operated_or_restarted':False,'actual_process_termination_verified_by_this_script':False,
  'owned_supervisor_exit_and_cleanup_required_separately':True,'launch_Popen_PID_must_be_recorded_separately_from_actual_fixture_PID':True,
  'scope':'Six fixed source main-floor negative rules in a real manual node reader,36 main-floor contexts, source invalidation and observed/history preservation; no actual generation, probability, game, chat or full validation.'}
 with destination.open('x',encoding='utf8')as stream:stream.write(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 return 0 if report['passed']else 1

if __name__=='__main__':raise SystemExit(main())
