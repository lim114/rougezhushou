"""Independent stdlib source/physical-reference audit. Never import reviewed code."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = Path('/workspace/.continuation/full095-regression-ui-identity-resume-source-v1')
OLD = Path('/workspace/.continuation/full095-regression-ui-cache-resume-final-v1')
ROOT = Path('/workspace/rougezhushou')
checked = {}
checks = []

def ref(path):
    path = Path(path)
    data = path.read_bytes()
    return {'path': str(path), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}

def physical(reference):
    path = Path(reference['path'])
    assert path.is_absolute() and path.is_file() and not path.is_symlink(), reference
    assert type(reference['bytes']) is int and reference['bytes'] >= 0, reference
    digest = hashlib.sha256()
    count = 0
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            count += len(block)
            digest.update(block)
    actual = {'path': str(path), 'bytes': count, 'sha256': digest.hexdigest()}
    assert actual == {key: reference[key] for key in actual}, (actual, reference)
    if str(path) in checked:
        assert checked[str(path)] == actual
    checked[str(path)] = actual
    return path.read_bytes() if path.suffix == '.json' else None

def refs(value):
    if isinstance(value, dict):
        if {'path', 'bytes', 'sha256'} <= value.keys():
            yield value
        else:
            for child in value.values():
                yield from refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from refs(child)

def note(name, detail):
    checks.append({'name': name, 'source_or_physical_check_passed': True, 'detail': detail})

def functions(data):
    lines = data.splitlines(keepends=True)
    tree = ast.parse(data)
    return {node.name: {'node': node, 'bytes': b''.join(lines[node.lineno-1:node.end_lineno])}
            for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}

def literals(data):
    result = {}
    for node in ast.parse(data).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                result[node.targets[0].id] = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                pass
    return result

candidate_path = SOURCE / 'identity_binding095.py'
inverse_path = SOURCE / 'identity-recovery-helper-inverse095.json'
candidate = candidate_path.read_bytes()
inverse = json.loads(inverse_path.read_bytes())
assert ref(candidate_path) == inverse['candidate_reference']
old = physical(inverse['baseline_reference'])
if old is None:
    old = Path(inverse['baseline_reference']['path']).read_bytes()
assert (SOURCE / 'recovery_binding095.py').read_bytes() == old
physical(inverse['candidate_reference'])
physical(ref(inverse_path))
recovered = candidate.decode('utf-8')
reverse_rows = []
for index in range(len(inverse['changes'])-1, -1, -1):
    change = inverse['changes'][index]
    count = recovered.count(change['after'])
    assert type(change['count']) is int and count == change['count'], (index, count)
    recovered = recovered.replace(change['after'], change['before'], count)
    reverse_rows.append({'index': index, 'exact_after_occurrences': count,
                         'after_utf8_bytes': len(change['after'].encode('utf-8')),
                         'before_utf8_bytes': len(change['before'].encode('utf-8'))})
assert recovered.encode('utf-8') == old
note('whole_byte_inverse', {'changes': len(inverse['changes']), 'rows': reverse_rows,
                           'baseline': inverse['baseline_reference'], 'candidate': inverse['candidate_reference']})

old_functions = functions(old)
new_functions = functions(candidate)
assert len(old_functions) == 7 and len(new_functions) == 8
unchanged = []
literal_only = []
for name, row in old_functions.items():
    if name == 'validate_recovery_inputs':
        continue
    newer = new_functions[name]['bytes']
    if newer == row['bytes']:
        unchanged.append(name)
    else:
        normalized = newer.decode('utf-8')
        for change in reversed(inverse['changes'][:-1]):
            normalized = normalized.replace(change['after'], change['before'])
        assert normalized.encode('utf-8') == row['bytes'], name
        literal_only.append(name)
assert unchanged == ['check_prior_recovery', 'check_incomplete_ui', 'check_recovery_passes', 'check_selected_failure', 'project_outputs']
assert literal_only == ['ui_retry_projection']
note('legacy_functions_preserved', {'five_whole_byte': unchanged, 'one_output_literal_only': literal_only,
                                  'one_replaced': 'validate_recovery_inputs', 'one_added': 'check_prior_ui_retry'})

support_refs = []
for name in ('recovery_binding095.py', 'capability_binding095.py', 'binding_validation095.py'):
    current = (SOURCE / name).read_bytes()
    assert current == (OLD / name).read_bytes(), name
    compile(current, str(SOURCE / name), 'exec')
    support_refs.append(ref(SOURCE / name))
    physical(support_refs[-1])
compile(candidate, str(candidate_path), 'exec')
core = literals((SOURCE / 'binding_validation095.py').read_bytes())
assert len(core['OUTPUT_NAMES']) == 13 and len(core['EXECUTION_NAMES']) == 8
note('whole_old_validator_chain', {'support': support_refs, 'core_output_names': core['OUTPUT_NAMES'],
                                  'execution_names': list(core['EXECUTION_NAMES']),
                                  'reviewed_module_executed': False, 'compile_only': True})

constants = literals(candidate)
prior_refs = constants['IDENTITY_PRIOR_UI_RETRY']
for reference in prior_refs.values():
    physical(reference)
prior = json.loads(Path(prior_refs['binding']['path']).read_bytes())
prior_context = json.loads(Path(prior_refs['context']['path']).read_bytes())
original_ref = prior['recovery_spec']['original']['context']
physical(original_ref)
original_context = json.loads(Path(original_ref['path']).read_bytes())
assert original_context['started_at'] == '2026-10-08T22:54:16.947394+00:00'
assert prior_context['started_at'] == original_context['started_at']
assert prior_context['recovery_started_at'] == '2026-10-08T23:36:41.779450+00:00'
assert prior_context['ui_retry_started_at'] == '2026-10-09T00:59:43.753835+00:00'
assert prior_context['available_checks_passed'] is False
note('historical_epoch_only', {'original_epoch': original_context['started_at'],
                              'recovery_boundary': prior_context['recovery_started_at'],
                              'prior_ui_boundary': prior_context['ui_retry_started_at'],
                              'new_identity_boundary': None, 'new_actual_spec_or_binding_read': False})

passed = {}
for field in ('preserved_passed_executions', 'preserved_recovery_passed_executions'):
    for name, row in prior['recovery_spec'][field].items():
        for reference in refs(row):
            physical(reference)
        observation = json.loads(Path(row['observation']['path']).read_bytes())
        assert observation['primary_exit_code'] == 0 and type(observation['primary_exit_code']) is int
        assert observation['actual_root_observed_primary_exit'] is True
        assert observation['primary_exit_code_captured'] is True
        assert Path(observation['exit_code_file']['path']).read_bytes() in (b'0\n', b'0\r\n')
        for reference in refs(observation):
            physical(reference)
        passed[name] = {'observation': row['observation'], 'actual_tool_observation': observation['actual_tool_observation'],
                        'primary_exit_code': 0, 'raw_status': observation['exit_code_file']}
assert set(passed) == {'linux_full', 'linux_selected', 'linux_pip', 'wine_pip', 'wine_full', 'wine_selected'}
note('six_historical_primary_zero_proofs', passed)

failures = {}
for field in ('prior_failed_execution', 'prior_selected_failed_execution'):
    row = prior['recovery_spec'][field]
    for reference in refs(row):
        physical(reference)
    observation = json.loads(Path(row['observation']['path']).read_bytes())
    assert observation['primary_exit_code'] == 1
    assert Path(observation['exit_code_file']['path']).read_bytes() in (b'1\n', b'1\r\n')
    for reference in refs(observation):
        physical(reference)
    failures[field] = {'observation': row['observation'], 'primary_exit_code': 1,
                       'actual_tool_observation': observation['actual_tool_observation']}
note('two_earlier_actual_failure_proofs', failures)

losses = []
for constant, expected_session, expected_chunks, expected_records, directory in (
    ('INCOMPLETE_UI', 61366, 275, 10272, '/workspace/.compat/full095-ui-native-v3'),
    ('IDENTITY_INCOMPLETE_UI', 53266, 2310, 136836, '/workspace/.compat/full095-ui-native-cache-retry-v1')):
    capsule_ref = constants[constant]
    physical(capsule_ref)
    capsule = json.loads(Path(capsule_ref['path']).read_bytes())
    assert capsule['actual_original_UI_session_id'] == expected_session
    assert capsule['primary_exit_code'] is None and capsule['primary_exit_code_captured'] is False
    assert capsule['actual_root_requested_process_termination'] is False
    assert capsule['cause_of_external_session_loss'] == 'UNKNOWN'
    assert capsule['full_validation_passed'] is False
    assert capsule['closed_native_chunks'] == expected_chunks and capsule['closed_targeted_records'] == expected_records
    for reference in refs(capsule):
        physical(reference)
    index = json.loads(Path(capsule['native_index']['path']).read_bytes())
    assert index['outcome'] == 'pending' and len(index['chunks']) == expected_chunks
    assert index['records_completed'] == expected_records
    chunks = []
    for chunk in index['chunks']:
        path = Path('/workspace/.compat') / chunk['file']
        assert path.parent == Path(directory)
        reference = {'path': str(path), 'bytes': chunk['bytes'], 'sha256': chunk['sha256']}
        physical(reference)
        chunks.append(reference)
    if expected_session == 53266:
        assert chunks == capsule['all_closed_compressed_chunk_refs_verified']
        assert Path(capsule['preserved_native_index_snapshot']['path']).read_bytes() == Path(capsule['native_index']['path']).read_bytes()
        assert capsule['same_UI_execution_problem_incomplete_attempt_count'] == 2
        assert capsule['third_attempt_failure_requires_deferral'] is True
        paths = prior['actual_inputs']['global_output_plan']['paths']
        raw_path = prior['actual_inputs']['execution_contracts']['wine_ui']['exit_code_path']
        receipt_path = paths['wine_ui']
    else:
        raw_path = '/workspace/.continuation/root-full095-wine_ui.exit-code'
        receipt_path = '/workspace/.compat/wine-ui-095.json'
    assert not Path(raw_path).exists() and not Path(receipt_path).exists()
    losses.append({'capsule': capsule_ref, 'session_id': expected_session, 'primary_exit_code': None,
                   'closed_chunks_verified': expected_chunks, 'partial_records': expected_records,
                   'raw_status_remains_absent': raw_path, 'final_receipt_remains_absent': receipt_path,
                   'outcome': 'pending', 'runtime_pass': None})
note('two_lost_UI_physical_histories', losses)

maintained = {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
              for folder in ('rouge', 'tests', 'scripts')
              for path in sorted((ROOT / folder).rglob('*'))
              if path.is_file() and path.suffix in ('.py', '.json') and '__pycache__' not in path.parts}
assert maintained == prior['actual_inputs']['source_sha256']
assert len(maintained) == prior['actual_inputs']['source_files'] == 735
note('read_only_current_maintained_source_hashes', {'files': len(maintained), 'matches_prior_735_source_guard': True,
                                                 'project_import_or_test_executed': False})

manifest_path = SOURCE / 'public-artifacts-manifest-ui-retry095.json'
manifest = json.loads(manifest_path.read_bytes())
for reference in manifest['payload_files']:
    physical(reference)
assert manifest['STOPWRITE'] is True and manifest['runtime_executed'] is False
note('frozen_source_packet_physical_references', {'manifest': ref(manifest_path),
                                               'payload_files_verified': len(manifest['payload_files']),
                                               'current_helper_is_only_Source': True})

new_validate = new_functions['validate_recovery_inputs']['bytes'].decode('utf-8')
assert 'validate_prior_ui_inputs(base_spec, prior_immutable)' in new_validate
assert "original['root_spec'] == prior['root_spec'] and actual == prior['actual_inputs']" in new_validate
assert "projected['execution_contracts']['wine_selected']" not in new_validate
assert "projected['execution_contracts']['wine_ui'].update(" in new_validate
assert "projected['execution_contracts']['saved_review'].update(" in new_validate
note('only_two_new_execution_contract_projections', {'changed_from_b83': ['wine_ui', 'saved_review'],
                                                  'wine_selected_unchanged_from_b83': True,
                                                  'caller_runs_no_code_in_this_audit': True})

report = {
    'format_version': 1, 'section': 95, 'scope': 'INDEPENDENT_SOURCE_AND_HISTORICAL_PHYSICAL_REFERENCES_ONLY',
    'source_scope_checks_passed': True, 'source_gate_passed': None,
    'not_a_completed_actual_spec_or_sealer_approval': True,
    'reviewed_helper': ref(candidate_path), 'inverse_ledger': ref(inverse_path),
    'checks': checks,
    'qualifications': [
        'No helper, validator, sealer, context, producer, Saved, codec, project, test, Wine, Git or target process was executed or manipulated.',
        'Source compile/AST, in-memory byte inverse and raw physical hashes are not runtime acceptance.',
        'The helper does not directly require root_ui_prelaunch to be non-null or validate its actual fields; it requires only the exact planned_root_prelaunch_path. references_in ignores null. Actual Root spec review must supply this gate before sealing.',
        'This helper binding contains two earlier failed executions and two lost UI executions. A fifth failure/loss is not established in this limited helper scope.',
        'Core OUTPUT_NAMES has 13 unchanged entries; full execution contracts have 8 entries; prior UI root binding has 9 keys and own maintained source scope has 129 keys. These are separate counts.',
        'Current maintained bytes were read and hashed; live Git/index and helper invocation gates remain Root-only unexecuted.',
        'Unknown exits for both lost UI attempts stay NULL. Neither partial-record count is completion or PASS.',
        'Third incomplete/failing UI attempt requires preserving evidence and deferring; no fourth runtime attempt is established here.',
        'All new actual spec/binding/boundary/UI/Saved/finish/commit/push evidence remain NULL in this review; sections 96-98 remain paused.'
    ],
    'actual_new_spec': None, 'actual_new_binding': None, 'actual_identity_boundary': None,
    'actual_UI_primary_exit': None, 'actual_Saved_primary_exit': None, 'actual_runtime_pass': None,
    'actual_sealer_result': None, 'actual_finish_result': None, 'actual_commit': None, 'actual_push': None,
    'runtime_executed': False, 'project_calls': 0, 'checked_physical_files': len(checked),
    'checked_file_refs': [checked[key] for key in sorted(checked)]
}
output = HERE / 'formal-helper-independent-scope-review095.json'
with output.open('xb') as stream:
    stream.write((json.dumps(report, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
print(json.dumps({'status': 'SOURCE_SCOPE_AND_HISTORICAL_REFERENCES_REVIEWED_NO_ACTUAL_SPEC_GATE',
                  'source_scope_checks_passed': True, 'checks': len(checks),
                  'checked_physical_files': len(checked), 'formal': ref(output),
                  'runtime_executed': False, 'actual_new_spec': None}, ensure_ascii=False))
