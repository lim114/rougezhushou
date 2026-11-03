"""Independent SOURCE admission. Execute no reviewed helpers or target code."""
import argparse
import ast
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).parent
SOURCE = Path('/workspace/.continuation/full095-regression-ui-identity-resume-source-v1')
ASSEMBLER = Path('/workspace/.continuation/full095-ui-identity-root-spec-source-preparation-v1')
ROOT = Path('/workspace/rougezhushou')
GUARD = '41b9f4662a31b0c8ade2cf51c019bda0a04f6569e92770249bcf2e7ebabe9eab'
refs = {}
checks = []

def sha(data):
    return hashlib.sha256(data).hexdigest()

def read(path, expected=None):
    path = Path(path)
    assert path.is_absolute() and path.is_file() and not path.is_symlink(), str(path)
    data = path.read_bytes()
    ref = {'path': str(path), 'bytes': len(data), 'sha256': sha(data)}
    if expected:
        assert all(ref[k] == v for k, v in expected.items()), (ref, expected)
    assert str(path) not in refs or refs[str(path)] == ref, 'Input changed during review'
    refs[str(path)] = ref
    return data

def bound(ref):
    assert type(ref) is dict and set(ref) == {'path', 'bytes', 'sha256'}
    assert type(ref['path']) is str and type(ref['bytes']) is int and ref['bytes'] >= 0
    assert type(ref['sha256']) is str and re.fullmatch('[0-9a-f]{64}', ref['sha256'])
    return read(ref['path'], ref)

def doc(ref):
    return json.loads(bound(ref))

def pathname(path):
    return json.loads(read(path))

def check(name, evidence):
    checks.append({'name': name, 'passed': True, 'evidence': evidence})

def collect(value):
    if type(value) is dict:
        if set(value) == {'path', 'bytes', 'sha256'} and type(value.get('path')) is str:
            bound(value)
        else:
            for child in value.values(): collect(child)
    elif type(value) is list:
        for child in value: collect(child)

def pointer(value, location):
    assert type(location) is str and location.startswith('/')
    for key in location.split('/')[1:]:
        key = key.replace('~1', '/').replace('~0', '~')
        value = value[int(key)] if type(value) is list else value[key]
    return value

def functions(data):
    lines = data.splitlines(keepends=True)
    return {n.name: b''.join(lines[n.lineno - 1:n.end_lineno])
            for n in ast.parse(data).body if isinstance(n, ast.FunctionDef)}

def literal(data, name):
    nodes = [n for n in ast.parse(data).body if isinstance(n, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == name for t in n.targets)]
    assert len(nodes) == 1
    return ast.literal_eval(nodes[0].value)

def inverse(path, candidate_key, baseline_key, count):
    ledger = pathname(path)
    assert len(ledger['changes']) == count
    candidate = bound(ledger[candidate_key])
    recovered = candidate.decode('utf-8')
    for row in reversed(ledger['changes']):
        assert type(row['count']) is int and row['count'] > 0
        assert recovered.count(row['after']) == row['count']
        recovered = recovered.replace(row['after'], row['before'], row['count'])
    baseline = bound(ledger[baseline_key])
    assert recovered.encode('utf-8') == baseline
    check('Whole-byte inverse ' + Path(path).name, {'ledger': refs[str(path)], 'changes': count,
          'candidate': ledger[candidate_key], 'baseline': ledger[baseline_key]})
    return candidate, baseline

def source_gate(row, runner, argv, keys=None):
    review = doc(row['source_review']); pointers = row['review_pointers']
    assert pointer(review, pointers['source_pass']) is True
    assert pointer(review, pointers['runtime_pass']) is False
    assert pointer(review, pointers['runner_sha256']) == runner['sha256']
    assert pointer(review, pointers['argv']) == argv
    if keys is not None:
        assert pointer(review, pointers['source_keys']) == keys
    return review

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--spec', required=True, type=Path)
parser.add_argument('--spec-sha256', required=True)
args = parser.parse_args()
assert args.spec == Path('/workspace/.continuation/root-full095-ui-identity-retry-v1-actual-spec.json')
assert re.fullmatch('[0-9a-f]{64}', args.spec_sha256)
spec = json.loads(read(args.spec, {'sha256': args.spec_sha256}))
assert spec['status'] == 'ROOT_BOUND_ACTUAL_FULL095_UI_IDENTITY_RETRY_SOURCE_INPUTS'
assert spec['format_version'] == 3 and spec['section'] == 95
check('Concrete actual Root spec physical bytes and required status', refs[str(args.spec)])

