from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import sys
import unittest
from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QApplication

ROOT = next(path for path in Path(__file__).resolve().parents if (path/'rouge/__init__.py').is_file())
WORK = Path(__file__).resolve().parent
if (WORK/'movement_source_view.py').is_file():
    for name in ('movement_source_planning', 'movement_source_view'):
        specification = importlib.util.spec_from_file_location('rouge.' + name, WORK/(name+'.py'))
        module = importlib.util.module_from_spec(specification)
        sys.modules[specification.name] = module
        specification.loader.exec_module(module)
        if name == 'movement_source_planning':
            module.DATA = WORK/'data'
    planning = sys.modules['rouge.movement_source_planning']
    view = sys.modules['rouge.movement_source_view']
else:
    from rouge import movement_source_planning as planning, movement_source_view as view

M04 = 'rogue_6_scrap_M_04'
M08 = 'rogue_6_scrap_M_08'
M11 = 'rogue_6_scrap_M_11'


class MovementSourceViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.panel = view.MovementSourcePanel()
        self.panel.show()
        self.app.processEvents()

    def tearDown(self):
        self.panel.close()
        self.panel.deleteLater()
        self.app.processEvents()

    def select_row(self, channel, node=None, history=False, item_id=None):
        for i in range(self.panel.sources.topLevelItemCount()):
            group = self.panel.sources.topLevelItem(i)
            for j in range(group.childCount()):
                item = group.child(j)
                key = json.loads(item.data(0, Qt.ItemDataRole.UserRole))
                if key[2] == channel and key[3] == history and (node is None or key[1] == node) and (item_id is None or key[0] == item_id):
                    self.panel.sources.setCurrentItem(item)
                    return item
        self.fail('missing source row ' + channel)

    def test_goal_checklist_retains_owned_goal_and_distinguishes_presence_from_quantity(self):
        self.assertEqual(self.panel.targets.topLevelItemCount(), 12)
        self.panel.set_reference([M04], context={'item_presence': {M04: True}})
        self.assertEqual(self.panel.target_ids(), [M04])
        self.assertEqual(len(self.panel.result['rows']), 6)
        self.assertIn('件数未知', self.panel.sources.topLevelItem(0).text(0))
        self.panel.set_context({'item_quantities': {M04: 2}})
        self.assertEqual(self.panel.target_ids(), [M04])
        self.assertIn('2件', self.panel.sources.topLevelItem(0).text(0))
        self.panel.targets.topLevelItem(3).setCheckState(0, Qt.CheckState.Unchecked)
        self.assertEqual(self.panel.target_ids(), [])
        self.assertEqual(self.panel.result['rows'], [])

    def test_shop_controls_require_explicit_quote_and_do_not_update_inventory(self):
        context = {'node_type': '秘境行商', 'gold': 6, 'item_quantities': {M04: 0}}
        snapshot = deepcopy(context)
        self.panel.set_reference([M04], context=context)
        self.select_row('scrap_shop')
        self.assertEqual(self.panel.price.value(), -1)
        self.assertFalse(self.panel.unmodified.isChecked())
        self.panel.access.setCurrentIndex(self.panel.access.findData(True))
        self.panel.stock.setCurrentIndex(self.panel.stock.findData(True))
        self.assertEqual(self.panel.selected_row()['status'], 'unknown')
        self.panel.unmodified.setChecked(True)
        self.assertEqual(self.panel.selected_row()['status'], 'matched')
        self.assertEqual(self.panel.selected_row()['comparison_price_reference'], 6)
        self.assertEqual(context, snapshot)
        self.assertFalse(self.panel.result['inventory_updated'])
        self.assertFalse(self.panel.result['run_state_updated'])

    def test_contradictory_price_edit_shows_error_and_remains_recoverable(self):
        self.panel.set_reference([M04], context={'node_type': '秘境行商', 'gold': 6})
        self.select_row('scrap_shop')
        self.panel.unmodified.setChecked(True)
        self.panel.price.setValue(5)
        self.assertIn('矛盾', self.panel.detail.toPlainText())
        self.assertIsNotNone(self.panel.selected_row())
        self.assertTrue(self.panel.price.isEnabled())
        self.panel.unmodified.setChecked(False)
        self.assertEqual(self.panel.selected_row()['comparison_price_reference'], 5)
        self.assertEqual(self.panel.selected_row()['comparison_price_source'], 'independent_declared_price')

    def test_seed_controls_are_independent_and_same_source_node_declarations_survive_target_switch(self):
        graph = {'zone_id': 'z', 'template_id': 't', 'nodes': [{'id': 's', 'row': 0, 'col': 0, 'observed_type': '秘境行商'}]}
        self.panel.set_reference([M04, M08], graph, epoch=1)
        self.select_row('seed', 's', item_id=M04)
        self.assertTrue(self.panel.seed.isEnabled())
        self.assertFalse(self.panel.price.isEnabled())
        self.panel.access.setCurrentIndex(self.panel.access.findData(True))
        self.panel.seed.setCurrentIndex(self.panel.seed.findData(True))
        self.panel.completion.setCurrentIndex(self.panel.completion.findData(True))
        self.assertEqual(self.panel.selected_row()['status'], 'matched')
        self.select_row('seed', 's', item_id=M08)
        self.assertEqual(self.panel.selected_row()['status'], 'matched')
        self.select_row('scrap_shop', 's', item_id=M08)
        self.panel.stock.setCurrentIndex(self.panel.stock.findData(True))
        self.select_row('scrap_shop', 's', item_id=M04)
        self.assertIsNone(self.panel.selected_row()['stock_presence_declared'])

    def test_exact_map_preview_and_three_independent_same_title_catalogue_signals(self):
        graph = {'zone_id': 'z', 'template_id': 't', 'nodes': [{'id': 'e', 'row': 2, 'col': 4, 'observed_type': '险路小径'}]}
        self.panel.set_reference([M08], graph, epoch=5)
        self.select_row('path_exit', 'e')
        positions, catalogues = [], []
        self.panel.mapNodeSelected.connect(lambda key, binding: positions.append((key, binding)))
        self.panel.catalogEventSelected.connect(catalogues.append)
        self.panel.map_button.click()
        self.assertEqual(positions, [('e', {'node_id': 'e', 'row': 2, 'col': 4, 'zone_id': 'z', 'template_id': 't', 'epoch': 5})])
        self.assertEqual(self.panel.catalogue.count(), 3)
        self.assertEqual(len({self.panel.catalogue.itemText(i) for i in range(3)}), 3)
        for i in range(3):
            self.panel.catalogue.setCurrentIndex(i)
            self.panel.catalogue_button.click()
        self.assertEqual(catalogues, ['community_group_034', 'community_group_035', 'community_group_036'])
        self.assertFalse(self.panel.result['source_origin_gap_closed'])

    def test_historical_shop_disables_controls_and_never_borrows_current_budget(self):
        graph = {'nodes': [{'id': 'old', 'row': 1, 'col': 0, 'observed_type': '林间空地', 'remembered_type': '秘境行商'}]}
        self.panel.set_reference([M04], graph, {'gold': 99}, epoch=2)
        self.select_row('scrap_shop', 'old', True)
        self.assertEqual(self.panel.selected_row()['status'], 'history_only')
        self.assertIsNone(self.panel.selected_row()['gold_declared'])
        for control in (self.panel.access, self.panel.stock, self.panel.price, self.panel.gold, self.panel.unmodified):
            self.assertFalse(control.isEnabled())
        self.assertTrue(self.panel.map_button.isEnabled())

    def test_refresh_preserves_goal_selection_collapsed_groups_reading_and_ephemeral_declarations(self):
        graph = {'zone_id': 'z', 'template_id': 't', 'nodes': [{'id': 's', 'row': 0, 'col': 0, 'observed_type': '秘境行商'}]}
        self.panel.set_reference([M04], graph, {'gold': 6}, epoch=9)
        self.select_row('scrap_shop', 's')
        self.panel.stock.setCurrentIndex(self.panel.stock.findData(True))
        self.panel.unmodified.setChecked(True)
        group = self.panel.sources.topLevelItem(0)
        group.setExpanded(False)
        cursor = self.panel.detail.textCursor()
        cursor.setPosition(5)
        cursor.setPosition(16, QTextCursor.MoveMode.KeepAnchor)
        self.panel.detail.setTextCursor(cursor)
        self.panel.detail.verticalScrollBar().setValue(3)
        key = self.panel.selected_key()
        text_state = (cursor.anchor(), cursor.position(), self.panel.detail.verticalScrollBar().value())
        self.panel.set_map_context(deepcopy(graph), {'gold': 6}, epoch=9)
        self.assertEqual(self.panel.target_ids(), [M04])
        self.assertEqual(self.panel.selected_key(), key)
        self.assertFalse(self.panel.sources.topLevelItem(0).isExpanded())
        cursor = self.panel.detail.textCursor()
        self.assertEqual((cursor.anchor(), cursor.position(), self.panel.detail.verticalScrollBar().value()), text_state)
        self.assertTrue(self.panel.stock.currentData())
        self.assertTrue(self.panel.unmodified.isChecked())

    def test_epoch_and_changed_node_identity_do_not_reuse_old_stock_declarations(self):
        graph = {'zone_id': 'z', 'template_id': 't', 'nodes': [{'id': 's', 'row': 0, 'col': 0, 'observed_type': '秘境行商'}]}
        self.panel.set_reference([M04], graph, epoch=9)
        self.select_row('scrap_shop', 's')
        self.panel.stock.setCurrentIndex(self.panel.stock.findData(True))
        self.panel.set_map_context(graph, epoch=10)
        self.select_row('scrap_shop', 's')
        self.assertIsNone(self.panel.selected_row()['stock_presence_declared'])
        self.panel.set_map_context(graph, epoch=9)
        self.select_row('scrap_shop', 's')
        self.assertTrue(self.panel.selected_row()['stock_presence_declared'])
        changed = deepcopy(graph)
        changed['nodes'][0]['col'] = 1
        self.panel.set_map_context(changed, epoch=9)
        self.select_row('scrap_shop', 's')
        self.assertIsNone(self.panel.selected_row()['stock_presence_declared'])


if __name__ == '__main__':
    unittest.main()
