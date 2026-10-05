"""0.30 public-entry regression and numeric non-interference checks."""
import hashlib
import json
import sys
import time
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.offline_scope import partition,scope_counts
from rouge.relics import mechanics

NAMES=['tests.test_offline_scope_030','tests.test_damage','tests.test_timing','tests.test_relics',
    'tests.test_relic_extension','tests.test_relic_conditions_022','tests.test_relic_events_022',
    'tests.test_relic_candidates_025','tests.test_deployment_relics_027','tests.test_mantra_events_024',
    'tests.test_report','tests.test_run_modifiers','tests.test_wine_timing','tests.test_difficulty_rules',
    'tests.test_target_memory','tests.test_received_sp_026','tests.test_event_sp_028',
    'tests.test_enemy_environment.EnemyEnvironmentTests.test_relic_enemy_modifiers_follow_stage_and_difficulty_and_are_reported',
    'tests.test_enemy_environment.EnemyEnvironmentTests.test_portal_keeps_main_depth_and_missing_context_does_not_guess',
    'tests.test_enemy_environment.EnemyEnvironmentTests.test_boss_reduction_is_independent_from_relic_vulnerability_and_preserves_healing_and_timing',
    'tests.test_enemy_environment.EnemyEnvironmentTests.test_emergency_stage_and_region_use_pinned_enemy_instead_of_manual_defense']


def output(r):
    return {key:r.get(key) for key in ('total_damage','components','deployment_cost','relic_protection','relic_token_stats')} | {
        'base_stats':r['estimate']['base_stats'],'skill':r['estimate']['skill']}


def main():
    start=time.perf_counter()
    suite=unittest.defaultTestLoader.loadTestsFromNames(NAMES)
    tested=unittest.TextTestRunner(verbosity=0).run(suite)
    assert tested.wasSuccessful(),'Regression failure; no success receipt.'
    data=mechanics();reference_ids=[]
    for rid,entry in data['relics'].items():
        active,reference,pending,reference_pending=partition(entry,rid)
        if (reference or reference_pending) and not (active or pending):reference_ids.append(rid)
    cases=wine_cases=0
    for op,profile in catalog()['operators'].items():
        for skill in range(1,len(profile['skills'])+1):
            for mode in ('frames','continuous'):
                s={'operator':op,'skill':skill,'timing_mode':mode}
                base=calculate_damage(s)
                for rid in reference_ids:
                    result=calculate_damage({**s,'relic_ids':[rid]})
                    assert output(result)==output(base),(rid,op,skill,mode)
                    record=result['relic_resolution']['records'][0]
                    assert record['status']=='reference_only' and not record['missing_conditions'] and not record['pending'],(rid,op,skill)
                    assert not result['relic_resolution']['rules'] and not result['relic_resolution']['token_effects']
                    cases+=1
                wine=calculate_damage({**s,'relic_ids':['rogue_6_relic_legacy_97']})
                combined=calculate_damage({**s,'relic_ids':['rogue_6_relic_legacy_97','rogue_6_relic_fight_5',
                    'rogue_6_relic_hand_5','rogue_6_relic_legacy_118']})
                assert output(combined)==output(wine),(op,skill,mode,'wine')
                wine_cases+=1
        print(json.dumps({'operator':op,'numeric_cases':cases,'wine_cases':wine_cases}),flush=True)
    # Source raw data remains the pinned 0.29 file, despite new application scope.
    raw_hash=hashlib.sha256((ROOT/'rouge/data/relic-mechanics.json').read_bytes()).hexdigest()
    raw_before=hashlib.sha256((ROOT/'.cache/batch-030-before/rouge/data/relic-mechanics.json').read_bytes()).hexdigest()
    assert raw_hash==raw_before
    visual_hash=hashlib.sha256((ROOT/'rouge/relic_recognition.py').read_bytes()).hexdigest()
    assert visual_hash=='8edff23d07bd013063d6c0d2fe4993500f66a80026a5d44c83373b8d4e700eb6'
    receipt={'version':'0.30.0','verified_at':time.time(),'policy':'offline_stable_effects',
        'scope':scope_counts(data),'tests_run':tested.testsRun,
        'tests_passed':tested.testsRun-len(tested.skipped),'tests_failed':len(tested.failures)+len(tested.errors),
        'historical_combat_tests_skipped':len(tested.skipped),
        'skipped_tests':[{'test':test.id(),'reason':reason} for test,reason in tested.skipped],'test_modules':NAMES,
        'reference_items':len(reference_ids),'skills':87,'timing_modes':2,'numeric_non_interference_cases':cases,
        'wine_callback_non_interference_cases':wine_cases,'raw_mechanics_unchanged':True,
        'recognition_unchanged_from_029':True,'raw_sha256':raw_hash,'recognition_sha256':visual_hash,
        'elapsed_seconds':time.perf_counter()-start,'new_live_measurements':0,'chat_requests':0,'game_actions':0,
        'source_hashes':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
            ('rouge/offline_scope.py','rouge/app.py','rouge/relics.py','rouge/deployment.py','rouge/reporting.py',
             'scripts/verify_relic_mechanics.py','tests/test_offline_scope_030.py','tests/offline_scope_retirement.py')}}
    folder=ROOT/'.cache/offline-scope-030';folder.mkdir(parents=True,exist_ok=True)
    (ROOT/'SCOPE_0.30_VERIFICATION.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:receipt[k] for k in ('scope','tests_passed','historical_combat_tests_skipped',
        'numeric_non_interference_cases','wine_callback_non_interference_cases','elapsed_seconds')},ensure_ascii=False))


if __name__=='__main__':main()
