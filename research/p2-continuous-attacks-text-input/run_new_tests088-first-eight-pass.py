from pathlib import Path
import importlib.util,json,sys,threading,unittest
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(OUT/'draft'))
path=OUT/'test_continuous_attacks_text_input.py'
spec=importlib.util.spec_from_file_location('section088_new_tests',path)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
from rouge.damage import calculate_damage
from rouge.sp_events import charge
from rouge import condition_inputs
counts={'public_function_entries':0,'explicit_test_public_requests':0,
        'explicit_test_context_helper_requests':0,'standalone_event_charge_function_entries':0,
        'private_leaf_function_entries':{},'all_project_function_entries_instrumented':False}
lock=threading.Lock()
leaf=str((OUT/'draft/rouge/condition_inputs.py').resolve())
test=str(path.resolve())
def profile(frame,event,arg):
    if event!='call':return
    code=frame.f_code;parent=frame.f_back
    direct=parent is not None and parent.f_code.co_filename==test
    with lock:
        if code is calculate_damage.__code__:
            counts['public_function_entries']+=1
            if direct:counts['explicit_test_public_requests']+=1
        elif code is charge.__code__:
            counts['standalone_event_charge_function_entries']+=1
            if direct:counts['explicit_test_context_helper_requests']+=1
        elif code.co_filename==leaf:
            d=counts['private_leaf_function_entries'];d[code.co_name]=d.get(code.co_name,0)+1
            if direct:counts['explicit_test_context_helper_requests']+=1
sys.setprofile(profile);threading.setprofile(profile)
suite=unittest.defaultTestLoader.loadTestsFromModule(module)
result=unittest.TextTestRunner(verbosity=2).run(suite)
threading.setprofile(None);sys.setprofile(None)
assert counts['public_function_entries']<=32 and counts['explicit_test_context_helper_requests']<=32,counts
receipt={'status':'PASS' if result.wasSuccessful() else 'FAIL','methods_run':result.testsRun,
         'failures':len(result.failures),'errors':len(result.errors),'skips':len(result.skipped),'counts':counts,
         'scope':'New eight methods once, no old tests; recorded named function entries only, no invented all-helper grand total.'}
(OUT/'new-tests088-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False))
sys.exit(0 if result.wasSuccessful() else 1)
