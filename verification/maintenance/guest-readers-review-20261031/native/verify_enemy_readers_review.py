"""Native exact buttons and lifecycle checks for all seven shared reader slots."""
from pathlib import Path
from importlib import import_module
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
  from PySide6.QtTest import QTest
  from rouge.player_map_reader import make_reader
  from rouge.battle_enemy_readers import _READERS
  import win32gui,win32process
  def save(widget,name):
   gui.processEvents();h=int(widget.winId());require(widget.isVisible()and win32gui.IsWindowVisible(h)and win32process.GetWindowThreadProcessId(h)[1]==os.getpid(),name+'_owned_visible')
   path=args.receipt.with_name(name+'.png');require(widget.grab().save(str(path)),name+'_saved');images.append({'file':path.as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
  window.show_compact();window.hide();bar=window.compact_window
  require(set(_READERS)=={'hanko','elbert','sun_boss','boss_documents','guest_knights','guest_crystals','guest_material'},'all_seven_existing_mechanism_readers_retained')
  for name,spec in _READERS.items():
   provider=import_module('rouge.'+spec.provider);sid=provider.STAGES[0];data=provider.reference(sid);row=(data.get('rows')or data.get('entities'))[0];key=row['enemy_key']if name=='boss_documents'else row['key']
   frame=make_reader('battle',{'id':sid,'title':'固定资料'},bar);frame.resize(860,700);frame.show();p=frame.panel;p.tabs.setCurrentIndex(1);gui.processEvents()
   combo=p.enemy_combo;index=combo.findData(key);require(index>=0,name+'_exact_enemy_in_current_battle');combo.setFocus();QTest.keyClick(combo,Qt.Key.Key_Home)
   for _ in range(index):QTest.keyClick(combo,Qt.Key.Key_Down)
   gui.processEvents();button=getattr(p,name+'_button');require(button.isVisible()and button.isEnabled(),name+'_exact_mechanism_button_available')
   QTest.mouseClick(button,Qt.MouseButton.LeftButton);gui.processEvents();child=getattr(p,name+'_dialog');c=child.panel
   require(child.isVisible()and c.result is not None and c.stage_id==sid,name+'_actual_button_opens_original_exact_reader')
   require(c.result['battle_source_identity']==p.result['source_identity'],name+'_child_and_parent_sources_match')
   if c.topic.count()>1:c.topic.setFocus();QTest.keyClick(c.topic,Qt.Key.Key_Home);QTest.keyClick(c.topic,Qt.Key.Key_Down);gui.processEvents()
   QTest.mouseClick(c.tabs.tabBar(),Qt.MouseButton.LeftButton,pos=c.tabs.tabBar().tabRect(1).center());gui.processEvents();c.technical.setFocus();QTest.keyClick(c.technical,Qt.Key.Key_Home,Qt.KeyboardModifier.ControlModifier)
   for _ in range(12):QTest.keyClick(c.technical,Qt.Key.Key_Right,Qt.KeyboardModifier.ShiftModifier)
   scroll=c.technical.verticalScrollBar();require(scroll.maximum()>0,name+'_technical_reading_has_real_scroll');scroll.setValue(min(3,scroll.maximum()));cursor=c.technical.textCursor();before=(c.tabs.currentIndex(),c.topic.currentData(),cursor.anchor(),cursor.position(),scroll.value())
   QTest.mouseClick(p.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents();cursor=c.technical.textCursor()
   require(before==(c.tabs.currentIndex(),c.topic.currentData(),cursor.anchor(),cursor.position(),scroll.value()),name+'_parent_refresh_preserves_topic_tab_selection_and_scroll')
   QTest.mouseClick(c.tabs.tabBar(),Qt.MouseButton.LeftButton,pos=c.tabs.tabBar().tabRect(0).center());gui.processEvents();save(child,name+'-mechanism')
   with patch.object(provider,'reference',return_value=None):QTest.mouseClick(p.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents()
   require(c.result is None and button.isHidden()and not button.isEnabled(),name+'_provider_failure_clears_reader_and_exact_entry')
   if name=='guest_material':save(child,'mechanism-source-cleared')
   QTest.mouseClick(p.refresh_button,Qt.MouseButton.LeftButton);gui.processEvents()
   require(getattr(c,'base',c.result)is not None and c.selected_key is None,name+'_source_recovery_requires_manual_entity_choice')
   combo.setFocus();QTest.keyClick(combo,Qt.Key.Key_Home);gui.processEvents();require(p.enemy_key is None and not child.isVisible()and c.result is None,name+'_changing_enemy_closes_and_clears_owned_reader')
   observations.append({'reader':name,'stage':sid,'exact_enemy_key':key,'refresh_reading_preserved':True,'source_loss_and_recovery_checked':True});frame.close();gui.processEvents()
  frame=make_reader('battle',{'id':'ro6_n_5_2','title':'固定资料'},bar);frame.show();frame.panel.tabs.setCurrentIndex(1);combo=frame.panel.enemy_combo;combo.setCurrentIndex(combo.findData(observations[-1]['exact_enemy_key']));frame.panel.open_guest_material();gui.processEvents();window.player_validation_target=frame.panel.guest_material_dialog
 player_acceptance.check=check;code=run(419,args.receipt)
 args.receipt.with_name('reader-images.json').write_text(json.dumps({'images':images,'observations':observations,'temporary_public_fixtures_only':True,'whole_video_parity_claimed':False},ensure_ascii=False,indent=2)+'\n','utf8')
 raise SystemExit(code)
