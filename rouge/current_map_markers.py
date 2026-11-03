"""Direct visible map symbols; no arbitrary-cell or combat-foot projection."""
from pathlib import Path,PurePosixPath
from hashlib import sha256
from copy import deepcopy
import json
from .expansion_reference import NEW_COMMIT
ROOT=Path(__file__).resolve().parents[1]
PACK='research/p3-current-map-markers-337';DATA='rouge/data/current-map-markers.json';MANIFEST=PACK+'/runtime-manifest.json'
MANIFEST_SHA256='79761c515532707a7701fde9ab5a2b4b2a9ecd4a77b822ba1ac6fbd1077030e9'
STAGES=('ro6_b_7','ro6_b_7_b')
def packet():
    try:
        raw=(ROOT/MANIFEST).read_bytes()
        if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
        m=json.loads(raw);expected={DATA,PACK+'/observations.json',PACK+'/source-notes.json','research/p3-expansion-313/current-topic.json','research/p3-expansion-313/map-images.json','research/p3-current-battle-314/source-inputs.json','rouge/data/expansion-maps/4101637d58ee19ad807bebb36de0b7eecc480a2b.png'}
        if m['schema']!='current_map_markers_337_manifest_v1'or m['game_commit']!=NEW_COMMIT or set(m['files'])!=expected:return None
        data=None
        for n,pin in m['files'].items():
            rel=PurePosixPath(n)
            if rel.is_absolute()or'..'in rel.parts or'\\'in n or':'in n:return None
            p=ROOT.joinpath(*rel.parts)
            if p.is_symlink()or not p.resolve().is_relative_to(ROOT.resolve()):return None
            for parent in p.parents:
                if parent==ROOT:break
                if parent.is_symlink():return None
            raw=p.read_bytes()
            if len(raw)!=pin['bytes']or sha256(raw).hexdigest()!=pin['sha256']:return None
            if n==DATA:data=json.loads(raw)
        if data is None or data['schema']!='current_map_markers_337_v1'or tuple(data['bindings'])!=STAGES:return None
        return {'data':data,'source_identity':MANIFEST_SHA256}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,RecursionError):return None
def mapping_for(stage_id,current):
    if type(stage_id)is not str or stage_id not in STAGES:return None
    try:
        ref=packet()
        if ref is None:return None
        d=ref['data'];row=d['bindings'][stage_id];version=current['version']
        if d['game_commit']!=NEW_COMMIT:return None
        if row['expected_stage']!=version['current']['details']['stages'][stage_id]or row['image']!=version['images']['images'][stage_id]:return None
        level=current['inputs']['levels'][row['current_level_key']]
        if {k:level[k]for k in d['geometry_keys']}!=row['full_selected_geometry']:return None
        for p in row['points']:
            if level['mapData']['tiles'][level['mapData']['map'][p['row']][p['col']]]['tileKey']!=p['tile_key']:return None
        return {'mapping':deepcopy(row),'source_identity':ref['source_identity'],'absolute_accuracy_verified':False,'actual_spawn_position':None}
    except(OSError,ValueError,KeyError,TypeError,UnicodeError,AttributeError,IndexError):return None
