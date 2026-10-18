"""Unexecuted draft: require actual sealed second305 and root visual evidence."""
import argparse
import importlib
import json
import re
import sys
from copy import deepcopy
from datetime import datetime, timezone, timedelta
from hashlib import sha256
from pathlib import Path, PurePosixPath

ROOT=Path(__file__).resolve().parents[2]
RUNTIME=ROOT/'.cache/p3-full305-attempt2-prep-revision2'
FREEZE='verification/full-305/source-freeze-attempt2.json'
FREEZE_SHA='4e2528deb25cbb166b74d74db8e0c3a6212ec6095a6d7b441bf62a911ade8086'
ACTIVATION_SHA='8623ee7ab99e9a198169e289f84c7db22266b60eb1bed2fba74422a57d430fda'
READY_SHA='ace93acba7ef077714dd2519b0b8008fdfab80c1a1cc8bf3235bc05a3c3a8bcd'
FIRST='verification/full-305/execution-attempt1/archive-manifest.json'
FIRST_SHA='e07579c8b1b1b4b2f7a47d21851133bd03b2c3bafcdf2ad3795cdc2e7a04bb9c'
SECOND='verification/full-305/execution-attempt2/archive-manifest.json'
SUMMARY='verification/full-305/summary.json'

def need(value,message):
    if not value:raise ValueError(message)
def sha(path):return sha256(path.read_bytes()).hexdigest()
def public(name):
    need(type(name)is str,'Explicit public relative path required.')
    rel=PurePosixPath(name)
    need(not rel.is_absolute()and'..'not in rel.parts and'\\'not in name and':'not in name and rel.as_posix()==name,'Unsafe public identity.')
    need(rel.parts[0]in('verification','rouge','scripts','tests','research')or name=='CORE_0.70_VERIFICATION.json','No private/document/cache input.')
    path=ROOT.joinpath(*rel.parts)
    need(path.is_file()and not path.is_symlink()and path.resolve().is_relative_to(ROOT),'Missing/linked public file: '+name)
    return path
def read(name):return json.loads(public(name).read_bytes())
def ref(name):return {'path':name,'sha256':sha(public(name))}
def exact_ref(value):
    need(type(value)is dict and sha(public(value['path']))==value['sha256'],'Actual public reference hash differs.')
    return read(value['path'])
def archive(name,expected_sha):
    path=public(name);need(sha(path)==expected_sha,'Exact actual archive SHA required: '+name)
    record=read(name);base=path.parent
    need(record.get('section')==305 and type(record.get('files'))is dict and record['files'],'Actual complete305 archive required.')
    for member,pin in record['files'].items():
        rel=PurePosixPath(member)
        need(not rel.is_absolute()and'..'not in rel.parts and'\\'not in member and':'not in member,'Unsafe archive member.')
        target=public((base/Path(member)).relative_to(ROOT).as_posix())
        need(sha(target)==pin['sha256']and target.stat().st_size==pin['bytes'],'Captured archive byte mismatch: '+member)
    return record
def prefix_paths(folder,manifest):
    components={'legacy','current30','current29',*('p3_'+str(n)for n in range(286,306))}
    return {(folder/name).relative_to(ROOT).as_posix():pin['sha256']for name,pin in manifest['files'].items()
        if len(PurePosixPath(name).parts)==3 and PurePosixPath(name).parts[0]in components
        and PurePosixPath(name).parts[1]=='actual'and name.lower().endswith('.png')}
