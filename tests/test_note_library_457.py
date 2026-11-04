from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace,MethodType
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication,QWidget,QPushButton
from rouge.player_note_library import NoteLibrary,NoteLibraryPanel
from rouge.player_notes import NotesDialog,content_key
from rouge.player_reference_window import ReferenceWindow,ToolPage
from rouge.player_compact import CompactAssistant
from rouge.run_state import RunState


class LibraryPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def setUp(self):
        self.temp=TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.path=Path(self.temp.name)
        self.editor=NotesDialog(self.path/'notes');self.editor.autosave.setChecked(False)
        self.owner=QWidget();self.owner.owner=SimpleNamespace(player_notes=self.editor,run=RunState(self.path/'run.json'))
        self.owner.reference_window=self.host=ReferenceWindow(self.owner);self.owner.present=self.host.present;self.owner.refresh=lambda:None
        self.owner.note_library=None;self.owner.note_library_page=None;self.owner.recent_notes_popup=None
        for name in ['open_note_library','notes_popup','open_saved_note']:
            setattr(self.owner,name,MethodType(getattr(CompactAssistant,name),self.owner))
        self.context={'kind':'battle','title':'公开笔记甲','variant_id':'public-test-a'}
        self.other={'kind':'battle','title':'公开笔记乙','variant_id':'public-test-b'}
        self.save(self.context,'\n'.join('机关提醒'+str(i)for i in range(120)))
        self.save(self.other,'第二条笔记')
        self.addCleanup(self.cleanup)
    def cleanup(self):
        self.editor.dirty=False;self.editor.autosave_timer.stop();self.host.close();self.owner.close();self.owner.deleteLater();self.qt.processEvents()
    def save(self,context,text):
        store=self.editor.store;key=content_key(context);store.save(key,text,store.read(key)[1]);NoteLibrary(store.folder).record(context)
    def select(self,title):
        p=self.owner.note_library
        p.entries.setCurrentRow(next(i for i in range(p.entries.count())if p.entries.item(i).text()==title))
    def test_shared_library_scans_once_and_back_keeps_search_selection_reading_and_split(self):
        base=ToolPage('地图',QWidget(),self.owner);self.host.present(base);self.qt.processEvents();handle=int(self.host.winId())
        with patch.object(NoteLibrary,'rows',autospec=True,side_effect=NoteLibrary.rows)as scan:
            self.assertTrue(self.owner.open_note_library());self.qt.processEvents();self.assertEqual(scan.call_count,1)
        p=self.owner.note_library;page=self.owner.note_library_page
        self.assertIsInstance(p,NoteLibraryPanel);self.assertFalse(p.isWindow());self.assertIs(p.window(),self.host);self.assertEqual(int(self.host.winId()),handle)
        p.search.setText('机关');p.refresh();self.select(self.context['title']);self.qt.processEvents()
        p.detail.verticalScrollBar().setValue(25);offset=p.detail.verticalScrollBar().value();self.assertGreater(offset,0);p.split.setSizes([220,500]);sizes=p.split.sizes()
        self.host.navigate(self.host.cursor-1);self.assertIs(self.host.pages.currentWidget(),base)
        self.assertTrue(self.owner.open_note_library());self.qt.processEvents();self.assertIs(self.host.pages.currentWidget(),page)
        self.assertEqual(p.search.text(),'机关');self.assertEqual(p.entries.currentItem().text(),self.context['title']);self.assertEqual(p.detail.verticalScrollBar().value(),offset);self.assertEqual(p.split.sizes(),sizes)
        self.assertEqual(p.notice.text(),'共1条笔记')
    def test_directory_button_and_unsaved_veto_keep_the_real_editor(self):
        self.assertTrue(self.owner.open_saved_note(self.context,allow_archived=True));self.qt.processEvents();note=self.owner.recent_notes_popup
        button=next(x for x in note.header.findChildren(QPushButton)if x.text()=='笔记目录');self.assertTrue(button.isVisible());button.click();self.qt.processEvents()
        self.assertIs(self.host.pages.currentWidget(),self.owner.note_library_page);self.select(self.context['title']);self.owner.note_library.open_button.click();self.qt.processEvents()
        self.assertIs(self.host.pages.currentWidget(),note);self.assertEqual(self.editor.key,content_key(self.context))
        self.editor.editor.insertPlainText('未保存草稿');self.assertTrue(self.editor.dirty);history=list(self.host.history)
        self.assertFalse(self.owner.open_note_library());self.assertIs(self.host.pages.currentWidget(),note);self.assertEqual(self.host.history,history);self.assertTrue(self.editor.dirty);self.assertIn('未保存草稿',self.editor.editor.toPlainText())
    def test_saved_file_removal_clears_preview_and_actions(self):
        self.owner.open_note_library();self.select(self.context['title']);p=self.owner.note_library;self.assertTrue(p.open_button.isEnabled())
        self.editor.store.path(content_key(self.context)).unlink();self.owner.open_note_library()
        self.assertIsNone(p.entries.currentItem());self.assertEqual(p.detail.toPlainText(),'选择一条本机笔记。');self.assertFalse(p.open_button.isEnabled());self.assertFalse(p.reference_button.isEnabled())
    def test_search_return_only_refreshes_after_an_action_had_focus(self):
        self.owner.open_note_library();self.select(self.context['title']);p=self.owner.note_library
        p.open_button.setFocus();self.qt.processEvents();p.search.setFocus();QTest.keyClick(p.search,Qt.Key.Key_Return);self.qt.processEvents()
        self.assertIs(self.host.pages.currentWidget(),self.owner.note_library_page);self.assertIsNone(self.owner.recent_notes_popup)
    def test_read_failure_keeps_cause_visible_and_files_unchanged(self):
        self.owner.open_note_library();p=self.owner.note_library;before={v.name:v.read_bytes()for v in self.editor.store.folder.iterdir()}
        with patch.object(p.library,'rows',side_effect=OSError('测试：目录拒绝访问')):self.assertTrue(self.owner.open_note_library())
        self.assertEqual(p.notice.text(),'测试：目录拒绝访问');self.assertEqual(p.entries.count(),0);self.assertFalse(p.open_button.isEnabled());self.assertEqual(before,{v.name:v.read_bytes()for v in self.editor.store.folder.iterdir()})
    def test_same_name_saved_stages_show_existing_canonical_mode_labels(self):
        from rouge.player_reference_notes import note_for
        from rouge.player_note_selector import catalogue_snapshot
        contexts=[note_for('stages',sid)for sid in ['ro6_n_1_2','ro6_e_1_2']]
        for c in contexts:self.save(c,'作战提醒')
        self.owner.open_note_library();p=self.owner.note_library
        labels={r['context']['event_id']:r['label']for r in catalogue_snapshot()['rows']if r['context'].get('event_id')in [c['event_id']for c in contexts]}
        visible=[p.entries.item(i).text()for i,r in enumerate(p.rows)if r['content']in contexts]
        self.assertEqual(set(visible),set(labels.values()));self.assertEqual(len(set(visible)),2)
        with patch('rouge.player_note_selector.catalogue_snapshot',return_value={'rows':[],'unavailable':['固定资料']}):p.refresh()
        self.assertEqual([p.entries.item(i).text()for i,r in enumerate(p.rows)if r['content']in contexts],[c['title']for c in contexts])


if __name__=='__main__':unittest.main()
