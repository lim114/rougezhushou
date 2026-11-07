from copy import deepcopy
from unittest import TestCase
from unittest.mock import patch
from rouge import current_route_itinerary as model,current_map_position as positions


class ItinerarySnapshotReuseTests(TestCase):
    def test_one_packet_and_stage_preserve_declared_step(self):
        result=model.stage_reference('ro6_n_1_3')
        route=next(r for r in result['entries']if any(s['spatial_reference_permitted']for s in r['steps']))
        step=next(s for s in route['steps']if s['spatial_reference_permitted'])
        with patch.object(positions,'packet',wraps=positions.packet) as packet,patch.object(model.battle,'stage_reference',wraps=model.battle.stage_reference) as stage,patch.object(positions,'cell_reference') as repeat:
            value=model.position_reference(result,route['key'],step['key'])
        packet.assert_called_once_with();self.assertEqual(stage.call_count,1);repeat.assert_not_called()
        self.assertEqual(value['step'],step);self.assertEqual(value['cell'],step['cell'])

    def test_forged_snapshot_does_not_build_grid(self):
        result=model.stage_reference('ro6_n_1_3');route=result['entries'][0];bad=deepcopy(result);bad['stage_name']='forged'
        with patch.object(positions,'stage_reference') as grid:
            self.assertIsNone(model.position_reference(bad,route['key'],'0'))
        grid.assert_not_called()
