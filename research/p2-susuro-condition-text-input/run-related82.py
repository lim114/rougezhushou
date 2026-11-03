import hashlib
import json
import sys
import unittest
from pathlib import Path

OUT=Path(__file__).parent
sys.path.insert(0,str(OUT/'draft'))
sys.path.insert(0,str(OUT/'draft/tests'))
modules=['test_susuro_recipient_factor','test_friendly_scope_report',
         'test_target_count_input_types','test_declared_count_input_types',
         'test_training_input_types','test_module_qualification_notes']
suite=unittest.TestLoader().loadTestsFromNames(modules)
result=unittest.TextTestRunner(verbosity=2).run(suite)
receipt={'passed':result.wasSuccessful(),'modules':modules,'run':result.testsRun,
         'passed_count':result.testsRun-len(result.skipped)-len(result.errors)-len(result.failures),
         'skipped':[{'id':t.id(),'reason':r} for t,r in result.skipped],
         'errors':[{'id':t.id(),'detail':r} for t,r in result.errors],
         'failures':[{'id':t.id(),'detail':r} for t,r in result.failures],
         'source':str(OUT/'draft'),'seed':0,'gui_executed':False,'wine_executed':False,
         'unchanged_old_files':717,'new8_not_repeated':True}
(OUT/'related-tests82.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
sys.exit(not result.wasSuccessful())
