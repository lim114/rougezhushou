"""Pure fixed-source reconstruction for exact battle-to-event reading references."""
import argparse
from copy import deepcopy
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote,urljoin

DEPENDENCIES = {'rouge/data/node-catalog.json': {'sha256': '7df1d94bb69650eb19fc811af661e54d44bf07d72b1c0793de511adc1b2e915d', 'bytes': 521326}, 'rouge/data/event-planning-reference.json': {'sha256': 'b9de2c98dac306eafc40dba8fa3ee5765c6720afa18c907488ff1f4f199e4f14', 'bytes': 313122}, 'rouge/data/battle-previews.json': {'sha256': 'f0155647af8766eb2f01e84295f85b7300264fc49b40ffc82e89800837d274f3', 'bytes': 9920110}, 'rouge/event_planning.py': {'sha256': 'f5715822efb181d9b8d84c59eda2667a23e64ca7d341eb63edc2c7eaf834d8ba', 'bytes': 37199}, 'rouge/node_catalog.py': {'sha256': '5fd1d9d839f2d26ee0d1a0c6e99935b0197017dcb491bf9525e5b1081de404c1', 'bytes': 34666}, 'research/p3-choice-recruitment-290/prts-events-427904.html': {'sha256': 'faa088b0474e75806b357df8648c6a59b1be6dcbc9be749db7c934ca9e6307e9', 'bytes': 183007}, 'research/p3-choice-recruitment-290/prts-events-440271.html': {'sha256': 'e04971ad361436e5bb3721883423d98ad66636d5156794dd6221a977ffd6dac8', 'bytes': 183838}}
GAME_SHA='f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86'
GAME_COMMIT='a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'
PACKET='research/p3-battle-event-references-296'
DATA='rouge/data/battle-event-references.json'
STAGES=('ro6_t_1','ro6_t_2','ro6_t_3','ro6_t_4','ro6_t_5','ro6_e_t_3','ro6_e_t_4','ro6_e_t_5')
EVENTS=('community_group_012','community_group_013','community_group_014','community_group_015','community_group_016')
DOCS={'427904':'research/p3-choice-recruitment-290/prts-events-427904.html',
 '440271':'research/p3-choice-recruitment-290/prts-events-440271.html'}

