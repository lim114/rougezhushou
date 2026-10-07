from pathlib import Path
import hashlib,json,datetime
root=Path('/workspace/rougezhushou'); base=Path(__file__).parent
commit='a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
files={};data={}
for name,sha in [('character_table.json','68e3a3b5ee0d407ce234afaa5867c6fda6379a6843c7d5317a7bbda4779f8697'),('skill_table.json','86f4aa64c785f39727edd06d6dd8a4f27f371c8e4ace5345ba0dc61dee1386ca')]:
 p=root/'.cache/p2-s1-binding'/name; raw=p.read_bytes(); actual=hashlib.sha256(raw).hexdigest();assert actual==sha
 files[name]={'sha256':actual,'bytes':len(raw),'current_cache_rehashed':True,'source_commit':commit,'url':f'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/{commit}/zh_CN/gamedata/excel/{name}'};data[name]=json.loads(raw)
p=json.loads((root/'rouge/data/catalog.json').read_bytes())['operators']['char_2025_shu']
talent=data['character_table.json']['char_2025_shu']['talents'][1]['candidates'][0]
values={b['key']:b['value'] for b in talent['blackboard']};assert values==p['talents'][1][0]['values']
assert talent['unlockCondition']=={'phase':'PHASE_2','level':1};assert talent['requiredPotentialRank']==0
assert values['interval']==4 and values['sp']==1 and values['atk']==.12
skills=[]
for i,s in enumerate(p['skills']):
 raw=data['skill_table.json'][s['id']]['levels']
 assert len(raw)==len(s['levels'])==10
 for j,(orig,norm) in enumerate(zip(raw,s['levels'])):
  assert orig['spData']['spType']==norm['sp_type'] and orig['spData']['spCost']==norm['sp_cost'] and orig['spData']['initSp']==norm['initial_sp']
  skills.append({'selector':f"skill_table.{s['id']}.levels[{j}].spData",'raw':orig['spData'],'normalized':{k:norm[k] for k in ('sp_type','sp_cost','initial_sp','sp_increment','max_charges')}})
patterns=('char_2025_shu','skchr_shu','shu_t_','天有四时')
scan=[];matches=[]
for q in sorted((root/'.cache/research').rglob('*')):
 if q.is_file() and q.suffix in ('.json','.txt','.md'):
  raw=q.read_bytes();scan.append({'path':str(q.relative_to(root)),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
  text=raw.decode('utf-8',errors='replace')
  hits=[s for s in patterns if s in text]
  if hits:matches.append({'path':str(q.relative_to(root)),'matched':hits})
receipt={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_commit':commit,'files':files,
 'original_selector':'character_table.char_2025_shu.talents[1].candidates[0]','original_talent':talent,
 'normalized_talent':p['talents'][1][0],'all_30_skill_rank_sp_selectors':skills,
 'qualification':{'elite':2,'level':1,'potential_rank':0,'scenario_condition':'four_sui is existing truthy condition input; not inferred from squad'},
 'native_cache_search':{'patterns':patterns,'scope':'only current .cache/research textual receipts/configuration/disassembly; not complete installed files or live process','files':scan,'matches':matches},
 'native_talent_binding_verified':False,'first_tick_seconds':None,'clock_origin':None,'reset_rule':None,'blocked_credit_rule':None,
 'not_established':['periodic credit as natural regeneration speed','first tick at deployment/activation/4 seconds','reset on activation/finish/redeploy','blocked credit bank/discard order','owner or deployment clock identity','live XLua equivalence'],
 'existing_066_scope':'only five named positive natural SP additions and profession/recipient selection; does not establish Shu periodic talent clock',
 'existing_066_report':{'path':'.cache/research/sp-attributes-066/REPORT.md','sha256':hashlib.sha256((root/'.cache/research/sp-attributes-066/REPORT.md').read_bytes()).hexdigest()},
 'changes_no_game_operation':True}
(base/'source-receipt060.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'current_source_hashes_verified':True,'skill_rank_selectors':len(skills),'searched_files':len(scan),'matches':matches,'native_binding_verified':False},ensure_ascii=False))
