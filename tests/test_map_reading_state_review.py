from copy import deepcopy
from unittest.mock import patch
import unittest
from PySide6.QtWidgets import QApplication,QTreeWidgetItem
from rouge import player_map,player_map_reference
from rouge.player_map_acceptance import fixtures


class MapReadingStateReview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])

    def setUp(self):
        from tests.test_batch185_mainwindow import Batch185WindowTests
        Batch185WindowTests.setUp(self)
        self.graphs,self.node,*_=fixtures();self.window.run.state['maps']={g['zone_id']:g for g in self.graphs}
        self.window.show_compact();self.window.compact_window.open_map();self.p=self.window.compact_window.map_popup.panel
        self.p.view.select_node(self.node);self.p.detail.setFixedSize(400,60);self.qt.processEvents()

    def test_node_lookup_reports_invalid_inputs_and_exposes_internal_errors(self):
        from rouge.node_catalog import NodeQueryError
        p = self.p
        for error in (NodeQueryError('invalid node'), FileNotFoundError('catalog missing')):
            with patch.object(player_map_reference, 'node_dossier', side_effect=error):
                self.assertFalse(p.open_hover_entry(self.node, 'event', 'unused'))
                p.selected(self.node)
                self.assertIn(str(error), p.detail.toPlainText())
                self.assertFalse(p.entries.signalsBlocked())
        for error in (TypeError, KeyError, ValueError):
            with patch.object(player_map_reference, 'node_dossier', side_effect=error('internal')):
                with self.assertRaises(error):
                    p.open_hover_entry(self.node, 'event', 'unused')
                with self.assertRaises(error):
                    p.selected(self.node)
                self.assertFalse(p.entries.signalsBlocked())

    def test_refresh_restores_each_group_once_and_keeps_collapsed_selection(self):
        p=self.p;p.entry_search.setText('桑尼');root=p.entries.topLevelItem(0);p.entries.setCurrentItem(root.child(0));key=p.selected_reference;root.setExpanded(False)
        calls=[]
        class Item(QTreeWidgetItem):
            def setExpanded(self,value):calls.append(self.text(0));super().setExpanded(value)
        with patch.object(player_map,'QTreeWidgetItem',Item):p.refresh()
        self.assertEqual(len(calls),p.entries.topLevelItemCount())
        self.assertEqual(p.selected_reference,key);self.assertFalse(p.entries.topLevelItem(0).isExpanded());self.assertEqual(p.entry_search.text(),'桑尼')

    def test_floor_roundtrip_preserves_node_overview_scroll(self):
        p=self.p;self.assertIsNone(p.selected_reference)
        bar=p.detail.verticalScrollBar();self.assertGreater(bar.maximum(),0);offset=min(40,bar.maximum());bar.setValue(offset)
        original=p.floors.currentIndex();p.floors.setCurrentIndex(1-original);p.floors.setCurrentIndex(original);self.qt.processEvents()
        self.assertEqual(p.view.selected,self.node);self.assertIsNone(p.selected_reference);self.assertEqual(p.detail.verticalScrollBar().value(),offset)

    def test_missing_reference_does_not_restore_its_old_scroll_over_overview(self):
        p=self.p;p.entry_search.setText('桑尼');root=p.entries.topLevelItem(0);p.entries.setCurrentItem(root.child(0));self.qt.processEvents()
        bar=p.detail.verticalScrollBar();self.assertGreater(bar.maximum(),0);bar.setValue(min(40,bar.maximum()))
        dossier=deepcopy(player_map_reference.node_dossier(p.view.graph,self.node,{}))
        for key in ('rows','battle_rows','function_rows','history_observed_event_rows','history_observed_battle_rows','excluded_event_candidates'):dossier[key]=[]
        with patch.object(player_map_reference,'node_dossier',return_value=dossier):p.refresh()
        self.assertIsNone(p.selected_reference);self.assertFalse(p.open_button.isEnabled());self.assertEqual(p.detail.verticalScrollBar().value(),0)

    def test_unconfirmed_node_overview_keeps_its_own_scroll(self):
        p=self.p
        with patch.object(player_map_reference,'node_dossier',return_value=None):
            p.view.select_node(self.node);self.qt.processEvents()
            bar=p.detail.verticalScrollBar();self.assertGreater(bar.maximum(),0);offset=min(12,bar.maximum());bar.setValue(offset)
            p.refresh()
            self.assertEqual(p.detail.verticalScrollBar().value(),offset);self.assertIn('节点类型：待确认',p.detail.toPlainText())


if __name__=='__main__':unittest.main()
