"""Run old relevant checks; new9 passed separately and are not rerun here."""
import functools
import json
from pathlib import Path
import sys
import unittest

OUT=Path(__file__).parent
sys.path.insert(0,str(OUT/'draft'))
sys.path.insert(1,str(OUT/'draft/tests'))
from rouge import damage
calls=0
original=damage.calculate_damage
@functools.wraps(original)
def counted(*args,**kwargs):
    global calls
    calls+=1
    return original(*args,**kwargs)
damage.calculate_damage=counted
modules=('test_orchid_arrow_reference','test_orchid_redeploy_reference',
         'test_training_input_types','test_module_qualification_notes','test_integer_option_input_types')
suite=unittest.TestLoader().loadTestsFromNames(modules)
result=unittest.TextTestRunner(verbosity=2).run(suite)
receipt={'passed':result.wasSuccessful() and not result.skipped,'old_related_modules':list(modules),
    'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),
    'actual_old_related_calculate_damage_calls':calls,'new_tests_reused_without_rerun':9,
    'new_tests_log':'new-tests085.log','new_tests_call_count_not_instrumented':True,
    'matrix_calls_separately_counted':394,'GUI_executed':False,'Wine_executed':False}
(OUT/'related-tests-receipt085.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False))
raise SystemExit(0 if receipt['passed'] else 1)
