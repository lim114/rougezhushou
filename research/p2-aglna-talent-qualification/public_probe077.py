from pathlib import Path
import argparse, collections, copy, datetime, hashlib, itertools, json, sys

base = Path(__file__).parent
parser = argparse.ArgumentParser()
parser.add_argument('--package', required=True)
parser.add_argument('--out', required=True)
args = parser.parse_args()
sys.path.insert(0, str(base / args.package))
from rouge.catalog import catalog, stage_previews
from rouge.damage import calculate_damage
from rouge.operator_engine import selected_talents
from rouge.run_config import config_data


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


OP = 'char_1015_aglna2'
profile = catalog()['operators'][OP]
cache_before = {key: digest(value) for key, value in
                (('catalog', catalog()), ('stage_previews', stage_previews()), ('run_config', config_data()))}
old_receipt = json.loads((base / 'readonly-public-results077.json').read_bytes())
reusable = {canonical(row['request']): row for row in old_receipt['records']} if args.package == 'baseline' else {}
records = []
seen = set()
groups = collections.Counter()
reused = 0
fresh = 0


def add(group, request):
    global reused, fresh
    key = canonical(request)
    if key in seen:
        return
    seen.add(key)
    request = json.loads(key)
    original = copy.deepcopy(request)
    if key in reusable:
        row = {k: copy.deepcopy(value) for k, value in reusable[key].items() if k != 'selected_talents'}
        row['group'] = group
        row['reused_completed_source_call_without_rerun'] = True
        reused += 1
    else:
        row = {'group': group, 'request': original}
        try:
            result = json.loads(canonical(calculate_damage(request)))
            row['full_result'] = result
            row['full_result_sha256'] = digest(result)
        except Exception as error:
            row['error'] = {'type': type(error).__name__, 'message': str(error)}
        fresh += 1
    assert request == original
    records.append(row)
    groups[group] += 1


for row in old_receipt['records']:
    add(row['group'], row['request'])
for elite, rank, levelmax, potential, mode, weight in itertools.product((0, 1, 2), (1, 7, 10),
                                                                     (False, True), (1, 3, 6),
                                                                     ('frames', 'continuous'), (0, 3, 4, 100)):
    add('all_cultivation_rank_potential_and_actual_weight_predicate_boundaries',
        {'operator': OP, 'skill': 1, 'elite': elite,
         'level': profile['phases'][elite]['max_level'] if levelmax else 1,
         'potential': potential, 'skill_rank': rank, 'timing_mode': mode, 'enemy_weight': weight, 'window_seconds': 10})
for elite, skill, mode, level in itertools.product((0, 1, 2), (1, 2, 3), ('frames', 'continuous'), (1, 59, 60, 90)):
    for module in (None, *[record['id'] for record in profile['modules']]):
        add('actual_module_gate_does_not_supply_a_locked_base_talent',
            {'operator': OP, 'skill': skill, 'elite': elite, 'level': level, 'skill_rank': 7,
             'timing_mode': mode, 'window_seconds': 10,
             **({'module_id': module, 'module_level': 3} if module else {})})
for elite, mode, observation in itertools.product((0, 1, 2), ('frames', 'continuous'),
    ({'window_seconds': 0}, {'window_seconds': .1}, {'window_seconds': 3},
     {'timing': {'target_disappears_seconds': 0}}, {'timing': {'target_windows': []}},
     {'timing': {'interrupt_windows': [[0, 10]]}}, {'timing': {'target_disappears_seconds': 1}},
     {'base_attack': 0}, {'continuous_attacks': False})):
    add('zero_and_positive_observation_global_absence_and_independent_resource_controls',
        {'operator': OP, 'skill': 1, 'elite': elite, 'skill_rank': 1,
         'timing_mode': mode, 'window_seconds': 10, **observation})
for elite, mode, relics in itertools.product((0, 1, 2), ('frames', 'continuous'),
    ([], ['rogue_6_relic_legacy_67'], ['rogue_6_relic_legacy_45'],
     ['rogue_6_relic_legacy_116'], ['rogue_6_relic_fight_5'], ['rogue_6_relic_legacy_81'])):
    add('independent_and_retired_combat_relic_count_chains_not_reactivated',
        {'operator': OP, 'skill': 1, 'elite': elite, 'skill_rank': 1, 'timing_mode': mode,
         'window_seconds': 10, 'relic_ids': relics, 'effects': [{'kind': 'sp_recovery', 'value': .2}]})
for elite, mode, weight in itertools.product((0, 1, 2), ('frames', 'continuous'), (0, 100)):
    add('selected_enemy_identity_overrides_manual_weight_in_both_qualification_states',
        {'operator': OP, 'skill': 1, 'elite': elite, 'skill_rank': 1, 'timing_mode': mode,
         'window_seconds': 10, 'enemy_weight': weight,
         'target_enemy': {'stage_id': 'ro6_n_1_1', 'enemy_id': 'enemy_2133_shdopl', 'level': 0},
         'run_config': {'difficulty': {'value': 4}}})
for owner, entry in catalog()['operators'].items():
    for skill, mode in itertools.product(range(1, len(entry['skills']) + 1), ('frames', 'continuous')):
        add('all_87_skills_both_modes_default_full_output_controls',
            {'operator': owner, 'skill': skill, 'timing_mode': mode, 'window_seconds': 10})
for condition in ({'elite': -1}, {'elite': 3}, {'level': 0}, {'level': 999}, {'potential': 0},
                  {'potential': 7}, {'skill': 4}, {'skill_rank': 11}, {'window_seconds': -1},
                  {'timing_mode': 'missing'}, {'module_id': 'missing', 'module_level': 1}):
    add('prior_complete_training_timing_module_error_precedence',
        {'operator': OP, 'skill': 1, 'elite': 0, 'skill_rank': 1, **condition})
cache_after = {key: digest(value) for key, value in
               (('catalog', catalog()), ('stage_previews', stage_previews()), ('run_config', config_data()))}
assert cache_before == cache_after
out = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'package': args.package,
       'paired_scenario_records': len(records), 'actual_fresh_public_calls': fresh,
       'reused_completed_readonly_calls_without_rerun': reused, 'groups': dict(groups), 'records': records,
       'cache_before_sha256': cache_before, 'cache_after_sha256': cache_after,
       'callers_and_public_static_caches_preserved': True}
(base / args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print({k: v for k, v in out.items() if k != 'records'})
print({'successes': sum('full_result' in row for row in records),
       'errors': dict(collections.Counter(row['error']['message'] for row in records if 'error' in row))})
