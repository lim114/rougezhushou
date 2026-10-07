import importlib.util
import json
from pathlib import Path
import sys
import unittest

HERE=Path(__file__).resolve().parent
PACKAGE=HERE/'current60-compat/merged'
sys.dont_write_bytecode=True;sys.path.insert(0,str(PACKAGE))
names=['test_shu_periodic_sp_reference','test_damage_subtotal_sources',
       'test_emergency_recruitment_condition','test_integer_option_input_types','test_target_count_input_types']
suite=unittest.TestSuite()
for name in names:
    spec=importlib.util.spec_from_file_location('current60_'+name,PACKAGE/'tests'/f'{name}.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    suite.addTests(unittest.defaultTestLoader.loadTestsFromModule(module))
result=unittest.TextTestRunner(verbosity=2).run(suite)
receipt={'fixed_source_head':'c3ccf25d59144227dd0f8f5ca9ef6c8bf81ad8cf','package':str(PACKAGE),'modules':names,
    'methods_run':result.testsRun,'passed':result.wasSuccessful(),'failures':len(result.failures),
    'errors':len(result.errors),'skips':len(result.skipped),'root_tracked_edits':0,'Wine_run':False,'actual_GUI_run':False}
(HERE/'current60-tests.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False))
if not result.wasSuccessful():sys.exit(1)
