from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock, patch
from rouge.player_map import MapPanel


class ManualCatalogTests(TestCase):
    def panel(self, kind='battle'):
        key=('资料',kind,'public-id')
        return SimpleNamespace(
            selected_reference=key, reader_binding=Mock(return_value=('same-node',)),
            refresh=Mock(), rows={key:{'id':'public-id'}}, close_reference=Mock(),
            view=SimpleNamespace(historical=False), page_owner=None,
            owner=Mock(run=SimpleNamespace(state={'config':{}})))

    def test_cancel_does_not_open_or_activate_catalog(self):
        panel=self.panel()
        with patch('rouge.player_map_reader.make_reader',return_value=None), patch('rouge.player_map.QMessageBox') as box:
            box.return_value.clickedButton.return_value=None
            self.assertFalse(MapPanel.open_entry(panel))
        self.assertEqual(panel.owner.mock_calls,[])
        self.assertEqual(panel.refresh.call_count,1)

    def test_manual_choice_routes_exact_identity_after_recheck(self):
        for kind,method in [('battle','show_catalog_battle'),('event','show_source_catalog_event')]:
            with self.subTest(kind=kind):
                panel=self.panel(kind)
                with patch('rouge.player_map_reader.make_reader',return_value=None), patch('rouge.player_map.QMessageBox') as box:
                    box.return_value.clickedButton.return_value=box.return_value.addButton.return_value
                    self.assertTrue(MapPanel.open_entry(panel))
                getattr(panel.owner,method).assert_called_once_with('public-id')
                panel.owner.show.assert_called_once()
                panel.owner.activateWindow.assert_called_once()
                self.assertEqual(panel.refresh.call_count,2)

    def test_changed_binding_during_dialog_does_not_open_old_entry(self):
        panel=self.panel()
        panel.reader_binding.side_effect=[('same-node',),('same-node',),('new-node',)]
        with patch('rouge.player_map_reader.make_reader',return_value=None), patch('rouge.player_map.QMessageBox') as box:
            box.return_value.clickedButton.return_value=box.return_value.addButton.return_value
            self.assertFalse(MapPanel.open_entry(panel))
        self.assertEqual(panel.owner.mock_calls,[])

    def test_available_reader_does_not_prompt_for_catalog(self):
        panel=self.panel();panel.page_owner=Mock();panel.prepare_reference=Mock()
        popup=Mock()
        with patch('rouge.player_map_reader.make_reader',return_value=popup), patch('rouge.player_map.QMessageBox') as box:
            MapPanel.open_entry(panel)
        box.assert_not_called()
        panel.page_owner.present.assert_called_once_with(popup)
        self.assertEqual(panel.owner.mock_calls,[])
