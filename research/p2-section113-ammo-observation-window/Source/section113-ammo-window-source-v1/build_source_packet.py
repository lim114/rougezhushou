"""Author-only stdlib Source builder; never imports or runs the project/tests."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path('/workspace/rougezhushou')
OUT = Path(__file__).parent
SHA = lambda value: hashlib.sha256(value).hexdigest()
local = [
 {'path':'rouge/operator_engine.py', 'before':"        mode=full['mode']\n        total_damage=full['damage'];total_healing=full['healing'];duration=full['duration']\n", 'after':"        mode=full['mode']\n        observation_seconds=self.s['window_seconds'] if mode=='ammo' and 'window_seconds' in self.s else shown['duration']\n        total_damage=full['damage'];total_healing=full['healing'];duration=full['duration']\n"},
 {'path':'rouge/operator_engine.py', 'before':"            'window_seconds':shown['duration'],\n            'window_healing':shown['healing'],\n            'window_dps':shown['damage']/shown['duration'] if shown['duration'] else None,\n            'window_hps':shown['healing']/shown['duration'] if shown['duration'] else None},\n", 'after':"            'window_seconds':observation_seconds,\n            'window_healing':shown['healing'],\n            'window_dps':shown['damage']/observation_seconds if observation_seconds else None,\n            'window_hps':shown['healing']/observation_seconds if observation_seconds else None},\n"},
 {'path':'rouge/estimate.py', 'before':"    if duration is not None:window_seconds=min(window_seconds,duration)\n", 'after':"    finite_ammo_window='window_seconds' in scenario and (operator,skill_index) in (('mechanist',1),('kaltsit',2))\n    if duration is not None and not finite_ammo_window:window_seconds=min(window_seconds,duration)\n"},
 {'path':'rouge/uncertain_sources.py', 'before':"    subtotal['window_dps'] = subtotal['window_damage'] / shown['duration'] if shown['duration'] else None\n", 'after':"    observation_seconds = skill['window_seconds']\n    subtotal['window_dps'] = subtotal['window_damage'] / observation_seconds if observation_seconds else None\n"},
 {'path':'rouge/uncertain_sources.py', 'before':"    subtotal['window_hps']=subtotal['window_healing']/shown['duration'] if shown['duration'] else None\n", 'after':"    observation_seconds=skill['window_seconds']\n    subtotal['window_hps']=subtotal['window_healing']/observation_seconds if observation_seconds else None\n"},
]
current = {}
for row in local:
    if row['path'] not in current:
        current[row['path']] = (ROOT / row['path']).read_bytes()
checks = []
for path, raw in current.items():
    before = raw.decode('utf-8')
    newline = '\r\n' if '\r\n' in before else '\n'
    after = before
    rows = [row for row in local if row['path'] == path]
    for row in rows:
        a = row['before'].replace('\n', newline)
        b = row['after'].replace('\n', newline)
        assert after.count(a) == 1, (path, 'unique-before')
        after = after.replace(a, b, 1)
    inverse = after
    for row in reversed(rows):
        a = row['before'].replace('\n', newline)
        b = row['after'].replace('\n', newline)
        assert inverse.count(b) == 1, (path, 'unique-after')
        inverse = inverse.replace(b, a, 1)
    assert inverse.encode('utf-8') == raw
    old_ast = ast.parse(before)
    new_ast = ast.parse(after)
    compile(new_ast, path, 'exec')
    old_functions = {n.name:ast.dump(n, include_attributes=False) for n in old_ast.body if isinstance(n,ast.FunctionDef)}
    new_functions = {n.name:ast.dump(n, include_attributes=False) for n in new_ast.body if isinstance(n,ast.FunctionDef)}
    changed = [name for name in old_functions if old_functions[name] != new_functions[name]]
    if path.endswith('operator_engine.py'):
        old_class = next(n for n in old_ast.body if isinstance(n, ast.ClassDef) and n.name=='Combat')
        new_class = next(n for n in new_ast.body if isinstance(n, ast.ClassDef) and n.name=='Combat')
        old_methods = {n.name:ast.dump(n, include_attributes=False) for n in old_class.body if isinstance(n,ast.FunctionDef)}
        new_methods = {n.name:ast.dump(n, include_attributes=False) for n in new_class.body if isinstance(n,ast.FunctionDef)}
        changed = [name for name in old_methods if old_methods[name] != new_methods[name]]
        assert changed == ['calculate']
        assert ast.dump(next(n for n in old_class.body if isinstance(n,ast.FunctionDef) and n.name=='plan'),include_attributes=False) == ast.dump(next(n for n in new_class.body if isinstance(n,ast.FunctionDef) and n.name=='plan'),include_attributes=False)
    elif path.endswith('estimate.py'):
        assert changed == ['build_estimate']
    else:
        assert changed == ['mask_pending_damage', 'mask_pending_healing']
    checks.append({'path':path,'original_sha256':SHA(raw),'candidate_source_sha256':SHA(after.encode()),'original_bytes':len(raw),'candidate_bytes':len(after.encode()),'newline':repr(newline),'local_transport_count':len(rows),'inverse_byte_exact':True,'compile_only':True,'changed_functions':changed})

catalog = json.loads((ROOT/'rouge/data/catalog.json').read_text())
base = {'operator':'char_1041_angel2','skill':1,'elite':2,'level':1,'skill_rank':7,
        'trust':0,'potential':1,'base_attack':1000,'enemy_defense':0,'enemy_resistance':0,
        'timing_mode':'frames'}
fixtures=[]
for window in (5,60):
    for travel in (0,20):
        fixtures.append({'id':f'angel-s1-window{window}-travel{travel}','source':{**base,'window_seconds':window,'timing':{'windup_frames':0,'recovery_frames':0,'projectile_travel_seconds':travel}},'required_original_observation':True})
for op,n in [('char_1041_angel2',2),('char_1041_angel2',3),('char_1015_aglna2',3),('char_1035_wisdel',3),('mechanist',1),('kaltsit',2)]:
    s={**base,'operator':op,'skill':n,'window_seconds':60,'timing':{'windup_frames':0,'recovery_frames':0,'projectile_travel_seconds':20}}
    if op=='char_1041_angel2' and n==3:s['delivery_coordinate']=False
    fixtures.append({'id':f'{op}-s{n}-window60-travel20','source':s,'required_original_observation':False})
for mode in ('frames','continuous'):
    fixtures.append({'id':f'kaltsit-s2-friendly-empty-enemy-{mode}','source':{**base,'operator':'kaltsit','skill':2,'window_seconds':60,'healing_targets':1,'timing_mode':mode,'timing':{'windup_frames':0,'recovery_frames':0,'target_windows':[]}},'required_original_observation':False})
for f in fixtures:
    p=catalog['operators'][f['source']['operator']]
    assert len(p['phases'])>2 and p['phases'][2]['max_level']>=1
    assert len(p['skills'])>=f['source']['skill']
    assert len(p['skills'][f['source']['skill']-1]['levels'])>=7
    f['catalog_qualification']={'known_operator':True,'phase':2,'within_public_level_bound':True,'rank_index':6,'duration_type':p['skills'][f['source']['skill']-1]['levels'][6]['duration_type']}

inputs={'kind':'ROOT_ONLY_113_ORIGINAL_PUBLIC_API_INPUT_PLAN','observation_only':True,'product_pass':False,'root_original_results':None,'future_actual110_source_guard_sha256':None,'fixtures':fixtures,'measurement_fields':['full result','three full texts','whole caller before/after','estimate.skill duration/phase/cycle/SP','window requested vs metric','component hit times','all report sections'],'producer_scope':'public JSON numerical API inputs, not OCR or private run data'}
(OUT/'public-inputs.json').write_text(json.dumps(inputs,ensure_ascii=False,indent=2)+'\n')
(OUT/'exact-local-transports.json').write_text(json.dumps({'kind':'INACTIVE_113_SOURCE_ONLY_LOCAL_PROPOSAL','apply_ready':False,'future_actual110_guard_sha256':None,'future_actual113_original_receipt_sha256':None,'product_paths':[str(p) for p in current],'local_transports':local,'author_checks':checks},ensure_ascii=False,indent=2)+'\n')
source_paths=['rouge/operator_engine.py','rouge/estimate.py','rouge/uncertain_sources.py','rouge/damage.py','rouge/reporting.py','rouge/timing.py','rouge/catalog.py','rouge/data/catalog.json','rouge/data/operator-profiles.json']
source_map={p:{'bytes':len((ROOT/p).read_bytes()),'sha256':SHA((ROOT/p).read_bytes())} for p in source_paths}
(OUT/'author-source-check.json').write_text(json.dumps({'kind':'SOURCE_ONLY_NO_PROJECT_EXECUTION','project_or_tests_or_helper_executed':False,'runtime_completed':False,'observed_source_map':source_map,'future_actual110_guard':None,'compile_only':True,'checks':checks,'test_method_count':sum(isinstance(n,ast.FunctionDef) and n.name.startswith('test_') for n in ast.walk(ast.parse((OUT/'test_ammo_observation_window_113.py').read_text())))},ensure_ascii=False,indent=2)+'\n')
compile(ast.parse((OUT/'test_ammo_observation_window_113.py').read_text()),str(OUT/'test_ammo_observation_window_113.py'),'exec')
print(json.dumps({'local_transports':len(local),'product_files':len(current),'public_input_count':len(fixtures),'required_original_grid':4,'test_methods':16,'compile_only':True,'project_exec':False}))
