"""Validate actual selected repairs and exact verification-only source equivalence."""
from pathlib import Path
from hashlib import sha256
import importlib.util,json,sys,gzip
R=Path(__file__).resolve().parents[1];B=R/'.cache/full425-prepared/attempt-4';A=R/'verification/full-425/selected-repair4';sys.path[:0]=[str(B),str(R),str(R/'scripts')]
from full425_common import bound,sha
launch=json.loads((R/'.cache/425-selected-repair4-launch-input.json').read_bytes());data,activation=bound(launch['parent'],launch['freeze_sha256'],launch['activation_sha256']);old=json.loads((R/'verification/full-425/source-freeze-attempt3.json').read_bytes())
manifest=json.loads((A/'archive-manifest.json').read_bytes());assert manifest['actual_selected_root_exit']==0 and manifest['private_or_dependency_directories_traversed']is False and manifest['full_available_scope_PASS_claimed_by_archive']is False
C=Path(manifest['container']);assert not C.is_symlink()
assert set(p.relative_to(A).as_posix()for p in A.rglob('*')if p.is_file())==set(manifest['files'])|{'archive-manifest.json'}
for name,row in manifest['files'].items():
 assert '..'not in Path(name).parts and not Path(name).is_absolute();p=A/name;origin=Path(row['origin']);assert p.is_file()and not p.is_symlink()and p.resolve().is_relative_to(A.resolve())
 assert sha(p)==row['sha256']and p.stat().st_size==row['bytes']and p.read_bytes()==origin.read_bytes()
allowed={'tests/test_player_compact_389.py','tests/test_player_feature_416.py','rouge/player_feature_416_acceptance.py'};differences={}
for key in ['source_sha256','supplemental_public_inputs_sha256','legacy_native_source_sha256']:
 assert set(old[key])==set(data[key]);diff={name:{'baseline':old[key][name],'current':data[key][name]}for name in old[key]if old[key][name]!=data[key][name]};assert set(diff)<=allowed;differences[key]=diff
