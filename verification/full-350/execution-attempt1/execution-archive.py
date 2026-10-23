"""Read-only archive after every observed component terminates; never launches tests."""
from pathlib import Path
from hashlib import sha256
import json,sys,ctypes
from ctypes import wintypes
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.cache/full350-prep';sys.path.insert(0,str(BASE))
from full350_common import bound,sha,tool_pins,FREEZE,READY_PATH,write_new,now
PARENT='87b3f79683d0a406ae2d544502323e9239003a70';FROZEN='fb542f9f6f8eead58bfb51f432131266d2135f48ded4ecbce99ef88ff5e4d350';ACTIVATION='9646c0f42c408209df6ffbcb3e984e3a3c0a2341f54d4e2374ba9029747ac5cd'
def load(p):return json.loads(p.read_bytes())
def not_live(pid):
    kernel=ctypes.WinDLL('kernel32',use_last_error=True);kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];kernel.OpenProcess.restype=wintypes.HANDLE;kernel.WaitForSingleObject.argtypes=[wintypes.HANDLE,wintypes.DWORD];kernel.WaitForSingleObject.restype=wintypes.DWORD;kernel.CloseHandle.argtypes=[wintypes.HANDLE]
    handle=kernel.OpenProcess(0x00100000,False,pid)
    if not handle:assert ctypes.get_last_error()==87;return
    try:assert kernel.WaitForSingleObject(handle,0)==0
    finally:kernel.CloseHandle(handle)

def main():
    data,activation=bound(PARENT,FROZEN,ACTIVATION)
    container=Path(load(BASE/'full350-once.json')['container'])
    process={'actual_observed_exit':1,'unified_exec_session_id':76034,'observation_source':'write_stdin actual tool result 2026-10-22, exit_code1; no wrapper invented'}
    authority=load(container/'owned-execution.json');assert authority['root_freeze_sha256']==FROZEN and authority['activation_sha256']==ACTIVATION
    not_live(authority['controller_fixture_pid'])
    orchestration=load(container/'orchestration.json');expected=['offline','legacy','legacy_typed','current30','current29',*data['p3_scripts']]
    assert len(expected)==70 and orchestration['status']=='all_required_components_terminal'and orchestration['required_components']==expected and [v['name']for v in orchestration['steps']]==expected
    from review_results350 import terminal
    shared=['--expected-parent-commit',PARENT,'--freeze-sha256',FROZEN,'--activation-sha256',ACTIVATION]
    for row in orchestration['steps']:
        name=row['name'];folder=container/name
        if row['status'].startswith('not_run_'):
            assert name=='legacy_typed'and not folder.exists()and orchestration['automated_available_scope_passed']is False
            continue
        assert row['status']=='terminal'and row['terminal_supervisor_and_job_verified']is True
        argv=([str(ROOT/'.venv/Scripts/python.exe'),'-B','-X','utf8',str(BASE/'readback_child350.py'),'--legacy-container',str(container/'legacy'),*shared]if name=='legacy_typed'else[str(ROOT/'.venv/Scripts/python.exe'),'-B','-X','utf8',str(BASE/'component_child350.py'),'--mode',name,'--out',str(folder/'actual'),*shared])
        terminal(folder,argv,success=False)
    out=ROOT/'verification/full-350/execution-attempt1';assert not out.exists();out.mkdir();files={}
    def copy(p,name,role):
        dest=out/name;assert p.is_file()and not p.is_symlink()and not Path(name).is_absolute()and'..'not in Path(name).parts and name not in files
        dest.parent.mkdir(parents=True,exist_ok=True);raw=p.read_bytes();dest.write_bytes(raw);assert sha(dest)==sha(p)
        files[name]={'sha256':sha(p),'bytes':len(raw),'role':role}
    for n in ('owned-execution.json','orchestration.json','automated-scope-review.json'):copy(container/n,n,'original retained execution observations')
    for p,n in [(FREEZE,'source-freeze.json'),(BASE/'activation350.json','activation350.json'),(BASE/'full350-once.json','full350-once.json'),(READY_PATH,'execution-tools/'+READY_PATH.name)]:copy(p,n,'root authority')
    copy(Path(__file__),'execution-archive.py','exact root archive consumer')
    for n in tool_pins()['files']:copy(BASE/n,'execution-tools/'+n,'exact frozen preparation and controller source')
    for mode,value in activation['bundles'].items():
        folder=BASE/('bound-'+mode)
        for n,h in value['execution_tools_sha256'].items():assert sha(folder/n)==h;copy(folder/n,'executed-'+mode+'/'+n,'actual source-bound original fixture bundle')
        copy(folder/'activation350.json','executed-'+mode+'/activation350.json','actual child source binding')
    stepfiles=('step.json','controller-process.json','controller-supervisor.stdout.log','controller-supervisor.stderr.log','process.exit','process-exit-origin.json','supervisor.json','supervisor.json.stdout.log','supervisor.json.stderr.log')
    legacyfiles=('wine-ui-100.json','wine-ui-new-states-100.json.gz','full125-113-bridge-ledger.json','full125-bridge-closure.json','full125-progress.json','native275-constructor-ledger.json','native275-launcher-closure.json','recipient-false-reset-ledger.json','source100-guard-input.json','hard-timeout-100.json','full350-source-closure.json')
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
            allowed=p.name in legacyfiles or(p.name.startswith('wine-')and p.suffix=='.png')if n=='legacy'else p.name in('windows-offline.json','windows-offline.log','full350-source-closure.json')if n=='offline'else p.suffix in('.json','.png')
            if allowed:copy(p,n+'/actual/'+p.name,'exact public isolated output; no temporary private-state or clone directory traversed')
    for n in ('independent-saved-readback-audit.json','full350-typed-audit-invocation.json'):
        p=container/'legacy'/n
        if p.is_file():copy(p,'legacy/'+n,'unchanged complete typed auditor actual output')
    bound(PARENT,FROZEN,ACTIVATION)
    report={'section':350,'actual_validation_attempt':1,'kind':'EXACT_FULL350_ORIGINAL_EXECUTION_ARCHIVE','sealed_at':now(),'source_freeze_sha256':FROZEN,'activation_sha256':ACTIVATION,'actual_root_controller_exit':process['actual_observed_exit'],'root_exit_observation':process,'all_actual_root_identifiers_not_live_at_archive':True,'required_component_positions':70,'all_original_ordered_components_retained':True,'all_executed_retained_Popen_and_assigned_jobs_terminal':True,'files':files,'raw_namespace_preserved_in_original_bytes':str(container),'automated_available_scope_passed':orchestration['automated_available_scope_passed'],'final_available_checks_passed_not_claimed_by_archive':True,'private_or_dependency_directories_traversed_or_copied':False,'PNG_visual_inspection_claimed':False,'complete_repository_validation':False}
    write_new(out/'archive-manifest.json',report)
    for name,v in files.items():assert sha(out/name)==v['sha256']and(out/name).stat().st_size==v['bytes']
    print(json.dumps({'archive':str(out),'files':len(files),'sha256':sha(out/'archive-manifest.json'),'final_PASS_claimed':False}))
if __name__=='__main__':main()
