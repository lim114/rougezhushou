import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
from unittest.mock import patch
import unittest
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QTextCursor
from rouge import current_route_itinerary as model
from rouge.current_route_itinerary_view import CurrentRouteItineraryPanel,CurrentRouteItineraryDialog
class CurrentRouteItineraryView375Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.app=QApplication.instance()or QApplication([])
    def setUp(self):self.panel=CurrentRouteItineraryPanel('ro6_n_1_3');self.panel.resize(1050,560);self.panel.show();self.app.processEvents()
    def tearDown(self):self.panel.close();self.panel.deleteLater();self.app.processEvents()
    def select(self):self.panel.entries.setCurrentIndex(self.panel.entries.findData('$.routes[10]'));self.app.processEvents();self.assertIsNotNone(self.panel.selected_route())
    def test_all_routes_unselected_and_no_auto_action_or_map(self):self.assertIsNotNone(self.panel.result);self.assertIsNone(self.panel.selected_route());self.assertIsNone(self.panel.selected_step());self.assertFalse(self.panel.action_button.isEnabled());self.assertFalse(self.panel.position_button.isEnabled())
    def test_scopes_are_actual_branches_and_changed_filter_clears_selection(self):
        self.select();self.panel.scope.setCurrentIndex(self.panel.scope.findData('extra'));self.assertIsNone(self.panel.selected_route());self.assertTrue(all(self.panel.entries.itemData(i).startswith('$.extraRoutes[')for i in range(1,self.panel.entries.count())))
    def test_checkpoint_combo_preserves_order_and_wait_has_no_map_button(self):
        self.select();route=self.panel.selected_route();self.assertEqual([self.panel.steps.itemData(i)for i in range(1,self.panel.steps.count())],[s['key']for s in route['steps']]);step=next(s for s in route['steps']if s['kind']=='DISAPPEAR');self.panel.steps.setCurrentIndex(self.panel.steps.findData(step['key']));self.assertFalse(self.panel.position_button.isEnabled());self.assertIn('占位坐标不画到地图',self.panel.player.toPlainText())
    def test_exact_step_position_map_opens_and_clears_on_new_step(self):
        self.select();self.panel.steps.setCurrentIndex(1);self.assertTrue(self.panel.open_position());d=self.panel.position_dialog;self.assertEqual(d.panel.result['route']['key'],'$.routes[10]');self.panel.steps.setCurrentIndex(2);self.assertFalse(d.isVisible());self.assertIsNone(d.panel.result)
    def test_bound_main_action_signal_reaches_exact_original_ordinal(self):
        route=next(r for r in self.panel.result['entries']if r['actions']);self.panel.entries.setCurrentIndex(self.panel.entries.findData(route['key']));self.panel.actions.setCurrentIndex(1);received=[];self.panel.actionSelected.connect(received.append);self.assertTrue(self.panel.follow_action());self.assertEqual(received,[route['actions'][0]['key']])
    def test_unassigned_action_is_not_displayed_as_chosen_route(self):
        self.select();self.panel.unassigned.setCurrentIndex(1);self.assertIsNone(self.panel.selected_route());self.assertIsNone(self.panel.selected_step());self.assertIsNotNone(self.panel.selected_action());self.assertIn('路线尚未确认的出怪',self.panel.player.toPlainText());self.assertFalse(self.panel.position_button.isEnabled());self.assertTrue(self.panel.follow_action())
    def test_same_identity_keeps_search_route_step_action_tab_and_two_readings(self):
        self.select();self.panel.steps.setCurrentIndex(1);key=self.panel.entries.currentData();step=self.panel.steps.currentData()
        for reader in(self.panel.player,self.panel.technical):
            self.panel.tabs.setCurrentWidget(reader);c=reader.textCursor();c.setPosition(10);c.setPosition(28,QTextCursor.MoveMode.KeepAnchor);reader.setTextCursor(c);prior=(c.anchor(),c.position(),c.selectedText());tab=self.panel.tabs.currentIndex();self.assertTrue(self.panel.refresh_reference());now=reader.textCursor();self.assertEqual((now.anchor(),now.position(),now.selectedText()),prior);self.assertEqual(self.panel.tabs.currentIndex(),tab)
        self.assertEqual(self.panel.entries.currentData(),key);self.assertEqual(self.panel.steps.currentData(),step)
    def test_bad_source_clears_actual_owned_map_and_both_readers(self):
        self.select();self.panel.steps.setCurrentIndex(1);self.panel.open_position();d=self.panel.position_dialog
        with patch.object(model,'packet',return_value=None):self.assertFalse(self.panel.refresh_reference())
        self.assertIsNone(self.panel.result);self.assertFalse(d.isVisible());self.assertIsNone(d.panel.result);self.assertEqual(self.panel.technical.toPlainText(),'')
    def test_repaired_source_requires_manual_reselection(self):self.select();self.panel.clear_reference();self.assertTrue(self.panel.refresh_reference());self.assertIsNone(self.panel.selected_route());self.assertFalse(self.panel.action_button.isEnabled())
    def test_forged_snapshot_cannot_jump_or_map(self):
        self.select();self.panel.steps.setCurrentIndex(1);self.panel.result['stage_name']='forged';self.assertFalse(self.panel.open_position());self.assertIsNone(self.panel.result)
    def test_close_and_escape_done_clear_owned_map_actual_data(self):
        for via in('close','reject'):
            d=CurrentRouteItineraryDialog('ro6_n_1_3');d.show();d.panel.entries.setCurrentIndex(d.panel.entries.findData('$.routes[10]'));d.panel.steps.setCurrentIndex(1);d.panel.open_position();m=d.panel.position_dialog;getattr(d,via)();self.app.processEvents();self.assertIsNone(d.panel.result);self.assertFalse(m.isVisible());self.assertIsNone(m.panel.result);d.deleteLater()
