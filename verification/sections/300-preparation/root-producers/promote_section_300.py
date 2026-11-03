from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json, subprocess, ast

ROOT = Path(__file__).resolve().parents[1]
PARENT = '796c5d406a8d4ac36d924ce6d70db9081267ef68'
def sha(raw): return sha256(raw).hexdigest()
def load(relative, expected):
    raw = (ROOT/relative).read_bytes(); assert sha(raw) == expected, relative
    return json.loads(raw)
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip() == 'codex/p2-development'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip() == PARENT
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=ROOT)
assert set(subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines()) == {'DEVELOPMENT_CHECKPOINT.json','WORK_IN_PROGRESS.md'}
receipt = ROOT/'verification/sections/300-preparation/promotion.json'
assert not receipt.exists()
backend_name = '.cache/p3-300-backend/HANDOFF.json'
view_name = '.cache/p3-300-view/HANDOFF.json'
native_name = '.cache/p3-300-native-window/READY.json'
backend = load(backend_name,'461ef31062db4462d09f79fec4c6f46f974b5859da9dccdab2a1ab333d90b28d')
view = load(view_name,'f7b639ae271b34f73b827a1fb473f53abb35970594892efc6b65ca0791ce5c87')
native = load(native_name,'4701943194ffab3c2d4befc3bc6f2a9165dfbbd8abe2d1afe31aef07fbe378ed')
pending = {}
def add(name, source, pin):
    assert name not in pending and not (ROOT/name).exists(), name
    assert not name.startswith(('.local/','.cache/')) and name != 'local-settings.json'
    raw = source.read_bytes(); assert sha(raw) == pin, name
    if name.endswith('.py'): ast.parse(raw)
    pending[name] = raw
for name, pin in backend['promote_files'].items():
    add(name, Path(backend['candidate_directory_absolute'])/name, pin['sha256'])
for name, pin in view['promotion_allowlist'].items():
    add(name, Path(pin['candidate']), pin['sha256'])
name = 'tests/test_future_region_integration_300.py'
add(name,ROOT/'.cache/p3-300-parent/revision2'/name,'27ca7e9e6cfe1811abc9d0575f06ca0ab63b08f490877340c357c20aaa641954')
add(native['canonical'], ROOT/'.cache/p3-300-native-window/verify_future_region_effects_window_300.py',
    'b430008537a70f094ef9713e82f158318eff796cc0d079f2e0c1b50e75304213')
old_name = 'rouge/node_catalog_view.py'
before = (ROOT/old_name).read_bytes()
assert sha(before) == 'c6a7f25e00644c1ec1f6b6a2ad6517b29977207f32558be65ebc22957018f4bf'
assert (ROOT/'verification/sections/300-preparation/before'/old_name).read_bytes() == before
old_new = (ROOT/'.cache/p3-300-parent/revision2'/old_name).read_bytes()
assert sha(old_new) == '2e51d99f86bff9ca85e49db63493dc80ed488f815577defaa2db141c2dce123c'
ast.parse(old_new)
assert len(pending) == 19
for name, raw in pending.items():
    path = ROOT/name; path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('xb') as stream: stream.write(raw)
(ROOT/old_name).write_bytes(old_new)
record = {'section':300,'kind':'root_reviewed_functional_promotion_before_formal_verification',
    'at_utc':datetime.now(timezone.utc).isoformat(),'parent_commit':PARENT,
    'promoted':{n:sha(v) for n,v in pending.items()},
    'existing_production_changes':{old_name:sha(old_new)},
    'before_existing_sha256':{old_name:sha(before)},
    'author_backend_handoff':backend_name,'author_backend_handoff_sha256':sha((ROOT/backend_name).read_bytes()),
    'author_view_handoff':view_name,'author_view_handoff_sha256':sha((ROOT/view_name).read_bytes()),
    'native_ready':native_name,'native_ready_sha256':sha((ROOT/native_name).read_bytes()),
    'formal_verification_or_publication_claimed':False,'old_tests_modified':False,
    'prepromotion_contract_mismatch':{'original_parent_draft_retained':True,
        'reason':'Parent first draft used EVENT but frozen backend declares EVENT_ID; corrected before execution.',
        'real_test_failure_claimed':False},
    'runtime_full_primary_table_read':False,'full_build_authority_retained':True}
with receipt.open('x',encoding='utf8') as stream: stream.write(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'section':300,'new_files':len(pending),'existing_source_changed':old_name,
                  'total_functional_sources':len(pending)+1,'formal_verification_claimed':False}))
