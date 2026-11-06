from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QApplication, QPushButton
from rouge import current_ritual_view as view, player_reference_links as links, current_exchange_reference as offers


class MaterialFailureReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.qt = QApplication.instance() or QApplication([])

    def test_standalone_failed_target_does_not_requery(self):
        panel = SimpleNamespace(_recheck=lambda: True, result={'kept': True}, scene_id='scene', choice_id='choice', _close_material=Mock(), _sync_extra=Mock(), material_button=QPushButton())
        panel.material_button.show()
        source = {'kind': 'exchange', 'source_choice_id': 'choice'}
        with patch.object(view.model, 'acquisition_reference', return_value=source), patch.object(links, 'open_material_source', return_value=None), patch.object(offers, 'target_entry', return_value=None) as locate:
            self.assertFalse(view.CurrentRitualPanel.open_material(panel))
        locate.assert_called_once_with('choices', 'choice')
        panel._sync_extra.assert_not_called()
        panel._close_material.assert_called_once_with()
        self.assertTrue(panel.material_button.isHidden())
        self.assertFalse(panel.material_button.isEnabled())
        self.assertEqual(panel.result, {'kept': True})

    def test_shared_failed_target_does_not_requery(self):
        class Host: pass
        panel = SimpleNamespace(window=lambda: Host(), _close_material=Mock(), _sync_extra=Mock(), material_button=QPushButton(), result={'kept': True})
        panel.material_button.show()
        with patch.object(links, 'ReferenceWindow', Host), patch.object(offers, 'target_entry', return_value=None) as locate:
            self.assertFalse(links.open_material_source(panel, {'kind': 'exchange', 'source_choice_id': 'choice'}))
        locate.assert_called_once_with('choices', 'choice')
        panel._sync_extra.assert_not_called()
        panel._close_material.assert_called_once_with()
        self.assertTrue(panel.material_button.isHidden())
        self.assertFalse(panel.material_button.isEnabled())
        self.assertEqual(panel.result, {'kept': True})
