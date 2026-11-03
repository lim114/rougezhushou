from pathlib import Path
import sys,json,hashlib,itertools,datetime
sys.path.insert(0,sys.argv[1])
from rouge.damage import calculate_damage
from rouge.catalog import catalog
SHU='char_2025_shu'

def digest(obj):return hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def cases():
 for op,p in catalog()['operators'].items():
  for skill in range(1,len(p['skills'])+1):
   for mode in ('frames','continuous'):
    yield 'false_flag_all_skills',{'operator':op,'skill':skill,'timing_mode':mode,'four_sui':False}
    if op!=SHU:yield 'inactive_flag_non_shu',{'operator':op,'skill':skill,'timing_mode':mode,'four_sui':True}
 for elite,rank,skills in ((0,1,(1,)),(1,7,(1,2))):
  for skill,mode,potential in itertools.product(skills,('frames','continuous'),(1,6)):
   yield 'locked_original_talent',{'operator':SHU,'skill':skill,'elite':elite,'skill_rank':rank,'timing_mode':mode,'potential':potential,'four_sui':True}
 training=[{'level':1,'potential':1},{'level':90,'potential':1},{'level':90,'potential':6},
           {'level':59,'potential':1,'module_id':'uniequip_002_shu','module_level':3},
           {'level':60,'potential':1,'module_id':'uniequip_002_shu','module_level':1},
           {'level':90,'potential':6,'module_id':'uniequip_002_shu','module_level':3}]
 environments=[{}, {'window_seconds':0}, {'window_seconds':10}, {'window_seconds':10,'timing':{'target_windows':[]}},
               {'window_seconds':10,'timing':{'target_disappears_seconds':0}}]
 effects=[{}, {'effects':[{'kind':'sp_recovery','value':.3}]},
          {'relic_ids':['rogue_6_relic_legacy_'+str(n) for n in (2,3,4,74,67)]},
          {'relic_ids':['rogue_6_relic_legacy_99']},
          {'relic_ids':['rogue_6_relic_legacy_118','rogue_6_relic_fight_5'],'timing':{'sp_events':{'initial':[],'cycle':[]}}}]
 for skill,mode,rank,timing,effect,train in itertools.product((1,2,3),('frames','continuous'),(1,7,10),environments,effects,training):
  timing_config={**timing.get('timing',{}),**effect.get('timing',{})}
  request={'operator':SHU,'skill':skill,'timing_mode':mode,'skill_rank':rank,'four_sui':True,
           **timing,**effect,**train,'timing':timing_config}
  yield 'eligible_original_periodic_sp',request
 for mode in ('frames','continuous'):
  for flags in ({'three_professions':True},{'three_same_profession':True},{'three_professions':True,'three_same_profession':True}):
   yield 'eligible_other_static_conditions',{'operator':SHU,'skill':2,'timing_mode':mode,'four_sui':True,**flags}

records=[]
for group,request in cases():
 try:
  r=calculate_damage(request);s=r['estimate']['skill']
  direct={'base_stats':r['estimate']['base_stats'],'attack':r['attack'],'total_damage':r['total_damage'],
          'total_healing':r.get('total_healing'),'attack_speed':r['attack_speed'],'interval_seconds':r['interval_seconds'],
          'components_sha256':digest(r.get('components')),
          'skill':{k:s.get(k) for k in ('duration_seconds','total_damage','total_healing','phase_damage','phase_healing','window_seconds','window_healing','window_dps','window_hps')}}
  resource={k:s[k] for k in ('initial_seconds','recharge_seconds','cycle_seconds','cycle_damage','cycle_healing','cycle_dps','cycle_hps','sp_recovery_per_second')}
  ref=r.get('shu_periodic_sp_reference')
  records.append({'group':group,'request':request,'full_result_sha256':digest(r),'direct_values':direct,'resource_values':resource,
                  'reference':ref,'recharge_streams':r['timing'].get('recharge_streams'),
                  'scope_synced':r['scope']==r['estimate']['scenario_scope'],
                  'relic_resolution_sha256':digest(r['relic_resolution'])})
 except Exception as error:
  records.append({'group':group,'request':request,'error':{'type':type(error).__name__,'message':str(error)}})
output={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'package':sys.argv[1],'calls':len(records),'records':records}
Path(sys.argv[2]).write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'calls':len(records),'errors':sum('error' in r for r in records),'output':sys.argv[2]}))
