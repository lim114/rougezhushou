"""Capture unchanged nonzero/invalid/other timing behavior through the public API."""
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
from rouge.damage import calculate_damage


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


configs = [('omitted', {})]
configs += [('positive:' + repr(value), {'target_disappears_seconds': value})
            for value in (1, '1', 2.5, '2.5', 3600, '3600', '0.000000000001')]
configs += [('invalid:' + repr(value), {'target_disappears_seconds': value})
            for value in (False, True, None, -1, float('nan'), float('inf'), '-1', 'nan', 'inf', 'unknown', '3601')]
configs += [('other:' + field, {field: '0'}) for field in
            ('windup_frames', 'recovery_frames', 'start_delay_frames', 'post_skill_lock_frames',
             'sp_lockout_extra_seconds', 'projectile_travel_seconds')]
configs += [('positive-and-owner-window', {'target_disappears_seconds': '1', 'target_windows': [[0, 10]]}),
            ('positive-and-owner-empty', {'target_disappears_seconds': '1', 'target_windows': []}),
            ('nested-unit-zero-only', {'units': {'token_10001_deepcl_tentac': {'target_disappears_seconds': '0'}}}),
            ('positive-and-nested-zero', {'target_disappears_seconds': '2.5',
                'units': {'token_10001_deepcl_tentac': {'target_disappears_seconds': '0'}}})]
operators = [('mechanist', 1), ('kaltsit', 2), ('char_002_amiya', 1),
             ('char_1037_amiya3', 1), ('char_4202_haruka', 1), ('char_110_deepcl', 1)]
rows = []
for operator, skill in operators:
    for mode in ('frames', 'continuous'):
        for label, timing in configs:
            scenario = {'operator': operator, 'skill': skill, 'base_attack': 1000,
                        'timing_mode': mode, 'window_seconds': 10, 'timing': timing}
            before = canonical(scenario)
            try:
                result = calculate_damage(scenario)
            except Exception as exc:
                result = {'error_type': type(exc).__name__, 'error': str(exc)}
            rows.append({'case': '|'.join((operator, str(skill), mode, label)),
                'operator': operator, 'skill': skill, 'mode': mode, 'label': label,
                'result_sha256': hashlib.sha256(canonical(result).encode()).hexdigest(),
                'accepted': 'error' not in result, 'error': result.get('error'),
                'input_unchanged': before == canonical(scenario)})
assert len({row['case'] for row in rows}) == len(rows)
receipt = {'repo': str(args.repo), 'public_calls': len(rows),
           'all_inputs_unchanged': all(row['input_unchanged'] for row in rows),
           'source_hashes': {p: hashlib.sha256((args.repo / p).read_bytes()).hexdigest()
                             for p in ('rouge/damage.py', 'rouge/timing.py')},
           'rows': rows}
args.out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({key: receipt[key] for key in ('public_calls', 'all_inputs_unchanged')}, ensure_ascii=False))
