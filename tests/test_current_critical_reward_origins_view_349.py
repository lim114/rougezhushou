from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import current_critical_reward_origins as model
from rouge.current_reward_origins_view import CurrentRewardOriginsDialog
from rouge.current_critical_reward_origins_view import make_event_dialog
from tests.test_current_critical_reward_origins_349 import clone

class CriticalRewardView349Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.qt = QApplication.instance() or QApplication([])
    def dialog(self, iid):
        d = CurrentRewardOriginsDialog('relics', iid); d.show(); self.qt.processEvents(); self.addCleanup(d.close); return d
    def child(self, iid):
        p = self.dialog(iid).panel; self.assertIsNone(p.entries.currentItem()); self.assertFalse(p.open_button.isEnabled())
        p.entries.setCurrentRow(0); self.assertTrue(p.open_event()); return p, p.event_dialog.panel

    def test_three_exact_flows_and_only_relevant_condition_controls(self):
        for event, cid, iid in model.SELECTIONS:
            p, child = self.child(iid)
            expected = {'entry': {'floor', 'node_type', 'post_update_clear'}, 'revive': {'node_type', 'next_unmarked_after_first_down', 'rescue_used'}, 'blueprint': set()}[event]
            self.assertEqual(set(child.controls), expected); self.assertEqual(hasattr(child, 'gold'), event == 'entry')
            self.assertIn(child.flow_button.text(), child.player.toPlainText())
            self.assertTrue(child.open_flow()); flow = child.flow_dialog.panel
            self.assertEqual((flow.scene_id, flow.choice_id), (child.result['rows'][0]['reader_target']['scene_id'], child.result['rows'][0]['reader_target']['choice_id']))
            if event == 'entry':
                self.assertEqual(flow.result['source_request'], {'category': 'choices', 'key': cid})
                self.assertEqual(flow.result['choices'][flow.choice_id]['variant_ids'], [cid])
            else: self.assertEqual(flow.choice_id, cid)
            self.assertIsNone(child.result['actual_received']); self.assertFalse(child.result['run_updated'])
            self.assertIn('不补成1件', p.player.toPlainText()); p.close()

    def test_parent_refresh_keeps_two_nonzero_readings_manual_context_and_advanced_flow(self):
        p, c = self.child('rogue_6_relic_final_7'); p.window().resize(700, 390)
        c.gold.setValue(9); c.controls['post_update_clear'].setCurrentIndex(1); self.assertTrue(c.open_flow())
        flow = c.flow_dialog; c.window().resize(700, 390); self.qt.processEvents()
        for reader in (c.player, c.technical):
            c.tabs.setCurrentWidget(reader); self.qt.processEvents(); cursor = reader.textCursor(); cursor.setPosition(3); cursor.setPosition(15, QTextCursor.MoveMode.KeepAnchor); reader.setTextCursor(cursor)
            bar = reader.verticalScrollBar(); self.assertGreater(bar.maximum(), 0); bar.setValue(min(3, bar.maximum()))
            prior = (cursor.anchor(), cursor.position(), bar.value(), c.tabs.currentIndex())
            self.assertTrue(p.refresh_reference()); self.qt.processEvents(); cursor = reader.textCursor()
            self.assertEqual(prior, (cursor.anchor(), cursor.position(), bar.value(), c.tabs.currentIndex()))
        self.assertEqual(c.gold.value(), 9); self.assertIs(c.flow_dialog, flow); self.assertTrue(flow.isVisible())
        self.assertEqual(flow.panel.result['choices'][flow.panel.choice_id]['variant_ids'], ['choice_ro6_final1_8'])

    def test_damage_clears_nested_flow_and_recovery_requires_item_reselection(self):
        p, c = self.child('rogue_6_relic_final_9'); self.assertTrue(c.open_flow()); flow = c.flow_dialog; child = p.event_dialog
        with TemporaryDirectory() as folder:
            root = Path(folder); clone(root); path = root / model.DATA; raw = path.read_bytes()
            with patch.object(model, 'ROOT', root):
                path.write_bytes(raw + b'x'); self.assertFalse(p.refresh_reference()); self.assertFalse(flow.isVisible()); self.assertFalse(child.isVisible())
                self.assertIsNone(p.result); self.assertEqual(p.entries.count(), 0); self.assertEqual(p.technical.toPlainText(), '')
                path.write_bytes(raw); self.assertTrue(p.refresh_reference()); self.assertIsNone(p.entries.currentItem()); self.assertFalse(p.open_event())

    def test_repeat_open_deselect_and_parent_close_clean_whole_tree_forged_row_rejected(self):
        p, c = self.child('rogue_6_relic_final_10'); self.assertTrue(c.open_flow()); old = c.flow_dialog
        self.assertTrue(c.open_flow()); self.assertFalse(old.isVisible()); flow = c.flow_dialog; child = p.event_dialog
        p.entries.setCurrentRow(-1); self.assertFalse(child.isVisible()); self.assertFalse(flow.isVisible())
        p.entries.setCurrentRow(0); p.open_event(); c = p.event_dialog.panel; c.open_flow(); flow = c.flow_dialog; p.window().close(); self.assertFalse(flow.isVisible())
        row = deepcopy(model.packet()['data']['rows'][0]); row['target'] = {}; self.assertIsNone(make_event_dialog(row))

if __name__ == '__main__': unittest.main()
