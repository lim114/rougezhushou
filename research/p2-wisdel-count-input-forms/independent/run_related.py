from pathlib import Path
import hashlib
import json
import subprocess
import sys
import unittest
sys.dont_write_bytecode = True

out = Path(__file__).resolve().parent
head = '0e0d098e8bc8444cd74fb74f32754cc0ff78ecfb'
package = Path(sys.argv[1]).resolve()
tests = out/'tests-from-baseline63'
tests.mkdir(exist_ok=True)
names = ['test_wisdel_ghost_clock','test_wisdel_secondary_reference',
         'test_integer_option_input_types','test_summon_composition_068',
         'test_summon_limits_069','test_summon_modules_038','test_timing']
hashes = {}
for name in names:
    blob = subprocess.check_output(['git','-C','/workspace/rougezhushou','show',
                                    head+':tests/'+name+'.py'])
    (tests/(name+'.py')).write_bytes(blob)
    hashes[name] = hashlib.sha256(blob).hexdigest()
new = package/'tests/test_wisdel_count_input_forms.py'
assert hashlib.sha256(new.read_bytes()).hexdigest() == '37235f0ba701ac462d8b6f8ab0028e0d82fad9725dac126aa195dc2466a73cc9'
sys.path[:0] = [str(package),str(tests),str(package/'tests')]
suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(name) for name in names)
result = unittest.TextTestRunner(verbosity=2).run(suite)
author = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName('test_wisdel_count_input_forms'))


def counts(r):
    return {'run':r.testsRun,'failures':len(r.failures),'errors':len(r.errors),
            'skips':len(r.skipped),'passed':r.wasSuccessful()}


receipt = {'package':str(package),'baseline_test_head':head,'test_source_hashes':hashes,
           'related':counts(result),'author_new':counts(author),
           'author_new_source_sha256':hashlib.sha256(new.read_bytes()).hexdigest(),
           'native_validation':False,'private_fixtures_used':False,
           'passed':result.wasSuccessful() and author.wasSuccessful()}
(out/'related-test-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False))
sys.exit(not receipt['passed'])
