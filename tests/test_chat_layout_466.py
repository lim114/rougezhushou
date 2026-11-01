from unittest.mock import Mock
import unittest
from PySide6.QtWidgets import QWidget,QApplication
from PySide6.QtTest import QTest
from rouge.app import MainWindow

class ChatHarness(QWidget):
 make_chat_tab=MainWindow.make_chat_tab
 chat_mode_changed=MainWindow.chat_mode_changed
 def __init__(self):
  super().__init__();self.desktop_snapshot=None;self.chat_busy=False;self.desktop_request_busy=False;self.last_chat_mode=0;self.history=[]
  for name in('save_settings','clear_chat','send_chat','cancel_chat','desktop_request','bind_desktop','desktop_state_received'):setattr(self,name,Mock(side_effect=AssertionError('no backend operation: '+name)))
  self.page=self.make_chat_tab()

class ChatLayoutTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.app=QApplication.instance()or QApplication([])
 def setUp(self):self.w=ChatHarness();self.addCleanup(self.w.page.close);self.addCleanup(self.w.close)
 def test_client_and_provider_modes_only_show_their_own_form_rows(self):
  w=self.w;w.chat_connection_fold.expand(animate=False)
  for field in(w.profile,w.base_url,w.protocol,w.model,w.key):self.assertFalse(w.chat_form.isRowVisible(field));self.assertFalse(field.isEnabled())
  self.assertTrue(w.chat_form.isRowVisible(w.desktop_threads));self.assertTrue(w.chat_form.isRowVisible(w.chat_desktop_buttons));w.mode.setCurrentIndex(1)
  for field in(w.profile,w.base_url,w.protocol,w.model,w.key):self.assertTrue(w.chat_form.isRowVisible(field));self.assertTrue(field.isEnabled())
  self.assertFalse(w.chat_form.isRowVisible(w.desktop_threads));self.assertFalse(w.chat_form.isRowVisible(w.chat_desktop_buttons))
 def test_fold_and_mode_changes_retain_unsent_draft_and_api_values(self):
  w=self.w;w.question.setPlainText('暂存问题');w.base_url.setText('https://example.invalid/v1');w.model.setText('测试模型');w.chat_connection_fold.expand(animate=False);w.mode.setCurrentIndex(1);w.chat_connection_fold.collapse(animate=False);w.mode.setCurrentIndex(0);self.assertEqual(w.question.toPlainText(),'暂存问题');self.assertEqual(w.base_url.text(),'https://example.invalid/v1');self.assertEqual(w.model.text(),'测试模型')
 def test_pending_send_rejects_mode_change_before_clearing_local_text(self):
  w=self.w;w.history.append({'role':'user','content':'保留'});w.transcript.setPlainText('已有对话');w.chat_busy=True;w.mode.setCurrentIndex(1);self.assertEqual(w.mode.currentIndex(),0);self.assertEqual(w.transcript.toPlainText(),'已有对话');self.assertEqual(len(w.history),1);self.assertFalse(w.chat_form.isRowVisible(w.base_url));self.assertTrue(w.chat_form.isRowVisible(w.desktop_threads))
 def test_expanded_settings_resize_for_provider_fields_without_overlap(self):
  w=self.w;w.page.resize(760,650);w.page.show();w.chat_connection_fold.expand(animate=False);self.app.processEvents();w.mode.setCurrentIndex(1);self.app.processEvents();QTest.qWait(30);self.app.processEvents()
  fields=(w.mode,w.profile,w.base_url,w.protocol,w.model,w.key)
  for upper,lower in zip(fields,fields[1:]):self.assertLessEqual(upper.geometry().bottom(),lower.geometry().top())
  self.assertGreaterEqual(w.chat_connection_fold.content().height(),w.chat_connection_fold.content().minimumSizeHint().height())
 def test_configuration_starts_folded_and_no_backend_is_called(self):
  w=self.w;self.assertFalse(w.chat_connection_fold.isExpanded());self.assertEqual(w.chat_connection_fold.content().maximumHeight(),0)
  for name in('save_settings','clear_chat','send_chat','cancel_chat','desktop_request','bind_desktop','desktop_state_received'):getattr(w,name).assert_not_called()

if __name__=='__main__':unittest.main()
