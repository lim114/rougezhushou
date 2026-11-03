"""Independent metadata, AST and byte review only; execute no reviewed code."""
import ast
import base64
import datetime
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).parent
SAVED = Path('/workspace/.continuation/full095-saved-validator-ui-identity-source-v1')
OLD = Path('/workspace/.continuation/full095-saved-validator-ui-cache-pending-v4')
PRODUCER = Path('/workspace/.continuation/full095-ui-identity-retry-source-v1')
GUARD_SHA = '41b9f4662a31b0c8ade2cf51c019bda0a04f6569e92770249bcf2e7ebabe9eab'
references = {}
checks = []

def digest(data):
    return hashlib.sha256(data).hexdigest()

def read(path, expected=None):
    path = Path(path)
    assert path.is_absolute() and path.is_file() and not path.is_symlink()
    data = path.read_bytes()
    ref = {'path': str(path), 'bytes': len(data), 'sha256': digest(data)}
    if expected:
        assert all(ref[k] == v for k, v in expected.items()), (path, ref, expected)
    assert str(path) not in references or references[str(path)] == ref
    references[str(path)] = ref
    return data

def document(path, expected=None):
    return json.loads(read(path, expected))

def row(name, evidence):
    checks.append({'name': name, 'passed': True, 'evidence': evidence})

def spans(source):
    lines = source.splitlines(keepends=True)
    result = {}
    for node in ast.parse(source).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            start = min([node.lineno, *[d.lineno for d in node.decorator_list]])
            span = b''.join(lines[start - 1:node.end_lineno])
            result[node.name] = {'data': span, 'first_line': start, 'last_line': node.end_lineno,
                                 'bytes': len(span), 'sha256': digest(span)}
    return result

def reverse(data, operations):
    for operation in reversed(operations):
        start, count = operation['pending_byte_start'], operation['pending_byte_count']
        assert type(start) is int and type(count) is int and start >= 0 and count >= 0
        assert start + count <= len(data)
        assert digest(data[start:start + count]) == operation['pending_sha256']
        before = base64.b64decode(operation['before_base64'], validate=True)
        if 'original_byte_count' in operation:
            assert len(before) == operation['original_byte_count']
        if 'before_sha256' in operation:
            assert digest(before) == operation['before_sha256']
        data = data[:start] + before + data[start + count:]
    return data

def literals(source):
    result = {}
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                result[node.targets[0].id] = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                pass
    return result

mf_path = SAVED / 'public-artifacts-manifest-source-preparation095.json'
mf = document(mf_path, {'bytes': 2303, 'sha256': '47251cbe499c14253bf5c6f0636fdf43d951c6624f47c05f7ef9edea05e7f81b'})
assert mf['STOPWRITE'] is True and mf['runtime_pass'] is False and mf['target_execution_calls'] == 0
for name, ref in mf['files'].items():
    assert Path(ref['path']) == SAVED / name
    read(ref['path'], ref)
row('Saved manifest all eight payloads physically exact and STOPWRITE', references[str(mf_path)])

candidate = read(SAVED / 'saved.py', {'bytes': 98186, 'sha256': '6d94c3effb6c56987ece108af152b885ce35485f6220533596ed888d259f41ff'})
original = read(OLD / 'saved.py', {'bytes': 97726, 'sha256': '34aee7208c81f155715acf444cf967e234dd4a7cb84182051068223b052b3b96'})
compile(candidate, str(SAVED / 'saved.py'), 'exec')
ledger = document(SAVED / 'exact-inverse-saved-ui-identity095.json')
assert ledger['candidate'] == references[str(SAVED / 'saved.py')]
assert ledger['original'] == references[str(OLD / 'saved.py')]
assert len(ledger['operations']) == 9 and reverse(candidate, ledger['operations']) == original
row('Saved nine-operation whole-byte inverse restores original v4 and compile has no execution', {
    'candidate': references[str(SAVED / 'saved.py')], 'original': references[str(OLD / 'saved.py')],
    'ledger': references[str(SAVED / 'exact-inverse-saved-ui-identity095.json')],
    'target_code_object_executions': 0})

