"""Explicit root-only five-module necessary producer, never preparation execution."""
from pathlib import Path,PurePosixPath
from hashlib import sha256
from datetime import datetime,timezone
import argparse,json,subprocess,sys,os,runpy
ROOT=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file())
PARENT='c2b78e4aa4136fe739067b5ccf9d13b595142320'
CANONICAL='scripts/verify_direct_map_window_303.py'
BINDINGS_PUBLIC='verification/sections/303-preparation/historical-source-inputs/local-public-bindings.json'
BINDINGS_SHA256='df86f3604392ad20e6f20b5a796277ce1796eb7d6ded031ddfab38b2e5522d05'
MODULES=['tests.test_direct_landmark_303','tests.test_direct_landmark_294','tests.test_direct_landmark_288','tests.test_direct_landmark_mapping','tests.test_map_projection_048']
HISTORICAL_TEST_PINS={'tests/test_direct_landmark_294.py':'263cea49f3f19514a5fb6be72a3dc42926ba4cab6007bbc14d21a489a07c1f52','tests/test_map_projection_048.py':'b2454d2c5c53a3b81164cce528f6dcd5c9f99aa2b0a3027b721e23aa50e145de'}
LOCAL_PUBLIC_BINDINGS=[{'local_path': '.cache/batch-048-before/rouge/data/battle-map-projections.json', 'public_path': 'verification/sections/303-preparation/historical-source-inputs/legacy-cache/batch-048-before/rouge/data/battle-map-projections.json', 'sha256': 'bf098d817f9e978d0198ea59aa3c34a0ccba3217d0085bd9e6cec03f51b1a9f4', 'bytes': 16432}, {'local_path': '.cache/research/map-projection-048/calibration-input.json', 'public_path': 'verification/sections/303-preparation/historical-source-inputs/legacy-cache/research/map-projection-048/calibration-input.json', 'sha256': '52423463da6d936027b7eb9c04b062032c00d4eeeba65b7ce435ddb2a775c514', 'bytes': 8357}, {'local_path': '.cache/research/map-projection-048/ro6_n_3_4-fit.json', 'public_path': 'verification/sections/303-preparation/historical-source-inputs/legacy-cache/research/map-projection-048/ro6_n_3_4-fit.json', 'sha256': '45650cd79e5ca7e64b9ec7be68a93999117e60e6997f5d94eafcbe156d4cc82c', 'bytes': 4208}, {'local_path': '.cache/research/map-projection-048/ro6_n_3_6-fit.json', 'public_path': 'verification/sections/303-preparation/historical-source-inputs/legacy-cache/research/map-projection-048/ro6_n_3_6-fit.json', 'sha256': 'd3fdcd3dddbf0b850fb0d0febc17f879a39352abbe257ac105ad9ac41a9c9e8d', 'bytes': 3550}, {'local_path': '.cache/research/map-projection-048/ro6_n_2_3-fit.json', 'public_path': 'verification/sections/303-preparation/historical-source-inputs/legacy-cache/research/map-projection-048/ro6_n_2_3-fit.json', 'sha256': 'f8856ae9fcdf770eec0ac70379591704ac0a7589d2cfa865fcb2f2e188bf7920', 'bytes': 2954}, {'local_path': '.cache/research/map-projection-048/ro6_n_2_4-fit.json', 'public_path': 'verification/sections/303-preparation/historical-source-inputs/legacy-cache/research/map-projection-048/ro6_n_2_4-fit.json', 'sha256': '43bc3ddc9f1b9fb8892a235709ae2a44b002271ab2a98966d37ca1517dfce6b5', 'bytes': 3737}, {'local_path': '.cache/research/map-projection-048/ro6_t_1-fit.json', 'public_path': 'verification/sections/303-preparation/historical-source-inputs/legacy-cache/research/map-projection-048/ro6_t_1-fit.json', 'sha256': '19c059b8f3054a162651d78827e00cc5c3f4d1e3c0c7ab77c3bed44575b325ff', 'bytes': 3012}, {'local_path': '.cache/research/map-projection-048/ro6_n_3_5-fit.json', 'public_path': 'verification/sections/303-preparation/historical-source-inputs/legacy-cache/research/map-projection-048/ro6_n_3_5-fit.json', 'sha256': '559557c0cb75b5ac506a01be70a2a56f9464b68537178ac8ae925e251bdb1ce0', 'bytes': 3711}, {'local_path': '.cache/game-data/levels/obt/roguelike/ro6/level_rogue6_3-4.json', 'public_path': 'research/p3-spawn-candidates-299/levels/a890d1b5061475e594844c9275510631256b00c97f852717f8750fdc696659c7.json', 'sha256': 'a890d1b5061475e594844c9275510631256b00c97f852717f8750fdc696659c7', 'bytes': 109196}, {'local_path': '.cache/game-data/levels/obt/roguelike/ro6/level_rogue6_3-6.json', 'public_path': 'research/p3-spawn-candidates-299/levels/2d2e89306c3d3c4a2a6c21f71b3828f66cb7a7996ab149faaad043d4867e8296.json', 'sha256': '2d2e89306c3d3c4a2a6c21f71b3828f66cb7a7996ab149faaad043d4867e8296', 'bytes': 233958}]
def public(name):
 pure=PurePosixPath(name)
 if pure.is_absolute()or'..'in pure.parts or'.cache'in pure.parts or'\\'in name or':'in name:raise ValueError('Standard source maps contain only exact public relative paths.')
 p=ROOT.joinpath(*pure.parts)
 if not p.is_file()or p.is_symlink()or not p.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Regular public source required: '+name)
 return p
