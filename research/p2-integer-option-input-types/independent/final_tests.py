"""Independently load new guard tests and the two adjacent public contracts."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
DRAFT=Path('/workspace/.continuation/p2-integer-option-audit-061/draft')
sys.dont_write_bytecode=True
sys.path.insert(0,str(DRAFT))
names=['test_integer_option_input_types','test_target_count_input_types','test_declared_count_input_types']
suite=unittest.TestSuite()
for name in names:
    path=DRAFT/'tests'/f'{name}.py'
    spec=importlib.util.spec_from_file_location('independent_'+name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
result=unittest.TextTestRunner(verbosity=2).run(suite)
receipt={'modules':names,'tests_run':result.testsRun,'passed':result.wasSuccessful(),
         'failures':[{'test':str(t),'traceback':tb} for t,tb in result.failures],
         'errors':[{'test':str(t),'traceback':tb} for t,tb in result.errors],
         'skips':[{'test':str(t),'reason':reason} for t,reason in result.skipped]}
(HERE/'final-tests.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:receipt[k] for k in ('tests_run','passed','failures','errors','skips')}))
if not result.wasSuccessful():sys.exit(1)
