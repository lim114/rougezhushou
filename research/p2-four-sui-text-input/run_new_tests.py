"""Run the same public new tests against a chosen external package."""
import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parent
package=Path(sys.argv[1]).resolve()
output=Path(sys.argv[2]).resolve()
sys.path.insert(0,str(package))
spec=importlib.util.spec_from_file_location('public_contract062',ROOT/'draft062/tests/test_four_sui_text_input.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(module))
r={'package':str(package),'tests_run':result.testsRun,'failures':len(result.failures),
   'errors':len(result.errors),'skipped':len(result.skipped),'passed':result.wasSuccessful()}
output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(r,ensure_ascii=False))
sys.exit(0 if result.wasSuccessful() else 1)