mf_path = SOURCE / 'public-artifacts-manifest-ui-retry095.json'
mf = json.loads(read(mf_path, {'bytes': 3578, 'sha256': 'bacdf2336d69c08e994f06df41c184d7ce7086900b935207e797515af7ac297c'}))
assert mf['STOPWRITE'] is True and mf['runtime_executed'] is False and mf['available_checks_passed'] is False
assert len(mf['payload_files']) == 14
for row in mf['payload_files']:
    assert Path(row['path']).parent == SOURCE
    bound(row)
assert {p.name for p in SOURCE.iterdir()} == {Path(r['path']).name for r in mf['payload_files']} | {mf_path.name, 'handoff-ui-retry095.json'}
check('Fourteen Source payloads and exact sixteen-file frozen physical set', refs[str(mf_path)])

context, old_context = inverse(SOURCE / 'ui-retry-context-inverse095.json', 'pending_context_reference', 'baseline_context_reference', 12)
helper, old_helper = inverse(SOURCE / 'identity-recovery-helper-inverse095.json', 'candidate_reference', 'baseline_reference', 8)
sealer, old_sealer = inverse(SOURCE / 'ui-retry-sealer-delta095.json', 'candidate_reference', 'baseline_reference', 9)
assert len(context) == 36275 and sha(context) == '0cddc35c272e73fb44fbede3564cf487064dda28fcaaf4066bc3889d01148066'
assert len(helper) == 35084 and sha(helper) == 'c856d3d15bcba22eef1be61bc7f77f0f987e525c275ad4197be50c9cfeefcb99'
assert len(sealer) == 12552 and sha(sealer) == '540d00188b62da3ed56f211c4e497c1fc2ce74b6892524cc2b0fe5d655353faf'
old_f, new_f = functions(old_context), functions(context)
assert old_f.keys() == new_f.keys() and len(old_f) == 15
same = [n for n in old_f if old_f[n] == new_f[n]]
assert len(same) == 13 and [n for n in old_f if n not in same] == ['load_actual_binding', 'require_primary_executions']
check('Thirteen of fifteen full context functions retain all strict receipts and Saved visual evidence predicates', {'whole': same, 'changed': ['load_actual_binding', 'require_primary_executions']})

for name, digest in [('binding_validation095.py', 'b7a6c9b9517e3c93fb598d42b1a45ffe9969d8fb871cce04aee34d56594aa5ce'),
                     ('capability_binding095.py', 'ad1b5a9c9c4979ccd736f9571e9705e3d5a946beaeb80f868ed56800ac9a9afa'),
                     ('historical-classifications090.json', 'c17cfb0fbb87c3ecf9247b2d2492d23418b7c5782e9cb02c733b88acf749819b'),
                     ('recovery_binding095.py', 'a2c36dc353bc62bb0c96b61bf9fe47d1634ba7ea0b2b2a1d7d74af1f20a8f534')]:
    data = read(SOURCE / name, {'sha256': digest})
    assert data == read(Path('/workspace/.continuation/full095-regression-ui-cache-resume-final-v1') / name)
    if name.endswith('.py'):
        compile(data, str(SOURCE / name), 'exec')
for name, data in [('context', context), ('identity-helper', helper), ('sealer', sealer)]:
    compile(data, name, 'exec')
check('Original b7a6 ad1b c17 a2c support copies whole byte; compilation never executes', {'target_code_object_executions': 0})

