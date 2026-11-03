"""Public node entry and reading continuity for the exact red-moss choices."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication
from rouge import future_region_effects as model, node_catalog as catalog, event_planning
from rouge.node_catalog_view import NodeCatalogPanel

ROOT = Path(__file__).resolve().parents[1]

def reading(w):
    c = w.textCursor()
    return w.toPlainText(), c.anchor(), c.position(), w.verticalScrollBar().value()

def entry(identity):
    return next(e for e in catalog.all_events(include_indirect=True)['rows'] if e['id'] == identity)

def canon(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()

class FutureRegionIntegration300Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.qt = QApplication.instance() or QApplication([])
    def setUp(self):
        self.node = NodeCatalogPanel()
        self.node.resize(1050, 720)
        self.node.show()
        self.select(model.EVENT)
    def tearDown(self):
        if self.node.future_region_window: self.node.future_region_window.close()
        self.node.close(); self.node.deleteLater(); self.qt.processEvents()
    def select(self, identity):
        self.node.kind.setCurrentIndex(self.node.kind.findData('event'))
        self.node.floor.setCurrentIndex(self.node.floor.findData(None))
        self.node.node_type.setCurrentIndex(self.node.node_type.findData(None))
        self.node.search.setText(entry(identity)['title']); self.node.refresh()
        index = next(i for i, e in enumerate(self.node.entries)
                     if e['kind'] == 'event' and e['record']['id'] == identity)
        self.node.list.setCurrentRow(index); self.qt.processEvents()
    def open(self):
        self.node.future_region_button.click(); self.qt.processEvents()
        return self.node.future_region_window
    def choose(self, dialog, index=0):
        dialog.choice.setCurrentIndex(index); self.qt.processEvents()
        self.assertIsNotNone(dialog.choice.currentData())
    def test_public_manual_entry_opens_unselected_two_choice_reader(self):
        self.assertTrue(self.node.future_region_button.isVisible())
        self.assertTrue(self.node.future_region_button.isEnabled())
        d = self.open()
        self.assertIsNone(d.choice.currentData()); self.assertEqual(d.choice.count(), 2)
        self.assertIs(d.reading_tabs.currentWidget(), d.player_text)
    def test_each_exact_choice_is_separate_without_changing_parent_selection(self):
        key = self.node.list.selected_key(); parent = reading(self.node.player_detail)
        d = self.open(); output = []
        for i in range(2):
            self.choose(d, i); output.append(d.player_text.toPlainText())
            self.assertIn('希望的沃土', output[-1]); self.assertIn('随机零件', output[-1])
        self.assertIn('30', output[0]); self.assertIn('种子', output[1])
        self.assertNotEqual(output[0], output[1]); self.assertEqual(key, self.node.list.selected_key())
        self.assertEqual(parent, reading(self.node.player_detail))
    def test_known_context_changes_recompute_documented_phase_without_reselecting(self):
        self.node.set_map_context(None, runtime_context={'exploration_mode':'NORMAL', 'difficulty':6})
        d = self.open(); self.choose(d); selected = d.choice.currentData()
        self.assertEqual(d.packet['documented_phase'], 'middle')
        first = d.player_text.toPlainText()
        self.node.set_map_context(None, runtime_context={'exploration_mode':'NORMAL', 'difficulty':12})
        self.qt.processEvents()
        self.assertEqual(d.packet['documented_phase'], 'late'); self.assertEqual(selected, d.choice.currentData())
        self.assertNotEqual(first, d.player_text.toPlainText())
    def test_low_difficulty_keeps_all_stages_readable_and_actual_unknown(self):
        self.node.set_map_context(None, runtime_context={'exploration_mode':'NORMAL', 'difficulty':1})
        d = self.open(); self.choose(d)
        self.assertIsNone(d.packet['documented_phase'])
        for text in ('早期','中期','晚期','未'):
            self.assertIn(text, d.player_text.toPlainText())
    def test_unknown_mode_does_not_inherit_normal_reference_phase(self):
        self.node.set_map_context(None, runtime_context={'difficulty':12})
        d = self.open(); self.choose(d)
        self.assertIsNone(d.packet['documented_phase'])
    def test_same_scope_refresh_preserves_actual_reading_in_parent_and_dialog(self):
        d = self.open(); self.choose(d)
        self.node.reading_tabs.setCurrentWidget(self.node.detail)
        d.reading_tabs.setCurrentWidget(d.source_text); self.qt.processEvents()
        states = []
        for widget in (self.node.detail, d.source_text):
            c = QTextCursor(widget.document()); c.setPosition(5)
            c.setPosition(26, QTextCursor.MoveMode.KeepAnchor); widget.setTextCursor(c)
            self.assertGreater(widget.verticalScrollBar().maximum(), 0)
            widget.verticalScrollBar().setValue(max(1,widget.verticalScrollBar().maximum()//2))
            states.append(reading(widget))
        choice = d.choice.currentData(); self.node.refresh(); self.qt.processEvents()
        self.assertIs(self.node.future_region_window, d)
        self.assertEqual(states, [reading(self.node.detail),reading(d.source_text)])
        self.assertEqual(choice, d.choice.currentData()); self.assertIs(d.reading_tabs.currentWidget(), d.source_text)
    def test_source_failure_clears_old_effects_and_recovery_does_not_reselect(self):
        d = self.open(); self.choose(d); old = d.player_text.toPlainText()
        with patch.object(model, 'MANIFEST', 'research/missing-future-region-300.json'):
            self.node.refresh(); self.qt.processEvents()
            self.assertFalse(self.node.future_region_button.isEnabled()); self.assertIsNone(d.choice.currentData())
            self.assertNotEqual(old, d.player_text.toPlainText()); self.assertNotIn('+30%',d.player_text.toPlainText())
        self.node.refresh(); self.qt.processEvents()
        self.assertTrue(self.node.future_region_button.isEnabled()); self.assertIsNone(d.choice.currentData())
    def test_stale_enabled_button_rechecks_source_before_open(self):
        self.assertIsNone(self.node.future_region_window)
        with patch.object(model, 'MANIFEST', 'research/missing-future-region-300.json'):
            self.node.open_future_region_effects()
        self.assertIsNone(self.node.future_region_window); self.assertFalse(self.node.future_region_button.isEnabled())
    def test_switch_event_clears_open_reader_and_hides_irrelevant_option(self):
        d = self.open(); self.choose(d); self.select('community_group_001')
        self.assertFalse(self.node.future_region_button.isVisible()); self.assertIsNone(d.choice.currentData())
        self.assertNotIn('+30%',d.player_text.toPlainText()); self.node.open_future_region_effects()
        self.assertIs(self.node.future_region_window,d)
        self.select(model.EVENT); self.assertIsNone(d.choice.currentData())
    def test_historical_context_does_not_borrow_current_mode_or_difficulty(self):
        self.node.runtime_context = {'exploration_mode':'NORMAL','difficulty':15}
        self.node.dossier = {}; self.node.node_context = ({'nodes':[{'id':'old','remembered_type':'不期而遇'}]},'old',{})
        self.node.dossier = {'history_events':[]}
        historical = deepcopy(entry(model.EVENT)); historical['historical_read_reference'] = True
        context = self.node._event_context(historical)
        self.assertNotIn('exploration_mode',context); self.assertNotIn('difficulty',context)
    def test_all_original_190_resource_queries_are_unchanged(self):
        baseline=json.loads((ROOT/'verification/sections/297-preparation/before-output-hashes.json').read_bytes())
        seen={}
        for e in catalog.all_events(include_indirect=True)['rows']:
            for scene in catalog.event_details(e['id'])['rows']:
                seen[scene['key']]=sha256(canon(event_planning.choice_resources(e['id'],scene['key']))).hexdigest()
        self.assertEqual(len(seen),190); self.assertEqual(seen,baseline['choice_resources_scenes'])
if __name__ == '__main__': unittest.main()
