"""Build semantic reading roles from complete pinned catalog and both public DOMs."""
from pathlib import Path
from hashlib import sha256
from html.parser import HTMLParser
from copy import deepcopy
import argparse,json

ROOT=Path(__file__).resolve().parents[1]
PACK='research/p3-choice-annotations-307'
DATA='rouge/data/choice-annotations.json'
CATALOG='rouge/data/node-catalog.json'
GAME='research/p3-future-region-effects-300/game-topic-complete.json'
PINS={CATALOG:'7df1d94bb69650eb19fc811af661e54d44bf07d72b1c0793de511adc1b2e915d',
 GAME:'f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86',
 'research/p3-future-region-effects-300/prts-events-427904.html':'faa088b0474e75806b357df8648c6a59b1be6dcbc9be749db7c934ca9e6307e9',
 'research/p3-future-region-effects-300/prts-events-440271.html':'e04971ad361436e5bb3721883423d98ad66636d5156794dd6221a977ffd6dac8'}
# Exact selections, not text-pattern guessing. Four conditions and twelve results.
ROLES=((8,0,0,'preselection_requirement','held_item'),(8,0,1,'selection_result','random_named_battle'),
 (14,2,0,'selection_result','emergency_battle'),(15,0,1,'preselection_requirement','gold_threshold'),
 (15,2,0,'selection_result','emergency_battle'),(16,8,0,'selection_result','emergency_battle'),
 (17,6,0,'selection_result','next_floor_battle'),(18,0,1,'selection_result','recruitment_professions'),
 (19,1,0,'selection_result','movement_exception'),(23,1,0,'selection_result','future_reward'),
 (23,6,0,'selection_result','future_reward'),(23,9,1,'selection_result','future_reward'),
 (23,11,0,'selection_result','future_reward'),(25,0,2,'preselection_requirement','held_item'),
 (30,0,0,'preselection_requirement','excluded_by_history_or_items'),(31,0,1,'selection_result','leave_revisit'))
LABELS={'held_item':'出现前条件','gold_threshold':'出现前条件','excluded_by_history_or_items':'出现前条件',
 'random_named_battle':'选择后可能的战斗','emergency_battle':'选择后的战斗难度',
 'next_floor_battle':'选择后战斗的候选范围','recruitment_professions':'选择后可能的职业组合',
 'movement_exception':'选择后的移动例外','future_reward':'后续奖励分支说明','leave_revisit':'暂离与再访说明'}

class Node:
 def __init__(self,tag,attrs):self.tag=tag;self.attrs=dict(attrs);self.children=[]
class Document(HTMLParser):
 VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
 def __init__(self,text):super().__init__(convert_charrefs=True);self.nodes=[];self.stack=[Node('root',[])];self.feed(text)
 def handle_starttag(self,tag,attrs):
  n=Node(tag,attrs);self.nodes.append(n);self.stack[-1].children.append(n)
  if tag not in self.VOID:self.stack.append(n)
 def handle_startendtag(self,tag,attrs):
  self.handle_starttag(tag,attrs)
  if tag not in self.VOID:self.handle_endtag(tag)
 def handle_endtag(self,tag):
  for i in range(len(self.stack)-1,0,-1):
   if self.stack[i].tag==tag:del self.stack[i:];break
 def handle_data(self,text):self.stack[-1].children.append(text)
def cls(n,k):return isinstance(n,Node)and k in n.attrs.get('class','').split()
def children(n,k):return[x for x in n.children if cls(x,k)]
def text(n):return n if isinstance(n,str)else''.join(text(x)for x in n.children)
def descendants(n):
 for x in n.children:
  if isinstance(x,Node):yield x;yield from descendants(x)
def part(n,k):
 matches=[x for x in descendants(n)if cls(x,k)]
 if len(matches)!=1:raise ValueError('Expected exact DOM '+k)
 return text(matches[0]).strip()
