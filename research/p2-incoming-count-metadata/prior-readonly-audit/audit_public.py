"""Read-only source-pinned integer compatibility audit; no model or patch changes."""
from copy import deepcopy
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parent
FROZEN=ROOT/'frozen'
sys.path.insert(0,str(FROZEN))
from rouge.catalog import catalog
from rouge.damage import calculate_damage

OP='char_1042_phatm2'
VALUES=[('absent',None),('zero_int',0),('zero_float',0.0),('zero_text','0'),
        ('zero_decimal_text','0.0'),('zero_exp_text','0e0'),
        ('one_int',1),('one_float',1.0),('one_text','1'),
        ('one_decimal_text','1.0'),('one_exp_text','1e0'),
        ('twenty_int',20),('twenty_text','20'),('twenty_decimal_text','20.0'),
        ('twenty_exp_text','2e1'),('maximum_int',10000),('maximum_exp_text','1e4'),
        ('false_bool',False),('true_bool',True),('null',None),('fraction_intlike',1.5),
        ('fraction_text','1.5'),('negative',-1),('over_maximum',10001),
        ('nonnumeric','unknown'),('empty_text',''),('nonfinite_text','nan')]
SCOPES=[('default',{}),('zero_window',{'window_seconds':0}),
        ('short_window',{'window_seconds':.1}),('ten_window',{'window_seconds':10}),
        ('life_zero',{'timing':{'target_disappears_seconds':0}}),
        ('empty_targets',{'timing':{'target_windows':[]}}),
        ('immune',{'enemy_buildup_resistance':100}),
        ('with_river',{'relic_ids':['rogue_6_relic_fight_22']})]
records={}
for skill in (1,2,3):
    for mode in ('frames','continuous'):
        for scope,extra in SCOPES:
            for label,value in VALUES:
                args={'operator':OP,'skill':skill,'timing_mode':mode,'base_attack':1000,**extra}
                if label!='absent':args['enemy_attack_count']=value
                name=f'active:S{skill}:{mode}:{scope}:{label}'
                records[name]={'scenario':args}
# Same-owner locked talent preserves the real query/qualification order.
for skill in (1,2):
    for mode in ('frames','continuous'):
        for label,value in VALUES:
            args={'operator':OP,'skill':skill,'timing_mode':mode,'elite':1,
                  'level':80,'skill_rank':7,'base_attack':1000,'window_seconds':10}
            if label!='absent':args['enemy_attack_count']=value
            records[f'locked:S{skill}:{mode}:{label}']={'scenario':args}
for op,skill in (('mechanist',1),('silverash',3),('char_002_amiya',1),('char_2025_shu',3)):
    for mode in ('frames','continuous'):
        for label,value in VALUES:
            args={'operator':op,'skill':skill,'base_attack':1000,'window_seconds':10,'timing_mode':mode}
            if label!='absent':args['enemy_attack_count']=value
            records[f'inactive:{op}:S{skill}:{mode}:{label}']={'scenario':args}

for name,record in records.items():
    args=record['scenario'];before=deepcopy(args)
    try:
        record['outcome']={'result':calculate_damage(args),'error':None}
    except Exception as exc:
        record['outcome']={'result':None,'error':{'type':type(exc).__name__,'message':str(exc)}}
    assert args==before,name

pairs={}
for skill in (1,2,3):
    for mode in ('frames','continuous'):
        for scope,_ in SCOPES:
            key=f'active:S{skill}:{mode}:{scope}:'
            for left,right in (('zero_int','zero_text'),('zero_int','zero_decimal_text'),
                               ('zero_int','zero_exp_text'),('zero_int','absent'),
                               ('one_int','one_float'),('one_int','one_text'),
                               ('one_int','one_decimal_text'),('one_int','one_exp_text'),
                               ('twenty_int','twenty_decimal_text'),('twenty_int','twenty_exp_text'),
                               ('maximum_int','maximum_exp_text')):
                l,r=records[key+left]['outcome'],records[key+right]['outcome']
                pairs[key+left+'='+right]={'left':key+left,'right':key+right,
                    'full_outcomes_equal':l==r,'left_error':l['error'],'right_error':r['error']}
assert all(v['full_outcomes_equal'] for k,v in pairs.items()
           if any(k.endswith('='+x) for x in ('zero_text','zero_decimal_text','zero_exp_text','absent','one_float','one_text')))
inactive_count=0
for name,record in records.items():
    if name.startswith('inactive:'):
        absent=records[name.rsplit(':',1)[0]+':absent']['outcome']
        assert record['outcome']==absent,name
        inactive_count+=1
files={str(p.relative_to(FROZEN)):hashlib.sha256(p.read_bytes()).hexdigest()
       for p in FROZEN.rglob('*') if p.is_file() and p.suffix in ('.py','.json')}
(ROOT/'freeze-receipt.json').write_text(json.dumps({'head':'0d446fc3523fd09452c84f65c133d23f33b31696',
    'source':'git archive exact clean commit rouge/tests/scripts','files':files},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with gzip.open(ROOT/'public-outcomes.json.gz','wt',encoding='utf-8') as out:
    json.dump({'head':'0d446fc3523fd09452c84f65c133d23f33b31696','cases':records,
               'all_inputs_preserved':True},out,ensure_ascii=False,indent=2)
    out.write('\n')
(ROOT/'paired-outcome-comparison.json').write_text(json.dumps({'pairs':pairs},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
summary={'readonly':True,'public_calls':len(records),'full_result_outcomes':sum(r['outcome']['error'] is None for r in records.values()),
         'old_error_outcomes':sum(r['outcome']['error'] is not None for r in records.values()),
         'semantic_integer_pairs':len(pairs),'different_pairs':sum(not p['full_outcomes_equal'] for p in pairs.values()),
         'inactive_outcomes_equal_absence':inactive_count,
         'existing_zero_and_float_one_controls_equal':True,
         'new_actual_damage_or_clock_model':False,'patch_written':False}
(ROOT/'audit-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False))
