"""SOURCE-only actual spec audit using own stdlib logic; no helper imports."""
import ast
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PureWindowsPath

HERE = Path(__file__).resolve().parent
PACKET = Path('/workspace/.continuation/full095-regression-capability-resume-pending-v1')
ROOT = Path('/workspace/rougezhushou')
SPEC = Path('/workspace/.continuation/root-full095-recovery-input-spec-v1.json')
EXPECTED_SHA = '1e2479c3a0079b1cc96f746f7b74fd37ff8fc7b0746f3bc0c298ffa808a78254'
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
    checks.append({'id': f'P{len(checks)+1:02d}', 'check': label, 'passed': bool(passed), 'evidence': evidence})

def pointer(document, value):
    current = document
    for part in value.split('/')[1:]:
        part = part.replace('~1', '/').replace('~0', '~')
        current = current[int(part)] if isinstance(current, list) else current[part]
    return current

spec_ref = ref(SPEC)
spec = read_json(SPEC)
mf_ref = ref(PACKET / 'public-artifacts-manifest-recovery095.json')
mf = read_json(mf_ref['path'])
package_review_path = Path('/workspace/.continuation/full095-recovery-independent-source-review-v1/formal-independent-source-review-recovery095-v1.json')
package_review = read_json(package_review_path)
check('Root actual spec exact requested physical length/hash and actual-bound status',
      spec_ref['bytes'] == 11837 and spec_ref['sha256'] == EXPECTED_SHA
      and spec['format_version'] == 2 and spec['section'] == 95
      and spec['status'] == 'ROOT_BOUND_ACTUAL_FULL095_RECOVERY_SOURCE_INPUTS', spec_ref)
check('Root spec exact top schema has no outcome or future pass field',
      set(spec) == {'format_version', 'section', 'status', 'original',
                    'preserved_passed_executions', 'prior_failed_execution', 'replacement_output_paths', 'adapters'})
check('Frozen recovery package physical source refs match approved separate package SOURCE report',
      package_review['source_gate_passed'] is True and package_review['runtime_pass'] is False
      and package_review['recovery_spec_sha256'] is None and package_review['source_manifest_sha256'] == mf_ref['sha256']
      and all(ref(row['path']) == row for row in mf['payload_files'])
      and {path.name for path in PACKET.iterdir()} == {Path(row['path']).name for row in mf['payload_files']}
      | {'public-artifacts-manifest-recovery095.json', 'handoff-recovery095.json'})
all_spec_refs = refs_in(spec)
check('Every actual fullref in root spec verifies physical path, length and SHA without reading reserved future UI outputs',
      all(ref(row['path']) == row for row in all_spec_refs), {'fullref_occurrences': len(all_spec_refs)})
original_refs = spec['original']
check('Original refs use exact existing actual binding/runner/context/start console/raw sinks',
      set(original_refs) == {'binding', 'context', 'runner', 'start_console', 'start_exit_code'}
      and original_refs['binding']['path'] == '/workspace/.continuation/full095-regression-final-v1/actual-full095-source-binding.json'
      and original_refs['binding']['sha256'] == '8b11354e50fe7a3cd291df2a86c765b65285434c44ba8bd119ab01aa29e09245'
      and original_refs['runner']['sha256'] == 'cc28fb21c3f62d4377ae9c79af4014dff6d6d38dfcd080db18b4dbe40af96afc'
      and original_refs['context']['path'] == '/workspace/.compat/wine-validation-095-context.json'
      and original_refs['start_console']['path'] == '/workspace/.continuation/root-start-full095-context.log'
      and original_refs['start_exit_code']['path'] == '/workspace/.continuation/root-start-full095-context.exit-code')
