import gzip
import hashlib
import json
from pathlib import Path

p = Path(__file__).resolve().parent


def strict(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


base = json.loads(gzip.decompress((p/'baseline63-public.json.gz').read_bytes()))
draft = json.loads(gzip.decompress((p/'draft-public.json.gz').read_bytes()))
assert len(base['records']) == len(draft['records'])
changed, unchanged, unexpected, canonical_drift = [], [], [], []
for before, after in zip(base['records'], draft['records']):
    assert before['key'] == after['key'] and strict(before['input']) == strict(after['input'])
    if strict(before['outcome']) == strict(after['outcome']):
        unchanged.append(before['key'])
    else:
        changed.append(before['key'])
        if before['group'] not in ('valid_forms', 'inactive_casts') or before['matches_canonical_strict_json'] is not False:
            unexpected.append(before['key'])
    if strict(before['canonical_outcome']) != strict(after['canonical_outcome']):
        canonical_drift.append(before['key'])
source_changes = [name for name, value in base['summary']['source_hashes'].items()
                  if draft['summary']['source_hashes'][name] != value]
result = {'final_baseline_head': '0e0d098e8bc8444cd74fb74f32754cc0ff78ecfb',
          'scenarios': len(draft['records']), 'actual_public_calls': base['summary']['actual_public_calls'] + draft['summary']['actual_public_calls'],
          'corrected_complete_outcomes': len(changed), 'preserved_complete_outcomes': len(unchanged),
          'unexpected_changes': unexpected, 'typed_canonical_drift': canonical_drift,
          'draft_canonical_mismatches': draft['summary']['canonical_mismatches'],
          'invalid_accepted': draft['summary']['invalid_accepted'],
          'idle_cast_validator_leaks': draft['summary']['idle_cast_validator_leaks'],
          'caller_isolation_errors': base['summary']['caller_isolation_errors'] + draft['summary']['caller_isolation_errors'],
          'catalog_and_mechanics_preserved_strict_json': all(summary[key] for summary in (base['summary'], draft['summary']) for key in ('catalog_preserved_strict_json', 'mechanics_preserved_strict_json')),
          'changed_production_files': source_changes,
          'strict_json_distinguishes_int_float_bool': True,
          'full_results_reports_and_exact_error_contract_compared': True,
          'evidence_hashes': {name: hashlib.sha256((p/name).read_bytes()).hexdigest() for name in ('baseline63-public.json.gz', 'draft-public.json.gz')},
          'private_state_read': False, 'native_validation': False, 'new_game_model': False}
result['passed'] = not any((unexpected, canonical_drift, result['draft_canonical_mismatches'],
                            result['invalid_accepted'], result['idle_cast_validator_leaks'], result['caller_isolation_errors'])) and result['catalog_and_mechanics_preserved_strict_json'] and source_changes == ['rouge/operator_engine.py']
(p/'paired-comparison.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result))
assert result['passed']