old_functions, new_functions = spans(original), spans(candidate)
assert old_functions.keys() == new_functions.keys() and len(old_functions) == 44
same = [name for name in old_functions if old_functions[name]['data'] == new_functions[name]['data']]
changed = [name for name in old_functions if name not in same]
assert len(same) == 43 and changed == ['recover_original_final095']
assert ledger['functions_whole_byte_unchanged'] == same and ledger['functions_changed'] == changed
row('Independent 43 of 44 complete function spans including final newline unchanged', {
    'whole': [{k: v for k, v in new_functions[n].items() if k != 'data'} | {'name': n} for n in same],
    'changed': changed, 'span_definition': 'def through AST end_lineno, including complete final physical line and LF'})
codec_names = ['graph', 'decode', 'native090', 'projection090', 'legacy_inverse']
assert all(n in same for n in codec_names)
row('All five Saved graph and inverse codec bodies unchanged without invoking a codec', codec_names)

old_saved_ledger = document(OLD / 'exact-inverse-saved-ui-cache095-v4.json')
oldest_saved = read(old_saved_ledger['original']['path'], old_saved_ledger['original'])
assert reverse(original, old_saved_ledger['operations']) == oldest_saved
assert len(old_saved_ledger['operations']) == 9
row('Whole old v4 to 90632-byte v3 Saved inverse independently exact', old_saved_ledger['original'])

producer_mf_path = PRODUCER / 'public-artifacts-manifest-identity-retry095.json'
producer_mf = document(producer_mf_path, {'bytes': 2290, 'sha256': '6ca4fd70d8acf5a9eb6b58927874c881e2196c8ccf0ab0de1e90d096983542c8'})
assert producer_mf['STOPWRITE'] is True and producer_mf['runtime_calls'] == 0
assert producer_mf['root_source_guard_sha256'] == GUARD_SHA
for name, ref in producer_mf['artifacts'].items():
    read(PRODUCER / name, ref)
contract = document(PRODUCER / 'source-contract-identity-retry095.json')
ui_runner = read(contract['runner']['path'], contract['runner'])
assert len(ui_runner) == 1185253 and digest(ui_runner) == '0e8a0bc1ed4e890cd6a0cf762c7437ced1080dba6ac82e48c680e8d6dc226b0d'
assert contract['source_gate_passed'] is True and contract['runtime_pass'] is False
assert contract['execution_ready'] is False and contract['actual_attempt_execution_count'] == 0
assert contract['source_guard']['sha256'] == GUARD_SHA
row('Concrete third producer packet all six payloads exact and no runtime evidence claimed', {
    'manifest': references[str(producer_mf_path)], 'contract': references[str(PRODUCER / 'source-contract-identity-retry095.json')],
    'runner': references[contract['runner']['path']]})

producer_inverse = document(contract['inverse_recovery']['ledger']['path'], contract['inverse_recovery']['ledger'])
assert producer_inverse['schema'] == 'full-ui095-identity-retry-exact-inverse-v1'
stages = producer_inverse['reverse_stages']
assert len(stages) == 3 and [len(s['operations']) for s in stages] == [31, 27, 3]
expected_stages = [contract['runner'], contract['prior_cache_retry_runner'], contract['cache_candidate'], contract['original_final']]
recovered = ui_runner
for i, stage in enumerate(stages):
    assert stage['from'] == expected_stages[i] and stage['to'] == expected_stages[i + 1]
    assert recovered == read(stage['from']['path'], stage['from'])
    recovered = reverse(recovered, stage['operations'])
    assert recovered == read(stage['to']['path'], stage['to'])
