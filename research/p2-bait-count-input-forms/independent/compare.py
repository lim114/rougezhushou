from pathlib import Path
import gzip
import hashlib
import json

root = Path(__file__).resolve().parent


def read(name):
    with gzip.open(root/name, 'rt', encoding='utf-8') as handle:
        return json.load(handle)


base = read('baseline61-public.json.gz')
draft = read('draft-public.json.gz')
assert len(base['records']) == len(draft['records'])
changed, unchanged, unexpected, canonical_drift = [], [], [], []
for before, after in zip(base['records'], draft['records']):
    assert before['key'] == after['key'] and before['input'] == after['input']
    key = before['key']
    if before['outcome'] == after['outcome']:
        unchanged.append(key)
    else:
        changed.append(key)
        if before['group'] != 'valid_forms' or before['matches_canonical'] is not False:
            unexpected.append(key)
    if before['canonical_outcome'] != after['canonical_outcome']:
        canonical_drift.append(key)
source_changes = [name for name, value in base['summary']['source_hashes'].items()
                  if draft['summary']['source_hashes'].get(name) != value]
summary = {
    'cases': len(draft['records']),
    'public_calls': base['summary']['public_calls']+draft['summary']['public_calls'],
    'changed_cases': len(changed), 'unchanged_cases': len(unchanged),
    'unexpected_changes': unexpected, 'typed_canonical_outcome_changes': canonical_drift,
    'draft_canonical_mismatches': draft['summary']['canonical_mismatches'],
    'invalid_accepted': draft['summary']['invalid_accepted'],
    'caller_isolation_errors': draft['summary']['caller_isolation_errors'],
    'catalog_preserved': draft['summary']['catalog_preserved'],
    'changed_existing_sources': source_changes,
    'existing_source_change_scope_ok': source_changes == ['rouge/operator_engine.py'],
    'native_validation': False,
    'new_mechanism_inferred': False,
    'evidence_sha256': {name:hashlib.sha256((root/name).read_bytes()).hexdigest()
                       for name in ('baseline61-public.json.gz','draft-public.json.gz')},
}
summary['passed'] = not any((unexpected, canonical_drift, summary['draft_canonical_mismatches'],
                             summary['invalid_accepted'], summary['caller_isolation_errors'])) and (
    summary['catalog_preserved'] and summary['existing_source_change_scope_ok'])
(root/'matrix-comparison.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False))
assert summary['passed']
