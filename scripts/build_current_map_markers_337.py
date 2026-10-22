"""Visible original-map symbol measurements, never inferred world projections."""
from pathlib import Path
from hashlib import sha256,sha1
from copy import deepcopy
import json,argparse,sys
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
PACK='research/p3-current-map-markers-337';DATA='rouge/data/current-map-markers.json'
CURRENT='research/p3-expansion-313/current-topic.json';IMAGES='research/p3-expansion-313/map-images.json';INPUTS='research/p3-current-battle-314/source-inputs.json'
GEOMETRY=('mapData','tilesDisallowToLocate','cameraPlugin','mapId')
def encoded(d):return(json.dumps(d,ensure_ascii=False,indent=2)+chr(10)).encode('utf8')
def digest(d):return sha256(json.dumps(d,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def build(root=ROOT):
    root=Path(root);o=json.loads((root/PACK/'observations.json').read_bytes());stages=json.loads((root/CURRENT).read_bytes())['details']['stages'];images=json.loads((root/IMAGES).read_bytes())['images'];levels=json.loads((root/INPUTS).read_bytes())['levels']
    raw=(root/o['image_file']).read_bytes()
    if sha256(raw).hexdigest()!=o['image_sha256']:raise ValueError('Exact observed PNG required.')
    im=Image.open(root/o['image_file']).convert('RGB')
    if im.size!=(512,286)or o['stage_ids']!=['ro6_b_7','ro6_b_7_b']:raise ValueError('Explicit whole-image and two-stage scope required.')
    points=[]
    for p in o['points']:
        if type(p['row'])is not int or type(p['col'])is not int or p['channel_rule']not in ('red','blue')or any(type(x)is not int for x in p['marker_bbox']):raise ValueError('Typed explicit symbol cell, channel and bounds required.')
        x0,y0,x1,y1=p['marker_bbox'];pixels=[]
        if not(0<=x0<x1<=512 and 0<=y0<y1<=286):raise ValueError('Marker ROI outside original image.')
        for y in range(y0,y1):
            for x in range(x0,x1):
                r,g,b=im.getpixel((x,y))
                match=(r>130 and r>1.45*g and r>1.2*b)if p['channel_rule']=='red'else(b>120 and b>1.1*r and g>80)
                if match:pixels.append((x,y))
        if not pixels:raise ValueError('No observed marker color pixels.')
        centroid=[sum(p[i]for p in pixels)/len(pixels)for i in range(2)];pixel=[int(v+.5)for v in centroid]
        points.append({**deepcopy(p),'pixel':pixel,'color_centroid':centroid,'color_pixel_count':len(pixels),'kind':'visible_map_symbol','label':'保护目标标志'if p['tile_key']=='tile_end'else'敌人入口标志','absolute_accuracy_verified':False,'actual_spawn_position':None,'tile_center_measured':False})
    if len(points)!=8 or len({(p['row'],p['col'])for p in points})!=8:raise ValueError('All eight distinct map-symbol correspondences required.')
    bindings={}
    for sid in o['stage_ids']:
        stage=stages[sid];key='levels/'+stage['levelId'].lower()+'.json';level=levels[key];image=images[sid]
        if image['file']!=o['image_file']or image['sha256']!=sha256(raw).hexdigest()or image['git_blob_sha1']!=sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest():raise ValueError('Exact complete stage-specific resource image required.')
        grid=level['mapData']['map'];tiles=level['mapData']['tiles'];symbols={(r,c):tiles[v]['tileKey']for r,row in enumerate(grid)for c,v in enumerate(row)if tiles[v]['tileKey']in('tile_start','tile_end')}
        if len(grid)!=9 or any(len(row)!=13 for row in grid)or symbols!={(p['row'],p['col']):p['tile_key']for p in points}:raise ValueError('Complete source symbol topology changed.')
        geometry={k:deepcopy(level[k])for k in GEOMETRY}
        bindings[sid]={'stage_id':sid,'expected_stage':deepcopy(stage),'current_level_key':key,'image':deepcopy(image),'full_selected_geometry':geometry,'full_selected_geometry_sha256':digest(geometry),'points':deepcopy(points),'annotation_kind':'visible_map_symbol','actual_combat_positions_verified':False,'supports_inverse':False,'supports_segments':False}
    d={'schema':'current_map_markers_337_v1','game_commit':'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d','geometry_keys':list(GEOMETRY),'bindings':bindings,'observation':o,'source_notes':json.loads((root/PACK/'source-notes.json').read_bytes()),'absolute_accuracy_verified':False,'current_server_verified':False,'new_external_ground_truth_claimed':False,'whole_map_projection_verified':False};blob=encoded(d)
    names=[PACK+'/observations.json',PACK+'/source-notes.json',o['image_file'],CURRENT,IMAGES,INPUTS]
    files={n:{'bytes':len((root/n).read_bytes()),'sha256':sha256((root/n).read_bytes()).hexdigest()}for n in names};files[DATA]={'bytes':len(blob),'sha256':sha256(blob).hexdigest()}
    return blob,encoded({'schema':'current_map_markers_337_manifest_v1','game_commit':d['game_commit'],'files':files})
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--output-dir',type=Path);a=p.parse_args();d,m=build()
    if a.output_dir:a.output_dir.mkdir(parents=True,exist_ok=False);(a.output_dir/'current-map-markers.json').write_bytes(d);(a.output_dir/'runtime-manifest.json').write_bytes(m)
    if a.check:assert(ROOT/DATA).read_bytes()==d and(ROOT/PACK/'runtime-manifest.json').read_bytes()==m
    print(json.dumps({'stage_bindings':2,'distinct_symbol_observations':8,'stage_symbol_pairs':16,'manifest_sha256':sha256(m).hexdigest()}))
