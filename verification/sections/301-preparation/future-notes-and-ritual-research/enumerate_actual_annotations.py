"""Actual public choice API inventory with no UI, run or private inputs."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
from copy import deepcopy
import json
import sys

ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from rouge import node_catalog as catalog
from rouge import event_planning as planning

def pin(path):
 raw=path.read_bytes();return {'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
sources=('rouge/node_catalog.py','rouge/event_planning.py','rouge/data/node-catalog.json')
before={str(ROOT/p):pin(ROOT/p) for p in sources}
full=[];notes=[];scene_count=0;choice_count=0
events=catalog.all_events(include_indirect=True)['rows']
for summary in events:
 event=catalog._event(summary['id']);event_results=[]
 for scene in event['scenes']:
  result=planning.choice_eligibility(event['id'],scene['key'],{})
  scene_count+=1;choice_count+=len(result['rows'])
  event_results.append({'scene_key':scene['key'],'actual_API_result':result})
  by_key={row['choice_key']:row for row in result['rows']}
  for choice in scene['choices']:
   row=by_key[choice['key']]
   if row['unparsed_condition_text']:
    notes.append({'event_id':event['id'],'event_title':event['title'],'scene_key':scene['key'],
     'choice_key':choice['key'],'choice_title':choice['title'],'conditional':choice['conditional'],
     'actual_API_row':row,'complete_event':deepcopy(event),'complete_scene':deepcopy(scene),
     'complete_choice':deepcopy(choice)})
 full.append({'event_id':event['id'],'scenes':event_results})
after={str(ROOT/p):pin(ROOT/p) for p in sources}
assert before==after
assert 'rouge.app' not in sys.modules
result={'kind':'actual-public-API-annotation-inventory-not-tests-or-feature-acceptance',
 'created_at':datetime.now(timezone.utc).isoformat(),'context':{},'event_count':len(events),
 'scene_count':scene_count,'choice_count':choice_count,'unparsed_count':len(notes),'unparsed_notes':notes,
 'all_actual_scene_results':full,'source_before':before,'source_after':after,'source_unchanged':before==after,
 'Qt_tests_Git_private_game_chat_operations':False}
target=HERE/'actual-unparsed-annotations.json'
target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'output':str(target),'sha256':sha256(target.read_bytes()).hexdigest(),'bytes':target.stat().st_size,
 'counts':{k:result[k] for k in ('event_count','scene_count','choice_count','unparsed_count')},
 'notes':[{k:r[k] for k in ('event_id','event_title','scene_key','choice_key','choice_title','conditional')} for r in notes]},ensure_ascii=False,indent=2))
