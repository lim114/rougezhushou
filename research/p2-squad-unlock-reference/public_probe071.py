from pathlib import Path
import sys,json,hashlib,itertools,collections,datetime,argparse

base=Path(__file__).parent
parser=argparse.ArgumentParser();parser.add_argument('--package',required=True);parser.add_argument('--out',required=True)
args=parser.parse_args();sys.path.insert(0,str(base/args.package))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.run_config import config_data
from rouge.technology import _data

def canonical(o):return json.dumps(o,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def digest(o):return hashlib.sha256(canonical(o).encode()).hexdigest()
public_before=canonical(catalog());config_before=canonical(config_data());tech_before=canonical(_data())
records=[];seen=set();groups=collections.Counter()
def add(group,request):
    key=canonical(request)
    if key in seen:return
    seen.add(key);request=json.loads(key);before=json.loads(key)
    try:
        result=calculate_damage(request)
        # The public artifact is complete serialized JSON, including every report field.
        result=json.loads(canonical(result))
        row={'group':group,'request':before,'full_result':result,'full_result_sha256':digest(result)}
    except Exception as error:row={'group':group,'request':before,'error':{'type':type(error).__name__,'message':str(error)}}
    assert request==before
    records.append(row);groups[group]+=1
flags=({}, {'effect_verified':False},{'effect_verified':True})
owners=(('mechanist',1),('char_110_deepcl',1),('char_2025_shu',2),('char_1035_wisdel',3))
for squad,flag,mode,(owner,skill) in itertools.product(config_data()['squads'],flags,('frames','continuous'),owners):
    add('all_22_squad_variants_confirmation_and_owner_controls',{'operator':owner,'skill':skill,'timing_mode':mode,'window_seconds':10,'run_config':{'squad':{'id':squad,**flag}}})
for owner,entry in catalog()['operators'].items():
    for skill,mode,flag in itertools.product(range(1,len(entry['skills'])+1),('frames','continuous'),(False,True)):
        add('all_public_skills_preserve_math_and_training',{'operator':owner,'skill':skill,'timing_mode':mode,'window_seconds':10,'run_config':{'squad':{'id':'rogue_6_band_7','effect_verified':flag}}})
upgrades=[key for key,value in config_data()['squads'].items() if value['bandLevel']==1]
conditions=({'window_seconds':0},{'timing':{'target_disappears_seconds':0}}, {'timing':{'target_windows':[]}},
            {'four_sui':True,'three_professions':True,'three_same_profession':True},
            {'elite':0,'skill_rank':1},{'elite':1,'skill_rank':7},
            {'level':59,'potential':6,'module_id':'uniequip_002_shu','module_level':3},
            {'level':60,'potential':6,'module_id':'uniequip_002_shu','module_level':3},
            {'effects':[{'kind':'hp_pct','value':.2},{'kind':'attack_speed','value':18}], 'relic_ids':['rogue_6_relic_legacy_15']})
for squad,mode,condition in itertools.product(upgrades,('frames','continuous'),conditions):
    add('training_window_and_independent_unknown_clock_boundaries',{'operator':'char_2025_shu','skill':2,'timing_mode':mode,'window_seconds':10,'run_config':{'squad':{'id':squad,'effect_verified':True}},**condition})
for squad,mode,grade,flag in itertools.product(upgrades,('frames','continuous'),(0,2,3,5,6,8,9,15),(False,True)):
    add('raw_grade_references_do_not_replace_explicit_squad_effect',{'operator':'mechanist','skill':1,'timing_mode':mode,'window_seconds':10,
        'target_enemy':{'stage_id':'ro6_n_1_2','enemy_id':'enemy_1093_ccsbr','level':0},
        'run_config':{'squad':{'id':squad,'effect_verified':flag},'difficulty':{'value':grade},'zone':{'id':'zone_2'}}})
for squad in upgrades:
    for mode in ('MONTH_TEAM','CHALLENGE'):
        add('prior_mode_errors',{'operator':'mechanist','skill':1,'run_config':{'squad':{'id':squad,'effect_verified':True},'difficulty':{'value':0,'modeDifficulty':mode}}})
    for flag in ('false',None,1):
        add('prior_confirmation_errors',{'operator':'mechanist','skill':1,'run_config':{'squad':{'id':squad,'effect_verified':flag}}})
    add('prior_identity_errors',{'operator':'mechanist','skill':1,'run_config':{'squad':{'id':squad,'name':'wrong','effect_verified':True}}})
    add('mechanist_current_training_is_not_account_unlock_evidence',{'operator':'mechanist','skill':1,'elite':0,'skill_rank':1,'run_config':{'squad':{'id':squad,'effect_verified':True}}})
for config in (None,{}, {'squad':None},{'squad':{}},{'difficulty':{'value':0}}):
    add('absent_selected_squad_full_output_controls',{'operator':'mechanist','skill':1,'run_config':config})
assert canonical(catalog())==public_before and canonical(config_data())==config_before and canonical(_data())==tech_before
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'package':args.package,'public_calls':len(records),
     'groups':groups,'records':records,'caller_and_catalog_run_config_technology_cache_preserved':True}
(base/args.out).write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print({'package':args.package,'public_calls':len(records),'groups':dict(groups),'successes':sum('full_result' in r for r in records),
       'errors':dict(collections.Counter(r['error']['message'] for r in records if 'error' in r))})
