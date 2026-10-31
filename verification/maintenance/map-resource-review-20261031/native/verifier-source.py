"""Read newly recorded same-frame resources in actual native map replay."""
from pathlib import Path
from copy import deepcopy
from hashlib import sha256
import argparse,json,os,sys
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parent)]
from player_ui_verification import run
from rouge import player_acceptance

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--receipt',type=Path,required=True);args=parser.parse_args();images=[]
 def check(section,window,gui,require):
  from PySide6.QtCore import Qt
  from PySide6.QtTest import QTest
  from rouge.player_replay_archive import reload_history
  from tests.test_map_resource_review import graph
  import win32gui,win32process
  before=deepcopy(window.run.state);at=before['started_at']+1
  def save(widget,name):
   gui.processEvents();h=int(widget.winId());require(widget.isVisible()and win32gui.IsWindowVisible(h)and win32process.GetWindowThreadProcessId(h)[1]==os.getpid(),name+'_owned_visible')
   path=args.receipt.with_name(name+'.png');require(widget.grab().save(str(path)),name+'_saved');images.append({'file':path.as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
  def choose(page,index):
   item=page.entries.item(index);page.entries.scrollToItem(item);gui.processEvents();QTest.mouseClick(page.entries.viewport(),Qt.MouseButton.LeftButton,pos=page.entries.visualItemRect(item).center());gui.processEvents();require(page.entries.currentItem()is item,'actual_mouse_selects_exact_saved_row')
  try:
   require(window.apply_run_observation({'map':graph(),'resources':{'gold':{'value':7}}},at),'actual_MainWindow_accepts_same_frame_map_and_resource')
   history=deepcopy(window.run.state['history']);window.show_compact();window.hide();bar=window.compact_window;bar.open_replay();gui.processEvents();dialog=bar.replay_popup;panel=dialog.panel;page=panel.nodes
   idx=panel.tabs.indexOf(page);QTest.mouseClick(panel.tabs.tabBar(),Qt.MouseButton.LeftButton,pos=panel.tabs.tabBar().tabRect(idx).center());gui.processEvents();require(page.isVisible()and page.entries.count()==2,'actual_replay_tab_has_both_new_map_rows')
   choose(page,0);require('源石锭 7'in page.resources.text(),'first_same_frame_map_row_shows_accepted_resource');selected=page.entries.currentItem().data(Qt.ItemDataRole.UserRole);save(dialog,'same-frame-first-map')
   require(window.apply_run_observation({'map':graph(position=1),'resources':{'gold':{'value':99}}},at+1),'actual_MainWindow_accepts_later_frame');bar.refresh();gui.processEvents()
   require(window.run.state['history'][:len(history)]==history,'later_apply_does_not_reorder_or_rewrite_old_history');require(page.entries.currentItem().data(Qt.ItemDataRole.UserRole)==selected and'源石锭 7'in page.resources.text(),'actual_refresh_keeps_selected_past_value');save(dialog,'same-frame-keeps-past')
   choose(page,page.entries.count()-1);require('源石锭 99'in page.resources.text(),'later_map_row_has_own_new_resource');save(dialog,'same-frame-later-map')
   archived=deepcopy(window.run.state);panel.history_store.archive(archived);reload_history(panel);gui.processEvents();session=panel.sessions.findData('archive:'+archived['id']);require(session>=0,'actual_temporary_archive_session_available');panel.sessions.setCurrentIndex(session);gui.processEvents();choose(page,0)
   require('源石锭 7'in page.resources.text()and page.view.graph is not None,'archived_first_map_keeps_exact_same_frame_resource');save(dialog,'same-frame-archive');require(window.run.state==archived,'reading_archive_keeps_current_temporary_run');window.player_validation_target=dialog
  finally:window.run.state=before
  require(window.run.state==before,'all_public_map_checks_restore_only_owned_temporary_fixture')
 player_acceptance.check=check;code=run(403,args.receipt)
 args.receipt.with_name('review-images.json').write_text(json.dumps({'images':images,'temporary_public_fixtures_only':True,'game_observation_claimed':False,'whole_video_parity_claimed':False},ensure_ascii=False,indent=2)+'\n','utf8');raise SystemExit(code)
