from pathlib import Path
from hashlib import sha256
from importlib import import_module
from unittest.mock import patch
import json,unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from rouge import battle_enemy_readers as readers

ROOT=Path(__file__).resolve().parents[1]


class MechanismReadingDensityReview(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.qt=QApplication.instance()or QApplication([]);cls.fixtures=[]
  cls.before={r['reader']:r for r in json.loads((ROOT/'verification/maintenance/mechanism-reading-density-20261101/reading-before.json').read_bytes())}
  for name,spec in readers._READERS.items():
   model=import_module('rouge.'+spec.provider);sid=model.STAGES[0];ref=model.reference(sid);row=(ref.get('rows')or ref.get('entities'))[0];key=row['enemy_key']if name=='boss_documents'else row['key'];view=import_module('rouge.'+spec.provider.removesuffix('_reference')+'_view');cls.fixtures.append((name,getattr(view,spec.dialog),sid,key))
 def dialog(self,fixture):
  _,ctor,sid,key=fixture;d=ctor(sid,key);self.addCleanup(d.deleteLater);d.show();QTest.qWait(20);return d
 def test_more_first_screen_body_without_losing_any_original_text(self):
  for f in self.fixtures:
   d=self.dialog(f);p=d.panel;old=self.before[f[0]];self.assertEqual([d.width(),d.height()],old['actual_size']);self.assertGreaterEqual(p.player.viewport().height()-old['body_height'],48,f[0]);self.assertFalse(p.notice.isVisible());self.assertEqual(p.notice.text(),old['notice'])
   for key in ('player','technical'):self.assertEqual(sha256(getattr(p,key).toPlainText().encode('utf8')).hexdigest(),old[key+'_sha256'],(f[0],key))
   d.reject()
 def test_real_keyboard_disclosure_and_refresh_preserve_reading_and_user_size(self):
  for f in self.fixtures:
   d=self.dialog(f);p=d.panel;scope=p.reading_header.scope;button=scope.toggleButton();body=p.player.viewport().height();p.tabs.setCurrentWidget(p.technical);cursor=p.technical.textCursor();cursor.setPosition(2);cursor.setPosition(12,QTextCursor.MoveMode.KeepAnchor);p.technical.setTextCursor(cursor);d.resize(800,650);QTest.qWait(10)
   selected=(p.selected_key,p.topic.currentData(),p.tabs.currentIndex(),cursor.selectedText());button.setFocus();QTest.keyClick(button,Qt.Key.Key_Space);self.qt.processEvents();self.assertTrue(scope.isExpanded());self.assertTrue(p.notice.isVisible());self.assertLess(p.player.viewport().height(),body+50)
   QTest.mouseClick(p.refresh_button,Qt.MouseButton.LeftButton);self.qt.processEvents();self.assertTrue(scope.isExpanded());self.assertEqual((p.selected_key,p.topic.currentData(),p.tabs.currentIndex(),p.technical.textCursor().selectedText()),selected);self.assertEqual((d.width(),d.height()),(800,650))
   button.setFocus();QTest.keyClick(button,Qt.Key.Key_Space);self.qt.processEvents();self.assertFalse(p.notice.isVisible());self.assertEqual((p.selected_key,p.topic.currentData(),p.tabs.currentIndex(),p.technical.textCursor().selectedText()),selected);d.reject()
 def test_missing_portrait_explanation_wraps_and_source_loss_removes_it(self):
  from rouge import current_elbert_reference as model
  from rouge.current_elbert_view import CurrentElbertDialog
  with patch.object(model.battle,'picture_bytes',return_value=None):d=CurrentElbertDialog('ro6_b_3','1')
  self.addCleanup(d.deleteLater);d.resize(640,600);d.show();QTest.qWait(20);p=d.panel;self.assertIn('不借用',p.portrait.text());self.assertTrue(p.portrait.wordWrap());self.assertGreaterEqual(p.portrait.height(),p.portrait.heightForWidth(p.portrait.width()))
  with patch.object(model,'reference',return_value=None):self.assertFalse(p.refresh_reference())
  self.assertIsNone(p.result);self.assertFalse(p.portrait.isVisible());d.reject()
