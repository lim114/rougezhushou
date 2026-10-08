"""Seal author evidence only; all project runtime calls stay completed/preserved."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
SOURCE = Path('/workspace/.continuation/p2-crew-count-boolean-089-source')
LEAD = Path('/workspace/.continuation/p2-section089-crew-count-source-lead')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def bound(path, archive):
    data = path.read_bytes()
    return {'source_path': str(path), 'archive_path': archive,
            'bytes': len(data), 'sha256': sha(data)}


def json_new(path, value):
    with path.open('x', encoding='utf-8') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write('\n')


files = []
packets = []
for directory, name, expected, prefix, expected_count in (
    (SOURCE, 'public-manifest.json',
     'adf1b2a619cadea7c747669e9bb2f9c710c5d12ce83de48a63afcc992b3b7aca', 'source089', 38),
    (LEAD, 'v1-public-files-manifest089.json',
     '2df0d0ee9f59fb20e225b88d3562d0ca944896ae3a22f39216f3499ee2112030', 'static-lead089', 11),
):
    manifest_path = directory / name
    assert sha(manifest_path.read_bytes()) == expected
    manifest = json.loads(manifest_path.read_bytes())
    assert manifest['version'] == 1 and manifest['file_count'] == expected_count
    total = 0
    for original in manifest['files']:
        path = Path(original['source_path'])
        if not path.is_absolute() or not path.exists():
            archive = Path(original['archive_path'])
            path = archive if archive.is_absolute() else directory / archive
        data = path.read_bytes()
        assert len(data) == original['bytes'] and sha(data) == original['sha256']
        total += len(data)
        files.append(bound(path, prefix + '/' + path.relative_to(directory).as_posix()))
    assert total == manifest['total_bytes']
    files.append(bound(manifest_path, prefix + '/' + name))
    packets.append({'stage': prefix, 'manifest': bound(manifest_path, prefix + '/' + name),
                    'original_file_count': expected_count, 'original_total_bytes': total,
                    'project_calls_this_seal': 0})

freeze_path = OUT / 'draft-freeze089.json'
freeze = json.loads(freeze_path.read_bytes())
assert sha(freeze_path.read_bytes()) == '04c9567954f2b7bcd34c2abe1b2b616988400d4193943e94ec4e46e32a8cc248'
for entry in freeze['files'] + [freeze['section_patch'], freeze['registry_proposal']]:
    data = Path(entry['source_path']).read_bytes()
    assert len(data) == entry['bytes'] and sha(data) == entry['sha256']
old = (OUT / 'baseline/rouge/run_state.py').read_bytes()
new = (OUT / 'draft/rouge/run_state.py').read_bytes()
assert sha(old) == freeze['source_run_state_old_sha256']
line = b'        if isinstance(crew,bool):crew=None\r\n'
assert new.count(line) == 1 and new.replace(line, b'', 1) == old
assert b'\n' not in new.replace(b'\r\n', b'')
assert b'\r\n' not in (OUT / 'draft/tests/test_run_crew_count_boolean_input.py').read_bytes()
summary = json.loads((OUT / 'new-test-summary089.json').read_bytes())
saved = json.loads((OUT / 'saved-only-check089.json').read_bytes())
assert summary['status'] == 'PASS' and saved['status'] == 'PASS_SAVED_ONLY'
assert summary['tests_run'] == 7 and summary['errors'] == summary['failures'] == summary['skips'] == 0
assert summary['actual_explicit_entry_roles'] == freeze['approved_author_budget'] | {} or summary['budget_exact']
own_paths = [p for p in OUT.rglob('*') if p.is_file() and 'runtime' not in p.relative_to(OUT).parts]
for path in sorted(own_paths):
    files.append(bound(path, 'author089/' + path.relative_to(OUT).as_posix()))
handoff_path = OUT / 'author-review-handoff089.json'
handoff = {
    'status': 'AUTHOR_FROZEN_PASS_READY_FOR_FORMAL_REVIEW',
    'source_base_commit': freeze['source_base_commit'], 'transport_root_commit': freeze['transport_root_commit'],
    'freeze': bound(freeze_path, 'author089/draft-freeze089.json'),
    'product_and_new_test': freeze['files'], 'section_patch': freeze['section_patch'],
    'registry_proposal': freeze['registry_proposal'], 'original_source_packets': packets,
    'author_validation': {'attempts': 1, 'new_test_methods_run': 7, 'pass': 7, 'skip': 0,
                          'new_scenario_groups': 12, 'constructors_new': 12, 'constructors_reload': 2,
                          'seed_apply': 12, 'subject_apply': 12, 'actual_constructor_entries': 14,
                          'actual_apply_entries': 24, 'early_ignored_subject_entries': 2,
                          'complete_saved_records': 38, 'internal_RunState_entries': summary['actual_RunState_file_entries'],
                          'other_internal_helpers': 'not instrumented; no whole-project total inferred'},
    'saved_gzip_proof': {k: summary[k] for k in ('saved_gzip_bytes', 'saved_gzip_sha256', 'decoded_bytes', 'decoded_sha256')},
    'source5_repeated': False, 'saved_only_check_new_calls': 0,
    'real_local_damage_training_app_recognition_formatter_Qt_Wine_calls': 0,
    'tracked_edits': 0,
    'formal_reviewer': '/root/source_080_resume/review_trait_binding',
    'formal_authorized_budget': 'Root specified <=6 different-risk fresh groups with constructors/apply split, plus new7 tests once; do not repeat author12/source5.',
    'pending': ['independent formal final', 'root current transport/registry static check',
                'root sole apply', 'root fresh related and selected validation', 'root commit/archive89'],
    'public_manifest': str(OUT / 'author-review-manifest089.json'),
    'limits': ['state-only proof; no measured damage/training delta',
               'no old-state migration or native P1 departure/buff inference',
               'int/None producer; nonbool float/string tests are compatibility only',
               'natural UUID/time retained; reload key scope, no full cross-case equality'],
}
json_new(handoff_path, handoff)
files.append(bound(handoff_path, 'author089/' + handoff_path.name))
assert len({f['source_path'] for f in files}) == len(files)
assert len({f['archive_path'] for f in files}) == len(files)
manifest = {'version': 1, 'status': 'AUTHOR_FROZEN_READY_FORMAL', 'files': files,
            'file_count': len(files), 'total_bytes': sum(f['bytes'] for f in files),
            'immutable_original_source_counts': {'source089': 38, 'static_lead089': 11}}
manifest_path = OUT / 'author-review-manifest089.json'
json_new(manifest_path, manifest)
for entry in files:
    data = Path(entry['source_path']).read_bytes()
    assert len(data) == entry['bytes'] and sha(data) == entry['sha256']
print(json.dumps({'status': manifest['status'], 'files': len(files), 'bytes': manifest['total_bytes'],
                  'manifest': bound(manifest_path, manifest_path.name), 'handoff': bound(handoff_path, handoff_path.name),
                  'new_project_calls': 0}))
