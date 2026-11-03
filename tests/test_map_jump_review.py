"""Compare real previous readers with current exact-source navigation and images."""
from pathlib import Path
from copy import deepcopy
from hashlib import sha256
from types import ModuleType
from unittest.mock import patch
import unittest
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication
from rouge import current_enemy_spawns as spawns, current_map_position as positions
from rouge import current_map_position_view as view
from rouge.current_enemy_spawns_view import CurrentEnemySpawnsPanel

ROOT=Path(__file__).resolve().parents[1]
BEFORE={
 'current-map-position-view': 'eacac9ad997fbc4fae4f6790dda460504c0dc76be217da7f7c2ae2bb1af0ea32',
 'current-enemy-spawns-view': '4fe453c01f0a7479df67ffb3cfc683a9b59501823f2dc3843fce7dc7ac760191'}

def prior(name):
 raw=(ROOT/('research/map-jump-review-20261031/before-'+name+'.py')).read_bytes()
 assert sha256(raw).hexdigest()==BEFORE[name]
 m=ModuleType('rouge._before_'+name.replace('-','_'));m.__package__='rouge';exec(compile(raw,'<verified-own-prior-reader>','exec'),m.__dict__);return m


class MapJumpReviewTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.qt=QApplication.instance()or QApplication([])
  cls.grid=positions.stage_reference('ro6_n_6_2');assert cls.grid is not None
  cls.raw=positions.battle.version.image_bytes(cls.grid['image']);assert cls.raw

 def test_same_image_four_updates_decode_once_and_match_all_prior_pixels_and_centers(self):
  before=prior('current-map-position-view');records=[];counts=[]
  for module in [before,view]:
   calls=[]
   class CountPixmap(QPixmap):
    def loadFromData(self,*a,**k):calls.append(1);return super().loadFromData(*a,**k)
   with patch.object(module,'QPixmap',CountPixmap):
    widget=module.CurrentOriginalCenters();self.addCleanup(widget.close);widget.resize(620,360);widget.show()
    rows=[]
    for i,point in enumerate([self.grid['points'][0],self.grid['points'][-1],None,self.grid['points'][0]]):
     raw=bytes(bytearray(self.raw))if i==2 else self.raw
     self.assertTrue(widget.set_image(raw,point));self.qt.processEvents();center=widget.point_center()
     rows.append((widget.pixmap.toImage(),None if center is None else(center.x(),center.y())))
    records.append(rows);counts.append(len(calls))
  self.assertEqual(counts,[4,1]);self.assertEqual(records[0],records[1])

 def test_changed_corrupt_missing_and_restored_image_never_retains_an_old_marker(self):
  w=view.CurrentOriginalCenters();self.addCleanup(w.close);point=self.grid['points'][0]
  self.assertTrue(w.set_image(self.raw,point));self.assertIsNotNone(w.point_center())
  for raw in [b'not a png',None,b'']:
   self.assertFalse(w.set_image(raw,point));self.assertTrue(w.pixmap.isNull());self.assertIsNone(w.point_center())
  self.assertTrue(w.set_image(self.raw));self.assertIsNone(w.point_center())
  self.assertTrue(w.set_image(self.raw,point));self.assertIsNotNone(w.point_center())

 def test_mutable_input_is_compared_to_a_retained_immutable_image_value(self):
  w=view.CurrentOriginalCenters();self.addCleanup(w.close);buffer=bytearray(self.raw)
  self.assertTrue(w.set_image(buffer,self.grid['points'][0]));buffer[:]=b'changed and invalid'
  self.assertFalse(w.set_image(buffer,self.grid['points'][0]));self.assertTrue(w.pixmap.isNull());self.assertIsNone(w.point_center())

 def test_enemy_position_jump_keeps_exact_signal_with_one_instead_of_two_resolutions(self):
  before=prior('current-enemy-spawns-view');signals=[];counts=[];results=[]
  for cls in [before.CurrentEnemySpawnsPanel,CurrentEnemySpawnsPanel]:
   p=cls('ro6_n_1_1','5');self.addCleanup(p.close);p.entries.setCurrentIndex(1);self.assertIsNotNone(p.selected())
   emitted=[];p.actionPositionRequested.connect(emitted.append)
   with patch.object(spawns,'stage_reference',wraps=spawns.stage_reference)as resolve:self.assertTrue(p.follow_position())
   counts.append(resolve.call_count);signals.append(emitted);results.append(deepcopy(p.result))
  self.assertEqual(counts,[2,1]);self.assertEqual(signals[0],signals[1]);self.assertEqual(results[0],results[1])

 def test_missing_selection_performs_no_lookup_and_emits_no_jump(self):
  p=CurrentEnemySpawnsPanel('ro6_n_1_1','5');self.addCleanup(p.close);received=[];p.actionPositionRequested.connect(received.append)
  with patch.object(spawns,'position_reference',side_effect=AssertionError('No selected action')):self.assertFalse(p.follow_position())
  self.assertEqual(received,[]);self.assertIsNotNone(p.result)

 def test_stale_snapshot_or_lost_position_source_clears_and_never_emits(self):
  for kind in ['mutated','source']:
   p=CurrentEnemySpawnsPanel('ro6_n_1_1','5');self.addCleanup(p.close);p.entries.setCurrentIndex(1)
   received=[];p.actionPositionRequested.connect(received.append)
   if kind=='mutated':
    p.result['enemy']['name']='synthetic stale snapshot';self.assertFalse(p.follow_position())
   else:
    with patch.object(spawns,'position_reference',return_value=None):self.assertFalse(p.follow_position())
   self.assertIsNone(p.result);self.assertEqual(received,[])


if __name__=='__main__':unittest.main()
