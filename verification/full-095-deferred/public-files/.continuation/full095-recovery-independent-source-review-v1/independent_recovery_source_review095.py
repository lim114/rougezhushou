"""Independent frozen recovery SOURCE audit; no reviewed code is imported."""
import ast
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKET = Path('/workspace/.continuation/full095-regression-capability-resume-pending-v1')
ORIGINAL = Path('/workspace/.continuation/full095-regression-final-v1')
ROOT = Path('/workspace/rougezhushou')
checks = []

def ref(path):
    path = Path(path)
    data = path.read_bytes()
    return {'path': str(path), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}

def read_json(path):
    return json.loads(Path(path).read_bytes())

def source(path):
    return Path(path).read_text(encoding='utf-8')

def check(label, passed, evidence=None):
    checks.append({'id': f'R{len(checks)+1:02d}', 'check': label,
                   'passed': bool(passed), 'evidence': evidence})

def func(text, name):
    node = next(node for node in ast.parse(text).body if isinstance(node, ast.FunctionDef) and node.name == name)
    return ast.get_source_segment(text, node)

def literals(text):
    result = {}
    for node in ast.parse(text).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            try:
                result[node.targets[0].id] = ast.literal_eval(node.value)
            except (ValueError, TypeError):
                pass
    return result

def contains(text, items):
    return all(item in text for item in items)

mf_path = PACKET / 'public-artifacts-manifest-recovery095.json'
mf_before = ref(mf_path)
mf = read_json(mf_path)
rows = mf['payload_files']
hand = read_json(PACKET / 'handoff-recovery095.json')
check('STOPWRITE recovery source packet and actual manifest reference, no runtime or actual spec claims',
      hand['status'].startswith('STOPWRITE_SOURCE_ONLY') and hand['manifest'] == mf_before
      and hand['runtime_pass'] is False and mf['runtime_pass'] is False
      and hand['actual_root_recovery_spec'] is None and hand['actual_independent_source_review'] is None
      and hand['actual_context_resume'] is None and hand['actual_two_adapter_executions'] is None)
physical = {str(path.relative_to(PACKET)) for path in PACKET.rglob('*') if path.is_file()}
expected = {Path(row['path']).name for row in rows} | {mf_path.name, 'handoff-recovery095.json'}
check('Exact 11 regular physical files and nine direct SOURCE payload members',
      physical == expected and len(physical) == 11 and len(rows) == 9
      and all(Path(row['path']).parent == PACKET and ref(row['path']) == row for row in rows)
      and all(not path.is_symlink() and path.is_file() for path in PACKET.iterdir()))
original = source(ORIGINAL / 'full095_context_final.py')
pending = source(PACKET / 'full095_context_recovery_pending.py')
helper = source(PACKET / 'recovery_binding095.py')
sealer = source(PACKET / 'seal_recovery095.py')
validator = source(PACKET / 'binding_validation095.py')
for name, data in (('pending context', pending), ('recovery binding helper', helper), ('sealer', sealer), ('original validator', validator)):
    ast.parse(data)
    check(name + ' parses as source without importing it', True)
check('Original binding validator and historical classifications preserved as whole exact physical bytes',
      (PACKET / 'binding_validation095.py').read_bytes() == (ORIGINAL / 'binding_validation095.py').read_bytes()
      and (PACKET / 'historical-classifications090.json').read_bytes() == (ORIGINAL / 'historical-classifications090.json').read_bytes(),
      {'validator': ref(PACKET / 'binding_validation095.py'), 'historical': ref(PACKET / 'historical-classifications090.json')})
inverse = read_json(PACKET / 'recovery-context-inverse095.json')
recovered = pending
unique = True
for row in reversed(inverse['changes']):
    unique = unique and recovered.count(row['after']) == 1
    recovered = recovered.replace(row['after'], row['before'], 1)
check('Exactly 15 uniquely bounded SOURCE deltas reverse to complete original context bytes',
      len(inverse['changes']) == 15 and unique and recovered.encode() == original.encode()
      and inverse['original_context_reference'] == ref(ORIGINAL / 'full095_context_final.py')
      and inverse['pending_context_sha256'] == ref(PACKET / 'full095_context_recovery_pending.py')['sha256'],
      {'original': inverse['original_context_reference'], 'inverse': ref(PACKET / 'recovery-context-inverse095.json')})
