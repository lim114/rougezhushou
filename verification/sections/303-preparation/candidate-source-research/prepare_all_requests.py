"""All source-eligible cells, unfiltered; no observed pixel or projection data."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def encoded(value):return(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def pin(path):
 raw=path.read_bytes();return{'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
inventory=json.loads((HERE/'candidate-inventory.json').read_bytes())
result={'kind':'ALL_SOURCE_ELIGIBLE_DIRECT_GROUND_REQUESTS_NOT_MEASUREMENTS_OR_ACCEPTANCE',
 'source_inventory_sha256':pin(HERE/'candidate-inventory.json')['sha256'],
 'coordinate_rule':'Zero-based display row,col index the original JSON mapData.map directly; do not flip the array using route source_row.',
 'eligibility':'Every tile whose heightType is LOWLAND and tileKey is tile_floor or tile_road; no visibility/success filtering.',
 'reader_instruction':'Independently read the fixed original center for every logical request, or null with a reason if not readable. No other reader, projection, interpolation or error-driven adjustment. Freeze first full output before any comparison. No required accepted count.',
 'pixel_or_fit_data_included':False,'full_map_calibration_claimed':False,
 'whole_map_gaps_unchanged':[81,59], 'groups':[]}
for source in inventory['candidates']:
 requests=[]
 for row,values in enumerate(source['complete_grid_map']):
  for col,index in enumerate(values):
   tile=source['complete_tile_metadata'][index]
   if tile['heightType']!='LOWLAND' or tile['tileKey']not in('tile_floor','tile_road'):continue
   requests.append({'request_id':source['stage_id']+':display:'+str(row)+':'+str(col),
    'row':row,'col':col,'tile_key':tile['tileKey'],'height_type':'LOWLAND','tile_metadata':tile})
 assert len(requests)==source['lowland_floor_road_count']
 result['groups'].append({'stage_id':source['stage_id'],'name':source['name'],
  'aliases':[a['stage_id']for a in source['aliases']],'rows':source['rows'],'cols':source['cols'],
  'image_path':source['image_path'],'image_sha256':source['image']['sha256'],'image_size':[512,286],
  'level_path':source['level_path'],'level_sha256':source['level_source']['sha256'],
  'semantic_grid_sha256':source['semantic_grid_sha256'],'requests':requests})
assert[len(g['requests'])for g in result['groups']]==[55,34]
with(HERE/'logical-reader-requests-all.json').open('xb')as stream:stream.write(encoded(result))
for name,expected in inventory['source_pins'].items():assert pin(ROOT/name)==expected
ready={'kind':'SECTION303_FIXED_MAP_SOURCE_REQUEST_READY_NOT_READINGS_OR_ACCEPTANCE',
 'at_utc':datetime.now(timezone.utc).isoformat(),'source_after_section':302,
 'source_inventory':{'file':'candidate-inventory.json',**pin(HERE/'candidate-inventory.json')},
 'reader_request':{'file':'logical-reader-requests-all.json',**pin(HERE/'logical-reader-requests-all.json')},
 'groups':{g['stage_id']:len(g['requests'])for g in result['groups']},'total_requests':89,
 'prior_initial24_source_only_requests_retained_not_the_final_scope':{'file':'logical-reader-requests.json',**pin(HERE/'logical-reader-requests.json')},
 'source_pins':inventory['source_pins'],
 'measurement_coordinates_or_fits_created':False,'other_reader_pixel_data_seen':False,
 'source_data_and_coverage_code_changed':False,'Qt_tests_game_chat_Git_private_operations':False,
 'regular_ground_reference12_24_and_direct10_18_58_not_all_terrain_completion':True,
 'whole_map_gaps_unchanged':[81,59],
 'comparison_policy':'Independent nulls allowed. Preserve both full first readings, reject if either null or direct distance>4 original pixels; retain author point only, no averaging/correction; no inverse/segments/whole-map claim from direct references.'}
with(HERE/'READY.json').open('xb')as stream:stream.write(encoded(ready))
print(json.dumps({'READY':pin(HERE/'READY.json'),'all_requests':pin(HERE/'logical-reader-requests-all.json'),
 'request_counts':ready['groups'],'pixel_measurements_or_fits':False,'Qt_or_tests':False},ensure_ascii=False,indent=2))
