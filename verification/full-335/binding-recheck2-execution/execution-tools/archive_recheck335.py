from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
from ctypes import wintypes
import json,sys,ctypes
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.cache/full335-recheck2';sys.path.insert(0,str(BASE));from common import guard,PIN,FREEZE
sys.path.insert(0,str(ROOT/'.cache/full335-prep'));from execution335 import terminal_job_record

def read(p):return json.loads(p.read_bytes())
def sha(p):return sha256(p.read_bytes()).hexdigest()
def notlive(pid):
 k=ctypes.WinDLL('kernel32',use_last_error=True);k.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];k.OpenProcess.restype=wintypes.HANDLE;k.WaitForSingleObject.argtypes=[wintypes.HANDLE,wintypes.DWORD];k.WaitForSingleObject.restype=wintypes.DWORD;k.CloseHandle.argtypes=[wintypes.HANDLE]
 h=k.OpenProcess(0x00100000,False,pid)
 if not h:assert ctypes.get_last_error()==87;return
 try:assert k.WaitForSingleObject(h,0)==0
 finally:k.CloseHandle(h)
guard();r=read(BASE/'root-launch/controller-process.json');f=Path(read(BASE/'once.json')['container']);o=read(f/'orchestration.json');assert r['status']=='completed'and r['actual_observed_exit']==0 and r['exit_observed_directly_from_retained_popen']and not r['exit_inferred_from_output_json']and o['status']=='all_required_components_terminal'and o['passed']
assert int((BASE/'root-launch/process.exit').read_text())==0
for pid in {r['controller_pid'],r['root_wrapper_pid'],o['root_controller_pid']}:notlive(pid)
assert [x['mode']for x in o['components']]==['p3_304','p3_305']
for row in o['components']:
 folder=f/row['mode'];p=read(folder/'controller-process.json');terminal,details=terminal_job_record(folder,p);assert terminal and details['child_primary_exit']==details['supervisor_exit']==0 and not details['timed_out'];c=read(folder/'actual/recheck-source-closure.json');w=read(folder/'actual/window.json');assert c['component_automated_passed']and c['actual_fixture_exit']==0 and not c['fixture_exception']and not c['source_guard_exception_after']and not c['qt_cleanup_error']and c['source_freeze_sha256']==PIN and w['passed']and c['actual_receipt_sha256']==sha(folder/'actual/window.json')
out=ROOT/'verification/full-335/binding-recheck2-execution';assert not out.exists();out.mkdir();files={}
def copy(p,n):
 dest=out/n;assert p.is_file()and not p.is_symlink()and n not in files;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes());assert sha(dest)==sha(p);files[n]={'sha256':sha(p),'bytes':p.stat().st_size}
copy(f/'orchestration.json','orchestration.json')
for row in o['components']:
 folder=f/row['mode']
 for p in sorted(folder.iterdir()):
  if p.is_file()and not p.is_symlink():copy(p,row['mode']+'/'+p.name)
 for p in sorted((folder/'actual').iterdir()):
  if p.is_file()and p.suffix in ('.json','.png'):copy(p,row['mode']+'/actual/'+p.name)
for folder,label in [(BASE,'execution-tools'),(BASE/'root-launch','root-launch'),(ROOT/'.cache/full335-recheck1/root-launch','initial-preparation-root-failure')]:
 for p in sorted(folder.iterdir()):
  if p.is_file()and p.suffix in ('.json','.py','.txt','.exit'):copy(p,label+'/'+p.name)
for n in ['.cache/run_owned_recheck335.py','.cache/run_owned_recheck335_2.py','.cache/archive_recheck335.py']:
 copy(ROOT/n,'execution-tools/'+Path(n).name)
value={'section':335,'source_freeze':FREEZE,'source_freeze_sha256':PIN,'actual_root_exit':0,'actual_retained_root_and_all_components_terminal':True,'actual_components':['p3_304','p3_305'],'actual_passed':True,'original_failed_full_preserved':'verification/full-335/execution-attempt1/archive-manifest.json','unchanged_complete_component_scope':True,'recheck1_failed_before_native_launch_preserved':True,'private_or_dependency_directories_traversed':False,'PNG_review_claimed':False,'files':files,'at_utc':datetime.now(timezone.utc).isoformat()};(out/'archive-manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+chr(10),encoding='utf8');guard();print(json.dumps({'recheck_archive_files':len(files),'passed':True,'raw_components':2}))
