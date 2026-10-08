"""Keep original child schema immutable and bind actual artifacts explicitly."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent / 'sp-source-preparation'
manifest = ROOT / 'v1-public-files-manifest088.json'
handoff = ROOT / 'sp-source-preparation-handoff088.json'
assert hashlib.sha256(manifest.read_bytes()).hexdigest() == 'b150988c2b4c5298d3d5109bbb4340a1fb2a9cb2adffba661ad11c67a8d38a21'
assert hashlib.sha256(handoff.read_bytes()).hexdigest() == 'bff95a9642d547a91a9709447c513b23f93ffe3afe03952bf3d29770bd5203ea'
original = json.loads(manifest.read_bytes())
assert original['version'] == 1 and len(original['files']) == 13
actual_rows = []
for row in original['files']:
    path = Path(row['archive_path'])
    assert path.is_absolute() and path.is_relative_to(ROOT)
    data = path.read_bytes()
    assert len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256']
    actual_rows.append({'source_path': str(path), 'archive_path': str(path.relative_to(ROOT)),
                        'bytes': len(data), 'sha256': row['sha256'],
                        'original_source_provenance_field': row['source_path']})
assert sum(row['bytes'] for row in actual_rows) == 74215
result = {'format_version': 1, 'status': 'PASS_CHILD_SOURCE_PREPARATION_IMPORT_0CALLS',
          'archive_root': str(ROOT), 'files': actual_rows, 'file_count': 13, 'total_bytes': 74215,
          'original_child_manifest': {'source_path': str(manifest), 'bytes': manifest.stat().st_size,
                                      'sha256': hashlib.sha256(manifest.read_bytes()).hexdigest()},
          'original_child_handoff': {'source_path': str(handoff), 'bytes': handoff.stat().st_size,
                                     'sha256': hashlib.sha256(handoff.read_bytes()).hexdigest()},
          'schema_mapping': 'Original source_path is provenance; original absolute archive_path locates actual saved artifact. Sidecar binds actual artifacts without changing original manifest.',
          'new_project_calls': 0, 'child_files_modified': False,
          'initial_schema_import_failure_preserved': True}
(OUT / 'child-source-preparation-import088.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': result['status'], 'files': 13, 'bytes': 74215, 'new_project_calls': 0}))