def visual_review(name,archive_sha,expected_images):
    value=read(name)
    need(value.get('section')==305 and value.get('reviewer')=='root'and value.get('actual_validation_attempt')==2
        and value.get('all_reviewed')is True and value.get('source_freeze_sha256')==FREEZE_SHA
        and value.get('archive_manifest_sha256')==archive_sha,'Root visual record must bind the actual second305 freeze/archive.')
    rows=value.get('images');need(type(rows)is list and rows,'Actual root image list cannot be empty.')
    need(len(rows)==len({x['file']for x in rows})and{x['file']:x['sha256']for x in rows}==expected_images,'Root PNG review must exactly cover every actual second archived PNG path/hash.')
    by_name={x['file']:x for x in rows}
    for row in rows:
        need(row.get('reviewed')is True and sha(public(row['file']))==row['sha256'],'Unreviewed/changed actual PNG.')
        method=row.get('method');representative=row.get('representative_file')
        if method=='direct_view':
            need(representative==row['file']and row.get('representative_sha256')==row['sha256'],'Direct view must identify that exact actually viewed file.')
        elif method=='same_byte_reuse':
            other=by_name.get(representative)
            need(other is not None and other.get('method')=='direct_view'and other.get('reviewed')is True
                and row.get('representative_sha256')==other['sha256']==row['sha256'],'Same-byte reuse requires a direct-view representative within this actual second PNG list.')
        else:raise ValueError('Unknown visual method; never infer a view from HWND/assertions.')
    return {'receipt':name,'sha256':sha(public(name)),'images':len(rows),
        'directly_viewed_images':sum(x['method']=='direct_view'for x in rows),
        'same_current_execution_byte_reuses':sum(x['method']=='same_byte_reuse'for x in rows),
        'unique_current_execution_PNG_hashes':len(set(expected_images.values())),
        'representative_PNGs_do_not_prove_unpictured_rows_or_game_execution':True}
def actual_component(folder,name,freeze,activation_sha):
    raw_base=(folder/name).relative_to(ROOT).as_posix()
    row=read(raw_base+'/step.json');proc=read(raw_base+'/controller-process.json');sup=read(raw_base+'/supervisor.json')
    need(row.get('status')=='terminal'and row.get('terminal_supervisor_and_job_verified')is True
        and proc.get('status')=='completed'and proc.get('owned_popen_retained')is True
        and type(proc.get('actual_observed_popen_exit'))is int,'Original retained component Popen is not terminal: '+name)
    observed=int(public(raw_base+'/process.exit').read_text('ascii').strip())
    origin=read(raw_base+'/process-exit-origin.json')
    need(observed==proc['actual_observed_popen_exit']==sup['supervisor_exit']
        and origin.get('derived_from_supervisor_json')is False and origin.get('actual_observed_popen_exit')==observed
        and origin.get('process_exit_sha256')==sha(public(raw_base+'/process.exit')),'Original observed component exit provenance differs: '+name)
    need(sup.get('owned_handle_retained')is True and sup.get('owned_job_assigned')is True
        and sup.get('owned_job_no_live_execution_verified')is True and sup.get('timed_out')is False,'Assigned job not complete/non-timeout: '+name)
    if name!='current30':need(observed==sup.get('child_primary_exit')==0,'Actual component nonzero: '+name)
    if name=='legacy_typed':return None,sup
    close=read(raw_base+'/actual/full305-source-closure.json')
    need(close.get('root_freeze_sha256')==FREEZE_SHA and close.get('activation_sha256')==activation_sha
        and close.get('mode')==name and close.get('fixture_exception')is None
        and close.get('source_guard_exception_after')is None and close.get('qt_cleanup_error')is None,'Actual component source/Qt closure differs: '+name)
    filename=close['actual_receipt_file'];need(Path(filename).name==filename,'Flat actual receipt required.')
    actual=raw_base+'/actual/'+filename
    need(sha(public(actual))==close['actual_receipt_sha256'],'Original fixture JSON hash differs.')
    if name!='current30':need(close.get('actual_fixture_exit')==0 and close.get('actual_receipt_passed')is True
        and close.get('component_automated_passed')is True,'Actual fixture did not pass: '+name)
    return read(actual),sup

