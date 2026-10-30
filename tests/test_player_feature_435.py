import unittest
from copy import deepcopy
from PySide6.QtWidgets import QApplication
from rouge.player_map_acceptance import fixtures
from rouge.player_map_reference import node_dossier

class NodeDirectoryReading(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def setUp(self):
  from tests.test_batch185_mainwindow import Batch185WindowTests
  Batch185WindowTests.setUp(self)
  self.graphs,self.node,self.other,_=fixtures();self.window.run.state['maps']={g['zone_id']:g for g in self.graphs}
  self.window.show_compact();self.window.compact_window.open_map();self.qt.processEvents();self.p=self.window.compact_window.map_popup.panel
  self.p.view.select_node(self.node);self.p.select_interactive(self.node)
 def test_search_only_filters_selected_node_and_does_not_mutate_run(self):
  before=deepcopy(self.window.run.state);self.p.entry_search.setText('桑尼');self.qt.processEvents()
  self.assertEqual(len(self.p.rows),1);self.assertTrue(all('桑尼'in r['title']for r in self.p.rows.values()));self.assertEqual(self.window.run.state,before)
 def test_collapsed_group_selection_and_query_survive_refresh(self):
  p=self.p;p.entry_search.setText('桑尼');root=p.entries.topLevelItem(0);p.entries.setCurrentItem(root.child(0));key=p.selected_reference;text=p.detail.toPlainText();root.setExpanded(False);p.refresh();self.qt.processEvents()
  self.assertEqual(p.entry_search.text(),'桑尼');self.assertFalse(p.entries.topLevelItem(0).isExpanded());self.assertEqual(p.selected_reference,key);self.assertEqual(p.detail.toPlainText(),text)
 def test_each_node_has_its_own_reading_state(self):
  p=self.p;p.entry_search.setText('桑尼');p.view.select_node(self.other);self.qt.processEvents();self.assertEqual(p.entry_search.text(),'')
  p.entry_search.setText('另一份筛选');p.view.select_node(self.node);self.qt.processEvents();self.assertEqual(p.entry_search.text(),'桑尼')
  p.view.select_node(self.other);self.qt.processEvents();self.assertEqual(p.entry_search.text(),'另一份筛选')
 def test_exact_hover_navigation_reveals_hidden_target_but_bad_link_keeps_query(self):
  p=self.p;target=node_dossier(self.graphs[0],self.node,{})['rows'][0]['id'];p.entry_search.setText('没有匹配项')
  self.assertTrue(p.open_hover_entry(self.node,'event',target));self.assertEqual(p.entry_search.text(),'');self.assertEqual(p.selected_reference[1:],('event',target))
  p.entry_search.setText('桑尼');self.assertFalse(p.open_hover_entry(self.node,'event','invalid-source-id'));self.assertEqual(p.entry_search.text(),'桑尼')
 def test_new_run_clears_only_fixture_ui_reading_memory(self):
  self.p.entry_search.setText('桑尼');self.window.run.state['id']='isolated-new-run';self.window.run.state['maps']={};self.p.refresh();self.qt.processEvents()
  self.assertEqual(self.p.entry_search.text(),'');self.assertEqual(self.p.entry_readings,{})

if __name__=='__main__':unittest.main()
