import unittest
from PySide6.QtWidgets import QApplication,QMainWindow,QWidget,QPlainTextEdit,QPushButton
from PySide6.QtGui import QTextCursor
from rouge.player_workspace import PlayerWorkspace
from rouge.player_reference_window import ReferenceWindow,ToolPage,NotesPage
from rouge.player_compact import CompactAssistant

class Harness(QWidget):
 open_full=CompactAssistant.open_full
 open_operators=CompactAssistant.open_operators
 open_chat=CompactAssistant.open_chat
 def __init__(self):
  super().__init__();self.owner=QMainWindow();self.owner.diagnostic_layout=False;self.owner.workspace=PlayerWorkspace();self.owner.setCentralWidget(self.owner.workspace);self.workspace_popup=None;self.reference_window=ReferenceWindow(self);self.active_popup=None
 def present(self,p):
  shown=self.reference_window.present(p)
  if shown:self.active_popup=p
  return shown

class WorkspaceReaderTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.app=QApplication.instance()or QApplication([])
 def setUp(self):
  self.c=Harness();self.ws=self.c.owner.workspace;self.a=QPlainTextEdit('培养与技能');self.b=QPlainTextEdit('关卡目标');self.chat=QPlainTextEdit('暂存的问题');self.ws.addTab(self.a,'伤害测试');self.ws.addTab(self.b,'战斗计算参考');self.ws.addTab(self.chat,'聊天分析');self.c.owner.chat_page=self.chat;self.addCleanup(self.c.owner.close);self.addCleanup(self.c.close);self.addCleanup(self.c.reference_window.close)
 def test_one_original_workspace_transfers_into_reference_host(self):
  self.assertIs(self.c.owner.centralWidget(),self.ws);self.assertTrue(self.c.open_full());page=self.c.workspace_popup;self.assertIs(page.panel,self.ws);self.assertIs(page.body_scroll.widget(),self.ws);self.assertIsNone(self.c.owner.centralWidget());self.assertFalse(self.c.owner.isVisible());self.assertIs(self.c.reference_window.pages.currentWidget(),page)
  for _ in range(3):self.assertTrue(self.c.open_full());self.assertIs(self.c.workspace_popup,page)
 def test_operator_and_chat_shortcuts_retain_child_selection_and_draft(self):
  self.ws.setCurrentWidget(self.b);self.assertTrue(self.c.open_chat());self.assertIs(self.ws.currentWidget(),self.chat);self.chat.setPlainText('保留这个问题');self.assertTrue(self.c.open_operators());self.assertIs(self.ws.currentWidget(),self.b);self.assertTrue(self.c.open_chat());self.assertEqual(self.chat.toPlainText(),'保留这个问题')
 def test_exact_workspace_alias_and_group_navigation_work_after_transfer(self):
  m,n=QWidget(),QWidget();self.ws.addTab(m,'地图预览');self.ws.addTab(n,'本图节点');self.ws.combine_map_and_node(m,n);self.c.open_full(n);self.assertIs(self.ws.currentWidget(),n);self.assertTrue(self.c.open_full(m));self.assertIs(self.ws.currentWidget(),m);self.assertTrue(self.c.open_operators());self.assertIs(self.ws.currentWidget(),self.a)
 def test_same_page_reopen_and_host_back_forward_keep_reading(self):
  self.c.open_operators();host=self.c.reference_window;page=self.c.workspace_popup;cursor=self.a.textCursor();cursor.setPosition(1);cursor.setPosition(4,QTextCursor.MoveMode.KeepAnchor);self.a.setTextCursor(cursor);other=ToolPage('资料',QWidget(),self.c,object_name='mapReferenceWindow');self.c.present(other);host.navigate(host.cursor-1);self.assertIs(host.pages.currentWidget(),page);self.assertIs(self.ws.currentWidget(),self.a);self.assertEqual(self.a.textCursor().selectedText(),'养与技');host.close();self.assertTrue(self.c.open_operators());self.assertIs(self.c.workspace_popup,page)
 def test_unsaved_notes_veto_before_workspace_routing(self):
  self.ws.setCurrentWidget(self.b);editor=QWidget();editor.finish_edit=lambda:False;note=NotesPage('笔记',editor,self.c);note.panel=editor;self.c.present(note);self.assertFalse(self.c.open_chat());self.assertIs(self.c.reference_window.pages.currentWidget(),note);self.assertIs(self.ws.currentWidget(),self.b);editor.finish_edit=lambda:True
 def test_workspace_previous_column_button_uses_existing_history(self):
  self.c.open_operators();self.c.open_chat();button=next(b for b in self.c.workspace_popup.header.findChildren(QPushButton)if b.text()=='上一栏目');self.assertTrue(button.isEnabled());button.click();self.assertIs(self.ws.currentWidget(),self.a)
 def test_explicit_diagnostic_layout_keeps_main_window_route(self):
  self.c.owner.diagnostic_layout=True;self.assertTrue(self.c.open_full(self.chat));self.assertIsNone(self.c.workspace_popup);self.assertIs(self.c.owner.centralWidget(),self.ws);self.assertTrue(self.c.owner.isVisible());self.assertIs(self.ws.currentWidget(),self.chat)

if __name__=='__main__':unittest.main()
