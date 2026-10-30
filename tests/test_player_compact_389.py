import unittest
from types import SimpleNamespace
from PySide6.QtWidgets import QApplication,QWidget
from PySide6.QtCore import Qt
from rouge.player_compact import CompactAssistant
class Compact(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.gui=QApplication.instance()or QApplication([])
 def test_compact_facts_pin_and_no_note_without_context(self):
  # Historical selector retained: manual notes are available without a scene since425.
  owner=QWidget();owner.run=SimpleNamespace(state={});owner.closing=True;owner.open_scene_notes=lambda:None;owner.open_public_statistics=lambda:None
  panel=CompactAssistant(owner);self.assertLessEqual(panel.width(),480);self.assertEqual(panel.cards['保密等级'].text(),'尚未确认');self.assertTrue(panel.buttons['场景笔记'].isEnabled())
  self.assertTrue(panel.windowFlags()&Qt.WindowType.WindowStaysOnTopHint);panel.set_pinned(False);self.assertFalse(panel.windowFlags()&Qt.WindowType.WindowStaysOnTopHint);panel.close();owner.close()
