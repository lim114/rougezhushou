"""Close the whole requested-field preparation map, reuse saved5, then prepare remaining3."""
import ast
import gzip
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
OLD = HERE / 'resume_ui090_section088_remaining5.py'
FAILURE = HERE / 'api-ui090-section088-new8-resume-failure.json.gz'
OUT = HERE / 'resume_ui090_section088_remaining3.py'
assert not OUT.exists()
document = json.loads(gzip.decompress(FAILURE.read_bytes()))
assert len(document['saved_records']) == document['ledger']['actual_public_calculation_requests'] == 5
assert document['ledger']['formatter_text_requests'] == 15
source = OLD.read_text()
source = source.replace("api-ui090-section088-new8-resume-failure.json.gz", "api-ui090-section088-new8-final3-failure.json.gz")
source = source.replace("first_segment = json.loads(gzip.decompress((HERE / 'api-ui090-section088-new8-failure.json.gz').read_bytes()))",
    "first_segment = json.loads(gzip.decompress((HERE / 'api-ui090-section088-new8-resume-failure.json.gz').read_bytes()))")
source = source.replace("new8-resume-execution-freeze090.json", "new8-final3-execution-freeze090.json")
source = source.replace("assert starting_completed_records == 3", "assert starting_completed_records == 5")
source = source.replace("saved3-timing-contract-reassertion090.json", "saved5-full-preparation-contract-reassertion090.json")
old = """        for key in case['input']:
            if key == 'timing':
                # Combat.calculate1469 preserves the declared timing and adds
                # exactly its private resume frame. Continuous returned
                # streams append only for deployment-speed rules, absent
                # here; full streams=[] and the existing max defaults to0.
                assert case['input']['operator'] == 'char_002_amiya'
                assert case['input']['timing_mode'] == 'continuous'
                expected = {**case['input']['timing'], '_resume_frames': 0}
                assert typed(scenario['timing']) == typed(expected)
            else:
                assert typed(scenario[key]) == typed(case['input'][key]), key
"""
new = """        # Public caller input is exact and unchanged. The internal prepared
        # scenario follows the existing preparation pipeline, whose declared
        # input-field projection differs only in these two source-defined ways.
        expected = {**case['input'], 'relic_ids': []}
        modern = case['input']['operator'] != 'mechanist'
        if modern:
            declared_timing = case['input']['timing'] if 'timing' in case['input'] else {}
            expected['timing'] = {**declared_timing, '_resume_frames': 0}
        projected = {key: scenario[key] for key in expected}
        assert typed(projected) == typed(expected)
        if not modern:
            assert 'timing' not in scenario
        assert type(scenario['relic_ids']) is list and scenario['relic_ids'] == []
        assert typed(scenario['_relic_rules']) == typed(result['relic_resolution']['rules'])
        expected_ids = case['input']['relic_ids']
        assert [row['id'] for row in result['relic_resolution']['records']] == expected_ids
"""
assert source.count(old) == 1
source = source.replace(old, new)
source = source.replace("        assert resume_proof['actual_rules_include_deployment_attack_speed'] is False",
    "        assert resume_proof['actual_rules_include_deployment_attack_speed'] is False\n        expected_timing = {**(case['input']['timing'] if 'timing' in case['input'] else {}), '_resume_frames': 0}\n        assert typed(resume_proof['actual_internal_prepared_timing']) == typed(expected_timing)")
start = source.index("    'execution_segments': [")
end = source.index("    'same_harness_issue_failed_attempts': 1}", start) + len("    'same_harness_issue_failed_attempts': 1}")
source = source[:start] + """    'execution_segments': [
        {'actual_API_calls': 3, 'explicit_text_requests': 9, 'actual_formatter_entries': 12},
        {'actual_API_calls': 2, 'explicit_text_requests': 6, 'actual_formatter_entries': 8},
        {'actual_API_calls': API_calls - 5, 'explicit_text_requests': formatter_requests - 15,
         'actual_formatter_entries': sum(formatter_entries.values()) - 20}],
    'saved_first3_and_saved_first5_whole_prefixes_retained': True,
    'same_harness_issue_failed_attempts': 2}""" + source[end:]
