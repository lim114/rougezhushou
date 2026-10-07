"""Compare every full public return; invalid identities reuse existing None."""
from collections import Counter
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
baseline = json.loads((OUT / 'baseline-matrix.json').read_text())
draft = json.loads((OUT / 'draft-matrix.json').read_text())
before = {row['id']: row for row in baseline['cases']}
after = {row['id']: row for row in draft['cases']}
assert before.keys() == after.keys()
counts = Counter()
failures = []
changed = []
for key, original in before.items():
    actual = after[key]
    assert original['scenario'] == actual['scenario']
    unknown = original['held'] and original['identity'] not in (
        'omitted', 'none', 'negative', 'positive')
    if unknown:
        oracle = key.rsplit('/', 1)[0] + '/none'
        expected = before[oracle]['outcome']
        if actual['outcome'] != expected:
            failures.append({'id': key, 'failure': 'not full existing None outcome',
                             'oracle': oracle})
        if actual['outcome'] == original['outcome']:
            failures.append({'id': key, 'failure': 'original false confirmation unchanged'})
        counts['applicable_invalid_changed_to_existing_pending'] += 1
        counts['changed_' + original['group']] += 1
        changed.append(key)
    else:
        if actual['outcome'] != original['outcome']:
            failures.append({'id': key, 'failure': 'preserved full outcome changed'})
        counts['preserved_full_outcomes'] += 1
        counts['preserved_' + original['group']] += 1
    if not actual['outcome']['accepted']:
        counts['draft_error_outcomes'] += 1
    else:
        counts['draft_accepted_outcomes'] += 1

source_changes = [rel for rel, sha in baseline['source_hashes'].items()
                  if draft['source_hashes'][rel] != sha]
assert source_changes == ['rouge/relics.py']
receipt = {'frozen_baseline_head': baseline['frozen_baseline_head'],
           'pairs': len(before), 'public_calls': len(before) * 2,
           'counts': dict(counts), 'full_return_comparison': True,
           'unknown_oracle': 'matching exact public case with recruitment_kind=None from untouched HEAD55',
           'changed_ids': changed, 'failures': failures,
           'source_changes': source_changes, 'source_drift': [],
           'caller_input_unchanged': True, 'shared_mechanics_unchanged': True,
           'private_state_read': False, 'native_validation': False,
           'artifacts': {name: {'sha256': hashlib.sha256((OUT / name).read_bytes()).hexdigest(),
                                'bytes': (OUT / name).stat().st_size}
                         for name in ('baseline-matrix.json', 'draft-matrix.json',
                                      'public_matrix.py', 'section58.patch')}}
(OUT / 'matrix-comparison.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({key: receipt[key] for key in ('pairs', 'public_calls', 'counts',
                                               'failures', 'source_changes')}, ensure_ascii=False))
assert not failures
