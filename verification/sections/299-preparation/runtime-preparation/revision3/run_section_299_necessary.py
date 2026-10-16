"""Root-only necessary299 producer; preparation never invokes this file.
Explicit --execute is required after the canonical native script is promoted.
No full suite; QT_QPA_PLATFORM=offscreen and existing tests use public temp state.
"""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import argparse,json,subprocess,sys,os,runpy
ROOT=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file())
CANONICAL='scripts/verify_spawn_candidates_window_299.py'
MODULES=['tests.test_spawn_candidates_299','tests.test_spawn_candidates_view_299',
 'tests.test_spawn_candidates_integration_299','tests.test_battle_planning_161_170',
 'tests.test_battle_preview_039','tests.test_player_battle_information_286',
 'tests.test_player_information_view_286','tests.test_battle_entry_integration_296',
 'tests.test_event_preview_filters_292','tests.test_battle_event_references_296',
 'tests.test_battle_entry_compatibility_299']
def main(args):
 if not args.execute:raise RuntimeError('Preparation only. Root must explicitly supply --execute after final promotion.')
 branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
 parent=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 if branch!='codex/p2-development'or parent!=args.expected_parent:raise RuntimeError('Expected branch/parent changed.')
 destination=(ROOT/args.receipt_directory).resolve()
 if not destination.is_relative_to((ROOT/'verification/sections').resolve())or destination.exists():
  raise ValueError('Use a new exclusive public sections receipt directory.')
 names=set(ROOT.glob('rouge/**/*.py'))|set(ROOT.glob('rouge/data/*.json'))
 names|={ROOT/('tests/'+module.split('.')[-1]+'.py')for module in MODULES}
 namespace=runpy.run_path(str(ROOT/CANONICAL))
 names|={ROOT/name for name in namespace['bound_files']()}
 names.add(ROOT/'scripts/build_spawn_candidates_299.py')
 if not all(p.is_file()and not p.is_symlink()and p.resolve().is_relative_to(ROOT.resolve())for p in names):
  raise ValueError('Regular public selected sources required.')
 def hashes():return{p.relative_to(ROOT).as_posix():sha256(p.read_bytes()).hexdigest()for p in sorted(names)}
 before=hashes();started=datetime.now(timezone.utc).isoformat();destination.mkdir(parents=True,exist_ok=False)
 argv=[sys.executable,'-B','-X','utf8','-m','unittest','-v',*MODULES];timeout=False
 with(destination/'stdout.txt').open('xb')as out,(destination/'stderr.txt').open('xb')as err:
  try:
   process=subprocess.run(argv,cwd=ROOT,stdout=out,stderr=err,timeout=300,
    env=dict(os.environ,QT_QPA_PLATFORM='offscreen',PYTHONDONTWRITEBYTECODE='1'))
   exit_code=process.returncode
  except subprocess.TimeoutExpired:timeout=True;exit_code=124
 after=hashes()
 record={'section':299,'kind':'necessary_change_related_tests_not_full_suite','argv':argv,'modules':MODULES,
  'source_commit_before':parent,'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),
  'exit_code':exit_code,'timed_out':timeout,'source_sha256_before':before,'source_sha256_after':after,'source_unchanged':before==after,
  'game_sampling_verified':False,'chat_verified':False,'full_scope_reduced':False,'full_suite_rerun':False}
 with(destination/'process.json').open('x',encoding='utf8')as stream:stream.write(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'section':299,'actual_exit':exit_code,'source_unchanged':before==after,'source_files':len(before),
  'receipt':str(destination/'process.json')},ensure_ascii=False))
 return exit_code if before==after else 97
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--receipt-directory',required=True)
 parser.add_argument('--expected-parent',required=True);parser.add_argument('--execute',action='store_true')
 raise SystemExit(main(parser.parse_args()))
