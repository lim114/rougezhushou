import hashlib
import json
import sys
import unittest
from pathlib import Path

OUT=Path(__file__).parent
sys.path.insert(0,str(OUT/'draft'))
sys.path.insert(0,str(OUT/'draft/tests'))
modules=['test_haruka_bubble_talent_qualification','test_haruka_event_reference',
         'test_haruka_healing_targets','test_integer_option_input_types']
suite=unittest.TestLoader().loadTestsFromNames(modules)
result=unittest.TextTestRunner(verbosity=2).run(suite)
receipt={'passed':result.wasSuccessful(),'modules':modules,'run':result.testsRun,
         'passed_count':result.testsRun-len(result.skipped)-len(result.errors)-len(result.failures),
         'skipped':[{'id':t.id(),'reason':r} for t,r in result.skipped],
         'errors':[{'id':t.id(),'detail':r} for t,r in result.errors],
         'failures':[{'id':t.id(),'detail':r} for t,r in result.failures],
         'source':str(OUT/'draft'),'seed':0,'gui_executed':False,'wine_executed':False,
         'unchanged_old_files':719,'new8_not_repeated':True}
(OUT/'related-tests84.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
sys.exit(not result.wasSuccessful())