assembler_mf_path = ASSEMBLER / 'public-artifacts-manifest-root-spec095.json'
assembler_mf = json.loads(read(assembler_mf_path, {'bytes': 987, 'sha256': 'e3146ee6e6b8b12205248f0cbed796f1bfa65aaa0b17f34ff80ed4bec2171b75'}))
assert assembler_mf['STOPWRITE'] is True and assembler_mf['target_execution_calls'] == 0
for row in assembler_mf['payload_files']: bound(row)
assembler_source = read(ASSEMBLER / 'assemble_root_identity_spec095.py', {'bytes': 20108, 'sha256': 'd733aa1ffa8c20e224e04867487e6cc988258570e7e437a6d544a0f1a34eb0fe'})
compile(assembler_source, 'unexecuted-metadata-assembler', 'exec')
tree = ast.parse(assembler_source)
imports = {n.module.split('.')[0] for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)}
imports |= {a.name.split('.')[0] for n in ast.walk(tree) if isinstance(n, ast.Import) for a in n.names}
assert imports <= {'argparse', 'ast', 'copy', 'datetime', 'hashlib', 'json', 'pathlib', 're'}
assert not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in {'exec', 'eval', '__import__'} for n in ast.walk(tree))
check('Frozen metadata assembler standard-library imports without target code execution', {'manifest': refs[str(assembler_mf_path)], 'source': refs[str(ASSEMBLER / 'assemble_root_identity_spec095.py')], 'imports': sorted(imports)})

template = pathname(SOURCE / 'root-ui-retry-input-template095.json')
prior = doc(spec['prior_ui_retry']['binding'])
assert spec['prior_ui_retry'] == literal(helper, 'IDENTITY_PRIOR_UI_RETRY')
assert spec['prior_incomplete_ui_cache'] == literal(helper, 'IDENTITY_INCOMPLETE_UI')
base = prior['recovery_spec']
for key in ('original', 'preserved_passed_executions', 'prior_failed_execution', 'adapters', 'prior_recovery',
            'prior_incomplete_ui', 'preserved_recovery_passed_executions', 'selected_retry_output_paths', 'prior_selected_failed_execution'):
    assert spec[key] == base[key]
collect(spec)
assert spec['ui_retry_output_paths'] == {**literal(helper, 'UI_OUTPUTS'), **literal(helper, 'CONTROL_OUTPUTS')}
assert spec['replacement_output_paths'] == {**spec['ui_retry_output_paths'],
    **{k: v for k, v in base['replacement_output_paths'].items() if k not in base['ui_retry_output_paths']},
    **spec['selected_retry_output_paths']}
check('Exact old b83 immutable fields and only fresh UI Saved control projection', {'prior_binding': spec['prior_ui_retry']['binding'], 'unchanged_fields': ['original', 'preserved_passed_executions', 'prior_failed_execution', 'adapters', 'prior_recovery', 'prior_incomplete_ui', 'preserved_recovery_passed_executions', 'selected_retry_output_paths', 'prior_selected_failed_execution']})

guard = pathname('/workspace/.continuation/root-source-095-v2.json')
assert refs['/workspace/.continuation/root-source-095-v2.json']['sha256'] == GUARD
maintained = {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for d in ('rouge', 'tests', 'scripts')
              for p in sorted((ROOT / d).rglob('*')) if p.is_file() and p.suffix in ('.py', '.json') and '__pycache__' not in p.parts}
assert len(maintained) == 735 and maintained == guard['source_sha256_after'] == prior['actual_inputs']['source_sha256']
assert prior['actual_inputs']['branch'] == 'codex/p2-development' and prior['actual_inputs']['actual_base_HEAD'] == 'f509d186e501bfcfd042e45b46e398ec756840ec'
check('All 735 physical maintained source files match immutable guard and paused b83 source map', {'source_files': 735, 'guard': refs['/workspace/.continuation/root-source-095-v2.json'], 'branch_in_existing_binding': 'codex/p2-development', 'actual_live_Git_invocations_by_reviewer': 0})

original_epoch = doc(spec['original']['context'])
recovery_epoch = doc(spec['prior_recovery']['context'])
ui_epoch = doc(spec['prior_ui_retry']['context'])
assert original_epoch['started_at'] == recovery_epoch['started_at'] == ui_epoch['started_at']
assert recovery_epoch['recovery_started_at'] == ui_epoch['recovery_started_at'] == '2026-10-08T23:36:41.779450+00:00'
assert ui_epoch['ui_retry_started_at'] == '2026-10-09T00:59:43.753835+00:00'
assert all(v['available_checks_passed'] is False for v in (original_epoch, recovery_epoch, ui_epoch))
assert 'ui_identity_retry_started_at' not in spec
check('Three actual prior epoch boundaries immutable and new resume boundary still uncreated', {'started_at': original_epoch['started_at'], 'recovery_started_at': recovery_epoch['recovery_started_at'], 'ui_retry_started_at': ui_epoch['ui_retry_started_at'], 'ui_identity_retry_started_at': None})

