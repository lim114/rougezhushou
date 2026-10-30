"""Real run identity, same-note external updates and coalesced local search."""
from pathlib import Path
from tempfile import TemporaryDirectory
from copy import deepcopy
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from rouge.run_state import RunState
from rouge.player_notes import NoteStore,NotesDialog,content_key
from rouge.player_recent_notes import RecentNotesPanel
from rouge.player_note_library import NoteLibrary,NoteLibraryDialog

class NoteReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def setUp(self):
        self.temp=TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.store=NoteStore(self.root/'notes');self.run=RunState(self.root/'run.json');self.a={'kind':'battle','title':'隔离同名关卡','variant_id':'normal'};self.b={**self.a,'variant_id':'emergency'}
    def save(self,context,text):
        key=content_key(context);self.store.save(key,text,self.store.read(key)[1]);return key
    def panel(self):
        panel=RecentNotesPanel(self.run,self.store);self.addCleanup(panel.close);self.addCleanup(panel.timer.stop);return panel
    def editor(self):
        dialog=NotesDialog(self.store.folder);dialog.autosave.setChecked(False);self.addCleanup(dialog.discard);self.addCleanup(dialog.deleteLater);return dialog
    def test_real_manual_reset_clears_old_paused_scene_without_touching_note_or_draft(self):
        key=self.save(self.a,'上一局的本机笔记');self.run.state['last_node_content']=self.a;panel=self.panel();panel.follow.setChecked(False)
        dialog=self.editor();dialog.set_context(self.a);dialog.editor.setPlainText('未保存草稿');self.run.reset(save=False);panel.refresh(force=True)
        self.assertIsNone(panel.context);self.assertEqual(panel.preview.toPlainText(),'');self.assertFalse(panel.edit.isEnabled());self.assertIn('暂停',panel.status.text())
        self.assertEqual(self.store.read(key)[0],'上一局的本机笔记');self.assertTrue(dialog.dirty);self.assertEqual(dialog.editor.toPlainText(),'未保存草稿');self.assertEqual(dialog.key,key)
        self.run.state['last_node_content']=self.b;panel.follow.setChecked(True);panel.refresh(force=True);self.assertEqual(panel.context,self.b)
    def test_manual_choice_immediately_after_new_run_is_kept_and_reads_once(self):
        self.save(self.a,'甲');self.save(self.b,'乙');self.run.state['last_node_content']=self.a;panel=self.panel();self.run.reset(save=False)
        with patch.object(self.store,'read',wraps=self.store.read)as read:
            panel.select_context(self.b);self.assertEqual(read.call_count,1)
        self.assertEqual(panel.context,self.b);self.assertFalse(panel.follow.isChecked());panel.refresh(force=True);self.assertEqual(panel.context,self.b)
    def test_manual_choice_does_not_first_read_the_previous_followed_file(self):
        self.save(self.a,'甲');self.save(self.b,'乙');self.run.state['last_node_content']=self.a;panel=self.panel()
        with patch.object(self.store,'read',wraps=self.store.read)as read:
            panel.select_context(self.b);self.assertEqual([c.args[0]for c in read.call_args_list],[content_key(self.b)])
    def test_clean_reopen_reads_external_change_and_reuses_unicode_reading_state(self):
        key=self.save(self.a,'😀笔记开头\n'+'段落\n'*50);dialog=self.editor();dialog.set_context(self.a);dialog.resize(500,300);dialog.show();self.qt.processEvents()
        cursor=dialog.editor.textCursor();cursor.setPosition(2);cursor.setPosition(5,QTextCursor.MoveMode.KeepAnchor);dialog.editor.setTextCursor(cursor);dialog.editor.verticalScrollBar().setValue(12)
        anchor,position=cursor.anchor(),cursor.position();self.store.path(key).write_text('😀更新内容\n'+'新段落\n'*50,'utf8');dialog.set_context(self.a)
        self.assertIn('更新内容',dialog.editor.toPlainText());self.assertFalse(dialog.dirty);self.assertEqual((dialog.editor.textCursor().anchor(),dialog.editor.textCursor().position()),(anchor,position))
        self.assertFalse(dialog.autosave_timer.isActive());self.assertFalse(dialog.editor.signalsBlocked())
    def test_unchanged_reopen_keeps_cursor_and_dirty_reopen_never_reads_over_draft(self):
        key=self.save(self.a,'既有正文');dialog=self.editor();dialog.set_context(self.a);cursor=dialog.editor.textCursor();cursor.setPosition(2);dialog.editor.setTextCursor(cursor)
        self.assertTrue(dialog.set_context(self.a));self.assertEqual(dialog.editor.textCursor().position(),2)
        dialog.editor.setPlainText('未保存的新正文');digest=dialog.digest;self.store.path(key).write_text('外部更新','utf8')
        with patch.object(dialog.store,'read',wraps=dialog.store.read)as read:self.assertTrue(dialog.set_context(self.a));self.assertEqual(read.call_count,0)
        self.assertEqual(dialog.editor.toPlainText(),'未保存的新正文');self.assertEqual(dialog.digest,digest);self.assertFalse(dialog.set_context(self.b))
    def test_same_note_read_failure_keeps_existing_body_and_does_not_publish(self):
        key=self.save(self.a,'保留正文');dialog=self.editor();dialog.set_context(self.a)
        with patch.object(dialog.store,'read',side_effect=PermissionError('isolated read error')):self.assertFalse(dialog.set_context(self.a))
        self.assertEqual(dialog.editor.toPlainText(),'保留正文');self.assertEqual(self.store.read(key)[0],'保留正文');self.assertFalse(dialog.dirty)
    def test_refresh_button_reloads_picker_and_lost_fixed_source_preserves_saved_note(self):
        panel=self.panel();context=panel.selector.rows[0]['context'];self.save(context,'这份版本的笔记');panel.select_context(context)
        from rouge import player_note_selector as selector,player_reference_notes as refs
        before=deepcopy(panel.context)
        with patch.object(selector,'catalogue_snapshot',return_value={'rows':[],'unavailable':['固定资料']}),patch.object(refs,'reference_target',return_value=None):
            panel.reload.click();self.assertEqual(panel.selector.scene.count(),0);self.assertIn('原固定资料暂不可核对',panel.status.text())
            panel.select_context({**context,'variant_id':'unknown-source'});self.assertEqual(panel.context,before)
        self.assertEqual(self.store.read(content_key(context))[0],'这份版本的笔记')
    def test_search_burst_has_one_disk_scan_return_is_immediate_and_hidden_stops_pending(self):
        for context,text in((self.a,'普通作战注意'),(self.b,'紧急机关说明')):
            self.save(context,text);NoteLibrary(self.store.folder).record(context)
        dialog=NoteLibraryDialog(self.store.folder);self.addCleanup(dialog.close);dialog.show();self.qt.processEvents()
        with patch.object(dialog.library,'rows',wraps=dialog.library.rows)as rows:
            for text in('紧','紧急','紧急机','紧急机关'):dialog.search.setText(text)
            self.assertEqual(rows.call_count,0);QTest.qWait(210);self.qt.processEvents();self.assertEqual(rows.call_count,1);self.assertEqual(dialog.entries.count(),1)
            dialog.search.setText('普通');dialog.search.returnPressed.emit();self.assertEqual(rows.call_count,2);self.assertEqual(dialog.entries.count(),1);self.assertFalse(dialog.search_timer.isActive())
            dialog.search.setText('机关');dialog.hide();QTest.qWait(210);self.assertEqual(rows.call_count,2)
            dialog.refresh();self.assertEqual(rows.call_count,3);self.assertEqual(dialog.entries.count(),1)

