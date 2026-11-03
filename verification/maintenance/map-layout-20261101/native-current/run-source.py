from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
from hashlib import sha256
import json,sys,subprocess
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/maintenance/map-layout-20261101/native-current'
if len(sys.argv)==1:
 out.mkdir()
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  p=subprocess.Popen([sys.executable,'-B','-X','utf8',str(Path(__file__)),'child'],stdout=a,stderr=b);print({'actual_retained_PID':p.pid},flush=True);code=p.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':p.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
from rouge import app as a,player_map_acceptance as acceptance
from PySide6.QtCore import QTimer,Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QPushButton
from player_ui_verification import run
original_check=acceptance.check;original_close=a.MainWindow.closeEvent
images={};geometry=[]
def check(window,gui,require):
 original_check(window,gui,require)
 before=deepcopy(window.run.state);old_graph=deepcopy(window.map_view.graph);old_historical=window.map_view.historical;graphs,candidate,passed,known=acceptance.fixtures()
 for timer in window.findChildren(QTimer):timer.stop()
 try:
  window.run.state['maps']={g['zone_id']:g for g in graphs};window.run.state['resources']={'gold':{'value':99,'captured_at':2000}}
  row={'kind':'floor_resources_read','source':'same_frame_zone_and_resources','zone_id':graphs[0]['zone_id'],'template_id':graphs[0]['template_id'],'at':1000,'values':{'gold':7,'hope':1},'capacities':{'hope':8}}
  window.run.state['history']=[row,{**row,'template_id':'other-layout','values':{'gold':777}}];window.map_view.set_map(graphs[1]);bar=window.compact_window;bar.open_map();popup=bar.map_popup;p=popup.panel;p.hover_card.dismiss();p.details_toggle.setChecked(False);p.finder_toggle.setChecked(False);p.scope_toggle.setChecked(False);p.set_type_filter(None);p.floors.setCurrentIndex(0);popup.resize(1200,460);gui.processEvents()
  require([p.floors.tabText(i)for i in range(2)]==['第一层','第二层'],'map_layout_short_floor_labels_keep_exact_zone_ids')
  require(not p.finder.isVisible()and not p.palette.isVisible()and not p.information.isVisible(),'map_layout_default_removes_permanent_sidebar_and_long_scope')
  require(popup.width()==1200 and popup.height()==460,'map_layout_actual_default_size_is1200_by460')
  require([(r['key'],r['value'])for r in p.resources.rows]==[('gold','7'),('hope','1/8')],'map_layout_historical_header_uses_matching_snapshot_not_current_or_other_template')
  images['history-map']=popup.grab();p.finder_toggle.setFocus();QTest.keyClick(p.finder_toggle,Qt.Key.Key_Space);gui.processEvents()
  require(p.palette.isVisible()and p.zoom.isVisible()and p.scope_toggle.isVisible(),'map_layout_keyboard_opens_all_tools')
  p.scope_toggle.click();gui.processEvents();require(p.status.isVisible()and p.floor_resources.isVisible(),'map_layout_full_scope_and_snapshot_remain_readable')
  p.type_buttons['诡意行商'].click();gui.processEvents();require(p.view.filter_kind=='诡意行商'and p.filter_notice.isVisible(),'map_layout_tools_preserve_exact_type_filter')
  p.finder_toggle.click();gui.processEvents();require(not p.palette.isVisible()and p.clear_filter.isVisible(),'map_layout_active_filter_stays_visible_outside_closed_tools')
  p.clear_filter.click();p.scope_toggle.setChecked(False);gui.processEvents();require(not p.filter_notice.isVisible(),'map_layout_clearing_filter_does_not_leave_empty_notice')
  chip=p.resources.chips['gold'];p.refresh();gui.processEvents();require(p.resources.chips['gold']is chip and p.floors.currentIndex()==0,'map_layout_refresh_keeps_historical_chip_and_selected_floor')
  p.view.select_node(candidate);p.select_interactive(candidate);gui.processEvents();require(p.drawer.isVisible()and p.view.selected==candidate,'map_layout_node_still_opens_details_from_default_map')
  p.details_toggle.setChecked(False);p.finder_toggle.setChecked(True);p.scope_toggle.setChecked(False)
  for width in(640,900,1200):
   popup.resize(width,740);gui.processEvents();require(popup.width()==width,'map_layout_actual_width_'+str(width))
   require(all(b.isVisible()and popup.rect().contains(b.mapTo(popup,b.rect().bottomRight()))for b in p.type_buttons.values()),'map_layout_all_type_buttons_remain_inside_'+str(width))
   require(popup.rect().contains(p.find_node.mapTo(popup,p.find_node.rect().bottomRight())),'map_layout_finder_remains_inside_'+str(width));geometry.append({'requested_width':width,'actual_size':[popup.width(),popup.height()]})
  images['map-tools']=popup.grab();p.finder_toggle.setChecked(False);p.scope_toggle.setChecked(False);p.floors.setCurrentIndex(1);popup.resize(1200,460);gui.processEvents()
  require(not p.view.historical and next(r for r in p.resources.rows if r['key']=='gold')['value']=='99','map_layout_current_floor_keeps_recent_resource_values')
  images['recent-map']=popup.grab();p.zoom.setCurrentIndex(2);gui.processEvents();scroll=p.scroll.horizontalScrollBar();require(scroll.maximum()>0,'map_layout_zoom_produces_scrollable_map');scroll.setValue(scroll.maximum()//2);old_center=(scroll.value()+scroll.pageStep()/2)/p.view.width();p.zoom.setCurrentIndex(3);gui.processEvents();center=(scroll.value()+scroll.pageStep()/2)/p.view.width();require(abs(center-old_center)<3/p.view.width(),'map_layout_upstream_zoom_preserves_map_center');p.zoom.setCurrentIndex(0);gui.processEvents()
  p.floors.setCurrentIndex(0);window.run.state['history']=[];p.refresh();gui.processEvents();require([r['value']for r in p.resources.rows]==['未记录']and'当时资源未记录'in p.context_notice.text(),'map_layout_missing_history_never_borrows_recent99')
  close_button=popup.findChild(QPushButton,'popoverCloseButton');ink=close_button.grab().toImage()
  require(sum(ink.pixelColor(x,y).alpha()>127 and ink.pixelColor(x,y).lightness()<120 for y in range(ink.height())for x in range(ink.width()))>5,'map_layout_close_glyph_visible_against_light_header')
  QTest.mouseClick(close_button,Qt.MouseButton.LeftButton);gui.processEvents();require(not popup.isVisible(),'map_layout_owned_close_button_closes_window');bar.open_map();gui.processEvents();require(popup.isVisible(),'map_layout_map_can_reopen_after_close')
  window.player_validation_target=popup
 finally:
  window.run.state=before;window.map_view.set_map(old_graph,historical=old_historical)
def close(self,event):
 rows=[]
 for name,pix in images.items():
  p=out/(name+'.png');assert pix.save(str(p));rows.append({'file':p.relative_to(R).as_posix(),'sha256':sha256(p.read_bytes()).hexdigest()})
 (out/'details.json').write_text(json.dumps({'images':rows,'geometry':geometry},ensure_ascii=False,indent=2)+'\n','utf8');original_close(self,event)
with patch.object(acceptance,'check',check),patch.object(a.MainWindow,'closeEvent',close):code=run(392,out/'window.json')
raise SystemExit(code)
