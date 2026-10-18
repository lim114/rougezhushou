from pathlib import Path
from hashlib import sha256
import sys,json
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'scripts/verify_full_available.py';s=p.read_text('utf8')
old="'tests.test_relic_exchange_flow_view_305')"
assert s.count(old)==1
replacement="'tests.test_relic_exchange_flow_view_305', 'tests.test_enemy_form_reference_306', 'tests.test_enemy_form_view_306')"
p.write_text(s.replace(old,replacement),encoding='utf8')
sys.path.insert(0,str(ROOT/'scripts'))
from verify_full_available import maintained_selectors
before=json.loads((ROOT/'verification/full-305/source-freeze-attempt2.json').read_bytes())['selectors'];after=maintained_selectors()
assert after[:len(before)]==before and after[len(before):]==['tests.test_enemy_form_reference_306','tests.test_enemy_form_view_306']
record={'section':306,'kind':'actual_selector_registration_check_not_full_test_run','maintained_previous_selectors':len(before),'current_selectors':len(after),'original_ordered_prefix_unchanged':True,'new_selectors':after[len(before):],'script_sha256':sha256(p.read_bytes()).hexdigest(),'full_suite_rerun':False,'earlier_shell_invocations':{'source_edit_actual_tool_exit':1,'reason':'PowerShell rejected quoting before Python executed; no mutation','following_readonly_assertion_exit':1,'reason_following_assertion':'Registration had not occurred; did not write a pass record'}}
out=ROOT/'verification/sections/306-preparation'
(out/'selector-registration.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8');(out/'execution-register-selectors.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps(record,ensure_ascii=False))