def digest(raw):return sha256(raw).hexdigest()
def encode(value):return(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode()
def require(condition,message):
 if condition is not True:raise ValueError(message)

class Node:
 def __init__(self,tag='',attrs=None):self.tag=tag;self.attrs=dict(attrs or []);self.children=[];self.parts=[]
 def text(self):return''.join(self.parts).strip()
def walk(node):
 yield node
 for child in node.children:yield from walk(child)
def classes(node,cls):return cls in node.attrs.get('class','').split()
class Parser(HTMLParser):
 def __init__(self):super().__init__();self.root=Node();self.stack=[self.root]
 def handle_starttag(self,tag,attrs):
  node=Node(tag,attrs);self.stack[-1].children.append(node)
  if tag not in('link','br','img','hr','meta','input','wbr','area','base','embed','source','track','col','param'):self.stack.append(node)
 def handle_endtag(self,tag):
  for index in range(len(self.stack)-1,0,-1):
   if self.stack[index].tag==tag:self.stack=self.stack[:index];break
 def handle_data(self,text):
  if self.stack[-1].tag not in('script','style'):
   for node in self.stack:node.parts.append(text)

def stage_record(sid,stage):
 return{'stage_id':sid,'name':stage['name'],'code':stage['code'],'difficulty':stage['difficulty'],
  'level_id':stage['levelId'],'is_boss_parameter':stage['isBoss'],'source_selector':'$.details.rogue_6.stages.'+sid}

def build(source_root,game_table):
 blobs={}
 require(len(DEPENDENCIES)==7,'Exactly three current data, two unchanged code and two document dependencies are pinned')
 for name,pin in DEPENDENCIES.items():
  path=(source_root/name)
  require(path.is_file()and not path.is_symlink()and path.resolve().is_relative_to(source_root.resolve()),'regular public dependency '+name)
  raw=path.read_bytes();require(digest(raw)==pin['sha256']and len(raw)==pin['bytes'],'fixed dependency '+name);blobs[name]=raw
 game=game_table.read_bytes();require(digest(game)==GAME_SHA,'whole original fixed game table')
 detail=json.loads(game)['details']['rogue_6']
 catalog=json.loads(blobs['rouge/data/node-catalog.json']);planning=json.loads(blobs['rouge/data/event-planning-reference.json'])
 battle=json.loads(blobs['rouge/data/battle-previews.json'])
 require(battle['source']['game_commit']==GAME_COMMIT,'same fixed primary version for battle levels')
 events={e['id']:e for e in catalog['events']if e['id']in EVENTS}
 require(set(events)==set(EVENTS),'five exact community events')
 records=[r for r in planning['battle_links']if r['event_id']in EVENTS]
 require(len(records)==8 and len({r['choice_key']for r in records})==8,'eight complete source choices')
 originals={'source':deepcopy(planning['sources']['original_game']),'stages':{sid:deepcopy(detail['stages'][sid])for sid in STAGES},'choices':{}}
 edges=[]
 for record in records:
  event=events[record['event_id']]
  scene=next(s for s in event['scenes']if s['key']==record['scene_key'])
  choice=next(c for c in scene['choices']if c['key']==record['choice_key'])
  require((choice['title'],choice['description'],choice['conditional'])==
   (record['choice_title'],record['description'],record['conditional_text']),'complete fixed choice content')
  require(len(choice['game_choice_ids'])==1,'one existing original content pointer, not an inferred source script')
  cid=choice['game_choice_ids'][0];originals['choices'][cid]=deepcopy(detail['choices'][cid])
  require(originals['choices'][cid]['title']==choice['title'],'full original choice title')
  for page in record['stage_page_links']:
   for stage in page['stage_records']:
    sid=stage['stage_id'];require(sid in STAGES,'no scope expansion by same-name page')
    require(stage==stage_record(sid,detail['stages'][sid]),'exact full stage record '+sid)
    preview=battle['stages'][sid]
    require(preview['id']==sid and preview['name']==stage['name']and preview['difficulty']==stage['difficulty'],'exact fixed preview alias')
    level=preview['level_source']
    require(level['url'].endswith(stage['level_id'].lower()+'.json')
     and '/'+GAME_COMMIT+'/'in level['url']and len(level['sha256'])==64 and type(level['bytes'])is int,
     'complete primary level identity without filename fallback')
    excluded=record['conditional_text']=='升级为紧急作战'and stage['difficulty']!='FOUR_STAR'
    edges.append({'stage_id':sid,'event_id':event['id'],'event_title':event['title'],
     'event_documented_main_floors':deepcopy(event['floors']),'event_node_types':deepcopy(event['node_types']),
     'scene_key':scene['key'],'choice_key':choice['key'],'choice_title':choice['title'],
     'choice_description':choice['description'],'conditional_text':choice['conditional'],
     'game_choice_ids':deepcopy(choice['game_choice_ids']),'stage_record':deepcopy(stage),
     'stage_page':{'title':page['title'],'url':page['href'],'anchor_text':page['anchor_text']},
     'level_source':deepcopy(level),'excluded_by_explicit_difficulty':excluded,
     'source_difficulty_matches':None if record['conditional_text']!='升级为紧急作战'else not excluded})
 require(len(edges)==14 and sum(r['excluded_by_explicit_difficulty']for r in edges)==3
  and set(r['stage_id']for r in edges)==set(STAGES),'14 raw edges, three explicit normal exclusions, eight exact IDs')
 for edge in edges:
  identity={key:edge[key]for key in('stage_id','event_id','scene_key','choice_key','stage_record','stage_page','level_source')}
  edge['reference_id']='battle-event:'+digest(json.dumps(identity,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
 require(len({edge['reference_id']for edge in edges})==14,'every original edge has a stable full-identity reference')
 docs={}
 for revision,name in DOCS.items():
  parser=Parser();parser.feed(blobs[name].decode('utf8'))
  groups=[n for n in walk(parser.root)if classes(n,'IS-event-data')]
  require(len(groups)==len(catalog['events'])==38,'complete document group identity')
  extracted=[]
  for event in events.values():
   index=next(i for i,e in enumerate(catalog['events'])if e['id']==event['id'])
   group=groups[index];scenes=[n for n in group.children if classes(n,'scene')]
   require(len(scenes)==len(event['scenes'])and scenes[0].attrs['data-name']==event['title']
    and scenes[0].attrs['data-efloor']==event['scenes'][0]['attributes']['data-efloor'],'exact event ordinal and floor declaration')
   choices=[]
   for si,known_scene in enumerate(event['scenes']):
    dom_choices=[n for n in scenes[si].children if classes(n,'choose')]
    require(len(dom_choices)==len(known_scene['choices']),'complete source scene choice count')
    for ci,choice in enumerate(known_scene['choices']):
     if choice['key']not in{r['choice_key']for r in records}:continue
     node=dom_choices[ci];require(node.attrs['data-title']==choice['title'],'exact DOM choice ordinal/title')
     description=next(n.text()for n in node.children if classes(n,'desc1'))
     condition=next((n.text()for n in node.children if classes(n,'desc2')),None)
     require(description==choice['description']and condition==choice['conditional'],'full DOM description and conditional')
     anchors=[]
     for anchor in walk(node):
      if anchor.tag!='a'or not anchor.attrs.get('href'):continue
      title=anchor.attrs.get('title')or unquote(anchor.attrs['href']).rsplit('/',1)[-1].replace('_',' ')
      if title.startswith('ISW-'):
       anchors.append({'title':title,'url':urljoin('https://prts.wiki',anchor.attrs['href']),'anchor_text':anchor.text()})
     expected=[r for r in records if r['choice_key']==choice['key']][0]
     require(anchors==[{'title':p['title'],'url':p['href'],'anchor_text':p['anchor_text']}for p in expected['stage_page_links']],
      'fixed page-link order and all identity fields')
     choices.append({'scene_key':known_scene['key'],'choice_key':choice['key'],'scene_ordinal':si,'choice_ordinal':ci,
      'attributes':deepcopy(node.attrs),'description':description,'conditional_text':condition,'stage_pages':anchors})
   extracted.append({'event_id':event['id'],'event_title':event['title'],'group_ordinal':index,
    'entry_scene_attributes':deepcopy(scenes[0].attrs),'event_documented_main_floors':deepcopy(event['floors']),'choices':choices})
  docs[revision]={'file':name,'sha256':digest(blobs[name]),'bytes':len(blobs[name]),'events':extracted}
 sources={'original_game':deepcopy(planning['sources']['original_game']),'documents':[
  {'revision':rev,'file':name,**deepcopy(DEPENDENCIES[name])}for rev,name in DOCS.items()]}
 data={'schema_version':1,'reference_kind':'fixed_battle_documented_event_choices','stage_ids':list(STAGES),
  'event_ids':list(EVENTS),'counts':{'raw_edges':14,'admitted_edges':11,'explicit_exclusions':3,'events':5,'choices':8,'stage_ids':8},
  'edges':edges,'sources':sources,'actual_stage_id':None,'actual_choice_eligible':None,'actual_entered':None,
  'stage_global_floors':None,'full_stage_origin_floors_known':False,'current_server_verified':False,
  'notice':'这是资料中与固定战斗对应的事件选项，不代表本局发生、可选或已进入；所列主层仅属于该事件资料，不是作战全部入口。'}
 outputs={DATA:encode(data),PACKET+'/original-records.json':encode(originals),
  PACKET+'/event-doc-spans.json':encode({'scope':'Complete DOM ordinal/choice/page/floor extraction, not game script or server execution','documents':docs})}
 pins=deepcopy(DEPENDENCIES)
 for name,raw in outputs.items():pins[name]={'sha256':digest(raw),'bytes':len(raw)}
 manifest={'schema_version':1,'section':296,'files':pins,
  'scope':'Exact8 fixed stages to source-admitted event choices; full document and original objects are version-bound content only.'}
 outputs[PACKET+'/source-manifest.json']=encode(manifest)
 receipt={'kind':'PURE_SOURCE_RECONSTRUCTION_NOT_PRODUCT_PASS','source_manifest_sha256':digest(outputs[PACKET+'/source-manifest.json']),
  'counts':deepcopy(data['counts']),'whole_original_game_sha256':GAME_SHA,'whole_original_game_bytes':len(game),
  'whole_original_game_copied_into_public_packet':False,'full_preview_copied_into_public_packet':False,
  'network_game_chat_private_Qt_or_tests_executed':False,
  'outputs':{name:{'sha256':digest(raw),'bytes':len(raw)}for name,raw in outputs.items()}}
 outputs[PACKET+'/build-receipt.json']=encode(receipt)
 return outputs,receipt

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--source-root',required=True);parser.add_argument('--game-table',required=True);parser.add_argument('--output-dir',required=True)
 args=parser.parse_args();root=Path(args.source_root).resolve();dest=Path(args.output_dir).resolve()
 require(not dest.exists(),'exclusive new output directory')
 outputs,receipt=build(root,Path(args.game_table).resolve())
 dest.mkdir(parents=True)
 for name,raw in outputs.items():
  path=dest/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
 print(json.dumps({'source_build_only':True,'counts':receipt['counts'],'manifest_sha256':receipt['source_manifest_sha256']}))
if __name__=='__main__':main()
