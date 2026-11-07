from unittest import TestCase
from unittest.mock import patch
from rouge import current_route_itinerary as model, current_map_position as positions


class ItineraryPositionBoundaryTests(TestCase):
    def test_independent_cell_reader_still_checks_bounds(self):
        self.assertIsNone(positions.cell_reference({'rows':2,'cols':2},2,0))

    def test_valid_unmapped_step_still_returns_cell_without_center(self):
        selected={'route':{},'step':{'cell':{'row':0,'col':0},'spatial_reference_permitted':True}}
        result={'stage_id':'stage','level_key':'level','source_identity':'route'}
        grid={'rows':1,'cols':1,'map':[[0]],'tiles':[{'tileKey':'tile_floor'}],'points':[],'current_level_key':'level','source_identity':'grid'}
        with patch.object(model,'_resolve',return_value=selected),patch.object(model,'stage_reference',return_value={}),patch.object(model.battle,'stage_reference',return_value={'id':'stage'}),patch.object(positions,'packet',return_value={'current':{}}),patch.object(positions,'stage_reference',return_value=grid):
            value=model.position_reference(result,'route','step')
        self.assertEqual(value['cell'],{'row':0,'col':0})
        self.assertIsNone(value['center'])
