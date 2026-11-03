import hashlib,json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent;REPO=ROOT.parent.parent
sys.path.insert(0,str(REPO))
paths=('rouge/recognition.py','rouge/page_ocr.py','rouge/dynamic_ocr.py','tests/test_page_ocr_seed_bridge.py')
def hashes():return {path:hashlib.sha256((REPO/path).read_bytes()).hexdigest() for path in paths}
before=hashes()
modules=('tests.test_page_ocr_seed_bridge','tests.test_page_ocr_056','tests.test_page_ocr_058','tests.test_hybrid_safety_058')
suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromName(name) for name in modules])
result=unittest.TextTestRunner(verbosity=2).run(suite)
after=hashes();assert after==before
(ROOT/'production-unit.json').write_text(json.dumps({'modules':modules,'tests':result.testsRun,'failures':[(str(t),trace) for t,trace in result.failures],'errors':[(str(t),trace) for t,trace in result.errors],'skips':[(str(t),reason) for t,reason in result.skipped],'protocol_doubles_not_real_OCR':True,'successful':result.wasSuccessful(),'source_hashes_before':before,'source_hashes_after':after,'source_unchanged':before==after},indent=2))
sys.exit(not result.wasSuccessful())