original = read_json(original_refs['binding']['path'])
context = read_json(original_refs['context']['path'])
actual = original['actual_inputs']
outputs = actual['global_output_plan']['paths']
start_console = read_json(original_refs['start_console']['path'])
check('Original real start primary zero, immutable original source epoch/context/binding and planned sinks match',
      Path(original_refs['start_exit_code']['path']).read_bytes() in (b'0\n', b'0\r\n')
      and context['status'] == start_console['status'] == 'ACTUAL_FULL095_STARTED_NOT_PASSED'
      and context['section'] == start_console['section'] == 95
      and context['binding'] == original_refs['binding'] and context['final_context_runner'] == original_refs['runner']
      and context['source_sha256'] == actual['source_sha256']
      and context['planned_fresh_sinks'] == outputs
      and context['actual_base_HEAD'] == actual['actual_base_HEAD'] == start_console['actual_base_HEAD']
      and context['branch'] == actual['branch'] == 'codex/p2-development')
check('Original source spec and actual inputs/saved/UI contracts remain sealed and not edited by root spec',
      original['status'] == 'SEALED_REAL95_SOURCE_NOT_RUNTIME_PASS'
      and ref(original['root_spec_reference']['path']) == original['root_spec_reference']
      and all(ref(row['path']) == row for row in original['final_support_files']))
check('Reuse set contains exactly four already completed original jobs and no running UI/future saved or adapter entry',
      set(spec['preserved_passed_executions']) == {'linux_full', 'linux_selected', 'linux_pip', 'wine_pip'}
      and {'wine_full', 'wine_selected', 'wine_ui', 'saved_review'}.isdisjoint(spec['preserved_passed_executions']))
epoch = datetime.fromisoformat(context['started_at'])
stop = datetime.now(timezone.utc)
observed = {}
def check_observation(row, name, code):
    value = read_json(row['path'])
    contract = actual['execution_contracts'][name]
    expected_refs = refs_in(value)
    okay = (all(ref(item['path']) == item for item in expected_refs)
            and value['actual_root_observed_primary_exit'] is True
            and value['primary_exit_code_captured'] is True
            and type(value['primary_exit_code']) is int and value['primary_exit_code'] == code
            and value['fresh_execution'] is True
            and all(value[key] == contract[key] for key in ('argv', 'cwd', 'runner', 'entry_kind', 'script_arg_index'))
            and value['stdout_log']['path'] == outputs[contract['stdout_key']]
            and value['exit_code_file']['path'] == contract['exit_code_path']
            and Path(value['exit_code_file']['path']).read_bytes() in (str(code).encode() + b'\n', str(code).encode() + b'\r\n')
            and epoch <= datetime.fromisoformat(value['started_at']) <= datetime.fromisoformat(value['completed_at']) <= stop
            and type(value['actual_tool_observation']['session_id']) is int
            and value['actual_tool_observation']['session_id'] > 0
            and bool(value['actual_tool_observation']['completion_tool_chunk']))
    check(name + ' original outcome verifies exact contract/root observation/time/raw/stdout refs', okay, row)
    return value

for name, row in spec['preserved_passed_executions'].items():
    check(name + ' exact observation/receipt-null schema', set(row) == {'observation', 'receipt'}
          and (row['receipt'] is not None if name == 'linux_full' else row['receipt'] is None))
    observed[name] = check_observation(row['observation'], name, 0)
    log = Path(observed[name]['stdout_log']['path']).read_text(encoding='utf-8', errors='replace')
    if name == 'linux_full':
        receipt = read_json(row['receipt']['path'])
        check('Actual Linux full receipt remains pass with no errors/source drift and exact original full selectors/classifier map',
              row['receipt']['path'] == outputs[name] and receipt['available_checks_passed'] is True
              and receipt['failures'] == receipt['errors'] == 0 and receipt['source_drift'] == []
              and receipt['source_sha256'] == actual['classifier_source_sha256']
              and receipt['selectors'] == actual['full_selectors'],
              {key: receipt[key] for key in ('tests_run', 'tests_passed', 'historical_or_declared_skips', 'unavailable_records')})
    elif name.endswith('_pip'):
        check(name + ' actual physical zero stdout shows no broken requirements', 'No broken requirements found.' in log)
    else:
        summaries = []
        for line in log.splitlines():
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict) and 'tests_run' in value:
                summaries.append(value)
        check('Actual Linux selected receipt is exact original current-epoch stdout and passed with one declared skip',
              bool(summaries) and summaries[-1]['passed'] is True
              and summaries[-1]['failures'] == summaries[-1]['errors'] == 0
              and summaries[-1]['tests_run'] == 1107 and summaries[-1]['skipped'] == 1,
              summaries[-1] if summaries else None)
