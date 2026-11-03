from pathlib import Path
import hashlib
import json
import sys
import unittest

sys.dont_write_bytecode = True
p = Path(__file__).resolve().parent
sys.path[:0] = [str(p/'draft'), str(p/'draft/tests')]
names = ['test_bait_count_input_forms', 'test_bait_unknown_048', 'test_damage_subtotal_sources',
         'test_integer_option_input_types', 'test_target_count_input_types']
suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(name) for name in names)
result = unittest.TextTestRunner(verbosity=2).run(suite)
receipt = {'baseline_head': 'd0ec6b618721863830518418aa95dc846f83e7c5',
           'source_package': str(p/'draft'), 'run': result.testsRun,
           'failures': len(result.failures), 'errors': len(result.errors), 'skips': len(result.skipped),
           'passed': result.wasSuccessful(),
           'test_source_hashes': {name: hashlib.sha256((p/'draft/tests'/(name+'.py')).read_bytes()).hexdigest() for name in names},
           'private_fixtures_used': False, 'native_validation': False}
(p/'author-test-receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps(receipt))
sys.exit(not result.wasSuccessful())
