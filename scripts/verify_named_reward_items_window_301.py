"""Cache candidate: exact named reward illustrations via an isolated MainWindow.
Root freezes/promotes and supervises the actual run. No actual reward is inferred.
"""
import argparse
from contextlib import ExitStack
from copy import deepcopy
from datetime import datetime,timezone
from html import unescape
import hashlib,json,os,re
from pathlib import Path
import sys,tempfile,traceback
from unittest.mock import patch
ROOT=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file())
sys.path.insert(0,str(ROOT))
CANONICAL='scripts/verify_named_reward_items_window_301.py'
PACKET='research/p3-named-reward-items-301';MANIFEST=PACKET+'/source-manifest.json';DATA='rouge/data/named-reward-items.json'
MANIFEST_SHA='a7501b82da0c9e3fa75809656f371f20a43c196eeef2cd37cfd388c16f185374';DATA_SHA='437684110f9e1190e1e7b681ef14f9d20ceb17e45e814a769244cca1a072353c'
SIZE=(1050,720);DIALOG_SIZE=(900,680)
CASES=((5,0,0,'rogue_6_relic_fight_11'),(5,0,1,'rogue_6_relic_legacy_142'),(5,0,2,'rogue_6_relic_legacy_141'),
 (6,0,0,'rogue_6_relic_fight_18'),(6,0,1,'rogue_6_relic_fight_19'),
 (7,0,0,'rogue_6_scrap_G_12'),(7,0,1,'rogue_6_scrap_G_12'),(8,0,0,'rogue_6_relic_cargo_12'),
 (10,17,0,'rogue_6_relic_artifact_4'),(11,0,0,'rogue_6_relic_artifact_5'),
 (11,0,1,'rogue_6_relic_artifact_5'),(11,0,2,'rogue_6_relic_artifact_5'),
 (19,0,0,'rogue_6_relic_cargo_11'),(20,0,0,'rogue_6_relic_cargo_10'),
 (22,0,0,'rogue_6_relic_final_4'),(25,9,0,'rogue_6_relic_final_6'))
def identity(case):
 event='community_group_'+str(case[0]).zfill(3);scene=event+':scene:'+str(case[1]);return event,scene,scene+':choice:'+str(case[2])
FIRST=identity(CASES[0])[0];OTHER='community_group_001'
ACTUAL=('actual_reward','actual_quantity','actual_claimed','actual_held','actual_effect','actual_eligible')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_bytes())
def text_sha(s):return hashlib.sha256(s.encode('utf8')).hexdigest()
def plain(value):
 text=unescape(value or '');text=re.sub(r'<br\s*/?>','\n',text,flags=re.I)
 return re.sub(r'</?[A-Za-z][^<>]*>|<[@$][^<>]*>|</>','',text).strip()
