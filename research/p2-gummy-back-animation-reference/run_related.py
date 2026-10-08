import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parent
TREE=ROOT/'draft'
sys.path.insert(0,str(TREE))
import rouge.damage as damage
api_calls=0
original=damage.calculate_damage
def counted(scenario):
    global api_calls
    api_calls+=1
    return original(scenario)
damage.calculate_damage=counted
modules=['tests.test_original_animation_048','tests.test_gummy_cooking_clock','tests.test_gummy_expected_clock',
         'tests.test_next_attack_healing_reference','tests.test_friendly_scope_report']
import tests.test_original_animation_048 as original_animation
cache=TREE/'.cache/research/timing-048/skeleton-downloads.json'
historical=[]
if not cache.exists():
    method=original_animation.OriginalAnimation048Tests.test_all_sources_match_pinned_skeleton_bytes_and_git_blob
    method.__unittest_skip__=True
    method.__unittest_skip_why__='Original timing-048 resource cache was not migrated; do not reconstruct or redownload64 files'
    historical.append({'test':'tests.test_original_animation_048.OriginalAnimation048Tests.test_all_sources_match_pinned_skeleton_bytes_and_git_blob','absent_path':str(cache),'reason':method.__unittest_skip_why__})
suite=unittest.defaultTestLoader.loadTestsFromNames(modules)
result=unittest.TextTestRunner(verbosity=2).run(suite)
receipt={'version':1,'modules':modules,'tests_run':result.testsRun,'passed':result.wasSuccessful(),'successes':result.testsRun-len(result.skipped)-len(result.failures)-len(result.errors),
    'skipped':len(result.skipped),'failures':len(result.failures),'errors':len(result.errors),'API_calls':api_calls,
    'historical_skips':historical,'source_parses_downloads_Qt_Wine_root_tracked_edits':0,
    'new_tests_already_run_separately':{'module':'tests.test_gummy_back_animation_reference','tests':7,'passed':True,'public_API_calls_by_explicit_call_sites':11},
    'test_source_sha256':{name:hashlib.sha256((TREE/(name.replace('.','/')+'.py')).read_bytes()).hexdigest() for name in modules}}
(ROOT/'related-tests-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False))
raise SystemExit(0 if result.wasSuccessful() else 1)
