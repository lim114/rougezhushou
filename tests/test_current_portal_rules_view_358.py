"""Manual rule/region branches, relevant controls, reading and source recovery."""
import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
from copy import deepcopy
import unittest
from unittest.mock import patch
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from rouge import current_portal_rules as model
from rouge.current_portal_rules_view import CurrentPortalRulesPanel


class CurrentPortalRulesView358Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.reference = model.reference()
        if cls.reference is None: raise AssertionError('Installed current source is required, not skipped.')

    def setUp(self):
        self.query = patch.object(model, 'reference', side_effect=lambda: deepcopy(self.reference))
        self.query.start(); self.widget = CurrentPortalRulesPanel()
        self.widget.resize(780, 620); self.widget.show(); self.app.processEvents()

    def tearDown(self):
        self.widget.close(); self.widget.deleteLater(); self.app.processEvents(); self.query.stop()

    def choose(self, key):
        for index in range(self.widget.entries.count()):
            item = self.widget.entries.item(index)
            if item.data(Qt.ItemDataRole.UserRole) == key:
                self.widget.entries.setCurrentItem(item); self.app.processEvents(); return
        self.fail('Concrete requested row is missing: ' + key)

    def test_initial_directory_and_red_fog_do_not_choose_a_rule(self):
        self.assertEqual(self.widget.entries.count(), 9)
        self.assertIsNone(self.widget.selected_key)
        self.assertTrue(self.widget.floor_controls.isHidden())
        self.assertTrue(self.widget.refresh_controls.isHidden())
        self.widget.fog.setCurrentIndex(self.widget.fog.findData('红雾'))
        self.assertEqual(self.widget.entries.count(), 4)
        self.assertIsNone(self.widget.selected_key)
        self.assertIn('四种候选之一', self.widget.player.toPlainText())

    def test_rule_specific_conditions_never_appear_on_unrelated_rules(self):
        self.choose('variation_7')
        self.assertFalse(self.widget.floor_controls.isHidden())
        self.assertTrue(self.widget.refresh_controls.isHidden())
        self.widget.floor.setCurrentIndex(self.widget.floor.findData(3))
        self.assertIn('不在文献列出的', self.widget.player.toPlainText())
        self.choose('variation_5')
        self.assertTrue(self.widget.floor_controls.isHidden())
        self.assertFalse(self.widget.refresh_controls.isHidden())
        self.assertTrue(self.widget.shop_controls.isHidden())
        self.widget.node_type.setCurrentIndex(self.widget.node_type.findData('BATTLE_SHOP'))
        self.assertFalse(self.widget.shop_controls.isHidden())
        self.widget.completed_shop.setCurrentIndex(self.widget.completed_shop.findData(True))
        self.assertIn('不参加这条刷新规则', self.widget.player.toPlainText())
        self.choose('variation_1')
        self.assertTrue(self.widget.floor_controls.isHidden())
        self.assertTrue(self.widget.refresh_controls.isHidden())

    def test_refresh_preserves_rule_inputs_tab_and_two_nonzero_readings(self):
        self.choose('variation_8')
        self.widget.floor.setCurrentIndex(self.widget.floor.findData(4))
        self.widget.resize(620, 350); self.app.processEvents()
        before = []
        for index, reader in enumerate((self.widget.player, self.widget.technical)):
            self.widget.tabs.setCurrentIndex(index); self.app.processEvents()
            bar = reader.verticalScrollBar(); self.assertGreater(bar.maximum(), 0)
            bar.setValue(max(1, bar.maximum() // 2)); before.append(bar.value())
        self.assertTrue(self.widget.refresh_reference()); self.app.processEvents()
        self.assertEqual(self.widget.selected_key, 'variation_8')
        self.assertEqual(self.widget.floor.currentData(), 4)
        self.assertEqual(self.widget.tabs.currentIndex(), 1)
        self.assertEqual([reader.verticalScrollBar().value() for reader in (self.widget.player, self.widget.technical)], before)

    def test_region_branch_preserves_all_nineteen_names_and_three_tables_without_fog(self):
        self.widget.branch.setCurrentIndex(self.widget.branch.findData('refresh'))
        self.assertEqual(self.widget.entries.count(), 19)
        self.assertTrue(self.widget.fog.isHidden())
        self.choose('zone_portal_normal_5_1')
        self.assertIn('不期而遇', self.widget.player.toPlainText())
        self.assertIn('不是所有乌托邦的通用节点池', self.widget.player.toPlainText())
        self.choose('zone_portal_normal_1_1')
        self.assertIn('未列独立刷新表', self.widget.player.toPlainText())
        self.assertTrue(self.widget.floor_controls.isHidden())

    def test_source_loss_closes_owned_source_and_recovery_requires_manual_choice(self):
        self.choose('variation_6')
        for index in range(self.widget.source_combo.count()):
            request = self.widget.source_combo.itemData(index)
            if request and request['kind'] == 'item': self.widget.source_combo.setCurrentIndex(index); break
        self.assertTrue(self.widget.open_source()); child = self.widget.link_dialog
        self.assertIsNotNone(child)
        with patch.object(model, 'reference', return_value=None):
            self.assertFalse(self.widget.refresh_reference())
        self.app.processEvents()
        self.assertFalse(child.isVisible())
        self.assertIsNone(self.widget.result)
        self.assertEqual(self.widget.technical.toPlainText(), '')
        self.assertFalse(self.widget.source_button.isEnabled())
        self.assertTrue(self.widget.refresh_reference())
        self.assertIsNone(self.widget.selected_key)
        self.assertIsNone(self.widget.floor.currentData())
        self.assertIsNone(self.widget.completed_shop.currentData())

    def test_foreign_link_does_not_open_old_source(self):
        self.choose('variation_5')
        self.widget.source_combo.setCurrentIndex(1)
        with patch.object(model, 'resolve_link', return_value=None):
            self.assertFalse(self.widget.open_source())
        self.assertIsNone(self.widget.result)
        self.assertIsNone(self.widget.link_dialog)


if __name__ == '__main__': unittest.main()
