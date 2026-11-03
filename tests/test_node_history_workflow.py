"""Historical reads retain preview entrances without becoming current facts."""
from copy import deepcopy
import unittest
from PySide6.QtWidgets import QApplication
from rouge import node_catalog as catalog
from rouge.node_catalog_view import NodeCatalogPanel
from tests.test_node_map_navigation import graph
from tests import test_batch185_mainwindow as setup_module


def past_graph():
    value=graph();node=value['nodes'][1]
    node['remembered_content']={'kind':'event','title':'思乡心切'}
    node['content_history']=[{'kind':'event','title':'鸭托邦'},{'kind':'event','title':'思乡心切'}]
    return value


class NodeHistoryWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])
    def setUp(self):self.panel=NodeCatalogPanel();self.addCleanup(self.panel.close)
    def bind(self,source):
        self.panel.set_map_context(source,{'floor':1},epoch='public-run',runtime_context={
            'gold':99,'item_presence':{'rogue_6_relic_final_1':True},'inventory_complete':True})
        self.panel.set_node(source,'b',floor=1);self.panel.bind_current_node()
    def pick(self,title):
        index=next(i for i,e in enumerate(self.panel.entries) if e['title']==title and e.get('history_read'))
        self.panel.list.setCurrentRow(index)

    def test_bound_scope_controls_are_locked_then_directory_restores_them(self):
        source=past_graph();self.bind(source)
        self.assertFalse(self.panel.node_type.isEnabled());self.assertFalse(self.panel.floor.isEnabled())
        self.assertIn('目录类型/层数筛选已停用',self.panel.context_label.text())
        self.panel.show_directory();self.assertTrue(self.panel.node_type.isEnabled());self.assertTrue(self.panel.floor.isEnabled())
        self.panel.map_button.click();self.assertTrue(self.panel.node_type.isEnabled());self.assertFalse(self.panel.floor.isEnabled())

    def test_dossier_separates_recorded_history_from_whole_old_type_candidates(self):
        source=past_graph();before=deepcopy(source);value=catalog.node_dossier(source,'b',floor=1)
        self.assertEqual({e['title'] for e in value['history_observed_event_rows']},{'思乡心切','鸭托邦'})
        self.assertGreater(len(value['history_events']),len(value['history_observed_event_rows']))
        row=next(e for e in value['history_observed_event_rows'] if e['title']=='思乡心切')
        self.assertEqual(row['reading_sources'],['remembered_content','content_history:1'])
        self.assertFalse(row['floor_filter_applied']);self.assertEqual(source,before)

    def test_recorded_event_branch_opens_battle_and_keeps_its_map_binding(self):
        self.bind(past_graph());self.pick('思乡心切')
        self.assertIn('历史已读取内容',self.panel.detail.toPlainText())
        self.assertTrue(self.panel.battle_button.isEnabled());self.assertEqual(self.panel.event_stage.currentData(),'ro6_t_1')
        binding=self.panel.map_location.currentData();self.assertEqual(binding['node_id'],'b')
        self.assertEqual(binding['epoch'],'public-run');self.assertTrue(self.panel.map_jump.isEnabled())
        self.assertEqual({e['title'] for e in self.panel.entries if e.get('history_read') and e['kind']=='event'},
                         {'思乡心切','鸭托邦'})
        calls=[];self.panel.stageSelected.connect(calls.append);self.panel.battle_button.click()
        self.assertEqual(calls,['ro6_t_1'])

    def test_current_inventory_and_gold_do_not_claim_historical_option_qualification(self):
        self.bind(past_graph());self.pick('思乡心切')
        row=next(e for e in self.panel.entries if e['title']=='思乡心切' and e.get('history_read'))
        context=self.panel._event_context(row['record'])
        self.assertNotIn('gold',context);self.assertNotIn('item_presence',context);self.assertNotIn('inventory_complete',context)
        self.assertEqual(context['node_type'],'不期而遇');self.assertEqual(context['entry_mode'],'content')
        self.assertNotEqual(row['qualification']['status'],'excluded')
        self.assertIsNone(row['qualification']['actual_server_eligible'])

    def test_historical_variant_is_exact_and_title_only_keeps_all_aliases(self):
        source=past_graph();node=source['nodes'][1]
        node['remembered_content']={'kind':'battle','title':'陌生旅伴','variant_id':'ro6_t_1'}
        node['content_history']=[];value=catalog.node_dossier(source,'b',floor=6)
        self.assertEqual([r['id'] for r in value['history_observed_battle_rows']],['ro6_t_1'])
        self.assertTrue(value['history_observed_battle_rows'][0]['observed_variant_reference'])
        node['remembered_content']={'kind':'battle','title':'遗忘时间'}
        value=catalog.node_dossier(source,'b',floor=6)
        expected={r['id'] for r in catalog.battle_candidates(context='all')['rows'] if r['title']=='遗忘时间'}
        self.assertEqual(expected,{'ro6_n_1_2','ro6_e_1_2'})
        self.assertEqual({r['id'] for r in value['history_observed_battle_rows']},expected)
        self.assertTrue(all(not r['observed_variant_reference'] for r in value['history_observed_battle_rows']))

    def test_history_and_current_content_keep_distinct_keys_and_refresh_selection(self):
        source=past_graph();node=source['nodes'][1]
        node.update(observed_type='不期而遇',content={'kind':'event','title':'思乡心切'})
        self.bind(source);entries=[e for e in self.panel.entries if e['title']=='思乡心切']
        self.assertEqual(len(entries),2);self.assertNotEqual(entries[0]['key'],entries[1]['key'])
        self.pick('思乡心切');key=self.panel.detail_key;self.panel.collapse_button.click()
        self.panel.refresh();self.assertEqual(key,self.panel.detail_key);self.assertFalse(self.panel.list.expanded_groups())

    def test_unknown_type_vocabulary_retains_prediction_and_past_function_has_own_branch(self):
        source=past_graph();node=source['nodes'][1]
        node.update(observed_type='类型未确认',prediction={'candidates':['不期而遇']},remembered_type='羽瞰点')
        value=catalog.node_dossier(source,'b',floor=1)
        self.assertTrue(value['generic_event_candidates'])
        self.assertEqual([f['node_type'] for f in value['history_observed_function_rows']],['羽瞰点'])
        self.bind(source);self.assertTrue(any(e['kind']=='function' and e.get('history_read') and e['title']=='羽瞰点' for e in self.panel.entries))


