import unittest
from unittest.mock import patch
from rouge import current_sun_boss, current_boss_documents


class DocumentMapSnapshotTests(unittest.TestCase):
    def test_fresh_reference_reused_with_identical_mapping(self):
        for model, stage in ((current_sun_boss, 'ro6_b_7'), (current_boss_documents, 'ro6_b_5')):
            result = model.reference(stage)
            expected = model.map_reference(result)
            self.assertIsNotNone(expected)
            with patch.object(model, 'reference', wraps=model.reference) as read:
                actual = model.map_reference(result, prepared_reference=result)
                read.assert_not_called()
            self.assertEqual(actual, expected)

    def test_independent_map_request_still_rechecks_source(self):
        for model, stage in ((current_sun_boss, 'ro6_b_7'), (current_boss_documents, 'ro6_b_5')):
            result = model.reference(stage)
            with patch.object(model, 'reference', return_value=None) as read:
                self.assertIsNone(model.map_reference(result))
                read.assert_called_once()

    def test_prepared_reference_does_not_bypass_map_identity(self):
        from rouge import current_map_position as maps
        for model, stage in ((current_sun_boss, 'ro6_b_7'), (current_boss_documents, 'ro6_b_5')):
            result = model.reference(stage)
            with patch.object(maps, 'stage_reference', return_value={'stage_id':'wrong'}):
                self.assertIsNone(model.map_reference(result, prepared_reference=result))