source = source.replace("'remaining5_elapsed_seconds'", "'remaining3_elapsed_seconds'")
ast.parse(source)
OUT.write_text(source)

def decode(node):
    kind = node['type']
    if kind == 'dict':
        return {decode(k): decode(v) for k, v in node['items']}
    if kind in ('list', 'tuple'):
        items = [decode(v) for v in node['items']]
        return tuple(items) if kind == 'tuple' else items
    if kind == 'float':
        return float.fromhex(node['hex'])
    value = node['value']
    assert type(value).__name__ == kind
    return value

tree = ast.parse(source)
functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ('typed', 'require_result')]
namespace = {'math': math}
exec(compile(ast.Module(body=functions, type_ignores=[]), str(OUT), 'exec'), namespace)
cases = json.loads((HERE / 'original-approved-additional8-input-plan090.json').read_bytes())['cases']
for i, record in enumerate(document['saved_records']):
    assert record['sequence'] == i + 1 and record['input'] == cases[i]['input']
    result = decode(record['result_native'])
    assert namespace['typed'](result) == record['result_native']
    assert record['caller_native_before'] == record['caller_native_after']
    assert namespace['typed'](record['input']) == record['caller_native_before']
    assert record['reports']['estimate'] == record['reports']['default']
    for name, report in record['reports'].items():
        assert hashlib.sha256(report.encode()).hexdigest() == record['reports_sha256'][name]
    scenarios = record['same_call_processed_report_scenarios']
    for saved in scenarios:
        native = decode(saved['scenario_native'])
        assert namespace['typed'](native) == saved['scenario_native']
        saved['scenario'] = native
    namespace['processed_scenarios'] = scenarios
    namespace['require_result'](cases[i], result)
    if i >= 3:
        proof = record['same_call_internal_resume_proof'][0]
        assert proof['full_timing_streams'] == [] and proof['calculated_internal_resume'] == 0
        assert type(proof['calculated_internal_resume']) is int
        assert proof['actual_rules_include_deployment_attack_speed'] is False
        expected_timing = {**(cases[i]['input']['timing'] if 'timing' in cases[i]['input'] else {}), '_resume_frames': 0}
        assert namespace['typed'](proof['actual_internal_prepared_timing']) == namespace['typed'](expected_timing)
original3 = json.loads(gzip.decompress((HERE / 'api-ui090-section088-new8-failure.json.gz').read_bytes()))['saved_records']
assert document['saved_records'][:3] == original3
receipt = {
    'status': 'PASS_FULL_SAVED5_NATIVE_REPORT_AND_SOURCE_DEFINED_PREPARATION_REASSERTION_ZERO_CALLS',
    'saved_records': 5, 'strict_reused_texts': 15, 'remaining_distinct_API_requests_only': 3,
    'same_prepared_shape_harness_failed_attempts': 2, 'product_failures': 0,
    'caller_whole_native_and_JSON_exact_unchanged': True,
    'prepared_declared_input_projection_contract': {
        'relic_ids': 'relics.prepare250 clears the internal ids list after explicit resolution; full active rules and record ids bind back to the unchanged requested ids.',
        'timing': 'Combat.calculate1469 adds exactly integer _resume_frames0; fixed inputs have no deployment_speed rules and full streams=[]; caller timing stays exact.',
        'all_other_declared_keys': 'Complete native projection identical under the fixed no-run-config/no-target-enemy/no-attribute-rune inputs; no get fallback or unknown deletion.',
        'internal_added_fields': 'Full original/native same-call trace retained, not represented as caller identity or new public fields.',
    },
    'first_saved3_whole_prefix_exact': True,
    'saved5_counterexample_archive_sha256': hashlib.sha256(FAILURE.read_bytes()).hexdigest(),
    'remaining3_adapter_sha256': hashlib.sha256(OUT.read_bytes()).hexdigest(),
    'API_helpers_formatter_RunState_constructor_apply_Qt_Wine_tests_calls': 0,
}
(HERE / 'saved5-full-preparation-contract-reassertion090.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(receipt, ensure_ascii=False))
