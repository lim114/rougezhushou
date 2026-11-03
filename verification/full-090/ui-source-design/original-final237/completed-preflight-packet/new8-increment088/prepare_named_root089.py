"""Transport the named actual root089 source before the single authorized new8 pass."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path('/workspace/rougezhushou')
SOURCE_PLAN = Path('/workspace/.continuation/root-transport-preparation090/additional8-input-plan090.json')
SOURCE_STAGE = Path('/workspace/.continuation/root-transport-preparation090/public-artifacts-manifest-input-preparation090.json')
ROOT088 = '66df88c3274e37ba0f176adcd862a439a6f99767'
SOURCE_PLAN_SHA = '31beb7f95a256172591226127562324be6625317fd1ad406baa84851130dd521'

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def git(*args):
    return subprocess.check_output(['git', *args], cwd=REPO)

args = argparse.ArgumentParser()
args.add_argument('--named-root089', required=True)
root089 = args.parse_args().named_root089
assert git('rev-parse', 'p2-section-089').decode().strip() == root089
assert git('rev-parse', 'p2-section-088').decode().strip() == ROOT088
assert git('merge-base', '--is-ancestor', ROOT088, root089) == b''
assert sha(SOURCE_PLAN.read_bytes()) == SOURCE_PLAN_SHA
assert sha(SOURCE_STAGE.read_bytes()) == '2baa273240109b09d8d4446752a877a2ae8b298848745399cdf1f78034f91047'
assert not (HERE / 'actual-root089-ui090-source-proof.json').exists()
plan_copy = HERE / 'original-approved-additional8-input-plan090.json'
plan_copy.write_bytes(SOURCE_PLAN.read_bytes())
entries = {}
for entry in git('ls-tree', '-r', '-z', root089).split(b'\0'):
    if not entry:
        continue
    head, name = entry.split(b'\t', 1)
    mode, kind, blob = head.split()
    name = name.decode()
    if name.split('/')[0] in ('rouge', 'tests', 'scripts') and Path(name).suffix in ('.py', '.json'):
        assert kind == b'blob'
        entries[name] = blob.decode()
package = HERE / 'public-schema-actual-root089'
package.mkdir()
names = sorted(entries)
process = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=REPO,
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
process.stdin.write(''.join(entries[name] + '\n' for name in names).encode())
process.stdin.close()
public = {}
rows = []
for name in names:
    blob, kind, length = process.stdout.readline().rstrip(b'\n').split()
    raw = process.stdout.read(int(length))
    assert process.stdout.read(1) == b'\n'
    assert blob.decode() == entries[name] and kind == b'blob'
    digest = sha(raw)
    rows.append({'source_path': name, 'git_blob_sha1': entries[name], 'bytes': len(raw), 'sha256': digest})
    if name.startswith('rouge/'):
        target = package / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        public[name] = digest
assert process.wait() == 0
changes = git('diff', '--name-only', ROOT088, root089, '--', 'rouge').decode().splitlines()
assert changes == ['rouge/run_state.py'], changes
public88 = {}
for name in public:
    if name == 'rouge/run_state.py':
        continue
    raw88 = git('show', f'{ROOT088}:{name}')
    assert sha(raw88) == public[name], name
    public88[name] = sha(raw88)
source_contract = json.loads(SOURCE_PLAN.read_bytes())
assert len(source_contract['cases']) == 8
assert len({json.dumps(row['input'], sort_keys=True) for row in source_contract['cases']}) == 8
proof = {
    'format_version': 1,
    'status': 'PASS_NAMED_ACTUAL_ROOT089_PUBLIC_PACKAGE_TRANSPORT_NEW8_RUNTIME_PENDING',
    'actual_root089_commit': root089, 'actual_root088_commit': ROOT088,
    'maintenance_python_json_files': len(rows), 'public_files': len(public),
    'public_source_sha256': public, 'files': rows,
    'public_package': str(package), 'all_public_bytes_match_named_git_blobs': True,
    'actual088_to089_public_changes': changes,
    'all_non_runstate_public_bytes_exact_actual088': True,
    'approved_new8_original_plan_sha256': SOURCE_PLAN_SHA,
    'approved_new8_original_stage_manifest_sha256': sha(SOURCE_STAGE.read_bytes()),
    'approved_new8_original_inputs_unmodified': True,
    'future_actual090_source_freeze_complete': False,
    'source_body_package_rebuildable_from_named_git_without_duplicate_archive': True,
    'API_helpers_formatter_RunState_constructor_apply_Qt_Wine_tests_network_calls': 0,
}
path = HERE / 'actual-root089-ui090-source-proof.json'
path.write_text(json.dumps(proof, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': proof['status'], 'root089': root089,
    'maintained': len(rows), 'public': len(public), 'proof_path': str(path),
    'proof_sha256': sha(path.read_bytes()), 'actual_new8_API_calls': 0}))
