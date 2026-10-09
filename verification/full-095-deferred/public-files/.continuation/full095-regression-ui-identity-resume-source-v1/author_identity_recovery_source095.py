"""SOURCE-only authoring: no project imports, codecs, tests, UI, Wine or Git."""
import ast
import hashlib
import json
from pathlib import Path
from copy import deepcopy

HERE = Path(__file__).resolve().parent
OLD_FINAL = Path('/workspace/.continuation/full095-regression-ui-cache-resume-final-v1')
OLD_PENDING = Path('/workspace/.continuation/full095-regression-ui-cache-resume-pending-v3')
FINAL = Path('/workspace/.continuation/full095-regression-ui-identity-resume-final-v1')

def digest(data):
    return hashlib.sha256(data).hexdigest()

def ref(path):
    path = Path(path)
    data = path.read_bytes()
    return {'path': str(path), 'bytes': len(data), 'sha256': digest(data)}

def write(name, data):
    if not isinstance(data, bytes):
        data = (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode()
    path = HERE / name
    with path.open('xb') as stream:
        stream.write(data)
    return ref(path)

def changed(before, replacements):
    after = before.decode()
    rows = []
    for old, new in replacements:
        count = after.count(old)
        if count < 1:
            raise ValueError('Missing exact SOURCE span: ' + old[:100])
        after = after.replace(old, new)
        rows.append({'before': old, 'after': new, 'count': count})
    reverse = after
    for row in reversed(rows):
        if reverse.count(row['after']) != row['count']:
            raise ValueError('Inverse SOURCE span count differs')
        reverse = reverse.replace(row['after'], row['before'])
    if reverse.encode() != before:
        raise ValueError('Whole SOURCE inverse differs')
    ast.parse(after)
    compile(after, '<source-only-compile>', 'exec')
    return after.encode(), rows

prior_binding = json.loads((OLD_FINAL / 'actual-full095-source-binding.json').read_bytes())
prior_spec = prior_binding['recovery_spec']
prior_context_path = Path('/workspace/.compat/wine-validation-095-context-ui-cache-retry-v1.json')
prior_context = json.loads(prior_context_path.read_bytes())
lost_path = Path('/workspace/.continuation/ROOT_CURRENT_WORK_095_UI_CACHE_SESSION_LOST_PRIMARY_UNAVAILABLE.json')
lost = json.loads(lost_path.read_bytes())
prior_refs = {'binding': ref(OLD_FINAL / 'actual-full095-source-binding.json'),
              'runner': ref(OLD_FINAL / 'full095_context_ui_retry.py'),
              'context': ref(prior_context_path),
              'resume_console': ref('/workspace/.continuation/root-resume-full095-ui-cache-retry-v1.log'),
              'resume_exit_code': ref('/workspace/.continuation/root-resume-full095-ui-cache-retry-v1.exit-code')}
if prior_refs['binding']['sha256'] != 'b83ab67ca978d1b1b9e393c6d4e2cfb6c77e3bf9600af9d7ae87fe40975dbb84':
    raise ValueError('Prior actual b83 binding differs')
if not (lost['actual_original_UI_session_id'] == 53266 and lost['primary_exit_code'] is None
        and lost['closed_native_chunks'] == 2310 and lost['closed_targeted_records'] == 136836):
    raise ValueError('Actual second incomplete attempt differs')

# Retain all four original validation support modules byte-for-byte.
for support in ('binding_validation095.py', 'capability_binding095.py',
                'historical-classifications090.json', 'recovery_binding095.py'):
    write(support, (OLD_FINAL / support).read_bytes())

old_helper = (OLD_FINAL / 'recovery_binding095.py').read_bytes()
old_text = old_helper.decode()
validator_start = old_text.index('def validate_recovery_inputs(spec, extra_immutable_paths=()):\n')
old_validator = old_text[validator_start:]
new_validator = '''def check_prior_ui_retry(spec, prior, original_context, actual):
    import json
    row = spec['prior_ui_retry']
    require(row == IDENTITY_PRIOR_UI_RETRY,
            'Preserve the exact actual second-UI binding/runner/context/resume proof')
    context = bound_json(row['context'])
    bound_bytes(row['runner'])
    require(bound_bytes(row['resume_exit_code']) in (b'0\\n', b'0\\r\\n'),
            'The previous actual UI retry resume proof must remain primary zero')
    console = json.loads(bound_bytes(row['resume_console']))
    require(console['status'] == 'ACTUAL_FULL095_STARTED_NOT_PASSED'
            and console['section'] == 95 and console['source_files'] == actual['source_files']
            and console['actual_base_HEAD'] == actual['actual_base_HEAD']
            and console['actual_original_epoch_recovery'] is True
            and console['actual_ui_retry'] is True and console['original_start_replayed'] is False,
            'Preserve the actual previous UI retry resume result')
    require(context['status'] == 'ACTUAL_FULL095_STARTED_NOT_PASSED'
            and context['available_checks_passed'] is False and context['section'] == 95
            and context['actual_original_epoch_recovery'] is True and context['actual_ui_retry'] is True
            and context['binding'] == row['binding'] and context['final_context_runner'] == row['runner']
            and context['started_at'] == original_context['started_at']
            and context['recovery_started_at'] == '2026-10-08T23:36:41.779450+00:00'
            and context['ui_retry_started_at'] == '2026-10-09T00:59:43.753835+00:00'
            and console['ui_retry_started_at'] == context['ui_retry_started_at']
            and context['source_sha256'] == actual['source_sha256']
            and context['planned_current_epoch_sinks'] == actual['global_output_plan']['paths']
            and context['planned_fresh_sinks'] == prior['recovery_spec']['ui_retry_output_paths']
            and context['preserved_passed_executions'] == prior['recovery_spec']['preserved_passed_executions']
            and context['preserved_recovery_passed_executions'] == prior['recovery_spec']['preserved_recovery_passed_executions']
            and context['prior_failed_execution'] == prior['recovery_spec']['prior_failed_execution']
            and context['prior_incomplete_ui'] == prior['recovery_spec']['prior_incomplete_ui']
            and context['prior_selected_failed_execution'] == prior['recovery_spec']['prior_selected_failed_execution']
            and context['prior_recovery'] == prior['recovery_spec']['prior_recovery']
            and context['ui_retry_source'] == prior['recovery_spec']['ui_retry'],
            'Previous UI retry changed an earlier epoch, source, pass/failure or exact contract')
    require(datetime.fromisoformat(context['started_at'])
            <= datetime.fromisoformat(context['recovery_started_at'])
            <= datetime.fromisoformat(context['ui_retry_started_at']) <= datetime.now(timezone.utc),
            'Previous actual UI retry boundary is outside the original epoch')
    require(spec['prior_incomplete_ui_cache'] == IDENTITY_INCOMPLETE_UI,
            'Preserve the exact actual second incomplete UI capsule')
    capsule = bound_json(spec['prior_incomplete_ui_cache'])
    require(capsule['section'] == 95
            and capsule['status'] == 'INCOMPLETE_UI_EXECUTION_SESSION_LOST_PRIMARY_UNAVAILABLE'
            and capsule['actual_original_UI_session_id'] == 53266
            and capsule['primary_exit_code'] is None and capsule['primary_exit_code_captured'] is False
            and capsule['actual_root_requested_process_termination'] is False
            and capsule['cause_of_external_session_loss'] == 'UNKNOWN'
            and capsule['raw_primary_status_absent'] is True and capsule['final_UI_receipt_absent'] is True
            and capsule['native_outcome'] == 'pending' and capsule['states_committed'] == 0
            and capsule['closed_native_chunks'] == 2310 and capsule['closed_targeted_records'] == 136836
            and capsule['full_validation_passed'] is False
            and capsule['source_files_unchanged'] == actual['source_files'] and capsule['source_drift'] == []
            and capsule['previous_incomplete_UI'] == prior['recovery_spec']['prior_incomplete_ui']
            and capsule['same_UI_execution_problem_incomplete_attempt_count'] == 2
            and capsule['third_attempt_failure_requires_deferral'] is True,
            'The second lost UI outcome must remain unknown/incomplete; third failure requires deferral')
    expected = {name: value['observation'] for field in
                ('preserved_passed_executions', 'preserved_recovery_passed_executions')
                for name, value in prior['recovery_spec'][field].items()}
    require(capsule['six_completed_primary_observations_preserved'] == expected,
            'Second incomplete UI capsule must preserve the same six actual primary-zero proofs')
    references = references_in(capsule)
    for reference in references:
        bound_bytes(reference)
    launch = bound_json(capsule['actual_launch'])
    contract = actual['execution_contracts']['wine_ui']
    require(launch['launch_result']['session_id'] == 53266
            and launch['started_at'] == capsule['actual_original_UI_start_from_prior_trusted_observation']
            and all(launch[key] == contract[key] for key in ('argv', 'cwd', 'runner', 'entry_kind', 'script_arg_index'))
            and not Path(contract['exit_code_path']).exists()
            and not Path(actual['global_output_plan']['paths']['wine_ui']).exists(),
            'Preserve the second UI actual launch and absent primary/final proof; never backfill')
    index = bound_json(capsule['native_index'])
    snapshot = bound_bytes(capsule['preserved_native_index_snapshot'])
    require(snapshot == bound_bytes(capsule['native_index'])
            and index['outcome'] == 'pending' and len(index['chunks']) == capsule['closed_native_chunks']
            and index['records_completed'] == capsule['closed_targeted_records'],
            'Second incomplete native index changed its pending outcome/closed counts')
    chunks = []
    for chunk in index['chunks']:
        path = Path('/workspace/.compat') / chunk['file']
        require(path.parent == Path('/workspace/.compat/full095-ui-native-cache-retry-v1'),
                'Second incomplete native chunk escaped the actual previous namespace')
        reference = {'path': str(path), 'bytes': chunk['bytes'], 'sha256': chunk['sha256']}
        bound_bytes(reference)
        chunks.append(reference)
    require(chunks == capsule['all_closed_compressed_chunk_refs_verified'],
            'Preserve every actual second-attempt closed native chunk reference and order')
    return context, references + chunks


def validate_recovery_inputs(spec, extra_immutable_paths=()):
    require(spec.get('format_version') == 3 and spec.get('section') == 95
            and spec.get('status') == 'ROOT_BOUND_ACTUAL_FULL095_UI_IDENTITY_RETRY_SOURCE_INPUTS',
            'Actual ROOT-bound identity retry spec required; pending/future references cannot seal')
    require(spec['prior_ui_retry'] == IDENTITY_PRIOR_UI_RETRY,
            'Identity retry must preserve the exact actual previous b83 binding and UI context')
    prior = bound_json(IDENTITY_PRIOR_UI_RETRY['binding'])
    base_spec = prior['recovery_spec']
    for key in ('original', 'preserved_passed_executions', 'prior_failed_execution', 'adapters',
                'prior_recovery', 'prior_incomplete_ui', 'preserved_recovery_passed_executions',
                'selected_retry_output_paths', 'prior_selected_failed_execution'):
        require(spec[key] == base_spec[key], 'Identity retry changed an immutable previous recovery field: ' + key)
    require(spec['ui_retry_output_paths'] == NEW_OUTPUTS
            and spec['replacement_output_paths'] == REPLACED_OUTPUTS,
            'Only the exact reviewed identity UI/saved/control sinks may change')
    for reference in prior['final_support_files']:
        bound_bytes(reference)
    require(bound_json(prior['recovery_spec_reference']) == base_spec,
            'Previous physical Root UI retry spec changed')
    prior_immutable = prior['source_package_input_paths'] + [prior['recovery_spec_reference']['path']]
    prior_immutable.extend((IDENTITY_PRIOR_UI_RETRY['binding']['path'], IDENTITY_PRIOR_UI_RETRY['runner']['path']))
    prior_immutable.extend(reference['path'] for reference in prior['final_support_files'])
    # Whole-byte old recovery module invokes whole-byte ad1b/b7a6 validation before new projection.
    original, original_context, actual = validate_prior_ui_inputs(base_spec, prior_immutable)
    require(original['root_spec'] == prior['root_spec'] and actual == prior['actual_inputs'],
            'Previous exact b83 root spec/actual inputs or strict original validator projection changed')
    prior_ui_context, incomplete_refs = check_prior_ui_retry(spec, prior, original_context, actual)
    ui, saved, ui_refs = ui_retry_projection(spec, prior, actual)
    projected_root = deepcopy(original)
    projected_root['root_spec']['ui'] = ui
    projected_root['root_spec']['saved_review'] = saved
    projected_root['root_spec']['io_plan']['exit_code_paths'].update(
        wine_ui=UI_OUTPUTS['wine_ui_exit_code'], saved_review=CONTROL_OUTPUTS['saved_review_exit_code'])
    projected_root['root_spec']['io_plan'].update(visual_review_path=CONTROL_OUTPUTS['visual_review'],
                                                ui_extra_acceptance_path=CONTROL_OUTPUTS['ui_extra_acceptance'])
    projected = deepcopy(actual)
    projected['UI_source_binding'] = ui
    projected['ui_retry'] = spec['ui_retry']
    projected['execution_contracts']['wine_ui'].update(
        runner=ui['runner'], argv=ui['execution_contract']['argv'], exit_code_path=UI_OUTPUTS['wine_ui_exit_code'])
    projected['execution_contracts']['saved_review'].update(
        runner=saved['runner'], argv=saved['execution_contract']['argv'],
        exit_code_path=CONTROL_OUTPUTS['saved_review_exit_code'])
    refs = references_in(spec) + incomplete_refs + ui_refs
    for reference in refs:
        bound_bytes(reference)
    immutable = [reference['path'] for reference in refs] + list(extra_immutable_paths)
    immutable.extend(prior_immutable)
    preserved = []
    for field in ('preserved_passed_executions', 'preserved_recovery_passed_executions'):
        for row in base_spec[field].values():
            entry = bound_json(row['observation'])
            immutable.extend(reference['path'] for reference in references_in(entry))
            preserved.extend((entry['stdout_log']['path'], entry['exit_code_file']['path']))
            if row['receipt'] is not None:
                preserved.append(row['receipt']['path'])
    projected['global_output_plan'] = project_outputs(actual['global_output_plan'], spec, immutable, preserved)
    return projected_root, original_context, projected
'''
identity_constants = '\nfrom recovery_binding095 import validate_recovery_inputs as validate_prior_ui_inputs\n\n' + (
    'IDENTITY_PRIOR_UI_RETRY = ' + repr(prior_refs) + '\nIDENTITY_INCOMPLETE_UI = ' + repr(ref(lost_path)) + '\n\n')
helper_replacements = [('cache-retry-v1', 'identity-retry-v1'),
    ('full095-ui-cache-retry-source-v1', 'full095-ui-identity-retry-source-v1'),
    ('wine-full-ui-095-cache-retry.py', 'wine-full-ui-095-identity-retry.py'),
    ('source-contract-cache-retry095.json', 'source-contract-identity-retry095.json'),
    ('public-artifacts-manifest-cache-retry095.json', 'public-artifacts-manifest-identity-retry095.json'),
    ('STOPWRITE_CACHE_RETRY_SOURCE_ONLY_RUNTIME_UNRUN', 'STOPWRITE_IDENTITY_RETRY_SOURCE_ONLY_RUNTIME_UNRUN'),
    ('/workspace/.continuation/full095-saved-validator-ui-cache-pending-v4/saved.py',
     '/workspace/.continuation/full095-saved-validator-ui-identity-source-v1/saved.py'),
    (old_validator, identity_constants + new_validator)]
helper, helper_changes = changed(old_helper, helper_replacements)
helper_ref = write('identity_binding095.py', helper)
write('identity-recovery-helper-inverse095.json',
      {'scope': 'SOURCE_ONLY_NO_RECOVERY_VALIDATOR_EXECUTION', 'baseline_reference': ref(OLD_FINAL / 'recovery_binding095.py'),
       'candidate_reference': helper_ref, 'whole_inverse_exact': True, 'changes': helper_changes})

old_context = (OLD_FINAL / 'full095_context_ui_retry.py').read_bytes()
context_text = old_context.decode()
resume_start = context_text.index("if phase == 'resume':\n")
finish_start = context_text.index("elif phase == 'finish':\n")
old_resume = context_text[resume_start:finish_start]
new_resume = old_resume.replace("    prior_recovery_context = bound_json(recovery_spec['prior_recovery']['context'])\n",
    "    prior_recovery_context = bound_json(recovery_spec['prior_recovery']['context'])\n    prior_ui_context = bound_json(recovery_spec['prior_ui_retry']['context'])\n")
new_resume = new_resume.replace('ctx = deepcopy(prior_recovery_context)', 'ctx = deepcopy(prior_ui_context)')
new_resume = new_resume.replace('               ui_retry_started_at=now(),\n',
    "               ui_retry_started_at=prior_ui_context['ui_retry_started_at'],\n               actual_ui_identity_retry=True,\n               ui_identity_retry_started_at=now(),\n               prior_ui_retry=recovery_spec['prior_ui_retry'],\n               prior_incomplete_ui_cache=recovery_spec['prior_incomplete_ui_cache'],\n")
new_resume = new_resume.replace("            <= datetime.fromisoformat(ctx['ui_retry_started_at']),\n",
    "            <= datetime.fromisoformat(ctx['ui_retry_started_at'])\n            <= datetime.fromisoformat(ctx['ui_identity_retry_started_at']),\n")
new_resume = new_resume.replace("                      'ui_retry_started_at': ctx['ui_retry_started_at'],\n",
    "                      'ui_retry_started_at': ctx['ui_retry_started_at'],\n                      'actual_ui_identity_retry': True,\n                      'ui_identity_retry_started_at': ctx['ui_identity_retry_started_at'],\n")
context_replacements = [
    ('PENDING = False\n', 'PENDING = True\n'),
    ("raise SystemExit('PENDING SOURCE-only full095 UI cache retry: actual prior recovery, new reviewed UI/saved source and paths are not bound.')",
     "raise SystemExit('PENDING SOURCE-only full095 UI identity retry: actual prior UI epoch, unknown outcomes and newly reviewed UI/saved source are not bound.')"),
    ('from recovery_binding095 import validate_recovery_inputs, validate_capability_receipt',
     'from identity_binding095 import validate_recovery_inputs, validate_capability_receipt'),
    ("BOUND_BINDING_SHA256 = 'b83ab67ca978d1b1b9e393c6d4e2cfb6c77e3bf9600af9d7ae87fe40975dbb84'",
     "BOUND_BINDING_SHA256 = '__ACTUAL_UI_IDENTITY_RETRY_BINDING_SHA256_PENDING__'"),
    ("path = OUT / 'wine-validation-095-context-ui-cache-retry-v1.json'",
     "path = OUT / 'wine-validation-095-context-ui-identity-retry-v1.json'"),
    ("            and binding.get('actual_ui_retry') is True,",
     "            and binding.get('actual_ui_retry') is True\n            and binding.get('actual_ui_identity_retry') is True,"),
    ("            require(began >= datetime.fromisoformat(context['ui_retry_started_at']),\n",
     "            require(began >= datetime.fromisoformat(context['ui_identity_retry_started_at']),\n"),
    (old_resume, new_resume),
    ("            and ctx.get('actual_original_epoch_recovery') is True and ctx.get('actual_ui_retry') is True,",
     "            and ctx.get('actual_original_epoch_recovery') is True and ctx.get('actual_ui_retry') is True\n            and ctx.get('actual_ui_identity_retry') is True,"),
    ("            and ctx['ui_retry_source'] == recovery_spec['ui_retry']\n",
     "            and ctx['ui_retry_source'] == recovery_spec['ui_retry']\n            and ctx['prior_ui_retry'] == recovery_spec['prior_ui_retry']\n            and ctx['prior_incomplete_ui_cache'] == recovery_spec['prior_incomplete_ui_cache']\n            and ctx['ui_retry_started_at'] == bound_json(recovery_spec['prior_ui_retry']['context'])['ui_retry_started_at']\n"),
    ("            <= datetime.fromisoformat(ctx['ui_retry_started_at']) <= datetime.now(timezone.utc),\n",
     "            <= datetime.fromisoformat(ctx['ui_retry_started_at'])\n            <= datetime.fromisoformat(ctx['ui_identity_retry_started_at']) <= datetime.now(timezone.utc),\n"),
    ('               prior_recovery_started_at_preserved=True, ui_retry_contract_projection_verified=True,\n',
     '               prior_recovery_started_at_preserved=True, ui_retry_contract_projection_verified=True,\n               prior_ui_retry_started_at_preserved=True, prior_incomplete_ui_cache_preserved=True,\n               ui_identity_retry_contract_projection_verified=True,\n')]
context, context_changes = changed(old_context, context_replacements)
if any(row['count'] != 1 for row in context_changes):
    raise ValueError('Context inverse must retain unique exact spans for Root sealer')
context_ref = write('full095_context_ui_retry_pending.py', context)
write('ui-retry-context-inverse095.json', {'format_version': 1,
    'scope': 'SOURCE_ONLY_NO_CONTEXT_OR_PROJECT_EXECUTION',
    'baseline_context_reference': ref(OLD_FINAL / 'full095_context_ui_retry.py'),
    'pending_context_reference': context_ref, 'changes': context_changes})

# Root spec is a pending projection, carrying real prior refs without inventing fresh refs.
template = deepcopy(prior_spec)
template['status'] = 'SOURCE_ONLY_PENDING_ACTUAL_ROOT_UI_RETRY_BINDING'
template['prior_ui_retry'] = prior_refs
template['prior_incomplete_ui_cache'] = ref(lost_path)
for key in ('replacement_output_paths', 'ui_retry_output_paths'):
    template[key] = {name: path.replace('cache-retry-v1', 'identity-retry-v1')
                     for name, path in template[key].items()}
retry = template['ui_retry']
for key in ('manifest', 'source_contract', 'runner', 'source_review'):
    retry[key] = None
retry['planned_root_prelaunch_path'] = '/workspace/.continuation/root-full095-ui-identity-retry-v1-prelaunch.json'
retry['planned_saved_input_path'] = '/workspace/.continuation/root-full095-ui-identity-retry-v1-saved-input-spec.json'
retry['ui'] = None
retry['saved_review_source'] = {'runner': None, 'source_review': None,
    'review_pointers': deepcopy(prior_spec['ui_retry']['saved_review_source']['review_pointers']),
    'argv': ['/workspace/rougezhushou/.venv/bin/python',
             '/workspace/.continuation/full095-saved-validator-ui-identity-source-v1/saved.py',
             '--spec', '/workspace/.continuation/root-full095-ui-identity-retry-v1-saved-input-spec.json',
             '--output', '/workspace/.continuation/root-full095-ui-identity-retry-v1-saved-review.json']}
template['root_ui_prelaunch'] = None
write('root-ui-retry-input-template095.json', template)

# The original Root-only sealer remains strict; only the declared new packet/helper/history extends.
old_sealer = (OLD_PENDING / 'seal_ui_retry095.py').read_bytes()
sealer_replacements = [
    ('from recovery_binding095 import NEW_OUTPUTS, NATIVE_DIRECTORIES, SELECTED_RETRY_OUTPUTS, validate_recovery_inputs',
     'from identity_binding095 import NEW_OUTPUTS, NATIVE_DIRECTORIES, SELECTED_RETRY_OUTPUTS, validate_recovery_inputs'),
    ('/workspace/.continuation/full095-regression-ui-cache-resume-final-v1', str(FINAL)),
    ("('binding_validation095.py', 'historical-classifications090.json', 'capability_binding095.py', 'recovery_binding095.py')",
     "('binding_validation095.py', 'historical-classifications090.json', 'capability_binding095.py', 'recovery_binding095.py', 'identity_binding095.py')"),
    ("digest((here / 'recovery_binding095.py').read_bytes())", "digest((here / 'identity_binding095.py').read_bytes())"),
    ("'root_spec_projection_from_ui_retry': True,", "'root_spec_projection_from_ui_retry': True, 'actual_ui_identity_retry': True,"),
    ("'prior_incomplete_ui': spec['prior_incomplete_ui'], 'project_calls': 0,",
     "'prior_incomplete_ui': spec['prior_incomplete_ui'],\n               'prior_ui_retry': spec['prior_ui_retry'],\n               'prior_incomplete_ui_cache': spec['prior_incomplete_ui_cache'], 'project_calls': 0,"),
    ('__ACTUAL_UI_RETRY_BINDING_SHA256_PENDING__', '__ACTUAL_UI_IDENTITY_RETRY_BINDING_SHA256_PENDING__'),
    ("'changed_execution_contracts_from_prior_recovery': ['wine_ui', 'saved_review', 'wine_selected'],",
     "'changed_execution_contracts_from_prior_recovery': ['wine_ui', 'saved_review', 'wine_selected'],\n               'changed_execution_contracts_from_prior_ui_retry': ['wine_ui', 'saved_review'],\n               'prior_ui_retry': spec['prior_ui_retry'],\n               'prior_incomplete_ui_cache': spec['prior_incomplete_ui_cache'],\n               'prior_ui_retry_started_at': bound_json(spec['prior_ui_retry']['context'])['ui_retry_started_at'],"),
    ('adds real ui_retry_started_at', 'preserves real ui_retry_started_at and adds real ui_identity_retry_started_at')]
sealer, sealer_changes = changed(old_sealer, sealer_replacements)
sealer_ref = write('seal_ui_retry095.py', sealer)
write('ui-retry-sealer-delta095.json', {'scope': 'SOURCE_ONLY_NO_SEALER_EXECUTION',
    'baseline_reference': ref(OLD_PENDING / 'seal_ui_retry095.py'), 'candidate_reference': sealer_ref,
    'whole_inverse_exact': True, 'changes': sealer_changes})

proof = {'format_version': 1, 'section': 95, 'scope': 'SOURCE_ONLY_AST_COMPILE_AND_EXACT_INVERSE',
    'source_gate_passed': None, 'runtime_pass': False, 'actual_runtime_calls': 0,
    'original_epoch': prior_context['started_at'], 'prior_recovery_boundary': prior_context['recovery_started_at'],
    'prior_ui_retry_boundary': prior_context['ui_retry_started_at'], 'new_identity_boundary': None,
    'prior_ui_retry': prior_refs, 'prior_incomplete_ui_cache': ref(lost_path),
    'whole_prior_recovery_helper_retained': True, 'whole_core_and_capability_binders_retained': True,
    'helper_inverse_exact': True, 'context_inverse_exact': True, 'sealer_inverse_exact': True,
    'context_changes': len(context_changes), 'helper_changes': len(helper_changes),
    'sealer_changes': len(sealer_changes), 'producer_source_ref': None, 'producer_formal_review': None,
    'Saved_source_ref': None, 'Saved_formal_review': None, 'Root_actual_spec': None,
    'Root_actual_seal': None, 'Root_actual_resume': None, 'Root_actual_UI_or_Saved_or_finish': None,
    'commit_or_push_performed': False, 'third_attempt_failure_requires_deferral': True}
write('author-source-checks-ui-retry095.json', proof)
write('UI_RETRY_CONTRACT095.md', b'''# Third UI attempt: Source-only strict recovery extension\n\nOriginal 2026-10-08 22:54:16 epoch, 23:36:41 recovery and actual second UI 2026-10-09 00:59:43 boundary stay immutable. The new final resume must preserve ui_retry_started_at and set ui_identity_retry_started_at to actual invocation time. No new time, PASS, exit or publication is authored here.\n\nThe complete prior recovery_binding095.py is retained, along with whole b7a6/ad1b/c17 support. identity_binding095.py first revalidates the physical b83 spec and its exact prior actual_inputs through those whole original modules. It then validates the second lost capsule and all 2,310 closed chunks without treating 136,836 partial records as completion. Primary status remains NULL, original sinks remain absent, cause UNKNOWN and Root termination false. Six actual primary-zero observations stay unchanged and are never replayed.\n\nAll eight primary, exact argv/source, graph/saved, Root-viewed PNG, physical file references and original finish gates remain required. UI/Saved freshness uses only the new actual identity boundary; prior four and two Wine proofs retain the earlier actual boundaries. New output/native namespaces must be unused and disjoint from immutable history.\n\nRoot fills only actual physical producer/Saved/formal/prelaunch refs and the exact UI projection in the pending template, obtains an independent review bound to the complete Root spec/package, then invokes the Root-only exclusive sealer. A second independent final Source/spec projection review precedes actual resume/UI/Saved/finish. Source-only author checks and compile are not runtime acceptance.\n\nIf the third actual UI attempt remains incomplete or fails, preserve its evidence and defer the recurring issue; no fourth attempt is authorized by this packet. Sections 96-98 are not applied or completed here.\n''')

manifest = {'format_version': 1, 'section': 95,
    'status': 'SOURCE_ONLY_PENDING_ACTUAL_ROOT_UI_RETRY_BINDING', 'STOPWRITE': True,
    'runtime_executed': False, 'project_calls': 0, 'available_checks_passed': False,
    'payload_files': [ref(path) for path in sorted(HERE.iterdir()) if path.is_file()]}
manifest_ref = write('public-artifacts-manifest-ui-retry095.json', manifest)
write('handoff-ui-retry095.json', {'format_version': 1, 'section': 95,
    'status': 'STOPWRITE_IDENTITY_UI_RETRY_SOURCE_ONLY_ROOT_SPEC_FORMAL_FINAL_RUNTIME_PENDING',
    'manifest': manifest_ref, 'pending_context': context_ref, 'recovery_helper': helper_ref,
    'sealer': sealer_ref, 'root_template': ref(HERE / 'root-ui-retry-input-template095.json'),
    'source_gate_passed': None, 'runtime_pass': False, 'actual_identity_retry_boundary': None,
    'root_actual_spec': None, 'root_actual_seal': None, 'root_actual_resume': None,
    'available_checks_passed': False, 'commit_or_push_performed': False,
    'missing_actual_references': ['producer Source runner/contract/MF/formal', 'Saved reviewed runner/formal',
                                 'Root actual prelaunch/spec/formal/final/seal/resume'],
    'reserved_final_directory': str(FINAL), 'third_attempt_failure_requires_deferral': True})
print(json.dumps({'status': 'STOPWRITE_SOURCE_ONLY_NOT_EXECUTED', 'manifest': manifest_ref,
                  'pending_context': context_ref, 'identity_helper': helper_ref, 'sealer': sealer_ref}))
