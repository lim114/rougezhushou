from pathlib import Path
from datetime import datetime,timezone
from hashlib import sha256
import json,os,subprocess,sys,time

root=Path(__file__).resolve().parents[1]
base=root/'.cache/full320-prep'
folder=base/'root-launch'
assert folder.is_dir() and not (folder/'controller-process.json').exists()
assert sha256((base/'CONTROLLER_READY320.json').read_bytes()).hexdigest()=='f55b1a8542a053a0ea8204e23464938bbcba51ffac23fdbba5ad2b7f8ebe7494'
assert sha256((root/'verification/full-320/source-freeze-attempt1.json').read_bytes()).hexdigest()=='f4a0e158fac691ddbf7a53567281dbe349a88d11171e4742909145c14d05525d'
assert sha256((base/'activation320.json').read_bytes()).hexdigest()=='1a8345bb9211f4d24a9cd538990740105f870c368531bdedeb23c62fb4120497'
argv=[sys.executable,'-B','-X','utf8',str(base/'run_full320_controller.py'),'--execute',
 '--expected-parent-commit','e320b50d43f713c50941a29ffc1e89c2311761dc',
 '--freeze-sha256','f4a0e158fac691ddbf7a53567281dbe349a88d11171e4742909145c14d05525d',
 '--activation-sha256','1a8345bb9211f4d24a9cd538990740105f870c368531bdedeb23c62fb4120497']
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
