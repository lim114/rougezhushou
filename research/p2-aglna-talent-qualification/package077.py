from pathlib import Path
import datetime, difflib, hashlib, json, subprocess

base = Path(__file__).parent
root = Path('/workspace/rougezhushou')
name = 'rouge/operator_engine.py'
old = (base / 'baseline' / name).read_bytes().decode()
new = (base / 'draft077' / name).read_bytes().decode()
patch = f'diff --git a/{name} b/{name}\n' + ''.join(difflib.unified_diff(
    old.splitlines(True), new.splitlines(True), fromfile='a/' + name, tofile='b/' + name))
test_name = 'tests/test_aglna_talent_qualification.py'
test = (base / 'test_aglna_talent_qualification.py').read_text()
patch += f'diff --git a/{test_name} b/{test_name}\nnew file mode 100644\n' + ''.join(difflib.unified_diff(
    [], test.splitlines(True), fromfile='/dev/null', tofile='b/' + test_name))
path = base / 'section77.patch'
path.write_bytes(patch.encode())
freeze = json.loads((base / 'baseline-freeze077.json').read_bytes())
for relative, record in freeze['files'].items():
    raw = (base / 'baseline' / relative).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == record['sha256'] and len(raw) == record['bytes']
matrix = json.loads((base / 'matrix-comparison077.json').read_bytes())
new_tests = json.loads((base / 'new-tests077.json').read_bytes())
related = json.loads((base / 'related-tests077.json').read_bytes())
assert not matrix['mismatches'] and new_tests['passed'] == 9 and related['passed'] == 38
assert new_tests['available_checks_passed'] and related['available_checks_passed']
source_sha = hashlib.sha256((base / 'draft077' / name).read_bytes()).hexdigest()
assert source_sha == new_tests['source_start_sha256'] == new_tests['source_end_sha256']
assert source_sha == related['source_start_sha256'] == related['source_end_sha256']
end = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'baseline_intact': True,
       'baseline_public_files_verified': freeze['file_count'], 'changed_source_hashes': {name: source_sha},
       'new_test_sha256': hashlib.sha256((base / 'test_aglna_talent_qualification.py').read_bytes()).hexdigest(),
       'source_tables_rehashed_before_patch': True, 'no_product_source_changes_after_completed_matrix': True}
(base / 'author-end-source077.json').write_text(json.dumps(end, ensure_ascii=False, indent=2) + '\n')
check = subprocess.run(['git', 'apply', '--check', str(path)], cwd=root, capture_output=True, text=True)
reverse = None
already_applied = False
if check.returncode:
    reverse = subprocess.run(['git', 'apply', '--reverse', '--check', str(path)], cwd=root, capture_output=True, text=True)
    already_applied = reverse.returncode == 0
reviewfile = base / 'independent-review077.json'
review = json.loads(reviewfile.read_bytes()) if reviewfile.exists() else None
if review:
    assert review['status'] == 'independent_review_passed' and not review['blockers']
    assert review['patch_sha256'] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert review['changed_source_hashes'] == end['changed_source_hashes']
names = ['baseline-freeze077.json', 'source_audit077.py', 'source-receipt077.json', 'source-audit077.log',
         'selected-original-objects077.json', 'readonly-public-results077.json', 'build_draft077.py',
         'draft-receipt077.json', 'public_probe077.py', 'baseline-results077.json', 'draft-results077.json',
         'baseline-probe077.log', 'draft-probe077.log', 'diff_paths077.py', 'complete-json-changed-paths077.json',
         'changed-paths077.log', 'compare_matrix077.py', 'matrix-comparison077.json', 'matrix077.log',
         'test_aglna_talent_qualification.py', 'run_tests077.py', 'new-tests077.json', 'new-tests077.log',
         'related-tests077.json', 'related-tests077.log',
         'initial-test-contract-error077-new-tests077.json', 'initial-test-contract-error077-new-tests077.log',
         'initial-test-contract-error077-test_aglna_talent_qualification.py',
         'section77.patch', 'author-end-source077.json', 'NOTE077.md', 'package077.py']
names.extend(str(p.relative_to(base)) for p in sorted((base / 'prior-research').glob('*')) if p.is_file())
names.extend(p.name for p in sorted(base.glob('independent*077*')) if p.is_file())
files = {relative: {'sha256': hashlib.sha256((base / relative).read_bytes()).hexdigest(),
                    'bytes': (base / relative).stat().st_size} for relative in dict.fromkeys(names)}
manifest = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'files': files,
            'scope': 'public exact raw selected objects, frozen source and complete JSON/errors; excludes package copies and private state'}
(base / 'manifest077.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
out = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'section': 77,
       'baseline_commit': freeze['commit'], 'baseline_public_files': freeze['file_count'], 'baseline_intact': True,
       'observed_root_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
       'root_apply_check': {'exit_code': check.returncode, 'stderr': check.stderr}, 'root_patch_already_applied': already_applied,
       'root_reverse_apply_check': None if reverse is None else {'exit_code': reverse.returncode, 'stderr': reverse.stderr},
       'patch_sha256': files['section77.patch']['sha256'], 'changed_source_hashes': end['changed_source_hashes'],
       'new_test_sha256': end['new_test_sha256'], 'changed_files': [name, test_name],
       'register_new_test_required': 'scripts/verify_cloud.py MODULES tests.test_aglna_talent_qualification; no outdated runner hunk',
       'suggested_research_directory': 'research/p2-aglna-talent-qualification',
       'new_tests_passed': 9, 'related_tests_passed': 38, 'skips': 0,
       'paired_scenarios': matrix['paired_scenarios'], 'matrix_counts': matrix['counts'],
       'matrix_actual_new_public_calls': matrix['matrix_actual_new_public_calls'],
       'source_audit_calls_reused_without_rerun': matrix['reused_readonly_public_calls_without_rerun'],
       'total_actual_author_public_calls_including_source_audit': matrix['total_actual_author_public_calls_including_reused_source_audit'],
       'only_E0_unselected_talent_phantom_hits_times_and_skill_count_zeroed': True,
       'all_math_training_status_unknown_clocks_owner_streams_and_prior_errors_unchanged': True,
       'native_snapshot_order_and_S2_phase_clocks_remain_unknown': True,
       'no_tracked_private_state_native_binaries_gui_or_wine': True,
       'independent_review_status': 'passed' if review else 'pending_final_frozen_patch_review',
       'independent_fresh_paired_scenarios': review['fresh_paired_scenarios'] if review else None,
       'independent_fresh_public_calls': review['public_calls'] if review else None,
       'independent_new_tests_passed': review['new_tests_passed'] if review else None,
       'independent_saved_author_pairs_strictly_recompared': review['saved_author_pairs_strictly_recompared'] if review else None,
       'independent_review_sha256': hashlib.sha256(reviewfile.read_bytes()).hexdigest() if review else None,
       'manifest_sha256': hashlib.sha256((base / 'manifest077.json').read_bytes()).hexdigest()}
(base / 'handoff-receipt077.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print(out)
assert check.returncode == 0 or already_applied
