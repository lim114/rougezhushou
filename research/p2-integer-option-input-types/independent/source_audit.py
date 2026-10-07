"""Read-only independent AST/UI contract audit of frozen HEAD58 public code."""
import ast
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
AUDIT=Path('/workspace/.continuation/p2-integer-option-audit-061')
FROZEN=AUDIT/'frozen'
ROOT=Path('/workspace/rougezhushou')
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
freeze=json.loads((AUDIT/'freeze.json').read_text())
assert freeze['baseline_head']=='4543b9b91ac7b61fc019bb96a3d6d5ac2593a6bc'
drift=[name for name,expected in freeze['public_source_hashes'].items() if sha(FROZEN/name)!=expected]
assert not drift,drift
engine_path=FROZEN/'rouge/operator_engine.py'
engine=engine_path.read_text()
tree=ast.parse(engine)
parents={}
for node in ast.walk(tree):
    for field,value in ast.iter_fields(node):
        if isinstance(value,ast.AST):parents[value]=(node,field)
        elif isinstance(value,list):
            for child in value:
                if isinstance(child,ast.AST):parents[child]=(node,field)
calls=[]
for node in ast.walk(tree):
    if not (isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr=='option'):
        continue
    if not any(k.arg=='integer' and isinstance(k.value,ast.Constant) and k.value.value is True for k in node.keywords):
        continue
    key=ast.literal_eval(node.args[0])
    chain=[];child=node;function=None
    while child in parents:
        parent,route=parents[child]
        if isinstance(parent,ast.If):
            condition=ast.unparse(parent.test)
            # Elif operator chains imply negatives of all preceding operators;
            # these are omitted for readability, not reinterpreted as facts.
            if route in ('body','test') or ('op' not in condition and route=='orelse'):
                chain.append({'route':route,'condition':condition,'line':parent.lineno})
        elif isinstance(parent,ast.IfExp):
            chain.append({'route':route,'condition':ast.unparse(parent.test),'line':parent.lineno})
        elif isinstance(parent,ast.FunctionDef):function=parent.name
        child=parent
    calls.append({'key':key,'line':node.lineno,'function':function,
                  'source_call':ast.get_source_segment(engine,node),'if_ancestry':list(reversed(chain))})
calls.sort(key=lambda row:row['line'])
keys={row['key'] for row in calls}
excluded={'healing_targets','amiya_hit_targets','stolen_enemy_count'}
remaining=keys-excluded
assert len(calls)==28 and len(keys)==27 and len(remaining)==24
options_path=FROZEN/'rouge/operator_options.py'
options_tree=ast.parse(options_path.read_text())
options=next(ast.literal_eval(node.value) for node in options_tree.body if isinstance(node,ast.Assign)
             and any(isinstance(target,ast.Name) and target.id=='OPTIONS' for target in node.targets))
controls=[];checkboxes=[]
for owner,entries in options.items():
    for key,label,default,maximum,skills in entries:
        record={'owner':owner,'key':key,'label':label,'default':default,'default_type':type(default).__name__,
                'UI_maximum':maximum,'UI_visible_skills':list(skills)}
        if type(default) is bool:checkboxes.append(record)
        if key in remaining:
            assert type(default) is int,(key,type(default))
            record['constructor_from_actual_source']='QSpinBox'
            controls.append(record)
assert len(controls)==25
assert {row['key'] for row in controls}==remaining
assert not keys & {row['key'] for row in checkboxes}
app= (FROZEN/'rouge/app.py').read_text().splitlines()
assert app[664].strip()=='if isinstance(default,bool):'
assert app[665].strip()=='widget=QCheckBox(label);widget.setChecked(default)'
assert app[667].strip()=='elif isinstance(default,int):'
assert app[668].strip()=='widget=QSpinBox();widget.setRange(0,maximum);widget.setValue(default)'
assert app[1036].strip()=='scenario[key]=widget.isChecked() if isinstance(widget,QCheckBox) else widget.value()'
damage=(FROZEN/'rouge/damage.py').read_text()
assert "if has_healing(scenario['operator'],skill):" in damage
assert "active_counts.append(('healing_targets'" in damage
assert "if scenario['operator']=='char_1037_amiya3' and skill==2:" in damage
assert "if scenario['operator']=='char_4087_ines':" in damage
assert 'if isinstance(scenario.get(field),bool):raise ValueError(error)' in damage
enemy=(FROZEN/'rouge/enemy_environment.py').read_text().splitlines()
assert 'isinstance(weight,bool)' in enemy[19]

