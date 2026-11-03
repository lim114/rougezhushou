import unittest,tempfile
from pathlib import Path
from unittest.mock import patch
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest
from rouge.player_notes import NotesDialog
class AutosaveTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.gui=QApplication.instance()or QApplication([])
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.notes=NotesDialog(self.tmp.name);self.notes.set_context({'kind':'battle','title':'准确测试场景','variant_id':'one'})
 def tearDown(self):self.notes.discard();self.notes.close();self.tmp.cleanup()
 def test_burst_debounces_and_saves_exact_current_context(self):
  n=self.notes
  with patch.object(n.store,'save',wraps=n.store.save)as saved:
   for text in ('# 草稿','# 最终正文'):n.editor.setPlainText(text)
   QTest.qWait(1100);self.gui.processEvents();self.assertFalse(n.dirty);self.assertEqual(saved.call_count,1);self.assertEqual(n.store.read(n.key)[0],'# 最终正文')
 def test_external_conflict_pauses_without_overwriting_either_copy(self):
  n=self.notes;n.editor.setPlainText('待保存正文');n.store.path(n.key).write_text('外部正文','utf8');n.save_pending()
  self.assertTrue(n.dirty);self.assertFalse(n.autosave.isChecked());self.assertEqual(n.editor.toPlainText(),'待保存正文');self.assertEqual(n.store.read(n.key)[0],'外部正文');self.assertIn('暂停',n.status.text())
 def test_failed_write_preserves_dirty_text_and_stops_timer(self):
  n=self.notes;n.editor.setPlainText('保持编辑')
  with patch.object(n.store,'save',side_effect=PermissionError()):n.save_pending()
  self.assertTrue(n.dirty);self.assertFalse(n.autosave_timer.isActive());self.assertFalse(n.autosave.isChecked())
 def test_discard_and_manual_mode_never_leave_pending_auto_save(self):
  n=self.notes;n.editor.setPlainText('放弃');n.discard();QTest.qWait(1000);self.assertFalse(n.store.path(n.key).exists())
  n.autosave.setChecked(False);n.editor.setPlainText('手动稿');n.save_pending();self.assertTrue(n.dirty);self.assertFalse(n.store.path(n.key).exists());self.assertTrue(n.save())
 def test_pending_draft_cannot_switch_context_and_close_flushes(self):
  n=self.notes;n.show();n.editor.setPlainText('原场景内容');key=n.key;self.assertFalse(n.set_context({'kind':'event','title':'其他'}));n.close();self.assertEqual(n.store.read(key)[0],'原场景内容');self.assertFalse(n.dirty)
