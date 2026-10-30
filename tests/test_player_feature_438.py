import unittest
from PySide6.QtWidgets import QApplication
from rouge.player_map_acceptance import fixtures
class LatestPosition(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def setUp(self):
  from tests.test_batch185_mainwindow import Batch185WindowTests
  Batch185WindowTests.setUp(self);self.gs,*_=fixtures();g=self.gs[0];g['last_confirmed_current_node']=g['nodes'][0]['id'];self.window.run.state['maps']={g['zone_id']:g for g in self.gs};self.window.map_view.set_map(g,historical=True);self.window.show_compact();self.window.compact_window.open_map();self.p=self.window.compact_window.map_popup.panel
 def test_return_exact_previous_location_without_claiming_current(self):
  p=self.p;p.floors.setCurrentIndex(1);self.assertTrue(p.focus_latest_position());self.assertEqual(p.view.selected,self.gs[0]['nodes'][0]['id']);self.assertTrue(p.view.historical)
 def test_missing_position_does_not_select_arbitrary_node(self):
  self.window.map_view.graph.pop('last_confirmed_current_node');self.p.refresh();self.assertFalse(self.p.latest_position.isEnabled());self.assertFalse(self.p.focus_latest_position())
if __name__=='__main__':unittest.main()
