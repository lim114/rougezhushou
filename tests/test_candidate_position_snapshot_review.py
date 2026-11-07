from copy import deepcopy
from unittest import TestCase
from unittest.mock import patch
from rouge import current_spawn_candidates as model,current_map_position as positions,current_action_positions as actions


class CandidatePositionSnapshotTests(TestCase):
    def test_single_packet_and_stage_with_exact_output(self):
        result=model.stage_reference('ro6_n_1_1');relation=result['groups'][0];key=relation['members'][0]['action_key']
        expected=actions.reference(result['stage_id'],key)
        with patch.object(positions,'packet',wraps=positions.packet) as packet,patch.object(model.battle,'stage_reference',wraps=model.battle.stage_reference) as stage:
            actual=model.position_reference(result,relation['key'],key)
        packet.assert_called_once_with();self.assertEqual(stage.call_count,1)
        self.assertEqual(actual,expected)

    def test_invalid_inputs_do_not_load_and_forgery_does_not_project(self):
        with patch.object(positions,'packet') as packet:
            for value,relation,key in [(None,'x','0'),({},False,'0'),({},'x',False)]:
                self.assertIsNone(model.position_reference(value,relation,key))
        packet.assert_not_called()
        result=model.stage_reference('ro6_n_1_1');relation=result['groups'][0];key=relation['members'][0]['action_key']
        forged=deepcopy(result);forged['actual_count']=0
        with patch.object(actions,'_reference') as project:
            self.assertIsNone(model.position_reference(forged,relation['key'],key))
            self.assertIsNone(model.position_reference(result,'foreign',key))
        project.assert_not_called()
