"""Capture public default text and exact note blocks; no UI/test/state inputs."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
from copy import deepcopy
import json,re,sys
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from rouge.player_node_information import node_information_text
from rouge import node_catalog as catalog,event_planning as planning
inventory=json.loads((HERE/'actual-unparsed-annotations.json').read_bytes())
pin=lambda p:{'sha256':sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
sources=('rouge/player_node_information.py','rouge/event_planning.py','rouge/node_catalog.py','rouge/data/node-catalog.json')
before={str(ROOT/p):pin(ROOT/p) for p in sources}
texts={};rows=[]
for note in inventory['unparsed_notes']:
 event=note['complete_event'];identity=event['id']
 if identity not in texts:
  texts[identity]=node_information_text({'kind':'event','record':deepcopy(event)},context={})
 scene=note['complete_scene'];choice=note['complete_choice']
 scene_number=next(i for i,s in enumerate(event['scenes'],1) if s['key']==scene['key'])
 choice_number=next(i for i,c in enumerate(scene['choices'],1) if c['key']==choice['key'])
 scene_text=texts[identity].split('【场景 '+str(scene_number)+'】',1)[1]
 scene_text=re.split(r'\n【场景 \d+】',scene_text,1)[0]
 block=scene_text.split('选项 '+str(choice_number)+'：',1)[1]
 block=re.split(r'\n(?:选项|说明参考)[^\n]*\d+：',block,1)[0]
 row=next(r for r in planning.choice_eligibility(identity,scene['key'],{})['rows'] if r['choice_key']==choice['key'])
 rows.append({'event_id':identity,'scene_key':scene['key'],'choice_key':choice['key'],
  'conditional':choice['conditional'],'status':row['status'],'checks':row['checks'],
  'unparsed_condition_text':row['unparsed_condition_text'],'actual_default_choice_block':block,
  'labels_as_condition':('条件原文：'+choice['conditional']) in block,
  'says_unparsed_condition': '这段附加条件尚未完整解析；保留原文，不当作已满足。' in block,
  'unparsed_added_as_check':any(c.get('source_text')==choice['conditional'] for c in row['checks'])})
extras={}
for identity in ('community_group_030','community_group_032'):
 event=deepcopy(catalog._event(identity));text=node_information_text({'kind':'event','record':event},context={})
 extras[identity]={'complete_event':event,'actual_default_text':text,
  'actual_battle_links':planning.event_battle_links(identity,context={})}
after={str(ROOT/p):pin(ROOT/p) for p in sources};assert before==after
assert 'rouge.app' not in sys.modules
result={'kind':'actual-default-player-text-inspection-not-UI-or-tests','at':datetime.now(timezone.utc).isoformat(),
 'context':{},'notes':rows,'complete_default_event_texts':texts,'additional_candidates':extras,
 'source_before':before,'source_after':after,'source_unchanged':True,'private_game_chat_Git_Qt_tests':False}
target=HERE/'actual-default-note-and-candidate-text.json'
target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'path':str(target),'sha256':sha256(target.read_bytes()).hexdigest(),'bytes':target.stat().st_size,
 'actual_note_count':len(rows),'condition_label_count':sum(r['labels_as_condition'] for r in rows),
 'unparsed_warning_count':sum(r['says_unparsed_condition'] for r in rows),
 'matching_check_count':sum(r['unparsed_added_as_check'] for r in rows),
 'new_candidate_battle_link_counts':{k:len(v['actual_battle_links']['rows']) for k,v in extras.items()}},ensure_ascii=False,indent=2))
