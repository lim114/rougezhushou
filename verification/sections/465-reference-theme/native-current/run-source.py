from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import sys,json,subprocess,traceback
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/sections/465-reference-theme/native-current'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
from PySide6.QtCore import Qt,QPoint,QTimer
from PySide6.QtTest import QTest
from rouge import player_acceptance,player_map_acceptance as acceptance,public_event_samples as model
import player_ui_verification as ui
data_paths=['rouge/player_theme.py','rouge/player_reference_window.py','rouge/player_map_reader.py','rouge/current_map_position_view.py','rouge/player_map_hover.py','rouge/player_cannot_links.py','rouge/current_cannot_view.py','rouge/current_battle_view.py'];data_paths += [p.relative_to(R).as_posix()for p in(R/'rouge/data/player-theme').rglob('*')if p.is_file()];data_before={n:sha256((R/n).read_bytes()).hexdigest()for n in data_paths};(out/'additional-source-before.json').write_text(json.dumps(data_before,indent=2)+'\n','utf8')
errors=[]
def hook(kind,value,tb):errors.append(str(value));traceback.print_exception(kind,value,tb)
sys.excepthook=hook

def check(section,window,gui,require):
 from rouge.player_reference_notes import note_for
 from rouge.player_notes import content_key
 from rouge import current_cannot_reference as model
 from PySide6.QtWidgets import QScrollArea
 from PySide6.QtGui import QPalette,QTextCursor
 before=deepcopy(window.run.state);app_palette=gui.palette();notes=window.player_notes;notes.autosave.setChecked(False);images=[];palette_rows=[]
 window.show_compact();c=window.compact_window
 for timer in window.findChildren(QTimer):timer.stop()
 def settle():gui.processEvents();QTest.qWait(100);gui.processEvents()
 def click(button):
  ancestor=button.parentWidget()
  while ancestor is not None and ancestor is not host:
   if isinstance(ancestor,QScrollArea):ancestor.ensureWidgetVisible(button)
   ancestor=ancestor.parentWidget()
  settle();require(button.isVisible()and button.isEnabled(),'clickable_'+button.text());QTest.mouseClick(button,Qt.MouseButton.LeftButton);settle()
 def save(name):
  path=out/(name+'.png');require(host.grab().save(str(path)),name+'_saved');require(host.screen().availableGeometry().contains(host.geometry()),name+'_within_screen');images.append({'file':path.relative_to(R).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
 def color(label,expected):
  page=host.pages.currentWidget();actual=host.palette().color(QPalette.ColorRole.Window).name();require(actual==expected,label+'_host_palette');require(page.palette().color(QPalette.ColorRole.Window).name()==expected,label+'_page_palette');palette_rows.append({'page':label,'host_window':actual,'variant':host.property('playerThemeVariant')})
 content=note_for('stages','ro6_t_6');require(c.open_saved_note(content),'exact_shop_stage_note');host=c.reference_window;c.recent_notes_popup.panel.more.setChecked(True);settle();click(notes.reference_button);root=host.pages.currentWidget();p=root.panel;handle=int(host.winId());require(p.stage_id=='ro6_t_6','exact_initial_stage');color('reference','#262528');p.tabs.setCurrentIndex(1);p.enemy_choices.select_value('0',emit=True);settle();click(p.shop_vault_button);page=host.pages.currentWidget();r=page.panel;require(page.source_parent is root and r.target==model.target_for_enemy('ro6_t_6','0'),'exact_cannot_source');color('shop-reference','#262528');save('cannot-reference')
 def back(target):require(host.back.isEnabled(),'back_button_enabled');QTest.mouseClick(host.back,Qt.MouseButton.LeftButton);settle();require(host.pages.currentWidget()is target,'back_to_'+target.windowTitle())
 def related(target):
  row=next(r.related.item(i)for i in range(r.related.count())if r.related.item(i).data(Qt.ItemDataRole.UserRole)==target);r.related.scrollToItem(row);settle();QTest.mouseClick(r.related.viewport(),Qt.MouseButton.LeftButton,pos=r.related.visualItemRect(row).center());settle();click(r.open_button)
 r.topic.setCurrentIndex(r.topic.findData('free'));settle();related({'kind':'battle','stage_id':'ro6_t_6','enemy_key':'0','reward_id':None});require(host.pages.currentWidget()is root and p.enemy_key=='0'and p.tabs.currentIndex()==1,'same_enemy_returns_to_existing_battle');click(p.shop_vault_button);require(host.pages.currentWidget()is page and r.topic.currentData()=='free','same_reference_retains_topic')
 vault=model.target_for_reward('ro6_t_6','$.predefines.tokenInsts[0]');r.entries.setCurrentIndex(next(i for i in range(r.entries.count())if r.entries.itemData(i)==vault));settle();require(r.result['selected']['pickup_free_slots_reference']==2,'vault_source_quantity_unchanged');require('不是实际已领取'not in r.player.toPlainText()and'不是实际已领取'in r.technical.toPlainText(),'vault_concise_copy_and_complete_notes');save('vault-conditions');related({'kind':'battle','stage_id':'ro6_t_6','enemy_key':None,'reward_id':vault['key']});require(host.pages.currentWidget()is root and p.rewards.combo.currentData()==vault['key'],'vault_opens_exact_reward_in_original_battle');require(p.tabs.currentWidget()is p.rewards,'reward_tab_selected');color('reward-reference','#262528');save('vault-reward-record');p.tabs.setCurrentIndex(1);click(p.shop_vault_button);require(host.pages.currentWidget()is page and r.target==vault,'vault_target_retained_on_reopen')
 r.navigate({'kind':'shop','stage_id':None,'key':None});r.floor.setCurrentIndex(r.floor.findData(4));settle();related({'kind':'battle','stage_id':'ro6_t_7','enemy_key':None,'reward_id':None});other=host.pages.currentWidget();require(other.source_parent is page and other.panel.stage_id=='ro6_t_7','other_stage_in_same_source_chain');require(int(host.winId())==handle,'same_native_host_for_other_stage');color('other-stage','#262528');back(page);require(r.floor.currentData()==4,'declared_floor_kept');r.floor.setCurrentIndex(r.floor.findData(3));host.navigate(host.cursor+1);settle();require(other not in host.history and host.pages.currentWidget()is page,'changed_floor_removes_previous_stage');r.navigate(model.target_for_enemy('ro6_t_6','0'));r.topic.setCurrentIndex(r.topic.findData('free'));r.tabs.setCurrentIndex(1);settle();r.technical.verticalScrollBar().setValue(25);offset=r.technical.verticalScrollBar().value();require(offset>0,'technical_reading_nonzero');require(r.refresh_reference(),'identical_source_refresh');settle();require(r.technical.verticalScrollBar().value()==offset,'identical_source_keeps_scroll')
 back(root);p.tabs.setCurrentIndex(0);p.map_section.expand(animate=False);click(p.position_button);map_page=host.pages.currentWidget();mp=map_page.panel;settle();color('fixed-map','#262528');require(mp.grid.grab().toImage().pixelColor(1,1).name()=='#262528','grid_margin_matches_reference');require(mp.original.grab().toImage().pixelColor(1,1).name()=='#262528','original_map_margin_matches_reference');save('neutral-fixed-map')
 require(c.open_inventory(),'inventory_entry');settle();inv=c.inventory_popup.panel;inv.held.setChecked(False);settle();color('inventory','#111213');require(c.reference_window.pages.currentWidget()is c.inventory_popup,'inventory_in_shared_host');save('neutral-inventory')
 graphs,*_=acceptance.fixtures();window.run.state['maps']={g['zone_id']:g for g in graphs};require(c.open_map(),'light_exploration_map');settle();color('exploration-map','#f5f5f7');save('light-exploration-map')
 key=content_key(content);notes.store.save(key,'### 商店挑战\n\n- 查看坎诺特机制\n- 按条件查阅保险柜奖励\n\n笔记与资料同窗切换。',notes.store.read(key)[1]);require(c.open_saved_note(content),'light_notebook_entry');settle();color('notebook','#f5f5f7');require('商店挑战'in c.recent_notes_popup.panel.preview.toPlainText(),'temporary_public_note_visible');save('light-notebook');c.recent_notes_popup.panel.more.setChecked(True);settle();click(notes.reference_button);require(host.pages.currentWidget()is root,'note_source_retains_original_stage');color('back-to-reference','#262528');require(gui.palette()==app_palette,'application_palette_not_changed');require(c.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground),'toolbar_stays_transparent');require(not c.mask().isEmpty(),'toolbar_native_input_mask_kept');require(p.shop_vault_dialog is None and r.battle_dialog is None,'legacy_dialogs_not_created');require(all(w is host or w is c or not w.isVisible()for w in gui.topLevelWidgets()),'one_reference_window_visible');require(not window.isVisible(),'full_workspace_hidden');window.run.state=before;require(window.run.state==before,'temporary_map_restored');require(not errors,'no_Qt_slot_errors');window.player_validation_target=host
 (out/'images.json').write_text(json.dumps({'images':images,'public_fixed_data_and_temporary_note_only':True},indent=2)+'\n','utf8');(out/'palette.json').write_text(json.dumps(palette_rows,indent=2)+'\n','utf8')

player_acceptance.check=check
raise SystemExit(ui.run(465,out/'window.json'))
