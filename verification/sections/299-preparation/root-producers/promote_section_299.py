from pathlib import Path
from hashlib import sha256
import json,subprocess
ROOT=Path(__file__).resolve().parents[1];PREP=ROOT/'verification/sections/299-preparation'
def digest(p):return sha256(p.read_bytes()).hexdigest()
def load(p,pin):
 assert digest(p)==pin
 return json.loads(p.read_bytes())
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()=='b56cbf352cf5d171f52ba05839312950df462e8c'
backend=ROOT/'.cache/p3-299-spawn-candidates-candidate/revision2'
b=load(backend/'HANDOFF.json','82c04abf0f8179186e595f8e5ab484bfd4947608e75d009ece9392a7194a96ab')
view=ROOT/'.cache/p3-299-spawn-view-candidate/revision2'
v=load(view/'HANDOFF.json','5dd687f1a6ca274edc489450083ef7f9ed3621efa822b02f2076c4ce6d7548b7')
tests=ROOT/'.cache/p3-299-parent-integration-tests'
t=load(tests/'READY.json','d9f813cec1aee4f3e693e242e568e8ce7afea9654c913ed19373d06b40483b10')
entries={}
for name,pin in b['promoted'].items():entries[name]=(backend/b['candidate_directory']/name,pin)
for name,pin in v['promotion_allowlist'].items():entries[name]=(ROOT/v['candidate_root']/name,pin)
for name,pin in t['promotion_allowlist'].items():entries[name]=(ROOT/pin['path'],{k:pin[k]for k in ('sha256','bytes')})
assert len(entries)==49
for name,(path,pin)in entries.items():
 assert digest(path)==pin['sha256']and path.stat().st_size==pin['bytes']and not(ROOT/name).exists(),name
parent='rouge/battle_view.py';old=PREP/'before'/parent
assert (ROOT/parent).read_bytes()==old.read_bytes()
new=ROOT/'.cache/p3-299-root-integration/revision2/rouge/battle_view.py'
assert digest(new)=='a865bb46b7ed304d294a3af758bd880e8efdb25dd8925fbecd0044999a956ce0'
for name,(path,pin)in entries.items():
 p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(path.read_bytes())
(ROOT/parent).write_bytes(new.read_bytes())
row={'section':299,'kind':'root_backend_view_parent_promotion_before_actual_product_validation',
 'promoted':{name:pin for name,(path,pin)in entries.items()},
 'existing_production_changes':{parent:{'before_sha256':digest(old),'sha256':digest(new),'bytes':new.stat().st_size}},
 'handoff_pins':{'backend_revision2':digest(backend/'HANDOFF.json'),'view_revision2':digest(view/'HANDOFF.json'),'parent_tests':digest(tests/'READY.json')},
 'functional_complete':False,'native_script_pending':True}
(PREP/'promotion.json').write_bytes((json.dumps(row,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'promoted_new_paths':len(entries),'existing_production_changes':1,'formal_tests_run_by_this_tool':0}))
