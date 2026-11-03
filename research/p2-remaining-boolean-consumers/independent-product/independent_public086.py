"""12 independent public inputs; native trees captured before JSON, read-only trace."""
import copy
import gzip
import hashlib
import json
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent
AUTHOR = OUT.with_name('p2-remaining-boolean-consumers-086-draft')
source, destination = map(Path, sys.argv[1:3])
canon = lambda v: json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)


def typed(v):
    if isinstance(v,dict): return {'type':'dict','items':[[typed(k),typed(x)] for k,x in v.items()]}
    if isinstance(v,(list,tuple)): return {'type':type(v).__name__,'items':[typed(x) for x in v]}
    if isinstance(v,float): return {'type':'float','hex':v.hex()}
    return {'type':type(v).__name__,'value':v}


ALL = ('reinforcement_blocks_target','enemy_below_half','frozen_at_skill_end','ines_first_deployment',
       'ranged_attack','organ_mode','fever','power_coating','double_charge','steal_success','delivery_coordinate','overload')
rowspec = [
    ('S1 actual normal inactive', 'same', 'char_4182_oblvns', 1,
     {'level':60,'module_id':'uniequip_002_oblvns','module_level':3,'continuous_attacks':True,
      'timing_mode':'continuous','ranged_attack':'','_oblvns_ranged_attack_consumed':True}),
    ('S2 module override and normal inactive', 'same', 'char_4182_oblvns', 2,
     {'level':60,'module_id':'uniequip_002_oblvns','module_level':2,'continuous_attacks':True,
      'ranged_attack':'\x00','organ_mode':False,'fever':0,'_oblvns_ranged_attack_consumed':True}),
    ('S3 normal disabled with deployment relic', 'same', 'char_4182_oblvns', 3,
     {'level':60,'module_id':'uniequip_002_oblvns','module_level':3,'continuous_attacks':False,
      'timing_mode':'continuous','ranged_attack':'0','organ_mode':'false','fever':'false',
      'relic_ids':['rogue_6_relic_legacy_105'],'_oblvns_ranged_attack_consumed':True}),
    ('S3 actual normal reads ranged condition', 'ranged_attack', 'char_4182_oblvns', 3,
     {'level':60,'module_id':'uniequip_002_oblvns','module_level':3,'continuous_attacks':True,
      'ranged_attack':'未知','_oblvns_ranged_attack_consumed':False}),
    ('Mizuki unselected E1 talent', 'same', 'char_437_mizuki', 2,
     {'elite':1,'level':43,'skill_rank':7,'enemy_below_half':'false'}),
    ('Mizuki selected E2 talent on S1', 'enemy_below_half', 'char_437_mizuki', 1,
     {'level':60,'module_id':'uniequip_004_mizuki','module_level':3,'enemy_below_half':''}),
    ('Gnosis zero window second consumer', 'frozen_at_skill_end', 'char_206_gnosis', 3,
     {'window_seconds':0,'timing_mode':'continuous','frozen_at_skill_end':'\x00',
      'timing':{'target_windows':[]},'effects':[{'kind':'attack_pct','value':0.13}]}),
    ('Ines disappeared target second consumer', 'ines_first_deployment', 'char_4087_ines', 3,
     {'ines_first_deployment':'False','timing':{'target_disappears_seconds':0.7}}),
    ('Orchid S1 deployment double SP consumer', 'double_charge', 'char_1048_orchd2', 1,
     {'double_charge':'0','power_coating':False,'near_previous_deployment':False,
      'timing_mode':'continuous','relic_ids':['rogue_6_relic_legacy_105']}),
    ('Orchid tuple and dict aliases unchanged', 'same', 'char_1048_orchd2', 1,
     {'double_charge':(False,),'power_coating':{'x':False},'near_previous_deployment':False}),
    ('Legacy owner all fields ignored', 'same', 'silverash', 3, dict.fromkeys(ALL,'false')),
    ('Old near deployment guard wins over two new guards', 'old_error', 'char_1048_orchd2', 1,
     {'near_previous_deployment':'','double_charge':'false','power_coating':'False'}),
]
cases = [{'index':i,'label':label,'expect':expect,'input':{
    'operator':op,'skill':n,'elite':2,'level':90,'skill_rank':10,'potential':6,
    'base_attack':1097,'window_seconds':17.25,'timing_mode':'frames',**extra}}
    for i,(label,expect,op,n,extra) in enumerate(rowspec,1)]
