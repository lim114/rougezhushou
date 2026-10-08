"""One bounded44 real-bool API preflight; full typed/JSON/3text evidence."""
import gzip
import hashlib
import json
import sys
import time
import traceback
from collections import Counter
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE / 'public-schema-086-ui090'
TARGET = HERE / 'api-ui090-section086.json.gz'
assert not TARGET.exists() and not (HERE / 'api-ui090-section086-failure.json.gz').exists()
proof = json.loads((HERE / 'root086-ui090-source-proof.json').read_bytes())
assert proof['root_commit'] == '0f27027e7e1f49c08f298706b599e310e299238b'
assert proof['maintenance_python_json_files'] == 724 and proof['public_files'] == 125
sys.dont_write_bytecode = True
sys.path[:0] = [str(PACKAGE), str(HERE)]
from cases090_section086 import cases090_section086
def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)
def typed(value):
    if isinstance(value, dict):
        return {'type': 'dict', 'items': [[typed(key), typed(item)] for key, item in value.items()]}
    if isinstance(value, (list, tuple)):
        return {'type': type(value).__name__, 'items': [typed(item) for item in value]}
    assert type(value) in (str, int, float, bool, type(None)), type(value)
    return {'type': type(value).__name__, 'value': value}
def source_hashes():
    return {path.relative_to(PACKAGE).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted((PACKAGE / 'rouge').rglob('*'))
        if path.is_file() and path.suffix in ('.py', '.json')}
before_source = source_hashes()
assert before_source == proof['public_source_sha256']

import rouge.catalog as catalog_module
original_catalog = catalog_module.catalog
catalog_ref = None
catalog_baseline = None
catalog_entries = Counter()
phase = 'imports'
def observed_catalog():
    global catalog_ref, catalog_baseline
    catalog_entries[phase] += 1
    value = original_catalog()
    if catalog_ref is None:
        catalog_ref = value
        catalog_baseline = canonical(value)
    assert value is catalog_ref
    return value
catalog_module.catalog = observed_catalog
import rouge.damage as damage_module
import rouge.reporting as reporting_module
import rouge.estimate as estimate_module
assert Path(damage_module.__file__).resolve().is_relative_to(PACKAGE)
formatter_entries = Counter()
formatter_requests = 0
original_report = reporting_module.format_report
original_estimate = estimate_module.format_estimate
def format_report(result, *, technical=False):
    formatter_entries['format_report_technical' if technical else 'format_report_default'] += 1
    return original_report(result, technical=technical)
def format_estimate(result):
    formatter_entries['format_estimate'] += 1
    return original_estimate(result)
reporting_module.format_report = format_report
estimate_module.format_estimate = format_estimate

ENGINE = str((PACKAGE / 'rouge/operator_engine.py').resolve())
trace_rows = []
normal_calls = Counter()
def observe_normal(frame, event, arg):
    if frame.f_code.co_filename != ENGINE or frame.f_code.co_name not in ('plan', 'calculate'):
        return None
    self = frame.f_locals['self']
    if self.s['operator'] != 'char_4182_oblvns':
        return None
    if event == 'call' and frame.f_code.co_name == 'plan' and frame.f_locals['normal'] is True:
        normal_calls[id(self)] += 1
    if event == 'return' and frame.f_code.co_name == 'calculate':
        local = frame.f_locals
        trace_rows.append({'operator': self.s['operator'], 'skill': self.n,
            'module_id': self.s.get('module_id'), 'module_level': self.s.get('module_level', 0),
            'continuous_attacks': self.s['continuous_attacks'],
            'normal_plan_calls_observed': normal_calls[id(self)],
            'normal_local_exists': 'normal' in local,
            'normal_local_is_not_None': 'normal' in local and local['normal'] is not None,
            'actual_object_ranged_attack_condition_consumed': self.ranged_attack_condition_consumed,
            'ranged_overridden_local': local['ranged_overridden'],
            'selected_note_max_cnt': self.tv['颂乐音符']['max_cnt']})
    return observe_normal

