"""Pure cached AST/public-read preparation; no publication tool execution."""
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import ast
import json
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SCRIPTS = ['stage_section_296.py', 'push_section_296.py', 'verify_publication_296.py', 'finish_publication_296.py']
PARENT = 'c772147f4ee4846464b32b88f51c88f874db3fcd'
for name in SCRIPTS:
    text = (HERE / name).read_text(encoding='utf8')
    ast.parse(text, filename=name); compile(text, name, 'exec')
    assert 'parents[2]' in text and "['git','commit'" not in text and '--force' not in text
    assert 'e517095f388baad3aa7824dbd5b9dee6a68fb450' not in text
    assert 'alpha-item' not in text and 'all38' not in text and 'and38 full reward' not in text
stage = (HERE / SCRIPTS[0]).read_text(encoding='utf8')
tree = ast.parse(stage)
tracked = next(ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign)
    and any(isinstance(target, ast.Name) and target.id == 'tracked' for target in n.targets))
assert tracked == ['AGENTS.md', 'CLOUD_HANDOFF.md', 'CLOUD_INDEX.json', 'DEVELOPMENT_CHECKPOINT.json',
    'PROJECT_COMPLETED.md', 'PROJECT_REQUIREMENTS.md', 'WORK_IN_PROGRESS.md', 'rouge/app.py',
    'rouge/battle_view.py', 'rouge/node_catalog_view.py', 'rouge/player_node_information.py']
assert "'.html'" in stage and 'PROJECT_PROGRESS.md' not in tracked
assert "'HEAD:refs/heads/codex/p2-development'" in (HERE / SCRIPTS[1]).read_text(encoding='utf8')
baseline = json.loads((HERE / 'BASELINE.json').read_bytes())
for name, pin in baseline['files'].items():
    raw = (ROOT / '.cache/p3-295-publication-prep' / name).read_bytes()
    assert len(raw) == pin['bytes'] and sha256(raw).hexdigest() == pin['sha256']
promotion_file = ROOT / 'verification/sections/296-preparation/promotion.json'
assert sha256(promotion_file.read_bytes()).hexdigest() == baseline['promotion_receipt_sha256']
promotion = json.loads(promotion_file.read_bytes())
assert promotion['section'] == 296 and len(promotion['promoted']) == 49
assert set(promotion['existing_production_changes']) == set(tracked[-4:])
necessary_file = ROOT / 'verification/sections/296-necessary-reading-retry2/process.json'
necessary = json.loads(necessary_file.read_bytes())
assert necessary['section'] == 296 and necessary['source_commit_before'] == PARENT
assert necessary['exit_code'] == 0 and necessary['source_unchanged'] is True
assert necessary['source_sha256_before'] == necessary['source_sha256_after']
stderr = (necessary_file.parent / 'stderr.txt').read_text(encoding='utf8')
methods = re.findall(r'Ran (\d+) tests in ', stderr)
assert len(methods) == 1 and stderr.rstrip().endswith('OK')
for name, expected in necessary['source_sha256_after'].items():
    assert not name.startswith(('.cache/', '.local/')) and name != 'local-settings.json'
    assert sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
section_file = ROOT / 'verification/sections/296.json'
section = json.loads(section_file.read_bytes())
assert section['section'] == 296 and section['prior_commit'] == PARENT and section['next_section'] == 297
assert section['necessary_validation']['receipt'] == necessary_file.relative_to(ROOT).as_posix()
assert section['necessary_validation']['sha256'] == sha256(necessary_file.read_bytes()).hexdigest()
assert section['necessary_validation']['methods_run'] == int(methods[0])
native_ref = section['native_windows_validation']
native_file = ROOT / native_ref['receipt']
assert sha256(native_file.read_bytes()).hexdigest() == native_ref['sha256']
native = json.loads(native_file.read_bytes())
assert native['passed'] is True and native['qt_exit_code'] == 0 and native['verification_window_closed'] is True
assert native['source_sha256_before'] == native['source_sha256_after']
necessary_map = necessary['source_sha256_after']; native_map = native['source_sha256_after']
common = set(necessary_map) & set(native_map)
assert all(necessary_map[name] == native_map[name] for name in common)
extra = set(native_map) - set(necessary_map)
assert extra == {'research/p3-stage-context/community-main.html'}
assert native_map[next(iter(extra))] == '366e0bf14b526816b20750f1d83b6c7b132d556dfc0b09a0ab3c302fd00610e9'
joined = dict(necessary_map); joined.update(native_map)
for name, expected in joined.items():
    assert sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
