from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,os,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'verification/sections/308-necessary-attempt1';OUT.mkdir()
selectors=['tests.test_direct_landmark_308','tests.test_direct_landmark_303','tests.test_direct_landmark_294','tests.test_direct_landmark_288','tests.test_direct_landmark_mapping','tests.test_map_projection_048','tests.test_map_projection_049','tests.test_player_tile_information_288','tests.test_highland_top_reference']
names=set(json.loads((ROOT/'research/p3-map-direct-ground-308/source-manifest.json').read_bytes())['files'])
names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'research/p3-map-direct-ground-308').rglob('*')if p.is_file())
names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'rouge').glob('*.py'))
names.update(s.replace('.','/')+'.py'for s in selectors)
names.update(['rouge/data/fixed-landmark-references.json','scripts/extend_direct_landmark_308.py','scripts/extend_direct_landmark_303.py','scripts/verify_full_available.py','scripts/verify_direct_map_window_308.py','scripts/verify_direct_map_window_303_full308.py','scripts/verify_direct_map_window_294_full308.py','verification/sections/308-preparation/first-frozen-comparison.json'])
def bound():return{n:sha256((ROOT/n).read_bytes()).hexdigest()for n in sorted(names)}
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
before=bound();env=dict(os.environ,QT_QPA_PLATFORM='offscreen',PYTHONDONTWRITEBYTECODE='1');start=datetime.now(timezone.utc).isoformat()
argv=[sys.executable,'-B','-X','utf8','-m','unittest','-v',*selectors]
with(OUT/'stdout.txt').open('xb')as stdout,(OUT/'stderr.txt').open('xb')as stderr:
 p=subprocess.Popen(argv,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,env=env);code=p.wait()
after=bound();error=(OUT/'stderr.txt').read_text('utf8',errors='replace');m=re.search(r'Ran (\d+) tests? in ([\d.]+)s',error)
r={'section':308,'kind':'actual_necessary_complete67_raw_readers_and_real_current123_with_explicit_legacy107_scope','selectors':selectors,'argv':argv,'actual_retained_popen_pid':p.pid,'actual_observed_exit':code,'exit_code':code,'started_at':start,'finished_at':datetime.now(timezone.utc).isoformat(),'methods_ran':int(m[1])if m else None,'seconds':float(m[2])if m else None,'source_sha256_before':before,'source_sha256_after':after,'source_unchanged':before==after,'passed':code==0 and m is not None and before==after,'full_validation_rerun':False,'source_guard_is_selected_not_all_transitive_dependencies':True,'QT_QPA_PLATFORM':'offscreen'}
(OUT/'process.json').write_bytes(enc(r));(OUT/'process.exit').write_text(str(code)+'\n',encoding='ascii');(OUT/'execution-runner.py').write_bytes(Path(__file__).read_bytes());print(json.dumps({k:v for k,v in r.items()if not k.startswith('source_sha')},ensure_ascii=False))
if not r['passed']:print(error[-11000:])
raise SystemExit(0 if r['passed']else 1)
