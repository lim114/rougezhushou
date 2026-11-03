from pathlib import Path
import sys,json,unittest,importlib.util
sys.dont_write_bytecode=True
OUT=Path(__file__).parent;DRAFT=OUT/'draft74-independent'
sys.path.insert(0,str(DRAFT));sys.path.insert(0,str(OUT))
freeze=json.loads((OUT/'draft74-independent-freeze.json').read_text())
files=[OUT/'test_wisdel_source74_independent.py',DRAFT/'tests/test_wisdel_summon_qualification_reference.py']+[DRAFT/p for p in freeze['related_oldtests']]
suites=[];counts={}
for i,p in enumerate(files):
 spec=importlib.util.spec_from_file_location('independent74_test_'+str(i),p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 suite=unittest.defaultTestLoader.loadTestsFromModule(m);suites.append(suite);counts[p.name]=suite.countTestCases()
with (OUT/'final74-tests.log').open('w') as log:r=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.TestSuite(suites))
receipt={'methods_by_file':counts,'methods_total':r.testsRun,'failures':len(r.failures),'errors':len(r.errors),'skips':len(r.skipped),'pass':r.wasSuccessful(),'interpreter':sys.executable,'private_native_wine_or_gui_tests':False}
(OUT/'final74-tests-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False));sys.exit(0 if r.wasSuccessful() else 1)
