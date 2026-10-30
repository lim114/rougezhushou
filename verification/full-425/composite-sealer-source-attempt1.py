"""Seal only full original coverage plus actual repairs with strict verifier-only equivalence.

No original failure, root exit, source map, skip or unavailable record is rewritten.
This must never be reported as a single all-green full4 execution.
"""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import importlib.util,json,sys
R=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file());D=R/'verification/full-425';B=R/'.cache/full425-prepared/attempt-4';sys.path[:0]=[str(B),str(R),str(R/'scripts')]
from full425_common import bound,sha
def read(path):return json.loads(path.read_bytes())
def proof(path):return {'path':path.relative_to(R).as_posix(),'sha256':sha(path),'bytes':path.stat().st_size}
def check_ref(row):
 name=row.get('path',row.get('file',row.get('receipt')));p=R/name;assert p.is_file()and not p.is_symlink()and p.resolve().is_relative_to(R.resolve())and sha(p)==row['sha256'];return p
out=D/'summary.json';assert not out.exists()
launch=read(R/'.cache/425-selected-repair4-launch-input.json');data,activation=bound(launch['parent'],launch['freeze_sha256'],launch['activation_sha256']);old=read(D/'source-freeze-attempt3.json')
baseline=read(D/'baseline3-readonly-audit.json');repair=read(D/'selected-repair4-audit.json');assert baseline['passed']and repair['passed']and not baseline['baseline_full_suite_passed']and baseline['actual_original_root_exit']==1 and not repair['full4_execution_claimed']
schema_path=D/'postprocessing-schema-repair/closure.json';schema=read(schema_path);assert schema['passed']and schema['only_changed_validator_function']=='verify_functional'and schema['test_or_native_fixture_results_modified']is False and schema['product_or_frozen4_inputs_changed']is False
for key in ['original_failed_audit','actual_current_selected_audit','actual_public_canonical_contract_process','actual_public_canonical_contract','original_validator','current_public_validator','actual_public_contract_reader','original_failure_and_sources']:check_ref(schema[key])
assert read(check_ref(schema['original_failed_audit']))['actual_observed_exit']==1
assert read(check_ref(schema['actual_current_selected_audit']))['actual_observed_exit']==0
assert read(check_ref(schema['actual_public_canonical_contract_process']))['actual_observed_exit']==0
assert check_ref(schema['current_public_validator']).read_bytes()==(R/'.cache/full425-post-attempt4/seal_summary425.py').read_bytes()
for stage,path,key in [('baseline3',D/'baseline3-readonly-audit-process','reader_source_sha256'),('selected4',D/'selected-repair4-audit-process-attempt2','audit_source_sha256')]:
 process=read(path/'process.json');auditor=baseline if stage=='baseline3'else repair
 assert process['passed']and process['actual_observed_exit']==0 and process['source_sha256_before']==process['source_sha256_after']
 assert sha(path/'auditor-source.py')==auditor[key]
 expected=old if stage=='baseline3'else data;union={**expected['source_sha256'],**expected['supplemental_public_inputs_sha256']}
 assert all(union[n]==h for n,h in process['source_sha256_after'].items())
 for key in ['actual_original_root_exit']if stage=='baseline3'else['actual_full3_root_exit']:assert auditor[key]==1
allowed={'tests/test_player_compact_389.py','tests/test_player_feature_416.py','rouge/player_feature_416_acceptance.py'}
for key in ['source_sha256','supplemental_public_inputs_sha256','legacy_native_source_sha256']:
 assert set(old[key])==set(data[key]);changed={n for n in old[key]if old[key][n]!=data[key][n]};assert changed<=allowed
 assert changed==set(repair['verification_only_changes'][key])
