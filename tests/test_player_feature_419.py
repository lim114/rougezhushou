import unittest,tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from rouge.player_note_selector import catalogue,matching,SceneNoteSelector
from rouge.player_reference_notes import reference_target
from rouge.player_notes import NoteStore,content_key
from rouge.player_recent_notes import RecentNotesPanel
class SelectorTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.gui=QApplication.instance()or QApplication([]);cls.rows=catalogue()
 def test_current_catalogue_contexts_resolve_exactly(self):
  self.assertTrue(self.rows)
  for row in self.rows[::max(1,len(self.rows)//12)]:self.assertIsNotNone(reference_target(row['context']))
  self.assertEqual(len({content_key(r['context'])for r in self.rows}),len(self.rows))
 def test_filter_is_intersection_and_unknown_not_every_floor(self):
  rows=[{'floors':['floor1'],'nodes':['作战']},{'floors':['unknown'],'nodes':['作战']},{'floors':['floor1'],'nodes':['不期而遇']}]
  self.assertEqual(matching(rows,'floor1','作战'),rows[:1]);self.assertEqual(matching(rows,'unknown'),rows[1:2])
 def test_manual_selection_pauses_follow_without_run_write(self):
  with tempfile.TemporaryDirectory()as d:
   state={'run_id':'one','last_node_content':{'kind':'event','title':'原场景'}};run=SimpleNamespace(state=state.copy());panel=RecentNotesPanel(run,NoteStore(d));target=self.rows[0]['context']
   try:
    panel.select_context(target);self.assertFalse(panel.follow.isChecked());self.assertEqual(panel.context,target);self.assertIn('手选固定资料',panel.scene.text());self.assertEqual(run.state,state);self.assertFalse(list(Path(d).iterdir()))
    panel.refresh();self.assertEqual(panel.context,target)
   finally:panel.close()
 def test_selection_preserved_and_source_loss_clears_picker(self):
  with patch('rouge.player_note_selector.catalogue',return_value=self.rows[:3]):
   widget=SceneNoteSelector();widget.scene.setCurrentIndex(1);old=widget.scene.currentData();widget.reload();self.assertEqual(widget.scene.currentData(),old)
  with patch('rouge.player_note_selector.catalogue',return_value=[]):widget.reload();self.assertEqual(widget.scene.count(),0);self.assertIsNone(widget.scene.currentData())
  widget.close()
