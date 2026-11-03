"""Run only the nine frozen new tests once and count actual public calls."""
from pathlib import Path
import importlib.util
import io
import json
import sys
import unittest

OUT=Path(__file__).resolve().parent
PACKAGE=OUT/'fixed-draft'
sys.path.insert(0,str(PACKAGE))
import rouge.damage as damage
actual=damage.calculate_damage
counter={'actual_public_calls':0,'successful_calls':0,'error_calls':0}
def counted(scenario):
    counter['actual_public_calls']+=1
    try:
        result=actual(scenario)
    except Exception:
        counter['error_calls']+=1
        raise
    counter['successful_calls']+=1
    return result
damage.calculate_damage=counted
spec=importlib.util.spec_from_file_location('fixed_independent_neural_condition_tests',PACKAGE/'tests/test_neural_condition_text_input.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
suite=unittest.defaultTestLoader.loadTestsFromModule(module)
stream=io.StringIO()
result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
text=stream.getvalue()
with (OUT/'new-tests083.log').open('x',encoding='utf-8') as f:f.write(text)
summary={'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
    'skipped':len(result.skipped),'successful':result.wasSuccessful(),**counter,
    'related_tests_repeated':False,'baseline_new_tests_repeated':False,'only_frozen_new_test_module':True}
with (OUT/'new-tests083.json').open('x',encoding='utf-8') as f:
    json.dump(summary,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps(summary))
assert result.testsRun==9 and result.wasSuccessful() and not result.skipped
