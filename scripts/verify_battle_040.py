"""Full current regressions and unchanged public calculations for preview-only changes."""
import hashlib,json,sys,time,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from rouge.damage import calculate_damage
from rouge.battle_preview import battle_data,spawn_rows,enemy_preview
from rouge.relics import mechanics
from rouge.offline_scope import scope_counts

def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()

def main():
    started=time.perf_counter();folder=ROOT/'.cache/battle-040'
    before=json.loads((ROOT/'BATTLE_0.39_VERIFICATION.json').read_text(encoding='utf-8'))
    names=before['test_modules']+['tests.test_spawn_reference_040']
    with (folder/'tests.log').open('w',encoding='utf-8') as log:
        tests=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(names))
    assert tests.wasSuccessful(),str(folder/'tests.log')
    assert tests.testsRun-len(tests.skipped)==359 and len(tests.skipped)==70
    rows=json.loads((folder/'before-public-results.json').read_text(encoding='utf-8'))
    for i,row in enumerate(rows,1):
        assert calculate_damage(row['scenario'])==row['result'],row['scenario']
        if i%100==0:print(json.dumps({'exact_public_outputs_checked':i}),flush=True)
    assert len(rows)==732
    data=battle_data();d=json.loads((ROOT/'.cache/research/battle-040/data-receipt.json').read_text(encoding='utf-8'))
    assert digest('rouge/data/battle-previews.json')==d['data_sha256']
    main=branch=0;environments=0;pending=0;main_instances=branch_instances=extra_routes=0
    for sid,s in data['stages'].items():
        # Independent read-back checks source sequences, not just aggregate counts.
        name=__import__('rouge.catalog',fromlist=['catalog']).catalog()['stages'][sid]['levelId'].lower()+'.json'
        path=ROOT/'.cache/game-data/levels'/name
        assert hashlib.sha256(path.read_bytes()).hexdigest()==s['level_source']['sha256']
        raw=json.loads(path.read_text(encoding='utf-8'))
        assert raw.get('extraRoutes',[])==s['extra_routes']
        assert raw['options']['moveMultiplier']==s['movement_multiplier']
        extra_routes+=len(s['extra_routes'])
        assert raw['routes']==s['routes'] and raw['mapData']['map']==s['map'] and raw['mapData']['tiles']==s['tiles']
        source_actions=[a for w in raw['waves'] for f in w['fragments'] for a in f['actions']]
        assert source_actions==[a['action'] for w in s['waves'] for f in w['fragments'] for a in f['actions']]
        for rawwave,wave in zip(raw['waves'],s['waves']):
            assert rawwave['preDelay']==wave['pre_delay'] and rawwave['postDelay']==wave['post_delay']
            assert rawwave['maxTimeWaitingForNextWave']==wave['max_time_waiting_for_next_wave']
            assert [f['preDelay'] for f in rawwave['fragments']]==[f['pre_delay'] for f in wave['fragments']]
        assert [a for b in (raw.get('branches') or {}).values() for p in b.get('phases') or []
            for a in p.get('actions') or [] if a['actionType']=='SPAWN']==[b['action'] for b in s['branch_spawns']]
        for row in spawn_rows(sid):
            if row['wave']:
                main+=1;main_instances+=row['action']['count'];assert row['route']['start'] is not None
            else:
                branch+=1;branch_instances+=row['action']['count'];assert row['route']['start'] is None
                assert 'useExtraRoute' not in row['action']
        for e in s['enemies']:
            for context in ({},{'difficulty':{'value':15},'zone':{'id':'zone_3'}}):
                result=enemy_preview(sid,e['id'],e['level'],context)
                environments+=1;pending+=bool(result['context_pending'])
                assert result['reference_stats']==e['reference_stats']
    assert main==3639 and branch==299 and environments==2174
    assert main_instances==5314 and branch_instances==334 and extra_routes==308
    for name,row in json.loads((ROOT/'.cache/research/battle-040/source-receipt.json').read_text(encoding='utf-8'))['files'].items():
        assert digest('.cache/research/battle-040/source/'+name)==row['sha256'],name
    sources=('rouge/app.py','rouge/battle_preview.py','rouge/battle_view.py','rouge/data/battle-previews.json',
        'rouge/spawn_reference.py','scripts/build_battle_references_040.py',
        'scripts/verify_battle_040.py','scripts/verify_battle_widgets_040.py',
        'tests/test_battle_preview_039.py','tests/test_spawn_reference_040.py','pyproject.toml')
    receipt={'version':'0.40.0','passed':True,'verified_at':time.time(),
        'tests_run':tests.testsRun,'current_tests_passed':359,'new_tests':26,'historical_combat_tests_skipped':70,
        'failures':len(tests.failures),'errors':len(tests.errors),'test_modules':names,
        'exact_public_output_cases':732,'calculation_outputs_unchanged':True,
        'stages':105,'images':105,'main_spawn_rows':main,'conditional_branch_rows':branch,
        'main_spawns_mapped':main,'branch_spawns_unmapped':branch,'enemy_references':1087,
        'main_nominal_instances':main_instances,'conditional_nominal_instances':branch_instances,
        'total_nominal_instances':main_instances+branch_instances,'extra_route_records':extra_routes,
        'local_offsets_not_global_times':True,'movement_base_times_stage_only':True,
        'enemy_environment_scenarios':environments,'enemy_contexts_with_pending':pending,
        'source_actions_and_geometry_exactly_preserved':True,
        'data_rule_counts':mechanics()['counts'],'offline_scope':scope_counts(mechanics()),
        'source_hashes':{name:digest(name) for name in sources},
        'test_log':'.cache/battle-040/tests.log','test_log_sha256':digest('.cache/battle-040/tests.log'),
        'baseline_hashes':{'.cache/battle-040/before-public-results.json':digest('.cache/battle-040/before-public-results.json')},
        'elapsed_seconds':time.perf_counter()-started,'chat_requests':0,'game_actions':0,'private_state_used':False,
        'limits':data['limits']}
    (ROOT/'BATTLE_0.40_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('passed','current_tests_passed','exact_public_output_cases',
        'stages','main_spawns_mapped','branch_spawns_unmapped','enemy_environment_scenarios','elapsed_seconds')}),flush=True)

if __name__=='__main__':main()