original_names = [node.name for node in ast.parse(original).body if isinstance(node, ast.FunctionDef)]
same = [name for name in original_names if func(original, name) == func(pending, name)]
changed = [name for name in original_names if name not in same]
pending_names = [node.name for node in ast.parse(pending).body if isinstance(node, ast.FunctionDef)]
check('Fourteen original functions retain twelve complete byte-exact bodies and two bounded binding/witness changes',
      len(original_names) == 14 and len(same) == 12
      and changed == ['load_actual_binding', 'require_primary_executions']
      and set(pending_names) - set(original_names) == {'wine_full_receipt'},
      {'unchanged': same, 'changed': changed, 'new_function': 'wine_full_receipt'})
check('All original Linux/selected/strict raw-zero/UI/saved/native/PNG acceptance functions remain whole exact',
      {'full_receipt', 'selected_receipt', 'actual_exit_code', 'actual_ui_receipt',
       'proof_file_binding', 'saved_review_execution', 'actual_ui_extra_acceptance'} <= set(same))
values = literals(helper)
expected_paths = {
    'context_start': '/workspace/.compat/wine-validation-095-context-recovery-v1.json',
    'wine_full': '/workspace/.compat/wine-full095-capability-retry-v1/wine-available-full095.json',
    'wine_full_log': '/workspace/.compat/wine-full095-capability-retry-v1/wine-available-full095.log',
    'wine_full_console': '/workspace/.compat/wine-full095-capability-retry-v1/wine-available-full095-console.log',
    'wine_full_exit_code': '/workspace/.continuation/root-full095-wine_full-capability-retry-v1.exit-code',
}
check('Projection allowlist contains exactly two Wine contracts and fixed five new context/full sinks',
      values['REPLACED_EXECUTIONS'] == ('wine_full', 'wine_selected') and values['REPLACED_OUTPUTS'] == expected_paths
      and all(not Path(path).exists() for path in expected_paths.values()))
actual_original = read_json(ORIGINAL / 'actual-full095-source-binding.json')
check('Original runner and real sealed original binding refs are exact current physical bytes',
      values['ORIGINAL_BINDING'] == ref(ORIGINAL / 'actual-full095-source-binding.json')
      and values['ORIGINAL_CONTEXT_RUNNER'] == ref(ORIGINAL / 'full095_context_final.py'))
template = read_json(PACKET / 'root-recovery-input-template095.json')
check('Pending root recovery template has no fabricated outcome/input reference or future source approval',
      template['status'] == 'SOURCE_ONLY_PENDING_ACTUAL_ROOT_RECOVERY_BINDING'
      and all(value is None for value in template['original'].values())
      and set(template['preserved_passed_executions']) == {'linux_full', 'linux_pip'}
      and all(value is None for row in template['preserved_passed_executions'].values() for value in row.values())
      and all(value is None for key, value in template['prior_failed_execution'].items() if key != 'execution_name')
      and template['adapters']['manifest'] is None and template['adapters']['source_contract'] is None
      and template['adapters']['source_evidence'] == []
      and all(value is None for row in template['adapters']['executions'].values() for value in row.values()))
validate = func(helper, 'validate_recovery_inputs')
check('Recovery validates exact original root_spec and complete actual_inputs with original validator before any projection',
      contains(validate, ["actual = validate_actual_inputs(original['root_spec'], immutable)",
                         "actual == original['actual_inputs']", "spec['original']['binding'] == ORIGINAL_BINDING",
                         "spec['original']['runner'] == ORIGINAL_CONTEXT_RUNNER"])
      and validate.index("actual = validate_actual_inputs(original['root_spec'], immutable)")
      < validate.index("contracts = deepcopy(actual['execution_contracts'])"))
