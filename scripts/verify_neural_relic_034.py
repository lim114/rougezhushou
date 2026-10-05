"""Pinned neural burst evidence, partial damage, and public-entry regressions."""
import copy,hashlib,json,math,sys,time,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from verify_offline_scope_030 import NAMES,output
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.relics import mechanics
from rouge.offline_scope import partition,scope_counts
from tests.test_neural_relic_034 import RIVER

FILES=('rouge/relics.py','rouge/operator_engine.py','rouge/elemental_relics.py',
    'rouge/reporting.py','rouge/app.py','rouge/offline_scope.py',
    'rouge/data/relic-mechanics.json','scripts/build_relic_mechanics.py',
    'tests/test_neural_relic_034.py','scripts/verify_neural_relic_034.py')


def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))


def near(actual,expected):
    if expected is None:assert actual is None,(actual,expected)
    else:assert actual is not None and math.isclose(actual,expected,rel_tol=1e-12,abs_tol=1e-8),(actual,expected)


def check_baseline():
    before=read('.cache/relic-034/before-public-results.json')
    assert len(before)==348
    unchanged=neural=partial=0
    for row in before:
        s=row['scenario'];old=row['result'];r=calculate_damage(s);current=output(r)
        reference=r.get('neural_relic_reference')
        if not reference:
            assert current==old,s
            unchanged+=1;continue
        neural+=1
        expected=copy.deepcopy(old)
        for c in expected['components']:
            if c['name']=='神经损伤爆发':
                c['per_hit']*=2;c['total']*=2
        fields=reference['affected_damage_phases']
        if fields['window']:expected['total_damage']=None
        for phase,keys in {'cast':('total_damage','phase_damage'),
                           'window':('window_damage','window_dps'),
                           'cycle':('cycle_damage','cycle_dps')}.items():
            if fields[phase]:
                for key in keys:expected['skill'][key]=None
        assert current==expected,s
        # Independent delta oracle: one additional ordinary 6000-point burst
        # for each unchanged, already-modelled burst; no invented DoT ticks.
        subtotals=r.get('known_damage_subtotals')
        if subtotals:
            oldskill=old['skill'];partial+=1
            additions={p:6000*len(reference[p+'_burst_times']) for p in ('cast','window','cycle')}
            for key,phase in (('total_damage','cast'),('cycle_damage','cycle')):
                value=oldskill[key]
                near(subtotals[key],None if value is None else value+additions[phase])
            phase_times=reference['cast_burst_times']
            duration=oldskill['duration_seconds']
            phase_extra=6000*sum(t<duration for t in phase_times) if duration is not None else 0
            near(subtotals['phase_damage'],None if oldskill['phase_damage'] is None else oldskill['phase_damage']+phase_extra)
            near(subtotals['window_damage'],old['total_damage']+additions['window'])
            cycle=oldskill['cycle_seconds']
            near(subtotals['cycle_dps'],None if oldskill['cycle_dps'] is None else oldskill['cycle_dps']+additions['cycle']/cycle)
            assert not reference['periodic_damage_scheduled']
            assert not r['complete'] and not r['estimate']['complete']
    assert unchanged+neural==348 and unchanged>=174
    return {'public_before_after_cases':348,'unaffected_exactly_equal':unchanged,
            'neural_component_cases':neural,'partial_damage_cases':partial,
            'baseline_sha256':digest('.cache/relic-034/before-public-results.json')}


