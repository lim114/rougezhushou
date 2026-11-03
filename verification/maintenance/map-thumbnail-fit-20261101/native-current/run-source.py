from pathlib import Path
import sys,json,subprocess,traceback
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/maintenance/map-thumbnail-fit-20261101/native-current'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
from copy import deepcopy
from hashlib import sha256
from unittest.mock import patch
from PySide6.QtCore import Qt,QPoint,QRectF
from PySide6.QtGui import QTextCursor
from PySide6.QtTest import QTest
from rouge import player_acceptance,current_battle_reference as model,current_map_position as positions
from rouge.player_map_reader import make_reader
import player_ui_verification as ui
errors=[]
def hook(kind,value,tb):errors.append(str(value));traceback.print_exception(kind,value,tb)
sys.excepthook=hook
def check(section,window,gui,require):
 before=deepcopy(window.run.state);window.show_compact();c=window.compact_window;d=make_reader('battle',{'id':'ro6_n_2_3','title':'公开固定地图'},c);c.present(d);QTest.qWait(40);p=d.panel;original=p.map_image.original.toImage();key=p.map_image.original.cacheKey();images=[];sizes=[]
 def save(dialog,name):
  path=out/(name+'.png');require(dialog.grab().save(str(path)),name+'_saved');images.append({'file':path.relative_to(R).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
 def thumbnail(label):
  m=p.map_image;size=m.pixmap().deviceIndependentSize();center=QRectF(m.contentsRect()).center();rect=QRectF(center.x()-size.width()/2,center.y()-size.height()/2,size.width(),size.height());rect.translate(m.mapTo(p.overview_scroll.viewport(),QPoint(0,0)));require(QRectF(p.overview_scroll.viewport().rect()).contains(rect),label+'_full_pixmap_inside_viewport');require(p.position_button.visibleRegion().contains(p.position_button.rect().center()),label+'_magnify_entry_actually_visible');require(abs(size.width()/size.height()-m.original.width()/m.original.height())<.03,label+'_original_aspect_ratio');require(m.original.toImage()==original,label+'_original_pixels_unchanged')
 require((d.width(),d.height())==(800,340),'map_default_actual_compact_geometry');thumbnail('default');save(d,'map-whole-default')
 for w,h in((640,360),(1040,600),(800,340)):
  d.resize(w,h);QTest.qWait(30);require((d.width(),d.height())==(w,h),'map_actual_resize_'+str(w));thumbnail('resize_'+str(w));require(p.map_image.original.cacheKey()==key,'resize_'+str(w)+'_no_image_reload');sizes.append({'requested':[w,h],'actual':[d.width(),d.height()],'thumbnail_height':p.map_image.height()})
 QTest.mouseClick(p.position_button,Qt.MouseButton.LeftButton);gui.processEvents();child=p.position_dialog;q=child.panel;QTest.qWait(30);area=child.screen().availableGeometry();require(child.isVisible()and child.objectName()==d.objectName(),'map_real_button_opens_same_theme_expansion');require((child.width(),child.height())==(min(960,area.width()-40),min(640,area.height()-40)),'map_expansion_actual_default_size');require(q.result==positions.stage_reference(p.stage_id),'map_expansion_exact_original_reference');require(q.selected is None and q.original.point is None,'map_expansion_initially_no_marker');require(QRectF(q.original.rect()).contains(q.original.image_rect()),'map_expansion_original_image_whole');save(child,'map-expanded-whole')
 point=q.result['points'][0];center=q.grid.center(point['row'],point['col']);require(q.grid.rect().contains(center.toPoint()),'map_verified_cell_actual_visible');QTest.mouseClick(q.grid,Qt.MouseButton.LeftButton,pos=center.toPoint());gui.processEvents();require(q.selected==(point['row'],point['col'])and q.original.point==point,'map_real_grid_click_exact_verified_marker');save(child,'map-expanded-marker');cursor=q.player.textCursor();cursor.setPosition(3);cursor.setPosition(13,QTextCursor.MoveMode.KeepAnchor);q.player.setTextCursor(cursor);child.resize(1000,700);QTest.qWait(30);old=deepcopy(q.result);QTest.mouseClick(q.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();require(q.result==old and q.selected==(point['row'],point['col']),'map_refresh_keeps_exact_cell_and_source');require((q.player.textCursor().anchor(),q.player.textCursor().position())==(3,13),'map_refresh_keeps_reading_selection');require((child.width(),child.height())==(1000,700),'map_refresh_keeps_manual_size')
 unknown=next((r,col)for r in range(q.result['rows'])for col in range(q.result['cols'])if positions.cell_reference(q.result,r,col)['point']is None);center=q.grid.center(*unknown);QTest.mouseClick(q.grid,Qt.MouseButton.LeftButton,pos=center.toPoint());gui.processEvents();require(q.selected==unknown and q.original.point is None,'map_unmeasured_grid_cell_never_fakes_original_marker');QTest.mouseClick(child.titleBar.closeBtn,Qt.MouseButton.LeftButton);gui.processEvents();require(not child.isVisible(),'map_expansion_actual_native_close')
 QTest.mouseClick(p.position_button,Qt.MouseButton.LeftButton);gui.processEvents();require(p.position_dialog.isVisible(),'map_exact_reader_reopens');QTest.mouseClick(d.titleBar.closeBtn,Qt.MouseButton.LeftButton);gui.processEvents();require(not d.isVisible()and not p.position_dialog.isVisible(),'map_native_parent_close_closes_owned_reader');c.present(d);QTest.qWait(30);p.map_section.collapse(animate=False);p.quick_section.collapse(animate=False);p.refresh_reference();gui.processEvents();require(not p.map_section.isExpanded()and not p.quick_section.isExpanded(),'map_refresh_keeps_user_folds');p.map_section.expand(animate=False);p.overview_scroll.verticalScrollBar().setValue(0);QTest.qWait(30);thumbnail('refreshed');save(d,'map-restored-default')
 with patch.object(model,'stage_reference',return_value=None):require(not p.refresh_reference()and p.map_image.original.isNull(),'map_source_loss_removes_original')
 require(p.refresh_reference()and p.enemy_key is None,'map_recovery_requires_new_enemy_choice');require(window.run.state==before,'map_preview_never_changes_fixture_run');require(not errors,'map_no_swallowed_Qt_slot_error');(out/'images.json').write_text(json.dumps({'stage_id':p.stage_id,'images':images,'sizes':sizes,'public_fixed_data_only':True,'whole_video_parity_claimed':False},indent=2)+'\n','utf8');window.player_validation_target=d
player_acceptance.check=check
raise SystemExit(ui.run(419,out/'window.json'))
