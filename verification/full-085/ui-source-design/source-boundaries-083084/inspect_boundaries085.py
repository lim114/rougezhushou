"""Static source/control boundary notes only; no production imports or calls."""
import ast
import hashlib
import json
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=Path('/workspace/rougezhushou')
COMMIT='b5a40f30683bfc0945decaabbd4db5914c28427f'
sources={}
records=[]
for name in ('rouge/operator_engine.py','rouge/operator_options.py','rouge/app.py',
             'rouge/damage.py','rouge/enemy_environment.py','rouge/haruka_healing_reference.py'):
    data=subprocess.check_output(['git','show',f'{COMMIT}:{name}'],cwd=REPO)
    target=HERE/'source'/Path(name).name
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_bytes(data)
    sources[name]=data.decode().replace('\r\n','\n')
    ast.parse(sources[name])
    records.append({'source_commit':COMMIT,'source_path':name,'snapshot_path':str(target),
                    'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})

option_tree=ast.parse(sources['rouge/operator_options.py'])
options=next(ast.literal_eval(node.value)for node in option_tree.body
    if isinstance(node,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='OPTIONS'for t in node.targets))
selected={owner:options[owner]for owner in ('char_1042_phatm2','char_4204_mantra','char_4202_haruka')}
def skills(owner,key):return next(tuple(row[4])for row in options[owner]if row[0]==key)
assert skills('char_1042_phatm2','enemy_is_boss')==(1,2,3)
assert skills('char_1042_phatm2','enemy_in_neural_break')==(1,2,3)
assert skills('char_4204_mantra','enemy_is_boss')==(1,2)
assert skills('char_4204_mantra','enemy_in_neural_break')==(1,2)
assert skills('char_4202_haruka','haruka_repeat')==(2,)
engine=sources['rouge/operator_engine.py'];app=sources['rouge/app.py']
assert "threshold=2000 if self.s.get('enemy_is_boss') else 1000"in engine
assert "breaking_until=break_end(0) if self.s.get('enemy_in_neural_break') else -1"in engine
assert engine.count('self.neural(')==3
assert "scenario['enemy_is_boss']=record['level_type']=='BOSS'"in sources['rouge/enemy_environment.py']
assert "if owner==op and self.skill.currentData() in skills:"in app
assert "scenario[key]=widget.isChecked() if isinstance(widget,QCheckBox) else widget.value()"in app
assert "repeat=self.s.get('haruka_repeat',False)"in engine
assert "if repeat:mode='infinite';duration=window if window is not None else 30"in engine

def excerpt(text,start,end):
    first=text.index(start);last=text.index(end,first)+len(end)
    return text[first:last]

catalog_data=subprocess.check_output(['git','show',f'{COMMIT}:rouge/data/catalog.json'],cwd=REPO)
catalog=json.loads(catalog_data)['operators']
profiles={owner:{'id':owner,'name':catalog[owner]['name'],
    'skill_unlocks':[{'number':n,'skill_id':skill['id'],'unlock_elite':skill['unlock_elite']}
        for n,skill in enumerate(catalog[owner]['skills'],1)],
    'modules':[{key:mod[key]for key in ('id','name','unlock_elite','unlock_level')}
        for mod in catalog[owner]['modules']]}
    for owner in selected}
receipt={'status':'STATIC_BOUNDARIES_PASS_FINAL_SECTION_SCOPE_PENDING',
    'baseline_root_commit':COMMIT,'production_snapshots':records,
    'public_catalog_source':{'source_path':'rouge/data/catalog.json','git_commit':COMMIT,
        'bytes':len(catalog_data),'sha256':hashlib.sha256(catalog_data).hexdigest()},
    'actual_options':selected,'public_profiles':profiles,
    'section83':{
        'real_checkbox_skills':{'char_1042_phatm2':[1,2,3],'char_4204_mantra':[1,2]},
        'mantra_S3':'Both booleans are absent from the genuine S3 serializer; the unconditional postmodifier neural call still consumes scenario defaults and validates the threshold. UI absence does not imply API inactivity.',
        'selected_enemy':'Public identity processing overwrites enemy_is_boss before the proposed text guard; raw Qt scenario stores the actual bool checkbox separately. Any future fixed-target proof must also inspect the processed enemy resolution.',
        'manual_inputs':'Only genuine True/False checkbox values, visible source-defined numeric controls and readonly cultivation. Strings, null and containers remain separate API regressions.',
        'unknowns_retained':['S1 attachment and same-hit order','S3 secondary clock',
            'incoming attack timestamps','bait deployment snapshots','River periodic scheduling and active phase masks']},
    'section84':{
        'real_checkbox_skills':[2],
        'consumer':'Only non-normal Haruka S2 reads haruka_repeat. S1/S3 omit the key in the real serializer, and normal plans ignore it.',
        'qualification':'Existing elite/rank/skill errors precede the proposed end-of-evaluation guard. E0 cannot select S2 through the actual skill combo.',
        'unknowns_retained':['repeat activation history','native target composition','friendly acquisition clock',
            'bubble/levitate event placement and snapshots'],
        'prior_080':'All original 432 Haruka actual cases remain byte-preserved; the 084 scope is not finalized and no new case is claimed.'},
    'consumer_excerpts':{
        'neural':excerpt(engine,'    def neural(','        return burst_times'),
        'mantra_postmodifier':excerpt(engine,"        if op=='char_4204_mantra':\n            # Damage-dependent",'        for c in components:'),
        'haruka_repeat':excerpt(engine,"        elif op=='char_4202_haruka':",'                from .haruka_healing_reference import reference'),
        'Qt_serializer':excerpt(app,'        for owner,key,skills,widget in self.model_option_widgets:\n            if owner==op','        state=self.current_operator_state()'),
        'identity_override':excerpt(sources['rouge/enemy_environment.py'],'    # Identity-derived state wins',"    scenario['_run_damage_factor']=enemy['damage_factor']")},
    'application_API_calls':0,'formatter_calls':0,'Qt_executed':False,'Wine_executed':False,
    'final_public_package_created':False,'final_085_preflight_executed':False,
    'ready_for_actual_execution':False}
target=HERE/'source-control-boundaries085.json'
target.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':receipt['status'],'production_snapshots':len(records),
    'notes_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'application_API_calls':0}))