assert expected_stages[1]['sha256'] == 'e5dec2d704cecbde56762cf7c2f92016f5123b592633fae12840a892869e6bc5'
assert expected_stages[2]['sha256'] == '1a6ac7f0db3096de170a9e0d035148bfbad372cc58f704bb7ad39da6cb7cfb6d'
assert expected_stages[3]['sha256'] == '83c412ce7e456109dc32a6415f7a61526955d48b01d25dbb72198870e6cf18ee'
row('Concrete producer full 31 then 27 then 3 sequential-operation inverses exact at every physical stage', {
    'inverse': references[contract['inverse_recovery']['ledger']['path']], 'operation_counts': [31, 27, 3],
    'stages': expected_stages})

new_rec = new_functions['recover_original_final095']['data'].decode('utf-8')
required = [
    "contract_name == 'source-contract-identity-retry095.json'",
    "inverse_contract['schema'] == 'full-ui095-identity-retry-exact-inverse-v1'",
    "ledger_name == 'exact-inverse-identity-retry095.json'",
    "len(stages) == 3", "[len(stage['operations']) for stage in stages] == [31, 27, 3]",
    "stages[0]['from'] == retry['runner'] and stages[0]['to'] == prior",
    "stages[1]['from'] == prior and stages[1]['to'] == cache",
    "stages[2]['from'] == cache and stages[2]['to'] == original",
    "recovered == read_ref(stage['from'])", "recovered == read_ref(stage['to'])",
    "sha(recovered[start:end]) == operation['pending_sha256']",
    "base64.b64decode(operation['before_base64'], validate=True)",
    "contract['runner'] == retry['runner']", "contract['source_guard'] == spec['actual_source_guard']",
    "final_files[contract_name] == contract_bytes", "final_files[ledger_name] == ledger_bytes",
    "graph(literal(runner_data.decode('utf-8'), 'BINDING095'))",
    "ui['execution_contract']['argv'] == contract['exact_argv']",
    "contract['exact_argv'] == spec['actual_UI_primary']['argv']",
    "contract['cwd'] == str(REPO)", "REPORT['UI_identity_retry_three_stage_inverse_exact'] = True"
]
assert all(text in new_rec for text in required)
row('Changed recovery function strictly binds contract manifest argv all stages physical bytes and original binding', required)

saved_literals, ui_literals = literals(candidate), literals(ui_runner)
assert saved_literals['EXPECTED_GUARD_SHA'] == GUARD_SHA
assert saved_literals['PNG_NAMES'] == tuple(Path(p).name for p in contract['output_plan']['pngs'])
assert len(saved_literals['PNG_NAMES']) == 4
assert b"NATIVE_DIRECTORY = COMPAT / 'full095-ui-native-identity-retry-v1'" in candidate
assert contract['output_plan']['native_directory'] == '/workspace/.compat/full095-ui-native-identity-retry-v1'
assert ui_literals['PENDING095'] is False
binding = read(contract['binding']['path'], contract['binding'])
assert binding == read(Path(contract['original_final']['path']).parent / 'root-bound-input095.json')
assert ast.dump(ast.parse(repr(ui_literals['BINDING095']))) == ast.dump(ast.parse(repr(json.loads(binding))))
row('Identity native and all four PNG namespace constants match actual concrete producer and entire original binding bytes', {
    'PNGs': contract['output_plan']['pngs'], 'native_directory': contract['output_plan']['native_directory'],
    'binding': references[contract['binding']['path']]})

