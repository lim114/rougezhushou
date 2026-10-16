from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
PARENT='c2b78e4aa4136fe739067b5ccf9d13b595142320'
def sha(raw):return sha256(raw).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
assert git('branch','--show-current')=='codex/p2-development' and git('rev-parse','HEAD')==PARENT
assert not git('diff','--cached','--name-only')
assert set(git('diff','--name-only').splitlines())=={'DEVELOPMENT_CHECKPOINT.json'}
handoff_path=ROOT/'.cache/p3-303-backend/HANDOFF.json';raw=handoff_path.read_bytes()
assert sha(raw)=='542ae38af9f39788310cd4d2c0bdfc7e3a99f1714fe4bf9f59be7363589fe8d2'
packet=json.loads(raw);candidate=ROOT/packet['candidate_root']
for name,pin in packet['reused_public_authority'].items():
    body=(ROOT/name).read_bytes();assert sha(body)==pin['sha256'] and len(body)==pin['bytes'],name
pending={};existing={};before={}
for name,pin in packet['promotion_files'].items():
    assert not Path(name).is_absolute() and '..' not in Path(name).parts and not name.startswith(('.cache/','.local/'))
    body=(candidate/name).read_bytes();assert sha(body)==pin['sha256'] and len(body)==pin['bytes'],name
    if name.endswith('.py'):ast.parse(body)
    if name=='rouge/data/fixed-landmark-references.json':
        old=(ROOT/name).read_bytes();assert sha(old)=='63ec9488f8f905d2ced1a4e349413e9c92d78125b9f1c94c00293cafa4d348f5'
        original=json.loads(old);new=json.loads(body)
        for group in ('references','stages'):
            assert all(new[group][k]==v for k,v in original[group].items())
        assert len(new['references'])==12 and len(new['stages'])==21 and sum(len(v['points']) for v in new['references'].values())==107
        existing[name]=body;before[name]=sha(old)
        out=ROOT/'verification/sections/303-preparation/before'/name;out.parent.mkdir(parents=True,exist_ok=True);assert not out.exists();out.write_bytes(old)
    else:
        assert not (ROOT/name).exists(),name
        pending[name]=body
assert len(pending)==15 and len(existing)==1
maintenance={}
for name in ('tests/test_direct_landmark_294.py','tests/test_map_projection_048.py'):
    archived=ROOT/'verification/sections/303-preparation/historical-tests/before'/name
    old=(ROOT/name).read_bytes();assert archived.read_bytes()==old
    body=(ROOT/'.cache/p3-303-parent'/name).read_bytes();ast.parse(body)
    expected='263cea49f3f19514a5fb6be72a3dc42926ba4cab6007bbc14d21a489a07c1f52' if '294' in name else 'b2454d2c5c53a3b81164cce528f6dcd5c9f99aa2b0a3027b721e23aa50e145de'
    assert sha(body)==expected
    maintenance[name]=body;before[name]=sha(old)
record={'section':303,'kind':'partial_backend_and_historical_test_promotion_before_native_source_freeze_and_formal_verification',
 'at_utc':datetime.now(timezone.utc).isoformat(),'parent_commit':PARENT,
 'promoted':{n:sha(v) for n,v in pending.items()},'existing_production_changes':{n:sha(v) for n,v in existing.items()},
 'historical_test_maintenance':{n:sha(v) for n,v in maintenance.items()},'before_existing_sha256':before,
 'old_tests_modified':True,'old_test_maintenance_scope_exact':True,'native_canonical_promoted':False,
 'formal_product_or_native_or_publication_passed':False,'source_pixel_adjustments':0,'source_request_count':89,
 'sourceaccepted_new_points':49,'new_point_totals':[12,21,107],'whole_map_gaps_unchanged':[81,59],
 'author_backend_handoff':'.cache/p3-303-backend/HANDOFF.json','author_backend_handoff_sha256':sha(raw)}
target=ROOT/'verification/sections/303-preparation/backend-promotion.json';assert not target.exists()
for name,body in pending.items():
    out=ROOT/name;out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('xb') as stream:stream.write(body)
for name,body in {**existing,**maintenance}.items():(ROOT/name).write_bytes(body)
target.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'new_functional_sources':15,'existing_production_sources':1,'historical_test_maintenance':2,'native_not_yet_promoted':True,'actual_product_pass_claimed':False}))
