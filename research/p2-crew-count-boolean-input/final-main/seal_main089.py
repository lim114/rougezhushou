"""Once-only final import/seal; hashes/decompresses evidence, no project imports."""
import gzip
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
AUTHOR = Path('/workspace/.continuation/p2-crew-count-boolean-089-draft')
IND = Path('/workspace/.continuation/p2-crew-count-boolean-089-independent')
TRANSPORT = Path('/workspace/.continuation/p2-crew-count-boolean-089-root-transport')


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
packet_records = []
for path, expected_sha, expected_count, prefix in (
    (AUTHOR / 'author-review-manifest089.json',
     'bd067b62de388092018288d2d240ac22f3701d5e081a5b0f5210e6edf33adbc5', 71, 'author-packet'),
    (IND / 'formal-review/final-public-artifacts-manifest089.json',
     'b6b69cd595be5f98d60ae0973635b45cdcd5d20277f65a355e26423b15dd64a2', 177, 'independent-packet'),
):
    assert sha(path.read_bytes()) == expected_sha
    manifest = json.loads(path.read_bytes())
    assert manifest['version'] == 1 and manifest['file_count'] == expected_count
    total = 0
    for row in manifest['files']:
        original = Path(row['source_path'])
        data = original.read_bytes()
        assert len(data) == row['bytes'] and sha(data) == row['sha256']
        total += len(data)
        files.append(bound(original, prefix + '/' + row['archive_path']))
    assert total == manifest['total_bytes']
    files.append(bound(path, prefix + '/' + path.name))
    packet_records.append({'original_manifest': bound(path, prefix + '/' + path.name),
                           'original_file_count': expected_count, 'original_total_bytes': total})
freeze_path = AUTHOR / 'draft-freeze089.json'
assert sha(freeze_path.read_bytes()) == '04c9567954f2b7bcd34c2abe1b2b616988400d4193943e94ec4e46e32a8cc248'
freeze = json.loads(freeze_path.read_bytes())
for row in freeze['files'] + [freeze['section_patch'], freeze['registry_proposal']]:
    data = Path(row['source_path']).read_bytes()
    assert len(data) == row['bytes'] and sha(data) == row['sha256']
old = (AUTHOR / 'baseline/rouge/run_state.py').read_bytes()
new = Path(freeze['files'][0]['source_path']).read_bytes()
assert sha(old) == freeze['source_run_state_old_sha256']
line = b'        if isinstance(crew,bool):crew=None\r\n'
assert new.count(line) == 1 and new.replace(line, b'', 1) == old
assert b'\n' not in new.replace(b'\r\n', b'')
test = Path(freeze['files'][1]['source_path']).read_bytes()
assert b'\r\n' not in test
registry = json.loads((AUTHOR / 'registry-proposal.json').read_bytes())
assert registry['module'] == 'tests.test_run_crew_count_boolean_input'
author_summary = json.loads((AUTHOR / 'new-test-summary089.json').read_bytes())
ind_receipt_path = IND / 'formal-review/independent-formal-review089.json'
assert sha(ind_receipt_path.read_bytes()) == 'b7bdd31f8decd64ad9bcdbc5fca245e3d0111bf50dc423b191ca6229522f42b9'
ind_receipt = json.loads(ind_receipt_path.read_bytes())
ind_handoff_path = IND / 'formal-review/final-handoff089.json'
assert sha(ind_handoff_path.read_bytes()) == 'f1a745479265ed696b264b3ac757ae9faaba7ca1a3aa8509dc0287d9df2726b7'
assert author_summary['tests_run'] == 7 and author_summary['errors'] == author_summary['failures'] == author_summary['skips'] == 0
assert ind_receipt['actual_constructor_entries'] == 20 and ind_receipt['actual_apply_entries'] == 30
assert ind_receipt['frozen_newtests_once']['pass'] == 7 and ind_receipt['frozen_newtests_once']['skip'] == 0
assert ind_receipt['same_real_seed_whole_comparison'] and ind_receipt['no_UUID_time_normalization']
assert ind_receipt['baseline_execution_reused_exact']['repeated'] is False
gzip_rows = [{'source_path': str(AUTHOR / 'new-tests-native-records089.json.gz'),
              'bytes': author_summary['saved_gzip_bytes'], 'sha256': author_summary['saved_gzip_sha256'],
              'decoded_bytes': author_summary['decoded_bytes'], 'decoded_sha256': author_summary['decoded_sha256']}]
gzip_rows += ind_receipt['record_bindings']
for row in gzip_rows:
    compressed = Path(row['source_path']).read_bytes()
    assert len(compressed) == row['bytes'] and sha(compressed) == row['sha256']
    decoded = gzip.decompress(compressed)
    assert len(decoded) == row['decoded_bytes'] and sha(decoded) == row['decoded_sha256']
    json.loads(decoded)
