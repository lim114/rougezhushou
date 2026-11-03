from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.cache/full335-recheck2'))
from common import guard, FREEZE, PIN
def read(n):return json.loads((ROOT/n).read_bytes())
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
def ref(n):return {'path':n,'sha256':sha(n)}
final=guard();original=read('verification/full-335/source-freeze-attempt1.json')
prefix='verification/full-335/execution-attempt1/'
rp='verification/full-335/binding-recheck2-execution/'
archives=[prefix+'archive-manifest.json',rp+'archive-manifest.json']
for manifest in archives:
    archive=read(manifest);base=str(Path(manifest).parent).replace('\\','/')+'/'
    for n,pin in archive['files'].items():
        assert sha(base+n)==pin['sha256'] and (ROOT/(base+n)).stat().st_size==pin['bytes'],base+n
o=read(prefix+'orchestration.json');review=read(prefix+'automated-scope-review.json')
expected=['offline','legacy','legacy_typed','current30','current29',*original['p3_scripts']]
assert len(expected)==55 and o['required_components']==expected==[r['name']for r in o['steps']]
assert o['status']=='all_required_components_terminal'
assert read(prefix+'root-launch/controller-process.json')['actual_observed_exit']==1
assert {r['component']for r in review['review_failures']}=={'p3_304','p3_305'}
assert read(rp+'root-launch/controller-process.json')['actual_observed_exit']==0
assert read(rp+'orchestration.json')['passed']
raw={};details=dict(review['component_details'])
for row in o['steps']:
    n=row['name']
    assert row['status']=='terminal' and row['terminal_supervisor_and_job_verified'] and row['owned_job_no_live_execution_verified'] and not row['timed_out']
    if n=='legacy_typed':continue
    closure=read(prefix+n+'/actual/full335-source-closure.json')
    assert closure['root_freeze_sha256']==sha('verification/full-335/source-freeze-attempt1.json')
    assert closure['source_guard_exception_after']is None and closure['qt_cleanup_error']is None
    if n in ('p3_304','p3_305'):
        assert row['child_primary_exit']==1 and closure['fixture_exception']['type']=='ValueError' and not closure['actual_receipt_exists']
        c=read(rp+n+'/actual/recheck-source-closure.json');w=read(rp+n+'/actual/window.json')
        assert c['source_freeze_sha256']==PIN and c['component_automated_passed'] and c['actual_fixture_exit']==0
        assert not c['fixture_exception'] and not c['source_guard_exception_after'] and not c['qt_cleanup_error']
        assert c['actual_receipt_sha256']==sha(rp+n+'/actual/window.json') and w['passed'] and w['qpa']=='windows' and w['qt_exit_code']==0 and w['verification_window_closed']
        assert w['source_sha256_before']==w['source_sha256_after']
        for name,h in w['source_sha256_after'].items():assert sha(name)==h,name
        assert all(v==0 for v in w['external_operation_attempts'].values())
        details[n]={'passed':True,'source':ref(rp+n+'/actual/window.json'),'unique_checks':w['unique_checks'],'actual_fixture_exit':0,'complete_original_assertions_retained':True,'source_binding_repaired_only':True}
        raw[n]=w
        continue
    receipt=prefix+n+'/actual/'+closure['actual_receipt_file']
    assert sha(receipt)==closure['actual_receipt_sha256'];raw[n]=read(receipt)
    if n!='current30':assert row['child_primary_exit']==row['supervisor_exit']==0 and closure['component_automated_passed'] and closure['actual_fixture_exit']==0
offline=raw['offline'];assert offline['source_sha256']==original['source_sha256'] and offline['selectors']==final['selectors']==original['selectors'] and offline['failures']==offline['errors']==0 and offline['source_drift']==[] and offline['available_checks_passed']
old=read('verification/full-320/source-freeze-attempt2.json')
assert len(final['selectors'])==539 and final['selectors'][:len(old['selectors'])]==old['selectors'] and len(final['p3_scripts'])==50 and list(final['p3_scripts'])[:len(old['p3_scripts'])]==list(old['p3_scripts'])
typed=read(prefix+'legacy/independent-saved-readback-audit.json')
assert typed['passed'] and typed['saved_rows']==52 and typed['complete_runtime_checks']==4283 and typed['current_revised_assertions']==862
c30=raw['current30'];assert raw['current29']['passed'] and len(raw['current29']['checks'])==29
assert not c30['passed'] and c30['failure']['type']=='OSError' and '[WinError 1314]'in c30['failure']['message'] and 'diagnostic.symlink_to(public_target.name)'in c30['failure']['traceback'] and 'os.symlink('in c30['failure']['traceback'] and review['current30_original_actual_symlink_prerequisite_unavailable']
visual_name='verification/full-335/root-visual-review.json';visual=read(visual_name);images={}
for manifest in archives:
    base=str(Path(manifest).parent).replace('\\','/')+'/'
    for n,pin in read(manifest)['files'].items():
        if n.endswith('.png')and len(Path(n).parts)==3 and Path(n).parts[1]=='actual':images[base+n]=pin['sha256']
