from pathlib import Path
import argparse,collections,copy,datetime,hashlib,itertools,json,sys
base=Path(__file__).parent
p=argparse.ArgumentParser();p.add_argument('--package',required=True);p.add_argument('--out',required=True);a=p.parse_args();sys.path.insert(0,str(base/a.package))
from rouge.catalog import catalog,stage_previews
from rouge.damage import calculate_damage
from rouge.relics import mechanics
from rouge.run_config import config_data
OP='char_4204_mantra'
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def digest(v):return hashlib.sha256(canonical(v).encode()).hexdigest()
cache_before={k:digest(v) for k,v in [('catalog',catalog()),('stage_previews',stage_previews()),('mechanics',mechanics()),('run_config',config_data())]}
records=[];seen=set();groups=collections.Counter()
def add(group,request):
 key=canonical(request)
 if key in seen:return
 seen.add(key);original=copy.deepcopy(request);r={'group':group,'request':original}
 try:r['full_result']=json.loads(canonical(calculate_damage(request)));r['full_result_sha256']=digest(r['full_result'])
 except Exception as e:r['error']={'type':type(e).__name__,'message':str(e)}
 assert original==request
 records.append(r);groups[group]+=1
 if request.get('elite')==0 and request['palsy_triggers']>0 and 'full_result' in r:add('locked_zero_count_complete_output_counterfactual',{**request,'palsy_triggers':0})
for elite,skill,mode,boundary in itertools.product((1,2),(1,2,3),('frames','continuous'),(
 {'window_seconds':0},{'timing':{'target_disappears_seconds':0}},
 {'timing':{'target_windows':[]}},{'base_attack':0},{'enemy_elemental_resistance':100},
 {'enemy_buildup_resistance':100},{'continuous_attacks':False})):
 add('qualified_all_skills_global_body_scope_immunity_and_zero_attack',{'operator':OP,'skill':skill,'elite':elite,'level':1,'potential':5,'skill_rank':7,'timing_mode':mode,'base_attack':1000,'window_seconds':10,'palsy_triggers':2,'palsy_overflow_hits':3,**boundary})
for elite,mode,skill in itertools.product((0,1,2),('frames','continuous'),(1,2,3)):
 for effect in ([{'kind':'sp_recovery','value':.2}],[]):
  add('max_cultivation_and_natural_attack_SP_complete_output',{'operator':OP,'skill':skill,'elite':elite,'level':catalog()['operators'][OP]['phases'][elite]['max_level'],'potential':6,'skill_rank':7,'timing_mode':mode,'base_attack':1000,'window_seconds':10,'palsy_triggers':1,'palsy_overflow_hits':2,'effects':effect,'relic_ids':['rogue_6_relic_legacy_67']})
for elite,mode in itertools.product((0,1,2),('frames','continuous')):
 add('selected_enemy_reference_and_out_of_battle_stat_layers',{'operator':OP,'skill':1,'elite':elite,'level':1,'skill_rank':1,'timing_mode':mode,'window_seconds':10,'palsy_triggers':1,'target_enemy':{'stage_id':'ro6_n_1_1','enemy_id':'enemy_2133_shdopl','level':0},'run_config':{'difficulty':{'value':4}}})
cache_after={k:digest(v) for k,v in [('catalog',catalog()),('stage_previews',stage_previews()),('mechanics',mechanics()),('run_config',config_data())]}
assert cache_before==cache_after
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'package':a.package,'paired_scenario_records':len(records),'actual_fresh_public_calls':len(records),'reused_completed_readonly_calls_without_rerun':0,'groups':dict(groups),'records':records,'cache_before_sha256':cache_before,'cache_after_sha256':cache_after,'callers_and_public_static_caches_preserved':True}
(base/a.out).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print({k:v for k,v in out.items() if k!='records'})
