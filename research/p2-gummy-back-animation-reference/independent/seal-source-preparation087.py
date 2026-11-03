"""Seal only the current source preparation; later formal work must add new files."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / 'source-preparation-manifest087.json'
HANDOFF = ROOT / 'source-preparation-handoff087.json'
assert not MANIFEST.exists() and not HANDOFF.exists()

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

child = ROOT / 'choices-child'
expected = {
    'handoff-choices-final087.json': '9a38faed3e3999ff716c0af87dd755d55e64a584d955767fed361199363fcdb4',
    'choices-boundary-receipt-final087.json': 'e59e896827015f0eb8639bd66b48896a6cf3215ea7efdb37dc885f60de0da6ef',
    'public-artifacts-manifest-choices087.json': '10d2d2c10aa74b1dfb722bbfff725daabca4c05b62b5586194d48604aaf39850'}
for name, value in expected.items():
    assert sha(child / name) == value
child_manifest = json.loads((child / 'public-artifacts-manifest-choices087.json').read_text())
assert len(child_manifest['files']) == 4
for row in child_manifest['files']:
    path = child / row['archive_path']
    assert path.stat().st_size == row['bytes'] and sha(path) == row['sha256']
prepared = json.loads((ROOT / 'source-preparation-receipt087.json').read_text())
assert prepared['final_source_freeze_received'] is False
assert prepared['status'] == 'PREPARATION_SOURCE_CONTRACT_PASS_FINAL_DRAFT_PENDING'
timestamp = datetime.now(timezone.utc).isoformat()
dump(HANDOFF, {'version': 1, 'status': 'SOURCE_PREPARATION_SEALED_FORMAL_PRODUCT_PENDING',
    'prepared_at_utc': timestamp, 'baseline_commit': prepared['baseline_commit'],
    'source_preparation_receipt': {'source_path': str(ROOT / 'source-preparation-receipt087.json'),
        'sha256': sha(ROOT / 'source-preparation-receipt087.json')},
    'original923_record_byte_type_value_index': {'source_path': str(ROOT / 'baseline923-record-byte-index087.json'),
        'sha256': sha(ROOT / 'baseline923-record-byte-index087.json')},
    'child_choices_status': 'FINAL_SOURCE_TEXT_ONLY', 'child_fixed_receipts_sha256': expected,
    'source_preparation_manifest_path': str(MANIFEST),
    'source_origin_full102_operation_repeated': False,
    'expected_counts': prepared['expected_post_append_counts'],
    'final_product_draft_reviewed': False, 'public_fresh_or_saved_product_results_reviewed': False,
    'reviewer_new_application_API_formatter_tests_source_runtime_parser_network_Qt_Wine_calls': 0,
    'production_helper_calls': 0, 'tracked_changes': 0,
    'preservation_rule': 'All listed preparation files are immutable. Add later formal receipts/scripts/results in a new formal-review subdirectory; do not overwrite preparation evidence.',
    'next': 'Wait for parent final freeze and coordinated bounded fresh/test budget; first review exact source delta and saved outputs.'})
origins = {row['archive_path']: row['source_path'] for row in prepared['input_bindings']}
files = []
for path in sorted(ROOT.rglob('*')):
    if not path.is_file() or path == MANIFEST:
        continue
    relative = str(path.relative_to(ROOT))
    files.append({'source_path': origins.get(relative, str(path)), 'archive_path': relative,
        'bytes': path.stat().st_size, 'sha256': sha(path)})
dump(MANIFEST, {'version': 1, 'status': 'PREPARATION_SNAPSHOT_SEALED_NOT_FORMAL_PRODUCT',
    'sealed_at_utc': timestamp, 'file_count': len(files), 'total_bytes': sum(row['bytes'] for row in files),
    'manifest_self_excluded': True, 'handoff_included': True, 'files': files})
for row in files:
    path = ROOT / row['archive_path']
    assert path.stat().st_size == row['bytes'] and sha(path) == row['sha256']
print(json.dumps({'status': 'SOURCE_PREPARATION_SEALED_FORMAL_PENDING',
    'file_count': len(files), 'total_bytes': sum(row['bytes'] for row in files),
    'manifest_sha256': sha(MANIFEST), 'handoff_sha256': sha(HANDOFF)}))