def build(args):
    need(sha(public(FREEZE))==FREEZE_SHA,'The actual second305 freeze is immutable.')
    freeze=read(FREEZE)
    need(sha(RUNTIME/'CONTROLLER_READY_ATTEMPT2_REV2.json')==READY_SHA,'Original sealed222 controller READY differs.')
    # Reuse the complete original before/after current-source/tool/bundle/local-
    # public guard. It is read-only and starts no tests/Qt/processes.
    sys.path.insert(0,str(RUNTIME));common=importlib.import_module('full305_common')
    need(Path(common.__file__).resolve()==(RUNTIME/'full305_common.py').resolve(),'Wrong original guard module.')
    data,_=common.bound(freeze['parent_commit'],FREEZE_SHA,ACTIVATION_SHA)
    need(data==freeze,'Original full guard returned a different freeze.')
    first=archive(FIRST,FIRST_SHA)
    first_control=read('verification/full-305/execution-attempt1/orchestration.json')
    need(first_control.get('automated_available_scope_passed')is False,'Keep actual first failed full result; never reclassify it.')
    captured=archive(SECOND,args.archive_sha256);folder=public(SECOND).parent
    need(captured.get('actual_validation_attempt')==2 and captured.get('source_freeze_sha256')==FREEZE_SHA
        and captured.get('activation_sha256')==ACTIVATION_SHA,'Wrong actual second archive identity.')
    gate=captured.get('complete_scope_gate')or{};root_gate=captured.get('actual_root_process_closure')or{}
    need(gate.get('complete25_ordered_component_positions')is True
        and gate.get('every_executed_assignedJob_and_retainedPopen_terminal')is True
        and root_gate.get('actual_root_controller_exit')==0
        and root_gate.get('all_recorded_root_identifiers_currently_not_live')is True,'The original strict full25/root process archive gate did not pass.')
    control=read('verification/full-305/execution-attempt2/orchestration.json')
    review=read('verification/full-305/execution-attempt2/automated-scope-review.json')
    expected=['offline','legacy','legacy_typed','current30','current29',*freeze['p3_scripts']]
    need(len(expected)==25 and len(freeze['p3_scripts'])==20 and control.get('status')=='all_required_components_terminal'
        and control.get('required_components')==expected and[x['name']for x in control['steps']]==expected,'Exact original25 ordered positions are required.')
    need(review.get('root_freeze_sha256')==FREEZE_SHA and review.get('automated_available_scope_passed')is True
        and review.get('review_failures')==[] and review.get('scope_not_reduced')is True
        and control.get('automated_available_scope_passed')is True and captured.get('automated_available_scope_passed')is True,'Original complete automated review must actually pass, not a new reduced substitute.')
    need(sha(public('verification/full-305/execution-attempt2/execution-tools/review_results305.py'))==sha(RUNTIME/'review_results305.py'),'Captured original complete-review code differs.')
    actual={};supers={}
    for name in expected:actual[name],supers[name]=actual_component(folder,name,freeze,ACTIVATION_SHA)
    current=actual['current30'];failure=current.get('failure')or{};trace=failure.get('traceback','');message=failure.get('message','')
    unavailable=(current.get('passed')is not True and failure.get('type')=='OSError'and'[WinError 1314]'in message
        and'public-261-never-create.txt'in message and'diagnostic.symlink_to(public_target.name)'in trace
        and'pathlib.py'in trace and'os.symlink('in trace and supers['current30']['child_primary_exit']==supers['current30']['supervisor_exit']==1)
    need(unavailable and review.get('current30_original_actual_symlink_prerequisite_unavailable')is True
        and actual['current29'].get('passed')is True,'Only the exact original unpassed1314 prerequisite plus independent29 actual0 is admissible.')
    png=visual_review(args.visual_review,args.archive_sha256,prefix_paths(folder,captured))
    typed=read('verification/full-305/execution-attempt2/legacy/independent-saved-readback-audit.json')
    invocation=read('verification/full-305/execution-attempt2/legacy/full305-typed-audit-invocation.json')
    need(typed.get('passed')is True and invocation.get('actual_auditor_exit')==0,'Original typed actual0 required.')
    details=review['component_details'];legacy=deepcopy(details['legacy'])
    legacy.update(passed=True,actual_validation_attempt=2,component_source_freeze_sha256=FREEZE_SHA,
        actual_child_and_supervisor_exit=0,formal_typed_readback_actual_exit=0,
        receipt='verification/full-305/execution-attempt2/legacy/actual/wine-ui-100.json',
        independent_saved_readback='verification/full-305/execution-attempt2/legacy/independent-saved-readback-audit.json')
    refs=freeze['functional_validation'];maintenance=exact_ref(refs['maintenance'])
    need(maintenance.get('exit_code')==0 and maintenance['source_sha256_before']==maintenance['source_sha256_after']==freeze['source_sha256'],'Actual targeted maintenance must bind the final full source map.')
    log=public((Path(refs['maintenance']['path']).parent/'stderr.log').as_posix())
    text=log.read_text(encoding='utf8');runs=re.findall(r'^Ran (\d+) tests? in ',text,re.M)
    need(len(runs)==1 and re.search(r'^OK\s*$',text,re.M),'Actual targeted unittest completion log required.')
    regression=exact_ref(refs['native296_regression']);regprocess=exact_ref(refs['native296_regression_process'])
    need(regression.get('passed')is True and regprocess.get('exit_code')==regprocess.get('child_primary_exit')==0
        and regprocess.get('owned_job_no_live_execution_verified')is True,'Actual repaired296 regression0 is required; not just static proof.')
    offline=actual['offline'];p3={}
    for name in freeze['p3_scripts']:
        raw=actual[name];detail=details[name]
        p3[name.removeprefix('p3_')]={'passed':True,'actual_execution_attempt':2,'component_source_freeze_sha256':FREEZE_SHA,
            'actual_child_and_supervisor_exit':0,'unique_check_labels':detail['checks'],
            'actual_assertion_executions':raw.get('successful_assertion_executions_including_repeated_guards',len(raw.get('checks',[]))),
            'selected_source_files':detail['source_count'],'actual_fixture_pid':detail['actual_fixture_pid'],
            'owned_launcher_pid':detail['owned_launcher_pid'],'receipt':'verification/full-305/execution-attempt2/'+name+'/actual/window.json',
            'PID_equality_or_ancestry_assumed':False}
    old=read('verification/full-290/source-freeze-final-A3.json')
    need(freeze['selectors'][:len(old['selectors'])]==old['selectors']and len(old['selectors'])==430,'Complete original430 ordered selector prefix lost.')
    summary={'after_section':305,'kind':'functional_section_full_validation','checked_at_Beijing':datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=8))).isoformat(),
        'available_checks_passed':True,'complete_repository_validation':False,'scope_not_reduced':True,'P2_complete':False,
        'single_execution_all_green':False,'actual_validation_attempt':2,'all_final_component_source_maps_share_one_freeze':True,
        'all_historical_source_maps_same_freeze':False,'current_worktree_validation_authority':True,
        'source_files':len(freeze['source_sha256']),'maintained_selectors':len(freeze['selectors']),
        'supplemental_public_input_files':len(freeze['supplemental_public_inputs_sha256']),
        'legacy_native_sources':len(freeze['legacy_native_source_sha256']),'legacy_additional_sources':len(freeze['legacy_external_additional_sha256']),
        'source_freeze':FREEZE,'source_freeze_sha256':FREEZE_SHA,'activation_sha256':ACTIVATION_SHA,
        'tested_worktree_parent_commit':freeze['parent_commit'],'source_drift':[],
        'native_current_windows_gui_verified':True,'native_windows_game_chat_verified':False,'historical_original_Windows_verified':False,
        'archive_manifests_sha256':{FIRST:FIRST_SHA,SECOND:args.archive_sha256},'root_second_PNG_visual_review':png,
        'offline_windows':{k:offline[k]for k in ('tests_run','tests_passed','historical_or_declared_skips','failures','errors','unavailable_records','unavailable_parent_count','qt_shutdown','qt_shutdown_error')},
        'actual_offline_process_exit':0,'offline_receipt':'verification/full-305/execution-attempt2/offline/actual/windows-offline.json',
        'legacy_window':legacy,'current_window':{'maintained_scope':30,'actual_execution_attempt':2,'component_source_freeze_sha256':FREEZE_SHA,
            'available_original_workflows_passed':len(actual['current29']['checks']),'actual_full30_attempt_preserved':True,
            'full30_actual_child_and_supervisor_exit':1,'current29_actual_child_and_supervisor_exit':0,
            'original_symlink_operation_passed':False,'symlink_specialization':'Original Path.symlink_to -> os.symlink WinError1314 unavailable, not passed.',
            'current29_receipt':'verification/full-305/execution-attempt2/current29/actual/window.json',
            'full30_failure_receipt':'verification/full-305/execution-attempt2/current30/actual/window.json'},
        'p3_supplementary_windows':p3,'original_complete_scope_review':ref('verification/full-305/execution-attempt2/automated-scope-review.json'),
        'fresh_maintenance_checks':{'receipt':deepcopy(refs['maintenance']),'actual_process_exit':0,'actual_tests_run':int(runs[0]),'actual_selectors':maintenance['selectors'],
            'actual_stderr':ref(log.relative_to(ROOT).as_posix()),'declared_source_count':len(maintenance['source_sha256_after']),'count_not_added_to_full_offline_total':True},
        'repaired296_independent_native_regression':{'receipt':deepcopy(refs['native296_regression']),'process':deepcopy(refs['native296_regression_process']),
            'unique_check_labels':regression['unique_checks'],'actual_assertion_executions':regression['successful_assertion_executions_including_repeated_guards'],
            'not_a_substitute_for_second_full_p3_296':True},
        'functional305_necessary_and_native':deepcopy(refs),'first_failed_attempt_preserved':{'archive':ref(FIRST),
            'actual_original_controller_exit':1,'offline_counts':{k:read('verification/full-305/execution-attempt1/offline/actual/windows-offline.json')[k]for k in ('tests_run','failures','errors')},
            'all_first_traces_and_p3_296_failure_retained':True,'first_available_checks_passed':False},
        'unavailable_scopes':['Exact original native symlink WinError1314 prerequisite remains unavailable and unpassed.',
            'Linux/WSL/Wine, historical original Windows/private095/109 and game/chat are not verified by this run.'],
        'assigned_owned_jobs_empty_not_global_descendant_enumeration':True,
        'usage_wrap_up_triggered_below5_percent':True,'below5_trigger_is_historical_not_current_usage':True,'current_wrap_up_threshold_percent':15,'user_requested_pause_after_section':305,'current_remaining_usage_not_inferred':True,'finish305_publication_then_stop_no306':True}
    common.bound(freeze['parent_commit'],FREEZE_SHA,ACTIVATION_SHA)
    pointer={'last_full_validation':{'after_section':305,'receipt':SUMMARY,'available_checks_passed':True,'complete_repository_validation':False,
            'scope_not_reduced':True,'native_current_windows_gui_verified':True,'native_windows_game_chat_verified':False,
            'unresolved_available_failures':False,'original_failed_attempts_preserved':True,'actual_validation_attempt':2,
            'source_freeze_sha256':FREEZE_SHA},
        'current_available_full_validation':{'section':305,'receipt':SUMMARY,'available_scope_passed':True,'native_windows_game_chat_verified':False,
            'actual_validation_attempt':2,'source_freeze_sha256':FREEZE_SHA}}
    return summary,pointer

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--archive-sha256',required=True)
    parser.add_argument('--visual-review',required=True)
    parser.add_argument('--draft-output',type=Path)
    parser.add_argument('--apply',action='store_true')
    args=parser.parse_args();summary,pointers=build(args)
    if args.draft_output:
        path=args.draft_output.resolve();need(path.is_relative_to(ROOT/'.cache')and not path.is_symlink(),'Draft output must be new cache-only JSON.')
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('x',encoding='utf8')as stream:stream.write(json.dumps({'summary':summary,'checkpoint_pointer_proposal':pointers},ensure_ascii=False,indent=2)+'\n')
    if args.apply:
        path=ROOT/SUMMARY
        with path.open('x',encoding='utf8')as stream:stream.write(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'preview_only':not args.apply,'summary_written':SUMMARY if args.apply else None,'available_scope_gate_satisfied':True,
        'actual_selectors':summary['maintained_selectors'],'actual_sources':summary['source_files'],
        'PNG_review':summary['root_second_PNG_visual_review'],'checkpoint_pointer_proposal':pointers,
        'docs_private_Git_mutation_Qt_or_test_operations_performed':False},ensure_ascii=False))

if __name__=='__main__':main()