class CatalogueSourceReviewTests(unittest.TestCase):
    def test_one_unavailable_classifier_does_not_hide_other_verified_note_categories(self):
        from rouge import player_note_selector as model
        complete=model.catalogue_snapshot();self.assertFalse(complete['unavailable']);self.assertTrue(complete['rows'])
        with patch.object(model.events,'packet',return_value=None):
            rows=model.catalogue_snapshot();self.assertEqual(rows['unavailable'],['事件分类']);self.assertEqual(rows['rows'],[r for r in complete['rows']if r['context']['kind']=='reference-stage'])
        with patch.object(model.stages,'packet',return_value=None):
            rows=model.catalogue_snapshot();self.assertEqual(rows['unavailable'],['关卡分类']);self.assertEqual(rows['rows'],[r for r in complete['rows']if r['context']['kind']=='reference-scene'])
        with patch.object(model.model,'packet',return_value=None):self.assertEqual(model.catalogue_snapshot(),{'rows':[],'unavailable':['固定资料']})
    def test_unrelated_program_source_is_not_runtime_data_but_corrupted_data_still_refuses(self):
        from rouge import current_event_directory as model
        from tests.test_current_event_directory_372 import clone
        import json
        with TemporaryDirectory()as folder:
            root=clone(folder)
            self.assertTrue(all(not n.endswith('.py')for n in json.loads((root/model.MANIFEST).read_bytes())['files']))
            (root/'rouge/node_catalog.py').write_text('# unrelated reviewed source change','utf8')
            with patch.object(model,'ROOT',root):
                self.assertIsNotNone(model.packet());p=root/model.DATA;raw=p.read_bytes();p.write_bytes(raw+b' ');self.assertIsNone(model.packet());p.write_bytes(raw);self.assertIsNotNone(model.packet())
    def test_migrated_derived_rows_are_identical_except_the_new_data_source_binding(self):
        import json
        from rouge import current_event_resources as resources,current_event_item_uses as uses
        root=Path(__file__).resolve().parents[1]
        for model,path,field in((resources,'rouge/data/current-event-resources.json','directory_source_identity'),(uses,'rouge/data/current-event-item-uses.json','source_directory_identity')):
            old=json.loads((root/path).read_bytes());new=model.packet()['data'];self.assertEqual({k:v for k,v in old.items()if k!=field},{k:v for k,v in new.items()if k!=field})

if __name__=='__main__':unittest.main()
