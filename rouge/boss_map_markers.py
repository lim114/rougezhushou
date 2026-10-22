"""Exact boss configuration bindings to directly observed visible map symbols."""
from pathlib import Path,PurePosixPath
from hashlib import sha256
from copy import deepcopy
import json
from .expansion_reference import NEW_COMMIT
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-boss-map-markers-348';DATA='rouge/data/boss-map-markers.json';MANIFEST=PACK+'/runtime-manifest.json';MANIFEST_SHA256='9d906683f8dce973ec3317624e5b1ec4cf2776c1b035814a5293d1468c7406ca'
STAGES=('ro6_b_1','ro6_b_1_dlc1','ro6_b_1_b','ro6_b_1_b_dlc1','ro6_b_2','ro6_b_2_dlc1','ro6_b_2_b','ro6_b_2_b_dlc1','ro6_b_3','ro6_b_3_dlc1','ro6_b_3_b','ro6_b_3_b_dlc1','ro6_b_4','ro6_b_4_b','ro6_b_5','ro6_b_5_b')
def packet():
    try:
        raw=(ROOT/MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        m=json.loads(raw);expected={DATA,PACK+'/observations.json',PACK+'/source-notes.json','research/p3-expansion-313/current-topic.json','research/p3-expansion-313/map-images.json','research/p3-current-battle-314/source-inputs.json',*[f'rouge/data/battle-maps/{sid}.png'for sid in('ro6_b_1','ro6_b_1_b','ro6_b_2','ro6_b_2_b','ro6_b_3','ro6_b_3_b','ro6_b_4','ro6_b_4_b','ro6_b_5')],'rouge/data/expansion-maps/8de6a9b7a7cdc0b1e69ddaad4b96c36067d9afd1.png'}
        if m['schema']!='boss_map_markers_348_manifest_v1'or m['game_commit']!=NEW_COMMIT or set(m['files'])!=expected:return None
        data=None
        for name,pin in m['files'].items():
            rel=PurePosixPath(name)
            if rel.is_absolute()or'..'in rel.parts or'\\'in name or':'in name:return None
            p=ROOT.joinpath(*rel.parts)
            if p.is_symlink()or not p.resolve().is_relative_to(ROOT.resolve()):return None
            for parent in p.parents:
                if parent==ROOT:break
                if parent.is_symlink():return None
            raw=p.read_bytes()
            if len(raw)!=pin['bytes']or sha256(raw).hexdigest()!=pin['sha256']:return None
            if name==DATA:data=json.loads(raw)
        if data is None or data['schema']!='boss_map_markers_348_v1'or tuple(data['bindings'])!=STAGES:return None
        return{'data':data,'source_identity':MANIFEST_SHA256}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,RecursionError):return None
def mapping_for(stage_id,current):
    if type(stage_id)is not str or stage_id not in STAGES:return None
    try:
        p=packet()
        if p is None:return None
        d=p['data'];row=d['bindings'][stage_id];v=current['version']
        if row['expected_stage']!=v['current']['details']['stages'][stage_id]or row['image']!=v['images']['images'][stage_id]:return None
        level=current['inputs']['levels'][row['current_level_key']]
        if {k:level[k]for k in d['geometry_keys']}!=row['full_selected_geometry']:return None
        for point in row['points']:
            if level['mapData']['tiles'][level['mapData']['map'][point['row']][point['col']]]['tileKey']!=point['tile_key']:return None
        return{'mapping':deepcopy(row),'source_identity':p['source_identity'],'absolute_accuracy_verified':False,'actual_spawn_position':None}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,IndexError):return None