assert len(images)==303 and visual['all_reviewed'] and visual['final_source_freeze_sha256']==PIN and {r['file']:r['sha256']for r in visual['images']}==images
for r in visual['images']:
    assert r['reviewed'] and sha(r['file'])==r['sha256']
    if r['method']=='previous_root_same_bytes':assert sha(r['reviewed_file'])==r['sha256'] and sha(r['review_receipt'])==r['review_receipt_sha256']
    elif r['method']=='same_byte_reuse':assert any(x['file']==r['representative_file'] and x['sha256']==r['sha256'] and x['method']!='same_byte_reuse'for x in visual['images'])
    elif r['method']=='contact_sheet_review':
        sheet=read(r['contact_sheet_receipt']);assert sheet['root_viewed'] and sha(sheet['file'])==sheet['sha256'] and any(x['file']==r['file']and x['sha256']==r['sha256']for x in sheet['members'])
    else:assert r['method']=='direct_view'
repair=read('verification/full-335/binding-repair/repair-scope.json')
assert not repair['production_changed'] and not repair['tests_selectors_changed'] and len(repair['files'])==2 and all(x['complete_AST_outside_binding_and_one_parser_option_identical']for x in repair['files'])
summary={'after_section':335,'kind':'functional_section_full_validation','checked_at_UTC':datetime.now(timezone.utc).isoformat(),'available_checks_passed':True,'complete_repository_validation':False,'scope_not_reduced':True,'P3_complete':False,'P2_complete':False,'P1_complete':False,'actual_validation_attempt':1,'single_available_scope_execution_all_green':False,'original_full_actual_root_exit':1,'original_full_failed_components':['p3_304','p3_305'],'binding_only_recheck_actual_root_exit':0,'all_final_component_source_maps_share_one_freeze':False,'current_worktree_validation_authority':True,'source_files':len(final['source_sha256']),'maintained_selectors':539,'supplemental_public_input_files':len(final['supplemental_public_inputs_sha256']),'source_freeze':FREEZE,'source_freeze_sha256':PIN,'original_full_source_freeze':ref('verification/full-335/source-freeze-attempt1.json'),'tested_worktree_parent_commit':original['parent_commit'],'source_drift':[],'maintenance_reconciliation':{**ref('verification/full-335/binding-repair/repair-scope.json'),'only_changed_files':final['only_changed_source_files'],'no_production_data_models_tests_or_assertions_changed':True,'unaffected_original_complete_checks_reused_not_rerun':True,'affected_two_native_workflows_reexecuted_completely':True,'first_recheck_preparation_failed_before_native_launch_preserved':True,'future_full_controller_must_pass_explicit_source_freeze_to_two_scripts':True},'native_current_windows_gui_verified':True,'native_windows_game_chat_verified':False,'historical_original_Windows_verified':False,'all_tests_executed_on_original_local_Windows':True,'cloud_test_execution_started':False,'archive_manifests_sha256':{n:sha(n)for n in archives},'root_PNG_visual_review':{**ref(visual_name),'images':303,'appearance_only_not_unpictured_semantics':True},'offline_windows':{k:offline[k]for k in('tests_run','tests_passed','historical_or_declared_skips','failures','errors','unavailable_records','unavailable_parent_count','qt_shutdown','qt_shutdown_error')},'actual_offline_process_exit':0,'legacy_window':details['legacy'],'current_window':{'maintained_scope':30,'actual_full30_attempt_preserved':True,'available_original_workflows_passed':29,'original_symlink_operation_passed':False,'unavailable_reason':'Actual Path.symlink_to/os.symlink WinError1314; original failure retained, not passed.'},'p3_supplementary_windows':{n:details[n]for n in final['p3_scripts']},'original_complete_scope_review':ref(prefix+'automated-scope-review.json'),'311_current300s_complete_workflow_profile_only':True,'311_original120s_budget_PASS_claimed':False,'311_previous120s_failure_retained':'verification/full-320/summary.json','311_profile_is_not_normal_latency_benchmark':True,'repeated_refresh_performance_issue_closed':False,'functional335_necessary_and_native':original['functional_validation'],'unavailable_scopes':['Original actual symlink1314 is unavailable, not passed.','Original Linux/WSL/Wine and historical private Windows samples remain unverified.','No live game sampling, operation or chat request.'],'current_wrap_up_threshold_percent':15}
guard();p=ROOT/'verification/full-335/summary.json';assert not p.exists();p.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+chr(10),encoding='utf8');(ROOT/'verification/full-335/execution-summary335.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({'available_scope_passed':True,'tests_run':offline['tests_run'],'passed':offline['tests_passed'],'original_full_exit':1,'native_binding_recheck_exit':0,'PNG_scope':303,'scope_not_reduced':True}))
