"""Independent static review only; no production/API/formatter/Qt imports."""
from pathlib import Path
from collections import Counter
import ast
import hashlib
import io
import json
import subprocess
import tarfile

OUT=Path(__file__).resolve().parent
AUTHOR=OUT.parent
REPO=Path('/workspace/rougezhushou')
ROOT='2dfd9fa2c9a62db0112bc0fb98cd23123dd3b48b'
BASE_SHA='c58ff7ac462e7a9aa457e4b59471a162cbf5c6daf58192f6b5a852901fcdcc98'
def sha(data):return hashlib.sha256(data).hexdigest()
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def save(name,value):
    with (OUT/name).open('x',encoding='utf-8') as f:
        json.dump(value,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def copy_exact(source,name):
    data=source.read_bytes();target=OUT/name;target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('xb') as f:f.write(data)
    assert source.read_bytes()==data
    return {'source_path':str(source),'archive_path':name,'bytes':len(data),'sha256':sha(data)}
snapshots=[]
for name in ['wine-ui-smoke-085.py','cases085.py','public_contracts.py','supplemental-checks.py.fragment',
             'build_runner.py','check_public_schema085.py','make_public_package.py','check_root_compatibility.py','CHECKPOINT.md']:
    snapshots.append(copy_exact(AUTHOR/name,'initial-static-snapshot/'+name))
base=Path('/workspace/.compat/wine-ui-smoke-080.py').read_bytes();assert sha(base)==BASE_SHA
snapshots.append(copy_exact(Path('/workspace/.compat/wine-ui-smoke-080.py'),'actual080-preserved.py'))
initial=OUT/'initial-static-snapshot'
runner=(initial/'wine-ui-smoke-085.py').read_bytes();text=runner.decode();old=base.decode()
helpers=(initial/'public_contracts.py').read_text()+'\n'+(initial/'cases085.py').read_text()
fragment=(initial/'supplemental-checks.py.fragment').read_text()
first="if __name__ == '__main__' and "
assert text.startswith(first)
entry=text[:text.index('\n\n')+2]
assert entry in ["if __name__ == '__main__' and "+v+":\n    raise RuntimeError('UI085 final source/schema are pending; no Qt execution is permitted')\n\n"for v in ['True','False']]
assert text.count(fragment+'\n')==1 and text.count(helpers+'\n\n')==1
restored=text[len(entry):].replace(fragment+'\n','',1).replace(helpers+'\n\n','',1)
for name in ['wine-ui-report-difference-080.json','wine-window-080.png','wine-ui-080.json','wine-ui-failure-080.png',
             'wine-sown-tile-control-080.png','wine-movement-reference-080.png','wine-medical-trait-080.png']:
    restored=restored.replace(name.replace('-080','-085'),name)
for name in ['preserved_old_checks','preserved_full_060_checks','preserved_full_065_checks','preserved_full_070_checks','preserved_full_075_checks']:
    line=next(line for line in old.splitlines()if line.strip().startswith(f"receipt['{name}']=len(checks)"))
    assert restored.count(line+'-(group085_end-group085_start)')==1
    restored=restored.replace(line+'-(group085_end-group085_start)',line,1)
added="        receipt['preserved_full_080_checks']=len(checks)-(group085_end-group085_start)\n        assert receipt['preserved_full_080_checks']==3063,receipt['preserved_full_080_checks']\n"
assert restored.count(added)==1
restored=restored.replace(added,'',1)
assert restored.encode()==base
ast.parse(runner);ast.parse(base)
case_tree=ast.parse((initial/'cases085.py').read_bytes())
assert not any(isinstance(n,(ast.Import,ast.ImportFrom))for n in ast.walk(case_tree))
namespace={};exec(compile(case_tree,'pure-local-case-data085','exec'),namespace)
cases=namespace['cases085']()
counts=Counter(row['section']for row in cases)
assert counts=={81:136,82:216,83:450,84:88,85:264}and len(cases)==1154
assert len({canonical(row)for row in cases})==1154
new_functions={node.name for node in ast.parse(helpers).body if isinstance(node,ast.FunctionDef)}
old_functions={node.name for node in ast.parse(base).body if isinstance(node,ast.FunctionDef)}
assert not(new_functions&old_functions)
paths=subprocess.check_output(['git','ls-tree','-r','--name-only',ROOT,'rouge','tests','scripts'],cwd=REPO,text=True).splitlines()
paths=[p for p in paths if p.endswith(('.py','.json'))]
assert len(paths)==723
archive=subprocess.check_output(['git','archive','--format=tar',ROOT,*paths],cwd=REPO)
sources={};public_bytes={}
with tarfile.open(fileobj=io.BytesIO(archive))as f:
    for member in f:
        if not member.isfile():continue
        assert member.name in paths;data=f.extractfile(member).read()
        sources[member.name]={'bytes':len(data),'sha256':sha(data)}
        if member.name.startswith('rouge/'):public_bytes[member.name]=data
assert len(public_bytes)==125
catalog=json.loads(public_bytes['rouge/data/catalog.json'])
options_tree=ast.parse(public_bytes['rouge/operator_options.py'])
options=next(ast.literal_eval(n.value)for n in options_tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='OPTIONS'for t in n.targets))
source_names=['rouge/app.py','rouge/operator_engine.py','rouge/damage.py','rouge/operator_options.py','rouge/catalog.py',
              'rouge/reporting.py','rouge/estimate.py','rouge/relics.py','rouge/timing.py','rouge/enemy_environment.py',
              'rouge/haruka_healing_reference.py','rouge/data/catalog.json']
