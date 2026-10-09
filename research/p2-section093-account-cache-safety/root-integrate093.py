"""Root-only transport from the actual section92 commit; no project imports."""
from pathlib import Path
import ast
import hashlib
import json
import subprocess
import sys

ROOT = Path('/workspace/rougezhushou')
LOCAL = Path('/workspace/.continuation')
BASE = 'f509d186e501bfcfd042e45b46e398ec756840ec'
PLAN = LOCAL / 'root-integration-plan093.json'
TARGETS = {'rouge/app.py', 'rouge/account_cache.py', 'tests/test_account_cache_093.py', 'scripts/verify_cloud.py'}
def sha(data):
    return hashlib.sha256(data).hexdigest()
def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)
def snapshot():
    return {path.relative_to(ROOT).as_posix(): sha(path.read_bytes())
            for directory in ('rouge', 'tests', 'scripts')
            for path in sorted((ROOT / directory).rglob('*'))
            if path.is_file() and path.suffix in ('.py', '.json') and '__pycache__' not in path.parts}
def save_new(path, value):
    with path.open('xb') as stream:
        stream.write((json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode())
assert git('branch', '--show-current').decode().strip() == 'codex/p2-development'
assert git('rev-parse', 'HEAD').decode().strip() == BASE
phase = sys.argv[1]
if phase == 'prepare':
    assert not git('status', '--porcelain').strip()
    # Metadata names come from the actual finalized handoff, never a convention.
    manifest_path = Path(sys.argv[2])
    packet = manifest_path.parent
    handoff_path = Path(sys.argv[4])
    assert sha(manifest_path.read_bytes()) == sys.argv[3]
    assert handoff_path.parent == packet and sha(handoff_path.read_bytes()) == sys.argv[5]
    manifest = json.loads(manifest_path.read_bytes())
    assert manifest['schema_version'] == 1
    for row in manifest['files']:
        source = packet / row['archive_path']
        data = source.read_bytes()
        assert len(data) == row['bytes'] and sha(data) == row['sha256'], source
    transport_path = Path(sys.argv[6])
    assert transport_path.parent == packet
    transport = json.loads(transport_path.read_bytes())
    changes = transport['changes']
    assert len(changes) == 4 and {row['target_path'] for row in changes} == TARGETS
    for row in changes:
        target = ROOT / row['target_path']
        if row['original_sha256'] is None:
            assert not target.exists()
        else:
            before = target.read_bytes()
            assert sha(before) == row['original_sha256']
            assert before == git('show', BASE + ':' + row['target_path'])
        source = Path(row['source_path'])
        assert source.is_relative_to(packet / 'candidate')
        after = source.read_bytes()
        assert len(after) == row['bytes'] and sha(after) == row['new_sha256']
        ast.parse(after.decode(), filename=row['target_path'])
        if row['target_path'] == 'rouge/app.py':
            assert b'\r\n' in after and b'\n' not in after.replace(b'\r\n', b'')
        else:
            assert b'\r\n' not in after
    before = snapshot()
    assert len(before) == 730
    assert before == json.loads((LOCAL / 'root-source-092.json').read_bytes())['source_sha256_after']
    save_new(PLAN, {'format_version': 1, 'status': 'PREPARED_PENDING_FORMAL_REVIEW_NOT_APPLIED', 'base': BASE,
        'candidate_directory': str(packet), 'candidate_manifest': str(manifest_path), 'candidate_manifest_sha256': sys.argv[3],
        'candidate_handoff_sha256': sys.argv[5], 'transport_sha256': sha(transport_path.read_bytes()),
        'changes': changes, 'before_maintained_sha256': before, 'project_calls': 0})
    print(json.dumps({'prepared': True, 'files': 4, 'before_maintained': 730, 'project_calls': 0}))
elif phase == 'apply':
    assert not git('status', '--porcelain').strip()
    plan = json.loads(PLAN.read_bytes())
    assert snapshot() == plan['before_maintained_sha256']
    receipt_path = Path(sys.argv[2])
    raw = receipt_path.read_bytes()
    assert sha(raw) == sys.argv[3]
    receipt = json.loads(raw)
    assert receipt['status'] == sys.argv[4] and 'PASS' in receipt['status']
    for row in plan['changes']:
        data = Path(row['source_path']).read_bytes()
        assert len(data) == row['bytes'] and sha(data) == row['new_sha256']
    for row in plan['changes']:
        (ROOT / row['target_path']).write_bytes(Path(row['source_path']).read_bytes())
    save_new(LOCAL / 'root-integration-applied093.json', {'format_version': 1,
        'status': 'APPLIED_PENDING_ROOT_REGRESSION_AND_ACTUAL_WINDOW', 'base': BASE, 'changes': plan['changes'],
        'independent': {'path': str(receipt_path), 'sha256': sys.argv[3], 'status': sys.argv[4]}, 'project_calls': 0})
    print(json.dumps({'applied': True, 'files': 4, 'project_calls': 0}))
elif phase == 'source':
    plan = json.loads(PLAN.read_bytes())
    before = plan['before_maintained_sha256']
    current = snapshot()
    assert len(current) == 732 and set(before) < set(current)
    new = sorted(set(current) - set(before))
    changed = sorted(name for name in before if current[name] != before[name])
    assert new == ['rouge/account_cache.py', 'tests/test_account_cache_093.py']
    assert changed == ['rouge/app.py', 'scripts/verify_cloud.py']
    for row in plan['changes']:
        assert current[row['target_path']] == row['new_sha256']
    save_new(LOCAL / 'root-source-093.json', {'format_version': 1, 'passed': True, 'base': BASE,
        'old_maintained': 730, 'current_maintained': 732, 'unchanged_maintained': 728,
        'changed_maintained': changed, 'new_maintained': new, 'source_sha256_after': current,
        'frozen_candidate_bytes_exact': True, 'project_calls': 0})
    print(json.dumps({'passed': True, 'current_maintained': 732, 'old_unchanged': 728, 'changed': changed, 'new': new, 'project_calls': 0}))
else:
    raise ValueError(phase)
