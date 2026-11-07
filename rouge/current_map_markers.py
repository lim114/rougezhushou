"""Direct visible map symbols; no arbitrary-cell or combat-foot projection."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import json
from .expansion_reference import NEW_COMMIT
from .marker_packet import load_marker_packet
ROOT=Path(__file__).resolve().parents[1]
PACK='research/p3-current-map-markers-337';DATA='rouge/data/current-map-markers.json';MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='79761c515532707a7701fde9ab5a2b4b2a9ecd4a77b822ba1ac6fbd1077030e9'
STAGES=('ro6_b_7','ro6_b_7_b')
def packet():
    expected={DATA,PACK+'/observations.json',PACK+'/source-notes.json','research/p3-expansion-313/current-topic.json','research/p3-expansion-313/map-images.json','research/p3-current-battle-314/source-inputs.json','rouge/data/expansion-maps/4101637d58ee19ad807bebb36de0b7eecc480a2b.png'}
    return load_marker_packet(ROOT,MANIFEST,MANIFEST_SHA256,DATA,expected,
        'current_map_markers_337_manifest_v1','current_map_markers_337_v1',NEW_COMMIT,STAGES)

def mapping_for(stage_id,current):
    if type(stage_id)is not str or stage_id not in STAGES:return None
    return _mapping_for_stage(stage_id,current)

def _mapping_for_stage(stage_id,current):
    """Bind a stage already selected from this package by the caller."""
    ref=packet()
    if ref is None:return None
    d=ref['data'];row=d['bindings'][stage_id];version=current['version']
    if d['game_commit']!=NEW_COMMIT:return None
    if row['expected_stage']!=version['current']['details']['stages'][stage_id]or row['image']!=version['images']['images'][stage_id]:return None
    key='levels/'+version['current']['details']['stages'][stage_id]['levelId'].lower()+'.json'
    if row['current_level_key']!=key:return None
    level=current['inputs']['levels'][key]
    geometry={k:level[k]for k in d['geometry_keys']}
    digest=sha256(json.dumps(geometry,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if digest!=row['full_selected_geometry_sha256']:return None
    for p in row['points']:
        if level['mapData']['tiles'][level['mapData']['map'][p['row']][p['col']]]['tileKey']!=p['tile_key']:return None
    return {'mapping':deepcopy(row),'source_identity':ref['source_identity'],'absolute_accuracy_verified':False,'actual_spawn_position':None}
