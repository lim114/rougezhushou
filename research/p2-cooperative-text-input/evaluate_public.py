"""Evaluate the same complete public scenarios on exact64 or final69 draft."""
from copy import deepcopy
import gzip
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
package = sys.argv[1]
assert package in ('baseline64', 'draft69')
sys.path.insert(0, str(ROOT / package))
from rouge.catalog import catalog
from rouge.damage import calculate_damage

with gzip.open(ROOT / 'prior-readonly-audit/public-full-outcomes.json.gz', 'rt', encoding='utf-8') as inp:
    previous = json.load(inp)
records = {name: {'scenario': row['scenario']} for name, row in previous['cases'].items()}
for mode in ('frames', 'continuous'):
    vectors = [
        {'preexisting_fragile': text, 'cooperative': value}
        for text in ('false', '') for value in ('unknown', '', True)]
    vectors += [{'elite': 0, 'skill_rank': 7, 'cooperative': 'unknown'},
                {'elite': 1, 'skill_rank': 7, 'cooperative': 'false'},
                {'skill_rank': True, 'cooperative': 'unknown'},
                {'skill': True, 'cooperative': 'false'},
                {'level': 0, 'cooperative': 'unknown'},
                {'potential': 0, 'cooperative': 'unknown'}]
    for index, extra in enumerate(vectors):
        records[f'priority:{mode}:{index}'] = {'scenario': {
            'operator': 'silverash', 'skill': 3, 'base_attack': 1000,
            'timing_mode': mode, 'window_seconds': 10, **extra}}
before_catalog = deepcopy(catalog())
for name, row in records.items():
    args = deepcopy(row['scenario'])
    before = deepcopy(args)
    try:
        row['outcome'] = {'result': calculate_damage(args), 'error': None}
    except Exception as error:
        row['outcome'] = {'result': None, 'error': {'type': type(error).__name__, 'message': str(error)}}
    assert args == before, name
assert catalog() == before_catalog
with gzip.open(ROOT / (package + '-public-full-outcomes.json.gz'), 'wt', encoding='utf-8') as out:
    json.dump({'package': package, 'baseline_head': 'f4ca1c97278c5354f32940f56db2de60bbd21423',
               'cases': records, 'all_inputs_and_catalog_preserved': True}, out, ensure_ascii=False, indent=2)
    out.write('\n')
print(json.dumps({'package': package, 'public_calls': len(records),
                  'successes': sum(v['outcome']['error'] is None for v in records.values()),
                  'errors': sum(v['outcome']['error'] is not None for v in records.values())}))
