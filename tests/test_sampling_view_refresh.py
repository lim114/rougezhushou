"""Hidden views coalesce rendering while models and visible readers stay current."""
from copy import deepcopy
import time,unittest
from unittest.mock import patch
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QWidget
from tests import test_sampling_flow as fixtures


class SamplingViewRefreshTests(unittest.TestCase):
    setUpClass=classmethod(fixtures.SamplingFlowTests.setUpClass.__func__)
    setUp=fixtures.SamplingFlowTests.setUp

    def show_panel(self,panel):
        # A child of the hidden workspace cannot become visible by show() alone.
        panel.setParent(None);self.addCleanup(panel.close)
        panel.show();self.qt.processEvents()
        self.assertTrue(panel.isVisible())

    def test_hidden_catalog_installs_latest_context_without_rebuilding(self):
        panel=self.window.node_catalog
        with patch.object(panel,'refresh',wraps=panel.refresh) as refresh:
            for value in (3,9,51):
                panel.set_map_context(None,epoch='isolated',runtime_context={'gold':value},defer_refresh=True)
            self.assertEqual(refresh.call_count,0)
            self.assertEqual(panel.runtime_context['gold'],51)
            self.show_panel(panel)
            self.assertGreaterEqual(refresh.call_count,1)
        self.assertTrue(all(e['qualification']['context']['gold']==51
                            for e in panel.entries if e['kind']=='event'))

    def test_visible_catalog_and_independent_reader_refresh_immediately(self):
        panel=self.window.node_catalog;self.show_panel(panel)
        with patch.object(panel,'refresh',wraps=panel.refresh) as refresh:
            panel.set_map_context(None,runtime_context={'gold':7},defer_refresh=True)
            self.assertEqual(refresh.call_count,1)
        panel.hide();child=QWidget();panel.current_reference_window=child;child.show();self.qt.processEvents()
        try:
            # The real refresh owns reader invalidation; spy only the decision.
            with patch.object(panel,'refresh') as refresh:
                panel.set_map_context(None,runtime_context={'gold':8},defer_refresh=True)
                self.assertEqual(refresh.call_count,1)
        finally:child.close();panel.current_reference_window=None

    def test_explicit_hidden_context_calls_keep_existing_immediate_contract(self):
        panel=self.window.node_catalog
        with patch.object(panel,'refresh',wraps=panel.refresh) as refresh:
            panel.set_map_context(None,runtime_context={'gold':12})
            self.assertEqual(refresh.call_count,1)

    def test_map_epoch_and_freshness_are_current_before_hidden_view_opens(self):
        from rouge.player_map_acceptance import fixtures as maps
        panel=self.window.node_catalog;graph=deepcopy(maps()[0][0])
        panel.set_map_context(graph,{'floor':1},epoch='first',historical=False,defer_refresh=True)
        graph['captured_at']=999
        self.assertNotEqual(panel.map_context[0].get('captured_at'),999)
        panel.set_map_context(None,epoch='second',historical=True,runtime_context={'gold':4},defer_refresh=True)
        self.assertIsNone(panel.map_context);self.assertEqual(panel.runtime_context['gold'],4)
        self.assertFalse(panel.map_button.isEnabled())

    def test_hidden_inventory_skips_run_refresh_but_opens_with_latest_holdings(self):
        panel=self.window.inventory_panel
        from rouge.player_inventory import inventory_rows
        identity=inventory_rows({},held_only=False)[0]['id']
        self.window.run.state['relics'][identity]={'held':True,'captured_at':time.time(),'source':'isolated_test'}
        with patch.object(panel,'refresh',wraps=panel.refresh) as refresh:
            self.window.sync_run_config()
            self.assertEqual(refresh.call_count,0)
            self.show_panel(panel)
            self.assertGreaterEqual(refresh.call_count,1)
        self.assertIn(identity,panel.rows)

    def test_visible_inventory_updates_without_reopening_and_keeps_search(self):
        panel=self.window.inventory_panel;self.show_panel(panel)
        panel.search.setText('攻击');query=panel.search.text()
        with patch.object(panel,'refresh',wraps=panel.refresh) as refresh:
            self.window.sync_run_config()
            self.assertGreaterEqual(refresh.call_count,1)
        self.assertEqual(panel.search.text(),query)

    def test_show_revalidates_sources_even_without_pending_game_sample(self):
        panel=self.window.inventory_panel;self.show_panel(panel);panel.hide()
        with patch.object(panel,'reload_sources',wraps=panel.reload_sources) as load:
            panel.show();self.qt.processEvents();self.assertGreaterEqual(load.call_count,1)
        catalog=self.window.node_catalog;self.show_panel(catalog);catalog.hide()
        with patch.object(catalog,'refresh',wraps=catalog.refresh) as refresh:
            catalog.show();self.qt.processEvents();self.assertGreaterEqual(refresh.call_count,1)


if __name__=='__main__':unittest.main()
