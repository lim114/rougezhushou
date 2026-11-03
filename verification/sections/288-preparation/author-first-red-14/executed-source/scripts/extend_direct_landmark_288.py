"""Replay frozen human readings; append only agreed lowland road/floor centers.

This command is read-only unless --write is explicit. No failed regular plane,
averaged coordinate, interpolation, inverse mapping or actual combat position
is admitted. All historical cache paths in the public inputs are provenance;
replay reads only this public source pack and the existing public stage data.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import sys

import cv2
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge.battle_preview import battle_data,DATA
from rouge.map_projection import grid_digest
from scripts.map_fit_replay import verify_fit_replay

BASE=ROOT/'research/p3-map-direct-road-288'
OUTPUT=DATA/'fixed-landmark-references.json'
SOURCE_MANIFEST_SHA256='015f18ec8a0f5f8a6360ee66e022dddf5df8a0bf56e768f1febe397bf353c958'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_inputs():
    manifest_path=BASE/'source-manifest.json'
    if sha(manifest_path)!=SOURCE_MANIFEST_SHA256:
        raise ValueError('The sealed public source manifest changed.')
    manifest=read(manifest_path)
    if len(manifest['files'])!=13:
        raise ValueError('The original public source set changed.')
    for name,item in manifest['files'].items():
        if Path(name).name!=name or sha(BASE/name)!=item['sha256'] or (BASE/name).stat().st_size!=item['bytes']:
            raise ValueError('A frozen public source changed: '+name)
    return manifest


def replay_failed_fit(observation,frozen):
    anchors=observation['anchors']
    if len(anchors)!=4 or {(r,c) for r,c,*_ in anchors}&{(r,c) for r,c,*_ in observation['checks']}:
        raise ValueError('A holdout entered the original four-anchor fit.')
    matrix,_=cv2.findHomography(np.asarray([[c,r] for r,c,*_ in anchors],float),
        np.asarray([[x,y] for r,c,x,y,*_ in anchors],float),method=0)
    if matrix is None or not np.isfinite(matrix).all():
        raise ValueError('The original failed fit cannot be replayed.')
    checks=[]
    for r,c,x,y,cue in observation['checks']:
        vector=matrix@np.asarray([c,r,1.0]);point=(vector[:2]/vector[2]).tolist()
        checks.append({'row':r,'col':c,'observed_pixel':[x,y],'projected_pixel':point,
            'error_px':math.dist(point,[x,y]),'cue':cue})
    current={'id':observation['id'],'matrix':matrix.ravel().tolist(),'checks':checks,
        'accepted':max(row['error_px'] for row in checks)<=4}
    original={key:copy.deepcopy(frozen[key]) for key in ('id','matrix','checks')}
    original['accepted']=frozen['author_fit_gate_pass']
    verify_fit_replay(current,original)
    if current['accepted'] or frozen['accepted_for_production'] is not False:
        raise ValueError('An original failed plane cannot be promoted.')
    return {'id':frozen['id'],'max_error_px':frozen['max_error_px'],
        'accepted_for_runtime':False,'holdouts':len(checks)}


def check_stage_source(sid,expected):
    stage=battle_data()['stages'][sid];image=stage['image']
    if image!=expected['image'] or stage['level_source']!=expected['level_source'] or grid_digest(stage)!=expected['grid_sha256']:
        raise ValueError('A stage image, level or grid binding changed: '+sid)
    raw=(DATA/image['file']).read_bytes()
    if hashlib.sha256(raw).hexdigest()!=image['sha256'] or len(raw)!=image['bytes']:
        raise ValueError('The original stage bitmap changed: '+sid)
    if hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()!=image['source_blob_sha1']:
        raise ValueError('The original resource blob changed: '+sid)
    level=BASE/('level_rogue6_t-1.json' if sid=='ro6_t_1' else 'level_rogue6_t-3.json')
    if sha(level)!=stage['level_source']['sha256'] or level.stat().st_size!=stage['level_source']['bytes']:
        raise ValueError('The pinned original level changed: '+sid)
    raw_map=read(level)['mapData']
    if raw_map['map']!=stage['map'] or raw_map['tiles']!=stage['tiles']:
        raise ValueError('The logical grid differs from the pinned original: '+sid)
    return stage


def build(write=False):
    source_inputs()
    author=read(BASE/'author-readings-before-fit.json')
    independent=read(BASE/'independent-readings-before-comparison.json')
    request=read(BASE/'blind-source-request.json')
    comparison=read(BASE/'point-comparison.json')
    delta=read(BASE/'unpublished-direct-center-delta.json')
    failed=read(BASE/'first-failed-regular-fit.json')
    prior=read(BASE/'prior-direct-references.json')
    regular=read(BASE/'prior-regular-projections.json')
    if author['pixel_tolerance']!=4 or comparison['agreement_tolerance_px']!=4 or not comparison['no_averaging_or_adjustment']:
        raise ValueError('The four-pixel gate or no-adjustment rule changed.')
    if independent['kind']!='root_independent_visual_centers_before_author_comparison':
        raise ValueError('The sealed independent reading is missing.')
    if (len(prior['references']),len(prior['stages']),sum(len(row['points']) for row in prior['references'].values()))!=(6,11,28):
        raise ValueError('The direct reference baseline changed.')
    if (len(regular['calibrations']),len(regular['stages']))!=(12,24):
        raise ValueError('The regular-plane baseline changed.')
    if read(DATA/'battle-map-projections.json')!=regular:
        raise ValueError('The existing regular-plane dictionaries changed.')
    output=copy.deepcopy(prior);agreements=[];failed_planes=[]
    stages={entry['stage_id']:entry for entry in delta['source_records']}
    for expected in request['items']:
        sid=expected['id'];stage=check_stage_source(sid,stages[sid]);image=stage['image']
        original=next(row for row in author['observations'] if row['id']==sid)
        original_fit=next(row for row in failed['results'] if row['id']==sid)
        failed_planes.append(replay_failed_fit(original,original_fit))
        first={(r,c):(x,y,cue) for r,c,x,y,cue in original['checks']}
        second={(r,c):(x,y) for r,c,x,y in independent['observations'][sid]}
        requested={(row['row'],row['col']) for row in expected['center_cells']}
        if len(first)!=len(original['checks']) or len(second)!=len(independent['observations'][sid]) or set(first)!=requested or set(second)!=requested:
            raise ValueError('A frozen requested/observed point set changed.')
        accepted=[]
        for r,c in sorted(requested):
            x,y,cue=first[r,c];peer=second[r,c];tile=stage['tiles'][stage['map'][r][c]]
            if tile['heightType']!='LOWLAND' or tile['tileKey'] not in ('tile_floor','tile_road'):
                raise ValueError('An unverified ground type entered the candidate.')
            distance=math.sqrt((x-peer[0])**2+(y-peer[1])**2)
            sealed=next(row for row in comparison['comparisons'] if (row['stage_id'],row['row'],row['col'])==(sid,r,c))
            if sealed['observed_pixel']!=[x,y] or sealed['independent_pixel']!=list(peer) or sealed['agreement_px']!=distance or sealed['accepted'] is not (distance<=4):
                raise ValueError('A frozen pair, distance or acceptance changed.')
            agreements.append(copy.deepcopy(sealed))
            if distance<=4:
                accepted.append({'row':r,'col':c,'observed_pixel':[x,y],
                    'independent_pixel':list(peer),'agreement_px':distance,'tile_key':tile['tileKey']})
        if not accepted or sid in output['references']:
            raise ValueError('The new partial reference is empty or already exists.')
        output['references'][sid]={'rows':len(stage['map']),'cols':len(stage['map'][0]),
            'width':image['width'],'height':image['height'],'bitmap_sha256':image['sha256'],
            'grid_sha256':grid_digest(stage),'agreement_tolerance_px':4,
            'scope':'Only the listed independently concordant LOWLAND floor/road centers. No plane, inverse, interpolation, segments or actual-position accuracy claim.',
            'points':accepted}
        for alias_id in expected['stage_ids']:
            alias=check_stage_source(alias_id,stages[alias_id])
            if alias_id in output['stages'] or alias['image']['sha256']!=image['sha256'] or grid_digest(alias)!=grid_digest(stage):
                raise ValueError('An existing or mismatching alias cannot inherit points.')
            output['stages'][alias_id]={'reference':sid,'image_file':alias['image']['file'],
                'level_sha256':alias['level_source']['sha256']}
    if len(agreements)!=23 or sum(row['accepted'] for row in agreements)!=12:
        raise ValueError('The frozen23 pairs /12 acceptances changed.')
    for group in ('references','stages'):
        if any(output[group][key]!=value for key,value in prior[group].items()):
            raise ValueError('An earlier direct reference changed.')
    output['source']['scope']='Only agreed observed LOWLAND floor centers and explicitly labelled LOWLAND road centers; no plane, extrapolation, inverse, or path.'
    output['source'].setdefault('additional_source_packs',[]).append('research/p3-map-direct-road-288')
    output['source']['direct_road_288']={'source_manifest_sha256':SOURCE_MANIFEST_SHA256,
        'comparison_sha256':sha(BASE/'point-comparison.json'),'source_pixel_adjustments':0}
    content=json.dumps(output,ensure_ascii=False,indent=2).encode('utf-8')
    receipt={'status':'PASS_PARTIAL_DIRECT_CENTER_AGREEMENT_ONLY','new_requested_points':23,
        'new_accepted_points':12,'new_rejected_points':11,'new_partial_images':2,'new_partial_stage_bindings':3,
        'prior_partial_points':28,'total_partial_images':len(output['references']),
        'total_partial_stage_bindings':len(output['stages']),
        'total_partial_points':sum(len(row['points']) for row in output['references'].values()),
        'agreement_tolerance_px':4,'agreement_comparisons':agreements,'rejected_plane_fits':failed_planes,
        'prior_direct_references_unchanged':True,'regular_dictionaries_unchanged':True,
        'regular_calibrations':12,'regular_stage_bindings':24,'complete_calibration_added':0,
        'remaining_regular_unbound_stages':81,'remaining_regular_distinct_bitmaps':59,
        'absolute_position_accuracy_verified':False,'extrapolation':False,'inverse_cell_assignment':False,
        'bitmap_checkpoint_connections':False,'game_actions':0,'chat_requests':0,'live_samples':0,
        'output_sha256':hashlib.sha256(content).hexdigest()}
    if write:
        if OUTPUT.read_bytes() not in ((BASE/'prior-direct-references.json').read_bytes(),content):
            raise ValueError('Refusing to overwrite an unreviewed concurrent direct-data change.')
        OUTPUT.write_bytes(content)
        (BASE/'build-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    return output,receipt


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true')
    args=parser.parse_args();_,result=build(write=args.write)
    print(json.dumps({key:value for key,value in result.items() if key not in ('agreement_comparisons','rejected_plane_fits')},ensure_ascii=False))
