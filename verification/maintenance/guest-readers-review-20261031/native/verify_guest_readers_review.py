"""Retain all seven mechanism entry checks and exercise the shared guest maps."""
from pathlib import Path
from importlib import import_module
from hashlib import sha256
from unittest.mock import patch
import argparse,json,os,runpy,sys
sys.path[:0]=[str(Path(__file__).resolve().parents[1]),str(Path(__file__).resolve().parent)]
import player_ui_verification
from rouge import player_acceptance


if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--receipt',type=Path,required=True);args=parser.parse_args();native_run=player_ui_verification.run;images=[];observations=[]
 def augmented_run(section,receipt):
  previous=player_acceptance.check
  def check(section,window,gui,require):
   from PySide6.QtCore import Qt
   from PySide6.QtTest import QTest
   from rouge.player_map_reader import make_reader
   from rouge.guest_mechanism_view import GuestMechanismPanel
   import win32gui,win32process
   previous(section,window,gui,require)
   def save(widget,name):
    gui.processEvents();h=int(widget.winId());require(widget.isVisible()and win32gui.IsWindowVisible(h)and win32process.GetWindowThreadProcessId(h)[1]==os.getpid(),name+'_owned_visible')
    path=receipt.with_name(name+'.png');require(widget.grab().save(str(path)),name+'_saved');images.append({'file':path.as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
   for name in ['knights','crystals','material']:
    provider=import_module('rouge.current_guest_'+name);sid=provider.STAGES[0];data=provider.reference(sid);key=data['rows'][0]['key'];reader='guest_'+name
    frame=make_reader('battle',{'id':sid,'title':'固定资料'},window.compact_window);frame.show();p=frame.panel;p.tabs.setCurrentIndex(1);combo=p.enemy_combo;index=combo.findData(key);require(index>=0,reader+'_map_entry_exact_enemy_exists');combo.setFocus();QTest.keyClick(combo,Qt.Key.Key_Home)
    for _ in range(index):QTest.keyClick(combo,Qt.Key.Key_Down)
    gui.processEvents();QTest.mouseClick(getattr(p,reader+'_button'),Qt.MouseButton.LeftButton);gui.processEvents();dialog=getattr(p,reader+'_dialog');c=dialog.panel
    require(isinstance(c,GuestMechanismPanel)and c.model is provider,reader+'_actual_shared_widget_uses_its_own_provider')
    QTest.mouseClick(c.map_button,Qt.MouseButton.LeftButton);gui.processEvents();mapped=c.map_dialog
    require(mapped is not None and mapped.isVisible()and mapped.panel.result['stage_id']==sid and mapped.panel.result['current_level_key']==c.result['level_key'],reader+'_actual_map_button_keeps_exact_stage_and_geometry')
    points=mapped.panel.result['points'];cell=(points[0]['row'],points[0]['col'])if points else(0,0)
    QTest.mouseClick(mapped.panel.grid,Qt.MouseButton.LeftButton,pos=mapped.panel.grid.center(*cell).toPoint());gui.processEvents()
    require(mapped.panel.selected==cell,reader+'_actual_grid_click_selects_declared_cell')
    require(mapped.panel.original.point_center()is not None if points else mapped.panel.original.point_center()is None,reader+'_only_previously_calibrated_point_is_drawn');save(mapped,reader+'-shared-map')
    QTest.keyClick(mapped,Qt.Key.Key_Escape);gui.processEvents()
    require(not mapped.isVisible()and mapped.panel.result is None,reader+'_map_escape_clears_owned_pixels_and_reference')
    QTest.mouseClick(c.map_button,Qt.MouseButton.LeftButton);gui.processEvents();mapped=c.map_dialog
    with patch.object(provider,'map_target',return_value=None):QTest.mouseClick(c.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents()
    require(c.result is not None and c.map_dialog is None and not mapped.isVisible()and mapped.panel.result is None and not c.map_button.isEnabled(),reader+'_map_source_failure_keeps_mechanism_but_clears_map')
    QTest.mouseClick(c.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(c.map_button.isEnabled()and c.map_dialog is None,reader+'_map_recovery_waits_for_explicit_open')
    frame.close();gui.processEvents();require(c.result is None and not dialog.isVisible(),reader+'_parent_close_clears_shared_guest_dialog')
    observations.append({'profile':name,'stage':sid,'mapped_point_available':bool(points),'exact_map_and_escape_and_source_failure_checked':True})
   frame=make_reader('battle',{'id':'ro6_n_5_2','title':'固定资料'},window.compact_window);frame.show();p=frame.panel;p.tabs.setCurrentIndex(1);p.enemy_combo.setCurrentIndex(p.enemy_combo.findData('5'));p.open_guest_material();gui.processEvents();window.player_validation_target=p.guest_material_dialog
  player_acceptance.check=check;code=native_run(section,receipt)
  receipt.with_name('guest-map-images.json').write_text(json.dumps({'images':images,'observations':observations,'temporary_public_fixtures_only':True,'whole_video_parity_claimed':False},ensure_ascii=False,indent=2)+'\n','utf8');return code
 with patch.object(player_ui_verification,'run',augmented_run),patch.object(sys,'argv',['verify_enemy_readers_review.py','--receipt',str(args.receipt)]):runpy.run_path(str(Path(__file__).with_name('verify_enemy_readers_review.py')),run_name='__main__')