six = {name: row for field in ('preserved_passed_executions', 'preserved_recovery_passed_executions') for name, row in spec[field].items()}
assert set(six) == {'linux_full', 'linux_selected', 'linux_pip', 'wine_pip', 'wine_full', 'wine_selected'}
for name, row in six.items():
    observation = doc(row['observation'])
    assert observation['actual_root_observed_primary_exit'] is True and observation['primary_exit_code_captured'] is True
    assert type(observation['primary_exit_code']) is int and observation['primary_exit_code'] == 0
    assert bound(observation['exit_code_file']) in (b'0\n', b'0\r\n')
    bound(observation['stdout_log'])
    assert observation['argv'] == prior['actual_inputs']['execution_contracts'][name]['argv']
    assert observation['cwd'] == prior['actual_inputs']['execution_contracts'][name]['cwd']
check('Six real primary zeros exact observations physical logs raw status and reviewed launch contracts retained without replay', {n: r['observation'] for n, r in six.items()})

lost_details = []
for field, chunk_count, session in [('prior_incomplete_ui', 275, 61366), ('prior_incomplete_ui_cache', 2310, 53266)]:
    loss = doc(spec[field]); collect(loss)
    assert loss['primary_exit_code'] is None and loss['primary_exit_code_captured'] is False
    assert loss['actual_root_requested_process_termination'] is False and loss['full_validation_passed'] is False
    assert loss['actual_original_UI_session_id'] == session and loss['closed_native_chunks'] == chunk_count
    assert loss['raw_primary_status_absent'] is True and loss['final_UI_receipt_absent'] is True
    index = doc(loss['native_index'])
    assert index['outcome'] == 'pending' and len(index['chunks']) == chunk_count
    chunk_refs = []
    for row in index['chunks']:
        ref = {'path': str(Path('/workspace/.compat') / row['file']), 'bytes': row['bytes'], 'sha256': row['sha256']}
        bound(ref); chunk_refs.append(ref)
    if field == 'prior_incomplete_ui_cache':
        assert loss['cause_of_external_session_loss'] == 'UNKNOWN'
        assert loss['same_UI_execution_problem_incomplete_attempt_count'] == 2 and loss['third_attempt_failure_requires_deferral'] is True
        assert chunk_refs == loss['all_closed_compressed_chunk_refs_verified']
        assert bound(loss['preserved_native_index_snapshot']) == bound(loss['native_index'])
        assert loss['six_completed_primary_observations_preserved'] == {n: r['observation'] for n, r in six.items()}
    lost_details.append({'capsule': spec[field], 'chunks_verified': chunk_count, 'primary_exit_code': None, 'runtime_PASS': False})
check('Both lost UI capsules every 275 plus 2310 compressed native chunk physical bytes preserved with unknown primary outcomes', lost_details)

retry = spec['ui_retry']; contract = doc(retry['source_contract'])
producer = doc(retry['manifest'])
assert producer['STOPWRITE'] is True and producer['root_source_guard_sha256'] == GUARD and producer['runtime_calls'] == 0
runner = bound(retry['runner'])
assert retry['runner'] == contract['runner'] and retry['runner']['sha256'] == '0e8a0bc1ed4e890cd6a0cf762c7437ced1080dba6ac82e48c680e8d6dc226b0d'
assert sum(isinstance(n, ast.Assert) for n in ast.walk(ast.parse(runner))) == 907
assert contract['source_keys'] == prior['actual_inputs']['UI_expected_own_source_keys'] and len(contract['source_keys']) == 129
ui_formal = source_gate(retry, retry['runner'], contract['execution_argv'], contract['source_keys'])
saved = retry['saved_review_source']; saved_formal = source_gate(saved, saved['runner'], saved['argv'])
assert saved['runner']['sha256'] == '6d94c3effb6c56987ece108af152b885ce35485f6220533596ed888d259f41ff'
assert saved['argv'] == [prior['root_spec']['linux_python_entry'], saved['runner']['path'], '--spec', spec['ui_retry_output_paths']['saved_review_input'], '--output', spec['ui_retry_output_paths']['saved_review_receipt']]
check('Concrete UI and Saved independent Source gates exact runner argv own129 keys with runtime false', {'UI_formal': retry['source_review'], 'Saved_formal': saved['source_review'], '907_assertions': True})