def serial(n):return n if isinstance(n,str)else{'tag':n.tag,'attributes':n.attrs,'children':[serial(x)for x in n.children]}
def encoded(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
def pin(b):return{'sha256':sha256(b).hexdigest(),'bytes':len(b)}

def build(root):
 root=Path(root);blobs={name:(root/name).read_bytes()for name in PINS}
 for name,digest in PINS.items():
  if sha256(blobs[name]).hexdigest()!=digest:raise ValueError('Complete source changed: '+name)
 catalog=json.loads(blobs[CATALOG]);game=json.loads(blobs[GAME])['details']['rogue_6']
 assert len(catalog['events'])==38
 docs={}
 for rev in ('427904','440271'):
  name=f'research/p3-future-region-effects-300/prts-events-{rev}.html'
  groups=[n for n in Document(blobs[name].decode('utf-8')).nodes if cls(n,'IS-event-data')]
  assert len(groups)==38;docs[rev]=(name,groups)
 expected={};rows=[];selected_dom={rev:{}for rev in docs};original_choices={};original_scenes={}
 for gi,si,ci,role,subtype in ROLES:
  event=catalog['events'][gi];eid=event['id'];assert eid==f'community_group_{gi:03d}'
  scene=event['scenes'][si];choice=scene['choices'][ci];assert choice['conditional']
  expected[eid]=deepcopy(event);sources=[]
  for rev,(name,groups)in docs.items():
   scenes=children(groups[gi],'scene');assert len(scenes)==len(event['scenes'])
   node=scenes[si];options=children(node,'choose');assert len(options)==len(scene['choices'])
   option=options[ci]
   assert node.attrs['data-name']==event['title'] and option.attrs==choice['attributes']
   assert part(option,'desc1')==choice['description']and part(option,'desc2')==choice['conditional']
   selected_dom[rev][eid]=serial(groups[gi])
   sources.append({'file':name,'revision':rev,'group_index':gi,'scene_index':si,'choice_index':ci,
    'field':'choose.desc2','source_text':part(option,'desc2'),
    'url':f'https://m.prts.wiki/index.php?title=沉沦者的黑流树海/事件一览&oldid={rev}'})
  for cid in choice['game_choice_ids']:
   original_choices[cid]=game['choices'][cid]
   nxt=game['choices'][cid]['nextSceneId']
   if nxt:original_scenes[nxt]=game['choiceScenes'][nxt]
  for sid in scene['game_scene_ids']:original_scenes[sid]=game['choiceScenes'][sid]
  limits=[]
  if subtype=='future_reward':
   limits=['这是后续分支说明，不是当前点击时立即领取；完整奖励池与实际结果仍未知。']
   if si in(9,11):limits.append('原注写2种奖励，但该页明确列出'+str(1 if si==9 else 3)+'种后续；数量不一致，不能视为完整候选范围。')
  elif subtype=='next_floor_battle':limits=['下一层普通作战的固定候选沿用原入口；特殊区域规则、完整服务器候选与实际关卡仍未知。']
  elif subtype=='random_named_battle':limits=['列出的三个关卡只是文献候选，不证明等概率、本局出现或实际选中。']
  rows.append({'event_id':eid,'scene_key':scene['key'],'choice_key':choice['key'],
   'role':role,'subtype':subtype,'label':LABELS[subtype],'text':choice['conditional'],
   'catalog_choice':deepcopy(choice),'source_refs':sources,'limits':limits,
   'existing_result_support':{'api':'resting_corner_results.resting_result_cards'if subtype=='future_reward'else
     'curiosity_node_rules.choice_reference'if subtype=='leave_revisit'else
     'choice_recruitment_results.choice_reference'if subtype=='recruitment_professions'else
     'peace_guardian_results.choice_result_reference'if subtype=='movement_exception'else
     'event_planning.event_battle_links'if role=='selection_result'else None},
   'actual_selectable':None,'actual_result':None,'inventory_updated':False,'qualification_changed':False})
 assert len(rows)==16 and sum(r['role']=='preselection_requirement'for r in rows)==4
 assert sum(bool(ch['conditional'])for e in catalog['events']for s in e['scenes']for ch in s['choices'])==16
 data={'schema':'choice_annotation_roles_v1','rows':rows,'expected_events':expected,
  'scope':'Semantic reading only: four existing requirements and twelve post-choice results; no new mechanism, condition match, actual selection or state changes.'}
 authority={'schema':'choice_annotation_selected_authority_v1','rows':deepcopy(rows),'complete_expected_events':expected,
  'complete_selected_DOM_groups':selected_dom,'complete_original_choices':original_choices,'complete_original_scenes':original_scenes,
  'original_game_source':{'file':GAME,**pin(blobs[GAME]),'commit':'a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'}}
 outputs={DATA:encoded(data),PACK+'/selected-authority-records.json':encoded(authority)}
 runtime={**{n:pin(b)for n,b in outputs.items()},**{n:pin(b)for n,b in blobs.items()if n!=GAME}}
 manifest={'schema':'choice_annotation_source_manifest_v1','runtime_files':runtime,'source_build_files':{n:pin(b)for n,b in blobs.items()},
  'all_runtime_members_required_each_target_query':True,'game_table_build_only':True,'qualification_or_state_changed':False}
 outputs[PACK+'/source-manifest.json']=encoded(manifest)
 return outputs

def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 artifacts=build(a.root)
 for name,raw in artifacts.items():
  target=a.out/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
 print(json.dumps({n:pin(b)for n,b in artifacts.items()},ensure_ascii=False))
if __name__=='__main__':main()
