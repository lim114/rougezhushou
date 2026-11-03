"""Retain precise map/navigation checks and verify bounded owned reader reuse."""
from pathlib import Path
from hashlib import sha256
from unittest.mock import patch
import argparse,json,os,runpy,sys
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parent)]
import player_ui_verification
from rouge import player_acceptance


if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--receipt',type=Path,required=True);args=parser.parse_args()
 native_run=player_ui_verification.run;images=[];observations={}
 def augmented_run(section,receipt):
  previous=player_acceptance.check
  def check(section,window,gui,require):
   from PySide6.QtCore import Qt
   from PySide6.QtTest import QTest
   from rouge.current_map_position_view import CurrentMapPositionDialog
   from rouge.current_action_positions_view import CurrentActionPositionsDialog
   from rouge.player_map_reader import make_reader
   from rouge import current_spawn_candidates as candidates
   import win32gui,win32process
   previous(section,window,gui,require)
   def save(widget,name):
    gui.processEvents();h=int(widget.winId());require(widget.isVisible()and win32gui.IsWindowVisible(h)and win32process.GetWindowThreadProcessId(h)[1]==os.getpid(),name+'_owned_visible')
    path=receipt.with_name(name+'.png');require(widget.grab().save(str(path)),name+'_saved');images.append({'file':path.as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
   def choose(combo,key):
    index=combo.findData(key);require(index>=0,'exact_owned_reader_choice_available');combo.setFocus();QTest.keyClick(combo,Qt.Key.Key_Home)
    for _ in range(index):QTest.keyClick(combo,Qt.Key.Key_Down)
    gui.processEvents();require(combo.currentData()==key,'actual_keyboard_selects_owned_reader_identity')
   dialog=window.player_validation_target;owner=dialog.parentWidget();choose(dialog.panel.combo,dialog.panel.combo.itemData(1));selected=dialog.panel.selected
   for _ in range(3):
    dialog.close();QTest.mouseClick(owner.position_button,Qt.MouseButton.LeftButton);gui.processEvents()
    require(owner.position_dialog is dialog and dialog.isVisible()and dialog.panel.selected==selected,'repeat_map_button_reuses_same_window_and_selected_cell')
   require(len(owner.findChildren(CurrentMapPositionDialog))==1,'three_reopens_keep_one_owned_map_dialog');save(dialog,'map-window-reused');observations['map_dialog_objects_after_three_reopens']=1
   owner.window().close();gui.processEvents()
   frame=make_reader('battle',{'id':'ro6_n_2_3','title':'固定资料'},window.compact_window);frame.show();p=frame.panel;p.tabs.setCurrentIndex(2);gui.processEvents()
   def action(key):
    item=next(p.actions.item(i)for i in range(p.actions.count())if p.actions.item(i).data(Qt.ItemDataRole.UserRole)==key)
    p.actions.scrollToItem(item);gui.processEvents();QTest.mouseClick(p.actions.viewport(),Qt.MouseButton.LeftButton,pos=p.actions.visualItemRect(item).center());gui.processEvents();require(p.action_key==key,'actual_action_choice_has_exact_current_key')
   action('1');QTest.mouseClick(p.action_position_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=p.action_position_dialog;choose(dialog.panel.combo,'0');selected=(dialog.panel.entry_key,dialog.panel.grid.selected)
   for _ in range(3):
    dialog.close();QTest.mouseClick(p.action_position_button,Qt.MouseButton.LeftButton);gui.processEvents()
    require(p.action_position_dialog is dialog and dialog.isVisible()and selected==(dialog.panel.entry_key,dialog.panel.grid.selected),'repeat_action_button_preserves_owned_window_and_exact_point')
   require(len(p.findChildren(CurrentActionPositionsDialog))==1,'three_reopens_keep_one_owned_action_dialog');save(dialog,'same-action-window-reused');observations['action_dialog_objects_after_three_reopens']=1
   action('2');require(not dialog.isVisible(),'changing_selected_action_hides_old_map_until_explicit_open')
   QTest.mouseClick(p.action_position_button,Qt.MouseButton.LeftButton);gui.processEvents()
   require(p.action_position_dialog is dialog and dialog.panel.result['action_key']=='2'and dialog.panel.entry_key is None and dialog.panel.original.point_center()is None,'reuse_for_new_action_clears_old_position_before_show');save(dialog,'changed-action-unselected')
   QTest.mouseClick(p.spawn_candidates_button,Qt.MouseButton.LeftButton);gui.processEvents();source=p.spawn_candidates_dialog;data=source.panel.result
   relation=next(row for row in data['groups']if any(m['can_request_position']for m in row['members']));member=next(m for m in relation['members']if m['can_request_position'])
   choose(source.panel.relation_combo,relation['key']);choose(source.panel.member_combo,member['action_key'])
   QTest.mouseClick(source.panel.position_button,Qt.MouseButton.LeftButton);gui.processEvents()
   require(p.action_position_dialog is dialog and p.spawn_candidates_position_dialog is dialog and dialog.isVisible(),'actual_candidate_position_jump_registers_shared_window_owner')
   with patch.object(candidates,'stage_reference',return_value=None):QTest.mouseClick(source.panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents()
   require(not dialog.isVisible()and dialog.panel.result is None,'candidate_source_failure_closes_and_clears_only_owned_position')
   QTest.mouseClick(p.action_position_button,Qt.MouseButton.LeftButton);gui.processEvents();require(dialog.isVisible()and p.spawn_candidates_position_dialog is None,'manual_position_reopen_detaches_previous_candidate_ownership')
   QTest.mouseClick(source.panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents()
   with patch.object(candidates,'stage_reference',return_value=None):QTest.mouseClick(source.panel.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents()
   require(dialog.isVisible()and dialog.panel.result is not None,'old_candidate_failure_does_not_close_new_manual_map')
   save(dialog,'manual-reader-survives-old-source-loss');frame.close();gui.processEvents();require(not dialog.isVisible()and not source.isVisible(),'root_reader_close_still_closes_shared_position_and_candidate_windows')
   frame=make_reader('battle',{'id':'ro6_n_2_3','title':'固定资料'},window.compact_window);frame.show();frame.panel.action_key='1';frame.panel.open_action_positions();window.player_validation_target=frame.panel.action_position_dialog
  player_acceptance.check=check;code=native_run(section,receipt)
  receipt.with_name('lifecycle-images.json').write_text(json.dumps({'images':images,'observations':observations,'temporary_public_fixtures_only':True,'RSS_or_whole_program_memory_claimed':False},ensure_ascii=False,indent=2)+'\n','utf8')
  return code
 with patch.object(player_ui_verification,'run',augmented_run),patch.object(sys,'argv',['verify_map_jump_review.py','--receipt',str(args.receipt)]):runpy.run_path(str(Path(__file__).with_name('verify_map_jump_review.py')),run_name='__main__')
