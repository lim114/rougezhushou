from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1];PREP=ROOT/'verification/sections/299-preparation'
def digest(p):return sha256(p.read_bytes()).hexdigest()
base=ROOT/'.cache/p3-299-native-window/revision3';assert digest(base/'READY.json')=='28cbf8852d7fc5c0af08052e2414bd35d2cdcfa61aee2bd94bcbee36dbb1fe63'
canonical='scripts/verify_spawn_candidates_window_299.py';old=ROOT/canonical
assert digest(old)=='8a359acb41c7c8d963f6ebc2a304ae58c9cc415234d80608c055947c4b1f17c7'
saved=PREP/'first-necessary-source'/canonical;saved.parent.mkdir(parents=True,exist_ok=True);saved.write_bytes(old.read_bytes())
new=base/Path(canonical).name;assert digest(new)=='4a3b71df8119eae543388e3fbe8f3221efa42fb762451be52f044f8c14e75d4d'
old.write_bytes(new.read_bytes())
record=json.loads((PREP/'final-promotion.json').read_bytes())
record['pre_repair_freeze']='verification/sections/299-preparation/final-promotion.json'
record['source_compatibility_repair']='verification/sections/299-preparation/entry-binding-repair.json'
record['native_repair_READY_sha256']=digest(base/'READY.json')
for name in (canonical,'research/p3-battle-entry-compatibility-299/source-manifest.json',
 'research/p3-battle-entry-compatibility-299/README.md','tests/test_battle_entry_compatibility_299.py'):
 p=ROOT/name;record['promoted'][name]={'sha256':digest(p),'bytes':p.stat().st_size}
name='rouge/battle_event_references.py';p=ROOT/name
record['existing_production_changes'][name]={'before_sha256':digest(PREP/'before'/name),'sha256':digest(p),'bytes':p.stat().st_size}
record['kind']='root_final_functional_and_compatibility_scope_before_revalidation'
assert len(record['promoted'])==53 and len(record['existing_production_changes'])==2
for name,pin in {**record['promoted'],**record['existing_production_changes']}.items():assert digest(ROOT/name)==pin['sha256']
(PREP/'final-promotion-repair.json').write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'new_public_paths':53,'existing_production_paths':2,'native_v3':digest(old),'first_failure_preserved':True}))
