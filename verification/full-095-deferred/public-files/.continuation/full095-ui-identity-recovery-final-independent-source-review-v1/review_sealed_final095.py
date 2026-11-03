"""Independent actual FINAL Source review; execute no target or reviewed helper."""
import ast
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).parent
FINAL = Path('/workspace/.continuation/full095-regression-ui-identity-resume-final-v1')
SOURCE = Path('/workspace/.continuation/full095-regression-ui-identity-resume-source-v1')
ROOT = Path('/workspace/rougezhushou')
refs = {}
checks = []

def sha(data): return hashlib.sha256(data).hexdigest()

def read(path, expected=None):
    path = Path(path)
    assert path.is_absolute() and path.is_file() and not path.is_symlink()
    data = path.read_bytes()
    ref = {'path': str(path), 'bytes': len(data), 'sha256': sha(data)}
    if expected:
        assert all(ref[k] == v for k, v in expected.items()), (ref, expected)
    assert str(path) not in refs or refs[str(path)] == ref
    refs[str(path)] = ref
    return data

def bound(ref):
    return read(ref['path'], {k:ref[k] for k in ('path', 'bytes', 'sha256')})

def doc(ref): return json.loads(bound(ref))

def load(path, expected=None): return json.loads(read(path, expected))

def item(name, evidence): checks.append({'name': name, 'passed': True, 'evidence': evidence})

def references(value):
    if isinstance(value, dict):
        if {'path', 'bytes', 'sha256'} <= set(value): return [value]
        return [r for child in value.values() for r in references(child)]
    if isinstance(value, list): return [r for child in value for r in references(child)]
    return []

def canonical(path):
    path = Path(path)
    assert path.is_absolute() and '..' not in path.parts
    return str(path.resolve(strict=False))

manifest_path = FINAL / 'public-artifacts-manifest-sealed-recovery095.json'
manifest = load(manifest_path, {'bytes':2287, 'sha256':'6a75293891156344f21176040fa57a3f57860cb857264f7c22f918e27323a1c5'})
assert manifest['status'] == 'FINAL_UI_RETRY_SOURCE_BOUND_RUNTIME_NOT_EXECUTED'
assert len(manifest['payload_files']) == 8
for ref in manifest['payload_files']:
    assert Path(ref['path']).parent == FINAL
    bound(ref)
assert {p.name for p in FINAL.iterdir()} == {Path(r['path']).name for r in manifest['payload_files']} | {manifest_path.name, 'handoff-sealed-recovery095.json'}
item('Actual FINAL manifest exact eight payloads and ten-file physical set', refs[str(manifest_path)])

binding_path = FINAL / 'actual-full095-source-binding.json'
binding = load(binding_path, {'bytes':693455, 'sha256':'e818ba9aefa4d8cd739da561540ef2e49cbf38c70311346cd10c7b2d86be1bf6'})
context_path = FINAL / 'full095_context_ui_retry.py'
context = read(context_path, {'bytes':36289, 'sha256':'07c011b1fa94a3def915f4ff0efeaa32c21b6e1d91e9f8c3d3ef9dbbd4ea39ef'})
pending = read(SOURCE / 'full095_context_ui_retry_pending.py', {'bytes':36275, 'sha256':'0cddc35c272e73fb44fbede3564cf487064dda28fcaaf4066bc3889d01148066'})
changes = [(b'PENDING = True\n', b'PENDING = False\n'),
    (b"BOUND_BINDING_SHA256 = '__ACTUAL_UI_IDENTITY_RETRY_BINDING_SHA256_PENDING__'",
     b"BOUND_BINDING_SHA256 = 'e818ba9aefa4d8cd739da561540ef2e49cbf38c70311346cd10c7b2d86be1bf6'")]
recovered = context
for before, after in reversed(changes):
    assert recovered.count(after) == 1
    recovered = recovered.replace(after, before, 1)
assert recovered == pending
compile(context, str(context_path), 'exec')
tree = ast.parse(context)
literal_values = {n.targets[0].id: ast.literal_eval(n.value) for n in tree.body if isinstance(n, ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0], ast.Name) and n.targets[0].id in ('PENDING', 'BOUND_BINDING_SHA256')}
assert literal_values == {'PENDING':False, 'BOUND_BINDING_SHA256':refs[str(binding_path)]['sha256']}
item('Entire FINAL context inverse differs only by two exact binding literals', {'pending':refs[str(SOURCE / 'full095_context_ui_retry_pending.py')], 'actual_context':refs[str(context_path)], 'actual_binding':refs[str(binding_path)], 'target_code_object_executions':0})

