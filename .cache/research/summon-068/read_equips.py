"""Extract AMMO skill prefab graphs from one bounded public base bundle."""
from pathlib import Path
import runpy,json,hashlib
OUT=Path(__file__).resolve().parent
BASE=Path('D:/Hypergryph Launcher/games/Arknights/Arknights_Data/StreamingAssets/AB/Windows')
SOURCE='battle/prefabs/[uc]equips.ab'
r=runpy.run_path(str(OUT.parent/'p1-runtime-source-054/read_unity_stdlib.py'))
manifest=json.loads((BASE/'hot_update_list.json').read_text(encoding='utf8'))
entry=next(x for x in manifest['abInfos'] if x['name']==SOURCE)
raw=(BASE/SOURCE).read_bytes();assert len(raw)==entry['abSize'] and len(raw)<2000000
assert hashlib.md5(raw).hexdigest()==entry['md5']
info,files=r['bundle'](raw);results=[];stats=[]
def pp(x):
    if isinstance(x,dict):
        if 'm_FileID' in x and 'm_PathID' in x:yield x
        for v in x.values():yield from pp(v)
    elif isinstance(x,list):
        for v in x:yield from pp(v)
for fname,data in files:
    if '.resS' in fname or '.resource' in fname:continue
    v=r['serialized'](data);assert all(o.get('read_exact') for o in v['objects'])
    stats.append({'name':fname,'object_count':len(v['objects']),'read_exact_count':sum(o['read_exact'] for o in v['objects'])})
    om={o['path_id']:o for o in v['objects']}
    assets=[o for o in v['objects'] if o['class_id']==142]
    assert len(assets)==1
    choices=[a for a in assets[0]['data']['m_Container'] if any(s in a['first'] for s in ['deepcl_equip'])]
    for a in choices:
        root=a['second']['asset'];assert root['m_FileID']==0
        todo=[root['m_PathID']];seen=set();os=[]
        while todo:
            oid=todo.pop()
            if oid==0 or oid in seen:continue
            seen.add(oid);assert oid in om,(a['first'],oid)
            o=om[oid];os.append(o)
            todo.extend(p['m_PathID'] for p in pp(o['data']) if p['m_FileID']==0)
        results.append({'asset_path':a['first'],'root_id':root['m_PathID'],'objects':os,'types':v['types']})
receipt={'source_name':SOURCE,'source_bytes':len(raw),'source_sha256':hashlib.sha256(raw).hexdigest(),
         'source_md5':entry['md5'],'base_version':manifest['versionId'],'bundle':info,'parse_stats':stats,
         'selected_prefabs':results,'game_dll_executed':False,'process_memory_read':False,'private_files_read':False}
(OUT/'deepcl-equip-prefabs.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'source_bytes':len(raw),'objects':sum(s['object_count'] for s in stats),
                 'selected_prefabs':[(o['asset_path'],len(o['objects'])) for o in results]},ensure_ascii=False))
