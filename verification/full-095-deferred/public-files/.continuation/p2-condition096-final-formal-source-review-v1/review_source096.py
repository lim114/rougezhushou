"""Independent stdlib-only source review. Never import or execute target code."""
import ast
import base64
import hashlib
import json
from pathlib import Path
import stat

ROOT = Path('/workspace/rougezhushou')
CANDIDATE = Path('/workspace/.continuation/p2-condition096-candidate-v1')
OUT = Path(__file__).parent
GUARD = Path('/workspace/.continuation/root-source-095-v2.json')
CHECKS = []


def sha(data):
    return hashlib.sha256(data).hexdigest()


def ref(path):
    path = Path(path)
    assert stat.S_ISREG(path.lstat().st_mode) and not path.is_symlink(), str(path)
    data = path.read_bytes()
    return {'path': str(path), 'bytes': len(data), 'sha256': sha(data)}


def load(path):
    return json.loads(Path(path).read_bytes())


def check(code, title, observation, evidence=None):
    CHECKS.append({'id': code, 'status': 'PASS_SOURCE_ONLY', 'title': title,
                   'observation': observation, 'evidence': evidence or {}})


def verify_ref(record):
    actual = ref(record['path'])
    assert actual['bytes'] == record['bytes'], actual
    assert actual['sha256'] == record['sha256'], actual
    return actual


def json_exact(a, b):
    # Separate reviewer serialization, not any target helper or target codec.
    # Exact JSON text retains bool/int/float distinctions, signed zero and order.
    return json.dumps(a, ensure_ascii=False, allow_nan=False) == json.dumps(b, ensure_ascii=False, allow_nan=False)


def funcs(data):
    text = data.decode('utf-8')
    tree = ast.parse(text)
    result = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Three distinct nested work functions have the same local name.
            # Full qualified function inventory is checked separately below.
            if node.name in result:
                assert node.name == 'work', node.name
            result[node.name] = (node, ast.get_source_segment(text, node))
    return tree, result


def qualified_functions(data):
    text = data.decode('utf-8')
    tree = ast.parse(text)
    result = {}
    def visit(node, prefix):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            prefix = prefix + (node.name,)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                key = '.'.join(prefix)
                assert key not in result, key
                result[key] = ast.get_source_segment(text, node)
        for child in ast.iter_child_nodes(node):
            visit(child, prefix)
    visit(tree, ())
    return result


manifest_path = CANDIDATE / 'public-artifacts-manifest-candidate096.json'
code_manifest_path = CANDIDATE / 'public-code-artifacts-manifest096.json'
handoff_path = CANDIDATE / 'final-handoff-candidate096.json'
manifest, code_manifest, handoff = load(manifest_path), load(code_manifest_path), load(handoff_path)
assert ref(manifest_path)['sha256'] == '0a7db453bbe170aa23b978a8b5c34ef81f07dffd3594cbe976211cab5eeaca51'
assert ref(code_manifest_path)['sha256'] == '255d95b7c7241ebc34bb85a01a543bac0f50f7d9b44ad9de7b178a4598c45c36'
verify_ref(handoff['manifest'])
verify_ref(handoff['code_manifest'])
for row in manifest['files']:
    verify_ref({'path': row['source_path'], 'bytes': row['bytes'], 'sha256': row['sha256']})
expected = {Path(row['source_path']).relative_to(CANDIDATE).as_posix() for row in manifest['files']}
expected |= {manifest_path.name, handoff_path.name}
physical = set()
for path in CANDIDATE.rglob('*'):
    if path.is_dir():
        assert not path.is_symlink(), str(path)
        continue
    assert stat.S_ISREG(path.lstat().st_mode) and not path.is_symlink(), str(path)
    physical.add(path.relative_to(CANDIDATE).as_posix())
assert physical == expected and len(expected) == 18
assert len(manifest['files']) == 16 and len(code_manifest['files']) == 5
check('S01', 'Sealed complete candidate manifest', 'All 16 payload byte counts and SHA-256 hashes match; exact regular physical set is 18 including manifest and handoff.', {'candidate_manifest': ref(manifest_path), 'code_manifest': ref(code_manifest_path), 'handoff': ref(handoff_path), 'physical_files': sorted(physical)})

guard = load(GUARD)
assert ref(GUARD)['sha256'] == '41b9f4662a31b0c8ade2cf51c019bda0a04f6569e92770249bcf2e7ebabe9eab'
assert len(guard['source_sha256_after']) == 735
current_sources = []
for rel, expected_sha in guard['source_sha256_after'].items():
    actual = ref(ROOT / rel)
    assert actual['sha256'] == expected_sha, rel
    current_sources.append({'repo_path': rel, **actual})
