from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,math
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-map-direct-ground-308';OUT=ROOT/PACK
assert not OUT.exists();OUT.mkdir()
def enc(v):return (json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf8')
def read(p):return json.loads(p.read_bytes())
def pin(p):return {'bytes':p.stat().st_size,'sha256':sha256(p.read_bytes()).hexdigest()}
def copy(src,name):
 p=OUT/name;assert not p.exists();p.write_bytes((ROOT/src).read_bytes());return p
inputs=ROOT/'.cache/p3-308-reader-inputs';req=read(inputs/'REQUESTS.json');pins=read(inputs/'SOURCE_PINS.json')
for n,p in pins['files'].items():assert pin(inputs/n)==p
paths={'A':'.cache/p3-308-reader-A/READER_A_ORIGINAL.json','B':'.cache/p3-308-reader-b/READER_B_ORIGINAL.json'}
frozen={'A':'8b4ea818165eeaccf01d2790bd054af4bbd56af2611838a2577a412123f3fd9f','B':'b2e581f8033a6fa6150bc1c6043b52f2506c529f0be78b559d1b1c610dac3f21'}
readers={}
for label,src in paths.items():
 p=ROOT/src;assert pin(p)['sha256']==frozen[label];readers[label]=read(p)
 copy(src,'READER_'+label+'_ORIGINAL.json')
copy('.cache/p3-308-reader-A/READY_A_ORIGINAL.json','READER_A_READY_ORIGINAL.json')
copy('.cache/p3-308-reader-b/READY_B_ORIGINAL.json','READER_B_READY_ORIGINAL.json')
copy('.cache/p3-308-reader-inputs/REQUESTS.json','REQUEST_MANIFEST.json')
copy('.cache/p3-308-reader-inputs/SOURCE_PINS.json','ORIGINAL_INPUT_PINS.json')
for sid in('ro6_n_5_1','ro6_n_5_5'):copy('.cache/p3-308-reader-inputs/'+sid+'-grid.json','reader-grid-'+sid+'.json')
copy('rouge/data/fixed-landmark-references.json','prior-direct-references.json')
copy('rouge/data/battle-map-projections.json','prior-regular-projections.json')
battle=read(ROOT/'rouge/data/battle-previews.json')['stages'];stages={};links={};comparisons=[]
for label,r in readers.items():
 keys=r['source_pins']if label=='A'else{x['path']:x for x in r['source_pins']['files']}
 links[label]={}
 for name in keys:
  rawname=Path(name).name
  if rawname=='REQUESTS.json':target=PACK+'/REQUEST_MANIFEST.json'
  elif rawname.endswith('-grid.json'):target=PACK+'/reader-grid-'+rawname.replace('-grid.json','.json')
  else:target='rouge/data/battle-maps/'+rawname
  links[label][name]=target
  p=keys[name];assert pin(ROOT/target)=={'bytes':p['bytes'],'sha256':p['sha256']}
 assert len(links[label])==5
for group in req['groups']:
 sid=group['stage_id'];a=next(x for x in readers['A']['images']if x['stage_id']==sid);b=next(x for x in readers['B']['images']if x['stage_id']==sid)
 assert len(a['readings'])==len(b['readings'])==len(group['all_requests'])
 for alias in group['explicit_alias_records']:
  identity=alias['stage_id'];s=battle[identity]
  assert s['level_source']==alias['level_source']and s['image']==alias['image']
  stages[identity]={'image':s['image'],'level_source':s['level_source'],'level_file':'research/p3-spawn-candidates-299/levels/'+s['level_source']['sha256']+'.json','grid_size':[len(s['map']),len(s['map'][0])],'grid_sha256':alias['semantic_grid_sha256']}
 for r in group['all_requests']:
  ar=next(x for x in a['readings']if x['request_id']==r['request_id']);br=next(x for x in b['readings']if x['request_id']==r['request_id'])
  for rr in(ar,br):assert all(rr[k]==r[k]for k in('row','col','tile_key','request_id'))
  ap,bp=ar['observed_pixel'],br['pixel'];dist=math.dist(ap,bp)if ap is not None and bp is not None else None
  comparisons.append({'request_id':r['request_id'],'stage_id':sid,'row':r['row'],'col':r['col'],'original_A':ap,'original_B':bp,'unrounded_distance':dist,'accepted':dist is not None and dist<=4})
assert len(comparisons)==67 and len({x['request_id']for x in comparisons})==67
source={'section':308,'status':'BOTH_FIRST_COMPLETE_READINGS_FROZEN_BEFORE_FIRST_COMPARISON','agreement_tolerance_px':4,'all_source_eligible_requests':67,'both_first_complete_readings_frozen_before_comparison':True,'source_pixel_adjustments_after_comparison':0,'stages':stages,'reader_source_pin_links':links,'source_only_readers_not_human_gameplay_observers':True,'whole_map_gaps_unchanged':[81,59],'reader_originals':{label:{'original_path':paths[label],'public_copy':'READER_'+label+'_ORIGINAL.json','sha256':frozen[label]}for label in paths},'raw_shapes_differ_preserved_without_rewriting':True,'absolute_bitmap_accuracy_verified':False}
(OUT/'source-records.json').write_bytes(enc(source))
names=[p.relative_to(ROOT).as_posix()for p in OUT.iterdir()if p.is_file()]
names+=['rouge/data/battle-previews.json',*[v['image']['file']for v in []]]
names+=['rouge/data/'+s['image']['file']for s in stages.values()]+[s['level_file']for s in stages.values()]
manifest={'section':308,'all_source_eligible_requests':67,'agreement_tolerance_px':4,'files':{n:pin(ROOT/n)for n in sorted(set(names))},'source_paths_are_exact_public_files':True,'original_reader_bytes_preserved':True}
(OUT/'source-manifest.json').write_bytes(enc(manifest))
counts=[{'stage_id':g['stage_id'],'requested':len(g['all_requests']),'accepted':sum(c['accepted']for c in comparisons if c['stage_id']==g['stage_id']),'unknown_or_disagreed':sum(not c['accepted']for c in comparisons if c['stage_id']==g['stage_id'])}for g in req['groups']]
record={'section':308,'kind':'ACTUAL_FIRST_FROZEN_COMPARISON_NOT_PRODUCT_ACCEPTANCE','at_utc':datetime.now(timezone.utc).isoformat(),'source_manifest_sha256':pin(OUT/'source-manifest.json')['sha256'],'original_reader_sha256':frozen,'comparisons':comparisons,'per_image':counts,'accepted':sum(x['accepted']for x in comparisons),'rejected':sum(not x['accepted']for x in comparisons),'source_pixel_adjustments':0,'readers_are_agent_contexts_not_humans':True,'absolute_accuracy_verified':False}
prep=ROOT/'verification/sections/308-preparation'
(prep/'first-frozen-comparison.json').write_bytes(enc(record));(prep/'execution-source-seal.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({k:v for k,v in record.items()if k!='comparisons'},ensure_ascii=False))
