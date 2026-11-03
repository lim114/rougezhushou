"""Admit only identical complete exported geometry and exact observed bitmap."""
from pathlib import Path
from hashlib import sha256
import argparse,json,math
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-current-map-position-319';DATA='rouge/data/current-map-position.json'
GEOMETRY_KEYS=('mapData','tilesDisallowToLocate','cameraPlugin','mapId')
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
def canonical(value):return sha256(json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def finite(v):return type(v)in(int,float)and math.isfinite(v)
def checked_points(old,binding,record):
    assert binding['level_sha256']==old['level_source']['sha256']and binding['image_file']==old['image']['file']
    assert record['bitmap_sha256']==old['image']['sha256']and(record['width'],record['height'])==(old['image']['width'],old['image']['height'])
    assert len(old['map'])==record['rows']and all(len(r)==record['cols']for r in old['map'])and record['agreement_tolerance_px']==4
    normalized=[[{k:old['tiles'][i].get(k)for k in('tileKey','heightType','buildableType','passableMask')}for i in row]for row in old['map']]
    assert sha256(json.dumps(normalized,sort_keys=True,separators=(',',':')).encode()).hexdigest()==record['grid_sha256']
    result=[];seen=set()
    for p in record['points']:
        row,col=p['row'],p['col'];a,b=p['observed_pixel'],p['independent_pixel'];key=p.get('tile_key','tile_floor')
        assert type(row)is int and type(col)is int and 0<=row<record['rows']and 0<=col<record['cols']and(row,col)not in seen
        assert len(a)==len(b)==2 and all(finite(x)for x in(*a,*b))and all(0<=x[0]<record['width']and 0<=x[1]<record['height']for x in(a,b))and math.dist(a,b)<=4
        tile=old['tiles'][old['map'][row][col]];assert key in('tile_floor','tile_road')and tile['tileKey']==key and tile['heightType']=='LOWLAND'
        seen.add((row,col));result.append({'row':row,'col':col,'pixel':a,'independent_pixel':b,'tile_key':key,'agreement_limit_px':4,'absolute_accuracy_verified':False})
    assert result;return result
def build(root=ROOT):
    root=Path(root);read=lambda n:json.loads((root/n).read_bytes());old=read('rouge/data/battle-previews.json')['stages'];land=read('rouge/data/fixed-landmark-references.json');geometries=read(PACK+'/old-selected-complete-geometries.json');current=read('research/p3-current-battle-314/source-inputs.json');stages=read('research/p3-expansion-313/current-topic.json')['details']['stages'];images=read('research/p3-expansion-313/map-images.json')['images'];compatible={};unmapped=[]
    for sid,stage in stages.items():
        image=images[sid];level_key='levels/'+stage['levelId'].lower()+'.json';level=current['levels'][level_key];envelope={k:level[k]for k in GEOMETRY_KEYS};donors=[]
        for oid,binding in land['stages'].items():
            baseline=old[oid];original=geometries.get(baseline['level_source']['sha256'])
            if original is None or original['geometry']!=envelope or baseline['image']['sha256']!=image['sha256']:continue
            assert original['source']==baseline['level_source']and level['mapData']['map']==baseline['map']and level['mapData']['tiles']==baseline['tiles']
            record=land['references'][binding['reference']];points=checked_points(baseline,binding,record)
            assert(image['width'],image['height'])==(record['width'],record['height'])
            donors.append({'baseline_stage_id':oid,'reference':binding['reference'],'baseline_level_source':baseline['level_source'],'points':points})
        if not donors:unmapped.append(sid);continue
        by_cell={}
        for donor in donors:
            for p in donor['points']:by_cell.setdefault((p['row'],p['col']),[]).append(p)
        points=[]
        for cell,values in sorted(by_cell.items()):
            assert all(math.dist(a['pixel'],b['pixel'])<=4 for a in values for b in values)
            points.append(values[0]|{'donor_count':len(values)})
        compatible[sid]={'stage_id':sid,'current_level_key':level_key,'full_selected_geometry_sha256':canonical(envelope),'image':image,'donors':donors,'points':points,'mapping_mode':'verified_centers_only','supports_inverse':False,'supports_segments':False,'absolute_accuracy_verified':False}
    data={'schema':'current_map_position_319_v1','game_commit':'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d','geometry_keys':list(GEOMETRY_KEYS),'compatible_stages':compatible,'unmapped_stage_ids':unmapped,'all_current_stage_ids':list(stages),'new_landmarks_measured':False,'whole_map_projection_verified':False,'actual_combat_positions_verified':False}
    raw=enc(data);names=[PACK+'/old-selected-complete-geometries.json',PACK+'/source-selection.json','rouge/data/battle-previews.json','rouge/data/fixed-landmark-references.json','research/p3-current-battle-314/source-inputs.json','research/p3-expansion-313/map-images.json','research/p3-expansion-313/current-topic.json'];files={n:{'sha256':sha256((root/n).read_bytes()).hexdigest(),'bytes':(root/n).stat().st_size}for n in names};files[DATA]={'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
    return raw,enc({'schema':'current_map_position_319_manifest_v1','game_commit':data['game_commit'],'files':files,'current_battle_packet_required':True})
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args();data,manifest=build()
    for name,raw in((DATA,data),(PACK+'/runtime-manifest.json',manifest)):
        if a.write:(ROOT/name).write_bytes(raw)
        if a.check:assert(ROOT/name).read_bytes()==raw
    result=json.loads(data);print(json.dumps({'manifest_sha256':sha256(manifest).hexdigest(),'compatible_stage_refs':len(result['compatible_stages']),'unique_images':len({x['image']['sha256']for x in result['compatible_stages'].values()}),'point_references_across_stage_refs':sum(len(x['points'])for x in result['compatible_stages'].values()),'all_current_stage_refs':len(result['all_current_stage_ids'])}))
