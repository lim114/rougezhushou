"""Build fixed normal-stage hunt documentation; no phase or combat simulation."""
from pathlib import Path
from copy import deepcopy
from hashlib import sha256
from html.parser import HTMLParser
import argparse,json,re

ROOT=Path(__file__).resolve().parents[1]
PACK='research/p3-boss-hunt-311'
DATA='rouge/data/boss-hunt-reference.json'
MANIFEST=PACK+'/source-manifest.json'
SELECTED=PACK+'/runtime-selected-authority.json'
TARGETS=(('ro6_b_4','enemy_2145_cadejo',0),('ro6_b_4','enemy_2146_cadesd',0),('ro6_b_4','enemy_2137_shsdgo',0))
ENEMIES=('enemy_2145_cadejo','enemy_2146_cadesd','enemy_2137_shsdgo','enemy_2146_cadesd_2','enemy_2146_cadesd_3')
STAGES=('ro6_b_4','ro6_b_4_b')
FROZEN_HANDOFF_SHA='43a21c4cf43b55546cf33bcb6b433a7cbdfc5b54713bee3a64dea7c1a28320d3'
TEMPLATE_SHA='5605865e2168c58035d5edec792f73512d26afea65884bfad9153af757dfe800'
PLAYER_NAME='player-reading-proposal.json'

