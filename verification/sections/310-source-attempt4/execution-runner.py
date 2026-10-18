from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import argparse,json,os,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('kind',choices=['source','necessary','native']);kind=parser.parse_args().kind
out=ROOT/('verification/sections/310-'+kind+'-attempt4');out.mkdir()
selectors=['tests.test_boss_cycle_reference_310','tests.test_boss_cycle_view_310','tests.test_boss_cycle_integration_310','tests.test_boss_phase_view_309','tests.test_boss_phase_integration_309','tests.test_enemy_form_view_306','tests.test_spawn_candidates_integration_299']
names={p.relative_to(ROOT).as_posix()for p in(ROOT/'research/p3-boss-cycle-310').rglob('*')if p.is_file()}
names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'rouge').glob('*.py'))
names.update(s.replace('.','/')+'.py'for s in selectors)
names.update(['rouge/data/boss-cycle-reference.json','rouge/data/battle-previews.json','rouge/data/enemy-skill-references.json','scripts/verify_full_available.py','scripts/build_boss_cycle_reference_310.py','scripts/verify_boss_cycle_window_310.py'])
def bound():return{n:sha256((ROOT/n).read_bytes()).hexdigest()for n in sorted(names)}
before=bound();start=datetime.now(timezone.utc).isoformat();prefix=[sys.executable,'-B','-X','utf8']
if kind=='source':argv=prefix+['scripts/build_boss_cycle_reference_310.py','--check']
elif kind=='necessary':argv=prefix+['-m','unittest','-v',*selectors]
else:argv=prefix+['scripts/verify_boss_cycle_window_310.py','--receipt',str(out/'actual/window.json'),'--visible-ms','60000']
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',QT_QPA_PLATFORM='windows'if kind=='native'else'offscreen')
with(out/'stdout.txt').open('xb')as stdout,(out/'stderr.txt').open('xb')as stderr:
    p=subprocess.Popen(argv,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,env=env);code=p.wait()
after=bound();error=(out/'stderr.txt').read_text('utf8',errors='replace');m=re.search(r'Ran (\d+) tests? in ([\d.]+)s',error)
native=out/'actual/window.json';value=json.loads(native.read_bytes())if native.is_file()else None
record={'section':310,'kind':kind,'argv':argv,'retained_popen_pid':p.pid,'actual_observed_exit':code,'exit_code':code,'start_utc':start,'finish_utc':datetime.now(timezone.utc).isoformat(),'source_sha256_before':before,'source_sha256_after':after,'source_unchanged':before==after,'source_guard_is_selected_not_all_transitive_dependencies':True,'methods_ran':int(m[1])if m else None,'selectors':selectors if kind=='necessary'else None,'full_validation_rerun':False,'passed':code==0 and before==after and(kind!='necessary'or m is not None)and(kind!='native'or value is not None and value.get('passed')is True),'descendant_job_closure_claimed':False}
if value:record.update(actual_fixture_pid=value['process_id'],window_receipt=native.relative_to(ROOT).as_posix(),window_receipt_sha256=sha256(native.read_bytes()).hexdigest(),window_passed=value['passed'],PID_equality_assumed=False)
(out/'process.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8');(out/'process.exit').write_text(str(code)+'\n',encoding='ascii');(out/'execution-runner.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({k:v for k,v in record.items()if not k.startswith('source_sha')},ensure_ascii=False))
if value:print(json.dumps({'native_checks':value['unique_checks'],'native_failure':value['failure']},ensure_ascii=False))
if not record['passed']:print(error[-9000:])
raise SystemExit(0 if record['passed']else 1)
