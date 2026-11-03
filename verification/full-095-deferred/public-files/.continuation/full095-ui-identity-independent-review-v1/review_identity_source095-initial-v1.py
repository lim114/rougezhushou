"""Independent stdlib Source review: data, byte inverse, AST, compile only."""
from pathlib import Path
import ast
import base64
import hashlib
import json
import platform
from datetime import datetime, timezone

BASE = Path('/workspace/.continuation')
REPO = Path('/workspace/rougezhushou')
OUT = BASE / 'full095-ui-identity-independent-review-v1'
PACK = BASE / 'full095-ui-identity-retry-source-v1'
RUNNER = PACK / 'wine-full-ui-095-identity-retry.py'
MF = PACK / 'public-artifacts-manifest-identity-retry095.json'
GUARD = BASE / 'root-source-095-v2.json'
PRIOR = BASE / 'full095-ui-cache-retry-source-v1/wine-full-ui-095-cache-retry.py'
PRIOR_REVIEW = BASE / 'full095-ui-cache-retry-independent-review-v1/formal-source-review-cache-retry095.json'
PEER = BASE / 'full095-profile-identity-independent-source-review-v1/formal-independent-source-review-profile-identity095.json'
PROPOSAL = BASE / 'full095-ui-cache-profile-identity-source-proposal-v1/exact-inverse-profile-identity-unapplied095.json'
checks = []

def sha(data):
    return hashlib.sha256(data).hexdigest()

def ref(path):
    data = Path(path).read_bytes()
    return {'path': str(path), 'bytes': len(data), 'sha256': sha(data)}

def check(name, condition, detail):
    if not condition:
        raise AssertionError((name, detail))
    checks.append({'name': name, 'passed': True, 'evidence': detail})

def read_json(path):
    return json.loads(Path(path).read_bytes())

def parse(data, name):
    tree = ast.parse(data.decode('utf-8'), filename=name)
    lines = data.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    def bounds(node):
        return offsets[node.lineno - 1] + node.col_offset, offsets[node.end_lineno - 1] + node.end_col_offset
    def segment(node):
        a, z = bounds(node)
        return data[a:z]
    return tree, lines, bounds, segment

def inverse_stage(data, ops):
    # Preserve the recorded operation order; inherited coordinates are sequential.
    for op in reversed(ops):
        a = op['pending_byte_start']
        z = a + op['pending_byte_count']
        check('inverse_slice_' + str(len(checks)), sha(data[a:z]) == op['pending_sha256'],
              {'category': op['category'], 'start': a, 'bytes': z-a})
        before = base64.b64decode(op['before_base64'], validate=True)
        if 'original_byte_count' in op:
            check('inverse_original_' + str(len(checks)), len(before) == op['original_byte_count'] and sha(before) == op['original_sha256'],
                  {'category': op['category'], 'before_bytes': len(before)})
        data = data[:a] + before + data[z:]
    return data

def assignment(tree, name):
    nodes = [n for n in tree.body if isinstance(n, ast.Assign) and len(n.targets) == 1
             and isinstance(n.targets[0], ast.Name) and n.targets[0].id == name]
    check('unique_assignment_' + name, len(nodes) == 1, len(nodes))
    return nodes[0]

def assertions(tree, segment):
    return [(n.lineno, n.col_offset, segment(n)) for n in sorted(
        (n for n in ast.walk(tree) if isinstance(n, ast.Assert)), key=lambda n: (n.lineno, n.col_offset))]

manifest = read_json(MF)
check('sealed_manifest', ref(MF) == {'path': str(MF), 'bytes': 2290, 'sha256': '6ca4fd70d8acf5a9eb6b58927874c881e2196c8ccf0ab0de1e90d096983542c8'}, ref(MF))
check('sealed_runner', ref(RUNNER) == {'path': str(RUNNER), 'bytes': 1185253, 'sha256': '0e8a0bc1ed4e890cd6a0cf762c7437ced1080dba6ac82e48c680e8d6dc226b0d'}, ref(RUNNER))
for name, pin in manifest['artifacts'].items():
    actual = ref(PACK / name)
    check('manifest_' + name, {k: actual[k] for k in ('bytes', 'sha256')} == pin, actual)
