"""Full public output probes from one explicitly named immutable package."""
import copy
import gzip
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
package = Path(sys.argv[1]).resolve()
destination = Path(sys.argv[2]).resolve()
sys.path.insert(0, str(package))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.relics import mechanics
from rouge.reporting import format_report

before_catalog = copy.deepcopy(catalog())
before_mechanics = copy.deepcopy(mechanics())
calls = 0
isolation_errors = []
records = []
canonical_cache = {}


def outcome(args):
    global calls
    calls += 1
    original = copy.deepcopy(args)
    try:
        result = calculate_damage(args)
        value = {'accepted': True, 'result': result, 'formatted_report': format_report(result)}
    except Exception as error:
        value = {'accepted': False, 'error_type': type(error).__name__, 'error': str(error)}
    if args != original:
        isolation_errors.append(original)
    return value


def add(key, group, args, canonical=None):
    result = outcome(copy.deepcopy(args))
    expected = None
    if canonical is not None:
        identifier = json.dumps(canonical, sort_keys=True)
        if identifier not in canonical_cache:
            canonical_cache[identifier] = outcome(copy.deepcopy(canonical))
        expected = canonical_cache[identifier]
    records.append({'key': key, 'group': group, 'input': args, 'outcome': result,
                    'canonical_input': canonical, 'canonical_outcome': expected,
                    'matches_canonical': result == expected if canonical is not None else None})


forms = [(0, 0), (0.0, 0), ('0', 0), ('0.0', 0), ('-0', 0), ('0e0', 0), (' 0 ', 0),
         (1, 1), (1.0, 1), ('1', 1), ('1.0', 1), ('1e0', 1), (' 1 ', 1),
         (100, 100), ('100.0', 100), ('1e2', 100)]
contexts = [{}, {'window_seconds': 0}, {'timing': {'target_disappears_seconds': 0}},
            {'timing': {'target_windows': []}}, {'enemy_buildup_resistance': 100},
            {'relic_ids': ['rogue_6_relic_fight_22']},
            {'timing': {'target_disappears_seconds': 2}, 'window_seconds': 50}]
for mode in ('frames', 'continuous'):
    for rank in range(1, 11):
        for ci, context in enumerate(contexts):
            plain = {'operator': 'char_1042_phatm2', 'skill': 2, 'base_attack': 1000,
                     'window_seconds': 10, 'skill_rank': rank, 'timing_mode': mode, **context}
            for vi, (raw, number) in enumerate(forms):
                add(f'active:{mode}:{rank}:{ci}:{vi}', 'valid_alias',
                    {**plain, 'bait_triggers': raw}, {**plain, 'bait_triggers': number})
            add(f'absent:{mode}:{rank}:{ci}', 'absent', plain,
                {**plain, 'bait_triggers': 0})

invalid = [True, False, -1, '-1.0', .5, '0.5', 101, '101.0', 'NaN', 'Infinity',
           '-Infinity', '1e309', None, {}, [], '', 'bad']
for mode in ('frames', 'continuous'):
    plain = {'operator': 'char_1042_phatm2', 'skill': 2, 'base_attack': 1000,
             'window_seconds': 10, 'timing_mode': mode}
    for vi, raw in enumerate(invalid):
        add(f'invalid:{mode}:{vi}', 'invalid', {**plain, 'bait_triggers': raw})
    for operator, skill in (('char_1042_phatm2', 1), ('char_1042_phatm2', 3),
                            ('silverash', 3), ('mechanist', 3)):
        plain = {'operator': operator, 'skill': skill, 'base_attack': 1000,
                 'window_seconds': 10, 'timing_mode': mode}
        for vi, raw in enumerate(('0.0', '1.0', True, False, None, {}, [], 'bad')):
            add(f'inactive:{operator}:{skill}:{mode}:{vi}', 'inactive',
                {**plain, 'bait_triggers': raw}, plain)

summary = {'package': str(package), 'scenarios': len(records), 'actual_public_calls': calls,
           'counts_by_group': {group: sum(r['group'] == group for r in records)
                               for group in sorted({r['group'] for r in records})},
           'canonical_mismatches': [r['key'] for r in records if r['matches_canonical'] is False],
           'invalid_accepted': [r['key'] for r in records if r['group'] == 'invalid' and r['outcome']['accepted']],
           'caller_isolation_errors': isolation_errors,
           'catalog_preserved': catalog() == before_catalog,
           'mechanics_preserved': mechanics() == before_mechanics,
           'source_hashes': {str(p.relative_to(package)): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in sorted((package / 'rouge').rglob('*'))
                             if p.is_file() and p.suffix in ('.py', '.json')},
           'private_state_read': False, 'native_validation': False, 'new_game_model': False}
payload = json.dumps({'summary': summary, 'records': records}, ensure_ascii=False, sort_keys=True).encode()
with destination.open('wb') as handle:
    with gzip.GzipFile(filename='', mode='wb', fileobj=handle, mtime=0) as zipped:
        zipped.write(payload)
assert gzip.decompress(destination.read_bytes()) == payload
compact = {k: v for k, v in summary.items() if k not in ('canonical_mismatches', 'source_hashes')}
compact.update({'canonical_mismatch_count': len(summary['canonical_mismatches']),
                'raw_bytes': len(payload), 'raw_sha256': hashlib.sha256(payload).hexdigest(),
                'gzip_bytes': destination.stat().st_size,
                'gzip_sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
                'decompression_verified': True})
destination.with_suffix('.summary.json').write_text(json.dumps(compact, indent=2) + '\n')
print(json.dumps(compact))
