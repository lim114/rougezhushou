"""Compare full public returns; require changed identities equal existing pending."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
baseline=json.loads((HERE/'baseline-controls.json').read_text())
draft=json.loads((HERE/'draft-controls.json').read_text())
old={r['key']:r for r in baseline['public_cases']}
new={r['key']:r for r in draft['public_cases']}
assert old.keys()==new.keys()
unchanged=[];pending=[];failures=[]
known_labels={'absent','null','legal_zero','legal_one'}
for key,row in new.items():
    change_expected=row['group'] in {'cargo_only','cargo_plus_other'} and row['label'] not in known_labels
    if not change_expected:
        if old[key]['outcome']!=row['outcome']: failures.append({'case':key,'reason':'preserved complete public output differs'})
        else: unchanged.append(key)
        continue
    absent_key=key.rsplit(':',1)[0]+':absent'
    if row['outcome']!=new[absent_key]['outcome']:
        failures.append({'case':key,'reason':'unrecognized identity does not equal complete existing pending output'})
    elif row['outcome']==old[key]['outcome']:
        failures.append({'case':key,'reason':'invalid held source remains asserted non-emergency'})
    else: pending.append(key)
for row in draft['direct_python_controls']:
    if row['outcome'] != {'accepted':True,'value':None}:
        failures.append({'direct_python_control':row['label'],'reason':'non-built-in-string must be pending without consulting equality','outcome':row['outcome']})
receipt={'public_paired_cases':len(old),'public_calls_both_packages':len(old)+len(new),
         'unchanged_complete_public_outputs':len(unchanged),
         'invalid_applicable_cases_equal_existing_pending':len(pending),
         'direct_python_controls_pending':len(draft['direct_python_controls']),
         'failures':failures,'passed':not failures,
         'baseline_hashes':baseline['source_hashes'],'draft_hashes':draft['source_hashes'],
         'controls_inputs_unchanged':baseline['public_input_unchanged'] and draft['public_input_unchanged'],
         'cached_mechanics_unchanged':baseline['cached_mechanics_unchanged'] and draft['cached_mechanics_unchanged'],
         'native_attachment_proven':False,'game_actions':0,'private_state_read':False,
         'artifact_hashes':{name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in ['baseline-controls.json','draft-controls.json','public_controls.py','source-review.json']}}
(HERE/'control-comparison.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k not in {'baseline_hashes','draft_hashes','artifact_hashes'}},ensure_ascii=False))
assert not failures, failures[:3]
