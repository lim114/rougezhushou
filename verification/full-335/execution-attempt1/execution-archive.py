"""Read-only archive after every observed component terminates; never launches tests."""
from pathlib import Path
from hashlib import sha256
import json,sys,ctypes
from ctypes import wintypes
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.cache/full335-prep';sys.path.insert(0,str(BASE))
from full335_common import bound,sha,tool_pins,FREEZE,READY_PATH,write_new,now
PARENT='595ef0ff364319f2b5f284bbae24b7cf536e4c4e';FROZEN='1350c6832d1c3b0d03f1708be940c95b7615b582c77f8734176bffeae441fff3';ACTIVATION='ab0e080eece174b2389010c9c556c6431c4bd792291462e5fd60968001b6bee8'
def load(p):return json.loads(p.read_bytes())
def not_live(pid):
    kernel=ctypes.WinDLL('kernel32',use_last_error=True);kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];kernel.OpenProcess.restype=wintypes.HANDLE;kernel.WaitForSingleObject.argtypes=[wintypes.HANDLE,wintypes.DWORD];kernel.WaitForSingleObject.restype=wintypes.DWORD;kernel.CloseHandle.argtypes=[wintypes.HANDLE]
    handle=kernel.OpenProcess(0x00100000,False,pid)
    if not handle:assert ctypes.get_last_error()==87;return
    try:assert kernel.WaitForSingleObject(handle,0)==0
    finally:kernel.CloseHandle(handle)

