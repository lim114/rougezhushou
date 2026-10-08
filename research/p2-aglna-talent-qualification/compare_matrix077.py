from pathlib import Path
import collections, copy, datetime, hashlib, json

base = Path(__file__).parent
before = json.loads((base / 'baseline-results077.json').read_bytes())
after = json.loads((base / 'draft-results077.json').read_bytes())
TALENT = '飘浮大地之上'


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


assert before['paired_scenario_records'] == after['paired_scenario_records'] == 875
counts = collections.Counter()
pairs = []
mismatches = []
for old, new in zip(before['records'], after['records']):
    assert (old['group'], old['request']) == (new['group'], new['request'])
    for row in (old, new):
        if 'full_result' in row:
            assert row['full_result_sha256'] == digest(row['full_result'])
    request = old['request']
    if 'error' in old:
        kind = 'prior_complete_errors_unchanged'
        passed = old['error'] == new.get('error')
    elif request['operator'] == 'char_1015_aglna2' and request.get('elite', 2) == 0:
        trimmed = copy.deepcopy(new['full_result'])
        old_components = [c for c in old['full_result']['components'] if c['name'] == TALENT]
        new_components = [c for c in trimmed['components'] if c['name'] == TALENT]
        assert len(old_components) == len(new_components) == 1
        old_component, new_component = old_components[0], new_components[0]
        passed = new_component['hits'] == 0 and new_component['times_seconds'] == []
        passed = passed and new_component['per_hit'] == new_component['total'] == 0
        passed = passed and trimmed['estimate']['skill']['hit_counts'][TALENT] == 0
        new_component['hits'] = old_component['hits']
        new_component['times_seconds'] = copy.deepcopy(old_component['times_seconds'])
        trimmed['estimate']['skill']['hit_counts'][TALENT] = old['full_result']['estimate']['skill']['hit_counts'][TALENT]
        passed = passed and trimmed == old['full_result']
        kind = 'only_locked_talent_phantom_hits_times_and_skill_count_zeroed' if old['full_result'] != new['full_result'] else 'complete_json_unchanged'
    else:
        kind = 'complete_json_unchanged'
        passed = old['full_result'] == new.get('full_result')
    counts[kind] += 1
    pair = {'group': old['group'], 'request': request, 'kind': kind, 'passed': passed,
            'before_result_sha256': old.get('full_result_sha256'), 'after_result_sha256': new.get('full_result_sha256'),
            'before_error': old.get('error'), 'after_error': new.get('error')}
    pairs.append(pair)
    if not passed:
        mismatches.append(pair)
out = {'utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'paired_scenarios': len(pairs),
       'matrix_actual_new_public_calls': before['actual_fresh_public_calls'] + after['actual_fresh_public_calls'],
       'reused_readonly_public_calls_without_rerun': before['reused_completed_readonly_calls_without_rerun'],
       'total_actual_author_public_calls_including_reused_source_audit':
           before['actual_fresh_public_calls'] + after['actual_fresh_public_calls'] + before['reused_completed_readonly_calls_without_rerun'],
       'counts': dict(counts), 'pairs': pairs, 'mismatches': mismatches,
       'strict_full_json_only_restores_exact_three_locked_talent_fields': True,
       'all_math_training_completion_source_clocks_timeline_streams_relic_records_and_old_errors_unchanged': not mismatches,
       'eligible_E1_E2_and_other_owner_complete_outputs_unchanged': not mismatches,
       'callers_and_public_static_caches_preserved': before['callers_and_public_static_caches_preserved'] and after['callers_and_public_static_caches_preserved']}
(base / 'matrix-comparison077.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + '\n')
print({k: v for k, v in out.items() if k not in ('pairs', 'mismatches')})
assert not mismatches
