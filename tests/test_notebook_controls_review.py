"""Notebook controls cannot consume the real text viewport or replace the draft."""
from copy import deepcopy
import unittest
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt
from tests import test_notebook_layout_review as notebook
from rouge.player_notes import content_key
from rouge.flow_layout import FlowLayout

class NotebookControlsReview(unittest.TestCase):
 @classmethod
 def setUpClass(cls):notebook.NotebookLayoutReviewTests.setUpClass()
 def make(self):
  f=notebook.NotebookLayoutReviewTests();f.setUp();self.addCleanup(f.doCleanups);return f,f.panel,f.editor
 def open_manual(self):
  f,p,e=self.make();e.autosave.setChecked(False);f.click_body();e.editor.setPlainText('# 第一层\n\n- 注意机制。\n- 保留这份草稿。');p.more.setChecked(True);QTest.qWait(30);f.qt.processEvents();return f,p,e
 def test_actions_are_the_original_real_widgets_in_external_flow(self):
  f,p,e=self.open_manual();self.assertIsInstance(p.option_flow,FlowLayout);self.assertIs(p.options_scroll.widget(),p.options);self.assertEqual({p.option_flow.itemAt(i).widget()for i in range(p.option_flow.count())},{p.edit,p.follow,p.reload,e.autosave,e.save_button,e.discard_button,e.reference_button,e.export_button});self.assertTrue(p.options_scroll.isVisible())
 def test_expanded_controls_keep_four_real_lines_at_actual_widths(self):
  f,p,e=self.open_manual();text=e.editor.toPlainText();cursor=e.editor.textCursor();cursor.setPosition(2);cursor.setPosition(5,cursor.MoveMode.KeepAnchor);e.editor.setTextCursor(cursor)
  for width in (480,640,900,1200):
   p.resize(width,420);QTest.qWait(40);p.fit_content();f.qt.processEvents();self.assertGreaterEqual(e.editor.viewport().height(),4*e.editor.fontMetrics().lineSpacing());self.assertLessEqual(p.card.geometry().bottom(),p.height());self.assertEqual(e.editor.toPlainText(),text);self.assertEqual(e.editor.textCursor().selectedText(),text[2:5]);self.assertLessEqual(p.options_scroll.height(),4*p.reload.sizeHint().height())
 def test_matching_owner_is_not_repeated_inside_edit_card(self):
  f,p,e=self.open_manual();self.assertFalse(e.context.isVisible());self.assertIs(e.context.parentWidget(),p);self.assertTrue(all(e.layout().itemAt(i).widget()is not e.context for i in range(e.layout().count())));self.assertEqual(p.card_title.text(),f.content['title']);self.assertEqual(e.key,content_key(f.content))
 def test_other_owner_warning_is_visible_outside_editor_and_options(self):
  f,p,e=self.open_manual();owner=e.key;text=e.editor.toPlainText();p.run.state['last_node_content']={'kind':'battle','title':'另一关','variant_id':'other'};p.follow.setChecked(True);p.refresh(force=True);QTest.qWait(30);p.more.setChecked(False);f.qt.processEvents();self.assertTrue(e.context.isVisible());self.assertIn(f.content['title'],e.context.text());self.assertIs(e.context.parentWidget(),p);self.assertFalse(p.options_scroll.isVisible());self.assertEqual(e.key,owner);self.assertEqual(e.editor.toPlainText(),text);self.assertGreaterEqual(e.editor.viewport().height(),4*e.editor.fontMetrics().lineSpacing())
 def test_more_roundtrip_does_not_recreate_controls_or_change_draft(self):
  f,p,e=self.open_manual();before=(e.key,e.editor.toPlainText(),e.dirty,e.digest);controls=[p.option_flow.itemAt(i).widget()for i in range(p.option_flow.count())]
  for value in (False,True,False,True):p.more.setChecked(value);QTest.qWait(20);f.qt.processEvents();self.assertEqual((e.key,e.editor.toPlainText(),e.dirty,e.digest),before);self.assertEqual([p.option_flow.itemAt(i).widget()for i in range(p.option_flow.count())],controls)
 def test_original_save_action_remains_reachable_inside_options_scroll(self):
  f,p,e=self.open_manual();p.options_scroll.ensureWidgetVisible(e.save_button);f.qt.processEvents();QTest.mouseClick(e.save_button,Qt.MouseButton.LeftButton);f.qt.processEvents();self.assertFalse(e.dirty);self.assertEqual(e.store.read(e.key)[0],e.editor.toPlainText());self.assertEqual(p.save_state.text(),'已保存')
 def test_save_conflict_reason_stays_visible_even_when_options_collapse(self):
  f,p,e=self.open_manual();text=e.editor.toPlainText();e.store.folder.mkdir(exist_ok=True);e.store.path(e.key).write_text('外部保存原文','utf8');e.save_button.click();reason=e.status.text();self.assertIn('本次未覆盖',reason);p.more.setChecked(False);f.qt.processEvents();self.assertTrue(e.status.isVisible());self.assertEqual(e.status.text(),reason);self.assertEqual(e.editor.toPlainText(),text);self.assertEqual(e.store.read(e.key)[0],'外部保存原文');self.assertTrue(e.dirty)
 def test_long_note_scrolls_without_truncating_text_and_collapse_keeps_selection(self):
  f,p,e=self.open_manual();text='\n'.join('第'+str(i)+'条机制提醒'for i in range(80));e.editor.setPlainText(text);QTest.qWait(30);f.qt.processEvents();self.assertGreater(e.editor.verticalScrollBar().maximum(),0);e.editor.verticalScrollBar().setValue(15);before=(e.editor.textCursor().position(),e.editor.toPlainText());p.more.setChecked(False);QTest.qWait(30);f.qt.processEvents();self.assertEqual((e.editor.textCursor().position(),e.editor.toPlainText()),before);self.assertGreaterEqual(e.editor.viewport().height(),4*e.editor.fontMetrics().lineSpacing())
 def test_option_background_is_the_readable_light_surface_in_standalone_panel(self):
  f,p,e=self.open_manual();image=p.options.grab().toImage();self.assertEqual(image.pixelColor(image.width()-2,image.height()-2).name(),'#f5f5f7');self.assertEqual(p.options_scroll.viewport().objectName(),'noteOptionsViewport')
 def test_empty_parent_notice_wraps_without_reserving_a_large_blank_panel(self):
  f,p,e=self.make();e.autosave.setChecked(False);self.assertTrue(p.open_for_context({'kind':'battle','title':'无目录归属的场景','variant_id':'unmapped'}));e.editor.setPlainText('无上级目录的公开笔记');p.parent_toggle.setChecked(True);p.more.setChecked(False)
  for width in (480,900,640):
   p.resize(width,420);QTest.qWait(40);f.qt.processEvents();self.assertEqual(p.parent_views,[]);self.assertLess(p.parent_area.height(),100);self.assertGreaterEqual(p.parent_area.height(),p.parent_layout.totalHeightForWidth(p.parent_area.viewport().width()));self.assertGreaterEqual(e.editor.viewport().height(),4*e.editor.fontMetrics().lineSpacing())
 def test_real_parent_notes_keep_reading_and_scroll_in_bounded_area(self):
  from rouge.player_note_scopes import scope
  f,p,e=self.make();rows=p.selector.rows;parent=scope(rows);e.store.save(content_key(parent),'# 通用提醒\n\n'+'很多行机制提醒\n'*60,e.store.read(content_key(parent))[1]);p.parent_toggle.setChecked(True);QTest.qWait(40);f.qt.processEvents();self.assertTrue(p.parent_views);self.assertLessEqual(p.parent_area.height(),200);self.assertGreater(p.parent_area.verticalScrollBar().maximum(),0);self.assertIn('很多行机制提醒',p.parent_views[0].toPlainText())
if __name__=='__main__':unittest.main()
