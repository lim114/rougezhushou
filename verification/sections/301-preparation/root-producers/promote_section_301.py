from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,json,subprocess
ROOT=Path(__file__).resolve().parents[1]
PARENT='5607cbc46c9cf17a841939a778a247e6e1a2a371'
def sha(raw):return sha256(raw).hexdigest()
def bound(name,pin):
    raw=(ROOT/name).read_bytes();assert sha(raw)==pin,name
    return json.loads(raw)
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='codex/p2-development'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==PARENT
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=ROOT)
assert set(subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines())=={'DEVELOPMENT_CHECKPOINT.json','WORK_IN_PROGRESS.md'}
backend_name='.cache/p3-301-backend/HANDOFF.json';view_name='.cache/p3-301-view/HANDOFF.json'
native_name='.cache/p3-301-native-window/READY.json'
backend=bound(backend_name,'3ed3e4f09145eb13558ab6af1f37dde0c6ac3f529a6f15860b1b9bcaa70e9ab3')
view=bound(view_name,'ca50b3fb718c0efb1e2297bb496d5206237ae4675d7ad5df9b9b2f70c6653ca5')
native=bound(native_name,'e5798bff19420a0f91dcc766ecda7d92ab50f27ef3684fc38f0845637d979cf9')
pending={}
def add(name,source,pin):
    assert name not in pending and not (ROOT/name).exists(),name
    assert not name.startswith(('.cache/','.local/')) and name!='local-settings.json'
    raw=Path(source).read_bytes();assert sha(raw)==pin,name
    if name.endswith('.py'):ast.parse(raw)
    pending[name]=raw
for name,pin in backend['existing_public_dependencies_not_to_promote'].items():
    raw=(ROOT/name).read_bytes();assert sha(raw)==pin['sha256'] and len(raw)==pin['bytes'],name
for name,pin in backend['promote_files'].items():add(name,Path(backend['candidate_root'])/name,pin['sha256'])
for name,pin in view['promotion_allowlist'].items():add(name,pin['candidate'],pin['sha256'])
name='tests/test_named_reward_integration_301.py'
add(name,ROOT/'.cache/p3-301-parent'/name,'ff9ac9f639cc6c78c8ac2ec72d00c596eccd8e8558058b50f81ed8e52bfa6961')
add('scripts/verify_named_reward_items_window_301.py',ROOT/'.cache/p3-301-native-window/verify_named_reward_items_window_301.py',
    '0354369e37c1dbb9a5567a5d18b5a7336e63bd46b97b0cb6396fc34ed6f9989a')
old_name='rouge/node_catalog_view.py';before=(ROOT/old_name).read_bytes()
assert sha(before)=='2e51d99f86bff9ca85e49db63493dc80ed488f815577defaa2db141c2dce123c'
assert (ROOT/'verification/sections/301-preparation/before'/old_name).read_bytes()==before
after=(ROOT/'.cache/p3-301-parent'/old_name).read_bytes()
assert sha(after)=='65420d73c69c275d96b63b14274e7b481b5795ca7053ea9f1b0412027e659bf5'
assert len(pending)==18
for name,raw in pending.items():
    target=ROOT/name;target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as stream:stream.write(raw)
(ROOT/old_name).write_bytes(after)
record={'section':301,'kind':'root_reviewed_functional_promotion_before_formal_verification',
 'at_utc':datetime.now(timezone.utc).isoformat(),'parent_commit':PARENT,
 'promoted':{n:sha(v) for n,v in pending.items()},'existing_production_changes':{old_name:sha(after)},
 'before_existing_sha256':{old_name:sha(before)},'old_tests_modified':False,
 'author_backend_handoff':backend_name,'author_backend_handoff_sha256':sha((ROOT/backend_name).read_bytes()),
 'author_view_handoff':view_name,'author_view_handoff_sha256':sha((ROOT/view_name).read_bytes()),
 'native_ready':native_name,'native_ready_sha256':sha((ROOT/native_name).read_bytes()),
 'formal_verification_or_publication_claimed':False,'runtime_reads_complete_primary_table':False,
 'old17_records_preserved':True,'rest4_original_entry_restored':False,
 'fixed_reference_inventory':{'events':10,'choices':16,'items':13,'RELIC':12,'SCRAP':1}}
target=ROOT/'verification/sections/301-preparation/promotion.json'
with target.open('x',encoding='utf8') as stream:stream.write(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'new_files':len(pending),'existing_production_files':1,'sources':19,'formal_verified':False}))
