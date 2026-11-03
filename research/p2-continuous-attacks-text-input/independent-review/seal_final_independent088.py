"""Seal existing static/saved and unique fresh evidence; zero new project calls."""
import gzip
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
sha = lambda b: hashlib.sha256(b).hexdigest()


def load(name):
    return json.loads((OUT / name).read_bytes())


def binding(path):
    data = path.read_bytes()
    return {'source_path': str(path), 'archive_path': str(path.relative_to(OUT)),
            'bytes': len(data), 'sha256': sha(data)}


def verify_manifest(path, expected, root, version_key):
    assert sha(path.read_bytes()) == expected
    manifest = json.loads(path.read_bytes())
    assert manifest[version_key] == 1
    for row in manifest['files']:
        source = Path(row['source_path'])
        assert source.is_absolute() and source.is_relative_to(root)
        target = Path(row['archive_path'])
        assert not target.is_absolute() and '..' not in target.parts
        data = source.read_bytes()
        assert len(data) == row['bytes'] and sha(data) == row['sha256']
    assert len({r['archive_path'] for r in manifest['files']}) == len(manifest['files'])
    return manifest


child_root = OUT / 'formal-source-saved'
child_manifest = child_root / 'public-manifest088.json'
child = verify_manifest(child_manifest, '66bb1856cc32dae9d7be31661e6b6dd71d9e05d733f0c9bed3597f2da5737356', child_root, 'version')
assert len(child['files']) == 45 and sum(r['bytes'] for r in child['files']) == 1323473
child_handoff = child_root / 'handoff-final088.json'
assert sha(child_handoff.read_bytes()) == '991cfb7f77ada1a7331e8906bb4f0aa341993e20f15362c1d64acfb3c1ad2a7f'
assert json.loads(child_handoff.read_bytes())['status'] == 'FINAL_SEALED_PASS_INDEPENDENT088_SOURCE_AND_SAVED60_ONLY'
static_path = child_root / 'static-source-review088.json'
saved_path = child_root / 'saved60-review088.json'
assert sha(static_path.read_bytes()) == 'c6e62734887a4d0fe3d3d9df72976f9168ff05f34701da7cbf9d17a80fef866b'
assert sha(saved_path.read_bytes()) == '85670dfc981a2a1175b2127b471dfcf32ba42f6e924997d74f635abca8d6bbb9'
static = json.loads(static_path.read_bytes())
saved = json.loads(saved_path.read_bytes())
assert static['status'] == 'PASS_STATIC_FROZEN_SOURCE_BYTE_AST_AND_SCOPE_ONLY'
assert saved['pairs'] == 60 and saved['new_rejections'] == 23
assert saved['whole_native_JSON_three_text_same'] == 32 and saved['exact_old_errors'] == 5
source_root = OUT / 'source-preparation'
source = verify_manifest(source_root / 'v1-public-files-manifest088.json',
    '2794f5c6bb7d0d334a165d43b8087f5e7ff0412dbecefa7bbfe36abb04dd8042', source_root, 'format_version')
assert len(source['files']) == 17
sp_sidecar = load('source-preparation/child-source-preparation-import088.json')
for row in sp_sidecar['files']:
    data = Path(row['source_path']).read_bytes()
    assert len(data) == row['bytes'] and sha(data) == row['sha256']
