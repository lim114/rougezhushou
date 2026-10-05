"""Current offline regression and spawn-HP alternatives, with no game or chat."""
import hashlib,importlib.util,json,sys,time,unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from verify_offline_scope_030 import NAMES,output
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.relics import mechanics
from rouge.offline_scope import scope_counts
from tests.test_spawn_hp_033 import scenario,target,COFFEE,PICTURE,FIRE,DRAGON

FILES=('rouge/relics.py','rouge/run_modifiers.py','rouge/reporting.py','rouge/app.py',
    'rouge/offline_scope.py','rouge/data/relic-mechanics.json','scripts/build_relic_mechanics.py',
    'tests/test_spawn_hp_033.py','scripts/verify_spawn_hp_033.py')


def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
def read(name):return json.loads((ROOT/name).read_text(encoding='utf-8-sig'))


def main():
    start=time.perf_counter();folder=ROOT/'.cache/relic-033';folder.mkdir(parents=True,exist_ok=True)
    hashes={n:digest(n) for n in FILES}
    modules=NAMES+['tests.test_offline_relics_031','tests.test_spawn_hp_033',
        'tests.test_relic_grade_sync_032','tests.test_run_reuse_guards_032','tests.test_sampling_flow']
    with (folder/'tests.log').open('w',encoding='utf-8') as log:
        tested=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(modules))
    assert tested.wasSuccessful(),str(folder/'tests.log')
    print(json.dumps({'passed_tests':tested.testsRun-len(tested.skipped),'historical_skipped':len(tested.skipped)}),flush=True)
    spec=importlib.util.spec_from_file_location('rouge._relics_previous_033',ROOT/'.cache/batch-033-before/rouge/relics.py')
    previous=importlib.util.module_from_spec(spec);spec.loader.exec_module(previous)
    matrices=combos=0
    for op,profile in catalog()['operators'].items():
        for skill in range(1,len(profile['skills'])+1):
            for mode in ('frames','continuous'):
                for grade in (0,5,15):
                    for stage in ('ro6_n_1_2','ro6_e_1_2'):
                        s=scenario(operator=op,skill=skill,timing_mode=mode,target_enemy=target(stage),
                            run_config={'difficulty':{'value':grade},'zone':{'id':'zone_2'}})
                        manual=calculate_damage({**s,'effects':[{'kind':'attack_pct','value':.3,'target_scope':'all_units'},
                            {'kind':'hp_pct','value':.3,'target_scope':'all_units'}]})
                        actual=calculate_damage({**s,'relic_ids':[COFFEE]})
                        with patch('rouge.relics.prepare',previous.prepare),patch('rouge.relics.finish',previous.finish):
                            older=calculate_damage({**s,'relic_ids':[COFFEE]})
                        # The previous implementation also records token modifier
                        # provenance; direct test effects lack that display record.
                        assert output(actual)==output(older),(op,skill,mode,grade,stage)
                        direct={k:v for k,v in output(manual).items() if k!='relic_token_stats'}
                        assert direct=={k:v for k,v in output(actual).items() if k!='relic_token_stats'},(op,skill,mode,grade,stage)
                        p=actual['run_resolution']['enemy']['spawn_hp']
                        assert p['probabilities']=={'untriggered':.97,'triggered':.03} and p['current_variant'] is None
                        hp=manual['run_resolution']['enemy']['stats']['maxHp']
                        assert p['untriggered_max_hp']==hp and p['triggered_max_hp']==hp*2
                        assert actual['relic_resolution']['complete']
                        matrices+=1
                for extra,context in (([PICTURE],{}),([PICTURE,'rogue_6_relic_legacy_85'],{}),
                    ([DRAGON],{}),([DRAGON],{'entered_zone_count':0}),
                    ([DRAGON],{'entered_zone_count':3})):
                    r=calculate_damage(scenario(operator=op,skill=skill,timing_mode=mode,
                        relic_ids=[COFFEE,*extra],relic_context=context))
                    p=r['run_resolution']['enemy']['spawn_hp']
                    assert (p['triggered_max_hp'] is None)==bool(p['excluded_hp_sources'])
                    assert p['current_variant'] is None
                    combos+=1
    assert matrices==1044 and combos==870
    print(json.dumps({'skill_environment_cases':matrices,'hp_combination_cases':combos}),flush=True)
    data=mechanics();old=read('.cache/batch-033-before/rouge/data/relic-mechanics.json')
    assert set(old['relics'])==set(data['relics'])
    changed=[r for r in old['relics'] if old['relics'][r]!=data['relics'][r]]
    assert changed==[COFFEE]
    assert old['char_buffs']==data['char_buffs']
    assert all(old['relics'][r]['raw_buffs']==data['relics'][r]['raw_buffs'] for r in data['relics'])
    assert hashes=={n:digest(n) for n in FILES}
    raw=read('.cache/game-data/roguelike_topic_table.json')['details']['rogue_6']
    original=raw['relics'][COFFEE]['buffs']
    assert original==data['relics'][COFFEE]['raw_buffs']
    board={b['key']:b['valueStr'] if b.get('valueStr') is not None else b['value'] for b in original[0]['blackboard']}
    assert board=={'key':'rogue_6_enemy_prob_max_hp','prob':.03,'max_hp':1}
    evidence={'version':'0.33.0','verified_at':time.time(),'source_url':data['source_url'],
        'source_sha256':digest('.cache/game-data/roguelike_topic_table.json'),'source_commit':data['commit'],
        'relic_id':COFFEE,'raw_buffs':original,'decoded_spawn_parameters':board,
        'community_url':'https://prts.wiki/w/沉沦者的黑流树海/拟造物质编目#猎犬咖啡',
        'changed_relic_ids':changed,'char_buffs_unchanged':True,
        'limits':['Only a single-item 2x spawn HP branch is confirmed; other relic HP order/combination remains unknown.',
            '3% is the per-enemy marginal; independent draws, current spawn outcomes and kill time are not inferred.',
            'Existing unverified stage scripts, enemy phases and difficulty gaps remain disclosed.']}
    proof=ROOT/'.cache/research/relics-033';proof.mkdir(parents=True,exist_ok=True)
    (proof/'evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
    receipt={'version':'0.33.0','passed':True,'verified_at':time.time(),
        'tests_run':tested.testsRun,'current_tests_passed':tested.testsRun-len(tested.skipped),
        'new_tests':17,'historical_combat_tests_skipped':len(tested.skipped),
        'skipped_tests':[{'test':t.id(),'reason':r} for t,r in tested.skipped],
        'failures':len(tested.failures),'errors':len(tested.errors),'test_modules':modules,
        'test_log':'.cache/relic-033/tests.log','test_log_sha256':digest('.cache/relic-033/tests.log'),
        'skill_environment_cases':matrices,'hp_combination_cases':combos,
        'changed_relic_ids':changed,'char_buffs_unchanged':True,'raw_buffs_unchanged':True,
        'offline_scope':scope_counts(data),'data_rule_counts':data['counts'],'source_hashes':hashes,
        'chat_requests':0,'game_actions':0,'new_live_combat_measurements':0,
        'elapsed_seconds':time.perf_counter()-start,'limits':evidence['limits']}
    (ROOT/'RELIC_0.33_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('passed','current_tests_passed','new_tests','skill_environment_cases',
        'hp_combination_cases','offline_scope','elapsed_seconds')},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