assert len({canon(typed(r['input'])) for r in cases}) == 12
saved = [json.loads(line) for line in gzip.decompress((AUTHOR/'baseline-matrix.jsonl.gz').read_bytes()).splitlines()]
assert not ({canon(typed(r['input'])) for r in cases} & {canon(r['input_typed_before']) for r in saved})
freeze_path = AUTHOR/'review-freeze86.json'
assert hashlib.sha256(freeze_path.read_bytes()).hexdigest() == 'aa066032869298b11b06819a2533fa53e78096dd725d4006f01bbde551edab55'
for proof in json.loads(freeze_path.read_bytes())['files']:
    data=Path(proof['source_path']).read_bytes()
    assert len(data)==proof['bytes'] and hashlib.sha256(data).hexdigest()==proof['sha256']
sys.path.insert(0,str(source))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.operator_engine import Combat
from rouge.estimate import format_estimate
from rouge.reporting import format_report

# Transparent observation of the actual internal calls; no values or self state are assigned.
original_plan = Combat.plan
original_calculate = Combat.calculate
object_plans = {}; traces = []


def observe_plan(self, normal=False, window=None):
    result = original_plan(self,normal=normal,window=window)
    object_plans.setdefault(id(self),[]).append({'normal':normal,'window_typed':typed(window)})
    return result


def observe_calculate(self):
    object_plans[id(self)] = []
    error = None
    try:
        return original_calculate(self)
    except Exception as exc:
        error = {'type':type(exc).__name__,'message':str(exc)}
        raise
    finally:
        trace = {'operator':self.s['operator'],'skill':self.n,'actual_plan_calls':object_plans[id(self)],
                 'selected_talent_names':list(self.tv),'module_id':self.s.get('module_id'),
                 'actual_module_max_cnt':typed(self.tv.get('颂乐音符',{}).get('max_cnt',10)),
                 'ranged_signal_present':hasattr(self,'ranged_attack_condition_consumed'),
                 'ranged_signal':getattr(self,'ranged_attack_condition_consumed',None)}
        if error is not None: trace['calculation_error']=error
        traces.append(trace)


Combat.plan = observe_plan
Combat.calculate = observe_calculate
catalog_before = hashlib.sha256(canon(typed(catalog())).encode()).hexdigest()
rows = []; formatters = 0
for case in cases:
    args=copy.deepcopy(case['input']); before=typed(args); traces.clear()
    row={'index':case['index'],'label':case['label'],'expect':case['expect'],
         'input':args,'input_typed_before':before}
    try:
        result=calculate_damage(args)
    except Exception as error:
        row.update(outcome='error',error_type=type(error).__name__,error_message=str(error))
    else:
        native=typed(result)
        reports={'estimate':format_estimate(result),'user':format_report(result),'technical':format_report(result,technical=True)}
        formatters+=3; row.update(outcome='accepted',result=result,result_typed=native,reports=reports)
    row['input_typed_after']=typed(args)
    row['catalog_native_sha256_before']=catalog_before
    row['catalog_native_sha256_after']=hashlib.sha256(canon(typed(catalog())).encode()).hexdigest()
    row['actual_internal_trace']=copy.deepcopy(traces)
    assert canon(before)==canon(row['input_typed_after']) and row['catalog_native_sha256_after']==catalog_before
    rows.append(row)
raw=json.dumps(rows,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
with destination.open('xb') as handle:handle.write(gzip.compress(raw,compresslevel=9,mtime=0))
print(json.dumps({'status':'CAPTURED','fresh_public_calls':12,'accepted':sum(r['outcome']=='accepted' for r in rows),
                  'errors':sum(r['outcome']=='error' for r in rows),'formatter_calls':formatters,
                  'new_explicit_project_helper_calls':0,'distinct_from_author268':True,
                  'caller_and_catalog_native_types_unchanged':True,'whole_native_trees_before_JSON':True,
                  'transparent_observation_only_no_return_or_object_state_changes':True,
                  'gzip_sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),'bytes':destination.stat().st_size}))
