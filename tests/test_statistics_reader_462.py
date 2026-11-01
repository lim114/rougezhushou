from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace,MethodType
from copy import deepcopy
from unittest.mock import patch,Mock
import unittest,time
from PySide6.QtCore import Qt,Signal,QRect
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication,QWidget,QLabel
from rouge.node_statistics_source import NodeStatisticsSource
from rouge.public_node_statistics_view import StatisticsPanel
from rouge.public_archive_view import ArchivePanel
from rouge.player_reference_window import ReferenceWindow,ToolPage
from rouge.player_compact import CompactAssistant
from tests import test_node_card_source_review as samples


class StatisticsReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def setUp(self):
        self.temp=TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.source=NodeStatisticsSource(Path(self.temp.name)/'nodes.json');self.source.accept(samples.public_example())
        self.owner=QWidget();self.owner.owner=SimpleNamespace(public_statistics=None,node_statistics_source=lambda:self.source);self.owner.statistics_popup=None
        self.owner.reference_window=self.host=ReferenceWindow(self.owner);self.owner.present=self.host.present
        for name in ['statistics_reader','open_statistics','open_map_statistics']:setattr(self.owner,name,MethodType(getattr(CompactAssistant,name),self.owner))
        self.owner.open_statistics();self.p=self.owner.owner.public_statistics;self.qt.processEvents();self.addCleanup(self.cleanup)
    def cleanup(self):self.host.close();self.owner.deleteLater();self.qt.processEvents()
    def graph(self,distance=2):return {'zone_id':'zone_1','grid':{'rows':3},'nodes':[{'id':'point-a','row':1,'col':3,'distance':distance}]}
    def test_map_query_uses_exact_node_and_manual_edit_clears_old_position(self):
        self.assertTrue(self.p.set_map_node(self.graph(),'point-a'));self.assertEqual((self.p.floor.currentData(),self.p.distance.value()),('0',2));self.assertIn('中排 · 第4列',self.p.context.text());self.assertEqual(self.p.table.item(0,1).text(),'70.00%')
        self.p.distance.setValue(3);self.assertIn('手动查询',self.p.context.text());self.assertNotIn('第4列',self.p.context.text());self.assertEqual(self.p.table.rowCount(),0);self.assertIn('暂无统计',self.p.status.text())
    def test_invalid_or_outside_map_distance_does_not_clamp_into_other_query(self):
        self.p.distance.setValue(2)
        for distance in [-1,101,True,2.5]:
            self.assertFalse(self.p.set_map_node(self.graph(distance),'point-a'));self.assertEqual(self.p.distance.value(),2);self.assertIn('手动查询',self.p.context.text())
        self.assertFalse(self.p.set_map_node({'zone_id':'zone_6','nodes':self.graph()['nodes']},'point-a'));self.assertNotIn('查询位置',self.p.context.text())
    def test_shared_reopen_keeps_manual_query_type_selection_and_skips_repeat_render(self):
        self.p.distance.setValue(2);self.p.table.setCurrentCell(1,3);selected=self.p.table.item(1,0).data(Qt.ItemDataRole.UserRole)
        other=ToolPage('另一页',QWidget(),self.owner);self.host.present(other)
        with patch.object(self.p.table,'setRowCount',wraps=self.p.table.setRowCount)as rebuilt:
            self.assertTrue(self.owner.open_statistics());self.p.render();rebuilt.assert_not_called()
        self.assertIs(self.p.window(),self.host);self.assertFalse(self.p.isWindow());self.assertEqual(self.p.distance.value(),2);self.assertEqual(self.p.table.item(self.p.table.currentRow(),0).data(Qt.ItemDataRole.UserRole),selected)
    def test_shared_source_update_keeps_query_and_selected_type_when_row_order_changes(self):
        self.p.set_map_node(self.graph(),'point-a');self.p.table.setCurrentCell(1,2);selected=self.p.table.item(1,0).data(Qt.ItemDataRole.UserRole)
        changed=samples.public_example(80);changed['counts']=dict(reversed(list(changed['counts'].items())));self.source.accept(changed)
        self.assertIs(self.p.source,self.source);self.assertEqual(self.p.distance.value(),2);self.assertEqual(self.p.table.item(self.p.table.currentRow(),0).data(Qt.ItemDataRole.UserRole),selected);self.assertEqual(self.p.table.currentColumn(),2)
        trader=next(i for i in range(self.p.table.rowCount())if self.p.table.item(i,0).data(Qt.ItemDataRole.UserRole)=='rogue-trader');self.assertEqual(self.p.table.item(trader,1).text(),'80.00%');self.assertIn('查询位置',self.p.context.text())
    def test_failed_or_invalid_update_keeps_previous_source_and_reading(self):
        self.p.distance.setValue(2);before=deepcopy(self.source.data);self.p.table.setCurrentCell(1,0);selected=self.p.table.currentRow()
        self.p.accept_data({'error':'simulated offline'});self.assertEqual(self.source.data,before);self.assertEqual(self.p.table.currentRow(),selected);self.assertIn('更新失败',self.p.status.text())
        self.p.accept_data({'data':{}});self.assertEqual(self.source.data,before);self.assertEqual(self.p.table.item(0,1).text(),'70.00%')
    def test_identical_successful_update_clears_loading_label_without_rebuilding_table(self):
        self.p.distance.setValue(2);self.p.table.setCurrentCell(1,0);self.p.busy=True;self.p.refresh_button.setEnabled(False);self.p.status.setText('正在更新公开统计…')
        with patch.object(self.p.table,'setRowCount',wraps=self.p.table.setRowCount)as rebuilt:
            self.p.accept_data({'data':deepcopy(self.source.data)});rebuilt.assert_not_called()
        self.assertFalse(self.p.busy);self.assertTrue(self.p.refresh_button.isEnabled());self.assertNotIn('正在',self.p.status.text());self.assertEqual(self.p.table.currentRow(),1)
    def test_unavailable_source_has_no_stale_table_and_does_not_fetch(self):
        with patch('rouge.public_node_statistics.load',side_effect=ValueError('isolated unavailable source')):
            empty=NodeStatisticsSource(Path(self.temp.name)/'empty.json')
        p=StatisticsPanel(empty.cache,source=empty);self.addCleanup(p.close);self.assertEqual(p.table.rowCount(),0);self.assertIn('暂无公开统计',p.status.text());self.assertFalse(p.busy)


class ArchiveResizeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def test_effect_rows_reflow_after_window_width_changes_without_reloading_data(self):
        with TemporaryDirectory()as folder:
            p=ArchivePanel(Path(folder)/'absent-public-cache.json');self.addCleanup(p.close);p.resize(1100,600);p.show();p.pools.setCurrentRow(0)
            rows=[{'id':'public-layout-example','name':'效果说明示例','rate':None,'count':None,'total':None,'effect':'这段说明用于验证改变窗口宽度后仍可逐行阅读。'*5,'icon':None}]
            with patch('rouge.public_archive_view.model.members',return_value=rows):p.render_members()
            self.qt.processEvents();QTest.qWait(60);wide=p.members.rowHeight(0);p.resize(550,600);self.qt.processEvents();QTest.qWait(60);narrow=p.members.rowHeight(0)
            self.assertGreater(narrow,wide);self.assertEqual(p.members.item(0,3).text(),rows[0]['effect']);p.resize(1100,600);self.qt.processEvents();QTest.qWait(60);self.assertEqual(p.members.rowHeight(0),wide)


class HoverSourceRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def test_accepted_owned_card_opens_exact_archive_pool_through_current_route(self):
        from rouge.player_game_hover import GameHover
        class Card(QWidget):
            poolRequested=Signal(str,str)
            def __init__(self,parent):super().__init__(parent);self.notice=QLabel(self)
            def install(self,*_):return True
            def dismiss(self):self.hide()
        c=QWidget();self.addCleanup(c.deleteLater);c.open_archive_pool=Mock();c.hidden_windows=None
        snapshot={'active':True,'cursor_on_game':True,'key':(101,102),'physical_client':(0,0,1000,700),'logical_client':QRect(0,0,1000,700),'cursor':(30,30),'screen':SimpleNamespace(availableGeometry=lambda:QRect(0,0,1000,700))}
        c.game_binding=SimpleNamespace(target=lambda:{'hwnd':101,'pid':102},api=SimpleNamespace(read=lambda _:snapshot))
        inventory=SimpleNamespace(reload_sources=Mock(),version=SimpleNamespace(currentData=lambda:'dlc1'),source_index=object(),source_signature='public-fixture')
        owner=SimpleNamespace(closing=False,run=SimpleNamespace(recognition_context=lambda:{'run_id':'isolated'}),inventory_panel=inventory)
        hover=GameHover(c,owner);hover.timer.stop();self.addCleanup(hover.close)
        request={'serial':hover.serial,'run_id':'isolated','captured_at':time.time(),'key':(101,102),'target':{},'physical_client':snapshot['physical_client'],'cursor':snapshot['cursor']}
        with patch('rouge.expansion_reference.packet',return_value={'current':{'details':{'items':{'example':{'name':'藏品示例','iconId':None}}}}}),patch('rouge.player_item_hover.ItemHoverCard',Card):
            hover.accept({'request':request,'item':{'id':'example','confirmed':True}})
        self.assertTrue(hover.last_report['accepted']);hover.card.poolRequested.emit('dlc1','pool-a');c.open_archive_pool.assert_called_once_with('dlc1','pool-a')
