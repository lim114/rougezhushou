import unittest
from types import SimpleNamespace
from unittest.mock import patch
from copy import deepcopy
from PySide6.QtWidgets import QApplication
from rouge.player_scene_battle import stage_candidates,SceneBattlePanel

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
