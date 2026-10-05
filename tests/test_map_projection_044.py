"""Offline bitmap mapping boundaries and independently observed landmarks."""
import copy,dataclasses,hashlib,math,unittest
from rouge.battle_preview import battle_data,DATA
from rouge.map_projection import projection_data,projection_for,FixedMapProjection


class FixedMapTests(unittest.TestCase):
    def setUp(self):
        self.stage=copy.deepcopy(battle_data()['stages']['ro6_n_1_2'])
        self.projection=self.load(self.stage)

    @staticmethod
    def load(stage,sha=None,size=None):
        image=stage['image']
        return projection_for(stage,image['sha256'] if sha is None else sha,
            (image['width'],image['height']) if size is None else size)

    def test_observed_landmarks_within_original_pixel_tolerance(self):
        data=projection_data()
        self.assertGreaterEqual(len(data['calibrations']),3)
        self.assertGreaterEqual(len(data['stages']),6)
        for cid,c in data['calibrations'].items():
            p=self.load(battle_data()['stages'][cid])
            self.assertIsNotNone(p)
            for point in c['checks']:
                actual=p.project(point)
                error=math.dist(actual,point['observed_pixel'])
                self.assertLessEqual(error,4.0,(cid,point['cue']))

    def test_all_bound_images_have_the_expected_bytes(self):
        for sid in projection_data()['stages']:
            s=battle_data()['stages'][sid]
            sha=hashlib.sha256((DATA/s['image']['file']).read_bytes()).hexdigest()
            self.assertIsNotNone(self.load(s,sha))

    def test_visible_tile_centers_invert_without_row_flip(self):
        for sid in projection_data()['stages']:
            s=battle_data()['stages'][sid];p=self.load(s)
            for r,line in enumerate(s['map']):
                for c,_ in enumerate(line):
                    cell={'row':r,'col':c};x,y=p.project(cell)
                    if 0<=x<p.width and 0<=y<p.height:
                        self.assertEqual(p.cell_at(x,y),cell,(sid,cell))

    def test_protection_cell_is_on_left_of_near_red_entrance(self):
        blue=self.projection.project({'row':3,'col':0})
        red=self.projection.project({'row':2,'col':7})
        self.assertLess(blue[0],red[0]);self.assertGreater(blue[1],red[1])
        self.assertLess(math.dist(blue,(98,129)),4)

    def test_unreviewed_bitmap_does_not_get_an_inferred_transform(self):
        for sid in ('ro6_n_2_1','ro6_e_2_1','ro6_n_2_2'):
            self.assertIsNone(self.load(battle_data()['stages'][sid]))

    def test_unbound_alias_cannot_inherit_matching_geometry(self):
        self.stage['id']='different-stage'
        self.assertIsNone(self.load(self.stage))

    def test_changed_image_bytes_block_mapping(self):
        self.assertIsNone(self.load(self.stage,'f'*64))
        self.assertIsNone(self.load(self.stage,''))

    def test_changed_image_declaration_cannot_whitelist_other_bytes(self):
        self.stage['image']['sha256']='f'*64
        self.assertIsNone(self.load(self.stage,'f'*64))

    def test_changed_file_path_blocks_mapping(self):
        self.stage['image']['file']='different.png'
        self.assertIsNone(self.load(self.stage))

    def test_changed_level_version_blocks_mapping(self):
        self.stage['level_source']['sha256']='different-level'
        self.assertIsNone(self.load(self.stage))

    def test_changed_grid_dimensions_block_mapping(self):
        self.stage['map'].pop()
        self.assertIsNone(self.load(self.stage))

    def test_changed_tile_semantics_block_mapping(self):
        index=self.stage['map'][1][1]
        self.stage['tiles'][index]['tileKey']='changed-road'
        self.assertIsNone(self.load(self.stage))

    def test_changed_actual_or_declared_pixel_size_blocks_mapping(self):
        self.assertIsNone(self.load(self.stage,size=(511,286)))
        self.stage['image']['width']=511
        self.assertIsNone(self.load(self.stage))

    def test_invalid_cells_remain_unmapped(self):
        for value in (None,{},'cell',{'row':True,'col':1},{'row':'1','col':1},
                {'row':math.nan,'col':1},{'row':1,'col':math.inf},
                {'row':-1,'col':1},{'row':7,'col':1},{'row':1,'col':9}):
            self.assertIsNone(self.projection.project(value),value)

    def test_fractional_interior_position_stays_in_same_tile(self):
        for dr,dc in ((-.2,-.2),(.2,.2),(.1,-.1)):
            x,y=self.projection.project({'row':3+dr,'col':2+dc})
            self.assertEqual(self.projection.cell_at(x,y),{'row':3,'col':2})

    def test_bitmap_edges_and_nonfinite_clicks_remain_unmapped(self):
        for x,y in ((-1,100),(512,100),(100,-1),(100,286),(math.nan,100),(100,math.inf),(True,100)):
            self.assertIsNone(self.projection.cell_at(x,y))

    def test_projection_value_is_immutable_and_empty_stage_clears(self):
        with self.assertRaises(dataclasses.FrozenInstanceError):self.projection.cols=1
        self.assertIsNone(projection_for(None,'anything',(512,286)))

    def test_singular_denominator_does_not_fabricate_a_point(self):
        p=FixedMapProjection((1,0,0,0,1,0,0,0,0),(1,0,0,0,1,0,0,0,0),7,9,512,286,4)
        self.assertIsNone(p.project({'row':3,'col':4}))
        self.assertIsNone(p.cell_at(100,100))


if __name__=='__main__':unittest.main()
