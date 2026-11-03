"""API-only design check for future actual Qt assertions; no fake Qt or GUI."""
import gzip
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

P=Path(__file__).resolve().parent
PACKAGE=P/'public-schema-65'
sys.path.insert(0,str(PACKAGE));sys.dont_write_bytecode=True
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.operator_options import OPTIONS
from rouge.reporting import format_report

def source_hashes():
    return {p.relative_to(PACKAGE).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted((PACKAGE/'rouge').rglob('*')) if p.is_file() and p.suffix in ('.py','.json')}
before=source_hashes();rows=[];counts=Counter()
def scenario(op,skill,mode,rank=10,**extra):
    profile=catalog()['operators'][op]
    args={'operator':op,'skill':skill,'skill_rank':rank,'elite':2,
          'level':profile['phases'][2]['max_level'],'potential':1,'trust':100,
          'module_id':None,'module_level':0,'window_seconds':10,'timing_mode':mode,
          'enemy_defense':0,'enemy_resistance':0,'preexisting_fragile':False,
          'cooperative':False,'relic_ids':[],'healing_targets':1}
    args.update({key:default for key,label,default,maximum,skills in OPTIONS.get(op,[]) if skill in skills})
    args.update(extra);return args
def check(section,args):
    original=json.dumps(args,sort_keys=True)
    result=calculate_damage(args)
    assert json.dumps(args,sort_keys=True)==original
    text=format_report(result)
    rows.append({'section':section,'input':args,'result':result,'human_report':text})
    counts[section]+=1;return result,text
def metrics(result,name):
    return {row['key']:row['value'] for section in result['report']['sections']
            if section['id']==name for row in section['metrics']}
def strict(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,allow_nan=False)

fields={'summon_count','casts_used','slash_kills','amiya_slash_kills','incoming_hits',
        'shield_contact_ticks','cold_state','dash_hits','bubble_bursts','levitate_triggers',
        'snow_entries','drone_warmup_hits','note_count','bait_triggers','enemy_attack_count',
        'palsy_triggers','palsy_overflow_hits','connected_stones','trap_triggers',
        'trap_dot_ticks','dragon_arrow_hits','ghost_count','ghost_casts'}
controls=[(owner,key,skills) for owner,entries in OPTIONS.items()
          for key,label,default,maximum,skills in entries if key in fields]
assert len(controls)==24 and len(fields)==23
for owner,key,skills in controls:
    for mode in ('frames','continuous'):
        for value in (0,1):
            args=scenario(owner,skills[0],mode,**{key:value})
            if key=='ghost_casts':args['ghost_count']=1
            check(61,args)

for elite,number,rank in ((2,3,10),(1,2,7)):
    for mode in ('frames','continuous'):
        plain=None
        for flag in (False,True):
            result,text=check(62,scenario('char_2025_shu',number,mode,rank,
                elite=elite,level=90 if elite==2 else 80,four_sui=flag))
            if not flag:
                plain=result;assert 'shu_periodic_sp_reference' not in result
            elif elite==1:assert strict(result)==strict(plain)
            else:
                ref=result['shu_periodic_sp_reference'];skill=result['estimate']['skill']
                assert abs(result['estimate']['base_stats']['attack']-plain['estimate']['base_stats']['attack']*1.12)<1e-7
                assert ref['interval_seconds_parameter']==4 and ref['sp_per_pulse_parameter']==1
                assert ref['first_tick_seconds'] is None and ref['clock_verified'] is False
                assert ref['events_scheduled'] is False
                assert all(skill[k] is None for k in ('initial_seconds','recharge_seconds','cycle_seconds'))
                assert '实际周期首跳：未知' in text

training=[({'elite':0,'level':45,'module_id':None,'module_level':0},4,2),
          ({'elite':1,'level':60,'module_id':None,'module_level':0},7,3),
          ({'elite':2,'level':70,'module_id':None,'module_level':0},10,4),
          ({'elite':2,'level':39,'module_id':'uniequip_002_deepcl','module_level':3},10,4),
          ({'elite':2,'level':40,'module_id':'uniequip_002_deepcl','module_level':1},10,7),
          ({'elite':2,'level':40,'module_id':'uniequip_002_deepcl','module_level':2},10,7),
          ({'elite':2,'level':40,'module_id':'uniequip_002_deepcl','module_level':3},10,7)]
