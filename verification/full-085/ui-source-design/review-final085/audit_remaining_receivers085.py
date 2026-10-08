"""Read saved results and AST/JSON only; never import the application package."""
import ast
from collections import Counter
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUTHOR = HERE.parent
SOURCE = AUTHOR / 'public-schema-085'
ROOT = '2dfd9fa2c9a62db0112bc0fb98cd23123dd3b48b'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)

def save(name, data):
    raw = (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode()
    (HERE / name).write_bytes(raw)
    return sha(raw)

freeze = json.loads((AUTHOR / 'public-source-freeze-085.json').read_bytes())
assert freeze['base_commit'] == ROOT and not freeze['patches']
original_static = json.loads((HERE / 'initial-static-review085.json').read_bytes())
assert original_static['approved_root_commit'] == ROOT
source_bindings = []
for name in ('operator_engine.py', 'enemy_environment.py', 'damage.py', 'reporting.py',
             'uncertain_sources.py', 'haruka_healing_reference.py', 'river_effects.py',
             'catalog.py', 'operator_options.py', 'data/catalog.json', 'data/previews.json'):
    relative = 'rouge/' + name
    raw = (SOURCE / relative).read_bytes()
    expected = original_static['source723_hashes'][relative]
    assert expected == {'bytes': len(raw), 'sha256': sha(raw)}
    assert freeze['source_sha256'][relative] == sha(raw)
    destination = HERE / 'remaining-source-snapshot' / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(raw)
    source_bindings.append({'source_path': str(SOURCE / relative),
        'archive_path': str(destination.relative_to(HERE)), 'bytes': len(raw), 'sha256': sha(raw)})

texts = {name: (SOURCE / 'rouge' / name).read_text() for name in
    ('operator_engine.py', 'enemy_environment.py', 'reporting.py', 'uncertain_sources.py',
     'haruka_healing_reference.py')}
engine = texts['operator_engine.py']
assert "enemy={**target,'name':record['name']" in texts['enemy_environment.py']
assert "scenario['enemy_is_boss']=record['level_type']=='BOSS'" in texts['enemy_environment.py']
assert "'periodic_damage_scheduled':False" in engine
assert "'preexisting_break_assumed':bool(self.s.get('enemy_in_neural_break'))" in engine
assert "'window_reference':shown['external_event_reference'],'actual_event_times_seconds':None" in engine
assert "'window_reference':shown['haruka_healing_reference']" in engine
assert "'actual_hit_times_seconds':None,'actual_end_seconds':None" in engine
assert "'actual_retreat_seconds':None,'actual_defeat_seconds':None" in engine
assert "'actual_next_deployment_seconds':None,'events_scheduled':False" in engine
assert "'observation_seconds':window,'collision_clock_verified':False" in texts['uncertain_sources.py']
assert "section('river_neural'" in texts['reporting.py']
assert "metric('first_tick','额外持续伤害首跳时刻',None,'秒')" in texts['reporting.py']

helper_raw = (AUTHOR / 'public_contracts.py').read_bytes()
(HERE / 'remaining-contracts-snapshot085.py').write_bytes(helper_raw)
tree = ast.parse(helper_raw)
functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
assert all(not any(isinstance(node, (ast.Import, ast.ImportFrom)) for node in ast.walk(fn))
           for fn in functions)
namespace = {'json': json}
exec(compile(ast.Module(body=functions, type_ignores=[]), '<saved-only-assertions>', 'exec'), namespace)
inventory = {fn.name: sorted({ast.unparse(node) for node in ast.walk(fn)
    if isinstance(node, ast.Subscript)}) for fn in functions}
cases = json.loads((HERE / 'initial-pure-cases085.json').read_bytes())
catalog = json.loads((SOURCE / 'rouge/data/catalog.json').read_bytes())
options_tree = ast.parse((SOURCE / 'rouge/operator_options.py').read_bytes())
options = next(ast.literal_eval(n.value) for n in options_tree.body if isinstance(n, ast.Assign)
    and any(isinstance(t, ast.Name) and t.id == 'OPTIONS' for t in n.targets))

def prepare(case):
    requested = case['input']
    result = {key: default for key, label, default, maximum, numbers
        in options.get(requested['operator'], []) if requested['skill'] in numbers}
    result.update(requested)
    return result

def independent_json_factor(args, name, key, absent):
    """Project these two named source candidates without invoking selected_talents."""
    profile = catalog['operators'][args['operator']]
    elite, level, rank = args['elite'], args['level'], args['potential'] - 1
    def eligible(candidate):
        condition = candidate.get('unlockCondition')
        phase = int(condition['phase'][-1]) if condition else candidate['phase']
        minimum = condition['level'] if condition else candidate['level']
        potential = candidate.get('requiredPotentialRank', candidate.get('potential_rank', 0))
        return phase <= elite and (phase < elite or minimum <= level) and potential <= rank
    selected = {}
    for index, candidates in enumerate(profile['talents']):
        eligible_rows = [row for row in candidates if eligible(row)]
        if eligible_rows:
            row = eligible_rows[-1]
            selected[index] = (row['name'], row['values'])
    module = next((row for row in profile['modules'] if row['id'] == args['module_id']), None)
    if module and elite >= module['unlock_elite'] and level >= module['unlock_level']:
        for part in module['levels'][args['module_level'] - 1]['parts']:
            if part.get('isToken'):
                continue
            for row in (part.get('addOrOverrideTalentDataBundle') or {}).get('candidates') or []:
                if row['talentIndex'] >= 0 and eligible(row):
                    selected[row['talentIndex']] = (row['name'], {b['key']: b['value'] for b in row['blackboard']})
    return next((values[key] for label, values in selected.values() if label == name), absent)

failure_path = AUTHOR / 'public-schema-resume085-failure.json.gz'
raw = failure_path.read_bytes()
assert sha(raw) == 'e64c99c83dff40e262ee616ca7b50cb54945c26674e24b1dafb903d107e0f7f8'
(HERE / 'initial-enemy-identity-counterexample085.json.gz').write_bytes(raw)
saved = json.loads(gzip.decompress(raw))
assert saved['fresh_public_calls_in_resume'] == 512
assert saved['previous_saved_public_calls'] == 69
assert saved['completed_asserted_cases'] == len(saved['completed_records']) == 580
assert saved['current_case'] == cases[580]
assert saved['source_hashes_before'] == saved['source_hashes_after'] == freeze['source_sha256']
enemy = saved['current_result']['run_resolution']['enemy']
target = saved['current_input']['target_enemy']
assert 'id' not in enemy
assert all(enemy[key] == target[key] for key in ('enemy_id', 'stage_id', 'level'))
assert enemy['level_type'] == 'BOSS'
rows = deepcopy(saved['completed_records'])
rows.append({'section': saved['current_case']['section'], 'context': saved['current_case']['context'],
    'input': saved['current_input'], 'result': saved['current_result'],
    'visible_report': saved['current_visible_report'], 'report_texts': saved['current_report_texts'],
    'all_three_texts_preserve_result_bytes': True})
controls = {}
counts = Counter()
errors = Counter()
for index, row in enumerate(rows):
    case = cases[index]
    assert row['section'] == case['section'] and row['context'] == case['context']
    assert canonical(row['input']) == canonical(prepare(case))
    before = canonical(row)
    args, result = row['input'], row['result']
    if case.get('expected_error'):
        assert result is None and row['report_texts'] is None
        assert row['actual_error_type'] == 'ValueError'
        assert row['actual_error'] == row['expected_error'] == case['expected_error']
        assert row['visible_report'] == case['expected_error']
        errors[case['section']] += 1
    else:
        assert type(result) is dict
        report_texts = row['report_texts']
        assert set(report_texts) == {'estimate', 'default', 'technical'}
        assert all(type(value) is str and value for value in report_texts.values())
        assert report_texts['estimate'] == report_texts['default']
        assert row['visible_report'] == report_texts['technical' if case.get('technical', False) else 'default']
        assert row['all_three_texts_preserve_result_bytes'] is True
        if case['section'] == 81:
            namespace['require_warning_order085'](result, args, row['visible_report'], case['technical'])
        elif case['section'] == 82:
            anchor = canonical({key: value for key, value in args.items() if key != 'low_cost_healing_target'})
            if not args['low_cost_healing_target']:
                controls[anchor] = result
            factor = independent_json_factor(args, '微创治疗', 'heal_scale', 1.0)
            namespace['require_susuro_checkbox085'](result, args, row['visible_report'], controls[anchor], factor)
        elif case['section'] == 83:
            namespace['require_neural_checkbox085'](result, args, row['visible_report'])
        else:
            raise AssertionError('No saved84/85 output before this failure')
    assert before == canonical(row)
    counts[case['section']] += 1

mapping = [
 {'domain': 'neural manual/hidden inputs', 'receiver': 'require_neural_checkbox085',
  'producer': ['cases085.py:neural_options', 'rouge/app.py:active owner/skill serializer'],
  'contract': 'Mantra S3 omits four hidden keys; both owners actual neural consumer still runs. All other requested initial buildup is integer and flags are bool.'},
 {'domain': 'selected enemy identity', 'receiver_fields': ['run_resolution.enemy.enemy_id', 'stage_id', 'level', 'level_type'],
  'producer': ['rouge/enemy_environment.py:37-40 target spread', 'rouge/enemy_environment.py:boss override'],
  'contract': 'Accepted targeted cases are BOSS only; NORMAL yields exact prior threshold error. Target enemy_id differs from preview record id; no fallback.'},
 {'domain': 'River reference and report', 'receiver_fields': ['neural_relic_reference.periodic_damage_scheduled', 'preexisting_break_assumed', 'report.sections[river_neural].metrics[first_tick].value'],
  'producer': ['rouge/operator_engine.py:247-278 Combat.neural all owner/skill consumers', 'rouge/operator_engine.py:1845-1850 result attachment', 'rouge/reporting.py:723-731 river_neural'],
  'qualification': 'Exactly one sourced neural_burst_scale rule from selected River. Absent with empty relic selection.',
  'contract': 'Periodic scheduled false, first_tick explicit None; preexisting break reflects exact bool request. No actual periodic clock.'},
 {'domain': 'Mantra external events', 'receiver_fields': ['external_event_reference.kind', 'actual_event_times_seconds'],
  'producer': ['rouge/operator_engine.py:980-990 non-normal Mantra all skills', 'rouge/operator_engine.py:1594-1596 public attachment'],
  'contract': 'Kind mantra_events exists despite zero declared triggers; public actual event time None. Phatm incoming and bait refs absent because counts are zero.'},
 {'domain': 'Haruka acquisition parameters', 'receiver_fields': ['haruka_healing_reference.actual_target_count', 'actual_acquisition_times_seconds', 'native_composition_verified', 'native_attachment_verified', 'window_reference.same_fields'],
  'producer': ['rouge/haruka_healing_reference.py:reference all Haruka profiles', 'rouge/operator_engine.py:711-712 all skill plan', 'rouge/operator_engine.py:1590-1592 full/window attachment'],
  'contract': 'Full and shown dictionaries always carry exact None/False fields; E0/E1 lack floating talent but retain trait/body reference. No native target count inferred.'},
 {'domain': 'Haruka external events and repeat', 'receiver_fields': ['external_event_reference.kind', 'actual_event_times_seconds', 'estimate.base_stats.attack', 'estimate.skill.mode', 'skill_attack', 'duration_seconds', 'cycle_seconds', 'cycle_damage', 'cycle_healing', 'attack', 'components.[name,hits,total]', 'total_healing'],
  'producer': ['rouge/operator_engine.py:767 haruka_bubbles all skills', 'rouge/operator_engine.py:1594-1596 public actual time', 'rouge/operator_engine.py:1509-1537 extended result/estimate', 'rouge/operator_engine.py:mode infinite handling', 'rouge/uncertain_sources.py:mask_pending_healing'],
  'contract': 'No legacy damage-only receiver: all Haruka requests use extended engine. S2 repeat changes skill mode/attack only; exact None duration/cycle required for infinite, not converted to zero. Base stats remain same. Non-S2 repeat omitted. Zero recipient/window healing0. Talent dependent E0/E1 floating components zero.'},
 {'domain': 'Orchid near qualification and stats', 'receiver_fields': ['attack', 'estimate.base_stats.attack', 'estimate.skill.skill_attack', 'estimate.skill.cycle_seconds', 'total_damage', 'total_healing'],
  'producer': ['rouge/operator_engine.py:211-219 selected named talent initialization', 'rouge/operator_engine.py:1509-1537 extended result/estimate', 'rouge/operator_engine.py:1388-1391 unbound cast cycle unknown', 'rouge/uncertain_sources.py:mask_pending_damage'],
  'contract': 'E0 factor0 and full result equals False anchor; E1 .1/E2 .15/X2,3 unlocked .2 read qualified JSON source. No 30second expiration clock. Existing unknown damage preserved except exact zero observation/target lifetime.'},
 {'domain': 'Orchid redeploy', 'receiver_fields': ['orchid_redeploy_reference.events_scheduled', 'native_attachment_verified', 'actual_retreat_seconds', 'actual_next_deployment_seconds'],
  'producer': ['rouge/operator_engine.py:211-218 redeploy delta initialized including E0', 'rouge/operator_engine.py:1915-1943 Orchid owner result regardless skill/elite'],
  'contract': 'All valid Orchid case skills/cultivations receive same shaped reference; near flag changes no redeploy field. Events false and both actual times None.'},
 {'domain': 'Orchid cast reference', 'receiver_fields': ['unbound_cast_reference.kind', 'collision_clock_verified', 'actual_hit_times_seconds', 'actual_end_seconds'],
  'producer': ['rouge/operator_engine.py:1032/1041/1052 S1/S2/S3 dictionaries', 'rouge/operator_engine.py:1212-1216 preserve_unplaced_sources', 'rouge/uncertain_sources.py:75-89 collision flag', 'rouge/operator_engine.py:1601-1604 actual hit/end fields'],
  'contract': 'Every requested skill non-normal plan has kind orchid_arrows; collision false and times/end None. Empty enemy acquisition windows do not bind projectile clocks or erase potential arrow source.'}
]
receipt = {'status': 'PASS_REMAINING_RECEIVERS_SOURCE_BOUND_AND_SAVED581_REASSERTED',
    'approved_root_commit': ROOT, 'helper_snapshot_sha256': sha(helper_raw),
    'counterexample_gzip_sha256': sha(raw), 'counterexample_actual_enemy_identity': enemy,
    'saved_completed_rows': 580, 'saved_counterexample_reasserted': 1, 'saved_total_rows': 581,
    'saved_section_counts': dict(counts), 'saved_exact_existing_errors': dict(errors),
    'saved_success_rows': len(rows) - sum(errors.values()), 'saved_whole_rows_and_three_texts_unchanged': True,
    'remaining_case_count': 573, 'remaining_sections': dict(Counter(case['section'] for case in cases[581:])),
    'field_subscription_inventory': inventory, 'remaining_receiver_source_map': mapping,
    'additional_unclosed_shape_hazards_found': [], 'source_bindings': source_bindings,
    'own_application_API_calls': 0, 'own_formatter_calls': 0, 'own_production_selected_talents_calls': 0,
    'own_Qt_calls': 0, 'own_Wine_calls': 0, 'tracked_mutations': False,
    'local_AST_assertions_on_saved_rows_only': True,
    'local_JSON_candidate_projection_used_for_Susuro': True,
    'scope': 'Permits remaining-only573 author preflight after its parallel source audit; final1154/runner/GUI remain pending. Two different assertion preparation failures each once; neither establishes a product defect.'}
digest = save('remaining-receiver-source-and-saved581-review085.json', receipt)
print(json.dumps({'status': receipt['status'], 'receipt_sha256': digest, 'saved': 581,
    'remaining': 573, 'calls': 0, 'formatters': 0, 'production_helpers': 0}, ensure_ascii=False))