check('Original validator retains actual branch/HEAD/source735/physical archive/index blob gates',
      contains(validator, ["git_output(root, 'branch', '--show-current')", "git_output(root, 'rev-parse', 'HEAD')",
                           "current == guard95['source_sha256_after']", "[93, 94, 95]",
                           'physical == expected_physical', "git_output(root, 'ls-files', '--stage', '-z'",
                           "staged[name] == expected_blob", "CLASSIFIER_SHA256"]))
check('Original immutable context, original primary-zero start log/status and original source map must match',
      contains(validate, ["spec['original']['start_exit_code']", "(b'0\\n', b'0\\r\\n')",
                         "'/workspace/.continuation/root-start-full095-context.exit-code'",
                         "context['binding'] == spec['original']['binding']",
                         "context['source_sha256'] == actual['source_sha256']",
                         "context['planned_fresh_sinks'] == actual['global_output_plan']['paths']",
                         "actual['global_output_plan']['canonical_paths']['context_start']"]))
observation = func(helper, 'check_observation')
check('Reusable observation checks exact original contract, stdout/raw/ref, actual tool witness and original-epoch timestamps',
      contains(observation, ["type(entry['primary_exit_code']) is int", "entry['primary_exit_code'] == expected_code",
                            "('argv', 'cwd', 'runner', 'entry_kind', 'script_arg_index')",
                            "outputs[contract['stdout_key']]", "contract['exit_code_path']",
                            "context['started_at']", 'began <= ended', "entry['actual_tool_observation']",
                            "type(tool['session_id']) is int", "tool['completion_tool_chunk']"]))
passes = func(helper, 'check_preserved_passes')
check('Only actually completed unchanged original-epoch jobs can be preserved; Linux full/pip mandatory and no Wine adapter reuse',
      contains(passes, ["{'linux_full', 'linux_pip'} <= set(passed)",
                       'set(passed) <= set(EXECUTION_NAMES) - set(REPLACED_EXECUTIONS)',
                       "check_observation(row['observation'], name, original, context, 0)",
                       "receipt['available_checks_passed'] is True", "'No broken requirements found.' in log",
                       "receipt['source_sha256'] == original['actual_inputs']['classifier_source_sha256']",
                       "receipt['selectors'] == original['actual_inputs']['full_selectors']"]))
failure = func(helper, 'check_prior_failure')
check('Prior failure remains exact primary one, session/chunk, original failed full receipt/log and both original IDs',
      contains(failure, ["check_observation(failed['observation'], 'wine_full', original, context, 1)",
                        "{'session_id': 37864, 'completion_tool_chunk': '6e35c0'}",
                        "receipt['available_checks_passed'] is False", "receipt['failures'] == 1 and receipt['errors'] == 1",
                        "receipt['source_sha256'] == original['actual_inputs']['classifier_source_sha256']",
                        "== FAILED_TEST_NAMES", "len(receipt['failed_cases']) == 2"]))
check('Exact adapter manifest/contract/shared source/runner/CLI/SOURCE review gates precede two narrow assignments',
      contains(validate, ["contract['shared_admission'] in declared", "runner == contract['runners'][name] and runner in declared",
                         "row['argv'] == contract['execution_argv'][name]", "exact_source_review(row['source_review']",
                         "contracts[name]['runner'] = runner", "contracts[name]['argv'] = expected",
                         "if name == 'wine_full':", "contracts[name]['exit_code_path'] = REPLACED_OUTPUTS['wine_full_exit_code']"]))
projection = func(helper, 'projected_outputs')
check('Projection keeps all original outputs except five fixed paths and maintains unique disjoint file/native namespaces',
      contains(projection, ['plan = deepcopy(original_plan)', "plan['paths'].update(REPLACED_OUTPUTS)",
                           'len(set(canonical.values())) == len(canonical)',
                           'set(inputs).intersection(canonical.values()) == preserved',
                           "directories == original_plan['fresh_evidence_directories']",
                           'Recovery immutable input overlaps the unchanged UI native namespace',
                           'Recovery nonnative output may not be placed inside native namespace']))
