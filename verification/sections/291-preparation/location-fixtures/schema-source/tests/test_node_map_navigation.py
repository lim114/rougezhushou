"""Read-only node navigation and conditional event UI, using public temporary state."""
from copy import deepcopy
import unittest
from PySide6.QtWidgets import QApplication
from rouge.node_catalog_view import NodeCatalogPanel
from tests import test_batch185_mainwindow as setup_module


def graph():
    return {'zone_id':'zone_1','template_id':'public-t','grid':{'rows':3,'cols':4},'edges':[],
        'source':{'url':'https://example.invalid/public-ui-fixture'},
        'nodes':[{'id':'a','row':1,'col':2,'distance':2,'observed_type':'不期而遇',
            'content':{'kind':'event','title':'思乡心切'}},
            {'id':'b','row':0,'col':1,'distance':1,'observed_type':'林间空地',
             'remembered_type':'不期而遇','remembered_content':{'kind':'event','title':'呼吸的红苔'}}]}


class NodeMapNavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])
    def setUp(self):self.panel=NodeCatalogPanel();self.addCleanup(self.panel.close)
    def select_title(self,title):
        self.panel.list.setCurrentRow(next(i for i,e in enumerate(self.panel.entries) if e['title']==title))

    def test_exact_event_choice_previews_and_emergency_variants(self):
        self.select_title('思乡心切');values=[];self.panel.stageSelected.connect(values.append)
        self.assertEqual(self.panel.event_stage.currentData(),'ro6_t_1')
        self.assertIn('强行驱赶',self.panel.event_stage.currentText());self.panel.select_stage()
        self.assertEqual(values,['ro6_t_1'])
        self.select_title('鸭托邦')
        # The source option title may differ: check any explicitly qualified emergency row separately.
        self.assertIn('ro6_e_t_3',[self.panel.event_stage.itemData(i) for i in range(self.panel.event_stage.count())])
        self.assertIn('当前服务器资格仍未知',self.panel.detail.toPlainText())

    def test_collapse_and_selection_survive_refresh_without_reopening(self):
        self.select_title('思乡心切');key=self.panel.detail_key
        self.panel.collapse_button.click();self.panel.refresh()
        self.assertEqual(key,self.panel.detail_key);self.assertFalse(self.panel.list.expanded_groups())
        self.panel.expand_button.click();self.assertTrue(self.panel.list.expanded_groups())

    def test_visible_tree_refresh_preserves_collapsed_selected_group(self):
        self.panel.resize(1000,700);self.panel.show();self.qt.processEvents()
        self.select_title('思乡心切');self.qt.processEvents();key=self.panel.detail_key
        self.panel.collapse_button.click();self.assertFalse(self.panel.list.expanded_groups())
        self.panel.refresh();self.qt.processEvents()
        self.assertFalse(self.panel.list.expanded_groups())
        self.assertEqual(self.panel.detail_key,key)
        self.assertEqual(self.panel.event_stage.currentData(),'ro6_t_1')

    def test_map_context_copy_tree_history_and_round_trip_directory(self):
        source=graph();before=deepcopy(source)
        self.panel.set_map_context(source,{'floor':1},epoch=123,historical=True)
        self.panel.map_button.click();self.assertEqual(set(self.panel.list.groups),{'不期而遇','林间空地'})
        self.panel.list.setCurrentRow(1);self.assertIn('过去类型',self.panel.detail.toPlainText())
        self.assertIn('呼吸的红苔',self.panel.detail.toPlainText());self.assertEqual(source,before)
        self.panel.all_button.click();self.assertIsNone(self.panel.kind.currentData())
        self.assertTrue(any(e['title']=='思乡心切' for e in self.panel.entries))

    def test_map_node_contents_narrow_to_observed_event_and_emit_copy_binding(self):
        self.panel.set_map_context(graph(),{'floor':1},epoch=123)
        self.panel.map_button.click();self.panel.list.setCurrentRow(0)
        calls=[];self.panel.mapNodeSelected.connect(lambda key,binding:calls.append((key,binding)))
        self.panel.map_jump.click();self.assertEqual(calls[0][0],'a');self.assertEqual(calls[0][1]['epoch'],123)
        self.panel.map_contents.click()
        self.assertEqual([e['title'] for e in self.panel.entries if e['kind']=='event'],['思乡心切'])
        self.select_title('思乡心切');self.assertTrue(self.panel.battle_button.isEnabled())
        self.assertTrue(self.panel.map_jump.isEnabled())

    def test_special_conditions_stay_visible_as_unknown_or_excluded(self):
        self.panel.node_type.setCurrentIndex(self.panel.node_type.findData('不期而遇'))
        self.select_title('呼吸的红苔')
        self.assertEqual(next(e['qualification']['status'] for e in self.panel.entries if e['title']=='呼吸的红苔'),'unknown')
        self.assertIn('沉寂之屋',self.panel.detail.toPlainText())
        self.panel.show_directory();self.panel.node_type.setCurrentIndex(0)
        self.select_title('安眠一隅')
        self.assertIn('已列条件不符',self.panel.detail.toPlainText())

    def test_unrevealed_type_cannot_falsely_exclude_all_event_candidates(self):
        source=graph();source['nodes'][0].pop('content')
        source['nodes'][0].update(observed_type='未知的命运',prediction={'candidates':['不期而遇']})
        self.panel.set_map_context(source,{'floor':1},epoch=123)
        self.panel.set_node(source,'a',floor=1);self.panel.bind_current_node()
        row=next(e for e in self.panel.entries if e['title']=='思乡心切')
        self.assertNotEqual(row['qualification']['status'],'excluded')
        self.panel.map_button.click();self.panel.list.setCurrentRow(0)
        self.assertNotIn('思乡心切：已列条件不符',self.panel.detail.toPlainText())

    def test_choice_variant_and_map_match_selection_are_preserved(self):
        self.select_title('鸭托邦')
        self.panel.event_stage.setCurrentIndex(self.panel.event_stage.count()-1)
        token=self.panel.event_stage.itemData(self.panel.event_stage.currentIndex(),257)
        self.panel.refresh();self.assertEqual(self.panel.event_stage.itemData(self.panel.event_stage.currentIndex(),257),token)
        source=graph();source['nodes'][1]['remembered_content']={'kind':'event','title':'思乡心切'}
        self.panel.set_map_context(source,{'floor':1},epoch=123)
        self.select_title('思乡心切');self.panel.map_location.setCurrentIndex(1)
        self.panel.refresh();self.assertEqual(self.panel.map_location.currentData()['node_id'],'b')

    def test_null_history_keeps_directory_and_map_detail_available(self):
        source=graph();source['nodes'][0]['content_history']=None
        self.panel.set_map_context(source,{'floor':1},epoch=123)
        self.select_title('思乡心切');self.assertTrue(self.panel.map_jump.isEnabled())
        self.panel.map_button.click();self.panel.list.setCurrentRow(0)
        self.assertIn('思乡心切',self.panel.detail.toPlainText())

    def test_past_function_type_maps_to_passed_clearing_without_current_claim(self):
        source=graph();source['nodes'][1]['remembered_type']='羽瞰点'
        source['nodes'][1].pop('remembered_content')
        self.panel.set_map_context(source,{'floor':1},epoch=123)
        self.select_title('羽瞰点');self.assertEqual(self.panel.map_location.currentData()['node_id'],'b')
        self.assertIn('过去已读取类型',self.panel.map_location.currentText())
        self.assertEqual(source['nodes'][1]['observed_type'],'林间空地')

    def test_next_main_floor_source_pool_provides_all_fixed_preview_entrances(self):
        from rouge import event_planning
        self.panel.floor.setCurrentIndex(self.panel.floor.findData(3));self.select_title('洞中宝')
        event=next(e for e in self.panel.entries if e['title']=='洞中宝')
        result=event_planning.event_battle_links(event['record']['id'],context=self.panel._event_context(event['record']))
        pool=next(r['generic_pool_requirement']['fixed_named_pool'] for r in result['rows'] if r['generic_pool_requirement'])
        self.assertEqual(len(pool),7)
        self.assertEqual({self.panel.event_stage.itemData(i) for i in range(self.panel.event_stage.count())},{r['id'] for r in pool})
        self.assertTrue(self.panel.battle_button.isEnabled());self.assertIn('完整服务器池与实际选择未知',self.panel.detail.toPlainText())
        calls=[];self.panel.stageSelected.connect(calls.append);selected=self.panel.event_stage.currentData()
        self.panel.battle_button.click();self.assertEqual(calls,[selected])

    def test_unknown_or_special_next_main_floor_never_fabricates_preview_pool(self):
        self.select_title('洞中宝');self.assertEqual(self.panel.event_stage.count(),0)
        source=graph();source['nodes'][0]['content']={'kind':'event','title':'洞中宝'}
        self.panel.set_map_context(source,{'floor':2,'special_region':True},epoch='public-run')
        self.panel.set_node(source,'a',floor=2,special_region=True);self.panel.bind_current_node();self.select_title('洞中宝')
        self.assertEqual(self.panel.event_stage.count(),0);self.assertFalse(self.panel.battle_button.isEnabled())


