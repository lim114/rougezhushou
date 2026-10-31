"""Actual fixed-map selection/reuse and exact enemy-to-action-to-map navigation."""
from pathlib import Path
from hashlib import sha256
from unittest.mock import patch
import argparse,json,os,sys
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parent)]
from player_ui_verification import run
from rouge import player_acceptance


if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--receipt',type=Path,required=True);args=parser.parse_args();images=[];observations={}
 def check(section,window,gui,require):
  from PySide6.QtCore import Qt
  from PySide6.QtGui import QPixmap
  from PySide6.QtTest import QTest
  import win32gui,win32process
  from rouge.player_map_reader import make_reader
  from rouge import current_map_position_view as view,current_enemy_spawns as spawns
  def save(widget,name):
   gui.processEvents();h=int(widget.winId());require(widget.isVisible()and win32gui.IsWindowVisible(h)and win32process.GetWindowThreadProcessId(h)[1]==os.getpid(),name+'_owned_visible')
   path=args.receipt.with_name(name+'.png');require(widget.grab().save(str(path)),name+'_saved');images.append({'file':path.as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
  window.show_compact();window.hide();bar=window.compact_window
  owner=make_reader('battle',{'id':'ro6_n_6_2','title':'固定资料'},bar);require(owner is not None,'exact_sixth_floor_map_owner_available');owner.show();gui.processEvents()
  loads=[]
  class CountPixmap(QPixmap):
   def loadFromData(self,*a,**k):loads.append(1);return super().loadFromData(*a,**k)
  with patch.object(view,'QPixmap',CountPixmap):
   QTest.mouseClick(owner.panel.position_button,Qt.MouseButton.LeftButton);gui.processEvents();dialog=owner.panel.position_dialog;p=dialog.panel
   require(p.result is not None and p.result['stage_id']=='ro6_n_6_2','map_button_opens_exact_current_fixed_map')
   require(len(loads)==1 and not p.original.pixmap.isNull(),'map_original_decoded_once_at_open')
   first=p.result['points'][0];QTest.mouseClick(p.grid,Qt.MouseButton.LeftButton,pos=p.grid.center(first['row'],first['col']).toPoint());gui.processEvents()
   require(p.selected==(first['row'],first['col'])and p.original.point is not None,'actual_grid_click_maps_only_verified_center');save(dialog,'fixed-map-selected')
   known={(point['row'],point['col'])for point in p.result['points']};other=next((r,c)for r in range(p.result['rows'])for c in range(p.result['cols'])if(r,c)not in known)
   QTest.mouseClick(p.grid,Qt.MouseButton.LeftButton,pos=p.grid.center(*other).toPoint());gui.processEvents()
   require(p.selected==other and p.original.point_center()is None and not p.original.pixmap.isNull(),'unmapped_grid_click_keeps_image_without_inventing_marker')
   p.combo.setFocus();QTest.keyClick(p.combo,Qt.Key.Key_Home);QTest.keyClick(p.combo,Qt.Key.Key_Down);gui.processEvents()
   require(p.selected==(first['row'],first['col']),'actual_known_cell_choice_restores_exact_marker')
   selected=p.selected;key=p.original.pixmap.cacheKey();QTest.mouseClick(p.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents()
   require(p.selected==selected and p.original.pixmap.cacheKey()==key and len(loads)==1,'same_source_refresh_preserves_selection_and_decoded_map')
   for width in (840,1200):
    dialog.resize(width,650);gui.processEvents();rect=p.original.image_rect();center=p.original.point_center()
    require(abs((center.x()-rect.left())/rect.width()-first['pixel'][0]/p.original.pixmap.width())<1e-8,'original_center_scales_with_fixed_map_'+str(width));save(dialog,'fixed-map-width-'+str(width))
   observations['decodes_after_open_selection_refresh_and_resize']=len(loads)
   with patch.object(view.model.battle.version,'image_bytes',return_value=None):QTest.mouseClick(p.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents()
   require(p.result is None and p.original.pixmap.isNull()and p.original.image_raw is None and p.original.point_center()is None,'missing_image_clears_reused_pixels_and_marker')
   QTest.mouseClick(p.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents()
   require(p.result is not None and p.selected is None and p.original.point_center()is None and len(loads)==2,'restored_image_redecodes_and_requires_manual_choice');save(dialog,'fixed-map-restored')
  owner.close();gui.processEvents();require(not dialog.isVisible(),'owner_close_hides_owned_map_reader')
  battle=make_reader('battle',{'id':'ro6_n_1_1','title':'固定资料'},bar);battle.show();p=battle.panel;p.tabs.setCurrentIndex(1);gui.processEvents()
  combo=p.enemy_combo;index=combo.findData('5');require(index>=0,'exact_enemy_reference_is_available');combo.setFocus();QTest.keyClick(combo,Qt.Key.Key_Home)
  for _ in range(index):QTest.keyClick(combo,Qt.Key.Key_Down)
  gui.processEvents();require(p.enemy_key=='5','actual_keyboard_selects_exact_enemy_reference')
  QTest.mouseClick(p.enemy_spawns_button,Qt.MouseButton.LeftButton);gui.processEvents();child=p.enemy_spawns_dialog;lookup=child.panel
  lookup.entries.setFocus();QTest.keyClick(lookup.entries,Qt.Key.Key_Home);QTest.keyClick(lookup.entries,Qt.Key.Key_Down);gui.processEvents();action_key=lookup.entries.currentData();require(action_key is not None,'actual_corresponding_spawn_record_selected');save(child,'enemy-spawn-record')
  with patch.object(spawns,'stage_reference',wraps=spawns.stage_reference)as resolve:QTest.mouseClick(lookup.position_button,Qt.MouseButton.LeftButton);gui.processEvents()
  target=p.action_position_dialog;require(target is not None and target.isVisible(),'actual_enemy_position_button_opens_owned_map')
  require(target.panel.result['action_key']==action_key and target.panel.result['stage_id']=='ro6_n_1_1'and p.action_key==action_key,'enemy_spawn_jump_matches_exact_action_in_parent_and_map')
  require(resolve.call_count==2,'full_owned_jump_has_two_reverse_resolutions_with_parent_gate_retained');observations['current_full_parent_jump_reverse_resolutions']=resolve.call_count
  if target.panel.combo.count()>1:target.panel.combo.setFocus();QTest.keyClick(target.panel.combo,Qt.Key.Key_Home);QTest.keyClick(target.panel.combo,Qt.Key.Key_Down);gui.processEvents()
  save(target,'enemy-exact-position')
  lookup.result['enemy']['name']='synthetic stale local snapshot';received=[];lookup.actionPositionRequested.connect(received.append)
  QTest.mouseClick(lookup.position_button,Qt.MouseButton.LeftButton);gui.processEvents()
  require(lookup.result is None and not received and not target.isVisible(),'stale_reverse_snapshot_emits_nothing_and_closes_owned_position')
  battle.close();gui.processEvents();require(not child.isVisible(),'battle_close_hides_owned_reverse_reader')
  owner=make_reader('battle',{'id':'ro6_n_6_2','title':'固定资料'},bar);owner.show();QTest.mouseClick(owner.panel.position_button,Qt.MouseButton.LeftButton);gui.processEvents();window.player_validation_target=owner.panel.position_dialog
 player_acceptance.check=check;code=run(419,args.receipt)
 args.receipt.with_name('review-images.json').write_text(json.dumps({'images':images,'observations':observations,'temporary_public_fixtures_only':True,'whole_video_parity_claimed':False},ensure_ascii=False,indent=2)+'\n','utf8')
 raise SystemExit(code)
