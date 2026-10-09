"""Actual existing AvailableResult for related101; missing evidence stays U."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest

root=Path('/workspace/rougezhushou');base=Path('/workspace/.continuation')
sys.path.insert(0,str(root));sys.path.insert(0,str(root/'scripts'))
from verify_full_available import AvailableResult
from native_evidence import source_map

guard=json.loads((base/'resume101-applied-source-v1.json').read_bytes())
before=source_map(root);assert before==guard['source_sha256']
selectors=['tests.test_cache_consumers_101','tests.test_run_state_reliability',
           'tests.test_run_persistence_099','tests.test_training_view_100',
           'tests.test_counter_semantics_054','tests.test_counter_lifecycle_064',
           'tests.test_recipient_binding_050','tests.test_run_reuse_guards_032']
with (base/'resume101-related-available-v3.log').open('x') as log:
    result=unittest.TextTestRunner(stream=log,verbosity=1,resultclass=AvailableResult).run(
        unittest.defaultTestLoader.loadTestsFromNames(selectors))
after=source_map(root);assert after==before
receipt={'available_checks_passed':result.wasSuccessful(),'complete_repository_validation':False,
         'tests_run':result.testsRun,'tests_passed':result.passed_count,
         'unavailable':result.unavailable,'unavailable_parent_count':len(result.unavailable_parents),
         'skipped':len(result.skipped),'failures':len(result.failures),'errors':len(result.errors),
         'selectors':selectors,'source_sha256':before,'source_drift':[],
         'classifier':'Unmodified maintained AvailableResult; no test/product replacement',
         'native_windows_game_chat_verified':False}
with (base/'resume101-related-available-v3.json').open('x') as handle:
    json.dump(receipt,handle,ensure_ascii=False,indent=2);handle.write('\n')
print(json.dumps({k:receipt[k] for k in ['available_checks_passed','tests_run','tests_passed','unavailable_parent_count','skipped','failures','errors']}))
sys.exit(0 if result.wasSuccessful() else 1)
