"""Read three small public eligible archetype prefabs for snapshot configuration."""
from pathlib import Path
import runpy,json,hashlib
OUT=Path(__file__).resolve().parent
BASE=Path('D:/Hypergryph Launcher/games/Arknights/Arknights_Data/StreamingAssets/AB/Windows')
SOURCES=['charpack/char_1042_phatm2.ab']
r=runpy.run_path(str(OUT.parent/'p1-runtime-source-054/read_unity_stdlib.py'))
manifest=json.loads((BASE/'hot_update_list.json').read_text(encoding='utf8'))
receipts=[];counters=[]
for source in SOURCES:
    entry=next(x for x in manifest['abInfos'] if x['name']==source)
    raw=(BASE/source).read_bytes()
    assert len(raw)==entry['abSize'] and len(raw)<200000
    assert hashlib.md5(raw).hexdigest()==entry['md5']
    info,files=r['bundle'](raw);parsed=[]
    for name,data in files:
        if '.resS' in name or '.resource' in name:continue
        v=r['serialized'](data);assert all(o.get('read_exact') for o in v['objects'])
        parsed.append({'name':name,'serialized':v})
        os=v['objects'];go={o['path_id']:o['data'] for o in os if o['class_id']==1}
        tr={o['path_id']:o['data'] for o in os if o['class_id']==4}
        tr_go={d['m_GameObject']['m_PathID']:d for d in tr.values()}
        def path(g):
            parts=[];seen=set()
            while g in go:
                assert g not in seen;seen.add(g);parts.append(go[g]['m_Name'])
                t=tr_go.get(g);parent=tr.get(t['m_Father']['m_PathID']) if t else None
                if parent is None:break
                g=parent['m_GameObject']['m_PathID']
            return '/'.join(reversed(parts))
        for o in os:
            d=o.get('data')
            if o['class_id']==114 and True:
                counters.append({'source_name':source,'source_sha256':hashlib.sha256(raw).hexdigest(),
                                 'path_id':o['path_id'],'hierarchy':path(d['m_GameObject']['m_PathID']),
                                 'attack_data':d})
    receipts.append({'source_name':source,'source_bytes':len(raw),'source_sha256':hashlib.sha256(raw).hexdigest(),
                     'source_md5':entry['md5'],'installed_base_version':manifest['versionId'],'bundle':info,'files':parsed})
receipt={'sources':receipts,'game_dll_executed':False,'private_files_read':False,
         'parser_sha256':hashlib.sha256((OUT.parent/'p1-runtime-source-054/read_unity_stdlib.py').read_bytes()).hexdigest()}
(OUT/'character-prefabs.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf8')
(OUT/'character-components.json').write_text(json.dumps({'counters':counters,'private_files_read':False},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'sources':[(o['source_name'],o['source_bytes']) for o in receipts], 'attacks':[(o['source_name'],o['hierarchy'],list(o['attack_data'])[:8]) for o in counters]},ensure_ascii=False))
