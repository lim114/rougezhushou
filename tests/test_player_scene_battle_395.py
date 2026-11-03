import unittest
from types import SimpleNamespace
from unittest.mock import patch
from copy import deepcopy
from PySide6.QtWidgets import QApplication
from rouge.player_scene_battle import stage_candidates,SceneBattlePanel

class DiagnosticLayout395(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])

    def test_diagnostic_layout_is_explicit_and_does_not_enable_routes(self):
        from tests import test_batch185_mainwindow as fixture
        import os
        with patch.dict(os.environ,{'ROUGE_DIAGNOSTIC_LAYOUT':'1'}):fixture.Batch185WindowTests.setUp(self)
        window=self.window
        self.assertTrue(window.diagnostic_layout);self.assertFalse(window.include_historical_route_diagnostics)
        self.assertEqual(type(window.centralWidget()).__name__,'DiagnosticWorkspace')
        self.assertFalse(hasattr(window,'route_constraints'));self.assertTrue(window.run_cards.isHidden())
        self.assertTrue(window.damage_tools_fold.toggle.isChecked());self.assertTrue(window.capture_details.toggle.isChecked())
        panel=window.reference_panel('scenes');self.qt.processEvents()
        self.assertIs(window.centralWidget().currentWidget(),panel);self.assertTrue(panel.event_item_uses_button.isVisible())

    def test_other_environment_text_does_not_enable_diagnostic_layout(self):
        from tests import test_batch185_mainwindow as fixture
        import os
        with patch.dict(os.environ,{'ROUGE_DIAGNOSTIC_LAYOUT':'true'}):fixture.Batch185WindowTests.setUp(self)
        self.assertFalse(self.window.diagnostic_layout);self.assertEqual(self.window.centralWidget().count(),5)

    def test_explicit_non_boolean_layout_is_rejected_before_io(self):
        from rouge.app import MainWindow
        with self.assertRaises(ValueError):MainWindow(diagnostic_layout='false')

class SceneBattle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.gui=QApplication.instance()or QApplication([])
    def test_name_keeps_all_exact_variants(self):
        rows=stage_candidates({'kind':'battle','title':'遗忘时间'});self.assertGreaterEqual(len(rows),2);self.assertEqual(len({r['id']for r in rows}),len(rows))
    def test_invalid_explicit_id_never_guesses_same_name(self):self.assertEqual(stage_candidates({'kind':'battle','title':'遗忘时间','stage_id':'nonexistent'}),[])
    def test_no_battle_no_candidates(self):
        for content in(None,{}, {'kind':'event','title':'遗忘时间'}, {'kind':'battle','title':''}):self.assertEqual(stage_candidates(content),[])
    def test_exact_identity_restricts_to_one(self):
        rows=stage_candidates({'kind':'battle','title':'遗忘时间'});self.assertEqual(len(stage_candidates({'kind':'battle','stage_id':rows[0]['id']})),1)
    def test_refresh_retains_enemy_reading_on_timestamp_only_change(self):
        state={'last_node_content':{'kind':'battle','title':'遗忘时间','captured_at':1}};run=SimpleNamespace(state=state);panel=SceneBattlePanel(run)
        try:
            panel.stages.setCurrentIndex(1);kind=next(k for k,w in panel.lists.items()if w.count());widget=panel.lists[kind];panel.tabs.setCurrentWidget(widget);widget.setCurrentRow(0);item=widget.currentItem();text=panel.detail.toPlainText()
            state['last_node_content']['captured_at']=2;panel.refresh();self.assertIs(widget.currentItem(),item);self.assertEqual(panel.detail.toPlainText(),text)
        finally:panel.close()
    def test_context_change_and_source_loss_clear(self):
        run=SimpleNamespace(state={'last_node_content':{'kind':'battle','title':'遗忘时间'}});panel=SceneBattlePanel(run)
        try:
            panel.stages.setCurrentIndex(1)
            with patch('rouge.player_scene_battle.expansion_reference.packet',return_value=None):panel.refresh();self.assertFalse(panel.enemies);self.assertFalse(panel.open_button.isEnabled())
        finally:panel.close()
    def test_no_mutation_no_default_variant(self):
        state={'last_node_content':{'kind':'battle','title':'遗忘时间'}};before=deepcopy(state);panel=SceneBattlePanel(SimpleNamespace(state=state))
        try:self.assertIsNone(panel.stages.currentData());self.assertEqual(state,before)
        finally:panel.close()

    def test_invalid_typed_explicit_identity_never_falls_back(self):
        for value in(False,True,0,[],{},''):
            self.assertEqual(stage_candidates({'kind':'battle','title':'遗忘时间','stage_id':value}),[])

    def test_same_context_battle_source_failure_clears_and_recovery_needs_selection(self):
        run=SimpleNamespace(state={'last_node_content':{'kind':'battle','title':'遗忘时间'}});panel=SceneBattlePanel(run)
        try:
            panel.stages.setCurrentIndex(1);self.assertTrue(panel.enemies)
            with patch('rouge.player_scene_battle.model.packet',return_value=None):
                panel.open_stage();self.assertFalse(panel.enemies);self.assertIsNone(panel.dialog);self.assertFalse(panel.open_button.isEnabled())
            panel.refresh();self.assertIsNone(panel.stages.currentData());self.assertFalse(panel.enemies)
        finally:panel.close()

    def test_malformed_context_clears_without_crashing(self):
        run=SimpleNamespace(state={'last_node_content':{'kind':'battle','title':'遗忘时间'}});panel=SceneBattlePanel(run)
        try:
            panel.stages.setCurrentIndex(1)
            for value in('malformed',[1],True):
                run.state['last_node_content']=value;panel.refresh();self.assertFalse(panel.enemies);self.assertIsNone(panel.stages.currentData())
        finally:panel.close()