assert {n for n in old['source_sha256']if old['source_sha256'][n]!=data['source_sha256'][n]}==allowed
for key in ['selectors','p3_scripts','p3_script_options','p3_script_selected_paths','template_bundle_sha256','local_public_input_bindings','historical_manifest_bindings','canonical_local_public_input_bindings','canonical_local_public_input_sha256','legacy_external_additional_sha256','local_public_input_sha256','maintained_runner_sha256','cloud_selector_api_sha256','original_typed_auditor_sha256','previous_full_scope_receipt','previous_full_scope_receipt_sha256','new_installed_native_scripts','new_installed_selector_count','diagnostic_layout_modes']:assert old[key]==data[key],key
assert len(data['selectors'])==672 and len(data['p3_scripts'])==140
# Re-check all original archived bytes against their immutable manifests and
# retained actual outputs, without calling an old-source worktree guard.
spec=importlib.util.spec_from_file_location('composite425_archive_reader',R/'.cache/full425-post-attempt4/seal_summary425.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
prior=[]
for attempt in [1,3]:
 A=D/f'execution-attempt{attempt}';manifest=read(A/'archive-manifest.json');m.verify_archive(sha(A/'archive-manifest.json'),archive=A,base=R/f'.cache/full425-prepared/attempt-{attempt}',freeze=D/f'source-freeze-attempt{attempt}.json',attempt=attempt,freeze_sha=manifest['source_freeze_sha256'],activation_sha=manifest['activation_sha256'])
 assert manifest['actual_root_controller_exit']==1;prior.append({'actual_validation_attempt':attempt,'manifest':proof(A/'archive-manifest.json'),'actual_root_exit':1,'not_relabelled_PASS':True})
rejected=D/'execution-rejected-attempt2';rj=read(rejected/'manifest.json');assert rj['actual_root_exit']==1 and rj['actual_failed_guard_before_child_launch']and rj['any_test_component_passed_claimed']is False
for row in rj['files']:p=check_ref(row);assert p.resolve().is_relative_to(rejected.resolve())and p.stat().st_size==row['bytes']
assert read(rejected/'root-launch/controller-process.json')['actual_observed_exit']==1 and not(rejected/'namespace/offline/actual').exists();prior.append({'actual_validation_attempt':2,'manifest':proof(rejected/'manifest.json'),'actual_root_exit':1,'kind':'pre_child_rejection_not_a_full_test_execution','not_relabelled_PASS':True});prior.sort(key=lambda row:row['actual_validation_attempt'])
selected=D/'selected-repair4';selected_manifest=read(selected/'archive-manifest.json');assert selected_manifest['actual_selected_root_exit']==0 and selected_manifest['full_available_scope_PASS_claimed_by_archive']is False
for name,row in selected_manifest['files'].items():
 p=selected/name;assert p.is_file()and not p.is_symlink()and p.resolve().is_relative_to(selected.resolve())and sha(p)==row['sha256']and p.stat().st_size==row['bytes']and p.read_bytes()==Path(row['origin']).read_bytes()
assert set(p.relative_to(selected).as_posix()for p in selected.rglob('*')if p.is_file())==set(selected_manifest['files'])|{'archive-manifest.json'}
selected_process=read(D/'selected-repair4-process/process.json');assert selected_process['passed']and selected_process['actual_observed_exit']==0
assert repair['actual_selected_root_exit']==0 and repair['all_product_code_and_game_data_identical_to_full3']
for row in [repair['baseline3_evidence_audit'],repair['baseline3_auditor_process'],repair['selected_archive'],repair['current_source_freeze']]:check_ref(row)
for qpa in repair['actual_repaired_modules_by_backend']:
 process=read(check_ref(qpa['process']));unit=read(check_ref(qpa['actual_receipt']));assert process['actual_observed_exit']==0 and process['passed']and unit['passed']and unit['tests_run']==5
failed={row['test']for row in baseline['original_offline']['failed_cases']};assert failed=={'tests.test_player_compact_389.Compact.test_compact_facts_pin_and_no_note_without_context','tests.test_player_feature_416.BindingTests.test_owned_native_identity_and_geometry'}
windows=next(row for row in repair['actual_repaired_modules_by_backend']if row['qpa']=='windows');actual=read(check_ref(windows['actual_receipt']));assert failed<=set(actual['selectors'])and actual['skips']==actual['errors']==actual['failures']==[]
assert repair['original_native_identity_unit_actual_execution']['was_successful']and repair['original_native_identity_unit_actual_execution']['skips']==[]
visual_path=D/'root-visual-review-composite.json';visual=read(visual_path);assert visual['all_reviewed']and visual['pending_actual_root_view']==[] and visual['whole_full4_run_claimed']is False
pngs={str((selected/name).relative_to(R)).replace('\\','/')for name in selected_manifest['files']if len(Path(name).parts)==3 and Path(name).parts[1]=='actual'and name.endswith('.png')};assert{row['file']for row in visual['images']}==pngs
for row in visual['images']:
 assert row['reviewed']and sha(R/row['file'])==row['sha256']
 if row['method']=='direct_view':
  p=check_ref(row['review_proof']);doc=read(p);assert doc['actor']=='/root'and not doc['blocking_visual_issues']and doc['recorded_only_after_actual_tool_viewing']and doc['viewing_performed_by_this_script']is False
  assert any(r['file']==row['file']and r['sha256']==row['sha256']and r['actual_view_image_called']and r['actual_pixels_visually_reviewed']for r in doc['images'])
 else:
  assert row['method']in ['previous_exact_bytes','contact_sheet'];registry=read(check_ref(row['registry_proof']));entry=registry['entries'][row['sha256']];origin=entry['review_origins'][row['registry_proof']['origin_index']]
  assert sha(R/origin['original_png'])==row['sha256']and(R/origin['original_png']).read_bytes()==(R/row['file']).read_bytes();check_ref({'file':origin['leaf_proof'],'sha256':origin['leaf_proof_sha256']})
  m.verify_registry_chain(entry,origin,(R/row['file']).read_bytes(),{})
bv=baseline['baseline_visual'];assert bv['all_reviewed']and sha(R/bv['file'])==bv['sha256']and visual['original_failed_full3_visual']==bv
current=repair['current30_and_independent29'];typed=repair['legacy_complete_original_typed_scope'];assert current['available_original_workflows_passed']and typed['actual_complete_scope']['saved_rows']==52 and typed['actual_complete_scope']['current_revised_assertions']==862
reused={k:v for k,v in baseline['actual_component_proofs'].items()if k.startswith('p3_')and k not in ['p3_416','p3_425']};assert len(reused)==138
assert set(reused)|{'p3_416','p3_425'}==set(data['p3_scripts'])
for detail in reused.values():
 for key in ['step','controller_process','actual_exit','exit_origin','supervisor','closure','receipt']:check_ref(detail[key])
 assert detail['actual_child_exit']==detail['actual_supervisor_exit']==detail['actual_fixture_exit']==0
bound(launch['parent'],launch['freeze_sha256'],launch['activation_sha256'])
result={'after_section':425,'kind':'COMPLETE_ORIGINAL_SCOPE_PLUS_ACTUAL_SELECTED_REPAIRS_WITH_STRICT_VERIFICATION_ONLY_SOURCE_EQUIVALENCE','checked_at_UTC':datetime.now(timezone.utc).isoformat(),'available_checks_passed':True,'complete_repository_validation':False,'scope_not_reduced':True,'P3_complete':False,'P2_complete':False,'P1_complete':False,'actual_validation_attempt':4,'actual_root_controller_exit':1,'actual_full_root_attempt':3,'actual_selected_repair_controller_exit':0,'validation_composition':'Complete actual full3 scope, unchanged product/data evidence reused, repaired verification premises and original full legacy+typed/current30/current29/native416/native425 re-executed under source4. Both repaired unit modules executed offscreen and on genuine Windows. Original full3 root1 and all failed originals remain unchanged.','single_available_scope_execution_all_green':False,'all_final_component_source_maps_share_one_freeze':False,'all_product_and_game_data_bytes_equivalent_across_composition':True,'verification_only_source_changes':repair['verification_only_changes'],'composition_verified':True,'current_worktree_validation_authority':True,'source_freeze':'verification/full-425/source-freeze-attempt4.json','source_freeze_sha256':launch['freeze_sha256'],'activation_sha256':launch['activation_sha256'],'source_files':len(data['source_sha256']),'maintained_selectors':len(data['selectors']),'native_supplements':len(data['p3_scripts']),'actual_required_component_positions':145,'tested_worktree_parent_commit':launch['parent'],'source_drift':[],'full_original_offline_execution':baseline['original_offline'],'offline_repair_actual_executions':repair['actual_repaired_modules_by_backend'],'offline_original_failed_results_not_edited':True,'original_full3_assessment':proof(D/'baseline3-readonly-audit.json'),'actual_selected_repair_assessment':proof(D/'selected-repair4-audit.json'),'actual_selected_repair_process':proof(D/'selected-repair4-process/process.json'),'archive_manifests_sha256':{'verification/full-425/execution-attempt3/archive-manifest.json':sha(D/'execution-attempt3/archive-manifest.json'),'verification/full-425/selected-repair4/archive-manifest.json':sha(selected/'archive-manifest.json')},'earlier_actual_attempts_preserved':prior,'actual_reused_native_component_proofs':reused,'actual_selected_component_proofs':repair['actual_selected_component_proofs'],'legacy_window':typed,'current_window':current,'functional425_necessary_and_native':repair['functional425_necessary_and_native'],'root_PNG_visual_review':{'path':visual_path.relative_to(R).as_posix(),'sha256':sha(visual_path),'baseline':bv,'selected_images':len(visual['images']),'all_reviewed':True,'appearance_only':True,'actual_new_root_calls':visual['actual_new_root_view_image_calls']},'actual_layout_scope_baseline':baseline['actual_layout_scope_assessment'],'native_current_windows_gui_verified':True,'native_windows_game_chat_verified':False,'historical_original_Windows_verified':False,'all_tests_executed_on_original_local_Windows':True,'cloud_test_execution_started':False,'unavailable_scopes':['Original actual unavailable and historical skip records are preserved; no skip counts as a passed test.','Original Linux/WSL/Wine, private samples and actual game/chat remain unverified.']+(['Original30 exact WinError1314 remains unavailable.']if current['original_symlink_prerequisite_unavailable']else[]),'postprocessing_schema_repair':proof(schema_path),'summary_sealer':proof(Path(__file__)),'no_tests_or_windows_run_by_summary_sealer':True,'current_wrap_up_threshold_percent':15}
out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'summary':proof(out),'available_checks_passed':True,'single_all_green_execution':False,'original_full_root_exit':1,'actual_selected_repair_exit':0,'native_supplements_covered':140,'scope_not_reduced':True}))
