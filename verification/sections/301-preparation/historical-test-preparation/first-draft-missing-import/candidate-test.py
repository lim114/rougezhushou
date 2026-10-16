"""Player item reading must remain separate from rewards and preserve context."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import node_catalog as catalog, documented_choice_items as model
from rouge.node_catalog_view import NodeCatalogPanel
from rouge.player_node_information import node_information_text

ROOT=Path(__file__).resolve().parents[1]
BASELINE=ROOT/'verification/sections/295-preparation/pre295-query-baseline.json'
BASELINE_SHA='50799b7758d235963e97f3c844211abcce9cfcb3caf5b3be16a69495a347bb27'

def entry(event_id=model.EVENT):
    return {'kind':'event','record':next(e for e in catalog.all_events(include_indirect=True)['rows'] if e['id']==event_id)}

class DocumentedItemIntegration295Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance() or QApplication([])

    def test_every_reward_query_including_target_is_exactly_unchanged(self):
        raw=BASELINE.read_bytes();self.assertEqual(sha256(raw).hexdigest(),BASELINE_SHA)
        old=json.loads(raw);self.assertEqual(len(old['events']),38)
        for event_id,row in old['events'].items():
            self.assertEqual(catalog.event_reward_options(event_id),row['reward_options'],event_id)
        original=(ROOT/'verification/sections/298-preparation/before/rouge/node_catalog.py').read_bytes()
        self.assertEqual(sha256(original).hexdigest(),old['node_catalog_sha256'])
        original_tree=ast.parse(original.decode('utf8'))
        current_tree=ast.parse((ROOT/'rouge/node_catalog.py').read_bytes().decode('utf8'))
        original_query=next(n for n in original_tree.body if isinstance(n,ast.FunctionDef) and n.name=='event_reward_options')
        current_query=next(n for n in current_tree.body if isinstance(n,ast.FunctionDef) and n.name=='event_reward_options')
        self.assertEqual(ast.dump(current_query,include_attributes=False),ast.dump(original_query,include_attributes=False))

    def test_non_target_player_output_is_exactly_unchanged(self):
        old=json.loads(BASELINE.read_bytes())
        # Replay the295 presentation scope;297 separately verifies all37 current
        # non-target outputs and the new delayed expedition-result rendering.
        with patch('rouge.player_node_information.expedition_results.event_reference',return_value=None):
            for event_id,row in old['events'].items():
                if event_id==model.EVENT:continue
                text=node_information_text(entry(event_id))
                self.assertEqual(sha256(text.encode()).hexdigest(),row['player_sha256'],event_id)

    def test_player_reference_is_under_exact_option_and_not_claimed_as_reward(self):
        text=node_information_text(entry());self.assertEqual(text.count('资料写明的物品：沙盘α'),1)
        start=text.index('我受雇于梅兰德');end=text.index('资料写明的物品：沙盘α')
        self.assertLess(start,end);self.assertIn('查看选项中的物品说明',text)
        self.assertIn('数量与本局实际领取尚未确认',text)
        self.assertNotIn('具名奖励：沙盘α',text);self.assertNotIn('documented_named_item',text)
        original=catalog.event_details(model.EVENT)
        self.assertEqual(original['rows'][0]['choices'][0]['game_choice_ids'],[])

    def test_same_choice_key_from_another_scene_or_event_cannot_supply_item(self):
        reference=model.event_item_references(model.EVENT)
        for field in ('event_id','scene_key','choice_key'):
            forged=deepcopy(reference);forged['items'][0][field]='other'
            with patch('rouge.player_node_information.event_item_references',return_value=forged):
                self.assertNotIn('资料写明的物品：沙盘α',node_information_text(entry()))

    def test_missing_source_keeps_original_option_and_explains_supplement_unknown(self):
        with patch('rouge.player_node_information.event_item_references',return_value={'status':'unknown','items':[]}):
            text=node_information_text(entry())
        self.assertIn('补充物品资料暂时无法核对',text);self.assertIn('我受雇于梅兰德',text)
        self.assertNotIn('资料写明的物品：沙盘α',text)

    def parent(self):
        parent=NodeCatalogPanel();parent.resize(1050,720);parent.show();self.qt.processEvents()
        i=next(i for i,r in enumerate(parent.entries) if r['kind']=='event' and r['record']['id']==model.EVENT)
        parent.list.setCurrentRow(i);self.qt.processEvents();return parent

    def close_parent(self,parent):
        if parent.documented_item_window:parent.documented_item_window.close()
        parent.close();parent.deleteLater();self.qt.processEvents()

    def test_main_entry_is_manual_and_does_not_borrow_current_other_choice_filter(self):
        parent=self.parent()
        try:
            other=next(i for i in range(parent.event_choice_filter.count())
                if parent.event_choice_filter.itemData(i) not in (None,model.CHOICE))
            parent.event_choice_filter.setCurrentIndex(other);self.qt.processEvents()
            parent.documented_item_button.click();self.qt.processEvents();dialog=parent.documented_item_window
            self.assertTrue(dialog.isVisible());self.assertFalse(dialog.isModal())
            self.assertIsNone(dialog.choice.currentData());self.assertFalse(dialog.icon.isVisible())
            self.assertIn('我受雇于梅兰德',dialog.choice.itemText(0))
            self.assertIsNone(dialog._details_identity)
        finally:self.close_parent(parent)

    def test_parent_and_opened_item_reading_survive_same_scope_refresh(self):
        parent=self.parent()
        try:
            parent.reading_tabs.setCurrentWidget(parent.detail);reader=parent.detail;self.qt.processEvents()
            cursor=QTextCursor(reader.document());cursor.setPosition(4);cursor.setPosition(28,QTextCursor.MoveMode.KeepAnchor)
            reader.setTextCursor(cursor);bar=reader.verticalScrollBar();self.assertGreater(bar.maximum(),0)
            bar.setValue(max(1,bar.maximum()//2));self.qt.processEvents()
            def state(widget):
                c=widget.textCursor();return c.anchor(),c.position(),widget.verticalScrollBar().value()
            before=(parent.list.selected_key(),parent.event_choice_filter.currentData(),state(reader),
                    deepcopy((parent.map_context,parent.node_context,parent.dossier,parent.runtime_context)))
            parent.documented_item_button.click();dialog=parent.documented_item_window
            dialog.choice.setCurrentIndex(0);dialog.open_item_button.click()
            dialog.reading_tabs.setCurrentWidget(dialog.source_text);self.qt.processEvents()
            sub=dialog.source_text;c=QTextCursor(sub.document());c.setPosition(3);c.setPosition(40,QTextCursor.MoveMode.KeepAnchor)
            sub.setTextCursor(c);b=sub.verticalScrollBar();self.assertGreater(b.maximum(),0);b.setValue(max(1,b.maximum()//2))
            self.qt.processEvents();sub_before=(dialog.choice.currentData(),dialog._details_identity,state(sub))
            parent.refresh();self.qt.processEvents()
            self.assertEqual((parent.list.selected_key(),parent.event_choice_filter.currentData(),state(reader),
                    (parent.map_context,parent.node_context,parent.dossier,parent.runtime_context)),before)
            self.assertEqual((dialog.choice.currentData(),dialog._details_identity,state(sub)),sub_before)
            self.assertEqual(parent.reading_tabs.currentWidget(),reader);self.assertEqual(dialog.reading_tabs.currentWidget(),sub)
        finally:self.close_parent(parent)

    def test_parent_source_failure_clears_open_child_and_recovery_stays_manual(self):
        parent=self.parent()
        try:
            parent.documented_item_button.click();dialog=parent.documented_item_window
            dialog.choice.setCurrentIndex(0);dialog.open_item_button.click();self.assertTrue(dialog.icon.isVisible())
            with patch.object(model,'MANIFEST','research/nonexistent-295-manifest.json'):
                parent.refresh();self.qt.processEvents()
                self.assertFalse(parent.documented_item_button.isEnabled());self.assertEqual(dialog.choice.count(),0)
                self.assertFalse(dialog.icon.isVisible());self.assertIsNone(dialog._details_identity)
                self.assertIn('补充物品资料暂时无法核对',parent.player_detail.toPlainText())
                for reader in (dialog.item_text,dialog.choice_text,dialog.source_text):
                    self.assertNotIn('沙盘α',reader.toPlainText())
            parent.refresh();self.qt.processEvents();self.assertTrue(parent.documented_item_button.isEnabled())
            self.assertIsNone(dialog.choice.currentData());self.assertFalse(dialog.icon.isVisible())
            self.assertIsNone(dialog._details_identity)
        finally:self.close_parent(parent)

    def test_switch_to_other_event_clears_child_and_direct_entry_cannot_reopen_it(self):
        parent=self.parent()
        try:
            parent.documented_item_button.click();dialog=parent.documented_item_window
            dialog.choice.setCurrentIndex(0);dialog.open_item_button.click()
            other=next(i for i,r in enumerate(parent.entries) if r['kind']=='event' and r['record']['id']!=model.EVENT)
            parent.list.setCurrentRow(other);self.qt.processEvents();parent.open_documented_items()
            self.assertFalse(parent.documented_item_button.isVisible());self.assertEqual(dialog.choice.count(),0)
            self.assertFalse(dialog.icon.isVisible());self.assertIsNone(dialog._details_identity)
        finally:self.close_parent(parent)

if __name__=='__main__':unittest.main()
