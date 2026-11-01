from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import sys,json,subprocess,traceback
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/sections/461-archive/native-final3'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
from PySide6.QtCore import Qt,QPoint,QTimer
from PySide6.QtTest import QTest
from rouge import player_acceptance,player_map_acceptance as acceptance,public_event_samples as model
import player_ui_verification as ui
data_paths=['rouge/public_archive_view.py','rouge/player_compact.py','rouge/app.py','research/public-reference-391/snapshot.json','tests/test_shared_archive_461.py'];data_before={n:sha256((R/n).read_bytes()).hexdigest()for n in data_paths};(out/'additional-source-before.json').write_text(json.dumps(data_before,indent=2)+'\n','utf8')
errors=[]
def hook(kind,value,tb):errors.append(str(value));traceback.print_exception(kind,value,tb)
sys.excepthook=hook

def check(section,window,gui,require):
 from tempfile import TemporaryDirectory
 from unittest.mock import patch
 from rouge import public_archive as model
 from rouge.public_archive_view import ArchivePanel
 before=deepcopy(window.run.state);window.show_compact();c=window.compact_window
 for timer in window.findChildren(QTimer):timer.stop()
 images=[]
 def settle():gui.processEvents();QTest.qWait(120);gui.processEvents()
 def save(name):
  path=out/(name+'.png');require(c.reference_window.grab().save(str(path)),name+'_saved');images.append({'file':path.relative_to(R).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
 with TemporaryDirectory()as folder:
  cache=Path(folder)/'public.json';data=model.load();cache.write_text(json.dumps(data,ensure_ascii=False),'utf8')
  with patch('rouge.public_archive_view.ArchivePanel',side_effect=lambda *a,**k:ArchivePanel(cache)):
   require(c.open_archive(),'settings_archive_entry')
  settle();page=c.archive_popup;p=window.public_archive;host=c.reference_window;handle=int(host.winId())
  require(p is page.panel and p.window()is host and not p.isWindow(),'archive_is_shared_page');require(not p.pool_note.isVisible()and not p.scope_note.isVisible(),'source_explanation_collapsed');require([host.width(),host.height()]==[850,600],'archive_compact_size');require(not window.isVisible(),'workspace_hidden')
  version='base';pool=data['versions'][version][0]['id'];require(window.open_public_pool_reference(version,pool),'workspace_exact_pool_route');settle();require(host.pages.currentWidget()is page and int(host.winId())==handle,'workspace_uses_same_host');require(p.version.currentData()==version and p.pools.currentItem().data(Qt.ItemDataRole.UserRole)==pool,'pool_id_and_version_exact');save('public-pool')
  p.scope.setChecked(True);cursor=p.pool_note.textCursor();cursor.setPosition(1);cursor.setPosition(5,cursor.MoveMode.KeepAnchor);p.pool_note.setTextCursor(cursor);selected=cursor.selectedText()
  require(c.open_inventory(),'open_inventory');c.inventory_popup.panel.openPoolReference.emit(version,pool);settle();require(host.pages.currentWidget()is page,'inventory_pool_route_shared');require(p.pool_note.textCursor().selectedText()==selected,'pool_reopen_keeps_reading')
  input_pool=next(v for v in data['versions'][version]if v['name']=='失与得：N藏品输入'and v['collectibles']);require(c.open_exchange(version,input_pool['collectibles'][0]),'exchange_input_opens');settle();exchange=c.exchange_popup.panel;exchange.choices.setCurrentIndex(1);settle();target=exchange.current_link();require(target is not None and exchange.open_button.isEnabled(),'exchange_output_has_reference');QTest.mouseClick(exchange.open_button,Qt.MouseButton.LeftButton);settle();require(host.pages.currentWidget()is page and p.pools.currentItem().data(Qt.ItemDataRole.UserRole)==target['output_id'],'exchange_output_pool_route_shared')
  require(not c.open_archive_pool('missing-version',pool),'missing_pool_range_rejected');require(p.pools.currentItem()is None and p.members.rowCount()==0,'missing_pool_clears_old_members');require(c.open_archive(),'archive_can_reopen')
  p.tabs.setCurrentIndex(1);p.floor.setCurrentIndex(p.floor.findData(3));p.event_search.setText('黑诞');p.events.setCurrentRow(next(i for i in range(p.events.count())if p.events.item(i).data(Qt.ItemDataRole.UserRole)=='rogue_6:scene_ro6_normal2_enter'));settle();context=deepcopy(p.reference_context());require('黑诞'in p.event_note.toPlainText(),'event_name_and_conditions_readable');QTest.keyClick(p.event_search,Qt.Key.Key_Return);settle();require(not p.busy,'search_return_does_not_fetch');require(page.body_scroll.verticalScrollBar().maximum()==0,'default_event_page_fits_body');require(p.event_button.mapTo(page.body_scroll.viewport(),p.event_button.rect().bottomRight()).y()<page.body_scroll.viewport().height(),'event_action_is_in_viewport');save('public-event');(out/'layout.json').write_text(json.dumps({'panel':[p.width(),p.height()],'viewport':[page.body_scroll.viewport().width(),page.body_scroll.viewport().height()],'scroll_max':page.body_scroll.verticalScrollBar().maximum(),'event_list_height':p.events.height(),'event_button_top':p.event_button.mapTo(page.body_scroll.viewport(),p.event_button.rect().topLeft()).y(),'event_button_bottom':p.event_button.mapTo(page.body_scroll.viewport(),p.event_button.rect().bottomRight()).y()},indent=2)+'\n','utf8')
  QTest.mouseClick(p.event_button,Qt.MouseButton.LeftButton);settle();flow_page=host.pages.currentWidget();flow=flow_page.panel;require(flow_page.source_parent is page and flow.scene_id=='scene_ro6_normal2_enter','exact_full_event_in_shared_host');require(flow.choice_id is None,'no_game_choice_assumed')
  cid=next(v['id']for v in flow.result['choices'].values()if'choice_ro6_normal2_2'in v['variant_ids']);flow.choices.setCurrentRow(next(i for i in range(flow.choices.count())if flow.choices.item(i).data(Qt.ItemDataRole.UserRole)==cid));settle();require(flow.battle_button.isEnabled(),'event_battle_link_available');save('complete-event')
  QTest.mouseClick(flow.battle_button,Qt.MouseButton.LeftButton);settle();config_page=host.pages.currentWidget();configs=config_page.panel;require(config_page.source_parent is flow_page,'event_configuration_in_same_chain');configs.stages.setCurrentIndex(next(i for i in range(configs.stages.count())if configs.stages.itemData(i)=='ro6_t_13'));settle();QTest.mouseClick(configs.open_button,Qt.MouseButton.LeftButton);settle();battle=host.pages.currentWidget();require(battle.source_parent is config_page and battle.panel.stage_id=='ro6_t_13','archive_event_reaches_fixed_battle');save('archive-to-battle')
  require(int(host.winId())==handle,'same_native_host_throughout');host.navigate(host.history.index(page));settle();require(p.reference_context()==context and p.event_search.text()=='黑诞','back_keeps_event_filter_selection');QTest.mouseClick(p.event_button,Qt.MouseButton.LeftButton);settle();require(host.pages.currentWidget()is flow_page,'full_event_page_reused')
  p.event_search.setText('not-an-event');require(not flow_page.prepare(),'changed_parent_range_rejects_child');settle();require(host.pages.currentWidget()is page and all(v not in host.history for v in [flow_page,config_page,battle]),'changed_event_removes_entire_child_chain')
  p.event_search.setText('黑诞');p.events.setCurrentRow(0);settle()
  with patch('rouge.documented_readers.reader_plan',return_value=None):QTest.mouseClick(p.event_button,Qt.MouseButton.LeftButton)
  settle();raw=host.pages.currentWidget();require(raw.source_parent is page and raw.panel.identity=='scene_ro6_normal2_enter','original_scene_fallback_is_exact');host.navigate(host.history.index(page));settle()
  cache.write_text('{}','utf8');p.reload_local();settle();require(p.data is None and p.events.count()==0 and p.members.rowCount()==0,'source_loss_clears_archive');require(not raw.prepare(),'source_loss_removes_old_original_scene');require(not host.linked_pages,'source_loss_removes_linked_pages')
 require(window.run.state==before,'temporary_run_unchanged');require(not errors,'no_Qt_slot_errors');require(all(w is c or w is host or not w.isVisible()for w in gui.topLevelWidgets()),'one_visible_reference_window');window.player_validation_target=host
 (out/'images.json').write_text(json.dumps({'images':images,'public_source_fixture_only':True},ensure_ascii=False,indent=2)+'\n','utf8')

player_acceptance.check=check
raise SystemExit(ui.run(461,out/'window.json'))
