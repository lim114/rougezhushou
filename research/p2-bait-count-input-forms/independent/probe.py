"""Independent public probes; use only the named frozen/draft package."""
from copy import deepcopy
from pathlib import Path
import gzip
import hashlib
import json
import sys
sys.dont_write_bytecode = True

package = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(package))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.reporting import format_report

OP = 'char_1042_phatm2'
before_catalog = deepcopy(catalog())
records = []
isolation_errors = []


def outcome(scenario):
    caller = deepcopy(scenario)
    try:
        result = calculate_damage(scenario)
        value = {'accepted': True, 'result': result, 'report': format_report(result)}
    except Exception as exc:
        value = {'accepted': False, 'error_type': type(exc).__name__, 'error': str(exc)}
    if scenario != caller:
        isolation_errors.append(repr(caller))
    return value


def add(key, scenario, canonical=None, group='control'):
    value = outcome(deepcopy(scenario))
    expected = outcome(deepcopy(canonical)) if canonical is not None else None
    records.append({'key': key, 'group': group, 'input': scenario, 'outcome': value,
                    'canonical_input': canonical, 'canonical_outcome': expected,
                    'matches_canonical': value == expected if expected is not None else None})


forms = [(0, 0), (0.0, 0), ('0', 0), ('0.0', 0), ('-0', 0), (' 0 ', 0), ('0e0', 0),
         (1, 1), (1.0, 1), ('1', 1), ('1.0', 1), ('1e0', 1), ('+1', 1), (' 1 ', 1),
         (100, 100), ('100.0', 100), ('1e2', 100)]
contexts = [{'window_seconds': 10}, {'window_seconds': 0},
            {'window_seconds': 10, 'timing': {'target_disappears_seconds': 0}},
            {'window_seconds': 10, 'timing': {'target_windows': []}},
            {'window_seconds': 10, 'relic_ids': ['rogue_6_relic_fight_22']},
            {'window_seconds': 10, 'enemy_buildup_resistance': 100}]
for mode in ('frames', 'continuous'):
    for rank in (1, 7, 10):
        for ci, context in enumerate(contexts):
            base = {'operator': OP, 'skill': 2, 'skill_rank': rank, 'base_attack': 1000,
                    'timing_mode': mode, **deepcopy(context)}
            base['timing'] = dict(context.get('timing', {}))
            for vi, (raw, parsed) in enumerate(forms):
                add(f'active:{mode}:{rank}:{ci}:{vi}', {**base, 'bait_triggers': raw},
                    {**base, 'bait_triggers': parsed}, 'valid_forms')

invalid = [-1, '-1.0', 0.5, '0.5', 101, '101.0', 'NaN', 'Infinity', '-Infinity',
           None, '', 'bad', {}, [], '1e309']
for mode in ('frames', 'continuous'):
    for vi, raw in enumerate(invalid):
        add(f'invalid:{mode}:{vi}', {'operator': OP, 'skill': 2, 'base_attack': 1000,
                                   'window_seconds': 10, 'timing_mode': mode,
                                   'bait_triggers': raw}, group='invalid')

# Every other catalog skill must continue to ignore this inactive option.
for op, profile in catalog()['operators'].items():
    for skill in range(1, len(profile['skills']) + 1):
        if op == OP and skill == 2:
            continue
        for mode in ('frames', 'continuous'):
            base = {'operator': op, 'skill': skill, 'base_attack': 1000,
                    'window_seconds': 10, 'timing_mode': mode}
            add(f'inactive:{op}:{skill}:{mode}', {**base, 'bait_triggers': '0.0'},
                base, 'inactive')

for skill in (1, 3):
    for mode in ('frames', 'continuous'):
        base = {'operator': OP, 'skill': skill, 'base_attack': 1000,
                'window_seconds': 10, 'timing_mode': mode}
        for vi, raw in enumerate((True, False, None, {}, [], '1.0', 'NaN')):
            add(f'inactive_phatm2:{skill}:{mode}:{vi}', {**base, 'bait_triggers': raw},
                base, 'inactive')

catalog_preserved = catalog() == before_catalog
summary = {
    'package': str(package), 'cases': len(records),
    'public_calls': sum(1 + (r['canonical_input'] is not None) for r in records),
    'valid_forms': sum(r['group'] == 'valid_forms' for r in records),
    'canonical_mismatches': [r['key'] for r in records if r['matches_canonical'] is False],
    'invalid_accepted': [r['key'] for r in records if r['group'] == 'invalid' and r['outcome']['accepted']],
    'caller_isolation_errors': isolation_errors,
    'catalog_preserved': catalog_preserved,
    'source_hashes': {str(p.relative_to(package)): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in sorted((package/'rouge').rglob('*'))
                      if p.is_file() and p.suffix in ('.py', '.json')},
    'native_validation': False,
    'new_mechanism_inferred': False,
}
payload = {'summary': summary, 'records': records}
out = Path(sys.argv[2]).resolve()
with gzip.open(out, 'wt', encoding='utf-8') as handle:
    json.dump(payload, handle, ensure_ascii=False, sort_keys=True)
out.with_suffix('.summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k != 'source_hashes'}, ensure_ascii=False))