def require_result(case, result):
    assert type(result) is dict and all(key in result for key in
        ('attack', 'total_damage', 'total_healing', 'components', 'estimate', 'report'))
    assert type(result['components']) is list
    assert result['estimate']['training'] == {key: case['input'][key] for key in
        ('elite', 'level', 'trust', 'potential', 'module_id', 'module_level')}
    if 'gnosis_terminal_reference' in result:
        reference = result['gnosis_terminal_reference']
        assert reference['terminal_clock_verified'] is False
        assert reference['freeze_removal_order_verified'] is False
    if 'gnosis_s1_reference' in result:
        assert result['gnosis_s1_reference']['relative_hit_times_seconds'] is None
        assert result['gnosis_s1_reference']['multi_event_binding_verified'] is False
    if 'external_event_reference' in result:
        assert result['external_event_reference']['actual_event_times_seconds'] is None
    if 'unbound_cast_reference' in result:
        assert result['unbound_cast_reference']['actual_hit_times_seconds'] is None
        assert result['unbound_cast_reference']['actual_end_seconds'] is None
    if case['input']['operator'] == 'char_4182_oblvns':
        assert len(trace_rows) == 1
        trace = trace_rows[0]
        assert trace['normal_local_exists']
        assert (trace['normal_plan_calls_observed'] > 0) is trace['normal_local_is_not_None']
        if case['pair_id'] == 'coveredmodule:oblvns-ranged-skill-vs-normal':
            assert trace['selected_note_max_cnt'] == 12
            assert trace['ranged_overridden_local'] is True
            assert trace['normal_plan_calls_observed'] == 1 and trace['normal_local_is_not_None']
            assert trace['actual_object_ranged_attack_condition_consumed'] is True

cases = cases090_section086()
assert len(cases) == 44
unique_inputs = len({canonical(case['input']) for case in cases})
assert unique_inputs == json.loads((HERE / 'cases090-section086.json').read_bytes())['unique_requested_calculation_inputs']
records = []
anchors = {}
API_calls = 0
started = time.perf_counter()
def preserve_failure(error_type, error, stack):
    failure = {'scope': 'Bounded44 UI09086 only; no old36 or4217 rerun; no GUI/Wine',
        'root_commit': proof['root_commit'], 'actual_API_calls': API_calls,
        'saved_completed_records': len(records), 'formatter_text_requests': formatter_requests,
        'formatter_entry_counts': dict(formatter_entries),
        'source_hashes_before': before_source, 'source_hashes_after': source_hashes(),
        'current_case': globals().get('case'), 'current_input': globals().get('args'),
        'current_result': globals().get('result'), 'current_result_typed': globals().get('result_typed'),
        'current_reports': globals().get('reports'), 'current_trace': trace_rows,
        'records': records, 'error_type': error_type.__name__, 'error': str(error),
        'traceback': ''.join(traceback.format_exception(error_type, error, stack)),
        'external_product_helper_calls': 0, 'Qt_calls': 0, 'Wine_calls': 0}
    raw = gzip.compress(json.dumps(failure, ensure_ascii=False, allow_nan=False).encode(), mtime=0)
    with (HERE / 'api-ui090-section086-failure.json.gz').open('xb') as output:
        output.write(raw)
    sys.__excepthook__(error_type, error, stack)
