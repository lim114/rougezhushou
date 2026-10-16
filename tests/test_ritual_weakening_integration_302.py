"""Read exact ritual references through the public node page, without a run."""
import unittest
from unittest.mock import patch
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import node_catalog as catalog, ritual_weakening as model
from rouge.node_catalog_view import NodeCatalogPanel

EVENT='community_group_032'
EXPECTED=((2,0,1),(2,1,1),(3,0,3),(3,1,3),(4,0,2),(4,1,2))
def reading(widget):
    cursor=widget.textCursor()
    return widget.toPlainText(),cursor.anchor(),cursor.position(),widget.verticalScrollBar().value()

class RitualWeakeningIntegration302Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])
    def setUp(self):
        self.node=NodeCatalogPanel();self.node.resize(1050,720);self.node.show();self.select(EVENT)
    def tearDown(self):
        for name in ('ritual_weakening_window','named_reward_window','documented_item_window','expedition_window','future_region_window'):
            window=getattr(self.node,name,None)
            if window:
                child=getattr(window,'battle_window',None)
                if child:child.close()
                window.close()
        self.node.close();self.node.deleteLater();self.qt.processEvents()
    def select(self,identity):
        event=next(e for e in catalog.all_events(include_indirect=True)['rows'] if e['id']==identity)
        self.node.kind.setCurrentIndex(self.node.kind.findData('event'))
        self.node.floor.setCurrentIndex(self.node.floor.findData(None))
        self.node.node_type.setCurrentIndex(self.node.node_type.findData(None))
        self.node.search.setText(event['title']);self.node.refresh()
        index=next(i for i,e in enumerate(self.node.entries) if e['kind']=='event' and e['record']['id']==identity)
        self.node.list.setCurrentRow(index);self.qt.processEvents()
    def open(self):
        self.assertTrue(self.node.ritual_weakening_button.isVisible())
        self.assertTrue(self.node.ritual_weakening_button.isEnabled())
        self.node.ritual_weakening_button.click();self.qt.processEvents()
        self.assertIsNotNone(self.node.ritual_weakening_window)
        return self.node.ritual_weakening_window
    def choose(self,dialog,scene,choice):
        identity=f'{EVENT}:scene:{scene}:choice:{choice}'
        index=dialog.choice.findData(identity);self.assertGreaterEqual(index,0)
        dialog.choice.setCurrentIndex(index);self.qt.processEvents()
        self.assertEqual(dialog.choice.currentData(),identity)
        return next(r for r in dialog.packet['choices'] if r['choice_key']==identity)
    def test_public_entry_keeps_six_exact_options_and_three_effects_without_auto_battle(self):
        dialog=self.open();self.assertIsNone(dialog.choice.currentData());self.assertEqual(dialog.choice.count(),6)
        for scene,choice,effect in EXPECTED:
            row=self.choose(dialog,scene,choice)
            self.assertEqual(row['weakening_id'],f'rogue_6_chimera_weaken_{effect}')
            self.assertTrue(dialog.player_text.toPlainText())
            self.assertTrue(dialog.open_stage_button.isEnabled())
            self.assertIsNone(dialog.battle_window)
            self.assertIsNone(row['actual_effect']);self.assertFalse(row['calculation_applied'])
        self.assertEqual(len({dialog.choice.itemText(i) for i in range(6)}),6)
    def test_related_battle_requires_click_and_retains_parent_selection(self):
        dialog=self.open();self.choose(dialog,3,1)
        key=self.node.list.selected_key();parent=reading(self.node.player_detail)
        self.assertIsNone(dialog.battle_preview)
        dialog.open_stage_button.click();self.qt.processEvents()
        self.assertIsNotNone(dialog.battle_preview)
        self.assertEqual(dialog.battle_preview.current_stage,'ro6_b_6')
        self.assertEqual(self.node.list.selected_key(),key)
        self.assertEqual(reading(self.node.player_detail),parent)
        self.assertEqual(dialog.choice.currentData(),f'{EVENT}:scene:3:choice:1')
    def test_non_target_clears_old_selection_and_related_preview_then_returns_unselected(self):
        dialog=self.open();self.choose(dialog,2,0);dialog.open_stage_button.click();self.qt.processEvents()
        self.select('community_group_001')
        self.assertFalse(self.node.ritual_weakening_button.isVisible())
        self.assertIsNone(dialog.choice.currentData());self.assertIsNone(dialog.battle_preview)
        self.assertIsNone(dialog.battle_window)
        self.select(EVENT);self.assertIsNone(dialog.choice.currentData())
        self.assertFalse(dialog.open_stage_button.isEnabled())
    def test_failed_sources_clear_related_window_and_recover_without_selection(self):
        dialog=self.open();self.choose(dialog,4,1);dialog.open_stage_button.click();self.qt.processEvents()
        with patch.object(model,'MANIFEST','research/missing-ritual-302.json'):
            self.node.refresh();self.qt.processEvents()
            self.assertFalse(self.node.ritual_weakening_button.isEnabled())
            self.assertIsNone(dialog.choice.currentData());self.assertIsNone(dialog.battle_window)
            self.assertIsNone(dialog.battle_preview)
        self.node.refresh();self.qt.processEvents()
        self.assertTrue(self.node.ritual_weakening_button.isEnabled())
        self.assertIsNone(dialog.choice.currentData());self.assertFalse(dialog.open_stage_button.isEnabled())
    def test_stale_entry_checks_sources_before_constructing_reader(self):
        self.assertIsNone(self.node.ritual_weakening_window)
        with patch.object(model,'MANIFEST','research/missing-ritual-302.json'):
            self.node.open_ritual_weakening()
        self.assertIsNone(self.node.ritual_weakening_window)
        self.assertFalse(self.node.ritual_weakening_button.isEnabled())
    def test_same_scope_refresh_keeps_parent_child_reading_and_battle_identity(self):
        dialog=self.open();self.choose(dialog,2,1);dialog.open_stage_button.click();self.qt.processEvents()
        battle=dialog.battle_preview;window=dialog.battle_window
        self.node.reading_tabs.setCurrentWidget(self.node.detail)
        dialog.reading_tabs.setCurrentWidget(dialog.source_text);self.qt.processEvents()
        states=[]
        for widget in (self.node.detail,dialog.source_text):
            cursor=QTextCursor(widget.document());cursor.setPosition(5)
            cursor.setPosition(25,QTextCursor.MoveMode.KeepAnchor);widget.setTextCursor(cursor)
            self.assertGreater(widget.verticalScrollBar().maximum(),0)
            widget.verticalScrollBar().setValue(max(1,widget.verticalScrollBar().maximum()//2))
            states.append(reading(widget))
        selected=dialog.choice.currentData();self.node.refresh();self.qt.processEvents()
        self.assertEqual(states,[reading(self.node.detail),reading(dialog.source_text)])
        self.assertEqual(dialog.choice.currentData(),selected)
        self.assertIs(dialog.battle_preview,battle);self.assertIs(dialog.battle_window,window)
        self.assertEqual(battle.current_stage,'ro6_b_6')
    def test_existing_special_readers_stay_separate(self):
        for identity,button,window in (
            ('community_group_021','documented_item_button','documented_item_window'),
            ('community_group_024','expedition_button','expedition_window'),
            ('community_group_009','future_region_button','future_region_window'),
            ('community_group_005','named_reward_button','named_reward_window')):
            self.select(identity);self.assertFalse(self.node.ritual_weakening_button.isVisible())
            entry=getattr(self.node,button);self.assertTrue(entry.isVisible());self.assertTrue(entry.isEnabled())
            entry.click();self.qt.processEvents();self.assertIsNotNone(getattr(self.node,window))

if __name__=='__main__':unittest.main()
