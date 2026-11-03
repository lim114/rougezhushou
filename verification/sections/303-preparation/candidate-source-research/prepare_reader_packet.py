"""Narrow blind-reader packet, same89 requests; preserve every earlier draft."""
from hashlib import sha256
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def encoded(value):return(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def pin(path):
 raw=path.read_bytes();return{'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
old=HERE/'logical-reader-requests-all.json'
new=HERE/'logical-reader-requests-all-lowland.json'
with new.open('xb')as stream:stream.write(old.read_bytes())
inventory=json.loads((HERE/'candidate-inventory.json').read_bytes())
allowed={str(new.resolve()):pin(new)}
grids={}
for candidate in inventory['candidates']:
 source=ROOT/candidate['level_path'];raw=json.loads(source.read_bytes())
 assert raw['mapData']==candidate['original_mapData']
 relative='reader-grid-'+candidate['stage_id']+'.json';target=HERE/relative
 document={'kind':'COMPLETE_ORIGINAL_MAPDATA_VIEW_NO_PIXEL_MEASUREMENTS',
  'stage_id':candidate['stage_id'],'rows':candidate['rows'],'cols':candidate['cols'],
  'source_level_file':candidate['level_path'],'source_level_sha256':pin(source)['sha256'],
  'coordinate_rule':'mapData.map JSON row directly indexes display rows; no route source_row flip.',
  'mapData':raw['mapData']}
 with target.open('xb')as stream:stream.write(encoded(document))
 grids[candidate['stage_id']]={'file':str(target.resolve()),**pin(target)}
 allowed[str(target.resolve())]=pin(target)
 allowed[str((ROOT/candidate['image_path']).resolve())]=pin(ROOT/candidate['image_path'])
ready={'kind':'ALL89_BLIND_READER_SOURCE_PACKET_READY_NOT_OBSERVATIONS_OR_ACCEPTANCE',
 'reader_request':{'file':str(new.resolve()),**pin(new)},'request_count':89,'groups':{'ro6_b_6':55,'ro6_n_2_3':34},
 'complete_original_grid_views':grids,'reader_allowed_source_files':allowed,
 'prior_initial24':{'file':'logical-reader-requests.json',**pin(HERE/'logical-reader-requests.json'),
  'history':'Initial source-only scope, not a failure. Expanded to all89 before producing or seeing pixel observations.'},
 'prior_all89_ready':{'file':'READY.json',**pin(HERE/'READY.json')},
 'same_request_bytes_under_root_requested_filename':pin(old)==pin(new),
 'forbidden_inputs':'Old projections, landmark point data, fitting predictions, any other reader measurements, current game or user samples.',
 'pixel_observations_or_fit_coordinates_included':False,
 'reading_acceptance_guaranteed':False,'null_and_reason_allowed_for_every_cell':True,
 'scope':'LOWLAND tile_floor/road only. No whole-map/all-height/inverse/segment claim;81/59 gap stays.'}
with(HERE/'ALL_LOWLAND_READY.json').open('xb')as stream:stream.write(encoded(ready))
print(json.dumps({'ready_file':'ALL_LOWLAND_READY.json','ready_pin':pin(HERE/'ALL_LOWLAND_READY.json'),
 'requests':pin(new),'grid_views':grids,'pixel_data':False},ensure_ascii=False,indent=2))
