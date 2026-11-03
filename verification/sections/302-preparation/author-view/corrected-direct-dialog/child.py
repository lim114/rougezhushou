from pathlib import Path
import importlib.util,json,sys,unittest
root,original,receipt=map(Path,sys.argv[1:4])
sys.path.insert(0,str(root))
import rouge
rouge.__path__.append(str(original/'rouge'))
from rouge import ritual_weakening as model
from rouge import ritual_weakening_view as view
assert model.ROOT==root,(model.ROOT,root)
assert Path(model.__file__).resolve()==root/'rouge/ritual_weakening.py'
assert Path(view.__file__).resolve()==root/'rouge/ritual_weakening_view.py'
spec=importlib.util.spec_from_file_location('isolated_ritual_weakening_view_302',root/'tests/test_ritual_weakening_view_302.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
suite=unittest.defaultTestLoader.loadTestsFromModule(module)
result=unittest.TextTestRunner(verbosity=2).run(suite)
not_loaded={name:name not in sys.modules for name in ('rouge.app','rouge.capture','rouge.capture_windows','rouge.desktop_chat')}
assert all(not_loaded.values()),not_loaded
receipt.write_text(json.dumps({'kind':'cache-direct-dialog-offscreen-checks-not-product-or-native-acceptance',
 'model_import':str(Path(model.__file__).resolve()),'view_import':str(Path(view.__file__).resolve()),
 'public_source_ROOT':str(model.ROOT),'QPA_platform':__import__('os').environ.get('QT_QPA_PLATFORM'),
 'actual_tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),
 'skipped':len(result.skipped),'successful':result.wasSuccessful(),
 'excluded_modules_not_loaded':not_loaded},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
sys.exit(0 if result.wasSuccessful() else 1)
