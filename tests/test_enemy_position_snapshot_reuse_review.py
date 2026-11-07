from copy import deepcopy
from unittest import TestCase
from unittest.mock import patch
from rouge import current_enemy_spawns as model,current_action_positions as actions,current_map_position as positions


class EnemyPositionSnapshotReuseTests(TestCase):
    def test_one_packet_and_stage_derivation_preserve_position_result(self):
        result=model.stage_reference('ro6_n_1_1','0');key=result['entries'][0]['key']
        expected=actions.reference(result['stage_id'],key)
        with patch.object(positions,'packet',wraps=positions.packet) as packet,patch.object(model.battle,'stage_reference',wraps=model.battle.stage_reference) as stage:
            actual=model.position_reference(result,key)
        packet.assert_called_once_with()
        self.assertEqual(stage.call_count,1)
        self.assertEqual(actual,expected)

    def test_forged_and_unknown_action_do_not_build_position(self):
        result=model.stage_reference('ro6_n_1_1','0');key=result['entries'][0]['key'];forged=deepcopy(result);forged['enemy']['name']='changed'
        with patch.object(actions,'_reference') as build:
            self.assertIsNone(model.position_reference(forged,key))
            self.assertIsNone(model.position_reference(result,'missing'))
        build.assert_not_called()

    def test_invalid_inputs_do_not_read_packet(self):
        with patch.object(positions,'packet') as packet:
            for result,key in [(None,'0'),([], '0'),({},False),({},0)]:self.assertIsNone(model.position_reference(result,key))
        packet.assert_not_called()
