"""Root real106 environment consumers plus existing public numeric/cache assertions; original classifier."""
import json
from pathlib import Path
import sys
import unittest

root=Path('/workspace/rougezhushou');base=Path('/workspace/.continuation')
sys.path.insert(0,str(root));sys.path.insert(0,str(root/'scripts'));sys.path.insert(0,str(base/'section106-window-source-v1'))
from verify_full_available import AvailableResult
from native_evidence import source_map,sha256
guard=json.loads((base/'resume106-applied-source-v1.json').read_bytes());before=source_map(root)
assert before==guard['source_sha256'] and len(before)==749
for name,want in guard['source_additional_sha256'].items():assert sha256((root/name).read_bytes())==want
selectors=['tests.test_environment_input_106', 'tests.test_run_config_validation', 'tests.test_run_modifiers', 'tests.test_enemy_environment', 'tests.test_enemy_rune_selectors', 'tests.test_aglna_manual_weight', 'tests.test_relics', 'tests.test_resource_observation_104', 'tests.test_cache_recovery_103', 'tests.test_inventory_confirmation_102', 'tests.test_cache_consumers_101', 'tests.test_training_view_100', 'tests.test_run_persistence_099', 'tests.test_run_state_reliability', 'tests.test_account_cache_093', 'tests.test_relic_resolution_052', 'tests.test_recipient_lifecycle_063', 'tests.test_counter_semantics_054', 'tests.test_counter_lifecycle_064', 'tests.test_run_config.RunConfigTests.test_settings_survive_missing_pages_restart_and_only_manual_reset_clears_them']
with (base/'resume106-related-v1.log').open('x') as stream:
    result=unittest.TextTestRunner(stream=stream,verbosity=1,resultclass=AvailableResult).run(unittest.defaultTestLoader.loadTestsFromNames(selectors))
after=source_map(root);assert before==after
for name,want in guard['source_additional_sha256'].items():assert sha256((root/name).read_bytes())==want
receipt={'available_checks_passed':result.wasSuccessful(),'tests_run':result.testsRun,'tests_passed':result.passed_count,
         'unavailable':result.unavailable,'unavailable_parent_count':len(result.unavailable_parents),'skipped':len(result.skipped),
         'failures':len(result.failures),'errors':len(result.errors),'selectors':selectors,'source_sha256':before,'source_drift':[],
         'source_additional_sha256':guard['source_additional_sha256'],'assertions_and_classifier_unchanged':True,'native_windows_game_chat_verified':False}
with (base/'resume106-related-v1.json').open('x') as stream:json.dump(receipt,stream,ensure_ascii=False,indent=2);stream.write('\n')
print(json.dumps({key:receipt[key] for key in ('available_checks_passed','tests_run','tests_passed','unavailable_parent_count','skipped','failures','errors')}))
sys.exit(0 if result.wasSuccessful() else 1)
