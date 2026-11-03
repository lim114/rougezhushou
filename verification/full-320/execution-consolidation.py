"""Same immutable source: complete attempt2 plus exact full-scope timeout rechecks."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.cache/full320-attempt2-prep';HERE=ROOT/'.cache/full320-recheck298';sys.path.insert(0,str(BASE))
from full320_common import bound,sha,write_new,now,PYTHON
from review_results320 import terminal,closure,source_stable
PARENT='e320b50d43f713c50941a29ffc1e89c2311761dc';FROZEN='954012182a0f700e504ae4349f8b5847b4ab2ced6bb2ab5bce3abec3ee98cb51';ACT='796d46e88869e1854e938d61a8ff8d7ec1bb80ff8b64b23b186d4b7be3bbe596'
def read(p):return json.loads(p.read_bytes())
def archive(folder):
 manifest=read(folder/'archive-manifest.json')
 for name,pin in manifest['files'].items():
  p=folder/name;assert p.is_file()and not p.is_symlink()and p.resolve().is_relative_to(ROOT)
  assert sha(p)==pin['sha256']and p.stat().st_size==pin['bytes']
 return manifest

def main():
 data,_=bound(PARENT,FROZEN,ACT);full=ROOT/'verification/full-320/execution-attempt2';extra=ROOT/'verification/full-320/rechecks-source-freeze2-1';a=archive(full);b=archive(extra)
 assert a['source_freeze_sha256']==b['source_freeze_sha256']==FROZEN and a['actual_root_controller_exit']==1 and b['actual_root_controller_exit']==0 and b['all_recheck_actual_child_and_supervisor_exit0']
 original=read(full/'automated-scope-review.json');modes=['p3_298','p3_311','p3_312'];assert{r['component']for r in original['review_failures']}==set(modes)and not original['automated_available_scope_passed']and original['scope_not_reduced']
 control=read(full/'orchestration.json');expected=['offline','legacy','legacy_typed','current30','current29',*data['p3_scripts']];assert len(expected)==40 and control['required_components']==expected==[r['name']for r in control['steps']]
 assert {r['name']for r in control['steps']if r['child_primary_exit']!=0}=={'current30',*modes}
 assert all(r['status']=='terminal'and r['terminal_supervisor_and_job_verified']and r['owned_job_no_live_execution_verified']and not r['timed_out']for r in control['steps'])
 for mode in modes:
  raw=read(full/mode/'actual/window.json');assert raw['passed']is False and raw['failure']['type']=='TimeoutError'
 for n in data['p3_scripts']:
  if n not in modes:assert n in original['component_details']
 invocation=read(full/'legacy/full320-typed-audit-invocation.json');assert invocation['passed']and invocation['actual_auditor_exit']==0
 assert read(full/'legacy/independent-saved-readback-audit.json')['passed']and original['current30_original_actual_symlink_prerequisite_unavailable']
 observed=read(extra/'recheck-observed.json');assert [v['name']for v in observed['steps']]==modes and observed['all_primary_and_supervisor_exit0']
 details=dict(original['component_details']);sources={};targets={};namespace=Path(read(HERE/'once.json')['actual_namespace']);shared=['--expected-parent-commit',PARENT,'--freeze-sha256',FROZEN,'--activation-sha256',ACT]
 root_record=read(extra/'root-launch/controller-process.json');assert root_record['status']=='completed'and root_record['actual_observed_exit']==0 and root_record['exit_observed_directly_from_retained_popen']and root_record['exit_inferred_from_output_json']is False
 for name,pin in read(extra/'root-launch/source-pins.json').items():assert sha(HERE/name)==pin==sha(extra/'execution-tools'/name)
 for mode in modes:
  folder=extra/mode;child=[str(PYTHON),'-B','-X','utf8',str(HERE/'component_child320_recheck.py'),'--mode',mode,'--out',str(namespace/mode/'actual'),*shared]
  sup=terminal(folder,child);target=ROOT/data['p3_scripts'][mode];duration=300000 if mode=='p3_311'else 120000;argv=[str(target),'--receipt',str(namespace/mode/'actual/window.json'),'--visible-ms',str(duration)]
  raw,close=closure(folder,mode,FROZEN,ACT,target,argv)
  selected={n:({**data['source_sha256'],**data['supplemental_public_inputs_sha256']})[n]for n in data['p3_script_selected_paths'][mode]};source_stable(raw,selected)
  assert raw['passed']and raw['qpa']=='windows'and raw['qt_exit_code']==0 and raw['verification_window_closed']and type(raw['process_id'])is int
  assert raw['state_paths_replaced_before_constructor']==['ROOT','SETTINGS','OPERATOR_STATE','RUN_STATE']and raw['temporary_state_root']and raw['private_state_read_copied_or_restored']is False
  assert raw['game_captures']==0 and raw['game_operated']is False and raw['chat_sent']is False
  counters=raw['external_operation_attempts'];assert len(counters)==8 and all(type(v)is int and v==0 for v in counters.values())
  oldpath=ROOT/'verification/full-320/execution-attempt1/p3_298/actual/window.json'if mode=='p3_298'else ROOT/f'verification/sections/{mode[3:]}-native-attempt1/actual/window.json'
  old=read(oldpath);assert old['passed']and set(raw['checks'])==set(old['checks'])and raw['successful_assertion_executions_including_repeated_guards']>=old['successful_assertion_executions_including_repeated_guards']
  if mode=='p3_298':
   assert len(raw['main_floor_observations'])==36 and len(raw['same_scope_refresh_observations'])==3 and len(raw['source_negative_fixtures'])==1
  else:
   assert len(raw['actual_entry_overviews'])==3 and len(raw['same_identity_refresh_observations'])==6 and len(raw['actual_topic_readings'])==len(old['actual_topic_readings'])and raw['source_negative_fixture']['restored_exact_bytes']
  details[mode]={'receipt_sha256':close['actual_receipt_sha256'],'actual_fixture_pid':raw['process_id'],'owned_launcher_pid':sup['pid'],'checks':raw['unique_checks'],'screenshots':raw['screenshots'],'source_count':len(selected),'current_receipt':(folder/'actual/window.json').relative_to(ROOT).as_posix(),'recheck_same_canonical_source':True,'requested_visible_ms':duration,'311_profile_not_normal_latency_benchmark':mode=='p3_311'}
  sources[mode]=(folder/'actual/window.json').relative_to(ROOT).as_posix();targets[mode]={'target':data['p3_scripts'][mode],'source_sha256':sha(target),'all_original_assertion_labels_retained':True,'complete_assertion_executions':raw['successful_assertion_executions_including_repeated_guards']}
 assert all(n in details for n in data['p3_scripts'])and len(data['p3_scripts'])==35 and len(data['selectors'])==509
 result={'section':320,'kind':'COMPLETE_AVAILABLE_FUNCTIONAL_SCOPE_SAME_FROZEN_SOURCE_WITH_THREE_RECHECKS','available_checks_passed':True,'scope_not_reduced':True,'all40_original_components_preserved':True,'all_final_component_source_maps_share_one_freeze':True,'same_canonical_or_product_code_changed_for_rechecks':False,'full_original_root_exit':1,'original_full_execution_passed':False,'raw_full_review':'verification/full-320/execution-attempt2/automated-scope-review.json','raw_full_review_failures_retained':original['review_failures'],'recheck_archive':'verification/full-320/rechecks-source-freeze2-1/archive-manifest.json','all_recheck_actual_child_and_supervisor_exit0':True,'current_receipt_overrides':sources,'source_freeze_sha256':FROZEN,'activation_sha256':ACT,'component_details':details,'recheck_targets_and_complete_scopes':targets,'single_execution_all_green':False,'311_original120s_timeout_passed':False,'311_profile300s_complete_workflow_passed':True,'311_normal_unprofiled_latency_not_proved':True,'performance_issue_not_closed':True,'P3_complete':False,'complete_repository_validation':False,'private_contents_copied_or_restored':False,'game_operated':False,'chat_sent':False,'sealed_at':now()}
 bound(PARENT,FROZEN,ACT);write_new(ROOT/'verification/full-320/current-scope-review.json',result);print(json.dumps({'all_available_functional_scope_passed':True,'original40_retained':True,'rechecks':modes,'same_source_freeze':FROZEN,'performance_issue_closed':False}))
if __name__=='__main__':main()
