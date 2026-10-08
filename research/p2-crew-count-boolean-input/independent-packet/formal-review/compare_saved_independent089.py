"""Strictly review already captured native records and ledger; zero new calls."""
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def native(value):
    kind = type(value)
    if kind is dict:
        return {'type': 'dict', 'items': [[native(k), native(v)] for k, v in value.items()]}
    if kind in (list, tuple):
        return {'type': kind.__name__, 'items': [native(v) for v in value]}
    if kind is float:
        return {'type': 'float', 'hex': value.hex()}
    assert kind in (str, int, bool, type(None)), kind
    return {'type': kind.__name__, 'value': value}

def differences(left, right, prefix=()):
    if type(left) is not type(right):
        return [list(prefix)]
    if type(left) is dict:
        assert list(left) == list(right)
        return [path for key in left for path in differences(left[key], right[key], prefix + (key,))]
    if type(left) in (list, tuple):
        assert len(left) == len(right)
        return [path for i in range(len(left)) for path in differences(left[i], right[i], prefix + (i,))]
    return [] if native(left) == native(right) else [list(prefix)]

payloads, summaries, bindings = {}, {}, []
totals = Counter()
for mode in ('baseline', 'draft', 'tests'):
    directory = OUT / ('fresh-' + mode + '089')
    summary = json.loads((directory / 'summary.json').read_bytes())
    compressed = (directory / 'complete-native-records.json.gz').read_bytes()
    raw = gzip.decompress(compressed)
    assert len(compressed) == summary['gzip_bytes'] and sha(compressed) == summary['gzip_sha256']
    assert len(raw) == summary['decoded_bytes'] and sha(raw) == summary['decoded_sha256']
    payload = json.loads(raw)
    for key, value in payload['summary'].items():
        assert summary[key] == value
    records = payload['records']
    incremental = [json.loads(line) for line in (directory / 'incremental-completed-native-records.jsonl').read_text().splitlines()]
    assert native(incremental) == native(records)
    ledger = [json.loads(line) for line in (directory / 'actual-entry-ledger.jsonl').read_text().splitlines()]
    roles = Counter(row['role'] for row in ledger)
    assert roles == summary['actual_roles'] == Counter(row['role'] for row in records)
    assert [row['entry_sequence'] for row in ledger] == list(range(1, len(ledger) + 1))
    assert len(records) == len(ledger) == summary['records']
    assert summary['constructor_entries'] == summary['RunState_source_actual_entries']['__init__']
    assert summary['apply_entries'] == summary['RunState_source_actual_entries']['apply']
    assert len(ledger) == summary['constructor_entries'] + summary['apply_entries']
    for record, entry in zip(records, ledger):
        for field in ('entry_sequence', 'method', 'role', 'file_path'):
            assert record[field] == entry[field]
        assert entry['product_sha256'] == summary['product_sha256']
        for field in ('state_before', 'state_after', 'return_value'):
            assert native(record[field]) == record[field + '_typed']
        for field in ('disk_before', 'disk_after'):
            disk = record[field]
            if disk is None:
                continue
            raw_disk = disk['UTF8_raw_bytes'].encode()
            assert len(raw_disk) == disk['bytes'] and sha(raw_disk) == disk['sha256']
            assert native(json.loads(raw_disk)) == native(disk['JSON']) == disk['JSON_typed']
        if record['method'] == 'apply':
            assert native(record['observed_before']) == record['observed_before_typed']
            assert native(record['observed_after']) == record['observed_after_typed']
            assert record['observed_before_typed'] == record['observed_after_typed']
            assert native(record['captured_at']) == record['captured_at_typed']
            assert record['state_before']['id'] == record['state_after']['id']
            assert record['state_before']['started_at'].hex() == record['state_after']['started_at'].hex()
            if record['return_value'] is True:
                assert record['state_after_typed'] == record['disk_after']['JSON_typed']
            else:
                assert record['return_value'] is False or mode in ('baseline', 'draft')
                assert record['state_before_typed'] == record['state_after_typed']
                assert record['disk_before'] == record['disk_after']
    if mode == 'tests':
        assert summary['status'] == 'PASS'
        assert summary['test_result'] == {'run': 7, 'errors': 0, 'failures': 0, 'skips': 0, 'success': True}
        assert roles == {'constructor_new': 12, 'constructor_reload': 2, 'seed_apply': 12, 'subject_apply': 12}
    else:
        assert roles == {'constructor_reload': 3, 'subject_apply': 3}
        assert len(payload['cases']) == 3
    totals.update(roles)
    summaries[mode], payloads[mode] = summary, payload
    bindings.append({'mode': mode, 'source_path': str(directory / 'complete-native-records.json.gz'),
        'bytes': len(compressed), 'sha256': sha(compressed), 'decoded_bytes': len(raw), 'decoded_sha256': sha(raw)})
assert totals == {'constructor_reload': 8, 'constructor_new': 12, 'seed_apply': 12, 'subject_apply': 18}
assert sum(value['constructor_entries'] for value in summaries.values()) == 20
assert sum(value['apply_entries'] for value in summaries.values()) == 30

