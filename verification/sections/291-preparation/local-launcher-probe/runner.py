from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,subprocess
ROOT=Path(__file__).resolve().parents[1]
dest=ROOT/'verification/sections/291-preparation/local-launcher-probe';dest.mkdir()
exe=ROOT/'.venv/Scripts/python.exe'
source="import os,sys,json;print(json.dumps({'pid':os.getpid(),'parent_pid':os.getppid(),'executable':sys.executable,'base_executable':sys._base_executable}))"
argv=[str(exe),'-B','-X','utf8','-c',source]
started=datetime.now(timezone.utc).isoformat()
with (dest/'stdout.txt').open('xb') as out,(dest/'stderr.txt').open('xb') as err:
    proc=subprocess.Popen(argv,cwd=ROOT,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
    launch_pid=proc.pid;code=proc.wait(timeout=20)
child=json.loads((dest/'stdout.txt').read_bytes());assert code==0
assert child['parent_pid']==launch_pid and child['pid']!=launch_pid
report={'kind':'actual_local_venv_launcher_pid_probe_not_historical_window_replay','argv':argv,
 'exit_code':code,'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),
 'popen_launcher_pid':launch_pid,'actual_python':child,
 'exact_venv_executable_sha256':sha256(exe.read_bytes()).hexdigest(),
 'observed_distinct_launcher_and_interpreter_PIDs':True,
 'interpreter_parent_matches_owned_probe_popen_pid':True,
 'historical_window_ancestry_reconstructed':False,'new_GUI_or_game_chat_execution':False,
 'scope':'Explains why local launcher PID equality cannot be assumed. Does not reconstruct the completed window execution process tree.'}
(dest/'process.json').write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
(dest/'runner.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'actual_probe_exit':code,'local_distinct_launcher_interpreter_PIDs_confirmed':True,'historical_replay':False}))