class NodeMainWindowNavigationTests(unittest.TestCase):
    setUpClass=classmethod(setup_module.Batch185WindowTests.setUpClass.__func__)
    setUp=setup_module.Batch185WindowTests.setUp

    def install_map(self):
        source=graph();source['captured_at']=self.window.run.state['started_at']+1
        self.window.run.state['maps']['zone_1']=source
        self.window.run.state['config']['zone']={'id':'zone_1'}
        self.window.run.state['resources']['gold']={'value':51,'captured_at':source['captured_at']}
        self.window.render_map();return source

    def test_actual_window_event_to_battle_and_node_to_map(self):
        self.install_map();panel=self.window.node_catalog;panel.map_button.click()
        self.window.centralWidget().setCurrentWidget(panel);panel.list.setCurrentRow(0);panel.map_jump.click()
        self.assertIs(self.window.centralWidget().currentWidget(),self.window.exploration_map_tab)
        self.assertEqual(self.window.map_view.selected,'a')
        self.window.centralWidget().setCurrentWidget(panel);panel.map_contents.click()
        panel.list.setCurrentRow(next(i for i,e in enumerate(panel.entries) if e['title']=='思乡心切'))
        panel.battle_button.click();self.assertEqual(self.window.target_stage.currentData(),'ro6_t_1')
        self.assertIs(self.window.centralWidget().currentWidget(),self.window.battle_preview)
        self.assertEqual(panel.runtime_context['gold'],51)

    def test_stale_epoch_template_and_position_never_jump(self):
        self.install_map();panel=self.window.node_catalog;panel.map_button.click();panel.list.setCurrentRow(0)
        binding=deepcopy(panel.map_location.currentData());self.window.centralWidget().setCurrentWidget(panel)
        for field,value in (('epoch','other-run'),('template_id','other'),('row',2),('col',True)):
            bad={**binding,field:value};self.window.show_catalog_map_node('a',bad)
            self.assertIs(self.window.centralWidget().currentWidget(),panel);self.assertIsNone(self.window.map_view.selected)
        self.assertIn('链接已过期',panel.status.text())

    def test_changed_run_id_rejects_old_link_even_if_clock_is_unchanged(self):
        self.install_map();panel=self.window.node_catalog;panel.map_button.click();panel.list.setCurrentRow(0)
        binding=deepcopy(panel.map_location.currentData());self.window.centralWidget().setCurrentWidget(panel)
        before=self.window.run.state['started_at'];self.window.run.state['id']='different-local-run'
        self.assertEqual(self.window.run.state['started_at'],before)
        self.window.show_catalog_map_node('a',binding)
        self.assertIs(self.window.centralWidget().currentWidget(),panel);self.assertIsNone(self.window.map_view.selected)

    def test_periodic_refresh_keeps_collapsed_tree_and_selected_event(self):
        source=self.install_map();panel=self.window.node_catalog
        panel.list.setCurrentRow(next(i for i,e in enumerate(panel.entries) if e['title']=='思乡心切'))
        panel.collapse_button.click();key=panel.detail_key
        self.window.run.state['maps']['zone_1']['captured_at']=source['captured_at']+1
        self.window.render_map();self.assertEqual(panel.detail_key,key)
        self.assertFalse(panel.list.expanded_groups())
