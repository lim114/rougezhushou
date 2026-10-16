from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.cache/p3-298-runtime-preparation'
READY=BASE/'READY.json';assert sha256(READY.read_bytes()).hexdigest()=='67103d296025cf6a6501ccb0483cd5c557eaaaeb5d77ab051fcfe56b74b52970'
r=json.loads(READY.read_bytes())
for name,pin in r['promotion_allowlist'].items():
 p=BASE/name if name.startswith('tests/')else BASE/Path(name).name
 assert sha256(p.read_bytes()).hexdigest()==pin['sha256']and p.stat().st_size==pin['bytes']and not(ROOT/name).exists()
for name in r['promotion_allowlist']:
 source=BASE/name if name.startswith('tests/')else BASE/Path(name).name
 target=ROOT/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes())
prep=ROOT/'verification/sections/298-preparation'
backend=json.loads((prep/'promotion.json').read_bytes())
promoted={**backend['promoted'],**r['promotion_allowlist']}
name='tests/test_event_node_requirements_integration_298.py';p=ROOT/name
promoted[name]={'sha256':sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'authorship':'root actual integration tests, not cache promotion'}
changed={}
for name in ('rouge/node_catalog.py','rouge/event_planning.py','rouge/node_catalog_view.py','rouge/player_node_information.py'):
 p=ROOT/name;changed[name]={'sha256':sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
row={'section':298,'kind':'complete_root_functional_scope_source_freeze_before_actual_tests',
 'promoted':promoted,'existing_production_changes':changed,
 'initial_backend_promotion_receipt':'verification/sections/298-preparation/promotion.json',
 'runtime_READY_sha256':sha256(READY.read_bytes()).hexdigest(),
 'historical_test_migration':'verification/sections/298-preparation/historical-test-migration.json'}
(prep/'root-promotion.json').write_bytes((json.dumps(row,ensure_ascii=False,indent=2)+'\n').encode())
old=(ROOT/'.cache/run_section_297_window.py').read_bytes()
new=old.replace(b'297',b'298').replace(b'verify_expedition_results_window_298.py',b'verify_event_node_requirements_window_298.py')
p=ROOT/'.cache/run_section_298_window.py';assert not p.exists();p.write_bytes(new)
print(json.dumps({'new_public_paths':len(promoted),'existing_production_seams':len(changed),'runtime_ready_verified':True}))