check('S02', 'Exact current 735-source golden binding', 'Independently read and hashed every one of the 735 declared maintained sources; zero drift. Historical runtime fields in guard are not treated as current section authority.', {'guard': ref(GUARD), 'actual_current_source_entries': 735, 'actual_source_drift': {}})

candidate_destinations = []
for row in code_manifest['files']:
    verify_ref({'path': row['source_path'], 'bytes': row['bytes'], 'sha256': row['sha256']})
    old = row['expected_old']
    destination = ROOT / row['destination_repo_path']
    if old is None:
        assert not destination.exists(), str(destination)
    else:
        verify_ref(old)
        assert destination.read_bytes() == Path(old['path']).read_bytes()
        assert old['sha256'] == guard['source_sha256_after'][row['destination_repo_path']]
    candidate_destinations.append(row['destination_repo_path'])
assert candidate_destinations == ['rouge/app.py', 'rouge/condition_cultivation.py', 'rouge/data/condition-cultivation-source.json', 'tests/test_condition_cultivation.py', 'scripts/verify_cloud.py']
check('S03', 'Exactly five proposed maintained files', 'Only two existing files have proposed insertions and three new files are proposed. Original app and registry match current guarded golden bytes; all new destinations remain absent.', {'destinations': candidate_destinations})

freeze = load(CANDIDATE / 'implementation-source-freeze096.json')
for record in (handoff['source_freeze'], handoff['gold_source_guard'], handoff['independent_raw_source_fact_review'], handoff['independent_draft_logic_source_review'], handoff['original_source_qualification']):
    verify_ref(record)
assert handoff['formal_implementation_source_gate_passed'] is None
assert handoff['runtime_pass'] is False and handoff['actual_candidate_calls'] == 0 and handoff['actual_test_calls'] == 0
assert handoff['actual_full095_prerequisite'] is None and handoff['actual_post_full095_commit_push'] is None
assert code_manifest['actual_full095_validation_receipt'] is None and code_manifest['actual_post_full095_commit_push'] is None
assert freeze['actual_full095_validation_and_post_full095_commit_push_prerequisite'] is None
assert handoff['completed_section_increment'] == 0 and handoff['actual096_completed'] is False
check('S04', 'Source-only prerequisite and status truth', 'The sealed candidate does not invent future full095 validation or commit/push receipt; those prerequisites remain null, runtime false and section increment zero. Previous draft correction is retained as source history, not target runtime failure.', {'source_freeze': ref(CANDIDATE / 'implementation-source-freeze096.json')})

ledger = load(CANDIDATE / 'exact-source-inverse096.json')
old_app = (CANDIDATE / 'baseline/rouge/app.py').read_bytes()
new_app = (CANDIDATE / 'rouge/app.py').read_bytes()
restored = new_app
assert len(ledger['app_operations']) == 3
for operation in reversed(ledger['app_operations']):
    start, count = operation['candidate_byte_start'], operation['candidate_byte_count']
    actual = restored[start:start+count]
    assert len(actual) == count and sha(actual) == operation['candidate_sha256']
    assert actual == operation['added_utf8'].encode('utf-8')
    assert base64.b64decode(operation['before_base64']) == b''
    restored = restored[:start] + restored[start+count:]
assert restored == old_app and len(old_app) == 96725 and sha(old_app) == '589b9ac2b846206581c394d037baec0d9e43a165a7bdd5becc0982ab0e09c0fd'
old_registry = (CANDIDATE / 'baseline/scripts/verify_cloud.py').read_bytes()
new_registry = (CANDIDATE / 'scripts/verify_cloud.py').read_bytes()
op = ledger['registry_operation']
assert sha(new_registry[op['candidate_byte_start']:op['candidate_byte_start']+op['candidate_byte_count']]) == op['candidate_sha256']
assert new_registry[:op['candidate_byte_start']] + base64.b64decode(op['before_base64']) + new_registry[op['candidate_byte_start']+op['candidate_byte_count']:] == old_registry
assert len(old_registry) == 5028 and sha(old_registry) == '8f5f0fd958c29e1f863651d671bf2c63a003a3604fa0eae488d9636b9adde223'
check('S05', 'Whole-byte app and registry inverse', 'Removing only the three exact declared app insertions restores the whole 96,725-byte guarded app. Removing the unique 40-byte test registry insertion restores the whole 5,028-byte guarded registry; no whitespace or newline normalization.', {'ledger': ref(CANDIDATE / 'exact-source-inverse096.json'), 'app_operation_count': 3, 'registry_operation_count': 1, 'restored_app_sha256': sha(restored), 'restored_registry_sha256': sha(old_registry)})

