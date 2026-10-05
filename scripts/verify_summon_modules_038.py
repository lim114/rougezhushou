"""Public regression and module matrix against saved actual 0.37 outputs."""
import hashlib,json,sys,time,unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from rouge.damage import calculate_damage
from rouge.catalog import catalog
from rouge.relics import mechanics
from rouge.offline_scope import scope_counts
from rouge.summons import module_reference

def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()

def damage_payload(result):
    return {'base_stats':result['estimate']['base_stats'],'skill':result['estimate']['skill'],
            **{k:result.get(k) for k in ('total_damage','total_healing','components','timing','deployment_cost')}}

def main():
    started=time.perf_counter();folder=ROOT/'.cache/summon-038'
    previous=json.loads((ROOT/'IMPACT_0.37_VERIFICATION.json').read_text(encoding='utf-8'))
    names=previous['test_modules']+['tests.test_summon_modules_038']
    with (folder/'tests.log').open('w',encoding='utf-8') as log:
        tests=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(names))
    assert tests.wasSuccessful(),str(folder/'tests.log')
    assert tests.testsRun-len(tests.skipped)==309 and len(tests.skipped)==70
    rows=json.loads((folder/'before-public-results.json').read_text(encoding='utf-8'))
    for i,row in enumerate(rows,1):
        assert calculate_damage(row['scenario'])==row['result'],row['scenario']
        if i%100==0:print(json.dumps({'exact_public_outputs_checked':i}),flush=True)
    assert len(rows)==732
    module_rows=json.loads((folder/'before-module-results.json').read_text(encoding='utf-8'))
    changed=unchanged=0
    profile=catalog()['operators']['char_110_deepcl'];tid='token_10001_deepcl_tentac'
    for row in module_rows:
        s=row['scenario'];before=row['result'];after=calculate_damage(s)
        assert damage_payload(after)==damage_payload(before),s
        if module_reference(profile,s,tid):
            assert after!=before,s;changed+=1
        else:assert after==before,s;unchanged+=1
    assert len(module_rows)==264 and changed==108 and unchanged==156
    combinations=0
    for skill in (1,2):
        for rid in mechanics()['relics']:
            s={'operator':'char_110_deepcl','skill':skill,'module_id':'uniequip_002_deepcl',
               'module_level':3,'relic_ids':[rid]}
            actual=calculate_damage(s)
            with patch('rouge.summons.module_rules',return_value={}):without=calculate_damage(s)
            assert damage_payload(actual)==damage_payload(without),(skill,rid)
            combinations+=1
    assert combinations==544
    receipt={'version':'0.38.0','passed':True,'verified_at':time.time(),
        'tests_run':tests.testsRun,'current_tests_passed':tests.testsRun-len(tests.skipped),
        'new_tests':18,'historical_combat_tests_skipped':len(tests.skipped),
        'failures':len(tests.failures),'errors':len(tests.errors),'test_modules':names,
        'exact_public_output_cases':len(rows),'module_matrix_cases':len(module_rows),
        'eligible_module_cases':changed,'unaffected_module_cases':unchanged,
        'all_relic_module_damage_invariance_cases':combinations,
        'damage_timing_owner_stats_unchanged':True,'test_log':'.cache/summon-038/tests.log',
        'test_log_sha256':digest('.cache/summon-038/tests.log'),
        'data_rule_counts':mechanics()['counts'],'offline_scope':scope_counts(mechanics()),
        'baseline_hashes':{'.cache/summon-038/'+n+'.json':digest('.cache/summon-038/'+n+'.json')
                           for n in ('before-public-results','before-module-results')},
        'source_hashes':{n:digest(n) for n in ('rouge/summons.py','rouge/operator_engine.py',
            'rouge/relics.py','rouge/reporting.py','rouge/operator_options.py',
            'rouge/data/summon-module-rules.json','tests/test_summon_modules_038.py',
            'scripts/verify_summon_modules_038.py','scripts/capture_summon_baseline_038.py')},
        'elapsed_seconds':time.perf_counter()-started,'chat_requests':0,'game_actions':0,'private_state_used':False,
        'limits':['Only Deepcolor SUM-Y token cost, stock and standalone HP references are implemented.',
            'The module HP modifier layer with other HP sources is unverified; the composite and dependent percentage regeneration stay unknown.',
            'Stock is not concurrent count. The offline model still supports at most the unlocked base count, up to4.',
            'Other summon modules, real animation timings and P1-P3 tasks remain incomplete.',
            'No new recognition throughput or complete inventory accuracy claim.']}
    (ROOT/'SUMMON_0.38_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('passed','current_tests_passed','new_tests',
        'exact_public_output_cases','module_matrix_cases','eligible_module_cases',
        'all_relic_module_damage_invariance_cases','elapsed_seconds')}),flush=True)

if __name__=='__main__':main()