failed = spec['prior_failed_execution']
check('Prior failure row exact schema names only Wine full and retains original receipt/log',
      set(failed) == {'execution_name', 'observation', 'receipt', 'runner_log'} and failed['execution_name'] == 'wine_full'
      and failed['receipt']['path'] == outputs['wine_full'] and failed['runner_log']['path'] == outputs['wine_full_log'])
failed_observation = check_observation(failed['observation'], 'wine_full', 1)
failed_receipt = read_json(failed['receipt']['path'])
check('Prior original failed full is not admitted as pass and preserves exact root tool completion, original counts and two failures',
      failed_observation['actual_tool_observation'] == {'session_id': 37864, 'completion_tool_chunk': '6e35c0'}
      and failed_receipt['available_checks_passed'] is False and failed_receipt['complete_repository_validation'] is False
      and failed_receipt['failures'] == failed_receipt['errors'] == 1
      and failed_receipt['tests_run'] == 1991 and failed_receipt['tests_passed'] == 1839
      and failed_receipt['historical_or_declared_skips'] == 84 and failed_receipt['unavailable_records'] == 123
      and failed_receipt['source_sha256'] == actual['classifier_source_sha256']
      and failed_receipt['selectors'] == actual['full_selectors'] and failed_receipt['source_drift'] == [])
template = read_json(PACKET / 'root-recovery-input-template095.json')
check('Root replacement paths exactly equal approved fixed five-path template and are all unused',
      spec['replacement_output_paths'] == template['replacement_output_paths']
      and all(not Path(path).exists() for path in spec['replacement_output_paths'].values())
      and not Path(outputs['context_final']).exists()
      and not Path(outputs['wine_selected']).exists()
      and not Path(actual['execution_contracts']['wine_selected']['exit_code_path']).exists())
adapters = spec['adapters']
contract = read_json(adapters['source_contract']['path'])
adapter_mf = read_json(adapters['manifest']['path'])
declared = [{key: row[key] for key in ('path', 'bytes', 'sha256')} for row in adapter_mf['payload_files']]
check('Root adapter schema and frozen manifest include exact SOURCE contract/shared source/current two runners',
      set(adapters) == {'manifest', 'source_contract', 'source_evidence', 'executions'}
      and set(adapters['executions']) == {'wine_full', 'wine_selected'}
      and adapters['source_contract'] in declared and contract['shared_admission'] in declared
      and all(ref(row['path']) == row for row in declared)
      and contract['allowlisted_test_ids'] == [row['test'] for row in failed_receipt['failed_cases']])
check('Actual root includes all precise pinned diagnosis/binary/source/failure/probe evidence without omissions or guesses',
      adapters['source_evidence'] == list(contract['runtime_evidence_references'].values()))
projected_contracts = deepcopy(actual['execution_contracts'])
for name, row in adapters['executions'].items():
    review = read_json(row['source_review']['path'])
    p = row['review_pointers']
    expected_argv = ['/workspace/.compat/run-wine-python.sh',
                     str(PureWindowsPath('Z:/' + row['runner']['path'].lstrip('/'))), '--wine']
    if name == 'wine_full':
        expected_argv += ['--output', str(PureWindowsPath('Z:/' + spec['replacement_output_paths']['wine_full'].lstrip('/')))]
    check(name + ' ROOT runner/argv/review pointers satisfy exact adapter formal SOURCE approval and own manifest',
          set(row) == {'runner', 'argv', 'source_review', 'review_pointers'}
          and row['runner'] == contract['runners'][name] and row['runner'] in declared
          and row['argv'] == contract['execution_argv'][name] == expected_argv
          and set(p) == {'source_pass', 'runtime_pass', 'runner_sha256', 'argv'}
          and pointer(review, p['source_pass']) is True and pointer(review, p['runtime_pass']) is False
          and pointer(review, p['runner_sha256']) == row['runner']['sha256']
          and pointer(review, p['argv']) == expected_argv
          and review['manifest_sha256'] == adapters['manifest']['sha256'],
          {'runner': row['runner'], 'review': row['source_review'], 'argv': expected_argv})
    projected_contracts[name]['runner'] = row['runner']
    projected_contracts[name]['argv'] = row['argv']
    if name == 'wine_full':
        projected_contracts[name]['exit_code_path'] = spec['replacement_output_paths']['wine_full_exit_code']
