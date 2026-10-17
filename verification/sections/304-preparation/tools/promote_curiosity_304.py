from pathlib import Path
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1]
handoff=ROOT/'.cache/p3-304-backend/revision2/HANDOFF_FINAL.json'
assert sha256(handoff.read_bytes()).hexdigest()=='556cb20b426485a54bd2178defd42eb93075b4810e8d07192b01d77468a9e38c'
info=json.loads(handoff.read_bytes())
candidate=ROOT/info['candidate_root']
rows={}
for name,pin in info['promotion_files'].items():
    source=candidate/name
    assert source.is_file() and not source.is_symlink()
    raw=source.read_bytes()
    assert {'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}==pin
    target=ROOT/name
    assert not target.exists(),name
    rows[name]=raw
for name,pin in info['existing_dependencies'].items():
    raw=(ROOT/name).read_bytes()
    assert {'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}==pin
ui=ROOT/'.cache/p3-304-ui'
baseline=json.loads((ui/'rouge/integration-baseline.json').read_bytes())
assert sha256((ROOT/'rouge/node_catalog_view.py').read_bytes()).hexdigest()==baseline['baseline_sha256']
for name in ('rouge/curiosity_node_rules_view.py','rouge/node_catalog_view.py','tests/test_curiosity_node_rules_view_304.py'):
    assert name=='rouge/node_catalog_view.py' or not (ROOT/name).exists()
    rows[name]=(ui/name).read_bytes()
for name,raw in rows.items():
    target=ROOT/name
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(raw)
report={'section':304,'backend_handoff_sha256':sha256(handoff.read_bytes()).hexdigest(),
        'promoted_source_sha256':{n:sha256(raw).hexdigest() for n,raw in rows.items()},
        'source_build_not_product_acceptance':True,'Qt_or_tests_executed':False}
(ROOT/'verification/sections/304-preparation/promotion.json').write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'promoted_files':len(rows),'passed':True}))
