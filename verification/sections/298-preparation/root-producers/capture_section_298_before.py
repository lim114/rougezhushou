from pathlib import Path
from hashlib import sha256
import json,sys,types,subprocess
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
DEST=ROOT/'verification/sections/298-preparation'
PARENT='bb4927a2a2760d48882f3945b750053d7a5617fc'
import rouge
sources={}
for name in ('node_catalog','event_planning','player_node_information'):
 relative='rouge/'+name+'.py';p=DEST/'before'/relative
 raw=p.read_bytes();assert subprocess.check_output(['git','show',PARENT+':'+relative],cwd=ROOT)==raw
 module=types.ModuleType('rouge.'+name);module.__file__=str(ROOT/relative);module.__package__='rouge'
 sys.modules[module.__name__]=module;setattr(rouge,name,module)
 exec(compile(raw,str(p),'exec'),module.__dict__);sources[relative]=sha256(raw).hexdigest()
catalog=rouge.node_catalog;planning=rouge.event_planning;player=rouge.player_node_information
def canon(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
events=catalog.all_events(include_indirect=True)['rows'];resources={};players={};context_players={};target_resources={}
targets={'community_group_'+str(i).zfill(3) for i in (24,25,27,28,29,37)}
for e in events:
 entry={'kind':'event','record':e};players[e['id']]=sha256(player.node_information_text(entry).encode()).hexdigest()
 if e['id'] not in targets:
  context={'node_type':e['node_types'][0] if e['node_types'] else None,'floor':3,'entry_mode':'natural'}
  context_players[e['id']]=sha256(player.node_information_text(entry,context=context).encode()).hexdigest()
 for s in catalog.event_details(e['id'])['rows']:
  resources[s['key']]=sha256(canon(planning.choice_resources(e['id'],s['key']))).hexdigest()
  if e['id'] in targets:
   context={'node_type':e['node_types'][0],'floor':6,'entry_mode':'natural'}
   target_resources[s['key']]=planning.choice_resources(e['id'],s['key'],context)
result={'section':298,'kind':'actual_prechange_public_source_execution_no_private_state','parent':PARENT,
 'source_sha256':sources,'execution_note':'Three exact parent source modules executed with their original package identity and data location; no product mutation, tests, Qt/game/chat/private access.',
 'default_player_events':players,'non_target_natural_floor3_player_events':context_players,
 'default_choice_resources_scenes':resources,'target_natural_floor6_resources':target_resources}
p=DEST/'before-output.json';assert not p.exists();p.write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode())
print(json.dumps({'events':len(players),'non_target_explicit_context':len(context_players),'scenes':len(resources),'target_scenes':len(target_resources),'sha256':sha256(p.read_bytes()).hexdigest()}))
