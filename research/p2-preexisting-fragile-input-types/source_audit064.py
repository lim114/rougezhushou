from pathlib import Path
import sys,json,hashlib,datetime
base=Path(__file__).parent;root=Path('/workspace/rougezhushou')
sys.path.insert(0,str(base/'baseline'))
from rouge.catalog import catalog
from rouge.operator_engine import selected_talents
commit='a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
raws={};receipt={}
for name,expected in [('character_table.json','68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697'),('skill_table.json','86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca')]:
 p=root/'.cache/p2-s1-binding'/name;raw=p.read_bytes();sha=hashlib.sha256(raw).hexdigest();assert sha==expected
 raws[name]=json.loads(raw);receipt[name]={'sha256':sha,'bytes':len(raw),'current_cache_rehashed':True,'url':f'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/{commit}/zh_CN/gamedata/excel/{name}'}
const=base/'gamedata_const.json';raw=const.read_bytes();assert hashlib.sha256(raw).hexdigest()=='216985a6185c199ee703eac1fb8c35f51ca6d45141894df9c1fd9397b6c940ee'
receipt['gamedata_const.json']={'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw),'fresh_verified_download':True,'url':f'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/{commit}/zh_CN/gamedata/excel/gamedata_const.json'}
p=catalog()['operators']['silverash'];native=raws['character_table.json']['char_1045_svash2']
assert p['id']=='char_1045_svash2' and p['profession']=='pioneer'
records=[]
for n,s in enumerate(p['skills']):
 raw=raws['skill_table.json'][s['id']]['levels']
 assert int(native['skills'][n]['unlockCond']['phase'][-1])==s['unlock_elite']
 for j,(orig,norm) in enumerate(zip(raw,s['levels'])):
  bb={row['key']:row['value'] for row in orig['blackboard']}
  assert bb==norm['values'];assert orig['description']==norm['description'];assert orig['duration']==norm['duration']
  records.append({'character_selector':f'character_table.char_1045_svash2.skills[{n}]','skill_selector':f"skill_table.{s['id']}.levels[{j}]",'raw_unlock':native['skills'][n]['unlockCond'],'normalized_unlock_elite':s['unlock_elite'],'description':orig['description'],'raw_blackboard':orig['blackboard'],'normalized_values':norm['values']})
selected=[]
for elite in (0,1,2):
 for potential in (1,5,6):
  scenario={'operator':'silverash','elite':elite,'potential':potential}
  talents,parts=selected_talents(p,scenario)
  selected.append({'scenario':scenario,'selected_talents':talents,'parts':parts,'contains_damage_scale':any('damage_scale' in t['values'] for t in talents)})
assert not any(row['contains_damage_scale'] for row in selected)
search_patterns=['char_1045_svash2','skchr_svash2_3','svash2_s_3','svash2_t_','ba.fragile']
scanned=[];matches=[]
for f in sorted((root/'.cache/research').rglob('*')):
 if f.is_file() and f.suffix in ('.json','.txt','.md'):
  data=f.read_bytes();scanned.append({'path':str(f.relative_to(root)),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
  text=data.decode('utf-8',errors='replace');hits=[x for x in search_patterns if x in text]
  if hits:matches.append({'path':str(f.relative_to(root)),'patterns':hits})
source_files={}
for name in ['rouge/damage.py','rouge/estimate.py','rouge/operator_engine.py','rouge/reporting.py','rouge/app.py','rouge/offline_scope.py','rouge/relics.py','rouge/data/catalog.json']:
 f=base/'baseline'/name;source_files[name]={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size}
out={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_commit':commit,'frozen_repository_commit':'c3ccf25d59144227dd0f8f5ca9ef6c8bf81ad8cf','raw_sources':receipt,'source_files':source_files,
 'alias_resolution':{'public_operator':'silverash','native_id':p['id'],'name':p['name'],'profession':p['profession']},
 'all_30_skill_selectors':records,'raw_talents':native['talents'],'normalized_talents':p['talents'],'selected_talent_cases':selected,
 'fragile_term':json.loads(const.read_bytes())['termDescriptionDict']['ba.fragile'],
 'execution_routes':{'public_prepare':'_prepare_damage validates skill/rank/training/skill elite before legacy _skill_damage','actual_skill':'silverash is legacy route, not Combat.calculate; _skill_damage silver S3 uses skill bb.damage_scale only when preexisting_fragile truthy','estimate_talents':'build_estimate locally selects phase/level/potential named talents; only initial SP/redeploy/defense/regen reference, no fragile value','report_talents':'mechanism_sections uses operator_engine.selected_talents; currently selected original named talents have no damage_scale key'},
 'gui_contract':{'widget':'MainWindow.fragile QCheckBox','default':True,'label':'全程计该技能脆弱（不勾选则全程未计）','visibility_condition':"operator=='silverash' and skill==3",'input_producer':"scenario['preexisting_fragile']=self.fragile.isChecked() (Python bool)",'no_text_parser_for_this_field':True,'gui_runtime_executed_this_audit':False},
 'current_math_contract':{'skill_damage_type':'physical','single_source_damage_scale':'rank1 1.15 to rank10 1.3, from original selected S3 blackboard','truthiness_gate':'raw scenario.get(preexisting_fragile,False), no type validation','all_skill_fragile_off_when_absent':True,'other_sources':'manual damage_taken of matching dtype sum to 1+values, then multiply single skill conditional damage_scale; existing formula not new gameplay proof'},
 'stacking_boundary':{'original_term_same_name_rule':'同名效果取最高','same_name_identification_from_manual_damage_taken_verified':False,'skill_vs_external_fragile_attachment_and_precedence_verified':False,'actual_first_hit_application_refresh_residual_verified':False,'do_not_change_stack_formula_in_this_candidate':True},
 'native_search':{'patterns':search_patterns,'files':scanned,'matches':matches,'scope':'current .cache/research textual receipts only; absent matching actual S3 native template/CFG not a claim of absent game implementation'},
 'no_tracked_changes':True,'no_game_or_gui_execution':True}
(base/'source-receipt064.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'raw_source_hashes_verified':True,'all_skill_selectors':len(records),'selected_talent_cases':len(selected),'native_receipt_files':len(scanned),'native_matches':matches,'skill_rank_damage_scales':[s['values']['damage_scale'] for s in p['skills'][2]['levels']]},ensure_ascii=False))
