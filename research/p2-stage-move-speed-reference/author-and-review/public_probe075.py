from pathlib import Path
import argparse, collections, copy, datetime, hashlib, itertools, json, sys

base = Path(__file__).parent
parser = argparse.ArgumentParser()
parser.add_argument('--package', required=True)
parser.add_argument('--out', required=True)
args = parser.parse_args()
sys.path.insert(0, str(base / args.package))
from rouge.battle_preview import battle_data, enemy_preview, enemy_text
from rouge.catalog import catalog, stage_previews
from rouge.damage import calculate_damage
from rouge.run_config import config_data


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


cache_before = {name: digest(value) for name, value in
                (('battle', battle_data()), ('catalog', catalog()),
                 ('stage_previews', stage_previews()), ('run_config', config_data()))}
records = []
seen = set()
groups = collections.Counter()


def add(api, group, request):
    identity = canonical({'api': api, 'request': request})
    if identity in seen:
        return
    seen.add(identity)
    request = json.loads(canonical(request))
    original = copy.deepcopy(request)
    row = {'api': api, 'group': group, 'request': original}
    try:
        if api == 'enemy_preview':
            value = enemy_preview(request['stage_id'], request['enemy_id'], request['level'], request.get('run_config'))
            result = {'preview': value, 'default_text': enemy_text(value),
                      'technical_text': enemy_text(value, technical=True)}
        else:
            result = calculate_damage(request)
        row['full_result'] = json.loads(canonical(result))
        row['full_result_sha256'] = digest(row['full_result'])
    except Exception as error:
        row['error'] = {'type': type(error).__name__, 'message': str(error)}
    assert request == original
    records.append(row)
    groups[group] += 1


stages = battle_data()['stages']
enemy_references = 0
for sid, stage in stages.items():
    for enemy in stage['enemies']:
        enemy_references += 1
        for config in (None, {'difficulty': {'value': 4}}):
            add('enemy_preview', 'all_105_stages_all_selected_enemy_references',
                {'stage_id': sid, 'enemy_id': enemy['id'], 'level': enemy['level'], 'run_config': config})
for sid in ('ro6_n_3_6', 'ro6_e_3_6'):
    for grade in (0, 5, 9, 15):
        for enemy in stages[sid]['enemies']:
            add('enemy_preview', 'raw_parameter_independent_from_actual_difficulty_context',
                {'stage_id': sid, 'enemy_id': enemy['id'], 'level': enemy['level'],
                 'run_config': {'difficulty': {'value': grade}, 'zone': {'id': 'zone_3'}}})
for sid, level, enemy in (('missing', 0, 'missing'), ('ro6_e_3_6', 999, 'enemy_10107_mjcdog_2'),
                          ('ro6_e_3_6', 0, 'missing'), ('ro6_n_3_6', 999, 'enemy_10107_mjcdog_2')):
    add('enemy_preview', 'prior_selected_enemy_identity_errors',
        {'stage_id': sid, 'enemy_id': enemy, 'level': level})
for config in ({'difficulty': {'value': 16}}, {'difficulty': {'value': True}},
               {'difficulty': {'value': 4, 'modeDifficulty': 'CHALLENGE'}},
               {'squad': {'id': 'missing', 'effect_verified': True}},
               {'squad': {'id': 'rogue_6_band_7', 'effect_verified': 'false'}},
               {'difficulty': 'bad'}, ['bad'], 'bad'):
    add('enemy_preview', 'prior_invalid_context_remains_unknown_without_fake_speed',
        {'stage_id': 'ro6_e_3_6', 'enemy_id': 'enemy_10107_mjcdog_2', 'level': 0, 'run_config': config})
for owner, entry in catalog()['operators'].items():
    for skill, mode, sid in itertools.product(range(1, len(entry['skills']) + 1),
                                            ('frames', 'continuous'), ('ro6_e_3_6', 'ro6_n_3_6')):
        add('calculate_damage', 'all_87_skills_both_modes_complete_math_training_status_controls',
            {'operator': owner, 'skill': skill, 'timing_mode': mode, 'window_seconds': 10,
             'target_enemy': {'stage_id': sid, 'enemy_id': 'enemy_10107_mjcdog_2', 'level': 0},
             'run_config': {'difficulty': {'value': 4}}})
conditions = ({'window_seconds': 0}, {'timing': {'target_disappears_seconds': 0}},
              {'timing': {'target_windows': []}}, {'elite': 0, 'skill_rank': 1},
              {'elite': 1, 'skill_rank': 7}, {'potential': 6},
              {'three_professions': True, 'three_same_profession': True},
              {'effects': [{'kind': 'sp_per_second', 'value': .2}, {'kind': 'attack_speed', 'value': 18}]},
              {'level': 59, 'module_id': 'uniequip_002_shu', 'module_level': 3})
for skill, mode, flag, condition in itertools.product((1, 2, 3), ('frames', 'continuous'), (False, True), conditions):
    add('calculate_damage', 'independent_shu_training_flags_clock_and_empty_target_boundaries',
        {'operator': 'char_2025_shu', 'skill': skill, 'four_sui': flag,
         'timing_mode': mode, 'window_seconds': 10,
         'target_enemy': {'stage_id': 'ro6_e_3_6', 'enemy_id': 'enemy_10107_mjcdog_2', 'level': 0},
         'run_config': {'difficulty': {'value': 4}}, **condition})
for scenario in ({'elite': 2, 'level': 999}, {'skill': 4}, {'skill_rank': 11},
                 {'timing_mode': 'missing'}, {'window_seconds': -1},
                 {'run_config': {'difficulty': {'value': 16}}},
                 {'run_config': {'difficulty': {'value': 4, 'modeDifficulty': 'CHALLENGE'}}}):
    add('calculate_damage', 'prior_complete_training_timing_and_mode_errors',
        {'operator': 'char_2025_shu', 'skill': 1, 'four_sui': True,
         'target_enemy': {'stage_id': 'ro6_e_3_6', 'enemy_id': 'enemy_10107_mjcdog_2', 'level': 0},
         'run_config': {'difficulty': {'value': 4}}, **scenario})
cache_after = {name: digest(value) for name, value in
               (('battle', battle_data()), ('catalog', catalog()),
                ('stage_previews', stage_previews()), ('run_config', config_data()))}
assert cache_before == cache_after
out = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'package': args.package,
       'public_calls': len(records), 'stage_count': len(stages), 'selected_enemy_references': enemy_references,
       'groups': dict(groups), 'records': records, 'cache_before_sha256': cache_before,
       'cache_after_sha256': cache_after, 'callers_and_public_static_caches_preserved': True}
(base / args.out).write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print({k: v for k, v in out.items() if k != 'records'})
print({'successes': sum('full_result' in row for row in records),
       'errors': dict(collections.Counter(row['error']['message'] for row in records if 'error' in row))})
