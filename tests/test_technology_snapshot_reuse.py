import unittest
from unittest.mock import patch
from rouge import technology, technology_state
from rouge.technology_state import TechnologyState


class TechnologySnapshotTests(unittest.TestCase):
    def test_display_reads_one_state_and_one_catalog_node(self):
        state = TechnologyState(None)
        with patch.object(technology, 'technology_node', wraps=technology.technology_node) as entry, patch.object(technology_state, 'technology_node', wraps=technology_state.technology_node) as repeated, patch.object(state, 'view', wraps=state.view) as views:
            technology.format_technology('rogue_6_outbuff_1', account_state=state)
        self.assertEqual(entry.call_count, 1)
        self.assertEqual(repeated.call_count, 0)
        self.assertEqual(views.call_count, 1)

    def test_independent_entries_reject_unknown_and_read_current_status(self):
        state = TechnologyState(None)
        for reader in (state.view, state.describe):
            with self.assertRaises(ValueError):
                reader('not-a-node')
        identity = 'rogue_6_outbuff_1'
        self.assertIn('账户解锁状态：未知', technology.format_technology(identity, account_state=state))
        state.set_status(identity, 'unlocked')
        text = technology.format_technology(identity, account_state=state)
        self.assertIn('已解锁', text)
        self.assertNotIn('账户解锁状态：未知', text)

    def test_catalog_rows_reuse_validation(self):
        state = TechnologyState(None)
        for node in technology.technology_nodes():
            expected = state.view(node['buffId'])
            with patch.object(technology_state, 'technology_node', side_effect=AssertionError('duplicate catalog lookup')):
                self.assertEqual(state.view(node['buffId'], prepared_node=node), expected)