old_app_tree, old_functions = funcs(old_app)
new_app_tree, new_functions = funcs(new_app)
assert len(old_functions) == 61 and len(new_functions) == 62
changed = [name for name, (_, text) in old_functions.items() if new_functions[name][1] != text]
assert changed == ['make_damage_tab', 'update_skill_options'], changed
assert set(new_functions) - set(old_functions) == {'update_condition_cultivation_explanations'}
unchanged = sorted(set(old_functions) - set(changed))
old_qualified = qualified_functions(old_app)
new_qualified = qualified_functions(new_app)
assert len(old_qualified) == 63 and len(new_qualified) == 64
qualified_changed = [key for key, source in old_qualified.items() if new_qualified[key] != source]
assert qualified_changed == ['MainWindow.make_damage_tab', 'MainWindow.update_skill_options']
assert set(new_qualified) - set(old_qualified) == {'MainWindow.update_condition_cultivation_explanations'}
for name in ('calculate', 'current_operator_state', 'training_conditions', 'skill_rank_value', 'update_operator', 'level_changed', 'skill_changed', 'render_damage', 'apply_operator_observation', 'apply_run_observation', 'show_observed_operator', '__init__'):
    assert name in unchanged
check('S06', 'All original numerical, state, early-return and text paths preserved', '61 of all 63 qualified original functions, including three distinct nested work functions, are byte-exact; only make_damage_tab and update_skill_options contain new presentation insertions. The complete calculate method, early returns/error handling, native/report/text path, state merge and cultivation methods remain exact. The earlier draft used 61 unique local names/59 unchanged; this full qualified inventory removes that name-collision undercount.', {'actual_original_qualified_functions': 63, 'actual_unchanged_qualified_functions': 61, 'unchanged_unique_local_names': unchanged, 'changed_original_functions': qualified_changed, 'new_functions': ['MainWindow.update_condition_cultivation_explanations'], 'calculate_source_sha256': sha(old_functions['calculate'][1].encode()), 'all_qualified_source_sha256': {key: sha(value.encode()) for key, value in old_qualified.items()}})

helper_bytes = (CANDIDATE / 'rouge/condition_cultivation.py').read_bytes()
helper_text = helper_bytes.decode()
helper_tree, helper_functions = funcs(helper_bytes)
assert list(helper_functions) == ['_source_data', '_eligible', '_typed_equal', '_original_source', '_provenance', 'explanations', 'format_explanation']
test_bytes = (CANDIDATE / 'tests/test_condition_cultivation.py').read_bytes()
test_tree = ast.parse(test_bytes)
test_methods = [n.name for n in ast.walk(test_tree) if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')]
assert len(test_methods) == 16
registry_tree = ast.parse(new_registry)
registry_addition = new_registry[op['candidate_byte_start']:op['candidate_byte_start']+op['candidate_byte_count']].decode()
assert registry_addition.count('tests.test_condition_cultivation') == 1
for name in ('rouge/app.py', 'rouge/condition_cultivation.py', 'tests/test_condition_cultivation.py', 'scripts/verify_cloud.py'):
    ast.parse((CANDIDATE / name).read_bytes(), filename=name)
check('S07', 'Complete candidate syntax and test registry', 'All four candidate Python files parse as AST without import or execution. The existing registry gains exactly one unique condition-cultivation test module; all 16 meaningful boundary test methods are source-read, with no test pass inferred.', {'test_methods_written': test_methods, 'test_methods_executed': 0, 'registry_insertion': registry_addition})

raw_audit = load(handoff['independent_raw_source_fact_review']['path'])
qualification = load(handoff['original_source_qualification']['path'])
data_path = CANDIDATE / 'rouge/data/condition-cultivation-source.json'
data = load(data_path)
originals = {}
original_refs = []
for item in raw_audit['fixed_originals']:
    original_refs.append(verify_ref(item))
    originals[item['table']] = load(item['path'])
assert len(originals) == 4
assert data['source']['commit'] == 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
for record in data['source']['originals']:
    original = next(r for r in raw_audit['fixed_originals'] if r['table'] == record['table'])
    for key in ('bytes', 'sha256', 'pinned_url', 'commit'):
        assert record[key] == original[key]
catalog = load(ROOT / 'rouge/data/catalog.json')
options_tree = ast.parse((ROOT / 'rouge/operator_options.py').read_bytes())
options = ast.literal_eval(next(n.value for n in options_tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'OPTIONS' for t in n.targets)))
check('S08', 'Actual pinned originals and producer catalog', 'Rehashed all four actual original tables and read their complete JSON, plus current golden catalog and literal OPTIONS. Source commit, table identities, URLs, bytes and hashes match the candidate provenance; no network fetch, source module import or mechanism invention.', {'originals': original_refs, 'catalog': ref(ROOT / 'rouge/data/catalog.json'), 'OPTIONS': ref(ROOT / 'rouge/operator_options.py')})

