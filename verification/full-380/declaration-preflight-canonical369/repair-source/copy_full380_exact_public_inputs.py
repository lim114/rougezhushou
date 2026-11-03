from pathlib import Path
from hashlib import sha256
import json, subprocess

R = Path(__file__).resolve().parents[1]
P = R / '.cache/full380-canonical-cache-binding-repair/plan.json'
assert sha256(P.read_bytes()).hexdigest() == '443d920669eae3f5228dee562ab222d2c0dc5f89aaeeba0af11242493e3ae6a7'
p = json.loads(P.read_bytes())
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip() == 'afab40c3bb4ea8b95118e8cbe34aa07204c1c615'
assert subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip() == 'codex/p2-development'
assert not (R/'verification/full-380/source-freeze-attempt1.json').exists()
assert not any((R/'.cache/full380-prepared/attempt-1'/x).exists() for x in ('activation380.json','full380-once.json','root-launch'))
assert len(p['bindings']) == 5 and len(p['new_public_files']) == 3
copies = []
for row in p['bindings']:
    source = R/row['local_path']
    assert row['mode'] == 'p3_369' and row['canonical_script'] == 'scripts/verify_current_boss_documents_window_369.py'
    assert source.is_file() and not source.is_symlink() and source.resolve().is_relative_to(R)
    assert all(not parent.is_symlink() for parent in source.parents if parent.is_relative_to(R))
    raw = source.read_bytes()
    assert len(raw) == row['bytes'] and sha256(raw).hexdigest() == row['sha256']
    for original in row['origin_manifests']:
        authority = R/original['path']; auth_raw = authority.read_bytes()
        assert not authority.is_symlink() and len(auth_raw) == original['bytes'] and sha256(auth_raw).hexdigest() == original['sha256']
        assert json.loads(auth_raw)['build_authority_files'][row['local_path']] == {'bytes':row['bytes'],'sha256':row['sha256']}
    dest = R/row['public_path']
    if row in p['new_public_files']:
        assert row['public_path'] == 'verification/full-380/explicit-public-build-inputs/'+row['sha256']+'.json'
        assert not dest.exists()
        dest.parent.mkdir(parents=True,exist_ok=True)
        with dest.open('xb') as out: out.write(raw)
        copies.append({'public_path':row['public_path'],'bytes':len(raw),'sha256':row['sha256']})
    assert dest.is_file() and not dest.is_symlink() and dest.resolve().is_relative_to(R)
    assert dest.read_bytes() == raw
print(json.dumps({'exact_public_copies_created':copies,'bindings_checked':5,'private_data_copied':False,'full_execution_started':False},ensure_ascii=False,indent=2))
