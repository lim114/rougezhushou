"""Load only public external draft tests; no repository discovery or fixtures."""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parent
DRAFT=Path('/workspace/.continuation/p2-after-055-audit/relic-scope/draft')
sys.dont_write_bytecode=True
sys.path.insert(0,str(DRAFT))
sys.path.insert(1,str(DRAFT/'tests'))
names=['test_emergency_recruitment_condition','test_relics','test_relic_scope_052',
       'test_offline_relics_031','test_relic_resolution_052']
suite=unittest.TestSuite()
for name in names:
    path=DRAFT/'tests'/f'{name}.py'
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
result=unittest.TextTestRunner(verbosity=2).run(suite)
receipt={'test_modules':names,'tests_run':result.testsRun,'passed':result.testsRun-len(result.failures)-len(result.errors)-len(result.skipped),
         'failures':[{'test':str(t),'traceback':tb} for t,tb in result.failures],
         'errors':[{'test':str(t),'traceback':tb} for t,tb in result.errors],
         'skipped':[{'test':str(t),'reason':why} for t,why in result.skipped],
         'successful':result.wasSuccessful(),'private_state_read':False,'native_attachment_proven':False}
(HERE/'independent-tests.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k not in {'test_modules','skipped','failures','errors'}},ensure_ascii=False))
if not result.wasSuccessful():sys.exit(1)
