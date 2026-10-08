"""Root transport gate for the frozen actual-window runner; no product execution."""
import ast
import hashlib
import json
import shutil
import subprocess
from pathlib import Path, PurePosixPath

ROOT = Path('/workspace/rougezhushou')
PACKET = Path('/workspace/.continuation/ui-090-final-gate-revision')
ORIGINAL = Path('/workspace/.continuation/ui-090-final')
OUT = Path('/workspace/.compat')
COMMIT = '5e2ff697402d06e78b239e01f0b4307b50dd5633'
FIXED = {
    'wine-ui-smoke-090-final-gate-revision.py': '9f7f2d192496f01a4e542cdbbfc1be9932381a6373eb3b46c8fefb2a965e62d9',
    'public-artifacts-manifest-two-gate-revision090.json': '354dc2b0bbd7f311fd302a39473edd8cfe2524ff5cee88effe4f4ae88205abbc',
    'handoff-two-gate-revision090.json': '0a55c070deee0e2ca5d07fcd9e90889c57c646084aa821f003bd2faedc756ec6',
    'two-gate-diff-and-reachability-proof090.json': '6058980599b4aa10e08cb66675d8819b716f1b60c1a98617bce2c764b2dfe8e2',
    'runner-scope-and-source-freeze090-revision.json': '79149d37546fbdef3e709c0239570b746c54726e1e22625f9b0fda701dc2b832',
}
ORIGINAL_FIXED = {
    'wine-ui-smoke-090-final.py': 'bb35222b37dbbdb4416f415a011f3a0b678c5285729ac0bccb76ec8ba336983a',
    'public-artifacts-manifest-final-runner090.json': '7675565345cd55711cb975c83dc49c433d1be7cfe0054634bc68938576822e10',
    'actual-root090-source-binding.json': '0175e121f0df09f724949a85c1a3e4f8c0ab28c671867977c6579c422529879f',
    'old4217-byte-inverse-proof090.json': '904f9af12dd13e24167c9032fe5f4cd047cc58be2e3c42162efea66cfb07c839',
    'runner-scope-and-source-freeze090.json': '0e2884742715adb0832f86c1fe44e575caab7a8e5008cdfd68c47d400f530fde',
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


assert git('rev-parse', 'HEAD').decode().strip() == COMMIT
assert git('rev-parse', 'p2-section-090^{commit}').decode().strip() == COMMIT
assert git('branch', '--show-current').decode().strip() == 'codex/p2-development'
assert git('status', '--porcelain') == b''
for name, digest in FIXED.items():
    assert sha((PACKET / name).read_bytes()) == digest, name
for name, digest in ORIGINAL_FIXED.items():
    assert sha((ORIGINAL / name).read_bytes()) == digest, name
manifest = json.loads((PACKET / 'public-artifacts-manifest-two-gate-revision090.json').read_bytes())
assert len(manifest['files']) == 245
assert sum(row['bytes'] for row in manifest['files']) == 7533110
seen = set()
for row in manifest['files']:
    name = PurePosixPath(row['archive_path'])
    assert not name.is_absolute() and '..' not in name.parts
    assert str(name) == row['archive_path'] and str(name) not in ('', '.')
    assert str(name) not in seen
    seen.add(str(name))
    path = Path(row['source_path'])
    assert path.is_absolute() and path.is_file() and not path.is_symlink()
    raw = path.read_bytes()
    assert len(raw) == row['bytes'] and sha(raw) == row['sha256'], str(name)
ctx = json.loads((OUT / 'wine-validation-090-context.json').read_bytes())
assert ctx['commit'] == COMMIT and len(ctx['source_sha256']) == 730
current = {
    path.relative_to(ROOT).as_posix(): sha(path.read_bytes())
    for folder in ('rouge', 'tests', 'scripts')
    for path in sorted((ROOT / folder).rglob('*'))
    if path.is_file() and path.suffix in ('.py', '.json') and '__pycache__' not in path.parts
}
assert current == ctx['source_sha256']
for name, digest in current.items():
    assert sha(git('show', COMMIT + ':' + name)) == digest, name
runtime = {
    path.relative_to(ROOT).as_posix(): sha(path.read_bytes())
    for path in sorted((ROOT / 'rouge').rglob('*'))
    if path.is_file() and path.suffix in ('.py', '.json') and '__pycache__' not in path.parts
}
assert len(runtime) == 126 and all(current[name] == digest for name, digest in runtime.items())
inverse = json.loads((ORIGINAL / 'old4217-byte-inverse-proof090.json').read_bytes())
assert inverse['passed'] is True and inverse['whole_old_literal_restored_byte_exact'] is True
assert inverse['old_check_rows'] == 4217 and inverse['expected_total_rows'] == 4283
scope = json.loads((ORIGINAL / 'runner-scope-and-source-freeze090.json').read_bytes())
assert scope['planned_new_actual_check_rows'] == {
    '86_real_boolean_and_hidden_producers': 44,
    '87_Back_Attack_controls_and_generic_Skill_exclusion': 4,
    '88_shared_continuous_checkbox_and_timing_JSON': 8,
    '89_saved_state_readonly_training_consumers': 10,
}
assert scope['planned_new_rows_total'] == 66
assert scope['planned_total_actual_check_rows'] == 4283
source = (PACKET / 'wine-ui-smoke-090-final-gate-revision.py').read_bytes()
original = (ORIGINAL / 'wine-ui-smoke-090-final.py').read_bytes()
oldgate = b"['kind']=='coveredmodule'"
newgate = b"['pair_id']=='coveredmodule:oblvns-ranged-skill-vs-normal'"
assert original.count(oldgate) == 2 and source.count(newgate) == 2
assert source.replace(newgate, oldgate) == original
ast.parse(source, filename='wine-ui-smoke-090-final.py')
destination = OUT / 'wine-ui-smoke-090.py'
assert not destination.exists()
for name in ('wine-ui-090.json', 'wine-ui-new-states-090.json.gz', 'wine-window-090.png',
             'wine-movement-reference-090.png', 'wine-sown-tile-control-090.png',
             'wine-medical-trait-090.png', 'wine-ui-090-process.log'):
    assert not (OUT / name).exists(), name
receipt = {
    'passed': True, 'source_commit': COMMIT, 'source_files_verified': 730,
    'root_named_Git_working_context_source_bytes_exact': True,
    'actual_UI_runtime_source_selector_files': 126,
    'runtime126_exact_selector_and_every_value_bound_to_context730': True,
    'public_attachments_verified_before_actual_execution': 245,
    'public_packet_bytes': 7533110,
    'public_manifest_name': 'public-artifacts-manifest-two-gate-revision090.json',
    'fixed_hashes': FIXED, 'original_immutable_fixed_hashes': ORIGINAL_FIXED,
    'two_gate_inverse_to_original_frozen_runner_exact': True,
    'planned_actual_UI_records': 4283,
    'planned_new_UI_records': 66, 'preserved_old_UI_records': 4217,
    'actual_window_tests_or_API_executed_by_preflight': 0,
    'actual_window_validation_passed': False,
    'scope': 'Read-only source and artifact transport gate; runtime maps126, independent root context maps730. Actual Qt remains pending.',
}
with (OUT / 'root-ui-preflight-090.json').open('x', encoding='utf-8') as handle:
    json.dump(receipt, handle, ensure_ascii=False, indent=2)
    handle.write('\n')
shutil.copyfile(PACKET / 'wine-ui-smoke-090-final-gate-revision.py', destination)
assert sha(destination.read_bytes()) == FIXED['wine-ui-smoke-090-final-gate-revision.py']
print(json.dumps(receipt, ensure_ascii=False))