support_names = ('binding_validation095.py', 'historical-classifications090.json', 'capability_binding095.py', 'recovery_binding095.py', 'identity_binding095.py')
support_refs = []
for name in support_names:
    assert read(FINAL / name) == read(SOURCE / name)
    support_refs.append(refs[str(FINAL / name)])
assert binding['final_support_files'] == support_refs
item('All five whole-byte support copies and exact ordered final_support_files', support_refs)

spec = doc(binding['recovery_spec_reference'])
assert refs[binding['recovery_spec_reference']['path']]['sha256'] == '54cc86e167062dc368b4d74e3cde602bd81a2c716a7bc8e024eeb8ccb862fa33'
assert spec == binding['recovery_spec']
formal = doc(binding['recovery_formal_source_review'])
assert binding['recovery_formal_source_review']['sha256'] == '19547003dbeeb96ddb65c7dac9bab6963f8cd976f80625760c1985c3916083f6'
assert formal['source_gate_passed'] is True and formal['runtime_pass'] is False
assert formal['recovery_spec_sha256'] == binding['recovery_spec_reference']['sha256']
assert formal['actual_prelaunch'] == spec['root_ui_prelaunch']
prelaunch = doc(spec['root_ui_prelaunch'])
assert prelaunch['source_gate_passed'] is True and prelaunch['runtime_pass'] is False and prelaunch['target_execution_performed'] is False
assert prelaunch['runner'] == spec['ui_retry']['runner'] and prelaunch['formal_source_review'] == spec['ui_retry']['source_review']
for ref in formal['checked_file_refs'].values(): bound(ref)
item('Exact physical actualspec and independent formal gate plus every 2696 previously checked file ref retained', {'spec':binding['recovery_spec_reference'], 'formal':binding['recovery_formal_source_review'], 'actual_prelaunch':spec['root_ui_prelaunch'], 'previous_refs_reread':len(formal['checked_file_refs'])})

assert binding['format_version'] == 3 and binding['section'] == 95 and binding['status'] == 'SEALED_REAL95_SOURCE_NOT_RUNTIME_PASS'
assert all(binding[k] is True for k in ('actual_original_epoch_recovery','actual_ui_retry','root_spec_projection_from_ui_retry','actual_ui_identity_retry','original_classifier_unchanged'))
assert all(binding[k] is False for k in ('full095_execution_performed_by_sealer','available_checks_passed','commit_or_push_performed'))
assert binding['project_calls'] == 0
for key in ('prior_incomplete_ui','prior_ui_retry','prior_incomplete_ui_cache'):
    assert binding[key] == spec[key]
assert binding['prior_recovery_binding'] == spec['prior_recovery']['binding']
source_mf = doc(binding['source_preparation_manifest'])
expected_source_paths = [r['path'] for r in source_mf['payload_files']]
expected_source_paths += [binding['source_preparation_manifest']['path'], str(SOURCE / 'handoff-ui-retry095.json'), binding['recovery_spec_reference']['path'], binding['recovery_formal_source_review']['path']]
assert binding['source_package_input_paths'] == expected_source_paths
assert binding['pending_context'] == refs[str(SOURCE / 'full095_context_ui_retry_pending.py')]
assert binding['original_context_inverse']['path'] == str(SOURCE / 'ui-retry-context-inverse095.json')
item('Sealed binding exact recovery flags Source-only statuses input paths old outcomes and actualspec', {'available_checks_passed':False, 'actual_UI_execution_by_sealer':False, 'source_input_path_count':len(expected_source_paths)})

prior = doc(spec['prior_ui_retry']['binding'])
expected_root = deepcopy(prior['root_spec'])
expected_root['ui'] = deepcopy(spec['ui_retry']['ui'])
saved_source = spec['ui_retry']['saved_review_source']
saved = deepcopy(prior['root_spec']['saved_review'])
saved.update(runner=saved_source['runner'], receipt_path=spec['ui_retry_output_paths']['saved_review_receipt'], stdout_log_path=spec['ui_retry_output_paths']['saved_review_stdout'])
saved['execution_contract'].update(argv=saved_source['argv'], source_review=saved_source['source_review'], review_pointers=saved_source['review_pointers'])
expected_root['saved_review'] = saved
expected_root['io_plan']['exit_code_paths'].update(wine_ui=spec['ui_retry_output_paths']['wine_ui_exit_code'], saved_review=spec['ui_retry_output_paths']['saved_review_exit_code'])
expected_root['io_plan'].update(visual_review_path=spec['ui_retry_output_paths']['visual_review'], ui_extra_acceptance_path=spec['ui_retry_output_paths']['ui_extra_acceptance'])
assert binding['root_spec'] == expected_root
assert binding['root_spec_reference'] == prior['root_spec_reference']
item('Entire sealed root_spec reconstructed from old b83 with only reviewed UI Saved and their planned controls changed', {'unchanged_original_root_spec_reference':binding['root_spec_reference'], 'all_other_fields_preserved':True})

