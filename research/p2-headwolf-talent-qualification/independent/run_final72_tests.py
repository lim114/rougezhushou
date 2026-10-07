from pathlib import Path
import sys,json,unittest,hashlib
sys.dont_write_bytecode=True
OUT=Path(__file__).parent;DRAFT=OUT/'draft72-independent'
sys.path.insert(0,str(DRAFT));sys.path.insert(0,str(OUT))
mods=['test_headwolf72_independent','tests.test_headwolf_talent_qualification','tests.test_drone_traits','tests.test_drone_attack_clock','tests.test_drone_aura_reference','tests.test_drone_arrival_reference','tests.test_wisdel_secondary_reference','tests.test_wisdel_ghost_clock','tests.test_module_qualification_notes']
# tests is an existing namespace directory; load file paths to avoid an installed package with that name.
import importlib.util
suites=[];counts={}
for name in mods:
 path=(OUT/'test_headwolf72_independent.py') if name=='test_headwolf72_independent' else DRAFT/(name.replace('.','/')+'.py')
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 suite=unittest.defaultTestLoader.loadTestsFromModule(m);counts[name]=suite.countTestCases();suites.append(suite)
with (OUT/'final72-independent-and-related-tests.log').open('w') as log:
 r=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.TestSuite(suites))
receipt={'test_methods_by_module':counts,'methods_total':r.testsRun,'failures':len(r.failures),'errors':len(r.errors),'skips':len(r.skipped),'success':r.wasSuccessful(),'interpreter':sys.executable,'kind':'Independent review tests plus untouched author new8 and immutable related old tests; no native/Wine'}
(OUT/'final72-test-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False));sys.exit(0 if r.wasSuccessful() else 1)
