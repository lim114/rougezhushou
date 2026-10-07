"""Preflight planned public API contracts, not actual Qt or Wine evidence."""
import gzip,hashlib,json,sys
from collections import Counter
from pathlib import Path
P=Path(__file__).resolve().parent
PACKAGE=Path(sys.argv[1]);THROUGH=int(sys.argv[2]);LABEL=sys.argv[3]
sys.dont_write_bytecode=True;sys.path.insert(0,str(PACKAGE))
from rouge.damage import calculate_damage
from rouge.run_config import config_data
from rouge.operator_options import OPTIONS
from rouge.reporting import format_report
from cases075 import cases075,preview_cases075
from public_contracts import require_squad075,require_headwolf075,require_mei075,require_wisdel_routes075,require_movement075,canonical075
def source_hashes():
 return {p.relative_to(PACKAGE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
  for p in sorted((PACKAGE/'rouge').rglob('*'))if p.is_file() and p.suffix in('.py','.json')}
before=source_hashes();data=config_data();counts=Counter();rows=[];plain={}
for row in cases075(data['squads']):
 section=row['section']
 if section>THROUGH:continue
 requested=row['input'];args=dict(requested)
 defaults={k:v for k,label,v,maximum,skills in OPTIONS.get(args['operator'],[])if args['skill'] in skills}
 args={**defaults,**args};original=canonical075(args)
 result=calculate_damage(args);text=format_report(result)
 assert canonical075(args)==original
 if section==71:require_squad075(result,args,text,data['squads'][args['run_config']['squad']['id']])
 elif section==72:
  key=(args['potential'],args['timing_mode'],args['drone_warmup_hits'])
  if args['elite']==0 and args['deployment_elapsed_seconds']==0:plain[key]=result
  require_headwolf075(result,args,text,plain.get(key) if args['elite']==0 else None)
 elif section==73:
  require_mei075(result,args,text,args['elite']==2 and args['level']>=40,args['module_level'])
  if args['window_seconds']==0:assert result['total_damage']==0
 elif section==74:
  require_wisdel_routes075(result,args,text)
  if args['window_seconds']==0:assert result['total_damage']==0
 else:raise AssertionError(section)
 counts[section]+=1;rows.append({'section':section,'input':args,'result':result,'human_report':text})
if THROUGH>=75:
 from rouge.battle_preview import battle_data,enemy_preview,enemy_text
 for case in preview_cases075(battle_data()['stages']):
  entry=enemy_preview(case['stage_id'],case['enemy_id'],case['level'])
  text=enemy_text(entry,technical=case['technical'])
  require_movement075(entry,text,case['technical'],battle_data()['stages'][case['stage_id']])
  counts[75]+=1;rows.append({'section':75,'input':case,'preview':entry,'visible_text':text})
assert source_hashes()==before
receipt={'scope':'Public API-only planned Qt contracts; no GUI/Wine execution',
 'gui_executed':False,'wine_executed':False,'through_section':THROUGH,'calls':len(rows),
 'cases_by_section':dict(counts),'source_drift':[],'source_hashes':before,'records':rows}
raw=gzip.compress(json.dumps(receipt,ensure_ascii=False,allow_nan=False).encode(),mtime=0)
(P/f'public-schema-{LABEL}.json.gz').write_bytes(raw)
summary={k:v for k,v in receipt.items()if k not in ('records','source_hashes')}
summary['full_receipt_sha256']=hashlib.sha256(raw).hexdigest()
(P/f'public-schema-{LABEL}-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False))
