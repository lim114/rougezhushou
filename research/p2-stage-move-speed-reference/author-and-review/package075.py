from pathlib import Path
import datetime, difflib, hashlib, json, subprocess

base = Path(__file__).parent
root = Path('/workspace/rougezhushou')
changed = ('rouge/spawn_reference.py', 'rouge/battle_preview.py')
added = {'tests/test_stage_move_speed_reference.py': 'test_stage_move_speed_reference.py'}
patch = ''
for name in changed:
    old = (base / 'baseline' / name).read_bytes().decode()
    new = (base / 'draft075' / name).read_bytes().decode()
    patch += f'diff --git a/{name} b/{name}\n' + ''.join(difflib.unified_diff(
        old.splitlines(True), new.splitlines(True), fromfile='a/' + name, tofile='b/' + name))
for name, local in added.items():
    value = (base / local).read_text()
    patch += f'diff --git a/{name} b/{name}\nnew file mode 100644\n' + ''.join(difflib.unified_diff(
        [], value.splitlines(True), fromfile='/dev/null', tofile='b/' + name))
path = base / 'section75.patch'
path.write_bytes(patch.encode())
freeze = json.loads((base / 'baseline-freeze075.json').read_bytes())
for name, record in freeze['files'].items():
    raw = (base / 'baseline' / name).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == record['sha256'] and len(raw) == record['bytes']
raw = (base / 'level_rogue6_3-6.json').read_bytes()
assert len(raw) == 233958 and hashlib.sha256(raw).hexdigest() == '2d2e89306c3d3c4a2a6c21f71b3828f66cb7a7996ab149faaad043d4867e8296'
matrix = json.loads((base / 'matrix-comparison075.json').read_bytes())
supplement = json.loads((base / 'supplemental-sp-comparison075.json').read_bytes())
new_tests = json.loads((base / 'new-tests075.json').read_bytes())
related = json.loads((base / 'related-tests075.json').read_bytes())
assert not matrix['mismatches'] and not supplement['mismatches']
assert new_tests['passed'] == 8 and new_tests['available_checks_passed']
assert related['available_checks_passed'] and not related['failures'] and not related['errors']
end = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
       'raw_stage_sha256': hashlib.sha256(raw).hexdigest(), 'raw_stage_bytes': len(raw),
       'draft_source_sha256': {name: hashlib.sha256((base / 'draft075' / name).read_bytes()).hexdigest() for name in changed},
       'new_test_sha256': hashlib.sha256((base / 'test_stage_move_speed_reference.py').read_bytes()).hexdigest(),
       'baseline_public_files_verified': freeze['file_count'], 'baseline_intact': True}
assert end['draft_source_sha256'] == new_tests['source_start_sha256'] == new_tests['source_end_sha256']
assert end['draft_source_sha256'] == related['source_start_sha256'] == related['source_end_sha256']
(base / 'author-end-source075.json').write_text(json.dumps(end, ensure_ascii=False, indent=2) + '\n')
check = subprocess.run(['git', 'apply', '--check', str(path)], cwd=root, capture_output=True, text=True)
reverse = None
already_applied = False
if check.returncode:
    reverse = subprocess.run(['git', 'apply', '--reverse', '--check', str(path)], cwd=root, capture_output=True, text=True)
    already_applied = reverse.returncode == 0
reviewfile = base / 'independent-review075.json'
review = json.loads(reviewfile.read_bytes()) if reviewfile.exists() else None
if review:
    assert review['status'] == 'independent_review_passed' and not review['blockers']
    assert review['patch_sha256'] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert review['changed_source_hashes'] == end['draft_source_sha256']
