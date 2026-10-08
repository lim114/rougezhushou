"""Freeze the original inputs, exact-key review and actual source before calls."""
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path('/workspace/rougezhushou')
ROOT089 = '3a59aa0c3d09199caea14de3c5fe89781225a8d6'
FREEZE = HERE / 'new8-execution-freeze090.json'

def describe(path):
    raw = path.read_bytes()
    return {'source_path': str(path), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}

assert not FREEZE.exists(), 'Freeze only once before the authorized requests'
assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO).decode().strip() == ROOT089
assert not subprocess.check_output(['git', 'diff', '--name-only', 'HEAD', '--', 'rouge', 'tests', 'scripts'], cwd=REPO)
proof_path = HERE / 'actual-root089-ui090-source-proof.json'
proof = json.loads(proof_path.read_bytes())
assert proof['actual_root089_commit'] == ROOT089
assert describe(proof_path)['sha256'] == '41bf44ddcc68ccc812cf1d8cacbfa07d062c3d9b3ac59eb429929c8f4f992634'
public = HERE / 'public-schema-actual-root089'
for row in proof['files']:
    current = (REPO / row['source_path']).read_bytes()
    assert len(current) == row['bytes'] and hashlib.sha256(current).hexdigest() == row['sha256']
    if row['source_path'].startswith('rouge/'):
        assert current == (public / row['source_path']).read_bytes()
plan = HERE / 'original-approved-additional8-input-plan090.json'
assert describe(plan)['sha256'] == '31beb7f95a256172591226127562324be6625317fd1ad406baa84851130dd521'
review = HERE / 'review-result-contract'
manifest = review / 'manifest.json'
receipt = review / 'receipt.json'
assert manifest.is_file() and receipt.is_file(), 'Named-source result contract must be sealed'
assert describe(manifest)['sha256'] == '3ee4c0fa7ea7ca7cd80e40e62800d99a310aceab2a9bfa7e70aca31ccd2df177'
assert describe(receipt)['sha256'] == '38d8264606898c2eb3283d0784ae940cccdad3efbe41d88f5f5c0eb19a607da8'
for row in json.loads(manifest.read_bytes())['files']:
    relpath = Path(row['path'])
    assert not relpath.is_absolute() and '..' not in relpath.parts
    actual = describe(review / relpath)
    assert actual['bytes'] == row['bytes'] and actual['sha256'] == row['sha256']
input_files = [plan, proof_path, HERE / 'prepare_named_root089.py',
    HERE / 'preflight_ui090_section088.py', HERE / 'freeze_new8_execution090.py',
    manifest, receipt, review / 'key-inventory.json']
freeze = {
    'format_version': 1,
    'status': 'FROZEN_ACTUAL_ROOT089_APPROVED_NEW8_PRECALL_RUNTIME_PENDING',
    'actual_root089_commit': ROOT089, 'actual_root088_commit': proof['actual_root088_commit'],
    'maintenance_source_files': proof['maintenance_python_json_files'],
    'public_source_files': proof['public_files'],
    'full_maintained_current_and_named_git_package_hashes_verified_before_calls': True,
    'original_plan_inputs_unmodified': True, 'unique_argument_count': 8,
    'maximum_public_calculation_requests': 8, 'maximum_explicit_three_text_requests': 24,
    'expected_formatter_entries_if_source_delegate_unchanged': 32,
    'actual_calculation_calls_so_far': 0, 'actual_formatter_calls_so_far': 0,
    'RunState_constructor_apply_Qt_Wine_tests_network_calls': 0,
    'counterexample_persist_before_resume_and_no_completed_request_reexecution': True,
    'future_actual090_source_freeze_complete': False,
    'files': [describe(path) for path in input_files],
}
FREEZE.write_text(json.dumps(freeze, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(describe(FREEZE), ensure_ascii=False))
