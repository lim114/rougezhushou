from pathlib import Path
import argparse,collections,copy,datetime,hashlib,itertools,json,sys
base=Path(__file__).parent
parser=argparse.ArgumentParser();parser.add_argument('--package',required=True);parser.add_argument('--out',required=True);args=parser.parse_args()
sys.path.insert(0,str(base/args.package))
from rouge.catalog import catalog,stage_previews
from rouge.damage import calculate_damage
from rouge.run_config import config_data
from rouge.relics import mechanics

def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def digest(v):return hashlib.sha256(canonical(v).encode()).hexdigest()
OP='char_4204_mantra';profile=catalog()['operators'][OP]
cache_before={k:digest(v) for k,v in [('catalog',catalog()),('stage_previews',stage_previews()),('run_config',config_data()),('mechanics',mechanics())]}
initial=json.loads((base/'initial-public-results078.json').read_bytes())
reusable={canonical(r['request']):r for r in initial['records']} if args.package=='baseline' else {}
records=[];seen=set();groups=collections.Counter();fresh=0;reused=0

def add(group,request,golden=True):
 global fresh,reused
 key=canonical(request)
 if key in seen:return
 seen.add(key);request=json.loads(key);original=copy.deepcopy(request)
 if key in reusable:
  r={k:copy.deepcopy(v) for k,v in reusable[key].items() if k!='selected_talents'}
  r['group']=group;r['full_result_sha256']=digest(r['full_result']);r['reused_completed_source_call_without_rerun']=True;reused+=1
 else:
  r={'group':group,'request':original}
  try:r['full_result']=json.loads(canonical(calculate_damage(request)));r['full_result_sha256']=digest(r['full_result'])
  except Exception as e:r['error']={'type':type(e).__name__,'message':str(e)}
  fresh+=1
 assert request==original
 records.append(r);groups[group]+=1
 # A complete baseline zero-count counterpart is the exact expected result,
 # with only validated declared-count metadata restored. No numeric-field masking.
 if golden and request['operator']==OP and request.get('elite',2)==0 and request.get('palsy_triggers',0)!=0 and 'full_result' in r:
  add('locked_talent_zero_count_complete_output_counterfactual',{**request,'palsy_triggers':0},golden=False)

for r in initial['records']:add('initial_exact_source_public_calls',r['request'])
for elite,potential,mode,count,rank in itertools.product((0,1,2),(1,5),('frames','continuous'),(0,1,3,10000),(1,7,10)):
 add('cultivation_rank_potential_and_declared_integer_endpoints',{'operator':OP,'skill':1,'elite':elite,'level':1,'potential':potential,'skill_rank':rank,'base_attack':1000,'window_seconds':10,'timing_mode':mode,'palsy_triggers':count})
for elite,mode,observation in itertools.product((0,1,2),('frames','continuous'),(
 {},{'window_seconds':0},{'window_seconds':.1},{'window_seconds':1},{'window_seconds':10},
 {'timing':{'target_disappears_seconds':0}},{'timing':{'target_disappears_seconds':1}},
 {'timing':{'target_windows':[]}},{'timing':{'target_windows':[[9,10]]}},
 {'timing':{'interrupt_windows':[[0,10]]}},{'base_attack':0},{'continuous_attacks':False})):
 for count in (0,2):
  add('zero_positive_observation_global_vs_body_scope_and_selected_zero_damage',{'operator':OP,'skill':1,'elite':elite,'level':1,'skill_rank':1,'base_attack':1000,'timing_mode':mode,'palsy_triggers':count,**observation})
for elite,skill,mode,rank in itertools.product((0,1,2),(1,2,3),('frames','continuous'),(1,7,10)):
 for potential in (1,5):
  add('all_skills_exact_old_cultivation_gate_precedence',{'operator':OP,'skill':skill,'elite':elite,'level':1,'potential':potential,'skill_rank':rank,'base_attack':1000,'window_seconds':10,'timing_mode':mode,'palsy_triggers':2,'palsy_overflow_hits':3})
for skill,mode,palsy,overflow in itertools.product((1,2,3),('frames','continuous'),(0,1,2),(0,1,3)):
 add('qualified_S3_overflow_and_global_palsy_are_independent_parameters',{'operator':OP,'skill':skill,'elite':2,'level':90,'potential':5,'skill_rank':10,'base_attack':1000,'window_seconds':1,'timing_mode':mode,'palsy_triggers':palsy,'palsy_overflow_hits':overflow})
