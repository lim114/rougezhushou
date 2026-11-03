from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from rouge.battle_preview import battle_data,DATA
from rouge.map_projection import grid_digest
from scripts.extend_fixed_map_projections import fit
BASE=ROOT/'.cache/p3-297-ground-candidate/research/p3-map-ground-challenges-297'
assert not BASE.exists();BASE.mkdir(parents=True)
def encode(x):return (json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def copy(name,path,pin=None):
 raw=path.read_bytes()
 if pin is not None:assert sha256(raw).hexdigest()==pin,(name,'source pin')
 (BASE/name).write_bytes(raw);return raw
fraw=copy('fit-seam-observations.json',ROOT/'.cache/p3-297-fit-seams/fit_observations.json','6229a58f8b918bacdb35810ad7dd6835d32277b871e5475d2582cbf1cd74f7ae')
hraw=copy('independent-holdout-observations.json',ROOT/'.cache/p3-297-independent-holdouts/observations.json','ae2ba58250e9cceccb0c95ace0e3f2daa29f40fbaa475c7d3085830986157006')
copy('fit-sourcepins.json',ROOT/'.cache/p3-297-fit-seams/fit_sourcepins.json','cdf28e03decb3c80caf890a988498252db8a427f690c8becd0bbe384d7e4e429')
copy('independent-holdout-README.md',ROOT/'.cache/p3-297-independent-holdouts/README.md')
copy('prior-projections.json',DATA/'battle-map-projections.json')
f=json.loads(fraw);h=json.loads(hraw)
assert not f['fit_executed'] and not f['matrix_or_prediction_computed'] and not f['independent_holdout_seen']
assert h['independence']['frozen_before_fit_comparison'] and not h['independence']['inspected_candidate_fit']
sources={};entries=[]
for author,held in zip(f['stages'],h['stages'],strict=True):
 sid=author['stage_id'];assert sid==held['stage_id'];stage=battle_data()['stages'][sid]
 assert sid in ('ro6_c_2','ro6_c_4')
 image=stage['image'];raw=(DATA/image['file']).read_bytes()
 assert sha256(raw).hexdigest()==image['sha256']==held['source_image']['sha256']==author['image']['sha256']
 assert len(raw)==image['bytes'] and sha256((DATA/'battle-previews.json').read_bytes()).hexdigest()==h['data_source']['sha256']
 assert stage['level_source']==held['sourcelevels']==author['level_source']
 level_name=sid+'-level.json';levelraw=copy(level_name,ROOT/author['level_local_file'],stage['level_source']['sha256'])
 rawlevel=json.loads(levelraw);assert rawlevel['mapData']['map']==stage['map'] and rawlevel['mapData']['tiles']==stage['tiles']
 assert held['grid']=={'map':stage['map'],'tiles':stage['tiles']}
 anchors=[[p['row'],p['col'],*p['observed_pixel'],p['cue']]for p in author['fit_seams']if p['observed_pixel'] is not None]
 checks=[[p['row'],p['col'],*p['pixel'],p['cue']]for p in held['observations']]
 assert len(anchors)>=8 and len(checks)>=10
 assert all(r%1==c%1==.5 for r,c,*_ in anchors)
 assert len({r for r,c,*_ in anchors})>=3 and len({c for r,c,*_ in anchors})>=3
 assert len({r for r,c,*_ in checks})>=3 and len({c for r,c,*_ in checks})>=3
 for row,col,*_ in checks:
  assert type(row)is int and type(col)is int
  tile=stage['tiles'][stage['map'][row][col]];assert tile['heightType']=='LOWLAND'and tile['tileKey']in('tile_floor','tile_road')
 assert {(r,c)for r,c,*_ in anchors}.isdisjoint((r,c)for r,c,*_ in checks)
 sources[sid]={'image':image,'level_source':stage['level_source'],'level_local_file':level_name,'grid_sha256':grid_digest(stage),
  'rows':len(stage['map']),'cols':len(stage['map'][0]),'fit_readings':len(anchors),'unreadable_fit_readings':len(author['fit_seams'])-len(anchors),
  'heldout_centers':len(checks),'heldout_rows':held['coverage']['rows'],'heldout_cols':held['coverage']['cols']}
 entries.append({'id':sid,'aliases':[],'anchors':anchors,'checks':checks,
  'grid_correspondence':'Display map row0 at top and col0 at left; half-integer source wood-ground seams fit, independent integer LOWLAND centers check.',
  'independent_coverage':'Only recorded LOWLAND centers independently read; unmeasured rows/columns, outer borders, elevated surfaces and portal foot offsets remain extrapolated or unknown.'})
input_row={'kind':'FROZEN_SEPARATE_FIT_AND_INDEPENDENT_HELDOUT_INPUTS_BEFORE_FIRST_FIT','at_utc':datetime.now(timezone.utc).isoformat(),
 'pixel_tolerance':4,'calibrations':entries,'observations_adjusted':False,'holdouts_used_in_fit':False,
 'independent_contexts_are_agents_not_human_absolute_validation':True}
(BASE/'calibration-input.json').write_bytes(encode(input_row))
results=[fit(e)for e in entries]
(BASE/'initial-fit-results.json').write_bytes(encode(results))
prior=json.loads((BASE/'prior-projections.json').read_bytes());assert(len(prior['calibrations']),len(prior['stages']))==(12,24)
receipt={'kind':'ACTUAL_FIRST_GROUND_FIT_NOT_PRODUCT_ACCEPTANCE','created_utc':datetime.now(timezone.utc).isoformat(),
 'pixel_tolerance':4,'source_game_commit':'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add',
 'source_resource_commit':'d0b5af0b004b044d322397ce5ae79632b6d9fcdd','sources':sources,
 'fit_method':'Existing scripts.extend_fixed_map_projections.fit; cv2.findHomography method0; all frozen readable seam points, no RANSAC/exclusion/refit/tuning; heldout centers never fit.',
 'inputs_before_fit':{'fit-seam-observations.json':sha256(fraw).hexdigest(),'independent-holdout-observations.json':sha256(hraw).hexdigest(),
  'calibration-input.json':sha256((BASE/'calibration-input.json').read_bytes()).hexdigest()},
 'results':[{'id':r['id'],'accepted':r['accepted'],'heldout_checks':len(r['checks']),
   'max_error_px':max(p['error_px']for p in r['checks'])}for r in results],
 'production_or_private_changed':False,'Qt_game_chat_or_Git_mutation':False,'product_acceptance_passed':False,
 'raw_source_copyright':'Original game art belongs to Hypergryph; no new license asserted.',
 'scope':'Nominal planar LOWLAND ground-grid reference only; source-image reading agreement on measured centers, not absolute accuracy, elevated surfaces, portal roofs or feet, actual spawn offsets, random ranges, hitboxes, pathfinding, live trajectories or timings.'}
(BASE/'source-receipt.json').write_bytes(encode(receipt))
print(json.dumps({'actual_first_fit_results':receipt['results'],'raw_observations_adjusted':False,'product_or_private_changed':False},ensure_ascii=False))
