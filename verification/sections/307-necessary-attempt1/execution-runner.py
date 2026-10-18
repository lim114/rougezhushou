from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,os,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'verification/sections/307-necessary-attempt1';OUT.mkdir()
selectors=['tests.test_choice_annotations_307','tests.test_choice_annotation_view_307','tests.test_annotation_presentation_pairs_307','tests.test_event_planning','tests.test_original_destinations','tests.test_player_information_view_286','tests.test_documented_item_integration_295','tests.test_expedition_integration_297','tests.test_event_node_requirements_integration_298','tests.test_battle_entry_compatibility_299']
names=set(json.loads((ROOT/'research/p3-choice-annotations-307/source-manifest.json').read_bytes())['runtime_files'])
names.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'research/p3-choice-annotations-307').rglob('*') if p.is_file())
names.update(p.relative_to(ROOT).as_posix() for p in (ROOT/'rouge').glob('*.py'))
names.update(s.replace('.','/')+'.py' for s in selectors)
names.update(['scripts/build_choice_annotations_307.py','tests/player_presentation_legacy_307.py','verification/sections/307-preparation/before/rouge/player_node_information.py'])
def bound():return {name:sha256((ROOT/name).read_bytes()).hexdigest() for name in sorted(names)}
before=bound();env=dict(os.environ,QT_QPA_PLATFORM='offscreen',PYTHONDONTWRITEBYTECODE='1');start=datetime.now(timezone.utc).isoformat()
argv=[sys.executable,'-B','-X','utf8','-m','unittest','-v',*selectors]
with (OUT/'stdout.txt').open('xb') as stdout,(OUT/'stderr.txt').open('xb') as stderr:
 p=subprocess.Popen(argv,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,env=env);code=p.wait()
after=bound();error=(OUT/'stderr.txt').read_text('utf8',errors='replace');m=re.search(r'Ran (\d+) tests? in ([\d.]+)s',error)
record={'section':307,'kind':'actual_necessary_checks_including_current_38_event_pairs_and_legacy_scope','selectors':selectors,'argv':argv,'actual_retained_popen_pid':p.pid,'actual_observed_exit':code,'exit_code':code,'started_at':start,'finished_at':datetime.now(timezone.utc).isoformat(),'methods_ran':int(m[1]) if m else None,'seconds':float(m[2]) if m else None,'source_sha256_before':before,'source_sha256_after':after,'source_unchanged':before==after,'passed':code==0 and m is not None and before==after,'full_validation_rerun':False,'QT_QPA_PLATFORM':'offscreen'}
(OUT/'process.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8');(OUT/'process.exit').write_text(str(code)+'\n',encoding='ascii');(OUT/'execution-runner.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({k:v for k,v in record.items() if not k.startswith('source_sha')},ensure_ascii=False))
if not record['passed']:print(error[-8000:])
raise SystemExit(0 if record['passed'] else 1)
