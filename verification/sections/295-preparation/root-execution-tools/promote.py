from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import ast, json
ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'.cache/p3-295-item-reference'
DEST=ROOT/'verification/sections/295-preparation'
handoff=json.loads((CACHE/'HANDOFF.json').read_bytes())
assert sha256((CACHE/'HANDOFF.json').read_bytes()).hexdigest()=='7a8dd00aeeb163552a3f9dd4674dc9a6bf56d2f83aa17f2aced6cdaf2b95fa5a'
root=ROOT/'.cache/p3-295-root-integration'
integration=json.loads((root/'HANDOFF.json').read_bytes());plan=[]
for row in handoff['promotion_allowlist']:
    name=row['path'];raw=(CACHE/'candidate'/name).read_bytes()
    assert sha256(raw).hexdigest()==row['sha256'] and len(raw)==row['bytes'] and not(ROOT/name).exists()
    plan.append((name,raw))
for row in integration['files']:
    name=row['path'];assert sha256((ROOT/name).read_bytes()).hexdigest()==row['before_sha256']
    raw=(root/name).read_bytes();assert sha256(raw).hexdigest()==row['after_sha256'];plan.append((name,raw))
for name,source,expected in [('tests/test_documented_item_integration_295.py',root/'test_documented_item_integration_295.py',None),
    ('scripts/verify_documented_choice_item_window_295.py',ROOT/'.cache/p3-295-native-window/revision3/verify_documented_choice_item_window_295.py',
     'a93e69365eef3032a20c9b65c90ea598990a590b357a9fc69f978a5ce7b10f89')]:
    raw=source.read_bytes();assert not(ROOT/name).exists()
    if expected:assert sha256(raw).hexdigest()==expected
    ast.parse(raw,filename=name);plan.append((name,raw))
assert len(plan)==18
for name,row in handoff['external_existing_public_dependencies'].items():assert sha256((ROOT/name).read_bytes()).hexdigest()==row['sha256']
for name,raw in plan:
    target=ROOT/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
archive={'candidate-HANDOFF.json':CACHE/'HANDOFF.json','INTEGRATION_CONTRACT.md':CACHE/'INTEGRATION_CONTRACT.md',
         'root-integration-HANDOFF.json':root/'HANDOFF.json','pre295-query-baseline.json':root/'pre295-query-baseline.json',
         'native-READINESS.json':ROOT/'.cache/p3-295-native-window/revision3/READINESS.json',
         'native-CONTRACT.md':ROOT/'.cache/p3-295-native-window/revision3/CONTRACT.md',
         'independent-candidate-review.json':ROOT/'.cache/p3-295-independent-review/review.json'}
for folder in ('source-build-first','backend-first','backend-first-process'):
    for source in (CACHE/folder).iterdir():
        if source.is_file() and source.suffix in {'.py','.json','.txt'}:archive[folder+'/'+source.name]=source
for name,source in archive.items():
    target=DEST/name;target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as stream:stream.write(source.read_bytes())
receipt={'section':295,'kind':'ACTUAL_ROOT_SOURCE_PROMOTION_NOT_ACCEPTANCE','at_utc':datetime.now(timezone.utc).isoformat(),
         'promoted':{name:sha256(raw).hexdigest() for name,raw in plan},'old_node_catalog_unchanged':True,
         'root_owned_existing_files':['rouge/player_node_information.py','rouge/node_catalog_view.py'],
         'all_38_old_reward_query_outputs_preserved_for_test':True,'product_tests_or_native_executed':False,
         'archived_preparation':{name:{'sha256':sha256(source.read_bytes()).hexdigest(),'bytes':source.stat().st_size} for name,source in archive.items()}}
with(DEST/'promotion.json').open('xb') as stream:stream.write((json.dumps(receipt,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'section':295,'promoted':len(plan),'existing_production_files_changed':2,'acceptance_passed':False}))