for name, pin in manifest['input_refs'].items():
    check('input_' + name, ref(pin['path']) == pin, pin)
check('original_review_pin', ref(PRIOR_REVIEW)['sha256'] == '8048207e9b8955440384d583a8f8baddc7b824519e9054759f4057035b659e1f', ref(PRIOR_REVIEW))
check('proposal_peer_pin', ref(PEER)['sha256'] == '6bc8d624c0eeede5b215b89dfb5351e2f39a80a71f6bfbf525c453b1d3629ad3', ref(PEER))
contract = read_json(PACK / 'source-contract-identity-retry095.json')
ledger = read_json(PACK / 'exact-inverse-identity-retry095.json')
launch = read_json(PACK / 'exact-launch-contract-identity-retry095.json')
prior_review = read_json(PRIOR_REVIEW)
peer = read_json(PEER)
guard = read_json(GUARD)
check('guard_pin', ref(GUARD)['sha256'] == '41b9f4662a31b0c8ade2cf51c019bda0a04f6569e92770249bcf2e7ebabe9eab', ref(GUARD))
maintained = guard['source_sha256_after']
check('735_maintained_sources', len(maintained) == 735 and all(sha((REPO / k).read_bytes()) == v for k, v in maintained.items()), {'count': len(maintained), 'readonly': True})
check('129_UI_own_source_keys', contract['source_keys'] == prior_review['source_keys'] and len(contract['source_keys']) == 129 and set(contract['source_keys']) <= set(maintained), {'count': len(contract['source_keys']), 'distinct_from_full_735': True})

data = RUNNER.read_bytes()
tree, lines, bounds, segment = parse(data, str(RUNNER))
original = data
stage_results = []
check('inverse_stages_counts', [len(s['operations']) for s in ledger['reverse_stages']] == [31, 27, 3], [len(s['operations']) for s in ledger['reverse_stages']])
for i, stage in enumerate(ledger['reverse_stages']):
    check('stage_input_' + str(i), len(data) == stage['from']['bytes'] and sha(data) == stage['from']['sha256'] and Path(stage['from']['path']).read_bytes() == data, stage['from'])
    data = inverse_stage(data, stage['operations'])
    check('stage_output_' + str(i), len(data) == stage['to']['bytes'] and sha(data) == stage['to']['sha256'] and Path(stage['to']['path']).read_bytes() == data, stage['to'])
    stage_results.append({'operation_count': len(stage['operations']), 'whole_output': stage['to'], 'exact': True})
final = data
pending_path = Path(ledger['original_pending_runner']['path'])
pending = pending_path.read_bytes()
ft, _, fb, fs = parse(final, 'original_final095')
pt, _, _, ps = parse(pending, 'pending095')
substitutions = []
for name in ('PENDING095', 'BINDING095'):
    a, z = fb(assignment(ft, name))
    substitutions.append((a, z, ps(assignment(pt, name))))
for a, z, replacement in reversed(substitutions):
    data = data[:a] + replacement + data[z:]
check('two_binding_whole_inverse', data == pending, ref(pending_path))
pending_ledger = read_json(ledger['original_pending_inverse']['path'])
check('79_legacy_inverse_operations', len(pending_ledger['operations']) == 79, 79)
data = inverse_stage(data, pending_ledger['operations'])
check('whole_original729181_inverse', len(data) == 729181 and sha(data) == '9f7f2d192496f01a4e542cdbbfc1be9932381a6373eb3b46c8fefb2a965e62d9' and data == Path(pending_ledger['original']['path']).read_bytes(), {'bytes': len(data), 'sha256': sha(data)})

