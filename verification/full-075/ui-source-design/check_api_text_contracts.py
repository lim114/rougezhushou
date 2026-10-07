"""API errors/aliases only; none of these values is fabricated in Qt widgets."""
import gzip,hashlib,json,sys
from pathlib import Path
P=Path(__file__).resolve().parent;PACKAGE=Path(sys.argv[1]);LABEL=sys.argv[2]
sys.dont_write_bytecode=True;sys.path.insert(0,str(PACKAGE))
from rouge.damage import calculate_damage
from rouge.run_config import config_data
from public_contracts import canonical075
rows=[];errors=0;pairs=0
def call(args,error=None):
 global errors
 original=canonical075(args)
 try:
  result=calculate_damage(args)
 except ValueError as caught:
  assert error is not None and str(caught)==error,(args,str(caught),error)
  result=None;rows.append({'input':args,'status':'expected_error','error':{'type':'ValueError','message':str(caught)}});errors+=1
 else:
  assert error is None,(args,error)
  rows.append({'input':args,'status':'returned','result':result})
 assert canonical075(args)==original
 return result
for record in config_data()['squads'].values():
 if record['bandLevel']!=1:continue
 for flag in ('false','true',0,1,None):
  call({'operator':'silverash','skill':3,'window_seconds':10,'run_config':{'squad':{
   'id':record['id'],'name':record['name'],'effect_verified':flag}}},'分队效果确认标记需要布尔值。')
for elite,level,rank in ((0,50,4),(2,90,10)):
 for mode in ('frames','continuous'):
  base={'operator':'char_1035_wisdel','skill':1,'skill_rank':rank,'elite':elite,'level':level,
   'timing_mode':mode,'window_seconds':10,'ghost_count':1,'ghost_casts':1}
  for key in ('ghost_count','ghost_casts'):
   for flag in (False,True):call({**base,key:flag},key+'需要范围内的有限非负整数。')
   for alias in ('1','1.0'):
    typed=call(base);textual=call({**base,key:alias})
    assert canonical075(typed)==canonical075(textual),(elite,mode,key,alias)
    pairs+=1
receipt={'scope':'API-only exact errors and textual count aliases; no GUI/Wine execution',
 'gui_executed':False,'wine_executed':False,'calls':len(rows),'expected_errors':errors,'whole_json_alias_pairs':pairs,
 'source_files':{n:hashlib.sha256((PACKAGE/n).read_bytes()).hexdigest()for n in
  ('rouge/damage.py','rouge/operator_engine.py','rouge/run_modifiers.py')},'records':rows}
raw=gzip.compress(json.dumps(receipt,ensure_ascii=False,allow_nan=False).encode(),mtime=0)
(P/f'api-text-contracts-{LABEL}.json.gz').write_bytes(raw)
summary={k:v for k,v in receipt.items()if k not in('records','source_files')};summary['full_receipt_sha256']=hashlib.sha256(raw).hexdigest()
(P/f'api-text-contracts-{LABEL}-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False))
