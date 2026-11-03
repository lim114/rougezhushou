"""Preserve the first3 records and repair one source-derived harness assertion."""
import ast
import gzip
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORIGINAL = HERE / 'preflight_ui090_section088.py'
FAILURE = HERE / 'api-ui090-section088-new8-failure.json.gz'
RESUME = HERE / 'resume_ui090_section088_remaining5.py'
assert not RESUME.exists()
first = json.loads(gzip.decompress(FAILURE.read_bytes()))
assert first['ledger']['actual_public_calculation_requests'] == 3
assert first['ledger']['profile_observed_calculate_damage_function_entries'] == 3
assert first['ledger']['formatter_text_requests'] == 9
assert len(first['saved_records']) == 3
source = ORIGINAL.read_text()
old = """        for key in case['input']:
            assert typed(scenario[key]) == typed(case['input'][key]), key
"""
new = """        for key in case['input']:
            if key == 'timing':
                # Combat.calculate1469 preserves the declared timing and adds
                # exactly its private resume frame. Continuous returned
                # streams are appended only for deployment-speed rules;
                # these inputs have none, so the full streams list is empty.
                assert case['input']['operator'] == 'char_002_amiya'
                assert case['input']['timing_mode'] == 'continuous'
                expected = {**case['input']['timing'], '_resume_frames': 0}
                assert typed(scenario['timing']) == typed(expected)
            else:
                assert typed(scenario[key]) == typed(case['input'][key]), key
"""
assert source.count(old) == 1
source = source.replace(old, new)
source = source.replace("assert not TARGET.exists() and not (HERE / 'api-ui090-section088-new8-failure.json.gz').exists()",
    "assert not TARGET.exists() and not (HERE / 'api-ui090-section088-new8-resume-failure.json.gz').exists()")
source = source.replace("(HERE / 'new8-execution-freeze090.json')", "(HERE / 'new8-resume-execution-freeze090.json')")
source = source.replace("formatter_entries = Counter()", "first_segment = json.loads(gzip.decompress((HERE / 'api-ui090-section088-new8-failure.json.gz').read_bytes()))\nformatter_entries = Counter(first_segment['ledger']['formatter_function_entry_counts'])")
source = source.replace("observed_public_entries = Counter()", "observed_public_entries = Counter({'calculate_damage': first_segment['ledger']['profile_observed_calculate_damage_function_entries']})")
source = source.replace("records = []\nAPI_calls = 0\nformatter_requests = 0", "records = first_segment['saved_records']\nstarting_completed_records = len(records)\nassert starting_completed_records == 3\nassert (HERE / 'saved3-timing-contract-reassertion090.json').exists()\nAPI_calls = first_segment['ledger']['actual_public_calculation_requests']\nformatter_requests = first_segment['ledger']['formatter_text_requests']")
source = source.replace("for case in cases:\n        request", "for case in cases[starting_completed_records:]:\n        request")
source = source.replace("'api-ui090-section088-new8-failure.json.gz', failure)", "'api-ui090-section088-new8-resume-failure.json.gz', failure)")
source = source.replace("'internal_catalog_uncached_python_body_entries_by_phase': {name: sum(count", "'internal_catalog_uncached_python_body_entries_by_phase': {name: first_segment['ledger']['internal_catalog_uncached_python_body_entries_by_phase'][name] + sum(count")
source = source.replace("'elapsed_seconds': time.perf_counter() - started}", "'remaining5_elapsed_seconds': time.perf_counter() - started,\n    'execution_segments': [{'actual_API_calls': 3, 'explicit_text_requests': 9, 'actual_formatter_entries': 12,\n        'harness_contract_counterexample': 'prepared timing adds source-derived integer _resume_frames0',\n        'whole_saved_prefix_reasserted_without_calls': True},\n        {'actual_API_calls': API_calls - 3, 'explicit_text_requests': formatter_requests - 9,\n         'actual_formatter_entries': sum(formatter_entries.values()) - 12}],\n    'same_harness_issue_failed_attempts': 1}")
ast.parse(source)
RESUME.write_text(source)

def decode(node):
    kind = node['type']
    if kind == 'dict':
        return {decode(k): decode(v) for k, v in node['items']}
    if kind in ('list', 'tuple'):
        values = [decode(v) for v in node['items']]
        return tuple(values) if kind == 'tuple' else values
    if kind == 'float':
        return float.fromhex(node['hex'])
    value = node['value']
    assert type(value).__name__ == kind
    return value

tree = ast.parse(source)
selected = [node for node in tree.body if isinstance(node, ast.FunctionDef)
            and node.name in ('typed', 'require_result')]
assert [node.name for node in selected] == ['typed', 'require_result']
namespace = {'math': math}
exec(compile(ast.Module(body=selected, type_ignores=[]), str(RESUME), 'exec'), namespace)
cases = json.loads((HERE / 'original-approved-additional8-input-plan090.json').read_bytes())['cases']
assert len(cases) == 8
for i, record in enumerate(first['saved_records']):
    assert record['sequence'] == i + 1 and record['input'] == cases[i]['input']
    result = decode(record['result_native'])
    assert namespace['typed'](result) == record['result_native']
    assert record['caller_native_before'] == record['caller_native_after']
    assert namespace['typed'](record['input']) == record['caller_native_before']
    assert record['reports']['estimate'] == record['reports']['default']
    for name, report in record['reports'].items():
        assert hashlib.sha256(report.encode()).hexdigest() == record['reports_sha256'][name]
    scenarios = record['same_call_processed_report_scenarios']
    for processed in scenarios:
        assert namespace['typed'](decode(processed['scenario_native'])) == processed['scenario_native']
        processed['scenario'] = decode(processed['scenario_native'])
    namespace['processed_scenarios'] = scenarios
    namespace['require_result'](cases[i], result)
receipt = {
    'status': 'PASS_SAVED3_FULL_NATIVE_AND_REPORT_REASSERTION_ONLY_ZERO_CALLS',
    'same_harness_contract_failed_attempts': 1,
    'source_mechanism': 'operator_engine1469 adds exactly _resume_frames; continuous streams append only for deployment-speed rules, absent here; full streams list is empty and max defaults to0.',
    'saved_records': 3, 'saved_texts_strictly_reused': 9,
    'first_API_requests_preserved_not_rerun': 3, 'remaining_API_requests_only': 5,
    'first_segment_gzip_sha256': hashlib.sha256(FAILURE.read_bytes()).hexdigest(),
    'original_adapter_sha256': hashlib.sha256(ORIGINAL.read_bytes()).hexdigest(),
    'resume_adapter_sha256': hashlib.sha256(RESUME.read_bytes()).hexdigest(),
    'all_non_timing_input_keys_still_whole_typed_equal': True,
    'prepared_timing_accepts_no_extra_keys_except_exact_integer_resume_frame0': True,
    'public_inputs_or_source_modified': False,
    'API_formatter_externalhelpers_RunState_constructor_apply_Qt_Wine_tests_calls': 0,
}
(HERE / 'saved3-timing-contract-reassertion090.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(receipt, ensure_ascii=False))
