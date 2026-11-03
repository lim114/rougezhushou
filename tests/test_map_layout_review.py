from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from PySide6.QtWidgets import QApplication
from rouge.run_state import RunState
from rouge.map_view import MapView
from rouge.player_map import MapPanel,zone_info
from rouge.player_map_acceptance import fixtures


class MapLayoutReview(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.gui=QApplication.instance()or QApplication([])
 def panel(self):
  folder=TemporaryDirectory();self.addCleanup(folder.cleanup);r=RunState(Path(folder.name)/'run.json');graphs,*_=fixtures();r.state['maps']={g['zone_id']:g for g in graphs};r.state['resources']={'gold':{'value':99,'captured_at':2000}}
  r.state['history']=[{'kind':'floor_resources_read','source':'same_frame_zone_and_resources','zone_id':graphs[0]['zone_id'],'template_id':graphs[0]['template_id'],'at':1000,'values':{'gold':7,'hope':1},'capacities':{'hope':8}}]
  original=MapView();original.set_map(graphs[1]);owner=SimpleNamespace(run=r,map_view=original,compact_window=None);p=MapPanel(owner);self.addCleanup(p.close);self.addCleanup(original.close);p.resize(1200,460);p.show();self.gui.processEvents();p.floors.setCurrentIndex(0);self.gui.processEvents();return p,r,graphs
 def test_default_map_has_no_permanent_type_sidebar_and_tools_remain_available(self):
  p,r,g=self.panel();self.assertFalse(p.finder.isVisible());self.assertFalse(p.palette.isVisible());self.assertFalse(p.information.isVisible());self.assertFalse(p.drawer.isVisible());p.finder_toggle.click();self.gui.processEvents();self.assertTrue(p.palette.isVisible());self.assertTrue(p.zoom.isVisible());p.scope_toggle.click();self.assertTrue(p.information.isVisible());p.type_buttons['诡意行商'].click();self.assertEqual(p.view.filter_kind,'诡意行商');p.finder_toggle.click();self.assertTrue(p.filter_notice.isVisible());self.assertTrue(p.clear_filter.isVisible());p.clear_filter.click();self.assertFalse(p.filter_notice.isVisible())
 def test_compact_floor_names_retain_full_zone_names_and_identity(self):
  p,r,graphs=self.panel();self.assertEqual([p.floors.tabText(i)for i in range(2)],['第一层','第二层'])
  for i,g in enumerate(graphs):self.assertEqual(p.floors.tabData(i),g['zone_id']);self.assertEqual(p.floors.tabToolTip(i),zone_info(g)[0])
 def test_historical_chips_use_only_that_map_snapshot_and_capacity(self):
  p,r,g=self.panel();self.assertTrue(p.view.historical);rows={x['key']:x for x in p.resources.rows};self.assertEqual(rows['gold']['value'],'7');self.assertEqual(rows['hope']['value'],'1/8');self.assertEqual(set(rows),{'gold','hope'});self.assertIn('历史地图',p.context_notice.text());self.assertTrue(all('不是入层'in x['note']for x in rows.values()))
 def test_wrong_template_snapshot_does_not_replace_matching_map_resources(self):
  p,r,g=self.panel();r.state['history'].append({**r.state['history'][0],'template_id':'another-layout','values':{'gold':777}});p.refresh();self.assertEqual(next(x for x in p.resources.rows if x['key']=='gold')['value'],'7')
 def test_missing_or_zone_only_history_does_not_use_current_values(self):
  p,r,g=self.panel();r.state['history'][0]['template_id']=None;p.refresh();self.assertEqual([x['value']for x in p.resources.rows],['未记录']);self.assertIn('当时资源未记录',p.context_notice.text());self.assertNotIn('99',p.floor_resources.text())
 def test_current_floor_still_uses_recent_resources_and_does_not_backfill_history(self):
  p,r,g=self.panel();before=deepcopy(r.state);p.floors.setCurrentIndex(1);self.assertFalse(p.view.historical);self.assertEqual(next(x for x in p.resources.rows if x['key']=='gold')['value'],'99');self.assertIn('本局最近',p.context_notice.text());p.floors.setCurrentIndex(0);self.assertEqual(next(x for x in p.resources.rows if x['key']=='gold')['value'],'7');self.assertEqual(r.state,before)
 def test_same_historical_refresh_keeps_chip_objects_search_and_scope(self):
  p,r,g=self.panel();chip=p.resources.chips['gold'];p.finder_toggle.click();p.scope_toggle.click();p.node_query.setText('诡意行商');p.refresh();self.assertIs(chip,p.resources.chips['gold']);self.assertTrue(p.finder_toggle.isChecked());self.assertTrue(p.scope_toggle.isChecked());self.assertEqual(p.node_query.text(),'诡意行商');self.assertEqual(p.floors.currentIndex(),0)
 def test_switching_scopes_restores_resource_order_without_replacing_retained_chips(self):
  p,r,g=self.panel();gold=p.resources.chips['gold'];p.floors.setCurrentIndex(1);self.assertIs(gold,p.resources.chips['gold']);self.assertEqual([p.resources.flow.itemAt(i).widget()for i in range(p.resources.flow.count())],[p.resources.chips[row['key']]for row in p.resources.rows]);self.assertEqual(p.resources.rows[0]['key'],'items')
 def test_map_zoom_uses_upstream_center_preservation(self):
  p,r,g=self.panel();p.resize(1000,650);self.gui.processEvents();p.zoom.setCurrentIndex(2);self.gui.processEvents();bar=p.scroll.horizontalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(bar.maximum()//2);old_center=(bar.value()+bar.pageStep()/2)/p.view.width();p.zoom.setCurrentIndex(3);self.gui.processEvents();new_center=(bar.value()+bar.pageStep()/2)/p.view.width();self.assertAlmostEqual(old_center,new_center,delta=3/p.view.width());p.zoom.setCurrentIndex(0);self.gui.processEvents();self.assertTrue(p.scroll.widgetResizable());self.assertEqual(p.view.width(),p.scroll.viewport().width())
 def test_actual_width_controls_wrap_without_losing_buttons_or_graph(self):
  p,r,g=self.panel();p.finder_toggle.click()
  for width in(640,900,1200):
   p.resize(width,720);self.gui.processEvents();self.assertEqual(p.width(),width);self.assertEqual(p.view.graph['template_id'],g[0]['template_id']);self.assertTrue(all(b.isVisible()and p.rect().contains(b.mapTo(p,b.rect().bottomRight()))for b in p.type_buttons.values()));self.assertTrue(p.rect().contains(p.find_node.mapTo(p,p.find_node.rect().bottomRight())))


if __name__=='__main__':unittest.main()
