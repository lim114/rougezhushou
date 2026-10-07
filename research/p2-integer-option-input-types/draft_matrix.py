"""Reuse the finished baseline corpus; pair full returns from explicit draft."""
import copy
import gzip
import hashlib
import json
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent
PACKAGE = OUT / 'draft'
sys.dont_write_bytecode = True
sys.path.insert(0, str(PACKAGE))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.relics import mechanics
import rouge.operator_engine
assert Path(rouge.operator_engine.__file__).resolve().is_relative_to(PACKAGE)
baseline = json.loads((OUT / 'baseline-public-results.json').read_text())
before_catalog = copy.deepcopy(catalog())
before_mechanics = copy.deepcopy(mechanics())
freeze = json.loads((OUT / 'freeze.json').read_text())
before_sources = {rel: hashlib.sha256((PACKAGE / rel).read_bytes()).hexdigest()
                  for rel in freeze['public_source_hashes']}
canonical = lambda value: json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
rows = []
changed = []
preserved = []
failures = []
for index, original in enumerate(baseline['complete_public_cases']):
    args = copy.deepcopy(original['scenario'])
    before = copy.deepcopy(args)
    try:
        outcome = {'accepted': True, 'result': calculate_damage(args)}
    except Exception as error:
        outcome = {'accepted': False, 'error_type': type(error).__name__, 'error': str(error)}
    assert args == before
    row = {'index': index, 'group': original['group'], 'field': original['field'],
           'identity': original['identity'], 'scenario': before, 'outcome': outcome}
    rows.append(row)
    expected_rejection = (original['group'] == 'active_integer'
        and original['identity'] in ('false', 'true')
        and original['field_queried_as_integer'] and original['outcome']['accepted'])
    if expected_rejection:
        expected = {'accepted': False, 'error_type': 'ValueError',
                    'error': original['field'] + '需要范围内的有限非负整数。'}
        if canonical(outcome) != canonical(expected):
            failures.append({'index': index, 'problem': 'wrong raw bool rejection'})
        changed.append(index)
    else:
        if canonical(outcome) != canonical(original['outcome']):
            failures.append({'index': index, 'problem': 'preserved whole public outcome changed'})
        preserved.append(index)

assert catalog() == before_catalog
assert mechanics() == before_mechanics
after_sources = {rel: hashlib.sha256((PACKAGE / rel).read_bytes()).hexdigest()
                 for rel in freeze['public_source_hashes']}
assert after_sources == before_sources
summary = {'baseline_head': freeze['baseline_head'], 'pairs': len(rows),
           'new_draft_public_calls': len(rows), 'baseline_completed_calls_reused': len(rows),
           'total_public_calls_both_packages': len(rows) * 2,
           'queried_raw_bool_rejections': len(changed), 'full_outcomes_preserved': len(preserved),
           'changed_indices': changed, 'preserved_indices': preserved, 'failures': failures,
           'new_source_changes': [rel for rel, sha in freeze['public_source_hashes'].items()
                                   if before_sources[rel] != sha],
           'caller_input_unchanged': True, 'catalog_and_mechanics_unchanged': True,
           'source_drift': [], 'private_state_read': False, 'native_validation': False}
(OUT / 'matrix-comparison.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
raw = (json.dumps({'baseline_head': freeze['baseline_head'], 'package': str(PACKAGE),
                   'complete_public_cases': rows}, ensure_ascii=False, indent=2) + '\n').encode()
(OUT / 'draft-public-results.json').write_bytes(raw)
compressed = gzip.compress(raw, compresslevel=9, mtime=0)
(OUT / 'draft-public-results.json.gz').write_bytes(compressed)
assert gzip.decompress(compressed) == raw
(OUT / 'draft-compression-receipt.json').write_text(json.dumps({
    'source_sha256': hashlib.sha256(raw).hexdigest(), 'source_bytes': len(raw),
    'gzip_sha256': hashlib.sha256(compressed).hexdigest(), 'gzip_bytes': len(compressed),
    'decompression_verified': True}, indent=2) + '\n')
print(json.dumps({key: summary[key] for key in ('pairs', 'queried_raw_bool_rejections',
                  'full_outcomes_preserved', 'failures', 'new_source_changes')}))
assert not failures
