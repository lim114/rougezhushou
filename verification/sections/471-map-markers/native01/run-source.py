from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import sys,json,subprocess,traceback
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/sections/471-map-markers/native01'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
from PySide6.QtCore import Qt,QPoint,QTimer
from PySide6.QtTest import QTest
from rouge import player_acceptance,player_map_acceptance as acceptance,public_event_samples as model
import player_ui_verification as ui
data_paths=['rouge/player_calculation_target.py','rouge/battle_view.py','rouge/reporting.py','rouge/mechanism_reading.py','rouge/app.py','rouge/player_compact.py','rouge/player_workspace.py','rouge/player_theme.py','rouge/player_reference_window.py','rouge/player_map_reader.py','rouge/current_map_position_view.py','rouge/player_map_hover.py','rouge/player_cannot_links.py','rouge/current_cannot_view.py','rouge/current_battle_view.py','rouge/reference_copy.py','rouge/enemy_overview.py','rouge/player_spawn_filters.py','rouge/current_stage_objects.py'];data_paths += [p.relative_to(R).as_posix()for p in(R/'rouge/data/player-theme').rglob('*')if p.is_file()];data_before={n:sha256((R/n).read_bytes()).hexdigest()for n in data_paths};(out/'additional-source-before.json').write_text(json.dumps(data_before,indent=2)+'\n','utf8')
errors=[]
def hook(kind,value,tb):errors.append(str(value));traceback.print_exception(kind,value,tb)
sys.excepthook=hook

def check(section,window,gui,require):
 from PySide6.QtWidgets import QScrollArea
 from PySide6.QtGui import QTextCursor
 before=deepcopy(window.run.state);window.show_compact();c=window.compact_window;host=c.reference_window;images=[];layouts=[]
 for timer in window.findChildren(QTimer):timer.stop()
 def settle():gui.processEvents();QTest.qWait(120);gui.processEvents()
 def click(button):
  parent=button.parentWidget()
  while parent is not None and parent is not host:
   if isinstance(parent,QScrollArea):parent.ensureWidgetVisible(button)
   parent=parent.parentWidget()
  settle();require(button.isVisible()and button.isEnabled(),'clickable_'+button.text());QTest.mouseClick(button,Qt.MouseButton.LeftButton);settle()
 def point(widget,source):
  rect=widget.image_rect();return QPoint(round(rect.left()+rect.width()*source['pixel'][0]/widget.pixmap.width()),round(rect.top()+rect.height()*source['pixel'][1]/widget.pixmap.height()))
 def save(name):
  path=out/(name+'.png');require(host.grab().save(str(path)),name+'_saved');require(host.screen().availableGeometry().contains(host.geometry()),name+'_within_screen');images.append({'file':path.relative_to(R).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
 require(c.open_full(window.battle_preview),'original_target_workspace');window.battle_preview.set_stage('ro6_n_2_3');require(window.open_calculation_target(source='stage'),'fixed_stage_shared_host');battle_page=host.pages.currentWidget();battle=battle_page.panel;require(battle.open_map_positions(),'direct_fixed_map_entry');page=host.pages.currentWidget();p=page.panel;host.resize(1000,700);settle();require(len(p.original.markers)==len(p.result['points'])>0,'only_exact_observed_points_marked');require(p.selected is None,'no_automatic_point_selection');save('numbered-original-map')
 selected=p.result['points'][0];QTest.mouseClick(p.original,Qt.MouseButton.LeftButton,pos=point(p.original,selected));settle();require(p.selected==(selected['row'],selected['col'])and p.grid.selected==p.selected and p.combo.currentIndex()==1,'native_original_click_links_exact_grid_combo');save('original-click-selected')
 for width,height in((1000,700),(650,850)):
  host.resize(width,height);settle();require(p.grid.visibleRegion().boundingRect().size()==p.grid.size(),'whole_grid_visible_'+str(width));require(p.original.visibleRegion().boundingRect().size()==p.original.size(),'whole_original_visible_'+str(width));layouts.append({'window':[width,height],'orientation':p.map_split.orientation().name,'grid_size':[p.grid.width(),p.grid.height()],'original_size':[p.original.width(),p.original.height()]});save('map-width-'+str(width))
 require(p.map_split.orientation()==Qt.Orientation.Vertical,'narrow_map_stacks_views');click(p.marker_toggle);require(not p.original.markers_visible,'markers_hidden_by_choice');old=p.selected;QTest.mouseClick(p.original,Qt.MouseButton.LeftButton,pos=point(p.original,p.result['points'][1]));settle();require(p.selected==old,'hidden_marker_not_clickable');save('marker-visibility-off');click(p.marker_toggle)
 p.tabs.setCurrentIndex(1);settle();cursor=p.technical.textCursor();cursor.setPosition(2);cursor.setPosition(8,QTextCursor.MoveMode.KeepAnchor);p.technical.setTextCursor(cursor);reading=cursor.selectedText();p.technical.verticalScrollBar().setValue(8);offset=p.technical.verticalScrollBar().value();click(p.refresh_button);require(p.selected==old and p.technical.textCursor().selectedText()==reading and p.technical.verticalScrollBar().value()==offset,'refresh_keeps_marker_selection_and_reading');p.tabs.setCurrentIndex(0);click(host.back);require(host.pages.currentWidget()is battle_page,'return_to_same_battle')
 action=next(a for a in battle.result['actions']if a['key']=='1');require(battle.focus_action(action),'exact_predefined_action');click(battle.action_position_button);action_page=host.pages.currentWidget();a=action_page.panel;host.resize(1000,700);settle();require(action_page.source_parent is battle_page,'action_map_same_host_parent');require(bool(a.original.markers),'action_has_mapped_marker');marker=a.original.markers[0];QTest.mouseClick(a.original,Qt.MouseButton.LeftButton,pos=point(a.original,marker['point']));settle();require(a.combo.currentData()==marker['key']and a.entry_key==marker['key'],'original_click_selects_exact_action_entry');require(a.original.point==marker['point'],'action_keeps_original_source_point');save('action-map-click')
 host.resize(650,850);settle();require(a.map_split.orientation()==Qt.Orientation.Vertical,'narrow_action_map_stacks_views');require(a.original.visibleRegion().boundingRect().size()==a.original.size(),'narrow_action_original_visible');save('action-map-narrow');click(host.back);require(battle.open_map_positions(),'reopen_map_history');require(host.pages.currentWidget()is page and p.selected==old,'map_history_retains_exact_selection')
 require(window.run.state==before,'run_memory_unchanged');require(not errors,'no_Qt_slot_errors');require(not window.isVisible(),'no_duplicate_main_window');window.player_validation_target=host
 (out/'images.json').write_text(json.dumps({'images':images,'public_fixed_sources_only':True},indent=2)+'\n','utf8');(out/'layout.json').write_text(json.dumps(layouts,indent=2)+'\n','utf8')

player_acceptance.check=check
raise SystemExit(ui.run(471,out/'window.json'))

