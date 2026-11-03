from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,subprocess
ROOT=Path(__file__).resolve().parents[1]
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
assert git('branch','--show-current')=='codex/p2-development'
parent='c2b78e4aa4136fe739067b5ccf9d13b595142320'
assert git('rev-parse','HEAD')==git('rev-parse','origin/codex/p2-development')==parent
assert not git('status','--porcelain')
cp_path=ROOT/'DEVELOPMENT_CHECKPOINT.json';cp=json.loads(cp_path.read_bytes());assert cp['completed_sections']==302
request=ROOT/'.cache/p3-303-map-candidates/logical-reader-requests-all-lowland.json'
assert sha256(request.read_bytes()).hexdigest()=='c5a5ca22b11b36875c8890e8cce3a1f7d465925c7ddb7320de3963bd0b35854a'
base=ROOT/'verification/sections/303-preparation';base.mkdir(parents=True,exist_ok=True)
scope={'section':303,'status':'implementation_started_not_completed','parent_commit':parent,
 'at_utc':datetime.now(timezone.utc).isoformat(),'remaining_todo':'P3 fixed battle map location correspondence and independent landmark verification',
 'new_player_capability':'Show independently readable exact LOWLAND floor/road cells from 畸症 and 本性难移 on their fixed original maps, including supported MOVE checkpoints; unreadable or disagreeing positions remain unmarked.',
 'requested_scope':{'original_images':2,'stage_ids':['ro6_b_6','ro6_n_2_3','ro6_e_2_3'],'all_source_eligible_cells':89,'cells_by_image':{'ro6_b_6':55,'ro6_n_2_3':34},'accepted_cells':None},
 'evidence':{'source_request':'.cache/p3-303-map-candidates/logical-reader-requests-all-lowland.json','source_request_sha256':sha256(request.read_bytes()).hexdigest(),'source_inventory':'.cache/p3-303-map-candidates/candidate-inventory.json','source_ready':'.cache/p3-303-map-candidates/ALL_LOWLAND_READY.json'},
 'acceptance':['Two separate fresh-context visual readers inspect original PNGs and full original grid; freeze all89 rows before comparison. No old projection/readings or coordinate exchange.',
 'Retain both first complete readings, all nulls and every comparison. Accept only finite matching floor/road direct observations within the existing exact4 original-pixel gate. Keep A point without adjustment/averaging.',
 'Preserve all prior58 exact records, explicit alias image filename/PNG SHA/Git blob/level/grid/dimensions and existing LOWLAND type restrictions.',
 'Only accepted exact integer cells project; rejected/unlisted/noninteger/out-of-range/raised surfaces do not inherit markers, inverse or segments.',
 'Real native tests across actual three stage aliases and three sizes, map click/accepted MOVE correspondence where source supports it, same-geometry pixel evidence, real reading/selection refresh preservation; no actual game or chat.',
 'Historical294 replay and048 unaccepted-plane guards stay meaningful; archive original assertions and any precise compatibility change, do not skip modules or weaken current gates.',
 'Update original visible responsive test app, keep private5 paths; publish sources, original readings, real receipts, requirements and index together, ordinary push and actual remote blobs verified.'],
 'not_claimed':['Whole-map or all-terrain calibration','Highland surface, portal footpoints, spawn offsets or actual enemy positions','Inverse or route segments from sparse centers','New game采样 or chat','P3/P2/P1 completion'],
 'whole_map_remaining_scope_unchanged':[81,59],'prior_direct_scope':[10,18,58],
 'historical_full_validation':290,'next_periodic_full':305,'numeric_continuation_target':None}
target=base/'scope.json';assert not target.exists();target.write_text(json.dumps(scope,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
cache=ROOT/'.cache/p3-303-root';cache.mkdir(parents=True,exist_ok=True)
private=['.local/operator-state.json','.local/run-state.json','.local/desktop-chat/conversations.json','.local/desktop-chat/conversations.json.pending','local-settings.json']
baseline={'parent_commit':parent,'private_local_only':{n:sha256((ROOT/n).read_bytes()).hexdigest() if (ROOT/n).is_file() else None for n in private},'progress_sha256':sha256((ROOT/'PROJECT_PROGRESS.md').read_bytes()).hexdigest()}
(cache/'baseline-local-only.json').write_text(json.dumps(baseline,indent=2)+'\n',encoding='utf8')
cp['active_section']={'section':303,'scope':'verification/sections/303-preparation/scope.json','status':'implementation_not_yet_completed','functional_progress_claimed':False}
cp_path.write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'scope_started':303,'completed_sections':302,'requested_cells':89,'actual_accepted':None,'private_baseline_published':False}))
