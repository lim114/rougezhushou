from pathlib import Path
import sys,json,hashlib,datetime,ast
base=Path(__file__).parent;root=Path('/workspace/rougezhushou');sys.path.insert(0,str(base/'baseline'))
from rouge.catalog import catalog
from rouge.operator_engine import selected_talents
from rouge.operator_options import OPTIONS
commit='a550f5e048bb94e7cdefc6eb97a4091f0c4c7add';sources={};raws={}
for name,expected in [('character_table.json','68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697'),('skill_table.json','86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca')]:
 f=root/'.cache/p2-s1-binding'/name;raw=f.read_bytes();sha=hashlib.sha256(raw).hexdigest();assert sha==expected
 raws[name]=json.loads(raw);sources[name]={'sha256':sha,'bytes':len(raw),'current_cache_rehashed':True,'url':f'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/{commit}/zh_CN/gamedata/excel/{name}'}
p=catalog()['operators']['char_2025_shu'];raw_char=raws['character_table.json']['char_2025_shu'];raw_talent=raw_char['talents'][1]['candidates'][0]
assert len(raw_char['talents'][1]['candidates'])==1
norm=p['talents'][1][0];assert len(p['talents'][1])==1
values={v['key']:v['value'] for v in raw_talent['blackboard']}
assert values==norm['values'];assert raw_talent['name']==norm['name'] and raw_talent['description']==norm['description']
assert int(raw_talent['unlockCondition']['phase'][-1])==norm['phase']==2
assert raw_talent['unlockCondition']['level']==norm['level']==1
assert raw_talent['requiredPotentialRank']==norm['potential_rank']==0
assert values['max_hp']==.12 and values['attack_speed']==12 and values['atk']==.12 and values['interval']==4 and values['sp']==1
skill_records=[]
for n,skill in enumerate(p['skills']):
 orig=raws['skill_table.json'][skill['id']]['levels'];assert len(orig)==len(skill['levels'])==10
 assert int(raw_char['skills'][n]['unlockCond']['phase'][-1])==skill['unlock_elite']
 for i,(o,s) in enumerate(zip(orig,skill['levels'])):
  numeric={b['key']:b['value'] for b in o['blackboard']};assert numeric==s['values']
  assert o['description']==s['description'];assert o['duration']==s['duration'];assert o['spData']['spType']==s['sp_type'];assert o['spData']['spCost']==s['sp_cost'];assert o['spData']['initSp']==s['initial_sp']
  skill_records.append({'selector':f"skill_table.{skill['id']}.levels[{i}]",'raw_level':o,'normalized_level':s,
   'verified_projected_fields':['all numeric blackboard key/value pairs','description','duration','spData.spType','spData.spCost','spData.initSp'],'claims_full_dictionary_identity':False})
selected=[]
for elite in (0,1,2):
 for potential in (1,5,6):
  scenario={'operator':'char_2025_shu','elite':elite,'potential':potential};talents,parts=selected_talents(p,scenario)
  selected.append({'scenario':scenario,'selected_talents':talents,'selected_parts':parts,'four_seasons_selected':any(t['name']=='天有四时' for t in talents)})
for level in (59,60,90):
 for stage in (1,2,3):
  scenario={'operator':'char_2025_shu','elite':2,'level':level,'potential':6,'module_id':'uniequip_002_shu','module_level':stage};talents,parts=selected_talents(p,scenario)
  selected.append({'scenario':scenario,'selected_talents':talents,'selected_parts':parts,'four_seasons_selected':any(t['name']=='天有四时' for t in talents)})
assert all(row['four_seasons_selected']==(row['scenario']['elite']==2) for row in selected)
module_index1=[]
for module in p['modules']:
 for stage in module['levels']:
  for part in stage['parts']:
   for c in (part.get('addOrOverrideTalentDataBundle') or {}).get('candidates') or []:
    if c.get('talentIndex')==1:module_index1.append({'module':module['id'],'stage':stage['level'],'candidate':c})