for rel in source_names:
    target=OUT/'fixed-root085-source'/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(public_bytes[rel])
    snapshots.append({'source_path':f'git:{ROOT}:{rel}','archive_path':str(target.relative_to(OUT)),
                      'bytes':len(public_bytes[rel]),'sha256':sha(public_bytes[rel])})
app=public_bytes['rouge/app.py'].decode();engine=public_bytes['rouge/operator_engine.py'].decode()
assert 'if isinstance(default,bool):'in app and 'widget=QCheckBox(label)'in app
assert 'elif isinstance(default,int):'in app and 'widget=QSpinBox();widget.setRange(0,maximum);widget.setValue(default)'in app
assert 'widget=number(default,maximum,2)'in app
assert 'self.damage_form.setRowVisible(widget,owner==op and skill in skills)'in app
assert 'if owner==op and self.skill.currentData() in skills:'in app
assert 'widget.isChecked() if isinstance(widget,QCheckBox) else widget.value()'in app
estimate=ast.parse(public_bytes['rouge/estimate.py'])
delegator=next(n for n in estimate.body if isinstance(n,ast.FunctionDef)and n.name=='format_estimate')
condition=delegator.body[0]
assert isinstance(condition,ast.If)and isinstance(condition.test,ast.Compare)
assert ast.literal_eval(condition.test.left)=='report'
assert ast.unparse(condition.body[-1])=='return format_report(result)'
attack_tree=ast.parse(public_bytes['rouge/operator_engine.py'])
estimates=[n.value for n in ast.walk(attack_tree)if isinstance(n,ast.Assign)and isinstance(n.value,ast.Dict)
    and any(isinstance(t,ast.Subscript)and isinstance(t.value,ast.Name)and t.value.id=='result'
            and isinstance(t.slice,ast.Constant)and t.slice.value=='estimate'for t in n.targets)]
estimate_dict=next(n for n in estimates if any(isinstance(k,ast.Constant)and k.value=='skill'for k in n.keys))
skill_dict=next(v for k,v in zip(estimate_dict.keys,estimate_dict.values)if isinstance(k,ast.Constant)and k.value=='skill')
skill_fields={k.value for k in skill_dict.keys if isinstance(k,ast.Constant)}
required={'mode','initial_seconds','recharge_seconds','cycle_seconds','duration_seconds','sp_recovery_per_second','hit_counts',
          'total_healing','phase_healing','window_healing','window_hps','cycle_healing','cycle_hps','skill_attack'}
