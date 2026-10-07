"""Full public outcomes and actual count query gates, no hypothetical patch."""
import copy
import gzip
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
p = Path(__file__).resolve().parent
package = p/'frozen62'
sys.path.insert(0, str(package))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.operator_engine import Combat
from rouge.relics import mechanics
from rouge.reporting import format_report

catalog_before = copy.deepcopy(catalog())
mechanics_before = copy.deepcopy(mechanics())
queries = []
original_option = Combat.option
isolation_errors = []
calls = 0


def trace(self, key, default=0, maximum=None, integer=False):
    try:
        value = original_option(self, key, default, maximum, integer)
    except Exception as error:
        if key in ('ghost_count', 'ghost_casts'):
            queries.append({'key': key, 'raw': self.s.get(key, default), 'maximum': maximum,
                            'integer': integer, 'error_type': type(error).__name__, 'error': str(error)})
        raise
    if key in ('ghost_count', 'ghost_casts'):
        queries.append({'key': key, 'raw': self.s.get(key, default), 'maximum': maximum,
                        'integer': integer, 'validated_value': value})
    return value


Combat.option = trace


def outcome(args):
    global calls
    calls += 1
    before = copy.deepcopy(args)
    queries.clear()
    try:
        result = calculate_damage(args)
        value = {'accepted': True, 'result': result, 'formatted_report': format_report(result)}
    except Exception as error:
        value = {'accepted': False, 'error_type': type(error).__name__, 'error': str(error)}
    if args != before:
        isolation_errors.append(before)
    return value, list(queries)


records = []
ghost_forms = [(0, 0), ('0', 0), ('0.0', 0), (1, 1), ('1', 1), ('1.0', 1), (3, 3), ('3.0', 3)]
cast_forms = [(0, 0), ('0', 0), ('0.0', 0), (1, 1), ('1', 1), ('1.0', 1), ('1e0', 1), ('1e3', 1000)]
contexts = [{}, {'window_seconds': 0}, {'timing': {'target_disappears_seconds': 0}},
            {'timing': {'target_windows': []}}]
for skill in (1, 2, 3):
    for mode in ('frames', 'continuous'):
        for ci, context in enumerate(contexts):
            plain = {'operator': 'char_1035_wisdel', 'skill': skill, 'base_attack': 1000,
                     'window_seconds': 10, 'timing_mode': mode, **context}
            for gi, (ghosts, parsed_ghosts) in enumerate(ghost_forms):
                for ni, (casts, parsed_casts) in enumerate(cast_forms):
                    args = {**plain, 'ghost_count': ghosts, 'ghost_casts': casts}
                    canonical = {**plain, 'ghost_count': parsed_ghosts, 'ghost_casts': parsed_casts}
                    actual, actual_queries = outcome(copy.deepcopy(args))
                    expected, expected_queries = outcome(copy.deepcopy(canonical))
                    records.append({'key': f'forms:{skill}:{mode}:{ci}:{gi}:{ni}', 'group': 'valid_forms',
                                    'input': args, 'outcome': actual, 'queries': actual_queries,
                                    'canonical_input': canonical, 'canonical_outcome': expected,
                                    'canonical_queries': expected_queries, 'complete_outcomes_equal': actual == expected})
        for ghosts in (0, '0.0', 1):
            for vi, raw in enumerate((True, False, None, {}, [], 'bad', -1, '0.5', '1001')):
                args = {'operator': 'char_1035_wisdel', 'skill': skill, 'base_attack': 1000,
                        'window_seconds': 10, 'timing_mode': mode,
                        'ghost_count': ghosts, 'ghost_casts': raw}
                canonical = {**args, 'ghost_count': int(float(ghosts)), 'ghost_casts': 0}
                actual, actual_queries = outcome(copy.deepcopy(args))
                expected, expected_queries = outcome(copy.deepcopy(canonical))
                records.append({'key': f'cast_gate:{skill}:{mode}:{ghosts!r}:{vi}', 'group': 'cast_gate',
                                'input': args, 'outcome': actual, 'queries': actual_queries,
                                'inactive_count': int(float(ghosts)) == 0,
                                'canonical_input': canonical, 'canonical_outcome': expected,
                                'canonical_queries': expected_queries, 'complete_outcomes_equal': actual == expected})
summary = {'discovery_baseline_head': json.loads((p/'freeze62.json').read_text())['baseline_head'],
           'package': str(package), 'scenarios': len(records), 'actual_public_calls': calls,
           'valid_form_mismatches': [r['key'] for r in records if r['group'] == 'valid_forms' and not r['complete_outcomes_equal']],
           'inactive_cast_contract_mismatches': [r['key'] for r in records if r['group'] == 'cast_gate' and r['inactive_count'] and not r['complete_outcomes_equal']],
           'ghost_casts_queried_with_parsed_zero_ghosts': [r['key'] for r in records if r['group'] == 'cast_gate' and r['inactive_count'] and any(q['key'] == 'ghost_casts' for q in r['queries'])],
           'caller_isolation_errors': isolation_errors, 'catalog_preserved': catalog() == catalog_before,
           'mechanics_preserved': mechanics() == mechanics_before, 'private_state_read': False,
           'production_edits': 0, 'hypothetical_patch': False, 'native_validation': False}
raw = json.dumps({'summary': summary, 'records': records}, ensure_ascii=False, sort_keys=True).encode()
out = p/'readonly-public.json.gz'
with out.open('wb') as handle:
    with gzip.GzipFile(filename='', mode='wb', fileobj=handle, mtime=0) as zipped:
        zipped.write(raw)
assert gzip.decompress(out.read_bytes()) == raw
compact = {k: v for k, v in summary.items() if not isinstance(v, list)}
compact.update({key+'_count': len(summary[key]) for key in ('valid_form_mismatches', 'inactive_cast_contract_mismatches', 'ghost_casts_queried_with_parsed_zero_ghosts', 'caller_isolation_errors')})
compact['compressed_evidence'] = {'gzip_sha256': hashlib.sha256(out.read_bytes()).hexdigest(),
                                  'gzip_bytes': out.stat().st_size, 'raw_sha256': hashlib.sha256(raw).hexdigest(),
                                  'raw_bytes': len(raw), 'decompression_verified': True}
(p/'readonly-probe-receipt.json').write_text(json.dumps(compact, indent=2)+'\n')
print(json.dumps(compact))
