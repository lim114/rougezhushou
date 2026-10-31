"""Player catalogues retain full limits and reading as their shared layout changes."""
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch
import unittest
from PySide6.QtWidgets import QApplication,QTabBar,QPushButton
from rouge.player_parts import PartsPanel
from rouge.player_tools import ToolsPanel
from rouge.player_shop_memory import ShopMemoryPanel
from rouge.player_resource_strip import ResourceStrip
from tests.test_player_feature_426 import observations

class CatalogueHeaderReview(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.gui=QApplication.instance()or QApplication([])
 def own(self,p):self.addCleanup(p.close);p.resize(980,540);p.show();self.gui.processEvents();return p
 def test_three_catalogues_keep_scope_and_close_selected_reading(self):
  run=SimpleNamespace(state={'id':'public-fixture','history':[observations()]},save_issue=None)
  for cls in(PartsPanel,ToolsPanel,ShopMemoryPanel):
   p=self.own(cls(run));
   if isinstance(p,ToolsPanel):p.held.setChecked(False)
   self.assertFalse(p.notice.isVisible());self.assertTrue(p.summary.isVisible());p.scope.click();self.assertTrue(p.notice.isVisible());self.assertTrue(p.notice.text())
   p.entries.setCurrentRow(0);self.assertTrue(p.detail.isVisible());item=p.entries.currentItem();p.details_toggle.click();p.refresh();self.assertFalse(p.detail.isVisible());self.assertTrue(p.scope.isChecked());self.assertIs(p.entries.currentItem(),item)
 def test_repeated_parts_source_failure_stays_visible_without_resetting_state(self):
  run=SimpleNamespace(state={'resources':{'parts_count':{'value':7}}});p=self.own(PartsPanel(run));before=deepcopy(run.state);p.entries.setCurrentRow(0)
  with patch('rouge.player_parts.source.packet',return_value=None):
   for _ in range(3):p.refresh();self.assertIn('暂不可用',p.summary.text());self.assertIn('暂不可用',p.notice.text());self.assertFalse(p.detail.isVisible());self.assertEqual(p.entries.count(),0)
  p.refresh();self.assertIsNone(p.entries.currentItem());self.assertFalse(p.detail.isVisible());self.assertEqual(run.state,before)
 def test_tool_source_failure_is_not_hidden_in_the_scope_fold(self):
  run=SimpleNamespace(state={});p=self.own(ToolsPanel(run));p.held.setChecked(False);p.entries.setCurrentRow(0)
  with patch('rouge.player_tools.source.packet',return_value=None):p.refresh();p.refresh()
  self.assertIn('不可用',p.summary.text());self.assertFalse(p.notice.isVisible());self.assertFalse(p.detail.isVisible());self.assertFalse(p.details_toggle.isChecked())
 def test_new_shop_observation_preserves_the_old_exact_reading_cursor(self):
  first=observations();run=SimpleNamespace(state={'id':'public-fixture','history':[first]},save_issue=None);p=self.own(ShopMemoryPanel(run));p.entries.setCurrentRow(0);p.scope.click();snapshot=p.snapshots.currentData();text=p.detail.toPlainText();cursor=p.detail.textCursor();cursor.setPosition(8);p.detail.setTextCursor(cursor)
  second=deepcopy(first);second['at']+=2;run.state['history'].append(second);p.refresh()
  self.assertEqual(p.snapshots.currentData(),snapshot);self.assertEqual(p.detail.toPlainText(),text);self.assertEqual(p.detail.textCursor().position(),8);self.assertTrue(p.scope.isChecked())
  run.save_issue='isolated-error';p.refresh();self.assertIn('未保存',p.summary.text());self.assertEqual(p.detail.textCursor().position(),8)
 def test_shop_source_loss_is_visible_and_does_not_restore_a_stale_selection(self):
  run=SimpleNamespace(state={'id':'public-fixture','history':[observations()]},save_issue=None);p=self.own(ShopMemoryPanel(run));p.entries.setCurrentRow(0)
  with patch('rouge.expansion_reference.packet',return_value=None):p.refresh();p.refresh()
  self.assertIn('暂不可用',p.summary.text());self.assertFalse(p.detail.isVisible());self.assertEqual(p.entries.count(),0);p.refresh();self.assertIsNone(p.entries.currentItem())
 def test_navigation_controls_and_resource_pills_wrap_together(self):
  nav=QTabBar();nav.setUsesScrollButtons(True)
  for name in('收藏品 已读50','道具 1','零件箱 7/12','商店记录'):nav.addTab(name)
  crew=QPushButton('干员 未读');strip=self.own(ResourceStrip(leading=(nav,crew)));strip.set_rows([r for r in strip.rows if r['key']not in('items','parts','crew')])
  for width in(360,480,640,900,1200):
   strip.resize(width,strip.flow.heightForWidth(width));self.gui.processEvents();strip.resize(width,strip.flow.heightForWidth(width));self.gui.processEvents();rects=[w.geometry()for w in(nav,crew,*strip.chips.values())]
   self.assertTrue(all(strip.rect().contains(r)for r in rects),(width,rects));self.assertTrue(all(not a.intersects(b)for i,a in enumerate(rects)for b in rects[i+1:]));self.assertEqual(len(strip.chips),7)

if __name__=='__main__':unittest.main()
