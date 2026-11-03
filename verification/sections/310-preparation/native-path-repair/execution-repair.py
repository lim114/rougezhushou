from pathlib import Path
from hashlib import sha256
import ast,json
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'verification/sections/310-preparation/native-path-repair';out.mkdir()
before=(ROOT/'.cache/p3-310-view/candidate/scripts/verify_boss_cycle_window_310.py').read_bytes();after=(ROOT/'scripts/verify_boss_cycle_window_310.py').read_bytes()
(out/'original-script.py').write_bytes(before)
one,two=ast.parse(before),ast.parse(after)
for tree in(one,two):
    for node in tree.body:
        if isinstance(node,ast.Assign)and len(node.targets)==1 and isinstance(node.targets[0],ast.Name)and node.targets[0].id in('MANIFEST','PACK','DATA'):node.value=ast.Constant(value='path identity separately verified')
assert ast.dump(one,include_attributes=False)==ast.dump(two,include_attributes=False)
values={node.targets[0].id:ast.literal_eval(node.value)for node in ast.parse(after).body if isinstance(node,ast.Assign)and len(node.targets)==1 and isinstance(node.targets[0],ast.Name)and node.targets[0].id in('MANIFEST','PACK','DATA')}
from sys import path
path.insert(0,str(ROOT))
from rouge import boss_cycle_reference as model
assert values=={key:getattr(model,key)for key in values}
failure=json.loads((ROOT/'verification/sections/310-native-attempt1/actual/window.json').read_bytes());assert failure['passed']is False and failure['qpa']is None and failure['unique_checks']==0
r={'section':310,'kind':'native_harness_three_path_constant_repair','original_native_failure_receipt':'verification/sections/310-native-attempt1/actual/window.json','actual_first_native_exit':1,'actual_window_was_not_constructed':True,'only_changed_top_level_constants':values,'all_other_AST_unchanged':True,'original_script_sha256':sha256(before).hexdigest(),'current_script_sha256':sha256(after).hexdigest(),'matches_actual_model_constants':True,'application_model_data_views_tests_or_private_state_changed':False,'no_guard_relaxed':True,'verification_repeat_reason':'Canonical native script is part of bound source scope; repeat necessary and native checks against the corrected complete current package, preserve both actual first receipts.'}
(out/'repair.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8');(out/'execution-repair.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps(r,ensure_ascii=False))
