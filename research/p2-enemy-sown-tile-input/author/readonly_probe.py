"""Complete strict JSON public outcomes from frozen64, no hypothetical patch."""
import copy
import gzip
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
p = Path(__file__).resolve().parent
package = p/'frozen64'
sys.path.insert(0, str(package))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.relics import mechanics
from rouge.reporting import format_report


def strict(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


catalog_before, mechanics_before = strict(catalog()), strict(mechanics())
isolation_errors, records = [], []
cache = {}
calls = 0


def outcome(args):
    global calls
    identifier = strict(args)
    if identifier in cache:
        return cache[identifier]
    calls += 1
    before = strict(args)
    try:
        result = calculate_damage(args)
        value = {'accepted': True, 'result': result, 'formatted_report': format_report(result)}
    except Exception as error:
        value = {'accepted': False, 'error_type': type(error).__name__, 'error': str(error)}
    if strict(args) != before:
        isolation_errors.append(before)
    cache[identifier] = value
    return value


def add(key, group, plain, raw, include=True):
    args = {**plain, 'enemy_on_sown_tile': raw} if include else plain
    value = outcome(copy.deepcopy(args))
    false = outcome({**copy.deepcopy(plain), 'enemy_on_sown_tile': False})
    true = outcome({**copy.deepcopy(plain), 'enemy_on_sown_tile': True})
    records.append({'key': key, 'group': group, 'input': args, 'outcome': value,
                    'false_input': {**plain, 'enemy_on_sown_tile': False}, 'false_outcome': false,
                    'true_input': {**plain, 'enemy_on_sown_tile': True}, 'true_outcome': true,
                    'matches_false_strict_json': strict(value) == strict(false),
                    'matches_true_strict_json': strict(value) == strict(true)})


forms = [False, True, 0, 1, None, 'false', 'true', '', '0', '1', 'False', ' off ', {}, []]
contexts = [{}, {'window_seconds': 0}, {'timing': {'target_disappears_seconds': 0}},
            {'timing': {'target_windows': []}}, {'healing_targets': 0},
            {'four_sui': True}, {'four_sui': True, 'window_seconds': 50}]
for mode in ('frames', 'continuous'):
    for rank in (1, 7, 10):
        for ci, context in enumerate(contexts):
            plain = {'operator': 'char_2025_shu', 'skill': 3, 'skill_rank': rank,
                     'base_attack': 1000, 'window_seconds': 10, 'timing_mode': mode, **context}
            for vi, raw in enumerate(forms):
                add(f'active:{mode}:{rank}:{ci}:{vi}', 'active', plain, raw)
            add(f'missing:{mode}:{rank}:{ci}', 'active_missing', plain, None, include=False)
    for elite in (0, 1):
        for rank in (1, 10):
            plain = {'operator': 'char_2025_shu', 'skill': 3, 'elite': elite, 'skill_rank': rank,
                     'base_attack': 1000, 'window_seconds': 10, 'timing_mode': mode}
            for vi, raw in enumerate(forms):
                add(f'locked:{mode}:{elite}:{rank}:{vi}', 'qualification', plain, raw)

for operator, profile in catalog()['operators'].items():
    for skill in range(1, len(profile['skills'])+1):
        if operator == 'char_2025_shu' and skill == 3:
            continue
        for mode in ('frames', 'continuous'):
            plain = {'operator': operator, 'skill': skill, 'base_attack': 1000,
                     'window_seconds': 10, 'timing_mode': mode}
            add(f'inactive:{operator}:{skill}:{mode}', 'inactive', plain, 'false')

summary = {'discovery_baseline_head': json.loads((p/'freeze64.json').read_text())['baseline_head'],
           'scenarios': len(records), 'actual_public_calls': calls,
           'groups': {group: sum(r['group'] == group for r in records) for group in sorted({r['group'] for r in records})},
           'active_text_false_true_match': [r['key'] for r in records if r['group'] == 'active' and r['input']['enemy_on_sown_tile'] == 'false' and r['matches_true_strict_json']],
           'active_text_false_false_mismatch': [r['key'] for r in records if r['group'] == 'active' and r['input']['enemy_on_sown_tile'] == 'false' and not r['matches_false_strict_json']],
           'qualification_drift': [r['key'] for r in records if r['group'] == 'qualification' and not r['matches_false_strict_json']],
           'inactive_drift': [r['key'] for r in records if r['group'] == 'inactive' and not r['matches_false_strict_json']],
           'caller_isolation_errors': isolation_errors, 'catalog_preserved_strict_json': strict(catalog()) == catalog_before,
           'mechanics_preserved_strict_json': strict(mechanics()) == mechanics_before,
           'strict_json_distinguishes_numeric_and_bool': True, 'production_edits': 0,
           'patch_written': False, 'private_state_read': False, 'native_validation': False}
raw = strict({'summary': summary, 'records': records}).encode()
destination = p/'readonly-public.json.gz'
with destination.open('wb') as handle:
    with gzip.GzipFile(filename='', mode='wb', fileobj=handle, mtime=0) as zipped:
        zipped.write(raw)
assert gzip.decompress(destination.read_bytes()) == raw
compact = {k: v for k, v in summary.items() if not isinstance(v, list)}
compact.update({key+'_count': len(summary[key]) for key in ('active_text_false_true_match', 'active_text_false_false_mismatch', 'qualification_drift', 'inactive_drift', 'caller_isolation_errors')})
compact['compressed_evidence'] = {'gzip_bytes': destination.stat().st_size,
                                  'gzip_sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
                                  'raw_bytes': len(raw), 'raw_sha256': hashlib.sha256(raw).hexdigest(),
                                  'decompression_verified': True}
(p/'readonly-probe-receipt.json').write_text(json.dumps(compact, indent=2)+'\n')
print(json.dumps(compact))
