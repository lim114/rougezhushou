"""Exercise real event links, shared battle windows and ownership in isolation."""
from pathlib import Path
from copy import deepcopy
from hashlib import sha256
from unittest.mock import patch
import argparse,json,os,sys
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parent)]
from player_ui_verification import run
from rouge import player_acceptance

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--receipt',type=Path,required=True);args=parser.parse_args();images=[];observations=[]
 def check(section,window,gui,require):
  from PySide6.QtCore import Qt,QCoreApplication,QEvent
  from PySide6.QtGui import QPalette,QTextCursor
  from PySide6.QtWidgets import QPushButton
  from PySide6.QtTest import QTest
  from shiboken6 import isValid
  import win32gui,win32process
  from rouge import current_event_battles as events,current_battle_reference as battle
  from rouge.current_event_battles_view import CurrentEventBattlesDialog
  from rouge.player_map_reader import make_reader,REFERENCE_STYLE
  original=deepcopy(window.run.state)
  def save(widget,name):
   gui.processEvents();h=int(widget.winId());require(widget.isVisible()and win32gui.IsWindowVisible(h)and win32process.GetWindowThreadProcessId(h)[1]==os.getpid(),name+'_owned_visible')
   path=args.receipt.with_name(name+'.png');require(widget.grab().save(str(path)),name+'_saved');images.append({'file':path.as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
  def choose(combo,key):
   index=combo.findData(key);require(index>=0,'exact_stage_choice_available');combo.setFocus();QTest.keyClick(combo,Qt.Key.Key_Home)
   for _ in range(index):QTest.keyClick(combo,Qt.Key.Key_Down)
   gui.processEvents();require(combo.currentData()==key,'actual_keyboard_selects_exact_stage')
  frame=make_reader('battle',{'id':'ro6_t_3','title':'文献资料'},window);require(frame is not None,'original_shared_stage_available');frame.show();p=frame.panel
  require(p.event_origins_button.isVisible(),'actual_battle_to_event_entry_available');QTest.mouseClick(p.event_origins_button,Qt.MouseButton.LeftButton);gui.processEvents();source=p.event_origins_dialog
  require(source is not None and source.isVisible(),'actual_event_origins_button_opens_reader');ep=source.panel
  require(ep.stage_id=='ro6_t_3'and ep.choices.count()==1,'reverse_link_keeps_own_exact_stage_filter')
  item=ep.choices.item(0);QTest.mouseClick(ep.choices.viewport(),Qt.MouseButton.LeftButton,pos=ep.choices.visualItemRect(item).center());gui.processEvents();choose(ep.stages,'ro6_t_3');QTest.mouseClick(ep.open_button,Qt.MouseButton.LeftButton);gui.processEvents();d=ep.battle_dialog
  require(d is not None and d.isVisible()and d.panel.stage_id=='ro6_t_3','actual_event_choice_button_opens_exact_stage')
  require(d.windowFlags()&Qt.WindowType.FramelessWindowHint and d.objectName()=='mapReferenceWindow'and d.styleSheet()==REFERENCE_STYLE,'event_map_recent_share_same_real_window_factory')
  require(d.palette().color(QPalette.ColorRole.Window).name()=='#262528','shared_dark_canvas_matches_previously_verified_video_sample');require(d.panel.tabs.count()==4,'four_existing_player_groups_preserved');save(d,'event-battle-shared')
  rewards=d.panel.rewards;d.panel.tabs.setCurrentWidget(rewards);row=next(v for v in rewards.result['rows']if v['source_action_keys']);rewards.choices.select_value(row['id']);choose(rewards.source_combo,rewards.source_combo.itemData(1));selected=(rewards.combo.currentData(),rewards.source_combo.currentData());save(d,'event-battle-rewards')
  require(d.panel.open_event_origins(),'owned_nested_origin_opens');nested=d.panel.event_origins_dialog;gui.processEvents();require(nested.isVisible(),'owned_nested_origin_visible')
  close=d.findChild(QPushButton,'popoverCloseButton');require(close is not None,'actual_shared_close_button_exists');QTest.mouseClick(close,Qt.MouseButton.LeftButton);gui.processEvents();require(not d.isVisible()and not nested.isVisible()and d.panel.settlement.result is None,'real_close_clears_owned_children_and_settlement')
  for i in range(3):
   with patch.object(battle,'stage_reference',wraps=battle.stage_reference)as load:QTest.mouseClick(ep.open_button,Qt.MouseButton.LeftButton);gui.processEvents()
   require(ep.battle_dialog is d and load.call_count==1,'same_exact_link_reuses_one_window_and_single_refresh_'+str(i));require(d.panel.settlement.result is not None,'closed_base_reference_rehydrated_'+str(i))
   require(selected==(rewards.combo.currentData(),rewards.source_combo.currentData()),'reward_selection_survives_reopen_'+str(i));QTest.mouseClick(close,Qt.MouseButton.LeftButton);gui.processEvents()
  observations.append({'route':'battle_to_event_back_to_battle','exact_stage':'ro6_t_3','three_reopens_same_object':True,'stage_loads_per_reopen':1})
  source.reject();gui.processEvents();require(ep.battle_dialog is None,'Escape_reject_retires_owned_battle');frame.close()
  scope=CurrentEventBattlesDialog('黑诞','choice_ro6_normal2_2',parent=window);scope.resize(820,660);scope.show();p=scope.panel;gui.processEvents();require(p.stages.currentData()is None,'event_reader_does_not_default_actual_stage');save(scope,'event-choice-reference')
  require(p.stages.count()==7,'all_six_documented_alternatives_retained');choose(p.stages,p.stages.itemData(1));QTest.mouseClick(p.open_button,Qt.MouseButton.LeftButton);gui.processEvents();old=p.battle_dialog;old_sid=old.panel.stage_id
  choose(p.stages,p.stages.itemData(2));require(p.battle_dialog is None and not old.isVisible(),'changed_exact_stage_closes_old_source');QCoreApplication.sendPostedEvents(None,QEvent.Type.DeferredDelete);require(not isValid(old),'retired_old_window_actually_deleted')
  QTest.mouseClick(p.open_button,Qt.MouseButton.LeftButton);gui.processEvents();child=p.battle_dialog;require(child.panel.stage_id!=old_sid,'new_exact_stage_has_own_panel_and_geometry');save(child,'changed-event-battle')
  area=p.player;p.tabs.setCurrentWidget(area);c=area.textCursor();c.setPosition(3);c.setPosition(15,QTextCursor.MoveMode.KeepAnchor);area.setTextCursor(c);bar=area.verticalScrollBar();require(bar.maximum()>0,'real_parent_reader_has_scroll');bar.setValue(min(3,bar.maximum()));before=(c.anchor(),c.position(),bar.value(),p.choice_id,p.stages.currentData());QTest.mouseClick(p.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();c=area.textCursor();require(before==(c.anchor(),c.position(),bar.value(),p.choice_id,p.stages.currentData())and child.isVisible(),'real_refresh_keeps_parent_reading_and_exact_child')
  with patch.object(events,'reference',return_value=None):QTest.mouseClick(p.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(p.result is None and p.battle_dialog is None and not child.isVisible()and p.technical.toPlainText()=='','event_source_loss_clears_old_preview_and_technical_text')
  QTest.mouseClick(p.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(p.choice_id is None and p.stages.currentData()is None and not p.open_button.isEnabled(),'source_recovery_requires_new_manual_choice');save(scope,'event-source-recovered')
  scope.close();final=CurrentEventBattlesDialog('鸭托邦','choice_ro6_bat3_5',parent=window);final.resize(820,660);final.show();gui.processEvents();window.player_validation_target=final
  require(window.run.state==original,'all_event_operations_preserve_isolated_run')
 player_acceptance.check=check;code=run(419,args.receipt)
 args.receipt.with_name('review-images.json').write_text(json.dumps({'images':images,'observations':observations,'temporary_public_fixtures_only':True,'whole_video_parity_claimed':False},ensure_ascii=False,indent=2)+'\n','utf8');raise SystemExit(code)
