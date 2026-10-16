from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,subprocess,sys,os,runpy
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/sys.argv[1];DEST.mkdir(parents=True,exist_ok=False)
modules=['tests.test_expedition_results_297','tests.test_expedition_results_view_297',
 'tests.test_expedition_integration_297','tests.test_event_planning','tests.test_player_node_information_286',
 'tests.test_node_catalog_view','tests.test_documented_item_integration_295','tests.test_battle_entry_integration_296']
paths=set(ROOT.glob('rouge/**/*.py'))|set(ROOT.glob('rouge/data/*.json'))
paths|={ROOT/('tests/'+m.split('.')[-1]+'.py')for m in modules}
ns=runpy.run_path(str(ROOT/'scripts/verify_expedition_results_window_297.py'))
paths|={ROOT/name for name in ns['bound_files']()}
paths.add(ROOT/'verification/sections/297-preparation/before-output-hashes.json')
assert all(p.is_file()and not p.is_symlink()for p in paths)
def hashes():return {p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest()for p in sorted(paths)}
before=hashes();start=datetime.now(timezone.utc).isoformat()
argv=[sys.executable,'-B','-X','utf8','-m','unittest','-v',*modules]
with(DEST/'stdout.txt').open('xb')as out,(DEST/'stderr.txt').open('xb')as err:
 result=subprocess.run(argv,cwd=ROOT,stdout=out,stderr=err,timeout=300,
  env=dict(os.environ,QT_QPA_PLATFORM='offscreen',PYTHONDONTWRITEBYTECODE='1'))
after=hashes()
row={'section':297,'kind':'necessary_change_related_tests_not_full_suite','argv':argv,'modules':modules,
 'source_commit_before':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 'started_utc':start,'finished_utc':datetime.now(timezone.utc).isoformat(),'exit_code':result.returncode,
 'source_sha256_before':before,'source_sha256_after':after,'source_unchanged':before==after,
 'game_sampling_verified':False,'chat_verified':False,'full_scope_reduced':False,'full_suite_rerun':False}
(DEST/'process.json').write_bytes((json.dumps(row,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'section':297,'actual_exit':result.returncode,'source_unchanged':before==after,
 'source_files':len(before),'receipt':str(DEST/'process.json')}))
raise SystemExit(result.returncode if before==after else 97)
