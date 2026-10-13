import importlib.util,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent
sys.path.insert(0,str(REPO))
import rouge
rouge.__path__.insert(0,str(ROOT/'candidate/rouge'))
spec=importlib.util.spec_from_file_location('bridge_tests',ROOT/'test_page_ocr_seed_bridge.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromModule(module),*[unittest.defaultTestLoader.loadTestsFromName(name) for name in ('tests.test_page_ocr_056','tests.test_page_ocr_058','tests.test_hybrid_safety_058')]])
result=unittest.TextTestRunner(verbosity=2).run(suite)
(ROOT/'candidate-unit.json').write_text(json.dumps({'tests':result.testsRun,'failures':[(str(t),trace) for t,trace in result.failures],'errors':[(str(t),trace) for t,trace in result.errors],'skips':[(str(t),reason) for t,reason in result.skipped],'protocol_doubles_not_real_OCR':True,'successful':result.wasSuccessful()},indent=2))
sys.exit(not result.wasSuccessful())