field_records = []
named = set()
base_candidates = 0
module_count = 0
phase_count = 0
module_comparisons = []
for owner, source in data['operators'].items():
    raw = originals['character_table'][owner]
    profile = catalog['operators'][owner]
    assert source['name'] == raw['name'] == profile['name']
    assert json_exact(source['raw_character_talents'], raw['talents']), owner
    expected_fields = [entry for entry in options[owner] if entry[0] in ('three_professions', 'three_same_profession', 'four_sui', 'low_cost_healing_target', 'near_previous_deployment', 'power_coating', 'stolen_enemy_count', 'enemy_below_half', 'current_hp_ratio')]
    assert [r['field'] for r in source['fields']] == [e[0] for e in expected_fields]
    for row, option in zip(source['fields'], expected_fields):
        assert row['label'] == option[1] and row['skills'] == list(option[4])
        qualified = next(q for q in qualification['field_consumer_qualification'] if q['operator'] == owner and q['field'] == row['field'])
        assert row['talent_name'] == qualified['actual_named_consumer']
        assert json_exact(row['first_original_gate'], qualified['first_original_gate'])
        raw_candidates = raw['talents'][row['talent_index']]['candidates']
        assert all(r['name'] == row['talent_name'] for r in raw_candidates)
        first = raw_candidates[0]
        assert row['first_original_gate'] == {'elite': int(first['unlockCondition']['phase'][-1]), 'level': first['unlockCondition']['level'], 'potential_one_based': first['requiredPotentialRank']+1}
        named.add((owner, row['talent_index']))
        field_records.append({'owner': owner, 'field': row['field'], 'talent_index': row['talent_index'], 'talent_name': row['talent_name'], 'skills': row['skills'], 'first_original_gate': row['first_original_gate']})
    assert list(source['modules']) == [m['id'] for m in profile['modules']]
    for mid, module in source['modules'].items():
        assert json_exact(module['raw_metadata'], originals['uniequip_table']['equipDict'][mid]), mid
        assert json_exact(module['raw_phases'], originals['battle_equip_table'][mid]['phases']), mid
        assert module['raw_metadata']['charId'] == owner
        maintained = next(m for m in profile['modules'] if m['id'] == mid)
        assert maintained['name'] == module['raw_metadata']['uniEquipName']
        assert maintained['unlock_elite'] == int(module['raw_metadata']['unlockEvolvePhase'][-1])
        assert maintained['unlock_level'] == module['raw_metadata']['unlockLevel']
        assert len(maintained['levels']) == len(module['raw_phases']) == 3
        for stage, (level, phase) in enumerate(zip(maintained['levels'], module['raw_phases']), 1):
            assert level['level'] == phase['equipLevel'] == stage
            assert json_exact(level['parts'], phase['parts'])
            assert json_exact(level['attributes'], {b['key']: b['value'] for b in phase['attributeBlackboard']})
            phase_count += 1
        module_comparisons.append({'owner': owner, 'module_id': mid, 'phases': 3, 'unlock_elite': maintained['unlock_elite'], 'unlock_level': maintained['unlock_level']})
        module_count += 1
for owner, index in sorted(named):
    raw_candidates = originals['character_table'][owner]['talents'][index]['candidates']
    normalized = catalog['operators'][owner]['talents'][index]
    assert len(raw_candidates) == len(normalized)
    for raw, maintained in zip(raw_candidates, normalized):
        expected_projection = {'phase': int(raw['unlockCondition']['phase'][-1]), 'level': raw['unlockCondition']['level'], 'potential_rank': raw['requiredPotentialRank'], 'name': raw['name'], 'description': raw['description'], 'values': {b['key']: b['value'] for b in raw['blackboard']}}
        assert json_exact(expected_projection, maintained), (owner, index)
        base_candidates += 1