def main():
    data,activation=bound(PARENT,FROZEN,ACTIVATION)
    launch=BASE/'root-launch';process=load(launch/'controller-process.json');container=Path(load(BASE/'full335-once.json')['container'])
    assert process['status']=='completed'and type(process['actual_observed_exit'])is int and process['owned_popen_retained']is True and process['exit_observed_directly_from_retained_popen']is True and process['exit_inferred_from_output_json']is False
    assert int((launch/'process.exit').read_text())==process['actual_observed_exit']
    assert process['argv']==[str(ROOT/'.venv/Scripts/python.exe'),'-B','-X','utf8',str(BASE/'run_full335_controller.py'),'--execute','--expected-parent-commit',PARENT,'--freeze-sha256',FROZEN,'--activation-sha256',ACTIVATION]
    authority=load(container/'owned-execution.json');assert authority['root_freeze_sha256']==FROZEN and authority['activation_sha256']==ACTIVATION
    for pid in {process['controller_pid'],process['root_wrapper_pid'],authority['controller_fixture_pid']}:not_live(pid)
    orchestration=load(container/'orchestration.json');expected=['offline','legacy','legacy_typed','current30','current29',*data['p3_scripts']]
    assert len(expected)==55 and orchestration['status']=='all_required_components_terminal'and orchestration['required_components']==expected and [v['name']for v in orchestration['steps']]==expected
    from review_results335 import terminal
    shared=['--expected-parent-commit',PARENT,'--freeze-sha256',FROZEN,'--activation-sha256',ACTIVATION]
    for row in orchestration['steps']:
        name=row['name'];folder=container/name
        if row['status'].startswith('not_run_'):
            assert name=='legacy_typed'and not folder.exists()and orchestration['automated_available_scope_passed']is False
            continue
        assert row['status']=='terminal'and row['terminal_supervisor_and_job_verified']is True
        argv=([str(ROOT/'.venv/Scripts/python.exe'),'-B','-X','utf8',str(BASE/'readback_child335.py'),'--legacy-container',str(container/'legacy'),*shared]if name=='legacy_typed'else[str(ROOT/'.venv/Scripts/python.exe'),'-B','-X','utf8',str(BASE/'component_child335.py'),'--mode',name,'--out',str(folder/'actual'),*shared])
        terminal(folder,argv,success=False)
    out=ROOT/'verification/full-335/execution-attempt1';assert not out.exists();out.mkdir();files={}
    def copy(p,name,role):
        dest=out/name;assert p.is_file()and not p.is_symlink()and not Path(name).is_absolute()and'..'not in Path(name).parts and name not in files
        dest.parent.mkdir(parents=True,exist_ok=True);raw=p.read_bytes();dest.write_bytes(raw);assert sha(dest)==sha(p)
        files[name]={'sha256':sha(p),'bytes':len(raw),'role':role}
    for n in ('owned-execution.json','orchestration.json','automated-scope-review.json'):copy(container/n,n,'original retained execution observations')
    for p,n in [(FREEZE,'source-freeze.json'),(BASE/'activation335.json','activation335.json'),(BASE/'full335-once.json','full335-once.json'),(READY_PATH,'execution-tools/'+READY_PATH.name)]:copy(p,n,'root authority')
    for n in ('controller-process.json','process.exit','stdout.txt','stderr.txt'):copy(launch/n,'root-launch/'+n,'actual root retained Popen observations')
    copy(ROOT/'.cache/run_owned_full335.py','root-launch/execution-root-wrapper.py','actual retained Popen wrapper; not regenerated')
    copy(Path(__file__),'execution-archive.py','exact root archive consumer')
    for n in tool_pins()['files']:copy(BASE/n,'execution-tools/'+n,'exact frozen preparation and controller source')
    for mode,value in activation['bundles'].items():
        folder=BASE/('bound-'+mode)
        for n,h in value['execution_tools_sha256'].items():assert sha(folder/n)==h;copy(folder/n,'executed-'+mode+'/'+n,'actual source-bound original fixture bundle')
        copy(folder/'activation335.json','executed-'+mode+'/activation335.json','actual child source binding')
    stepfiles=('step.json','controller-process.json','controller-supervisor.stdout.log','controller-supervisor.stderr.log','process.exit','process-exit-origin.json','supervisor.json','supervisor.json.stdout.log','supervisor.json.stderr.log')
    legacyfiles=('wine-ui-100.json','wine-ui-new-states-100.json.gz','full125-113-bridge-ledger.json','full125-bridge-closure.json','full125-progress.json','native275-constructor-ledger.json','native275-launcher-closure.json','recipient-false-reset-ledger.json','source100-guard-input.json','hard-timeout-100.json','full335-source-closure.json')
    for row in orchestration['steps']:
        if row['status'].startswith('not_run_'):continue
        n=row['name'];folder=container/n
        for f in stepfiles:
            if(folder/f).is_file():copy(folder/f,n+'/'+f,'actual supervisor assigned job and retained Popen original')
        if n=='legacy_typed':continue
        actual=folder/'actual'
        if not actual.is_dir():continue
        for p in sorted(actual.iterdir()):
            if not p.is_file()or p.is_symlink():continue
            allowed=p.name in legacyfiles or(p.name.startswith('wine-')and p.suffix=='.png')if n=='legacy'else p.name in('windows-offline.json','windows-offline.log','full335-source-closure.json')if n=='offline'else p.suffix in('.json','.png')
            if allowed:copy(p,n+'/actual/'+p.name,'exact public isolated output; no temporary private-state or clone directory traversed')
    for n in ('independent-saved-readback-audit.json','full335-typed-audit-invocation.json'):
        p=container/'legacy'/n
        if p.is_file():copy(p,'legacy/'+n,'unchanged complete typed auditor actual output')
    bound(PARENT,FROZEN,ACTIVATION)
    report={'section':335,'actual_validation_attempt':1,'kind':'EXACT_FULL335_ORIGINAL_EXECUTION_ARCHIVE','sealed_at':now(),'source_freeze_sha256':FROZEN,'activation_sha256':ACTIVATION,'actual_root_controller_exit':process['actual_observed_exit'],'all_actual_root_identifiers_not_live_at_archive':True,'required_component_positions':55,'all_original_ordered_components_retained':True,'all_executed_retained_Popen_and_assigned_jobs_terminal':True,'files':files,'raw_namespace_preserved_in_original_bytes':str(container),'automated_available_scope_passed':orchestration['automated_available_scope_passed'],'final_available_checks_passed_not_claimed_by_archive':True,'private_or_dependency_directories_traversed_or_copied':False,'PNG_visual_inspection_claimed':False,'complete_repository_validation':False}
    write_new(out/'archive-manifest.json',report)
    for name,v in files.items():assert sha(out/name)==v['sha256']and(out/name).stat().st_size==v['bytes']
    print(json.dumps({'archive':str(out),'files':len(files),'sha256':sha(out/'archive-manifest.json'),'final_PASS_claimed':False}))
if __name__=='__main__':main()
