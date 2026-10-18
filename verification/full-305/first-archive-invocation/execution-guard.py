"""Root guard for final first-attempt archive; never stop or restart a job."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import argparse,ctypes,json,subprocess,sys
from ctypes import wintypes

root=Path(__file__).resolve().parents[1]
base=root/'.cache/p3-full305-prep'
container=Path('C:/Users/李娜/AppData/Local/Temp/rouge-full305-e6aada2377db4d4f9f58019bfa25502d')
def load(path):return json.loads(path.read_bytes())
def digest(path):return sha256(path.read_bytes()).hexdigest()
def require(value,message):
    if not value:raise ValueError(message)
def not_live(pid):
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];kernel.OpenProcess.restype=wintypes.HANDLE
    kernel.WaitForSingleObject.argtypes=[wintypes.HANDLE,wintypes.DWORD];kernel.WaitForSingleObject.restype=wintypes.DWORD
    kernel.CloseHandle.argtypes=[wintypes.HANDLE];kernel.CloseHandle.restype=wintypes.BOOL
    handle=kernel.OpenProcess(0x00100000,False,pid)
    if not handle:
        require(ctypes.get_last_error()==87,'Could not establish original process closure: '+str(pid));return
    try:require(kernel.WaitForSingleObject(handle,0)==0,'Original controller/wrapper still live or cannot verify closure: '+str(pid))
    finally:kernel.CloseHandle(handle)
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute-archive-after-all-terminal',action='store_true');args=parser.parse_args()
    require(args.execute_archive_after_all_terminal,'Explicit root archive action required; preparation does not execute.')
    observation=load(base/'root-launch-attempt1/controller-process.json')
    require(observation['status']=='completed' and type(observation['actual_observed_exit'])is int
        and observation.get('exit_observed_directly_from_retained_popen')is True
        and observation.get('exit_inferred_from_output_json')is False,'Original actual retained Popen not terminal.')
    require(int((base/'root-launch-attempt1/process.exit').read_text('ascii').strip())==observation['actual_observed_exit'],'Original root observed exit bytes differ.')
    for pid in(observation['controller_pid'],observation['root_wrapper_pid']):not_live(pid)
    freeze=root/'verification/full-305/source-freeze.json'
    require(digest(freeze)=='32033bd8a5ebc2920843e00ac2584a2b01bd9659ffcd46352fb69b780ecc1463','Original first freeze drift.')
    data=load(freeze);orchestration=load(container/'orchestration.json')
    expected=['offline','legacy','legacy_typed','current30','current29',*data['p3_scripts']]
    require(orchestration.get('status')=='all_required_components_terminal','First execution has not reached final complete observation.')
    require(orchestration['required_components']==expected and [row['name']for row in orchestration['steps']]==expected,'Incomplete, reordered or duplicate original full scope.')
    for row in orchestration['steps']:
        if row['status'].startswith('not_run_'):
            require(row['name']=='legacy_typed' and row['status']=='not_run_legacy_not_passed','Unexpected unattempted required component.')
            continue
        require(row['status']=='terminal' and row.get('terminal_supervisor_and_job_verified')is True,'Uncertain original assigned job closure: '+row['name'])
        supervisor=load(container/row['name']/'supervisor.json')
        require(supervisor.get('status')=='completed' and supervisor.get('owned_job_no_live_execution_verified')is True,'Assigned job not closed: '+row['name'])
    output=root/'verification/full-305/first-archive-invocation';output.mkdir()
    argv=[sys.executable,'-B','-X','utf8',str(base/'archive_full305.py'),'--archive','--container',str(container),
     '--attempt-name','execution-attempt1','--expected-parent-commit','89606d703dc121d26f869723e1bb7d1d356a913e',
     '--freeze-sha256','32033bd8a5ebc2920843e00ac2584a2b01bd9659ffcd46352fb69b780ecc1463',
     '--activation-sha256','098721d4a0b1b0daeafb6ff73e6f485e371bcc3a01f693dd291c50897de09959']
    with (output/'stdout.txt').open('xb')as stdout,(output/'stderr.txt').open('xb')as stderr:
        result=subprocess.run(argv,cwd=root,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr)
    (output/'process.exit').write_bytes((str(result.returncode)+'\n').encode('ascii'))
    record={'section':305,'kind':'root_all_components_closed_archive_invocation','at_utc':datetime.now(timezone.utc).isoformat(),
     'actual_exit':result.returncode,'original_controller_actual_exit':observation['actual_observed_exit'],
     'all_25_original_component_positions_accounted_for':len(expected)==25,'source_freeze_sha256':digest(freeze),
     'first_failed_attempt_not_presented_as_PASS':True,'assigned_jobs_only_not_global_process_enumeration':True,'argv':argv}
    if result.returncode==0:record['archive_manifest_sha256']=digest(root/'verification/full-305/execution-attempt1/archive-manifest.json')
    (output/'process.json').write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode())
    (output/'execution-guard.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps(record,ensure_ascii=False));return result.returncode
if __name__=='__main__':raise SystemExit(main())
