from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,os,subprocess,sys,tempfile,uuid
ROOT=Path(__file__).resolve().parents[1]
attempt=int(sys.argv[1]);assert 1<=attempt<=3
dest=ROOT/f'verification/sections/294-window-attempt{attempt}'
once=ROOT/f'.cache/294-window-attempt{attempt}.once.json'
assert not dest.exists() and not once.exists()
container=Path(tempfile.gettempdir()).resolve()/('rouge-294-window-'+uuid.uuid4().hex)
assert not container.exists() and not container.is_relative_to(ROOT)
container.mkdir();actual=container/'actual';actual.mkdir()
python=ROOT/'.venv/Scripts/python.exe'
canonical=ROOT/'scripts/verify_direct_map_window_294.py'
original=(ROOT/'.cache/p3-full290-final-A3-prep/supervisor3690.py').read_bytes()
assert sha256(original).hexdigest()=='b073d86b1ddb6d697278380e34b29fd3887a8ea14448f29ffd8a8852dc4b2309'
supervisor=ROOT/'.cache/section294-window-supervisor.py'
adapted=original.replace(b'SECTION290_ATTEMPT2_ACTUAL_WINDOWS_OWNED_POPEN_SUPERVISION',b'SECTION294_ACTUAL_WINDOWS_OWNED_POPEN_SUPERVISION')
if supervisor.exists():assert supervisor.read_bytes()==adapted
else:supervisor.write_bytes(adapted)
child=[str(python),'-B','-X','utf8',str(canonical),'--receipt',str(actual/'window.json'),'--visible-ms','60000']
argv=[str(python),'-B','-X','utf8',str(supervisor),'--status',str(container/'supervisor.json'),'--timeout','180','--',*child]
once.write_bytes((json.dumps({'section':294,'attempt':attempt,'container':str(container),'automatic_retry_allowed':False},ensure_ascii=False,indent=2)+'\n').encode('utf8'))
row={'section':294,'attempt':attempt,'kind':'actual_native_window_owned_process_execution','status':'launching',
 'argv':argv,'child_argv':child,'started_at':datetime.now(timezone.utc).isoformat(),
 'supervisor_sha256':sha256(adapted).hexdigest(),'supervisor_receipt':'supervisor.json',
 'supervisor_adaptation':'Only kind label changed from previously reviewed owned-job supervisor; execution and cleanup unchanged.',
 'native_full_repository_or_game_chat_verified':False,'private_state_copied':False}
print(json.dumps({'section':294,'attempt':attempt,'container':str(container),'starting_native_window':True},ensure_ascii=False),flush=True)
with (container/'controller.stdout.log').open('xb') as out,(container/'controller.stderr.log').open('xb') as err:
    process=subprocess.Popen(argv,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
    row['supervisor_pid']=process.pid;row['owned_popen_retained']=True
    try:
        code=process.wait(timeout=210)
    except subprocess.TimeoutExpired:
        row.update(status='incomplete_do_not_retry',exit_code=None)
        (container/'process.json').write_bytes((json.dumps(row,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
        raise RuntimeError('Outer observer elapsed; retained supervisor ownership uncertain. No duplicate permitted.')
supervision=json.loads((container/'supervisor.json').read_bytes())
row.update(status='completed',exit_code=code,child_primary_exit=supervision['child_primary_exit'],
 timed_out=supervision['timed_out'],owned_job_no_live_execution_verified=supervision.get('owned_job_no_live_execution_verified',False),
 finished_at=datetime.now(timezone.utc).isoformat())
if (actual/'window.json').is_file():
    receipt=json.loads((actual/'window.json').read_bytes())
    row['window_receipt_sha256']=sha256((actual/'window.json').read_bytes()).hexdigest()
    row['source_before_after_unchanged']=receipt['source_sha256_before']==receipt['source_sha256_after']
    row['window_receipt_passed']=receipt['passed']
else:row.update(window_receipt_passed=False,source_before_after_unchanged=False)
(container/'process.json').write_bytes((json.dumps(row,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
assert supervision['status']=='completed' and row['owned_job_no_live_execution_verified'], 'Owned job is not closed; do not retry'
dest.mkdir(parents=True)
copies={}
for p in container.rglob('*'):
    assert not p.is_symlink()
    if p.is_file():
        assert p.suffix in {'.json','.log','.png'}
        copies[p.relative_to(container).as_posix()]=p.read_bytes()
copies['execution-tools/runner.py']=Path(__file__).read_bytes()
copies['execution-tools/supervisor.py']=adapted
copies['execution-tools/window.py']=canonical.read_bytes()
for name,raw in copies.items():
    p=dest/name;p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('xb') as f:f.write(raw)
manifest={'kind':'294_EXACT_PUBLIC_NATIVE_ATTEMPT_OUTPUTS','attempt':attempt,
 'files':{n:{'sha256':sha256(v).hexdigest(),'bytes':len(v)} for n,v in copies.items()},
 'original_actual_paths_preserved':True,'private_state_copied':False}
with (dest/'archive-manifest.json').open('xb') as f:f.write((json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({k:row[k] for k in ('section','attempt','status','exit_code','child_primary_exit','timed_out','owned_job_no_live_execution_verified','window_receipt_passed','source_before_after_unchanged')},ensure_ascii=False),flush=True)
raise SystemExit(0 if code==row['child_primary_exit']==0 and row['window_receipt_passed'] and row['source_before_after_unchanged'] else 1)
