"""Capture public API results for the scoped target-count change."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--repo', required=True, type=Path)
parser.add_argument('--out', required=True, type=Path)
args = parser.parse_args()
sys.path.insert(0, str(args.repo))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.reporting import has_healing


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


rows = []


def capture(category, operator, skill, field, label, value, mode, omitted=False):
    scenario = {'operator': operator, 'skill': skill, 'base_attack': 1000,
                'window_seconds': 10, 'timing_mode': mode}
    if not omitted:
        scenario[field] = value
    before = canonical(scenario)
    try:
        result = calculate_damage(scenario)
        summary = {key: result.get(key) for key in ('attack', 'total_damage', 'total_healing')}
        error = None
    except Exception as exc:
        result = {'error_type': type(exc).__name__, 'error': str(exc)}
        summary = result
        error = type(exc).__name__
    rows.append({'case': '|'.join((category, operator, str(skill), field, label, mode)),
                 'category': category, 'operator': operator, 'skill': skill,
                 'field': field, 'value_label': label, 'timing_mode': mode,
                 'accepted': error is None, 'result_sha256': digest(result),
                 'summary': summary, 'input_unchanged': before == canonical(scenario)})


active = [(operator, number, 'healing_targets')
          for operator, profile in catalog()['operators'].items()
          for number in range(1, len(profile['skills']) + 1)
          if has_healing(operator, number)]
active += [('char_1037_amiya3', 2, 'amiya_hit_targets')]
active += [('char_4087_ines', number, 'stolen_enemy_count') for number in (1, 2, 3)]
variants = [('omitted', None)]
variants += [('int:' + str(value), value) for value in (0, 1, 5, 100, -1, 101)]
variants += [('float:' + str(value), float(value)) for value in (0, 1, 5, 100)]
variants += [('str:' + value, value) for value in ('0', '1', '5', '100')]
variants += [('float:0.5', .5), ('float:nan', float('nan')), ('float:inf', float('inf'))]
for operator, skill, field in active:
    for mode in ('frames', 'continuous'):
        for label, value in variants:
            capture('non_boolean_active', operator, skill, field, label, value, mode, label == 'omitted')
        for value in (False, True):
            capture('active_bool', operator, skill, field, str(value), value, mode)

inactive = [('mechanist', 1, 'healing_targets'), ('silverash', 3, 'healing_targets'),
            ('char_151_myrtle', 1, 'healing_targets'), ('char_1044_hsgma2', 1, 'healing_targets'),
            ('char_1037_amiya3', 1, 'amiya_hit_targets'), ('char_151_myrtle', 2, 'amiya_hit_targets'),
            ('char_151_myrtle', 2, 'stolen_enemy_count')]
flags = [('char_298_susuro', 2, 'low_cost_healing_target'), ('char_4202_haruka', 2, 'haruka_repeat'),
         ('char_206_gnosis', 3, 'frozen_at_skill_end'), ('char_4087_ines', 3, 'ines_first_deployment')]
other_integer = [('char_110_deepcl', 1, 'summon_count'), ('char_206_gnosis', 2, 'cold_state'),
                 ('char_4202_haruka', 1, 'bubble_bursts'), ('char_1035_wisdel', 1, 'ghost_casts'),
                 ('mechanist', 3, 'charge_count'), ('silverash', 2, 'activation_count')]
for category, cases in (('inactive_bool', inactive), ('checkbox_bool', flags), ('other_integer_bool', other_integer)):
    for operator, skill, field in cases:
        for mode in ('frames', 'continuous'):
            for value in (False, True):
                capture(category, operator, skill, field, str(value), value, mode)

assert len({row['case'] for row in rows}) == len(rows)
result = {'repo': str(args.repo), 'public_entrypoint': 'rouge.damage.calculate_damage',
          'public_calls': len(rows), 'active_operator_skill_fields': len(active),
          'all_inputs_unchanged': all(row['input_unchanged'] for row in rows),
          'damage_source_sha256': hashlib.sha256((args.repo / 'rouge/damage.py').read_bytes()).hexdigest(),
          'rows': rows}
args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({key: result[key] for key in ('public_calls', 'active_operator_skill_fields', 'all_inputs_unchanged')}, ensure_ascii=False))
