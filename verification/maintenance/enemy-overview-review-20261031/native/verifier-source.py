"""Real grouped enemy overview, exact row navigation and retained reading."""
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
  from PySide6.QtCore import Qt
  from PySide6.QtGui import QTextCursor
  from PySide6.QtTest import QTest
  import win32gui,win32process
  from rouge.player_map_reader import make_reader,REFERENCE_STYLE
  from rouge import current_battle_reference as model
  original=deepcopy(window.run.state);dialog=make_reader('battle',{'id':'ro6_n_2_6','title':'仅作资料'},window);require(dialog is not None,'exact_battle_source_available');dialog.show();p=dialog.panel;p.tabs.setCurrentIndex(1);gui.processEvents();tree=p.enemy_overview.tree
  def save(name):
   gui.processEvents();h=int(dialog.winId());require(dialog.isVisible()and win32gui.IsWindowVisible(h)and win32process.GetWindowThreadProcessId(h)[1]==os.getpid(),name+'_owned_visible')
   path=args.receipt.with_name(name+'.png');require(dialog.grab().save(str(path)),name+'_saved');images.append({'file':path.as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
  def rows():return [tree.topLevelItem(i).child(j)for i in range(tree.topLevelItemCount())for j in range(tree.topLevelItem(i).childCount())]
  require(p.enemy_overview.isVisible()and not p.enemy_player.isVisible()and p.enemy_key is None,'unselected_enemy_shows_actual_grouped_table')
  require([v.data(0,Qt.ItemDataRole.UserRole)for v in rows()]==[key for _,key,_ in p.enemy_choices.entries()],'all_exact_branch_references_in_table_without_name_merging')
  require(all(v.icon(0).cacheKey()==dict((key,icon.cacheKey())for _,key,icon in p.enemy_choices.entries())[v.data(0,Qt.ItemDataRole.UserRole)]for v in rows()),'table_reuses_verified_branch_icons')
  require('不用白值'in p.enemy_overview.notice.text(),'unverified_panel_not_filled_with_base_or_video_stats');require(dialog.styleSheet()==REFERENCE_STYLE,'actual_shared_reference_style_kept');save('enemy-overview')
  group=tree.topLevelItem(0);require(group.isExpanded(),'first_candidate_group_initially_expanded');tree.setCurrentItem(group);tree.setFocus();QTest.keyClick(tree,Qt.Key.Key_Left);gui.processEvents();require(not group.isExpanded(),'actual_keyboard_collapses_candidate_group')
  QTest.mouseClick(p.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();group=tree.topLevelItem(0);require(not group.isExpanded(),'actual_refresh_keeps_folded_candidate_group');save('enemy-overview-folded');tree.setCurrentItem(group);tree.setFocus();QTest.keyClick(tree,Qt.Key.Key_Right);gui.processEvents();require(group.isExpanded(),'actual_keyboard_reopens_candidate_group')
  item=rows()[0];key=item.data(0,Qt.ItemDataRole.UserRole);tree.scrollToItem(item);gui.processEvents();QTest.mouseClick(tree.viewport(),Qt.MouseButton.LeftButton,pos=tree.visualItemRect(item).center());gui.processEvents()
  require(p.enemy_key==key and p.enemy_player.isVisible()and not p.enemy_overview.isVisible(),'actual_table_row_opens_original_exact_enemy_reader')
  enemy=next(e for e in p.result['enemies']if e['key']==key);require(p.enemy_player.toPlainText()==model.enemy_text(enemy),'complete_original_mechanism_text_preserved');save('enemy-overview-selected')
  area=p.enemy_player;c=area.textCursor();c.setPosition(3);c.setPosition(15,QTextCursor.MoveMode.KeepAnchor);area.setTextCursor(c);bar=area.verticalScrollBar();require(bar.maximum()>0,'original_enemy_reading_has_actual_nonzero_scroll');bar.setValue(min(3,bar.maximum()));before=(c.anchor(),c.position(),bar.value());QTest.mouseClick(p.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();c=area.textCursor();require(before==(c.anchor(),c.position(),bar.value())and p.enemy_key==key,'actual_parent_refresh_keeps_full_enemy_reading')
  p.enemy_combo.setFocus();QTest.keyClick(p.enemy_combo,Qt.Key.Key_Home);gui.processEvents();require(p.enemy_overview.isVisible()and p.enemy_key is None,'actual_combo_returns_to_mechanism_overview')
  for width in (620,920):
   dialog.resize(width,720);gui.processEvents();require(p.enemy_overview.isVisible()and tree.viewport().width()>300 and len(rows())==len(p.result['enemies']),'overview_keeps_exact_rows_after_resize_'+str(width));save('enemy-overview-width-'+str(width));observations.append({'requested_width':width,'actual_width':dialog.width(),'table_viewport_width':tree.viewport().width(),'visible_columns':tree.columnCount()})
  p.enemy_search.setFocus();QTest.keyClicks(p.enemy_search,'__absent_enemy_9482__');gui.processEvents();require(not rows()and p.enemy_key is None,'actual_no_match_clears_overview_without_guess');save('enemy-overview-empty')
  QTest.keyClick(p.enemy_search,Qt.Key.Key_A,Qt.KeyboardModifier.ControlModifier);QTest.keyClick(p.enemy_search,Qt.Key.Key_Backspace);gui.processEvents();require(rows()and p.enemy_key is None,'clear_search_returns_exact_unselected_overview')
  with patch.object(model,'stage_reference',return_value=None):QTest.mouseClick(p.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(not rows()and not p.enemy_overview.isVisible(),'source_failure_clears_grouped_table')
  QTest.mouseClick(p.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(rows()and p.enemy_overview.isVisible()and p.enemy_key is None,'source_recovery_requires_manual_enemy_selection');save('enemy-overview-restored');window.player_validation_target=dialog
  require(window.run.state==original,'mechanism_overview_never_changes_isolated_run')
 player_acceptance.check=check;code=run(419,args.receipt)
 args.receipt.with_name('review-images.json').write_text(json.dumps({'images':images,'observations':observations,'temporary_public_fixtures_only':True,'whole_video_parity_claimed':False},ensure_ascii=False,indent=2)+'\n','utf8');raise SystemExit(code)
