"""Read-only public API audit of boolean target-count coercion.

Run from /workspace/rougezhushou with its .venv/bin/python.
Writes only beside this script, outside the tracked checkout.
"""
import copy
import datetime
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path('/workspace/rougezhushou')
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from rouge.catalog import catalog
from rouge.damage import calculate_damage


def serialized(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(value):
    return hashlib.sha256(serialized(value).encode()).hexdigest()


def file_digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def call(scenario):
    before = serialized(scenario)
    try:
        result = calculate_damage(scenario)
    except Exception as exc:
        result = {'error_type': type(exc).__name__, 'error': str(exc)}
    return result, before == serialized(scenario)


def summary(result):
    if 'error' in result:
        return result
    fields = ('operator', 'attack', 'total_damage', 'total_healing',
              'known_healing_subtotals', 'known_damage_subtotals',
              'haruka_healing_reference', 'amiya_phase_reference')
    compact = {key: result[key] for key in fields if key in result}
    compact['estimate_skill'] = {key: result['estimate']['skill'].get(key) for key in
        ('healing_targets', 'total_healing', 'window_healing', 'cycle_healing',
         'window_seconds', 'duration_seconds', 'initial_seconds', 'recharge_seconds', 'cycle_seconds')}
    return compact


cases = [
    ('myrtle_s2', 'char_151_myrtle', 2, 'healing_targets', {}),
    ('kaltsit_s1', 'kaltsit', 1, 'healing_targets', {'window_seconds': 10}),
    ('kaltsit_s2', 'kaltsit', 2, 'healing_targets', {'window_seconds': 10}),
    ('kaltsit_s3', 'kaltsit', 3, 'healing_targets', {'window_seconds': 10}),
    ('susuro_s2', 'char_298_susuro', 2, 'healing_targets', {'window_seconds': 10}),
    ('shu_s1', 'char_2025_shu', 1, 'healing_targets', {'window_seconds': 10}),
    ('shu_s2', 'char_2025_shu', 2, 'healing_targets', {'window_seconds': 10}),
    ('medical_amiya_s1', 'char_1037_amiya3', 1, 'healing_targets', {'window_seconds': 10}),
    ('haruka_s1', 'char_4202_haruka', 1, 'healing_targets',
        {'elite': 2, 'level': 60, 'module_id': 'uniequip_002_haruka', 'module_level': 1, 'window_seconds': 10}),
    ('haruka_s2', 'char_4202_haruka', 2, 'healing_targets',
        {'elite': 2, 'level': 60, 'module_id': 'uniequip_002_haruka', 'module_level': 1, 'window_seconds': 10}),
    ('haruka_s3', 'char_4202_haruka', 3, 'healing_targets',
        {'elite': 2, 'level': 60, 'module_id': 'uniequip_002_haruka', 'module_level': 1, 'window_seconds': 10}),
    ('medical_amiya_s2', 'char_1037_amiya3', 2, 'amiya_hit_targets', {'window_seconds': 10}),
    ('ines_s1', 'char_4087_ines', 1, 'stolen_enemy_count', {'window_seconds': 10}),
    ('ines_s2', 'char_4087_ines', 2, 'stolen_enemy_count', {'window_seconds': 10}),
    ('ines_s3', 'char_4087_ines', 3, 'stolen_enemy_count', {'window_seconds': 10}),
]
files = ('rouge/damage.py', 'rouge/operator_engine.py', 'rouge/estimate.py',
         'rouge/operator_options.py', 'rouge/app.py', 'rouge/data/catalog.json')
hashes_before = {path: file_digest(ROOT / path) for path in files}
rows = []
full_results = []
for case, operator, skill, field, extra in cases:
    for mode in ('frames', 'continuous'):
        base = {'operator': operator, 'skill': skill, 'base_attack': 1000,
                'skill_rank': 10, 'timing_mode': mode, **extra}
        for boolean in (False, True):
            boolean_scenario = {**base, field: boolean}
            numeric_scenario = {**base, field: int(boolean)}
            boolean_result, boolean_unmutated = call(boolean_scenario)
            numeric_result, numeric_unmutated = call(numeric_scenario)
            row = {'case': case, 'field': field, 'timing_mode': mode,
                   'boolean': boolean, 'numeric': int(boolean),
                   'boolean_accepted': 'error' not in boolean_result,
                   'numeric_accepted': 'error' not in numeric_result,
                   'public_output_json_equal': serialized(boolean_result) == serialized(numeric_result),
                   'boolean_result_sha256': digest(boolean_result),
                   'numeric_result_sha256': digest(numeric_result),
                   'inputs_unchanged': boolean_unmutated and numeric_unmutated,
                   'boolean_result_summary': summary(boolean_result)}
            rows.append(row)
            full_results.append({'case': case, 'timing_mode': mode,
                'boolean_scenario': boolean_scenario, 'numeric_scenario': numeric_scenario,
                'boolean_result': boolean_result, 'numeric_result': numeric_result})

# Boolean controls are a separate, supported UI contract; they are not counts.
flag_controls = []
for operator, skill, flag in (('char_298_susuro', 2, 'low_cost_healing_target'),
                            ('char_4202_haruka', 2, 'haruka_repeat'),
                            ('char_206_gnosis', 3, 'frozen_at_skill_end'),
                            ('char_4087_ines', 3, 'ines_first_deployment')):
    for value in (False, True):
        result, unchanged = call({'operator': operator, 'skill': skill,
            'base_attack': 1000, 'window_seconds': 10, flag: value})
        flag_controls.append({'operator': operator, 'skill': skill, 'flag': flag,
            'value': value, 'accepted': 'error' not in result, 'input_unchanged': unchanged,
            'result_sha256': digest(result)})

source_files = {
    'character_table': ('68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697',
        ROOT / '.cache/p2-s1-binding/character_table.json'),
    'skill_table': ('86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca',
        ROOT / '.cache/p2-s1-binding/skill_table.json'),
}
sources = []
tables = {}
for name, (expected, path) in source_files.items():
    actual = file_digest(path)
    sources.append({'name': name, 'path': str(path), 'expected_sha256': expected,
                    'actual_sha256': actual, 'sha256_matched': expected == actual,
                    'commit': 'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'})
    if actual != expected:
        raise RuntimeError('Pinned source hash mismatch: ' + name)
    tables[name] = json.loads(path.read_text(encoding='utf-8'))
catalog_operators = catalog()['operators']
selectors = {
    'character_table.char_4087_ines.talents[0].candidates': tables['character_table']['char_4087_ines']['talents'][0]['candidates'],
    'skill_table.skchr_myrtle_2.levels[9]': tables['skill_table']['skchr_myrtle_2']['levels'][9],
    'catalog.char_1037_amiya3.skills[1].levels[9]': catalog_operators['char_1037_amiya3']['skills'][1]['levels'][9],
}
source_receipt = {'recorded_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'sources': sources, 'selectors': selectors,
    'prior_receipts_reused': [
        'research/p2-amiya-input-qualification/source-receipt.json',
        'research/p2-haruka-healing-targets/source-receipt.json',
        'research/p2-deployment-independent-sources/source-and-reproduction.json'],
    'evidence_limit': 'Counts are numeric GUI/API scenario inputs; these facts do not establish actual target acquisition, timing, stacking, or native UI success.'}
hashes_after = {path: file_digest(ROOT / path) for path in files}
receipt = {'recorded_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'public_entrypoint': 'rouge.damage.calculate_damage',
    'scenario_cases': len(cases), 'bool_integer_pairs': len(rows), 'public_calls': len(rows) * 2 + len(flag_controls),
    'accepted_bool_cases': sum(r['boolean_accepted'] for r in rows),
    'rejected_bool_cases': sum(not r['boolean_accepted'] for r in rows),
    'all_bool_integer_results_json_equal': all(r['public_output_json_equal'] for r in rows),
    'all_inputs_unchanged': all(r['inputs_unchanged'] for r in rows),
    'source_files_before': hashes_before, 'source_files_after': hashes_after,
    'audited_files_unchanged': hashes_before == hashes_after,
    'rows': rows, 'supported_boolean_flag_controls': flag_controls,
    'limits': ['Read-only audit, no tracked source edits.',
               'Source/AST GUI inspection only; no actual GUI/Wine/native Windows run.',
               'Unknown target acquisition/real timing/stacking remain unknown.',
               'Does not cover training validation (section 51) or finite lifecycle scheduling (section 52).']}
for filename, value in (('public-pairs.json', receipt), ('public-results.json', full_results),
                        ('source-receipt.json', source_receipt)):
    (OUT / filename).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({key: receipt[key] for key in ('scenario_cases', 'bool_integer_pairs', 'public_calls',
    'accepted_bool_cases', 'rejected_bool_cases', 'all_bool_integer_results_json_equal',
    'all_inputs_unchanged', 'audited_files_unchanged')}, ensure_ascii=False))
for row in rows:
    if row['timing_mode'] == 'frames' and row['case'] in ('myrtle_s2', 'haruka_s1', 'medical_amiya_s2', 'ines_s2'):
        print(row['case'], row['field'], row['boolean'], serialized(row['boolean_result_summary']))