prelaunch_ref = spec['root_ui_prelaunch']; prelaunch = doc(prelaunch_ref)
assert prelaunch_ref['path'] == '/workspace/.continuation/root-full095-ui-identity-retry-v1-prelaunch.json'
assert prelaunch['source_gate_passed'] is True and prelaunch['runtime_pass'] is False and prelaunch['outputs_absent'] is True
assert prelaunch['runner'] == retry['runner'] and prelaunch['actual_argv'] == contract['execution_argv']
assert prelaunch['cwd'] == str(ROOT) and prelaunch['formal_source_review'] == retry['source_review']
assert prelaunch['source_contract'] == retry['source_contract'] and prelaunch['source_guard'] == contract['source_guard']
assert prelaunch['actual_Root_epoch_binding'] == spec['prior_ui_retry']['binding']
assert prelaunch['second_UI_loss_capsule_Root_binding_required'] == spec['prior_incomplete_ui_cache']
assert prelaunch['actual_source_files_verified'] == 735 and prelaunch['actual_assertions_in_source'] == 907
assert prelaunch['target_execution_performed'] is False and prelaunch['next_section_development_paused'] is True
assert prelaunch['root_source_assembler'] == refs[str(ASSEMBLER / 'assemble_root_identity_spec095.py')]
assert datetime.fromisoformat(prelaunch['recorded_at']) <= datetime.now(timezone.utc)
assert all(not Path(p).exists() for p in spec['ui_retry_output_paths'].values())
assert all(not Path(p).exists() for p in contract['fresh_evidence_directories'])
check('Actual prelaunch nonnull full reference strictly bound to Source formal guard 735 907 prior b83 lost2 and future sink absence', prelaunch_ref)

expected = deepcopy(template)
expected['status'] = spec['status']; expected['root_ui_prelaunch'] = prelaunch_ref
ui = deepcopy(prior['root_spec']['ui'])
ui.update(runner=retry['runner'], receipt_path=contract['output_plan']['receipt'], console_log_path=contract['output_plan']['console_log'],
          required_saved_outputs=contract['required_saved_outputs'], optional_output_paths=contract['optional_output_paths'], fresh_evidence_directories=contract['fresh_evidence_directories'])
ui['execution_contract'].update(argv=contract['execution_argv'], source_review=retry['source_review'], review_pointers={k: retry['review_pointers'][k] for k in ('source_pass', 'runtime_pass', 'runner_sha256', 'argv')})
ui['own_source_scope'].update(source_review=retry['source_review'], review_pointers={k: retry['review_pointers'][k] for k in ('source_pass', 'runtime_pass', 'runner_sha256', 'source_keys')})
expected['ui_retry'].update(manifest=retry['manifest'], source_contract=retry['source_contract'], runner=retry['runner'], source_review=retry['source_review'], ui=ui)
expected['ui_retry']['saved_review_source'].update(runner=saved['runner'], source_review=saved['source_review'])
assert spec == expected
check('Entire actual spec equals independently reconstructed frozen template plus reviewed minimal Source fields and actual prelaunch', {'unexpected_or_unqualified_field_deltas': []})

sealer_text = sealer.decode('utf-8')
assert "review['recovery_spec_sha256'] == args.spec_sha256" in sealer_text
assert "review['source_manifest_sha256'] == digest(manifest_path.read_bytes())" in sealer_text
assert "review['pending_context_sha256'] == digest(pending)" in sealer_text
assert "review['recovery_helper_sha256'] == digest((here / 'identity_binding095.py').read_bytes())" in sealer_text
assert "review['sealer_sha256'] == digest(Path(__file__).read_bytes())" in sealer_text
assert "reverse == pending" in sealer_text and "actual_ui_identity_retry': True" in sealer_text
assert literal(context, 'PENDING') is True
assert "ui_identity_retry_started_at=now()" in context.decode('utf-8')
assert "ui_retry_started_at=prior_ui_context['ui_retry_started_at']" in context.decode('utf-8')
assert "began >= datetime.fromisoformat(context['ui_identity_retry_started_at'])" in context.decode('utf-8')
check('Sealer formal admission pins exact actual spec and source; only two binding literals; actual new boundary created later by Root resume', {'new_actual_UI_boundary': None, 'sealer_executed_by_reviewer': False})

