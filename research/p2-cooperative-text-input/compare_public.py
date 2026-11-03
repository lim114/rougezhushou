"""Strict full-result or exact-error comparison, selected by concrete inputs."""
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
with gzip.open(ROOT / 'baseline64-public-full-outcomes.json.gz', 'rt', encoding='utf-8') as inp:
    before = json.load(inp)
with gzip.open(ROOT / 'draft69-public-full-outcomes.json.gz', 'rt', encoding='utf-8') as inp:
    after = json.load(inp)
assert before['cases'].keys() == after['cases'].keys()
exact_error = {'result': None, 'error': {'type': 'ValueError',
    'message': 'cooperative不接受字符串，请提供明确的布尔条件。'}}
records = {}
selected = same_success = same_error = 0
for name, left in before['cases'].items():
    right = after['cases'][name]
    assert left['scenario'] == right['scenario'], name
    args = left['scenario']
    # Active cases use valid E2/rank1..10 inputs and nontext fragile values.
    # The priority group instead contains explicit original64/training errors.
    applies = name.startswith('active:') and isinstance(args.get('cooperative'), str)
    old, new = left['outcome'], right['outcome']
    if applies:
        assert args['operator'] == 'silverash' and type(args['skill']) is int and args['skill'] == 3
        assert args.get('elite', 2) == 2 and type(args.get('skill_rank', 10)) is int
        assert 1 <= args.get('skill_rank', 10) <= 10
        assert not isinstance(args.get('preexisting_fragile'), str)
        assert old['error'] is None and new == exact_error, name
        selected += 1
    else:
        assert old == new, name
        if old['error'] is None:
            same_success += 1
        else:
            same_error += 1
    records[name] = {'scenario': args, 'qualified_string_guard_applies': applies,
                     'before': old, 'after': new}
assert (selected, same_success, same_error) == (102, 1794, 60)
with gzip.open(ROOT / 'paired-full-outcomes.json.gz', 'wt', encoding='utf-8') as out:
    json.dump({'baseline_head': before['baseline_head'], 'cases': records,
               'comparison': 'complete JSON equality or exact error type and literal'},
              out, ensure_ascii=False, indent=2)
    out.write('\n')
summary = {'baseline_head': before['baseline_head'], 'complete_before_after_pairs': len(records),
           'fresh_public_calls': 2 * len(records), 'qualified_texts_rejected': selected,
           'complete_success_outputs_unchanged': same_success, 'exact_prior_errors_unchanged': same_error,
           'all_other_whole_outcomes_unchanged': same_success + same_error,
           'all_preexisting_fragile_error_priority_preserved': True,
           'all_training_error_priority_preserved': True,
           'all_inputs_and_catalog_preserved': True, 'new_numeric_or_clock_model': False}
(ROOT / 'public-summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(summary, ensure_ascii=False))
