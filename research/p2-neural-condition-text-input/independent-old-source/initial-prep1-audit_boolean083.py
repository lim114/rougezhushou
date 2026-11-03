"""Bounded public counterexamples and static source review; no product mutation."""
from pathlib import Path
import copy
import hashlib
import io
import json
import subprocess
import sys
import tarfile

OUT = Path(__file__).resolve().parent
REPO = Path('/workspace/rougezhushou')
BASE = 'ea7866be6f2a8e89d382ec2982a45f1cb9231141'
GAME = 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
RIVER = 'rogue_6_relic_fight_22'

def sha(data): return hashlib.sha256(data).hexdigest()
def canon(value): return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
def save(name, value):
    with (OUT / name).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')

paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASE, 'rouge'], cwd=REPO, text=True).splitlines()
paths = [p for p in paths if p.endswith(('.py', '.json'))]
package = OUT / 'fixed-public-package'
package.mkdir()
archive = subprocess.check_output(['git', 'archive', '--format=tar', BASE, *paths], cwd=REPO)
with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
    for member in stream:
        if not member.isfile(): continue
        assert member.name in paths
        target = package / member.name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(stream.extractfile(member).read())
frozen = {p: {'bytes': (package/p).stat().st_size, 'sha256': sha((package/p).read_bytes())} for p in paths}
selected_paths = ['app.py', 'rouge/operator_options.py', 'rouge/operator_engine.py', 'rouge/damage.py',
                  'rouge/attributes.py', 'rouge/run_modifiers.py', 'rouge/enemy_environment.py',
                  'rouge/reporting.py', 'rouge/data/operator-profiles.json']
selected = []
for rel in selected_paths:
    data = subprocess.check_output(['git', 'show', f'{BASE}:{rel}'], cwd=REPO)
    target = OUT/'fixed-consumer-source'/rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    selected.append({'path': rel, 'archive_path': str(target.relative_to(OUT)), 'bytes': len(data), 'sha256': sha(data)})
raw_char = REPO/'.cache/p2-s1-binding/character_table.json'
raw_skill = REPO/'.cache/p2-s1-binding/skill_table.json'
assert sha(raw_char.read_bytes()) == '68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697'
assert sha(raw_skill.read_bytes()) == '86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca'
characters = json.loads(raw_char.read_bytes())
skills = json.loads(raw_skill.read_bytes())
ops = ['char_4204_mantra', 'char_1042_phatm2', 'char_1048_orchd2']
selected_chars = {op: characters[op] for op in ops}
selected_skills = {entry['skillId']: skills[entry['skillId']] for op in ops for entry in characters[op]['skills']}
save('original-objects083.json', {'pinned_game_commit': GAME, 'characters': selected_chars, 'skills': selected_skills,
    'raw_sources': [{'path': str(p), 'bytes': p.stat().st_size, 'sha256': sha(p.read_bytes())} for p in [raw_char, raw_skill]]})
prior = Path('/workspace/.continuation/p2-boolean-option-audit-062')
prior_names = ['NOTE.md', 'qt-contract-review.json', 'boolean-input-matrix.json', 'audit-validation.json']
prior_bindings = [{'path': str(prior/name), 'bytes': (prior/name).stat().st_size,
                   'sha256': sha((prior/name).read_bytes())} for name in prior_names]
old = json.loads((prior/'boolean-input-matrix.json').read_bytes())
assert isinstance(old['rows'], dict)
relevant_old = {k:v for k,v in old['rows'].items() if any(k.startswith(op+':') for op in ops)
                and any(':'+field in k for field in ['enemy_is_boss','enemy_in_neural_break','near_previous_deployment','double_charge'])}
save('reused062-observations083.json', {'prior_bindings': prior_bindings, 'fresh_public_calls': 0,
    'prior_is_observation_not_new_input_domain_or_native_mechanism_proof': True, 'rows': relevant_old})
save('freeze083.json', {'fixed_commit': BASE, 'pinned_game_commit': GAME, 'public_package': frozen,
    'selected_static_consumers': selected, 'planned_actual_public_calls': 8,
    'qt_source_read_only': True, 'qt_executed': False, 'wine_executed': False, 'tracked_edits': False})

sys.path.insert(0, str(package))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.reporting import format_report
from rouge.estimate import format_estimate
from rouge.operator_options import OPTIONS
before_catalog = copy.deepcopy(catalog())
option_rows = {op: [entry for entry in OPTIONS[op] if isinstance(entry[2], bool)] for op in ops}
save('qt-option-rows083.json', {'production_OPTIONS_boolean_definitions': option_rows,
    'static_binding_only_no_Qt_execution': True,
    'actual_app_builder_source': 'app.py bool default -> QCheckBox -> setChecked -> toggled calculate',
    'actual_serializer_source': 'current owner/skill QCheckBox -> isChecked() in scenario',
    'OPTIONS_is_UI_exposure_and_not_engine_consumer_scope': True})
