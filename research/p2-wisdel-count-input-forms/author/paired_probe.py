"""Strict JSON public pairs from the explicitly named final package."""
import copy
import gzip
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
p = Path(__file__).resolve().parent
package = Path(sys.argv[1]).resolve()
destination = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(package))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.operator_engine import Combat
from rouge.relics import mechanics
from rouge.reporting import format_report


def strict(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


catalog_before, mechanics_before = strict(catalog()), strict(mechanics())
queries, records, isolation_errors = [], [], []
calls = 0
canonical_cache = {}
original_option = Combat.option


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
    before = strict(args)
    queries.clear()
    try:
        result = calculate_damage(args)
        value = {'accepted': True, 'result': result, 'formatted_report': format_report(result)}
    except Exception as error:
        value = {'accepted': False, 'error_type': type(error).__name__, 'error': str(error)}
    if strict(args) != before:
        isolation_errors.append(before)
    return value, list(queries)


def add(key, group, args, canonical=None):
    actual, trace_actual = outcome(copy.deepcopy(args))
    expected, trace_expected = None, None
    if canonical is not None:
        identifier = strict(canonical)
        if identifier not in canonical_cache:
            canonical_cache[identifier] = outcome(copy.deepcopy(canonical))
        expected, trace_expected = canonical_cache[identifier]
    records.append({'key': key, 'group': group, 'input': args, 'outcome': actual,
                    'queries': trace_actual, 'canonical_input': canonical,
                    'canonical_outcome': expected, 'canonical_queries': trace_expected,
                    'matches_canonical_strict_json': strict(actual) == strict(expected) if canonical is not None else None})


forms = [(0, 0, 0, 0), ('0', '1', 0, 0), ('0.0', '1.0', 0, 0), (1, 1, 1, 1),
         ('1.0', '1.0', 1, 1), ('3.0', '1e0', 3, 1), ('3e0', '1e3', 3, 1000),
         ('1', '0.0', 1, 0)]
contexts = [{}, {'window_seconds': 0}, {'timing': {'target_disappears_seconds': 0}},
            {'timing': {'target_windows': []}}]
for skill in (1, 2, 3):
    for mode in ('frames', 'continuous'):
        for rank in range(1, 11):
            for ci, context in enumerate(contexts):
                plain = {'operator': 'char_1035_wisdel', 'skill': skill, 'base_attack': 1000,
                         'window_seconds': 10, 'skill_rank': rank, 'timing_mode': mode, **context}
                for vi, (ghosts, casts, parsed_ghosts, parsed_casts) in enumerate(forms):
                    add(f'forms:{skill}:{mode}:{rank}:{ci}:{vi}', 'valid_forms',
                        {**plain, 'ghost_count': ghosts, 'ghost_casts': casts},
                        {**plain, 'ghost_count': parsed_ghosts, 'ghost_casts': parsed_casts})
        for ci, context in enumerate(contexts):
            plain = {'operator': 'char_1035_wisdel', 'skill': skill, 'base_attack': 1000,
                     'window_seconds': 10, 'timing_mode': mode, **context}
            for gi, ghosts in enumerate((0, 0.0, '0', '0.0', '0e0')):
                for vi, casts in enumerate((True, False, None, {}, [], 'bad', -1, '0.5', '1001', '1.0')):
                    add(f'idle_casts:{skill}:{mode}:{ci}:{gi}:{vi}', 'inactive_casts',
                        {**plain, 'ghost_count': ghosts, 'ghost_casts': casts},
                        {**plain, 'ghost_count': 0, 'ghost_casts': 0})
        plain = {'operator': 'char_1035_wisdel', 'skill': skill, 'base_attack': 1000,
                 'window_seconds': 10, 'timing_mode': mode}
        invalid = (True, False, None, {}, [], 'bad', -1, '0.5', 'NaN', 'Infinity')
        for vi, value in enumerate(invalid):
            add(f'invalid_ghosts:{skill}:{mode}:{vi}', 'invalid',
                {**plain, 'ghost_count': value, 'ghost_casts': 0})
            add(f'invalid_casts:{skill}:{mode}:{vi}', 'invalid',
                {**plain, 'ghost_count': 1, 'ghost_casts': value})
        for field, value in (('ghost_count', 4), ('ghost_count', '4.0'),
                             ('ghost_casts', 1001), ('ghost_casts', '1001.0')):
            add(f'max:{skill}:{mode}:{field}:{value!r}', 'invalid',
                {**plain, 'ghost_count': 1, 'ghost_casts': 0, field: value})

for operator, profile in catalog()['operators'].items():
    if operator == 'char_1035_wisdel':
        continue
    for skill in range(1, len(profile['skills'])+1):
        for mode in ('frames', 'continuous'):
            plain = {'operator': operator, 'skill': skill, 'base_attack': 1000,
                     'window_seconds': 10, 'timing_mode': mode}
            add(f'other:{operator}:{skill}:{mode}', 'other_operator',
                {**plain, 'ghost_count': None, 'ghost_casts': {}}, plain)

summary = {'baseline_head': '0e0d098e8bc8444cd74fb74f32754cc0ff78ecfb', 'package': str(package),
           'scenarios': len(records), 'actual_public_calls': calls,
           'groups': {group: sum(r['group'] == group for r in records) for group in sorted({r['group'] for r in records})},
           'canonical_mismatches': [r['key'] for r in records if r['matches_canonical_strict_json'] is False],
           'invalid_accepted': [r['key'] for r in records if r['group'] == 'invalid' and r['outcome']['accepted']],
           'idle_cast_validator_leaks': [r['key'] for r in records if r['group'] == 'inactive_casts' and any(q['key'] == 'ghost_casts' for q in r['queries'])],
           'caller_isolation_errors': isolation_errors,
           'catalog_preserved_strict_json': strict(catalog()) == catalog_before,
           'mechanics_preserved_strict_json': strict(mechanics()) == mechanics_before,
           'source_hashes': {str(f.relative_to(package)): hashlib.sha256(f.read_bytes()).hexdigest()
                             for f in sorted((package/'rouge').rglob('*')) if f.is_file() and f.suffix in ('.py', '.json')},
           'strict_json_distinguishes_int_float_bool': True, 'private_state_read': False,
           'native_validation': False, 'new_game_model': False}
payload = strict({'summary': summary, 'records': records}).encode()
with destination.open('wb') as handle:
    with gzip.GzipFile(filename='', mode='wb', fileobj=handle, mtime=0) as zipped:
        zipped.write(payload)
assert gzip.decompress(destination.read_bytes()) == payload
compact = {k: v for k, v in summary.items() if k not in ('source_hashes', 'canonical_mismatches')}
compact.update({'canonical_mismatch_count': len(summary['canonical_mismatches']),
                'raw_bytes': len(payload), 'raw_sha256': hashlib.sha256(payload).hexdigest(),
                'gzip_bytes': destination.stat().st_size,
                'gzip_sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
                'decompression_verified': True})
destination.with_suffix('.summary.json').write_text(json.dumps(compact, indent=2)+'\n')
print(json.dumps(compact))
