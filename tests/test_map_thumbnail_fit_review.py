import unittest
from unittest.mock import patch
from copy import deepcopy
from PySide6.QtWidgets import QApplication,QWidget
from PySide6.QtCore import QPoint,QRectF
from PySide6.QtTest import QTest
from PySide6.QtGui import QPixmap
from rouge.player_map_reader import make_reader
from rouge.current_battle_view import CurrentBattleDialog
from rouge.current_map_position_view import CurrentMapPositionDialog
from rouge.player_window_frame import PlayerDialog
from rouge import current_battle_reference as model


class MapThumbnailFitReview(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def dialog(self,direct=False):
  owner=QWidget();self.addCleanup(owner.close);d=CurrentBattleDialog('ro6_n_2_6',owner)if direct else make_reader('battle',{'id':'ro6_n_2_6','title':'公开原图'},owner);d.show();self.addCleanup(d.close);QTest.qWait(30);return d
 def assert_map_visible(self,p):
  m=p.map_image;pix=m.pixmap();self.assertFalse(pix.isNull());size=pix.deviceIndependentSize();rect=QRectF(m.contentsRect()).center();bounds=QRectF(rect.x()-size.width()/2,rect.y()-size.height()/2,size.width(),size.height());bounds.translate(m.mapTo(p.overview_scroll.viewport(),QPoint(0,0)));self.assertTrue(QRectF(p.overview_scroll.viewport().rect()).contains(bounds));self.assertTrue(p.position_button.visibleRegion().contains(p.position_button.rect().center()));self.assertAlmostEqual(size.width()/size.height(),m.original.width()/m.original.height(),delta=.03)
 def test_factory_and_direct_default_show_entire_map_and_reference_entry(self):
  for direct in(False,True):
   d=self.dialog(direct);self.assertEqual((d.width(),d.height()),(800,340));self.assert_map_visible(d.panel)
 def test_repeated_small_large_small_preserves_full_current_map_without_reloading_pixels(self):
  d=self.dialog();p=d.panel;original=p.map_image.original.toImage();key=p.map_image.original.cacheKey()
  for width,height in((640,360),(1040,600),(800,340),(640,360)):
   d.resize(width,height);QTest.qWait(30);self.assertEqual((d.width(),d.height()),(width,height));self.assert_map_visible(p);self.assertEqual(p.map_image.original.toImage(),original);self.assertEqual(p.map_image.original.cacheKey(),key)
 def test_source_and_all_original_categories_unchanged_through_fold_and_refresh(self):
  d=self.dialog();p=d.panel;before=deepcopy(p.result);p.map_section.collapse(animate=False);p.quick_section.collapse(animate=False);p.refresh_reference();self.qt.processEvents();self.assertFalse(p.map_section.isExpanded());self.assertFalse(p.quick_section.isExpanded());self.assertEqual(p.result,before);self.assertEqual(p.tabs.count(),4);p.map_section.expand(animate=False);p.overview_scroll.verticalScrollBar().setValue(0);QTest.qWait(30);self.assert_map_visible(p)
 def test_expanded_map_reader_uses_original_data_shared_frame_and_manual_geometry(self):
  d=self.dialog();p=d.panel;self.assertTrue(p.open_map_positions());child=p.position_dialog;self.assertIsInstance(child,PlayerDialog);self.assertEqual(child.objectName(),d.objectName());area=child.screen().availableGeometry();self.assertEqual((child.width(),child.height()),(min(960,area.width()-40),min(640,area.height()-40)));before=deepcopy(child.panel.result);child.resize(1000,700);self.assertTrue(p.open_map_positions());self.assertIs(p.position_dialog,child);self.assertEqual(child.panel.result,before);self.assertEqual((child.width(),child.height()),(1000,700))
 def test_unavailable_source_removes_old_map_and_closes_owned_expansion(self):
  d=self.dialog();p=d.panel;p.open_map_positions();child=p.position_dialog
  with patch.object(model,'stage_reference',return_value=None):self.assertFalse(p.refresh_reference())
  self.assertTrue(p.map_image.original.isNull());self.assertFalse(child.isVisible());self.assertTrue(p.refresh_reference());QTest.qWait(30);p.overview_scroll.verticalScrollBar().setValue(0);self.assert_map_visible(p)