assert (len(data['operators']), len(field_records), len(named), base_candidates, module_count, phase_count) == (6, 9, 7, 20, 8, 24)
check('S09', 'Complete typed and ordered original data retention', 'All six complete raw character talent-group lists, eight full raw module metadata records and all 24 complete raw phase lists equal their exact actual originals by strict serialized JSON. Hidden, negative-index, null, zero, string sidecars and dictionary/list order remain in the data; no nonzero-value filter.', {'data': ref(data_path), 'operators': 6, 'named_groups': 7, 'base_candidates': 20, 'modules': 8, 'phases': 24, 'module_gates': module_comparisons})
check('S10', 'Nine exact existing field owners and actual named consumers', 'Data fields retain the exact existing OPTIONS order, labels and skill surface; seven fixed named talent groups and all 20 normalized catalog base candidates match their pinned raw projections. First original gates are derived from actual first candidates, not global elite assumptions.', {'field_records': field_records})

typed_source = helper_functions['_typed_equal'][1]
assert 'type(left) is not type(right)' in typed_source
assert 'list(left) == list(right)' in typed_source
assert 'zip(left, right)' in typed_source
assert 'left.hex() == right.hex()' in typed_source
original_lookup = helper_functions['_original_source'][1]
assert original_lookup.count('_typed_equal(') == 3
assert 'candidate is selected' in original_lookup and "level['parts'] is parts" in original_lookup
assert "module['id'] != scenario.get('module_id')" in original_lookup
assert "if part.get('isToken')" in original_lookup
assert 'talent_index >= 0 and _eligible(candidate, profile, scenario)' in original_lookup
assert 'grouped[talent_index] = (part_index, candidate_index, candidate)' in original_lookup
assert 'replacement = grouped[index]' in original_lookup
check('S11', 'Native JSON scalar types, float representation and order', 'Source comparator checks exact Python type before equality, ordered dictionary keys and list positions, then float.hex. All three base projection, selected module projection and full original module candidate comparisons use it. Bool False/int0/float0.0/-0.0 cannot conflate; reviewer did not call the comparator or any target codec.', {'helper_function': '_typed_equal', 'line': helper_functions['_typed_equal'][0].lineno, 'function_sha256': sha(typed_source.encode()), 'typed_source_comparison_sites': 3})
check('S12', 'Base and module provenance use actual producer identities', 'Base lookup requires selected object identity at a fixed talent index and exact raw-to-catalog projection. Module lookup first maps returned parts by container identity to its real stage, then traverses parts/candidates in order, skips tokens and negative indices, retains last eligible per index and sequential overwrites. Final selected and complete raw candidate must both match; mismatch becomes missing source, without changing selection.', {'lookup_line': helper_functions['_original_source'][0].lineno, 'function_sha256': sha(original_lookup.encode())})

eligibility = helper_functions['_eligible'][1]
assert "scenario.get('elite', 2)" in eligibility
assert "scenario.get('level') or profile['phases'][elite]['max_level']" in eligibility
assert "candidate.get('requiredPotentialRank', candidate.get('potential_rank', 0))" in eligibility
assert 'phase <= elite and (phase < elite or minimum <= level)' in eligibility
assert "rank <= scenario.get('potential', 1) - 1" in eligibility
check('S13', 'Existing selector predicate and module gate retained', 'Presentation source locator copies the original selector phase/level/potential predicate. Actual selected_talents determines eligibility and returned parts; therefore a module below its own gate retains a selected base talent and does not become unavailable. No source locator supplies a new numeric predicate.', {'gold_selector': ref(ROOT / 'rouge/operator_engine.py'), 'presentation_eligible_function_sha256': sha(eligibility.encode())})

explain = helper_functions['explanations'][1]
assert "if operator not in TARGET_OPERATORS or profile is None or not skill" in explain
assert 'if not definitions' in explain and explain.index('if not definitions') < explain.index('from .operator_engine import selected_talents')
assert "matching = [talent for talent in selected if talent.get('name') == definition['talent_name']]" in explain
assert 'talent = matching[0] if len(matching) == 1 else None' in explain
assert "'unavailable' if selection_error else 'met' if talent else 'unmet'" in explain
assert "except (ValueError, TypeError, KeyError, IndexError) as error" in explain
assert "'new_arithmetic_applied': False" in explain
check('S14', 'Zero selected parameters and natural/exception branches', 'Eligibility is based on one actual selected named talent, not any parameter magnitude or raw-source availability. A selected zero-valued candidate remains met. Placeholder/unrelated/no-skill/no-applicable-definition paths return before selector calls; supported presentation selector errors produce unavailable rows without rewriting the caller or original numerical method/error path.', {'function': 'explanations', 'line': helper_functions['explanations'][0].lineno, 'function_sha256': sha(explain.encode())})

