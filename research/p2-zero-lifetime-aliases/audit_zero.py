"""Read-only public zero-lifetime alias audit; preserve each baseline separately."""
import argparse
import datetime
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--repo', type=Path, default=Path('/workspace/rougezhushou'))
parser.add_argument('--out', type=Path, required=True)
parser.add_argument('--source-baseline-head')
parser.add_argument('--baseline-label', default='Current selected repository; interpret results using the exact saved HEAD and source hashes.')
args = parser.parse_args()
sys.path.insert(0, str(args.repo))
from rouge.catalog import catalog
from rouge.damage import calculate_damage


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def delta(before, after, path=''):
    if type(before) is not type(after):
        return [{'path': path, 'numeric': before, 'alias': after}]
    if isinstance(before, dict):
        found = []
        for key in before.keys() | after.keys():
            p = path + '.' + key if path else key
            if key not in before or key not in after:
                found.append({'path': p, 'numeric': before.get(key), 'alias': after.get(key)})
            else:
                found.extend(delta(before[key], after[key], p))
        return found
    if isinstance(before, list):
        if before == after:
            return []
        if len(before) != len(after):
            return [{'path': path, 'numeric': before, 'alias': after}]
        return [change for i, (b, a) in enumerate(zip(before, after)) for change in delta(b, a, path + '[' + str(i) + ']')]
    return [] if before == after else [{'path': path, 'numeric': before, 'alias': after}]


def call(scenario):
    before = canonical(scenario)
    try:
        result = calculate_damage(scenario)
    except Exception as exc:
        result = {'error_type': type(exc).__name__, 'error': str(exc)}
    return result, before == canonical(scenario)


def summary(result):
    if 'error' in result:
        return result
    view = {key: result.get(key) for key in ('attack', 'total_damage', 'total_healing', 'known_damage_subtotals', 'known_healing_subtotals')}
    view['estimate_skill'] = {key: result['estimate']['skill'].get(key) for key in
        ('initial_seconds', 'recharge_seconds', 'cycle_seconds', 'duration_seconds', 'window_seconds',
         'total_damage', 'window_damage', 'cycle_damage', 'total_healing', 'window_healing', 'cycle_healing')}
    return view


files = ('rouge/damage.py', 'rouge/operator_engine.py', 'rouge/estimate.py', 'rouge/timing.py',
         'rouge/charge_reference.py', 'rouge/data/catalog.json')
hashes_before = {p: hashlib.sha256((args.repo / p).read_bytes()).hexdigest() for p in files}
groups = []
full_results = []
pair_rows = []
skills = [(op, n, {}) for op, profile in catalog()['operators'].items() for n in range(1, len(profile['skills']) + 1)]
manual_cases = [
    ('mechanist', 2, {'shield_break_count': 2, 'skill_duration_seconds': 2}),
    ('mechanist', 3, {'charge_count': 2}),
    ('silverash', 2, {'activation_count': 2, 'deployment_stacks': 1, 'companion_attack': 1000}),
    ('char_1044_hsgma2', 1, {'incoming_hits': 2}),
    ('char_206_gnosis', 2, {'cold_state': 2}),
    ('char_1037_amiya3', 2, {'amiya_hit_targets': 1}),
    ('char_4202_haruka', 2, {'elite': 2, 'level': 60, 'module_id': 'uniequip_002_haruka',
        'module_level': 1, 'healing_targets': 3, 'bubble_bursts': 1}),
    ('kaltsit', 2, {'healing_targets': 0}),
]
for category, scenarios in (('all87', skills), ('manual', manual_cases)):
    for op, number, extra in scenarios:
        for mode in ('frames', 'continuous'):
            base = {'operator': op, 'skill': number, 'base_attack': 1000,
                    'enemy_defense': 0, 'enemy_resistance': 0, 'timing_mode': mode, **extra}
            records = []
            for lifetime in (0, '0', '0.0', '-0'):
                scenario = {**base, 'timing': {'target_disappears_seconds': lifetime}}
                result, unchanged = call(scenario)
                records.append({'lifetime': lifetime, 'result': result, 'input_unchanged': unchanged})
                full_results.append({'category': category, 'scenario': scenario, 'result': result, 'input_unchanged': unchanged})
            numeric = records[0]['result']
            for record in records[1:]:
                alias = record['result']
                changes = delta(summary(numeric), summary(alias))
                pair_rows.append({'category': category, 'operator': op, 'skill': number, 'timing_mode': mode,
                    'extra': extra, 'alias': record['lifetime'],
                    'full_result_equal': canonical(numeric) == canonical(alias),
                    'numerical_summary_equal': summary(numeric) == summary(alias),
                    'numeric_sha256': digest(numeric), 'alias_sha256': digest(alias),
                    'numeric_summary': summary(numeric), 'alias_summary': summary(alias),
                    'summary_differences': changes})
            groups.append({'category': category, 'operator': op, 'skill': number, 'timing_mode': mode,
                           'all_inputs_unchanged': all(r['input_unchanged'] for r in records)})

hashes_after = {p: hashlib.sha256((args.repo / p).read_bytes()).hexdigest() for p in files}
receipt = {'recorded_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'repo': str(args.repo), 'head': args.source_baseline_head or subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=args.repo, text=True).strip(),
    'baseline_limit': args.baseline_label,
    'public_entrypoint': 'rouge.damage.calculate_damage', 'supported_skills': len(skills),
    'all87_public_calls': len(skills) * 2 * 4, 'manual_public_calls': len(manual_cases) * 2 * 4,
    'pair_rows': len(pair_rows),
    'all_inputs_unchanged': all(g['all_inputs_unchanged'] for g in groups),
    'source_hashes_before': hashes_before, 'source_hashes_after': hashes_after, 'audited_files_unchanged': hashes_before == hashes_after,
    'different_full_results_by_category_mode': dict(Counter(row['category'] + '/' + row['timing_mode'] for row in pair_rows if not row['full_result_equal'])),
    'different_numerical_results_by_category_mode': dict(Counter(row['category'] + '/' + row['timing_mode'] for row in pair_rows if not row['numerical_summary_equal'])),
    'all87_affected_operator_skills': {mode: sorted({row['operator'] + '/S' + str(row['skill']) for row in pair_rows
        if row['category'] == 'all87' and row['timing_mode'] == mode and not row['numerical_summary_equal']}) for mode in ('frames', 'continuous')},
    'rows': pair_rows,
    'limits': ['Read-only API audit; no tracked edits.', 'No GUI, Wine, native Windows/game or desktop verification.',
               'No invented positive-lifetime clocks, stacking, target acquisition, or adjacent healing rule.']}
args.out.mkdir(parents=True, exist_ok=True)
(args.out / 'public-pairs.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(args.out / 'public-results.json').write_text(json.dumps(full_results, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({key: receipt[key] for key in ('head', 'supported_skills', 'all87_public_calls', 'manual_public_calls',
    'different_full_results_by_category_mode', 'different_numerical_results_by_category_mode', 'all_inputs_unchanged', 'audited_files_unchanged')}, ensure_ascii=False))
for row in pair_rows:
    if row['alias'] == '0' and row['category'] == 'all87' and row['operator'] in ('char_002_amiya', 'kaltsit', 'char_1037_amiya3', 'char_298_susuro'):
        print(row['operator'], row['skill'], row['timing_mode'], row['full_result_equal'], canonical(row['summary_differences']))
