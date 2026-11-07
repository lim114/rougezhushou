from copy import deepcopy
from unittest import TestCase
from unittest.mock import patch
from rouge import current_stage_objects as model,current_map_position as positions


class ObjectPositionSnapshotTests(TestCase):
    def test_one_packet_and_stage_build_preserve_exact_object_cell(self):
        result=model.stage_reference('ro6_n_1_1');row=next(r for r in result['entries']if r['kind']=='instance')
        with patch.object(positions,'packet',wraps=positions.packet) as packet,patch.object(model.battle,'stage_reference',wraps=model.battle.stage_reference) as stage:
            value=model.position_reference(result,row['key'])
        packet.assert_called_once_with();self.assertEqual(stage.call_count,1)
        raw=row['raw']['position'];self.assertEqual(value['cell'],{'row':value['grid']['rows']-1-raw['row'],'col':raw['col']})
        self.assertEqual(value['row'],row)

    def test_forged_snapshot_cannot_reach_map_builder(self):
        result=model.stage_reference('ro6_n_1_1');key=result['entries'][0]['key'];result=deepcopy(result);result['stage_name']='forged'
        with patch.object(positions,'stage_reference') as grid:
            self.assertIsNone(model.position_reference(result,key))
        grid.assert_not_called()
