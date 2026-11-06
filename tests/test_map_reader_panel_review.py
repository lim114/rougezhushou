from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock, patch
from rouge.player_map import MapPanel


class ReaderPanelTests(TestCase):
    def owner(self, panel, kind='event'):
        popup=SimpleNamespace(panel=panel,isVisible=lambda:True)
        return SimpleNamespace(reference_popup=popup,reference_binding=('same',),
            reader_binding=lambda:('same',),close_reference=Mock(),
            selected_reference=('资料',kind,'identity'),view=SimpleNamespace(historical=False),
            owner=SimpleNamespace(run=SimpleNamespace(state={'config':{'difficulty':2}})))

    def test_plain_event_panel_needs_no_refresh_method(self):
        owner=self.owner(SimpleNamespace())
        MapPanel.check_reference(owner)
        owner.close_reference.assert_not_called()

    def test_refresh_failure_closes_and_success_keeps_battle_context(self):
        for valid in (False,True):
            with self.subTest(valid=valid):
                panel=SimpleNamespace(refresh_reference=Mock(return_value=valid),set_context=Mock())
                owner=self.owner(panel,'battle')
                MapPanel.check_reference(owner)
                panel.refresh_reference.assert_called_once()
                if valid:
                    owner.close_reference.assert_not_called()
                    panel.set_context.assert_called_once_with({'difficulty':2})
                else:
                    owner.close_reference.assert_called_once()
                    panel.set_context.assert_not_called()

    def test_stale_event_binding_closes_before_panel_access(self):
        owner=self.owner(SimpleNamespace())
        owner.reference_popup.node_reference_binding={'identity':'public'}
        with patch('rouge.current_node_readers.recheck',return_value=None) as recheck:
            MapPanel.check_reference(owner)
        recheck.assert_called_once_with({'identity':'public'})
        owner.close_reference.assert_called_once()

    def test_missing_required_panel_is_not_silently_ignored(self):
        owner=self.owner(SimpleNamespace())
        del owner.reference_popup.panel
        with self.assertRaises(AttributeError):MapPanel.check_reference(owner)