cap = func(helper, 'validate_capability_receipt')
check('Saved capability validation reads source literal via AST only, never executes probe or adapter',
      contains(cap, ['require(name in REPLACED_EXECUTIONS', "bound_json(adapters['source_contract'])",
                     "bound_bytes(contract['shared_admission'])", 'ast.parse(shared)', 'ast.literal_eval(skip_assignments[0].value)'])
      and not any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                  and node.func.id in ('exec', 'eval', '__import__', 'compile') for node in ast.walk(ast.parse(helper))))
check('Saved capability receipt requires two honest unrun exact-ID records, zero passed credit and incomplete validation',
      contains(cap, ["'kind': 'environment_capability'", "'classification': 'declared_skip'",
                     "'actually_executed': False", "'fixture_body_run': False", "'product_assertions_passed': False",
                     "type(value['environment_capability_skips']) is int", "value['environment_capability_skips'] == 2",
                     "type(value['capability_skips_counted_passed']) is int", "value['capability_skips_counted_passed'] == 0",
                     "value['complete_repository_validation'] is False", "value['capability_records'] == expected_records"]))
check('Saved actual capability identity, installed module SHA/bytes, exact source evidence and original failure must match',
      contains(cap, ["probe['runtime_evidence_references'] == evidence", "probe['old_failed_full_primary_exit'] == 1",
                     "identity['wine_specific_export'] == 'ntdll.wine_get_version'", "identity['actual_version'].isascii()",
                     "active['sha256'] == expected['sha256'] and active['bytes'] == expected['bytes']",
                     "probe['project_calls_during_capability_probe'] == 0"]))
check('Saved actual fresh probe requires two default-Temp same-folder/volume phantom patterns with explicit lstat/readlink/open errors',
      contains(cap, ["len(observations) == 2", 'target.parent == link.parent', 'target.parent.parent == default_temp',
                     "row['target_present'] is present", "row['is_symlink'] is False and row['exists'] is False",
                     "row['target_bytes_unchanged'] is True", "row[operation]['winerror'] == 2",
                     "row['read_bytes']['winerror'] is None"]))
check('Saved capability adapter four-source before/after map, no drift and actual Python argv must match exact projected contract',
      contains(cap, ['before == after and set(before) == set(expected_sources)', "value['adapter_source_drift'] == []",
                     "'wine_symlink_capability095.py': contract['shared_admission']",
                     "'source-contract-wine-capability095.json': adapters['source_contract']",
                     "wine_argument_for(expected['path'], mapping)",
                     "value['actual_python_argv'] == binding['actual_inputs']['execution_contracts'][name]['argv'][1:]"]))
wine_func = func(pending, 'wine_full_receipt')
wine_original = wine_func.replace('def wine_full_receipt(', 'def full_receipt(', 1)
wine_original = wine_original.replace("    require(name == 'wine_full', 'Only the SOURCE-reviewed Wine full may use capability qualification')\n", '', 1)
wine_original = wine_original.replace("Path(binding['actual_inputs']['global_output_plan']['paths'][name])", 'Path(OUTPUT_NAMES[name])', 1)
wine_original = wine_original.replace("    validate_capability_receipt(value, binding, name)\n    require(value['complete_repository_validation'] is False,\n            'Actual admitted two Wine fixture skips prevent complete repository validation even without other unavailable rows')",
                                     "    require(value['complete_repository_validation'] is (not value['unavailable']),\n            f'{name} absent evidence cannot be called complete validation')", 1)
check('New Wine-only full receipt copy retains complete original classifier/counts/selectors/old skip validations',
      wine_original == func(original, 'full_receipt')
      and "wine_ref, wine = wine_full_receipt('wine_full', binding, historical)" in pending
      and "validate_capability_receipt(wine_selected, binding, 'wine_selected')" in pending)
witness = func(pending, 'require_primary_executions')
check('All eight original exact argv/cwd/runner/script/stdout/raw-zero witness gates remain and add strict preserved-row identity',
      contains(witness, ['set(executions) == set(EXECUTION_NAMES) == set(contracts)',
                         "entry['argv'] == contract['argv']", "entry['cwd'] == contract['cwd']",
                         "entry['entry_kind'] == contract['entry_kind']", "entry['script_arg_index'] == contract['script_arg_index']",
                         "entry['runner'] == contract['runner']", "actual_exit_code(entry['exit_code_file']",
                         "entry == bound_json(preserved[name]['observation'])", 'len(set(exit_files)) == len(EXECUTION_NAMES)']))
