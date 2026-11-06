import unittest
from unittest.mock import patch

from rouge import current_event_battles as model


class EventBattleQueryContractTests(unittest.TestCase):
    def test_invalid_types_raise_before_loading(self):
        with patch.object(model, 'packet') as load:
            for value in (False, 0, [], {}):
                calls = (
                    lambda: model.reference(event_id=value),
                    lambda: model.reference(stage_id=value),
                    lambda: model.locate(value, 'scene_ro6_unknown'),
                    lambda: model.locate('scenes', value),
                    lambda: model.choice({'rows': []}, value),
                    lambda: model.stage_has_reference(value),
                )
                for call in calls:
                    with self.subTest(value=value, call=call), self.assertRaises(TypeError):
                        call()
            load.assert_not_called()

    def test_absent_selection_and_unsupported_queries_do_not_load(self):
        with patch.object(model, 'packet') as load:
            self.assertIsNone(model.choice({'rows': []}, None))
            self.assertFalse(model.stage_has_reference(None))
            self.assertFalse(model.stage_has_reference('ro6_b_6'))
            self.assertIsNone(model.reference(stage_id='ro6_b_6'))
            self.assertIsNone(model.reference('黑诞', 'ro6_t_13'))
            self.assertIsNone(model.locate('items', 'item'))
            self.assertIsNone(model.locate('scenes', 'not-a-scene'))
            load.assert_not_called()

    def test_supported_stage_reads_once_and_invalid_source_stays_absent(self):
        source = model.packet()
        with patch.object(model, 'packet', return_value=source) as load:
            self.assertTrue(model.stage_has_reference('ro6_t_13'))
            load.assert_called_once_with()
        with patch.object(model, 'packet', return_value=None) as load:
            self.assertFalse(model.stage_has_reference('ro6_t_13'))
            load.assert_called_once_with()
