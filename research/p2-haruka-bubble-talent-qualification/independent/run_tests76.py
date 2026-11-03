import json
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
own = Path(__file__).parent
sys.path.insert(0, str(own / 'draft'))
modules = ['tests.test_haruka_bubble_talent_qualification', 'tests.test_haruka_event_reference',
           'tests.test_haruka_healing_targets', 'tests.test_healing_subtotal_scaling']
suite = unittest.defaultTestLoader.loadTestsFromNames(modules)
with (own / 'final-new-and-related-tests76.log').open('w') as stream:
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
receipt = {'status': 'PASS' if result.wasSuccessful() else 'FAIL', 'modules': modules,
           'methods_run': result.testsRun, 'failures': len(result.failures),
           'errors': len(result.errors), 'skipped': len(result.skipped),
           'source_tree': str(own / 'draft'), 'dont_write_bytecode': True}
(own / 'final-tests76.json').write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt))
sys.exit(0 if result.wasSuccessful() else 1)
