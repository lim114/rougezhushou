import hashlib,importlib.util,json,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P/'draft078'))
source=P/'draft078/rouge/operator_engine.py';before=hashlib.sha256(source.read_bytes()).hexdigest()
test=P/'test_mantra_talent_qualification.py'
spec=importlib.util.spec_from_file_location('independent_new_tests078',test)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(module))
after=hashlib.sha256(source.read_bytes()).hexdigest();assert before==after
receipt={'new_tests_run':result.testsRun,'new_tests_passed':result.testsRun-len(result.failures)-len(result.errors)-len(result.skipped),
 'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),
 'source_before_sha256':before,'source_after_sha256':after,'gui_executed':False,'wine_executed':False}
(P/'independent-new-tests078.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt));assert result.wasSuccessful() and result.testsRun==9 and not result.skipped
