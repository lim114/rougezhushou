"""Run frozen new/source-clock tests and the combined61 public contracts."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
PACKAGE=Path(sys.argv[1]).resolve();OUT=Path(sys.argv[2]).resolve()
sys.dont_write_bytecode=True;sys.path.insert(0,str(PACKAGE))
names=['test_four_sui_text_input','test_shu_periodic_sp_reference']
if PACKAGE.name=='combined061062':
    names+=['test_integer_option_input_types','test_target_count_input_types',
            'test_emergency_recruitment_condition','test_damage_subtotal_sources']
suite=unittest.TestSuite()
for name in names:
    spec=importlib.util.spec_from_file_location('independent062_'+name,PACKAGE/'tests'/f'{name}.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
result=unittest.TextTestRunner(verbosity=2).run(suite)
receipt={'package':str(PACKAGE),'modules':names,'methods_run':result.testsRun,'passed':result.wasSuccessful(),
    'failures':[{'test':str(t),'traceback':tb} for t,tb in result.failures],
    'errors':[{'test':str(t),'traceback':tb} for t,tb in result.errors],
    'skips':[{'test':str(t),'reason':reason} for t,reason in result.skipped],
    'root_tracked_edits':0,'Wine_run':False,'actual_GUI_run':False}
OUT.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'methods_run':result.testsRun,'passed':result.wasSuccessful()},ensure_ascii=False))
if not result.wasSuccessful():sys.exit(1)
