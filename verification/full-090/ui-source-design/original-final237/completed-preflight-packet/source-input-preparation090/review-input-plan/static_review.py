"""Small read-only plan/source inspection; no project imports or execution."""
import ast
from collections import Counter
import hashlib
import json
from pathlib import Path

P=Path('/workspace/.continuation/root-transport-preparation090')
O=P/'review-input-plan'
NAMES=('additional8-input-plan090.json','producer-and-consumer-preparation090.json',
       'source-production-boundary87/app.py','source-production-boundary87/timing.py',
       'saved89-native-proof090.json','saved89-five-state-UI-consumer-design090.json')
raw={name:(P/name).read_bytes()for name in NAMES}
sha=lambda b:hashlib.sha256(b).hexdigest()
plan=json.loads(raw[NAMES[0]]);producer=json.loads(raw[NAMES[1]])
proof=json.loads(raw[NAMES[4]]);states=json.loads(raw[NAMES[5]])
assert sha(raw[NAMES[2]])==producer['app_producer']['sha256']
assert sha(raw[NAMES[3]])==producer['timing_input_schema']['sha256']
assert len(raw[NAMES[2]])==producer['app_producer']['bytes']
assert len(raw[NAMES[3]])==producer['timing_input_schema']['bytes']
app=raw[NAMES[2]].decode();timing=raw[NAMES[3]].decode()
tree=ast.parse(app);ast.parse(timing)
factory=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='number')
assert any(isinstance(n,ast.Call)and isinstance(n.func,ast.Name)and n.func.id=='QDoubleSpinBox'for n in ast.walk(factory))
ranges=[n for n in ast.walk(factory)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='setRange']
assert len(ranges)==1 and ast.literal_eval(ranges[0].args[0])==0
assert isinstance(ranges[0].args[1],ast.Name)and ranges[0].args[1].id=='maximum'
window=next(n.value for n in ast.walk(tree)if isinstance(n,ast.Assign)and any(
    isinstance(t,ast.Attribute)and isinstance(t.value,ast.Name)and t.value.id=='self'and t.attr=='window_seconds'for t in n.targets))
assert isinstance(window,ast.Call)and isinstance(window.func,ast.Name)and window.func.id=='number'
assert [ast.literal_eval(n)for n in window.args]==[40,3600,2]
assert "self.attack=QLabel('由培养档案计算')"in app
assert "values=operator_attributes(self.operator.currentData(),**self.training_conditions())"in app
assert "'continuous_attacks':self.continuous_attacks.isChecked()"in app
assert "(self.continuous_attacks,current.get('sp_type')=='INCREASE_WHEN_ATTACK')"in app
assert 'self.timing_scenario=QPlainTextEdit()'in app
assert "scenario['timing']=json.loads(self.timing_scenario.toPlainText())"in app
assert "if not isinstance(scenario['timing'],dict)"in app
assert "value=self.options[key]"in timing and 'if not isinstance(value,list) or len(value)>100:'in timing
assert "'target_windows' not in self.options or any(a<=frame<b for a,b in self.windows)"in timing

cases=plan['cases'];assert len(cases)==8 and len(plan['pairs'])==4
assert len({json.dumps(c['input'],sort_keys=True,allow_nan=False)for c in cases})==8
counts=Counter(c['pair_id']for c in cases)
assert len(counts)==4 and set(counts.values())=={2}
for pair_id in counts:
    pair=[c for c in cases if c['pair_id']==pair_id]
    assert {c['widget_checked']for c in pair}=={False,True}
    left={k:v for k,v in pair[0]['input'].items()if k!='continuous_attacks'}
    right={k:v for k,v in pair[1]['input'].items()if k!='continuous_attacks'}
    assert left==right
    for case in pair:
        a=case['input']
        assert type(a['continuous_attacks'])is bool and a['continuous_attacks']is case['widget_checked']
        assert a['window_seconds']==12.75 and 0<=a['window_seconds']<=3600
        assert a['window_seconds']*100==int(a['window_seconds']*100)
        assert 'base_attack'not in a and 'attack'not in a
        assert case['UI_actual_execution']is False
empty=[c for c in cases if c['input'].get('timing')=={'target_windows':[]}]
assert len(empty)==2
assert producer['timing_editor']['actual_UI_editor_empty_target_executed']is False
assert producer['actual_root_source_transport_before_new8_required']is True
assert producer['actual88_89_90_source_freeze_complete']is False
assert 'reviewed_draft_not_actual_root'in next(k for k in producer if k.startswith('author088_helper'))

