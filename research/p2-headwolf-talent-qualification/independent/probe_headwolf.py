from pathlib import Path
import sys,json,gzip,hashlib,copy
sys.dont_write_bytecode=True
OUT=Path(__file__).parent
FROZEN=OUT/'frozen70-public'
sys.path.insert(0,str(FROZEN))
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.catalog import catalog
from rouge.operator_engine import selected_talents
rows=[]
for elite,skills,ranks in [(0,[1],range(1,8)),(1,[1,2],range(1,8)),(2,[1,2,3],range(1,11))]:
 for potential in range(1,7):
  for skill in skills:
   for rank in ranks:
    for mode in ['frames','continuous']:
     p=catalog()['operators']['char_1038_whitw2']
     base={'operator':'char_1038_whitw2','skill':skill,'skill_rank':rank,'elite':elite,
           'potential':potential,'base_attack':1000,'window_seconds':1,'timing_mode':mode}
     selected,_=selected_talents(p,base)
     head=next((t for t in selected if t['name']=='头狼'),None)
     interval=head['values']['interval'] if head else 20
     for age in [0,3*interval-1,3*interval,3*interval+60]:
      scenario={**base,'deployment_elapsed_seconds':age}
      try:
       result=calculate_damage(copy.deepcopy(scenario))
       outcome={'result':result,'report':format_estimate(result)}
       drones=[c for c in result['components'] if c['name']=='浮游单元']
       summary={'drone_rows':[{k:c[k] for k in ['hits','per_hit','total','times_seconds','timing_reference'] if k in c} for c in drones],
                'drone_reference_hits':sum(c['hits'] for c in drones),'total_damage':result['total_damage'],
                'body_damage':sum(c['total'] for c in result['components'] if c['name']=='本体攻击')}
      except Exception as e:
       outcome={'error':{'type':type(e).__name__,'message':str(e)}};summary={}
      rows.append({'scenario':scenario,'head_talent_selected':head,'summary':summary,'outcome':outcome})
# Controls: each owner reference is examined without changing the implementation.
# E0 cannot acquire the locked talent regardless of deployment age; S1's described extra unit is preserved.
e0=[r for r in rows if r['scenario']['elite']==0]
e0_no_head=all(r['head_talent_selected'] is None for r in e0)
errors=[r for r in rows if 'error' in r['outcome']]
examples=[]
for elite,potential,skill,rank,mode in [(0,1,1,7,'frames'),(1,1,1,7,'frames'),(1,6,1,7,'frames'),(2,1,1,10,'frames'),(2,6,1,10,'frames'),(2,1,3,10,'frames')]:
 examples.extend(r for r in rows if all(r['scenario'][k]==v for k,v in [('elite',elite),('potential',potential),('skill',skill),('skill_rank',rank),('timing_mode',mode)]))
raw=json.dumps(rows,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
compressed=gzip.compress(raw,mtime=0)
(OUT/'headwolf-public-cases.json.gz').write_bytes(compressed)
(OUT/'headwolf-public-examples.json').write_text(json.dumps(examples,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
freeze=json.loads((OUT/'freeze70-public.json').read_text())
drift=[]
for name,r in freeze['files'].items():
 b=(FROZEN/name).read_bytes()
 if len(b)!=r['bytes'] or hashlib.sha256(b).hexdigest()!=r['sha256']:drift.append(name)
receipt={'head':freeze['head'],'source_engine_sha256':freeze['files']['rouge/operator_engine.py']['sha256'],
 'scenarios':len(rows),'actual_public_calls':len(rows),'by_elite':{str(e):sum(r['scenario']['elite']==e for r in rows) for e in [0,1,2]},
 'public_errors':len(errors),'all_e0_head_talent_absent':e0_no_head,
 'source_files_checked':len(freeze['files']),'source_drift':drift,
 'scope':'Readonly existing owner-clock conditional reference; no new independent clock, native probability, actual targeting or patch',
 'compression':{'file':'headwolf-public-cases.json.gz','gzip_sha256':hashlib.sha256(compressed).hexdigest(),'gzip_bytes':len(compressed),
 'decompressed_format':'strict UTF-8 JSON array; numeric types preserved','raw_sha256':hashlib.sha256(raw).hexdigest(),'raw_bytes':len(raw),'gzip_roundtrip_verified':gzip.decompress(compressed)==raw}}
(OUT/'headwolf-public-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False))
for r in examples:
 if r['scenario']['elite']==0:print(json.dumps({'scenario':r['scenario'],'head_talent_selected':r['head_talent_selected'],'summary':r['summary']},ensure_ascii=False))
