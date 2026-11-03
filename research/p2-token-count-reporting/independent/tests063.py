"""Execute new and adjacent public contracts without touching the frozen package."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest

PACKAGE=Path(sys.argv[1]).resolve(); OUT=Path(sys.argv[2]).resolve()
sys.dont_write_bytecode=True;sys.path.insert(0,str(PACKAGE))
names=['test_summon_count_reporting','test_integer_option_input_types',
       'test_summon_composition_068','test_summon_limits_069']
suite=unittest.TestSuite()
for name in names:
    spec=importlib.util.spec_from_file_location('independent063_'+name,PACKAGE/'tests'/f'{name}.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
result=unittest.TextTestRunner(verbosity=2).run(suite)
receipt={'package':str(PACKAGE),'modules':names,'methods_run':result.testsRun,'passed':result.wasSuccessful(),
    'failures':[{'test':str(t),'traceback':tb} for t,tb in result.failures],
    'errors':[{'test':str(t),'traceback':tb} for t,tb in result.errors],
    'skips':[{'test':str(t),'reason':reason} for t,reason in result.skipped],
    'Wine_executed':False,'GUI_executed':False}
OUT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'methods_run':result.testsRun,'passed':result.wasSuccessful()}))
if not result.wasSuccessful():sys.exit(1)
