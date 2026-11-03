"""Read only pinned public source files; no product modules or tests imported."""
from pathlib import Path
from datetime import datetime, timezone
from hashlib import sha256
from html.parser import HTMLParser
import json

ROOT=Path(__file__).resolve().parents[2];HERE=Path(__file__).resolve().parent
SOURCES={
 '.cache/p3-287-event-research/fixed-game-topic.json':'f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86',
 'research/p3-stage-context/community-main.html':'366e0bf14b526816b20750f1d83b6c7b132d556dfc0b09a0ab3c302fd00610e9',
 'research/p3-choice-recruitment-290/prts-events-427904.html':'faa088b0474e75806b357df8648c6a59b1be6dcbc9be749db7c934ca9e6307e9',
 'research/p3-choice-recruitment-290/prts-events-440271.html':'e04971ad361436e5bb3721883423d98ad66636d5156794dd6221a977ffd6dac8',
 'rouge/data/node-catalog.json':'7df1d94bb69650eb19fc811af661e54d44bf07d72b1c0793de511adc1b2e915d'}
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
def descendants(node):
 for child in node.children:
  if isinstance(child,Node):yield child;yield from descendants(child)
def tree(node):
 if isinstance(node,str):return node
 return {'tag':node.tag,'attributes':node.attrs,'children':[tree(child) for child in node.children]}
def cls(node,name):return name in node.attrs.get('class','').split()
raws={};pins={}
for path,expected in SOURCES.items():
 raw=(ROOT/path).read_bytes();assert sha256(raw).hexdigest()==expected,path
 raws[path]=raw;pins[str((ROOT/path).resolve())]={'sha256':expected,'bytes':len(raw)}
game=json.loads(raws['.cache/p3-287-event-research/fixed-game-topic.json']);detail=game['details']['rogue_6']
doc=Document(raws['research/p3-stage-context/community-main.html'])
tables=[n for n in doc.nodes if n.tag=='table' and '实托邦景象' in text(n) and '保密等级·15' in text(n)]
assert len(tables)==1
table=tables[0];rows=[]
for n in descendants(table):
 if n.tag!='tr':continue
 cells=[{'tag':c.tag,'attributes':c.attrs,'text':text(c)} for c in n.children if isinstance(c,Node) and c.tag in ('td','th')]
 if cells:rows.append({'order':n.order,'cells':cells,'text':text(n)})
terms=('rogue_6_weather_8','rogue_6_subweather_4','rogue_6_next_weather_1','希望的沃土')
matches=[]
def walk(value,path):
 if isinstance(value,dict):
  for k,v in value.items():
   if any(term in str(k) for term in terms):matches.append({'kind':'key','path':path+[str(k)],'value_kind':type(v).__name__})
   walk(v,path+[str(k)])
 elif isinstance(value,list):
  for i,v in enumerate(value):walk(v,path+[str(i)])
 elif isinstance(value,str) and any(term in value for term in terms):matches.append({'kind':'string','path':path,'value':value})
walk(game,[])
normal=[r for r in detail['difficulties'] if r['modeDifficulty']=='NORMAL']
result={'kind':'source-only-phase-binding-audit','created_at':datetime.now(timezone.utc).isoformat(),
 'sources_absolute':pins,'commit':'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add',
 'complete_normal_difficulty_records':normal,'complete_difficulty_table_DOM':tree(table),'difficulty_rows':rows,
 'matching_primary_leaf_and_key_paths':matches,'complete_weather_records':{
  k:v for k,v in game['modules']['rogue_6']['weather']['mainWeatherData'].items() if v['type']=='rogue_6_weather_8'},
 'complete_gain_policy':game['modules']['rogue_6']['weather']['subWeatherData']['rogue_6_subweather_4'],
 'complete_force_weather_relic':detail['relics']['rogue_6_next_weather_1'],
 'complete_force_weather_item':detail['items']['rogue_6_next_weather_1'],
 'complete_weather_archive_entries':{k:detail['archiveComp']['weather']['weathers'][k]
  for k in ('rogue_6_weather_8_a','rogue_6_weather_8_b','rogue_6_weather_8_c','rogue_6_subweather_4')},
 'complete_original_red_moss_choices':{k:detail['choices'][k] for k in ('choice_ro6_normal3_1','choice_ro6_normal3_2')},
 'operation_scope':{'product_modified':False,'Qt_tests_Git_game_chat_private':False}}
target=HERE/'phase-and-binding-source-evidence-v2.json';target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'output':str(target),'sha256':sha256(target.read_bytes()).hexdigest(),'bytes':target.stat().st_size,
 'rows':[{ 'text':r['text'][:60], 'last_cells':r['cells'][-2:]} for r in rows],
 'primary_match_count':len(matches),'primary_matching_paths':[m['path'] for m in matches]},ensure_ascii=False,indent=2))
