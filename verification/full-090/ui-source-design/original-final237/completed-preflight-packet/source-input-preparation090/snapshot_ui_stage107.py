"""Preserve the original107-byte manifest before any subsequent UI preparation."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLD = Path('/workspace/.continuation/ui-090-draft')
OUT = HERE / 'immutable-preparation-stage107'
def sha(raw):
    return hashlib.sha256(raw).hexdigest()
def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
manifest_path = OLD / 'public-artifacts-manifest-stage-increment086.json'
handoff_path = OLD / 'handoff-stage-increment086.json'
assert sha(manifest_path.read_bytes()) == 'c0c4917b237731af75c4dafeba52f427d6c7b0dbf30f9ef44d73df4882ae2e7a'
assert sha(handoff_path.read_bytes()) == '39df5744e404b45e08e765c5962e2269a2d87a44b140a49c1802e35ff3c1ec08'
manifest = json.loads(manifest_path.read_bytes())
assert manifest['format_version'] == 1 and manifest['file_count'] == len(manifest['files']) == 107
assert manifest['total_bytes'] == 3068082
assert not OUT.exists(), 'Do not overwrite an immutable preparation snapshot'
for row in manifest['files']:
    raw = Path(row['source_path']).read_bytes()
    assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
OUT.mkdir()
transport = []
for row in manifest['files']:
    raw = Path(row['source_path']).read_bytes()
    target = OUT / row['archive_path']
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
    transport.append({'original_source_path': row['source_path'],
        'original_archive_path': row['archive_path'], 'source_path': str(target),
        'archive_path': target.relative_to(OUT).as_posix(), 'bytes': len(raw), 'sha256': sha(raw)})
for original, name in ((manifest_path, 'original-stage107-manifest.json'), (handoff_path, 'original-stage107-handoff.json')):
    target = OUT / name
    target.write_bytes(original.read_bytes())
    transport.append({'original_source_path': str(original), 'original_archive_path': name,
        'source_path': str(target), 'archive_path': name,
        'bytes': len(target.read_bytes()), 'sha256': sha(target.read_bytes()),
        'extra_original_document_copy': True})
save(OUT / 'transport-source-archive-map107.json', {
    'status': 'PASS_ORIGINAL107_ALL_ROWS_VERIFIED_BEFORE_SUBSEQUENT_PREPARATION',
    'original_stage_artifact_count': 107, 'original_stage_artifact_bytes': 3068082,
    'extra_manifest_and_handoff_copies': 2,
    'original_manifest_sha256': sha(manifest_path.read_bytes()),
    'original_handoff_sha256': sha(handoff_path.read_bytes()),
    'files': transport, 'original35_and_snapshot38_nested_bytes_preserved': True,
    'original107_files_and_manifest_handoff_unmodified': True,
    'project_API_helpers_formatter_tests_Qt_Wine_calls': 0})
rows = []
for path in sorted(OUT.rglob('*')):
    if path.is_file():
        raw = path.read_bytes()
        rows.append({'source_path': str(path), 'archive_path': path.relative_to(OUT).as_posix(),
            'bytes': len(raw), 'sha256': sha(raw)})
assert len(rows) == 110
snapshot_manifest = OUT / 'immutable-snapshot-stage107-manifest.json'
save(snapshot_manifest, {'format_version': 1, 'status': 'IMMUTABLE_ORIGINAL_STAGE107_PREPARATION',
    'file_count': 110, 'original_artifact_count': 107, 'files': rows,
    'total_bytes': sum(row['bytes'] for row in rows), 'manifest_self_excluded': True,
    'on_disk_files_including_this_manifest': 111})
for row in rows:
    raw = Path(row['source_path']).read_bytes()
    assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
print(json.dumps({'status': 'IMMUTABLE_STAGE107_COMPLETE', 'original_files': 107,
    'snapshot_manifest_rows': 110, 'snapshot_disk_files_including_manifest': 111,
    'snapshot_manifest_path': str(snapshot_manifest), 'snapshot_manifest_sha256': sha(snapshot_manifest.read_bytes()),
    'original107_35_nested38_unchanged': True}, ensure_ascii=False))
