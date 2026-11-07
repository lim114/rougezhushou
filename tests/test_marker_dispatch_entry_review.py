import unittest
from unittest.mock import patch
from rouge import current_map_position as positions, current_map_markers as normal, boss_map_markers as bosses


class MarkerDispatchEntryTests(unittest.TestCase):
    def test_public_entries_reject_invalid_stage_before_loading(self):
        for module in (normal, bosses):
            with patch.object(module, '_mapping_for_stage') as bind:
                for stage in (None, True, [], 'unlisted'):
                    self.assertIsNone(module.mapping_for(stage, {}))
                bind.assert_not_called()

    def test_dispatched_stage_binds_once_without_reentering_public_gate(self):
        source = positions.packet()
        for module in (normal, bosses):
            stage = module.STAGES[0]
            expected = module.mapping_for(stage, source['current'])
            with patch.object(module, 'mapping_for', side_effect=AssertionError('repeated gate')), \
                 patch.object(module, '_mapping_for_stage', wraps=module._mapping_for_stage) as bind:
                result = positions.stage_reference(stage, prepared_packet=source)
            bind.assert_called_once_with(stage, source['current'])
            self.assertEqual(result['mapping_evidence'], expected['mapping'])
            self.assertEqual(result['source_identity'][1], expected['source_identity'])
