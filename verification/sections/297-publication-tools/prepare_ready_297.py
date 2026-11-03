"""Only syntax and read-only public evidence checks; never executes publication producers."""
import ast
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PARENT = '7706a982b84fe64148da87d6d073786704c188d1'
SCRIPTS = ['stage_section_297.py', 'push_section_297.py', 'verify_publication_297.py', 'finish_publication_297.py']
HISTORICAL = 'tests/test_documented_item_integration_295.py'
HISTORICAL_SHA = '4e946fd3579f37bc3f222f855f9c23811c1279c946a4345431161ed141fcc2f9'


def load(relative):
    return json.loads((ROOT / relative).read_bytes())


def digest(relative):
    return sha256((ROOT / relative).read_bytes()).hexdigest()


for name in SCRIPTS:
    source = (HERE / name).read_text(encoding='utf8')
    compile(ast.parse(source, filename=name), name, 'exec')
    assert 'parents[2]' in source and "['git','commit'" not in source and '--force' not in source
    assert 'c772147f4ee4846464b32b88f51c88f874db3fcd' not in source
    assert 'actually_navigated_stage_count' not in source and 'actually_navigated_entry_count' not in source
    assert 'explicit_exclusions' not in source and 'autopsy configurations' not in source
stage = (HERE / SCRIPTS[0]).read_text(encoding='utf8')
tree = ast.parse(stage)
tracked = next(ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign)
    and any(isinstance(target, ast.Name) and target.id == 'tracked' for target in node.targets))
assert tracked == ['AGENTS.md', 'CLOUD_HANDOFF.md', 'CLOUD_INDEX.json', 'DEVELOPMENT_CHECKPOINT.json',
    'PROJECT_COMPLETED.md', 'PROJECT_REQUIREMENTS.md', 'WORK_IN_PROGRESS.md', 'rouge/node_catalog_view.py',
    'rouge/player_node_information.py', HISTORICAL]
assert "'.html'" in stage and 'PROJECT_PROGRESS.md' not in tracked
assert "'HEAD:refs/heads/codex/p2-development'" in (HERE / SCRIPTS[1]).read_text(encoding='utf8')
baseline = json.loads((HERE / 'BASELINE.json').read_bytes())
for name, pin in baseline['files'].items():
    raw = (ROOT / '.cache/p3-296-publication-prep' / name).read_bytes()
    assert len(raw) == pin['bytes'] and sha256(raw).hexdigest() == pin['sha256']
promotion_name = 'verification/sections/297-preparation/promotion.json'
assert digest(promotion_name) == baseline['promotion_receipt_sha256']
promotion = load(promotion_name)
assert promotion['section'] == 297 and len(promotion['promoted']) == 18
assert set(promotion['existing_production_changes']) == set(tracked[7:9])
bare_logs = {f'verification/sections/297-preparation/{name}': row['sha256']
    for name, row in promotion['archived_inputs'].items()
    if name in {'backend/first-real-pure-api-tests/stderr', 'backend/first-real-pure-api-tests/stdout',
                'backend/first-real-source-build/stderr', 'backend/first-real-source-build/stdout'}}
assert len(bare_logs) == 4
for name, expected in bare_logs.items():
    assert digest(name) == expected
for entry in (ROOT / 'verification/sections').iterdir():
    if not entry.name.startswith('297'):
        continue
    for member in [entry] if entry.is_file() else entry.rglob('*'):
        assert not member.is_symlink()
        if member.is_file():
            assert member.suffix in {'.json','.log','.md','.png','.py','.txt','.diff','.stderr','.stdout','.html'} or member.relative_to(ROOT).as_posix() in bare_logs
            assert member.stat().st_size < 20_000_000
migration_name = 'verification/sections/297-preparation/historical295-presentation-scope/migration.json'
migration = load(migration_name)
assert migration['path'] == HISTORICAL and migration['after_sha256'] == HISTORICAL_SHA == digest(HISTORICAL)
assert migration['all_original_assertion_AST_preserved'] is True
assert migration['current_default37_nontarget_and190resource_hashes_covered_by'] == 'tests/test_expedition_integration_297.py'
necessary_name = 'verification/sections/297-necessary-first/process.json'
necessary = load(necessary_name)
assert necessary['section'] == 297 and necessary['source_commit_before'] == PARENT
assert necessary['exit_code'] == 0 and necessary['source_unchanged'] is True
assert necessary['source_sha256_before'] == necessary['source_sha256_after']
stderr = (ROOT / necessary_name).with_name('stderr.txt').read_text(encoding='utf8')
methods = re.findall(r'Ran (\d+) tests in ', stderr)
assert len(methods) == 1 and int(methods[0]) == 104 and stderr.rstrip().endswith('OK')
necessary_map = necessary['source_sha256_after']
assert len(necessary_map) == 380
for name, expected in necessary_map.items():
    assert not name.startswith(('.cache/', '.local/')) and name != 'local-settings.json'
    assert digest(name) == expected, name
