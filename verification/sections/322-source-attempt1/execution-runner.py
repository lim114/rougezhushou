from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import argparse, json, os, re, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('kind',choices=['source','necessary','native']);parser.add_argument('--attempt',type=int,default=1);args=parser.parse_args()
out=ROOT/f'verification/sections/322-{args.kind}-attempt{args.attempt}';out.mkdir()
selectors=['tests.test_box_event_reference_322','tests.test_box_event_view_322','tests.test_documented_event_flows_321','tests.test_documented_event_flow_view_321','tests.test_expansion_reference_313','tests.test_expansion_view_313','tests.test_expansion_integration_313']
names={p.relative_to(ROOT).as_posix()for p in(ROOT/'research/p3-expansion-313').rglob('*')if p.is_file()}
names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'rouge').glob('*.py'))
names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'research/p3-current-rewards-315').rglob('*')if p.is_file())
manifest=json.loads((ROOT/'research/p3-current-rewards-315/runtime-manifest.json').read_bytes());names.update(manifest['files'])
names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'research/p3-current-battle-314').rglob('*')if p.is_file())
portraits=json.loads((ROOT/'research/p3-current-battle-314/enemy-images.json').read_bytes())['images'];names.update(v['file']for v in portraits.values())
image_index=json.loads((ROOT/'research/p3-expansion-313/map-images.json').read_bytes());names.update(row['file']for row in image_index['images'].values())
names.update(m.replace('.','/')+'.py'for m in selectors)
names.update(['rouge/data/battle-previews.json','rouge/data/enemy-skill-references.json','scripts/verify_full_available.py','scripts/build_current_map_position_319.py','scripts/verify_current_map_position_window_319.py','scripts/build_boss_hunt_reference_311.py'])
def bound():return{n:sha256((ROOT/n).read_bytes()).hexdigest()for n in sorted(names)}
names.update(p.relative_to(ROOT).as_posix()for p in(ROOT/'research/p3-current-map-position-319').rglob('*')if p.is_file());names.add('rouge/data/current-map-position.json');names.update(json.loads((ROOT/'research/p3-current-map-position-319/runtime-manifest.json').read_bytes())['files'])
names.update(['scripts/verify_current_action_positions_window_320.py','rouge/current_action_positions.py','rouge/current_action_positions_view.py']);names.update(['scripts/build_documented_event_flows_321.py','rouge/documented_event_flows.py','rouge/documented_event_flow_view.py','rouge/data/documented-event-flows.json']);names.update(q.relative_to(ROOT).as_posix()for q in(ROOT/'research/p3-document-flows-321').rglob('*')if q.is_file());
names.add('scripts/verify_documented_event_flows_window_321.py');
names.update(['scripts/build_box_event_reference_322.py','rouge/data/box-event-reference.json']);names.update(q.relative_to(ROOT).as_posix()for q in(ROOT/'research/p3-box-event-322').rglob('*')if q.is_file());
names.add('scripts/verify_box_event_window_322.py');
before=bound();start=datetime.now(timezone.utc).isoformat();prefix=[sys.executable,'-B','-X','utf8']
if args.kind=='source':argv=prefix+['scripts/build_box_event_reference_322.py','--check']
elif args.kind=='necessary':argv=prefix+['-m','unittest','-v',*selectors]
else:argv=prefix+['scripts/verify_box_event_window_322.py','--receipt',str(out/'actual/window.json'),'--visible-ms','60000']
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',QT_QPA_PLATFORM='windows'if args.kind=='native'else'offscreen')
with(out/'stdout.txt').open('xb')as stdout,(out/'stderr.txt').open('xb')as stderr:
 p=subprocess.Popen(argv,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,env=env);code=p.wait()
after=bound();log=(out/'stderr.txt').read_text('utf8',errors='replace');match=re.search(r'Ran (\d+) tests? in ([\d.]+)s',log)
native=out/'actual/window.json';v=json.loads(native.read_bytes())if native.is_file()else None
record={'section':322,'kind':args.kind,'argv':argv,'retained_popen_pid':p.pid,'actual_observed_exit':code,'exit_code':code,'start_utc':start,'finish_utc':datetime.now(timezone.utc).isoformat(),'source_sha256_before':before,'source_sha256_after':after,'source_unchanged':before==after,'source_guard_is_selected_not_all_transitive_dependencies':True,'methods_ran':int(match[1])if match else None,'selectors':selectors if args.kind=='necessary'else None,'full_validation_rerun':False,'passed':code==0 and before==after and(args.kind!='necessary'or match is not None)and(args.kind!='native'or v is not None and v.get('passed')is True),'descendant_job_closure_claimed':False}
if v:record.update(actual_fixture_pid=v['process_id'],window_receipt=native.relative_to(ROOT).as_posix(),window_receipt_sha256=sha256(native.read_bytes()).hexdigest(),window_passed=v['passed'],PID_equality_assumed=False)
(out/'process.json').write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode('utf8'));(out/'process.exit').write_text(str(code)+'\n',encoding='ascii');(out/'execution-runner.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({k:v for k,v in record.items()if not k.startswith('source_sha')},ensure_ascii=False))
if v:print(json.dumps({'native_checks':v['unique_checks'],'native_failure':v['failure']},ensure_ascii=False))
if not record['passed']:print(log[-9000:])
raise SystemExit(0 if record['passed']else 1)
