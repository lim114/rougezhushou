"""Seal this bounded negative audit; execute no project code."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
findings = json.loads((OUT / 'findings.json').read_text())
assert findings['status'] == 'bounded_negative_source_audit_not_numbered'
assert findings['actionable_candidates'] == []
assert all(value == 0 for value in findings['counters'].values())
receipt = json.loads((OUT / 'fixed-source-receipt.json').read_text())
assert len(receipt['files']) == 29
for name, expected in receipt['files'].items():
    data = (OUT / expected['archive_path']).read_bytes()
    assert len(data) == expected['bytes'] and hashlib.sha256(data).hexdigest() == expected['sha256']
handoff = {'status': 'final_stable_bounded_negative_source_audit',
    'fixed_commit': findings['fixed_commit'], 'numbered_section': False,
    'actionable_candidates': [], 'source_and_history_files': 29,
    'source_AST_call_sites': 133, 'full_guard_entry_functions': 18,
    'counters': findings['counters'], 'fresh_runtime_validation': False,
    'result': 'No source-supported missing finite check was found in the traced actual public float consumers.',
    'evidence': ['findings.json', 'fixed-source-receipt.json',
        'guard-function-excerpts.json', 'numeric-call-ast-inventory.json',
        'historical-saved-receipts-read.json', 'NOTE.md'],
    'limits': findings['limits'], 'restart': findings['restart'],
    'stop': 'Complete; release the agent slot. Root may archive this as an appendix without advancing a section.'}
(OUT / 'handoff.json').write_text(json.dumps(handoff, ensure_ascii=False, indent=2) + '\n')
rows = []
for path in sorted(OUT.rglob('*')):
    if not path.is_file() or path.name == 'public-artifacts-manifest.json':
        continue
    data = path.read_bytes()
    rows.append({'source_path': str(path), 'archive_path': path.relative_to(OUT).as_posix(),
                 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
manifest = {'format_version': 1, 'status': 'final_stable', 'numbered_section': False,
    'files': rows, 'bytes': sum(row['bytes'] for row in rows),
    'API_calls': 0, 'project_helper_calls': 0, 'tests': 0, 'Qt': 0, 'Wine': 0,
    'tracked_edits': 0}
(OUT / 'public-artifacts-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
for row in rows:
    data = Path(row['source_path']).read_bytes()
    assert len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256']
print(json.dumps({'passed': True, 'files': len(rows), 'bytes': manifest['bytes'],
    'handoff_sha256': hashlib.sha256((OUT / 'handoff.json').read_bytes()).hexdigest(),
    'manifest_sha256': hashlib.sha256((OUT / 'public-artifacts-manifest.json').read_bytes()).hexdigest(),
    'API_calls': 0, 'project_helper_calls': 0, 'tests': 0, 'Qt': 0, 'Wine': 0}))
