"""Read-only current canonical receipt contract; no tests or windows are run."""
from pathlib import Path
from hashlib import sha256
import ast,importlib.util,json,sys
R=next(p for p in Path(__file__).resolve().parents if(p/'rouge/app.py').is_file());D=Path(__file__).resolve().parent;B=R/'.cache/full425-prepared/attempt-4';sys.path[:0]=[str(B),str(R),str(R/'scripts')]
from full425_common import bound,sha
launch=json.loads((R/'.cache/425-selected-repair4-launch-input.json').read_bytes());data,_=bound(launch['parent'],launch['freeze_sha256'],launch['activation_sha256'])
current=D/'current-strict-validator.py';old=D/'original-strict-validator.py';assert current.read_bytes()==(R/'.cache/full425-post-attempt4/seal_summary425.py').read_bytes()
def functions(path):return {node.name:ast.dump(node,include_attributes=False)for node in ast.parse(path.read_text('utf8')).body if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef))}
before,after=functions(old),functions(current);assert before.keys()==after.keys()and {key for key in before if before[key]!=after[key]}=={'verify_functional'}
spec=importlib.util.spec_from_file_location('actual_public_current425_functional_validator',current);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.BASE=B;m.REVIEW_SHA=sha(B/'review_results425.py')
_,_,_,source_stable=m.load_readonly_helpers();actual=m.verify_functional(data,source_stable)
assert actual['necessary_tests_run']==88 and actual['native_unique_checks']==25
bound(launch['parent'],launch['freeze_sha256'],launch['activation_sha256']);assert current.read_bytes()==(R/'.cache/full425-post-attempt4/seal_summary425.py').read_bytes()
out=D/'canonical-contract.json';assert not out.exists();out.write_text(json.dumps({'section':425,'passed':True,'kind':'current_canonical_functional_receipt_contract_actual_readonly_check','only_changed_validator_function':'verify_functional','current_public_validator_sha256':sha(current),'original_validator_sha256':sha(old),'actual_public_reader_sha256':sha(Path(__file__)),'canonical_unit_module':data['selectors'][-1],'canonical_native_script':data['p3_scripts']['p3_425'],'actual_functional_scope':actual,'product_and_frozen4_sources_unchanged':True,'tests_or_windows_reexecuted':False,'original_failed_audit_not_relabelled':True},ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'canonical_contract_checked':True,'necessary_actual_tests':88,'native_actual_unique_checks':25,'new_tests_or_windows_run':False}))
