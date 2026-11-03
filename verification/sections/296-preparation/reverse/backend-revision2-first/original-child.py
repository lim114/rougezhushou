"""Actual isolated cache backend acceptance. Never imports Qt or writes live files."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import argparse,importlib.util,json,os,sys,time,traceback,unittest

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--receipt',required=True);args=parser.parse_args()
 dest=Path(args.receipt);assert not dest.exists()
 public=HERE/'backend-public-root';public.mkdir(exist_ok=False)
 candidate=HERE/'candidate';manifest_name='research/p3-battle-event-references-296/source-manifest.json'
 raw=(candidate/manifest_name).read_bytes();manifest=json.loads(raw)
 for name,pin in manifest['files'].items():
  source=candidate/name if(candidate/name).is_file()else ROOT/name
  content=source.read_bytes();assert len(content)==pin['bytes']and sha256(content).hexdigest()==pin['sha256']
  target=public/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(content)
 target=public/manifest_name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
 sys.path.insert(0,str(ROOT))
 import rouge
 spec=importlib.util.spec_from_file_location('rouge.battle_event_references',candidate/'rouge/battle_event_references.py')
 model=importlib.util.module_from_spec(spec);sys.modules[spec.name]=model;setattr(rouge,'battle_event_references',model);spec.loader.exec_module(model)
 model.ROOT=public
 durations=[];results=[]
 for number in range(5):
  start=time.perf_counter();value=model.stage_event_references('ro6_t_3');elapsed=time.perf_counter()-start
  durations.append({'phase':'cold_parse_and_hash'if number==0 else'warm_parse_cache_still_rehash_all_bytes','milliseconds':elapsed*1000})
  results.append(value['status']);assert value['status']=='documented_reference',value
 spec=importlib.util.spec_from_file_location('tests._candidate_battle_event_references_296',candidate/'tests/test_battle_event_references_296.py')
 tests=importlib.util.module_from_spec(spec);sys.modules[spec.name]=tests;spec.loader.exec_module(tests)
 suite=unittest.defaultTestLoader.loadTestsFromModule(tests)
 actual=unittest.TextTestRunner(stream=sys.stderr,verbosity=2).run(suite)
 qt=[name for name in sys.modules if name.startswith(('PySide6','PyQt5','PyQt6'))]
 row={'kind':'ACTUAL_CACHE_BACKEND_ONLY_NOT_PRODUCT_NATIVE_ACCEPTANCE','tests_run':actual.testsRun,
  'failures':len(actual.failures),'errors':len(actual.errors),'skipped':len(actual.skipped),
  'success':actual.wasSuccessful()and not qt,'Qt_modules_imported':qt,'actual_gui_game_chat_private_Git_operations':False,
  'model_sha256':sha256((candidate/'rouge/battle_event_references.py').read_bytes()).hexdigest(),
  'test_sha256':sha256((candidate/'tests/test_battle_event_references_296.py').read_bytes()).hexdigest(),
  'single_call_measurement':{'scope':'Isolated public clone, exact ro6_t_3; not application latency or real game performance',
   'samples':durations,'minimum_ms':min(r['milliseconds']for r in durations),'maximum_ms':max(r['milliseconds']for r in durations),
   'all_call_statuses':results,'every_call_rehashes_all_manifest_bytes':True,'no_threshold_asserted':True},
  'finished_utc':datetime.now(timezone.utc).isoformat()}
 with dest.open('xb')as f:f.write((json.dumps(row,ensure_ascii=False,indent=2)+'\n').encode())
 return 0 if row['success']else 1
if __name__=='__main__':raise SystemExit(main())
