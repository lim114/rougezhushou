from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from rouge import node_catalog as catalog,event_planning
from rouge.player_node_information import node_information_text
def sha(value):return sha256(value).hexdigest()
def canon(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
paths=['rouge/event_planning.py','rouge/node_catalog.py','rouge/node_rewards.py','rouge/player_node_information.py',
 'rouge/data/node-catalog.json','rouge/data/event-planning-reference.json']
before={p:sha((ROOT/p).read_bytes())for p in paths}
resource={};player={};target=None
for e in catalog.all_events(include_indirect=True)['rows']:
 player[e['id']]=sha(node_information_text({'kind':'event','record':e}).encode())
 if e['id']=='community_group_024':target=node_information_text({'kind':'event','record':e})
 for s in catalog.event_details(e['id'])['rows']:
  resource[s['key']]=sha(canon(event_planning.choice_resources(e['id'],s['key'])))
assert len(player)==38 and len(resource)==190
assert before=={p:sha((ROOT/p).read_bytes())for p in paths}
DEST=ROOT/'verification/sections/297-preparation'
assert not(DEST/'before-output-hashes.json').exists()
(DEST/'before-output-hashes.json').write_bytes((json.dumps({'kind':'ACTUAL_PRECHANGE_PUBLIC_DEFAULT_CONTEXT_OUTPUT_HASHES',
 'at_utc':datetime.now(timezone.utc).isoformat(),'source_before_after_sha256':before,'player_events':player,
 'choice_resources_scenes':resource,'actual_scene_query_count':190,'actual_player_query_count':38,
 'private_state_or_Qt_game_chat_used':False,'effect':'Baseline only; no product changes or acceptance claims.'},ensure_ascii=False,indent=2)+'\n').encode())
(DEST/'before-target-player.txt').write_bytes(target.encode())
print(json.dumps({'actual_resource_scene_queries':len(resource),'actual_player_queries':len(player),'unchanged_sources':True}))