def main():
    start=time.perf_counter();folder=ROOT/'.cache/relic-034';folder.mkdir(parents=True,exist_ok=True)
    hashes={n:digest(n) for n in FILES}
    modules=NAMES+['tests.test_offline_relics_031','tests.test_spawn_hp_033',
        'tests.test_relic_grade_sync_032','tests.test_run_reuse_guards_032','tests.test_sampling_flow',
        'tests.test_neural_relic_034']
    with (folder/'tests.log').open('w',encoding='utf-8') as log:
        tested=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(modules))
    assert tested.wasSuccessful(),str(folder/'tests.log')
    print(json.dumps({'passed_tests':tested.testsRun-len(tested.skipped),'historical_skipped':len(tested.skipped)}),flush=True)
    matrix=check_baseline()
    data=mechanics();old=read('.cache/batch-034-before/rouge/data/relic-mechanics.json')
    assert set(old['relics'])==set(data['relics'])
    changed=[r for r in old['relics'] if old['relics'][r]!=data['relics'][r]]
    assert changed==[RIVER]
    assert old['char_buffs']==data['char_buffs']
    assert all(old['relics'][r]['raw_buffs']==data['relics'][r]['raw_buffs'] for r in data['relics'])
    raw=read('.cache/game-data/roguelike_topic_table.json')['details']['rogue_6']
    original=raw['relics'][RIVER]['buffs']
    assert original==data['relics'][RIVER]['raw_buffs']
    neural_raw=next(b for b in original if any(v['key']=='key' and v['valueStr']=='rogue_6_enemy_ep_break_fix[sanity]' for v in b['blackboard']))
    board={b['key']:b['valueStr'] if b.get('valueStr') is not None else b['value'] for b in neural_raw['blackboard']}
    assert board=={'key':'rogue_6_enemy_ep_break_fix[sanity]','damage_scale':2,'damage':1000,'interval':1}
    active=[(r,p) for r,p in data['relics'].items() if partition(p,r)[0]]
    evidence={'version':'0.34.0','verified_at':time.time(),'source_url':data['source_url'],
        'source_sha256':digest('.cache/game-data/roguelike_topic_table.json'),'source_commit':data['commit'],
        'relic_id':RIVER,'raw_buffs':original,'decoded_neural_parameters':board,
        'community_url':'https://prts.wiki/w/沉沦者的黑流树海/拟造物质编目#河谷祭祈',
        'element_baseline_url':'https://prts.wiki/w/元素','community_checked_date':'2026-10-03',
        'raw_parameters_vs_script_boundary':'Blackboard parameters and detailed community descriptions agree; no hidden script or first-tick oracle was recovered.',
        'changed_relic_ids':changed,'char_buffs_unchanged':True,
        'independent_examples':[
            {'description':'20% elemental resistance; no other elemental amplification',
             'burst':9600,'formula':'6000 * 2 * 0.8'},
            {'description':'Mantra S2 first-hit known subtotal at max default training, initial neural buildup 999',
             'known_subtotal':11563,'formula':'755 * 2.4 + 6000 * 2 * 0.8 + 755 * 0.25 * 0.8'},
            {'description':'Ice in Fire elemental vulnerability with 20% elemental resistance',
             'burst':16800,'formula':'6000 * 2 * 0.8 * 1.75'}],
        'limits':['Only the instantaneous neural burst multiplier is scheduled; periodic first tick, end boundary and cooldown-acceleration interaction remain unknown.',
            'The 1000-point, 1-second periodic parameters do not prove a fixed ten-tick timeline; full affected totals/DPS remain unknown with a separate known subtotal.',
            'Dark, fire and water branches are still pending; no other operator acquires an invented elemental source.',
            'Existing neural skill/target-window approximations remain; no new live-combat calibration or recognition benchmark.']}
    proof=ROOT/'.cache/research/relics-034';proof.mkdir(parents=True,exist_ok=True)
    (proof/'evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
    assert hashes=={n:digest(n) for n in FILES}
    receipt={'version':'0.34.0','passed':True,'verified_at':time.time(),
        'tests_run':tested.testsRun,'current_tests_passed':tested.testsRun-len(tested.skipped),
        'new_tests':unittest.defaultTestLoader.loadTestsFromName('tests.test_neural_relic_034').countTestCases(),
        'historical_combat_tests_skipped':len(tested.skipped),
        'skipped_tests':[{'test':t.id(),'reason':r} for t,r in tested.skipped],
        'failures':len(tested.failures),'errors':len(tested.errors),'test_modules':modules,
        'test_log':'.cache/relic-034/tests.log','test_log_sha256':digest('.cache/relic-034/tests.log'),
        **matrix,'changed_relic_ids':changed,'char_buffs_unchanged':True,'raw_buffs_unchanged':True,
        'offline_scope':scope_counts(data),'data_rule_counts':data['counts'],
        'active_relic_items':len(active),'active_items_without_data_pending':sum(not partition(p,r)[2] for r,p in active),
        'source_hashes':hashes,'chat_requests':0,'game_actions':0,'new_live_combat_measurements':0,
        'elapsed_seconds':time.perf_counter()-start,'limits':evidence['limits']}
    (ROOT/'RELIC_0.34_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('passed','current_tests_passed','new_tests',
        'public_before_after_cases','unaffected_exactly_equal','neural_component_cases',
        'partial_damage_cases','active_relic_items','offline_scope','elapsed_seconds')},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