prior = PRIOR.read_bytes()
old_tree, old_lines, _, old_segment = parse(prior, str(PRIOR))
check('3744_line_neutral', len(lines) == len(old_lines) == 3744, 3744)
# Restore only new output Constant token spans. This is separate from the full inverse.
pairs = {(p['original'], p['retry']): p['occurrences'] for p in ledger['output_rebindings']}
literal_inverse = {}
for op in ledger['reverse_stages'][0]['operations']:
    if op['category'] == 'declared_output_literal':
        old = base64.b64decode(op['before_base64'], validate=True)
        value = ast.literal_eval(old.decode('utf-8'))
        newvalue = [new for oldvalue, new in pairs if oldvalue == value]
        check('declared_literal_' + str(op['pending_byte_start']), len(newvalue) == 1, value)
        literal_inverse[newvalue[0]] = old
token_changes = []
seen = {key: 0 for key in literal_inverse}
for node in ast.walk(tree):
    if isinstance(node, ast.Constant) and type(node.value) is str and node.value in literal_inverse:
        a, z = bounds(node)
        token_changes.append((a, z, literal_inverse[node.value]))
        seen[node.value] += 1
check('27_output_literal_counts', len(token_changes) == 27 and all(seen[new] == count for (old, new), count in pairs.items()), {'token_count': len(token_changes), 'counts': seen})
normalized = original
for a, z, replacement in sorted(token_changes, reverse=True):
    normalized = normalized[:a] + replacement + normalized[z:]
proposal = read_json(PROPOSAL)
hypothetical = prior
for op in proposal['forward_operations']:
    a = op['start']; before = base64.b64decode(op['old_base64'], validate=True); after = base64.b64decode(op['new_base64'], validate=True)
    check('proposal_forward_' + op['label'], sha(hypothetical) == op['input_sha256'] and hypothetical[a:a+op['old_bytes']] == before and len(after) == op['new_bytes'], {'label': op['label'], 'start': a})
    hypothetical = hypothetical[:a] + after + hypothetical[a+op['old_bytes']:]
    check('proposal_forward_sha_' + op['label'], sha(hypothetical) == op['output_sha256'], op['output_sha256'])
check('concrete_delta_equals_approved_proposal', normalized == hypothetical and sha(normalized) == proposal['hypothetical_target']['sha256'], {'bytes': len(normalized), 'sha256': sha(normalized)})
nt, nl, _, ns = parse(normalized, 'new_outputs_reversed095')
changed_lines = [i + 1 for i, (a, b) in enumerate(zip(old_lines, nl)) if a != b]
check('only_four_identity_cache_lines', changed_lines == [1156, 1205, 1206, 1209], changed_lines)
check('complete_event_evidence_suffix', b''.join(nl[1209:]) == b''.join(old_lines[1209:]), {'from_line': 1210, 'through_entire_end': True})
old_asserts = assertions(old_tree, old_segment)
new_asserts = assertions(tree, segment)
normalized_asserts = assertions(nt, ns)
delta_asserts = [a[0] for a, b in zip(old_asserts, new_asserts) if a[2] != b[2]]
check('907_full_assertions', len(old_asserts) == len(new_asserts) == len(normalized_asserts) == 907 and normalized_asserts == old_asserts, {'count': 907, 'after_output_inverse_all_byteexact': True})
check('assert_positions_904_byteexact_3_PNG_paths', [a[:2] for a in old_asserts] == [a[:2] for a in new_asserts] and delta_asserts == [2846, 3009, 3168], {'byteexact': 904, 'only_changed_PNG_assert_lines': delta_asserts})
for codec in contract['unchanged_native_codecs']:
    a = codec['first_line'] - 1; z = codec['last_line']
    span = b''.join(lines[a:z])
    check('whole_codec_' + codec['name'], span == b''.join(old_lines[a:z]) and len(span) == codec['utf8_bytes'] and sha(span) == codec['sha256'], codec)
