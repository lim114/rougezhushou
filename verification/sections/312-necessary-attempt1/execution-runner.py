from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import argparse, json, os, re, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('kind',choices=['source','necessary','native']);parser.add_argument('--attempt',type=int,default=1);args=parser.parse_args()
out=ROOT/f'verification/sections/312-{args.kind}-attempt{args.attempt}';out.mkdir()
selectors=['tests.test_gold_boss_reference_312','tests.test_gold_boss_view_312','tests.test_gold_boss_integration_312',
 'tests.test_boss_hunt_view_311','tests.test_boss_hunt_integration_311','tests.test_boss_cycle_integration_310',
 'tests.test_boss_phase_integration_309','tests.test_enemy_form_view_306','tests.test_spawn_candidates_integration_299']
names={p.relative_to(ROOT).as_posix()for p in(ROOT/'research/p3-gold-boss-312').rglob('*')if p.is_file()}
names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'rouge').glob('*.py'))
names.update(m.replace('.','/')+'.py'for m in selectors)
names.update(['rouge/data/gold-boss-reference.json','rouge/data/battle-previews.json','rouge/data/enemy-skill-references.json','scripts/verify_full_available.py','scripts/build_gold_boss_reference_312.py','scripts/verify_gold_boss_window_312.py','scripts/build_boss_hunt_reference_311.py'])
def bound():return{n:sha256((ROOT/n).read_bytes()).hexdigest()for n in sorted(names)}
before=bound();start=datetime.now(timezone.utc).isoformat();prefix=[sys.executable,'-B','-X','utf8']
if args.kind=='source':argv=prefix+['scripts/build_gold_boss_reference_312.py','--check']
elif args.kind=='necessary':argv=prefix+['-m','unittest','-v',*selectors]
else:argv=prefix+['scripts/verify_gold_boss_window_312.py','--receipt',str(out/'actual/window.json'),'--visible-ms','60000']
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',QT_QPA_PLATFORM='windows'if args.kind=='native'else'offscreen')
with(out/'stdout.txt').open('xb')as stdout,(out/'stderr.txt').open('xb')as stderr:
 p=subprocess.Popen(argv,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,env=env);code=p.wait()
after=bound();log=(out/'stderr.txt').read_text('utf8',errors='replace');match=re.search(r'Ran (\d+) tests? in ([\d.]+)s',log)
native=out/'actual/window.json';v=json.loads(native.read_bytes())if native.is_file()else None
record={'section':312,'kind':args.kind,'argv':argv,'retained_popen_pid':p.pid,'actual_observed_exit':code,'exit_code':code,'start_utc':start,'finish_utc':datetime.now(timezone.utc).isoformat(),'source_sha256_before':before,'source_sha256_after':after,'source_unchanged':before==after,'source_guard_is_selected_not_all_transitive_dependencies':True,'methods_ran':int(match[1])if match else None,'selectors':selectors if args.kind=='necessary'else None,'full_validation_rerun':False,'passed':code==0 and before==after and(args.kind!='necessary'or match is not None)and(args.kind!='native'or v is not None and v.get('passed')is True),'descendant_job_closure_claimed':False}
if v:record.update(actual_fixture_pid=v['process_id'],window_receipt=native.relative_to(ROOT).as_posix(),window_receipt_sha256=sha256(native.read_bytes()).hexdigest(),window_passed=v['passed'],PID_equality_assumed=False)
(out/'process.json').write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode('utf8'));(out/'process.exit').write_text(str(code)+'\n',encoding='ascii');(out/'execution-runner.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({k:v for k,v in record.items()if not k.startswith('source_sha')},ensure_ascii=False))
if v:print(json.dumps({'native_checks':v['unique_checks'],'native_failure':v['failure']},ensure_ascii=False))
if not record['passed']:print(log[-9000:])
raise SystemExit(0 if record['passed']else 1)
