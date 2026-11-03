"""Root's current insertion/source verification; no damage/API evaluations."""
import ast,hashlib,json,subprocess,sys,textwrap
from pathlib import Path
root=Path('/workspace/rougezhushou');src=Path('/workspace/.continuation/p2-orchid-near-text-085');ind=Path('/workspace/.continuation/p2-orchid-near-text-085-independent');sha=lambda b:hashlib.sha256(b).hexdigest()
assert subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip()=='codex/p2-development'
guard=(src/'guard085-crlf.txt').read_bytes();assert sha(guard)=='b9de57946088ba471f239ee3c2d993ce0ede3b22079fb6904d753508f5f25ca2'
damage=(root/'rouge/damage.py').read_bytes();assert damage.count(guard)==1 and damage.count(b'\n')==damage.count(b'\r\n')
prior=damage.replace(guard,b'',1);assert sha(prior)=='d02b8571542d08a63a56f08e6b129e9dfb43a9047595e77aabb54a3e0d04de6b'
function=next(n for n in ast.parse(damage.decode()).body if isinstance(n,ast.FunctionDef) and n.name=='_evaluate_damage_once')
assert isinstance(function.body[-1],ast.Return) and ast.dump(function.body[-2],include_attributes=False)==ast.dump(ast.parse(textwrap.dedent(guard.decode())).body[0],include_attributes=False)
fixed={}
for name in ('rouge/operator_engine.py','rouge/data/catalog.json','rouge/operator_options.py','rouge/app.py','rouge/reporting.py','rouge/estimate.py','rouge/data/relic-mechanics.json','rouge/relics.py'):
 b=(root/name).read_bytes();old=subprocess.check_output(['git','show','b5a40f30683bfc0945decaabbd4db5914c28427f:'+name],cwd=root);assert b==old;fixed[name]=sha(b)
test=(root/'tests/test_orchid_near_text_input.py').read_bytes();assert sha(test)=='8fd8cdaf383ab54945404ad33c5f610c2fc2e4bb018800b1a8bed3193a0dce86'
for module in ('tests.test_neural_condition_text_input','tests.test_haruka_repeat_text_input','tests.test_orchid_near_text_input'):
 assert '"'+module+'"' in (root/'scripts/verify_cloud.py').read_text()
source=json.loads((src/'source-only/source-receipt085.json').read_text());raw={}
for proof in source['fresh_original_files']:
 b=Path(proof['path']).read_bytes();assert sha(b)==proof['sha256'] and len(b)==proof['bytes'];raw[proof['table']]=json.loads(b)
sys.path.insert(0,str(root))
from rouge.catalog import catalog
from rouge.operator_engine import selected_talents
from rouge.operator_options import OPTIONS
op='char_1048_orchd2';p=catalog()['operators'][op];char=raw['character_table'][op];ranks=0
assert p['id']==op and p['name']==char['name'] and len(p['skills'])==len(char['skills'])==3
for i,skill in enumerate(p['skills']):
 assert skill['id']==char['skills'][i]['skillId'];originals=raw['skill_table'][skill['id']]['levels'];assert len(skill['levels'])==len(originals)==10
 for actual,original in zip(skill['levels'],originals):
  assert actual['values']=={row['key']:row['value'] for row in original['blackboard']};assert actual['name']==original['name'] and actual['description']==original['description'] and actual['duration']==original['duration'];ranks+=1
proof=json.loads((ind/'source-subreview/selected-helper-qualification085.json').read_text());assert proof['actual_selected_talents_calls']==9
for row in proof['rows']:
 talents,parts=selected_talents(p,row['scenario']);assert talents==row['selected_talents'] and parts==row['module_parts']
option=next(x for x in OPTIONS[op] if x[0]=='near_previous_deployment');assert option[2] is False and option[4]==(1,2,3)
app=(root/'rouge/app.py').read_text();assert 'widget=QCheckBox(label);widget.setChecked(default)' in app and 'scenario[key]=widget.isChecked() if isinstance(widget,QCheckBox) else widget.value()' in app
receipt={'passed':True,'section':85,'branch':'codex/p2-development','head_before_section_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'current_damage_sha256':sha(damage),'approved_prior84_damage_sha256':sha(prior),'all_prior83_84_bytes_preserved':True,'guard_is_final_core_step_after_report':True,'damage_crlf_preserved':True,'unchanged_current_source_files':fixed,'new_test_registered':True,'current_test_sha256':sha(test),'raw_original_files_rehashed':list(raw),'source_commit':source['game_commit'],'skill_ranks_verified':ranks,'current_actual_helper_selections':len(proof['rows']),'calculate_damage_calls':0,'native_clock_changes':False,'GUI_Wine_executed':False}
target=Path('/workspace/.continuation/root-source-085.json')
with target.open('x') as f:f.write(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:receipt[k] for k in ('passed','section','current_damage_sha256','skill_ranks_verified','current_actual_helper_selections','calculate_damage_calls')}))
