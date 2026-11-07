"""Exact boss configuration bindings to directly observed visible map symbols."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import json
from .expansion_reference import NEW_COMMIT
from .marker_packet import load_marker_packet
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-boss-map-markers-348';DATA='rouge/data/boss-map-markers.json';MANIFEST=PACK+'/runtime-manifest.json';MANIFEST_SHA256='9d906683f8dce973ec3317624e5b1ec4cf2776c1b035814a5293d1468c7406ca'
STAGES=('ro6_b_1','ro6_b_1_dlc1','ro6_b_1_b','ro6_b_1_b_dlc1','ro6_b_2','ro6_b_2_dlc1','ro6_b_2_b','ro6_b_2_b_dlc1','ro6_b_3','ro6_b_3_dlc1','ro6_b_3_b','ro6_b_3_b_dlc1','ro6_b_4','ro6_b_4_b','ro6_b_5','ro6_b_5_b')
def packet():
    expected={DATA,PACK+'/observations.json',PACK+'/source-notes.json','research/p3-expansion-313/current-topic.json','research/p3-expansion-313/map-images.json','research/p3-current-battle-314/source-inputs.json',*[f'rouge/data/battle-maps/{sid}.png'for sid in('ro6_b_1','ro6_b_1_b','ro6_b_2','ro6_b_2_b','ro6_b_3','ro6_b_3_b','ro6_b_4','ro6_b_4_b','ro6_b_5')],'rouge/data/expansion-maps/8de6a9b7a7cdc0b1e69ddaad4b96c36067d9afd1.png'}
    return load_marker_packet(ROOT,MANIFEST,MANIFEST_SHA256,DATA,expected,
        'boss_map_markers_348_manifest_v1','boss_map_markers_348_v1',NEW_COMMIT,STAGES)

def mapping_for(stage_id,current):
    if type(stage_id)is not str or stage_id not in STAGES:return None
    return _mapping_for_stage(stage_id,current)

def _mapping_for_stage(stage_id,current):
    """Bind a stage already selected from this package by the caller."""
    p=packet()
    if p is None:return None
    d=p['data'];row=d['bindings'][stage_id];v=current['version']
    if row['expected_stage']!=v['current']['details']['stages'][stage_id]or row['image']!=v['images']['images'][stage_id]:return None
    key='levels/'+v['current']['details']['stages'][stage_id]['levelId'].lower()+'.json'
    if row['current_level_key']!=key:return None
    level=current['inputs']['levels'][key]
    geometry={k:level[k]for k in d['geometry_keys']}
    digest=sha256(json.dumps(geometry,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    if digest!=row['full_selected_geometry_sha256']:return None
    for point in row['points']:
        if level['mapData']['tiles'][level['mapData']['map'][point['row']][point['col']]]['tileKey']!=point['tile_key']:return None
    return{'mapping':deepcopy(row),'source_identity':p['source_identity'],'absolute_accuracy_verified':False,'actual_spawn_position':None}
