"""Freeze eight source-bounded native inputs before any fresh project call."""
import gzip
import hashlib
import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUTHOR = Path('/workspace/.continuation/p2-continuous-attacks-text-088-draft')
SOURCE = Path('/workspace/.continuation/p2-section088-candidate-audit')


def typed(v):
    if isinstance(v, dict):
        return {'type': 'dict', 'items': [[typed(k), typed(x)] for k, x in v.items()]}
    if isinstance(v, (list, tuple)):
        return {'type': type(v).__name__, 'items': [typed(x) for x in v]}
    if isinstance(v, float):
        return {'type': 'float', 'hex': v.hex()}
    return {'type': type(v).__name__, 'value': v}


def fingerprint(v):
    return hashlib.sha256(json.dumps(typed(v), ensure_ascii=False, sort_keys=True,
                                    separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def gummy(**extra):
    return {'operator': 'char_196_sunbr', 'skill': 1, 'elite': 1, 'level': 45,
            'skill_rank': 7, 'potential': 2, 'base_attack': 911, 'window_seconds': 0,
            'relic_ids': ['rogue_6_relic_legacy_118'], **extra}


old_guard = 'enemy_in_neural_break 不接受文本条件；请使用布尔值。'
cases = [
    ('native0 actual wait tail with zero observation and empty text', 'new_text_error',
     gummy(continuous_attacks='', timing={'sp_events': {'initial': [], 'cycle': []}})),
    ('native0 missing initial events returns before read', 'whole_unchanged',
     gummy(continuous_attacks='false', timing={'sp_events': {'cycle': []}})),
    ('native0 ready tail reached even with no initial attack slots', 'new_text_error',
     gummy(continuous_attacks='false', timing={'sp_events': {'initial': [], 'cycle': []},
                                              'initial_target_windows': []})),
    ('periodic incoming zero takes incoming branch ahead of outgoing', 'whole_unchanged',
     {'operator': 'char_1044_hsgma2', 'skill': 1, 'elite': 2, 'level': 65,
      'skill_rank': 9, 'base_attack': 911, 'window_seconds': 0,
      'timing_mode': 'continuous', 'incoming_attack_interval': 0,
      'relic_ids': ['rogue_6_relic_legacy_97'], 'continuous_attacks': ''}),
    ('natural extended inactive getter ignores fake true markers', 'whole_unchanged',
     {'operator': 'char_1050_chen3', 'skill': 3, 'elite': 2, 'level': 65,
      'skill_rank': 9, 'base_attack': 911, 'window_seconds': 0,
      'continuous_attacks': 'false', '_continuous_attacks_text_pending': True,
      'continuous_attacks_text_pending': True}),
    ('native tuple nonstring truthiness retained before JSON encoding', 'whole_unchanged',
     {'operator': 'mechanist', 'skill': 1, 'elite': 2, 'level': 65,
      'skill_rank': 9, 'base_attack': 911, 'window_seconds': .125,
      'timing_mode': 'continuous', 'continuous_attacks': (1,)}),
    ('processed neural older error before accumulated text rejection', 'old_error_unchanged',
     {'operator': 'char_4204_mantra', 'skill': 1, 'elite': 2, 'level': 65,
      'skill_rank': 9, 'base_attack': 911, 'window_seconds': 0,
      'enemy_in_neural_break': 'false', 'continuous_attacks': 'false'}),
    ('actual consumer cannot be disabled by caller false markers', 'new_text_error',
     {'operator': 'mechanist', 'skill': 1, 'elite': 2, 'level': 65,
      'skill_rank': 9, 'base_attack': 911, 'window_seconds': .125,
      'continuous_attacks': 'false', '_continuous_attacks_text_pending': False,
      'continuous_attacks_text_pending': False}),
]
assert len(cases) == 8
source_rows = [json.loads(line) for line in gzip.decompress((SOURCE / 'public-source16.jsonl.gz').read_bytes()).splitlines()]
author_rows = json.loads((AUTHOR / 'matrix-plan088.json').read_bytes())
old_fingerprints = {fingerprint(r['input']) for r in source_rows + author_rows}
assert len({fingerprint(x[2]) for x in cases}) == 8
assert all(fingerprint(x[2]) not in old_fingerprints for x in cases)
rows = []
for index, (label, expected, args) in enumerate(cases, 1):
    rows.append({'case': index, 'label': label, 'expected': expected, 'input': deepcopy(args),
                 'input_typed': typed(args), 'native_input_sha256': fingerprint(args),
                 **({'expected_old_error': {'error_type': 'ValueError', 'error_message': old_guard}}
                    if expected == 'old_error_unchanged' else {})})
plan = {'format_version': 1, 'status': 'FROZEN_INDEPENDENT_RISKS_BEFORE_NEW_CALLS',
        'baseline_commit': '1ce970fd30aa3b42d8ef787cde02513f05682b66',
        'author_plan_bound_for_uniqueness': {'source_path': str(AUTHOR / 'matrix-plan088.json'),
                                            'sha256': hashlib.sha256((AUTHOR / 'matrix-plan088.json').read_bytes()).hexdigest()},
        'old_source16_sha256': hashlib.sha256((SOURCE / 'public-source16.jsonl.gz').read_bytes()).hexdigest(),
        'risk_pairs': 8, 'risk_public_calls': 16, 'new_tests_methods': 8,
        'new_tests_max_explicit_public_calls': 32, 'new_tests_max_explicit_context_helper_requests': 32,
        'actual_formatter_entries_instrumented': 'Required during collection, do not infer measured counts.',
        'native_inputs': 'Decode input_typed before API; JSON input is a display binding only and tuple becomes list when encoded.',
        'no_author_product_execution_until_final_freeze': True, 'cases': rows}
target = ROOT / 'formal-risk-plan088.json'
assert not target.exists()
target.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': plan['status'], 'risk_pairs': 8, 'new_calls_so_far': 0,
                  'plan_sha256': hashlib.sha256(target.read_bytes()).hexdigest()}))
