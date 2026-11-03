from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import sys,json,subprocess,traceback
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/sections/472-floor-map/native01'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
from PySide6.QtCore import Qt,QPoint,QTimer
from PySide6.QtTest import QTest
from rouge import player_acceptance,player_map_acceptance as acceptance,public_event_samples as model
import player_ui_verification as ui
data_paths=['rouge/player_calculation_target.py','rouge/battle_view.py','rouge/reporting.py','rouge/mechanism_reading.py','rouge/app.py','rouge/player_compact.py','rouge/player_workspace.py','rouge/player_theme.py','rouge/player_reference_window.py','rouge/player_map_reader.py','rouge/current_map_position_view.py','rouge/player_map_hover.py','rouge/player_cannot_links.py','rouge/current_cannot_view.py','rouge/current_battle_view.py','rouge/reference_copy.py','rouge/enemy_overview.py','rouge/player_spawn_filters.py','rouge/current_stage_objects.py','rouge/observed_map_symbols.py','rouge/data/observed-map-symbols.json','research/floor-map-472/observations.json'];data_paths += [p.relative_to(R).as_posix()for p in(R/'rouge/data/player-theme').rglob('*')if p.is_file()];data_before={n:sha256((R/n).read_bytes()).hexdigest()for n in data_paths};(out/'additional-source-before.json').write_text(json.dumps(data_before,indent=2)+'\n','utf8')
errors=[]
def hook(kind,value,tb):errors.append(str(value));traceback.print_exception(kind,value,tb)
sys.excepthook=hook

def check(section,window,gui,require):
 from PySide6.QtWidgets import QScrollArea
 from rouge import observed_map_symbols as extra,current_action_positions as positions
 before=deepcopy(window.run.state);window.show_compact();c=window.compact_window;host=c.reference_window;images=[];rows=[]
 for timer in window.findChildren(QTimer):timer.stop()
 def settle():gui.processEvents();QTest.qWait(100);gui.processEvents()
 def click(button):
  ancestor=button.parentWidget()
  while ancestor is not None and ancestor is not host:
   if isinstance(ancestor,QScrollArea):ancestor.ensureWidgetVisible(button)
   ancestor=ancestor.parentWidget()
  settle();require(button.isVisible()and button.isEnabled(),'clickable_'+button.text());QTest.mouseClick(button,Qt.MouseButton.LeftButton);settle()
 def pixel(widget,p):
  rect=widget.image_rect();return QPoint(round(rect.left()+rect.width()*p['pixel'][0]/widget.pixmap.width()),round(rect.top()+rect.height()*p['pixel'][1]/widget.pixmap.height()))
 def save(name):
  path=out/(name+'.png');require(host.grab().save(str(path)),name+'_saved');require(host.screen().availableGeometry().contains(host.geometry()),name+'_within_screen');images.append({'file':path.relative_to(R).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
 expected=[3,3,3,3,2,2,3,3]
 for sid,count in zip(extra.STAGES,expected):
  require(c.open_full(window.battle_preview),'target_workspace_'+sid);window.battle_preview.set_stage(sid);require(window.open_calculation_target(source='stage'),'fixed_reference_'+sid);battle_page=host.pages.currentWidget();battle=battle_page.panel;require(battle.stage_id==sid,'exact_battle_'+sid);require(battle.open_map_positions(),'map_entry_'+sid);page=host.pages.currentWidget();p=page.panel;host.resize(1000,700);settle();require(p.result['stage_id']==sid and len(p.original.markers)==count,'observed_symbol_count_'+sid);require(('紧急'in host.windowTitle())==p.result['is_elite'],'caption_mode_'+sid);marker=p.original.markers[0];QTest.mouseClick(p.original,Qt.MouseButton.LeftButton,pos=pixel(p.original,marker['point']));settle();require(p.combo.currentData()==marker['key']and p.grid.selected==p.selected,'native_marker_link_'+sid);require(p.original.point['kind']=='visible_map_symbol','visible_symbol_scope_'+sid);save(sid+'-symbols');rows.append({'stage_id':sid,'symbols':count,'emergency':p.result['is_elite'],'selected':list(p.selected)})
 host.resize(650,850);settle();require(p.map_split.orientation()==Qt.Orientation.Vertical,'last_map_narrow_layout');require(p.original.visibleRegion().boundingRect().size()==p.original.size(),'narrow_original_visible');save('narrow-first-floor');click(host.back)
 require(c.open_full(window.battle_preview),'action_target_workspace');window.battle_preview.set_stage('ro6_n_1_2');require(window.open_calculation_target(source='stage'),'action_fixed_reference');battle_page=host.pages.currentWidget();battle=battle_page.panel
 action=next(a for a in battle.result['actions']if a['raw']['actionType']=='SPAWN'and any(e['center']is not None for e in positions.reference(battle.stage_id,a['key'])['entries']))
 require(battle.focus_action(action),'exact_action_for_new_symbols');click(battle.action_position_button);action_page=host.pages.currentWidget();a=action_page.panel;host.resize(1000,700);settle();require(action_page.source_parent is battle_page,'action_same_host');marker=a.original.markers[0];QTest.mouseClick(a.original,Qt.MouseButton.LeftButton,pos=pixel(a.original,marker['point']));settle();require(a.entry_key==marker['key']and a.original.point['kind']=='visible_map_symbol','action_uses_new_observation');require('遗忘时间'in host.windowTitle(),'action_caption_stage_name');save('new-symbol-action-location');click(host.back);require(host.pages.currentWidget()is battle_page,'return_to_qualified_battle')
 require(window.run.state==before,'run_memory_unchanged');require(not errors,'no_Qt_slot_errors');require(not window.isVisible(),'no_duplicate_main_window');window.player_validation_target=host
 (out/'images.json').write_text(json.dumps({'images':images,'public_fixed_sources_only':True},indent=2)+'\n','utf8');(out/'configurations.json').write_text(json.dumps(rows,indent=2)+'\n','utf8')

player_acceptance.check=check
raise SystemExit(ui.run(472,out/'window.json'))