def encoded(v):return(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf8')
def pin(raw):return{'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def require(v,message):
 if not v:raise ValueError(message)
def same(a,b):
 if type(a)is not type(b):return False
 if type(a)is dict:return a.keys()==b.keys()and all(type(k)is str and same(a[k],b[k])for k in b)
 if type(a)is list:return len(a)==len(b)and all(same(x,y)for x,y in zip(a,b))
 return a==b

class Node:
 def __init__(self,tag,attrs,location=None):self.tag=tag;self.attrs=dict(attrs);self.children=[];self.location=location
class Document(HTMLParser):
 VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
 def __init__(self,text):
  super().__init__(convert_charrefs=True);self.original=text;self.starts=[0]+[m.end()for m in re.finditer('\n',text)]
  self.nodes=[];self.stack=[Node('root',[])];self.feed(text)
 def handle_starttag(self,tag,attrs):
  line,col=self.getpos();offset=self.starts[line-1]+col
  n=Node(tag,attrs,{'line':line,'column':col,'character_offset':offset,'byte_offset_utf8':len(self.original[:offset].encode('utf8'))})
  self.nodes.append(n);self.stack[-1].children.append(n)
  if tag not in self.VOID:self.stack.append(n)
 def handle_startendtag(self,tag,attrs):
  self.handle_starttag(tag,attrs)
  if tag not in self.VOID:self.handle_endtag(tag)
 def handle_endtag(self,tag):
  for i in range(len(self.stack)-1,0,-1):
   if self.stack[i].tag==tag:del self.stack[i:];break
 def handle_data(self,text):self.stack[-1].children.append(text)
def cls(n,k):return isinstance(n,Node)and k in n.attrs.get('class','').split()
def visible(n):
 if isinstance(n,str):return n
 if n.tag in('script','style')or'display:none'in n.attrs.get('style','').replace(' ',''):return''
 return''.join(visible(c)for c in n.children)+('\n'if n.tag in('p','li','dt','dd','tr','br')else'')
def serial(n):return n if isinstance(n,str)else{'tag':n.tag,'attributes':n.attrs,'location':n.location,'children':[serial(c)for c in n.children]}
def descendants(n):
 for c in n.children:
  if isinstance(c,Node):yield c;yield from descendants(c)

def verify_documents(blobs,records,extracted):
 counts={'skill':0,'ability':0};by_actor={}
 require(len(records)==5,'Five complete documentary pages required')
 require(set(extracted['documents'])=={r['title']for r in records},'Whole documentary selection differs')
 for source in records:
  raw=blobs[PACK+'/'+source['file']]
  require(same(pin(raw),{k:source[k]for k in('sha256','bytes')}),'Complete HTTP response differs')
  text=raw.decode('utf8')
  require(source['status']==200 and re.search(r'"wgRevisionId"\s*:\s*'+re.escape(str(source['revision']))+r'\b',text),'Fixed source revision differs')
  doc=Document(text);nodes=[n for n in doc.nodes if cls(n,'ak-card__body')and cls(n,'skill_card')]
  entry=extracted['documents'][source['title']]
  require(same(entry['source'],source),'Document source metadata differs')
  require(len(nodes)==len(entry['cards']),'Whole card selection differs')
  by_actor[source['title']]=[]
  for i,(node,card)in enumerate(zip(nodes,entry['cards'])):
   require(card['card_index']==i and same(serial(node),card['complete_DOM']),'Whole card DOM differs')
   title=next((c for c in node.children if cls(c,'ak-card__title')),None)
   header=visible(title).strip()if title else None
   role='skill'if header else'ability'
   paragraphs=[visible(c).strip()for c in node.children if isinstance(c,Node)and c.tag=='p']
   require(card['kind']==role and header==card['complete_visible_header'],'Card role or full header differs')
   require(same(re.findall(r'\[([^\[\]]+)\]',header or''),card['documented_modes_from_complete_header']),'Explicit modes differ')
   require(same(paragraphs,[p['text']for p in card['paragraphs']])and visible(node).strip()==card['complete_visible_card'],'Visible card body differs')
   allnodes=[node,*descendants(node)]
   require(len(card['tooltip_nodes'])==sum(cls(n,'mc-tooltips')for n in allnodes),'Complete tooltip selection differs')
   for tip in card['tooltip_nodes']:
    require(sum(same(serial(n),tip['complete_DOM'])for n in allnodes)==1,'Whole tooltip DOM differs')
   counts[role]+=1;by_actor[source['title']].append(card)
  tables=[n for n in doc.nodes if n.tag=='table'and cls(n,'wikitable')]
  require(len(tables)==len(entry['complete_wikitables']),'Whole table selection differs')
  for table,rawtable in zip(tables,entry['complete_wikitables']):
   require(same(serial(table),rawtable['complete_DOM'])and visible(table).strip()==rawtable['complete_visible_text'],'Whole table DOM differs')
 require(counts=={'skill':8,'ability':3},'Eight skills and three abilities required')
 return counts,by_actor

def build(root=ROOT,output_root=None,*,authority_root=None,enemy_database=None,normal_level=None,pursuit_level=None):
 root=Path(root);output=root if output_root is None else Path(output_root)
 authority=Path(authority_root)if authority_root is not None else output if(output/PACK/'HANDOFF.json').is_file()else root
 rawhandoff=(authority/PACK/'HANDOFF.json').read_bytes()
 require(sha256(rawhandoff).hexdigest()==FROZEN_HANDOFF_SHA,'Frozen source handoff differs')
 handoff=json.loads(rawhandoff);blobs={}
 for name,expected in handoff['source_files'].items():
  require(type(name)is str and not Path(name).is_absolute()and'..'not in Path(name).parts and '\\'not in name and ':'not in name,'Invalid frozen source name')
  raw=(authority/PACK/name).read_bytes();require(same(pin(raw),expected),'Frozen whole member differs: '+name)
  blobs[PACK+'/'+name]=raw
 selected=json.loads(blobs[PACK+'/selected-original-records.json'])
 extracted=json.loads(blobs[PACK+'/complete-document-cards-with-tooltips.json'])
 records=json.loads(blobs[PACK+'/http-source-records.json'])
 proposal=json.loads(blobs[PACK+'/'+PLAYER_NAME])
 counts,by_actor=verify_documents(blobs,records,extracted)
 inputs={}
 overrides={'enemy_database':enemy_database,'normal_level':normal_level,'pursuit_level':pursuit_level}
 suffixes={'enemy_database':'/enemy_database.json','normal_level':'/level_rogue6_b-4.json','pursuit_level':'/level_rogue6_b-4-b.json'}
 for source in selected['source_files']:
  name=source['file'];path=root/name
  for role,suffix in suffixes.items():
   if name.endswith(suffix)and overrides[role]is not None:path=Path(overrides[role])
  raw=path.read_bytes()
  require(same(pin(raw),{k:source[k]for k in('sha256','bytes')}),'Complete build authority differs: '+name)
  inputs[name]=raw
 battle=json.loads(inputs['rouge/data/battle-previews.json'])
 skills=json.loads(inputs['rouge/data/enemy-skill-references.json'])
 database=json.loads(next(raw for name,raw in inputs.items()if name.endswith('/enemy_database.json')))
 for eid in ENEMIES:
  require(same([r for r in database['enemies']if r['Key']==eid],selected['complete_original_enemy_records'][eid]),'Whole original database selection differs: '+eid)
  require(same(skills['definitions'][eid],selected['complete_skill_definitions'][eid]),'Whole selected skill definition differs: '+eid)
 for sid in STAGES:
  stage=battle['stages'][sid];require(same(stage,selected['complete_canonical_stages'][sid]),'Whole canonical stage differs: '+sid)
  name='.cache/game-data/levels/'+stage['level_source']['url'].split('/levels/',1)[1]
  level=json.loads(inputs[name]);require(same(level,selected['complete_original_levels'][sid]),'Whole original level differs: '+sid)
  require(same([r for r in level['enemyDbRefs']if r['id']in ENEMIES],selected['complete_stage_enemyDbRefs'][sid]),'Complete stage enemy references differ')
  require(same({k:v for k,v in skills['bindings'][sid].items()if k.split('@')[0]in ENEMIES},selected['complete_skill_bindings'][sid]),'Whole selected current bindings differ: '+sid)
 for _,eid,level in TARGETS:
  require(len([r for r in battle['stages']['ro6_b_4']['enemies']if r['id']==eid and type(r['level'])is int and r['level']==level])==1,'Normal target must be unique')
 custom=[r for r in selected['complete_stage_enemyDbRefs']['ro6_b_4_b']if r['id']in ENEMIES[-2:]]
 require(len(custom)==2 and all(r['useDb']is False and len(r['overwrittenData']['skills'])==3 for r in custom),'Both distinct nonempty custom skill sets required')
 require(same(proposal['targets'],[list(t)for t in TARGETS]),'Exact entry identity set required')
 require('不是本局必经时间轴'in proposal['overview_notice'],'Independent conditions must not become timeline')
 require(len(proposal['topics'])>=4 and len({t['id']for t in proposal['topics']})==len(proposal['topics']),'Distinct player topics required')
 require(len(proposal['skills'])==8,'Eight separate named player skills required')
 allskillcards=[(actor,c)for actor,cs in by_actor.items()for c in cs if c['kind']=='skill']
 require({(s['actor'],s['card_index'])for s in proposal['skills']}=={(a,c['card_index'])for a,c in allskillcards},'Player skill cards must cover all eight exact sources')
 for skill in proposal['skills']:
  card=next(c for a,c in allskillcards if a==skill['actor']and c['card_index']==skill['card_index'])
  require(skill['name']==card['complete_visible_header'].split('\n',1)[0]and same(skill['documented_modes'],card['documented_modes_from_complete_header']),'Player skill name/mode differs from source')
  require(same(skill['full_body_paragraphs'],[p['text']for p in card['paragraphs']]),'Complete source skill body required')
 runtime_selected={k:deepcopy(selected[k])for k in('complete_canonical_stages','complete_skill_definitions','complete_skill_bindings')}
 runtime_selected.update(complete_battle_source=battle['source'],complete_skill_source=skills['source'])
 ref=deepcopy(proposal);ref['kind']='documented_boss_hunt_reference';ref['not_a_linear_timeline']=True
 actor_topics={'卡德霍，黑流之源':'cadejo','痛楚化身':'avatars','猎犬proto':'hound'}
 for topic in ref['topics']:
  topic['source_paragraphs']=deepcopy(topic['paragraphs'])
  topic['paragraphs']=[p['text']for p in topic['paragraphs']]
 for skill in ref['skills']:
  skill['topic_id']=actor_topics[skill['actor']]
  skill['mode_label']='、'.join(skill['documented_modes'])or'文献未限定形态'
  skill['text']='\n'.join(skill['full_body_paragraphs'])
 ref['player_unknowns']=['本局各主体当前形态、技能是否触发、目标与发生时刻。',
  '原文标记存疑的波次释放次数，以及实际波次推进和出怪次数。',
  '降攻速20秒与10秒记载在当前对局中哪一项适用。',
  '增益或减益是否生效、实际层数，以及命中、回复、伤害与结算结果。',
  '痛苦将息关卡的两种自定义化身与基础文献之间，尚未核实的实际对应机制。']
 ref['source_differences']=json.loads(blobs[PACK+'/source-differences.json'])
 ref['reviewed_complete_documentation']=extracted;ref['source_documents']=records
 unknown={**{k:None for k in('actual_boss_form','actual_avatar_form','actual_hounds','actual_rest_gate','actual_skill','actual_transition','actual_elapsed_time','actual_target','actual_route','phase_stats','actual_damage')},
  **{k:False for k in('current_server_verified','numerical_phase_model_added','run_state_updated','inventory_updated','modifiers_changed','maps_changed')}}
 entry_names={eid:next(r['name']for r in battle['stages']['ro6_b_4']['enemies']if r['id']==eid and type(r['level'])is int and r['level']==0)for _,eid,_ in TARGETS}
 data={'schema':'boss_hunt_reference_v1','targets':[list(t)for t in TARGETS],'entry_names':entry_names,
  'reference':ref,'actual_and_mutation_fields':unknown}
 outputs={DATA:encoded(data),SELECTED:encoded(runtime_selected)}
 runtime_names=[PACK+'/'+r['file']for r in records]+[PACK+'/http-source-records.json',PACK+'/complete-document-cards-with-tooltips.json',PACK+'/'+PLAYER_NAME,
  PACK+'/source-differences.json',PACK+'/candidate-assessment.json']
 # All semantic review JSONs selected explicitly by the frozen source author are
 # also authority. Build scripts and whole large DB/levels remain build-only.
 runtime_names+= [PACK+'/'+name for name in handoff.get('runtime_semantic_members',[])]
 runtime_names=list(dict.fromkeys(runtime_names))
 for name in runtime_names:require(name in blobs,'Missing runtime semantic source: '+name)
 runtime={**{name:pin(raw)for name,raw in outputs.items()},**{name:pin(blobs[name])for name in runtime_names}}
 template=(authority/PACK/'backend-template.py').read_bytes()
 require(sha256(template).hexdigest()==TEMPLATE_SHA,'Frozen backend template differs')
 build_sources={name:pin(raw)for name,raw in blobs.items()if name not in runtime}
 build_sources.update({PACK+'/HANDOFF.json':pin(rawhandoff),PACK+'/backend-template.py':pin(template)})
 build_sources.update({name:pin(raw)for name,raw in inputs.items()})
 manifest={'schema':'boss_hunt_source_manifest_v1','data_file':DATA,'data_sha256':sha256(outputs[DATA]).hexdigest(),
  'targets':[list(t)for t in TARGETS],'runtime_files':runtime,'build_authority_files':build_sources,
  'all_runtime_members_required_for_each_target_query':True,'runtime_full_database_hashing':False,
  'runtime_scope':'Fresh small complete documents/semantic authority and complete current selected two stages/five definitions/eight bindings; no per-query whole database or level hashing.',
  'build_scope':'Whole fixed database, both original levels, battle/skill catalogues and all five complete HTMLs verified before extraction.',
  'actual_state_or_numeric_model_added':False}
 outputs[MANIFEST]=encoded(manifest)
 literal='{'+', '.join(repr(n)for n in sorted(runtime))+'}'
 outputs['rouge/boss_hunt_reference.py']=template.decode('utf8').replace('__DATA_SHA__',sha256(outputs[DATA]).hexdigest()).replace('__MANIFEST_SHA__',sha256(outputs[MANIFEST]).hexdigest()).replace('__RUNTIME_FILES__',literal).encode('utf8')
 for name,raw in outputs.items():
  path=output/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
 receipt={'kind':'SECTION311_SOURCE_BUILD_NOT_PRODUCT_ACCEPTANCE','targets':[list(t)for t in TARGETS],
  'boss_skill_cards':counts['skill'],'ability_cards':counts['ability'],'complete_source_pages':len(records),
  'selected_reference_stages':2,'selected_definition_objects':5,'runtime_source_members':len(runtime),
  'explicit_primary_override_roles':[role for role,path in overrides.items()if path is not None],
  'numeric_model_added':False,'outputs':{name:pin(raw)for name,raw in outputs.items()}}
 path=output/PACK/'build-receipt.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(encoded(receipt))
 return receipt

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,default=ROOT)
 parser.add_argument('--output-root',type=Path);parser.add_argument('--check',action='store_true')
 parser.add_argument('--enemy-database',type=Path,help='完整固定敌人数据库；仅替代读取位置，仍核对原字节。')
 parser.add_argument('--normal-level',type=Path,help='完整ro6_b_4原件：永无安宁。')
 parser.add_argument('--pursuit-level',type=Path,help='内部兼容角色名；实际为完整ro6_b_4_b原件：痛苦将息，不据此判定属于追猎。');args=parser.parse_args()
 overrides={'enemy_database':args.enemy_database,'normal_level':args.normal_level,'pursuit_level':args.pursuit_level}
 if args.check:
  import tempfile
  compare=args.root if args.output_root is None else args.output_root
  with tempfile.TemporaryDirectory()as directory:
   result=build(args.root,Path(directory),authority_root=compare,**overrides)
   for name in result['outputs']:require((Path(directory)/name).read_bytes()==(compare/name).read_bytes(),'Generated bytes differ: '+name)
 else:result=build(args.root,args.output_root,**overrides)
 print(json.dumps(result,ensure_ascii=False))