pending_dir = Path('/workspace/.continuation/full095-ui-migration-pending-v3')
pending_binding = document(pending_dir / 'pending-binding095.json')
old_ui_source = recovered.decode('utf-8')
assignment = next(n for n in ast.parse(old_ui_source).body if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == 'BINDING095' for t in n.targets))
actual_assignment = ast.get_source_segment(old_ui_source, assignment) + '\n'
assert old_ui_source.count(actual_assignment) == old_ui_source.count('PENDING095 = False') == 1
pending_recovered = old_ui_source.replace(actual_assignment, 'BINDING095 = ' + repr(pending_binding) + '\n', 1).replace('PENDING095 = False', 'PENDING095 = True', 1).encode('utf-8')
pending_actual = read(pending_dir / 'wine-full-ui-095-pending.py')
assert pending_recovered == pending_actual
pending_inverse = document(pending_dir / 'exact-inverse-ledger095.json')
original_ui = reverse(pending_actual, pending_inverse['operations'])
assert len(original_ui) == 729181 and digest(original_ui) == '9f7f2d192496f01a4e542cdbbfc1be9932381a6373eb3b46c8fefb2a965e62d9'
classification = document(pending_dir / 'original-assertion-and-delta-classification095.json')
assert sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(original_ui))) == classification['original_assert_count']
row('Inherited complete two-binding and pending-operation inverse still reaches exact original 729181 bytes', {
    'pending': references[str(pending_dir / 'wine-full-ui-095-pending.py')],
    'pending_inverse': references[str(pending_dir / 'exact-inverse-ledger095.json')],
    'original_bytes': len(original_ui), 'original_sha256': digest(original_ui),
    'original_assertions': classification['original_assert_count'], 'pending_operation_count': len(pending_inverse['operations'])})

prior_ui = read(contract['prior_cache_retry_runner']['path'], contract['prior_cache_retry_runner'])
new_asserts = [ast.get_source_segment(ui_runner.decode('utf-8'), n) for n in ast.walk(ast.parse(ui_runner)) if isinstance(n, ast.Assert)]
prior_asserts = [ast.get_source_segment(prior_ui.decode('utf-8'), n) for n in ast.walk(ast.parse(prior_ui)) if isinstance(n, ast.Assert)]
assert len(new_asserts) == len(prior_asserts) == 907
assert sum(a == b for a, b in zip(new_asserts, prior_asserts)) == 904
normalized_asserts = list(new_asserts)
for i, text in enumerate(normalized_asserts):
    for replacement in contract['output_rebindings']:
        text = text.replace(replacement['retry'], replacement['original'])
    normalized_asserts[i] = text
assert normalized_asserts == prior_asserts
row('907 producer assertions conserved with only three declared screenshot literal changes', {'count': 907, 'byte_exact': 904, 'all_exact_after_output_inverse': True})

strict_groups = {
    'typed_order_alias_graph_and_saved_raw_files': ['graph', 'decode', 'snapshot_value', 'filesystem_rows', 'durable'],
    'actual_root_prelaunch_UI_primary_raw_integer_zero': ['primary_launch'],
    'actual_full_735_source_guard_and_original_binding': ['source_and_binding', 'maintained', 'source_map'],
    'actual_receipt_native_API_phase_ledger': ['ui_receipt', 'native_archive', 'new_subgroup'],
    'old_native_baseline_and_source_qualified_delta': ['baseline_documents', 'strict_baseline', 'original52_archive'],
    'exact_four_PNG_framing_CRC_and_source_refs': ['png', 'validate'],
    'own_independent_source_gate_exact_real_input_spec_and_future_argv': ['validate', 'main'],
}
assert all(all(n in same for n in names) for names in strict_groups.values())
row('All strict Saved runtime and native evidence logic unchanged in complete preserved function bodies', strict_groups)

template = document(SAVED / 'root-input-template095.json')
assert read(SAVED / 'root-input-template095.json') == read(OLD / 'root-input-template095.json')
assert template['status'] == 'PENDING_ROOT_ACTUAL_FULL095_SAVED_INPUTS_NOT_PASS'
assert template['actual_UI_primary']['argv'] is None and template['actual_UI_receipt']['sha256'] is None
assert template['actual_source_guard']['sha256'] == GUARD_SHA
row('Planning spec remains PENDING with actual primary receipt and execution argv null', {
    'template': references[str(SAVED / 'root-input-template095.json')], 'actual_runtime_input_spec': None})

for ref in list(references.values()):
    read(ref['path'], ref)
row('All reviewed physical inputs reread without changed bytes', {'file_count': len(references)})