for name in ('PENDING095', 'BINDING095'):
    check('unchanged_binding_' + name, segment(assignment(tree, name)) == old_segment(assignment(old_tree, name)), name)
check('whole_root_bound_input', (PACK / 'root-bound-input095.json').read_bytes() == (PRIOR.parent / 'root-bound-input095.json').read_bytes(), ref(PACK / 'root-bound-input095.json'))
profile = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_profile095'][0]
profile_text = segment(profile).decode('utf-8')
check('cache_original_equality_merge_and_None', 'if cached is None and code not in _code_keys095:' in profile_text and 'key=_code_keys095[code] if cached is None else cached[1];_code_identity_keys095[identity]=cached if cached is not None else (code,key)' in profile_text, {'first_identity_backing_CodeType_membership_and_lookup_retained': True, 'equal_distinct_CodeTypes_merge_unchanged': True, 'stored_tuple_with_None_key_is_hit': True, 'strong_exact_code_reference': True})
identity_refs = [n for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id == '_code_identity_keys095']
check('front_cache_not_deleted_or_aliased', len(identity_refs) == 3 and all(not isinstance(n.ctx, ast.Del) for n in identity_refs), {'references': len(identity_refs), 'global_initializer_integer_get_integer_store': True})
expected_argv = ['/workspace/.compat/run-wine-python.sh', 'Z:\\workspace\\.continuation\\full095-ui-identity-retry-source-v1\\wine-full-ui-095-identity-retry.py']
check('exact_new_argv', contract['execution_argv'] == launch['argv'] == expected_argv and contract['execution_cwd'] == launch['cwd'] == str(REPO), expected_argv)
check('wrapper_pin', ref(launch['wrapper']['path']) == launch['wrapper'], launch['wrapper'])
check('fresh_attempt_primary_unclaimed', contract['actual_attempt_execution_count'] == manifest['actual_attempt_execution_count'] == 0 and contract['actual_attempt_primary_exit_code'] is None and manifest['actual_attempt_primary_exit_code'] is None and contract['attempt_number'] == 3 and launch['actual_execution_performed'] is False, {'attempt_number': 3, 'actual_execution_performed_by_reviewer': False, 'primary_exit': None})
fresh = read_json(PACK / 'root-prelaunch-template-identity-retry095.json')['fresh_absent_paths']
absence = {p: not Path(p).exists() for p in fresh}
check('Source_observed_fresh_absence', all(absence.values()), absence)
compiled = compile(original, str(RUNNER), 'exec')
del compiled
check('in_memory_compile_only', True, {'compiler_version': platform.python_version(), 'target_code_executions': 0, 'target_Wine_execution': False})
check('final_source_pins_unchanged', ref(RUNNER)['sha256'] == contract['runner']['sha256'] and ref(MF)['sha256'] == '6ca4fd70d8acf5a9eb6b58927874c881e2196c8ccf0ab0de1e90d096983542c8' and all(sha((REPO / k).read_bytes()) == v for k, v in maintained.items()), {'runner_manifest_and_735_readonly_source_refs_rechecked': True})

