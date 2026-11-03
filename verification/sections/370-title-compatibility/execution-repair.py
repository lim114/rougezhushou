from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import ast,json
R=Path(__file__).resolve().parents[1];name='scripts/verify_historical_route_window_270.py';p=R/name;raw=p.read_bytes();s=raw.decode('utf8')
old='黑流树海助手 0.91 · 局外计算与节点测试（234）';new='黑流树海助手 · 局外计算与节点测试'
assert s.count(old)==1;s=s.replace(old,new);before=ast.parse(raw);after=ast.parse(s)
values=[n for n in ast.walk(before)if isinstance(n,ast.Constant)and n.value==old];assert len(values)==1;values[0].value=new
assert ast.dump(before)==ast.dump(after)
out=R/'verification/sections/370-title-compatibility';out.mkdir();(out/'before-verify_historical_route_window_270.py').write_bytes(raw)
p.write_text(s,encoding='utf8',newline='\n')
record={'section':370,'kind':'one_literal_historical_harness_maintenance_in_functional_section','discovery':'targeted source search before publication found one historical diagnostic script asserting the old removed main window title','source_file':name,'old_title':old,'new_title':new,'all_other_original_270_AST_identical':True,'all_historical_scenarios_and_assertions_retained':True,'historical_270_script_rerun':False,'historical_private_sample_or_original_binary_validation_claimed':False,'current_normal_window_title_requires_actual_section370_main_window_receipt':True,'before_sha256':sha256(raw).hexdigest(),'after_sha256':sha256(p.read_bytes()).hexdigest(),'product_model_or_parameters_changed':False,'private_sample_read_or_copied_by_this_repair':False}
(out/'source-scope.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8');(out/'execution-repair.py').write_bytes(Path(__file__).read_bytes());print('Single stale historical title literal aligned; complete original AST otherwise preserved; no historical scenario executed or credited.')
