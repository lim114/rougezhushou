from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch,Mock
import importlib,json,unittest
from PySide6.QtWidgets import QApplication,QWidget
from PySide6.QtCore import Qt
from tests import test_note_library_457 as library_tests
from rouge.player_reference_notes import note_for,open_reference
from rouge.player_reference_window import ReferenceWindow,ToolPage
from rouge import documented_readers as flows


class NoteReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):library_tests.LibraryPageTests.setUpClass();cls.qt=library_tests.LibraryPageTests.qt
    def setUp(self):
        self.fixture=library_tests.LibraryPageTests();self.fixture.setUp();self.addCleanup(self.fixture.doCleanups)
        self.c=self.fixture.owner;self.host=self.fixture.host;self.notes=self.fixture.editor
        self.window=QWidget();self.addCleanup(self.window.close);self.window.player_notes=self.notes;self.window.compact_window=self.c;self.window.run=self.c.owner.run;self.c.owner=self.window
        self.window.reference_panel=Mock(side_effect=AssertionError('Shared references must stay in the player host'))
        self.notes.openReference.connect(lambda content:open_reference(self.window,content))
        self.normal=note_for('stages','ro6_n_1_2');self.elite=note_for('stages','ro6_e_1_2');self.scene=note_for('scenes','scene_ro6_normal2_enter')
        for context in (self.normal,self.elite,self.scene):self.fixture.save(context,'\n'.join('公开笔记'+str(i)for i in range(80)))
    def library(self,content):
        self.c.open_note_library();p=self.c.note_library
        p.entries.setCurrentRow(next(i for i,r in enumerate(p.rows)if r['content']==content));return p
    def test_library_opens_exact_stage_and_retains_reading_on_back(self):
        p=self.library(self.elite);self.qt.processEvents();handle=int(self.host.winId());p.detail.verticalScrollBar().setValue(20);offset=p.detail.verticalScrollBar().value()
        self.assertTrue(open_reference(self.window,self.elite));page=self.host.pages.currentWidget();self.assertEqual(page.panel.stage_id,'ro6_e_1_2');self.assertIs(page.source_parent,self.c.note_library_page);self.assertEqual(int(self.host.winId()),handle)
        self.host.navigate(self.host.cursor-1);self.qt.processEvents();self.assertEqual(p.detail.verticalScrollBar().value(),offset)
        self.assertTrue(open_reference(self.window,self.elite));self.assertIs(self.host.pages.currentWidget(),page);self.window.reference_panel.assert_not_called()
    def test_scene_opens_exact_complete_event_directly(self):
        self.library(self.scene);self.assertTrue(open_reference(self.window,self.scene));page=self.host.pages.currentWidget();p=page.panel
        self.assertEqual(p.scene_id,self.scene['event_id']);self.assertIs(page.source_parent,self.c.note_library_page);self.assertTrue(p.player.toPlainText());self.assertIs(page.window(),self.host)
    def test_scene_without_full_reader_still_shows_its_own_original(self):
        self.library(self.scene)
        with patch('rouge.documented_readers.reader_plan',return_value=None):self.assertTrue(open_reference(self.window,self.scene))
        page=self.host.pages.currentWidget();self.assertEqual(page.panel.identity,self.scene['event_id']);self.assertTrue(page.panel.text.toPlainText());self.assertEqual(page.preferred_size.height(),300)
        self.host.navigate(self.host.cursor-1);self.assertTrue(open_reference(self.window,self.scene));full=self.host.pages.currentWidget();self.assertIsNot(full,page);self.assertEqual(full.panel.scene_id,self.scene['event_id'])
    def test_changed_library_selection_removes_the_old_dependent_chain(self):
        p=self.library(self.normal);self.assertTrue(open_reference(self.window,self.normal));child=self.host.pages.currentWidget()
        p.entries.setCurrentRow(next(i for i,r in enumerate(p.rows)if r['content']==self.elite))
        self.assertFalse(self.host.present(child));self.assertNotIn(child,self.host.history);self.assertIs(self.host.pages.currentWidget(),self.c.note_library_page)
    def test_lost_source_removes_child_but_keeps_saved_note(self):
        self.library(self.scene);self.assertTrue(open_reference(self.window,self.scene));child=self.host.pages.currentWidget();files={p.name:p.read_bytes()for p in self.notes.store.folder.iterdir()}
        with patch('rouge.player_reference_notes.model.packet',return_value=None):self.assertFalse(self.host.present(child))
        self.assertNotIn(child,self.host.history);self.assertIs(self.host.pages.currentWidget(),self.c.note_library_page);self.assertEqual(files,{p.name:p.read_bytes()for p in self.notes.store.folder.iterdir()})
    def test_preview_reference_follows_reading_instead_of_cached_editor(self):
        self.assertTrue(self.c.open_saved_note(self.normal));p=self.c.recent_notes_popup.panel;p.request_edit();self.assertIs(p.stack.currentWidget(),p.preview)
        p.select_context(self.elite);p.refresh(force=True);p.more.setChecked(True);self.qt.processEvents();self.assertEqual(self.notes.content,self.normal);self.assertEqual(p.reference_context(),self.elite);self.assertTrue(self.notes.reference_button.isVisible())
        self.notes.reference_button.click();self.qt.processEvents();self.assertEqual(self.host.pages.currentWidget().panel.stage_id,'ro6_e_1_2');self.assertEqual(self.notes.content,self.normal)
    def test_dirty_note_stays_in_editor_until_saved(self):
        self.c.open_saved_note(self.normal);self.notes.editor.insertPlainText('未保存内容');note=self.c.recent_notes_popup;history=list(self.host.history)
        self.assertFalse(open_reference(self.window,self.normal));self.assertIs(self.host.pages.currentWidget(),note);self.assertEqual(self.host.history,history);self.assertTrue(self.notes.dirty);self.assertIn('未保存内容',self.notes.editor.toPlainText())
        self.assertTrue(self.notes.save());self.assertTrue(open_reference(self.window,self.normal));self.assertEqual(self.host.pages.currentWidget().panel.stage_id,'ro6_n_1_2')
    def test_wrong_version_same_name_does_not_open_a_substitute(self):
        self.library(self.normal);bad={**self.normal,'variant_id':'different-version'};history=list(self.host.history)
        self.assertFalse(open_reference(self.window,bad));self.assertEqual(self.host.history,history);self.window.reference_panel.assert_not_called()


class DocumentedReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def test_all_preserved_reader_constructors_match_standalone_panels(self):
        data=json.loads((Path(__file__).resolve().parents[1]/'research/note-references-458/reader-fixtures.json').read_bytes());self.assertEqual(len(data['cases']),22)
        self.owner=owner=QWidget();owner.reference_window=ReferenceWindow(owner);self.addCleanup(owner.reference_window.close);self.addCleanup(owner.close)
        for case in data['cases']:
            with self.subTest(reader=case['class']):
                plan=(case['view'],case['class'],tuple(case['args']));original=getattr(importlib.import_module('rouge.'+case['view']),case['class'])(*case['args'])
                page=flows.make_flow_reader(plan,page_owner=owner);self.assertIsNotNone(page);self.assertEqual(page.panel.result,original.panel.result);self.assertEqual((page.panel.scene_id,page.panel.choice_id),(original.panel.scene_id,original.panel.choice_id));self.assertFalse(page.isWindow());page.close();page.deleteLater();original.close();original.deleteLater();self.qt.processEvents()
    def test_existing_locator_order_and_fallbacks_resolve_original_inputs(self):
        data=json.loads((Path(__file__).resolve().parents[1]/'research/note-references-458/reader-fixtures.json').read_bytes())
        for case in data['cases']:
            with self.subTest(reader=case['class']):
                plan=flows.reader_plan(case['category'],case['identity']);self.assertIsNotNone(plan);self.assertEqual(plan[:2],(case['view'],case['class']));self.assertEqual(list(plan[2]),case['args'])
    def test_workspace_entry_still_opens_each_existing_reader(self):
        from rouge.expansion_view import ExpansionUpdatePanel
        from rouge import expansion_reference as model
        from PySide6.QtWidgets import QPushButton
        self.proxy=proxy=QWidget();proxy.flow_dialog=None;proxy.flow_button=QPushButton();proxy._close_flow=lambda:ExpansionUpdatePanel._close_flow(proxy);proxy._unavailable=Mock()
        data=json.loads((Path(__file__).resolve().parents[1]/'research/note-references-458/reader-fixtures.json').read_bytes())
        for case in data['cases']:
            with self.subTest(reader=case['class']):
                proxy.result=model.detail(case['category'],case['identity']);self.assertTrue(ExpansionUpdatePanel.open_documented_flow(proxy));self.assertEqual(type(proxy.flow_dialog).__name__,case['class']);self.assertIsNotNone(proxy.flow_dialog.panel.result);self.assertTrue(proxy.flow_dialog.isVisible());proxy.flow_dialog.close();proxy.flow_dialog.deleteLater();proxy.flow_dialog=None;self.qt.processEvents()
        proxy.close();proxy.deleteLater()


if __name__=='__main__':unittest.main()
