from pathlib import Path
import hashlib
import json
import subprocess
import sys
import unittest

sys.dont_write_bytecode = True
out = Path(__file__).resolve().parent
head = sys.argv[2]
package = Path(sys.argv[1]).resolve()
tests = out / ('tests-'+head[:12])
tests.mkdir(exist_ok=True)
names = ['test_bait_unknown_048', 'test_damage_subtotal_sources', 'test_s1_neural_boundary',
         'test_neural_incoming_clock', 'test_wine_timing', 'test_neural_sources_035',
         'test_neural_relic_034']
hashes = {}
for name in names:
    blob = subprocess.check_output(['git','-C','/workspace/rougezhushou','show',
                                    head+':tests/'+name+'.py'])
    (tests/(name+'.py')).write_bytes(blob)
    hashes[name] = hashlib.sha256(blob).hexdigest()
sys.path[:0] = [str(package), str(tests)]
suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(name) for name in names)
result = unittest.TextTestRunner(verbosity=2).run(suite)
receipt = {'package': str(package), 'baseline_test_head': head, 'test_source_hashes': hashes,
           'run': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
           'skips': len(result.skipped), 'passed': result.wasSuccessful(),
           'native_validation': False, 'private_fixtures_used': False}
(out/'related-test-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False))
sys.exit(not result.wasSuccessful())
