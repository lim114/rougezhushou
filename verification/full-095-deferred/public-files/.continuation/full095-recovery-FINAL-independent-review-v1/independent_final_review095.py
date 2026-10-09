"""Independent actual sealed recovery SOURCE audit; no reviewed source imports."""
import ast
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
FINAL = Path('/workspace/.continuation/full095-regression-capability-resume-final-v1')
PENDING = Path('/workspace/.continuation/full095-regression-capability-resume-pending-v1')
ROOT = Path('/workspace/rougezhushou')
SPEC = Path('/workspace/.continuation/root-full095-recovery-input-spec-v1.json')
REVIEW = Path('/workspace/.continuation/full095-recovery-actual-spec-independent-review-v1/formal-independent-actual-spec-review-recovery095-v1.json')
checks = []

def ref(path):
    data = Path(path).read_bytes()
    return {'path': str(path), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}

def read_json(path):
    return json.loads(Path(path).read_bytes())

def refs_in(value):
    if isinstance(value, dict):
        if {'path', 'bytes', 'sha256'} <= set(value):
            return [value]
        return [row for child in value.values() for row in refs_in(child)]
    if isinstance(value, list):
        return [row for child in value for row in refs_in(child)]
    return []

def check(label, passed, evidence=None):
    checks.append({'id': f'F{len(checks)+1:02d}', 'check': label, 'passed': bool(passed), 'evidence': evidence})

def canonical(path):
    return str(Path(path).resolve())

mf_path = FINAL / 'public-artifacts-manifest-sealed-recovery095.json'
mf_before = ref(mf_path)
mf = read_json(mf_path)
hand_path = FINAL / 'handoff-sealed-recovery095.json'
hand_before = ref(hand_path)
hand = read_json(hand_path)
rows = mf['payload_files']
expected = {Path(row['path']).name for row in rows} | {mf_path.name, hand_path.name}
check('Actual FINAL exactly eight regular files and six unique SHA-bound payload files',
      len(rows) == 6 and len(expected) == 8 and {path.name for path in FINAL.iterdir()} == expected
      and all(path.is_file() and not path.is_symlink() for path in FINAL.iterdir())
      and all(Path(row['path']).parent == FINAL and ref(row['path']) == row for row in rows))
check('Actual FINAL MF and STOPWRITE handoff declare SOURCE bound runtime pending without pass claims',
      mf['status'] == 'FINAL_RECOVERY_SOURCE_BOUND_RUNTIME_NOT_EXECUTED'
      and hand['status'] == 'FINAL_STOPWRITE_RECOVERY_SOURCE_BOUND_RUNTIME_PENDING'
      and hand['manifest'] == mf_before and hand['available_checks_passed'] is False
      and hand['source_binding_passed'] is True and hand['runtime_executions_by_sealer'] == 0)
spec_ref = ref(SPEC)
spec = read_json(SPEC)
review_ref = ref(REVIEW)
review = read_json(REVIEW)
source_mf_ref = ref(PENDING / 'public-artifacts-manifest-recovery095.json')
source_mf = read_json(source_mf_ref['path'])
binding_path = FINAL / 'actual-full095-source-binding.json'
binding_ref = ref(binding_path)
binding = read_json(binding_path)
runner_path = FINAL / 'full095_context_recovery.py'
runner_ref = ref(runner_path)
check('Actual root-reported FINAL MF/binding/runner fullrefs match independently inspected bytes',
      mf_before['bytes'] == 1818 and mf_before['sha256'] == '14805d5946187155431676d48303daf06f983865027240cc91531d9febb71ce7'
      and binding_ref['bytes'] == 383874 and binding_ref['sha256'] == 'af943d5f3b0c5996c83fb5d1ee82f793c96a7937e7ed493604fa126a4bbf73f3'
      and runner_ref['bytes'] == 32395 and runner_ref['sha256'] == '9e341441992d616bea7d91f22f4b14745d58799bde9f2e738f5b2d9434315403'
      and hand['context_runner'] == runner_ref and hand['source_binding'] == binding_ref)