check('Own independent metadata projection changes only two runners/argv and one Wine full raw sink, leaving other six contracts exact',
      all(projected_contracts[name] == value for name, value in actual['execution_contracts'].items()
          if name not in ('wine_full', 'wine_selected'))
      and {name for name in projected_contracts if projected_contracts[name] != actual['execution_contracts'][name]}
      == {'wine_full', 'wine_selected'})
projected_outputs = deepcopy(outputs)
projected_outputs.update(spec['replacement_output_paths'])
changed_outputs = {key for key, value in outputs.items() if projected_outputs[key] != value}
check('Own independent planned output projection changes exactly five paths and retains UI/native/PNG/saved/selected/pip sinks',
      changed_outputs == set(spec['replacement_output_paths']) and len(projected_outputs) == len(outputs) == 33
      and len(set(projected_outputs.values())) == 33,
      {'changed_output_names': sorted(changed_outputs), 'projected_paths': projected_outputs})
immutable_paths = {row['path'] for row in all_spec_refs}
for entry in (*observed.values(), failed_observation):
    immutable_paths.update(row['path'] for row in refs_in(entry))
preserved_output_paths = {path for entry in observed.values() for path in (entry['stdout_log']['path'], entry['exit_code_file']['path'])}
preserved_output_paths.add(spec['preserved_passed_executions']['linux_full']['receipt']['path'])
check('Source-bound immutable evidence overlaps projected outputs only at the exact reused original-epoch success sinks',
      immutable_paths & set(projected_outputs.values()) == preserved_output_paths
      and not (set(spec['replacement_output_paths'].values()) & immutable_paths))
running_future = {outputs['wine_ui'], outputs['saved_review_receipt'], outputs['execution_witness'], outputs['ui_extra_acceptance'], outputs['context_final']}
check('No actual UI/PNG/native/saved/witness/final future file is read or bound by root recovery spec',
      not (immutable_paths & running_future)
      and all(not Path(path).is_relative_to(Path(directory)) for path in immutable_paths
              for directory in actual['global_output_plan']['fresh_evidence_directories']))
source_map = {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
              for folder in ('rouge', 'tests', 'scripts') for path in sorted((ROOT / folder).rglob('*'))
              if path.is_file() and path.suffix in ('.py', '.json') and '__pycache__' not in path.parts}
check('Actual maintained source735 and original classifier/source full selectors unchanged',
      len(source_map) == 735 and source_map == actual['source_sha256']
      and ref(ROOT / 'scripts/verify_full_available.py')['sha256'] == 'ea4481c9cd95fb9438f673b76c14c9386263469e12b2855fa04e9a47d7c63dcc')
check('Original archive/index/HEAD and strict eight/UI/saved checks remain in exact helper/runtime SOURCE; ROOT still must execute original validator',
      ref(PACKET / 'binding_validation095.py')['sha256'] == package_review['binding_validator_sha256']
      and (PACKET / 'binding_validation095.py').read_bytes()
      == (Path(original_refs['binding']['path']).parent / 'binding_validation095.py').read_bytes())
check('All current root spec refs and frozen package remain unchanged after independent inspection',
      ref(SPEC) == spec_ref and ref(mf_ref['path']) == mf_ref
      and all(ref(row['path']) == row for row in all_spec_refs)
      and all(ref(row['path']) == row for row in mf['payload_files']))
