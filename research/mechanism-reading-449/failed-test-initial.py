"""Player topic navigation, exact original prose, and stable native reading state."""
from importlib import import_module
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from rouge import battle_enemy_readers as readers
from rouge.mechanism_reading import MechanismTextBrowser, replace_mechanism_text


class MechanismReadingTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.qt=QApplication.instance() or QApplication([])

 def test_plain_text_and_chinese_heading_format_do_not_parse_markup(self):
  w=MechanismTextBrowser();self.addCleanup(w.deleteLater)
  text='第一行😀\n正文 <b>不会解析</b>\n【条件与效果】\n完整原文'
  w.setPlainText(text);self.assertEqual(w.toPlainText(),text)
  for i,bold in enumerate((True,False,True,False)):
   block=w.document().findBlockByNumber(i);cursor=QTextCursor(block)
   cursor.movePosition(QTextCursor.MoveOperation.NextCharacter,QTextCursor.MoveMode.KeepAnchor)
   self.assertEqual(cursor.charFormat().fontWeight(),QFont.Weight.Bold if bold else QFont.Weight.Normal)
   self.assertFalse(cursor.charFormat().anchorHref())

 def test_changed_unicode_topic_and_empty_document_finish_without_losing_text(self):
  w=MechanismTextBrowser();self.addCleanup(w.deleteLater);w.resize(360,180);w.show()
  prefix='说明😀\n'+'保留的完整说明\n'*50
  w.setPlainText(prefix+'【旧主题】\n旧说明')
  text=prefix+'【新主题】\n'+'新的说明\n'*30
  replace_mechanism_text(w,text,preserve=False,follow_change=True);self.qt.processEvents()
  self.assertEqual(w.toPlainText(),text);self.assertEqual(w.textCursor().block().text(),'【新主题】')
  self.assertTrue(w.viewport().rect().intersects(w.cursorRect()));self.assertGreater(w.verticalScrollBar().value(),0)
  for text in ('', '说明😀\n'):
   replace_mechanism_text(w,text,preserve=False,follow_change=True);self.assertEqual(w.toPlainText(),text)

 def test_seven_real_topic_choices_reveal_their_own_section_and_keep_refresh_reading(self):
  expected={'hanko':'【完整文献参考 · 闪现】','elbert':'【闪现】','sun_boss':'【文献中的信仰、状态与阶段】','boss_documents':'【第一形态】','guest_knights':'【另一位离场时的强化】','guest_crystals':'【捕杀另一晶兽】','guest_material':'【屏障与隐匿条件】'}
  for name,spec in readers._READERS.items():
   model=import_module('rouge.'+spec.provider);sid=model.STAGES[0];ref=model.reference(sid);row=(ref.get('rows')or ref.get('entities'))[0];key=row['enemy_key'] if name=='boss_documents' else row['key']
   view=import_module('rouge.'+spec.provider.removesuffix('_reference')+'_view');d=getattr(view,spec.dialog)(sid,key);self.addCleanup(d.deleteLater);d.show();QTest.qWait(20);p=d.panel
   index=p.topic.findData('blink') if name in ('hanko','elbert') else p.topic.findData('faith') if name=='sun_boss' else 1
   p.topic.setFocus();QTest.keyClick(p.topic,Qt.Key.Key_Home)
   for _ in range(index):QTest.keyClick(p.topic,Qt.Key.Key_Down)
   self.qt.processEvents();self.assertEqual(p.player.textCursor().block().text(),expected[name],name)
   self.assertTrue(p.player.viewport().rect().intersects(p.player.cursorRect()),name)
   self.assertEqual(p.reading_header.scope.toggleButton().text(),'+ 固定机制资料 · 非本局实况')
   self.assertEqual(p.tabs.tabText(1),'原始资料（调试）')
   cursor=p.player.textCursor();cursor.movePosition(QTextCursor.MoveOperation.NextCharacter,QTextCursor.MoveMode.KeepAnchor);p.player.setTextCursor(cursor)
   before=(p.player.toPlainText(),p.technical.toPlainText(),p.topic.currentData(),cursor.selectedText(),p.player.verticalScrollBar().value())
   QTest.mouseClick(p.refresh_button,Qt.MouseButton.LeftButton);self.qt.processEvents()
   self.assertEqual((p.player.toPlainText(),p.technical.toPlainText(),p.topic.currentData(),p.player.textCursor().selectedText(),p.player.verticalScrollBar().value()),before,name);d.reject()

 def test_sun_skill_card_keyboard_choice_reveals_exact_complete_card(self):
  from rouge import current_sun_boss as model
  from rouge.current_sun_boss_view import CurrentSunBossDialog
  ref=model.reference(model.STAGES[0]);key=ref['entities'][0]['key'];d=CurrentSunBossDialog(model.STAGES[0],key);self.addCleanup(d.deleteLater);d.show();QTest.qWait(20);p=d.panel
  p.topic.setCurrentIndex(p.topic.findData('skills'));self.qt.processEvents();self.assertGreater(p.card.count(),1)
  p.card.setFocus();QTest.keyClick(p.card,Qt.Key.Key_Home);QTest.keyClick(p.card,Qt.Key.Key_Down);self.qt.processEvents()
  selected=model.card(p.result,key,p.card.currentData())
  self.assertEqual(p.player.textCursor().block().text(),'【完整文献原项 · '+selected['title']+'】')
  self.assertEqual(p.player.toPlainText(),model.player_text(p.result,key,'skills',p.card.currentData()))
  self.assertTrue(p.player.viewport().rect().intersects(p.player.cursorRect()));d.reject()
