from unittest import TestCase
from unittest.mock import patch
from rouge import current_stage_objects as model, current_map_position as positions


class PositionCenterReuseTests(TestCase):
    def test_verified_cell_reuses_center_without_building_tile_details(self):
        point={'row':1,'col':0,'pixel':[12,34]}
        grid={'rows':2,'cols':2,'points':[point],'current_level_key':'level','source_identity':'grid'}
        result={'stage_id':'stage','level_key':'level','source_identity':'source'}
        chosen={'row':{'kind':'instance','raw':{'position':{'row':0,'col':0}}}}
        with patch.object(model,'_resolve',return_value=chosen),patch.object(model,'from_battle',return_value={}),patch.object(model.battle,'stage_reference',return_value={'id':'stage'}),patch.object(positions,'packet',return_value={'current':{}}), patch.object(positions,'stage_reference',return_value=grid), patch.object(positions,'cell_reference') as cell_reader:
            value=model.position_reference(result,'object')
        cell_reader.assert_not_called()
        self.assertEqual(value['cell'],{'row':1,'col':0})
        self.assertEqual(value['center'],point)
        self.assertIsNot(value['center'],point)
        value['center']['pixel'][0]=999
        self.assertEqual(point['pixel'],[12,34])

    def test_unmapped_and_invalid_positions_do_not_gain_a_center(self):
        grid={'rows':2,'cols':2,'points':[],'current_level_key':'level','source_identity':'grid'}
        result={'stage_id':'stage','level_key':'level','source_identity':'source'}
        for row in (0,-1,2,True,0.5):
            with self.subTest(row=row):
                chosen={'row':{'kind':'instance','raw':{'position':{'row':row,'col':0}}}}
                with patch.object(model,'_resolve',return_value=chosen),patch.object(model,'from_battle',return_value={}),patch.object(model.battle,'stage_reference',return_value={'id':'stage'}),patch.object(positions,'packet',return_value={'current':{}}),patch.object(positions,'stage_reference',return_value=grid):
                    value=model.position_reference(result,'object')
                if type(row) is int and row==0:self.assertIsNone(value['center'])
                else:self.assertIsNone(value)
