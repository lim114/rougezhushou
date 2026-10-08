"""Freeze fixed public source and create one surgical external-only candidate."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path('/workspace/rougezhushou')
OUT=Path('/workspace/.continuation/p2-orchid-near-text-085')
BASE='b5a40f30683bfc0945decaabbd4db5914c28427f'
def sha(raw):return hashlib.sha256(raw).hexdigest()
names=subprocess.check_output(['git','-C',str(ROOT),'ls-tree','-r','--name-only',BASE]).decode().splitlines()
files={}
for name in names:
 if name.startswith(('rouge/','tests/','scripts/')) and name.endswith(('.py','.json')):
  raw=subprocess.check_output(['git','-C',str(ROOT),'show',BASE+':'+name])
  for target in ('baseline','draft'):
   path=OUT/target/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
  files[name]={'bytes':len(raw),'sha256':sha(raw),'git_blob':subprocess.check_output(['git','-C',str(ROOT),'rev-parse',BASE+':'+name]).decode().strip()}
path=OUT/'draft/rouge/damage.py';raw=path.read_bytes()
anchor=b"    result['report']=build_report(scenario,result)\r\n    return result\r\n\r\ndef _evaluate_damage(prepared,wine_phase=None)"
assert raw.count(anchor)==1
addition=(b"    result['report']=build_report(scenario,result)\r\n"
 b"    if (scenario['operator']=='char_1048_orchd2' and\r\n"
 b"            isinstance(scenario.get('near_previous_deployment'),str)):\r\n"
 b"        from .operator_engine import selected_talents\r\n"
 b"        talents,_=selected_talents(catalog()['operators'][scenario['operator']],scenario)\r\n"
 b"        if any(t.get('name')=='\xe7\xbf\x94\xe8\x99\xab\xe6\x9c\xba\xe5\x8a\xa8' for t in talents):\r\n"
 b"            raise ValueError('near_previous_deployment \xe4\xb8\x8d\xe6\x8e\xa5\xe5\x8f\x97\xe6\x96\x87\xe6\x9c\xac\xe6\x9d\xa1\xe4\xbb\xb6\xef\xbc\x9b\xe8\xaf\xb7\xe4\xbd\xbf\xe7\x94\xa8\xe5\xb8\x83\xe5\xb0\x94\xe5\x80\xbc\xe3\x80\x82')\r\n"
 b"    return result\r\n\r\ndef _evaluate_damage(prepared,wine_phase=None)")
path.write_bytes(raw.replace(anchor,addition))
assert b'\n' not in path.read_bytes().replace(b'\r\n',b'')
freeze={'status':'author_baseline_fixed_candidate_pending_tests','fixed_commit':BASE,'public_source_count':len(files),
 'public_source_files':files,'baseline_complete_public_source_byte_hashes':True,
 'mutation_scope':['draft/rouge/damage.py late near string guard only','new externaldraft test file tofollow'],
 'tracked_edits':False,'GUI_executed':False,'Wine_executed':False,
 'source_only_handoff':{'path':'/workspace/.continuation/p2-orchid-boolean-consumer-085-independent-source/handoff.json',
  'sha256':'841218b3c2c2e45615e27e54c4571d208067f73e59d461c1b946661f6ba3479a'},
 'historical_public_baseline_reuse':False,'draft_damage_sha256':sha(path.read_bytes())}
(OUT/'baseline-freeze085.json').write_text(json.dumps(freeze,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'frozen_source_count':len(files),'draft_damage_sha256':sha(path.read_bytes()),'fixed_commit':BASE,'tracked_edits':False}))