sys.excepthook = preserve_failure
for case in cases:
    args = deepcopy(case['input'])
    input_before = typed(args)
    input_JSON_before = canonical(args)
    result = None
    result_typed = None
    reports = None
    trace_rows.clear()
    normal_calls.clear()
    phase = 'API'
    API_calls += 1
    previous_trace = sys.gettrace()
    sys.settrace(observe_normal)
    try:
        result = damage_module.calculate_damage(args)
    finally:
        sys.settrace(previous_trace)
    assert typed(args) == input_before and canonical(args) == input_JSON_before
    result_typed = typed(result)
    result_JSON_before = canonical(result)
    phase = 'formatter'
    formatter_requests += 1
    estimate = format_estimate(result)
    formatter_requests += 1
    default = format_report(result)
    formatter_requests += 1
    technical = format_report(result, technical=True)
    reports = {'estimate': estimate, 'default': default, 'technical': technical}
    assert estimate == default and typed(result) == result_typed and canonical(result) == result_JSON_before
    assert canonical(catalog_ref) == catalog_baseline
    require_result(case, result)
    row = {'case': case, 'input': args, 'input_typed_before': input_before, 'input_typed_after': typed(args),
        'result': result, 'result_typed': result_typed, 'reports': reports,
        'all_three_texts_preserve_result_typed_and_JSON': True,
        'internal_same_call_trace': deepcopy(trace_rows), 'cached_catalog_canonical_JSON_unchanged': True}
    if case['widget_checked'] is False:
        assert case['pair_id'] not in anchors
        anchors[case['pair_id']] = row
    else:
        anchor = anchors[case['pair_id']]
        if case['kind'] == 'hidden':
            assert case['field'] not in args and case['field'] not in anchor['input']
            assert typed(args) == anchor['input_typed_before']
            assert result_typed == anchor['result_typed'] and reports == anchor['reports']
        elif case['pair_id'] == 'qualification:mizuki-E1':
            assert result_typed == anchor['result_typed'] and reports == anchor['reports']
        elif case['pair_id'] == 'coveredmodule:oblvns-ranged-skill-vs-normal':
            assert typed(result['components']) == typed(anchor['result']['components'])
            assert result['estimate']['skill']['skill_attack'] == anchor['result']['estimate']['skill']['skill_attack']
            assert result_typed != anchor['result_typed']
        else:
            assert result_typed != anchor['result_typed']
    records.append(row)
assert API_calls == len(records) == 44 and len(anchors) == 22
assert formatter_requests == 132
assert formatter_entries == {'format_estimate': 44, 'format_report_default': 88, 'format_report_technical': 44}
assert source_hashes() == before_source
receipt = {'status': 'PASS_BOUNDED44_UI090_SECTION086_API_TYPED_JSON_THREE_TEXTS',
    'root_source_commit': proof['root_commit'], 'root_maintenance_files': 724, 'public_source_files': 125,
    'UI_state_design_records': 44, 'pair_groups': 22, 'actual_API_calls': API_calls,
    'unique_requested_calculation_inputs': unique_inputs, 'successful_results': len(records),
    'expected_error_rows': 0, 'formatter_text_requests': formatter_requests,
    'formatter_entry_counts': dict(formatter_entries), 'actual_formatter_function_entries': sum(formatter_entries.values()),
    'catalog_helper_entries_internally_observed': dict(catalog_entries), 'external_product_helper_calls': 0,
    'same_call_normal_plan_trace_is_observation_not_extra_calculation': True,
    'old_source36_or4217_API_cases_repeated': 0, 'source_drift': [],
    'source_hashes': before_source, 'records': records, 'elapsed_seconds': time.perf_counter() - started,
    'Qt_calls': 0, 'Wine_calls': 0, 'tests_run': 0, 'UI090_all_final_sources': False,
    'pending090_runner_sha256': hashlib.sha256((HERE / 'wine-ui-smoke-090.py').read_bytes()).hexdigest()}
raw = gzip.compress(json.dumps(receipt, ensure_ascii=False, allow_nan=False).encode(), mtime=0)
with TARGET.open('xb') as output:
    output.write(raw)
summary = {key: value for key, value in receipt.items() if key not in ('records', 'source_hashes')}
summary['full_receipt_sha256'] = hashlib.sha256(raw).hexdigest()
(HERE / 'api-ui090-section086-summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(summary, ensure_ascii=False))
