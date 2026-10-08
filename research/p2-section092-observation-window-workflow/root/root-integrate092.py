"""Exact root integration of the reviewed window workflow; no project imports."""
import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path('/workspace/rougezhushou')
LOCAL = Path('/workspace/.continuation')
BASE = '59961ec3d633ac91b01014fb06b357d45e5979f7'
CANDIDATE = ROOT / 'research/p2-section091-attack-condition-regeneration/future092-source-and-unexecuted-candidate'
MANIFEST_SHA = '285a6ae53be573b6323f3144fd2a9ed26237162abe211faff7b0a5a1b772fece'
PLAN = LOCAL / 'root-integration-plan092.json'
sha = lambda b: hashlib.sha256(b).hexdigest()

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)

def snapshot():
    return {p.relative_to(ROOT).as_posix(): sha(p.read_bytes())
            for directory in ('rouge', 'tests', 'scripts')
            for p in sorted((ROOT / directory).rglob('*'))
            if p.is_file() and p.suffix in ('.py', '.json') and '__pycache__' not in p.parts}

def write_new(path, data):
    with path.open('xb') as out:
        out.write((json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode())

def check_packet():
    raw = (CANDIDATE / 'public-candidate-manifest.json').read_bytes()
    assert sha(raw) == MANIFEST_SHA
    packet = json.loads(raw)
    assert packet['format_version'] == 1 and packet['file_count'] == 49
    rows = packet['files']
    assert len(rows) == 49 and sum(row['bytes'] for row in rows) == packet['total_bytes'] == 1048120
    names = set()
    for row in rows:
        name = row['archive_path']
        relative = Path(name)
        assert not relative.is_absolute() and '..' not in relative.parts and name not in names
        names.add(name)
        data = (CANDIDATE / relative).read_bytes()
        assert len(data) == row['bytes'] and sha(data) == row['sha256'], name
        assert git('show', f'{BASE}:{(CANDIDATE / relative).relative_to(ROOT).as_posix()}') == data, name
    return {'manifest': str(CANDIDATE / 'public-candidate-manifest.json'), 'sha256': MANIFEST_SHA, 'files': 49, 'bytes': 1048120, 'actual_committed_payload_bytes_exact': True}

phase = sys.argv[1]
assert git('branch', '--show-current').decode().strip() == 'codex/p2-development'
assert git('rev-parse', 'HEAD').decode().strip() == BASE
if phase == 'prepare':
    assert not git('status', '--porcelain').strip()
    packet = check_packet()
    handoff = json.loads((CANDIDATE / 'candidate-handoff.json').read_bytes())
    changes = []
    for original in handoff['products']:
        name = 'rouge/' + Path(original['candidate_path']).name
        source = CANDIDATE / 'candidate' / name
        before = git('show', f'{BASE}:{name}')
        after = source.read_bytes()
        assert (ROOT / name).read_bytes() == before == (CANDIDATE / 'prospective91-base' / name).read_bytes()
        assert sha(before) == original['old_sha256'] and sha(after) == original['new_sha256']
        assert len(before) == original['old_bytes'] and len(after) == original['new_bytes']
        assert (b'\r\n' in before) == (b'\r\n' in after)
        ast.parse(after.decode(), filename=name)
        changes.append({'target_path': name, 'source_path': str(source), 'original_sha256': sha(before), 'new_sha256': sha(after), 'bytes': len(after)})
    before = snapshot()
    assert len(before) == 730 and {row['target_path'] for row in changes} == {'rouge/app.py', 'rouge/reporting.py'}
    write_new(PLAN, {'format_version': 1, 'status': 'PREPARED_PENDING_FORMAL_REVIEW_NOT_APPLIED', 'base': BASE, 'original_archived_packet': packet, 'changes': changes, 'before_maintained_sha256': before, 'project_calls': 0})
    print(json.dumps({'prepared': True, 'files': 2, 'maintained': 730, 'project_calls': 0}))
elif phase == 'apply':
    assert not git('status', '--porcelain').strip()
    plan = json.loads(PLAN.read_bytes())
    assert snapshot() == plan['before_maintained_sha256']
    receipt_path = Path(sys.argv[2])
    receipt_raw = receipt_path.read_bytes()
    assert sha(receipt_raw) == sys.argv[3]
    receipt = json.loads(receipt_raw)
    assert sys.argv[4] == receipt['status'] and 'PASS' in receipt['status']
    for row in plan['changes']:
        assert sha((ROOT / row['target_path']).read_bytes()) == row['original_sha256']
        data = Path(row['source_path']).read_bytes()
        assert sha(data) == row['new_sha256'] and len(data) == row['bytes']
    for row in plan['changes']:
        (ROOT / row['target_path']).write_bytes(Path(row['source_path']).read_bytes())
    write_new(LOCAL / 'root-integration-applied092.json', {'format_version': 1, 'status': 'APPLIED_PENDING_ROOT_REGRESSION_AND_ACTUAL_WINDOW', 'base': BASE, 'changes': plan['changes'], 'independent': {'path': str(receipt_path), 'sha256': sha(receipt_raw), 'status': receipt['status']}, 'project_calls': 0})
    print(json.dumps({'applied': True, 'files': 2, 'project_calls': 0}))
elif phase == 'source':
    plan = json.loads(PLAN.read_bytes())
    current = snapshot()
    before = plan['before_maintained_sha256']
    assert set(current) == set(before) and len(current) == 730
    changed = {name for name in current if current[name] != before[name]}
    assert changed == {'rouge/app.py', 'rouge/reporting.py'}
    for row in plan['changes']:
        assert current[row['target_path']] == row['new_sha256']
    write_new(LOCAL / 'root-source-092.json', {'format_version': 1, 'passed': True, 'base': BASE, 'old_maintained': 730, 'current_maintained': 730, 'unchanged_maintained': 728, 'changed_maintained': sorted(changed), 'source_sha256_after': current, 'frozen_candidate_bytes_exact': True, 'project_calls': 0})
    print(json.dumps({'passed': True, 'maintained': 730, 'unchanged': 728, 'changed': sorted(changed), 'project_calls': 0}))
else:
    raise ValueError(phase)
