"""Save complete public JSON, three text reports, and exact legacy errors."""
import copy
import json
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent
TARGET = Path(sys.argv[1])
sys.path.insert(0, str(TARGET))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.reporting import format_report


def scenario(owner, skill, mode='frames', **extra):
    return {'operator': owner, 'skill': skill, 'timing_mode': mode,
            'base_attack': 1000, 'window_seconds': 10, **extra}


if sys.argv[2] == 'cases':
    cases = []
    for owner in ('char_1042_phatm2', 'char_4204_mantra'):
        for skill in (1, 2, 3):
            for mode in ('frames', 'continuous'):
                args = scenario(owner, skill, mode)
                for boss in (False, True):
                    for breaking in (False, True):
                        cases.append({**args, 'enemy_is_boss': boss,
                            'enemy_in_neural_break': breaking,
                            'initial_neural_buildup': 1999 if boss else 999,
                            'relic_ids': ['rogue_6_relic_fight_22']})
                for field in ('enemy_is_boss', 'enemy_in_neural_break'):
                    for value in ('false', '', 'unknown', None, 0, 1, [], {'assumed': False}):
                        cases.append({**args, field: value})
                for elite, allowed in ((0, (1,)), (1, (1, 2)), (2, (1, 2, 3))):
                    if skill not in allowed:
                        continue
                    cases.append({**args, 'elite': elite, 'level': 1, 'skill_rank': 7})
                    cases.append({**args, 'elite': elite, 'level': 1, 'skill_rank': 7,
                                  'enemy_in_neural_break': 'false'})
        for mode in ('frames', 'continuous'):
            args = scenario(owner, 3, mode)
            for extra in ({'window_seconds': 0}, {'timing': {'target_disappears_seconds': 0}},
                          {'timing': {'target_windows': []}}):
                for value in (False, 'false'):
                    cases.append({**args, **extra, 'enemy_in_neural_break': value})
            for target in (
                {'stage_id': 'ro6_e_1_2', 'enemy_id': 'enemy_1093_ccsbr', 'level': 0},
                {'stage_id': 'ro6_b_3', 'enemy_id': 'enemy_2143_shwksc', 'level': 0},
            ):
                for value in (False, True, 'false', ''):
                    cases.append({**args, 'target_enemy': target, 'enemy_is_boss': value,
                                  'relic_ids': ['rogue_6_relic_fight_22']})
            for extra in (
                {'skill': False}, {'skill_rank': False}, {'elite': 1}, {'level': 999},
                {'module_id': 'unknown', 'module_level': 1}, {'initial_neural_buildup': 2500},
                {'initial_neural_buildup': 1500, 'enemy_is_boss': ''},
                {'enemy_buildup_resistance': 101}, {'enemy_elemental_resistance': 101},
                {'window_seconds': -1}, {'timing': {'windup_frames': -1}},
                {'timing': {'sp_lockout_extra_seconds': -1}},
                {'target_enemy': {'stage_id': 'unknown', 'enemy_id': 'unknown', 'level': 0}},
                {'run_config': {'difficulty': {'value': 16}}},
                {'enemy_attack_count': True} if owner == 'char_1042_phatm2' else {'palsy_triggers': True},
            ):
                cases.append({**args, 'enemy_is_boss': 'false',
                              'enemy_in_neural_break': 'false', **extra})
            cases.append({**args, 'enemy_is_boss': 'false', 'initial_neural_buildup': 1500})
            cases.append({**args, 'enemy_in_neural_break': 'false',
                          'relic_ids': ['rogue_6_relic_fight_22']})
    for owner, skill in (('silverash', 3), ('mechanist', 1), ('char_1037_amiya3', 2),
                         ('char_1048_orchd2', 3), ('char_298_susuro', 2)):
        for mode in ('frames', 'continuous'):
            cases.append(scenario(owner, skill, mode))
            cases.append(scenario(owner, skill, mode, enemy_is_boss='false',
                                  enemy_in_neural_break='unknown'))
    unique = {json.dumps(case, ensure_ascii=False, sort_keys=True): case for case in cases}
    (OUT / 'public-cases083.json').write_text(json.dumps(list(unique.values()),
        ensure_ascii=False, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'cases': len(unique), 'API_calls': 0}))
    sys.exit(0)

cases = json.loads((OUT / 'public-cases083.json').read_text())
original_catalog = copy.deepcopy(catalog())
rows = []
for index, args in enumerate(cases):
    before = copy.deepcopy(args)
    try:
        result = calculate_damage(args)
        row = {'index': index, 'scenario': args, 'result': result,
               'estimate_text': format_estimate(result), 'report_text': format_report(result),
               'technical_report_text': format_report(result, technical=True)}
    except (ValueError, TypeError) as exc:
        row = {'index': index, 'scenario': args,
               'error': {'type': type(exc).__name__, 'message': str(exc)}}
    assert args == before, ('caller mutation', index)
    rows.append(row)
assert catalog() == original_catalog, 'cached catalog mutation'
(OUT / ('public-' + sys.argv[2] + '083.json')).write_text(json.dumps(rows,
    ensure_ascii=False, indent=2, allow_nan=False) + '\n')
print(json.dumps({'cases': len(rows), 'API_calls': len(rows),
                  'accepted': sum('result' in row for row in rows),
                  'errors': sum('error' in row for row in rows),
                  'caller_and_catalog_preserved': True}))
