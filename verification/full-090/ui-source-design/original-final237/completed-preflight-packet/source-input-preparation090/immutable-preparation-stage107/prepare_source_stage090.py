"""Build bounded source-only090 stage; never import or call the application."""
import ast
import hashlib
import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path('/workspace/rougezhushou')
HISTORY = Path('/workspace/.continuation/p2-remaining-boolean-consumers-086-source')
COMMIT = '9ef5a469673502754db3be320a8eece9a7fd18d4'
EXPECTED = 'b6976652eb50e06909cca68490b0b9d3e11ea81fbc9a73ca87efcbb10354e306'
HERE.mkdir(parents=True, exist_ok=True)
def sha(raw):
    return hashlib.sha256(raw).hexdigest()
def write(name, value):
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')

source_names = ['rouge/app.py', 'rouge/operator_options.py', 'rouge/operator_engine.py',
                'rouge/damage.py', 'rouge/estimate.py', 'rouge/reporting.py',
                'rouge/catalog.py', 'rouge/data/catalog.json']
frozen = {}
source_rows = []
for name in source_names:
    raw = subprocess.check_output(['git', 'show', f'{COMMIT}:{name}'], cwd=REPO)
    blob = subprocess.check_output(['git', 'rev-parse', f'{COMMIT}:{name}'], cwd=REPO, text=True).strip()
    assert raw == (REPO / name).read_bytes(), name
    frozen[name] = raw
    source_rows.append({'path': name, 'bytes': len(raw), 'sha256': sha(raw), 'git_blob_object_id': blob})
    if name != 'rouge/data/catalog.json':
        target = HERE / 'source085' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
write('named-root085-source-proof090.json', {'status': 'PASS_SOURCE_ONLY_NAMED_ACTUAL085_BYTES',
    'root_commit': COMMIT, 'files': source_rows, 'catalog_full_bytes_omitted': True,
    'rebuild_recipe': 'Read git show <root_commit>:<path> without modifying bytes.',
    'application_API_calls': 0, 'production_helper_calls': 0, 'formatter_calls': 0,
    'Qt_calls': 0, 'Wine_calls': 0, 'tests_run': 0})

baseline = Path('/workspace/.compat/wine-ui-smoke-085.py').read_bytes()
assert sha(baseline) == EXPECTED and len(baseline) == 220392
(HERE / 'actual085-runner-preserved.py').write_bytes(baseline)
guard = ("if __name__ == '__main__' and True:\n"
         "    raise RuntimeError('UI090 sources and API contract remain pending; Qt execution is forbidden')\n\n")
renames = {name: name.replace('-085', '-090') for name in (
    'wine-ui-report-difference-085.json', 'wine-window-085.png', 'wine-ui-085.json',
    'wine-ui-failure-085.png', 'wine-sown-tile-control-085.png',
    'wine-movement-reference-085.png', 'wine-medical-trait-085.png')}
candidate = baseline.decode()
for old, new in renames.items():
    candidate = candidate.replace(old, new)
candidate = guard + candidate
ast.parse(candidate)
restored = candidate.removeprefix(guard)
for old, new in renames.items():
    restored = restored.replace(new, old)
assert restored.encode() == baseline
(HERE / 'wine-ui-smoke-090.py').write_text(candidate)
write('pending-runner-static-proof090.json', {'status': 'PASS_PENDING_ENTRY_GUARD_AND_EXACT_4217_BODY_INVERSE',
    'actual085_base_sha256': EXPECTED, 'actual085_preserved_checks': 4217, 'preserved_skills': 87,
    'candidate_runner_sha256': sha(candidate.encode()), 'candidate_runner_bytes': len(candidate.encode()),
    'earliest_entry_guard': True, 'entry_guard_precedes_every_import': True,
    'old4217_complete_body_exact_after_only_guard_removal_and_seven_output_suffix_inverse': True,
    'output_renames': renames, 'new_cases_wired_into_runner': 0,
    'source86_product_draft_pending': True, 'sections87_90_unknown': True,
    'ready_for_actual_execution': False, 'API_executed': False, 'Qt_executed': False, 'Wine_executed': False})