provenance = helper_functions['_provenance'][1]
assert "state.get('scope') == 'run'" in provenance
assert "key == 'level' and level_override" in provenance
assert "'preview_unconfirmed' if key not in fields" in provenance
assert "'run_confirmed' if key in confirmed else 'account_reference'" in provenance
assert 'deepcopy(state)' not in helper_text and 'deepcopy(scenario)' not in helper_text
assert 'deepcopy(talent)' in explain and 'deepcopy(definition[\'first_original_gate\'])' in explain
check('S15', 'Existing per-field run/account/preview provenance', 'Helper reads the already merged public state and only named cultivation keys. Run-confirmed fields, present account reference fields, absent preview fields and manual level override are separately labelled. Existing training_conditions/current_operator_state and precedence are unchanged; unknown/private/caller history is not copied.', {'provenance_sha256': sha(provenance.encode())})

new_method_node, new_method = new_functions['update_condition_cultivation_explanations']
assert "if not hasattr(self,'condition_cultivation_explanation'):return" in new_method
assert "if op not in TARGET_OPERATORS or not skill:return" in new_method
assert "profile=catalog()['operators'].get(op)" in new_method
assert 'if profile is None:return' in new_method
assert "self.training_conditions()" in new_method and 'state=self.current_operator_state()' in new_method
assert 'level_override=self.level_override' in new_method
assert "widget.isChecked() if isinstance(widget,QCheckBox) else widget.value()" in new_method
assert not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'calculate' for n in ast.walk(new_method_node))
assert "owner==op and skill in skills and key in text" in new_method
check('S16', 'Safe actual UI construction and current input reads', 'New explanation method guards early construction before the row exists, then owner/skill/profile placeholders before training or selector reads. Actual UI passes existing effective training and public merged state, reads bool/numeric widget values without writes, clears the new row for unrelated contexts and changes only its own QLabel/rows plus applicable tooltips.', {'line': new_method_node.lineno, 'function_sha256': sha(new_method.encode()), 'calculate_calls': 0})

addition0 = ledger['app_operations'][0]['added_utf8']
assert addition0.index('self.condition_cultivation_explanation=QLabel') < addition0.index('signal.connect(')
assert "if owner not in TARGET_OPERATORS or key not in TARGET_FIELDS:continue" in addition0
assert 'lambda _value:self.update_condition_cultivation_explanations' in addition0
assert "self.operator.currentData(),self.skill.currentData()" in addition0
assert sum(1 for owner, entries in options.items() for e in entries if owner in data['operators'] and e[0] in {r['field'] for o in data['operators'].values() for r in o['fields']}) == 9
check('S17', 'Nine extra presentation listeners preserve existing numeric signals', 'All old option setup and calculate listeners remain byte-exact. Exactly nine owner+field widgets receive an additional listener after the new row is fully constructed; each reads the current owner/skill and refreshes only presentation. No late-bound owner/key is used by the lambda. Original automatic numerical calls retain their existing listener and method.', {'actual_source_target_widgets': 9, 'insertion_sha256': ledger['app_operations'][0]['candidate_sha256']})

update_method = new_functions['update_skill_options'][1]
assert update_method.index('self.update_condition_cultivation_explanations(op,skill)') > update_method.index('for owner,key,skills,widget in self.model_option_widgets:')
assert old_functions['level_changed'][1] == new_functions['level_changed'][1]
assert old_functions['skill_changed'][1] == new_functions['skill_changed'][1]
assert 'self.update_skill_options()' in new_functions['update_operator'][1]
assert 'self.update_skill_options()' in new_functions['level_changed'][1]
assert 'self.update_skill_options()' in new_functions['skill_changed'][1]
check('S18', 'Owner, skill, cultivation, module and nine value refresh ordering', 'The existing update_operator, observation flows, level_changed and skill_changed already call update_skill_options; the new refresh is inserted after existing owner/skill visibility and before unchanged calculation. Existing cultivation/state updates therefore refresh explanations, and nine extra presentation slots close the earlier declared-value stale-text source gap.', {'changed_existing_refresh_method': 'update_skill_options', 'approved_insertion_bytes': 66, 'original_training_refresh_methods_exact': True})

