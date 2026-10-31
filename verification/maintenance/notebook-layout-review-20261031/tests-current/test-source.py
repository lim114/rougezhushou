"""Video notebook interactions reuse the original editor, store and safeguards."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from copy import deepcopy
import unittest
from PySide6.QtCore import Qt,QPoint
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from rouge.run_state import RunState
from rouge.player_notes import NotesDialog,content_key
from rouge.player_inline_notes import InlineNotesPanel
from rouge.player_note_scopes import scope
from tests import test_inline_notebook_review as old_tests


class NotebookLayoutReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def setUp(self):
        root=Path(self.enterContext(TemporaryDirectory(prefix='rouge-notebook-layout-')))
        rows=old_tests.rows();self.enterContext(patch('rouge.player_note_selector.catalogue_snapshot',return_value={'rows':rows,'unavailable':[]}))
        self.run=RunState(root/'run.json');self.editor=NotesDialog(root/'notes')
        self.panel=InlineNotesPanel(self.run,self.editor);self.panel.resize(900,360);self.panel.show();self.qt.processEvents()
        self.content=scope(rows,'floor1');self.panel.select_context(self.content)
        self.addCleanup(self.cleanup)
    def cleanup(self):
        self.panel.leave_timer.stop();self.panel.timer.stop();self.editor.discard();self.editor.autosave_timer.stop()
        self.panel.close();self.panel.deleteLater();self.qt.processEvents()
    def click_body(self):
        QTest.mouseClick(self.panel.preview.viewport(),Qt.MouseButton.LeftButton,pos=QPoint(10,10));self.qt.processEvents()
        self.assertIs(self.panel.stack.currentWidget(),self.editor)
        self.assertIs(self.editor.store,self.panel.store)
    def blur(self):
        self.panel.selector.floor.setFocus();self.editor.editor.clearFocus();self.panel.leave_editor();self.qt.processEvents()

    def test_default_surface_reuses_actions_but_does_not_reserve_footer_rows(self):
        p=self.panel
        self.assertFalse(p.options.isVisible());self.assertFalse(self.editor.pages.tabBar().isVisible())
        self.assertLess(p.card.height(),p.height()-p.card.y())
        self.assertEqual(p.card_title.text(),self.content['title'])
        self.assertEqual(p.save_state.text(),'自动保存')
        p.more.click();self.qt.processEvents()
        self.assertTrue(p.options.isVisible())
        for widget in (p.follow,p.reload,p.edit,self.editor.autosave,self.editor.save_button,self.editor.discard_button,self.editor.export_button):
            self.assertTrue(widget.isVisible(),widget.text())

    def test_direct_click_edits_and_blur_saves_same_identity_then_renders_markdown(self):
        state=deepcopy(self.run.state);self.click_body();self.editor.editor.setPlainText('# 第一层\n\n- 注意关卡机制。')
        self.blur()
        self.assertIs(self.panel.stack.currentWidget(),self.panel.preview)
        self.assertFalse(self.editor.dirty);self.assertEqual(self.editor.key,content_key(self.content))
        self.assertEqual(self.editor.store.read(self.editor.key)[0],'# 第一层\n\n- 注意关卡机制。')
        self.assertIn('注意关卡机制',self.panel.preview.toPlainText());self.assertEqual(self.run.state,state)
        self.assertEqual(self.panel.save_state.text(),'已保存')

    def test_manual_draft_is_not_saved_or_hidden_on_blur(self):
        self.editor.autosave.setChecked(False);self.click_body();self.editor.editor.setPlainText('手动草稿')
        self.blur()
        self.assertIs(self.panel.stack.currentWidget(),self.editor);self.assertTrue(self.editor.dirty)
        self.assertFalse(self.editor.store.path(self.editor.key).exists())
        self.assertEqual(self.panel.save_state.text(),'未保存')
        self.panel.more.click();self.editor.save_button.click();self.panel.refresh(force=True)
        self.assertFalse(self.editor.dirty);self.assertEqual(self.editor.store.read(self.editor.key)[0],'手动草稿')

    def test_external_conflict_remains_visible_and_never_overwrites_either_copy(self):
        self.click_body();self.editor.editor.setPlainText('当前草稿')
        self.editor.store.folder.mkdir(exist_ok=True);self.editor.store.path(self.editor.key).write_text('外部版本','utf8')
        self.blur()
        self.assertIs(self.panel.stack.currentWidget(),self.editor);self.assertTrue(self.editor.dirty)
        self.assertFalse(self.editor.autosave.isChecked());self.assertTrue(self.panel.more.isChecked())
        self.assertTrue(self.panel.options.isVisible());self.assertEqual(self.editor.editor.toPlainText(),'当前草稿')
        self.assertEqual(self.editor.store.read(self.editor.key)[0],'外部版本')

    def test_clicking_external_link_remains_blocked_instead_of_entering_editor(self):
        p=self.panel;p.preview.read_markdown('[外部链接](https://example.invalid/no-request)');self.qt.processEvents()
        position=next(QPoint(x,y)for y in range(3,65,3)for x in range(3,250,3)if p.preview.anchorAt(QPoint(x,y)))
        calls=[];p.preview.linkBlocked.connect(lambda:calls.append(True))
        QTest.mouseClick(p.preview.viewport(),Qt.MouseButton.LeftButton,pos=position);self.qt.processEvents()
        self.assertEqual(calls,[True]);self.assertIs(p.stack.currentWidget(),p.preview)

    def test_keyboard_editing_and_long_note_resize_keep_current_text_and_selection(self):
        p=self.panel;p.preview.setFocus();QTest.keyClick(p.preview,Qt.Key.Key_F2);self.qt.processEvents()
        self.assertIs(p.stack.currentWidget(),self.editor)
        text='\n'.join('第'+str(i)+'条测试记录'for i in range(90));self.editor.editor.setPlainText(text)
        cursor=self.editor.editor.textCursor();cursor.setPosition(7);self.editor.editor.setTextCursor(cursor)
        for size in [(1100,450),(720,420),(900,360)]:
            p.resize(*size);self.qt.processEvents();p.fit_content()
            self.assertEqual(self.editor.editor.toPlainText(),text);self.assertEqual(self.editor.editor.textCursor().position(),7)
            self.assertLessEqual(p.card.geometry().bottom(),p.height())
        self.blur();self.assertGreater(p.preview.verticalScrollBar().maximum(),0)

    def test_separate_editor_keeps_its_original_controls_and_storage_contract(self):
        with TemporaryDirectory(prefix='rouge-standalone-note-')as root:
            editor=NotesDialog(Path(root));editor.show();self.qt.processEvents()
            self.assertTrue(editor.pages.tabBar().isVisible());self.assertTrue(editor.autosave.isVisible())
            self.assertTrue(editor.set_context({'kind':'battle','title':'独立窗口'}))
            editor.editor.setPlainText('独立正文');self.assertTrue(editor.save());editor.close()