option_tree = ast.parse(frozen['rouge/operator_options.py'])
options = ast.literal_eval(next(node.value for node in option_tree.body
    if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == 'OPTIONS'
                                          for target in node.targets)))
catalog = json.loads(frozen['rouge/data/catalog.json'])['operators']
prior = json.loads((HISTORY / 'actual-qt-producer-static-closure.json').read_bytes())['options']
assert len(prior) == 12 and len({row['owner'] for row in prior}) == 8
probes_raw = (HISTORY / 'first-public-probes.jsonl').read_bytes()
probes = [json.loads(line) for line in probes_raw.decode().splitlines()]
assert len(probes) == 36
summary = json.loads((HISTORY / 'first-public-probe-summary.json').read_bytes())
assert summary['passed'] and summary['new_public_calls'] == 36
groups = {(row['operator'], row['field']): row for row in summary['groups']}
engine = frozen['rouge/operator_engine.py'].decode()
engine_lines = engine.splitlines()
engine_tree = ast.parse(engine)
field_reads = {}
for source_name in ('rouge/operator_engine.py', 'rouge/reporting.py'):
    source_text = frozen[source_name].decode()
    source_lines = source_text.splitlines()
    for node in ast.walk(ast.parse(source_text)):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'get' and node.args:
            key = node.args[0]
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                field_reads.setdefault(key.value, []).append({'path': source_name, 'line': node.lineno,
                    'source': source_lines[node.lineno - 1]})

contracts = []
projections = []
active_pairs = []
hidden_pairs = []
boundaries = {
 'reinforcement_blocks_target': 'Trait consumes the condition in all selected skills and normal plan; no reinforcement hit, position or attachment clock is inferred.',
 'enemy_below_half': 'Selected反移情 talent is E2-only; UI remains shown in E0/E1, while missing qualified talent leaves this attack source absent.',
 'frozen_at_skill_end': 'S3 nominal terminal source only. terminal_clock_verified and freeze_removal_order_verified remain false; nominal duration does not prove actual end or disappearance order.',
 'ines_first_deployment': 'S3 first-deployment branch and deployment-cost notes consume it. Shadow path collision and ownership clocks remain unknown.',
 'ranged_attack': 'All skills and normal consume it. Qualified module plus selected颂乐音符.max_cnt>10 overrides skill scale only; normal contribution to public output additionally requires calculate cycle/continuous gates.',
 'organ_mode': 'S2 switches source attack/attack speed and damage type. Normal and S1/S3 do not consume this switch; native note collisions remain unknown.',
 'fever': 'S2 doubles the described hits only. S3 native Fever leave-alive description is not this modeled consumer.',
 'power_coating': 'Actual selected强击瓶专家 exists from E0. Skill plans consume its multiplier, normal scale stays1; no per-arrow bottle history is inferred.',
 'double_charge': 'S1 consumes extra arrows plus initial/recharge and event-SP cost. Conditional rows do not prove arrow time or complete cast end.',
 'steal_success': 'S2 consumes source speed/ammo parameters. No actual ally steal recipient or native ammunition depletion is inferred.',
 'delivery_coordinate': 'S3 conditional external source; actual coordinate acquisition/collision remains unknown and source-derived None is preserved.',
 'overload': 'S2 consumes four-hit scale; actual hit times, random targeting, remnants and summons remain separate unresolved sources.'}
