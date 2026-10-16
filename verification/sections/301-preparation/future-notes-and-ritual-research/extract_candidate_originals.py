"""Pin complete original/DOM candidates without executing game or UI code."""
from pathlib import Path
from hashlib import sha256
from html.parser import HTMLParser
from datetime import datetime,timezone
import json
ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
PINS={'.cache/p3-287-event-research/fixed-game-topic.json':'f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86',
 'rouge/data/node-catalog.json':'7df1d94bb69650eb19fc811af661e54d44bf07d72b1c0793de511adc1b2e915d',
 'research/p3-stage-context/community-main.html':'366e0bf14b526816b20750f1d83b6c7b132d556dfc0b09a0ab3c302fd00610e9',
 'research/p3-choice-recruitment-290/prts-events-427904.html':'faa088b0474e75806b357df8648c6a59b1be6dcbc9be749db7c934ca9e6307e9',
 'research/p3-choice-recruitment-290/prts-events-440271.html':'e04971ad361436e5bb3721883423d98ad66636d5156794dd6221a977ffd6dac8'}
class Node:
 def __init__(self,tag,attrs,order):self.tag,self.attrs,self.order,self.children=tag,dict(attrs),order,[]
class Document(HTMLParser):
 VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
 def __init__(self,raw):
  super().__init__(convert_charrefs=True);self.nodes=[];self.stack=[Node('root',[],-1)];self.feed(raw.decode('utf8'))
 def handle_starttag(self,tag,attrs):
  node=Node(tag,attrs,len(self.nodes));self.nodes.append(node);self.stack[-1].children.append(node)
  if tag not in self.VOID:self.stack.append(node)
 def handle_startendtag(self,tag,attrs):
  self.handle_starttag(tag,attrs)
  if tag not in self.VOID:self.handle_endtag(tag)
 def handle_endtag(self,tag):
  for index in range(len(self.stack)-1,0,-1):
   if self.stack[index].tag==tag:del self.stack[index:];break
 def handle_data(self,value):self.stack[-1].children.append(value)
def text(n):
 if isinstance(n,str):return n
 return ''.join(text(c)+('\n' if isinstance(c,Node) and c.tag in ('br','p','li') else '') for c in n.children)
def descendants(n):
 for c in n.children:
  if isinstance(c,Node):yield c;yield from descendants(c)
def cls(n,name):return name in n.attrs.get('class','').split()
def tree(n):
 if isinstance(n,str):return n
 return {'tag':n.tag,'attributes':n.attrs,'children':[tree(c) for c in n.children]}
raws={};sources={}
for p,digest in PINS.items():
 raw=(ROOT/p).read_bytes();assert sha256(raw).hexdigest()==digest,p
 raws[p]=raw;sources[str((ROOT/p).resolve())]={'sha256':digest,'bytes':len(raw)}
game=json.loads(raws['.cache/p3-287-event-research/fixed-game-topic.json']);d=game['details']['rogue_6']
cat=json.loads(raws['rouge/data/node-catalog.json']);events={e['id']:e for e in cat['events'] if e['id'] in ('community_group_030','community_group_031','community_group_032')}
doms={}
for rev in ('427904','440271'):
 doc=Document(raws['research/p3-choice-recruitment-290/prts-events-'+rev+'.html']);out={}
 for identity,event in events.items():
  matches=[]
  for n in doc.nodes:
   if not cls(n,'IS-event-data'):continue
   scenes=[c for c in descendants(n) if cls(c,'scene')]
   if scenes and scenes[0].attrs.get('data-index')==event['scenes'][0]['attributes']['data-index']:matches.append((n,scenes))
  assert len(matches)==1,(identity,rev)
  group,scenes=matches[0]
  assert len(scenes)==len(event['scenes']) and all(n.attrs==s['attributes'] for n,s in zip(scenes,event['scenes']))
  out[identity]={'group_order':group.order,'complete_DOM':tree(group),'text':text(group),
                 'scene_count':len(scenes),'choice_count':sum(len(s['choices']) for s in event['scenes'])}
 doms[rev]=out
doc=Document(raws['research/p3-stage-context/community-main.html']);endings={}
for ending in ('end2','end3'):
 blocks=[]
 for n in doc.nodes:
  if cls(n,'AKCollapse-content'):
   titles=[c for c in descendants(n) if cls(c,'end_title')]
   if len(titles)==1 and cls(titles[0],ending):blocks.append(n)
 assert len(blocks)==1,(ending,len(blocks))
 endings[ending]={'order':blocks[0].order,'complete_DOM':tree(blocks[0]),'text':text(blocks[0])}
choice_ids={cid for event in events.values() for s in event['scenes'] for c in s['choices'] for cid in c['game_choice_ids']}
original_choices={cid:d['choices'][cid] for cid in sorted(choice_ids)}
scene_ids={sid for event in events.values() for s in event['scenes'] for sid in s['game_scene_ids']}
items={k:v for k,v in d['items'].items() if k.startswith('rogue_6_end_2') or k.startswith('rogue_6_chimera_weaken_')
       or k in ('rogue_6_relic_final_1','rogue_6_relic_final_2','rogue_6_relic_final_4','rogue_6_relic_final_5','rogue_6_relic_final_6','rogue_6_bubble_03')}
stages={k:v for k,v in d['stages'].items() if v['name'] in ('畸症','混沌源阶理论')}
battle_raw=(ROOT/'rouge/data/battle-previews.json').read_bytes()
battle=json.loads(battle_raw)
sources[str((ROOT/'rouge/data/battle-previews.json').resolve())]={
 'sha256':sha256(battle_raw).hexdigest(),'bytes':len(battle_raw),'role':'existing-capability-snapshot-not-new-mechanism-authority'}
result={'kind':'complete-public-candidate-originals-and-DOM-only','at':datetime.now(timezone.utc).isoformat(),
 'sources_absolute':sources,'game_commit':'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add','complete_events':events,
 'event_complete_DOMs':doms,'main_complete_ending_blocks':endings,'complete_original_choices':original_choices,
 'complete_original_scenes':{sid:d['choiceScenes'][sid] for sid in sorted(scene_ids)},
 'complete_items':items,'complete_relics':{k:d['relics'][k] for k in items if k in d['relics']},
 'complete_associated_stage_records':stages,
 'existing_boss_mechanism_record':next(e for e in battle['stages']['ro6_b_6']['enemies'] if e['id']=='enemy_2150_shchmr'),
 'selected_static_checks':{'tuning_six_choice_primary_ids':[original_choices['choice_ro6_end3_'+str(i)]['id'] for i in (3,4,6,7,9,10)],
  'tuning_choice_game_ids_complete':all(c['game_choice_ids'] for s in events['community_group_032']['scenes'] for c in s['choices']),
  'fixed_atypia_stage_id_count':sum(v['name']=='畸症' for v in d['stages'].values())},
 'limits':['Static configuration and independent documentation only; actual grant/attachment/consumption/active callbacks unknown.',
  'No original source-scene entry is restored by nextSceneId or shared names.'],
 'Qt_tests_Git_private_game_chat':False}
target=HERE/'complete-candidate-originals-and-DOM.json'
target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'path':str(target),'sha256':sha256(target.read_bytes()).hexdigest(),'bytes':target.stat().st_size,
 'event_counts':{rev:{k:[v['scene_count'],v['choice_count']] for k,v in out.items()} for rev,out in doms.items()},
 'complete_item_count':len(items),'stage_ids':list(stages),'selected_static_checks':result['selected_static_checks']},ensure_ascii=False,indent=2))
