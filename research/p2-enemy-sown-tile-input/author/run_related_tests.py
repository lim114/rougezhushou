from pathlib import Path
import hashlib
import json
import sys
import unittest

sys.dont_write_bytecode = True
p = Path(__file__).resolve().parent
sys.path[:0] = [str(p/'draft'), str(p/'draft/tests')]
names = ['test_enemy_sown_tile_text_input', 'test_shu_periodic_sp_reference',
         'test_four_sui_text_input', 'test_target_count_input_types',
         'test_next_attack_healing_reference', 'test_healing_subtotal_scaling']
suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(name) for name in names)
result = unittest.TextTestRunner(verbosity=2).run(suite)
receipt = {'final_baseline_head': 'f4ca1c97278c5354f32940f56db2de60bbd21423', 'package': str(p/'draft'),
           'run': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
           'skips': len(result.skipped), 'passed': result.wasSuccessful(),
           'test_source_hashes': {name: hashlib.sha256((p/'draft/tests'/(name+'.py')).read_bytes()).hexdigest() for name in names},
           'private_fixtures_used': False, 'native_validation': False}
(p/'author-test-receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps(receipt))
sys.exit(not result.wasSuccessful())
