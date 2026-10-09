"""Root real original assertions; unchanged maintained unavailable classifier."""
import argparse
import json
from pathlib import Path
import sys
import unittest

root=Path('/workspace/rougezhushou');base=Path('/workspace/.continuation')
sys.path.insert(0,str(root));sys.path.insert(0,str(root/'scripts'))
sys.path.insert(0,str(base/'section102-window-source-v2'))
from native_evidence import source_map,sha256
from verify_full_available import AvailableResult

parser=argparse.ArgumentParser();parser.add_argument('--phase',choices=('original-registry','candidate-registry','candidate-related'),required=True)
args=parser.parse_args();phase=args.phase
guard=json.loads((base/('resume101-applied-source-v1.json' if phase=='original-registry' else 'resume102-applied-source-v1.json')).read_bytes())
before=source_map(root);assert before==guard['source_sha256']
for name,want in guard['source_additional_sha256'].items():assert sha256((root/name).read_bytes())==want
if phase.endswith('registry'):
    selectors=json.loads((base/'section102-registry-increment-source-v1/increment-plan.json').read_bytes())['added_selectors']
else:
    selectors=['tests.test_inventory_confirmation_102','tests.test_cache_consumers_101','tests.test_training_view_100',
               'tests.test_run_persistence_099','tests.test_run_state_reliability','tests.test_run_reuse_guards_032',
               'tests.test_relic_grade_sync_032','tests.test_inventory_tools','tests.test_relic_recognition_022',
               'tests.test_run_config_validation','tests.test_counter_lifecycle_064']
suite=unittest.defaultTestLoader.loadTestsFromNames(selectors)
if phase.endswith('registry'):assert suite.countTestCases()==52,suite.countTestCases()
path=base/('resume102-'+phase+'-v2')
with path.with_suffix('.log').open('x') as stream:result=unittest.TextTestRunner(stream=stream,verbosity=1,resultclass=AvailableResult).run(suite)
after=source_map(root);assert before==after
for name,want in guard['source_additional_sha256'].items():assert sha256((root/name).read_bytes())==want
receipt={'available_checks_passed':result.wasSuccessful(),'tests_run':result.testsRun,'tests_passed':result.passed_count,
         'unavailable':result.unavailable,'unavailable_parent_count':len(result.unavailable_parents),'skipped':len(result.skipped),
         'failures':len(result.failures),'errors':len(result.errors),'selectors':selectors,'source_sha256':before,'source_drift':[],
         'source_additional_sha256':guard['source_additional_sha256'],'assertions_and_classifier_unchanged':True,
         'native_windows_game_chat_verified':False}
with path.with_suffix('.json').open('x') as stream:json.dump(receipt,stream,ensure_ascii=False,indent=2);stream.write('\n')
print(json.dumps({k:receipt[k] for k in ('available_checks_passed','tests_run','tests_passed','unavailable_parent_count','skipped','failures','errors')}))
sys.exit(0 if result.wasSuccessful() else 1)
