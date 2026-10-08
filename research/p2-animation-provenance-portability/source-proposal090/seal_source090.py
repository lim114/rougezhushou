"""Seal this immutable source-only proposal, not a numbered product section."""
from pathlib import Path, PurePosixPath
import hashlib
import json

ROOT = Path(__file__).resolve().parent


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def write(name, value):
    raw = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()
    with (ROOT / name).open('xb') as stream:
        stream.write(raw)
    return {'source_path': str(ROOT / name), 'archive_path': name,
            'bytes': len(raw), 'sha256': sha(raw)}


proposal = {
    'format_version': 1, 'status': 'SOURCE_ONLY_PROPOSAL_PRODUCT_AUTHORIZATION_PENDING',
    'baseline_commit': '1ce970fd30aa3b42d8ef787cde02513f05682b66',
    'positive_gap': 'Committed evidence replay relies on external absolute paths and unmigrated historical cache; two manifested official build leaves are ignored and absent from Git.',
    'minimum_product_scope': {
        'new_stdlib_read_only_CLI': 'scripts/verify_original_animation_provenance.py',
        'new_stdlib_regression_module_proposed': 'tests/test_original_animation_provenance.py',
        'registry': 'One module registration only',
        'public_source_exact_force_add': [
            'research/p2-gummy-back-animation-reference/source-packet087/official-reader/official-source/spine-ts/build/spine-core.js',
            'research/p2-gummy-back-animation-reference/source-packet087/official-reader/official-source/spine-ts/build/spine-core.d.ts'],
        'documentation': 'A short maintenance command and exact scope',
        'existing_gameplay_data_or_production_code_changes': False,
        'historical_generators_or_manifests_changes': False},
    'proposal_file': 'PROPOSAL.md',
    'required_public_source_leaves': 6,
    'tests_planned_not_run': 6,
    'project_API_helper_formatter_tests_parser_download_Qt_Wine_calls': 0,
    'tracked_edits': 0, 'product_drafts': 0,
    'unknowns_preserved': ['Native gameplay clock/binding', 'Geometry/rendering',
                          'EOF consumption', 'Historical parser/root cause']}
write('proposal090.json', proposal)
files = []
seen = set()
for path in sorted(ROOT.rglob('*')):
    if not path.is_file():
        continue
    archive_path = path.relative_to(ROOT).as_posix()
    if archive_path in ('public-artifacts-manifest-source090.json', 'final-handoff-source090.json'):
        continue
    pure = PurePosixPath(archive_path)
    assert not pure.is_absolute() and str(pure) == archive_path
    assert '\\' not in archive_path and all(part not in ('.', '..') and ':' not in part for part in pure.parts)
    assert archive_path not in seen
    seen.add(archive_path)
    raw = path.read_bytes()
    files.append({'source_path': str(path), 'archive_path': archive_path,
                  'bytes': len(raw), 'sha256': sha(raw)})
manifest = write('public-artifacts-manifest-source090.json', {
    'format_version': 1, 'status': 'FINAL_STABLE_SOURCE_ONLY_POSITIVE_PROPOSAL',
    'numbered_section': False, 'files': files,
    'bytes': sum(item['bytes'] for item in files),
    'source_snapshot_files': 21, 'actual_git_snapshot_files': 19,
    'existing_working_source_not_committed_files': 2,
    'required_source_leaves_hashed': 6,
    'application_API_project_helper_formatter_tests_parser_download_Qt_Wine_calls': 0,
    'tracked_edits': 0, 'product_drafts': 0,
    'new_source_parses_or_historical_cache_reconstruction': False})
handoff = write('final-handoff-source090.json', {
    'format_version': 1, 'status': 'FINAL_STABLE_SOURCE_ONLY',
    'directory': str(ROOT), 'manifest': manifest,
    'file_count': len(files), 'bytes': sum(item['bytes'] for item in files),
    'proposal': proposal,
    'freeze_failures_preserved': 1,
    'root_owns_tracked_apply_commit_and_numbered_section_count': True,
    'package_will_not_be_modified_after_this_seal': True})
print(json.dumps({'manifest': manifest, 'handoff': handoff,
                  'file_count': len(files), 'bytes': sum(item['bytes'] for item in files)}))
