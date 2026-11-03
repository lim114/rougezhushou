from pathlib import Path
from tempfile import TemporaryDirectory
from copy import deepcopy
import unittest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from tests import test_notebook_layout_review as notebook
from rouge.run_state import RunState
from rouge.player_replay import ReplayPanel
from rouge.player_replay_archive import card_text,reload_history
from rouge.relic_quantities import KETTLE,kettle_copies
from tests.test_inventory_modes_446 import observe,OTHER,TOOL
from tests.test_history_reader_review import history_example


class NotesHistoryLayoutReview(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([]);notebook.NotebookLayoutReviewTests.setUpClass()
 def note(self):
  fixture=notebook.NotebookLayoutReviewTests();fixture.setUp();self.addCleanup(fixture.doCleanups);return fixture
 def history(self):
  folder=TemporaryDirectory();self.addCleanup(folder.cleanup);r=RunState(Path(folder.name)/'run.json');p=ReplayPanel(r);p.resize(640,650);p.show();self.addCleanup(p.close);self.qt.processEvents();return p,r
 def test_short_edit_grows_with_actual_blocks_instead_of_fixed220(self):
  f=self.note();p=f.panel;e=f.editor;f.click_body();e.editor.setPlainText('短笔记');self.qt.processEvents();short=p.stack.height();self.assertLess(short,150);e.editor.setPlainText('\n'.join('第'+str(i)+'条提醒'for i in range(9)));self.qt.processEvents();self.assertGreater(p.stack.height(),short);self.assertLessEqual(p.card.geometry().bottom(),p.height());self.assertEqual(e.editor.toPlainText().count('\n'),8)
 def test_long_wrapped_paragraph_scrolls_and_preserves_exact_text_on_resize(self):
  f=self.note();p=f.panel;e=f.editor;p.resize(700,500);self.qt.processEvents();f.click_body();text='长段落提醒和机制说明，'*500;e.editor.setPlainText(text);self.qt.processEvents();self.assertGreater(e.editor.verticalScrollBar().maximum(),0);cursor=e.editor.textCursor();cursor.setPosition(40);cursor.setPosition(65,cursor.MoveMode.KeepAnchor);e.editor.setTextCursor(cursor)
  for width in(640,1100,720):
   p.resize(width,500);self.qt.processEvents();self.assertEqual(e.editor.toPlainText(),text);self.assertEqual(e.editor.textCursor().selectedText(),text[40:65]);self.assertLessEqual(p.card.geometry().bottom(),p.height())
 def test_plain_short_reading_uses_content_height_and_keeps_more_actions(self):
  f=self.note();p=f.panel;e=f.editor;f.click_body();e.editor.setPlainText('第三层是黑流树海的转折点');f.blur();self.assertIs(p.stack.currentWidget(),p.preview);self.assertLess(p.stack.height(),100);self.assertEqual(p.layout().contentsMargins().left(),2);p.more.click();self.assertTrue(e.save_button.isVisible());self.assertTrue(e.export_button.isVisible())
 def test_short_editor_has_room_for_its_actual_chrome_and_no_scrollbar(self):
  f=self.note();e=f.editor;f.click_body();e.editor.setPlainText('# 第一层\n\n- 注意关卡机制。');self.qt.processEvents();self.assertEqual(e.editor.verticalScrollBar().maximum(),0)
 def test_failed_save_reason_is_not_replaced_by_generic_unsaved_warning(self):
  f=self.note();e=f.editor;f.click_body();e.editor.setPlainText('本窗口草稿');e.store.folder.mkdir(exist_ok=True);e.store.path(e.key).write_text('外部更新原件','utf8');e.save_pending();reason=e.status.text();self.assertIn('自动保存已暂停',reason);self.assertFalse(f.panel.finish_edit());self.assertEqual(e.status.text(),reason);self.assertTrue(e.dirty);self.assertEqual(e.store.read(e.key)[0],'外部更新原件')
 def test_history_card_counts_repeated_kettles_without_mutating_state(self):
  p,r=self.history();observe(r,[KETTLE]*3+[OTHER,TOOL]);before=deepcopy(r.state);self.assertIn('已确认藏品 4 件',card_text(r.state,'当前对局'));p.refresh();self.assertIn('已确认藏品 4 件',p.session_cards.item(0).text());self.assertEqual(r.state,before)
 def test_partial_or_invalid_historical_records_cannot_supply_guessed_quantity(self):
  state={'relics':{KETTLE:{},'invalid':None},'history':[],'operators':{}};before=deepcopy(state);self.assertIsNone(kettle_copies(state));self.assertIn('已确认藏品 1 件',card_text(state,'本机历史'));self.assertEqual(state,before)
 def test_card_keeps_full_scope_in_tooltip_and_accessible_description(self):
  p,r=self.history();item=p.session_cards.item(0);self.assertEqual(len(item.text().splitlines()),3);self.assertIn('结算分数与种子尚未确认',item.toolTip());self.assertEqual(item.data(Qt.ItemDataRole.AccessibleDescriptionRole),item.toolTip());self.assertIn('归档不表示通关或完整结算',p.history_status.text());self.assertLess(p.history_scope_button.width(),200)
 def test_full_history_scope_can_expand_without_resetting_selected_map(self):
  p,r=self.history();state,t,ids=history_example();state['id']='public-layout';p.history_store.archive(state);reload_history(p);item=next(p.session_cards.item(i)for i in range(p.session_cards.count())if p.session_cards.item(i).data(Qt.ItemDataRole.UserRole)=='archive:public-layout');p.session_cards.itemClicked.emit(item);self.qt.processEvents();self.assertFalse(p.notice.isVisible());self.assertFalse(p.nodes.notice.isVisible());self.assertTrue(p.reading_label.isVisible());self.assertIn('本机历史',p.reading_label.text());node=p.nodes.view.selected;p.history_scope_button.click();self.assertTrue(p.notice.isVisible());self.assertTrue(p.nodes.notice.isVisible());p.refresh();self.assertEqual(p.nodes.view.selected,node);self.assertTrue(p.history_scope_button.isChecked())
 def test_unavailable_history_is_visible_without_expanding_scope(self):
  from unittest.mock import patch
  p,r=self.history();state,t,ids=history_example();state['id']='public-layout';p.history_store.archive(state);reload_history(p);p.sessions.setCurrentIndex(1);p.tabs.setCurrentWidget(p.nodes)
  with patch.object(p.history_store,'records',side_effect=OSError('isolated missing archive')):reload_history(p)
  self.assertFalse(p.history_scope_button.isChecked());self.assertTrue(p.reading_label.isVisible());self.assertIn('暂不可用',p.reading_label.text());self.assertIsNone(p.nodes.view.graph);self.assertFalse(p.nodes.resource_pills.rows)


if __name__=='__main__':unittest.main()
