import hashlib
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent
side=sys.argv[1]
assert side in ('baseline','draft')
sys.path.insert(0,str(ROOT/side))
from rouge.damage import calculate_damage
from rouge.reporting import format_report
from rouge.estimate import format_estimate
cases=json.loads((ROOT/'matrix-cases.json').read_text())['cases']
initial=json.loads((ROOT/'initial-public-inspection.json').read_text())['items'] if side=='draft' else []
reuse={json.dumps(i['scenario'],sort_keys=True,ensure_ascii=False):i for i in initial}
items=[];calls=0;reused=0;formats=0
for item in cases:
    old=reuse.get(json.dumps(item['scenario'],sort_keys=True,ensure_ascii=False))
    if old is not None:
        record={k:old[k] for k in ('accepted','result','error_type','error') if k in old};reused+=1
    else:
        calls+=1
        try:record={'accepted':True,'result':calculate_damage(item['scenario'])}
        except Exception as e:record={'accepted':False,'error_type':type(e).__name__,'error':str(e)}
    if record['accepted']:
        result=record['result']
        record['texts']={'plain':format_report(result),'technical':format_report(result,technical=True),'estimate':format_estimate(result)}
        formats+=3
    items.append({**item,**record})
receipt={'version':1,'side':side,'baseline_commit':'9ef5a469673502754db3be320a8eece9a7fd18d4','PYTHONHASHSEED':'0',
    'case_count':len(cases),'fresh_API_calls':calls,'reused_initial_API_results':reused,'formatter_calls':formats,
    'source_parses_or_downloads':0,'items':items}
out=ROOT/f'matrix-{side}-results.json'
out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'side':side,'cases':len(cases),'fresh_API_calls':calls,'reused':reused,'formatter_calls':formats,'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest()}))
