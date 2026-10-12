import json,time,unittest
from copy import deepcopy
from PySide6.QtCore import QUrl
from PySide6.QtWidgets import QApplication
from rouge.offline_tools_view import OfflineToolsPanel,public_payload,exploration_presets


class RouteSearchViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])
    def setUp(self):
        self.p=OfflineToolsPanel();self.p.resize(1050,750);self.p.show()
        self.p.select_query('exploration','search-routes');self.qt.processEvents()
    def tearDown(self):self.p.close();self.p.deleteLater();self.qt.processEvents()
    def execute(self):
        self.p.run_button.click();end=time.monotonic()+8
        while self.p._workers and time.monotonic()<end:self.qt.processEvents();time.sleep(.005)
        self.assertFalse(self.p._workers);self.assertIsNotNone(self.p.result_snapshot(),self.p.status.text())

    def test_all_four_presets_run_and_frontier_unknowns_are_in_chinese(self):
        for preset in exploration_presets('search-routes'):
            self.p.preset.setCurrentIndex(self.p.preset.findData(preset['id']));self.p.load_example.click()
            before=self.p.editor.toPlainText();self.execute();data=self.p.result_snapshot();text=self.p.result_view.toPlainText()
            self.assertEqual(before,self.p.editor.toPlainText());self.assertIn('有限声明图的路线候选构造',text)
            self.assertIn('实际终点可达性与最优路线：未知',text);self.assertFalse(data['all_actual_routes_enumerated'])
            self.assertNotIn('depth_limit',text);self.assertNotIn('eligibility_or_inventory_condition_unknown',text)
            if preset['id']=='default':self.assertEqual(len(data['plans']),2);self.assertIn('未触发上限',text)
            elif preset['id'] in ('search-zero','search-depth'):self.assertFalse(data['plans']);self.assertTrue(data['frontier'])
            elif preset['id']=='search-random':self.assertTrue(data['frontier']);self.assertIn('随机目的地未证',text)

    def test_goal_selection_map_import_and_guarded_result_links(self):
        graph=public_payload('exploration','search-routes')['graph'];self.p.set_graph(graph,epoch=50);self.p.import_graph.click()
        self.p.graph_node.setCurrentIndex(self.p.graph_node.findData('g'));self.assertTrue(self.p.fill_node.isEnabled())
        self.p.fill_node.click();self.assertEqual(json.loads(self.p.editor.toPlainText())['goal'],'g');self.execute()
        self.assertEqual(set(self.p._result_links),{'s','a','b','g'})
        calls=[];self.p.mapNodeSelected.connect(lambda node,binding:calls.append((node,binding)))
        self.p.result_view.anchorClicked.emit(QUrl('rouge-map-node:a'));self.assertEqual(calls[0][0],'a')
        self.p.set_graph(graph,epoch=51);self.p.result_view.anchorClicked.emit(QUrl('rouge-map-node:a'))
        self.assertEqual(len(calls),1);self.assertIn('链接已过期',self.p.status.text())

    def test_refresh_and_query_switch_preserve_search_declaration_results_and_goal(self):
        self.p.graph_node.setCurrentIndex(self.p.graph_node.findData('g'));self.execute()
        before=(self.p.editor.toPlainText(),deepcopy(self.p.result_snapshot()),self.p.graph_node.currentData())
        self.p.set_graph(public_payload('exploration','search-routes')['graph'],epoch=9)
        self.p.select_query('exploration','compare-routes');self.p.select_query('exploration','search-routes')
        self.qt.processEvents();self.assertEqual(before,(self.p.editor.toPlainText(),self.p.result_snapshot(),self.p.graph_node.currentData()))

if __name__=='__main__':unittest.main()
