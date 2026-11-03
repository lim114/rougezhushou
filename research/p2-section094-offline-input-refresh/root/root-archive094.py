"""Archive explicit frozen source packets only after root's actual94 apply."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path('/workspace/rougezhushou')
LOCAL = Path('/workspace/.continuation')
DEST = ROOT / 'research/p2-section094-offline-input-refresh'
BASE = 'f509d186e501bfcfd042e45b46e398ec756840ec'
HELPER = ROOT / 'research/p2-section092-observation-window-workflow/root/root-archive092.py'
raw = HELPER.read_bytes()
assert raw == subprocess.check_output(['git', 'show', BASE + ':' + HELPER.relative_to(ROOT).as_posix()], cwd=ROOT)
text = raw.decode()
assert text.count('phase = sys.argv[1]') == 1
ns = {}
exec(compile(text.split('phase = sys.argv[1]', 1)[0], str(HELPER), 'exec'), ns)
ns['DEST'] = DEST
row, sealed, copy_rows, save_new = (ns[name] for name in ('row', 'sealed', 'copy_rows', 'save_new'))

phase = sys.argv[1]
if phase == 'prepare':
    assert not DEST.exists()
    assert subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip() == 'codex/p2-development'
    guard = json.loads((LOCAL / 'root-source-094.json').read_bytes())
    assert guard['passed'] is True and guard['current_maintained'] == 732
    for rel, digest in guard['source_sha256_after'].items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == digest
    binding = guard['actual93_completed_working_tree_binding']
    receipt = Path(binding['receipt_path'])
    closure = Path(binding['closure_path'])
    assert hashlib.sha256(receipt.read_bytes()).hexdigest() == binding['receipt_sha256']
    assert hashlib.sha256(closure.read_bytes()).hexdigest() == binding['closure_sha256']
    assert json.loads(receipt.read_bytes())['workflow_complete'] is True
    assert json.loads(closure.read_bytes())['all_archive_index_blobs_exact'] is True
    packets = [
        ('p2-offline-input-refresh-candidate094-v1/public-manifest094.json', '31d2ea82865edcaf21bac24f81174b991a8bd92dd208223ac47f8dfee275659c', 'candidate-source-reviewed', ['handoff094.json']),
        ('ui-094-offline-input-refresh-draft/public-artifacts-manifest-pending094.json', '93706bdcdaae60823ebe59bcd933ac44ef49cc269468fe4ae689cb6bd13c8789', 'original-window-draft-source-blocked', ['handoff-pending094.json']),
        ('ui-094-offline-input-refresh-draft-v2/public-artifacts-manifest-pending094.json', '99552d99f179be50e72d3f943b40f6c10bad00b981e34512c798fc7f02f2449f', 'corrected-window-draft-v2-source-only', ['handoff-pending094.json']),
    ]
    rows = []
    for name, digest, prefix, extra in packets:
        rows += sealed(LOCAL / name, digest, prefix, 'local_artifact_dict', extra)
    rows += sealed(LOCAL / 'ui-094-saved-validator-draft/public-artifacts-manifest-saved-validator094.json',
        '4c3eb1b892c6e3ab760bf5a8709e423063e3c46a4e71c2171d9d2308dbd54cc4', '',
        'source_archive_rows', ['handoff-saved-validator094.json'])
    for name in ('root-integrate094.py', 'root-integration-plan094.json', 'root-integration-applied094.json',
                 'root-source-094.json', 'root-related094.py'):
        rows.append(row(LOCAL / name, 'root/' + name))
    rows.append(row(receipt, 'actual-base093/verification-sections093.json'))
    rows.append(row(closure, 'actual-base093/archived-working-tree-closure093.json'))
    rows.append(row(Path(__file__), 'root/' + Path(__file__).name))
    copy_rows(rows)
    save_new(LOCAL / 'root-archive-prepared094.json', {'format_version': 1,
        'status': 'ROOT_APPLIED094_FROZEN_SOURCE_HISTORY_COPIED_RUNTIME_PENDING', 'files': rows,
        'file_count': len(rows), 'total_bytes': sum(item['bytes'] for item in rows),
        'actual93_completed_binding': binding, 'project_calls': 0, 'section094_completed': False})
    print(json.dumps({'prepared_files': len(rows), 'section094_completed': False, 'project_calls': 0}))
elif phase == 'append':
    assert DEST.is_dir()
    spec = json.loads(Path(sys.argv[2]).read_bytes())
    copy_rows(spec['files'])
    print(json.dumps({'appended_files': len(spec['files']), 'project_calls': 0}))
else:
    raise ValueError(phase)
