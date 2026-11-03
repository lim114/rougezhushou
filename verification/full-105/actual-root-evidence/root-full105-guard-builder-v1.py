"""Root binds actual finalized105 Sources and actual independent Wine probe."""
import ast
import hashlib
import json
from pathlib import Path

BASE=Path('/workspace/.continuation')
ROOT=Path('/workspace/rougezhushou')
OUTPUT=BASE/'full105-source-suite-guard-v1.json'
assert not OUTPUT.exists()
guard=json.loads((BASE/'resume105-applied-source-v1.json').read_bytes())
assert guard['section']==105 and len(guard['source_sha256'])==748
sha=lambda raw:hashlib.sha256(raw).hexdigest()
for name,want in {**guard['source_sha256'],**guard['source_additional_sha256']}.items():
    assert sha((ROOT/name).read_bytes())==want,name
packet=BASE/'full105-suite-adapters-source-v1'
assert sha((packet/'manifest.json').read_bytes())=='09725f62dbb7e7c0d00b27864c7dfe2a763678acd3c4e945c29de6422c992601'
for row in json.loads((packet/'manifest.json').read_bytes())['files']:
    raw=(packet/row['path']).read_bytes()
    assert len(raw)==row['bytes'] and sha(raw)==row['sha256']
nodes=ast.parse((packet/'suite_common105.py').read_bytes()).body
names=ast.literal_eval(next(n.value for n in nodes if isinstance(n,ast.Assign)
    and any(isinstance(t,ast.Name) and t.id=='PACKET_NAMES' for t in n.targets)))
assert len(names)==7
adapters={name:sha((packet/name).read_bytes()) for name in names}
probe=BASE/'full105-wine-capability-probe-v1.json'
probe_exit=BASE/'full105-wine-capability-probe-v1.exit-code'
p=json.loads(probe.read_bytes())
assert probe_exit.read_bytes()==b'0\n'
assert p['passed'] is True and p['project_calls']==p['project_imports']==0
assert p['source_sha256']==adapters and p['source_drift']==[]
assert p['private_state_access'] is False and p['native_windows_integration_verified'] is False
def ref(path):
    raw=path.read_bytes();return {'path':str(path),'bytes':len(raw),'sha256':sha(raw)}
bound={**guard,'adapter_source_sha256':adapters,'wine_capability_probe':ref(probe),
       'wine_capability_probe_primary_exit':ref(probe_exit),
       'status':'ACTUAL_FINAL105_SOURCE_BOUND_FULL_VALIDATION_PENDING',
       'passed':False,'runtime_full105_pass_claimed':False}
with OUTPUT.open('x') as stream:
    json.dump(bound,stream,ensure_ascii=False,indent=2);stream.write('\n')
print(json.dumps({'guard':str(OUTPUT),'source_count':748,'adapter_files':7,'probe_primary':0}))
