from unittest import TestCase
from unittest.mock import patch
from rouge import current_action_positions as model


class ActionPositionPacketReuseTests(TestCase):
    def test_invalid_action_key_does_not_load_sources(self):
        with patch.object(model.positions,'packet') as loader:
            for value in (None,True,0,[],{}):
                self.assertIsNone(model.reference('ro6_n_1_1',value))
        loader.assert_not_called()

    def test_same_packet_supplies_action_and_map_without_second_read(self):
        packet=model.positions.packet()
        current=model.battle.stage_reference('ro6_n_1_1',prepared_packet=packet['current'])
        grid=model.positions.stage_reference('ro6_n_1_1',prepared_packet=packet)
        key=next(a['key'] for a in current['actions'] if a['raw']['actionType']=='SPAWN' and a['queue']['kind']=='main')
        expected=model._reference(current,grid,key)
        with patch.object(model.positions,'packet',return_value=packet) as loader,patch.object(model.battle,'packet') as duplicate:
            actual=model.reference('ro6_n_1_1',key)
        loader.assert_called_once_with()
        duplicate.assert_not_called()
        self.assertEqual(actual,expected)

    def test_unavailable_prepared_packet_does_not_trigger_fallback_read(self):
        with patch.object(model.positions,'packet') as loader:
            self.assertIsNone(model.positions.stage_reference('ro6_n_1_1',prepared_packet=None))
        loader.assert_not_called()