for state,rank,cap in training:
    for number in ((1,) if state['elite']==0 else (1,2)):
        for mode in ('frames','continuous'):
            for value in (0,1,cap):
                result,text=check(63,scenario('char_110_deepcl',number,mode,rank,**state,summon_count=value))
                report=metrics(result,'summons')
                assert type(report['summon_count']) is int and report['summon_count']==value
                assert report['concurrent_limit']==cap
                if number==1:
                    regen=metrics(result,'regeneration')
                    rate=catalog()['operators']['char_110_deepcl']['skills'][0]['levels'][rank-1]['values']['hp_recovery_per_sec']
                    assert regen['per_token_rate']==rate and regen['all_tokens_rate']==rate*value
                if cap==7:
                    mod=metrics(result,'relic_token_token_10001_deepcl_tentac')
                    assert type(mod['model_count']) is int and mod['model_count']==value
                    assert mod['held_limit']==mod['concurrent_limit']==7
                    assert '关卡可用部署位、地块和当前库存约束' in text
                assert '局外假设' in text

for rank in (1,7,10):
    factor={1:1.15,7:1.25,10:1.3}[rank]
    for mode in ('frames','continuous'):
        for coop in (False,True):
            plain=None
            for flag in (False,True):
                result,text=check(64,scenario('silverash',3,mode,rank,cooperative=coop,preexisting_fragile=flag))
                assert [r['name'] for r in result['components']]==(['本体丹增','协同丹增'] if coop else ['本体丹增'])
                assert all(r['damage_type']=='physical' for r in result['components'])
                if not flag:plain=result
                else:
                    assert abs(result['total_damage']-plain['total_damage']*factor)<1e-7
                    for old,new in zip(plain['components'],result['components']):
                        assert old['hits']==new['hits'] and abs(new['per_hit']-old['per_hit']*factor)<1e-7
for mode in ('frames','continuous'):
    plain=None
    for flag in (False,True):
        result,text=check(64,scenario('silverash',2,mode,7,elite=1,level=80,preexisting_fragile=flag))
        if not flag:plain=result
        else:assert strict(result)==strict(plain)

scopes=[('positive',10,{}),('zero_window',0,{}),
        ('zero_lifetime',10,{'target_disappears_seconds':0}),
        ('empty_target_windows',10,{'target_windows':[]})]
for mode in ('frames','continuous'):
    for name,horizon,timing in scopes:
        for value in (0,1):
            result,text=check(65,scenario('char_1042_phatm2',2,mode,level=60,
                window_seconds=horizon,timing=timing,bait_triggers=value))
            sections=[s['id'] for s in result['report']['sections']]
            if value==0:
                assert 'neural_bait_reference' not in result and 'neural_bait' not in sections
                assert '本能的召唤 · 诱饵持续效果待核验' not in text
            else:
                ref=result['neural_bait_reference'];m=metrics(result,'neural_bait')
                assert type(ref['triggers_requested']) is int and ref['triggers_requested']==1
                assert ref['snapshot_attack'] is None and ref['first_tick_seconds'] is None
                assert ref['events_scheduled'] is False
                assert m['trigger_count']==1 and m['snapshot_attack'] is None and m['first_tick'] is None
                if name in ('zero_window','zero_lifetime'):
                    assert ref['affected_damage_phases']['window'] is False
                else:
                    assert result['total_damage'] is None and result['estimate']['skill']['window_dps'] is None
            if name in ('zero_window','zero_lifetime'):assert result['total_damage']==0
    result,text=check(65,scenario('char_1042_phatm2',1,mode,level=60))
    assert 'neural_bait_reference' not in result

assert source_hashes()==before
assert dict(counts)=={61:96,62:8,63:78,64:28,65:18}
receipt={'scope':'API-only future GUI assertion design validation; not actual Qt/Wine proof',
         'source_hashes':before,'source_drift':[],'calls':len(rows),'counts_by_section':dict(counts),
         'all_public_calls_returned':True,'gui_executed':False,'wine_executed':False,'records':rows}
full=gzip.compress(json.dumps(receipt,ensure_ascii=False,allow_nan=False).encode(),mtime=0)
(P/'public-schema-checks.json.gz').write_bytes(full)
summary={k:v for k,v in receipt.items() if k not in ('records','source_hashes')}
summary['source_hashes_receipt']='public-schema-checks.json.gz'
summary['full_gzip_sha256']=hashlib.sha256(full).hexdigest()
(P/'public-schema-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False))