check('All seven actual-spec SOURCE approval fields and formal report current physical SHA satisfy exact sealer gate',
      review['source_gate_passed'] is True and review['runtime_pass'] is False
      and review['recovery_spec_sha256'] == spec_ref['sha256'] == '1e2479c3a0079b1cc96f746f7b74fd37ff8fc7b0746f3bc0c298ffa808a78254'
      and review['source_manifest_sha256'] == source_mf_ref['sha256']
      and review['pending_context_sha256'] == ref(PENDING / 'full095_context_recovery_pending.py')['sha256']
      and review['recovery_helper_sha256'] == ref(PENDING / 'recovery_binding095.py')['sha256']
      and review['sealer_sha256'] == ref(PENDING / 'seal_recovery095.py')['sha256']
      and review_ref['sha256'] == '52fbac3aed66d8a239b76bf25404e5413b50987ecd3016fd62c0935688c5780d')
check('Original frozen source packet and all current payload bytes remain unchanged',
      mf['original_source_packet'] == source_mf_ref and all(ref(row['path']) == row for row in source_mf['payload_files']))
support_names = ('binding_validation095.py', 'historical-classifications090.json', 'recovery_binding095.py')
support_refs = [ref(FINAL / name) for name in support_names]
check('Actual FINAL three support files are exact original/source-approved whole files with bound refs',
      all((FINAL / name).read_bytes() == (PENDING / name).read_bytes() for name in support_names)
      and binding['final_support_files'] == support_refs
      and (FINAL / 'binding_validation095.py').read_bytes()
      == (Path(spec['original']['binding']['path']).parent / 'binding_validation095.py').read_bytes())
pending = (PENDING / 'full095_context_recovery_pending.py').read_bytes()
final = runner_path.read_bytes()
expected_final = pending.replace(b'PENDING = True\n', b'PENDING = False\n', 1)
expected_final = expected_final.replace(b"BOUND_BINDING_SHA256 = '__ACTUAL_RECOVERY_BINDING_SHA256_PENDING__'",
                                      ("BOUND_BINDING_SHA256 = '" + binding_ref['sha256'] + "'").encode(), 1)
check('Actual pending to FINAL whole source differs only by two exact binding literals', final == expected_final)
inverse_to_pending = final.replace(b'PENDING = False\n', b'PENDING = True\n', 1)
inverse_to_pending = inverse_to_pending.replace(("BOUND_BINDING_SHA256 = '" + binding_ref['sha256'] + "'").encode(),
                                               b"BOUND_BINDING_SHA256 = '__ACTUAL_RECOVERY_BINDING_SHA256_PENDING__'", 1)
check('Independent actual FINAL two-literal inverse equals complete frozen pending bytes', inverse_to_pending == pending)
inverse = read_json(PENDING / 'recovery-context-inverse095.json')
back_to_original = inverse_to_pending.decode()
unique = True
for operation in reversed(inverse['changes']):
    unique = unique and back_to_original.count(operation['after']) == 1
    back_to_original = back_to_original.replace(operation['after'], operation['before'], 1)
check('Actual FINAL then original fifteen-delta inverse preserves entire actual original context',
      unique and len(inverse['changes']) == 15 and back_to_original.encode()
      == Path(spec['original']['runner']['path']).read_bytes())
tree = ast.parse(final)
bound_sha = next(ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign)
                 and any(isinstance(target, ast.Name) and target.id == 'BOUND_BINDING_SHA256' for target in node.targets))
pending_flag = next(ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign)
                   and any(isinstance(target, ast.Name) and target.id == 'PENDING' for target in node.targets))
check('Actual FINAL parses, disables pending guard only after binding and seals the actual binding SHA',
      pending_flag is False and bound_sha == binding_ref['sha256'])
