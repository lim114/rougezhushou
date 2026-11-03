import copy,hashlib,json,sys,subprocess
from pathlib import Path
sys.path.insert(0,'/workspace/rougezhushou')
from rouge.damage import calculate_damage
from rouge.catalog import catalog
active=(('mechanist',2,'shield_break_count'),('mechanist',3,'charge_count'),('silverash',2,'activation_count'),('silverash',2,'deployment_stacks'))
def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def digest(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
rows=[];cb=digest(catalog())
for op,skill,field in active:
 for mode in ('frames','continuous'):
  configs=[('default',{}),('zero-window',{'window_seconds':0})]+[(f'lifetime-{v!r}',{'timing':{'target_disappears_seconds':v}}) for v in (0,'0','0.0','-0','1')]
  for scope,extra in configs:
   for value in (False,True,0,1,2,1.0,'1','1.0','1e0'):
    args={'operator':op,'skill':skill,'base_attack':1000,'companion_attack':2000,'window_seconds':10,'timing_mode':mode,field:value,**extra};before=canonical(args)
    try:r={'accepted':True,'result':calculate_damage(args)}
    except (ValueError,TypeError,OverflowError) as ex:r={'accepted':False,'error_type':type(ex).__name__,'error':str(ex)}
    assert canonical(args)==before
    rows.append({'case':f'{op}/{skill}/{field}/{mode}/{scope}/{value!r}','raw_bool':isinstance(value,bool),'scenario':args,'outcome':r,'outcome_sha256':digest(r)})
assert digest(catalog())==cb
out={'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'source_sha256':{x:hashlib.sha256(Path(x).read_bytes()).hexdigest() for x in ('rouge/damage.py','rouge/charge_reference.py','rouge/shield_break_reference.py')},'calls':len(rows),'caller_inputs_unchanged':True,'catalog_unchanged':True,'rows':rows}
Path(sys.argv[1]).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print({'calls':len(rows),'head':out['head']})
