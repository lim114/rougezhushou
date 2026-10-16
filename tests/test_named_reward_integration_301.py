"""Exact public node-to-reward reading; no game, calculation toggle or run state."""
from copy import deepcopy
import unittest
from unittest.mock import patch
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import node_catalog as catalog, named_reward_items as model
from rouge.node_catalog_view import NodeCatalogPanel

EVENTS=tuple('community_group_'+s for s in ('005','006','007','008','010','011','019','020','022','025'))
def event(identity):
    return next(e for e in catalog.all_events(include_indirect=True)['rows'] if e['id']==identity)
def reading(widget):
    c=widget.textCursor()
    return widget.toPlainText(),c.anchor(),c.position(),widget.verticalScrollBar().value()

class NamedRewardIntegration301Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])
    def setUp(self):
        self.node=NodeCatalogPanel();self.node.resize(1050,720);self.node.show();self.select(EVENTS[0])
    def tearDown(self):
        for name in ('named_reward_window','documented_item_window','expedition_window','future_region_window'):
            window=getattr(self.node,name,None)
            if window:window.close()
        self.node.close();self.node.deleteLater();self.qt.processEvents()
    def select(self,identity):
        self.node.kind.setCurrentIndex(self.node.kind.findData('event'))
        self.node.floor.setCurrentIndex(self.node.floor.findData(None));self.node.node_type.setCurrentIndex(self.node.node_type.findData(None))
        self.node.search.setText(event(identity)['title']);self.node.refresh()
        index=next(i for i,e in enumerate(self.node.entries) if e['kind']=='event' and e['record']['id']==identity)
        self.node.list.setCurrentRow(index);self.qt.processEvents()
    def open(self):
        self.node.named_reward_button.click();self.qt.processEvents()
        return self.node.named_reward_window
    def choose(self,dialog,row):
        index=dialog.choice.findData(row['reference_id']);self.assertGreaterEqual(index,0)
        dialog.choice.setCurrentIndex(index);self.qt.processEvents()
        self.assertEqual(dialog.choice.currentData(),row['reference_id'])
    def test_all_ten_public_entries_and_sixteen_exact_choices_show_thirteen_item_images(self):
        count=0;items=set()
        for identity in EVENTS:
            with self.subTest(event=identity):
                self.select(identity);self.assertTrue(self.node.named_reward_button.isVisible())
                self.assertTrue(self.node.named_reward_button.isEnabled());dialog=self.open()
                self.assertIsNone(dialog.choice.currentData())
                packet=model.event_reference(identity);self.assertEqual(dialog.choice.count(),len(packet['choices']))
                for row in packet['choices']:
                    self.choose(dialog,row)
                    details=model.item_details(identity,row['scene_key'],row['choice_key'])
                    self.assertTrue(details['source_valid']);self.assertIn(details['item']['name'],dialog.player_text.toPlainText())
                    picture=dialog.icon.pixmap();self.assertTrue(picture and not picture.isNull())
                    self.assertIn('未',dialog.player_text.toPlainText());count+=1;items.add(row['item_id'])
        self.assertEqual(count,16);self.assertEqual(len(items),13)
    def test_different_conditions_for_same_item_remain_separate_manual_references(self):
        for identity,expected in (('community_group_007',2),('community_group_011',3)):
            self.select(identity);dialog=self.open();rows=model.event_reference(identity)['choices']
            self.assertEqual(len(rows),expected);self.assertEqual(len({r['item_id'] for r in rows}),1)
            self.assertEqual(len({dialog.choice.itemText(i) for i in range(dialog.choice.count())}),expected)
            selected=[]
            for row in rows:
                self.choose(dialog,row);selected.append(dialog.choice.currentData())
            self.assertEqual(len(set(selected)),expected)
    def test_source_failure_clears_image_and_text_then_recovers_without_selecting(self):
        dialog=self.open();self.choose(dialog,model.event_reference(EVENTS[0])['choices'][0])
        old=dialog.player_text.toPlainText()
        with patch.object(model,'MANIFEST','research/missing-named-reward-301.json'):
            self.node.refresh();self.qt.processEvents()
            self.assertFalse(self.node.named_reward_button.isEnabled());self.assertIsNone(dialog.choice.currentData())
            picture=dialog.icon.pixmap();self.assertTrue(not picture or picture.isNull())
            self.assertNotEqual(old,dialog.player_text.toPlainText())
        self.node.refresh();self.qt.processEvents()
        self.assertTrue(self.node.named_reward_button.isEnabled());self.assertIsNone(dialog.choice.currentData())
    def test_stale_entry_rechecks_sources_before_constructing_reader(self):
        self.assertIsNone(self.node.named_reward_window)
        with patch.object(model,'MANIFEST','research/missing-named-reward-301.json'):
            self.node.open_named_reward_items()
        self.assertIsNone(self.node.named_reward_window);self.assertFalse(self.node.named_reward_button.isEnabled())
    def test_non_target_event_hides_entry_and_clears_previous_item_without_defaulting(self):
        dialog=self.open();self.choose(dialog,model.event_reference(EVENTS[0])['choices'][0])
        self.select('community_group_001');self.assertFalse(self.node.named_reward_button.isVisible())
        self.assertIsNone(dialog.choice.currentData());picture=dialog.icon.pixmap();self.assertTrue(not picture or picture.isNull())
        self.node.open_named_reward_items();self.assertIs(self.node.named_reward_window,dialog)
        self.select(EVENTS[0]);self.assertIsNone(dialog.choice.currentData())
    def test_same_scope_refresh_keeps_parent_and_item_source_reading_position(self):
        dialog=self.open();self.choose(dialog,model.event_reference(EVENTS[0])['choices'][0])
        self.node.reading_tabs.setCurrentWidget(self.node.detail);dialog.reading_tabs.setCurrentWidget(dialog.source_text)
        self.qt.processEvents();states=[]
        for w in (self.node.detail,dialog.source_text):
            c=QTextCursor(w.document());c.setPosition(5);c.setPosition(25,QTextCursor.MoveMode.KeepAnchor);w.setTextCursor(c)
            self.assertGreater(w.verticalScrollBar().maximum(),0);w.verticalScrollBar().setValue(max(1,w.verticalScrollBar().maximum()//2))
            states.append(reading(w))
        selected=dialog.choice.currentData();self.node.refresh();self.qt.processEvents()
        self.assertEqual(states,[reading(self.node.detail),reading(dialog.source_text)])
        self.assertEqual(selected,dialog.choice.currentData());self.assertIs(dialog.reading_tabs.currentWidget(),dialog.source_text)
        self.assertFalse(dialog.icon.pixmap().isNull())
    def test_existing_special_item_and_next_region_entries_remain_distinct(self):
        for identity,button,window in (('community_group_021','documented_item_button','documented_item_window'),
          ('community_group_024','expedition_button','expedition_window'),
          ('community_group_009','future_region_button','future_region_window')):
            self.select(identity);self.assertFalse(self.node.named_reward_button.isVisible())
            original=getattr(self.node,button);self.assertTrue(original.isVisible());self.assertTrue(original.isEnabled())
            original.click();self.qt.processEvents();self.assertIsNotNone(getattr(self.node,window))

if __name__=='__main__':unittest.main()
