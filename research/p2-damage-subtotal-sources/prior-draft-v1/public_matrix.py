"""Exercise whole public outputs in a single explicitly selected sealed package."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
PACKAGE = Path(sys.argv[1]).resolve()
OUTPUT = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(PACKAGE))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate

RIVER = 'rogue_6_relic_fight_22'
OP = 'char_1042_phatm2'
cases = {}
identities = []
for key, operator in catalog()['operators'].items():
    for number, skill in enumerate(operator['skills'], 1):
        identities.append([key, number])
        for mode in ('frames', 'continuous'):
            for held in (False, True):
                cases[f'catalog:{key}:{number}:{mode}:river{int(held)}'] = {
                    'operator': key, 'skill': number, 'base_attack': 1000,
                    'timing_mode': mode, 'relic_ids': [RIVER] if held else []}
timings = ({}, {'window_seconds': 0}, {'window_seconds': .1},
           {'timing': {'target_windows': []}},
           {'timing': {'target_disappears_seconds': 0}},
           {'enemy_buildup_resistance': 100})
for skill in (1, 2, 3):
    for mode in ('frames', 'continuous'):
        for incoming in (0, 20):
            for held in (False, True):
                for i, timing in enumerate(timings):
                    cases[f'neural:{skill}:{mode}:incoming{incoming}:river{int(held)}:scope{i}'] = {
                        'operator': OP, 'skill': skill, 'base_attack': 1000,
                        'timing_mode': mode, 'enemy_attack_count': incoming,
                        'relic_ids': [RIVER] if held else [], **timing}
for mode in ('frames', 'continuous'):
    for incoming in (0, 20):
        for held in (False, True):
            cases[f'bait:{mode}:incoming{incoming}:river{int(held)}'] = {
                'operator': OP, 'skill': 2, 'base_attack': 1000,
                'timing_mode': mode, 'enemy_attack_count': incoming,
                'bait_triggers': 1, 'relic_ids': [RIVER] if held else []}
    for held in (False, True):
        cases[f'shield:{mode}:river{int(held)}'] = {
            'operator': 'mechanist', 'skill': 2, 'base_attack': 1000,
            'timing_mode': mode, 'shield_break_count': 2,
            'relic_ids': [RIVER] if held else []}
        cases[f'mantra:{mode}:river{int(held)}'] = {
            'operator': 'char_4204_mantra', 'skill': 2,
            'timing_mode': mode, 'window_seconds': 1,
            'initial_neural_buildup': 999, 'relic_ids': [RIVER] if held else []}
for key in ('char_1037_amiya3', 'char_1044_hsgma2'):
    for mode in ('frames', 'continuous'):
        cases[f'healing:{key}:{mode}'] = {'operator': key, 'skill': 2,
            'base_attack': 1000, 'timing_mode': mode,
            'relic_ids': ['rogue_6_relic_legacy_81']}

assert len(identities) == 87
outputs = {}
for name, args in cases.items():
    before = deepcopy(args)
    result = calculate_damage(args)
    assert args == before, name
    outputs[name] = {'scenario': args, 'result': result,
                     'formatted_report': format_estimate(result)}
payload = {'baseline_head': '15e0fa455aad05d27303428299d24d15db4c572c',
           'package_directory': str(PACKAGE), 'skill_identities': identities,
           'reporting_sha256': hashlib.sha256((PACKAGE / 'rouge/reporting.py').read_bytes()).hexdigest(),
           'cases': outputs, 'caller_inputs_preserved': True}
OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
print(json.dumps({'package': str(PACKAGE), 'public_calls': len(outputs),
                  'skills': len(identities), 'output': str(OUTPUT)}, ensure_ascii=False))
