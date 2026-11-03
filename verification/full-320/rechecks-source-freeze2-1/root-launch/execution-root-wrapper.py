from pathlib import Path
from datetime import datetime,timezone
from hashlib import sha256
import json,os,subprocess,sys
root=Path(__file__).resolve().parents[1]
base=root/'.cache/full320-recheck298';folder=base/'root-launch'
assert not folder.exists();folder.mkdir()
pins={name:sha256((base/name).read_bytes()).hexdigest()for name in ('controller.py','component_child320_recheck.py')}
(folder/'source-pins.json').write_text(json.dumps(pins,indent=2)+'\n',encoding='utf8')
argv=[sys.executable,'-B','-X','utf8',str(base/'controller.py')]

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
assert all(sha256((base/name).read_bytes()).hexdigest()==h for name,h in pins.items())
raise SystemExit(code)
