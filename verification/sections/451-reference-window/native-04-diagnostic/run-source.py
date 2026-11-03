from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import sys,json,subprocess,traceback
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/sections/451-reference-window/native-04-diagnostic'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
from PySide6.QtCore import Qt,QPoint,QTimer
from PySide6.QtTest import QTest
from rouge import player_acceptance,player_map_acceptance as acceptance,public_event_samples as model
import player_ui_verification as ui
data_paths=['rouge/player_reference_window.py','rouge/player_compact.py','tests/test_reference_window_451.py'];data_before={n:sha256((R/n).read_bytes()).hexdigest()for n in data_paths};(out/'additional-source-before.json').write_text(json.dumps(data_before,indent=2)+'\n','utf8')
errors=[]
def hook(kind,value,tb):errors.append(str(value));traceback.print_exception(kind,value,tb)
sys.excepthook=hook
def check(section,window,gui,require):
 from unittest.mock import patch
 import win32gui
 before=deepcopy(window.run.state);graphs,candidate,passed,known=acceptance.fixtures()
 window.run.state['maps']={g['zone_id']:g for g in graphs};window.show_compact();c=window.compact_window
 for timer in window.findChildren(QTimer):timer.stop()
 c.open_map();gui.processEvents();host=c.reference_window;handle=int(host.winId());p=c.map_popup.panel
 require(not c.settings_popup.isVisible() and not c.overview_popup.isVisible(),'major451_unregistered_settings_and_overview_hidden')
 require(not c.map_popup.isWindow() and c.map_popup.window() is host,'major451_map_is_child_page_not_native_dialog')
 p.type_buttons['诡意行商'].click();p.entry_search.setText('桑尼');host.resize(1100,600);gui.processEvents();query=p.entry_search.text();images=[]
 def save(name):
  path=out/(name+'.png');require(host.grab().save(str(path)),name+'_saved');images.append({'file':path.relative_to(R).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
 save('map-in-shared-host')
 c.open_inventory();gui.processEvents();require(int(host.winId())==handle and c.inventory_popup.window() is host,'major451_inventory_same_native_host');require(not c.map_popup.isVisible(),'major451_map_hidden_after_inventory');require(c.inventory_popup.resources.isVisible(),'major451_header_resources_visible');c.inventory_popup.pages.setCurrentIndex(2);save('inventory-in-shared-host')
 QTest.mouseClick(host.back,Qt.MouseButton.LeftButton);gui.processEvents();require(c.active_popup is c.map_popup and p.entry_search.text()==query,'major451_back_restores_exact_map_search');require(p.type_buttons['诡意行商'].isChecked(),'major451_back_restores_map_type_filter');require((host.width(),host.height())==(1100,600),'major451_back_restores_user_size')
 QTest.mouseClick(host.forward,Qt.MouseButton.LeftButton);gui.processEvents();require(c.active_popup is c.inventory_popup and c.inventory_popup.pages.currentIndex()==2,'major451_forward_restores_parts_tab')
 for label,open_page,attribute in [('team',c.open_team,'team_popup'),('history',c.open_replay,'replay_popup'),('scene',c.open_scene_battle,'scene_popup'),('notes',c.open_recent_notes,'recent_notes_popup')]:
  require(open_page() is not False,'major451_'+label+'_opened');gui.processEvents();page=getattr(c,attribute);require(sum(w.isVisible() for w in host.pages.findChildren(__import__('rouge.player_reference_window',fromlist=['ToolPage']).ToolPage,options=Qt.FindChildOption.FindDirectChildrenOnly))==1,'major451_'+label+'_only_one_child_page_visible');require(page.window() is host and not page.isWindow() and page.isVisible(),'major451_'+label+'_same_visible_native_host');require(int(host.winId())==handle,'major451_'+label+'_retains_handle');save(label+'-in-shared-host')
 print('SIZE_DIAGNOSTIC',[(type(w).__name__,w.size().toTuple(),w.minimumSize().toTuple(),w.minimumSizeHint().toTuple())for w in(host,host.pages,host.headers,host.titleBar,c.recent_notes_popup)],flush=True)
 require((host.width(),host.height())==(900,360),'major451_notes_initial_size_not_forced_by_hidden_large_pages')
 note=c.recent_notes_popup;history=list(host.history);cursor=host.cursor
 with patch.object(note.panel,'finish_edit',return_value=False):
  require(c.open_map() is False,'major451_unsaved_note_vetoes_switch');require(not host.close(),'major451_unsaved_note_vetoes_host_close');QTest.mouseClick(host.back,Qt.MouseButton.LeftButton);require(host.cursor==cursor and host.history==history and c.active_popup is note,'major451_unsaved_note_vetoes_back');require(host.isVisible() and note.isVisible(),'major451_unsaved_note_stays_readable')
 c.open_map();gui.processEvents();host.setProperty('playerSuspended',True);host.hide();host.show();host.setProperty('playerSuspended',False);gui.processEvents();require(c.map_popup.isVisible() and p.entry_search.text()==query,'major451_suspend_restore_preserves_map')
 c.present(c.settings_popup);gui.processEvents();require(c.settings_popup.window() is host and c.settings_scroll.isVisible(),'major451_settings_same_host');c.present(c.overview_popup);gui.processEvents();require(c.overview_popup.window() is host,'major451_overview_same_host')
 c.open_inventory();gui.processEvents();require(c.inventory_popup.pages.currentIndex()==2,'major451_direct_reopen_preserves_parts_selection');require(not c.reference_window.back.autoDefault() and not c.reference_window.forward.autoDefault(),'major451_navigation_does_not_steal_enter')
 visible=[w for w in gui.topLevelWidgets()if w.isVisible() and w is not c];require(visible==[host],'major451_only_one_visible_main_reference_top_level')
 require(host.rect().contains(host.titleBar.closeBtn.geometry()),'major451_close_button_inside_native_window');require(host in c.game_binding.surfaces(),'major451_host_in_existing_game_binding');require(not errors,'major451_no_Qt_slot_exceptions');require(window.run.state=={**before,'maps':{g['zone_id']:g for g in graphs}},'major451_no_run_change_outside_fixture')
 window.run.state=before;window.player_validation_target=host
 (out/'images.json').write_text(json.dumps({'images':images,'actual_game_or_whole_video_parity':False},indent=2)+'\n','utf8')

player_acceptance.check=check
raise SystemExit(ui.run(451,out/'window.json'))
