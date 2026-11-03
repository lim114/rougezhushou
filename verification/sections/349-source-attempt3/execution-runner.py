from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import argparse,json,os,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('kind',choices=['necessary','source','native']);p.add_argument('--attempt',type=int,default=1);args=p.parse_args()
out=ROOT/f'verification/sections/349-{args.kind}-attempt{args.attempt}';out.mkdir()
selectors=['tests.test_current_critical_reward_origins_349','tests.test_current_critical_reward_origins_view_349','tests.test_current_named_reward_origins_347','tests.test_current_named_reward_origins_view_347','tests.test_current_reward_origins_338','tests.test_current_reward_origins_view_338']
sys.path.insert(0,str(ROOT))
from scripts.verify_current_critical_reward_origins_window_349 import bound_files
before=bound_files();prefix=[sys.executable,'-B','-X','utf8'];start=datetime.now(timezone.utc).isoformat()
if args.kind=='source':argv=prefix+['scripts/build_current_critical_reward_origins_349.py','--check']
elif args.kind=='necessary':argv=prefix+['-m','unittest','-v',*selectors]
else:argv=prefix+['scripts/verify_current_critical_reward_origins_window_349.py','--receipt',str(out/'actual/window.json'),'--visible-ms','120000']
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',QT_QPA_PLATFORM='windows'if args.kind=='native'else'offscreen')
with(out/'stdout.txt').open('xb')as stdout,(out/'stderr.txt').open('xb')as stderr:
 child=subprocess.Popen(argv,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,env=env);code=child.wait()
after=bound_files();log=(out/'stderr.txt').read_text('utf8',errors='replace');match=re.search(r'Ran (\d+) tests? in ([\d.]+)s',log)
native=out/'actual/window.json';w=json.loads(native.read_bytes())if native.is_file()else None
r={'section':349,'kind':args.kind,'argv':argv,'retained_popen_pid':child.pid,'actual_observed_exit':code,'exit_code':code,'start_utc':start,'finish_utc':datetime.now(timezone.utc).isoformat(),'source_sha256_before':before,'source_sha256_after':after,'source_unchanged':before==after,'source_guard_is_selected_not_all_transitive_dependencies':True,'methods_ran':int(match[1])if match else None,'selectors':selectors if args.kind=='necessary'else None,'full_validation_rerun':False,'passed':code==0 and before==after and(args.kind!='necessary'or match is not None)and(args.kind!='native'or w is not None and w.get('passed')is True),'descendant_job_closure_claimed':False}
if w:r.update(actual_fixture_pid=w['process_id'],window_receipt=native.relative_to(ROOT).as_posix(),window_receipt_sha256=sha256(native.read_bytes()).hexdigest(),window_passed=w['passed'],PID_equality_assumed=False)
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+chr(10)).encode('utf8')
(out/'process.json').write_bytes(enc(r));(out/'process.exit').write_text(str(code)+chr(10),encoding='ascii');(out/'execution-runner.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({k:v for k,v in r.items()if not k.startswith('source_sha')},ensure_ascii=False))
if w:print(json.dumps({'native_checks':w['unique_checks'],'native_failure':w['failure']},ensure_ascii=False))
if not r['passed']:print(log[-9000:])
raise SystemExit(0 if r['passed']else 1)