assert sha((OUT / 'sp-source-preparation/v1-public-files-manifest088.json').read_bytes()) == 'b150988c2b4c5298d3d5109bbb4340a1fb2a9cb2adffba661ad11c67a8d38a21'
assert sha((OUT / 'sp-source-preparation/sp-source-preparation-handoff088.json').read_bytes()) == 'bff95a9642d547a91a9709447c513b23f93ffe3afe03952bf3d29770bd5203ea'
risk = load('independent-risk-comparison088.json')
test = load('new-tests-independent-receipt088.json')
test_saved = load('saved-native-test-proof088.json')
freeze = load('formal-execution-freeze088.json')
assert risk['status'] == 'PASS_UNIQUE_EIGHT_RISK_PAIRS'
assert risk['outcomes'] == {'whole_unchanged': 5, 'new_text_error': 2, 'old_error_unchanged': 1}
assert test['status'] == 'PASS' and test['methods_run'] == 8
assert test['failures'] == test['errors'] == test['skips'] == 0
assert test['counts']['public_function_entries'] == test['counts']['explicit_test_public_requests'] == 19
assert test['counts']['explicit_test_context_helper_requests'] == 25
assert test_saved['status'] == 'PASS_SAVED_NATIVE_TEST_PROOF_0PROJECTCALLS'
assert freeze['new_test_sha256'] == '8f60e65bae208476eadd06650b7aa4c87f43442fe092a52254f1b3631c2ce9f3'
lossless = []
for side in ('baseline', 'draft'):
    summary = load(side + '-risks088-summary.json')
    path = OUT / (side + '-risks088.jsonl.gz')
    data = path.read_bytes()
    raw = gzip.decompress(data)
    assert len(data) == summary['gzip_bytes'] and sha(data) == summary['gzip_sha256']
    assert len(raw) == summary['decoded_bytes'] and sha(raw) == summary['decoded_sha256']
    lossless.append({'packed': binding(path), 'original_bytes': len(raw),
                     'original_sha256': sha(raw), 'decompressed_sha256': sha(raw), 'lossless_roundtrip': True})
native_path = OUT / 'new-tests-native-evidence088.json.gz'
native_data = native_path.read_bytes()
native_raw = gzip.decompress(native_data)
assert sha(native_raw) == test['native_evidence_decoded_sha256']
assert sha(native_data) == test['native_evidence_gzip_sha256']
lossless.append({'packed': binding(native_path), 'original_bytes': len(native_raw),
                 'original_sha256': sha(native_raw), 'decompressed_sha256': sha(native_raw), 'lossless_roundtrip': True})

