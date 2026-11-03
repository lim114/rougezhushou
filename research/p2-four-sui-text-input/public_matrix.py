"""Save full public JSON or exact exception for every requested case, without private state."""
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
PACKAGE=Path(sys.argv[1]).resolve()
OUTPUT=Path(sys.argv[2]).resolve()
sys.path.insert(0,str(PACKAGE))
from rouge.damage import calculate_damage
cases=json.loads((ROOT/'requests.json').read_text())['cases']
outputs={}
calls=0
for name,args in cases.items():
    before=deepcopy(args)
    calls+=1
    try:
        outcome={'result':calculate_damage(args),'error':None}
    except Exception as exc:
        outcome={'result':None,'error':{'type':type(exc).__name__,'message':str(exc)}}
    assert args==before,name
    outputs[name]={'scenario':args,'outcome':outcome}
data={'baseline_head':'c3ccf25d59144227dd0f8f5ca9ef6c8bf81ad8cf',
      'package':str(PACKAGE),'public_calls':calls,
      'operator_engine_sha256':hashlib.sha256((PACKAGE/'rouge/operator_engine.py').read_bytes()).hexdigest(),
      'all_caller_inputs_preserved':True,'cases':outputs}
with gzip.open(OUTPUT,'wt',encoding='utf-8') as out:
    json.dump(data,out,ensure_ascii=False,indent=2)
    out.write('\n')
print(json.dumps({'public_calls':calls,'error_outcomes':sum(bool(v['outcome']['error']) for v in outputs.values()),
                  'compressed_full_outputs':str(OUTPUT),'sha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest()},ensure_ascii=False))
