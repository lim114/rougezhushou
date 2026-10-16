"""Cache candidate: actual isolated MainWindow next-region reference reading.
Root reviews final pins, promotes and explicitly supervises the only actual run.
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
CANONICAL='scripts/verify_future_region_effects_window_300.py'
PACKET='research/p3-future-region-effects-300';MANIFEST=PACKET+'/source-manifest.json';DATA='rouge/data/future-region-effects.json'
MANIFEST_SHA='1bbc5d7eb9b872cc2ed4b0857b011c4ffbdd05b440372a9e060932531ab39894'
DATA_SHA='ef6d699cb48318f9bab1895fa84d8bc78dcb64439a51a9da6b14f9c34ac7a367'
EVENT='community_group_009';OTHER='community_group_021'
CHOICES=tuple(EVENT+':scene:0:choice:'+str(i)for i in range(2))
SIZE=(1050,720);DIALOG_SIZE=(900,680)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def text_sha(text):return hashlib.sha256(text.encode('utf8')).hexdigest()
def bound_files():
 names={CANONICAL,MANIFEST,DATA,'rouge/app.py','rouge/node_catalog_view.py','rouge/node_catalog.py',
  'rouge/event_planning.py','rouge/player_node_information.py','rouge/ui_state.py','rouge/branch_choice.py',
  'rouge/future_region_effects.py','rouge/future_region_effects_view.py',
  'scripts/build_future_region_effects_300.py','tests/test_future_region_effects_300.py',
  'tests/test_future_region_effects_view_300.py','tests/test_future_region_integration_300.py'}
 names.update(read(ROOT/MANIFEST)['files'])
 names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/PACKET).rglob('*')if p.is_file())
 result={}
 for name in sorted(names):
  p=ROOT/name
  if not p.is_file()or p.is_symlink()or not p.resolve().is_relative_to(ROOT.resolve()):
   raise ValueError('Regular selected public source required: '+name)
  result[name]=sha(p)
 return result
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--receipt',required=True)
 parser.add_argument('--visible-ms',type=int,default=120000);args=parser.parse_args()
 destination=Path(args.receipt).resolve()
 if destination.exists():raise FileExistsError('Preserve first actual receipt.')
 if args.visible_ms<=0:raise ValueError('Positive visible interval required.')
 destination.parent.mkdir(parents=True,exist_ok=True);started=datetime.now(timezone.utc).isoformat()
 before={};after={};checks=[];executions=0;images=[];handles=[];rows=[];phases=[];refreshes=[];negatives=[]
 failure=None;done=False;closed=False;qpa=None;qt_exit=None
 attempts={k:0 for k in('game_enumeration','game_connect','game_capture','game_next_frame','desktop_start','desktop_request','provider_chat','credential_read')}
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
  if Path(__file__).resolve()!=(ROOT/CANONICAL).resolve():raise RuntimeError('Cache script is not acceptance.')
  require(type(MANIFEST_SHA)is str and type(DATA_SHA)is str and sha(ROOT/MANIFEST)==MANIFEST_SHA and sha(ROOT/DATA)==DATA_SHA,
   'final_documented_authority_and_data_exact_before_actual_window')
  before=bound_files()
  from rouge import future_region_effects as model
  from rouge import node_catalog as catalog
  packet=model.event_reference(EVENT,mode='NORMAL',difficulty=2)
  require(packet['source_valid']is True and packet['documented_phase']=='early','actual_fixed_reference_valid_before_Qt')
  from PySide6.QtCore import Qt,QPoint,QRect,QTimer
  from PySide6.QtGui import QTextCursor
  from PySide6.QtWidgets import QApplication
  from PySide6.QtTest import QTest
  import win32gui,win32process
  from rouge import app as app_module
  gui=QApplication([]);qpa=gui.platformName();require(qpa=='windows','actual_windows_QPA')
  class PublicWindow(app_module.MainWindow):
   def refresh_windows(self):self.windows.clear()
  with tempfile.TemporaryDirectory(prefix='rouge-300-future-region-')as folder,ExitStack()as stack:
   temporary=Path(folder)
   for key,value in{'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():
    stack.enter_context(patch.object(app_module,key,value))
   stack.enter_context(patch.object(app_module,'list_game_windows',side_effect=forbidden('game_enumeration')))
   for method,name in[('connect','game_connect'),('capture','game_capture'),('next_frame','game_next_frame')]:
    stack.enter_context(patch.object(app_module.GameCapture,method,side_effect=forbidden(name)))
   for method,name in[('start','desktop_start'),('request','desktop_request')]:
    stack.enter_context(patch.object(app_module.DesktopBackend,method,side_effect=forbidden(name)))
   stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')))
   stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
   window=PublicWindow();dialog=None
   try:
    window.setWindowTitle('第300节 · 下一地区影响（公开隔离验收）');window.resize(*SIZE);window.show()
    panel=window.node_catalog;tabs=window.centralWidget();initial_run=deepcopy(window.run.state)
    parent_saved=None;dialog_saved=None
    def isolated():
     require(not window.auto.isChecked()and not window.timer.isActive(),'automatic_sampling_and_timer_disabled')
     require(window.capture.target is None and window.desktop.process is None,'capture_and_desktop_backend_inactive')
     require(all(v==0 for v in attempts.values()),'all_eight_external_original_entry_attempts_zero')
    def native(widget,kind):
     hwnd=int(widget.winId());thread,pid=win32process.GetWindowThreadProcessId(hwnd);size=SIZE if kind=='parent'else DIALOG_SIZE
     require(win32gui.IsWindow(hwnd)and win32gui.IsWindowVisible(hwnd)and widget.isVisible(),kind+'_actual_owned_visible_HWND')
     require(pid==os.getpid()and not win32gui.IsIconic(hwnd),kind+'_actual_fixture_PID_not_minimized')
     require([widget.width(),widget.height()]==list(size),kind+'_actual_client_size_exact')
     return{'kind':kind,'hwnd':hwnd,'process_id':pid,'thread_id':thread,'qpa':qpa,'client_size':[widget.width(),widget.height()]}
    def choose(control,value):
     at=control.findData(value);require(at>=0,'exact_complete_reference_control_identity_present');control.setCurrentIndex(at);gui.processEvents()
    def event(identity):
     panel.show_directory();choose(panel.kind,'event');choose(panel.floor,None);choose(panel.node_type,None)
     panel.search.setText(catalog._event(identity)['title'])
     index=next(i for i,e in enumerate(panel.entries)if e['kind']=='event'and e['record']['id']==identity)
     panel.list.setCurrentRow(index);tabs.setCurrentWidget(panel);gui.processEvents()
     require(panel.entries[index]['record']['id']==identity,'actual_public_directory_exact_event_selected')
    def context(mode,difficulty):
     panel.set_map_context(None,runtime_context={'exploration_mode':mode,'difficulty':difficulty});event(EVENT)
     require(dialog.mode==mode and type(dialog.difficulty)is type(difficulty)and dialog.difficulty==difficulty,
      'actual_parent_passes_exploration_mode_and_exact_difficulty_to_owned_reader')
    def reader(w):
     c=w.textCursor();return{'text_sha256':text_sha(w.toPlainText()),'anchor':c.anchor(),'position':c.position(),
      'selected':c.selectedText(),'vertical':w.verticalScrollBar().value(),'horizontal':w.horizontalScrollBar().value()}
    def parent_state():
     return{'key':panel.list.selected_key(),'tab':panel.reading_tabs.currentIndex(),'scene':panel.event_scene_filter.currentData(),
      'choice':panel.event_choice_filter.currentData(),'stage':panel.event_stage.currentData(),'search':panel.search.text(),
      'search_cursor':panel.search.cursorPosition(),'search_selection':panel.search.selectedText(),
      'player':reader(panel.player_detail),'source':reader(panel.detail)}
    def dialog_state():
     return{'event':dialog.event_id,'scope':deepcopy(dialog.scope_key),'mode':dialog.mode,'difficulty':dialog.difficulty,
      'choice':dialog.choice.currentData(),'tab':dialog.reading_tabs.currentIndex(),'view_key':deepcopy(dialog._view_key),
      'player':reader(dialog.player_text),'source':reader(dialog.source_text)}
    def prime(w,scroll=False):
     gui.processEvents();require(w.document().characterCount()>30,'actual_existing_reader_text_can_be_selected')
     c=w.textCursor();c.setPosition(5);c.setPosition(25,QTextCursor.MoveMode.KeepAnchor);w.setTextCursor(c)
     if scroll:
      bar=w.verticalScrollBar();require(bar.maximum()>0,'actual_existing_reader_has_real_scroll_range')
      bar.setValue(max(1,bar.maximum()//2));require(bar.value()>0,'actual_existing_reader_nonzero_scroll_set')
     require(bool(w.textCursor().selectedText()),'actual_existing_reader_nonempty_selection')
    def click(button,owner,label):
     gui.processEvents();rect=QRect(button.mapTo(owner,QPoint(0,0)),button.size())
     require(button.isVisible()and button.isEnabled()and not button.visibleRegion().isEmpty()and owner.rect().contains(rect),
      label+'_visible_enabled_inside_actual_client')
     QTest.mouseClick(button,Qt.MouseButton.LeftButton,pos=button.rect().center());gui.processEvents()
    def selected_row():
     return next(r for r in dialog.packet['choices']if r['reference_id']==dialog.choice.currentData())
    def actual_unknown(p):
     fields=('actual_choice','actual_weather','actual_phase','actual_affected_nodes','actual_reward','actual_quantity')
     require(all(k in p and p[k]is None for k in fields)and p['calculation_applied']is False and p['run_state_updated']is False,
      'all_six_actual_packet_fields_unknown_and_no_calculation_or_run_write')
     require(len(p['choices'])==2 and all(all(k in r and r[k]is None for k in fields)for r in p['choices']),
      'all_six_actual_fields_on_both_exact_choices_remain_unknown')
     require(all(r['conditional_victory_reward']['resource']=='random_scrap'and all(
      r['conditional_victory_reward'][k]is None for k in('quantity_reference','complete_pool','actual_received'))for r in p['choices']),
      'victory_reference_keeps_quantity_complete_pool_and_actual_received_unknown')
    def select_choice(key):
     row=next(r for r in dialog.packet['choices']if r['choice_key']==key);choose(dialog.choice,row['reference_id']);return selected_row()
    def player():
     dialog.reading_tabs.setCurrentWidget(dialog.player_text);gui.processEvents();return dialog.player_text.toPlainText()
    def screenshot(name):
     isolated();require(dialog.reading_tabs.currentWidget()is dialog.player_text,'actual_representative_screenshot_shows_new_player_text')
     handle=native(dialog,'dialog');p=destination.with_name(destination.stem+'-'+name+'.png')
     if p.exists():raise FileExistsError('Preserve first actual representative PNG.')
     pixels=dialog.grab();require(not pixels.isNull()and pixels.save(str(p),'PNG'),'actual_owned_native_PNG_saved')
     images.append({'name':name,'path':str(p),'sha256':sha(p),'native_window':handle,'direct_player_text':True})
    def phase_read(mode,difficulty,expected):
     context(mode,difficulty);select_choice(CHOICES[1]);text=player();p=dialog.packet
     require(p['documented_phase']==expected and len(p['choices'])==2 and len(p['phases'])==3,
      'documented_phase_matches_only_supported_context_without_removing_manual_references')
     actual_unknown(p)
     values=[(r['phase'],r['attack_percent'],r['max_hp_percent'])for r in selected_row()['future_region_reference']['phases']]
     require(values==[('early',10,10),('middle',15,20),('late',20,30)],'all_three_documented_attribute_rows_exact_and_separate_from_current_panel')
     if expected is None:require('当前没有可确定的文献阶段'in text,'unsupported_context_never_defaults_to_early')
     else:require({'early':'早期','middle':'中期','late':'晚期'}[expected]+'（当前难度的文献阶段）'in text,
      'actual_player_text_names_documented_reference_phase')
     phases.append({'mode':mode,'difficulty':difficulty,'documented_phase':expected,'manual_choices':len(p['choices']),
      'manual_phases':len(p['phases']),'actual_generated_phase':None})
    def close_owned():
     if panel.future_region_window is not None:panel.future_region_window.close()
     window.close()
    def later(callback,delay=200):
     def guarded():
      nonlocal failure,done
      try:isolated();callback()
      except BaseException as error:
       failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()};done=False;close_owned();gui.exit(1)
     QTimer.singleShot(delay,guarded)
    def begin():
     nonlocal parent_saved
     panel.set_map_context(None,runtime_context={'exploration_mode':'NORMAL','difficulty':2});event(EVENT)
     panel.reading_tabs.setCurrentWidget(panel.detail);prime(panel.detail,True);panel.search.setSelection(0,2);parent_saved=parent_state()
     require(panel.future_region_window is None and panel.future_region_button.isVisible()and panel.future_region_button.isEnabled(),
      'exact_event_has_manual_entry_and_dialog_is_not_precreated')
     handles.append(native(window,'parent'));click(panel.future_region_button,window,'actual_MainWindow_future_region_entry_QTest_click');later(opened)
    def opened():
     nonlocal dialog
     dialog=panel.future_region_window;require(dialog is not None and dialog.parent()is panel,'actual_parent_entry_constructs_owned_modeless_reader')
     dialog.resize(*DIALOG_SIZE);gui.processEvents();handles.append(native(dialog,'dialog'))
     require(handles[-1]['hwnd']!=handles[-2]['hwnd'],'actual_parent_and_dialog_distinct_owned_HWNDs')
     require(dialog.event_id==EVENT and dialog.scope_key==panel.list.selected_key()and dialog.mode=='NORMAL'and dialog.difficulty==2,
      'actual_reader_has_exact_event_scope_and_parent_context')
     require(dialog.choice.count()==2 and dialog.choice.currentIndex()==-1 and dialog._view_key is None,
      'two_source_choices_default_unselected_without_automatic_phase_action')
     actual_unknown(dialog.packet)
     require(parent_state()==parent_saved,'opening_new_reader_preserves_actual_parent_reading')
     row=select_choice(CHOICES[0]);text=player()
     require(row['choice_key']==CHOICES[0]and row['game_choice_ids']==[]and len(row['direct_resources'])==1
      and[(r['resource'],r['action'],r['quantity_reference'],r['effect_phase'])for r in row['direct_resources']]==[('gold','gain',30,'on_choice')]
      and row['direct_resources']==read(ROOT/DATA)['choices'][0]['direct_resources'],
      'first_exact_option_direct_thirty_gold_not_future_reward_total')
     require(all(s in text for s in('获得30源石锭','【下一地区的条件效果】','【战斗胜利后的奖励】','随机零件','尚未确认'))
      and not any(s in text for s in('community_group_','rogue_6_','https://')),'actual_first_player_page_separates_chinese_direct_future_and_victory_information')
     rows.append({'choice_key':CHOICES[0],'direct_resources':deepcopy(row['direct_resources']),'actual_selected':None,'actual_reward':None})
     screenshot('player-first-option');later(second)
    def second():
     row=select_choice(CHOICES[1]);text=player()
     require(row['game_choice_ids']==['choice_ro6_normal3_2']and len(row['direct_resources'])==1
      and[(r['resource'],r['action'],r['quantity_reference'],r['effect_phase'])for r in row['direct_resources']]==[('seed','sow',1,'on_choice')]
      and row['direct_resources']==read(ROOT/DATA)['choices'][1]['direct_resources'],
      'second_exact_option_sows_one_seed_not_granted_seed_or_combined_resources')
     require(all(s in text for s in('种下1枚种子','不是领取种子','完整零件池、数量与本局实际领取：尚未确认','不是全队现在获得的加成')),
      'actual_second_player_page_keeps_conditional_attributes_and_unknown_victory_pool_quantity')
     rows.append({'choice_key':CHOICES[1],'direct_resources':deepcopy(row['direct_resources']),'actual_selected':None,'actual_reward':None})
     screenshot('player-second-option');phase_read('NORMAL',2,'early');later(middle)
    def middle():
     nonlocal parent_saved,dialog_saved
     phase_read('NORMAL',6,'middle');screenshot('player-normal-middle')
     panel.reading_tabs.setCurrentWidget(panel.detail);prime(panel.detail,True);panel.search.setSelection(0,2);parent_saved=parent_state()
     prime(dialog.player_text);dialog.reading_tabs.setCurrentWidget(dialog.source_text);prime(dialog.source_text,True)
     dialog_saved=dialog_state();later(refresh_once)
    def refresh_once():
     callbacks=[dialog.refresh_reference,panel.refresh,
      lambda:dialog.set_reference(EVENT,mode='NORMAL',difficulty=6,scope_key=deepcopy(panel.list.selected_key()))]
     callbacks[len(refreshes)]();gui.processEvents()
     require(dialog_state()==dialog_saved and parent_state()==parent_saved,'same_scope_refresh_preserves_dialog_and_parent_complete_actual_reading_state')
     refreshes.append({'path':['dialog','parent','same_reference'][len(refreshes)],'source_scroll':dialog.source_text.verticalScrollBar().value(),
      'source_selection':dialog.source_text.textCursor().selectedText(),'parent_scroll':panel.detail.verticalScrollBar().value(),'parent_unchanged':True})
     if len(refreshes)<3:later(refresh_once)
     else:later(boundaries)
    def boundaries():
     phase_read('NORMAL',12,'late');phase_read('NORMAL',0,None);phase_read('UNKNOWN',6,None);phase_read('NORMAL',1,None)
     screenshot('player-low-difficulty-unknown');later(source_failure)
    def source_failure():
     manifest=read(ROOT/MANIFEST);clone=temporary/'public-authority-negative'
     for name in set(manifest['files'])|{MANIFEST}:
      p=ROOT/name;require(p.is_file()and not p.is_symlink()and p.resolve().is_relative_to(ROOT.resolve()),'source_negative_copies_only_regular_public_authorities')
      out=clone/name;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(p.read_bytes())
     target=clone/MANIFEST;raw=target.read_bytes()
     with patch.object(model,'ROOT',clone):
      require(model.event_reference(EVENT,mode='NORMAL',difficulty=1)['source_valid']is True,'complete_public_source_clone_valid_before_warm_failure')
      try:
       target.write_bytes(raw+b' ');dialog.refresh_reference();panel.refresh();gui.processEvents()
       require(dialog.packet is None and dialog.choice.currentIndex()==-1 and dialog._view_key is None
        and not panel.future_region_button.isEnabled(),'source_failure_clears_previous_choice_reference_and_disables_parent_entry')
       require(all('已清除'in w.toPlainText()for w in(dialog.player_text,dialog.source_text)),
        'source_failure_clears_both_previous_player_and_source_readers')
       player();screenshot('player-source-unavailable')
      finally:target.write_bytes(raw)
      require(sha(target)==MANIFEST_SHA,'temporary_public_authority_restored_exact_bytes')
      dialog.refresh_reference();panel.refresh();gui.processEvents()
      require(dialog.packet is not None and dialog.choice.currentIndex()==-1 and dialog._view_key is None
       and panel.future_region_button.isEnabled(),'restored_sources_require_manual_choice_never_restore_previous_selection')
     negatives.append({'kind':'warm_manifest','manifest':MANIFEST,'damaged_member':MANIFEST,'public_clone_only':True,
      'restored_sha256':sha(target),'actual_generated_or_reward':None});later(non_target)
    def non_target():
     nonlocal done
     event(OTHER)
     require(not panel.future_region_button.isVisible()and dialog.packet is None and dialog.choice.currentIndex()==-1
      and all('已清除'in w.toPlainText()for w in(dialog.player_text,dialog.source_text)),
      'switching_non_target_event_hides_entry_and_clears_all_old_future_region_reading')
     require(len(images)==5 and all(r['direct_player_text']is True for r in images),'five_actual_representative_images_directly_show_new_player_text')
     require(len(refreshes)==3 and all(r['source_scroll']>0 and r['source_selection']and r['parent_scroll']>0 for r in refreshes),
      'actual_three_refreshes_keep_nonzero_parent_and_dialog_scroll_and_selection')
     require(window.run.state==initial_run,'manual_future_region_reader_does_not_write_temporary_run_memory')
     require(bound_files()==before,'selected_public_sources_unchanged_before_completion');handles.append(native(window,'parent'));done=True
    def deadline():
     nonlocal failure
     if not done and failure is None:failure={'type':'TimeoutError','message':'Future-region actual reading checks incomplete.'}
     close_owned()
    later(begin,500);QTimer.singleShot(max(30000,args.visible_ms),deadline);qt_exit=gui.exec()
    closed=not window.isVisible()and not(dialog and dialog.isVisible())
    if qt_exit!=0 or not closed or not done:
     if failure is None:failure={'type':'RuntimeError','message':'Actual checks, Qt or owned windows closure incomplete.'}
    if failure is None:isolated()
    after=bound_files()
    if before!=after and failure is None:failure={'type':'AssertionError','message':'Selected public sources changed before closure.'}
   finally:close_owned();gui.processEvents();closed=not window.isVisible()and not(dialog and dialog.isVisible())
 except BaseException as error:failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
 report={'section':300,'kind':'isolated_native_windows_future_region_effects_reader','passed':done and failure is None,'failure':failure,
  'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'process_id':os.getpid(),'qpa':qpa,'qt_exit_code':qt_exit,
  'verification_window_closed':closed,'checks':checks,'unique_checks':len(checks),'successful_assertion_executions_including_repeated_guards':executions,
  'requested_parent_client_size':list(SIZE),'requested_dialog_client_size':list(DIALOG_SIZE),'native_observations':handles,
  'screenshots':images,'screenshot_count':len(images),'choice_readings':rows,'documented_phase_observations':phases,
  'same_scope_refresh_observations':refreshes,'source_negative_fixtures':negatives,'source_sha256_before':before,'source_sha256_after':after,
  'source_guard_is_selected_not_all_transitive_dependencies':True,'temporary_state_root':True,
  'state_paths_replaced_before_constructor':['ROOT','SETTINGS','OPERATOR_STATE','RUN_STATE'],'private_state_read_copied_or_restored':False,
  'external_operation_attempts':attempts,'external_entrypoints_blocked_before_original_call':True,'game_operated':False,'game_captures':0,
  'chat_sent':False,'chat_attempted':bool(attempts['desktop_request']or attempts['provider_chat']),
  'original_project_window_operated_or_restarted':False,'actual_process_termination_verified_by_this_script':False,
  'owned_supervisor_exit_and_cleanup_required_separately':True,'launch_Popen_PID_must_be_recorded_separately_from_actual_fixture_PID':True,
  'actual_generation_attachment_phase_quantity_pool_reward_or_panel_application_verified':False,
  'scope':'Two exact documented choices and three conditional next-region phases; unknown low-difficulty/other-mode result, no live execution or reward inference.'}
 with destination.open('x',encoding='utf8')as stream:stream.write(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 return 0 if report['passed']else 1
if __name__=='__main__':raise SystemExit(main())
