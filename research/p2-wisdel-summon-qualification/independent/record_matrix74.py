from pathlib import Path
import sys,json,gzip,hashlib,copy,collections
sys.dont_write_bytecode=True
OUT=Path(__file__).parent
side=sys.argv[1];PACKAGE=OUT/('baseline70-public' if side=='baseline' else 'draft74-independent')
sys.path.insert(0,str(PACKAGE))
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.reporting import format_report
cases=[]
def add(group,**kw):cases.append({'group':group,'input':{'operator':'char_1035_wisdel','base_attack':1000,'window_seconds':1,**kw}})
for elite in [0,1,2]:
 for skill in [1,2,3]:
  for rank in range(1,11):
   for potential in [1,6]:
    for mode in ['frames','continuous']:
     for count,casts in [(0,0),(3,1)]:
      add('qualification_all_ranks',elite=elite,level=1,skill=skill,skill_rank=rank,potential=potential,timing_mode=mode,ghost_count=count,ghost_casts=casts)
for level in [59,60]:
 for stage in [1,2,3]:
  for skill in [1,2,3]:
   for rank in [1,6,7,10]:
    for mode in ['frames','continuous']:
     for count,casts in [(0,0),(3,1)]:
      add('module_boundary_original_route_only',elite=2,level=level,skill=skill,skill_rank=rank,timing_mode=mode,module_id='uniequip_002_wisdel',module_level=stage,ghost_count=count,ghost_casts=casts)
for elite,skill,rank in [(0,1,7),(1,2,7),(2,1,10),(2,2,10),(2,3,1),(2,3,6),(2,3,7),(2,3,10)]:
 for mode in ['frames','continuous']:
  for context in [{'window_seconds':0},{'timing':{'target_disappears_seconds':0}},{'timing':{'target_windows':[]}},{'window_seconds':10}]:
   for count,casts in [(0,0),(3,1)]:
    add('observation_and_unknown_sources',elite=elite,skill=skill,skill_rank=rank,timing_mode=mode,ghost_count=count,ghost_casts=casts,**context)
for elite,skill,rank in [(0,1,7),(2,3,10)]:
 for mode in ['frames','continuous']:
  for count,casts in [(0,'bad'),('0.0',None),('1.0','1.0'),(3,'1000.0'),(None,0),('false',0),(True,0),(4,0),(3,None),(3,'bad'),(3,True),(3,-1)]:
   add('existing_declarations_and_errors',elite=elite,skill=skill,skill_rank=rank,timing_mode=mode,ghost_count=count,ghost_casts=casts)
for op,skill,rank in [('char_1038_whitw2',1,7),('char_328_cammou',1,7),('char_1038_whitw2',3,10)]:
 for mode in ['frames','continuous']:
  add('other_owner_inactive_ghost_fields',operator=op,skill=skill,skill_rank=rank,timing_mode=mode,ghost_count='bad',ghost_casts=None)
rows=[]
for i,c in enumerate(cases):
 try:
  r=calculate_damage(copy.deepcopy(c['input']));o={'accepted':True,'result':r,'formatted_estimate':format_estimate(r),'formatted_report':format_report(r),'technical_report':format_report(r,technical=True)}
 except Exception as e:o={'accepted':False,'error_type':type(e).__name__,'error_message':str(e)}
 rows.append({'key':i,**c,'outcome':o})
raw=json.dumps(rows,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode();packed=gzip.compress(raw,mtime=0)
(OUT/f'{side}74-whole-outcomes.json.gz').write_bytes(packed)
receipt={'side':side,'baseline_head':'552a6f3ab8b16cce49a9cf0de1e247c3ff49e3a9','cases':len(rows),'actual_public_calculate_calls':len(rows),'accepted':sum(r['outcome']['accepted'] for r in rows),'errors':sum(not r['outcome']['accepted'] for r in rows),'groups':dict(collections.Counter(r['group'] for r in rows)),'source_engine_sha256':hashlib.sha256((PACKAGE/'rouge/operator_engine.py').read_bytes()).hexdigest(),'compression':{'gzip_sha256':hashlib.sha256(packed).hexdigest(),'gzip_bytes':len(packed),'raw_sha256':hashlib.sha256(raw).hexdigest(),'raw_bytes':len(raw),'roundtrip_verified':gzip.decompress(packed)==raw},'reports':'Complete standard/technical report and estimate strings with full result or exact exception shape; strict typed JSON','rolling_root_source_used':False,'native_clock_claim':False}
(OUT/f'{side}74-matrix-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False))
