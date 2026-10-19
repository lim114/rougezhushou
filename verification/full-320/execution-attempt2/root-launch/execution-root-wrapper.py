from pathlib import Path
from datetime import datetime,timezone
from hashlib import sha256
import json,os,subprocess,sys,time

root=Path(__file__).resolve().parents[1]
base=root/'.cache/full320-attempt2-prep'
folder=base/'root-launch'
assert folder.is_dir() and not (folder/'controller-process.json').exists()
assert sha256((base/'CONTROLLER_READY320.json').read_bytes()).hexdigest()=='a6a1dcd0b928f65db1c902b7b64301cb302f8c7ea51435ebad04c0fbf679e613'
assert sha256((root/'verification/full-320/source-freeze-attempt2.json').read_bytes()).hexdigest()=='954012182a0f700e504ae4349f8b5847b4ab2ced6bb2ab5bce3abec3ee98cb51'
assert sha256((base/'activation320.json').read_bytes()).hexdigest()=='796d46e88869e1854e938d61a8ff8d7ec1bb80ff8b64b23b186d4b7be3bbe596'
argv=[sys.executable,'-B','-X','utf8',str(base/'run_full320_controller.py'),'--execute',
 '--expected-parent-commit','e320b50d43f713c50941a29ffc1e89c2311761dc',
 '--freeze-sha256','954012182a0f700e504ae4349f8b5847b4ab2ced6bb2ab5bce3abec3ee98cb51',
 '--activation-sha256','796d46e88869e1854e938d61a8ff8d7ec1bb80ff8b64b23b186d4b7be3bbe596']
def checkpoint(value):
    temporary=folder/'controller-process.owned.tmp'
    with temporary.open('wb')as file:
        file.write((json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode());file.flush();os.fsync(file.fileno())
    os.replace(temporary,folder/'controller-process.json')
with (folder/'stdout.txt').open('xb')as out,(folder/'stderr.txt').open('xb')as err:
    process=subprocess.Popen(argv,cwd=root,stdin=subprocess.DEVNULL,stdout=out,stderr=err,close_fds=True,creationflags=subprocess.CREATE_NO_WINDOW)
    record={'section':320,'kind':'root_actual_full_controller_retained_Popen','status':'running','controller_pid':process.pid,'root_wrapper_pid':os.getpid(),'argv':argv,'owned_popen_retained':True,'actual_observed_exit':None,'started_at':datetime.now(timezone.utc).isoformat(),'automatic_retry_allowed':False,'global_process_termination':False}
    checkpoint(record)
    code=process.wait()
    with (folder/'process.exit').open('xb')as file:
        file.write((str(code)+'\n').encode('ascii'));file.flush();os.fsync(file.fileno())
    record.update(status='completed',actual_observed_exit=code,finished_at=datetime.now(timezone.utc).isoformat(),exit_observed_directly_from_retained_popen=True,exit_inferred_from_output_json=False)
    checkpoint(record)
raise SystemExit(code)
