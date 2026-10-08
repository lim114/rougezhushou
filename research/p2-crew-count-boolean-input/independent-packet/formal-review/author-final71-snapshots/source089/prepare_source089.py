"""Freeze only static source facts for the authorized five RunState groups."""
import ast,hashlib,json,subprocess
from pathlib import Path
OUT=Path(__file__).resolve().parent
REPO=Path('/workspace/rougezhushou');BASE='0f27027e7e1f49c08f298706b599e310e299238b'
def sha(data):return hashlib.sha256(data).hexdigest()
def write(name,value):
 p=OUT/name
 with p.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
 return p
def main():
 paths=subprocess.check_output(['git','-C',str(REPO),'ls-tree','-r','--name-only',BASE,'rouge']).decode().splitlines()
 paths=[p for p in paths if p.endswith(('.py','.json'))];expected={}
 for name in paths:
  blob=subprocess.check_output(['git','-C',str(REPO),'show',BASE+':'+name])
  expected[name]={'bytes':len(blob),'sha256':sha(blob)}
 names=('rouge/run_state.py','rouge/run_recognition.py','rouge/visual_recognition.py','rouge/app.py','rouge/catalog.py',
  'rouge/run_config.py','rouge/run_modifiers.py','rouge/recipient_state.py','rouge/relics.py','rouge/data/run-config.json')
 frozen=[];texts={}
 for name in names:
  blob=subprocess.check_output(['git','-C',str(REPO),'show',BASE+':'+name]);assert (REPO/name).read_bytes()==blob,name
  target=OUT/'frozen'/name;target.parent.mkdir(parents=True,exist_ok=True)
  with target.open('xb') as f:f.write(blob)
  if name.endswith('.py'):ast.parse(blob.decode())
  texts[name]=blob.decode();frozen.append({'path':name,'source_path':str(target),**expected[name]})
 state=texts['rouge/run_state.py'];recognition=texts['rouge/run_recognition.py'];app=texts['rouge/app.py']
 assert "if crew is not None and len({m['id'] for m in members})==crew:" in state
 assert "full_crew=type(crew) is int and len(incoming)==crew" in state
 assert "state['crew_count']=crew" in state
 assert "values={int(t['text']) for t in texts if valid(t)}" in recognition
 assert "if member and not member.get('present',True):member=None" in app
 assert 'crew_count' not in texts['rouge/run_modifiers.py']
 contexts=[]
 ranges={'rouge/run_state.py':[(13,29),(50,65),(83,88),(245,267),(372,378),(435,448),(563,568),(582,590)],
  'rouge/run_recognition.py':[(68,96),(122,128),(184,191)],'rouge/visual_recognition.py':[(132,141)],
  'rouge/app.py':[(739,742),(767,789),(806,822),(887,897),(1038,1067)],
  'rouge/catalog.py':[(28,38),(49,57)],'rouge/run_modifiers.py':[(4,42),(43,58)]}
 for name,sections in ranges.items():
  lines=texts[name].splitlines();contexts.append({'path':name,'ranges':[{'start':a,'end':b,'lines':lines[a-1:b]} for a,b in sections]})
 config=json.loads(texts['rouge/data/run-config.json'])
 static=write('static-source-facts089.json',{'status':'SOURCE_CONFIRMED_REPRO_AUTHORIZED_NOT_EXECUTED','base_commit':BASE,
  'crew_semantics':'Observed decimal integer crew count orNone; no actual-game population upper bound inferred from OCR format.',
  'storage_schema':'reset None; savedload only checks operators/relics dictionaries then update; apply stores any nonNone crew without type validation.',
  'boolean_collision':'False andempty unique roster meet0==False;True andone unique roster meet1==True and may mark other present members departed.',
  'same_class_strict_counter':"restore_origin_discovery_buffs requires type(crew) is int for complete crew qualification.",
  'UI_producer':'run_recognition near_number converts decimal OCR toint orNone; app.apply_run_observation forwards observed toRunState.apply. No crew checkbox/spinbox manual producer found in actual app.',
  'numeric_vs_display':'Count is not a direct numeric multiplier; corrupt present status affects actual roster choices/current_operator_state account fallback, cultivation/skill/buff scenario inputs. This is a static downstream path, not a measured damage/attribute delta.',
  'fixed_squad_source':{k:config[k] for k in ('commit','source_url','source_sha256')},
  'squad_independence':'Fixedsquad identity/effect verification remains inrun_config/run_modifiers; crew does not derive squad or auto-add preset starting members.',
  'load_boundary':'Existing saved corrupt presence cannot safely be repaired from count alone; no rejoin/receipt/real-game departure mechanics invented.',
  'other_types_scope':'This lead isolates boolean aliases only; no broad new policy forfloat/string/negative/large counts proposed.',
  'source_excerpts':contexts,'new_API_calls':0,'project_calls':0,'tests':0,'Qt':0,'Wine':0,'tracked_edits':0})
 write('fixed-public-source-bindings089.json',{'base_commit':BASE,'repo':str(REPO),'files':expected,'frozen_named_sources':frozen,
   'static_facts_path':str(static),'RunState_call_authorization':'Five isolated groups only;5constructors+5seed apply+5subject apply. No app/training/damage/recognition run.'})
 write('authorized-five-case-plan089.json',{'groups':[
  {'id':'empty-None','seed_ids':['mechanist'],'seed_crew':1,'subject_ids':[],'crew_count':None,'expected_source_departures':[]},
  {'id':'empty-False','seed_ids':['mechanist'],'seed_crew':1,'subject_ids':[],'crew_count':False,'expected_source_departures':['mechanist']},
  {'id':'empty-int0','seed_ids':['mechanist'],'seed_crew':1,'subject_ids':[],'crew_count':0,'expected_source_departures':['mechanist']},
  {'id':'one-True','seed_ids':['mechanist','char_151_myrtle'],'seed_crew':2,'subject_ids':['mechanist'],'crew_count':True,'expected_source_departures':['char_151_myrtle']},
  {'id':'one-int1','seed_ids':['mechanist','char_151_myrtle'],'seed_crew':2,'subject_ids':['mechanist'],'crew_count':1,'expected_source_departures':['char_151_myrtle']}],
  'clock':'Existing063/055 protocol uses each instance natural started_at+1 seed and+2 subject; preserve UUID/started_at and captured floats fully, no crossgroup full-tree equality.',
  'fixed_member_fields':'scope run; empty fields and skill_ranks, no P1 personalbuff fixture.',
  'actual_expected_method_counts':{'constructors':5,'seed_apply':5,'subject_apply':5},'tests':0})
 print(json.dumps({'source_preparation_pass':True,'base_commit':BASE,'bound_public_files':len(paths),'named_sources':len(names),'project_calls':0}))
if __name__=='__main__':main()