section_name = 'verification/sections/297.json'
section_file = ROOT / section_name
assert section_file.is_file(), 'Final297 receipt required for this final READY; initial preparation is never publication PASS'
section = load(section_name)
assert section['section'] == 297 and section['prior_commit'] == PARENT and section['next_section'] == 298
assert section['cloud_published'] is False
assert section['necessary_validation']['receipt'] == necessary_name
assert section['necessary_validation']['sha256'] == digest(necessary_name)
assert section['necessary_validation']['methods_run'] == int(methods[0])
native_ref = section['native_windows_validation']
native_name = native_ref['receipt']
assert digest(native_name) == native_ref['sha256']
native = load(native_name)
assert native['passed'] is True and native['qt_exit_code'] == 0 and native['verification_window_closed'] is True
assert native['source_sha256_before'] == native['source_sha256_after']
assert native['source_guard_is_selected_not_all_transitive_dependencies'] is True
native_map = native['source_sha256_after']
assert len(native_map) == 30 and set(native_map) <= set(necessary_map)
assert all(necessary_map[name] == value == digest(name) for name, value in native_map.items())
assert native['unique_checks'] == 65 and native['successful_assertion_executions_including_repeated_guards'] == 196
assert native['screenshot_count'] == 5
assert section['source_promotion']['sha256'] == baseline['promotion_receipt_sha256']
assert set(section['source_sha256']) == set(promotion['promoted']) | {HISTORICAL}
assert len(section['source_sha256']) == 19
assert all(necessary_map[name] == value == digest(name) for name, value in section['source_sha256'].items())
assert section['typed_named_grant_count_unchanged'] == 17 and section['original_entry_gaps_unchanged'] == [25, 57]
assert section['unparsed_notes_unchanged'] == 10 and section['remaining_global_stage_floor_gaps_unchanged'] == 15
assert section['old_resource_query_count_unchanged'] == 190 and section['other_event_player_output_count_unchanged'] == 37
assert section['partial_direct_reference_scope_unchanged'] == [10, 18, 58] and section['whole_map_gaps_unchanged'] == [81, 59]
assert digest('PROJECT_PROGRESS.md') == section['PROJECT_PROGRESS_unchanged_sha256']
assert section['full_validation']['after_section'] == 290 and section['full_validation']['full_suite_rerun'] is False
main_ref = native_ref['original_project_window']
for item in (main_ref, native_ref['owned_process']):
    assert digest(item['receipt']) == item['sha256']
assert digest(main_ref['focus_receipt']) == main_ref['focus_sha256']
assert main_ref['changed_private_paths'] == 0 and main_ref['private_hash_comparisons'] == 5
assert native_map['scripts/verify_expedition_results_window_297.py'] == native_ref['reviewed_native_source_sha256']
proof = native_ref['root_visual_review']
assert digest(proof['receipt']) == proof['sha256'] and proof['actual_root_reviewed_images'] == 5
files = SCRIPTS + ['prepare_tools_297.py', 'prepare_ready_297.py', 'RUN_PLAN.md', 'BASELINE.json']
result = {'kind': 'SECTION297_PUBLICATION_CACHE_PREPARATION_ONLY',
    'prepared_utc': datetime.now(timezone.utc).isoformat(),
    'static_AST_and_actual_public_necessary_schema_checked': True,
    'publication_tools_executed': False, 'Git_mutation_commit_push_or_Qt_tests_executed_by_preparation': False,
    'parent_commit': PARENT, 'functional_commit': None, 'metadata_commit': None,
    'remote_ref': None, 'publication_passed': None,
    'final_section_receipt_must_be_verified_again_at_execution': section_name,
    'observed_existing_validation_only': {'necessary_methods': int(methods[0]), 'necessary_source_files': len(necessary_map),
        'necessary_actual_exit': necessary['exit_code'], 'necessary_receipt_sha256': digest(necessary_name),
        'section_receipt_sha256': digest(section_name),
        'native_validation': {'receipt': native_name, 'sha256': digest(native_name),
            'actual_passed': native['passed'], 'actual_Qt_exit': native['qt_exit_code'],
            'actual_unique_checks': native['unique_checks'],
            'actual_repeated_assertion_executions': native['successful_assertion_executions_including_repeated_guards'],
            'actual_source_files': len(native_map), 'actual_screenshot_count': native['screenshot_count']},
        'necessary_native_source_join': {'common': len(native_map), 'joined': len(necessary_map),
            'native_is_subset_of_necessary': True, 'native_scope_is_selected_not_all_transitive': True},
        'main_receipt_sha256': main_ref['sha256'], 'focus_receipt_sha256': main_ref['focus_sha256'],
        'published_source_scope_still_requires_actual_Git_blob_and_remote_verification': True},
    'functional_tracked_allowlist': tracked, 'PROJECT_PROGRESS_staged': False,
    'explicit_HTML_allowed': True, 'bare_logs_require_exact_promoted_original_SHA': bare_logs,
    'promotion_provenance_entries': 18, 'final_feature_and_test_maintenance_source_entries': 19,
    'promotion_original_hashes_not_used_as_final_source_values': True,
    'files': {name: {'sha256': sha256((HERE / name).read_bytes()).hexdigest(),
                     'bytes': (HERE / name).stat().st_size} for name in files}}
with (HERE / 'READY.json').open('xb') as stream:
    stream.write((json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf8'))
print(json.dumps({'cache_preparation_only': True, 'all_four_scripts_AST_compile_valid': True,
    'publication_Git_Qt_tests_executed': False, 'READY_sha256': sha256((HERE / 'READY.json').read_bytes()).hexdigest(),
    'script_sha256': {name: result['files'][name]['sha256'] for name in SCRIPTS}}))