passed = all(row['passed'] for row in checks)
report = {'format_version': 1, 'section': 95, 'checked_at': datetime.now(timezone.utc).isoformat(),
          'status': 'PASS_INDEPENDENT_ACTUAL_ROOT_RECOVERY_SPEC_SOURCE_REVIEW' if passed else 'BLOCK_INDEPENDENT_ACTUAL_ROOT_RECOVERY_SPEC_SOURCE_REVIEW',
          'source_gate_passed': passed, 'runtime_pass': False,
          'recovery_spec_sha256': spec_ref['sha256'], 'source_manifest_sha256': mf_ref['sha256'],
          'pending_context_sha256': ref(PACKET / 'full095_context_recovery_pending.py')['sha256'],
          'recovery_helper_sha256': ref(PACKET / 'recovery_binding095.py')['sha256'],
          'sealer_sha256': ref(PACKET / 'seal_recovery095.py')['sha256'],
          'binding_validator_sha256': ref(PACKET / 'binding_validation095.py')['sha256'],
          'actual_spec': spec_ref, 'source_manifest': mf_ref, 'package_source_review': ref(package_review_path),
          'projected_execution_contracts': projected_contracts, 'projected_output_paths': projected_outputs,
          'original_context': original_refs['context'], 'original_started_at': context['started_at'],
          'preserved_actual_primary_observations': spec['preserved_passed_executions'],
          'prior_failed_execution': failed, 'source_checks': len(checks), 'checks': checks,
          'blocking_checks': [row for row in checks if not row['passed']],
          'reviewer_reads_running_or_future_UI_outputs': False,
          'agent_target_executions': 0, 'agent_helper_executions': 0, 'agent_project_imports': 0,
          'agent_codec_executions': 0, 'agent_tests_run': 0, 'agent_wine_executions': 0, 'agent_git_executions': 0,
          'tracked_source_edits': 0, 'section_completion_increment': 0, 'native_windows_verified': False,
          'future_actual_final_source_review': None, 'future_actual_resume': None, 'future_actual_adapter_outcomes': None,
          'trust_qualification': 'Root observation files bind actual trusted root process completion/session metadata and physical raw/log evidence. Reviewer verified saved SOURCE/data consistency; reviewer did not run these jobs or call Git/original binding validator.',
          'next_required_root_actions': ['Seal only this exact spec/review SHA with preserved SOURCE package.',
              'Obtain independent actual FINAL source/inverse/projection review before real resume.',
              'Keep original started_at and all successes/failure intact; start two adapters only after real recovery_started_at.',
              'Finish original eight actual zero contracts and all actual UI/saved/native/PNG proof gates before archive/commit/push.']}
report_path = HERE / 'formal-independent-actual-spec-review-recovery095-v1.json'
with report_path.open('x', encoding='utf-8') as stream:
    json.dump(report, stream, ensure_ascii=False, indent=2); stream.write('\n')
review_mf = HERE / 'public-artifacts-manifest-independent-actual-spec-recovery095-v1.json'
with review_mf.open('x', encoding='utf-8') as stream:
    json.dump({'format_version': 1, 'section': 95, 'status': 'STOPWRITE_ACTUAL_SPEC_SOURCE_REVIEW_ONLY',
               'payload_files': [ref(HERE / 'independent_actual_spec_review095.py'), ref(report_path)],
               'actual_spec': spec_ref, 'runtime_pass': False}, stream, ensure_ascii=False, indent=2); stream.write('\n')
hand_path = HERE / 'handoff-independent-actual-spec-recovery095-v1.json'
with hand_path.open('x', encoding='utf-8') as stream:
    json.dump({'format_version': 1, 'section': 95, 'stopwrite': True, 'source_gate_passed': passed,
               'runtime_pass': False, 'recovery_spec_sha256': spec_ref['sha256'], 'report': ref(report_path),
               'manifest': ref(review_mf), 'source_checks': len(checks), 'actual_FINAL_review_still_required': True,
               'target_helper_executions': 0}, stream, ensure_ascii=False, indent=2); stream.write('\n')
print(json.dumps({'source_gate_passed': passed, 'source_checks': len(checks), 'blocking_checks': report['blocking_checks'],
                  'report': ref(report_path), 'manifest': ref(review_mf), 'handoff': ref(hand_path)}))
raise SystemExit(0 if passed else 1)
