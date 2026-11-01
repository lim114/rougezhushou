from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import sys,json,subprocess,traceback
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];out=R/'verification/sections/462-statistics/native-final'
if len(sys.argv)==1:
 out.mkdir(exist_ok=False)
 with(out/'stdout.txt').open('xb')as a,(out/'stderr.txt').open('xb')as b:
  child=subprocess.Popen([sys.executable,'-B','-X','utf8',__file__,'child'],cwd=R,stdout=a,stderr=b);print({'actual_retained_PID':child.pid},flush=True);code=child.wait()
 (out/'process.json').write_text(json.dumps({'actual_retained_PID':child.pid,'actual_observed_exit':code},indent=2)+'\n','utf8');(out/'run-source.py').write_bytes(Path(__file__).read_bytes());print({'actual_exit':code});raise SystemExit(code)
from PySide6.QtCore import Qt,QPoint,QTimer
from PySide6.QtTest import QTest
from rouge import player_acceptance,player_map_acceptance as acceptance,public_event_samples as model
import player_ui_verification as ui
data_paths=['rouge/public_node_statistics_view.py', 'rouge/player_compact.py', 'rouge/player_game_hover.py', 'rouge/player_item_hover.py', 'rouge/public_archive_view.py', 'rouge/app.py', 'rouge/player_map.py', 'rouge/data/map-templates.json', 'research/public-statistics-388/nodes.json'];data_before={n:sha256((R/n).read_bytes()).hexdigest()for n in data_paths};(out/'additional-source-before.json').write_text(json.dumps(data_before,indent=2)+'\n','utf8')
errors=[]
def hook(kind,value,tb):errors.append(str(value));traceback.print_exception(kind,value,tb)
sys.excepthook=hook

