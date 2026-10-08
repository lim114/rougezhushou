"""Read already-saved failed case and frozen source; no API or formatter calls."""
from pathlib import Path
import ast
import gzip
import hashlib
import json

OUT=Path(__file__).resolve().parent
AUTHOR=OUT.parent
source=AUTHOR/'public-schema-final-085-failure.json.gz'
data=source.read_bytes()
def sha(data):return hashlib.sha256(data).hexdigest()
assert sha(data)=='513bb64717654c5c8b31cd69b437c66bf7b575377502520d7f74f39f8e142894'
target=OUT/'initial-mechanist-counterexample085.json.gz'
with target.open('xb')as f:f.write(data)
j=json.loads(gzip.decompress(data));assert j['fresh_public_calls']==69 and j['completed_asserted_cases']==68
cases=json.loads((OUT/'initial-pure-cases085.json').read_bytes())
assert j['current_case']==cases[68] and j['current_input']==cases[68]['input']
assert j['current_input']['operator']=='mechanist'and j['current_input']['skill']==3 and j['current_input']['window_seconds']==0
r=j['current_result'];assert 'total_healing'not in r and r['total_damage']==0
skill=r['estimate']['skill']
assert skill['total_healing']==skill['phase_healing']==skill['window_healing']==skill['cycle_healing']==0
assert set(j['current_report_texts'])=={'estimate','default','technical'}
assert j['current_report_texts']['estimate']==j['current_report_texts']['default']==j['current_visible_report']
assert all(isinstance(t,str)and t for t in j['current_report_texts'].values())
assert j['formatter_text_requests']==207
assert j['formatter_entry_counts']=={'format_estimate':69,'format_report_default':138,'format_report_technical':69}
assert j['source_hashes_before']==j['source_hashes_after']
damage=(OUT/'fixed-root085-source/rouge/damage.py').read_bytes()
tree=ast.parse(damage)
base=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='_skill_damage_base')
bombard=next(n for n in base.body if isinstance(n,ast.If)and isinstance(n.test,ast.Name)and n.test.id=='bombard')
last=bombard.body[-1];assert isinstance(last,ast.Return)and isinstance(last.value,ast.Dict)
keys=[k.value for k in last.value.keys if isinstance(k,ast.Constant)]
assert keys==['attack','total_damage','components','inapplicable_relics'] and 'total_healing'not in keys
definition=next(n for n in base.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='bombard'for t in n.targets))
assert "'mechanist'"in ast.unparse(definition.value)and '== 3'in ast.unparse(definition.value)
evaluation=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='_evaluate_damage_once')
top_healing=[n for n in evaluation.body if isinstance(n,ast.If)and any(isinstance(c,ast.Assign)and any(isinstance(t,ast.Subscript)and isinstance(t.slice,ast.Constant)and t.slice.value=='total_healing'for t in c.targets)for c in n.body)]
assert len(top_healing)==1 and "'kaltsit'"in ast.unparse(top_healing[0].test)
estimate=(OUT/'fixed-root085-source/rouge/estimate.py').read_text()
assert '    healing=0\n'in estimate and '    window_healing=0\n'in estimate
assert "'duration_seconds':duration,'total_damage':damage,'total_healing':healing"in estimate
assert "'window_healing':window_healing"in estimate
receipt={'status':'confirmed_legacy_shape_contract_preparation_failure_not_product_defect',
    'counterexample_gzip_sha256':sha(data),'original_69_calls_not_repeated':True,'independent_API_calls':0,
    'independent_formatter_calls':0,'Qt_calls':0,'Wine_calls':0,
    'completed_source_rows_preserved':68,'current_case_original_index':68,'current_source_row_preserved':True,
    'actual_legacy_shape_has_no_top_level_total_healing':True,'explicit_estimate_zero_healing_fields':
        {k:skill[k]for k in ['total_healing','phase_healing','window_healing','cycle_healing']},
    'correct_source_route':'damage._skill_damage_base bombard (Mechanist S3), return at180; build_estimate zero-healing fields; _evaluate only adds top healing for KaltsitS1/S3',
    'initial_readonly_message_source_line_correction':'Earlier message mistakenly cited154 (Silverash frost) and generic top-healing update; corrected without changing any artifact or calculation.',
    'allowed_contract_correction':'For section81 window0 MechanistS3 assert exact absence top-level total_healing plus explicit estimate window_healing==0 (and total_healing==0); all other owners retain exact existing top-level field assertion.',
    'forbidden_relaxations':['No dict.get default','No converting absence to None/0','No relaxed None arithmetic','No changing product or old3063 body'],
    'all_three_text_requests_already_saved':True,'source_before_after_no_drift':True,
    'format_requests_already_executed_by_author':207,'formatter_entries_already_executed_by_author':276,
    'final_saved_reassertion_and_remaining_only_run_pending':True,'tracked_mutations':False}
with(OUT/'legacy-shape-boundary085.json').open('x',encoding='utf-8')as f:
    json.dump(receipt,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
print(json.dumps({'status':'confirmed_legacy_shape','API':0,'formatters':0,
    'receipt_sha256':sha((OUT/'legacy-shape-boundary085.json').read_bytes())}))
