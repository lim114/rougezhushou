from pathlib import Path
from datetime import datetime,timezone
from hashlib import sha256
import json,os,subprocess,sys,time

root=Path(__file__).resolve().parents[1]
base=root/'.cache/full350-attempt2'
folder=base/'root-launch'
assert folder.is_dir() and not (folder/'controller-process.json').exists()
assert sha256((base/'CONTROLLER_READY350.json').read_bytes()).hexdigest()=='faddc91b26e9be669b3531c111882c3ef8ec56ca3c695d1e467baca112bb8de8'
assert sha256((root/'verification/full-350/source-freeze-attempt2.json').read_bytes()).hexdigest()=='57d5b8b33a978ebbbc5af3f7331c9dc4f5045a4b1f306fd5cb62190c8101742e'
assert sha256((base/'activation350.json').read_bytes()).hexdigest()=='9cc98f9c6df9036b9d26fdcb3fa3b683489345443c6a3cf8316148c8e7b93e28'
argv=[sys.executable,'-B','-X','utf8',str(base/'run_full350_controller.py'),'--execute',
 '--expected-parent-commit','87b3f79683d0a406ae2d544502323e9239003a70',
 '--freeze-sha256','57d5b8b33a978ebbbc5af3f7331c9dc4f5045a4b1f306fd5cb62190c8101742e',
 '--activation-sha256','9cc98f9c6df9036b9d26fdcb3fa3b683489345443c6a3cf8316148c8e7b93e28']
def checkpoint(value):
    temporary=folder/'controller-process.owned.tmp'
    with temporary.open('wb')as file:
        file.write((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode());file.flush();os.fsync(file.fileno())
    os.replace(temporary,folder/'controller-process.json')
with (folder/'stdout.txt').open('xb')as out,(folder/'stderr.txt').open('xb')as err:
    process=subprocess.Popen(argv,cwd=root,stdin=subprocess.DEVNULL,stdout=out,stderr=err,close_fds=True,creationflags=subprocess.CREATE_NO_WINDOW)
    record={'section':350,'kind':'root_actual_full_controller_retained_Popen','status':'running','controller_pid':process.pid,'root_wrapper_pid':os.getpid(),'argv':argv,'owned_popen_retained':True,'actual_observed_exit':None,'started_at':datetime.now(timezone.utc).isoformat(),'automatic_retry_allowed':False,'global_process_termination':False}
    checkpoint(record)
    code=process.wait()
    with (folder/'process.exit').open('xb')as file:
        file.write((str(code)+'\n').encode('ascii'));file.flush();os.fsync(file.fileno())
    record.update(status='completed',actual_observed_exit=code,finished_at=datetime.now(timezone.utc).isoformat(),exit_observed_directly_from_retained_popen=True,exit_inferred_from_output_json=False)
    checkpoint(record)
raise SystemExit(code)
