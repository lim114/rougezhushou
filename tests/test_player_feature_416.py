import unittest,os,sys
from types import SimpleNamespace
from unittest.mock import patch
from PySide6.QtWidgets import QApplication,QWidget
from PySide6.QtCore import QRect
from rouge.player_game_binding import logical_rect,BindingApi,GameWindowBinding
class BindingTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.gui=QApplication.instance()or QApplication([])
 def test_dpi_conversion_on_negative_monitor(self):
  rect=logical_rect((-1800,100,1500,900),(-1920,0,0,1080),(-1280,0),1.5)
  self.assertEqual(rect,QRect(-1200,67,1000,600))
 def test_invalid_geometry_or_scale_not_guessed(self):
  for args in (((0,0,0,100),(0,0,100,100),(0,0),1),((0,0,100,100),(0,0,100,100),(0,0),0)):
   with self.assertRaises(ValueError):logical_rect(*args)
 @unittest.skipUnless(sys.platform=='win32','native Windows identity check')
 def test_owned_native_identity_and_geometry(self):
  # This same case is explicitly executed by the real-Windows416 acceptance.
  if self.gui.platformName()!='windows':self.skipTest('Requires actual Windows QPA; same case runs in native416, not offscreen.')
  w=QWidget();w.resize(500,300);w.show();self.gui.processEvents()
  try:
   api=BindingApi();snap=api.read({'hwnd':int(w.winId()),'pid':os.getpid()});self.assertIsNotNone(snap);self.assertTrue(snap['active']);self.assertGreater(snap['physical_client'][2],0)
   self.assertIsNone(api.read({'hwnd':int(w.winId()),'pid':os.getpid()+10000000}))
  finally:w.close()
 def test_ambiguous_discovery_not_auto_selected(self):
  owner=SimpleNamespace(capture=SimpleNamespace(target=None),closing=False);w=QWidget();binding=GameWindowBinding(w,owner);binding.timer.stop()
  try:
   with patch('rouge.app.list_game_windows',return_value=[{'hwnd':1,'pid':1},{'hwnd':2,'pid':2}]):self.assertIsNone(binding.target())
   owner.capture.target={'hwnd':9,'pid':9};self.assertEqual(binding.target(),owner.capture.target)
  finally:binding.close();w.close()
