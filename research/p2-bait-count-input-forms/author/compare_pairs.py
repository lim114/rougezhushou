import gzip
import hashlib
import json
from pathlib import Path

p = Path(__file__).resolve().parent
before = json.loads(gzip.decompress((p / 'baseline61-public.json.gz').read_bytes()))
after = json.loads(gzip.decompress((p / 'draft-public.json.gz').read_bytes()))
assert len(before['records']) == len(after['records'])
changed, unchanged, unexpected, canonical_changed = [], [], [], []
for baseline, draft in zip(before['records'], after['records']):
    assert baseline['key'] == draft['key'] and baseline['input'] == draft['input']
    if baseline['outcome'] == draft['outcome']:
        unchanged.append(baseline['key'])
    else:
        changed.append(baseline['key'])
        if baseline['group'] != 'valid_alias' or baseline['matches_canonical'] is not False:
            unexpected.append(baseline['key'])
    if baseline['canonical_outcome'] != draft['canonical_outcome']:
        canonical_changed.append(baseline['key'])
changes = [name for name, value in before['summary']['source_hashes'].items()
           if after['summary']['source_hashes'][name] != value]
result = {'baseline_head': 'd0ec6b618721863830518418aa95dc846f83e7c5',
          'scenarios': len(after['records']), 'actual_public_calls': before['summary']['actual_public_calls'] + after['summary']['actual_public_calls'],
          'changed_entire_outcomes': len(changed), 'preserved_entire_outcomes': len(unchanged),
          'unexpected_changes': unexpected, 'typed_canonical_changes': canonical_changed,
          'draft_canonical_mismatches': after['summary']['canonical_mismatches'],
          'invalid_accepted': after['summary']['invalid_accepted'],
          'caller_isolation_errors': before['summary']['caller_isolation_errors'] + after['summary']['caller_isolation_errors'],
          'catalog_and_mechanics_preserved': all(s[key] for s in (before['summary'], after['summary']) for key in ('catalog_preserved', 'mechanics_preserved')),
          'changed_existing_production_files': changes,
          'full_results_errors_and_formatted_reports_compared': True,
          'private_state_read': False, 'native_validation': False,
          'evidence_hashes': {name: hashlib.sha256((p/name).read_bytes()).hexdigest()
                              for name in ('baseline61-public.json.gz', 'draft-public.json.gz')}}
result['passed'] = not any((unexpected, canonical_changed, result['draft_canonical_mismatches'],
                            result['invalid_accepted'], result['caller_isolation_errors'])) and result['catalog_and_mechanics_preserved'] and changes == ['rouge/operator_engine.py']
(p / 'paired-comparison.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result))
assert result['passed']