for elite,mode,condition in itertools.product((0,1,2),('frames','continuous'),(
 {'enemy_elemental_resistance':0},{'enemy_elemental_resistance':50},{'enemy_elemental_resistance':100},
 {'enemy_buildup_resistance':100},{'enemy_resistance':100},{'enemy_in_neural_break':True},
 {'initial_neural_buildup':999},{'initial_neural_buildup':1000},
 {'initial_neural_buildup':500,'enemy_in_neural_break':True},
 {'enemy_in_neural_break':True,'relic_ids':['rogue_6_relic_fight_22']},
 {'base_attack':0,'enemy_elemental_resistance':100},
 {'enemy_buildup_resistance':100,'enemy_elemental_resistance':100})):
 for count in (0,1):
  add('elemental_immunity_neural_first_hit_and_independent_river_boundaries',{'operator':OP,'skill':1,'elite':elite,'level':1,'skill_rank':1,'base_attack':1000,'window_seconds':10,'timing_mode':mode,'palsy_triggers':count,**condition})
for elite,skill,mode,relics in itertools.product((0,1,2),(1,2,3),('frames','continuous'),(
 [],['rogue_6_relic_legacy_67'],['rogue_6_relic_legacy_45'],['rogue_6_relic_legacy_116'],
 ['rogue_6_relic_fight_5'],['rogue_6_relic_legacy_81'])):
 add('independent_attack_SP_natural_SP_and_retired_combat_sources',{'operator':OP,'skill':skill,'elite':elite,'level':1,'skill_rank':1,'base_attack':1000,'window_seconds':10,'timing_mode':mode,'palsy_triggers':1,'relic_ids':relics,'effects':[{'kind':'sp_recovery','value':.2}]})
for elite,mode,value in itertools.product((0,1,2),('frames','continuous'),(False,True,None,-1,.5,10001,'false','1','1.0','1e0','0','0.0','nan','inf',[],{})):
 add('queried_count_old_nontext_text_and_range_contract',{'operator':OP,'skill':1,'elite':elite,'level':1,'skill_rank':1,'base_attack':1000,'window_seconds':10,'timing_mode':mode,'palsy_triggers':value})
for elite,mode,field in itertools.product((0,1,2),('frames','continuous'),(
 {'elite':-1},{'elite':3},{'level':0},{'level':999},{'potential':0},{'potential':7},
 {'skill':4},{'skill_rank':11},{'window_seconds':-1},{'timing_mode':'missing'},
 {'module_id':'missing','module_level':1},{'skill':3,'palsy_overflow_hits':False})):
 add('prior_whole_error_precedence_with_invalid_declared_count',{'operator':OP,'skill':1,'elite':elite,'level':1,'skill_rank':1,'palsy_triggers':False,'timing_mode':mode,**field})
for owner,p in catalog()['operators'].items():
 for skill,mode in itertools.product(range(1,len(p['skills'])+1),('frames','continuous')):
  add('all87_skills_both_modes_full_output_control',{'operator':owner,'skill':skill,'window_seconds':10,'timing_mode':mode})
  if owner!=OP:
   add('unqueried_other_owner_raw_palsy_fields_remain_ignored',{'operator':owner,'skill':skill,'window_seconds':10,'timing_mode':mode,'palsy_triggers':False,'palsy_overflow_hits':'unqueried'})
cache_after={k:digest(v) for k,v in [('catalog',catalog()),('stage_previews',stage_previews()),('run_config',config_data()),('mechanics',mechanics())]}
assert cache_before==cache_after
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'package':args.package,'paired_scenario_records':len(records),'actual_fresh_public_calls':fresh,'reused_completed_readonly_calls_without_rerun':reused,'groups':dict(groups),'records':records,'cache_before_sha256':cache_before,'cache_after_sha256':cache_after,'callers_and_public_static_caches_preserved':True}
(base/args.out).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print({k:v for k,v in out.items() if k!='records'})
print({'successes':sum('full_result' in r for r in records),'errors':dict(collections.Counter(r['error']['message'] for r in records if 'error' in r))})
