"""Static named git blobs and already sealed source receipts only; no product imports."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess

HERE=Path(__file__).resolve().parent
REPO=Path('/workspace/rougezhushou')
COMMIT='9ef5a469673502754db3be320a8eece9a7fd18d4'
AUTHOR=Path('/workspace/.continuation/p2-remaining-boolean-consumers-086-source')
INDEPENDENT=Path('/workspace/.continuation/independent-source086')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def save(name,value):
    raw=(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
    with (HERE/name).open('xb')as out:out.write(raw)
    return sha(raw)
assert subprocess.check_output(['git','rev-parse',COMMIT],cwd=REPO,text=True).strip()==COMMIT
bindings=[];sources={}
for name in ['rouge/app.py','rouge/operator_options.py','rouge/operator_engine.py',
             'rouge/data/catalog.json','rouge/reporting.py']:
    raw=subprocess.check_output(['git','show',COMMIT+':'+name],cwd=REPO)
    assert raw==(AUTHOR/'baseline'/name).read_bytes()
    sources[name]=raw
    bindings.append({'source_path':f'git:{COMMIT}:{name}','archive_path':name,
        'bytes':len(raw),'sha256':sha(raw),'same_bytes_as_sealed_b5_source':True,
        'reconstruction':'git show '+COMMIT+':'+name})
historical_files=[AUTHOR/'actual-qt-producer-static-closure.json',AUTHOR/'source-handoff.json',
    AUTHOR/'CONSUMER_BOUNDARIES.md',INDEPENDENT/'source-saved-review086.json',
    INDEPENDENT/'all-literal-field-inventory086.json',INDEPENDENT/'handoff-independent-source086.json',
    INDEPENDENT/'boundary-subreview/receipt-boundary-final086.json']
history=[]
for path in historical_files:
    raw=path.read_bytes()
    history.append({'source_path':str(path),'bytes':len(raw),'sha256':sha(raw),
        'scope':'Already sealed source/saved evidence read, not a fresh raw/API verification'})
producer=json.loads(historical_files[0].read_bytes())
old_review=json.loads((INDEPENDENT/'source-saved-review086.json').read_bytes())
assert old_review['status']=='PASS_SOURCE_AND_SAVED_ONLY'and old_review['flag_count']==12
assert old_review['saved_36_inputs_native_tree_result_binding_and_three_reports_recompared']is True
old_inventory=json.loads((INDEPENDENT/'all-literal-field-inventory086.json').read_bytes())
options_tree=ast.parse(sources['rouge/operator_options.py'])
options=next(ast.literal_eval(n.value)for n in options_tree.body if isinstance(n,ast.Assign)
    and any(isinstance(t,ast.Name)and t.id=='OPTIONS'for t in n.targets))
fields=[(r['owner'],r['field'])for r in producer['options']]
assert len(fields)==len(set(fields))==12 and len({r[0]for r in fields})==8
app=sources['rouge/app.py'].decode()
assert 'if isinstance(default,bool):'in app and 'widget=QCheckBox(label);widget.setChecked(default)'in app
assert 'self.damage_form.setRowVisible(widget,owner==op and skill in skills)'in app
assert 'if owner==op and self.skill.currentData() in skills:'in app
assert 'scenario[key]=widget.isChecked() if isinstance(widget,QCheckBox) else widget.value()'in app
assert 'self.model_option_widgets.append((operator,key,skills,widget))'in app
catalog=json.loads(sources['rouge/data/catalog.json'])
scope={
 'reinforcement_blocks_target':('all skill and normal plans','Original trait, all cultivation; not an E2 talent gate','No reinforcement position, separate hits or native attachment inferred.'),
 'enemy_below_half':('apply_self_talents before both plans','Selected named 反移情 exists only E2; E0/E1 UI can still emit bool while missing talent contributes0','Other Mizuki hidden/module attachments remain unknown.'),
 'frozen_at_skill_end':('S3 non-normal terminal component and result reference','S3 available E2; S1/S2 and normal have no terminal consumer','Nominal end does not bind terminal, freeze removal or same-frame disappearance.'),
 'ines_first_deployment':('S3 non-normal plan and fee_section note','S3 available E2; S1/S2 and normal inactive','No actual first-deployment history or independent shadow path collision clock inferred.'),
 'ranged_attack':('all skill and normal plans','Selected module max_cnt>10 overrides skill ranged_scale only; normal remains .8/1 with actual cycle/continuous public gates','Module alone proves neither whole API inactivity nor nonzero normal contribution. Note collision and hidden attachment remain unknown.'),
 'organ_mode':('S2 non-normal tone branch','S2 available E1; S1/S3 and normal inactive','No native tone-change history or note-flight clock inferred.'),
 'fever':('S2 non-normal two-hit argument','S2 available E1; S1/S3 and normal inactive','S3 lethal survival description does not create this output consumer; no native Fever start/end inferred.'),
 'power_coating':('all skill non-normal plans','Selected 强击瓶专家 exists from E0; normal expression reads flag but numeric factor1','Bool describes conditional first50 coverage, not an actual per-arrow counter or native coverage.'),
 'double_charge':('S1 extra arrows, parameter row, initial/recharge cost and event-SP cost','S1 all cultivation; S2/S3 and normal extra arrows inactive','Full cast end and arrow collision remain unknown; cost consumers must not be omitted.'),
 'steal_success':('S2 non-normal attack speed, interval and five extra ammunition','S2 available E1; S1/S3 and normal inactive','No actual successful ally theft, live shield decay or ammunition observation inferred.'),
 'delivery_coordinate':('S3 non-normal bombing source','S3 available E2; S1/S2 and normal inactive','Owner target windows do not establish coordinate collision or placement timing.'),
 'overload':('S2 non-normal four-hit source','S2 available E1; S1/S3 and normal inactive','Random targeting, afterimages and soul clocks remain unknown.')}
rows=[]
for old in producer['options']:
    owner,key=old['owner'],old['field']
    matches=[r for r in options[owner]if r[0]==key];assert len(matches)==1
    field,label,default,maximum,skills=matches[0]
    assert type(default)is bool and maximum==1
    assert default is old['default']and label==old['label']and list(skills)==old['skills']
    profile=catalog['operators'][owner]
    unlocks={str(i+1):s['unlock_elite']for i,s in enumerate(profile['skills'])}
    assert unlocks=={'1':0,'2':1,'3':2}
    consumer,qualification,unknown=scope[field]
    rows.append({'owner':owner,'field':field,'label':label,'default_bool':default,
        'QCheckBox_producer':True,'visible_and_serialized_skills':list(skills),
        'hidden_omitted_skills':[i for i in (1,2,3)if i not in skills],
        'wrong_owner_omitted':True,'skill_unlock_elite':unlocks,
        'serialization_result_type':'bool from isChecked; no text/None/integer checkbox state',
        'actual_consumer_scope':consumer,'qualification_boundary':qualification,'unknown_boundary':unknown})
literal_sites=[]
keys={f for _,f in fields}
for name in ('rouge/operator_engine.py','rouge/reporting.py'):
    tree=ast.parse(sources[name]);lines=sources[name].decode().splitlines()
    parents={child:node for node in ast.walk(tree)for child in ast.iter_child_nodes(node)}
    for node in ast.walk(tree):
        if not isinstance(node,ast.Call)or not isinstance(node.func,ast.Attribute)or node.func.attr!='get' or not node.args:continue
        if not isinstance(node.args[0],ast.Constant)or node.args[0].value not in keys:continue
        ancestor=node;conditions=[];function=None
        while ancestor in parents:
            ancestor=parents[ancestor]
            if isinstance(ancestor,ast.If):conditions.append(ast.unparse(ancestor.test))
            if isinstance(ancestor,ast.FunctionDef):function=ancestor.name;break
        literal_sites.append({'path':name,'line':node.lineno,'field':node.args[0].value,
            'expression':ast.unparse(node),'function':function,'enclosing_conditions':conditions,
            'source_context':[{'line':i+1,'text':lines[i]}for i in range(max(0,node.lineno-4),min(len(lines),node.lineno+3))]})
old_sites=old_inventory['literal_field_get_sites']
identity=lambda r:(r['path'],r['line'],r['field'],r['expression'])
assert {identity(r)for r in literal_sites}=={identity(r)for r in old_sites}
assert len(literal_sites)==17
named={}
for owner,talent_name in [('char_437_mizuki','反移情'),('char_4182_oblvns','颂乐音符'),('char_1048_orchd2','强击瓶专家')]:
    named[owner]=[t for group in catalog['operators'][owner]['talents']for t in group if t['name']==talent_name]
assert all(t['phase']==2 for t in named['char_437_mizuki'])
assert min(t['phase']for t in named['char_1048_orchd2'])==0
module=next(m for m in catalog['operators']['char_4182_oblvns']['modules']if m['id']=='uniequip_002_oblvns')
assert (module['unlock_elite'],module['unlock_level'])==(2,60)
limits=[]
for level,row in enumerate(module['levels'],1):
    candidates=[c for part in row['parts']if not part.get('isToken')
        for c in (part.get('addOrOverrideTalentDataBundle')or{}).get('candidates')or[]if c['name']=='颂乐音符']
    values=[{b['key']:b['value']for b in c['blackboard']}['max_cnt']for c in candidates]
    assert values==([]if level==1 else[12.0])
    limits.append({'module_level':level,'named_candidate_max_cnt':values})
excerpts=[]
needles=['if isinstance(default,bool):','self.damage_form.setRowVisible(widget,owner==op and skill in skills)',
    'for owner,key,skills,widget in self.model_option_widgets:',
    'scenario[key]=widget.isChecked() if isinstance(widget,QCheckBox) else widget.value()']
app_lines=app.splitlines()
for needle in needles:
    hits=[i for i,line in enumerate(app_lines)if needle in line]
    assert hits
    for hit in hits:excerpts.append({'needle':needle,'lines':[{'line':i+1,'text':app_lines[i]}
        for i in range(max(0,hit-2),min(len(app_lines),hit+5))]})
base_path=Path('/workspace/.compat/wine-ui-smoke-085.py')
base=base_path.read_bytes();assert sha(base)=='b6976652eb50e06909cca68490b0b9d3e11ea81fbc9a73ca87efcbb10354e306'
assert b"receipt['preserved_full_080_checks']==3063"in base
assert b'group085_counts=={81:136,82:216,83:450,84:88,85:264}'in base
notes={'app_actual_static_excerpts':excerpts,'current_exact17_literal_consumers':literal_sites,
    'three_named_cultivation_talent_sources':named,'covered_Oblvns_module_boundary':{
        'id':module['id'],'unlock_elite':2,'unlock_level':60,'named_candidate_limits':limits,
        'selected_talents_qualification_source':'selected_talents elite/level/potential gate; parts are only applied after module unlock',
        'skill_override_condition':'module_id and not normal and selected named max_cnt>10',
        'normal_contribution_unknown_without_runtime_cycle_and_continuous_gates':True}}
notes_sha=save('static-source-notes086.json',notes)
receipt={'status':'PASS_SOURCE_ONLY_REAL_QCHECKBOX_PRODUCERS_12_FIELDS_PENDING_UI090',
    'approved_actual085_commit':COMMIT,'actual085_runner_path':str(base_path),'actual085_runner_sha256':sha(base),
    'preserved_actual085_full_body_is_base_for_parent_UI090':True,'preserved_actual085_case_count':4217,
    'source_bindings':bindings,'same_five_consumers_as_sealed_b5_source':True,
    'field_count':12,'owner_count':8,'fields':rows,'producer_construction_and_active_serialization_static_only':True,
    'actual_current_Qt_runtime_executed':False,'visibility_is_not_API_qualification':True,
    'already_sealed_source_saved36_receipts_reused':history,
    'historical36_scope':'Qualified E2, no module, frames, three values per field only; not fresh9ef output or UI090 proof',
    'original240_skillrank_or12module_parts_audit_repeated':False,
    'static_source_notes_path':'static-source-notes086.json','static_source_notes_sha256':notes_sha,
    'product86_draft_and_final_UI090_not_approved_by_this_receipt':True,
    'new_case_design_or_Cartesian_matrix_created':False,
    'calls':{'application_API':0,'formatter':0,'production_helper':0,'tests':0,'Qt':0,'Wine':0},
    'tracked_mutations':False,'native_clocks_counts_probabilities_attachment_live_history_inferred':False,
    'next_action':'Parent may continue source-only UI090 designs preserving full4217; wait final86-90 sources and root authorization before any API or runner execution.'}
digest=save('source-producer-review086.json',receipt)
print(json.dumps({'status':receipt['status'],'fields':12,'owners':8,'source_notes_sha256':notes_sha,
    'receipt_sha256':digest,'API':0,'helpers':0,'Qt':0,'Wine':0},ensure_ascii=False))
