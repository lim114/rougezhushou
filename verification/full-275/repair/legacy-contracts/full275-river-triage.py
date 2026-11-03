from pathlib import Path
import json,hashlib
from collections import Counter
from copy import deepcopy
from unittest.mock import patch
from rouge.damage import calculate_damage
from rouge.reporting import river_reference_sections

root=Path(__file__).resolve().parents[1]
p=root/'.cache/research/river-effects-060/integration-before.json'
cases=json.loads(p.read_bytes())['cases']
def diffs(a,b,path='$'):
    if type(a)!=type(b): return [{'path':path,'before':a,'current':b,'change':'type'}]
    if isinstance(a,dict):
        out=[]
        for k in sorted(a.keys()|b.keys()):
            q=f'{path}.{k}'
            if k not in a:out.append({'path':q,'current':b[k],'change':'added'})
            elif k not in b:out.append({'path':q,'before':a[k],'change':'removed'})
            else:out+=diffs(a[k],b[k],q)
        return out
    if isinstance(a,list):
        if len(a)!=len(b):return [{'path':path,'before':a,'current':b,'change':'list-length'}]
        out=[]
        for i,(x,y) in enumerate(zip(a,b)):out+=diffs(x,y,f'{path}[{i}]')
        return out
    return [] if a==b else [{'path':path,'before':a,'current':b,'change':'value'}]
result={'baseline_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'cases':{}}
for name,f in cases.items():
    a=f['result'];s=deepcopy(f['scenario']);b=json.loads(json.dumps(calculate_damage(s),ensure_ascii=False))
    with patch('rouge.reporting.river_reference_sections',return_value=[]):c=json.loads(json.dumps(calculate_damage(deepcopy(s)),ensure_ascii=False))
    presentation=deepcopy(b)
    blocks={'river_dark','river_fire','river_sanity','river_water','river_limits'}
    presentation['report']['sections']=[z for z in presentation['report']['sections'] if z['id'] not in blocks]
    dd=diffs(a,b)
    result['cases'][name]={'scenario':s,'diff_count':len(dd),'diffs':dd,'current_full_result':b,
        'same_original_input_current_presentation_equivalence':presentation==c,
        'result_top_keys_before':sorted(a),'result_top_keys_current':sorted(b),
        'delta_top_counts':dict(Counter(x['path'].split('.')[1].split('[')[0] for x in dd))}
out=root/'.cache/full275-river-triage.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
for name,r in result['cases'].items():
    print(name,r['diff_count'],r['delta_top_counts'],'pair',r['same_original_input_current_presentation_equivalence'])
    for d in r['diffs']:
        if not any(z in d['path'] for z in ('report','notes','warnings','source','timing')):
            print(d['path'],d['change'],repr(d.get('before'))[:150],'=>',repr(d.get('current'))[:180])