assert section['source_promotion']['sha256'] == baseline['promotion_receipt_sha256']
assert set(section['source_sha256']) == set(promotion['promoted'])
assert all(joined[name] == expected for name, expected in section['source_sha256'].items())
assert section['typed_named_grant_count_unchanged'] == 17 and section['original_entry_gaps_unchanged'] == [25, 57]
assert section['remaining_global_stage_floor_gaps_unchanged'] == 15
assert section['partial_direct_reference_scope_unchanged'] == [10, 18, 58] and section['whole_map_gaps_unchanged'] == [81, 59]
assert sha256((ROOT / 'PROJECT_PROGRESS.md').read_bytes()).hexdigest() == section['PROJECT_PROGRESS_unchanged_sha256']
assert section['full_validation']['after_section'] == 290 and section['full_validation']['full_suite_rerun'] is False
window_refs = {'isolated_native': native_ref, 'main': native_ref['original_project_window']}
for item in (window_refs['main'], native_ref['owned_process']):
    assert sha256((ROOT / item['receipt']).read_bytes()).hexdigest() == item['sha256']
assert sha256((ROOT / window_refs['main']['focus_receipt']).read_bytes()).hexdigest() == window_refs['main']['focus_sha256']
assert window_refs['main']['changed_private_paths'] == 0 and window_refs['main']['private_hash_comparisons'] == 5
assert native_map['scripts/verify_battle_entry_references_window_296.py'] == native_ref['reviewed_native_source_sha256']
files = SCRIPTS + ['prepare_tools_296.py', 'prepare_ready_296.py', 'RUN_PLAN.md', 'BASELINE.json']
result = {'kind': 'SECTION296_PUBLICATION_CACHE_PREPARATION_ONLY',
    'prepared_utc': datetime.now(timezone.utc).isoformat(),
    'static_AST_and_actual_public_necessary_schema_checked': True,
    'publication_tools_executed': False, 'Git_mutation_commit_push_or_Qt_tests_executed_by_preparation': False,
    'parent_commit': PARENT, 'functional_commit': None, 'metadata_commit': None,
    'remote_ref': None, 'publication_passed': None,
    'final_section_receipt_must_be_generated_and_verified_at_execution': 'verification/sections/296.json',
    'observed_existing_validation_only': {'necessary_methods': int(methods[0]),
        'necessary_source_files': len(necessary['source_sha256_after']), 'necessary_actual_exit': necessary['exit_code'],
        'necessary_receipt_sha256': sha256(necessary_file.read_bytes()).hexdigest(),
        'section_receipt_sha256': sha256(section_file.read_bytes()).hexdigest(),
        'native_validation': {'receipt': native_ref['receipt'], 'sha256': native_ref['sha256'],
            'actual_passed': native['passed'], 'actual_Qt_exit': native['qt_exit_code'],
            'actual_unique_checks': native['unique_checks'],
            'actual_repeated_assertion_executions': native['successful_assertion_executions_including_repeated_guards'],
            'actual_source_files': len(native_map), 'actual_screenshot_count': native['screenshot_count'],
            'actual_manual_entry_count': native['actually_navigated_entry_count'],
            'actual_exact_stage_count': native['actually_navigated_stage_count'],
            'actual_excluded_choice_count': len(native['explicit_exclusions'])},
        'necessary_native_source_join': {'common': len(common), 'joined': len(joined),
            'native_is_subset_of_necessary': set(native_map) <= set(necessary_map),
            'fixed_additional_native_sources': {name: native_map[name] for name in sorted(extra)}},
        'main_receipt_sha256': window_refs['main']['sha256'], 'focus_receipt_sha256': window_refs['main']['focus_sha256'],
        'published_source_scope_still_requires_actual_Git_blob_and_remote_verification': True},
    'functional_tracked_allowlist': tracked, 'PROJECT_PROGRESS_staged': False,
    'explicit_HTML_allowed': True, 'promotion_provenance_entries': len(promotion['promoted']),
    'promotion_original_hashes_not_used_as_final_source_values': True,
    'files': {name: {'sha256': sha256((HERE / name).read_bytes()).hexdigest(), 'bytes': (HERE / name).stat().st_size} for name in files}}
with (HERE / 'READY.json').open('xb') as stream:
    stream.write((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
print(json.dumps({'cache_preparation_only': True, 'all_four_scripts_AST_compile_valid': True,
    'publication_Git_Qt_tests_executed': False, 'READY_sha256': sha256((HERE / 'READY.json').read_bytes()).hexdigest(),
    'script_sha256': {name: result['files'][name]['sha256'] for name in SCRIPTS}}))
