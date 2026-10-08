"""Only source hashes and static bindings; no calculation or project imports."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path('/workspace/rougezhushou')
OUT=Path('/workspace/.continuation/p2-orchid-boolean-consumer-085-independent-source')
BASE='b5a40f30683bfc0945decaabbd4db5914c28427f'
GAME='a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
OP='char_1048_orchd2'
MOD='uniequip_002_orchd2'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def write(name,value):(OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

source_files=[];originals={}
for name,path,expected in (
 ('character_table',ROOT/'.cache/p2-s1-binding/character_table.json','68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697'),
 ('skill_table',ROOT/'.cache/p2-s1-binding/skill_table.json','86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca'),
 ('battle_equip_table',Path('/workspace/.continuation/p2-after-070-source-audit/originals/battle_equip_table.json'),'006687f201a823abf31c6a1c57b2269099bd3ea375c2ec3ae5595cc98a1ec460'),
 ('uniequip_table',Path('/workspace/.continuation/p2-after-070-source-audit/originals/uniequip_table.json'),'b508483cc87c03d8313f4dd8dfc1b9195bc50385a8dfec51d17e657cb26ffad9')):
 raw=path.read_bytes();assert sha(raw)==expected
 originals[name]=json.loads(raw)
 source_files.append({'table':name,'path':str(path),'bytes':len(raw),'sha256':sha(raw),'game_commit':GAME})

fixed={}
for name in ('rouge/data/catalog.json','rouge/operator_engine.py','rouge/operator_options.py','rouge/app.py',
             'rouge/damage.py','rouge/catalog.py','rouge/gnosis_module_reference.py'):
 raw=subprocess.check_output(['git','-C',str(ROOT),'show',BASE+':'+name])
 dest=OUT/'fixed-current'/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
 fixed[name]={'bytes':len(raw),'sha256':sha(raw),'git_blob':subprocess.check_output(['git','-C',str(ROOT),'rev-parse',BASE+':'+name]).decode().strip()}
cat=json.loads((OUT/'fixed-current/rouge/data/catalog.json').read_bytes())
p=cat['operators'][OP];char=originals['character_table'][OP]
write('original-character-orchid.json',char)
skills={}
rank_rows=[]
for i,binding in enumerate(char['skills']):
 sid=binding['skillId'];source=originals['skill_table'][sid];skills[sid]=source
 norm=p['skills'][i];assert norm['id']==sid and norm['unlock_elite']==int(binding['unlockCond']['phase'][-1])
 assert len(norm['levels'])==len(source['levels'])==10
 for j,(n,r) in enumerate(zip(norm['levels'],source['levels'])):
  assert n['values']=={b['key']:b['value'] for b in r['blackboard']}
  assert n['name']==r['name'] and n['description']==r['description'] and n['duration']==r['duration']
  rank_rows.append({'selector':f'skill_table.{sid}.levels[{j}]','skill':i+1,'rank':j+1,'normalized_blackboard_name_description_duration_equal':True})
write('original-skills-orchid.json',skills)
for i,talent in enumerate(char['talents']):
 named=[c for c in talent['candidates'] if c['name'] is not None]
 assert len(p['talents'][i])==len(named)
 for n,r in zip(p['talents'][i],named):
  assert n['phase']==int(r['unlockCondition']['phase'][-1]) and n['level']==r['unlockCondition']['level']
  assert n['potential_rank']==r['requiredPotentialRank'] and n['name']==r['name'] and n['description']==r['description']
  assert n['values']=={b['key']:b['value'] for b in r['blackboard']}
module=next(m for m in p['modules'] if m['id']==MOD)
raw_module=originals['battle_equip_table'][MOD];equip=originals['uniequip_table']['equipDict'][MOD]
assert module['unlock_elite']==2 and module['unlock_level']==60
assert equip['charId']==OP and equip['unlockEvolvePhase']=='PHASE_2' and equip['unlockLevel']==60
for n,r in zip(module['levels'],raw_module['phases']):assert n['parts']==r['parts']
write('original-module-orchid.json',{'equip_selector':'uniequip_table.equipDict.'+MOD,'equip_record':equip,
 'battle_selector':'battle_equip_table.'+MOD,'battle_record':raw_module})

engine=(OUT/'fixed-current/rouge/operator_engine.py').read_text()
tree=ast.parse(engine)
fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='selected_talents')
helper=ast.get_source_segment(engine,fn)
(OUT/'selected_talents.fixed.py').write_text(helper+'\n',encoding='utf-8')
assert "if '翔虫机动' in self.tv:" in engine and "if self.s.get('near_previous_deployment')" in engine
app=(OUT/'fixed-current/rouge/app.py').read_text()
assert 'widget=QCheckBox(label);widget.setChecked(default)' in app
assert 'scenario[key]=widget.isChecked() if isinstance(widget,QCheckBox) else widget.value()' in app
option_tree=ast.parse((OUT/'fixed-current/rouge/operator_options.py').read_text())
assignment=next(n for n in option_tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='OPTIONS' for t in n.targets))
options=ast.literal_eval(assignment.value)
chosen=[dict(zip(('key','label','default','maximum','skills'),x)) for x in options[OP]
 if x[0] in ('near_previous_deployment','double_charge')]
assert chosen[0]['default'] is False and chosen[0]['skills']==(1,2,3)
assert chosen[1]['default'] is True and chosen[1]['skills']==(1,)
write('source-receipt085.json',{'status':'passed_readonly_original_and_static_consumer_closure',
 'product_commit':BASE,'game_commit':GAME,'operator':OP,'raw_name':char['name'],'module_id':MOD,
 'fresh_original_files':source_files,'fixed_public_files':fixed,'skills_checked':rank_rows,
 'base_talent_groups':len(char['talents']),'complete_raw_named_and_hidden_talents_retained':True,
 'named_base_candidates_checked':sum(len(x) for x in p['talents']),
 'condition_qualification':{'actual_selected_talents_source':'selected_talents.fixed.py',
  'helper_executed':False,'static_algorithm':'phase/level/potential eligibility selects lastqualified base candidate; eligible moduleparts select sameindex qualified candidates excluding isToken; preserve named identity under sameindex1/prefab1 moduleoverlays.',
  'base_named_identity':'character_table.char_1048_orchd2.talents[1].candidates[0..1], prefabKey1',
  'E0':'No named 翔虫机动 selected; near field inactive',
  'E1L1':'Named selected; atk0.10 and atk_duration30',
  'E2L1':'Named selected; atk0.15 and atk_duration30',
  'module_stages2and3_E2L60':'Same named talent index1/prefab1; atk0.20 and atk_duration30. Separate index3/null name only carries respawn_time−17/−18; never use it as near-condition identity.',
  'current_consumer':'operator_engine.py211-219 initialization; same selectedtalent presence applies allskills and normal plans; source is initialized once per Combat, not an observed live30second deployment clock.',
  'guard_requirement':'Use actual selected_talents helper on effective preparedscenario and named identity, not justelite. Do not expand E0/S2S3-doublecharge inactive domain.'},
 'Qt_producer':{'options':chosen,'real_creation':'app.py665-666 QCheckBox frombooldefault','owner_skill_visibility':'app.py968-969',
  'owner_skill_serialization':'app.py1035-1037 widget.isChecked()','GUI_executed':False},
 'later_error_priority':{'candidate_location':'damage._evaluate_damage_once afterbuild_report320 beforereturn321',
  'already_run':'Cultivation/skill/module validation, run/enemy/relic preparation, engine, charge/timing/rune/finishers, report all finish before candidate guard.',
  'scope':'near_previous_deployment text only when ownerOrchid and actualhelper selects named 翔虫机动. No double_charge repair inthissection.',
  'actual_execution_validation':'Author andformal reviewer later; thissource receipt doesnot claimAPI behavior.'},
 'mechanics_unchanged':['30second raw duration not converted to a new clock','Atk composition/placement/range/retreat/nativeattachment remain existing scope','Doublechargearrow/resource/clock contract not rewritten'],
 'unknowns':['Actual deployment location/30secondcoverage/skillclock and currenthotupdate','Actual arrow/charge consumption and endphase','Account/runcultivation availability beyond existing calculator eligibility'],
 'restart_conditions':'Mechanics expansion needs matched-version native attachment/actual placementcoverage/skillclock and composition evidence; accepted near boolean remains an offline scenario declaration.',
 'new_API_calls':0,'new_tests':0,'selected_talents_runtime_calls':0,'GUI_executed':False,'Wine_executed':False,'tracked_edits':False,
 'preparation_diagnostics':[{'kind':'readonly_wrong_raw_path','missing':'/workspace/.cache/p2-s1-binding/character_table.json','corrected_via_rg':'/workspace/rougezhushou/.cache/p2-s1-binding/character_table.json','raw_source_reconstructed':False},
  {'kind':'readonly_guessed_test_paths','wrong':['test_shu_profession_input_types.py','test_redeploy_parameters.py'],'corrected_via_fixed_ls_tree':['test_shu_profession_text_input.py','test_orchid_redeploy_reference.py'],'tests_executed':0}]})
print(json.dumps({'source_passed':True,'rank_checks':len(rank_rows),'new_API_calls':0,'receipt_sha256':sha((OUT/'source-receipt085.json').read_bytes())}))
