"""One-time preparation snapshot manifest; no RunState or production imports."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / 'source-preparation-manifest089.json'
HANDOFF = ROOT / 'source-preparation-handoff089.json'
assert not MANIFEST.exists() and not HANDOFF.exists()

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

receipt_path = ROOT / 'source-preparation-review089.json'
receipt = json.loads(receipt_path.read_text())
assert receipt['status'] == 'PASS_SOURCE_PACKAGE_AND_5_SAVED_NATIVE_CASES_FORMAL_DRAFT_PENDING'
assert receipt['all38_source_manifest_files_byte_hash_verified_and_preserved'] is True
assert receipt['real_local_files_accessed'] is False
timestamp = datetime.now(timezone.utc).isoformat()
dump(HANDOFF, {'version': 1, 'status': 'SEALED_SOURCE_ONLY_PREPARATION_FORMAL_PRODUCT_PENDING',
    'sealed_at_utc': timestamp, 'archive_root': str(ROOT),
    'source_manifest_sha256': receipt['source_manifest_sha256'],
    'source_handoff_sha256': receipt['source_handoff_sha256'],
    'source_base_commit': receipt['source_base_commit'],
    'current_HEAD_at_snapshot': receipt['actual_current_HEAD_at_public_source_snapshot'],
    'receipt': {'source_path': str(receipt_path), 'archive_path': receipt_path.name,
        'bytes': receipt_path.stat().st_size, 'sha256': sha(receipt_path)},
    'source38_files_preserved_and_verified': True, 'saved5_native_states_inputs_disk_history_verified': True,
    'same_case_UUID_started_at_and_actual_capture_time_preserved': True,
    'cross_case_time_or_identity_normalization': False,
    'reviewer_new_RunState_or_production_helper_API_formatter_test_network_Qt_Wine_calls': 0,
    'real_local_access_or_tracked_changes': 0,
    'damage_numeric_or_P1_strengthening_game_mechanism_validation': False,
    'formal_draft_or_new_tests_reviewed': False,
    'next': 'Await author completed final handoff and root temporary-state/new-test budget; add new formal-review files only.',
    'listed_preparation_files_immutable': True, 'manifest_path': str(MANIFEST)})
files = []
for path in sorted(ROOT.rglob('*')):
    if not path.is_file() or path == MANIFEST:
        continue
    files.append({'source_path': str(path), 'archive_path': str(path.relative_to(ROOT)),
        'bytes': path.stat().st_size, 'sha256': sha(path)})
dump(MANIFEST, {'version': 1, 'status': 'PREPARATION_SEALED_FORMAL_PRODUCT_PENDING',
    'sealed_at_utc': timestamp, 'archive_root': str(ROOT), 'file_count': len(files),
    'total_bytes': sum(row['bytes'] for row in files), 'manifest_self_excluded': True,
    'handoff_included': True, 'files': files})
for row in files:
    path = Path(row['source_path'])
    assert path.stat().st_size == row['bytes'] and sha(path) == row['sha256']
print(json.dumps({'status': 'SEALED_SOURCE_ONLY_PREPARATION', 'file_count': len(files),
    'total_bytes': sum(row['bytes'] for row in files), 'manifest_sha256': sha(MANIFEST),
    'handoff_sha256': sha(HANDOFF), 'reviewer_RunState_calls': 0}))
