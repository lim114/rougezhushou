"""SP acceptance: public entry matrix and independent 30-Hz cumulative oracle."""
import hashlib
import json
import math
import sys
import time
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.relics import mechanics

DEST=ROOT/'.cache/relic-026'
BLOOM='rogue_6_relic_legacy_118'
TANK='rogue_6_from_relic_4'


def events(times):
    return [{'at_seconds':time,'type':kind} for time in times for kind in ('attack','damage','elemental_loss')]


def oracle(required,rate,inputs,amounts,*,offset=0,block=0,wine_phase=None):
    """Brute-force cumulative SP per frame, independent of the event solver."""
    start=math.ceil((offset+block)*30-1e-9)
    discrete={}
    for event in inputs:
        release=math.ceil(event['at_seconds']*30-1e-9)
        if release>=start:
            discrete[release+1]=discrete.get(release+1,0)+amounts.get(event['type'],0)
    if wine_phase is not None:
        for frame in range(start+wine_phase+1,108001,45):
            discrete[frame]=discrete.get(frame,0)+1
    accrued=0
    for frame in range(start,108001):
        accrued+=discrete.get(frame,0)
        if accrued+rate*(frame-start)/30>=required-1e-9:
            return frame/30-offset
    return None


def main():
    DEST.mkdir(exist_ok=True)
    start=time.perf_counter()
    names=['tests.test_received_sp_026','tests.test_relic_candidates_025','tests.test_mantra_events_024',
        'tests.test_relic_events_022','tests.test_damage','tests.test_timing','tests.test_relics',
        'tests.test_relic_extension','tests.test_difficulty_rules','tests.test_wine_timing',
        'tests.test_relic_conditions_022','tests.test_report','tests.test_target_memory']
    names+=['tests.test_enemy_environment.EnemyEnvironmentTests.'+name for name in (
        'test_relic_enemy_modifiers_follow_stage_and_difficulty_and_are_reported',
        'test_portal_keeps_main_depth_and_missing_context_does_not_guess',
        'test_boss_reduction_is_independent_from_relic_vulnerability_and_preserves_healing_and_timing',
        'test_emergency_stage_and_region_use_pinned_enemy_instead_of_manual_defense')]
    with (DEST/'tests.log').open('w',encoding='utf-8') as output:
        tested=unittest.TextTestRunner(stream=output,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(names))
    assert tested.wasSuccessful(),str(DEST/'tests.log')
    cases=skills=0
    samples=[]
    for op,profile in catalog()['operators'].items():
        for number in range(1,len(profile['skills'])+1):
            skills+=1
            for mode in ('frames','continuous'):
                args={'operator':op,'skill':number,'timing_mode':mode}
                plain=calculate_damage(args)
                duration=plain['estimate']['skill']['duration_seconds'] or 0
                empty=calculate_damage({**args,'relic_ids':[BLOOM],
                    'timing':{'sp_events':{'initial':[],'cycle':[]}}})
                variants=[('missing',None),('empty',{'initial':[],'cycle':[]}),
                    ('sparse',{'initial':events([1,2,3]),'cycle':events([duration+1,duration+2,duration+3])}),
                    ('burst',{'initial':events([1]*100),'cycle':events([duration+1]*100)})]
                for name,table in variants:
                    scenario={**args,'relic_ids':[BLOOM]}
                    if table is not None:scenario['timing']={'sp_events':table}
                    result=calculate_damage(scenario)
                    for key in ('total_damage','total_healing','interval_seconds','components'):
                        assert result.get(key)==plain.get(key),(op,number,mode,name,key)
                    assert result['estimate']['base_stats']==plain['estimate']['base_stats']
                    assert not result['relic_resolution']['token_effects']
                    for key in ('initial_seconds','recharge_seconds','cycle_seconds','cycle_dps','cycle_hps'):
                        value=result['estimate']['skill'][key]
                        assert value is None or math.isfinite(value) and value>=0,(op,number,name,key,value)
                    if name in ('sparse','burst'):
                        for key in ('initial_seconds','recharge_seconds'):
                            value=result['estimate']['skill'][key];baseline=empty['estimate']['skill'][key]
                            if value is not None and baseline is not None:
                                assert value<=baseline+1e-8,(op,number,mode,name,key,value,baseline)
                    for phase,reference in result['estimate'].get('sp_events',{}).items():
                        if reference['status']=='missing':
                            assert not result['relic_resolution']['complete']
                            assert result['estimate']['skill']['initial_seconds' if phase=='initial' else 'recharge_seconds'] is None
                    cases+=1
                samples.append({'operator':op,'skill':number,'mode':mode,
                    'plan_mode':plain['estimate']['skill'].get('mode'),
                    'empty_initial_seconds':empty['estimate']['skill']['initial_seconds'],
                    'empty_cycle_seconds':empty['estimate']['skill']['cycle_seconds']})
    assert skills==87 and cases==696,(skills,cases)
    oracle_cases=[]
    for kind,ids,bindings,amounts in (
            ('tank',[],[TANK],{'attack':2}),
            ('bloom',[BLOOM],[],{'damage':1,'elemental_loss':1}),
            ('combined',[BLOOM],[TANK],{'attack':2,'damage':1,'elemental_loss':1})):
        for block in (0,2,3.25):
            for times in ([],[1,2,3],[.001,1.001,2.001],[1]*20):
                initial=events(times);cycle=events([1,39.9,40]+[40+block+t for t in times])
                result=calculate_damage({'operator':'mechanist','skill':3,'relic_ids':ids,'char_buff_ids':bindings,
                    'timing':{'sp_lockout_extra_seconds':block,'sp_events':{'initial':initial,'cycle':cycle}}})
                skill=result['estimate']['skill']
                first=oracle(10,1,initial,amounts)
                recharge=oracle(35,1,cycle,amounts,offset=40,block=math.ceil(block*30)/30)
                assert abs(skill['initial_seconds']-first)<1e-8,(kind,block,times,skill['initial_seconds'],first)
                assert abs(skill['recharge_seconds']-recharge)<1e-8,(kind,block,times,skill['recharge_seconds'],recharge)
                oracle_cases.append({'rules':kind,'block':block,'times':times,'initial':first,'recharge':recharge})
    wine_args={'operator':'mechanist','skill':1,'continuous_attacks':False,
               'relic_ids':['rogue_6_relic_legacy_97'],'char_buff_ids':[TANK]}
    duration=calculate_damage(wine_args)['estimate']['skill']['duration_seconds']
    incoming={'initial':[{'at_seconds':.2,'type':'attack'}],
              'cycle':[{'at_seconds':duration+.2,'type':'attack'}]}
    wine=calculate_damage({**wine_args,'timing':{'sp_events':incoming}})['estimate']['skill']
    for key,required,offset,table in (('initial_seconds_range',2,0,incoming['initial']),
                                    ('recharge_seconds_range',7,duration,incoming['cycle'])):
        values=[oracle(required,0,table,{'attack':2},offset=offset,wine_phase=phase) for phase in range(46)]
        assert all(v is not None for v in values)
        assert abs(wine[key]['lower']-min(values))<1e-8,(key,wine[key],min(values))
        assert abs(wine[key]['upper']-max(values))<1e-8,(key,wine[key],max(values))
    current=mechanics()
    before=json.loads((ROOT/'.cache/batch-026-before/rouge/data/relic-mechanics.json').read_text(encoding='utf-8'))
    changed_relics=[rid for rid,data in current['relics'].items() if data!=before['relics'][rid]]
    changed_bindings=[bid for bid,data in current['char_buffs'].items() if data!=before['char_buffs'][bid]]
    assert changed_relics==[BLOOM],changed_relics
    assert changed_bindings==[TANK],changed_bindings
    raw_path=ROOT/'.cache/game-data/roguelike_topic_table.json'
    raw_sha=hashlib.sha256(raw_path.read_bytes()).hexdigest()
    assert raw_sha==current['source_sha256']
    raw=json.loads(raw_path.read_text(encoding='utf-8'))['details']['rogue_6']
    assert len(current['relics'])==272
    evidence={'source_commit':current['commit'],'source_sha256':raw_sha,
        'source_url':current['source_url'],'changed_relics':changed_relics,'changed_bindings':changed_bindings,
        'bloom_raw':raw['relics'][BLOOM]['buffs'],'bloom_rules':current['relics'][BLOOM],
        'tank_parent':current['relics']['rogue_6_relic_assign_4'],'tank_binding':current['char_buffs'][TANK],
        'web_sources':['https://prts.wiki/w/沉沦者的黑流树海/拟造物质编目','https://prts.wiki/w/游戏数据基础#异常效果（AbnormalFlag）'],
        'oracle_cases':oracle_cases,'wine_oracle_phases':46,'matrix':samples}
    (DEST/'evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
    files=('scripts/build_relic_mechanics.py','rouge/relics.py','rouge/sp_events.py','rouge/timing.py',
        'rouge/damage.py','rouge/estimate.py','rouge/operator_engine.py','rouge/reporting.py','rouge/app.py',
        'rouge/data/relic-mechanics.json','tests/test_received_sp_026.py','scripts/verify_received_sp_026.py')
    receipt={'version':'0.26.0','verified_at':time.time(),'passed':True,'tests':tested.testsRun,
        'failures':len(tested.failures),'errors':len(tested.errors),'seconds':round(time.perf_counter()-start,3),
        'matrix_skills':skills,'matrix_cases':cases,'matrix_modes':['frames','continuous'],
        'independent_oracle_cases':len(oracle_cases),'wine_oracle_phases':46,
        'data_rule_counts':current['counts'],'changed_relics':changed_relics,'changed_bindings':changed_bindings,
        'source_commit':current['commit'],'source_sha256':raw_sha,
        'source_sha256_files':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files},
        'evidence':'.cache/relic-026/evidence.json','chat_requests':0,'game_actions':0,
        'limits':['Explicit offline callback tables; no automatic incoming-hit or recipient reading.',
            'Attack, damage and elemental-loss callbacks cannot be inferred from one another.',
            'Non-forced SP blocking and next-tick credit are reference assumptions pending client calibration.',
            'One initial phase and one cycle; no steady-state replay or unlisted future hits.',
            'Wine phase remains a marginal envelope; its hidden blocking script is unverified.',
            'No new live incoming-hit measurement or full OCR performance replay.']}
    (ROOT/'RELIC_0.26_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in receipt.items() if k!='source_sha256_files'},ensure_ascii=False))


if __name__=='__main__':main()
