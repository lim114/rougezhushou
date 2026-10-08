"""Execute the exact frozen eight new methods once, without discovery ambiguity."""
import ast
import hashlib
import importlib.util
import json
import sys
import unittest
from pathlib import Path

OUT=Path(__file__).resolve().parent
AUTHOR=OUT.with_name('p2-remaining-boolean-consumers-086-draft')
path=AUTHOR/'draft/tests/test_remaining_boolean_condition_text_input.py'
assert hashlib.sha256(path.read_bytes()).hexdigest()=='3f65ea9bc16f62a9103f8ee83000e2b5aada668a0408910d70e1d54f5d0bb438'
methods=[n.name for n in ast.walk(ast.parse(path.read_text())) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')]
assert len(methods)==8
sys.path.insert(0,str(AUTHOR/'draft'))
spec=importlib.util.spec_from_file_location('independent_frozen_new086',path)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
suite=unittest.defaultTestLoader.loadTestsFromModule(module)
assert suite.countTestCases()==8
result=unittest.TextTestRunner(verbosity=2).run(suite)
receipt={'status':'PASS' if result.wasSuccessful() else 'FAIL','tests_run':result.testsRun,'failures':len(result.failures),
         'errors':len(result.errors),'skips':len(result.skipped),'frozen_file_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
         'eight_method_names':methods,'exact_final_tests_executed_once':True,'expectations_edited':False,
         'existing_114_tests_repeated':False,'internal_public_API_calls':'not instrumented; no measured total claim',
         'Qt':0,'Wine':0,'tracked_edits':0}
(OUT/'independent-new-tests086.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False))
raise SystemExit(0 if result.wasSuccessful() else 1)