original = read_json(spec['original']['binding']['path'])
original_context = read_json(spec['original']['context']['path'])
source_paths = [row['path'] for row in source_mf['payload_files']]
source_paths.extend((source_mf_ref['path'], str(PENDING / 'handoff-recovery095.json'), str(SPEC), str(REVIEW)))
extra_immutable = source_paths + [row['path'] for row in support_refs]
extra_immutable.extend((str(runner_path), str(binding_path)))
actual = deepcopy(original['actual_inputs'])
actual['execution_contracts'] = deepcopy(review['projected_execution_contracts'])
plan = deepcopy(original['actual_inputs']['global_output_plan'])
plan['paths'].update(spec['replacement_output_paths'])
plan['canonical_paths'] = {name: canonical(path) for name, path in plan['paths'].items()}
immutable_paths = [row['path'] for row in refs_in(spec)]
observations = [read_json(row['observation']['path']) for row in spec['preserved_passed_executions'].values()]
failed_observation = read_json(spec['prior_failed_execution']['observation']['path'])
for observation in (*observations, failed_observation):
    immutable_paths.extend(row['path'] for row in refs_in(observation))
immutable_paths.extend(extra_immutable)
plan['immutable_input_paths'] = sorted(set(plan['immutable_input_paths']) | {canonical(path) for path in immutable_paths})
actual['global_output_plan'] = plan
check('Own independent metadata projection equals entire actual FINAL actual_inputs without calling helpers',
      actual == binding['actual_inputs'])
check('Projection retains complete source735/classifier342/selectors/UI own129/saved/archives/dependency maps',
      all(actual[key] == value for key, value in original['actual_inputs'].items()
          if key not in ('execution_contracts', 'global_output_plan'))
      and actual['source_files'] == 735 and len(actual['classifier_source_sha256']) == 342
      and len(actual['UI_expected_own_source_keys']) == 129)
check('Actual binding exactly retains original root spec/reference and current immutable source/recovery spec/review refs',
      binding['root_spec'] == original['root_spec'] and binding['root_spec_reference'] == original['root_spec_reference']
      and binding['recovery_spec'] == spec and binding['recovery_spec_reference'] == spec_ref
      and binding['recovery_formal_source_review'] == review_ref
      and binding['source_package_input_paths'] == source_paths
      and binding['source_preparation_manifest'] == source_mf_ref)
check('SOURCE binding metadata never claims actual full pass, execution, commit or push',
      binding['status'] == 'SEALED_REAL95_SOURCE_NOT_RUNTIME_PASS'
      and binding['actual_original_epoch_recovery'] is True
      and binding['original_classifier_unchanged'] is True and binding['project_calls'] == 0
      and binding['full095_execution_performed_by_sealer'] is False
      and binding['available_checks_passed'] is False and binding['commit_or_push_performed'] is False)
check('Exactly two Wine contracts change; all other six original execution contracts remain whole exact',
      {name for name in actual['execution_contracts'] if actual['execution_contracts'][name]
       != original['actual_inputs']['execution_contracts'][name]} == {'wine_full', 'wine_selected'}
      and actual['execution_contracts'] == review['projected_execution_contracts'])
check('Exactly five fixed planned output changes; all33 unique UI/native/PNG/saved/selected/pip output names retain their source-approved paths',
      plan['paths'] == review['projected_output_paths']
      and {name for name in plan['paths'] if plan['paths'][name]
           != original['actual_inputs']['global_output_plan']['paths'][name]} == set(spec['replacement_output_paths'])
      and len(plan['paths']) == len(set(plan['canonical_paths'].values())) == 33
      and plan['fresh_evidence_directories'] == original['actual_inputs']['global_output_plan']['fresh_evidence_directories'])
check('Four immutable actual success observations and original failure refs remain exact; no UI/future outcome was newly bound',
      set(spec['preserved_passed_executions']) == {'linux_full', 'linux_selected', 'linux_pip', 'wine_pip'}
      and all(ref(row['observation']['path']) == row['observation'] for row in spec['preserved_passed_executions'].values())
      and all(observation['primary_exit_code'] == 0 for observation in observations)
      and failed_observation['primary_exit_code'] == 1
      and failed_observation['actual_tool_observation'] == {'session_id': 37864, 'completion_tool_chunk': '6e35c0'}
      and ref(spec['prior_failed_execution']['receipt']['path']) == spec['prior_failed_execution']['receipt'])
