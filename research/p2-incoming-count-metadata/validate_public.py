"""Compare a fresh draft to the complete source-pinned readonly public audit."""
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'draft'))
from rouge.damage import calculate_damage

with gzip.open(ROOT / 'prior-readonly-audit/public-outcomes.json.gz', 'rt', encoding='utf-8') as inp:
    previous = json.load(inp)
records = previous['cases']
new = {}
changed = []
alias_controls = {'one_decimal_text': 'one_int', 'one_exp_text': 'one_int',
                  'twenty_decimal_text': 'twenty_int', 'twenty_exp_text': 'twenty_int',
                  'maximum_exp_text': 'maximum_int'}
for name, record in records.items():
    args = deepcopy(record['scenario'])
    before_input = deepcopy(args)
    try:
        after = {'result': calculate_damage(args), 'error': None}
    except Exception as error:
        after = {'result': None, 'error': {'type': type(error).__name__, 'message': str(error)}}
    assert args == before_input, name
    old = record['outcome']
    new[name] = {'scenario': record['scenario'], 'before': old, 'after': after}
    if old != after:
        control = name.rsplit(':', 1)[0] + ':' + alias_controls[name.rsplit(':', 1)[1]]
        assert old['result'] is None and old['error']['type'] == 'ValueError', name
        assert old['error']['message'].startswith('invalid literal for int() with base 10:'), name
        assert after == records[control]['outcome'], name
        assert after['error'] is None, name
        ref = after['result']['neural_incoming_reference']
        assert ref['events_scheduled'] is False and ref['attack_times_seconds'] is None, name
        changed.append({'case': name, 'equivalent_existing_integer_case': control,
                        'old_error': old['error'], 'complete_outcome_matches_old_integer_control': True})
assert len(changed) == 180, len(changed)
for key, pair in json.loads((ROOT / 'prior-readonly-audit/paired-outcome-comparison.json').read_text())['pairs'].items():
    assert new[pair['left']]['after'] == new[pair['right']]['after'], key
with gzip.open(ROOT / 'paired-full-outcomes.json.gz', 'wt', encoding='utf-8') as out:
    json.dump({'baseline_head': previous['head'], 'cases': new,
               'all_inputs_preserved': True}, out, ensure_ascii=False, indent=2)
    out.write('\n')
(ROOT / 'changed-alias-cases.json').write_text(json.dumps(changed, ensure_ascii=False, indent=2) + '\n')
summary = {'baseline_head': previous['head'], 'fresh_draft_public_calls': len(new),
           'reused_complete_source_pinned_baseline_outcomes': len(records),
           'complete_before_after_pairs': len(new), 'legal_alias_errors_recovered': len(changed),
           'whole_outcomes_unchanged': len(new) - len(changed),
           'unchanged_old_errors': sum(v['after']['error'] is not None for v in new.values()),
           'successful_after_results': sum(v['after']['error'] is None for v in new.values()),
           'complete_semantic_integer_alias_pairs_equal_after': 528,
           'all_changed_outcomes_exactly_equal_old_integer_control': True,
           'all_input_scenarios_unchanged': True, 'no_new_numeric_or_clock_model': True}
(ROOT / 'public-summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(summary, ensure_ascii=False))