receipt_path = OUT / 'independent-formal-receipt088.json'
handoff_path = OUT / 'final-handoff088.json'
manifest_path = OUT / 'final-public-artifacts-manifest088.json'
assert not receipt_path.exists() and not handoff_path.exists() and not manifest_path.exists()
receipt = {
    'format_version': 1, 'status': 'FINAL_PASS_INDEPENDENT_SECTION088',
    'product_patch_sha256': '6cad7ce79a0458e494cb975d3670b404c98f004227f97bb975e87b14fffd9627',
    'author_review_manifest_sha256': '4772c026843a995921c6013fb435fd547e2cb5a67d8f4f6e73245b7e5dbcc445',
    'author_review_freeze_sha256': '10e5e8bcbc3e6a8a74e838d5ddd12638a3574230385a876a0c6d03a7c98baf99',
    'source_and_saved_review': {'manifest': binding(child_manifest), 'handoff': binding(child_handoff),
                               'static': binding(static_path), 'saved60': binding(saved_path),
                               'new_API_helper_tests': 0, 'author_saved_pairs': 60,
                               'text_new_rejections': 23, 'whole_same': 32, 'exact_old_errors': 5},
    'fresh_risk_review': {'receipt': binding(OUT / 'independent-risk-comparison088.json'),
                          'unique_pairs': 8, 'public_requests_and_entries': 16,
                          'whole_beforeJSON_native_JSON_three_text_same': 5,
                          'text_new_rejections': 2, 'exact_old_errors': 1},
    'fresh_final_test_review': {'receipt': binding(OUT / 'new-tests-independent-receipt088.json'),
                                'methods_once': 8, 'passed': 8, 'failures': 0, 'errors': 0, 'skips': 0,
                                'public_requests_and_entries': 19, 'explicit_test_context_helper_requests': 25,
                                'charge_function_entries': 5, 'test_sha256': freeze['new_test_sha256'],
                                'original_test_body_and_expectations_unchanged': True},
    'fresh_ledger': {'public_requests_and_entries': 35, 'explicit_test_context_helper_requests': 25,
                     'explicit_three_text_requests': 36, 'actual_format_estimate_entries': 12,
                     'actual_format_report_entries': 36, 'actual_formatter_entries': 48,
                     'explicit_catalog_native_reads': 20, 'all_project_helpers_total_instrumented': False,
                     'author_source16_or60_or_old_tests_repeated': False},
    'caller_native_and_catalog_complete_native_hash_unchanged': True,
    'catalog_raw_native_tree_separately_saved': False,
    'thread_scope': 'MainThread plus one observed pool worker; nested/token/finally restoration. Two-worker simultaneous stress not claimed.',
    'actual_event_tail_scope': 'Frozen final eighth standalone/scoped helper test; current public received/event relics stay reference-only.',
    'whole_source_scope': '125 enumerated old maintained rouge files/119 unchanged draft/6 exact byte inverses and one new leaf; not all repository source.',
    'root_target_at_readonly_transport_check': freeze['current_root_commit'],
    'root_readonly_patch_applycheck_returncode': freeze['current_root_apply_check']['returncode'],
    'product_API_or_test_failures': 0,
    'preparation_failures_and_old_incorrect_plans_preserved': True,
    'no_fourth_execution_freeze_attempt': True,
    'lossless_native_saved_evidence': lossless,
    'new_network_Spine_source_parse_Qt_Wine_tracked_apply_commit': 0,
    'native_mechanism_clock_or_unknown_attribution_inferred': False,
    'final_scope_sidecar': binding(OUT / 'FORMAL_EVIDENCE_SCOPE088.md')
}
receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
handoff = {'format_version': 1, 'status': 'FINAL_SEALED_PASS_READY_FOR_AUTHOR_IMPORT_AND_ROOT_INTEGRATION',
           'packet_root': str(OUT), 'manifest_path': str(manifest_path),
           'designated_formal_receipt': binding(receipt_path),
           'source_static_saved_and_fresh_numeric_tests': 'PASS; no new product/source calls needed.',
           'fresh_public_total': 35, 'fresh_test_explicit_context_helper_requests': 25,
           'fresh_new_methods_once': 8, 'source_saved_old_calls_repeated': 0,
           'product_patch_sha256': receipt['product_patch_sha256'],
           'new_test_sha256': freeze['new_test_sha256'], 'author_packet_changed': False,
           'immutable_prior_packets': ['087', 'source-preparation17', 'SP-source-preparation13', 'author-review89', 'source16'],
           'next_action': 'Author imports these exact frozen artifacts once; root alone applies/archives/commits and runs related/selected/full/UI.',
           'all_files_listed_stop_writing': True}
handoff_path.write_text(json.dumps(handoff, ensure_ascii=False, indent=2) + '\n')
files = [binding(path) for path in sorted(OUT.rglob('*')) if path.is_file() and path != manifest_path]
assert not any('__pycache__' in Path(row['archive_path']).parts for row in files)
manifest_path.write_text(json.dumps({'format_version': 1, 'status': 'FINAL_IMMUTABLE_INDEPENDENT088',
                                    'archive_root': str(OUT), 'files': files, 'file_count': len(files),
                                    'total_bytes': sum(row['bytes'] for row in files),
                                    'manifest_self_excluded': True, 'handoff_included': True},
                                   ensure_ascii=False, indent=2) + '\n')
for row in files:
    actual = Path(row['source_path']).read_bytes()
    assert len(actual) == row['bytes'] and sha(actual) == row['sha256']
print(json.dumps({'status': handoff['status'], 'files': len(files), 'bytes': sum(row['bytes'] for row in files),
                  'manifest_sha256': sha(manifest_path.read_bytes()), 'handoff_sha256': sha(handoff_path.read_bytes()),
                  'formal_receipt_sha256': sha(receipt_path.read_bytes()), 'new_project_calls_at_seal': 0}))