seal_receipt_path = FINAL / 'seal-source-recovery-receipt095.json'
seal_receipt = read_json(seal_receipt_path)
check('Actual sealer receipt preserves original epoch, original failure and real prior successes without runtime claims',
      seal_receipt['status'] == 'PASS_SOURCE_RECOVERY_SEAL_ONLY_RUNTIME_PENDING'
      and seal_receipt['original_context'] == spec['original']['context']
      and seal_receipt['original_context_epoch_started_at'] == original_context['started_at']
      and seal_receipt['preserved_passed_executions'] == spec['preserved_passed_executions']
      and seal_receipt['prior_failed_execution'] == spec['prior_failed_execution']
      and seal_receipt['changed_output_paths'] == spec['replacement_output_paths']
      and seal_receipt['changed_execution_contracts'] == ['wine_full', 'wine_selected']
      and seal_receipt['runtime_executions'] == seal_receipt['project_calls'] == 0
      and seal_receipt['available_checks_passed'] is False)
new_paths = spec['replacement_output_paths']
check('Before actual resume all five new recovery/retry sinks and original final context sink remain unoccupied',
      all(not Path(path).exists() for path in new_paths.values()) and not Path(plan['paths']['context_final']).exists())
check('No actual new adapter witness can exist before resume at new raw/full sinks',
      not Path(new_paths['wine_full_exit_code']).exists()
      and not Path(actual['execution_contracts']['wine_selected']['exit_code_path']).exists())
source_map = {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
              for folder in ('rouge', 'tests', 'scripts') for path in sorted((ROOT / folder).rglob('*'))
              if path.is_file() and path.suffix in ('.py', '.json') and '__pycache__' not in path.parts}
check('Actual maintained source735 remains exactly original source epoch and current actual binding map',
      len(source_map) == 735 and source_map == original['actual_inputs']['source_sha256'] == actual['source_sha256'])
root_seal_exit = Path('/workspace/.continuation/root-seal-full095-recovery.exit-code')
root_seal_log = Path('/workspace/.continuation/root-seal-full095-recovery.log')
root_seal_summary = read_json(root_seal_log)
check('Actual root SOURCE sealer physical primary zero and stdout identify final packet without pretending runtime pass',
      root_seal_exit.read_bytes() in (b'0\n', b'0\r\n')
      and root_seal_summary['status'] == hand['status']
      and root_seal_summary['source_files'] == 735 and root_seal_summary['available_checks_passed'] is False
      and root_seal_summary['runtime_executions'] == 0 and root_seal_summary['original_start_replayed'] is False)
check('Final runner exact-source inverse retains all original eight/UI/saved/PNG/native/source assertions and adds adapter recovery timestamp gate',
      b"began >= datetime.fromisoformat(context['recovery_started_at'])" in final
      and b"entry == bound_json(preserved[name]['observation'])" in final
      and b"actual_ui_extra_acceptance(Path(sys.argv[5]), binding, ui_ref, witness)" in final
      and b"require(sys.argv[1] in ('resume', 'finish')" in final)
check('Actual FINAL MF/hand/source spec/current review and every payload remain unchanged at review end',
      ref(mf_path) == mf_before and ref(hand_path) == hand_before and ref(SPEC) == spec_ref and ref(REVIEW) == review_ref
      and all(ref(row['path']) == row for row in rows))