# These are public code query boundaries, not assertions about real mechanism
# attachment or native clocks. All skill lists are independently matched to UI.
scope={
 'summon_count':('char_110_deepcl','S1/S2; skill and normal plans'),
 'slash_kills':('char_1050_chen3','S2 only; non-normal plan'),
 'amiya_slash_kills':('char_1001_amiya2','S2 only; non-normal plan'),
 'incoming_hits':('char_1044_hsgma2','S1 only; non-normal plan'),
 'shield_contact_ticks':('char_1044_hsgma2','S2 only; non-normal plan'),
 'cold_state':('char_206_gnosis','S1/S2/S3; skill and normal plans'),
 'bubble_bursts':('char_4202_haruka','S1/S2/S3; non-normal plan only'),
 'levitate_triggers':('char_4202_haruka','S3 only; non-normal plan'),
 'snow_entries':('char_1046_sbell2','S1/S2/S3; conditional expression calls only for non-normal plan'),
 'drone_warmup_hits':('char_328_cammou / char_1038_whitw2','Cammou S1/S2 and Whitw2 S1/S2/S3; skill and normal plans'),
 'note_count':('char_4182_oblvns','S1/S2/S3; skill and normal plans'),
 'enemy_weight':('char_1015_aglna2','S1/S2/S3; skill and normal plans; manual raw bool already rejected upstream'),
 'bait_triggers':('char_1042_phatm2','S2 only; non-normal plan'),
 'enemy_attack_count':('char_1042_phatm2','S1/S2/S3; non-normal plan only'),
 'palsy_overflow_hits':('char_4204_mantra','S3 only; non-normal plan'),
 'palsy_triggers':('char_4204_mantra','S1/S2/S3; non-normal plan only'),
 'connected_stones':('char_2027_wang','S1/S2/S3; non-normal plan only'),
 'trap_triggers':('char_2027_wang','S1/S2/S3; non-normal plan only'),
 'trap_dot_ticks':('char_2027_wang','S1 only; non-normal plan'),
 'dragon_arrow_hits':('char_1048_orchd2','S3 only; non-normal plan'),
 'ghost_count':('char_1035_wisdel','S1/S2/S3; skill and normal plans'),
 'ghost_casts':('char_1035_wisdel','S1/S2/S3; skill and normal plans, but only if queried ghost_count is nonzero'),
 'dash_hits':('char_1029_yato2','S3 only; non-normal plan'),
 'casts_used':('char_298_susuro','S2 only; calculate short-circuit guard queried at lines 1255 and 1351; not a plan widget checkbox'),
}
assert scope.keys()==remaining
for row in controls:
    row['code_query_boundary']=scope[row['key']][1]
source_receipts=[
    'research/p2-target-count-input-types/source-receipt.json',
    'research/p2-incoming-clock/source-receipt.json',
    'research/p2-wisdel-ghost-clock/source-receipt.json',
    'research/p2-haruka-healing-targets/source-receipt.json',
    'research/p2-environment-and-lifecycle/source-receipt.json',
]
receipt_refs=[]
for rel in source_receipts:
    obj=json.loads((ROOT/rel).read_text())
    receipt_refs.append({'path':str(ROOT/rel),'sha256':sha(ROOT/rel),
                         'mode':'Existing committed receipt read only; no claim that historical /tmp raw files were freshly re-hashed'})