def digest(path):return sha256(path.read_bytes()).hexdigest()
def source_pin(value):
 if type(value)is str and len(value)==64:return value,None
 if type(value)is dict and type(value.get('sha256'))is str and type(value.get('bytes'))is int:return value['sha256'],value['bytes']
 raise ValueError('Explicit actual promotion SHA/bytes required.')
def main(args):
 if not args.execute:raise RuntimeError('Cache preparation only. Root must explicitly execute after promotion/freeze.')
 branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()
 parent=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
 if branch!='codex/p2-development'or parent!=args.expected_parent or parent!=PARENT:raise RuntimeError('Actual branch/source parent changed.')
 bindings_path=public(BINDINGS_PUBLIC)
 if digest(bindings_path)!=BINDINGS_SHA256:raise ValueError('Reviewed public local-input binding manifest changed.')
 binding_record=json.loads(bindings_path.read_bytes())
 if binding_record['section']!=303 or binding_record['bindings']!=LOCAL_PUBLIC_BINDINGS:raise ValueError('The complete ten original local/public bindings changed.')
 promotion_path=public(args.promotion_receipt);promotion=json.loads(promotion_path.read_bytes())
 if promotion['section']!=303 or promotion['parent_commit']!=PARENT:raise ValueError('Wrong actual root promotion receipt.')
 promoted=promotion['promoted']
 if type(promoted)is not dict or not promoted:raise ValueError('Actual root functional promotion required.')
 if promotion['historical_test_maintenance']!=HISTORICAL_TEST_PINS:raise ValueError('Root historical maintenance map differs from the exact reviewed two files.')
 pins=dict(promoted)
 for name,value in promotion.get('existing_production_changes',{}).items():
  if name in pins and source_pin(pins[name])!=source_pin(value):raise ValueError('Conflicting root source pins.')
  pins[name]=value
 for name,value in HISTORICAL_TEST_PINS.items():
  if digest(public(name))!=value:raise ValueError('Reviewed exact historical maintenance changed: '+name)
 for name,value in pins.items():
  p=public(name);expected,length=source_pin(value)
  if digest(p)!=expected or(length is not None and p.stat().st_size!=length):raise ValueError('Actual promoted source changed: '+name)
 destination=(ROOT/args.receipt_directory).resolve()
 if not destination.is_relative_to((ROOT/'verification/sections').resolve())or destination.exists():raise ValueError('New exclusive public receipt directory required.')
 names=set(p.relative_to(ROOT).as_posix()for p in ROOT.glob('rouge/**/*.py'))|set(p.relative_to(ROOT).as_posix()for p in ROOT.glob('rouge/data/*.json'))
 names|={'tests/'+module.split('.')[-1]+'.py'for module in MODULES}
 names|=set(runpy.run_path(str(public(CANONICAL)))['bound_files']())
 names|=set(pins)|set(HISTORICAL_TEST_PINS)|{args.promotion_receipt,BINDINGS_PUBLIC}
 names|={'scripts/extend_direct_landmark_303.py','scripts/extend_direct_landmark_294.py','scripts/extend_direct_landmark_288.py',
  'scripts/build_fixed_landmark_references.py','scripts/extend_fixed_map_projections.py','scripts/map_fit_replay.py'}
 for folder in('research/p3-map-direct-ground-303','research/p3-map-direct-checkpoints-294','research/p3-map-direct-road-288','research/p3-direct-ground-current'):
  names|={p.relative_to(ROOT).as_posix()for p in(ROOT/folder).rglob('*')if p.is_file()}
 # Original048 really consumes local public historical files. The standard
 # map binds exact public counterparts; the separate ledger below truthfully
 # guards the unchanged local runtime paths before AND after the real tests.
 names|={row['public_path']for row in LOCAL_PUBLIC_BINDINGS}
 # Preserve every image actually consumed by old048/288/direct-floor widgets,
 # without sweeping an unrelated private source/cache directory.
 battle=json.loads(public('rouge/data/battle-previews.json').read_bytes())['stages']
 source_stage_ids=('ro6_n_3_4','ro6_e_3_4','ro6_n_3_6','ro6_e_3_6','ro6_t_1','ro6_t_3','ro6_e_t_3','ro6_n_6_2','ro6_e_6_2','ro6_n_4_4','ro6_e_4_4')
 names|={'rouge/data/'+battle[sid]['image']['file']for sid in source_stage_ids}
 public_paths={name:public(name)for name in sorted(names)}
 def hashes():return{name:digest(p)for name,p in public_paths.items()}
 def local_readback():
  values={};sizes={}
  for row in LOCAL_PUBLIC_BINDINGS:
   local=ROOT/row['local_path'];copy=public_paths[row['public_path']]
   if not local.is_file()or local.is_symlink()or not local.resolve().is_relative_to((ROOT/'.cache').resolve()):raise ValueError('Required actual local public historical source unavailable.')
   a,b=local.read_bytes(),copy.read_bytes()
   if a!=b or len(a)!=row['bytes']or sha256(a).hexdigest()!=row['sha256']:raise ValueError('Local/public original bytes differ: '+row['local_path'])
   values[row['local_path']]=sha256(a).hexdigest();sizes[row['local_path']]=len(a)
  return values,sizes
 before=hashes();local_before,local_size_before=local_readback()
 started=datetime.now(timezone.utc).isoformat();destination.mkdir(parents=True,exist_ok=False)
 argv=[sys.executable,'-B','-X','utf8','-m','unittest','-v',*MODULES];timeout=False
 with(destination/'stdout.txt').open('xb')as out,(destination/'stderr.txt').open('xb')as err:
  try:
   process=subprocess.run(argv,cwd=ROOT,stdout=out,stderr=err,timeout=300,env=dict(os.environ,QT_QPA_PLATFORM='offscreen',PYTHONDONTWRITEBYTECODE='1'))
   exit_code=process.returncode
  except subprocess.TimeoutExpired:timeout=True;exit_code=124
 after=hashes();local_error=None
 try:local_after,local_size_after=local_readback()
 except(Exception)as error:local_after={};local_size_after={};local_error=repr(error)
 stable=before==after and local_before==local_after and local_size_before==local_size_after and local_error is None
 record={'section':303,'kind':'necessary_change_related_tests_not_full_suite','argv':argv,'modules':MODULES,
  'promotion_receipt':args.promotion_receipt,'promotion_receipt_sha256':before[args.promotion_receipt],
  'source_commit_before':parent,'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),
  'exit_code':exit_code,'timed_out':timeout,'source_sha256_before':before,'source_sha256_after':after,'source_unchanged':stable,
  'local_public_input_bindings':LOCAL_PUBLIC_BINDINGS,'local_public_input_sha256_before':local_before,'local_public_input_sha256_after':local_after,
  'local_public_binding_manifest':BINDINGS_PUBLIC,'local_public_binding_manifest_sha256':BINDINGS_SHA256,
  'local_public_input_bytes_before':local_size_before,'local_public_input_bytes_after':local_size_after,
  'local_public_input_binding_error_after':local_error,'original_test_runtime_paths_redirected':False,
  'historical_public_replay_not_private_original_samples':True,'game_sampling_verified':False,'chat_verified':False,'full_suite_rerun':False,'full_scope_reduced':False}
 with(destination/'process.json').open('x',encoding='utf8')as stream:stream.write(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({'section':303,'actual_exit':exit_code,'source_unchanged':stable,'public_source_files':len(before),
  'local_public_input_bindings':len(LOCAL_PUBLIC_BINDINGS),'receipt':str(destination/'process.json')},ensure_ascii=False))
 return exit_code if stable else 97
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--execute',action='store_true')
 parser.add_argument('--expected-parent',required=True);parser.add_argument('--receipt-directory',required=True);parser.add_argument('--promotion-receipt',required=True)
 raise SystemExit(main(parser.parse_args()))
