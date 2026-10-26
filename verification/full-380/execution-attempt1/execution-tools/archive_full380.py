"""Archive exact terminal380 outputs; never run tests, infer PASS or copy state dirs."""
from pathlib import Path
import argparse,json,re,tempfile
from full380_common import BASE,ROOT,ATTEMPT,FREEZE,READY_PATH,bound,sha,tool_pins,write_new,now


def load(path):
    if not path.is_file()or path.is_symlink():raise ValueError('Actual regular recorded output required: '+str(path))
    return json.loads(path.read_bytes())


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--archive',action='store_true')
    for name in('expected-parent-commit','freeze-sha256','activation-sha256'):p.add_argument('--'+name,required=True)
    args=p.parse_args()
    if not args.archive:raise ValueError('Explicit root archive required.')
    data,activation=bound(args.expected_parent_commit,args.freeze_sha256,args.activation_sha256)
    launch=BASE/'root-launch';process=load(launch/'controller-process.json');container=Path(load(BASE/'full380-once.json')['container'])
    if not container.is_absolute()or container.parent!=Path(tempfile.gettempdir()).resolve()or not re.fullmatch('rouge-full380-attempt'+str(ATTEMPT)+r'-[0-9a-f]{32}',container.name)or container.is_symlink():raise ValueError('Exact original owned temporary namespace required; do not inspect other state directories.')
    if not(process.get('status')=='completed'and type(process.get('actual_observed_exit'))is int and process.get('owned_popen_retained')is True
           and process.get('exit_observed_directly_from_retained_popen')is True and process.get('exit_inferred_from_output_json')is False):raise ValueError('Original retained root controller must actually finish before archive.')
    if int((launch/'process.exit').read_text('ascii'))!=process['actual_observed_exit']or sha(launch/'process.exit')!=process['actual_process_exit_sha256']:raise ValueError('Actual root exit provenance differs.')
    if process['wrapper_sha256']!=sha(BASE/'run_owned_full380.py'):raise ValueError('Recorded launch wrapper bytes differ.')
    expected_root_argv=[str(ROOT/'.venv/Scripts/python.exe'),'-B','-X','utf8',str(BASE/'run_full380_controller.py'),'--execute',
                        '--expected-parent-commit',args.expected_parent_commit,'--freeze-sha256',args.freeze_sha256,
                        '--activation-sha256',args.activation_sha256]
    if process['argv']!=expected_root_argv:raise ValueError('Actual retained root controller argv differs.')
    authority=load(container/'owned-execution.json');ledger=load(container/'orchestration.json')
    if authority['section']!=380 or authority['actual_validation_attempt']!=ATTEMPT or authority['root_freeze_sha256']!=args.freeze_sha256 or authority['activation_sha256']!=args.activation_sha256 or authority['parent_commit']!=args.expected_parent_commit:raise ValueError('Wrong owned namespace authority.')
    if authority['controller_sha256']!=sha(BASE/'run_full380_controller.py')or Path(authority['root']).resolve()!=ROOT.resolve():raise ValueError('Actual controller bytes/root differ.')
    expected=['offline','legacy','legacy_typed','current30','current29',*data['p3_scripts']]
    if ledger['status']!='all_required_components_terminal'or ledger['required_components']!=expected or[row['name']for row in ledger['steps']]!=expected:raise ValueError('No full archive while a component is missing, running or uncertain.')
    for row in ledger['steps']:
        name=row['name'];folder=container/name
        if row['status'].startswith('not_run_'):
            if name!='legacy_typed'or folder.exists()or ledger['automated_available_scope_passed']is not False:raise ValueError('An unavailable missing component cannot pass.')
            continue
        observed=load(folder/'controller-process.json');supervised=load(folder/'supervisor.json')
        if not(row['status']=='terminal'and row['terminal_supervisor_and_job_verified']is True
               and observed['status']=='completed'and type(observed['actual_observed_popen_exit'])is int
               and observed['owned_popen_retained']is True and supervised['status']=='completed'
               and supervised['supervisor_exit']==observed['actual_observed_popen_exit']
               and type(supervised['child_primary_exit'])is int and supervised['owned_handle_retained']is True
               and supervised['owned_job_assigned']is True and supervised['owned_job_no_live_execution_verified']is True):raise ValueError('Assigned original component job is not terminal: '+name)
        if int((folder/'process.exit').read_text('ascii'))!=observed['actual_observed_popen_exit']:raise ValueError('Actual component exit differs: '+name)
        origin=load(folder/'process-exit-origin.json')
        if origin['actual_observed_popen_exit']!=observed['actual_observed_popen_exit']or origin['derived_from_supervisor_json']is not False or origin['process_exit_sha256']!=sha(folder/'process.exit'):raise ValueError('Missing retained-Popen exit origin: '+name)
        # Timed-out or failed components may be preserved here, but never become PASS.
        for stream in('stdout','stderr'):
            record=supervised[stream];path=folder/record['file']
            if path.parent!=folder or sha(path)!=record['sha256']or path.stat().st_size!=record['bytes']:raise ValueError('Original supervisor stream changed: '+name)
    out=ROOT/'verification/full-380'/('execution-attempt'+str(ATTEMPT))
    if out.exists():raise FileExistsError('Never overwrite an original failure or full archive.')
    out.mkdir(parents=True);files={}
    def copy(path,name,role):
        if not path.is_file()or path.is_symlink()or Path(name).is_absolute()or'..'in Path(name).parts or name in files:raise ValueError('Only exact recorded regular public outputs may be copied.')
        dest=out/name;dest.parent.mkdir(parents=True,exist_ok=True);raw=path.read_bytes()
        with dest.open('xb')as stream:stream.write(raw)
        if sha(dest)!=sha(path):raise ValueError('Copied output differs.')
        files[name]={'sha256':sha(path),'bytes':len(raw),'role':role}
    for name in('owned-execution.json','orchestration.json','automated-scope-review.json'):copy(container/name,name,'original owned execution observation; not relabelled')
    for path,name in((FREEZE,'source-freeze.json'),(BASE/'activation380.json','activation380.json'),(BASE/'full380-once.json','full380-once.json'),(READY_PATH,'execution-tools/'+READY_PATH.name)):
        copy(path,name,'actual root authority')
    for name in('controller-process.json','process.exit','stdout.txt','stderr.txt'):copy(launch/name,'root-launch/'+name,'actual retained root Popen observation')
    for name in tool_pins()['files']:copy(BASE/name,'execution-tools/'+name,'exact frozen execution tool or unchanged original template')
    for mode,value in activation['bundles'].items():
        folder=BASE/('bound-'+mode)
        for name,pin in value['execution_tools_sha256'].items():
            if sha(folder/name)!=pin:raise ValueError('Executed fixture changed.')
            copy(folder/name,'executed-'+mode+'/'+name,'actual source-bound original complete fixture')
        copy(folder/'activation380.json','executed-'+mode+'/activation380.json','actual child activation')
    stepfiles=('step.json','controller-process.json','controller-supervisor.stdout.log','controller-supervisor.stderr.log',
               'process.exit','process-exit-origin.json','supervisor.json','supervisor.json.stdout.log','supervisor.json.stderr.log')
    legacyfiles=('wine-ui-100.json','wine-ui-new-states-100.json.gz','full125-113-bridge-ledger.json','full125-bridge-closure.json',
                 'full125-progress.json','native275-constructor-ledger.json','native275-launcher-closure.json','recipient-false-reset-ledger.json',
                 'source100-guard-input.json','hard-timeout-100.json','full380-source-closure.json')
    for row in ledger['steps']:
        if row['status'].startswith('not_run_'):continue
        name=row['name'];folder=container/name
        for leaf in stepfiles:
            if(folder/leaf).is_file():copy(folder/leaf,name+'/'+leaf,'actual retained Popen/job observation')
        if name=='legacy_typed':continue
        actual=folder/'actual'
        if not actual.is_dir():continue
        for path in sorted(actual.iterdir()):
            if not path.is_file()or path.is_symlink():continue
            if name=='legacy':allowed=path.name in legacyfiles or(path.name.startswith('wine-')and path.suffix=='.png')
            elif name=='offline':allowed=path.name in('windows-offline.json','windows-offline.log','full380-source-closure.json')
            else:allowed=path.suffix in('.json','.png')
            if allowed:copy(path,name+'/actual/'+path.name,'exact flat public isolated output; no runtime state directory traversed')
    for name in('independent-saved-readback-audit.json','full380-typed-audit-invocation.json'):
        path=container/'legacy'/name
        if path.is_file():copy(path,'legacy/'+name,'unchanged complete original typed readback')
    bound(args.expected_parent_commit,args.freeze_sha256,args.activation_sha256)
    report={'section':380,'actual_validation_attempt':ATTEMPT,'kind':'EXACT_FULL380_ORIGINAL_EXECUTION_ARCHIVE','sealed_at':now(),
            'source_freeze_sha256':args.freeze_sha256,'activation_sha256':args.activation_sha256,
            'actual_root_controller_exit':process['actual_observed_exit'],'root_exit_observed_from_retained_popen':True,
            'required_component_positions':len(expected),'all_original_ordered_components_retained':True,
            'all_executed_retained_Popen_and_assigned_jobs_terminal':True,'files':files,
            'raw_namespace_preserved_in_original_bytes':str(container),
            'automated_available_scope_passed':ledger['automated_available_scope_passed'],
            'final_available_checks_passed_not_claimed_by_archive':True,
            'private_or_dependency_directories_traversed_or_copied':False,'PNG_visual_inspection_claimed':False,
            'complete_repository_validation':False,'failed_and_timed_out_components_not_relabelled_PASS':True}
    write_new(out/'archive-manifest.json',report)
    print(json.dumps({'archive':str(out),'files':len(files),'sha256':sha(out/'archive-manifest.json'),'final_PASS_claimed':False}))


if __name__=='__main__':main()