result = {
    'format_version': 1, 'section': 95,
    'status': 'STOPWRITE_INDEPENDENT_SAVED_IDENTITY_SOURCE_REVIEW_PASSED_RUNTIME_UNRUN',
    'source_gate_passed': True, 'runtime_pass': False, 'execution_ready': False,
    'runner_sha256': digest(candidate), 'runner': references[str(SAVED / 'saved.py')],
    'manifest_sha256': references[str(mf_path)]['sha256'], 'sourcepack': references[str(mf_path)],
    'source_guard_sha256': GUARD_SHA,
    'execution_argv': ['/workspace/rougezhushou/.venv/bin/python', str(SAVED / 'saved.py'), '--spec',
                       '/workspace/.continuation/root-full095-ui-identity-retry-v1-saved-input-spec.json', '--output',
                       '/workspace/.continuation/root-full095-ui-identity-retry-v1-saved-review.json'],
    'execution_cwd': '/workspace/rougezhushou', 'script_arg_index': 1,
    'formal_pointers': {'source_gate': '/source_gate_passed', 'runtime': '/runtime_pass',
                        'runner_sha256': '/runner_sha256', 'argv': '/execution_argv', 'guard_sha256': '/source_guard_sha256'},
    'review_completed_at_UTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'reviewer_role': 'Independent Source reviewer; neither Saved nor producer author',
    'review_scope': 'Standard library metadata, full physical bytes, AST, in-memory exact source inverses, and unexecuted compilation only. No reviewed helper, graph codec, target code object, project, tests, Wine, Qt, DLL, Git, child subprocess, or process-control calls.',
    'independent_standard_library_review': {'checks': len(checks), 'passed': len(checks), 'blocked': 0, 'results': checks},
    'checked_file_refs': dict(sorted(references.items())),
    'qualification': [
        'This is a concrete source gate only; Root must still bind actual prelaunch, input spec, UI primary, complete UI receipt and Saved primary.',
        'The historical UI_retry_two_stage_inverse_exact report key is retained for compatibility; its current implementation validates exactly three stages and adds UI_identity_retry_three_stage_inverse_exact. No assertion that the current chain has only two stages is made.',
        'Existing complete graph, order, alias, float-hex, raw-byte and old API comparison limits remain unchanged. No cross-time Qt or Python runtime identity is reconstructed from JSON.',
        'Saved checks four complete PNG byte files; actual Root visual inspection is a separate required action.',
        '735 maintained file maps are verified by the preserved Saved source when Root runs it. This Source review reads the guard binding and pinned source, not all 735 maintained repository files.',
        'Third producer Source inverse includes 4 identity-cache source edits and 27 fresh output literal edits. No performance improvement or successful third execution is claimed.',
        'Source gate approval does not authorize restarting or creating a fourth same-issue UI attempt; user requires deferral after three unsuccessful attempts.'
    ],
    'actual_saved_input_spec': None, 'actual_UI_log': None, 'actual_UI_receipt': None,
    'actual_UI_primary_exit_code': None, 'actual_UI_raw_exit_file': None,
    'actual_Saved_runtime': None, 'actual_Saved_primary_exit_code': None, 'actual_runtime_PASS': None,
    'actual_finished_archive_spec': None, 'completed_section_increment': 0,
    'execution_counts': {'Saved': 0, 'codecs': 0, 'project': 0, 'tests': 0, 'Wine': 0, 'Qt': 0,
                         'DLL': 0, 'Git': 0, 'target_code_object': 0, 'process_control': 0, 'tracked_mutations': 0},
    'STOPWRITE': True,
}
path = OUT / 'formal-source-review-saved095-ui-identity-v1.json'
with path.open('x', encoding='utf-8') as handle:
    json.dump(result, handle, ensure_ascii=False, allow_nan=False, indent=2)
    handle.write('\n')
print(json.dumps({'source_gate_passed': True, 'runtime_pass': False, 'checks': len(checks), 'formal': str(path)}))
