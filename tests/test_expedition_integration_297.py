"""Actual node entry, delayed-result rendering and unchanged legacy outputs."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import expedition_results as results,event_planning,node_catalog as catalog
from rouge.node_catalog_view import NodeCatalogPanel
from rouge.player_node_information import node_information_text

ROOT=Path(__file__).resolve().parents[1]
BASELINE=ROOT/'verification/sections/297-preparation/before-output-hashes.json'
def canon(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def reading(w):
    c=w.textCursor();return (w.toPlainText(),c.anchor(),c.position(),w.verticalScrollBar().value())
def event_entry(event_id):
    return {'kind':'event','record':next(e for e in catalog.all_events(include_indirect=True)['rows']if e['id']==event_id)}

class ExpeditionPublicIntegration297Tests(unittest.TestCase):
    def test_all_190_old_resource_queries_are_exactly_unchanged(self):
        baseline=json.loads(BASELINE.read_bytes());seen={}
        for e in catalog.all_events(include_indirect=True)['rows']:
            for scene in catalog.event_details(e['id'])['rows']:
                seen[scene['key']]=sha256(canon(event_planning.choice_resources(e['id'],scene['key']))).hexdigest()
        self.assertEqual(len(seen),190);self.assertEqual(seen,baseline['choice_resources_scenes'])

    def test_all_37_other_event_player_outputs_are_exactly_unchanged(self):
        baseline=json.loads(BASELINE.read_bytes());count=0
        for e in catalog.all_events(include_indirect=True)['rows']:
            if e['id']==results.EVENT:continue
            self.assertEqual(sha256(node_information_text({'kind':'event','record':e}).encode()).hexdigest(),
                             baseline['player_events'][e['id']],e['id']);count+=1
        self.assertEqual(count,37)

    def test_source_choice_return_note_and_rest_have_separate_readable_phases(self):
        entry=event_entry(results.EVENT);before=deepcopy(entry);text=node_information_text(entry)
        self.assertIn('选择时（资料）：获得2希望；不派出干员。',text)
        self.assertIn('归来时（资料）：2希望和怦然信标；不是派出时立即获得。',text)
        self.assertIn('【探索源头的归来说明】',text)
        note=text.split('【探索源头的归来说明】',1)[1].split('【场景 4】',1)[0]
        self.assertNotIn('获得或回复：',note);self.assertNotIn('是否为实际按钮未确认',note)
        self.assertIn('不是另一个可点击的选择',note);self.assertIn('物资的具体内容、数量，以及是否进阶：尚未确认',text)
        self.assertIn('特殊区域是否相同仍未确认',text);self.assertEqual(entry,before)

    def test_invalid_source_keeps_original_text_and_marks_phase_unknown(self):
        with patch.object(results,'MANIFEST','research/missing-expedition-297.json'):
            text=node_information_text(event_entry(results.EVENT))
        self.assertIn('时点和实际领取仍待确认',text)
        self.assertNotIn('【探索源头的归来说明】',text)
        self.assertIn('通过此方式送出的干员不会被进阶',text)

    def test_changed_cached_reading_graph_cannot_borrow_original_phase_annotations(self):
        original=catalog.event_details
        def changed(identity):
            value=original(identity)
            if identity==results.EVENT:value['rows'][0]['description']+=' different cached scene'
            return value
        with patch.object(catalog,'event_details',side_effect=changed):
            text=node_information_text(event_entry(results.EVENT))
        self.assertIn('时点和实际领取仍待确认',text)
        self.assertNotIn('【探索源头的归来说明】',text)

class ExpeditionNodeEntry297Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def setUp(self):
        self.node=NodeCatalogPanel();self.node.resize(1050,720);self.node.show();self.select(results.EVENT)
    def tearDown(self):
        if self.node.expedition_window:self.node.expedition_window.close()
        self.node.close();self.node.deleteLater();self.qt.processEvents()
    def select(self,identity):
        self.node.kind.setCurrentIndex(self.node.kind.findData('event'))
        self.node.floor.setCurrentIndex(self.node.floor.findData(None));self.node.node_type.setCurrentIndex(self.node.node_type.findData(None))
        self.node.search.setText(event_entry(identity)['record']['title']);self.node.refresh()
        index=next(i for i,e in enumerate(self.node.entries)if e['kind']=='event'and e['record']['id']==identity)
        self.node.list.setCurrentRow(index);self.qt.processEvents()

    def test_real_node_button_opens_unselected_results_and_only_manual_root_item(self):
        self.assertTrue(self.node.expedition_button.isVisible());self.assertTrue(self.node.expedition_button.isEnabled())
        self.node.expedition_button.click();self.qt.processEvents();dialog=self.node.expedition_window
        self.assertIsNone(dialog.choice.currentData());self.assertFalse(dialog.open_item_button.isEnabled())
        for row in results.event_reference(results.EVENT)['rows']:
            dialog.choice.setCurrentIndex(dialog.choice.findData(row['reference_id']));self.qt.processEvents()
            self.assertEqual(dialog.choice.currentData(),row['reference_id'])
            if row['documented_return_item']:
                self.assertTrue(dialog.open_item_button.isVisible());self.assertTrue(dialog.open_item_button.isEnabled())
                self.assertTrue(dialog.icon.pixmap().isNull());dialog.open_item_button.click();self.qt.processEvents()
                self.assertFalse(dialog.icon.pixmap().isNull());self.assertIn('所有敌人的生命+20%',dialog.item_text.toPlainText())
            else:
                self.assertFalse(dialog.open_item_button.isVisible());self.assertTrue(dialog.icon.pixmap().isNull())

    def test_same_scope_refresh_retains_manual_item_choice_tab_selection_and_scroll(self):
        self.node.expedition_button.click();dialog=self.node.expedition_window
        row=results.event_reference(results.EVENT)['rows'][1];dialog.choice.setCurrentIndex(dialog.choice.findData(row['reference_id']))
        dialog.open_item_button.click();dialog.reading_tabs.setCurrentWidget(dialog.source_text);self.qt.processEvents()
        reader=dialog.source_text;cursor=QTextCursor(reader.document());cursor.setPosition(5)
        cursor.setPosition(37,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(cursor)
        self.assertGreater(reader.verticalScrollBar().maximum(),0);reader.verticalScrollBar().setValue(max(1,reader.verticalScrollBar().maximum()//2))
        self.qt.processEvents();before=(reading(reader),dialog.choice.currentData(),dialog.item_text.toPlainText())
        self.node.refresh();self.qt.processEvents()
        self.assertEqual((reading(reader),dialog.choice.currentData(),dialog.item_text.toPlainText()),before)
        self.assertIs(dialog.reading_tabs.currentWidget(),reader);self.assertFalse(dialog.icon.pixmap().isNull())

    def test_source_failure_clears_opened_item_and_recovery_does_not_reselect(self):
        self.node.expedition_button.click();dialog=self.node.expedition_window
        row=results.event_reference(results.EVENT)['rows'][1];dialog.choice.setCurrentIndex(dialog.choice.findData(row['reference_id']))
        dialog.open_item_button.click();self.qt.processEvents();self.assertFalse(dialog.icon.pixmap().isNull())
        with patch.object(results,'MANIFEST','research/missing-expedition-297.json'):
            self.node.refresh();self.qt.processEvents()
            self.assertFalse(self.node.expedition_button.isEnabled());self.assertIsNone(dialog.choice.currentData())
            self.assertTrue(dialog.icon.pixmap().isNull());self.assertNotIn('所有敌人的生命+20%',dialog.item_text.toPlainText())
        self.node.refresh();self.qt.processEvents()
        self.assertTrue(self.node.expedition_button.isEnabled());self.assertIsNone(dialog.choice.currentData())
        self.assertTrue(dialog.icon.pixmap().isNull());self.assertFalse(dialog.open_item_button.isEnabled())
        self.select('community_group_001');self.assertFalse(self.node.expedition_button.isVisible())
        self.assertIsNone(dialog.choice.currentData());self.node.open_expedition_results()
        self.assertIsNone(dialog.choice.currentData())

if __name__=='__main__':unittest.main()