ledger = {
    'status': 'FINAL_REVIEWED_PHASE_LEDGER',
    'source_original5': {'constructors': 5, 'seed_apply': 5, 'subject_apply': 5, 'apply_entries': 10,
                         'repeat_for_product_or_seal': False},
    'independent_static_lead11': {'project_calls': 0},
    'author_new7_once': {'methods': 7, 'pass': 7, 'skip': 0, 'groups': 12,
                        'constructors': 14, 'seed_apply': 12, 'subject_apply': 12,
                        'apply_entries': 24, 'complete_native_records': 38},
    'independent_formal': {'methods': 7, 'pass': 7, 'skip': 0, 'pairs': 3, 'paired_instances': 6,
                          'constructors': 20, 'apply_entries': 30, 'complete_native_records': 50,
                          'fresh_pair_seed_apply': 0, 'actual_roles': ind_receipt['actual_roles'],
                          'successful_baseline3_3_repeated': False},
    'packaging_saved_only_project_calls': 0,
    'not_instrumented': 'Other internal project helpers. No global total inferred.',
    'no_calls_scope': 'Damage/training/app/publicrecognition/formatter/Qt/Wine/real.local are outside this state-only validation.',
    'gzip_decoded_byte_proofs': gzip_rows,
    'current_root_transport': 'Pending actual final pre89 section88 commit. Included template is unexecuted.',
    'root_related_selected_tests': 'Pending; author/independent passes do not substitute.'}
ledger_path = OUT / 'final-phase-ledger089.json'
json_new(ledger_path, ledger)
for path in sorted(TRANSPORT.iterdir()):
    if path.is_file():
        files.append(bound(path, 'root-transport-pending/' + path.name))
handoff_path = OUT / 'handoff-final089.json'
handoff = {
    'status': 'FINAL_SEALED_REVIEWED_READY_ROOT_INTEGRATION', 'section': 89,
    'source_base_commit': freeze['source_base_commit'], 'historical_transport_commit': freeze['transport_root_commit'],
    'actual_pre89_root_commit': 'pending final section88 tag; not inferred from 619/1ce',
    'original_packets': packet_records, 'freeze': bound(freeze_path, 'author-packet/author089/draft-freeze089.json'),
    'product_and_new_test': freeze['files'], 'section_patch': freeze['section_patch'],
    'registry_proposal': freeze['registry_proposal'], 'old_baseline_sha256': freeze['source_run_state_old_sha256'],
    'CRLF_product_LF_newtest': True, 'one_line_inverse_exact': True,
    'formal_unique_final': bound(ind_handoff_path, 'independent-packet/formal-review/final-handoff089.json'),
    'phase_ledger': bound(ledger_path, ledger_path.name),
    'original_source38_and_staticlead11_seals_included_unchanged': True,
    'source_author_independent_passed_calls_repeated_for_seal': False,
    'packaging_new_project_calls': 0, 'tracked_mutations': 0,
    'root_current_checker': {'path': str(TRANSPORT / 'root_current_source089.template.py'),
                             'status': 'UNEXECUTED_TEMPLATE_PENDING_ACTUAL_PRE89',
                             'dependencies': [str(freeze_path), *[r['source_path'] for r in freeze['files']],
                                              'exact final section88 Git commit and root post-apply tracked Python files']},
    'remaining_root_work': ['actual pre89 source/registry transport proof', 'root sole tracked apply/registration',
                            'root fresh related/selected checks', 'root commit/archive89', 'full Linux/Wine/actualUI90'],
    'limits': ['state evidence only; no measured numeric training/damage delta',
               'no P1/native mechanics or old-state repair/migration',
               'natural same-seed UUID/time comparisons, no normalization',
               'cached preparation original failed rawscript unavailable; retained fixed copy is named explicitly'],
    'public_manifest': str(OUT / 'public-manifest-final089.json')}
json_new(handoff_path, handoff)
for path in sorted(OUT.iterdir()):
    if path.is_file():
        files.append(bound(path, 'final-main/' + path.name))
assert len({f['source_path'] for f in files}) == len(files)
assert len({f['archive_path'] for f in files}) == len(files)
manifest = {'version': 1, 'status': handoff['status'], 'files': files,
            'file_count': len(files), 'total_bytes': sum(f['bytes'] for f in files),
            'source38_staticlead11_author71_independent177_originals_immutable': True,
            'pending_root_current_transport_and_integration': True,
            'sealing_new_project_calls': 0}
manifest_path = OUT / 'public-manifest-final089.json'
json_new(manifest_path, manifest)
for row in files:
    data = Path(row['source_path']).read_bytes()
    assert len(data) == row['bytes'] and sha(data) == row['sha256']
print(json.dumps({'status': manifest['status'], 'file_count': len(files), 'total_bytes': manifest['total_bytes'],
                  'manifest': bound(manifest_path, manifest_path.name), 'handoff': bound(handoff_path, handoff_path.name),
                  'new_project_calls': 0, 'actual_root_current_proof': 'pending'}))