expected_actual = deepcopy(prior['actual_inputs'])
expected_actual['UI_source_binding'] = spec['ui_retry']['ui']
expected_actual['ui_retry'] = spec['ui_retry']
expected_actual['execution_contracts']['wine_ui'].update(runner=expected_root['ui']['runner'], argv=expected_root['ui']['execution_contract']['argv'], exit_code_path=spec['ui_retry_output_paths']['wine_ui_exit_code'])
expected_actual['execution_contracts']['saved_review'].update(runner=saved['runner'], argv=saved['execution_contract']['argv'], exit_code_path=spec['ui_retry_output_paths']['saved_review_exit_code'])
old_plan = expected_actual['global_output_plan']
plan = deepcopy(old_plan)
plan['paths'].update(spec['ui_retry_output_paths']); plan['paths'].update(spec['selected_retry_output_paths'])
plan['canonical_paths'] = {k:canonical(v) for k,v in plan['paths'].items()}
plan['fresh_evidence_directories'] = ['/workspace/.compat/full095-ui-native-identity-retry-v1']
loss = doc(spec['prior_incomplete_ui_cache'])
native = doc(loss['native_index'])
lost_chunks = [{'path':str(Path('/workspace/.compat')/r['file']), 'bytes':r['bytes'], 'sha256':r['sha256']} for r in native['chunks']]
producer_manifest = doc(spec['ui_retry']['manifest'])
producer_parent = Path(spec['ui_retry']['manifest']['path']).parent
producer_payloads = [{'path':str(producer_parent/name), **value} for name,value in producer_manifest['artifacts'].items()]
explicit_refs = references(spec) + references(loss) + lost_chunks + producer_payloads
immutable = [r['path'] for r in explicit_refs]
extra = expected_source_paths + [r['path'] for r in support_refs] + [str(context_path),str(binding_path)]
immutable += extra
prior_immutable = prior['source_package_input_paths'] + [prior['recovery_spec_reference']['path']]
prior_immutable += [spec['prior_ui_retry']['binding']['path'], spec['prior_ui_retry']['runner']['path']]
prior_immutable += [r['path'] for r in prior['final_support_files']]
immutable += prior_immutable
for field in ('preserved_passed_executions','preserved_recovery_passed_executions'):
    for row in spec[field].values():
        immutable += [r['path'] for r in references(doc(row['observation']))]
plan['immutable_input_paths'] = sorted(set(old_plan['immutable_input_paths']) | {canonical(v) for v in immutable})
expected_actual['global_output_plan'] = plan
assert expected_actual == binding['actual_inputs']
assert len(expected_actual['execution_contracts']) == 8
assert all(expected_actual['execution_contracts'][n] == prior['actual_inputs']['execution_contracts'][n]
           for n in ('linux_full','linux_selected','linux_pip','wine_full','wine_selected','wine_pip'))
item('Entire actual_inputs independently reconstructed including exact immutable paths plan and all eight contracts; six retained', {'actual_source_files':expected_actual['source_files'], 'execution_contracts':8, 'preserved_contracts':6, 'immutable_inputs':len(plan['immutable_input_paths'])})

assert len(set(plan['canonical_paths'].values())) == len(plan['canonical_paths'])
for name,path in plan['canonical_paths'].items():
    for other_name,other in plan['canonical_paths'].items():
        assert name == other_name or not Path(other).is_relative_to(Path(path))
assert all(not Path(p).exists() for p in spec['ui_retry_output_paths'].values())
assert not Path('/workspace/.compat/full095-ui-native-identity-retry-v1').exists()
assert not Path('/workspace/.compat/wine-validation-095-context-ui-identity-retry-v1.json').exists()
item('Every new third-attempt output and actual resume boundary still absent; unique fresh namespace', {'actual_third_resume_executed':False, 'actual_third_UI_started':False})