format_node = helper_functions['format_explanation'][0]
helper_newlines = [{'line': n.lineno, 'repr': repr(n.value), 'unicode_codepoints': [ord(ch) for ch in n.value[:2]]} for n in ast.walk(format_node) if isinstance(n, ast.Constant) and isinstance(n.value, str) and '\n' in n.value]
app_newlines = [n.value for n in ast.walk(new_method_node) if isinstance(n, ast.Constant) and isinstance(n.value, str) and '\n' in n.value]
assert '\n\n' in app_newlines
assert len(helper_newlines) == 2
assert not any(isinstance(n, ast.Constant) and isinstance(n.value, str) and '\\n' in n.value for n in ast.walk(format_node))
check('S19', 'Actual line breaks, clear named field text and plain UI source scope', 'AST Constant.value confirms actual LF characters in formatter and double-LF QLabel join, not visible backslash-n. Text names each condition/talent, current declared input and per-field cultivation source. No raw markup/hash/URL is rendered; account task unlock, actual trigger and native attachment remain unverified.', {'formatter_actual_newline_constants': helper_newlines, 'app_join_repr': repr('\n\n'), 'withdrawn_initial_display_escaping_suspicion': True, 'author_source_failure_or_runtime_failure': False})

check('S20', 'Specific mechanisms remain correctly bounded', 'Source notes retain Orchd E0 power versus E1 nearby and non-normal arrow scope, Ines count parsing even without own selected multiplier, Hsgma independent ratio parsing/reference and existing modeled keys, Mizuki second named talent distinct from hidden first-talent attachment, Shu unresolved SP clocks. No blanket hide/disable, consumer invention or new arithmetic.', {'scope_notes': [{'owner': owner, 'field': row['field'], 'modeled_parameter_keys': row['modeled_parameter_keys'], 'scope_note': row['scope_note']} for owner, source in data['operators'].items() for row in source['fields']]})

for key in ('account_unlock_verified', 'actual_activation', 'native_attachment'):
    assert repr(key) + ': None' in explain
assert freeze['report_or_numeric_public_keys_added'] == [] and freeze['report_sections_added'] == [] and freeze['three_text_insertions'] == []
helper_calls = [ast.unparse(n.func) for n in ast.walk(helper_tree) if isinstance(n, ast.Call)]
assert not any('.write_' in n or '.save' in n or n in ('calculate_damage', 'Combat', 'calculate') for n in helper_calls)
check('S21', 'No new public report/native/numerical or persistence contract', 'Candidate adds no result/report public keys, report sections or three-text insertions. Helper contains no numerical API, write/save, run/account mutation or network call; new UI selector use is presentation only. Full native/API/report/text invariance remains a required later runtime comparison, not a source proof of target execution.', {'added_report_keys': [], 'added_sections': [], 'added_text_insertions': [], 'runtime_native_equality_claim': False})

check('S22', 'Written boundary tests match actual source facts', 'Source-read 16 tests cover all nine owner/skill surfaces, placeholders, Orchd E0/E1, Susuro P4/P5, all 8 modules x 3 stages before gate, exact overlay part/index/candidate order, Mizuki other-module distinction, selected zero values, False/int0/-0.0 source mismatch, independent Ines/Hsgma input semantics, run/account/manual preview, detached rows, opaque state, supported selector exceptions and explicit unknowns. Test methods are not executed and declaration assertions are not substituted for native equivalence.', {'methods': test_methods, 'test_runtime_pass': False, 'later_required_full_native_three_text_and_UI_counts': True})

acceptance = load(CANDIDATE / 'runtime-acceptance-plan096.json')
assert acceptance['actual_full095_validation_and_commit_push_prerequisite'] is None
assert acceptance['actual_tests_run'] == 0 and acceptance['candidate_APIs_run'] == 0 and acceptance['actual_096_completed'] is False
assert len(acceptance['Linux_groups']) == 3 and len(acceptance['root_actual_MainWindow_groups']) == 4
assert all(row['actual'] is None for row in acceptance['Linux_groups'] + acceptance['root_actual_MainWindow_groups'])
check('S23', 'Concrete later validation remains pending', 'Plan requires actual isolated source tests, full typed/aliased gold API/native/report/all-three-text pairs, relevant regressions, real-window construction/placeholders/nine value refreshes/cultivation provenance and durable state. All observations remain null; root must bind actual full095 and commit/push before application. This source review grants neither runtime PASS nor section completion.', {'acceptance_plan': ref(CANDIDATE / 'runtime-acceptance-plan096.json')})

