from pathlib import Path
import hashlib
import json
import subprocess
import sys
import unittest
sys.dont_write_bytecode=True

out=Path(__file__).resolve().parent
package=Path(sys.argv[1]).resolve()
head='f4ca1c97278c5354f32940f56db2de60bbd21423'
directory=out/'final-tests-from-frozen64'
directory.mkdir(exist_ok=True)
names=['test_empty_enemy_scope','test_four_sui_text_input','test_friendly_scope_report',
       'test_shu_periodic_sp_reference','test_training_input_types']
hashes={}
for name in names:
    b=subprocess.check_output(['git','-C','/workspace/rougezhushou','show',head+':tests/'+name+'.py'])
    (directory/(name+'.py')).write_bytes(b);hashes[name]=hashlib.sha256(b).hexdigest()
author=package/'tests/test_enemy_sown_tile_text_input.py'
assert hashlib.sha256(author.read_bytes()).hexdigest()=='2e3c630225fa9f276ca6e69e96e48955f5c9fd800a5b910c9f8e60cd330dac2c'
sys.path[:0]=[str(package),str(directory),str(package/'tests')]
suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(name)for name in names)
related=unittest.TextTestRunner(verbosity=2).run(suite)
new=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromName('test_enemy_sown_tile_text_input'))


def counts(r):
    return {'run':r.testsRun,'failures':len(r.failures),'errors':len(r.errors),
            'skips':len(r.skipped),'passed':r.wasSuccessful()}


receipt={'baseline_head':head,'package':str(package),'test_source_hashes':hashes,
         'related':counts(related),'author_new':counts(new),
         'author_new_test_sha256':hashlib.sha256(author.read_bytes()).hexdigest(),
         'private_fixtures_used':False,'native_validation':False,
         'passed':related.wasSuccessful()and new.wasSuccessful()}
(out/'final-related-test-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False))
sys.exit(not receipt['passed'])
