from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication,QLabel
from rouge.player_personal_statistics import PersonalStatisticsPage
from rouge.relic_quantities import KETTLE
from tests.test_player_statistics_cohorts_407 import record


class PresentationCard447(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def page(self,rows):
  store=SimpleNamespace(records=lambda:(deepcopy(rows),[]));p=PersonalStatisticsPage(store);p.resize(640,650);p.show();self.addCleanup(p.close);p.card_controls.pages.setCurrentIndex(1);self.qt.processEvents();return p
 def records(self):
  rows=[]
  for index in range(49,-1,-1):
   row=record('public-card-'+str(index),index%2*15);row['created_at']=index;row['state']['resources']={'gold':{'value':index}};rows.append(row)
  return rows
 def test_latest_twenty_is_after_known_cohort_filter_and_does_not_change_main_result(self):
  rows=self.records();p=self.page(rows);c=p.card_controls;p.grade_filter.setCurrentIndex(p.grade_filter.findData(0));before=deepcopy(p.result);c.period.setCurrentIndex(c.period.findData(20));self.assertTrue(c.generate());text='\n'.join(c.card.lines);self.assertIn('本机归档样本：20局',text);self.assertIn('平均：29.00',text);self.assertIn('最多最近20局归档',text);self.assertEqual(p.result,before);self.assertEqual(p.result['archive_count'],25);self.assertEqual(c.preview.accessibleDescription(),text)
 def test_all_records_and_fewer_than_limit_show_actual_count(self):
  p=self.page(self.records()[:3]);c=p.card_controls
  for n in(0,20,50,100):
   c.period.setCurrentIndex(c.period.findData(n));self.assertTrue(c.generate());self.assertIn('本机归档样本：3局','\n'.join(c.card.lines));self.assertIn('平均：48.00','\n'.join(c.card.lines))
 def test_same_refresh_preserves_generated_subset_and_range_change_invalidates(self):
  p=self.page(self.records());c=p.card_controls;c.period.setCurrentIndex(c.period.findData(20));c.generate();card=c.card;p.refresh();self.assertIs(c.card,card);self.assertEqual(c.period.currentData(),20);c.period.setCurrentIndex(c.period.findData(50));self.assertIsNone(c.card);self.assertTrue(c.preview.original.isNull());self.assertFalse(c.save.isEnabled())
 def test_dark_card_has_large_values_sample_limits_and_full_local_png(self):
  p=self.page(self.records()[:3]);c=p.card_controls;c.generate();card=c.card;raw=card.png();image=QImage.fromData(raw,'PNG');self.assertFalse(image.isNull());self.assertEqual(image.width(),round(card.width()*card.devicePixelRatioF()));self.assertEqual(image.pixelColor(5,5).name(),'#1e1e20');self.assertGreater(card.width(),card.height());values=card.findChildren(QLabel,'cardMetricValue');self.assertEqual(len(values),3);self.assertTrue(any(v.text()=='48.00'for v in values));self.assertIn('不是掉落概率','\n'.join(card.lines));self.assertTrue(all(label.geometry().bottom()<card.height()for label in card.findChildren(QLabel)))
 def test_exact_relic_icon_and_unknown_zero_are_not_guessed(self):
  row=record('public-card-relic');row['state'].update(resources={'gold':{'value':0}},inventory_verified=True,relic_count=1,relics={KETTLE:{'held':True}});p=self.page([row]);p.relic.setCurrentIndex(p.relic.findData(KETTLE));c=p.card_controls;self.assertTrue(c.generate());pictures=[v for v in c.card.findChildren(QLabel)if v.accessibleName().startswith('统计条目图标：')];self.assertEqual(len(pictures),1);self.assertFalse(pictures[0].pixmap().isNull());values=[v.text()for v in c.card.findChildren(QLabel,'cardMetricValue')];self.assertIn('0.00',values);self.assertIn('未知',values);self.assertIn('100.0%',values)
 def test_missing_artwork_keeps_values_and_explicit_picture_gap(self):
  from unittest.mock import patch
  row=record('public-card-no-art');row['state'].update(inventory_verified=True,relic_count=1,relics={KETTLE:{'held':True}});p=self.page([row]);p.relic.setCurrentIndex(p.relic.findData(KETTLE))
  with patch('rouge.expansion_reference.packet',return_value=None):self.assertTrue(p.card_controls.generate())
  self.assertTrue(any(v.text()=='无图'for v in p.card_controls.card.findChildren(QLabel)));self.assertIn('归档时持有率：100.0%','\n'.join(p.card_controls.card.lines))
 def test_no_fields_or_known_empty_history_still_explains_unknown(self):
  p=self.page([]);c=p.card_controls;c.generate();self.assertIn('本机归档样本：0局','\n'.join(c.card.lines));self.assertNotIn('0.0%','\n'.join(c.card.lines))
  for box in c.fields.values():box.setChecked(False)
  self.assertTrue(c.generate());self.assertTrue(any('未选择展示指标'in v.text()for v in c.card.findChildren(QLabel)))
 def test_scaled_preview_preserves_full_size_export_and_current_card(self):
  p=self.page(self.records()[:3]);c=p.card_controls;c.generate();card=c.card;raw=card.png()
  for width in(400,900,550):
   p.resize(width,460);self.qt.processEvents();self.assertIs(c.card,card);self.assertFalse(c.preview.original.isNull());self.assertLessEqual(c.preview.pixmap().deviceIndependentSize().width(),c.preview.contentsRect().width()+.5/c.preview.devicePixelRatioF());self.assertEqual(c.preview.pixmap().devicePixelRatioF(),c.preview.devicePixelRatioF());self.assertEqual(c.scroll.horizontalScrollBar().maximum(),0);self.assertEqual(card.png(),raw)
 def test_enlarged_viewer_reuses_one_real_window_and_keeps_export(self):
  from PySide6.QtTest import QTest
  p=self.page(self.records()[:3]);c=p.card_controls;c.generate();raw=c.card.png();self.assertTrue(c.open_viewer());self.qt.processEvents();viewer=c.viewer;self.assertTrue(viewer.isVisible());self.assertTrue(c.open_viewer());self.assertIs(c.viewer,viewer);QTest.keyClick(viewer,Qt.Key.Key_Escape);self.qt.processEvents();self.assertFalse(viewer.isVisible());self.assertEqual(c.card.png(),raw);c.open_viewer();self.assertIs(c.viewer,viewer);self.assertTrue(viewer.isVisible())
 def test_scope_change_closes_stale_enlarged_card(self):
  p=self.page(self.records()[:3]);c=p.card_controls;c.generate();c.open_viewer();self.qt.processEvents();viewer=c.viewer;c.period.setCurrentIndex(c.period.findData(20));self.assertIsNone(c.viewer);self.assertFalse(viewer.isVisible());self.assertIsNone(c.card);self.assertFalse(c.view.isEnabled());self.assertFalse(c.open_viewer())


if __name__=='__main__':unittest.main()
