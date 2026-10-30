"""One consistent inventory read and actual rendered, size-aware Qt icons."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
import json
import unittest

from PySide6.QtWidgets import QApplication
from rouge import player_inventory as inventory, view_catalog as pictures


class CatalogRefreshReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gui = QApplication.instance() or QApplication([])

    def test_single_snapshot_updates_held_flags_without_resetting_reader(self):
        run = SimpleNamespace(state={'relics': {}})
        panel = inventory.InventoryPanel(run)
        self.addCleanup(panel.close)
        panel.held.setChecked(False)
        identity = 'rogue_6_relic_legacy_1'
        selected = next(panel.entries.item(i) for i in range(panel.entries.count())
                        if panel.entries.item(i).data(inventory.Qt.ItemDataRole.UserRole) == identity)
        panel.entries.setCurrentItem(selected)
        before = deepcopy(run.state)
        with patch.object(inventory, 'inventory_rows', wraps=inventory.inventory_rows) as read:
            panel.refresh()
        self.assertEqual(read.call_count, 1)
        self.assertIs(panel.entries.currentItem(), selected)
        self.assertEqual(run.state, before)
        run.state['relics'][identity] = {'held': True}
        panel.refresh()
        self.assertTrue(panel.rows[identity]['held'])
        self.assertEqual(panel.entries.currentItem().data(inventory.Qt.ItemDataRole.UserRole), identity)
        self.assertIn(panel.rows[identity]['name'], panel.detail.toPlainText())
        with patch.object(inventory.reference, 'packet', return_value=None):
            panel.refresh()
        self.assertEqual(panel.entries.count(), 0)
        self.assertEqual(panel.detail.toPlainText(), '')

    def test_all_catalog_icons_really_render_at_normal_and_higher_density_sizes(self):
        selections = [(kind, identity) for kind, group in (
            ('operator', 'operators'), ('enemy', 'enemies'))
            for identity in pictures.view_catalog()[group]]
        selections += [('skill', key) for key in pictures.skill_catalog()['skills']]
        selections += [('profession', key) for key in pictures.profession_catalog()['professions']]
        for kind, identity in selections:
            icon = pictures.portrait_icon(kind, identity)
            if pictures.portrait_record(kind, identity) is None:
                self.assertTrue(icon.isNull(), (kind, identity))
                continue  # Existing explicit missing-picture entries stay unbound.
            for edge in (28, 56):
                pixmap = icon.pixmap(edge, edge)
                self.assertFalse(pixmap.isNull(), (kind, identity, edge))
                logical = pixmap.deviceIndependentSize()
                self.assertLessEqual(max(logical.width(), logical.height()), edge)
        self.assertTrue(pictures.portrait_icon('operator', 'not-an-operator').isNull())

    def test_missing_image_does_not_become_another_subject(self):
        with TemporaryDirectory() as folder, patch.object(pictures, 'DATA', Path(folder)):
            self.assertTrue(pictures.portrait_icon('operator', 'mechanist').isNull())
            # A file-backed QIcon's isNull is not an image-integrity check.
            record = pictures.portrait_record('operator', 'mechanist')
            self.assertIsNotNone(record)
            path = Path(folder) / record['file']
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'not an image')
            self.assertTrue(pictures.portrait_icon('operator', 'mechanist').pixmap(28, 28).isNull())

    def test_shared_artwork_keeps_all_variant_names_effects_and_hover_identity(self):
        from PySide6.QtGui import QIcon
        mapping = json.loads((pictures.DATA/'relic-reference-equivalence.json').read_bytes())
        rows = {r['id']: r for r in inventory.inventory_rows({}, held_only=False)}
        count = 0
        for family in mapping['families'].values():
            expected = QIcon(str(pictures.DATA/family['file'])).pixmap(46, 46).toImage()
            for identity in family['ids'][1:]:
                self.assertEqual(pictures.relic_icon(identity).pixmap(46, 46).toImage(), expected)
                self.assertEqual(rows[identity]['id'], identity)
                self.assertNotEqual(rows[identity]['name'], rows[family['ids'][0]]['name'])
                count += 1
        self.assertEqual(count, 39)
        self.assertTrue(pictures.relic_icon('rogue_6_relic_legacy_22_not_a_real_tier').isNull())
        panel = inventory.InventoryPanel(SimpleNamespace(state={}))
        self.addCleanup(panel.close)
        identity = 'rogue_6_relic_legacy_22_a'
        row = rows[identity]
        self.assertTrue(panel.hover_card.install(row, panel.version.currentData(),
            panel.source_index, panel.source_signature))
        self.assertEqual(panel.hover_card.identity, identity)
        self.assertEqual(panel.hover_card.title.text(), row['name'])
        self.assertFalse(panel.hover_card.picture.pixmap().isNull())


if __name__ == '__main__':
    unittest.main()
