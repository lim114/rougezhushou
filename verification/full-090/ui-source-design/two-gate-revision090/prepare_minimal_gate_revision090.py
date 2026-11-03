"""Pure-source two-gate revision; no application or frozen-runner execution."""
from pathlib import Path
import ast, hashlib, json

HERE=Path(__file__).resolve().parent
OLD=Path('/workspace/.continuation/ui-090-final')
def sha(b):return hashlib.sha256(b).hexdigest()
def f(p,a=None):return {'source_path':str(p),'archive_path':a or p.name,'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}
def save(name,obj):
    p=HERE/name;p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n');return f(p)

old=OLD/'wine-ui-smoke-090-final.py'
b=old.read_bytes();assert sha(b)=='bb35222b37dbbdb4416f415a011f3a0b678c5285729ac0bccb76ec8ba336983a'
original=b.decode()
diffs=[
    ("profile_case090['kind']=='coveredmodule'", "profile_case090['pair_id']=='coveredmodule:oblvns-ranged-skill-vs-normal'"),
    ("row090['kind']=='coveredmodule':", "row090['pair_id']=='coveredmodule:oblvns-ranged-skill-vs-normal':"),
]
revised=original
for before,after in diffs:
    assert revised.count(before)==1
    revised=revised.replace(before,after)
ast.parse(revised)
p=HERE/'wine-ui-smoke-090-final-gate-revision.py';p.write_text(revised)
restored=revised
for before,after in reversed(diffs):
    assert restored.count(after)==1
    restored=restored.replace(after,before)
assert restored.encode()==b

def matrix(text):
    node=next(n for n in ast.walk(ast.parse(text)) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='rows090' for t in n.targets))
    return ast.literal_eval(node.value)
rows=matrix(revised);oldrows=matrix(original)
assert rows==oldrows and len(rows)==52
selected=[(i,r) for i,r in enumerate(rows) if r['pair_id']=='coveredmodule:oblvns-ranged-skill-vs-normal']
assert [i for i,r in selected]==[26,27]
assert [r['kind'] for i,r in selected]==['qualification','qualification']
assert [r['widget_checked'] for i,r in selected]==[False,True]
assert all(r['input']['operator']=='char_4182_oblvns' and r['input']['skill']==3 and r['input']['elite']==2 and r['input']['level']==60 and r['input']['module_level']==3 and r['input']['continuous_attacks'] is True for i,r in selected)
assert all(r['input']['module_id']=='uniequip_002_oblvns' for i,r in selected)
assert all((r['pair_id']=='coveredmodule:oblvns-ranged-skill-vs-normal') is (i in [26,27]) for i,r in enumerate(rows))
proof=save('two-gate-diff-and-reachability-proof090.json',{'format_version':1,'passed':True,'original_frozen_runner':f(old),'revised_runner':f(p),'exact_two_span_replacements':[{'before':x,'after':y} for x,y in diffs],'reverse_exact_restores_complete_original_frozen_runner':True,'original52_rows_inputs_kinds_projections_unchanged':True,'exact_selected_zero_based_rows':[26,27],'original_row_kinds_retained':['qualification','qualification'],'two_exact_pair_id_gates_reachable_for_both_states_and_only_these_states':True,'planned_trace_assertions_retained':['one normal=True plan entry','normal_not_none True','actual ranged condition consumed True','selected note max_cnt 12'],'730_source_freeze_old4217_inverse_and_full_other_formal_checks_reused':True,'new_API_helper_formatter_Qt_Wine_tests':0,'new_actual_GUI_pass':False})
scope=json.loads((OLD/'runner-scope-and-source-freeze090.json').read_bytes())
scope['runner']=f(p);scope['status']='FINAL_TWO_GATE_REVISION_PENDING_DIFFERENCE_STATIC_REVIEW_AND_ROOT_SOLE_ACTUAL_QT'
scope['minimal_revision']=proof
scope['original237_and_finalstage_remain_immutable']=True
scope['independent_final_formal_pending']=True
save('runner-scope-and-source-freeze090-revision.json',scope)
print(json.dumps({'runner':f(p),'proof':proof,'old_hash_unchanged':sha(old.read_bytes())},ensure_ascii=False))
