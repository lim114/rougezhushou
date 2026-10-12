"""Full exploration UI workflow on public temporary declarations only."""
from copy import deepcopy
import json,time,unittest
from urllib.parse import quote
from PySide6.QtCore import QUrl
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge.offline_tools_view import (OfflineToolsPanel,QUERIES,public_payload,
    exploration_presets,run_offline_query,render_offline_result)


class ExplorationToolsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])
    def setUp(self):
        self.panel=OfflineToolsPanel();self.panel.resize(1000,750);self.panel.show();self.qt.processEvents()
    def tearDown(self):self.panel.close();self.panel.deleteLater();self.qt.processEvents()
    def done(self):
        end=time.monotonic()+8
        while self.panel._workers and time.monotonic()<end:self.qt.processEvents();time.sleep(.005)
        self.assertFalse(self.panel._workers);self.qt.processEvents()
        self.assertIsNotNone(self.panel.result_snapshot(),self.panel.status.text())
    def execute(self,command):
        self.panel.select_query('exploration',command);self.panel.run_button.click();self.done()
    def source_graph(self):return public_payload('exploration','targets')['graph']
    def snapshot(self):
        cursor=self.panel.editor.textCursor()
        return (self.panel.current_query(),self.panel.editor.toPlainText(),cursor.anchor(),cursor.position(),
            self.panel.editor.verticalScrollBar().value(),self.panel.result_snapshot(),self.panel.result_view.toHtml(),
            self.panel.result_view.verticalScrollBar().value(),self.panel.raw_result.toPlainText(),
            self.panel.raw_result.verticalScrollBar().value(),self.panel.technical.isChecked(),
            self.panel.graph_node.currentData(),self.panel.preset.currentData(),
            [(w.textCursor().anchor(),w.textCursor().position(),w.horizontalScrollBar().value())
             for w in (self.panel.result_view,self.panel.raw_result)])

    def test_all_ten_queries_complete_public_results_and_readable_node_locations(self):
        count=new_count=route_count=0
        for command,title in QUERIES['exploration']:
            with self.subTest(command=command):
                payload=public_payload('exploration',command);before=deepcopy(payload)
                result=run_offline_query('exploration',command,payload)
                self.assertEqual(payload,before);self.assertFalse(result['inventory_updated'])
                rendered=render_offline_result('exploration',command,result,graph=payload.get('graph'))
                self.assertIn(title,rendered);self.assertIn('技术详情',rendered)
                self.assertIn('尚未验证当前客户端实机',rendered);json.dumps(result,allow_nan=False)
                if command=='targets':
                    self.assertIn('第2行、第4列',rendered);self.assertIn('1,3',rendered);self.assertIn('诡意行商',rendered)
                if command=='settlements':new_count+=1
                elif command=='compare-routes':route_count+=1
                else:count+=1
        self.assertEqual(count,10)
        self.assertEqual(new_count,1)
        self.assertEqual(route_count,1)

    def test_all_ten_queries_and_seven_boundary_presets_run_in_qt(self):
        count=variants=new_variants=reward_defaults=0
        original_variants={'exhausted','activation-unknown','payment-zero','random-price','exhausted-chain','main-final','gate-unknown'}
        seen_original=set()
        reward_variants=set()
        route_presets=set()
        for command,title in QUERIES['exploration']:
            self.panel.select_query('exploration',command)
            for preset in exploration_presets(command):
                with self.subTest(command=command,preset=preset['id']):
                    self.panel.preset.setCurrentIndex(self.panel.preset.findData(preset['id']))
                    self.panel.load_example.click();before=json.loads(self.panel.editor.toPlainText())
                    self.panel.run_button.click();self.done()
                    self.assertEqual(json.loads(self.panel.editor.toPlainText()),before)
                    self.assertIn(title,self.panel.result_view.toPlainText())
                    self.assertIn('所有持有/AP/状态均为说明声明',self.panel.result_view.toPlainText())
                    self.assertFalse(self.panel._result_links)
                    if command=='compare-routes':route_presets.add(preset['id'])
                    elif command=='settlements':
                        if preset['id']=='default':reward_defaults+=1
                        else:reward_variants.add(preset['id'])
                    elif preset['id']=='default':count+=1
                    elif preset['id'] in original_variants:variants+=1;seen_original.add(preset['id'])
                    else:new_variants+=1
        self.assertEqual((count,variants),(10,7))
        self.assertEqual(seen_original,original_variants)
        self.assertEqual(new_variants,6)
        self.assertEqual(reward_defaults,1)
        self.assertEqual(route_presets,{'default','route-zero','route-unknown-victory','route-repeat-reward'})
        self.assertEqual(reward_variants,{'base-pursuit-event','base-boss-pursuit','base-portal-origin-known',
            'base-portal-origin-unknown','base-special-unknown-gold','base-ambiguous-variants','base-graph-reference'})

    def test_graph_cache_refresh_preserves_complete_work_and_deep_copies(self):
        self.execute('targets');self.panel.technical.setChecked(True);self.qt.processEvents()
        c=self.panel.editor.textCursor();c.setPosition(12);c.setPosition(29,QTextCursor.MoveMode.KeepAnchor);self.panel.editor.setTextCursor(c)
        self.panel.editor.verticalScrollBar().setValue(7);self.panel.result_view.verticalScrollBar().setValue(13)
        self.panel.raw_result.verticalScrollBar().setValue(9);self.panel.graph_node.setCurrentIndex(3)
        before=self.snapshot();graph=self.source_graph()
        self.panel.set_graph(graph,epoch=123,historical=True);graph['nodes'][0]['row']=99
        self.assertNotEqual(self.panel._graph_cache['graph']['nodes'][0]['row'],99)
        refreshed=self.source_graph();refreshed['captured_at']=456
        self.panel.set_graph(refreshed,epoch=123,historical=False);self.qt.processEvents()
        self.assertEqual(self.snapshot(),before)
        self.assertIn('地图',self.panel.context_label.text())

    def test_explicit_imported_map_links_guard_epoch_template_id_and_position(self):
        graph=self.source_graph();self.panel.set_graph(graph,epoch=123,historical=False)
        self.panel.select_query('exploration','targets');self.panel.import_graph.click()
        self.panel.run_button.click();self.done();key=next(iter(self.panel._result_links));calls=[]
        self.panel.mapNodeSelected.connect(lambda node,binding:calls.append((node,binding)))
        url=QUrl('rouge-map-node:'+quote(key,safe=''));self.panel.result_view.anchorClicked.emit(url)
        self.assertEqual(calls[0][0],key);self.assertEqual(calls[0][1]['epoch'],123)
        calls[0][1]['row']=99;self.assertNotEqual(self.panel._result_links[key]['row'],99)
        before=self.snapshot()
        for field,value in (('epoch',124),('template_id','other'),('position',99)):
            changed=deepcopy(graph);epoch=123
            if field=='epoch':epoch=value
            elif field=='position':next(n for n in changed['nodes'] if n['id']==key)['row']=value
            else:changed[field]=value
            self.panel.set_graph(changed,epoch=epoch);self.panel.result_view.anchorClicked.emit(url)
            self.assertEqual(len(calls),1);self.assertIn('链接已过期',self.panel.status.text())
        self.assertEqual(self.snapshot(),before)

    def test_same_id_public_example_or_missing_epoch_never_binds_actual_map(self):
        self.panel.set_graph(self.source_graph(),epoch=123)
        self.execute('targets');self.assertFalse(self.panel._result_links)
        self.assertNotIn('rouge-map-node:',self.panel.result_view.toHtml())
        self.panel.set_graph(self.source_graph());self.panel.import_graph.click()
        self.panel.run_button.click();self.done();self.assertFalse(self.panel._result_links)

    def test_query_switch_restores_input_selection_scroll_result_and_last_family_choice(self):
        self.execute('targets');self.panel.technical.setChecked(True);self.qt.processEvents()
        cursor=self.panel.editor.textCursor();cursor.setPosition(17);cursor.setPosition(31,QTextCursor.MoveMode.KeepAnchor)
        self.panel.editor.setTextCursor(cursor);self.panel.graph_node.setCurrentIndex(4)
        self.panel.preset.setCurrentIndex(1)
        for widget in (self.panel.result_view,self.panel.raw_result):
            cursor=widget.textCursor();cursor.setPosition(4);cursor.setPosition(16,QTextCursor.MoveMode.KeepAnchor);widget.setTextCursor(cursor)
        for widget in (self.panel.editor,self.panel.result_view,self.panel.raw_result):
            widget.verticalScrollBar().setValue(widget.verticalScrollBar().maximum()//3)
        before=self.snapshot()
        self.panel.select_query('calibration','worksheets');self.qt.processEvents()
        self.panel.family.setCurrentIndex(self.panel.family.findData('exploration'));self.qt.processEvents()
        self.assertEqual(self.snapshot(),before)

    def test_fill_graph_node_and_region_import_preserve_inventory_and_ap_declarations(self):
        self.panel.select_query('exploration','options');before=json.loads(self.panel.editor.toPlainText())
        self.panel.graph_node.setCurrentIndex(1);key=self.panel.graph_node.currentData();self.panel.fill_node.click()
        after=json.loads(self.panel.editor.toPlainText());self.assertEqual(after['target'],key)
        self.assertEqual(after['inventory'],before['inventory']);self.assertEqual(after['action_points'],before['action_points'])
        graph=self.source_graph();self.panel.set_graph(graph,epoch=123)
        self.panel.select_query('exploration','budget');before=json.loads(self.panel.editor.toPlainText());self.panel.import_graph.click()
        after=json.loads(self.panel.editor.toPlainText());self.assertEqual(after['zone_id'],'zone_1')
        self.assertNotIn('graph',after);self.assertEqual(after['action_points'],before['action_points'])

    def test_stale_worker_cannot_replace_restored_query_result(self):
        self.execute('targets');before=self.panel.result_snapshot();serial=self.panel._serial
        self.panel.select_query('battle','actions');self.panel.select_query('exploration','targets')
        self.panel._finished(serial,'exploration','targets',{'wrong':'stale'},'')
        self.assertEqual(self.panel.result_snapshot(),before)

    def test_invalid_graph_structure_stays_editable_and_reports_worker_error(self):
        self.panel.select_query('exploration','targets')
        fixtures=[{'graph':{'nodes':None},'item_id':'rogue_6_scrap_M_10'},
                  {'graph':{'current_node':'a','nodes':[{'id':'a','row':0,'col':0,'node_type_raw':{'unexpected':1}}]},
                   'item_id':'rogue_6_scrap_M_10'}]
        for payload in fixtures:
            with self.subTest(payload=payload):
                text=json.dumps(payload);self.panel.editor.setPlainText(text)
                self.panel.select_query('battle','actions');self.panel.select_query('exploration','targets')
                self.assertFalse(self.panel._changing);self.assertEqual(self.panel.editor.toPlainText(),text)
                self.panel.run_button.click()
                end=time.monotonic()+8
                while self.panel._workers and time.monotonic()<end:self.qt.processEvents();time.sleep(.005)
                self.qt.processEvents();self.assertFalse(self.panel._workers)
                self.assertIsNone(self.panel.result_snapshot());self.assertIn('离线查询失败',self.panel.status.text())
                self.assertTrue(self.panel.run_button.isEnabled());self.assertFalse(self.panel._changing)
                self.panel.editor.appendPlainText(' ')
                self.assertIn('条件已修改',self.panel.status.text())

    def test_manually_moved_same_id_node_requires_fresh_visible_selection(self):
        self.panel.select_query('exploration','options');self.panel.graph_node.setCurrentIndex(1)
        node_id=self.panel.graph_node.currentData();payload=json.loads(self.panel.editor.toPlainText())
        next(n for n in payload['graph']['nodes'] if n['id']==node_id)['row']=99
        text=json.dumps(payload);self.panel.editor.setPlainText(text)
        self.panel.fill_node.click();self.assertEqual(self.panel.editor.toPlainText(),text)
        self.assertIn('请重新选择',self.panel.status.text());self.assertIsNone(self.panel.graph_node.currentData())
        index=self.panel.graph_node.findData(node_id);self.panel.graph_node.setCurrentIndex(index)
        self.assertIn('第100行',self.panel.graph_node.currentText());self.panel.fill_node.click()
        self.assertEqual(json.loads(self.panel.editor.toPlainText())['target'],node_id)


if __name__=='__main__':unittest.main()