required_paths = ['attack', 'total_damage', 'total_healing', 'components', 'estimate', 'report']
for row in prior:
    owner, key = row['owner'], row['field']
    option = next(entry for entry in options[owner] if entry[0] == key)
    assert type(option[2]) is bool and list(option[4]) == row['skills']
    profile = catalog[owner]
    matches = [probe for probe in probes if probe['input']['operator'] == owner and key in probe['input']]
    assert len(matches) == 3
    legal = [probe for probe in matches if type(probe['input'][key]) is bool]
    assert {probe['input'][key] for probe in legal} == {False, True}
    skill = legal[0]['input']['skill']
    assert skill in option[4]
    for probe in legal:
        assert all(name in probe['result'] for name in required_paths)
        result = probe['result']
        special = {name: value for name, value in result.items()
                   if name.endswith('_reference') and name not in ('attack_speed_reference', 'base_attack_speed_reference')}
        projections.append({'historical_index': probe['index'], 'owner': owner, 'field': key,
            'bool_value': probe['input'][key], 'input': probe['input'],
            'full_saved_result_sha256': sha(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()),
            'required_result_keys': required_paths,
            'required_key_types': {name: type(result[name]).__name__ for name in required_paths},
            'estimate_skill_key_types': {name: type(value).__name__ for name, value in result['estimate']['skill'].items()},
            'exact_source_references': special,
            'saved_three_report_sha256': {name: sha(value.encode()) for name, value in probe['reports'].items()}})
    field_contract = {**row, 'widget_class': 'QCheckBox', 'actual_serialized_type': 'bool',
        'display_and_serialization_condition': 'owner==selected operator and selected skill in declared skills',
        'hidden_or_other_owner_key_omitted': True,
        'skill_unlock_elite': {str(index + 1): record['unlock_elite']
                               for index, record in enumerate(profile['skills'])},
        'current_consumer_source': field_reads[key], 'boundary': boundaries[key],
        'required_result_keys_checked_from_existing_saved_legal_pairs': required_paths,
        'historical_qualified_bool_results_differ': groups[(owner, key)]['bool_values_differ'],
        'old_source36_evidence_commit': summary['base_commit'],
        'current_new_API_verification_pending': True}
    contracts.append(field_contract)
    fields = {'elite': 2, 'level': profile['phases'][2]['max_level'], 'potential': 1,
              'trust': 100, 'module_id': None, 'module_level': 0}
    defaults = {entry[0]: entry[2] for entry in options[owner] if skill in entry[4]}
    active_pairs.append({'id': 'active:' + owner + ':' + key, 'field': key,
        'owner': owner, 'skill': skill, 'skill_rank': 10, 'training_fields': fields,
        'option_defaults_before_toggle': defaults, 'states': [False, True],
        'timing_mode': 'frames', 'bounded_window_seconds': 30,
        'source_effect_relation': 'qualified conditional source differs; nullable totals and native clocks retain their exact source-derived boundaries',
        'base_attack_source': 'Read-only MainWindow cultivation value; do not copy historical API manual base_attack1000 into a fake Qt control.',
        'expected_actual_UI_or_API_result': 'PENDING_FUTURE_AUTHORIZED_VERIFICATION'})
    omitted = [index + 1 for index, item in enumerate(profile['skills'])
               if index + 1 not in option[4] and item['unlock_elite'] <= 2]
    if omitted:
        hidden_pairs.append({'id': 'hidden:' + owner + ':' + key, 'owner': owner, 'field': key,
            'skill': omitted[0], 'skill_rank': 10, 'training_fields': fields,
            'hidden_widget_checked_states': [False, True], 'requested_scenario_key': 'OMITTED',
            'expected_relation': 'Identical serialized scenario for this field; never add a hidden key merely to force an API behavior.',
            'expected_actual_UI_or_API_result': 'PENDING_FUTURE_AUTHORIZED_VERIFICATION'})
assert len(contracts) == 12 and sum(len(row['current_consumer_source']) for row in contracts) == 17
assert len(active_pairs) == 12 and len(hidden_pairs) == 8
write('source-producer-contracts090.json', {'status': 'SOURCE_ONLY_CURRENT085_PRODUCER_CONTRACTS',
    'root_commit': COMMIT, 'authorized_section': 86, 'source86_final': False,
    'sections87_90_known': False, 'owners': 8, 'fields': 12, 'direct_literal_consumers': 17,
    'shared_producer_source_ranges': {'construction': 'rouge/app.py:661-677',
        'display': 'rouge/app.py:968-969', 'serialization': 'rouge/app.py:1035-1037',
        'readonly_cultivation': 'rouge/app.py:768-835', 'skill_and_module_gates': 'rouge/operator_engine.py:24-107'},
    'options': contracts, 'application_API_calls': 0, 'production_helper_calls': 0,
    'formatter_calls': 0, 'Qt_calls': 0, 'Wine_calls': 0, 'tests_run': 0})
