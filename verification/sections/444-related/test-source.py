"""Clickable exact source cards and picture-backed item reading without empty maps."""
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch
import unittest
from PySide6.QtCore import Qt
from PySide6.QtTest import QSignalSpy
from PySide6.QtWidgets import QApplication
from rouge.player_inventory import InventoryPanel
from rouge.expansion_view import ExpansionUpdatePanel
from rouge.view_catalog import relic_icon

IDS=('rogue_6_relic_legacy_1','rogue_6_relic_legacy_3')
def choose(panel,identity):
    item=next(panel.entries.item(i)for i in range(panel.entries.count())if panel.entries.item(i).data(Qt.ItemDataRole.UserRole)==identity)
    panel.entries.setCurrentItem(item);return item

class ItemReading444Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.qt=QApplication.instance()or QApplication([])
    def inventory(self):
        run=SimpleNamespace(state={'relics':{key:{} for key in IDS}})
        panel=InventoryPanel(run);self.addCleanup(panel.close);panel.show();self.qt.processEvents();return panel
    def reader(self,categories=('relics','scrap')):
        panel=ExpansionUpdatePanel(categories=categories,full_catalog=True);self.addCleanup(panel.close)
        panel.show();self.qt.processEvents();return panel
    def test_source_button_is_disabled_until_an_exact_item_is_selected(self):
        panel=self.inventory();self.assertFalse(panel.source_button.isEnabled());choose(panel,IDS[0]);self.assertTrue(panel.source_button.isEnabled())
    def test_click_pins_existing_source_card_without_opening_full_reader(self):
        panel=self.inventory();before=deepcopy(panel.run.state);choose(panel,IDS[0]);signal=QSignalSpy(panel.openReference)
        panel.source_button.click();self.qt.processEvents()
        self.assertTrue(panel.hover_card.isVisible());self.assertTrue(panel.hover_card.pinned)
        self.assertEqual(panel.hover_card.identity,IDS[0]);self.assertEqual(signal.count(),0);self.assertEqual(panel.run.state,before)
        self.assertFalse(panel.hover_card.picture.pixmap().isNull())
    def test_pinned_card_reading_survives_refresh_and_explicit_other_item_replaces_it(self):
        panel=self.inventory();choose(panel,IDS[0]);panel.source_button.click();card=panel.hover_card
        old=card.pools.currentData();text=card.detail.toPlainText();panel.refresh()
        self.assertTrue(card.pinned);self.assertEqual(card.pools.currentData(),old);self.assertEqual(card.detail.toPlainText(),text)
        choose(panel,IDS[1]);panel.source_button.click();self.assertEqual(card.identity,IDS[1]);self.assertTrue(card.pinned)
    def test_source_loss_clears_card_and_disables_both_actions_without_reset(self):
        panel=self.inventory();choose(panel,IDS[0]);panel.source_button.click();before=deepcopy(panel.run.state)
        with patch('rouge.player_inventory.reference.packet',return_value=None):panel.source_button.click()
        self.assertFalse(panel.hover_card.isVisible());self.assertIsNone(panel.hover_card.identity)
        self.assertFalse(panel.source_button.isEnabled());self.assertFalse(panel.reference_button.isEnabled());self.assertEqual(panel.run.state,before)
    def test_explicit_full_reference_action_keeps_the_original_exact_id_signal(self):
        panel=self.inventory();choose(panel,IDS[1]);signal=QSignalSpy(panel.openReference);panel.reference_button.click()
        self.assertEqual(signal.count(),1);self.assertEqual(signal.at(0),[IDS[1]])
    def test_item_reader_has_exact_relic_and_part_images_and_no_empty_map(self):
        panel=self.reader();choose(panel,IDS[0]);self.assertTrue(panel.map_image.isHidden())
        self.assertFalse(panel.entries.currentItem().icon().pixmap(36,36).isNull())
        panel.category.setCurrentIndex(panel.category.findData('scrap'));choose(panel,'rogue_6_scrap_G_05')
        actual=panel.entries.currentItem().icon().pixmap(36,36).toImage()
        self.assertEqual(actual,relic_icon('rogue_6_scrap_G_05').pixmap(36,36).toImage());self.assertTrue(panel.map_image.isHidden())
    def test_real_stage_picture_returns_after_reading_an_item_and_source_loss_hides_it(self):
        panel=self.reader(('stages','relics'));choose(panel,'ro6_n_7_1');raw=panel.image_raw
        self.assertTrue(panel.map_image.isVisible());self.assertIsNotNone(raw)
        panel.category.setCurrentIndex(panel.category.findData('relics'));choose(panel,IDS[0]);self.assertTrue(panel.map_image.isHidden())
        panel.category.setCurrentIndex(panel.category.findData('stages'));choose(panel,'ro6_n_7_1')
        self.assertTrue(panel.map_image.isVisible());self.assertEqual(panel.image_raw,raw)
        with patch('rouge.expansion_view.model.packet',return_value=None):panel.refresh_reference()
        self.assertTrue(panel.map_image.isHidden());self.assertIsNone(panel.result)
    def test_declared_but_unavailable_map_keeps_its_failure_explanation(self):
        panel=self.reader(('stages',));choose(panel,'ro6_n_7_1')
        with patch('rouge.expansion_view.model.image_bytes',return_value=None):panel.refresh_reference()
        self.assertTrue(panel.map_image.isVisible());self.assertIsNone(panel.image_raw)

    def test_group_reference_picture_is_disclosed_in_full_reader(self):
        panel=self.reader();choose(panel,'rogue_6_legacy_01_1')
        self.assertIn('独立图样尚未核验',panel.entries.currentItem().toolTip())
        self.assertIn('图片说明',panel.player.toPlainText())
        self.assertIn('不据此判断实际持有或效果',panel.player.toPlainText())

if __name__=='__main__':unittest.main()

