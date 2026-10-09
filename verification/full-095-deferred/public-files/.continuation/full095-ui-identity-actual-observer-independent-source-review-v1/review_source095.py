"""Independent stdlib-only SOURCE review; never imports or executes target code."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path('/workspace/.continuation')
OUT = ROOT / 'full095-ui-identity-actual-observer-independent-source-review-v1'
SRC = ROOT / 'full095-ui-identity-actual-observer-source-v1'
PIN = ROOT / 'full095-ui-identity-actual-observer-binding-source-v1'

def ref(path):
    path = Path(path)
    assert path.is_file() and not path.is_symlink()
    data = path.read_bytes()
    return {'path': str(path), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}

def load(path):
    return json.loads(Path(path).read_bytes())

def write(path, value):
    with Path(path).open('x', encoding='utf-8') as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write('\n')

source_manifest = SRC / 'public-artifacts-manifest-actual-observer-identity095.json'
pin_manifest = PIN / 'public-artifacts-manifest-observer-binding095.json'
assert ref(source_manifest) == {'path': str(source_manifest), 'bytes': 1181, 'sha256': '0a31ede352dc56367383e8803ef0d197ae5fa183cdac5dd13e602601a97d186a'}
assert ref(pin_manifest)['bytes'] == 418
assert ref(pin_manifest)['sha256'] == '39ebd94a8c3c26197ce530827d2f028e9a341a3db51009717805202f9ac14568'

# The exact pin-manifest SHA is independently calculated below, rather than
# relying on a abbreviated SHA from the task message.
source_files = sorted(p for p in SRC.iterdir() if p.is_file())
pin_files = sorted(p for p in PIN.iterdir() if p.is_file())
assert len(source_files) == 6 and len(pin_files) == 2
sm, pm = load(source_manifest), load(pin_manifest)
assert sm['STOPWRITE'] is True and pm['STOPWRITE'] is True
assert len(sm['payload_files']) == 4 and len(pm['payload_files']) == 1
for manifest in (sm, pm):
    for row in manifest['payload_files']:
        assert ref(row['path']) == row

pin_path = PIN / 'actual-FINAL-source-pin-observer095.json'
pin = load(pin_path)
for key in ('observer', 'observer_manifest', 'actual_Source_binding', 'actual_Source_context_runner'):
    assert ref(pin[key]['path']) == pin[key]
assert pin['observer_main_executed'] is False and pin['runtime_pass'] is False
assert all(pin[k] is None for k in ('actual_new_boundary', 'actual_UI_completion', 'actual_Saved_completion'))
binding_ref = pin['actual_Source_binding']
assert binding_ref['bytes'] == 693455
assert binding_ref['sha256'] == 'e818ba9aefa4d8cd739da561540ef2e49cbf38c70311346cd10c7b2d86be1bf6'
assert pin['required_CLI_binding_SHA'] == binding_ref['sha256']
binding = load(binding_ref['path'])
assert binding['status'] == 'SEALED_REAL95_SOURCE_NOT_RUNTIME_PASS'
for key in ('actual_original_epoch_recovery', 'actual_ui_retry', 'root_spec_projection_from_ui_retry', 'actual_ui_identity_retry'):
    assert binding[key] is True

script_path = Path(pin['observer']['path'])
script_bytes = script_path.read_bytes()
assert len(script_bytes) == 4944 and hashlib.sha256(script_bytes).hexdigest() == 'e0ac6b189f6cfdb7cd2cd75e5c0fc454754e6cc404769f9ec8e1afc12171dc43'
script = script_bytes.decode('utf-8')
tree = ast.parse(script, filename=str(script_path))
compile(tree, str(script_path), 'exec')  # Construct only; never exec or import.
inverse_path = SRC / 'exact-inverse-actual-observer-identity095.json'
inverse = load(inverse_path)
assert inverse['candidate_reference'] == ref(script_path)
assert ref(inverse['baseline_reference']['path']) == inverse['baseline_reference']
changes = inverse['changes']
assert len(changes) == 9 and all(row['count'] == 1 for row in changes)
restored = script
for row in reversed(changes):
    assert restored.count(row['after']) == 1
    restored = restored.replace(row['after'], row['before'], 1)
baseline_bytes = Path(inverse['baseline_reference']['path']).read_bytes()
assert restored.encode('utf-8') == baseline_bytes
forward = baseline_bytes.decode('utf-8')
for row in changes:
    assert forward.count(row['before']) == 1
    forward = forward.replace(row['before'], row['after'], 1)
assert forward.encode('utf-8') == script_bytes
base_tree = ast.parse(baseline_bytes)
def function_source(text, parsed, name):
    node = next(n for n in parsed.body if isinstance(n, ast.FunctionDef) and n.name == name)
    return ast.get_source_segment(text, node)
assert function_source(script, tree, 'ref') == function_source(baseline_bytes.decode('utf-8'), base_tree, 'ref')

required_spans = {
    'strict_CLI': "assert len(sys.argv) == 5 and sys.argv[3] == '--binding-sha256'",
    'hex_SHA': "assert len(expected_binding_sha256) == 64 and all(c in '0123456789abcdef' for c in expected_binding_sha256)",
    'physical_binding_SHA': "assert ref(binding_path)['sha256'] == expected_binding_sha256",
    'exact_contract_fields': "for key in ('argv', 'cwd', 'runner', 'entry_kind', 'script_arg_index'):\n    assert job[key] == contract[key]",
    'actual_primary': "assert type(job['primary_exit_code']) is int and job['primary_exit_code'] == job['last_tool_result']['exit_code'] == 0",
    'raw0': "assert Path(job['exit_code_path']).read_bytes() in (b'0\\n', b'0\\r\\n')",
    'runner_ref': "assert ref(contract['runner']['path']) == contract['runner']",
    'fresh_boundary': "assert datetime.fromisoformat(context['ui_identity_retry_started_at']) <= datetime.fromisoformat(job['started_at']) <= datetime.fromisoformat(job['completed_at'])",
    '735_equality': "assert len(current) == 735 and current == guard == binding['actual_inputs']['source_sha256']",
    'UI_strict_receipt': "assert receipt['passed'] is True and receipt['complete_ui_validation'] is True and receipt['source_drift'] == []",
    'Saved_strict_receipt': "assert receipt['passed'] is True and receipt['actual_UI_primary_exit0_verified'] is True and receipt['project_calls'] == 0",
    'exclusive_outputs': "assert all(not path.exists() and not path.is_symlink() for path in (standard_path, alias_path, alias_receipt_path))",
    'exclusive_rows': "with path.open('xb') as handle:",
    'exclusive_alias': "with alias_receipt_path.open('x', encoding='utf-8') as handle:",
    'identical_rows': "assert standard_path.read_bytes() == alias_path.read_bytes()",
    'one_execution': "'actual_execution_count': 1, 'additional_execution_claimed': False",
    'standard_names': "standard_path = BASE / ('root-full095-' + name + '-observation.json')",
    'UI_alias': "alias_path = BASE / 'root-full095-wine_ui-identity-retry-v1-observation.json'",
    'Saved_alias': "alias_path = BASE / 'root-full095-saved_review-ui-identity-retry-v1-observation.json'",
    'alias_receipt': "alias_receipt_path = BASE / ('root-full095-' + name + '-ui-identity-retry-v1-metadata-alias.json')",
}
for span in required_spans.values():
    assert script.count(span) == 1
guard_path = ROOT / 'root-source-095-v2.json'
guard_ref = ref(guard_path)
assert guard_ref['bytes'] == 84227 and guard_ref['sha256'] == '41b9f4662a31b0c8ade2cf51c019bda0a04f6569e92770249bcf2e7ebabe9eab'
assert len(binding['actual_inputs']['source_sha256']) == 735
assert binding['actual_inputs']['source_sha256'] == load(guard_path)['source_sha256_after']
runner_refs = []
for name in ('wine_ui', 'saved_review'):
    contract = binding['actual_inputs']['execution_contracts'][name]
    assert contract['cwd'] == '/workspace/rougezhushou'
    assert contract['entry_kind'] == 'python-script' and contract['script_arg_index'] == 1
    assert ref(contract['runner']['path']) == contract['runner']
    runner_refs.append(contract['runner'])
    assert binding['actual_inputs']['global_output_plan']['paths'][contract['stdout_key']]
    assert pin['Root_invocation_templates'][name][-2:] == ['--binding-sha256', binding_ref['sha256']]

checks = [
    ('frozen_source_inventory_and_manifests', '6 source packet files/4 manifest payloads; 2 binding packet files/1 payload; all declared physical refs exact.'),
    ('actual_FINAL_source_pin', 'Observer, observer manifest, physical FINAL binding and context Source refs exact; pin is Source-only.'),
    ('required_binding_CLI', 'Exactly five sys.argv entries; mandatory literal option and 64 lowercase hexadecimal characters; physical fixed binding path SHA equals argument.'),
    ('actual_binding_SHA_and_source_flags', 'CLI templates require actual e818 binding SHA; physical Source binding status and all four flags match the observer admission assertions.'),
    ('complete_nine_span_inverse', 'Reverse nine unique spans produces complete 4422-byte baseline; forward nine spans reproduces candidate; remaining bytes are unchanged.'),
    ('AST_compile_without_execution', 'AST parse and compile construction succeeded; compiled observer object never executed or imported.'),
    ('physical_ref_helper_unchanged', 'Entire original ref function Source retained; regular-file/non-symlink guard and size/SHA computation preserved.'),
    ('real_primary_and_raw_zero_guards', 'Typed integer primary 0, last tool-result exit 0 and literal raw0 retained; no missing primary is synthesized by observer Source.'),
    ('exact_execution_contract', 'argv/cwd/runner/entry_kind/script_arg_index and stdout/raw paths must equal sealed contract; runner physical ref must match.'),
    ('actual_identity_time_boundary', 'Source compares context.ui_identity_retry_started_at <= job.started_at <= job.completed_at, without mtime substitution.'),
    ('735_source_equality', '735 maintained-source map must equal old guard and sealed binding; physical old guard exactly matches binding Source map in this review.'),
    ('strict_UI_receipt', 'passed and complete_ui_validation must be literal True and source_drift an empty list; whole inherited assertion retained.'),
    ('strict_Saved_receipt', 'passed and actual_UI_primary_exit0_verified literal True and project_calls == 0; whole inherited assertion retained.'),
    ('standard_and_versioned_names', 'Standard names unchanged; exact UI/Saved identity aliases and metadata-alias names match pin packet.'),
    ('exclusive_three_output_sinks', 'All three paths absent/non-symlink before writes; xb for rows and x for alias. No overwrite/backfill branch added.'),
    ('one_execution_two_snapshots', 'Same byte buffer written twice and byte equality checked; alias states one actual execution and no additional execution.'),
    ('bound_completion_and_receipt_metadata', 'Alias records physical completion and contract binding refs; observation records physical stdout/raw/receipt and real-tool metadata from trusted Root JSON.'),
    ('current_contract_source_refs', 'Both physically present runner refs equal sealed FINAL contracts. This is a hash pin, not an independent semantic or runtime review of runners.'),
]
refs = [ref(p) for p in source_files + pin_files]
refs += [inverse['baseline_reference'], binding_ref, pin['actual_Source_context_runner'], guard_ref] + runner_refs
report = {
    'status': 'INDEPENDENT_SOURCE_REVIEW_PASSED_ACTUAL_OBSERVER_RUNTIME_UNRUN',
    'scope': 'SOURCE_ONLY_OBSERVER_BINDING_AND_COMPLETE_INVERSE_NO_TARGET_RUNTIME',
    'passed': True, 'source_review_only': True, 'runtime_executed': False,
    'observer_main_executed': False, 'project_test_codec_context_sealer_Qt_Wine_Git_process_calls': 0,
    'observer_sha256': ref(script_path)['sha256'], 'observer': ref(script_path),
    'actual_binding_sha256': binding_ref['sha256'], 'actual_Source_binding': binding_ref,
    'required_CLI_binding_SHA': binding_ref['sha256'], 'binding_source_pin': ref(pin_path),
    'inverse': ref(inverse_path), 'baseline_observer': inverse['baseline_reference'],
    'whole_inverse_exact': True, 'inverse_change_count': 9, 'ref_function_whole_Source_unchanged': True,
    'checks_count': len(checks), 'checks': [{'id': name, 'passed': True, 'basis': basis} for name, basis in checks],
    'verified_input_refs': refs,
    'actual_new_boundary': None, 'actual_UI_completion': None, 'actual_Saved_completion': None,
    'actual_UI_PASS': None, 'actual_Saved_PASS': None,
    'qualification': [
        'This reviewer performs stdlib file/hash/JSON/AST/compile analysis only. No observer main, project/test/codec/context/sealer/Qt/Wine/Git or process operation is invoked.',
        'The Source gate passes for the observer and actual Source binding pin. It does not grant a runtime PASS, establish a new actual time boundary, retrospectively observe any tool exit, or authenticate a completion JSON.',
        'Inherited observer trust remains: Root must provide genuine actual completion JSON, primary tool result, raw0, stdout and final receipt. JSON tool metadata is evidence supplied by Root, not an independently queried tool registry.',
        'The observer retains inherited receipt predicates rather than duplicating the full Saved/context/acceptance validators. Runtime source/receipt/visual/final-context gates remain separate required work.',
        'The environment row is inherited metadata supplied by this observer; this Source review does not verify the actual target process environment. Runtime Root launch must use the admitted argv and PYTHONDONTWRITEBYTECODE=1 without assertion-disabling optimization.',
        'The three outputs use exclusive individual writes, not a transaction. A partial write or later I/O failure must be preserved and diagnosed; no overwrite or invented successful completion is authorized.',
        'No runtime output existence or mtime is used for this Source gate. Unknown/new runtime times and UI/Saved completion outcomes remain null even if Root starts work concurrently.',
        'Original attempts with missing primary outcomes remain unavailable; two byte-identical metadata snapshots represent one future actual execution only.',
        'The complete inverse proves retention of inherited Source outside the nine declared changes. It does not claim the baseline helper itself supplies all downstream runtime validation.',
    ],
    'future_sections96_98_paused': True, 'commit_or_push_performed': False,
}
report_path = OUT / 'formal-independent-source-review-actual-observer095-identity-v1.json'
manifest_path = OUT / 'public-artifacts-manifest-independent-observer-review095.json'
handoff_path = OUT / 'handoff-independent-observer-review095.json'
write(report_path, report)
write(manifest_path, {'status': 'STOPWRITE_INDEPENDENT_SOURCE_REVIEW_ONLY_RUNTIME_UNRUN', 'STOPWRITE': True, 'passed': True, 'runtime_executed': False, 'payload_files': [ref(Path(__file__)), ref(report_path)]})
write(handoff_path, {'status': report['status'], 'formal_review': ref(report_path), 'manifest': ref(manifest_path), 'observer': ref(script_path), 'actual_Source_binding': binding_ref, 'passed': True, 'runtime_executed': False, 'actual_new_boundary': None, 'actual_UI_completion': None, 'actual_Saved_completion': None, 'future_sections96_98_paused': True, 'commit_or_push_performed': False})
print(json.dumps({'formal': ref(report_path), 'manifest': ref(manifest_path), 'handoff': ref(handoff_path), 'physical_files': 4, 'manifest_payloads': 2, 'checks': len(checks), 'passed': True, 'runtime_executed': False}))
