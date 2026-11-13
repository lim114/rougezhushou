"""Hidden inventory tabs must not block delivery of newly recognized pages."""
import unittest
from contextlib import ExitStack
from unittest.mock import patch

from tests import test_sampling_flow as fixtures


class InventoryTabRefreshTests(unittest.TestCase):
    setUpClass = classmethod(fixtures.SamplingFlowTests.setUpClass.__func__)
    setUp = fixtures.SamplingFlowTests.setUp

    def inventory(self):
        self.window.show_compact()
        compact = self.window.compact_window
        compact.open_inventory()
        self.qt.processEvents()
        return compact, compact.inventory_popup

    def test_sample_refresh_only_rebuilds_the_current_tab(self):
        compact, popup = self.inventory()
        with ExitStack() as stack:
            readers = [popup.panel, popup.tools, popup.parts, popup.shop]
            refreshes = [stack.enter_context(patch.object(panel, 'refresh', wraps=panel.refresh))
                         for panel in readers]
            compact.refresh()
            self.assertEqual([call.call_count for call in refreshes], [1, 0, 0, 0])

    def test_switch_reads_latest_tools_and_preserves_search(self):
        from rouge.player_tools import tool_rows
        compact, popup = self.inventory()
        item = tool_rows({}, held_only=False)[0]
        self.window.run.state['tactical_tools'][item['id']] = {'held': True, 'captured_at': 1}
        popup.tools.search.setText(item['name'])
        # A later observation arrives while the tool tab is hidden.
        self.window.run.state['tactical_tools'][item['id']]['held'] = False
        with patch.object(popup.tools, 'refresh', wraps=popup.tools.refresh) as refresh:
            compact.refresh()
            self.assertEqual(refresh.call_count, 0)
            popup.pages.setCurrentWidget(popup.tools)
            self.assertGreaterEqual(refresh.call_count, 1)
        self.assertNotIn(item['id'], popup.tools.rows)
        self.assertEqual(popup.tools.search.text(), item['name'])

    def test_switch_revalidates_sources_before_showing_parts(self):
        compact, popup = self.inventory()
        self.assertTrue(popup.parts.rows)
        with patch('rouge.player_parts.source.packet', return_value=None):
            popup.pages.setCurrentWidget(popup.parts)
        self.assertEqual(popup.parts.rows, {})
        self.assertIn('暂不可用', popup.parts.summary.text())

    def test_visible_parts_reload_exchange_source_and_current_count(self):
        compact, popup = self.inventory()
        popup.pages.setCurrentWidget(popup.parts)
        self.window.run.state['resources']['parts_count'] = {'value': 7}
        with patch.object(popup.panel, 'reload_sources', wraps=popup.panel.reload_sources) as reload:
            compact.refresh()
            self.assertGreaterEqual(reload.call_count, 1)
        self.assertIn('7件', popup.parts.summary.text())

    def test_visible_shop_source_card_still_refreshes_when_another_tab_is_selected(self):
        compact, popup = self.inventory()
        with patch.object(popup.shop.source_card, 'isVisible', return_value=True), \
                patch.object(popup.shop, 'refresh', wraps=popup.shop.refresh) as refresh:
            compact.refresh()
            self.assertEqual(refresh.call_count, 1)

    def test_switch_to_shop_refreshes_even_without_a_new_sample(self):
        compact, popup = self.inventory()
        with patch.object(popup.shop, 'refresh', wraps=popup.shop.refresh) as refresh:
            popup.pages.setCurrentWidget(popup.shop)
            self.assertGreaterEqual(refresh.call_count, 1)
        self.assertEqual(popup.shop.signature[0], self.window.run.state['id'])

    def test_open_inventory_source_card_remains_current_on_another_tab(self):
        compact, popup = self.inventory()
        popup.pages.setCurrentWidget(popup.tools)
        with patch.object(popup.panel.hover_card, 'isVisible', return_value=True), \
                patch.object(popup.panel, 'refresh', wraps=popup.panel.refresh) as refresh:
            compact.refresh()
            self.assertEqual(refresh.call_count, 1)


if __name__ == '__main__':unittest.main()
