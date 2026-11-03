from pathlib import Path
from hashlib import sha256
import json,subprocess
ROOT=Path(__file__).resolve().parents[1];DEST=ROOT/'verification/sections/297-preparation'
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='codex/p2-development'
assert not(DEST/'promotion.json').exists()
backend=ROOT/'.cache/p3-297-expedition-candidate';ui=ROOT/'.cache/p3-297-expedition-ui';integration=ROOT/'.cache/p3-297-expedition-root'
hand=json.loads((backend/'HANDOFF.json').read_bytes());u=json.loads((ui/'HANDOFF.json').read_bytes())
files={};copies={}
for name,pin in hand['promotion_allowlist'].items():
 raw=(ROOT/hand['candidate_root']/name).read_bytes();assert sha256(raw).hexdigest()==pin['sha256']and len(raw)==pin['bytes']
 files[name]=raw
for name,pin in u['promotion_files'].items():
 raw=(ui/name).read_bytes();assert sha256(raw).hexdigest()==pin['sha256'];assert name not in files;files[name]=raw
for name in ['rouge/node_catalog_view.py','rouge/player_node_information.py','tests/test_expedition_integration_297.py']:
 assert name not in files;files[name]=(integration/name).read_bytes()
source=ROOT/'.cache/p3-297-expedition-native-window/verify_expedition_results_window_297.py';raw=source.read_bytes()
assert sha256(raw).hexdigest()=='9300d083f817351cc2b36672b9615b0adcd99014f0ecbc362b78b7c7b0fc8168'
files['scripts/verify_expedition_results_window_297.py']=raw
scope=json.loads((DEST/'scope.json').read_bytes());existing=set(scope['before_existing_sources'])
assert len(files)==18
# The interrupted producer already wrote exactly these18 sources. Revalidate,
# do not overwrite them or hide the original archival-path failure.
for name,raw in files.items():
 assert (ROOT/name).read_bytes()==raw,name
for name,path in {'backend/HANDOFF.json':backend/'HANDOFF.json','ui/HANDOFF.json':ui/'HANDOFF.json',
 'ui/prepare_check.py':ui/'prepare_check.py','ui/process.json':ui/'process.json',
 'root/HANDOFF.json':integration/'HANDOFF.json','root/producer.py':ROOT/'.cache/prepare_root_expedition_297.py',
 'root/baseline-producer.py':ROOT/'.cache/freeze_baseline_297.py',
 'native/READY.json':ROOT/'.cache/p3-297-expedition-native-window/READY.json',
 'review/independent-backend-review.json':ROOT/'.cache/p3-297-independent-backend-review.json'}.items():
 copies[name]=path.read_bytes()
for folder in ['first-real-source-build','first-real-pure-api-tests']:
 path=backend/folder
 assert path.is_dir(),folder
 for p in path.rglob('*'):
  assert not p.is_symlink()
  if p.is_file():copies['backend/'+folder+'/'+p.relative_to(path).as_posix()]=p.read_bytes()
research=ROOT/'.cache/p3-297-gap-research';ready=json.loads((research/'READY.json').read_bytes())
for name,pin in ready['files'].items():
 raw=(research/name).read_bytes();assert sha256(raw).hexdigest()==pin['sha256'];copies['research-originals/'+name]=raw
copies['research-originals/READY.json']=(research/'READY.json').read_bytes()
for name,raw in copies.items():
 path=DEST/name;assert not path.exists();path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
record={'section':297,'kind':'ACTUAL_ROOT_SOURCE_PROMOTION_NOT_ACCEPTANCE',
 'promoted':{n:sha256(v).hexdigest()for n,v in files.items()},'existing_production_changes':sorted(existing),
 'archived_inputs':{n:{'sha256':sha256(v).hexdigest(),'bytes':len(v)}for n,v in copies.items()},
 'map_candidates_promoted':False,'tests_GUI_or_private_operations_performed_by_this_script':False}
(DEST/'promotion.json').write_bytes((json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'promoted_paths':len(files),'archived_public_inputs':len(copies),'tests_executed':False}))