assert set(differences['source_sha256'])==allowed
for key in ['selectors','p3_scripts','p3_script_options','p3_script_selected_paths','template_bundle_sha256','local_public_input_bindings','historical_manifest_bindings','canonical_local_public_input_bindings','canonical_local_public_input_sha256','legacy_external_additional_sha256','local_public_input_sha256','maintained_runner_sha256','cloud_selector_api_sha256','original_typed_auditor_sha256','previous_full_scope_receipt','previous_full_scope_receipt_sha256','new_installed_native_scripts','new_installed_selector_count','diagnostic_layout_modes']:assert old[key]==data[key],key
baseline=json.loads((R/'verification/full-425/baseline3-readonly-audit.json').read_bytes());bp=json.loads((R/'verification/full-425/baseline3-readonly-audit-process/process.json').read_bytes());assert baseline['passed']and not baseline['baseline_full_suite_passed']and bp['passed']and bp['actual_observed_exit']==0
baseline_union={**old['source_sha256'],**old['supplemental_public_inputs_sha256']};assert bp['source_sha256_before']==bp['source_sha256_after']and all(baseline_union[n]==h for n,h in bp['source_sha256_after'].items())
spec=importlib.util.spec_from_file_location('selected425_current_source_reader',R/'.cache/full425-post-attempt4/seal_summary425.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
m.BASE=B;m.ARCHIVE=A;m.FREEZE=R/'verification/full-425/source-freeze-attempt4.json';m.PARENT=launch['parent'];m.ATTEMPT=4;m.FREEZE_SHA=launch['freeze_sha256'];m.ACTIVATION_SHA=launch['activation_sha256'];m.REVIEW_SHA=sha(B/'review_results425.py')
_,terminal,closure,source_stable=m.load_readonly_helpers();ledger=json.loads((A/'orchestration.json').read_bytes());assert ledger['status']=='all_selected_repairs_terminal'
for row in ledger['steps']:
 if row.get('child_primary_exit')!=0:continue
 log=(A/row['name']/'supervisor.json.stderr.log').read_text('utf8',errors='replace')
 assert not any(marker in log for marker in ['Traceback (most recent call last):','Error calling Python override','Exception ignored in:']),row['name']
# This is a fresh selected review built from actual raw outputs. It does not
# replace or relabel the failed original full3 automatic review.
details={}
for mode in ['p3_416','p3_425']:
 raw=json.loads((A/mode/'actual/window.json').read_bytes());close=json.loads((A/mode/'actual/full425-source-closure.json').read_bytes());sup=json.loads((A/mode/'supervisor.json').read_bytes())
 details[mode]={'receipt_sha256':close['actual_receipt_sha256'],'actual_fixture_pid':raw['process_id'],'owned_launcher_pid':sup['pid'],'source_count':len(data['p3_script_selected_paths'][mode]),'checks':raw['unique_checks']}
audit=json.loads((A/'legacy/independent-saved-readback-audit.json').read_bytes());rows=json.loads(gzip.decompress((A/'legacy/actual/wine-ui-new-states-100.json.gz').read_bytes()))['actual_new_window_states']
details['legacy']={key:audit[key]for key in ['complete_runtime_checks','saved_rows','passed_flag_records','metadata_records','current_revised_assertions','original552_maintry_sha256','readonly_trace_empty_rows_not_invented','exact_ten_admission_indices']}
details['legacy'].update(actual_original_typed_exit=0,audit_sha256=sha(A/'legacy/independent-saved-readback-audit.json'),explicit_three_text_requests=sum(row['explicit_three_text_requests']for row in rows),original_projection_scope=len(rows)-len(audit['exact_ten_admission_indices']),all_original552_body_preserved=audit['original552_maintry_sha256']=='11da3f02423dc96598480c85c31f3c8ba4672f6f4cd232741579ff45a7f87922')
raw30=json.loads((A/'current30/actual/window.json').read_bytes());failure=raw30.get('failure')or{}
review={'component_details':details,'current30_original_actual_symlink_prerequisite_unavailable':not raw30['passed']and failure.get('type')=='OSError'and '[WinError 1314]'in failure.get('message','')}
raws,supers,proofs=m.verify_components(data,C,ledger,review,terminal,closure,source_stable);typed=m.verify_typed(data,review,C);current=m.verify_current30(raws,supers,proofs,review);functional=m.verify_functional(data,source_stable)
identity=raws['p3_416'];assert identity['qpa']=='windows'and all(label in identity['checks']for label in ['native_identity_unittest_actual_windows_backend','original_native_identity_case_executed_without_skip'])and any(label.startswith('original_native_identity_assertions_passed_')for label in identity['checks'])
original_cases=[]
for line in(A/'p3_416/supervisor.json.stdout.log').read_text('utf8').splitlines():
 try:row=json.loads(line)
 except ValueError:continue
 if isinstance(row,dict)and row.get('kind')=='actual_original_native_identity_unittest':original_cases.append(row)
assert len(original_cases)==1 and original_cases[0]['tests_run']==1 and original_cases[0]['was_successful']and original_cases[0]['skips']==[]and original_cases[0]['qpa']=='windows'
unit=[]
for qpa in ['offscreen','windows']:
 folder=R/f'verification/full-425/selected-repair4-unit-{qpa}';p=json.loads((folder/'process.json').read_bytes());raw=json.loads((folder/'actual.json').read_bytes());assert p['passed']and p['actual_observed_exit']==0 and raw['passed']and raw['tests_run']==5 and raw['actual_qpa']==qpa and raw['failures']==raw['errors']==[]
 assert raw['source_sha256_before']==raw['source_sha256_after']==p['source_sha256_before']==p['source_sha256_after']
 assert all({**data['source_sha256'],**data['supplemental_public_inputs_sha256']}[n]==h for n,h in raw['source_sha256_after'].items())
 expected=['tests.test_player_feature_416.BindingTests.test_owned_native_identity_and_geometry']if qpa=='offscreen'else[];assert[r['test']for r in raw['skips']]==expected
 unit.append({'qpa':qpa,'process':m.proof(folder/'process.json'),'actual_receipt':m.proof(folder/'actual.json'),'tests_run':5,'actual_skip_count':len(raw['skips']),'actual_selectors':raw['selectors'],'skip_not_counted_as_PASS':True})
bound(launch['parent'],launch['freeze_sha256'],launch['activation_sha256'])
result={'section':425,'kind':'CURRENT_SELECTED_REPAIR_AND_VERIFICATION_ONLY_EQUIVALENCE_AUDIT','passed':True,'all_product_code_and_game_data_identical_to_full3':True,'full4_execution_claimed':False,'actual_full3_root_exit':1,'actual_selected_root_exit':0,'verification_only_changes':differences,'current_source_freeze':m.proof(m.FREEZE),'actual_selected_component_proofs':proofs,'legacy_complete_original_typed_scope':typed,'current30_and_independent29':current,'functional425_necessary_and_native':functional,'original_native_identity_unit_actual_execution':original_cases[0],'actual_repaired_modules_by_backend':unit,'baseline3_evidence_audit':m.proof(R/'verification/full-425/baseline3-readonly-audit.json'),'baseline3_auditor_process':m.proof(R/'verification/full-425/baseline3-readonly-audit-process/process.json'),'selected_archive':m.proof(A/'archive-manifest.json'),'visual_review_still_required':True,'audit_source_sha256':sha(Path(__file__))}
out=R/'verification/full-425/selected-repair4-audit.json';assert not out.exists();out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'selected_repair_and_equivalence_checks_passed':True,'full3_root_exit_preserved':1,'full4_execution_claimed':False,'visual_review_still_required':True}))
