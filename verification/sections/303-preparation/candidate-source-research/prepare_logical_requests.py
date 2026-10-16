"""Freeze source-only cells for independent readers. No observed pixels or fit."""
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
inventory = json.loads((HERE / 'candidate-inventory.json').read_bytes())
selected = {
    'ro6_b_6': [(1,2),(1,5),(1,8),(1,11),(3,3),(3,8),(4,5),(4,9),(5,2),(5,10),(7,3),(7,8)],
    'ro6_n_2_3': [(1,1),(1,4),(1,6),(1,8),(2,3),(2,5),(3,6),(3,8),(5,2),(5,6),(5,8),(6,2)],
}
result = {'kind': 'SOURCE_ONLY_DIRECT_GROUND_READER_REQUEST_NOT_OBSERVATION_OR_ACCEPTANCE',
          'inventory_sha256': sha256((HERE / 'candidate-inventory.json').read_bytes()).hexdigest(),
          'coordinate_rule': 'row and col are zero-based indices into original mapData.map and stage.map as displayed. Do not flip the map array using the different route source_row rule.',
          'source_scope': 'LOWLAND tile_floor or tile_road only. Not tile_start/end/fence/hole/wall or elevated/portal top.',
          'measurement_fields_absent': True, 'other_reader_observations_absent': True,
          'regular_reference_12maps_24stages_is_not_all_terrain_completion': True,
          'whole_map_gaps_remain': [81,59],
          'reader_instruction': 'Read independently from the fixed original. Reject/unknown obscured or ambiguous centers; do not infer pixels from adjacent centers, a projection or another reader. Freeze before comparison; <=4 original pixels remains the comparison gate. No expected success count and no whole-map claim.',
          'groups': []}
for row in inventory['candidates']:
    identity = row['stage_id']
    requests = []
    for r,c in selected[identity]:
        tile = row['complete_tile_metadata'][row['complete_grid_map'][r][c]]
        assert tile['heightType']=='LOWLAND' and tile['tileKey'] in ('tile_floor','tile_road')
        requests.append({'request_id': identity+':display:'+str(r)+':'+str(c),
                         'row':r,'col':c,'tile_key':tile['tileKey'],'height_type':'LOWLAND','tile_metadata':tile})
    result['groups'].append({'stage_id':identity,'aliases':[a['stage_id']for a in row['aliases']],
                             'rows':row['rows'],'cols':row['cols'], 'image_path':row['image_path'],
                             'image_sha256':row['image']['sha256'], 'image_size':[512,286],
                             'level_path':row['level_path'],'level_sha256':row['level_source']['sha256'],
                             'semantic_grid_sha256':row['semantic_grid_sha256'],
                             'all_eligible_count':row['lowland_floor_road_count'],
                             'initial_requests':requests})
with(HERE/'logical-reader-requests.json').open('xb')as stream:
    stream.write((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({'request_file':'logical-reader-requests.json','sha256':sha256((HERE/'logical-reader-requests.json').read_bytes()).hexdigest(),
                  'groups':{g['stage_id']:len(g['initial_requests'])for g in result['groups']},
                  'pixel_observations_or_fit':False,'completion_claimed':False},ensure_ascii=False))
