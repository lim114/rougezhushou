"""Construct actual Qt runner externally; execution belongs to root."""
import ast,difflib,hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
BASE=Path('/workspace/.compat/wine-ui-smoke-065.py')
EXPECTED='4f18f54047920ac6d7dd32675e070167fe3c172528861423bc9e08f7210ecdcc'
raw=BASE.read_bytes();assert hashlib.sha256(raw).hexdigest()==EXPECTED
(P/'wine-ui-smoke-065-preserved.py').write_bytes(raw)
base=raw.decode();helpers=(P/'public_contracts.py').read_text();fragment=(P/'supplemental-checks.py.fragment').read_text()
marker='        # Final visible screenshot scenario demonstrates the restored explanation.\n'
assert base.count(marker)==1
text=base.replace(marker,fragment+'\n'+marker)
assert text.count('def source_hashes():')==1
text=text.replace('def source_hashes():',helpers+'\n\ndef source_hashes():',1)
changes={
"receipt['preserved_old_checks']=len(checks)-(supplemental_end-supplemental_start)-(new_end-new_start)":
"receipt['preserved_old_checks']=len(checks)-(supplemental_end-supplemental_start)-(new_end-new_start)-(latest_end-latest_start)",
"receipt['preserved_full_060_checks']=len(checks)-(new_end-new_start)":
"receipt['preserved_full_060_checks']=len(checks)-(new_end-new_start)-(latest_end-latest_start)",
"        receipt['total_actual_checks']=len(checks)":
"        receipt['preserved_full_065_checks']=len(checks)-(latest_end-latest_start)\n        assert receipt['preserved_full_065_checks']==459,receipt['preserved_full_065_checks']\n        receipt['total_actual_checks']=len(checks)"}
for old,new in changes.items():
    assert text.count(old)==1,old
    text=text.replace(old,new)
for old,new in (('wine-ui-report-difference-065.json','wine-ui-report-difference-070.json'),
                ('wine-window-065.png','wine-window-070.png'),('wine-ui-065.json','wine-ui-070.json'),
                ('wine-ui-failure-065.png','wine-ui-failure-070.png')):text=text.replace(old,new)
def scopes(tree):
    return [v.value for n in ast.walk(tree)if isinstance(n,ast.Dict)
            for k,v in zip(n.keys,n.values)if isinstance(k,ast.Constant)and k.value=='scope'and isinstance(v,ast.Constant)]
old_scopes=scopes(ast.parse(base));new_scopes=scopes(ast.parse(text))
assert all(new_scopes.count(s)>=old_scopes.count(s)for s in old_scopes)
target=P/'wine-ui-smoke-070.py';target.write_text(text)
diff=''.join(difflib.unified_diff(base.splitlines(keepends=True),text.splitlines(keepends=True),fromfile='wine-ui-smoke-065.py',tofile='wine-ui-smoke-070.py'))
(P/'runner-070.patch').write_text(diff)
receipt={'scope':'Static construction only; no actual Qt/Wine execution',
         'base065_sha256':EXPECTED,'base_actual_checks':459,'base_skills':87,
         'all_old_scope_labels_preserved':True,'prior_scope_labels':old_scopes,
         'preserved_055_expected':152,'preserved_060_expected':231,'preserved_065_expected':459,
         'new_case_design_by_section':{'66':120,'67':74,'68':72,'69':36,'70':80},
         'new_case_design_count':382,'total_case_design_count':841,
         'expected_numeric_error_cases':12,'actual_counts_require_root_execution':True,
         'section70_final_checks_pending':False,'syntax_valid':True,
         'runner_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
         'diff_sha256':hashlib.sha256((P/'runner-070.patch').read_bytes()).hexdigest(),
         'gui_executed':False,'wine_executed':False}
(P/'runner-static-review.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in receipt.items()if k!='prior_scope_labels'},ensure_ascii=False))
