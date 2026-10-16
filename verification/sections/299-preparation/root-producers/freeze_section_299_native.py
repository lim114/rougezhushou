from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1];PREP=ROOT/'verification/sections/299-preparation'
BASE=ROOT/'.cache/p3-299-native-window/revision2';r=BASE/'READY.json'
assert sha256(r.read_bytes()).hexdigest()=='bc148c16f9447dcfe8049e9cb44b74dc44bf63365961232f39712e3e21c5863b'
p=BASE/'verify_spawn_candidates_window_299.py';pin='8a359acb41c7c8d963f6ebc2a304ae58c9cc415234d80608c055947c4b1f17c7'
assert sha256(p.read_bytes()).hexdigest()==pin
target=ROOT/'scripts/verify_spawn_candidates_window_299.py';assert not target.exists();target.write_bytes(p.read_bytes())
record=json.loads((PREP/'promotion.json').read_bytes());record['promoted']['scripts/verify_spawn_candidates_window_299.py']={'sha256':pin,'bytes':p.stat().st_size}
record.update(native_script_pending=False,kind='root_final_functional_scope_source_freeze_before_actual_product_tests',
 initial_promotion='verification/sections/299-preparation/promotion.json',native_READY_sha256=sha256(r.read_bytes()).hexdigest())
for name,pin in record['promoted'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==pin['sha256']
for name,pin in record['existing_production_changes'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==pin['sha256']
(PREP/'final-promotion.json').write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode())
before=(ROOT/'.cache/run_section_298_window.py').read_bytes()
adapted=before.replace(b'298',b'299').replace(b'verify_event_node_requirements_window_299.py',b'verify_spawn_candidates_window_299.py')
runner=ROOT/'.cache/run_section_299_window.py';assert not runner.exists();runner.write_bytes(adapted)
print(json.dumps({'new_public_paths':len(record['promoted']),'old_production_paths':len(record['existing_production_changes']),'native_sha256':pin}))
