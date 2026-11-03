"""Cache-only hash/AST handoff. No product import or further tests."""
import ast
from datetime import datetime, timezone
import difflib
from hashlib import sha256
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CANDIDATE = HERE / 'candidate'
PACK = 'research/p3-ritual-weakening-302'


def encoded(value): return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8')


def pin(path):
    raw = path.read_bytes()
    return {'sha256': sha256(raw).hexdigest(), 'bytes': len(raw)}


test_name = 'tests/test_ritual_weakening_302.py'
before = HERE / 'backend-first/source' / test_name
after = CANDIDATE / test_name
old_tree = ast.parse(before.read_text(encoding='utf8'))
new_tree = ast.parse(after.read_text(encoding='utf8'))
def methods(tree):
    return {n.name: ast.dump(n, include_attributes=False) for c in tree.body if isinstance(c, ast.ClassDef)
            for n in c.body if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}
old_methods, new_methods = methods(old_tree), methods(new_tree)
changed = [n for n in old_methods if old_methods[n] != new_methods[n]]
assert len(old_methods) == len(new_methods) == 24 and changed == ['test_complete_two_event_doms_and_fixed_ending_not_tool_snippet']
diff = ''.join(difflib.unified_diff(before.read_text(encoding='utf8').splitlines(True),
                                  after.read_text(encoding='utf8').splitlines(True),
                                  fromfile='first-actual-test', tofile='corrected-test'))
(HERE / 'first-test-premise-correction.diff').write_bytes(diff.encode('utf8'))
first = json.loads((HERE / 'backend-first/process.json').read_bytes())
final = json.loads((HERE / 'backend-corrected/process.json').read_bytes())
assert first['exit_code'] == 1 and final['exit_code'] == 0
assert first['all_preexisting_inputs_unchanged'] and final['all_preexisting_inputs_unchanged']
assert set(first['source_sha256_after']) == set(final['source_sha256_after'])
assert [n for n in first['source_sha256_after'] if first['source_sha256_after'][n] != final['source_sha256_after'][n]] == [test_name]
correction = {'kind': 'ONE_TEST_DOM_LOCATION_PREMISE_CORRECTION_NOT_PRODUCT_FIX',
              'first_actual_methods': 24, 'first_actual_exit': 1, 'first_actual_failures': 1,
              'first_process': 'backend-first/process.json', 'first_process_pin': pin(HERE / 'backend-first/process.json'),
              'original_source': 'backend-first/source/' + test_name, 'old_test_pin': pin(before), 'new_test_pin': pin(after),
              'changed_methods': changed, 'other_test_method_AST_unchanged': 23,
              'original_title_literals_retained': True,
              'cause': 'PRTS choice titles are complete DOM data-title attributes, not textContent; original expected titles were retained and exact description text added.',
              'production_data_builder_source_changed_for_correction': False,
              'final_actual_methods': 24, 'final_actual_exit': 0,
              'first_and_final_counts_added': False}
(HERE / 'first-test-premise-correction.json').write_bytes(encoded(correction))
manifest = json.loads((CANDIDATE / PACK / 'source-manifest.json').read_bytes())
new_paths = ['rouge/ritual_weakening.py', 'rouge/data/ritual-weakening.json',
             'scripts/build_ritual_weakening_302.py', test_name]
new_paths += [p.relative_to(CANDIDATE).as_posix() for p in (CANDIDATE / PACK).iterdir() if p.is_file()]
assert len(new_paths) == len(set(new_paths)) == 9
for n in new_paths:
    if n.endswith('.py'): ast.parse((CANDIDATE / n).read_text(encoding='utf8'))
for name, value in manifest['files'].items(): assert pin(CANDIDATE / name) == value
existing = {n: pin(CANDIDATE / n) for n in manifest['files'] if n not in new_paths}
assert len(existing) == 6
assert all(pin(ROOT / n) == value for n, value in existing.items())
history = ROOT / 'verification/sections/301-preparation/future-notes-and-ritual-research'
history_names = ['READY.json', 'PROPOSAL.md', 'first-candidate-source-extraction-failure.json',
                 'actual-chimera-HTTP-process-tool-result.json', 'actual-chimera-native-HTTP-process-tool-result.json',
                 'actual-chimera-page-tool-result.json']