def bound_files():
 names={CANONICAL,MANIFEST,DATA,'rouge/app.py','rouge/node_catalog_view.py','rouge/node_catalog.py',
  'rouge/event_planning.py','rouge/node_rewards.py','rouge/player_node_information.py','rouge/ui_state.py','rouge/branch_choice.py',
  'rouge/named_reward_items.py','rouge/named_reward_items_view.py','rouge/data/node-reward-reference.json',
  'scripts/build_named_reward_items_301.py','tests/test_named_reward_items_301.py',
  'tests/test_named_reward_items_view_301.py','tests/test_named_reward_integration_301.py'}
 names.update(read(ROOT/MANIFEST)['files'])
 names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/PACKET).rglob('*')if p.is_file())
 result={}
 for name in sorted(names):
  p=ROOT/name
  if not p.is_file()or p.is_symlink()or not p.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Regular selected public source required: '+name)
  result[name]=sha(p)
 return result
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--receipt',required=True)
 parser.add_argument('--visible-ms',type=int,default=120000);args=parser.parse_args();destination=Path(args.receipt).resolve()
 if destination.exists():raise FileExistsError('Preserve first actual receipt.')
 if args.visible_ms<=0:raise ValueError('Positive visible interval required.')
 destination.parent.mkdir(parents=True,exist_ok=True);started=datetime.now(timezone.utc).isoformat()
 before={};after={};checks=[];executions=0;images=[];handles=[];readings=[];refreshes=[];negatives=[];history=[]
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
   'final_named_reward_source_authority_and_data_exact_before_actual_window')
  before=bound_files()
  from rouge import named_reward_items as model,node_catalog as catalog
  require(model.event_reference(FIRST)['source_valid']is True,'actual_fixed_named_reward_reference_valid_before_Qt')
  from PySide6.QtCore import Qt,QPoint,QRect,QTimer
  from PySide6.QtGui import QTextCursor,QPixmap
  from PySide6.QtWidgets import QApplication
  from PySide6.QtTest import QTest
  import win32gui,win32process
  from rouge import app as app_module
  gui=QApplication([]);qpa=gui.platformName();require(qpa=='windows','actual_windows_QPA')
  class PublicWindow(app_module.MainWindow):
   def refresh_windows(self):self.windows.clear()
  with tempfile.TemporaryDirectory(prefix='rouge-301-reward-items-')as folder,ExitStack()as stack:
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
    window.setWindowTitle('第301节 · 选项奖励图文（公开隔离验收）');window.resize(*SIZE);window.show()
    panel=window.node_catalog;tabs=window.centralWidget();initial_run=deepcopy(window.run.state)
    calculation_before=tuple((window.relic_list.item(i).data(Qt.ItemDataRole.UserRole),window.relic_list.item(i).checkState().value)for i in range(window.relic_list.count()))
    parent_saved=None;dialog_saved=None;icon_refs={}
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
    def event(event_id,directory=True):
     if directory:
      panel.show_directory();panel.set_map_context(None);choose(panel.kind,'event');choose(panel.floor,None);choose(panel.node_type,None)
     panel.search.setText(catalog._event(event_id)['title']);tabs.setCurrentWidget(panel)
     at=next(i for i,e in enumerate(panel.entries)if e['kind']=='event'and e['record']['id']==event_id)
     item=panel.list.flat[at];item.parent().setExpanded(True);panel.list.scrollToItem(item);gui.processEvents();rect=panel.list.visualItemRect(item)
     require(not rect.isEmpty()and panel.list.viewport().rect().contains(rect.center()),'actual_exact_directory_event_item_visible')
     QTest.mouseClick(panel.list.viewport(),Qt.MouseButton.LeftButton,pos=rect.center());gui.processEvents()
     require(panel.list.selected_key()==panel.entries[at]['key'],'actual_QTest_selected_complete_event_identity_not_same_title')
     return panel.entries[at]
    def click(button,owner,label):
     gui.processEvents();rect=QRect(button.mapTo(owner,QPoint(0,0)),button.size())
     require(button.isVisible()and button.isEnabled()and not button.visibleRegion().isEmpty()and owner.rect().contains(rect),
      label+'_visible_enabled_inside_actual_client')
     QTest.mouseClick(button,Qt.MouseButton.LeftButton,pos=button.rect().center());gui.processEvents()
    def reader(w):
     c=w.textCursor();return{'text_sha256':text_sha(w.toPlainText()),'anchor':c.anchor(),'position':c.position(),
      'selected':c.selectedText(),'vertical':w.verticalScrollBar().value(),'horizontal':w.horizontalScrollBar().value()}
    def parent_state():
     return{'key':panel.list.selected_key(),'tab':panel.reading_tabs.currentIndex(),'scene':panel.event_scene_filter.currentData(),
      'choice':panel.event_choice_filter.currentData(),'stage':panel.event_stage.currentData(),'search':panel.search.text(),
      'search_cursor':panel.search.cursorPosition(),'search_selection':panel.search.selectedText(),
      'player':reader(panel.player_detail),'source':reader(panel.detail)}
    def icon_empty():
     p=dialog.icon.pixmap();return dialog.icon.isHidden()and(p is None or p.isNull())
    def dialog_state():
     p=dialog.icon.pixmap();return{'event':dialog.event_id,'scope':deepcopy(dialog.scope_key),'choice':dialog.choice.currentData(),
      'tab':dialog.reading_tabs.currentIndex(),'view_key':deepcopy(dialog._view_key),'reading_key':deepcopy(dialog._reading_key),
      'icon_visible':dialog.icon.isVisible(),'icon_name':dialog.icon.accessibleName(),'icon_size':None if p is None or p.isNull()else[p.width(),p.height()],
      'player':reader(dialog.player_text),'source':reader(dialog.source_text)}
    def prime(w,scroll=False):
     gui.processEvents();require(w.document().characterCount()>30,'actual_existing_reader_text_can_be_selected')
     c=w.textCursor();c.setPosition(5);c.setPosition(25,QTextCursor.MoveMode.KeepAnchor);w.setTextCursor(c)
     if scroll:
      bar=w.verticalScrollBar();require(bar.maximum()>0,'actual_existing_reader_has_real_scroll_range')
      bar.setValue(max(1,bar.maximum()//2));require(bar.value()>0,'actual_existing_reader_nonzero_scroll_set')
     require(bool(w.textCursor().selectedText()),'actual_existing_reader_nonempty_selection')
    def actual_unknown(value):
     return all(k in value and value[k]is None for k in ACTUAL)
    def select_item(case):
     event_id,scene_key,choice_key=identity(case)
     require(dialog.event_id==event_id,'manual_item_reader_exact_event_scope')
     expected=next(r for r in dialog.packet['choices']if r['scene_key']==scene_key and r['choice_key']==choice_key)
     choose(dialog.choice,expected['reference_id']);details=model.item_details(event_id,scene_key,choice_key)
     require(details['status']=='documented_reference'and details['source_valid']is True and details['reference']==expected,
      'manual_selection_fresh_details_match_complete_event_scene_choice_and_conditions')
     require(actual_unknown(details)and actual_unknown(expected)and details['inventory_updated']is False and expected['quantity_reference']is None,
      'all_six_actual_fields_and_reward_quantity_remain_unknown_without_inventory_change')
     item,icon=details['item'],details['icon_reference'];pixmap=dialog.icon.pixmap()
     require(item['id']==expected['item_id']==icon['item_id']==case[3]and icon['icon_id']==item['iconId'],
      'actual_item_and_icon_identity_are_exact_not_similar_picture_or_same_name')
     raw=(ROOT/icon['file']).read_bytes();blob=hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
     require(before[icon['file']]==icon['sha256']==hashlib.sha256(raw).hexdigest()and len(raw)==icon['bytes']and blob==icon['git_blob_sha1'],
      'actual_picture_bytes_match_exact_SHA256_length_and_original_Git_blob')
     reference=QPixmap();require(reference.loadFromData(raw)and pixmap is not None and not pixmap.isNull()and dialog.icon.isVisible(),
      'manual_choice_automatically_loads_real_decodable_visible_pixmap_without_second_button')
     scaled=reference.scaledToWidth(pixmap.width(),Qt.TransformationMode.SmoothTransformation)
     require(pixmap.width()==96 and pixmap.toImage()==scaled.toImage(),'actual_QLabel_picture_equals_exact_selected_source_scaled_pixels')
     dialog.reading_tabs.setCurrentWidget(dialog.player_text);gui.processEvents();text=dialog.player_text.toPlainText()
     require(plain(item['name'])in text and all(s in text for s in('【这个选项的条件资料】','【物品用途】','【完整物品说明】','【图鉴解锁说明】','不默认1件','尚未确认')),
      'actual_player_page_has_named_item_kind_condition_usage_description_unlock_and_unknown_quantity')
     require(all(plain(item[k])and plain(item[k])in text for k in('usage','description')),
      'actual_player_page_preserves_complete_primary_item_usage_and_description')
     if expected['condition_text']:require(plain(expected['condition_text'])in text,'same_item_alternative_keeps_its_own_complete_condition')
     if item.get('unlockCondDesc'):require(plain(item['unlockCondDesc'])in text,'primary_unlock_text_is_complete_and_separate_from_option_conditions')
     require(expected['item_kind_name']in text and(item['type']=='SCRAP'and details['relic']is None or item['type']=='RELIC'and details['relic']['id']==item['id']),
      'scrap_and_relic_types_remain_distinct_no_false_relic_record_for_scrap')
     require(not any(s in text for s in('community_group_','rogue_6_','https://')),'default_item_reader_has_no_raw_identifiers_or_source_URLs')
     source=json.loads(dialog.source_text.toPlainText())
     require(source['selected_item_details']==details,'actual_technical_reader_retains_complete_fresh_selected_details_not_only_title')
     icon_refs[item['id']]=deepcopy(icon);return details
    def screenshot(name):
     isolated();require(dialog.reading_tabs.currentWidget()is dialog.player_text and dialog.icon.isVisible(),
      'actual_representative_image_shows_player_reader_and_exact_icon')
     handle=native(dialog,'dialog');p=destination.with_name(destination.stem+'-'+name+'.png')
     if p.exists():raise FileExistsError('Preserve first actual PNG.')
     pixels=dialog.grab();require(not pixels.isNull()and pixels.save(str(p),'PNG'),'actual_owned_native_PNG_saved')
     images.append({'name':name,'path':str(p),'sha256':sha(p),'native_window':handle,'direct_player_text':True,'exact_icon_visible':True})
    def close_owned():
     if panel.named_reward_window is not None:panel.named_reward_window.close()
     window.close()
    def later(callback,delay=150):
     def guarded():
      nonlocal failure,done
      try:isolated();callback()
      except BaseException as error:
       failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()};done=False;close_owned();gui.exit(1)
     QTimer.singleShot(delay,guarded)
    def begin():
     nonlocal parent_saved
     event(FIRST);panel.reading_tabs.setCurrentWidget(panel.detail);prime(panel.detail,True);panel.search.setSelection(0,2);parent_saved=parent_state()
     require(panel.named_reward_window is None and panel.named_reward_button.isVisible()and panel.named_reward_button.isEnabled(),
      'only_bound_exact_event_has_manual_entry_and_dialog_not_precreated')
     handles.append(native(window,'parent'));click(panel.named_reward_button,window,'actual_MainWindow_named_reward_entry_QTest_click');later(opened)
    def opened():
     nonlocal dialog,dialog_saved
     dialog=panel.named_reward_window;require(dialog is not None and dialog.parent()is panel,'actual_parent_manual_entry_constructs_owned_modeless_reader')
     dialog.resize(*DIALOG_SIZE);gui.processEvents();handles.append(native(dialog,'dialog'))
     require(handles[-1]['hwnd']!=handles[-2]['hwnd'],'actual_parent_and_dialog_have_distinct_owned_HWNDs')
     require(dialog.choice.count()==3 and dialog.choice.currentIndex()==-1 and dialog._view_key is None and icon_empty(),
      'ordinary_multi_item_event_defaults_unselected_without_automatic_icon_or_reward')
     require(actual_unknown(dialog.packet)and dialog.packet['inventory_updated']is False and parent_state()==parent_saved,
      'opening_bound_reward_reference_keeps_actual_unknown_and_parent_reading_unchanged')
     dialog.reading_tabs.setCurrentWidget(dialog.source_text);prime(dialog.source_text,True);dialog_saved=dialog_state();later(unselected_refresh)
    def unselected_refresh():
     panel.refresh();gui.processEvents()
     require(dialog_state()==dialog_saved and parent_state()==parent_saved and icon_empty(),
      'unselected_same_scope_refresh_keeps_real_source_reading_without_loading_image')
     refreshes.append({'path':'unselected_parent','choice':None,'source_scroll':dialog.source_text.verticalScrollBar().value(),
      'source_selection':dialog.source_text.textCursor().selectedText(),'parent_unchanged':True});later(read_next)
    def read_next():
     nonlocal dialog,parent_saved,dialog_saved
     index=len(readings);case=CASES[index];event_id,scene_key,choice_key=identity(case)
     if dialog.event_id!=event_id:
      event(event_id);click(panel.named_reward_button,window,'actual_bound_event_reward_entry_QTest_click');dialog=panel.named_reward_window
      require(dialog.choice.currentIndex()==-1 and dialog._view_key is None and icon_empty(),
       'new_target_event_scope_clears_previous_choice_and_image_before_manual_selection')
     before_parent=parent_state();details=select_item(case)
     require(parent_state()==before_parent,'manual_reward_item_selection_preserves_parent_filters_text_selection_and_reading')
     row=details['reference'];readings.append({'event_id':event_id,'scene_key':scene_key,'choice_key':choice_key,
      'reference_id':row['reference_id'],'original_choice_id':row['original_choice_id'],'item_id':row['item_id'],'item_kind':row['item_kind'],
      'condition_text':row['condition_text'],'icon_file':details['icon_reference']['file'],'icon_sha256':details['icon_reference']['sha256'],
      'actual_reward':None,'actual_quantity':None,'inventory_updated':False})
     shots={(5,0,0):'player-ordinary-multi-item',(11,0,1):'player-repeated-item-condition',(7,0,0):'player-scrap-cage-controller',
      (10,17,0):'player-deep-scene-dog-sap',(25,9,0):'player-deep-scene-burned-civilization'}
     if case[:3]in shots:screenshot(shots[case[:3]])
     if index==0:
      panel.reading_tabs.setCurrentWidget(panel.detail);prime(panel.detail,True);panel.search.setSelection(0,2);parent_saved=parent_state()
      prime(dialog.player_text);dialog.reading_tabs.setCurrentWidget(dialog.source_text);prime(dialog.source_text,True);dialog_saved=dialog_state();later(selected_refresh)
     elif len(readings)<len(CASES):later(read_next)
     else:later(source_failure)
    def selected_refresh():
     selected=[r for r in refreshes if r['choice']is not None]
     callbacks=[dialog.refresh_reference,panel.refresh,lambda:dialog.set_reference(FIRST,scope_key=deepcopy(panel.list.selected_key()))]
     callbacks[len(selected)]();gui.processEvents()
     require(dialog_state()==dialog_saved and parent_state()==parent_saved,
      'selected_same_scope_refresh_preserves_exact_choice_icon_tab_nonzero_scroll_and_parent_reading')
     refreshes.append({'path':['selected_dialog','selected_parent','selected_same_reference'][len(selected)],
      'choice':dialog.choice.currentData(),'source_scroll':dialog.source_text.verticalScrollBar().value(),
      'source_selection':dialog.source_text.textCursor().selectedText(),'parent_unchanged':True})
     if len(selected)<2:later(selected_refresh)
     else:later(read_next)
    def source_failure():
     manifest=read(ROOT/MANIFEST);clone=temporary/'public-source-negative'
     for name in set(manifest['files'])|{MANIFEST}:
      p=ROOT/name;require(p.is_file()and not p.is_symlink()and p.resolve().is_relative_to(ROOT.resolve()),'negative_fixture_copies_only_regular_public_source_members')
      out=clone/name;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(p.read_bytes())
     bad=icon_refs['rogue_6_scrap_G_12'];target=clone/bad['file'];raw=target.read_bytes();last=identity(CASES[-1])
     with patch.object(model,'ROOT',clone):
      require(model.item_details(*last)['source_valid']is True,'complete_public_clone_valid_before_warm_nonselected_icon_damage')
      try:
       target.write_bytes(raw+b' ');dialog.refresh_reference();panel.refresh();gui.processEvents()
       unavailable=[model.event_reference(e)for e in sorted({identity(c)[0]for c in CASES})]
       require(len(unavailable)==10 and all(p['source_valid']is False and p['status']=='source_unavailable'and p['choices']==[]for p in unavailable)
        and dialog.packet is None and dialog.choice.currentIndex()==-1
        and dialog._view_key is None and icon_empty()and not panel.named_reward_button.isEnabled(),
        'any_bound_icon_failure_invalidates_all_targets_and_clears_stale_other_item_image_and_choice')
       require(all('已清除'in w.toPlainText()for w in(dialog.player_text,dialog.source_text)),
        'source_failure_clears_both_old_item_and_original_source_readers')
      finally:target.write_bytes(raw)
      require(sha(target)==bad['sha256'],'damaged_public_clone_icon_restored_exact_original_bytes')
      dialog.refresh_reference();panel.refresh();gui.processEvents()
      require(dialog.packet is not None and dialog.choice.currentIndex()==-1 and dialog._view_key is None and icon_empty()
       and panel.named_reward_button.isEnabled(),'restored_sources_do_not_automatically_reselect_or_reload_previous_reward_image')
     negatives.append({'kind':'warm_nonselected_icon','damaged_member':bad['file'],'public_clone_only':True,'all_target_references_unknown':True,
      'restored_sha256':sha(target),'actual_reward':None});later(historical_read)
    def historical_read():
     nonlocal dialog
     record=catalog._event(FIRST);content={'kind':'event','title':record['title'],'source':'same_frame_selected_node','identity_status':'visible_scene',
      'scene_candidates':deepcopy(record['scenes'][0]['game_scene_ids'])}
     graph={'zone_id':'zone_1','template_id':'public301-history','nodes':[{'id':'public301-past','row':0,'col':0,
      'observed_type':'林间空地','remembered_type':record['node_types'][0],'remembered_content':content}]};saved=deepcopy(graph)
     panel.search.clear();panel.set_map_context(graph,{'floor':1},epoch='public301-history',historical=True)
     panel.set_node(graph,'public301-past',floor=1);panel.bind_current_node();entry=event(FIRST,directory=False)
     require(entry.get('history_read')is True and panel._event_context(entry['record'])['reference_context_scope']=='historical_title_reference_only',
      'remembered_title_remains_separate_historical_reference_not_current_reward_eligibility')
     click(panel.named_reward_button,window,'actual_historical_named_reward_manual_entry_QTest_click');dialog=panel.named_reward_window
     require(dialog.choice.currentIndex()==-1 and icon_empty(),'historical_scope_does_not_inherit_previous_choice_or_image')
     details=select_item(CASES[2]);require(graph==saved and actual_unknown(details),'historical_item_read_leaves_input_graph_and_actual_outcome_unknown')
     history.append({'event_id':FIRST,'choice_key':identity(CASES[2])[2],'historical_reference_only':True,'caller_graph_unchanged':True,'actual_eligible':None})
     later(finish)
    def finish():
     nonlocal done
     event(OTHER)
     require(not panel.named_reward_button.isVisible()and dialog.packet is None and dialog.choice.currentIndex()==-1 and icon_empty()
      and all('已清除'in w.toPlainText()for w in(dialog.player_text,dialog.source_text)),
      'non_target_event_hides_reward_entry_and_clears_all_old_item_text_and_icon')
     require(len(readings)==16 and{(r['event_id'],r['scene_key'],r['choice_key'])for r in readings}=={identity(c)for c in CASES}
      and len({r['event_id']for r in readings})==10 and len(icon_refs)==13,'all_sixteen_exact_tuples_ten_events_and_thirteen_images_actually_read')
     require(sum(r['item_kind']=='SCRAP'for r in readings)==2 and sum(1 for k in icon_refs if k.startswith('rogue_6_relic_'))==12
      and all(r['original_choice_id']!='choice_ro6_rest_4'for r in readings),'thirteen_items_keep_twelve_relics_one_scrap_and_do_not_restore_unbound_choice')
     require(len(images)==5 and all(r['direct_player_text']and r['exact_icon_visible']for r in images),
      'five_actual_representative_images_show_player_information_and_exact_icons')
     require(len(refreshes)==4 and all(r['source_scroll']>0 and r['source_selection']and r['parent_unchanged']for r in refreshes),
      'actual_selected_and_unselected_refresh_paths_keep_real_nonzero_scroll_selection_and_parent_reading')
     calculation_after=tuple((window.relic_list.item(i).data(Qt.ItemDataRole.UserRole),window.relic_list.item(i).checkState().value)for i in range(window.relic_list.count()))
     require(window.run.state==initial_run and calculation_after==calculation_before,'manual_item_reading_does_not_change_run_memory_or_calculation_relic_checkboxes')
     require(bound_files()==before,'selected_public_sources_unchanged_before_completion');handles.append(native(window,'parent'));done=True
    def deadline():
     nonlocal failure
     if not done and failure is None:failure={'type':'TimeoutError','message':'Named reward actual reading checks incomplete.'}
     close_owned()
    later(begin,500);QTimer.singleShot(max(30000,args.visible_ms),deadline);qt_exit=gui.exec()
    closed=not window.isVisible()and not(dialog and dialog.isVisible())
    if qt_exit!=0 or not closed or not done:
     if failure is None:failure={'type':'RuntimeError','message':'Actual checks, Qt or owned-window closure incomplete.'}
    if failure is None:isolated()
    after=bound_files()
    if before!=after and failure is None:failure={'type':'AssertionError','message':'Selected public sources changed before closure.'}
   finally:close_owned();gui.processEvents();closed=not window.isVisible()and not(dialog and dialog.isVisible())
 except BaseException as error:failure={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}
 report={'section':301,'kind':'isolated_native_windows_named_reward_items_reader','passed':done and failure is None,'failure':failure,
  'started_at':started,'finished_at':datetime.now(timezone.utc).isoformat(),'process_id':os.getpid(),'qpa':qpa,'qt_exit_code':qt_exit,
  'verification_window_closed':closed,'checks':checks,'unique_checks':len(checks),'successful_assertion_executions_including_repeated_guards':executions,
  'requested_parent_client_size':list(SIZE),'requested_dialog_client_size':list(DIALOG_SIZE),'native_observations':handles,
  'screenshots':images,'screenshot_count':len(images),'actual_choice_readings':readings,'actual_distinct_item_images':icon_refs,
  'same_scope_refresh_observations':refreshes,'source_negative_fixtures':negatives,'historical_readings':history,
  'source_sha256_before':before,'source_sha256_after':after,'source_guard_is_selected_not_all_transitive_dependencies':True,
  'temporary_state_root':True,'state_paths_replaced_before_constructor':['ROOT','SETTINGS','OPERATOR_STATE','RUN_STATE'],
  'private_state_read_copied_or_restored':False,'external_operation_attempts':attempts,'external_entrypoints_blocked_before_original_call':True,
  'game_operated':False,'game_captures':0,'chat_sent':False,'chat_attempted':bool(attempts['desktop_request']or attempts['provider_chat']),
  'original_project_window_operated_or_restarted':False,'actual_process_termination_verified_by_this_script':False,
  'owned_supervisor_exit_and_cleanup_required_separately':True,'launch_Popen_PID_must_be_recorded_separately_from_actual_fixture_PID':True,
  'actual_reward_quantity_claim_held_effect_eligibility_verified':False,
  'scope':'Sixteen exact fixed choice references and thirteen original item images, no actual grant, inventory or calculation state mutation.'}
 with destination.open('x',encoding='utf8')as stream:stream.write(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
 return 0 if report['passed']else 1
if __name__=='__main__':raise SystemExit(main())