pair_results = []
for old, new in zip(payloads['baseline']['cases'], payloads['draft']['cases']):
    assert old['case_id'] == new['case_id']
    assert old['public_seed_path'] == new['public_seed_path']
    for field in ('initial_persisted_bytes', 'initial_persisted_sha256', 'initial_persisted_UTF8',
                  'actual_run_id', 'started_at_hex', 'captured_at_hex'):
        assert old[field] == new[field]
    seed = old['initial_persisted_UTF8'].encode()
    assert len(seed) == old['initial_persisted_bytes'] and sha(seed) == old['initial_persisted_sha256']
    assert Path(old['public_seed_path']).read_bytes() == seed
    assert old['state_before_typed'] == new['state_before_typed']
    assert old['disk_before'] == new['disk_before']
    assert old['observed_before_typed'] == old['observed_after_typed'] == new['observed_before_typed'] == new['observed_after_typed']
    if old['case_id'] == 'prior-personal-buff-typeerror':
        assert old['exception'] == new['exception'] == {'type': 'ValueError', 'message': '个人强化列表完整性必须为布尔值。'}
        assert old['returned'] is new['returned'] is None
        assert old['state_before_typed'] == old['state_after_typed'] == new['state_after_typed']
        assert old['disk_before'] == old['disk_after'] == new['disk_after']
        result = {'whole_native_after_exact': True, 'whole_raw_disk_after_exact': True, 'olderror_exact': True}
    else:
        assert old['exception'] is new['exception'] is None
        assert old['returned'] is new['returned'] is True
        assert differences(old['state_after'], new['state_after']) == [['crew_count']]
        assert old['disk_after']['JSON_typed'] == old['state_after_typed']
        assert new['disk_after']['JSON_typed'] == new['state_after_typed']
        assert native(new['state_after']['crew_count']) == native(new['state_before']['crew_count'])
        assert type(old['state_after']['crew_count']) is bool and type(new['state_after']['crew_count']) is int
        assert not any(event['kind'] == 'operator_no_longer_present'
            for event in new['state_after']['history'][len(new['state_before']['history']):])
        assert old['state_after']['selected_operator'] == new['state_after']['selected_operator'] == 'mechanist'
        if old['case_id'] == 'true-two-distinct-no-alias':
            assert old['state_after']['crew_count'] is True and new['state_after']['crew_count'] == 2
            assert new['state_after']['operators']['mechanist']['fields']['level'] == 8
            assert new['state_after']['operators']['mechanist']['skill_ranks']['1'] == 2
            assert new['state_after']['operators']['char_151_myrtle']['fields']['trust'] == 22
        else:
            assert old['case_id'] == 'false-positive-fields-resource'
            assert old['state_after']['crew_count'] is False and new['state_after']['crew_count'] == 1
            assert new['state_after']['operators']['mechanist']['fields']['trust'] == 73
            assert new['state_after']['resources']['gold']['value'] == 37
        result = {'whole_native_after_only_difference': ['crew_count'], 'count_prior_int_type_retained': True,
                  'other_positive_observation_merges_exact': True, 'no_departure_in_these_non_alias_cases': True}
    pair_results.append({'case_id': old['case_id'], 'actual_run_id': old['actual_run_id'],
        'actual_started_at_hex': old['started_at_hex'], 'initial_persisted_sha256': old['initial_persisted_sha256'],
        'same_actual_initial_native_and_rawbytes': True, 'result': result})

receipt = {'status': 'PASS_INDEPENDENT_FORMAL_NATIVE_STATE_DISK_CALLER_AND_ORIGINAL7',
    'actual_constructor_entries': 20, 'actual_apply_entries': 30, 'actual_roles': dict(totals),
    'complete_native_records': 50, 'fresh_pair_groups': 3, 'fresh_paired_instances': 6,
    'fresh_seed_apply': 0, 'frozen_newtests_once': {'methods': 7, 'pass': 7, 'skip': 0,
        'constructors': 14, 'apply': 24},
    'root_budget_max': {'constructors': 20, 'apply': 36}, 'budget_not_filled': True,
    'pairs': pair_results, 'record_bindings': bindings,
    'baseline_execution_reused_exact': {'gzip_sha256': summaries['baseline']['gzip_sha256'],
        'actual_previous_completed_constructors': 3, 'actual_previous_completed_apply': 3, 'repeated': False},
    'no_UUID_time_normalization': True, 'same_real_seed_whole_comparison': True,
    'limits': ['State evidence only; no measured training/damage delta.',
        'No actual P1 game departure/buff mechanism or new native clocks defined.',
        'Imported recognition modules are dependencies; no public recognition API invoked.',
        'Internal counts are actual RunState source body entries, not all project helpers.'],
    'other_calls': {'damage_app_API': 0, 'public_recognition_API': 0, 'formatter': 0,
        'network': 0, 'Qt': 0, 'Wine': 0, 'tracked': 0, 'real_local': 0},
    'author_saved38_review_not_repeated': True}
with (OUT / 'independent-formal-review089.json').open('x', encoding='utf-8') as stream:
    json.dump(receipt, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps({'status': receipt['status'], 'constructors': 20, 'apply': 30,
    'native_records': 50, 'pair_groups': 3, 'newtests_pass': 7, 'additional_calls_this_check': 0}))
