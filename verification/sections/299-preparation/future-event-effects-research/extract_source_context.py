"""Pure public-file extraction, not runtime tests or an implemented capability."""
from pathlib import Path
from datetime import datetime, timezone
from html.parser import HTMLParser
from hashlib import sha256
import json

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).resolve().parent
PINNED={
 '.cache/p3-287-event-research/fixed-game-topic.json':'f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86',
 'rouge/data/node-catalog.json':'7df1d94bb69650eb19fc811af661e54d44bf07d72b1c0793de511adc1b2e915d',
 'research/p3-choice-recruitment-290/prts-events-427904.html':'faa088b0474e75806b357df8648c6a59b1be6dcbc9be749db7c934ca9e6307e9',
 'research/p3-choice-recruitment-290/prts-events-440271.html':'e04971ad361436e5bb3721883423d98ad66636d5156794dd6221a977ffd6dac8',
 'research/p3-stage-context/community-main.html':'366e0bf14b526816b20750f1d83b6c7b132d556dfc0b09a0ab3c302fd00610e9',
 '.cache/p3-287-event-research/bwiki-investigation.html':'26b7768bf3556cf73c24529659c2c92f4095059476f782130bf3fa768422b908'}

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
def text(node):
 if isinstance(node,str):return node
 return ''.join(text(child)+('\n' if isinstance(child,Node) and child.tag in ('br','p','li') else '') for child in node.children)
def children(node):
 for child in node.children:
  if isinstance(child,Node):yield child;yield from children(child)
def tree(node):
 if isinstance(node,str):return node
 return {'tag':node.tag,'attributes':node.attrs,'children':[tree(child) for child in node.children]}
def cls(node,name):return name in node.attrs.get('class','').split()

files={};pins={}
for path,expected in PINNED.items():
 raw=(ROOT/path).read_bytes();assert sha256(raw).hexdigest()==expected,path
 files[path]=raw;pins[path]={'sha256':expected,'bytes':len(raw)}
primary=json.loads(files['.cache/p3-287-event-research/fixed-game-topic.json'])
detail=primary['details']['rogue_6'];weather=primary['modules']['rogue_6']['weather']
catalog=json.loads(files['rouge/data/node-catalog.json'])
events={e['id']:e for e in catalog['events'] if e['id'] in ('community_group_009','community_group_023')}
event_doms={}
for revision in ('427904','440271'):
 path='research/p3-choice-recruitment-290/prts-events-'+revision+'.html';doc=Document(files[path]);groups={}
 for identity,event in events.items():
  index=event['scenes'][0]['attributes']['data-index'];matches=[]
  for group in (n for n in doc.nodes if cls(n,'IS-event-data')):
   scenes=[n for n in children(group) if cls(n,'scene')]
   if scenes and scenes[0].attrs.get('data-index')==index:matches.append((group,scenes))
  assert len(matches)==1,(identity,revision)
  group,scenes=matches[0]
  assert len(scenes)==len(event['scenes']) and all(n.attrs==s['attributes'] for n,s in zip(scenes,event['scenes']))
  groups[identity]={'group_order':group.order,'complete_DOM':tree(group),'complete_group_text':text(group),
                    'scene_count':len(scenes),'choice_count':sum(len(s['choices']) for s in event['scenes'])}
 event_doms[revision]=groups
main=Document(files['research/p3-stage-context/community-main.html'])
normal_tables=[n for n in main.nodes if n.tag=='table' and '实托邦景象' in text(n) and '保密等级·15' in text(n)]
assert len(normal_tables)==1
main_rows=[{'order':n.order,'complete_DOM':tree(n),'text':text(n)} for n in main.nodes
           if n.tag=='tr' and ('实托邦' in text(n) or '理想域' in text(n))]
main_paragraphs=[{'order':n.order,'complete_DOM':tree(n),'text':text(n)} for n in main.nodes
                if n.tag in ('p','dd','li') and any(term in text(n) for term in ('理想源','实托邦影响','实托邦·理念','实托邦·方针'))]
ideal_headers=[n for n in main.nodes if cls(n,'AKCollapse-title') and '理想域：' in text(n)]
assert len(ideal_headers)==1
ideal_content=next(n for n in main.nodes if n.order>ideal_headers[0].order and cls(n,'AKCollapse-content'))
bw=Document(files['.cache/p3-287-event-research/bwiki-investigation.html'])
bw_matches=[{'order':n.order,'complete_DOM':tree(n),'text':text(n)} for n in bw.nodes
            if n.tag in ('p','td','dd') and any(term in text(n) for term in ('希望的沃土','美丽新大地'))]
original_choices={k:v for k,v in detail['choices'].items() if '希望的沃土' in (v.get('description') or '')
                  or v.get('displayData',{}).get('itemId')=='rogue_6_next_weather_2'}
scene_ids={s for e in events.values() for scene in e['scenes'] for s in scene['game_scene_ids']}
result={'kind':'source-only-future-region-context-inventory','created_at':datetime.now(timezone.utc).isoformat(),
 'sources':pins,'game_commit':'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add',
 'complete_expected_events':events,'event_DOMs':event_doms,
 'complete_original_choices':original_choices,'complete_original_scenes':{k:v for k,v in detail['choiceScenes'].items() if k in scene_ids},
 'complete_weather_records':{k:v for k,v in weather['mainWeatherData'].items() if v['type'] in ('rogue_6_weather_8','rogue_6_weather_10')},
 'complete_gain_policy':weather['subWeatherData']['rogue_6_subweather_4'],
 'complete_next_weather_items':{k:v for k,v in detail['items'].items() if k.startswith('rogue_6_next_weather_')},
 'normal_difficulty_records':[v for v in detail['difficulties'] if v['modeDifficulty']=='NORMAL'],
 'main_document_complete_rows':main_rows,'main_document_complete_paragraphs':main_paragraphs,
 'normal_difficulty_complete_table':{'order':normal_tables[0].order,'complete_DOM':tree(normal_tables[0]),'text':text(normal_tables[0])},
 'ideal_domain_complete_block':{'title':tree(ideal_headers[0]),'content':tree(ideal_content),'text':text(ideal_content)},
 'bwiki_exact_containing_elements':bw_matches,
 'limits':['Documentation relationships only; original source-scene and actual execution are not restored.',
           'Future region effects are not immediate rewards or actual currently attached modifiers.',
           'No probability, current climate, actual drop, pool membership or quantity is inferred.'],
 'production_Qt_tests_game_chat_private_Git_mutation':False}
target=HERE/'source-context-complete-v3.json';target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'path':str(target.relative_to(ROOT)),'sha256':sha256(target.read_bytes()).hexdigest(),'bytes':target.stat().st_size,
 'event_DOM_counts':{rev:{identity:{'scenes':g['scene_count'],'choices':g['choice_count']} for identity,g in groups.items()} for rev,groups in event_doms.items()},
 'primary_weather_records':list(result['complete_weather_records']),'original_choices':list(original_choices),
 'main_rows':len(main_rows),'main_paragraphs':len(main_paragraphs),'bwiki_matching_elements':len(bw_matches),
 'phase_cells':[{'attributes':n.attrs,'text':text(n)} for n in children(normal_tables[0]) if n.tag=='td' and any(term in text(n) for term in ('早期','中期','晚期'))]},ensure_ascii=False,indent=2))