def check(section,window,gui,require):
 from tempfile import TemporaryDirectory
 from unittest.mock import patch
 from rouge import public_node_statistics as statistics,public_archive
 from rouge.node_statistics_source import NodeStatisticsSource
 from rouge.public_archive_view import ArchivePanel
 before=deepcopy(window.run.state);old_source=window._node_statistics_source;original_map=(window.map_view.graph,window.map_view.selected);images=[];layouts=[]
 def settle():gui.processEvents();QTest.qWait(160);gui.processEvents()
 def save(name):
  path=out/(name+'.png');require(c.reference_window.grab().save(str(path)),name+'_saved');images.append({'file':path.relative_to(R).as_posix(),'sha256':sha256(path.read_bytes()).hexdigest()})
 with TemporaryDirectory()as folder:
  source=NodeStatisticsSource(Path(folder)/'nodes.json');data=statistics.load();source.accept(data);window._node_statistics_source=source
  graphs,node_id,*_=acceptance.fixtures();node=next(n for n in graphs[0]['nodes']if n['id']==node_id);node['distance']=2;graphs[1]['nodes'][0]['distance']=5
  window.run.state['maps']={g['zone_id']:g for g in graphs};window.map_view.graph=graphs[1];window.map_view.selected=graphs[1]['nodes'][0]['id'];window.show_compact();c=window.compact_window
  for timer in window.findChildren(QTimer):timer.stop()
  require(c.open_map(),'open_compact_map');mp=c.map_popup.panel;mp.floors.setCurrentIndex(next(i for i in range(mp.floors.count())if mp.floors.tabData(i)=='zone_1'));mp.view.selected=node_id;mp.selected(node_id);settle();require(mp.statistics_button.isVisible(),'map_statistics_action_visible');handle=int(c.reference_window.winId())
  QTest.mouseClick(mp.statistics_button,Qt.MouseButton.LeftButton);settle();host=c.reference_window;page=c.statistics_popup;p=window.public_statistics
  require(host.pages.currentWidget()is page and p.window()is host and not p.isWindow(),'statistics_in_main_host');require(p.source is source and mp.statistics_source is source,'map_and_statistics_share_source');require((p.floor.currentData(),p.distance.value())==('0',2),'compact_map_query_ignores_outer_workspace_map');require('查询位置'in p.context.text(),'map_location_caption');require([host.width(),host.height()]==[760,520],'compact_statistics_dimensions');require(not p.notice.isVisible(),'scope_details_collapsed')
  expected=statistics.frequency_rows(data,'0',2);require(p.table.rowCount()==len(expected),'original_public_row_count')
  for i,row in enumerate(expected):require([p.table.item(i,j).text()for j in range(4)]==[row['name'],f"{row['frequency']:.2%}",str(row['count']),str(row['total'])],str(i)+'_original_public_counts_and_frequency')
  save('mapped-statistics');p.distance.setValue(3);settle();require('手动查询'in p.context.text()and'查询位置'not in p.context.text(),'manual_edit_clears_old_map_caption');p.distance.setValue(2);p.table.setCurrentCell(0,1);selected=p.table.item(0,0).data(Qt.ItemDataRole.UserRole);save('manual-statistics')
  require(c.present(c.settings_popup),'settings_open');c.settings_scroll.ensureWidgetVisible(c.buttons['节点统计']);settle();QTest.mouseClick(c.buttons['节点统计'],Qt.MouseButton.LeftButton);settle();require(host.pages.currentWidget()is page and p.distance.value()==2,'settings_preserves_previous_query');require(p.table.item(p.table.currentRow(),0).data(Qt.ItemDataRole.UserRole)==selected,'settings_preserves_table_selection')
  with patch.object(p.table,'setRowCount',wraps=p.table.setRowCount)as rebuild:require(c.open_statistics(),'repeat_statistics_entry');rebuild.assert_not_called()
  p.status.setText('正在更新公开统计…');p.busy=True;p.accept_data({'data':deepcopy(data)});require(not p.busy and'正在'not in p.status.text(),'identical_success_clears_loading_state');require(p.table.currentRow()==0,'identical_success_keeps_reading');snapshot=[p.table.item(i,1).text()for i in range(p.table.rowCount())];p.accept_data({'error':'isolated failed update'});require([p.table.item(i,1).text()for i in range(p.table.rowCount())]==snapshot,'failed_update_retains_accepted_statistics')
  require(window.open_public_statistics(),'workspace_statistics_route');settle();require(host.pages.currentWidget()is page and p.floor.currentData()=='1'and p.distance.value()==5,'workspace_query_uses_its_explicit_map_context');require(int(host.winId())==handle,'workspace_same_native_host')
  cache=Path(folder)/'archive.json';cache.write_text(json.dumps(public_archive.load(),ensure_ascii=False),'utf8')
  with patch('rouge.public_archive_view.ArchivePanel',side_effect=lambda *a,**k:ArchivePanel(cache)):require(c.open_archive(),'archive_for_width_check')
  archive=c.archive_popup.panel;version='base';identity=archive.data['versions'][version][0]['id'];require(c.open_archive_pool(version,identity),'exact_pool_for_width_check');settle();table=archive.members;row=max(range(table.rowCount()),key=lambda i:len(table.item(i,3).text()));effect=table.item(row,3).text()
  for width in [1100,600,1100]:
   host.resize(width,600);settle();table.setCurrentCell(row,3);table.scrollToItem(table.item(row,3));settle();layouts.append({'width':host.width(),'effect_width':table.columnWidth(3),'row_height':table.rowHeight(row)});require(table.item(row,3).text()==effect,str(width)+'_effect_text_unchanged')
   if width==600:save('narrow-pool-effects')
  require(layouts[1]['row_height']>layouts[0]['row_height']and layouts[2]['row_height']==layouts[0]['row_height'],'real_pool_effect_reflows_without_source_reload');require(c.open_map(),'back_to_compact_map');settle();QTest.mouseClick(mp.statistics_button,Qt.MouseButton.LeftButton);settle();require((p.floor.currentData(),p.distance.value())==('0',2),'map_route_still_uses_displayed_floor_after_other_queries')
  require(int(host.winId())==handle,'one_native_host_for_map_statistics_and_archive');require(not window.isVisible(),'workspace_stays_hidden');require(all(w is host or w is c or not w.isVisible()for w in gui.topLevelWidgets()),'one_reference_window_visible')
 window.run.state=before;window._node_statistics_source=old_source;window.map_view.graph,window.map_view.selected=original_map;require(window.run.state==before,'temporary_run_restored');require(not errors,'no_Qt_slot_errors');window.player_validation_target=host
 (out/'images.json').write_text(json.dumps({'images':images,'licensed_public_statistics_and_archive_only':True},indent=2)+'\n','utf8');(out/'layout.json').write_text(json.dumps({'archive_resize':layouts},indent=2)+'\n','utf8')

player_acceptance.check=check
raise SystemExit(ui.run(462,out/'window.json'))