passed = all(row['passed'] for row in checks)
report = {'format_version': 1, 'section': 95, 'checked_at': datetime.now(timezone.utc).isoformat(),
          'status': 'PASS_INDEPENDENT_ACTUAL_FINAL_RECOVERY_SOURCE_REVIEW_RUNTIME_PENDING' if passed else 'BLOCK_ACTUAL_FINAL_RECOVERY_SOURCE_REVIEW',
          'source_gate_passed': passed, 'runtime_pass': False,
          'final_manifest_sha256': mf_before['sha256'], 'final_binding_sha256': binding_ref['sha256'],
          'runner_sha256': runner_ref['sha256'], 'recovery_spec_sha256': spec_ref['sha256'],
          'final_manifest': mf_before, 'final_binding': binding_ref, 'final_runner': runner_ref,
          'actual_root_spec': spec_ref, 'actual_spec_source_review': review_ref,
          'source_manifest_sha256': source_mf_ref['sha256'],
          'pending_context_sha256': ref(PENDING / 'full095_context_recovery_pending.py')['sha256'],
          'recovery_helper_sha256': ref(FINAL / 'recovery_binding095.py')['sha256'],
          'binding_validator_sha256': ref(FINAL / 'binding_validation095.py')['sha256'],
          'sealer_sha256': ref(PENDING / 'seal_recovery095.py')['sha256'],
          'original_context_started_at': original_context['started_at'],
          'execution_argv': {'resume': ['/workspace/rougezhushou/.venv/bin/python', str(runner_path), 'resume'],
              'finish': ['/workspace/rougezhushou/.venv/bin/python', str(runner_path), 'finish', '--executions',
              plan['paths']['execution_witness'], '--ui-acceptance', plan['paths']['ui_extra_acceptance']]},
          'actual_projected_execution_contracts': actual['execution_contracts'],
          'actual_projected_output_paths': plan['paths'], 'source_checks': len(checks), 'checks': checks,
          'blocking_checks': [row for row in checks if not row['passed']],
          'root_actual_source_sealer': {'console': ref(root_seal_log), 'physical_exit': ref(root_seal_exit),
              'trusted_root_tool_observation': {'session_id': 85247, 'completion_tool_chunk': '637a71', 'primary_exit_code': 0}},
          'agent_target_executions': 0, 'agent_helper_executions': 0, 'agent_project_imports': 0,
          'agent_codec_executions': 0, 'agent_tests_run': 0, 'agent_wine_executions': 0, 'agent_git_executions': 0,
          'tracked_edits': 0, 'section_completion_increment': 0, 'native_windows_verified': False,
          'running_UI_output_files_read': False, 'future_actual_resume': None, 'future_actual_adapter_outcomes': None,
          'qualification': 'Only independent stdlib file/AST/SHA/JSON metadata reconstruction and source reading. Root executed original actual HEAD/index/source/archive validator inside SOURCE sealer; reviewer did not call it or Git. Original strict validator remains exact and will run during root resume/finish.',
          'required_root_next_actions': ['Run exact actual FINAL resume and capture its real new recovery_started_at/primary status.',
              'Wait for currently running Wine UI actual completion; never overlap Wine.',
              'Launch two reviewed adapters after actual recovery epoch with fresh raw/log/receipt evidence and unchanged source735.',
              'Preserve original start, four passed proofs and original failed Wine full1; finish only original strict eight/UI/saved/native/PNG gates.']}
report_path = HERE / 'formal-independent-FINAL-review-recovery095-v1.json'
with report_path.open('x', encoding='utf-8') as stream:
    json.dump(report, stream, ensure_ascii=False, indent=2); stream.write('\n')
review_mf = HERE / 'public-artifacts-manifest-independent-FINAL-recovery095-v1.json'
with review_mf.open('x', encoding='utf-8') as stream:
    json.dump({'format_version': 1, 'section': 95, 'status': 'STOPWRITE_ACTUAL_FINAL_SOURCE_REVIEW_ONLY',
               'payload_files': [ref(HERE / 'independent_final_review095.py'), ref(report_path)],
               'actual_final_manifest': mf_before, 'runtime_pass': False}, stream, ensure_ascii=False, indent=2); stream.write('\n')
hand_path = HERE / 'handoff-independent-FINAL-recovery095-v1.json'
with hand_path.open('x', encoding='utf-8') as stream:
    json.dump({'format_version': 1, 'section': 95, 'stopwrite': True, 'source_gate_passed': passed,
               'runtime_pass': False, 'report': ref(report_path), 'manifest': ref(review_mf),
               'source_checks': len(checks), 'runtime_still_pending': True, 'target_helper_executions': 0},
              stream, ensure_ascii=False, indent=2); stream.write('\n')
print(json.dumps({'source_gate_passed': passed, 'source_checks': len(checks), 'blocking_checks': report['blocking_checks'],
                  'report': ref(report_path), 'manifest': ref(review_mf), 'handoff': ref(hand_path)}))
raise SystemExit(0 if passed else 1)
