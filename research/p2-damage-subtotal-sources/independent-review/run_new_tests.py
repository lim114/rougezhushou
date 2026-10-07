import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
DRAFT=Path('/workspace/.continuation/p2-derived-report-059/draft')
sys.dont_write_bytecode=True
sys.path.insert(0,str(DRAFT))
path=DRAFT/'tests/test_damage_subtotal_sources.py'
spec=importlib.util.spec_from_file_location('independent_subtotal_source_tests',path)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(module))
receipt={'tests_run':result.testsRun,'failures':[str(t) for t,_ in result.failures],
         'errors':[str(t) for t,_ in result.errors],'skips':[str(t) for t,_ in result.skipped],
         'passed':result.wasSuccessful()}
(HERE/'independent-tests.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt))
if not result.wasSuccessful():sys.exit(1)