rows = []
common = {'operator': 'char_4204_mantra', 'skill': 3, 'skill_rank': 10,
          'elite': 2, 'level': 90, 'base_attack': 1000, 'timing_mode': 'frames', 'window_seconds': 10}
requests = []
for label, value in [('false_bool', False), ('true_bool', True), ('false_text', 'false')]:
    requests.append(('mantra-s3-boss-'+label, {**common, 'enemy_is_boss': value, 'initial_neural_buildup': 1500}))
for label, value in [('false_bool', False), ('true_bool', True), ('false_text', 'false')]:
    requests.append(('mantra-s3-break-river-'+label, {**common, 'enemy_in_neural_break': value, 'relic_ids': [RIVER]}))
for label, value in [('false_bool', False), ('false_text', 'false')]:
    requests.append(('orchid-s3-near-'+label, {**common, 'operator': 'char_1048_orchd2', 'near_previous_deployment': value}))
assert len(requests) == 8
for name, scenario in requests:
    before = copy.deepcopy(scenario)
    try:
        result = calculate_damage(scenario)
    except Exception as error:
        row = {'case': name, 'scenario': scenario, 'error': {'type': type(error).__name__, 'message': str(error)},
               'actual_calculate_damage_calls': 1}
    else:
        row = {'case': name, 'scenario': scenario, 'result': result,
               'report_text': format_report(result), 'technical_report_text': format_report(result, technical=True),
               'estimate_text': format_estimate(result), 'actual_calculate_damage_calls': 1}
    row['caller_input_preserved'] = scenario == before
    save('public-'+name+'.json', row)
    rows.append(row)
save('public-counterexamples083.json', {'actual_public_calls': len(rows), 'rows': rows})
assert all(row['caller_input_preserved'] for row in rows)
assert catalog() == before_catalog
assert rows[0]['error']['type'] == 'ValueError'
assert 'result' in rows[1] and 'result' in rows[2]
assert canon(rows[1]['result']) == canon(rows[2]['result'])
assert 'result' in rows[3] and 'result' in rows[4] and 'result' in rows[5]
assert rows[3]['result']['neural_relic_reference']['preexisting_break_assumed'] is False
assert rows[4]['result']['neural_relic_reference']['preexisting_break_assumed'] is True
assert canon(rows[4]['result']) == canon(rows[5]['result'])
assert canon(rows[3]['result']) != canon(rows[5]['result'])
assert 'result' in rows[6] and 'result' in rows[7]
assert rows[6]['result']['estimate']['base_stats']['attack'] != rows[7]['result']['estimate']['base_stats']['attack']
for rel, binding in frozen.items():
    assert sha((package/rel).read_bytes()) == binding['sha256']
save('public-observation-review083.json', {
    'status': 'confirmed_narrow_consumed_text_truthiness_counterexamples', 'fixed_commit': BASE,
    'actual_public_calls': 8, 'successful_results': sum('result' in row for row in rows),
    'exact_errors': sum('error' in row for row in rows), 'caller_inputs_and_catalog_preserved': True,
    'Mantra_S3_is_actual_neural_consumer_even_without_checkbox': True,
    'boss_false_control_error': rows[0]['error'], 'boss_true_and_false_text_whole_result_identical': True,
    'River_true_and_false_text_whole_result_identical': True,
    'River_false_vs_false_text_whole_result_different': True,
    'River_false_vs_false_text_reference': [row['result']['neural_relic_reference'] for row in rows[3:6]],
    'Orchid_near_false_vs_false_text_attack': [row['result']['estimate']['base_stats']['attack'] for row in rows[6:8]],
    'guards_must_follow_actual_consumer_not_UI_OPTIONS_scope': True,
    'boss_selected_enemy_identity_override_precedes_guard': 'prepare_run -> resolve_enemy overrides enemy_is_boss from selected level_type before Combat',
    'Orchid_near_qualification': 'selected 翔虫机动 only; original E1Lv1 atk .10 / E2Lv1 atk .15',
    'Phatm2_selected_first_talent': '形为心役 already E0Lv1; no invented E1 talent gate',
    'proposal_scope': 'Only reject raw str at actual qualified consumers; preserve all old non-str values, upstream error precedence, selected-enemy override, and idle other-owner fields.',
    'unknowns_retained': ['native threshold/event-order/phase verification beyond existing model source',
                         'neural source clocks/probabilities and independent River periodic scheduling',
                         'global API bool/null/numeric domain is not authorized by these observations',
                         'Orchid actual 30s timeline and lifecycle binding unchanged'],
    'source_drift': False, 'tracked_edits': False, 'tests_executed': 0, 'Qt_executed': False, 'Wine_executed': False})
print(json.dumps({'status': 'passed', 'actual_public_calls': 8,
                  'successful_results': 7, 'exact_errors': 1, 'frozen_public_files': len(frozen),
                  'review_sha256': sha((OUT/'public-observation-review083.json').read_bytes())}, ensure_ascii=False))
