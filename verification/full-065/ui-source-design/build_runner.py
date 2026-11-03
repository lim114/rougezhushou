"""Build external actual Qt candidate; execution belongs exclusively to root."""
import ast
import hashlib
import json
import sys
from pathlib import Path

P=Path(__file__).resolve().parent
BASE=Path('/workspace/.compat/wine-ui-smoke-060.py')
EXPECTED='d10e4ba78041eee2e70c6793ddf211c06830c6b0bf7f588fa099e59eacbf10a1'
raw=BASE.read_bytes();assert hashlib.sha256(raw).hexdigest()==EXPECTED
(P/'wine-ui-smoke-060-preserved.py').write_bytes(raw)
base=raw.decode();fragment=(P/'supplemental-checks.py.fragment').read_text()
ready='--ready' in sys.argv
if ready:
    assert fragment.count("receipt['section65_final_checks_pending']=True")==1
    fragment=fragment.replace("receipt['section65_final_checks_pending']=True",
                              "receipt['section65_final_checks_pending']=False")
marker='        # Final visible screenshot scenario demonstrates the restored explanation.\n'
assert base.count(marker)==1
text=base.replace(marker,fragment+'\n'+marker)
old="receipt['preserved_old_checks']=len(checks)-(supplemental_end-supplemental_start)"
new="receipt['preserved_old_checks']=len(checks)-(supplemental_end-supplemental_start)-(new_end-new_start)"
assert text.count(old)==1;text=text.replace(old,new)
close='        window.close();app.processEvents();window=None\n'
assert text.count(close)==1
text=text.replace(close,"        receipt['preserved_full_060_checks']=len(checks)-(new_end-new_start)\n"
                        "        assert receipt['preserved_full_060_checks']==231,receipt['preserved_full_060_checks']\n"
                        "        receipt['total_actual_checks']=len(checks)\n"+close)
failure="    receipt['failure']={'type':type(error).__name__,'message':str(error),'traceback':traceback.format_exc()}\n"
assert text.count(failure)==1
text=text.replace(failure,failure+"    if window is not None:\n"
    "        try:\n"
    "            receipt['failure_actual_window']={'operator':window.operator.currentData(),\n"
    "                'skill':window.skill.currentData(),'visible_report_text':window.damage_text.toPlainText(),\n"
    "                'technical_checkbox':window.damage_technical.isChecked(),\n"
    "                'last_calculation':window.damage_result,'timing_text':window.timing_scenario.toPlainText()}\n"
    "            failure_screenshot=OUT/'wine-ui-failure-065.png'\n"
    "            if window.grab().save(str(failure_screenshot)):\n"
    "                receipt['failure_screenshot']=failure_screenshot.name\n"
    "        except Exception as context_error:\n"
    "            receipt['failure_context_capture_error']={'type':type(context_error).__name__,'message':str(context_error)}\n")
for before,after in (('wine-ui-report-difference-060.json','wine-ui-report-difference-065.json'),
                     ('wine-window-060.png','wine-window-065.png'),
                     ('wine-ui-060.json','wine-ui-065.json')):
    text=text.replace(before,after)
tree=ast.parse(text)
target=P/'wine-ui-smoke-065.py';target.write_text(text)
old_scopes=[nvalue.value for node in ast.walk(ast.parse(base)) if isinstance(node,ast.Dict)
            for key,nvalue in zip(node.keys,node.values)
            if isinstance(key,ast.Constant) and key.value=='scope' and isinstance(nvalue,ast.Constant)]
new_scopes=[nvalue.value for node in ast.walk(tree) if isinstance(node,ast.Dict)
            for key,nvalue in zip(node.keys,node.values)
            if isinstance(key,ast.Constant) and key.value=='scope' and isinstance(nvalue,ast.Constant)]
assert all(new_scopes.count(scope)>=old_scopes.count(scope) for scope in old_scopes)
receipt={'scope':'Static runner construction only; not Wine or actual Qt execution',
         'base_path':str(BASE),'base_sha256':EXPECTED,'base_actual_checks_from_prior_receipt':231,
         'preserved_055_checks_expected':152,'preserved_56_60_checks_expected':79,
         'new_sections':[61,62,63,64,65],
         'new_loop_cases_by_section_designed':{'61':96,'62':8,'63':78,'64':28,'65':18},
         'new_loop_cases_designed':228,'total_loop_cases_designed':459,
         'actual_count_requires_root_execution_receipt':True,
         'all_prior_static_scope_labels_retained':True,'prior_static_scope_labels':old_scopes,
         'prior_revised_emergency_source_semantics_retained':True,
         'syntax_valid':True,'section65_source_review_pending':not ready,
         'runner_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
         'fragment_sha256':hashlib.sha256((P/'supplemental-checks.py.fragment').read_bytes()).hexdigest(),
         'failure_receipt_captures_actual_text_and_isolated_public_calculation':True,
         'gui_executed':False,'wine_executed':False}
(P/'runner-static-review.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items() if k!='prior_static_scope_labels'},ensure_ascii=False))
