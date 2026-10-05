"""Fixed-delay public regression against the actual 0.36 full outputs."""
import hashlib,json,sys,time,unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'scripts'))
from verify_offline_scope_030 import NAMES
from rouge.damage import calculate_damage
from rouge.relics import mechanics
from rouge.offline_scope import scope_counts


def digest(name):return hashlib.sha256((ROOT/name).read_bytes()).hexdigest()


def main():
    started=time.perf_counter();folder=ROOT/'.cache/impact-037'
    names=NAMES+['tests.test_offline_relics_031','tests.test_spawn_hp_033',
        'tests.test_relic_grade_sync_032','tests.test_run_reuse_guards_032',
        'tests.test_sampling_flow','tests.test_neural_relic_034','tests.test_neural_sources_035',
        'tests.test_phase_flow_036','tests.test_impact_delay_037']
    with (folder/'tests.log').open('w',encoding='utf-8') as log:
        tests=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromNames(names))
    assert tests.wasSuccessful(),str(folder/'tests.log')
    rows=json.loads((folder/'before-public-results.json').read_text(encoding='utf-8'))
    exact=changed=0
    for i,row in enumerate(rows,1):
        s=row['scenario'];after=calculate_damage(s);before=row['result']
        if after==before:exact+=1
        else:
            assert s['operator']=='mechanist' and s['skill']==3 and s['timing_mode']=='frames',s
            # Isolate the new documented delay; removing only its reference
            # reproduces the entire previous output, including formatted UI.
            with patch('rouge.timing.impact_delays',return_value={}):
                assert calculate_damage(s)==before,s
            a=after['timing']['streams'][0];b=before['timing']['streams'][0]
            assert a['fixed_impact_delay_frames']==24 and not a['exact_binding']
            assert a['release_frames']==b['release_frames']
            assert a['emitted_release_frames']==b['emitted_release_frames']
            assert a['impact_frames']==[x+24 for x in b['impact_frames']]
            assert after['estimate']['base_stats']==before['estimate']['base_stats']
            assert after['estimate']['skill']==before['estimate']['skill']
            assert after['total_damage']==before['total_damage']
            changed+=1
        if i%100==0:print(json.dumps({'full_public_cases_checked':i}),flush=True)
    assert len(rows)==732 and changed==4 and exact==728
    previous=json.loads((ROOT/'FINAL_0.36_VERIFICATION.json').read_text(encoding='utf-8'))
    preserved=('rouge/damage.py','rouge/relics.py','rouge/operator_engine.py','rouge/estimate.py',
        'rouge/run_modifiers.py','rouge/data/relic-mechanics.json',
        'rouge/relic_recognition.py','rouge/run_state.py','rouge/recognition.py','rouge/visual_recognition.py')
    hashes={n:digest(n) for n in preserved}
    for n,checksum in hashes.items():assert checksum==previous['source_sha256'][n],n
    receipt={'version':'0.37.0','passed':True,'verified_at':time.time(),
        'tests_run':tests.testsRun,'current_tests_passed':tests.testsRun-len(tests.skipped),
        'new_tests':14,'historical_combat_tests_skipped':len(tests.skipped),
        'failures':len(tests.failures),'errors':len(tests.errors),'test_modules':names,
        'full_public_output_cases':len(rows),'exact_unchanged_cases':exact,
        'documented_delay_cases':changed,'previous_output_reproduced_without_new_delay':True,
        'baseline_sha256':digest('.cache/impact-037/before-public-results.json'),
        'test_log':'.cache/impact-037/tests.log','test_log_sha256':digest('.cache/impact-037/tests.log'),
        'data_rule_counts':mechanics()['counts'],'offline_scope':scope_counts(mechanics()),
        'source_hashes':{n:digest(n) for n in ('rouge/timing.py','rouge/reporting.py',
            'rouge/data/skill-impact-delays.json','tests/test_timing.py','tests/test_relics.py','tests/test_impact_delay_037.py',
            'scripts/verify_impact_delay_037.py','scripts/capture_impact_baseline_037.py')},
        'preserved_source_hashes':hashes,'elapsed_seconds':time.perf_counter()-started,
        'chat_requests':0,'game_actions':0,'private_state_used':False,
        'limits':['Only the main S3 cross projectile has a documented 0.8-second delay.',
            'First-three animation bindings remain unverified; movement through the cross area is not simulated.',
            'Summon charge timing, conditional modules, stacking and unknown relic scripts remain unresolved.',
            'No new recognition throughput or complete inventory accuracy claim.']}
    (ROOT/'IMPACT_0.37_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('passed','current_tests_passed','new_tests',
        'full_public_output_cases','exact_unchanged_cases','documented_delay_cases','elapsed_seconds')}),flush=True)


if __name__=='__main__':main()