main=json.loads((AUDIT/'type-audit-summary.json').read_text())
assert main['baseline_head']==freeze['baseline_head']
assert {row['field'] for row in main['integer_call_sites']}==keys
assert main['remaining_integer_keys']==sorted(remaining)
new_defect_keys={row['field'] for row in main['accepted_queried_raw_bool_findings']}
assert len(new_defect_keys)==23 and new_defect_keys==remaining-{'enemy_weight'}
receipt={
    'independent_read_only_source_review_passed':True,'baseline_head':freeze['baseline_head'],
    'frozen_source_files_checked':len(freeze['public_source_hashes']),'frozen_source_drift':drift,
    'integer_true_call_count':len(calls),'unique_integer_keys':len(keys),'section54_keys_explicitly_excluded':sorted(excluded),
    'remaining_integer_keys':sorted(remaining),'remaining_key_count':len(remaining),
    'new_public_bool_defect_key_count_from_main_executed_trace':len(new_defect_keys),
    'new_defect_keys':sorted(new_defect_keys),'existing_upstream_rejected_key':'enemy_weight',
    'integer_call_sites':calls,'UI_integer_records':controls,'UI_boolean_records':checkboxes,
    'UI_boolean_key_intersection_with_integer_true_calls':[],
    'UI_scope':'Actual constructor and forwarding source inspected; no Qt object instantiated or Wine/GUI run',
    'special_healing_targets_boundary':'plan queries healing_targets for every extended operator, even when has_healing is false; retain section54 active-only guard and exclude this key from shared bool guard',
    'special_inactive_boundary':'Reject only when a remaining integer key is actually queried; do not prevalidate all scenario keys/UI-visible entries',
    'ghost_casts_gate':'If ghost_count is zero, ghost_casts is not queried and old inactive behavior must remain',
    'source_receipts_read':receipt_refs,
    'main_public_trace_read_only_reference':{'path':str(AUDIT/'type-audit-summary.json'),'sha256':sha(AUDIT/'type-audit-summary.json'),
        'counts':main['counts'],'not_independently_reexecuted':True},
    'candidate_smallest_guard':'In Combat.option, before float conversion, reject isinstance(raw,bool) only if integer=True and key is an explicit remaining-key allowlist (or omit already-blocked enemy_weight for 23-new-defect-only list); delegate every other input to existing value unchanged.',
    'must_preserve':['section54 active-only counts and its inactive values','unqueried fields on other operators/skills',
       'ghost_casts with ghost_count=0','real QCheckBox values','existing numeric/string/range/default behavior including old summon_count string TypeError and enemy_weight string rejection',
       'non-integer option fields and UI integer-default fields lacking integer=True callsites','native clock/attachment/stacking unknowns'],
    'risks':['Generic guard for all integer=True keys would change healing_targets inactive behavior',
             'Scenario-global validation bypasses conditional query and broadens inactive semantics',
             '24 source candidate keys are not 24 new defects; enemy_weight already has upstream raw-bool rejection',
             'Normal-plan queries for several fields must be preserved; UI-visible-skill list alone is not the query boundary'],
    'patch_created':False,'runtime_public_matrix_reexecuted':False,'root_tracked_edits':0,'frozen_or_author_draft_edits':0,
    'private_state_read':False,'game_actions':0,'native_validation':False,'Wine_validation':False,'actual_GUI_validation':False,
    'source_hashes':{rel:sha(FROZEN/rel) for rel in ('rouge/operator_engine.py','rouge/operator_options.py','rouge/app.py','rouge/damage.py','rouge/enemy_environment.py')},
}
(HERE/'receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:receipt[k] for k in ('independent_read_only_source_review_passed','frozen_source_files_checked','integer_true_call_count','unique_integer_keys','remaining_key_count','new_public_bool_defect_key_count_from_main_executed_trace','UI_boolean_key_intersection_with_integer_true_calls')},ensure_ascii=False))