check('Two new adapter observations must start after actual new recovery epoch; unchanged original successes never replayed',
      contains(witness, ["if name in ('wine_full', 'wine_selected'):", "began >= datetime.fromisoformat(context['recovery_started_at'])"])
      and "require(sys.argv[1] in ('resume', 'finish')" in pending
      and 'original_successful_executions_replayed_by_context=0' in pending)
check('Actual resume inherits immutable original started_at and separately captures truthful new recovery_started_at',
      contains(pending, ['ctx = deepcopy(original_context)', 'recovery_started_at=now()',
                        'original_started_at_preserved_without_new_start=True',
                        "ctx['started_at'] == original_context['started_at']",
                        "ctx['preserved_passed_executions'] == recovery_spec['preserved_passed_executions']",
                        "ctx['prior_failed_execution'] == recovery_spec['prior_failed_execution']",
                        "with path.open('x', encoding='utf-8')"]))
check('Actual resume/finish preserve source735 and strict UI, saved, PNG/native set, pip and same-receipt checks',
      contains(pending, ["require(hashes() == actual['source_sha256']", "require(not drift, 'Maintained source drifted",
                        "'No broken requirements found.'", 'actual_ui_extra_acceptance(Path(sys.argv[5]), binding, ui_ref, witness)',
                        "complete_repository_validation=linux['complete_repository_validation'] and wine['complete_repository_validation']"]))
seal_main = func(sealer, 'main')
check('Sealer requires actual root spec SHA and independent approval binding all seven explicit SOURCE fields',
      contains(seal_main, ['digest(spec_data) == args.spec_sha256', "review.get('source_gate_passed') is True",
                          "review.get('runtime_pass') is False", "review['recovery_spec_sha256'] == args.spec_sha256",
                          "review['source_manifest_sha256'] == digest(manifest_path.read_bytes())",
                          "review['pending_context_sha256'] == digest(pending)", "review['recovery_helper_sha256']",
                          "review['sealer_sha256'] == digest(Path(__file__).read_bytes())"]))
check('All final source/input/namespace/freshness/inverse checks occur before exclusive new output write',
      seal_main.index('validate_recovery_inputs(spec, immutable_paths)') < seal_main.index('output.mkdir()')
      and seal_main.index('ast.parse(final)') < seal_main.index('output.mkdir()')
      and contains(seal_main, ['not output.exists()', 'for path in REPLACED_OUTPUTS.values()',
                              "(output / name).open('xb')", 'reverse == pending']))
tree = ast.parse(sealer)
replacement_node = next(node for node in ast.walk(tree) if isinstance(node, ast.Assign)
                        and any(isinstance(target, ast.Name) and target.id == 'replacements' for target in node.targets))
check('Pending to FINAL seal can replace only PENDING and actual recovery binding SHA literals',
      isinstance(replacement_node.value, ast.List) and len(replacement_node.value.elts) == 2
      and "(b'PENDING = True\\n', b'PENDING = False\\n')" in sealer
      and "BOUND_BINDING_SHA256 = '__ACTUAL_RECOVERY_BINDING_SHA256_PENDING__'" in sealer)
imports = [node.module for node in ast.walk(ast.parse(helper)) if isinstance(node, ast.ImportFrom)]
imports += [alias.name for node in ast.walk(ast.parse(helper)) if isinstance(node, ast.Import) for alias in node.names]
check('Recovery metadata helper imports only stdlib and original binding validator, without target/project/Wine subprocess paths',
      set(imports) <= {'copy', 'datetime', 'pathlib', 'ast', 'json', 'binding_validation095'}
      and not any(word in helper for word in ('subprocess.', 'os.system(', 'import rouge', 'import unittest', 'ctypes.')))
