"""Add actual root89 transport and independent evidence to the frozen 62 packet."""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--independent-manifest', type=Path, required=True)
parser.add_argument('--independent-receipt', type=Path, required=True)
parser.add_argument('--root-static-review', type=Path)
args = parser.parse_args()
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def write(name, value):
    raw = (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode()
    with (HERE / name).open('xb') as stream:
        stream.write(raw)
    return {'source_path': str(HERE / name), 'archive_path': name,
            'bytes': len(raw), 'sha256': sha(raw)}


files = []
seen = set()


def add(path, archive_path, expected=None):
    pure = PurePosixPath(archive_path)
    assert not pure.is_absolute() and str(pure) == archive_path
    assert '\\' not in archive_path and all(part not in ('.', '..') and ':' not in part for part in pure.parts)
    assert archive_path not in seen
    seen.add(archive_path)
    raw = path.read_bytes()
    if expected:
        assert len(raw) == expected['bytes'] and sha(raw) == expected['sha256'], archive_path
    files.append({'source_path': str(path), 'archive_path': archive_path,
                  'bytes': len(raw), 'sha256': sha(raw)})


review_path = HERE / 'archivable-author-review-manifest090.json'
assert sha(review_path.read_bytes()) == 'ca67748838191ddf110cec897be199799f4ee7657a3af667355908db2ddea47c'
review = json.loads(review_path.read_bytes())
assert len(review['files']) == 62
for entry in review['files']:
    add(Path(entry['source_path']), entry['archive_path'], entry)
add(review_path, review_path.name)
handoff_path = HERE / 'author-review-handoff090.json'
assert sha(handoff_path.read_bytes()) == 'cd2a90ecbd89baec7716d5abc63fde414bc2799db490aaa3587073a1253777ce'
add(handoff_path, handoff_path.name)
transport_path = HERE / 'root89-transport090.json'
transport = json.loads(transport_path.read_bytes())
assert transport['status'] == 'ACTUAL_ROOT89_TRANSPORT_PASS_NO_NEW_TESTS'
assert transport['actual_root_tag'] == 'p2-section-089'
assert transport['new_CLI_verifier_application_helper_formatter_test_parser_network_Qt_Wine_calls'] == 0
for name in ['root89-transport090.json', 'root89-verify_cloud.py',
             'registered-verify_cloud090-root89.py', 'seal_final090.py']:
    add(HERE / name, name)
independent_manifest = json.loads(args.independent_manifest.read_bytes())
assert sha(args.independent_manifest.read_bytes()) == 'c5fb75c696fa019ef7c0ec0cf38b46ad312398e471d210f934752fe4ecf8ad34'
assert independent_manifest['format_version'] == 1
for entry in independent_manifest['files']:
    add(Path(entry['source_path']), 'independent/' + entry['archive_path'], entry)
independent_paths = {entry['source_path'] for entry in independent_manifest['files']}
add(args.independent_manifest, 'independent/' + args.independent_manifest.name)
if str(args.independent_receipt) not in independent_paths:
    add(args.independent_receipt, 'independent/' + args.independent_receipt.name)
receipt = json.loads(args.independent_receipt.read_bytes())
assert sha(args.independent_receipt.read_bytes()) == '64d30e7ab43919b24730f3341d7554be9b802c2d9c442aeae7c1d31df0ebd6c4'
assert receipt['passed'] is True
assert type(receipt['fresh_verifier_function_entries']) is int
assert 0 <= receipt['fresh_verifier_function_entries'] <= 4
root_static_sha = None
if args.root_static_review:
    root_static_raw = args.root_static_review.read_bytes()
    root_static = json.loads(root_static_raw)
    assert root_static['status'] == 'ROOT_STATIC_REVIEW_PASS_PRE_ACTUAL89_TRANSPORT'
    assert root_static['test_API_helper_verifier_network_Qt_Wine_calls'] == 0
    root_static_sha = sha(root_static_raw)
    add(args.root_static_review, args.root_static_review.name)
scope = write('final-scope090.json', {
    'format_version': 1, 'root_baseline_commit': transport['root_baseline_commit'],
    'actual_root_tag': transport['actual_root_tag'],
    'immutable_author62_preserved': True, 'immutable_source28_manifest_handoff_preserved': True,
    'author_normal_CLI_precheck': 1, 'author_new_tests_methods': 6,
    'author_new_tests_CLI_invocations': 10, 'author_new_tests_direct_verifier_entries': 17,
    'author_CLI_total': 11, 'author_verifier_total': 28,
    'independent_receipt_path': str(args.independent_receipt),
    'independent_receipt_sha256': sha(args.independent_receipt.read_bytes()),
    'independent_fresh_verifier_function_entries': receipt['fresh_verifier_function_entries'],
    'author_plus_independent_verifier_entries': 28 + receipt['fresh_verifier_function_entries'],
    'root_static_pre_actual89_review_sha256': root_static_sha,
    'root_static_pre_actual89_review_new_verifier_entries': 0,
    'independent_results_are_separate_not_added_as_author_tests': True,
    'root89_transport_new_verifier_or_test_entries': 0,
    'supported_snapshot_exit_codes': {'verified': 0, 'verification_failed': 1, 'outside_supported_snapshot': 2},
    'source_skeleton_parser_network_application_API_project_helper_formatter_Qt_Wine_calls': 0,
    'production_data_gameplay_paths_historical_generator_manifest_ignore_rules_unchanged': True,
    'source6_only_not_full301_102_or315_closure': True,
    'known_unknowns': ['Native binding/clocks', 'Rendering/atlas/texture geometry',
                       'EOF consumption', 'Historical parser identity/rootcause'],
    'root_fresh_checks_and_five_section_full_validation_still_required': True})
add(HERE / scope['archive_path'], scope['archive_path'], scope)
manifest = write('archivable-public-manifest-final090.json', {
    'format_version': 1, 'status': 'FINAL_STABLE_PRODUCT_ROOT89_BOUND',
    'files': files, 'bytes': sum(entry['bytes'] for entry in files),
    'root_baseline_commit': transport['root_baseline_commit'],
    'author_review62_source28_original_manifests_handoffs_preserved': True,
    'formal_independent_manifest_sha256': sha(args.independent_manifest.read_bytes()),
    'formal_independent_receipt_sha256': sha(args.independent_receipt.read_bytes()),
    'tracked_edits': 0, 'root_owns_apply_commit_root_validation': True})
freeze = json.loads((HERE / 'review-freeze090.json').read_bytes())
handoff = write('final-handoff090.json', {
    'format_version': 1, 'status': 'FINAL_STABLE_ROOT89_BOUND_AUTHOR_PRODUCT',
    'directory': str(HERE), 'manifest': manifest, 'files': len(files),
    'bytes': sum(entry['bytes'] for entry in files),
    'root_baseline_commit': transport['root_baseline_commit'],
    'actual_root_tag': transport['actual_root_tag'],
    'product_files': freeze['product_files'],
    'patch_sha256': freeze['patch_sha256'], 'patch_bytes': freeze['patch_bytes'],
    'registry_proposal': 'registered-verify_cloud090-root89.py',
    'root_source_checker': 'root_current_source090.py',
    'author_CLI_verifier_entries': {'CLI': 11, 'verifier': 28},
    'independent_receipt_sha256': sha(args.independent_receipt.read_bytes()),
    'no_passed_author_calls_repeated_for_transport_or_seal': True,
    'root_owns_tracked_mutations_and_fresh_checks': True})
print(json.dumps({'manifest': manifest, 'handoff': handoff,
                  'files': len(files), 'bytes': sum(entry['bytes'] for entry in files)}))