records=states['selected_saved_records']
assert len(records)==states['UI_consumer_state_count']==proof['public_state_projection_count']==5
assert [r['saved_sequence']for r in records]==[19,9,3,22,6]
assert [r['crew_observed_type']for r in records]==['NoneType','bool','bool','int','int']
assert all(r['crew_stored_type']=='int'and type(r['crew_stored_value'])is int for r in records)
typed_nodes=0
for r in records:
    assert r['producer_is_saved_synthetic_public_RunState_test_input_not_native_OCR']is True
    assert type(r['state']['crew_count'])is int and r['state']['crew_count']==r['crew_stored_value']
    for member in r['members'].values():
        assert type(member['present'])is bool and member['sources']=={}
        assert all(type(value)is int for value in member['fields'].values())
    stack=[(r['observed'],r['observed_native']),(r['state'],r['state_native'])]
    while stack:
        value,node=stack.pop();typed_nodes+=1;kind=node['type']
        assert type(value).__name__==kind
        if kind=='dict':
            assert list(value)==[pair[0]['value']for pair in node['items']]
            stack.extend((value[pair[0]['value']],pair[1])for pair in node['items'])
        elif kind=='list':
            assert len(value)==len(node['items']);stack.extend(zip(value,node['items']))
        elif kind=='float':assert value.hex()==node['hex']
        else:assert value==node['value']
assert states['prep_RunState_constructor_calls']==states['prep_RunState_apply_calls']==0
assert states['prep_application_API_or_Qt_Wine_calls']==states['damage_API_new_requests_for89']==0
assert proof['RunState_constructor_calls']==proof['RunState_apply_calls']==0
assert proof['actual_GUI_membership_training_or_apply_pipeline_pass_claimed']is False
assert states['native_departure_or_OCR_skill_buff_rules_not_inferred']is True
assert states['actual_member_flag_name']=='present'
assert "member.get('present',True) and member.get('scope')!='account'"in app
assert "if member and not member.get('present',True):member=None"in app
assert 'if not member:return account'in app
assert raw=={name:(P/name).read_bytes()for name in NAMES},'review inputs changed'

receipt={'status':'STATIC_INPUT_PLAN_PASS_PENDING_ACTUAL_ROOT088_TRANSPORT',
 'scope':'Small source/plan/saved-state inspection of six named files only; no project execution',
 'input_files':{name:{'bytes':len(b),'sha256':sha(b)}for name,b in raw.items()},
 'declared_existing_producer_commit':producer['actual_existing_producer_commit'],
 'declared_commit_not_independently_reloaded_from_repository':True,
 'readonly_auto_base_source_and_omitted_manual_attack_verified':True,
 'hidden_continuous_checkbox_globally_serializes_native_bool_by_source':True,
 'target_windows_empty_list_really_expressible_by_editor_JSON_source':True,
 'pair_groups':4,'unique_input_designs':8,'fixed_window_seconds':12.75,
 'actual_window_factory_bounds_by_source':[0,3600],'actual_window_decimals_by_source':2,
 'window_default40_is_not_minimum':True,
 'five_saved89_states_checked':5,'native_type_float_hex_and_mapping_order_nodes':typed_nodes,
 'saved89_is_synthetic_public_mapping_replay_not_apply_pipeline_or_native_departure':True,
 'draft088_consumer_not_promoted_to_actual_root':True,'root088_transport_still_pending':True,
 'new_API_calls':0,'project_helper_calls':0,'formatter_calls':0,
 'RunState_constructor_calls':0,'RunState_apply_calls':0,'Qt_calls':0,'Wine_calls':0,'tests_run':0,
 'original44_or_original38_reexecuted':False,'live_runner_modified':False,
 'blockers':[],'limits':'Source-expressible input design only; actual root088 transport and final088/089/090 source freeze remain prerequisites. No actual Qt producer, private context reset, string guard, or native observation/apply claim.'}
with(O/'receipt.json').open('x',encoding='utf-8')as out:json.dump(receipt,out,ensure_ascii=False,indent=2);out.write('\n')
print(json.dumps({k:v for k,v in receipt.items()if k!='input_files'},ensure_ascii=False))
