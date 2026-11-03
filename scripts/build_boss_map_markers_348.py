"""Bind observed visible boss-map symbols; never interpolate arbitrary terrain."""
from pathlib import Path
from hashlib import sha256,sha1
from copy import deepcopy
import json,argparse,sys,math
from PIL import Image
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-boss-map-markers-348';DATA='rouge/data/boss-map-markers.json';CURRENT='research/p3-expansion-313/current-topic.json';IMAGES='research/p3-expansion-313/map-images.json';INPUTS='research/p3-current-battle-314/source-inputs.json';GEOMETRY=('mapData','tilesDisallowToLocate','cameraPlugin','mapId')
def encoded(d):return(json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def digest(d):return sha256(json.dumps(d,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def build(root=ROOT):
 root=Path(root);observations=json.loads((root/PACK/'observations.json').read_bytes());groups=observations['groups'];stages=json.loads((root/CURRENT).read_bytes())['details']['stages'];images=json.loads((root/IMAGES).read_bytes())['images'];levels=json.loads((root/INPUTS).read_bytes())['levels'];bindings={};unique=[]
 if len(groups)!=10:raise ValueError('Ten complete directly reviewed map images required')
 for group in groups:
  raw=(root/group['image_file']).read_bytes();im=Image.open(root/group['image_file']).convert('RGB')
  if im.size!=(512,286)or sha256(raw).hexdigest()!=group['image_sha256']:raise ValueError('Exact original image required')
  points=[]
  for p in group['points']:
   if type(p['row'])is not int or type(p['col'])is not int or p['channel_rule']not in('red','blue')or any(type(v)is not int for v in p['marker_bbox']):raise ValueError('Typed cell and explicit symbol box required')
   if p['channel_rule']!=('red'if p['tile_key']=='tile_start'else'blue')or p['tile_key']not in('tile_start','tile_end'):raise ValueError('Exact symbol channel/type required')
   x0,y0,x1,y1=p['marker_bbox']
   if not(0<=x0<x1<=512 and 0<=y0<y1<=286):raise ValueError('Symbol ROI outside image')
   minimum=p.get('minimum_red_channel',130)
   if type(minimum)is not int or minimum not in(90,130):raise ValueError('Explicit supported red contrast threshold required')
   hits=[]
   for y in range(y0,y1):
    for x in range(x0,x1):
     r,g,b=im.getpixel((x,y));matched=(r>minimum and r>1.45*g and r>1.2*b)if p['channel_rule']=='red'else(b>120 and b>1.1*r and g>80)
     if matched:hits.append((x,y))
   if not hits:raise ValueError('No declared marker color pixels:'+group['representative']+str((p['row'],p['col'])))
   center=[sum(v[i]for v in hits)/len(hits)for i in range(2)];pixel=[int(v+.5)for v in center]
   if math.dist(center,p['manual_symbol_estimate'])>8:raise ValueError('Pixel centroid disagrees with direct manual observation:'+group['representative']+str((p['row'],p['col'])))
   points.append({**deepcopy(p),'pixel':pixel,'color_centroid':center,'color_pixel_count':len(hits),'kind':'visible_map_symbol','label':'保护目标标志'if p['tile_key']=='tile_end'else'敌人入口标志','tile_center_measured':False,'absolute_accuracy_verified':False,'actual_spawn_position':None})
  if len({(p['row'],p['col'])for p in points})!=len(points):raise ValueError('No repeated symbol cell')
  unique.extend(points)
  for sid in group['stage_ids']:
   if sid in bindings:raise ValueError('Repeated stage binding')
   stage=stages[sid];key='levels/'+stage['levelId'].lower()+'.json';level=levels[key];image=images[sid]
   if image['file']!=group['image_file']or image['sha256']!=sha256(raw).hexdigest()or image['git_blob_sha1']!=sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest():raise ValueError('Exact stage image metadata required')
   grid=level['mapData']['map'];tiles=level['mapData']['tiles'];symbols={(r,c):tiles[t]['tileKey']for r,row in enumerate(grid)for c,t in enumerate(row)if tiles[t]['tileKey']in('tile_start','tile_end')}
   if len(grid)!=group['rows']or any(len(row)!=group['cols']for row in grid)or symbols!={(p['row'],p['col']):p['tile_key']for p in points}:raise ValueError('Whole source symbol topology differs')
   geo={k:deepcopy(level[k])for k in GEOMETRY};bindings[sid]={'stage_id':sid,'expected_stage':deepcopy(stage),'current_level_key':key,'image':deepcopy(image),'full_selected_geometry':geo,'full_selected_geometry_sha256':digest(geo),'points':deepcopy(points),'annotation_kind':'visible_map_symbol','actual_combat_positions_verified':False,'supports_inverse':False,'supports_segments':False}
 if(len(bindings),len(unique),sum(len(v['points'])for v in bindings.values()))!=(16,46,75):raise ValueError('Preserve16stage bindings/46visible observations/75pairs')
 result={'schema':'boss_map_markers_348_v1','game_commit':'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d','geometry_keys':list(GEOMETRY),'bindings':bindings,'observations':observations,'absolute_accuracy_verified':False,'current_server_verified':False,'whole_map_projection_verified':False,'new_external_ground_truth_claimed':False};data=encoded(result)
 names={CURRENT,IMAGES,INPUTS,PACK+'/observations.json',PACK+'/source-notes.json',*[g['image_file']for g in groups]};files={n:{'bytes':len((root/n).read_bytes()),'sha256':sha256((root/n).read_bytes()).hexdigest()}for n in sorted(names)};files[DATA]={'bytes':len(data),'sha256':sha256(data).hexdigest()}
 return data,encoded({'schema':'boss_map_markers_348_manifest_v1','game_commit':result['game_commit'],'files':files})
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args();d,m=build()
 if a.check:
  if(ROOT/DATA).read_bytes()!=d or(ROOT/PACK/'runtime-manifest.json').read_bytes()!=m:raise ValueError('Build differs')
 else:(ROOT/DATA).write_bytes(d);(ROOT/PACK/'runtime-manifest.json').write_bytes(m)
 print(json.dumps({'stages':16,'images':10,'visible_observations':46,'stage_symbol_pairs':75,'manifest_sha256':sha256(m).hexdigest()}))
