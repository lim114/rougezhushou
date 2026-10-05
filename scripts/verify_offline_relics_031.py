"""0.31 public offline regressions and independent stat/environment references."""
import hashlib,json,sys,time,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from verify_offline_scope_030 import NAMES,output
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.offline_scope import partition,scope_counts
from rouge.relics import mechanics

FILES=('rouge/relics.py','rouge/deployment.py','rouge/reporting.py','rouge/app.py',
    'rouge/offline_scope.py','scripts/build_relic_mechanics.py','scripts/verify_relic_mechanics.py',
    'rouge/data/relic-mechanics.json','tests/test_offline_relics_031.py','scripts/verify_offline_relics_031.py')


def main():
    start=time.perf_counter();folder=ROOT/'.cache/relic-031';folder.mkdir(parents=True,exist_ok=True)
    before={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in FILES}
    names=NAMES+['tests.test_offline_relics_031']
    with (folder/'tests.log').open('w',encoding='utf-8') as log:
        tested=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(names))
    assert tested.wasSuccessful(),str(folder/'tests.log')
    refs=[]
    for rid,entry in mechanics()['relics'].items():
        a,r,p,rp=partition(entry,rid)
        if (r or rp) and not(a or p):refs.append(rid)
    red=fees=environment=reference_cases=0
    for op,profile in catalog()['operators'].items():
        for skill in range(1,len(profile['skills'])+1):
            for mode in ('frames','continuous'):
                s={'operator':op,'skill':skill,'timing_mode':mode};base=calculate_damage(s)
                for count in (0,3,99,10000):
                    r=calculate_damage({**s,'relic_ids':['rogue_6_relic_cargo_2'],'relic_context':{'parts_count':count}})
                    manual=calculate_damage({**s,'effects':[{'kind':'attack_pct','value':.08*min(count,99)},
                        {'kind':'hp_pct','value':.08*min(count,99)}]})
                    assert output(r)==output(manual),(op,skill,mode,count)
                    assert r['relic_resolution']['complete'] and not r['relic_token_stats'],(op,skill,count)
                    red+=1
                r=calculate_damage({**s,'relic_ids':['rogue_6_relic_book_3']})
                assert r['estimate']['base_stats']==base['estimate']['base_stats'] and r['estimate']['skill']==base['estimate']['skill']
                if profile['profession']=='tank':
                    first=r['deployment_reference']['first_deployment_cost']
                    assert first['unrounded_single_item_reference']==base['deployment_cost']*.25
                    assert first['actual_cost'] is None and r['deployment_cost'] is None and first['first_deployment_only']
                else:
                    assert 'deployment_reference' not in r and r['deployment_cost']==base['deployment_cost']
                    assert r['relic_resolution']['records'][0]['status']=='inapplicable'
                fees+=1
                for difficulty in (0,10,11,15,None):
                    for eid in ('enemy_1093_ccsbr','enemy_2137_shsdgo'):
                        config={'zone':{'id':'zone_2'}}
                        if difficulty is not None:config['difficulty']={'value':difficulty}
                        args={**s,'target_enemy':{'stage_id':'ro6_n_1_2','enemy_id':eid,'level':0},'run_config':config}
                        plain=calculate_damage(args);hydra=calculate_damage({**args,'relic_ids':['rogue_6_start_4']})
                        a=plain['run_resolution']['enemy']['stats'];b=hydra['run_resolution']['enemy']['stats']
                        assert b['atk']==a['atk']*1.3 and b['maxHp']==a['maxHp']*1.3,(op,skill,mode,difficulty,eid)
                        assert b['def']==a['def'] and b['magicResistance']==a['magicResistance']
                        assert hydra['estimate']['base_stats']==plain['estimate']['base_stats']
                        environment+=1
                for rid in refs:
                    r=calculate_damage({**s,'relic_ids':[rid]})
                    assert output(r)==output(base),(rid,op,skill,mode)
                    assert not r['relic_resolution']['records'][0]['pending'] and not r['relic_resolution']['rules']
                    reference_cases+=1
        print(json.dumps({'operator':op,'red_cases':red,'first_cost_cases':fees,'enemy_cases':environment,'reference_cases':reference_cases}),flush=True)
    old=json.loads((ROOT/'.cache/batch-031-before/rouge/data/relic-mechanics.json').read_text(encoding='utf-8'))
    data=mechanics();changed=[rid for rid,e in data['relics'].items() if e!=old['relics'][rid]]
    assert set(changed)=={'rogue_6_relic_cargo_2','rogue_6_relic_book_3','rogue_6_start_4'}
    assert old['char_buffs']==data['char_buffs'] and data['source_sha256']==old['source_sha256']
    assert before=={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in FILES}
    recognition=hashlib.sha256((ROOT/'rouge/relic_recognition.py').read_bytes()).hexdigest()
    assert recognition=='8edff23d07bd013063d6c0d2fe4993500f66a80026a5d44c83373b8d4e700eb6'
    receipt={'version':'0.31.0','passed':True,'verified_at':time.time(),'tests_run':tested.testsRun,
        'current_tests_passed':tested.testsRun-len(tested.skipped),'new_tests':16,'historical_combat_tests_skipped':len(tested.skipped),
        'skipped_tests':[{'test':test.id(),'reason':reason} for test,reason in tested.skipped],
        'failures':len(tested.failures),'errors':len(tested.errors),'test_modules':names,
        'parts_stat_oracle_cases':red,'first_cost_cases':fees,'enemy_environment_cases':environment,
        'reference_non_interference_cases':reference_cases,'skills':87,'timing_modes':2,
        'changed_relic_ids':changed,'char_buffs_unchanged':True,'primary_source_unchanged':True,
        'data_rule_counts':data['counts'],'offline_scope':scope_counts(data),'recognition_unchanged':True,
        'recognition_sha256':recognition,'source_hashes':before,'elapsed_seconds':time.perf_counter()-start,
        'chat_requests':0,'game_actions':0,'new_live_combat_measurements':0,
        'limits':['Offline references, not hidden script/lifecycle/rounding/combination calibration.',
            'Hydra persistent ally growth remains pending; no inference from region depth or unseen earlier gains.',
            'Only 3 data records change; battle callbacks remain reference-only.']}
    (ROOT/'RELIC_0.31_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('passed','current_tests_passed','new_tests','historical_combat_tests_skipped',
        'parts_stat_oracle_cases','first_cost_cases','enemy_environment_cases','reference_non_interference_cases','elapsed_seconds')},ensure_ascii=False))


if __name__=='__main__':main()
