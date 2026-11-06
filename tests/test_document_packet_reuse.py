import unittest
from unittest.mock import patch
from rouge import current_battle_reference as battle
from rouge import current_hanko, current_sun_boss, current_boss_documents


class DocumentPacketReuseTests(unittest.TestCase):
    def test_document_queries_load_battle_source_once(self):
        for model, stage in ((current_hanko, 'ro6_b_1'),
                             (current_sun_boss, 'ro6_b_7'),
                             (current_boss_documents, 'ro6_b_5')):
            with self.subTest(model=model.__name__):
                with patch.object(battle, 'packet', wraps=battle.packet) as read:
                    result = model.reference(stage)
                self.assertIsNotNone(result)
                self.assertEqual(read.call_count, 1)

    def test_independent_stage_query_still_reads_and_prepared_result_matches(self):
        with patch.object(battle, 'packet', wraps=battle.packet) as read:
            expected = battle.stage_reference('ro6_b_1')
        read.assert_called_once()
        source = battle.packet()
        with patch.object(battle, 'packet', side_effect=AssertionError('duplicate source read')):
            self.assertEqual(battle.stage_reference('ro6_b_1', prepared_packet=source), expected)
            self.assertIsNone(battle.stage_reference('missing', prepared_packet=source))
            self.assertIsNone(battle.stage_reference('ro6_b_1', prepared_packet=None))

    def test_target_entry_delegates_type_check_but_requires_selection(self):
        for model, stage in ((current_hanko, 'ro6_b_1'),
                             (current_sun_boss, 'ro6_b_7'),
                             (current_boss_documents, 'ro6_b_5')):
            with self.subTest(model=model.__name__):
                with patch.object(model, 'packet', side_effect=AssertionError('invalid input loaded data')):
                    for key in (None, 0, False, [], {}):
                        self.assertFalse(model.target_available(stage, key))
                with patch.object(model, 'reference', wraps=model.reference) as query:
                    self.assertTrue(model.target_available(stage, '0'))
                query.assert_called_once_with(stage, '0')
                self.assertFalse(model.target_available(stage, 'not-an-entity'))