function_bindings = [{'file': 'rouge/condition_cultivation.py', 'function': name, 'line': node.lineno, 'end_line': node.end_lineno, 'source_sha256': sha(text.encode())} for name, (node, text) in helper_functions.items()]
function_bindings += [{'file': 'rouge/app.py', 'function': name, 'line': new_functions[name][0].lineno, 'end_line': new_functions[name][0].end_lineno, 'source_sha256': sha(new_functions[name][1].encode())} for name in ('make_damage_tab', 'update_skill_options', 'update_condition_cultivation_explanations', 'calculate', 'training_conditions', 'current_operator_state')]
result = {
    'format_version': 1,
    'status': 'PASS_FORMAL_INDEPENDENT_IMPLEMENTATION_SOURCE_ONLY096_NOT_EXECUTED',
    'source_gate_passed': True,
    'runtime_pass': False,
    'code_manifest_sha256': ref(code_manifest_path)['sha256'],
    'guard_sha256': ref(GUARD)['sha256'],
    'app_inverse_sha256': ref(CANDIDATE / 'exact-source-inverse096.json')['sha256'],
    'app_wholebyte_inverse_exact': True,
    'registry_wholebyte_inverse_exact': True,
    'candidate_manifest': ref(manifest_path),
    'candidate_handoff': ref(handoff_path),
    'code_manifest': ref(code_manifest_path),
    'guard': ref(GUARD),
    'source_freeze': ref(CANDIDATE / 'implementation-source-freeze096.json'),
    'independent_raw_source_fact_review': handoff['independent_raw_source_fact_review'],
    'independent_draft_source_review': handoff['independent_draft_logic_source_review'],
    'actual_current_guard_sources_verified': 735,
    'actual_source_drift': {},
    'checks': CHECKS,
    'source_check_count': len(CHECKS),
    'source_checks_passed': len(CHECKS),
    'source_checks_blocked': 0,
    'blocking_findings': [],
    'function_source_bindings': function_bindings,
    'reviewer_source_diagnostics_preserved': [
        {'kind': 'READ_ONLY_SEARCH_PATH_ERROR', 'tool_primary_exit_code': 2, 'missing_path': '/workspace/rougezhushou/rouge/operator_profiles.py', 'resolved_fact': 'operator_profiles is defined in guarded rouge/catalog.py; actual producer file read. No candidate execution or author failure.'},
        {'kind': 'WITHDRAWN_INITIAL_JSON_DISPLAY_ESCAPING_SUSPICION', 'initial_suspicion': 'Tool output JSON escaping made actual LF source strings appear as double-backslash strings.', 'correction': 'Independent AST Constant.value and ord confirm LF (10) and two LF (10,10); no literal backslash-n in formatter. Root was informed before this gate. Not an author SOURCE failure or runtime attempt.'},
    ],
    'review_execution': {'stdlib_AST_JSON_sha256_bytes_only': True, 'candidate_helpers_selector_codecs_project_imports': 0, 'numerical_APIs_tests_Qt_Wine_game_chat': 0, 'Git_network_private_state_reads': 0, 'tracked_repository_writes': 0, 'writes': 'Only this fresh independent external review directory.'},
    'actual_full095_validation_receipt': None,
    'actual_post_full095_commit_push': None,
    'actual_candidate_runtime_executions': 0,
    'completed_section_increment': 0,
    'actual096_completed': False,
    'required_later_validation': ['Root actual full095 available validation and normal batch commit/push binding before any apply.', 'Actual 16 new tests and appropriate related/selected regressions.', 'Complete native caller/scenario/result types, float bits, key order, aliases, report objects and all three formatted texts byte-exact to gold, no stripping.', 'Real MainWindow constructor/placeholders/nine controls/cultivation and provenance/durable states with equal original numerical API counts and qualified extra presentation selector stacks.'],
    'limitations': ['SOURCE-only gate does not establish candidate runtime success, native Windows/game behavior or unresolved mechanisms.', 'Standalone helper effective_training echoes the supplied scenario; actual UI supplies current training_conditions unchanged. No normalization or new numeric semantics are authorized.', 'Original UI/layout/widgets must still be physically observed during root window acceptance.'],
    'STOPWRITE': True,
}
report_path = OUT / 'formal-independent-source-review-condition096-v1.json'
with report_path.open('x', encoding='utf-8') as handle:
    json.dump(result, handle, ensure_ascii=False, indent=2)
    handle.write('\n')
print(json.dumps({'source_gate_passed': True, 'runtime_pass': False, 'source_checks': len(CHECKS), 'report': ref(report_path)}, ensure_ascii=False))
