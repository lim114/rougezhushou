from pathlib import Path
import json
root=Path(__file__).resolve().parents[1]
tri=json.loads((root/'.cache/full275-river-triage.json').read_text(encoding='utf-8'))
baseline=json.loads((root/'.cache/research/river-effects-060/integration-before.json').read_bytes())['cases']
def leaves(value,path='$'):
    out={}
    if isinstance(value,(int,float)) and not isinstance(value,bool):return {path:value}
    if isinstance(value,dict):
        for k,v in value.items():out.update(leaves(v,path+'.'+k))
    elif isinstance(value,list):
        identity=None
        if value and all(isinstance(v,dict) for v in value):
            for key in ('id','key','name'):
                if all(isinstance(v.get(key),str) for v in value) and len({v[key] for v in value})==len(value):identity=key;break
        for i,v in enumerate(value):
            token=(identity+'='+v[identity]) if identity else str(i)
            out.update(leaves(v,path+'['+token+']'))
    return out
for name,r in tri['cases'].items():
    old=leaves(baseline[name]['result']);cur=leaves(r['current_full_result'])
    changes=[{'path':k,'before':v,'current':cur.get(k),'missing_numeric_leaf':k not in cur}
        for k,v in old.items() if cur.get(k)!=v or k not in cur]
    r['original_numeric_leaves_count']=len(old)
    r['preserved_original_numeric_leaves_count']=len(old)-len(changes)
    r['original_numeric_leaf_changes']=changes
    print(name,len(old),len(changes))
    if name=='phantom_river':print(json.dumps(changes,ensure_ascii=False,indent=2))
(root/'.cache/full275-river-triage-with-numeric.json').write_text(json.dumps(tri,ensure_ascii=False,indent=2),encoding='utf-8')
