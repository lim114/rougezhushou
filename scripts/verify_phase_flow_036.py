"""Exact full-public-output comparison against the untouched 0.35 baseline."""
import hashlib,json,sys,time,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from verify_offline_scope_030 import NAMES
from rouge.damage import calculate_damage
from rouge.relics import mechanics
from rouge.offline_scope import scope_counts


def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()


def main():
    started=time.perf_counter();folder=ROOT/'.cache/phase-036'
    names=NAMES+['tests.test_offline_relics_031','tests.test_spawn_hp_033',
        'tests.test_relic_grade_sync_032','tests.test_run_reuse_guards_032',
        'tests.test_sampling_flow','tests.test_neural_relic_034','tests.test_neural_sources_035',
        'tests.test_phase_flow_036']
    with (folder/'tests.log').open('w',encoding='utf-8') as log:
        tests=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(names))
    assert tests.wasSuccessful(),str(folder/'tests.log')
    rows=json.loads((folder/'before-public-results.json').read_text(encoding='utf-8'))
    for i,row in enumerate(rows,1):
        assert calculate_damage(row['scenario'])==row['result'],row['scenario']
        if i%100==0:print(json.dumps({'exact_full_output_cases':i}),flush=True)
    previous=json.loads((ROOT/'FINAL_0.35_VERIFICATION.json').read_text(encoding='utf-8'))
    unchanged=('rouge/relics.py','rouge/operator_engine.py','rouge/estimate.py','rouge/timing.py',
        'rouge/run_modifiers.py','rouge/data/relic-mechanics.json')
    hashes={name:digest(name) for name in unchanged}
    # Historic receipt contains the files it actually verified; use public
    # fixed source hashes when available, not an invented blanket assertion.
    assert hashes['rouge/data/relic-mechanics.json']==previous['source_sha256']['rouge/data/relic-mechanics.json']
    receipt={'version':'0.36.0','passed':True,'verified_at':time.time(),
        'tests_run':tests.testsRun,'current_tests_passed':tests.testsRun-len(tests.skipped),
        'new_tests':9,'historical_combat_tests_skipped':len(tests.skipped),
        'failures':len(tests.failures),'errors':len(tests.errors),'test_modules':names,
        'full_public_output_cases':len(rows),'exact_unchanged_cases':len(rows),
        'baseline_sha256':digest('.cache/phase-036/before-public-results.json'),
        'test_log':'.cache/phase-036/tests.log','test_log_sha256':digest('.cache/phase-036/tests.log'),
        'data_rule_counts':mechanics()['counts'],'offline_scope':scope_counts(mechanics()),
        'source_hashes':{name:digest(name) for name in ('rouge/damage.py','tests/test_phase_flow_036.py',
            'scripts/capture_phase_baseline_036.py','scripts/verify_phase_flow_036.py')},
        'existing_model_hashes':hashes,'elapsed_seconds':time.perf_counter()-started,
        'chat_requests':0,'game_actions':0,'private_state_used':False,
        'limits':['No new stacking, activation phase, tick lifetime or animation binding is asserted.',
                  'All existing unknowns remain; neither full relic recognition nor all P1-3 work is complete.']}
    (ROOT/'PHASE_0.36_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('passed','current_tests_passed','new_tests',
        'full_public_output_cases','exact_unchanged_cases','elapsed_seconds')}),flush=True)


if __name__=='__main__':main()
