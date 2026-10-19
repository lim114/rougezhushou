"""Reproduce the version manifest from complete extracted-topic selections."""
from pathlib import Path
from hashlib import sha256,sha1
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[1]
PACK='research/p3-expansion-313'
def encoded(v):return(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf8')
def build(root=ROOT):
    root=Path(root)
    def read(name):return json.loads((root/PACK/name).read_bytes())
    old,new=read('baseline-topic.json'),read('current-topic.json')
    sources=read('sources.json');images=read('map-images.json')
    assert sources['DLC2_as_official_name_verified']is False and sources['current_server_or_installed_client_verified']is False
    assert sources['official_label']=='内容拓展·一'
    assert set(old)==set(new)=={'topics','details','modules','customizeData'}
    a,b=old['details']['stages'],new['details']['stages']
    changed=[k for k in b if a.get(k)!=b[k]]
    assert len(a)==105 and len(b)==184 and len(changed)==80
    assert set(images['images'])==set(b)and not images['failures']
    tree=read('mapreview-tree.json');assert tree['truncated']is False
    nodes={r['path']:r for r in tree['tree']}
    for sid,info in images['images'].items():
        raw=(root/info['file']).read_bytes()
        assert sha256(raw).hexdigest()==info['sha256']and len(raw)==info['bytes']
        assert sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==info['git_blob_sha1']==nodes[sid+'.png']['sha']
        assert info['level_geometry_or_position_calibration_verified']is False
    # Source selection reconstruction is available when the full two public inputs exist.
    # A missing cache is explicitly unavailable, not an implicitly passed original-input check.
    base={PACK+'/'+name:(root/PACK/name).read_bytes()for name in('baseline-topic.json','current-topic.json','sources.json','map-images.json')}
    manifest={'schema':'expansion_313_source_manifest_v1','baseline_commit':'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add',
              'current_commit':'bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',
              'files':{name:{'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}for name,raw in base.items()},
              'images_checked_separately_on_read':True,'current_server_verified':False,'baseline_calculation_migrated':False,
              'whole_level_or_enemy_data_migrated':False,'new_coordinate_mapping':False}
    return encoded(manifest)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--check',action='store_true');p.add_argument('--write',action='store_true');a=p.parse_args()
    raw=build(a.root);target=a.root/PACK/'runtime-manifest.json'
    if a.check:assert target.read_bytes()==raw
    if a.write:target.write_bytes(raw)
    print(json.dumps({'manifest_sha256':sha256(raw).hexdigest(),'changed_stage_entries':80,'current_stage_entries':184,'coordinate_mapping_added':False}))