assert not module_index1
files={}
for name in ['rouge/operator_engine.py','rouge/operator_options.py','rouge/app.py','rouge/damage.py','rouge/attribute_limits.py','rouge/data/catalog.json']:
 f=base/'baseline'/name;files[name]={'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'bytes':f.stat().st_size}
options=[list(x) for x in OPTIONS['char_2025_shu'] if x[0] in ('three_professions','three_same_profession','four_sui')]
app=(base/'baseline/rouge/app.py').read_text();assert 'widget=QCheckBox(label);widget.setChecked(default)' in app
assert 'scenario[key]=widget.isChecked() if isinstance(widget,QCheckBox) else widget.value()' in app
search_patterns=('char_2025_shu','shu_t_','天有四时');native=[];hits=[]
for f in sorted((root/'.cache/research').rglob('*')):
 if f.is_file() and f.suffix in ('.json','.txt','.md'):
  raw=f.read_bytes();native.append({'path':str(f.relative_to(root)),'sha256':hashlib.sha256(raw).hexdigest(),'bytes':len(raw)})
  text=raw.decode('utf-8',errors='replace');found=[key for key in search_patterns if key in text]
  if found:hits.append({'path':str(f.relative_to(root)),'matched':found})
receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frozen_repository_commit':'0e0d098e8bc8444cd74fb74f32754cc0ff78ecfb','source_commit':commit,
 'raw_sources':sources,'source_files':files,'raw_character_talent_selector':'character_table.char_2025_shu.talents[1].candidates[0]',
 'raw_talent_candidate_complete':raw_talent,'normalized_talent_candidate':norm,
 'talent_verified_projected_fields':['name','description','unlockCondition.phase','unlockCondition.level','requiredPotentialRank','all numeric blackboard key/value pairs'],
 'claims_full_character_or_talent_schema_identity':False,'all_30_skill_ranks':skill_records,'selected_talent_cases':selected,
 'module_basis':'current frozen normalized modules, not fresh downloaded original module table','module_index1_overlay_candidates':module_index1,
 'original_predicates':{'three_professions':'场上有三名不同职业干员时所有干员生命上限+12%','three_same_profession':'三名相同职业干员时所有干员攻击速度+12',
  'four_sui':'编队中有四名【岁】干员时所有干员攻击力+12%且4秒获得1点技力'},
 'actual_field_consumers':{'three_professions':"Combat.apply_self_talents if owner==Shu and truthy raw field then hp_bonus+=selected talent max_hp; self.stats['hp']=attributes['hp']*(1+hp_bonus)",
 'three_same_profession':"same selected owner/talent truthy raw field then as_bonus+=attack_speed; base_speed_reference=attributes['attack_speed']+as_bonus; existing effective timing speed/normal_interval applied",
 'scope':'original description global operators, this public calculation models selected Shu only; sibling fields in other owner ignored, not a proof actual squad qualifies'},
 'gui_contract':{'option_rows':options,'factory':'bool default constructs QCheckBox, setChecked(default)','producer':'owned applicable skill widget .isChecked() generates bool','default':False,'skills':[1,2,3],'text_parser_added':False,'actual_gui_not_run':True},
 'preserved_four_sui_062_contract':"if selected 天有四时 and raw four_sui str then original ValueError('four_sui 不接受文本条件；请使用布尔值。')",
 'preserved_section060_periodic_scope':'qualified four_sui keeps static ATK and original4sec/1SP parameters; first_tick/origin/reset/blocked/actual pulse times unknown, no uniform natural SP .25',
 'native_search':{'scope':'current textual .cache/research receipts only, not full installed process/native packages','patterns':search_patterns,'files':native,'matches':hits},
 'not_inferred':['squad/field profession counts from actual game state','owner/global coverage or attachment callbacks','predicate transition/reset order','multi-source HP/AS stack identity','periodic SP firsttick/reset/credit','hidden talent or module attachment','random processes'],
 'no_tracked_edits':True,'no_external_game_operations':True,'no_draft_or_patch_created':True}
(base/'source-receipt068.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'hashes_verified':True,'talent_projection_fields':len(receipt['talent_verified_projected_fields']),'full_character_schema_identity_claimed':False,'skill_ranks_checked':len(skill_records),'selected_talent_cases':len(selected),'native_receipts_scanned':len(native),'native_hits':hits},ensure_ascii=False))
