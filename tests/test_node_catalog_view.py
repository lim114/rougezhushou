import unittest
from copy import deepcopy
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge.node_catalog_view import NodeCatalogPanel,event_text,map_conditions
from rouge import node_catalog


class NodeCatalogViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance() or QApplication([])

    def setUp(self):self.panel=NodeCatalogPanel();self.panel.resize(1000,700);self.panel.show();self.app.processEvents()
    def tearDown(self):self.panel.close();self.panel.deleteLater();self.app.processEvents()

    def test_public_directory_keeps_same_title_groups_special_events_and_unclassified(self):
        self.assertEqual(sum(e['title']=='三重身' for e in self.panel.entries),3)
        self.assertIn('安眠一隅',[e['title'] for e in self.panel.entries])
        self.assertEqual(sum(e['kind']=='original' for e in self.panel.entries),108)
        self.assertTrue(any(e['title']=='羽瞰点' and e['kind']=='function' for e in self.panel.entries))

    def test_zone_variant_uses_original_icon_metadata_without_suffix_floor_guess(self):
        self.assertEqual(map_conditions({'zone_id':'zone_4_1'},{})['floor'],4)
        unknown=map_conditions({'zone_id':'zone_portal_unknown'},{'difficulty':{'value':True}})
        self.assertIsNone(unknown['floor']);self.assertTrue(unknown['special_region']);self.assertIsNone(unknown['difficulty'])
        self.assertEqual(map_conditions({'zone_id':'zone_1'},{'difficulty':{'value':4}})['difficulty'],4)

    def test_event_flow_text_includes_every_scene_and_choice_without_game_eligibility_claim(self):
        for e in node_catalog.all_events(include_indirect=True)['rows']:
            with self.subTest(event=e['id']):
                text=event_text(e['id'])
                for scene in node_catalog.event_details(e['id'])['rows']:
                    self.assertIn(scene['description'],text)
                    for choice in scene['choices']:self.assertIn(choice['title'],text)
                self.assertIn('按钮是否可选：未知',text)
        source=event_text(next(e['id'] for e in node_catalog.all_events(include_indirect=True)['rows'] if e['title']=='安眠一隅'))
        self.assertIn('子选择参考',source)

    def test_manual_selection_and_reading_survive_unchanged_refresh(self):
        index=next(i for i,e in enumerate(self.panel.entries) if e['title']=='安眠一隅')
        self.panel.list.setCurrentRow(index);self.app.processEvents()
        key=self.panel.detail_key;cursor=self.panel.detail.textCursor();cursor.setPosition(3);cursor.setPosition(12,QTextCursor.MoveMode.KeepAnchor)
        self.panel.detail.setTextCursor(cursor);before=self.panel.detail.textCursor().selectedText()
        self.panel.refresh();self.app.processEvents()
        self.assertEqual(self.panel.detail_key,key);self.assertEqual(self.panel.detail.textCursor().selectedText(),before)

    def test_map_selection_copy_binding_and_clearing_history(self):
        graph={'zone_id':'zone_1','template_id':'t','nodes':[{'id':'a','row':1,'col':2,'observed_type':'林间空地','remembered_type':'不期而遇','remembered_content':{'title':'桑尼的邀请'}}]}
        before=deepcopy(graph);self.panel.set_node(graph,'a',floor=1)
        self.assertIsNone(self.panel.dossier);self.panel.bind_current_node()
        self.assertIn('第2行、第3列',self.panel.context_label.text())
        self.assertEqual(graph,before);self.assertFalse(any(e['kind']=='event' for e in self.panel.entries))
        self.assertIn('过去读取',self.panel.detail.toPlainText())
        key=self.panel.detail_key;self.panel.set_node(graph,'a',floor=1)
        self.assertEqual(key,self.panel.detail_key)

    def test_fixed_battle_entry_selects_exact_variant_id(self):
        self.panel.kind.setCurrentIndex(self.panel.kind.findData('battle'));events=[]
        self.panel.stageSelected.connect(events.append)
        self.panel.list.setCurrentRow(1);expected=self.panel.entries[1]['record']['id']
        self.panel.select_stage();self.assertEqual(events,[expected])
        self.panel.kind.setCurrentIndex(self.panel.kind.findData('event'));self.panel.select_stage()
        self.assertEqual(events,[expected])

    def test_search_and_branch_filters_do_not_reset_when_sampling_context_changes(self):
        self.panel.search.setText('绒毛');before=[e['key'] for e in self.panel.entries]
        self.assertTrue(any(e['title']=='桑尼的邀请' for e in self.panel.entries))
        self.panel.set_node({'nodes':[{'id':'a','observed_type':'作战'}]},'a',floor=1)
        self.assertEqual(before,[e['key'] for e in self.panel.entries]);self.assertEqual(self.panel.search.text(),'绒毛')
