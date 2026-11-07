import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from rouge.player_source_map import targets, companion
from rouge.player_item_sources import ItemSourceIndex
from rouge.current_sand_view import CurrentSandPanel
from tests.test_player_item_sources_394 import fixture


class SourceNavigationBoundaryReview(unittest.TestCase):
    def test_pool_validation_leaves_node_bindings_opaque(self):
        data = fixture()
        data['versions']['base'][0]['nodeBindings'] = [None, 'bad', {'nodeType':'BATTLE_NORMAL','nodeName':'wrong'}, {'nodeType':'BATTLE_NORMAL','nodeName':'作战'}, {'nodeType':'BATTLE_NORMAL','nodeName':'作战'}]
        index = ItemSourceIndex(data)
        self.assertEqual(targets(index, 'base', 'a', 'pool1'), ['作战'])
        self.assertEqual(targets(index, 'base', 'a', 'absent'), [])
        self.assertEqual(targets(None, 'base', 'a', 'pool1'), [])

    def test_optional_host_lookup_keeps_standalone_and_parent_protocol(self):
        self.assertIsNone(companion(SimpleNamespace(parentWidget=lambda:None)))
        owner = SimpleNamespace(open_map=Mock(), map_popup=None)
        self.assertIs(companion(SimpleNamespace(parentWidget=lambda:owner)), owner)
        self.assertIs(companion(SimpleNamespace(compact_window=owner)), owner)

    def test_related_target_missing_closes_once_without_constructing(self):
        owner = SimpleNamespace(_recheck=lambda:True, _close_related=Mock())
        with patch('rouge.box_event_reference.locate', return_value=None), patch('rouge.box_event_view.BoxEventDialog') as dialog:
            self.assertFalse(CurrentSandPanel.open_related(owner))
            owner._close_related.assert_called_once_with()
            dialog.assert_not_called()

    def test_related_target_present_closes_then_opens_exact_scene(self):
        calls = []
        owner = SimpleNamespace(_recheck=lambda:True, _close_related=lambda:calls.append('close'))
        child = SimpleNamespace(show=lambda:calls.append('show'))
        with patch('rouge.box_event_reference.locate', return_value={'scene_id':'scene_ro6_end2_enter'}), patch('rouge.box_event_view.BoxEventDialog', return_value=child) as dialog:
            self.assertTrue(CurrentSandPanel.open_related(owner))
            dialog.assert_called_once_with('scene_ro6_end2_enter', None, owner)
            self.assertEqual(calls, ['close','show'])
            self.assertIs(owner.related_dialog, child)

    def test_invalid_current_source_does_not_lookup_related(self):
        with patch('rouge.box_event_reference.locate') as locate:
            self.assertFalse(CurrentSandPanel.open_related(SimpleNamespace(_recheck=lambda:False)))
            locate.assert_not_called()
