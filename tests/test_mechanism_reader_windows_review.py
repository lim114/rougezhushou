from importlib import import_module
from types import SimpleNamespace
from unittest.mock import patch
import unittest
from PySide6.QtWidgets import QApplication,QDialog,QPushButton
from PySide6.QtTest import QTest
from rouge import battle_enemy_readers as readers
from rouge.player_window_frame import PlayerDialog


class MechanismReaderWindowsReview(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.qt=QApplication.instance()or QApplication([]);cls.fixtures=[]
  for name,spec in readers._READERS.items():
   model=import_module('rouge.'+spec.provider);sid=model.STAGES[0];ref=model.reference(sid);row=(ref.get('rows')or ref.get('entities'))[0];key=row['enemy_key']if name=='boss_documents'else row['key'];view=import_module('rouge.'+spec.provider.removesuffix('_reference')+'_view');cls.fixtures.append((name,getattr(view,spec.dialog),sid,key))
 def dialog(self,fixture,show=True):
  _,ctor,sid,key=fixture;d=ctor(sid,key);self.addCleanup(d.deleteLater)
  if show:d.show();QTest.qWait(20)
  return d
 def test_all_seven_actual_dialogs_share_frame_theme_size_and_four_readable_lines(self):
  for fixture in self.fixtures:
   d=self.dialog(fixture);self.assertIsInstance(d,PlayerDialog);self.assertEqual(d.objectName(),'mapReferenceWindow');area=d.screen().availableGeometry();self.assertEqual((d.width(),d.height()),(min(760,area.width()-40),min(600,area.height()-40)));self.assertTrue(d.rect().contains(d.titleBar.closeBtn.geometry()));self.assertTrue(all(not b.autoDefault()for b in d.findChildren(QPushButton)));self.assertIsNotNone(d.panel.result);self.assertGreaterEqual(d.panel.player.viewport().visibleRegion().boundingRect().height(),4*d.panel.player.fontMetrics().lineSpacing());d.reject()
 def test_normal_close_and_hidden_owner_close_each_clear_exactly_once(self):
  for fixture in self.fixtures:
   for route in('close','owner_hidden'):
    d=self.dialog(fixture,show=route=='close')
    with patch.object(d.panel,'clear_reference',wraps=d.panel.clear_reference)as clear:
     if route=='close':d.close()
     else:readers.close_reader(SimpleNamespace(**{fixture[0]+'_dialog':d}),fixture[0])
     self.qt.processEvents();self.assertEqual(clear.call_count,1,(fixture[0],route));self.assertIsNone(d.panel.result);self.assertFalse(d.isVisible())
 def test_finished_signal_sees_cleared_source_for_both_done_results(self):
  for fixture in self.fixtures:
   for code in(QDialog.DialogCode.Accepted,QDialog.DialogCode.Rejected):
    d=self.dialog(fixture,False);seen=[];d.finished.connect(lambda result,p=d.panel:seen.append((result,p.result)))
    with patch.object(d.panel,'clear_reference',wraps=d.panel.clear_reference)as clear:d.done(code);self.assertEqual(clear.call_count,1)
    self.assertEqual(seen,[(int(code),None)])
 def test_guest_done_closes_and_clears_owned_map_before_finished(self):
  fixture=next(x for x in self.fixtures if x[0]=='guest_material');d=self.dialog(fixture);p=d.panel;self.assertTrue(p.open_map());child=p.map_dialog;seen=[];d.finished.connect(lambda _:seen.append((p.result,p.map_dialog,child.panel.result,child.isVisible())));d.done(QDialog.DialogCode.Rejected);self.qt.processEvents();self.assertEqual(seen,[(None,None,None,False)])

 def test_all_five_owned_maps_clear_exactly_once_for_each_finish_route(self):
  for fixture in self.fixtures:
   if fixture[0] not in ('sun_boss','boss_documents','guest_knights','guest_crystals','guest_material'):continue
   for route in ('close','reject','done','owner'):
    d=self.dialog(fixture);p=d.panel;self.assertTrue(p.open_map());child=p.map_dialog
    with patch.object(child.panel,'clear_reference',wraps=child.panel.clear_reference)as clear:
     if route=='owner':p.clear_reference()
     elif route=='done':child.done(QDialog.DialogCode.Rejected)
     else:getattr(child,route)()
     self.qt.processEvents();self.assertEqual(clear.call_count,1,(fixture[0],route));self.assertIsNone(child.panel.result);self.assertFalse(child.isVisible())
    d.reject()
