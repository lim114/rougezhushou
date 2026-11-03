"""Seal actual local full320 only after all original jobs, source and PNG review."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.cache/full320-attempt2-prep'
sys.path.insert(0,str(BASE))
from full320_common import bound
FROZEN='954012182a0f700e504ae4349f8b5847b4ab2ced6bb2ab5bce3abec3ee98cb51'
ACTIVATION='796d46e88869e1854e938d61a8ff8d7ec1bb80ff8b64b23b186d4b7be3bbe596'
PARENT='e320b50d43f713c50941a29ffc1e89c2311761dc'
def read(n):return json.loads((ROOT/n).read_bytes())
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
def ref(n):return {'path':n,'sha256':sha(n)}
def archive(attempt):
 name=f'verification/full-320/execution-attempt{attempt}/archive-manifest.json';v=read(name)
 assert v['actual_validation_attempt']==attempt and v['section']==320
 assert v['required_component_positions']==40 and v['all_original_ordered_components_retained']
 assert v['all_executed_retained_Popen_and_assigned_jobs_terminal'] and v['all_actual_root_identifiers_not_live_at_archive']
 for n,pin in v['files'].items():
  p=ROOT/Path(name).parent/n;assert p.resolve().is_relative_to(ROOT)and p.is_file()and not p.is_symlink()
  assert sha256(p.read_bytes()).hexdigest()==pin['sha256']and p.stat().st_size==pin['bytes']
 return v,ref(name)
def main():
 freeze,activation=bound(PARENT,FROZEN,ACTIVATION)
 first,first_ref=archive(1);second,second_ref=archive(2)
 assert first['actual_root_controller_exit']==1 and not first['automated_available_scope_passed']
 assert second['actual_root_controller_exit']==1 and second['automated_available_scope_passed']is False
 joint=read('verification/full-320/current-scope-review.json');assert joint['available_checks_passed']and joint['scope_not_reduced']and joint['all40_original_components_preserved']and joint['source_freeze_sha256']==FROZEN and joint['same_canonical_or_product_code_changed_for_rechecks']is False
 recheck_archive=read('verification/full-320/rechecks-source-freeze2-1/archive-manifest.json');assert recheck_archive['actual_root_controller_exit']==0 and recheck_archive['all_recheck_actual_child_and_supervisor_exit0']
 for n,pin in recheck_archive['files'].items():
  path=ROOT/'verification/full-320/rechecks-source-freeze2-1'/n;assert sha256(path.read_bytes()).hexdigest()==pin['sha256']and path.stat().st_size==pin['bytes']
 folder='verification/full-320/execution-attempt2/'
 c=read(folder+'orchestration.json');review=read(folder+'automated-scope-review.json')
 expected=['offline','legacy','legacy_typed','current30','current29',*freeze['p3_scripts']]
 assert len(expected)==40 and len(freeze['p3_scripts'])==35 and len(freeze['selectors'])==509
 assert c['required_components']==expected==[r['name']for r in c['steps']]
 assert c['status']=='all_required_components_terminal'and c['automated_available_scope_passed']is False
 assert review['automated_available_scope_passed']is False and review['scope_not_reduced']and {v['component']for v in review['review_failures']}=={'p3_298','p3_311','p3_312'}and review['root_freeze_sha256']==FROZEN
 actual={}
 for row in c['steps']:
  n=row['name'];assert row['status']=='terminal'and row['terminal_supervisor_and_job_verified']and not row['timed_out']and row['owned_job_no_live_execution_verified']
  if n in('current30','p3_298','p3_311','p3_312'):assert row['child_primary_exit']==row['supervisor_exit']==1
  else:assert row['child_primary_exit']==row['supervisor_exit']==0
  if n=='legacy_typed':continue
  v=read(folder+n+'/actual/full320-source-closure.json');assert v['root_freeze_sha256']==FROZEN and v['activation_sha256']==ACTIVATION and v['source_guard_exception_after']is None and v['qt_cleanup_error']is None
  rawname=folder+n+'/actual/'+v['actual_receipt_file'];assert sha(rawname)==v['actual_receipt_sha256'];raw=read(rawname);actual[n]=raw
  if n not in('current30','p3_298','p3_311','p3_312'):assert v['component_automated_passed']and v['actual_fixture_exit']==0 and v['actual_receipt_passed']
 for n,path in joint['current_receipt_overrides'].items():
  raw=read(path);assert raw['passed']and raw['failure']is None;actual[n]=raw
 failure=actual['current30']['failure'];assert failure['type']=='OSError'and'[WinError 1314]'in failure['message']and'diagnostic.symlink_to(public_target.name)'in failure['traceback']and'os.symlink('in failure['traceback']
 assert review['current30_original_actual_symlink_prerequisite_unavailable']and actual['current29']['passed']
 typed=read(folder+'legacy/independent-saved-readback-audit.json');assert typed['passed']
 visual_name='verification/full-320/root-second-visual-review.json';visual=read(visual_name)
 images={folder+n:pin['sha256']for n,pin in second['files'].items()if n.endswith('.png')and len(Path(n).parts)==3 and Path(n).parts[1]=='actual'}
 images.update({'verification/full-320/rechecks-source-freeze2-1/'+n:pin['sha256']for n,pin in recheck_archive['files'].items()if n.endswith('.png')and len(Path(n).parts)==3 and Path(n).parts[1]=='actual'})
 assert visual['also_reviewed_recheck_archive']['sha256']==sha('verification/full-320/rechecks-source-freeze2-1/archive-manifest.json')
 assert visual['all_reviewed']and visual['actual_validation_attempt']==2 and visual['source_freeze_sha256']==FROZEN and visual['archive_manifest_sha256']==second_ref['sha256']
 assert {r['file']:r['sha256']for r in visual['images']}==images and len(visual['images'])==len(images)
 for row in visual['images']:
  assert row['reviewed']and sha(row['file'])==row['sha256']and row['method']in('direct_view','previous_root_same_bytes','same_byte_reuse','contact_sheet_review')
  if row['method']=='previous_root_same_bytes':assert sha(row['reviewed_file'])==row['sha256']and sha(row['review_receipt'])==row['review_receipt_sha256']
  elif row['method']=='same_byte_reuse':assert any(r['file']==row['representative_file']and r['sha256']==row['sha256']and r['method']!='same_byte_reuse'for r in visual['images'])
  elif row['method']=='contact_sheet_review':
   sheet=read(row['contact_sheet_receipt']);assert sheet['root_viewed']and sha(sheet['file'])==sheet['sha256']and any(r['file']==row['file']and r['sha256']==row['sha256']for r in sheet['members'])
 offline=actual['offline'];old=read('verification/full-305/source-freeze-attempt2.json');assert freeze['selectors'][:len(old['selectors'])]==old['selectors']
 summary={'after_section':320,'kind':'functional_section_full_validation','checked_at_UTC':datetime.now(timezone.utc).isoformat(),'available_checks_passed':True,'complete_repository_validation':False,'scope_not_reduced':True,'P3_complete':False,'P2_complete':False,'P1_complete':False,'actual_validation_attempt':2,'single_execution_all_green':False,'all_final_component_source_maps_share_one_freeze':True,'current_worktree_validation_authority':True,'source_files':len(freeze['source_sha256']),'maintained_selectors':len(freeze['selectors']),'supplemental_public_input_files':len(freeze['supplemental_public_inputs_sha256']),'source_freeze':'verification/full-320/source-freeze-attempt2.json','source_freeze_sha256':FROZEN,'activation_sha256':ACTIVATION,'tested_worktree_parent_commit':PARENT,'source_drift':[],'native_current_windows_gui_verified':True,'native_windows_game_chat_verified':False,'historical_original_Windows_verified':False,'all_tests_executed_on_original_local_Windows':True,'cloud_test_execution_started':False,'archive_manifests_sha256':{first_ref['path']:first_ref['sha256'],second_ref['path']:second_ref['sha256']},'root_second_PNG_visual_review':{**ref(visual_name),'images':len(images),'appearance_only_not_unpictured_semantics':True},'offline_windows':{k:offline[k]for k in('tests_run','tests_passed','historical_or_declared_skips','failures','errors','unavailable_records','unavailable_parent_count','qt_shutdown','qt_shutdown_error')},'actual_offline_process_exit':0,'legacy_window':review['component_details']['legacy'],'current_window':{'maintained_scope':30,'actual_full30_attempt_preserved':True,'full30_actual_exit':1,'current29_actual_exit':0,'available_original_workflows_passed':len(actual['current29']['checks']),'original_symlink_operation_passed':False,'unavailable_reason':'Original native Path.symlink_to/os.symlink WinError1314; not passed.'},'p3_supplementary_windows':{n:joint['component_details'][n]for n in freeze['p3_scripts']},'original_complete_scope_review':ref('verification/full-320/current-scope-review.json'),'original_failed_second_full_review':ref(folder+'automated-scope-review.json'),'same_source_recheck_archive':ref('verification/full-320/rechecks-source-freeze2-1/archive-manifest.json'),'second_raw_root_exit':1,'second_full_execution_without_rechecks_passed':False,'311_original120s_budget_passed':False,'311_profile300s_complete_workflow_passed':True,'311_profile_is_not_normal_latency_benchmark':True,'repeated_refresh_performance_issue_closed':False,'functional320_necessary_and_native':freeze['functional_validation'],'first_failed_attempt_preserved':{'archive':first_ref,'actual_root_exit':1,'passed':False,'review_failures':read('verification/full-320/execution-attempt1/automated-scope-review.json')['review_failures']},'unavailable_scopes':['Original native symlink1314 is unavailable, not passed.','Original Linux/WSL/Wine and historical private Windows samples are unverified.','No live game sampling, game operation or chat request in validation.'],'assigned_owned_jobs_empty_not_global_descendant_enumeration':True,'current_wrap_up_threshold_percent':15}
 bound(PARENT,FROZEN,ACTIVATION)
 p=ROOT/'verification/full-320/summary.json';assert not p.exists();p.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf8');(ROOT/'verification/full-320/execution-summary320.py').write_bytes(Path(__file__).read_bytes());(ROOT/'verification/full-320/execution-consolidation.py').write_bytes((ROOT/'.cache/consolidate320.py').read_bytes());print(json.dumps({'available_scope_passed':True,'tests_run':offline['tests_run'],'supplements':35,'images':len(images),'scope_not_reduced':True}))
if __name__=='__main__':main()
