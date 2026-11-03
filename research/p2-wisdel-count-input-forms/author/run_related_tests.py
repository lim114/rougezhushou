from pathlib import Path
import hashlib
import json
import sys
import unittest

sys.dont_write_bytecode = True
p = Path(__file__).resolve().parent
sys.path[:0] = [str(p/'draft'), str(p/'draft/tests')]
names = ['test_wisdel_count_input_forms', 'test_wisdel_ghost_clock', 'test_wisdel_secondary_reference',
         'test_integer_option_input_types', 'test_target_count_input_types', 'test_ammo_refill_041']
suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(name) for name in names)
result = unittest.TextTestRunner(verbosity=2).run(suite)
receipt = {'final_baseline_head': '0e0d098e8bc8444cd74fb74f32754cc0ff78ecfb', 'package': str(p/'draft'),
           'run': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
           'skips': len(result.skipped), 'passed': result.wasSuccessful(),
           'test_source_hashes': {name: hashlib.sha256((p/'draft/tests'/(name+'.py')).read_bytes()).hexdigest() for name in names},
           'private_fixtures_used': False, 'native_validation': False}
(p/'author-test-receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps(receipt))
sys.exit(not result.wasSuccessful())
