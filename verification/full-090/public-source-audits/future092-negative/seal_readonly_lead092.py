"""Seal a negative source lead without counting a completed section."""
from pathlib import Path, PurePosixPath
import hashlib
import json

HERE = Path(__file__).resolve().parent
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def write(name, value):
    raw = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()
    with (HERE / name).open('xb') as stream:
        stream.write(raw)
    return {'source_path': str(HERE / name), 'archive_path': name,
            'bytes': len(raw), 'sha256': sha(raw)}


files = []
seen = set()
for path in sorted(HERE.rglob('*')):
    if not path.is_file():
        continue
    name = path.relative_to(HERE).as_posix()
    if name in {'public-artifacts-manifest-source092.json', 'final-handoff-source092.json'}:
        continue
    pure = PurePosixPath(name)
    assert not pure.is_absolute() and str(pure) == name
    assert '\\' not in name and all(part not in ('.', '..') and ':' not in part for part in pure.parts)
    assert name not in seen
    seen.add(name)
    raw = path.read_bytes()
    files.append({'source_path': str(path), 'archive_path': name, 'bytes': len(raw), 'sha256': sha(raw)})
lead = json.loads((HERE / 'source-lead092.json').read_bytes())
assert lead['no_new_positive_source_contract_gap_established'] is True
assert lead['application_API_project_helper_formatter_tests_Qt_Wine_calls'] == 0
manifest = write('public-artifacts-manifest-source092.json', {
    'format_version': 1, 'status': 'FINAL_STABLE_NEGATIVE_SOURCE_LEAD_NATIVE_USE_UNKNOWN',
    'numbered_section': False, 'files': files, 'bytes': sum(f['bytes'] for f in files),
    'source_baseline_commit': lead['actual_source_baseline_commit'],
    'historical_controls_reused_not_rerun': 16, 'new_API_helper_formatter_tests_Qt_Wine_calls': 0,
    'new_raw_source_hashes_or_downloads': 0, 'product_drafts_or_tracked_edits': 0,
    'completed_section_count_increment': 0})
handoff = write('final-handoff-source092.json', {
    'format_version': 1, 'status': 'FINAL_STABLE_SOURCE_ONLY_NEGATIVE_UNKNOWN',
    'directory': str(HERE), 'manifest': manifest, 'files': len(files),
    'bytes': sum(f['bytes'] for f in files), 'positive_product_candidate': False,
    'native_common_skill_use_and_account_to_run_inheritance_unresolved': True,
    'restart_condition': lead['restart_condition'], 'completed_section_increment': 0,
    'immutable90_original28_and_author62_not_modified': True})
print(json.dumps({'manifest': manifest, 'handoff': handoff,
                  'files': len(files), 'bytes': sum(f['bytes'] for f in files)}))
