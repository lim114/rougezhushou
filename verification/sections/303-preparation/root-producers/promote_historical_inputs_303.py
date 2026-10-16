from pathlib import Path,PurePosixPath
from hashlib import sha256
import json
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'.cache/p3-303-native-window/historical-local-public-bindings.json'
raw=p.read_bytes();assert sha256(raw).hexdigest()=='df86f3604392ad20e6f20b5a796277ce1796eb7d6ded031ddfab38b2e5522d05'
packet=json.loads(raw)
rows=packet['bindings']
assert len(rows)==10
pending={};reused=[]
for row in rows:
    local=row['local_path'];public=row['public_path']
    assert local.startswith(('.cache/research/map-projection-048/','.cache/batch-048-before/rouge/data/','.cache/game-data/levels/'))
    assert public.startswith(('verification/sections/303-preparation/historical-source-inputs/legacy-cache/','research/p3-spawn-candidates-299/levels/'))
    assert not PurePosixPath(public).is_absolute() and '..' not in PurePosixPath(public).parts
    original=(ROOT/local).read_bytes();assert len(original)==row['bytes'] and sha256(original).hexdigest()==row['sha256']
    json.loads(original)
    if (ROOT/public).exists():
        assert (ROOT/public).read_bytes()==original;reused.append(public)
    else:pending[public]=original
assert len(pending)==8 and len(reused)==2
base=ROOT/'verification/sections/303-preparation/historical-source-inputs'
dest=base/'local-public-bindings.json';assert not dest.exists()
for name,body in pending.items():
    target=ROOT/name;target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as stream:stream.write(body)
dest.write_bytes(raw)
proof={'section':303,'kind':'exact_public_historical_inputs_preserved_not_new_function_or_acceptance',
 'bindings_sha256':sha256(raw).hexdigest(),'copied_public_originals':list(pending),'existing_public_originals_reused':reused,
 'private_state_copied':False,'original_local_inputs_changed':False,'actual_original_cache_test_paths_preserved':True,
 'necessary_runner_must_verify_both_sides_fresh_before_and_after':True}
(base/'promotion.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'preserved_public_json':len(pending),'reused_exact_public_levels':len(reused),'private_state_copied':False,'test_pass_claimed':False}))
