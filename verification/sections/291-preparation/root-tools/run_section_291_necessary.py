from datetime import datetime,timezone
from hashlib import sha256
from pathlib import Path
import json,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/sys.argv[1];DEST.mkdir(parents=True,exist_ok=False)
modules=['tests.test_peace_guardian_results_291','tests.test_resident_location_references_291',
 'tests.test_peace_guardian_integration_291','tests.test_resident_reference_signals_291',
 'tests.test_choice_recruitment_integration_290','tests.test_event_planning',
 'tests.test_node_map_navigation','tests.test_readable_map_047','tests.test_node_catalog_view']
paths=set(ROOT.glob('rouge/**/*.py'))|set(ROOT.glob('rouge/data/*.json'))
paths|={ROOT/('tests/'+m.split('.')[-1]+'.py') for m in modules}
paths|=set(ROOT.glob('research/p3-peace-guardian-results-291/*'))
paths|=set(ROOT.glob('verification/sections/291-preparation/location-fixtures/**/*'))
paths|={ROOT/'verification/sections/291-preparation/before-integration/rouge/event_planning.py'}
paths|={ROOT/'scripts/verify_peace_guardian_window_291.py',ROOT/'scripts/build_peace_guardian_results_291.py'}
def hashes():return {p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest() for p in sorted(paths) if p.is_file()}
before=hashes();env=dict(os.environ,QT_QPA_PLATFORM='offscreen',PYTHONDONTWRITEBYTECODE='1')
argv=[sys.executable,'-B','-X','utf8','-m','unittest','-v',*modules]
started=datetime.now(timezone.utc).isoformat()
with (DEST/'stdout.txt').open('xb') as out,(DEST/'stderr.txt').open('xb') as err:
 result=subprocess.run(argv,cwd=ROOT,env=env,stdout=out,stderr=err,timeout=480)
after=hashes()
report={'kind':'necessary_change_related_tests_not_full_suite','section':291,'argv':argv,'modules':modules,
 'source_commit_before':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),'exit_code':result.returncode,
 'source_sha256_before':before,'source_sha256_after':after,'source_unchanged':before==after,
 'game_sampling_verified':False,'chat_verified':False,'full_scope_reduced':False,'full_suite_rerun':False}
(DEST/'process.json').write_bytes((json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({'actual_exit':result.returncode,'source_unchanged':before==after,'receipt':str(DEST/'process.json')}))
raise SystemExit(result.returncode if before==after else 97)