assert required<=skill_fields
anchors={82:set(),84:set(),85:set()};anchor_pairs=Counter();active_keys=Counter();hidden=Counter();errors=[]
order=list(catalog['relics'])
for index,case in enumerate(cases):
    args=case['input'];profile=catalog['operators'][args['operator']]
    assert type(args['skill'])is int and type(args['elite'])is int and type(args['level'])is int
    assert 1<=args['level']<=profile['phases'][args['elite']]['max_level']
    assert profile['skills'][args['skill']-1]['unlock_elite']<=args['elite']
    assert args['elite']==2 or args['skill_rank']<=7
    assert sorted(args['relic_ids'],key=order.index)==args['relic_ids']and len(set(args['relic_ids']))==len(args['relic_ids'])
    assert type(args['healing_targets'])is int and args['healing_targets']in [0,1]
    assert type(args['preexisting_fragile'])is bool and type(args['cooperative'])is bool
    if args['operator']=='mechanist':assert type(args['charge_count'])is int and args['charge_count']==0
    for key,label,default,maximum,skills in options.get(args['operator'],[]):
        if key not in args:continue
        assert args['skill']in skills,(index,key,'inactive option included')
        assert type(args[key])is type(default),(index,key,type(args[key]),type(default))
        if type(default)in [int,float]:assert 0<=args[key]<=maximum
        active_keys[(args['operator'],key,type(default).__name__)]+=1
    if case.get('hidden_neural_checkbox_state'):
        assert args['operator']=='char_4204_mantra'and args['skill']==3
        assert not({'enemy_is_boss','enemy_in_neural_break','initial_neural_buildup','enemy_buildup_resistance'}&args.keys())
        hidden['Mantra_S3']+=1
    if case.get('hidden_repeat_checkbox_state'):
        assert args['operator']=='char_4202_haruka'and args['skill']in [1,3]and 'haruka_repeat'not in args
        hidden['Haruka_inactive']+=1
    if args['operator']=='char_1048_orchd2':
        assert ('double_charge'in args)==(args['skill']==1)
    field={82:'low_cost_healing_target',84:'haruka_repeat',85:'near_previous_deployment'}.get(case['section'])
    if field and field in args:
        assert type(args[field])is bool
        anchor=canonical({k:v for k,v in args.items()if k!=field})
        if args[field]:assert anchor in anchors[case['section']];anchor_pairs[case['section']]+=1
        else:anchors[case['section']].add(anchor)
    if case.get('expected_error'):
        assert case['section']==83 and args['skill']==2 and args['initial_neural_buildup']==1500
        assert case['expected_error']=='initial_neural_buildup需要范围内的有限非负数。'
        assert args['enemy_is_boss']is False or case.get('processed_enemy_level_type')=='NORMAL'
        errors.append({'index':index,'case':case})
assert len(errors)==24 and anchor_pairs=={82:108,84:40,85:132}
assert "if op=='char_4204_mantra':"in engine and 'bursts=self.neural(neural_events,components)'in engine
assert "scenario['operator'] in ('char_1042_phatm2','char_4204_mantra')"in public_bytes['rouge/damage.py'].decode()
assert "isinstance(scenario.get('near_previous_deployment'),str)"in public_bytes['rouge/damage.py'].decode()
save('initial-pure-cases085.json',cases)
save('initial-static-review085.json',{'status':'passed_static_only_awaiting_final_source_API_and_runner_receipts',
    'approved_root_commit':ROOT,'source723_hashes':sources,'public_source_count':125,
    'runner_snapshot_sha256':sha(runner),'runner_prefix_pending':entry.startswith(first+'True'),
    'old_actual080_sha256':BASE_SHA,'full_old3063_body_inverse_exact':True,
    'new_pure_case_counts':dict(counts),'new_pure_cases':1154,'planned_total':4217,
    'case_objects_unique':True,'case_metadata_inactive_option_omissions_checked':True,
    'true_checkbox_and_numeric_spin_producers_static':True,'false_before_true_pairs':dict(anchor_pairs),
    'hidden_case_counts':dict(hidden),'exact_old_threshold_errors':errors,
    'source_estimate_fields_required':sorted(required),'source_estimate_fields_exist':True,
    'estimate_text_source_delegates_to_default_report':True,
    'expected_final_text_requests':3390,'expected_formatter_entries_with_delegate':4520,
    'actual_production_API_calls':0,'actual_formatter_calls':0,'actual_selected_talents_calls':0,
    'Qt_calls':0,'Wine_calls':0,'tracked_mutations':False,
    'snapshots':snapshots,'actual_control_claims_are_static_only':True,
    'Mantra_S3_API_consumer_remains_actual_despite_hidden_checkboxes':True,
    'pending_runner_never_executed':True,'all_native_clocks_and_stacking_unknowns_retained':True})
print(json.dumps({'status':'passed_static_only','pure_cases':1154,'source723':len(sources),'public125':len(public_bytes),
    'exact_existing_errors':24,'old3063_inverse':'exact','API':0,'formatters':0,'Qt':0,'Wine':0,
    'review_sha256':sha((OUT/'initial-static-review085.json').read_bytes())}))
