from pathlib import Path
from tempfile import TemporaryDirectory
from copy import deepcopy
import unittest
from PySide6.QtWidgets import QApplication,QWidget
from PySide6.QtCore import Qt,QPoint
from rouge.run_state import RunState
from rouge.player_replay import ReplayPanel,HISTORY_STYLE
from rouge.player_compact import ToolPopover
from rouge.player_personal_statistics import complete_inventory,statistics
from rouge.player_statistics_samples import sample_rows
from tests.test_inventory_modes_446 import observe,KETTLE,OTHER,TOOL


class HistoryStatisticsLayoutReview(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
 def run_state(self):
  folder=TemporaryDirectory();self.addCleanup(folder.cleanup);return RunState(Path(folder.name)/'run.json')
 def panel(self):
  r=self.run_state();parent=QWidget();p=ReplayPanel(r);w=ToolPopover('对局记录',p,parent,theme='light',extra_style=HISTORY_STYLE,object_name='historyWindow');p.tabs.setCurrentWidget(p.archive_page);w.resize(640,650);w.show();self.qt.processEvents();self.addCleanup(parent.close);self.addCleanup(w.close);return w,p,r,parent
 def test_repeated_confirmed_kettles_are_a_complete_statistical_sample(self):
  r=self.run_state();observe(r,[KETTLE]*3+[OTHER,TOOL]);before=deepcopy(r.state);self.assertTrue(complete_inventory(r.state));self.assertEqual(r.state,before)
 def test_holding_rate_and_its_exact_sample_rows_share_repeated_count(self):
  r=self.run_state();observe(r,[KETTLE]*3+[OTHER,TOOL]);records=[{'state':deepcopy(r.state),'state_sha256':'a'*64}];result=statistics(records,KETTLE);self.assertEqual(result['relic']['sample_count'],1);self.assertEqual(result['relic']['held_count'],1);self.assertEqual(result['relic']['fraction'],1);self.assertEqual(result['measures']['relic_count']['mean'],5);rows=sample_rows(records,'relic',KETTLE);self.assertTrue(rows[0]['included']);self.assertTrue(rows[0]['value'])
 def test_unproven_repeated_count_stays_excluded(self):
  r=self.run_state();observe(r,[KETTLE]*3+[OTHER,TOOL]);r.state['relic_icon_memory']['count']=999;before=deepcopy(r.state);self.assertFalse(complete_inventory(r.state));result=statistics([{'state':r.state}],KETTLE);self.assertIsNone(result['relic']['fraction']);self.assertEqual(result['relic']['excluded_incomplete_count'],1);self.assertEqual(r.state,before)
 def test_hidden_statistics_no_longer_enlarges_history_default(self):
  w,p,r,parent=self.panel();self.assertEqual((w.width(),w.height()),(640,650));self.assertIs(p.tabs.currentWidget(),p.archive_page);self.assertFalse(p.statistics.isVisible());self.assertLessEqual(w.minimumSizeHint().height(),650)
 def test_small_statistics_page_scrolls_to_controls_and_keeps_selection(self):
  w,p,r,parent=self.panel();p.tabs.setCurrentWidget(p.statistics);w.resize(550,360);self.qt.processEvents();stats=p.statistics;self.assertTrue(stats.scroll.widgetResizable());self.assertGreater(stats.scroll.verticalScrollBar().maximum(),0);self.assertEqual(stats.scroll.horizontalScrollBar().maximum(),0);stats.relic.setCurrentIndex(1);choice=stats.relic.currentData();stats.scroll.ensureWidgetVisible(stats.reload);self.qt.processEvents();stats.refresh();self.assertEqual(stats.relic.currentData(),choice);self.assertTrue(stats.reload.isVisible());self.assertGreater(stats.scroll.verticalScrollBar().value(),0)
 def test_card_field_options_wrap_using_real_external_qt_flow(self):
  from rouge.flow_layout import FlowLayout
  w,p,r,parent=self.panel();stats=p.statistics;p.tabs.setCurrentWidget(stats);controls=stats.card_controls;controls.pages.setCurrentIndex(1);w.resize(550,460);boxes=list(controls.fields.values());font=boxes[0].font();font.setPointSize(18)
  for box in boxes:box.setFont(font)
  self.qt.processEvents();self.assertIsInstance(boxes[0].parentWidget().layout().itemAt(0).layout(),FlowLayout);self.assertGreater(len({box.y()for box in boxes}),1);self.assertTrue(all(box.geometry().right()<box.parentWidget().width()for box in boxes));before=deepcopy(stats.result);controls.fields['relic'].setChecked(False);self.assertTrue(controls.generate());self.assertEqual(stats.result,before);self.assertFalse(controls.fields['relic'].isChecked())
 def test_summary_shows_values_before_expandable_full_scope_and_keeps_reading(self):
  w,p,r,parent=self.panel();state=deepcopy(r.state);state['id']='public-statistics-summary';state['resources']={'gold':{'value':0}};p.history_store.archive(state);stats=p.statistics;stats.refresh();p.tabs.setCurrentWidget(stats);self.qt.processEvents();text=stats.detail.toPlainText();self.assertIn('归档前最近读值',text);self.assertIn('0.00',text);self.assertIn('不是掉落概率',text);self.assertNotIn('筛选的是归档中已读保密等级',text);stats.toggle_details(None);self.assertIn('筛选的是归档中已读保密等级',stats.detail.toPlainText());self.assertTrue(stats.details_open);stats.detail.verticalScrollBar().setValue(30);position=stats.detail.verticalScrollBar().value();stats.render();self.assertEqual(stats.detail.verticalScrollBar().value(),position);self.assertTrue(stats.details_open);stats.toggle_details(None);self.assertFalse(stats.details_open);self.assertNotIn('筛选的是归档中已读保密等级',stats.detail.toPlainText())
 def test_statistics_heading_does_not_claim_the_selected_archive_is_its_scope(self):
  w,p,r,parent=self.panel();p.history_scope_button.setChecked(True);p.tabs.setCurrentWidget(p.statistics);self.qt.processEvents();self.assertEqual(p.reading_label.text(),'个人统计 · 本机归档');self.assertFalse(p.notice.isVisible());self.assertFalse(p.history_scope_button.isVisible());p.refresh();self.assertEqual(p.reading_label.text(),'个人统计 · 本机归档');p.tabs.setCurrentWidget(p.nodes);self.qt.processEvents();self.assertTrue(p.history_scope_button.isVisible());self.assertTrue(p.history_scope_button.isChecked());self.assertTrue(p.notice.isVisible())
 def test_unavailable_samples_and_known_empty_archive_have_different_meaning(self):
  from rouge.player_statistics_samples import StatisticsSamplesPage
  page=StatisticsSamplesPage();self.addCleanup(page.close);page.install([],None);self.assertTrue(page.source_available);self.assertIn('当前筛选下共0局',page.notice.text());page.install(None,None);self.assertFalse(page.source_available);self.assertIn('本项统计未知',page.notice.text());self.assertNotIn('当前筛选下共0局',page.notice.text());self.assertEqual(page.table.rowCount(),0);self.assertFalse(page.open_button.isEnabled());page.install([],None);self.assertIn('当前筛选下共0局',page.notice.text())
 def test_parent_source_failure_sends_unknown_to_samples_then_recovers_known_empty(self):
  from unittest.mock import patch
  w,p,r,parent=self.panel();stats=p.statistics
  with patch.object(stats.store,'records',side_effect=OSError('isolated unavailable archive')):stats.refresh()
  self.assertIsNone(stats.result);self.assertFalse(stats.samples.source_available);self.assertIn('本项统计未知',stats.samples.notice.text());stats.refresh();self.assertTrue(stats.samples.source_available);self.assertEqual(stats.result['archive_count'],0);self.assertIn('当前筛选下共0局',stats.samples.notice.text())


if __name__=='__main__':unittest.main()
