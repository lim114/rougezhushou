"""Explicit selected repair execution, not another whole full425 run.

The complete original scope is provided by the immutable full3 evidence plus
these dependency-directed repairs under proven product-source equivalence.
"""
from pathlib import Path
from hashlib import sha256
import argparse,json,runpy,sys,tempfile,uuid
R=Path(__file__).resolve().parents[1];B=R/'.cache/full425-prepared/attempt-4';sys.path[:0]=[str(B),str(R),str(R/'scripts')]
from full425_common import bound,native,sha,write_new,now,PYTHON
from run_full425_controller import observed_step
p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true')
for key in ['expected-parent-commit','freeze-sha256','activation-sha256']:p.add_argument('--'+key,required=True)
a=p.parse_args();assert a.execute;native();data,activation=bound(a.expected_parent_commit,a.freeze_sha256,a.activation_sha256)
tool_manifest=json.loads((R/'verification/full-425/selected-repair4-tools/manifest.json').read_bytes())
for row in tool_manifest['files']:
 assert sha(R/row['source'])==row['sha256']==sha(R/row['preserved'])
assert data['actual_validation_attempt']==4 and not(B/'full425-once.json').exists()and not(B/'root-launch').exists()
baseline=json.loads((R/'verification/full-425/baseline3-readonly-audit.json').read_bytes());assert baseline['passed']and not baseline['baseline_full_suite_passed']and baseline['actual_verified_native_supplements']==140
old=json.loads((R/'verification/full-425/source-freeze-attempt3.json').read_bytes());allowed={'tests/test_player_compact_389.py','tests/test_player_feature_416.py','rouge/player_feature_416_acceptance.py'}
for key in ['source_sha256','supplemental_public_inputs_sha256','legacy_native_source_sha256']:
 assert set(old[key])==set(data[key]);assert {name for name in old[key]if old[key][name]!=data[key][name]}<=allowed
assert {name for name in old['source_sha256']if old['source_sha256'][name]!=data['source_sha256'][name]}==allowed
for key in ['selectors','p3_scripts','p3_script_options','p3_script_selected_paths','template_bundle_sha256','local_public_input_bindings','historical_manifest_bindings','canonical_local_public_input_bindings','canonical_local_public_input_sha256','legacy_external_additional_sha256','local_public_input_sha256','maintained_runner_sha256','cloud_selector_api_sha256','original_typed_auditor_sha256','previous_full_scope_receipt','previous_full_scope_receipt_sha256','new_installed_native_scripts','new_installed_selector_count','diagnostic_layout_modes']:assert old[key]==data[key],key
C=Path(tempfile.gettempdir()).resolve()/('rouge-full425-selected-repair4-'+uuid.uuid4().hex);assert not C.exists()and not C.is_relative_to(R);C.mkdir()
once=R/'.cache/425-selected-repair4-once.json';write_new(once,{'section':425,'container':str(C),'kind':'SELECTED_REPAIR_NOT_WHOLE_FULL_EXECUTION','root_freeze_sha256':a.freeze_sha256,'activation_sha256':a.activation_sha256,'automatic_retry_allowed':False,'parent_commit':a.expected_parent_commit})
authority={'section':425,'kind':'SOURCE_EQUIVALENT_FULL_SCOPE_SELECTED_REPAIR_EXECUTION','actual_validation_attempt':4,'controller_fixture_pid':__import__('os').getpid(),'root':str(R),'parent_commit':a.expected_parent_commit,'root_freeze_sha256':a.freeze_sha256,'activation_sha256':a.activation_sha256,'controller_sha256':sha(Path(__file__)),'created_at':now(),'game_actions':0,'chat_requests':0,'private_state_copied':False,'whole_full4_run_claimed':False,'repair_tools_manifest_sha256':sha(R/'verification/full-425/selected-repair4-tools/manifest.json')}
write_new(C/'owned-execution.json',authority)
record={'section':425,'status':'running_selected_repairs','steps':[],'required_components':['legacy','legacy_typed','current30','current29','p3_416','p3_425'],'whole_full4_run_claimed':False};write_new(C/'orchestration.json',record)
from execution425 import checkpoint
shared=['--expected-parent-commit',a.expected_parent_commit,'--freeze-sha256',a.freeze_sha256,'--activation-sha256',a.activation_sha256]
for mode in ['legacy','current30','current29','p3_416','p3_425']:
 child=[str(PYTHON),'-B','-X','utf8',str(B/'component_child425.py'),'--mode',mode,'--out',str(C/mode/'actual'),*shared]
 row=observed_step(C,mode,child,3690 if mode=='legacy' else 1200,3780 if mode=='legacy' else 1290,a.expected_parent_commit,a.freeze_sha256,a.activation_sha256)
 record['steps'].append(row);checkpoint(C/'orchestration.json',record)
 if mode!='current30':assert row['child_primary_exit']==row['supervisor_exit']==0,mode
 if mode=='legacy':
  child=[str(PYTHON),'-B','-X','utf8',str(B/'readback_child425.py'),'--legacy-container',str(C/'legacy'),*shared]
  audit=observed_step(C,'legacy_typed',child,120,210,a.expected_parent_commit,a.freeze_sha256,a.activation_sha256);record['steps'].append(audit);checkpoint(C/'orchestration.json',record);assert audit['child_primary_exit']==audit['supervisor_exit']==0
base=runpy.run_path(str(R/'.cache/player_batch_pipeline.py'))
for qpa in ['offscreen','windows']:
 leaf=f'verification/full-425/selected-repair4-unit-{qpa}'
 base['execute']([str(PYTHON),'-B','-X','utf8',str(R/'.cache/repair425_unit_child.py'),'--qpa',qpa,'--receipt',str(R/leaf/'actual.json')],leaf)
bound(a.expected_parent_commit,a.freeze_sha256,a.activation_sha256)
for row in tool_manifest['files']:assert sha(R/row['source'])==row['sha256']==sha(R/row['preserved'])
record.update(status='all_selected_repairs_terminal',finished_at=now(),all_available_scope_PASS_not_claimed_here=True);checkpoint(C/'orchestration.json',record)
print(json.dumps({'selected_repairs_terminal':True,'complete_original_scope_still_requires_equivalence_audit_and_visual_review':True,'container':str(C)},ensure_ascii=False))