write('historical-saved36-field-projection090.json', {'scope': 'Read-only24 legal bool rows projected from existing oldsource36 evidence; not current fresh API pass',
    'historical_source_commit': summary['base_commit'], 'source36_file': str(HISTORY / 'first-public-probes.jsonl'),
    'source36_file_sha256': sha(probes_raw), 'all_original_records': 36,
    'projected_legal_bool_records': len(projections), 'new_API_calls': 0,
    'new_formatter_calls': 0, 'records': projections})
special_pairs = [
    {'id': 'qualification:mizuki-E1', 'owner': 'char_437_mizuki', 'field': 'enemy_below_half',
     'skill': 2, 'skill_rank': 7, 'training_fields': {'elite': 1, 'level': 1, 'potential': 1,
         'trust': 100, 'module_id': None, 'module_level': 0}, 'states': [False, True],
     'source_relation': 'Visible real checkbox; E2反移情 is absent at E1, so this attack source is not added.',
     'expected_actual_UI_or_API_result': 'PENDING_FUTURE_AUTHORIZED_VERIFICATION'},
    {'id': 'coveredmodule:oblvns-ranged-skill-vs-normal', 'owner': 'char_4182_oblvns', 'field': 'ranged_attack',
     'skill': 3, 'skill_rank': 10, 'training_fields': {'elite': 2, 'level': 60, 'potential': 1,
         'trust': 100, 'module_id': 'uniequip_002_oblvns', 'module_level': 3}, 'states': [False, True],
     'source_relation': 'Qualifiedselected颂乐音符.max_cnt12 overrides skill ratio1 for both flags; normal plan still .8/1. Do not assert whole API inactive or invent an actually executed normal phase.',
     'public_normal_phase_gate_source': 'operator_engine.calculate: cycle is not None and excludes INCREASE_WHEN_ATTACK without continuous_attacks',
     'expected_actual_UI_or_API_result': 'PENDING_FUTURE_AUTHORIZED_VERIFICATION'}]
write('small-explicit-pair-plan090.json', {'status': 'PURE_DECLARATIVE_PENDING_STAGE_ONLY',
    'source86_product_final': False, 'later_sections87_90_unknown': True,
    'active_pairs': active_pairs, 'qualification_and_coveredmodule_pairs': special_pairs,
    'hidden_key_omission_pairs': hidden_pairs, 'pair_groups': 22, 'planned_UI_states': 44,
    'case_states_wired_into_runner': 0, 'application_API_calls': 0, 'production_helper_calls': 0,
    'formatter_calls': 0, 'Qt_calls': 0, 'Wine_calls': 0, 'tests_run': 0})
write('preparation-diagnostics090.json', {'scope': 'Static file-discovery/reader preparation only; no product imports or calls',
    'diagnostics': [
        {'error': 'cat: source/handoff.json: No such file or directory', 'correction': 'Read actual source-handoff.json identified by rg; old sealed source unchanged.', 'attempts': 1},
        {'error': 'SyntaxError: type(v).__name__for', 'correction': 'Inserted missing space in one inline read-only summary; no API started.', 'attempts': 1},
        {'error': "KeyError: 'parts'", 'correction': 'Read full actual catalog module object first: parts are nested under levels; no module semantic audit or helper executed.', 'attempts': 1}],
    'product_failures': 0, 'application_API_calls': 0, 'production_helper_calls': 0,
    'formatter_calls': 0, 'Qt_calls': 0, 'Wine_calls': 0})
print(json.dumps({'root_commit': COMMIT, 'fields': 12, 'owners': 8, 'consumers': 17,
    'explicit_pair_groups': 22, 'planned_states': 44, 'new_cases_wired': 0,
    'pending_runner_sha256': sha(candidate.encode()), 'new_product_calls': 0}, ensure_ascii=False))