class NodeHistoryMainWindowTests(unittest.TestCase):
    setUpClass=classmethod(setup_module.Batch185WindowTests.setUpClass.__func__)
    setUp=setup_module.Batch185WindowTests.setUp

    def test_past_node_to_event_battle_and_back_to_same_map_in_actual_window(self):
        source=past_graph();source['captured_at']=self.window.run.state['started_at']+1
        self.window.run.state['maps']['zone_1']=source;self.window.run.state['config']['zone']={'id':'zone_1'}
        identity='rogue_6_relic_final_1';self.window.run.state['last_read']=source['captured_at']
        self.window.run.state['relics'][identity]={'held':True,'source':'held_name_usage','captured_at':source['captured_at']}
        self.window.render_map();panel=self.window.node_catalog
        self.assertTrue(panel.runtime_context['item_presence'][identity]);self.assertNotIn('item_quantities',panel.runtime_context)
        self.window.map_view.select_node('b');panel.bind_button.click()
        panel.list.setCurrentRow(next(i for i,e in enumerate(panel.entries) if e['title']=='思乡心切' and e.get('history_read')))
        key=panel.detail_key;panel.battle_button.click()
        self.assertEqual(self.window.target_stage.currentData(),'ro6_t_1')
        self.assertIs(self.window.centralWidget().currentWidget(),self.window.battle_preview)
        self.window.centralWidget().setCurrentWidget(panel);panel.map_jump.click()
        self.assertIs(self.window.centralWidget().currentWidget(),self.window.exploration_map_tab)
        self.assertEqual(self.window.map_view.selected,'b');self.assertEqual(panel.detail_key,key)
        self.assertEqual(self.window.run.state['maps']['zone_1'],source)


if __name__=='__main__':unittest.main()