names = ['source_first075.py', 'baseline-freeze075.json', 'source-receipt075.json', 'source-first075.log',
         'level_rogue6_3-6.json', 'build_draft075.py', 'draft-receipt075.json', 'public_probe075.py',
         'baseline-results075.json', 'draft-results075.json', 'baseline-probe075.log', 'draft-probe075.log',
         'compare_matrix075.py', 'matrix-comparison075.json', 'matrix075.log',
         'test_stage_move_speed_reference.py', 'run_tests075.py', 'new-tests075.json', 'new-tests075.log',
         'related-tests-freeze075.json', 'related-tests075.json', 'related-tests075.log',
         'supplemental_sp_probe075.py', 'compare_supplemental_sp075.py',
         'baseline-supplemental-sp075.json', 'draft075-supplemental-sp075.json',
         'baseline-supplemental-sp075.log', 'draft-supplemental-sp075.log',
         'supplemental-sp-comparison075.json', 'supplemental-sp-comparison075.log',
         'section75.patch', 'author-end-source075.json', 'NOTE075.md', 'package075.py']
for item in sorted(base.glob('independent*075*')):
    if item.is_file():
        names.append(item.name)
files = {name: {'sha256': hashlib.sha256((base / name).read_bytes()).hexdigest(),
                'bytes': (base / name).stat().st_size} for name in dict.fromkeys(names)}
manifest = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'files': files,
            'scope': 'public fixed source, author complete JSON/errors and independent review; excludes baseline/draft copies, private state and live data'}
(base / 'manifest075.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
out = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'section': 75,
       'baseline_commit': freeze['frozen_commit'], 'baseline_public_files': freeze['file_count'], 'baseline_intact': True,
       'observed_root_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
       'root_apply_check': {'exit_code': check.returncode, 'stderr': check.stderr},
       'root_patch_already_applied': already_applied,
       'root_reverse_apply_check': None if reverse is None else {'exit_code': reverse.returncode, 'stderr': reverse.stderr},
       'patch_sha256': files['section75.patch']['sha256'], 'draft_source_sha256': end['draft_source_sha256'],
       'new_test_sha256': end['new_test_sha256'], 'changed_files': [*changed, *added],
       'register_new_test_required': 'scripts/verify_cloud.py MODULES tests.test_stage_move_speed_reference; no outdated runner hunk',
       'suggested_research_directory': 'research/p2-stage-move-speed-reference',
       'new_test_methods': 8, 'new_test_methods_passed': 8,
       'related_run': related['run'], 'related_passed': related['passed'], 'related_skipped': related['skipped'],
       'main_paired_scenarios': matrix['paired_scenarios'], 'main_public_calls': matrix['public_calls'],
       'main_matrix_counts': matrix['counts'], 'supplemental_sp_paired_scenarios': supplement['paired_scenarios'],
       'supplemental_sp_public_calls': supplement['public_calls'],
       'total_author_paired_scenarios': matrix['paired_scenarios'] + supplement['paired_scenarios'],
       'total_author_public_calls': matrix['public_calls'] + supplement['public_calls'],
       'raw_move_speed_parameter_reference_only': True,
       'old_subtotal_default_text_all_math_training_state_and_errors_unchanged': True,
       'native_enemy_rune_move_speed_target_writer_layer_and_full_effective_speed_unverified': True,
       'no_private_state_reads_or_resets': True, 'no_native_binaries_or_gui_or_wine': True,
       'independent_review_status': 'passed' if review else 'pending_final_frozen_patch_review',
       'independent_fresh_paired_scenarios': review['fresh_paired_scenarios'] if review else None,
       'independent_fresh_public_calls': review['public_calls'] if review else None,
       'independent_fresh_counts': review['fresh_counts'] if review else None,
       'independent_new_tests_passed': review['new_tests_passed'] if review else None,
       'independent_saved_author_pairs_strictly_recompared': review['saved_author_pairs_strictly_recompared'] if review else None,
       'independent_review_sha256': hashlib.sha256(reviewfile.read_bytes()).hexdigest() if review else None,
       'manifest_sha256': hashlib.sha256((base / 'manifest075.json').read_bytes()).hexdigest()}
(base / 'handoff-receipt075.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print(out)
assert check.returncode == 0 or already_applied
