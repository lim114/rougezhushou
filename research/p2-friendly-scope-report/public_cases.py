import json,sys,copy,hashlib
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from rouge.damage import calculate_damage
from rouge.reporting import format_report
def normalized(result):
 r=copy.deepcopy(result);r.pop('report',None);r['estimate'].pop('notes',None)
 def clean(v):
  if isinstance(v,dict):return {k:clean(x) for k,x in v.items() if k!='target_scope_notes'}
  if isinstance(v,list):return [clean(x) for x in v]
  return v
 return clean(r)
rows=[]
for op,skill in (('char_298_susuro',1),('char_298_susuro',2),('char_151_myrtle',2),('kaltsit',2),('char_1037_amiya3',1)):
 for mode in ('frames','continuous'):
  for timing in ({},{'target_disappears_seconds':0},{'target_windows':[]}):
   scenario={'operator':op,'skill':skill,'timing_mode':mode,'window_seconds':10,'timing':timing}
   result=calculate_damage(scenario)
   rows.append({'scenario':scenario,'nonreport_result_sha256':hashlib.sha256(json.dumps(normalized(result),ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
    'total_damage':result['total_damage'],'total_healing':result.get('total_healing'),
    'total_healing_field_present':'total_healing' in result,'skill_fields':result['estimate']['skill'],
    'semantic_warning_visible':'真实友方获取时钟未核验' in format_report(result)})
Path(sys.argv[2]).write_text(json.dumps({'public_calls':len(rows),'cases':rows},ensure_ascii=False,indent=2)+'\n')
