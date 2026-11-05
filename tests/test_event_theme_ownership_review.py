"""The constructed reader owns its final theme, across both public entry paths."""
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtWidgets import QApplication
from rouge import player_theme, current_event_directory, current_node_readers
from rouge.current_event_directory_view import make_event_dialog
from rouge.current_node_readers_view import READERS, make_dialog
from rouge.player_map_reader import REFERENCE_STYLE


class EventThemeOwnershipTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def setUp(self):
        self.addCleanup(QCoreApplication.sendPostedEvents, None, QEvent.Type.DeferredDelete)

    def test_all_directory_reader_families_own_one_final_theme_and_exact_target(self):
        seen = set()
        for row in current_event_directory.reference()['rows']:
            if row['reader'] in seen:
                continue
            seen.add(row['reader'])
            with self.subTest(reader=row['reader']):
                target = current_event_directory.resolve(current_event_directory.reference(row['id']), row['entries'][-1]['key'])
                with patch.object(player_theme, 'apply_theme', wraps=player_theme.apply_theme) as apply:
                    dialog = make_event_dialog(target)
                self.assertIsNotNone(dialog)
                self.addCleanup(dialog.deleteLater)
                self.addCleanup(dialog.close)
                self.assertEqual(sum(c.args[0] is dialog for c in apply.call_args_list), 1)
                self.assertEqual(dialog.styleSheet(), player_theme.assets('reference')[0] + REFERENCE_STYLE)
                self.assertEqual((dialog.panel.scene_id, dialog.panel.choice_id), (target['scene_id'], target['choice_id']))
                dialog.close()
        self.assertEqual(len(seen), 21)

    def test_all_node_reader_families_own_one_final_theme_and_exact_binding(self):
        records = json.loads((Path(__file__).resolve().parents[1] / 'rouge/data/node-catalog.json').read_bytes())['events']
        seen = set()
        for record in records:
            binding = current_node_readers.binding_for(record)
            if binding is None or binding['reader'] in seen:
                continue
            seen.add(binding['reader'])
            with self.subTest(reader=binding['reader']):
                with patch.object(player_theme, 'apply_theme', wraps=player_theme.apply_theme) as apply:
                    dialog = make_dialog(binding)
                self.assertIsNotNone(dialog)
                self.addCleanup(dialog.deleteLater)
                self.addCleanup(dialog.close)
                self.assertEqual(sum(c.args[0] is dialog for c in apply.call_args_list), 1)
                self.assertEqual(dialog.property('playerThemeVariant'), 'reference')
                self.assertTrue(current_node_readers.matches_current(binding, dialog.panel.result))
                dialog.close()
        self.assertEqual(seen, set(READERS))


if __name__ == '__main__':
    unittest.main()
