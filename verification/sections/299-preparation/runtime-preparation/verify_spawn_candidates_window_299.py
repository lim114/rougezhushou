"""Unexecuted native299 draft; root promotes/freezes and supervises actual run.
Only fixed main-queue candidate reading and an independent static preview.
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
CANONICAL='scripts/verify_spawn_candidates_window_299.py'
PACKET='research/p3-spawn-candidates-299';MANIFEST=PACKET+'/source-manifest.json';DATA='rouge/data/spawn-candidates.json'
MANIFEST_SHA='7cba1db922459fea7eddd86a12ad37998bf93e5616ac63e46aa83fc6b6fab08c'
DATA_SHA='aaef1b86a73613ce833a4a5fe2ce39abb6241c0dcc2457fcc00a5b51fd61fbd2'
STAGE='ro6_n_2_1';ORIGIN='w1.f4.a1';OTHER='w1.f4.a8';SIZE=(1050,720);DIALOG_SIZE=(900,680)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def text_sha(s):return hashlib.sha256(s.encode('utf8')).hexdigest()
def bound_files():
 names={CANONICAL,'rouge/app.py','rouge/battle_view.py','rouge/battle_preview.py','rouge/spawn_candidates.py',
  'rouge/spawn_candidates_view.py','rouge/view_catalog.py','rouge/branch_choice.py','rouge/ui_state.py',
  'rouge/map_projection.py','rouge/player_tile_information.py','rouge/data/battle-map-projections.json',
  'rouge/data/fixed-landmark-references.json','rouge/data/view-catalog.json',MANIFEST,DATA,
  'scripts/build_spawn_candidates_299.py','tests/test_spawn_candidates_299.py',
  'tests/test_spawn_candidates_view_299.py','tests/test_spawn_candidates_integration_299.py'}
 names.update(read(ROOT/MANIFEST)['files']);names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/PACKET).rglob('*')if p.is_file())
 battle=read(ROOT/'rouge/data/battle-previews.json');pictures=read(ROOT/'rouge/data/view-catalog.json')
 for sid in(STAGE,'ro6_n_1_1','ro6_n_1_4'):
  stage=battle['stages'][sid];names.add('rouge/data/'+stage['image']['file'])
  for enemy in stage['enemies']:
   portrait=(pictures['enemies'].get(enemy['id'])or{}).get('portrait');row=pictures['images'].get(portrait)
   if row:names.add('rouge/data/'+row['file'])
 result={}
 for name in sorted(names):
  p=ROOT/name
  if not p.is_file()or p.is_symlink()or not p.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Regular selected public source required: '+name)
  result[name]=sha(p)
 return result
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--receipt',required=True);parser.add_argument('--visible-ms',type=int,default=120000)
 args=parser.parse_args();destination=Path(args.receipt).resolve()
 if destination.exists():raise FileExistsError('Preserve first actual receipt.')
 if args.visible_ms<=0:raise ValueError('Positive visible interval required.')
 destination.parent.mkdir(parents=True,exist_ok=True);started=datetime.now(timezone.utc).isoformat()
 before={};after={};checks=[];executions=0;images=[];handles=[];reads=[];refreshes=[];negatives=[]
 failure=None;done=False;closed=False;qpa=None;qt_exit=None
 attempts={k:0 for k in('game_enumeration','game_connect','game_capture','game_next_frame','desktop_start','desktop_request','provider_chat','credential_read')}
 def require(value,label):
  nonlocal executions
  if not value:raise AssertionError(label)
  executions+=1
  if label not in checks:checks.append(label)
 def forbidden(name):
  def blocked(*_,**__):attempts[name]+=1;raise AssertionError('Forbidden original entry: '+name)
  return blocked
 try:
  if sys.platform!='win32':raise RuntimeError('Actual native Windows required.')
  if Path(__file__).resolve()!=(ROOT/CANONICAL).resolve():raise RuntimeError('Cache script is not acceptance.')
  require(sha(ROOT/MANIFEST)==MANIFEST_SHA and sha(ROOT/DATA)==DATA_SHA,'final_candidate_source_packet_exact_before_window')
  from rouge import spawn_candidates as model
  require(model.action_reference(STAGE,ORIGIN)['source_valid']is True,'actual_current_main_action_packet_valid_before_Qt')
  before=bound_files()
  from PySide6.QtCore import Qt,QPoint,QRect,QTimer
  from PySide6.QtGui import QTextCursor
  from PySide6.QtWidgets import QApplication
  from PySide6.QtTest import QTest
  import win32gui,win32process
  from rouge import app as app_module
  from rouge.branch_choice import OVERVIEW
  gui=QApplication([]);qpa=gui.platformName();require(qpa=='windows','actual_windows_QPA')
  class PublicWindow(app_module.MainWindow):
   def refresh_windows(self):self.windows.clear()
  with tempfile.TemporaryDirectory(prefix='rouge-299-candidates-window-')as folder,ExitStack()as stack:
   temporary=Path(folder)
   for key,value in{'ROOT':temporary,'SETTINGS':temporary/'settings.json','OPERATOR_STATE':temporary/'operators.json','RUN_STATE':temporary/'run.json'}.items():stack.enter_context(patch.object(app_module,key,value))
   stack.enter_context(patch.object(app_module,'list_game_windows',side_effect=forbidden('game_enumeration')))
   for method,name in[('connect','game_connect'),('capture','game_capture'),('next_frame','game_next_frame')]:stack.enter_context(patch.object(app_module.GameCapture,method,side_effect=forbidden(name)))
   for method,name in[('start','desktop_start'),('request','desktop_request')]:stack.enter_context(patch.object(app_module.DesktopBackend,method,side_effect=forbidden(name)))
   stack.enter_context(patch.object(app_module,'stream_chat',side_effect=forbidden('provider_chat')));stack.enter_context(patch.object(app_module,'read_key',side_effect=forbidden('credential_read')))
   window=PublicWindow();dialog=None
   try:
    window.setWindowTitle('第299节 · 固定候选资料（公开隔离验收）');window.resize(*SIZE);window.show()
    panel=window.battle_preview;window.centralWidget().setCurrentWidget(panel);initial_run=deepcopy(window.run.state)
    saved_parent=None;saved_dialog=None;saved_child=None;old_child_hwnd=None
    def isolated():
     require(not window.auto.isChecked()and not window.timer.isActive(),'automatic_sampling_and_timer_disabled')
     require(window.capture.target is None and window.desktop.process is None,'capture_and_desktop_backend_inactive')
     require(all(v==0 for v in attempts.values()),'all_eight_external_entry_attempts_zero')
    def native(widget,kind,size):
     hwnd=int(widget.winId());thread,pid=win32process.GetWindowThreadProcessId(hwnd)
     require(win32gui.IsWindow(hwnd)and win32gui.IsWindowVisible(hwnd)and widget.isVisible(),kind+'_actual_visible_owned_HWND')
     require(pid==os.getpid()and not win32gui.IsIconic(hwnd),kind+'_actual_fixture_PID_nonminimized')
     require([widget.width(),widget.height()]==list(size),kind+'_actual_client_size_exact')
     return{'kind':kind,'hwnd':hwnd,'process_id':pid,'thread_id':thread,'qpa':qpa,'client_size':[widget.width(),widget.height()]}
    def screenshot(name,widget,kind,size,player=False):
     isolated();handle=native(widget,kind,size);p=destination.with_name(destination.stem+'-'+name+'.png')
     if p.exists():raise FileExistsError('Preserve first actual PNG.')
     if player:require(dialog.reading_tabs.currentWidget()is dialog.player_text,'representative_player_screenshot_actually_shows_default_reader')
     pixels=widget.grab();require(not pixels.isNull()and pixels.save(str(p),'PNG'),'actual_owned_native_PNG_saved')
     images.append({'name':name,'path':str(p),'sha256':sha(p),'native_window':handle,'direct_player_text':player})
    def click(button,owner,label):
     gui.processEvents();rect=QRect(button.mapTo(owner,QPoint(0,0)),button.size())
     require(button.isVisible()and button.isEnabled()and not button.visibleRegion().isEmpty()and owner.rect().contains(rect),label+'_visible_enabled_inside_client')
     QTest.mouseClick(button,Qt.MouseButton.LeftButton,pos=button.rect().center());gui.processEvents()
    def choose(control,value):
     at=control.findData(value);require(at>=0,'exact_full_source_control_identity_present');control.setCurrentIndex(at);gui.processEvents()
    def select_row(action):
     at=next(i for i,r in enumerate(panel.rows)if r['id']==action);item=panel.spawn_list.item(at);panel.spawn_list.scrollToItem(item);gui.processEvents()
     rect=panel.spawn_list.visualItemRect(item);require(not rect.isEmpty()and panel.spawn_list.viewport().rect().contains(rect.center()),'actual_parent_spawn_item_visible_before_manual_click')
     QTest.mouseClick(panel.spawn_list.viewport(),Qt.MouseButton.LeftButton,pos=rect.center());gui.processEvents()
     require(panel.spawn_list.currentItem().data(Qt.ItemDataRole.UserRole)['id']==action,'actual_parent_exact_action_selected')
    def configure(stage,action):
     panel.set_stage(stage);choose(panel.wave_combo,None);panel.enemy_choices.select_branch(OVERVIEW);panel.enemy_choices.select_value(None);panel.render_rows();gui.processEvents();select_row(action)
    def select_member(kind,action):
     choose(dialog.relation_kind,kind);relations=dialog.packet['groups'if kind=='group'else'packages']
     relation=next(r for r in relations if any(m['action_id']==action for m in r['members']));choose(dialog.relation,relation['reference_id'])
     member=next(m for m in relation['members']if m['action_id']==action);choose(dialog.member,member['reference_id']);return dialog._selected()
    def reader(w):
     c=w.textCursor();return{'text':text_sha(w.toPlainText()),'anchor':c.anchor(),'position':c.position(),'selected':c.selectedText(),
      'vertical':w.verticalScrollBar().value(),'horizontal':w.horizontalScrollBar().value()}
    def parent_state(p=panel):
     item=p.spawn_list.currentItem();return{'stage':p.current_stage,'wave':p.wave_combo.currentData(),'enemy':p.enemy_combo.currentData(),
      'include_branches':p.include_branches.isChecked(),'technical':p.technical.isChecked(),'spawn_id':item.data(Qt.ItemDataRole.UserRole)['id']if item else None,
      'spawn_scroll':p.spawn_list.verticalScrollBar().value(),'grid_selected':deepcopy(p.grid.selected),'grid_reference':deepcopy(p.grid.reference_cell),
      'original_selected':deepcopy(p.original.selected),'original_reference':deepcopy(p.original.reference_cell),'tile':deepcopy(p._tile_cell),
      'shown_enemy':deepcopy(p._shown_enemy),'ordinal':p.occurrence.value(),'spawn_reader':reader(p.spawn_detail),'enemy_reader':reader(p.enemy_detail)}
    def dialog_state():return{'relation_kind':dialog.relation_kind.currentData(),'relation':dialog.relation.currentData(),'member':dialog.member.currentData(),
     'manual_identity':deepcopy(dialog._manual_identity),'tab':dialog.reading_tabs.currentIndex(),'player':reader(dialog.player_text),'source':reader(dialog.source_text),
     'picture':dialog.picture.key,'button_enabled':dialog.open_spawn_button.isEnabled()}
    def prime(w,scroll=False):
     gui.processEvents();require(w.document().characterCount()>30,'real_reader_text_for_selection')
     c=w.textCursor();c.setPosition(5);c.setPosition(25,QTextCursor.MoveMode.KeepAnchor);w.setTextCursor(c)
     if scroll:
      bar=w.verticalScrollBar();require(bar.maximum()>0,'real_reader_has_nonzero_scroll_range');bar.setValue(max(1,bar.maximum()//2));require(bar.value()>0,'real_nonzero_reader_scroll_set')
     require(bool(w.textCursor().selectedText()),'real_nonempty_reader_selection')
    def later(fn,delay=200):
     def callback():
      try:isolated();fn()
      except BaseException as error:
       nonlocal failure,done
       failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()};done=False;close_owned();gui.exit(1)
     QTimer.singleShot(delay,callback)
    def close_owned():
     panel._clear_candidate_preview()
     if panel.spawn_candidates_window:panel.spawn_candidates_window.close()
     window.close()
    def begin():
     nonlocal dialog,saved_parent
     configure(STAGE,ORIGIN);panel.technical.setChecked(True);gui.processEvents()
     starts={(r['route']['start']['row'],r['route']['start']['col'])for r in panel.rows if r['route']['start']}
     stage=panel.grid.stage;cell=next({'row':r,'col':c}for r,line in enumerate(stage['map'])for c,t in enumerate(line)
      if(r,c)not in starts and stage['tiles'][t]['tileKey']in('tile_road','tile_floor'))
     QTest.mouseClick(panel.grid,Qt.MouseButton.LeftButton,pos=panel.grid.cell_center(cell).toPoint());gui.processEvents()
     require(panel._tile_cell==cell and panel._current_main_spawn_id()==ORIGIN,'manual_parent_grid_cell_does_not_replace_current_origin_action')
     prime(panel.enemy_detail,True);saved_parent=parent_state();handles.append(native(window,'main',SIZE))
     click(panel.spawn_group_button,window,'actual_current_group_entry_QTest_click');dialog=panel.spawn_candidates_window
     require(dialog is not None and dialog.parent()is panel,'actual_MainWindow_entry_constructed_owned_dialog');dialog.resize(*DIALOG_SIZE);gui.processEvents()
     require(dialog.origin_action_id==ORIGIN and dialog.stage_id==STAGE and dialog.relation.currentIndex()==dialog.member.currentIndex()==-1,
      'current_action_scope_kept_and_relation_member_default_unselected')
     require(parent_state()==saved_parent,'opening_candidate_reader_preserves_entire_parent_state');select_member('group',OTHER)
     dialog.reading_tabs.setCurrentWidget(dialog.player_text);gui.processEvents()
     require('辐能源石虫'in dialog.player_text.toPlainText()and'本条计划记录的数量'in dialog.player_text.toPlainText(),
      'player_reader_names_other_candidate_and_explains_single_documented_quantity')
     require(not any(s in dialog.player_text.toPlainText()for s in('enemy_1352','randomSpawn','https://','主队列','源参数')),
      'default_candidate_reader_is_plain_Chinese_without_raw_identifiers')
     screenshot('player-other-candidate',dialog,'dialog',DIALOG_SIZE,True);click(dialog.open_spawn_button,dialog,'actual_other_candidate_preview_QTest_click');later(previewed)
    def previewed():
     nonlocal saved_child,old_child_hwnd
     preview=panel.candidate_preview_window;require(preview is not None and preview is not panel,'manual_other_candidate_opens_independent_fixed_preview')
     member=dialog._selected()[1];reference=member['spawn_reference'];handles.append(native(preview,'candidate_preview',SIZE));old_child_hwnd=handles[-1]['hwnd']
     require(preview.current_stage==STAGE and preview.grid.selected['id']==OTHER and preview._shown_enemy==(STAGE,reference['enemy_id'],reference['level']),
      'independent_preview_exact_other_action_fixed_grid_and_enemy_reference')
     require(preview.original.selected['id']==OTHER and preview.grid.selected['action']==member['raw_action'],
      'independent_preview_uses_complete_fixed_action_not_same_enemy_name')
     require(parent_state()==saved_parent,'manual_preview_preserves_parent_filters_selection_map_enemy_and_reading')
     reads.append({'kind':'manual_other_candidate','stage_id':STAGE,'origin_action_id':ORIGIN,'member_action_id':OTHER,
      'enemy_id':reference['enemy_id'],'level_reference':reference['level'],'actual_selected':None,'parent_unchanged':True})
     screenshot('independent-fixed-preview',preview,'candidate_preview',SIZE);prime(dialog.player_text);dialog.reading_tabs.setCurrentWidget(dialog.source_text);prime(dialog.source_text,True)
     saved_child=(preview,deepcopy(panel._candidate_preview_token),parent_state(preview));later(refresh_prime)
    def refresh_prime():
     nonlocal saved_dialog
     saved_dialog=dialog_state();later(refresh_once)
    def refresh_once():
     callbacks=[dialog.refresh_reference,panel._refresh_spawn_candidates,
      lambda:dialog.set_reference(STAGE,ORIGIN,scope_key=deepcopy(dialog.scope_key))]
     callbacks[len(refreshes)]();gui.processEvents()
     require(dialog_state()==saved_dialog and parent_state()==saved_parent,'same_scope_refresh_preserves_dialog_and_parent_actual_reading_state')
     require(panel.candidate_preview_window is saved_child[0]and panel._candidate_preview_token==saved_child[1]
      and parent_state(panel.candidate_preview_window)==saved_child[2],'same_scope_refresh_does_not_recreate_or_reset_child_preview')
     refreshes.append({'path':['dialog','parent','same_reference'][len(refreshes)],'source_scroll':dialog.source_text.verticalScrollBar().value(),
      'source_selection':dialog.source_text.textCursor().selectedText(),'parent_unchanged':True,'child_same_instance':True})
     if len(refreshes)<3:later(refresh_once)
     else:later(source_failure)
    def source_failure():
     manifest=read(ROOT/MANIFEST);clone=temporary/'public-source-negative'
     for name in set(manifest['files'])|{MANIFEST}:
      p=ROOT/name;require(p.is_file()and not p.is_symlink()and p.resolve().is_relative_to(ROOT.resolve()),'source_negative_copies_only_regular_public_members')
      out=clone/name;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(p.read_bytes())
     target=clone/MANIFEST;raw=target.read_bytes()
     with patch.object(model,'ROOT',clone):
      require(model.action_reference(STAGE,ORIGIN)['source_valid']is True,'complete_clone_valid_before_warm_source_damage')
      try:
       target.write_bytes(raw+b' ');dialog.refresh_reference();panel._refresh_spawn_candidates();gui.processEvents()
       require(dialog.packet is None and dialog.relation.currentIndex()==dialog.member.currentIndex()==-1 and dialog.picture.isHidden()
        and not dialog.open_spawn_button.isEnabled(),'warm_source_failure_clears_old_member_picture_and_jump')
       require(panel.candidate_preview_window is None and not win32gui.IsWindowVisible(old_child_hwnd),'source_failure_closes_old_independent_preview')
       require(all('已清除'in w.toPlainText()for w in(dialog.player_text,dialog.source_text)),'source_failure_clears_both_old_readers')
       dialog.reading_tabs.setCurrentWidget(dialog.player_text);screenshot('source-unavailable',dialog,'dialog',DIALOG_SIZE,True)
      finally:target.write_bytes(raw)
      require(sha(target)==MANIFEST_SHA,'public_clone_source_restored_exact_bytes')
      dialog.refresh_reference();panel._refresh_spawn_candidates();gui.processEvents()
      require(dialog.packet is not None and dialog.relation.currentIndex()==dialog.member.currentIndex()==-1
       and panel.candidate_preview_window is None,'restored_source_requires_manual_choice_and_never_reopens_preview')
     negatives.append({'kind':'warm_manifest','manifest':MANIFEST,'damaged_member':MANIFEST,'public_clone_only':True,
      'restored_sha256':sha(target),'prior_child_closed':True,'actual_selection':None});later(package_reading)
    def package_reading():
     nonlocal dialog
     dialog.hide();configure('ro6_n_1_4','w1.f3.a5');click(panel.spawn_candidates_button,window,'actual_all_stage_candidates_QTest_click');dialog=panel.spawn_candidates_window
     require(dialog.origin_action_id is None,'all_stage_reader_is_explicit_scope_not_inherited_current_action')
     relation,member=select_member('package','w1.f3.a5');dialog.reading_tabs.setCurrentWidget(dialog.player_text);gui.processEvents()
     require([m['action_id']for m in relation['members']]==['w1.f3.a4','w1.f3.a5']and member['raw_action']['randomSpawnGroupKey']is None,
      'package_keeps_member_without_group_and_complete_same_queue_members')
     require('同一资料标记'in dialog.player_text.toPlainText()and'不能据此断定它们同时出场'in dialog.player_text.toPlainText(),
      'player_package_reader_explains_no_simultaneous_or_actual_count_inference')
     screenshot('player-package-ungrouped-member',dialog,'dialog',DIALOG_SIZE,True)
     reads.append({'kind':'package_member_without_group','stage_id':'ro6_n_1_4','member_action_id':'w1.f3.a5','actual_selected':None});later(empty_and_branch)
    def empty_and_branch():
     nonlocal dialog
     dialog.hide();configure('ro6_n_1_1','w1.f1.a1');click(panel.spawn_group_button,window,'actual_activation_group_QTest_click');dialog=panel.spawn_candidates_window
     _,member=select_member('group','w1.f1.a1');dialog.reading_tabs.setCurrentWidget(dialog.player_text);gui.processEvents()
     require(member['action_type']=='ACTIVATE_PREDEFINED'and member['predefined_reference']['status']=='empty_key'
      and not dialog.open_spawn_button.isEnabled()and dialog.picture.isHidden(),'empty_activation_key_has_no_borrowed_enemy_picture_or_jump')
     require('原记录没有指定激活目标'in dialog.player_text.toPlainText(),'player_empty_activation_keeps_unknown_target_distinct_from_empty_candidate')
     screenshot('player-empty-activation',dialog,'dialog',DIALOG_SIZE,True)
     dialog.hide();select_row('w3.f1.a1');click(panel.spawn_group_button,window,'actual_blank_candidate_group_QTest_click');_,member=select_member('group','w3.f1.a5')
     require(member['action_type']=='EMPTY'and not dialog.open_spawn_button.isEnabled()and dialog.picture.isHidden()
      and'不能据此认为本局没有敌人'in dialog.player_text.toPlainText(),'blank_candidate_keeps_uncertainty_and_cannot_jump_as_enemy')
     dialog.hide();select_row('branch:shsbox2.p1.a1');panel._refresh_spawn_candidates();gui.processEvents()
     require(not panel.spawn_group_button.isEnabled()and panel.open_current_spawn_candidates()is False,
      'actual_branch_current_row_rejects_main_group_entry_without_None_fallback')
     require(dialog.packet is None and panel.candidate_preview_window is None,'branch_scope_clears_old_current_action_reader_and_child')
     reads.append({'kind':'empty_activation_and_blank_and_branch','stage_id':'ro6_n_1_1','actual_selected':None});later(finish)
    def finish():
     nonlocal done
     require(len(images)==5 and sum(i['direct_player_text']for i in images)>=2,'five_actual_images_include_at_least_two_readable_new_player_pages')
     require(len(refreshes)==3 and all(r['source_scroll']>0 and r['source_selection']for r in refreshes),'three_actual_refreshes_preserve_nonzero_scroll_and_selection')
     require(window.run.state==initial_run,'manual_candidate_reading_does_not_write_temporary_run_memory')
     require(bound_files()==before,'selected_public_sources_unchanged_before_completion');handles.append(native(window,'main',SIZE));done=True
    def deadline():
     nonlocal failure
     if not done and failure is None:failure={'type':'TimeoutError','message':'Candidate source/manual-preview checks incomplete.'}
     close_owned()
    later(begin,500);QTimer.singleShot(max(30000,args.visible_ms),deadline);qt_exit=gui.exec()
    closed=not window.isVisible()and not(dialog and dialog.isVisible())and panel.candidate_preview_window is None
    if qt_exit!=0 or not closed or not done:
     if failure is None:failure={'type':'RuntimeError','message':'Actual checks/Qt/owned-window closure incomplete.'}
    if failure is None:isolated()
    after=bound_files()
    if before!=after and failure is None:failure={'type':'AssertionError','message':'Selected public sources changed before closure.'}
   finally:close_owned();gui.processEvents();closed=not window.isVisible()and not(dialog and dialog.isVisible())and panel.candidate_preview_window is None
 except BaseException as error:failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
 report={'section':299,'kind':'isolated_native_windows_spawn_candidate_reader','passed':done and failure is None,'failure':failure,
  'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'process_id':os.getpid(),'qpa':qpa,'qt_exit_code':qt_exit,
  'verification_window_closed':closed,'checks':checks,'unique_checks':len(checks),'successful_assertion_executions_including_repeated_guards':executions,
  'requested_parent_client_size':list(SIZE),'requested_dialog_client_size':list(DIALOG_SIZE),'requested_preview_client_size':list(SIZE),
  'native_observations':handles,'screenshots':images,'screenshot_count':len(images),'candidate_readings':reads,
  'same_scope_refresh_observations':refreshes,'source_negative_fixtures':negatives,'source_sha256_before':before,'source_sha256_after':after,
  'source_guard_is_selected_not_all_transitive_dependencies':True,'temporary_state_root':True,
  'state_paths_replaced_before_constructor':['ROOT','SETTINGS','OPERATOR_STATE','RUN_STATE'],'private_state_read_copied_or_restored':False,
  'external_operation_attempts':attempts,'external_entrypoints_blocked_before_original_call':True,'game_operated':False,'game_captures':0,
  'chat_sent':False,'chat_attempted':bool(attempts['desktop_request']or attempts['provider_chat']),
  'original_project_window_operated_or_restarted':False,'actual_process_termination_verified_by_this_script':False,
  'owned_supervisor_exit_and_cleanup_required_separately':True,'launch_Popen_PID_must_be_recorded_separately_from_actual_fixture_PID':True,
  'scope':'Manual fixed main-action group/package reading and independent exact-action preview; no probability, actual selection, simultaneous count, live enemy position or full validation.'}
 with destination.open('x',encoding='utf8')as stream:stream.write(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 return 0 if report['passed']else 1
if __name__=='__main__':raise SystemExit(main())
