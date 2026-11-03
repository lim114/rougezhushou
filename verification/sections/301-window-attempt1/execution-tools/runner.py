"""Cache-only root-owned actual native runner. Never auto-execute or auto-retry."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import argparse,json,subprocess,tempfile,uuid,runpy
ROOT=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file())
PARENT='5607cbc46c9cf17a841939a778a247e6e1a2a371'
CANONICAL='scripts/verify_named_reward_items_window_301.py'
def encode(value):return(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def main(args):
 if not args.execute:raise RuntimeError('Cache preparation only. Root must explicitly --execute after final source freeze.')
 if subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()!=args.expected_parent or args.expected_parent!=PARENT:
  raise RuntimeError('Expected actual source parent changed.')
 if subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()!='codex/p2-development':
  raise RuntimeError('Unexpected branch.')
 if not 1<=args.attempt<=9 or not 0<args.visible_ms<=120000:raise ValueError('Explicit bounded attempt/visible interval required.')
 canonical=ROOT/CANONICAL;native_before=canonical.read_bytes()
 if sha256(native_before).hexdigest()!=args.native_source_sha256:raise RuntimeError('Final reviewed canonical source changed.')
 selected_before=runpy.run_path(str(canonical))['bound_files']()
 dest=ROOT/f'verification/sections/301-window-attempt{args.attempt}'
 once=ROOT/f'.cache/301-window-attempt{args.attempt}.once.json'
 if dest.exists()or once.exists():raise FileExistsError('Preserve prior actual attempt; no automatic retry.')
 container=Path(tempfile.gettempdir()).resolve()/('rouge-301-window-'+uuid.uuid4().hex)
 if container.exists()or container.is_relative_to(ROOT):raise ValueError('New isolated owned namespace required.')
 container.mkdir();actual=container/'actual';actual.mkdir();python=ROOT/'.venv/Scripts/python.exe'
 original=(ROOT/'.cache/p3-full290-final-A3-prep/supervisor3690.py').read_bytes()
 if sha256(original).hexdigest()!='b073d86b1ddb6d697278380e34b29fd3887a8ea14448f29ffd8a8852dc4b2309':
  raise RuntimeError('Previously reviewed retained-Popen/owned-job supervisor source changed.')
 adapted=original.replace(b'SECTION290_ATTEMPT2_ACTUAL_WINDOWS_OWNED_POPEN_SUPERVISION',b'SECTION301_ACTUAL_WINDOWS_OWNED_POPEN_SUPERVISION')
 supervisor=ROOT/'.cache/section301-window-supervisor.py'
 if supervisor.exists():
  if supervisor.read_bytes()!=adapted:raise ValueError('Preserve unexpected existing supervisor source.')
 else:supervisor.write_bytes(adapted)
 child=[str(python),'-B','-X','utf8',str(canonical),'--receipt',str(actual/'window.json'),'--visible-ms',str(args.visible_ms)]
 argv=[str(python),'-B','-X','utf8',str(supervisor),'--status',str(container/'supervisor.json'),'--timeout','180','--',*child]
 with once.open('xb')as stream:stream.write(encode({'section':301,'attempt':args.attempt,'container':str(container),'automatic_retry_allowed':False}))
 row={'section':301,'attempt':args.attempt,'kind':'actual_native_window_owned_process_execution','status':'launching',
  'argv':argv,'child_argv':child,'started_at':datetime.now(timezone.utc).isoformat(),
  'supervisor_sha256':sha256(adapted).hexdigest(),'supervisor_receipt':'supervisor.json',
  'supervisor_adaptation':'Only kind label changed; original execution, ownership, bounded wait and cleanup unchanged.',
  'source_sha256_before':selected_before,'reviewed_native_source_sha256':args.native_source_sha256,
  'native_full_repository_or_game_chat_verified':False,'private_state_copied':False}
 print(json.dumps({'section':301,'attempt':args.attempt,'container':str(container),'starting_native_window':True},ensure_ascii=False),flush=True)
 with(container/'controller.stdout.log').open('xb')as out,(container/'controller.stderr.log').open('xb')as err:
  process=subprocess.Popen(argv,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
  row['supervisor_pid']=process.pid;row['owned_popen_retained']=True
  try:code=process.wait(timeout=210)
  except subprocess.TimeoutExpired:
   row.update(status='incomplete_do_not_retry',exit_code=None)
   (container/'process.json').write_bytes(encode(row))
   raise RuntimeError('Outer observer elapsed; owned supervisor uncertain. Preserve namespace; no duplicate or global termination.')
 supervision=json.loads((container/'supervisor.json').read_bytes())
 row.update(status='completed',exit_code=code,child_primary_exit=supervision['child_primary_exit'],timed_out=supervision['timed_out'],
  owned_job_no_live_execution_verified=supervision.get('owned_job_no_live_execution_verified',False),finished_at=datetime.now(timezone.utc).isoformat())
 if(actual/'window.json').is_file():
  receipt=json.loads((actual/'window.json').read_bytes())
  row['window_receipt_sha256']=sha256((actual/'window.json').read_bytes()).hexdigest()
  row['source_before_after_unchanged']=receipt['source_sha256_before']==receipt['source_sha256_after']==selected_before
  row['window_receipt_passed']=receipt['passed']
 else:row.update(window_receipt_passed=False,source_before_after_unchanged=False)
 selected_after=runpy.run_path(str(canonical))['bound_files']()
 row['source_sha256_after']=selected_after
 row['controller_source_guard_stable']=selected_before==selected_after and canonical.read_bytes()==native_before
 (container/'process.json').write_bytes(encode(row))
 if supervision['status']!='completed'or not row['owned_job_no_live_execution_verified']:
  raise RuntimeError('Owned job not closed; preserve actual namespace and do not retry.')
 dest.mkdir(parents=True);copies={}
 for p in container.rglob('*'):
  if p.is_symlink():raise ValueError('No symlink in owned actual namespace archive.')
  if p.is_file():
   if p.suffix not in{'.json','.log','.png'}:raise ValueError('Unexpected actual output kind.')
   copies[p.relative_to(container).as_posix()]=p.read_bytes()
 copies.update({'execution-tools/runner.py':Path(__file__).read_bytes(),'execution-tools/supervisor.py':adapted,
  'execution-tools/window.py':native_before})
 for name,raw in copies.items():
  p=dest/name;p.parent.mkdir(parents=True,exist_ok=True)
  with p.open('xb')as stream:stream.write(raw)
 manifest={'kind':'301_EXACT_PUBLIC_NATIVE_ATTEMPT_OUTPUTS','attempt':args.attempt,
  'files':{n:{'sha256':sha256(v).hexdigest(),'bytes':len(v)}for n,v in copies.items()},
  'original_actual_paths_preserved':True,'private_state_copied':False}
 with(dest/'archive-manifest.json').open('xb')as stream:stream.write(encode(manifest))
 print(json.dumps({k:row[k]for k in('section','attempt','status','exit_code','child_primary_exit','timed_out',
  'owned_job_no_live_execution_verified','window_receipt_passed','source_before_after_unchanged','controller_source_guard_stable')},ensure_ascii=False),flush=True)
 return 0 if(code==row['child_primary_exit']==0 and row['window_receipt_passed']
  and row['source_before_after_unchanged']and row['controller_source_guard_stable'])else 1
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--execute',action='store_true')
 parser.add_argument('--attempt',type=int,required=True);parser.add_argument('--native-source-sha256',required=True)
 parser.add_argument('--expected-parent',required=True);parser.add_argument('--visible-ms',type=int,default=60000)
 raise SystemExit(main(parser.parse_args()))