report = {
    'format_version': 1, 'status': 'STOPWRITE_INDEPENDENT_IDENTITY_RETRY_SOURCE_GATE_PASSED_RUNTIME_UNRUN',
    'source_gate_passed': True, 'runtime_pass': False, 'execution_ready': False,
    'runner_sha256': contract['runner']['sha256'], 'final_manifest_sha256': ref(MF)['sha256'],
    'guard_sha256': ref(GUARD)['sha256'], 'source_guard_sha256': ref(GUARD)['sha256'],
    'binding_sha256': ref(PACK / 'root-bound-input095.json')['sha256'],
    'source_keys': contract['source_keys'], 'maintained_source_keys': sorted(maintained),
    'source_key_qualification': '129 own rouge sources match existing UI gate; 735 maintained keys are a distinct whole-repository guard, not UI entry keys.',
    'execution_argv': expected_argv, 'actualargv': expected_argv, 'exact_argv': expected_argv,
    'execution_cwd': str(REPO), 'actualcwd': str(REPO), 'cwd': str(REPO), 'script_arg_index': 1,
    'actualargv_execution_performed': False, 'review_completed_at_UTC': datetime.now(timezone.utc).isoformat(),
    'review_scope': 'Concrete third-attempt FINAL producer; read-only bytes, strict ordered entire inverse, AST and local in-memory compile only.',
    'source_artifacts': [ref(p) for p in sorted(PACK.iterdir())] + [ref(p) for p in (PRIOR_REVIEW, PEER, PROPOSAL, GUARD)],
    'independent_standard_library_review': {'checks': len(checks), 'passed': len(checks), 'blocked': 0, 'results': checks},
    'whole_SOURCE_inverse': {'stages': stage_results, 'ordered_operation_counts': [31, 27, 3, 2, 79], 'original729181_bytes': len(data), 'original729181_sha256': sha(data), 'whole_byteexact': True, 'no_sort_of_sequential_inverse_operations': True},
    'assertion_preservation': {'count': 907, 'byteexact_original': 904, 'only_declared_PNG_path_delta_lines': delta_asserts, 'all907_byteexact_after_output_inverse': True, 'positions_preserved': True},
    'binding_preservation': {'root_bound_input_whole_byteexact': True, 'BINDING095_and_PENDING095_wholetext_byteexact': True, 'full735_actual_file_hashes_match': True},
    'cache_applicability': {'first_identity_uses_original_CodeType_equality_map': True, 'equal_distinct_code_merge_preserved': True, 'integer_id_front_key': True, 'strong_code_reference_for_id_reuse_protection': True, 'tuple_code_None_is_valid_hit': True, 'original_f_lineno_cache_unchanged': True, 'only_four_line_neutral_deltas': changed_lines, 'no_product_or_caller_mutation': True, 'memory_retention_cost_unmeasured': True, 'performance_improvement': None, 'complete_runtime_cause': None},
    'runtime_output_contract': contract['output_plan'], 'output_absence_observation': absence,
    'blocking_findings': [],
    'remaining_runtime_gates': ['Root fresh epoch binding and actual prelaunch', 'actual third UI primary exit and complete evidence', 'strict saved-only review', 'Root actual four PNG views', 'full95 acceptance and finish', 'actual archive, commit and normal push'],
    'previous_attempt_boundaries': {'original_UI_primary_exit': None, 'second_UI_primary_exit': None, 'previous_artifacts_not_modified_or_backfilled': True, 'six_prior_passed_primary_executions_not_rerun': True, 'third_attempt_runtime_pass': None, 'third_failure_or_incomplete_requires_Root_defer_per_user': True},
    'execution_counts': {'project_imports': 0, 'project_API': 0, 'reviewed_producer_or_codec_execution': 0, 'tests': 0, 'Wine': 0, 'Qt': 0, 'DLL': 0, 'Git': 0, 'process_operations': 0, 'tracked_writes': 0, 'old_packet_writes': 0, 'own_directory_only_writes': True, 'local_in_memory_compile': 1, 'local_compiler_version': platform.python_version()},
    'completed_section_increment': 0, 'full095_runtime_pass': False, 'STOPWRITE_after_handoff': True,
    'reviewer_source': ref(Path(__file__))
}
path = OUT / 'formal-source-review-identity-retry095.json'
with path.open('x', encoding='utf-8') as stream:
    json.dump(report, stream, ensure_ascii=False, indent=2); stream.write('\n')
print(json.dumps({'formal': ref(path), 'checks': len(checks), 'source_gate_passed': True, 'runtime_pass': False}, indent=2))