doc = source(PACKET / 'RECOVERY_CONTRACT095.md')
check('SOURCE scope explains current epoch proof reuse separately from historical selected reuse; Wine/native gaps stay explicit',
      'selected_reuse_performed' in doc and 'preserved_passed_executions' in doc
      and 'reused_passed_current_epoch_executions' in doc and '原生 Windows' in doc
      and '12' in doc and '15' in doc)
guard_ref = actual_original['root_spec']['completed_working_tree_chain'][-1]['source_guard']
guard = read_json(guard_ref['path'])
actual_map = {path.relative_to(ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
              for folder in ('rouge', 'tests', 'scripts') for path in sorted((ROOT / folder).rglob('*'))
              if path.is_file() and path.suffix in ('.py', '.json') and '__pycache__' not in path.parts}
check('Actual current 735-file maintained source equals original sealed map and section95 guard',
      len(actual_map) == 735 and actual_map == guard['source_sha256_after'] == actual_original['actual_inputs']['source_sha256'])
archive_rows = []
for row in actual_original['root_spec']['completed_working_tree_chain']:
    receipt = read_json(row['receipt']['path'])
    closure = read_json(row['closure']['path'])
    archive = ROOT / receipt['research_archive']
    archive_mf = read_json(archive / 'archive-manifest.json')
    archive_physical = {path.relative_to(archive).as_posix() for path in archive.rglob('*') if path.is_file()}
    okay = archive_physical == set(archive_mf) | {'archive-manifest.json'}
    okay = okay and ref(archive / 'archive-manifest.json')['sha256'] == closure['archive_manifest_sha256']
    okay = okay and all(ref(archive / name)['bytes'] == value['bytes'] and ref(archive / name)['sha256'] == value['sha256']
                        for name, value in archive_mf.items())
    archive_rows.append({'section': row['section'], 'archive_manifest': ref(archive / 'archive-manifest.json'),
                         'physical_files': len(archive_physical), 'passed': okay,
                         'index_claim_source': row['closure'], 'index_checked_by_this_reviewer': False})
check('Actual section93-95 physical archives, complete manifest member sets and all payload bytes remain exact',
      [row['physical_files'] for row in archive_rows] == [159, 87, 292] and all(row['passed'] for row in archive_rows), archive_rows)
check('Frozen recovery MF and every payload unchanged after independent SOURCE inspection',
      mf_before == ref(mf_path) and all(ref(row['path']) == row for row in rows))
passed = all(row['passed'] for row in checks)
adapter_report = Path('/workspace/.continuation/full095-wine-capability-independent-source-review-v1/formal-independent-source-review-wine-capability095-v1.json')
adapter = read_json(adapter_report)
report = {'format_version': 1, 'section': 95, 'checked_at': datetime.now(timezone.utc).isoformat(),
          'status': 'PASS_INDEPENDENT_RECOVERY_SOURCE_PACKET_ACTUAL_SPEC_PENDING' if passed else 'BLOCK_INDEPENDENT_RECOVERY_SOURCE_PACKET',
          'source_gate_passed': passed, 'runtime_pass': False, 'recovery_spec_sha256': None,
          'source_manifest_sha256': mf_before['sha256'], 'pending_context_sha256': ref(PACKET / 'full095_context_recovery_pending.py')['sha256'],
          'recovery_helper_sha256': ref(PACKET / 'recovery_binding095.py')['sha256'],
          'sealer_sha256': ref(PACKET / 'seal_recovery095.py')['sha256'],
          'binding_validator_sha256': ref(PACKET / 'binding_validation095.py')['sha256'],
          'original_context_sha256': ref(ORIGINAL / 'full095_context_final.py')['sha256'],
          'source_manifest': mf_before, 'pending_context': ref(PACKET / 'full095_context_recovery_pending.py'),
          'recovery_helper': ref(PACKET / 'recovery_binding095.py'), 'sealer': ref(PACKET / 'seal_recovery095.py'),
          'whole_source_inverse': ref(PACKET / 'recovery-context-inverse095.json'),
          'adapter_source_review': ref(adapter_report), 'adapter_manifest_sha256': adapter['manifest_sha256'],
          'adapter_runners': adapter['runners'], 'shared_admission': adapter['shared_admission'],
          'adapter_execution_argv': adapter['execution_argv'],
          'future_execution_argv': {'resume': ['/workspace/rougezhushou/.venv/bin/python',
              '/workspace/.continuation/full095-regression-capability-resume-final-v1/full095_context_recovery.py', 'resume'],
              'finish': ['/workspace/rougezhushou/.venv/bin/python',
              '/workspace/.continuation/full095-regression-capability-resume-final-v1/full095_context_recovery.py', 'finish',
              '--executions', '/workspace/.continuation/root-full095-primary-exits.json',
              '--ui-acceptance', '/workspace/.continuation/root-full095-ui-extra-acceptance.json']},
          'checks': checks, 'source_checks': len(checks), 'blocking_checks': [row for row in checks if not row['passed']],
          'agent_target_executions': 0, 'agent_helper_executions': 0, 'agent_project_imports': 0,
          'agent_codec_executions': 0, 'agent_tests_run': 0, 'agent_wine_executions': 0, 'agent_git_executions': 0,
          'tracked_edits': 0, 'section_completion_increment': 0, 'native_windows_verified': False,
          'index_validation_qualification': 'This reviewer ran no Git. Exact original index/HEAD validator source is preserved and must run before root seal/resume/finish. Physical archives were independently checked; original closure index claims are bound historical evidence, not a new reviewer index execution.',
          'future_actual_root_spec_review': None, 'future_actual_FINAL_review': None,
          'future_actual_resume_primary': None, 'future_actual_adapter_primaries': None,
          'required_root_next_actions': ['Assemble actual source/evidence/previous-outcome fullrefs into new ROOT recovery spec.',
              'Obtain separate independent SOURCE approval binding exact actual recovery spec SHA and the six current package hashes.',
              'Seal, independently review actual FINAL inverse/projection, resume with real new recovery timestamp.',
              'Run two new adapters after resume plus unfinished unchanged jobs; preserve successful original-epoch proofs.',
              'Finish only exact eight actual zero witnesses and all strict actual UI/saved/native/PNG gates.'],
          'precision_notes': ['Original start/failure/passed proofs are immutable and never rewritten or called new runs.',
              'SOURCE packet approval has null actual-spec SHA and cannot satisfy sealer actual-spec review gate.',
              'Two native symlink fixture assertions remain unverified and unavailable; original Linux bodies still run unchanged.',
              'Original context source function count is14:12 whole bodies exact, two bounded changes, one added Wine-only receipt function.']}
report_path = HERE / 'formal-independent-source-review-recovery095-v1.json'
with report_path.open('x', encoding='utf-8') as stream:
    json.dump(report, stream, ensure_ascii=False, indent=2); stream.write('\n')
manifest = {'format_version': 1, 'section': 95, 'status': 'STOPWRITE_INDEPENDENT_RECOVERY_SOURCE_REVIEW_ONLY',
            'payload_files': [ref(HERE / 'independent_recovery_source_review095.py'), ref(report_path)],
            'runtime_pass': False, 'source_packet_manifest': mf_before}
review_mf = HERE / 'public-artifacts-manifest-independent-recovery095-v1.json'
with review_mf.open('x', encoding='utf-8') as stream:
    json.dump(manifest, stream, ensure_ascii=False, indent=2); stream.write('\n')
hand_path = HERE / 'handoff-independent-recovery095-v1.json'
with hand_path.open('x', encoding='utf-8') as stream:
    json.dump({'format_version': 1, 'section': 95, 'stopwrite': True, 'source_gate_passed': passed,
               'runtime_pass': False, 'recovery_spec_sha256': None, 'report': ref(report_path),
               'manifest': ref(review_mf), 'source_checks': len(checks),
               'actual_spec_and_FINAL_review_still_required': True, 'target_helper_executions': 0},
              stream, ensure_ascii=False, indent=2); stream.write('\n')
print(json.dumps({'source_gate_passed': passed, 'source_checks': len(checks),
                  'blocking_checks': report['blocking_checks'], 'report': ref(report_path),
                  'manifest': ref(review_mf), 'handoff': ref(hand_path)}))
raise SystemExit(0 if passed else 1)
