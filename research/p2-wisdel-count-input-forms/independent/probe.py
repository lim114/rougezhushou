"""Read-only discovery proof against an explicitly frozen public package."""
from copy import deepcopy
from pathlib import Path
import gzip
import hashlib
import json
import sys
sys.dont_write_bytecode = True

package = Path(sys.argv[1]).resolve()
out = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(package))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.operator_engine import Combat
from rouge.reporting import format_report

OP = 'char_1035_wisdel'
original_option = Combat.option
trace = []


def option(self, key, default=0, maximum=None, integer=False):
    row = {'field': key, 'raw': deepcopy(self.s.get(key, default)), 'integer': integer}
    if key in ('ghost_count', 'ghost_casts'):
        trace.append(row)
    try:
        parsed = original_option(self, key, default, maximum, integer)
    except Exception as exc:
        row.update({'error_type': type(exc).__name__, 'error': str(exc)})
        raise
    row['parsed'] = parsed
    return parsed


Combat.option = option
before_catalog = deepcopy(catalog())
records, isolation_errors = [], []


def outcome(scenario):
    trace.clear()
    original = deepcopy(scenario)
    try:
        result = calculate_damage(scenario)
        value = {'accepted': True, 'result': result, 'report': format_report(result)}
    except Exception as exc:
        value = {'accepted': False, 'error_type': type(exc).__name__, 'error': str(exc)}
    if scenario != original:
        isolation_errors.append(original)
    return value, deepcopy(trace)


def add(key, scenario, canonical=None, group='control'):
    value, calls = outcome(deepcopy(scenario))
    expected, expected_calls = outcome(deepcopy(canonical)) if canonical is not None else (None, [])
    # Compare serialized complete values, preserving numeric JSON types too.
    matches = json.dumps(value, sort_keys=True) == json.dumps(expected, sort_keys=True) if canonical is not None else None
    records.append({'key': key, 'group': group, 'input': scenario, 'outcome': value,
                    'query_trace': calls, 'canonical_input': canonical,
                    'canonical_outcome': expected, 'canonical_trace': expected_calls,
                    'matches_canonical': matches})


count_zero = (0, 0.0, '0', '0.0', '0e0', '-0', ' 0 ')
inactive_casts = (0, 1, -1, 0.5, '0.0', '1.0', 'bad', True, False, None, {}, [])
active_counts = ((1, 1), ('1.0', 1), ('1e0', 1), (3, 3), ('3.0', 3))
active_casts = ((0, 0), ('0', 0), ('0.0', 0), ('-0', 0), ('0e0', 0),
                (1, 1), (1.0, 1), ('1', 1), ('1.0', 1), ('1e0', 1),
                (1000, 1000), ('1000.0', 1000), ('1e3', 1000))
contexts = ({'window_seconds': 10}, {'window_seconds': 0},
            {'window_seconds': 10, 'timing': {'target_disappears_seconds': 0}})
for skill in (1, 2, 3):
    for mode in ('frames', 'continuous'):
        for ci, context in enumerate(contexts):
            base = {'operator': OP, 'skill': skill, 'base_attack': 1000,
                    'timing_mode': mode, **deepcopy(context)}
            for gi, count in enumerate(count_zero):
                for vi, cast in enumerate(inactive_casts):
                    add(f'inactive:{skill}:{mode}:{ci}:{gi}:{vi}',
                        {**base, 'ghost_count': count, 'ghost_casts': cast},
                        {**base, 'ghost_count': 0}, 'inactive_casts')
            for gi, (count, parsed_count) in enumerate(active_counts):
                for vi, (cast, parsed_cast) in enumerate(active_casts):
                    add(f'active:{skill}:{mode}:{ci}:{gi}:{vi}',
                        {**base, 'ghost_count': count, 'ghost_casts': cast},
                        {**base, 'ghost_count': parsed_count, 'ghost_casts': parsed_cast},
                        'valid_active_forms')

invalid = (True, False, -1, '-1', .5, '0.5', 1001, '1001.0', 'NaN', 'Infinity', None, {}, [])
for skill in (1, 2, 3):
    for mode in ('frames', 'continuous'):
        for vi, raw in enumerate(invalid):
            base = {'operator': OP, 'skill': skill, 'base_attack': 1000,
                    'window_seconds': 10, 'timing_mode': mode}
            add(f'invalid_casts:{skill}:{mode}:{vi}',
                {**base, 'ghost_count': 1, 'ghost_casts': raw}, group='invalid_active_casts')
        for vi, raw in enumerate((True, False, -1, .5, 4, '4.0', 'NaN', None, {}, [])):
            add(f'invalid_count:{skill}:{mode}:{vi}',
                {**base, 'ghost_count': raw, 'ghost_casts': 'bad'}, group='invalid_count')

# Other owners continue to ignore both ghost fields completely.
for op, profile in catalog()['operators'].items():
    if op == OP:
        continue
    for skill in range(1, len(profile['skills'])+1):
        for mode in ('frames', 'continuous'):
            base = {'operator': op, 'skill': skill, 'base_attack': 1000,
                    'window_seconds': 10, 'timing_mode': mode}
            add(f'other_owner:{op}:{skill}:{mode}',
                {**base, 'ghost_count': '0.0', 'ghost_casts': {'unused': True}},
                base, 'other_owner')

summary = {'package': str(package), 'cases': len(records),
           'public_calls': sum(1+(r['canonical_input'] is not None) for r in records),
           'canonical_mismatches': [r['key'] for r in records if r['matches_canonical'] is False],
           'queried_casts_with_parsed_zero_count': [r['key'] for r in records
               if r['group'] == 'inactive_casts' and any(t['field']=='ghost_casts' for t in r['query_trace'])],
           'invalid_accepted': [r['key'] for r in records if r['group'] in ('invalid_active_casts','invalid_count')
                                and r['outcome']['accepted']],
           'caller_isolation_errors': isolation_errors, 'catalog_preserved': catalog()==before_catalog,
           'source_hashes': {str(p.relative_to(package)):hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in sorted((package/'rouge').rglob('*'))
                            if p.is_file() and p.suffix in ('.py','.json')},
           'production_edits': 0, 'native_validation': False, 'private_state_read': False,
           'new_mechanism_inferred': False}
with gzip.open(out, 'wt', encoding='utf-8') as handle:
    json.dump({'summary':summary,'records':records},handle,ensure_ascii=False,sort_keys=True)
out.with_suffix('.summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k not in ('source_hashes','canonical_mismatches')},ensure_ascii=False))