receipt = load(FINAL / 'seal-source-recovery-receipt095.json')
assert receipt['source_binding_passed'] is True and receipt['available_checks_passed'] is False
assert receipt['runtime_executions'] == receipt['project_calls'] == receipt['original_classifier_byte_changes'] == 0
assert receipt['changed_execution_contracts_from_prior_ui_retry'] == ['wine_ui','saved_review']
assert receipt['pending_to_final_changes'] == [{'before':a.decode(),'after':b.decode()} for a,b in changes]
assert receipt['prior_ui_retry_started_at'] == '2026-10-09T00:59:43.753835+00:00'
assert receipt['prior_recovery_started_at'] == '2026-10-08T23:36:41.779450+00:00'
assert receipt['original_context_epoch_started_at'] == '2026-10-08T22:54:16.947394+00:00'
for field in ('preserved_passed_executions','preserved_recovery_passed_executions','prior_failed_execution','prior_selected_failed_execution','prior_ui_retry','prior_incomplete_ui_cache','prior_incomplete_ui'):
    assert receipt[field] == spec[field]
item('Actual Source seal receipt preserves all actual prior epochs six zeros failures and two lost outcomes; no runtime PASS', refs[str(FINAL/'seal-source-recovery-receipt095.json')])

maintained = {p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for d in ('rouge','tests','scripts') for p in sorted((ROOT/d).rglob('*')) if p.is_file() and p.suffix in ('.py','.json') and '__pycache__' not in p.parts}
assert len(maintained) == 735 and maintained == binding['actual_inputs']['source_sha256']
for ref in manifest['payload_files']: bound(ref)
bound(binding['recovery_spec_reference']); bound(binding['recovery_formal_source_review'])
item('All735 current maintained bytes and sealed eight payloads unchanged during postseal review', {'source_files':735,'source_drift':[]})

result = {'format_version':1, 'section':95, 'status':'STOPWRITE_INDEPENDENT_ACTUAL_IDENTITY_FINAL_SOURCE_REVIEW_PASSED_RUNTIME_UNRUN',
          'source_gate_passed':True, 'runtime_pass':False, 'runtime_executed':False, 'execution_ready':False,
          'final_context_runner':refs[str(context_path)], 'final_context_runner_sha256':refs[str(context_path)]['sha256'],
          'actual_binding':refs[str(binding_path)], 'actual_binding_sha256':refs[str(binding_path)]['sha256'],
          'sealed_manifest':refs[str(manifest_path)], 'actual_spec':binding['recovery_spec_reference'],
          'actual_spec_sha256':binding['recovery_spec_reference']['sha256'], 'actual_spec_source_formal':binding['recovery_formal_source_review'],
          'actual_prelaunch':spec['root_ui_prelaunch'], 'review_completed_at_UTC':datetime.now(timezone.utc).isoformat(),
          'independent_standard_library_review':{'checks':len(checks),'passed':len(checks),'blocked':0,'results':checks},
          'checked_file_refs':dict(sorted(refs.items())),
          'qualification':['This validates actual sealed Source bytes and projections only. Root sealer metadata primary is separate from UI product validation.',
                           'Only two literal edits restore entire pending context; original strict eight-primary, native, Saved and four actual visual gates remain authoritative.',
                           'Old source gate refs including all2585 historical compressed chunks were independently reread. No gzip decompression, graph codec or target helper was executed.',
                           'Actual new binding exists as Source metadata. Actual third resume boundary and UI/Saved primary outcomes are still NULL and must be generated by real Root actions.',
                           'Unsuccessful third same-issue UI execution must be deferred. No fourth attempt authorized by this Source gate.',
                           'Live Git HEAD/branch was not queried by this reviewer; preserved original validators require those checks during actual Root resume.'],
          'actual_ui_identity_retry_started_at':None, 'actual_UI_primary_exit_code':None, 'actual_Saved_primary_exit_code':None,
          'actual_runtime_PASS':None, 'available_checks_passed':False, 'completed_section_increment':0, 'commit_or_push_performed':False,
          'target_execution_counts':{'context':0,'sealer':0,'helper':0,'codecs':0,'project':0,'tests':0,'Wine':0,'Qt':0,'DLL':0,'Git':0,'process_control':0}, 'STOPWRITE':True}
path = HERE/'formal-independent-final-source-review095-ui-identity-v1.json'
with path.open('x',encoding='utf-8') as stream:
    json.dump(result,stream,ensure_ascii=False,allow_nan=False,indent=2);stream.write('\n')
print(json.dumps({'source_gate_passed':True,'runtime_pass':False,'checks':len(checks),'formal':str(path)}))
