import importlib.util,json,platform,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent.parent
sys.path.insert(0,str(REPO))
import rouge
rouge.__path__.insert(0,str(ROOT/'candidate/rouge'))
spec=importlib.util.spec_from_file_location('test_initial_install',ROOT/'candidate/test_initial_install.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(module),unittest.defaultTestLoader.loadTestsFromName('tests.test_run_persistence_099'),unittest.defaultTestLoader.loadTestsFromName('tests.test_account_cache_093')])
result=unittest.TextTestRunner(verbosity=2).run(suite)
report={'platform':platform.platform(),'candidate_only':True,'native_Windows_verified':False,'tests':result.testsRun,'failures':[(str(t),trace) for t,trace in result.failures],'errors':[(str(t),trace) for t,trace in result.errors],'skips':[(str(t),reason) for t,reason in result.skipped],'successful':result.wasSuccessful()}
(ROOT/(sys.argv[1]+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
sys.exit(not result.wasSuccessful())
