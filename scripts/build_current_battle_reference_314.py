"""Check complete selected current levels and reproduce the source manifest."""
from pathlib import Path
from hashlib import sha256,sha1
import argparse,json
ROOT=Path(__file__).resolve().parents[1]
PACK='research/p3-current-battle-314'

def build(root=ROOT):
    root=Path(root)
    def read(n):return json.loads((root/n).read_bytes())
    inputs=read(PACK+'/source-inputs.json');selection=read(PACK+'/source-selection.json');images=read(PACK+'/enemy-images.json')
    stages=read('research/p3-expansion-313/current-topic.json')['details']['stages']
    paths={'levels/'+s['levelId'].lower()+'.json'for s in stages.values()}
    assert paths==set(inputs['levels'])and len(paths)==113 and len(stages)==184
    assert selection['commit']=='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d'
    refs={r['id']for l in inputs['levels'].values()for r in l['enemyDbRefs']}
    assert refs==set(selection['selected_enemy_ids'])and len(refs)==387
    assert set(inputs['enemy_definitions'])==refs-set(selection['enemy_ids_missing_database'])
    assert set(inputs['handbook'])==refs-set(selection['handbook_missing'])
    tree={x['path'].split('/gamedata/',1)[1]:x for n in('level-root-tree','level-dlc1-tree')for x in read(PACK+'/'+n+'.json')if x['type']=='file'}
    for path in paths:
        assert selection['original_sources'][path]['git_blob_sha1']==tree[path]['sha']
    unavailable={r['identity']for r in images['failures']}
    assert unavailable=={'enemy_1250_lyengs_2'}
    assert set(images['images'])==set(images['requested'])-unavailable
    image_tree=read(PACK+'/enemy-images-tree.json');assert image_tree['truncated']is False
    nodes={x['path']:x for x in image_tree['tree']}
    for key,info in images['images'].items():
        raw=(root/info['file']).read_bytes()
        assert len(raw)==info['bytes']==nodes[key+'.png']['size']and sha256(raw).hexdigest()==info['sha256']
        assert sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==info['git_blob_sha1']==nodes[key+'.png']['sha']
    files={PACK+'/'+name:(root/PACK/name).read_bytes()for name in('source-inputs.json','source-selection.json','enemy-images.json')}
    result={'schema':'current_battle_314_v1','game_commit':selection['commit'],'resource_commit':images['resource_commit'],
        'files':{n:{'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}for n,raw in files.items()},
        'levels':113,'stage_refs':184,'enemy_ids':387,'numeric_environment_migrated':False,'original_map_projection_verified':False}
    return(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');p.add_argument('--write',action='store_true');args=p.parse_args();raw=build();dest=ROOT/PACK/'runtime-manifest.json'
    if args.check:assert dest.read_bytes()==raw
    if args.write:dest.write_bytes(raw)
    print(json.dumps({'manifest_sha256':sha256(raw).hexdigest(),'levels':113,'stage_refs':184,'enemy_ids':387}))
