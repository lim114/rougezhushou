from types import SimpleNamespace
from unittest.mock import Mock, patch
import unittest
from rouge import current_enemy_spawns_view as view


class EnemyActionBoundaryTests(unittest.TestCase):
    def test_no_selection_does_not_resolve_or_clear(self):
        owner = SimpleNamespace(selected=lambda: None, clear_reference=Mock())
        with patch.object(view.model, 'resolve_action') as resolve:
            self.assertFalse(view.CurrentEnemySpawnsPanel.follow_action(owner))
            resolve.assert_not_called()
        owner.clear_reference.assert_not_called()

    def test_selected_snapshot_resolved_once_and_emitted(self):
        owner = SimpleNamespace(selected=lambda: {'key': 'entry'}, result={'source': 'verified'}, clear_reference=Mock(), actionSelected=Mock())
        with patch.object(view.model, 'resolve_action', return_value={'action_key': 'exact-action'}) as resolve:
            self.assertTrue(view.CurrentEnemySpawnsPanel.follow_action(owner))
            resolve.assert_called_once_with(owner.result, 'entry')
        owner.actionSelected.emit.assert_called_once_with('exact-action')
        owner.clear_reference.assert_not_called()

    def test_invalidated_action_clears_once_without_signal(self):
        owner = SimpleNamespace(selected=lambda: {'key': 'entry'}, result={'source': 'stale'}, clear_reference=Mock(), actionSelected=Mock())
        with patch.object(view.model, 'resolve_action', return_value=None) as resolve:
            self.assertFalse(view.CurrentEnemySpawnsPanel.follow_action(owner))
            resolve.assert_called_once_with(owner.result, 'entry')
        owner.clear_reference.assert_called_once_with()
        owner.actionSelected.emit.assert_not_called()