for ref in list(refs.values()):
    # Large historical gzip payloads were already hashed above; reread only Source and controls.
    if not ref['path'].endswith('.gz'): bound(ref)
after = {p.relative_to(ROOT).as_posix(): sha(p.read_bytes()) for d in ('rouge', 'tests', 'scripts') for p in sorted((ROOT / d).rglob('*')) if p.is_file() and p.suffix in ('.py', '.json') and '__pycache__' not in p.parts}
assert after == maintained
check('Source control inputs reread and full maintained735 map unchanged during independent review', {'large_compressed_history_hashed_once': True, 'source_files': 735, 'maintained_source_drift': []})

report = {'format_version': 1, 'section': 95, 'status': 'STOPWRITE_INDEPENDENT_ACTUAL_IDENTITY_RECOVERY_SPEC_SOURCE_GATE_PASSED_RUNTIME_UNRUN',
          'source_gate_passed': True, 'runtime_pass': False, 'execution_ready': False,
          'recovery_spec_sha256': args.spec_sha256, 'recovery_spec': refs[str(args.spec)],
          'source_manifest_sha256': refs[str(mf_path)]['sha256'], 'pending_context_sha256': sha(context),
          'recovery_helper_sha256': sha(helper), 'sealer_sha256': sha(sealer),
          'actual_prelaunch': prelaunch_ref, 'review_completed_at_UTC': datetime.now(timezone.utc).isoformat(),
          'reviewer_role': 'Independent Source reviewer, not context sealer or assembler author',
          'independent_standard_library_review': {'checks': len(checks), 'passed': len(checks), 'blocked': 0, 'results': checks},
          'checked_file_refs': dict(sorted(refs.items())),
          'qualification': ['Source admission of a real Root-spec file, not execution of its context, sealer, UI, Saved, or any product.',
                            'Actual nonnull Root prelaunch is checked here; identity helper alone only checks its planned path and does not reject NULL root_ui_prelaunch.',
                            'Both old UI primary outcomes remain NULL and incomplete; 275 plus 2310 compressed chunks are historical partial evidence, never successful UI proof.',
                            'Six earlier raw primary zeros are retained without rerunning. UI and Saved must later produce fresh genuine primary zeros after actual third resume.',
                            'Compile only checks local Source syntax. No reviewed code object, codec, project, test, Wine, Qt, DLL, sealer, context, Git, process-control, or API call was executed.',
                            'Read-only full735 hashing verifies maintained bytes; no live Git branch/head query is performed by this reviewer. Root original validators still enforce Git requirements.',
                            'New binding SHA, third resume boundary, UI final proof, Saved input proof and runtime PASS remain NULL until real Root actions.',
                            'The third same-issue UI unsuccessful attempt requires deferral; this gate does not approve any fourth retry.'],
          'actual_new_binding': None, 'actual_ui_identity_retry_started_at': None,
          'actual_UI_primary_exit_code': None, 'actual_Saved_primary_exit_code': None, 'actual_runtime_PASS': None,
          'completed_section_increment': 0, 'available_checks_passed': False, 'commit_or_push_performed': False,
          'reviewed_target_execution_counts': {'helper': 0, 'sealer': 0, 'context': 0, 'codecs': 0, 'project': 0, 'tests': 0, 'Wine': 0, 'Qt': 0, 'DLL': 0, 'Git': 0, 'process_control': 0}, 'STOPWRITE': True}
output = HERE / 'formal-source-review-actual-identity-recovery095-v1.json'
with output.open('x', encoding='utf-8') as stream:
    json.dump(report, stream, ensure_ascii=False, allow_nan=False, indent=2); stream.write('\n')
print(json.dumps({'source_gate_passed': True, 'runtime_pass': False, 'checks': len(checks), 'file': str(output), 'spec_sha256': args.spec_sha256}))
