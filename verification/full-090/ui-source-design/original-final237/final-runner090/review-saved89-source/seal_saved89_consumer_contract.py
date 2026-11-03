"""Seal only this narrow static contract; imports no project code."""
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def bound(path):
    raw = path.read_bytes()
    return {'source_path': str(path), 'archive_path': path.name, 'bytes': len(raw), 'sha256': sha(raw)}


def write(path, value):
    with path.open('x', encoding='utf-8') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write('\n')


design_path = Path('/workspace/.continuation/root-transport-preparation090/saved89-five-state-UI-consumer-design090.json')
design = json.loads(design_path.read_bytes())
presence = [{'saved_sequence': row['saved_sequence'],
             'raw_member_key_exists': {owner: owner in row['state']['operators']
                                       for owner in ('mechanist', 'char_151_myrtle')},
             'raw_member_present_only_when_key_exists': {owner: row['state']['operators'][owner]['present']
                                                        for owner in ('mechanist', 'char_151_myrtle')
                                                        if owner in row['state']['operators']}}
            for row in design['selected_saved_records']]
write(OUT / 'raw-member-key-presence089.json', {'status': 'STATIC_SAVED_PROJECTION_KEY_PRESENCE_ONLY',
                                              'rows': presence, 'missing_owner_None_sentinel_is_not_raw_present_field': True,
                                              'new_project_calls': 0})
contract = json.loads((OUT / 'expected-ten-state-contract089.json').read_bytes())
assert contract['row_count'] == 10 and len(contract['rows']) == 10
assert contract['new_ctor_apply_API_helper_formatter_tests_Qt_Wine_calls'] == 0
sources = json.loads((OUT / 'source-hashes089-consumer.json').read_bytes())
for row in sources['files']:
    raw = Path(row['source_path']).read_bytes()
    assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
handoff_path = OUT / 'handoff-static-consumer089.json'
write(handoff_path, {'status': 'FINAL_STATIC_SOURCE_CONTRACT_ONLY_FOR_UI_PENDING_REAL_WINDOW',
                    'named_actual90_source_commit': contract['named_actual90_source_commit'],
                    'selected_author_newtest_saved_sequences': [19, 9, 3, 22, 6],
                    'switch_states': 10,
                    'contract': bound(OUT / 'expected-ten-state-contract089.json'),
                    'source_hashes': bound(OUT / 'source-hashes089-consumer.json'),
                    'snapshot_state_injection_not_ctor_apply_or_native_observation': True,
                    'new_RunState_ctor_apply_helper_API_formatter_tests_Qt_Wine_calls': 0,
                    'old_source5_saved38_materials_modified_or_reexecuted': False,
                    'pending_runner_review_performed': False,
                    'sole_formal_reviewer': '/root/source_080_resume',
                    'actual_future_MainWindow_API_ctor_entries': 'Must be independently recorded; not predicted by this static0call review.',
                    'public_manifest': str(OUT / 'manifest-static-consumer089.json')})
files = [bound(p) for p in sorted(OUT.iterdir()) if p.is_file()]
manifest = {'version': 1, 'status': 'FINAL_STATIC_SOURCE_CONTRACT_ONLY_FOR_UI_PENDING_REAL_WINDOW',
            'files': files, 'file_count': len(files), 'total_bytes': sum(r['bytes'] for r in files),
            'source89_and_91_prior_seals_unchanged': True, 'new_project_calls': 0}
manifest_path = OUT / 'manifest-static-consumer089.json'
write(manifest_path, manifest)
for row in files:
    raw = Path(row['source_path']).read_bytes()
    assert len(raw) == row['bytes'] and sha(raw) == row['sha256']
print(json.dumps({'status': manifest['status'], 'files': len(files), 'bytes': manifest['total_bytes'],
                  'manifest': bound(manifest_path), 'handoff': bound(handoff_path), 'new_project_calls': 0}))