scope = {'section': 302, 'candidate_only': True, 'events': 1, 'exact_choices': 6, 'weakening_references': 3,
         'related_fixed_stage': 'ro6_b_6', 'ritual_feature_order': [1, 3, 2],
         'original_scene_entry_gaps_not_restored': [25, 57], 'calculation_run_state_eligibility_changed': False,
         'no_immediate_event_battle_transition_added': True,
         'first_cast_limitation_preserved': True, 'damage_scale_half_only_configuration_not_actual_result': True,
         'private_key_three_distinct_options_not_one_all_effects_purchase': True}
(HERE / 'SCOPE_CANDIDATE.json').write_bytes(encoded(scope))
handoff = {'kind': 'SECTION302_CACHE_BACKEND_READY_NOT_FORMAL_PRODUCT_ACCEPTANCE',
           'at_utc': datetime.now(timezone.utc).isoformat(), 'section': 302,
           'candidate_root': str(CANDIDATE), 'candidate_directory': 'candidate',
           'source_parent': '87a622e', 'promotion_files': {n: pin(CANDIDATE / n) for n in sorted(new_paths)},
           'promotion_allowlist': sorted(new_paths), 'existing_dependency_files': existing,
           'API': {'module': 'rouge.ritual_weakening', 'event_reference': '(event_id)',
                   'weakening_details': '(event_id,scene_key,choice_key)', 'event_id': 'community_group_032',
                   'source_failure_status': 'source_unavailable', 'backend_snapshot_cache': False},
           'source_schema': PACK + '/SCHEMA.md', 'source_manifest': PACK + '/source-manifest.json',
           'runtime_members': len(manifest['runtime_files']),
           'runtime_bytes_with_manifest': sum(p['bytes'] for p in manifest['runtime_files'].values()) + (CANDIDATE / PACK / 'source-manifest.json').stat().st_size,
           'runtime_reads_complete_primary_table': False,
           'runtime_clone_files': [PACK + '/source-manifest.json', *manifest['runtime_files']],
           'build_clone_files': [PACK + '/source-manifest.json', *manifest['files']],
           'author_source_build': {'path': 'source-build-first/process.json', 'pin': pin(HERE / 'source-build-first/process.json'), 'actual_exit': 0},
           'author_original_first_api': {'path': 'backend-first/process.json', 'pin': pin(HERE / 'backend-first/process.json'), 'actual_exit': 1, 'methods': 24, 'failures': 1},
           'author_corrected_api': {'path': 'backend-corrected/process.json', 'pin': pin(HERE / 'backend-corrected/process.json'), 'actual_exit': 0, 'methods': 24},
           'test_premise_correction': {'path': 'first-test-premise-correction.json', 'pin': pin(HERE / 'first-test-premise-correction.json')},
           'prior_research_actual_failure_and_source_history': {
               str((history / n).relative_to(ROOT)).replace('\\', '/'): pin(history / n) for n in history_names},
           'necessary_modules_suggested': ['tests.test_ritual_weakening_302'],
           'all_negative_tests_cleanup_own_legacy_cache': True,
           'scope': scope, 'Qt_tests_live_Git_game_chat_private_operations': False,
           'author_tests_are_preparation_not_additional_formal_counts': True,
           'formal_product_necessary_or_native_or_publication_passed': None}
with (HERE / 'HANDOFF.json').open('xb') as stream: stream.write(encoded(handoff))
print(json.dumps({'HANDOFF': pin(HERE / 'HANDOFF.json'), 'promotion_files': len(new_paths),
                  'core': pin(CANDIDATE / 'rouge/ritual_weakening.py'),
                  'test': pin(after), 'actual_author_final': '24/exit0', 'production_modified': False}, ensure_ascii=False, indent=2))
