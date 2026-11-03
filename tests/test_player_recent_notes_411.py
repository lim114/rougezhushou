from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
import unittest
from PySide6.QtWidgets import QApplication
from rouge.player_notes import NoteStore,NotesDialog,content_key
from rouge.player_recent_notes import RecentNotesPanel,scene_context

class RecentNotesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance()or QApplication([])
    def setUp(self):
        self.tmp=TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.store=NoteStore(self.tmp.name);self.run=SimpleNamespace(state={'id':'one','last_node_content':None})
        self.panel=RecentNotesPanel(self.run,self.store);self.addCleanup(self.panel.deleteLater)
        self.a={'kind':'battle','title':'同名关卡','variant_id':'normal'}
        self.b={**self.a,'variant_id':'emergency'}
    def save(self,content,text):
        key=content_key(content);self.store.save(key,text,self.store.read(key)[1])
    def bind(self,content):self.run.state['last_node_content']=content;self.panel.refresh(force=True)
    def test_automatic_scene_change_separates_exact_variants(self):
        self.save(self.a,'普通笔记');self.save(self.b,'紧急笔记');self.bind(self.a)
        self.assertIn('普通笔记',self.panel.preview.toPlainText());self.bind(self.b)
        self.assertIn('紧急笔记',self.panel.preview.toPlainText());self.assertNotIn('普通笔记',self.panel.preview.toPlainText())
    def test_no_context_clears_old_preview_without_touching_files(self):
        self.save(self.a,'保留原文');self.bind(self.a);before=list(Path(self.tmp.name).iterdir());self.bind(None)
        self.assertEqual(self.panel.preview.toPlainText(),'');self.assertFalse(self.panel.edit.isEnabled())
        self.assertEqual(list(Path(self.tmp.name).iterdir()),before);self.assertEqual(self.store.read(content_key(self.a))[0],'保留原文')
    def test_pause_is_explicit_and_resume_follows_latest(self):
        self.save(self.a,'甲');self.save(self.b,'乙');self.bind(self.a);self.panel.follow.setChecked(False);self.bind(self.b)
        self.assertEqual(self.panel.context,self.a);self.assertIn('暂停',self.panel.scene.text())
        self.panel.follow.setChecked(True);self.assertEqual(self.panel.context,self.b)
    def test_same_scene_poll_uses_metadata_and_force_refresh_rereads(self):
        self.save(self.a,'已有记录');self.bind(self.a)
        with patch.object(self.store,'read',wraps=self.store.read)as read:
            for _ in range(20):self.panel.refresh()
            self.assertEqual(read.call_count,0)
            self.panel.refresh(force=True);self.assertEqual(read.call_count,1)
    def test_external_save_and_delete_are_reflected(self):
        self.save(self.a,'旧笔记');self.bind(self.a);self.save(self.a,'更新内容');self.panel.refresh(force=True)
        self.assertIn('更新内容',self.panel.preview.toPlainText());self.store.path(content_key(self.a)).unlink();self.panel.refresh(force=True)
        self.assertEqual(self.panel.preview.toPlainText(),'');self.assertIn('还没有',self.panel.status.text())
    def test_read_failure_clears_visible_old_text_and_retains_original(self):
        self.save(self.a,'旧正文');self.bind(self.a)
        with patch.object(self.store,'read',side_effect=PermissionError('test only')):self.panel.refresh(force=True)
        self.assertEqual(self.panel.preview.toPlainText(),'');self.assertEqual(self.store.read(content_key(self.a))[0],'旧正文')
    def test_bad_input_and_reference_note_do_not_borrow_saved_game_notes(self):
        for row in(None,[],{}, {'kind':'battle','title':' '},{'kind':'battle','title':'x','variant_id':[]},
                   {'kind':'reference-stage','title':'同名关卡','variant_id':'normal'}):
            self.assertIsNone(scene_context(row));self.bind(row);self.assertIsNone(self.panel.context)
    def test_title_only_scope_is_disclosed(self):
        self.bind({'kind':'event','title':'已读事件'})
        self.assertIn('同名场景共用',self.panel.status.text());self.assertIn('不表示当前',self.panel.status.text())
    def test_new_run_clears_paused_reading_but_never_deletes_notes(self):
        self.save(self.a,'本机笔记');self.bind(self.a);self.panel.follow.setChecked(False)
        self.run.state={'id':'two','last_node_content':None};self.panel.refresh(force=True)
        self.assertIsNone(self.panel.context);self.assertEqual(self.store.read(content_key(self.a))[0],'本机笔记')
    def test_follow_preview_does_not_rebind_or_change_unsaved_editor(self):
        editor=NotesDialog(self.tmp.name);self.addCleanup(editor.deleteLater)
        editor.set_context(self.a);editor.editor.setPlainText('未保存原文');key=editor.key
        self.bind(self.b);self.panel.reload.click()
        self.assertTrue(editor.dirty);self.assertEqual(editor.key,key);self.assertEqual(editor.editor.toPlainText(),'未保存原文')
    def test_edit_request_rereads_scene_and_emits_detached_context(self):
        self.bind(self.a);emitted=[];self.panel.editRequested.connect(emitted.append)
        self.run.state['last_node_content']=self.b;self.panel.edit.click()
        self.assertEqual(emitted,[self.b]);emitted[0]['title']='edited';self.assertEqual(self.run.state['last_node_content']['title'],'同名关卡')
    def test_corrupt_utf8_is_not_overwritten(self):
        self.store.path(content_key(self.a)).write_bytes(b'\xff');self.bind(self.a)
        self.assertEqual(self.panel.preview.toPlainText(),'');self.assertEqual(self.store.path(content_key(self.a)).read_bytes(),b'\xff')

if __name__=='__main__':unittest.main()
