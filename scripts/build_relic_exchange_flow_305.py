"""Build complete fixed-body offering references and documentary flow (no execution).
Existing public 17MB primary is reused once at build time, never recopied/runtime.
"""
from pathlib import Path
from hashlib import sha256
from html.parser import HTMLParser
import argparse,json,re
from copy import deepcopy

PACK='research/p3-relic-exchange-305'
DATA='rouge/data/relic-exchange-flow.json'
EVENT='community_group_025'
PRIMARY='research/p3-future-region-effects-300/game-topic-complete.json'
PRIMARY_SHA='f5867e55d09472253083486174aa47bd94dd48b07684b74b60a5b29ca00eda86'
CATALOG='rouge/data/node-catalog.json'
CATALOG_SHA='7df1d94bb69650eb19fc811af661e54d44bf07d72b1c0793de511adc1b2e915d'
BWIKI='research/p3-choice-recruitment-290/bwiki-investigation.html'
BWIKI_SHA='26b7768bf3556cf73c24529659c2c92f4095059476f782130bf3fa768422b908'
MAIN='research/p3-future-region-effects-300/prts-main-433770.html'
MAIN_SHA='366e0bf14b526816b20750f1d83b6c7b132d556dfc0b09a0ab3c302fd00610e9'
COMMIT='a550f5e048bb94e7cdefc6eb97a4091f0c4c7add'

class Node:
 def __init__(self,tag,attrs,start):self.tag,self.attrs,self.start,self.end,self.children=tag,dict(attrs),start,None,[]
class Document(HTMLParser):
 VOID={'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
 def __init__(self,source):
  super().__init__(convert_charrefs=True);self.source=source;self.nodes=[];self.offsets=[];offset=0
  for line in source.splitlines(keepends=True):self.offsets.append(offset);offset+=len(line)
  self.stack=[Node('root',[],0)];self.feed(source);self.close()
 def pos(self):line,col=self.getpos();return self.offsets[line-1]+col
 def handle_starttag(self,tag,attrs):
  n=Node(tag,attrs,self.pos());self.nodes.append(n);self.stack[-1].children.append(n)
  if tag in self.VOID:n.end=n.start+len(self.get_starttag_text())
  else:self.stack.append(n)
 def handle_startendtag(self,tag,attrs):
  self.handle_starttag(tag,attrs)
  if tag not in self.VOID:self.handle_endtag(tag)
 def handle_endtag(self,tag):
  end=self.source.find('>',self.pos())+1
  for i in range(len(self.stack)-1,0,-1):
   if self.stack[i].tag==tag:
    for n in self.stack[i:]:n.end=end
    del self.stack[i:];break
 def handle_data(self,data):self.stack[-1].children.append(data)
def text(n):
 if isinstance(n,str):return n
 return ''.join(text(c)+('\n'if isinstance(c,Node)and c.tag in('br','p','li')else'')for c in n.children).strip()
def descendants(n):
 for c in n.children:
  if isinstance(c,Node):yield c;yield from descendants(c)
def cls(n,name):return name in n.attrs.get('class','').split()
def pin(raw):return{'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def jb(value):return(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def require(value,message):
 if not value:raise ValueError(message)
def load(root,path,h=None):
 b=(root/path).read_bytes()
 if h is not None:require(sha256(b).hexdigest()==h,'Source bytes changed: '+path)
 return b

def build(root,output):
 root,output=Path(root),Path(output);pack=output/PACK
 primary=load(root,PRIMARY,PRIMARY_SHA);game=json.loads(primary)['details']['rogue_6'];catalog_raw=load(root,CATALOG,CATALOG_SHA);catalog=json.loads(catalog_raw)
 e=next(e for e in catalog['events']if e['id']==EVENT)
 require(e['title']=='回滚文明'and e['node_types']==['失与得']and len(e['scenes'])==11 and sum(len(s['choices'])for s in e['scenes'])==19,'Full target event changed')
 items={k:deepcopy(v)for k,v in game['items'].items()if v['type']=='RELIC'}
 require(len(items)==272 and sum(x['canSacrifice']is False for x in items.values())==21 and all(type(x['canSacrifice'])is bool for x in items.values()),'Fixed complete 272 item flags changed')
 bwraw=load(root,BWIKI,BWIKI_SHA);bw=bwraw.decode('utf8');bd=Document(bw);heads=[n for n in bd.nodes if n.tag in('h2','h3')]
 at=next(i for i,n in enumerate(heads)if text(n).replace('[编辑]','').strip()=='回滚文明');start,end=heads[at].start,heads[at+1].start
 rows=[]
 for n in bd.nodes:
  if n.tag=='tr'and start<n.start<end:
   cells=[text(c)for c in n.children if isinstance(c,Node)and c.tag in('td','th')]
   if cells:rows.append({'cells':cells,'byte_start':len(bw[:n.start].encode('utf8')),'byte_end':len(bw[:n.end].encode('utf8')),'span_sha256':sha256(bw[n.start:n.end].encode('utf8')).hexdigest()})
 require(len(rows)==28,'Complete BW event structure changed')
 suspicious=[i for i,row in enumerate(rows)if row['cells']==['分支2','有点可疑\n见好就收']]
 require(suspicious==[20,26],'Two independently documented branch positions changed')
 scene_ids=('scene_ro6_sacrifice1_10','scene_ro6_sacrifice1_17','scene_ro6_sacrifice2_10','scene_ro6_sacrifice2_17')
 result_text=game['choiceScenes'][scene_ids[0]]['description']
 require(all(game['choiceScenes'][i]['description']==result_text for i in scene_ids),'Original repeated scene texts changed')
 require(all(rows[i+1]['cells']==[result_text]for i in suspicious),'Complete documentary result differs from original text')
 corner=load(output,PACK+'/notrade-corner-433235.html');collection=load(output,PACK+'/relic-index-current.html');http=load(output,PACK+'/http-source-records.json')
 require(re.findall(r'"wgRevisionId"\s*:\s*(\d+)',corner.decode('utf8'))==['433235'],'Corner actual revision is not433235')
 cd=Document(corner.decode('utf8'));corner_rows=[n for n in cd.nodes if n.tag=='tr'and any(c.tag=='td'and text(c)=='notrade'for c in n.children if isinstance(c,Node))]
 require(len(corner_rows)==1 and '不可于【失与得】交换'in text(corner_rows[0]),'Actual notrade template meaning missing')
 index_text=collection.decode('utf8');require('标志表示收藏品不可在【失与得】节点被交换出去。'in index_text,'Actual collection legend direction missing')
 idx=Document(index_text);cross=[]
 for item_id,item in items.items():
  if item['canSacrifice']:continue
  tables=[n for n in idx.nodes if n.tag=='table'and cls(n,'logo')and any(c.tag=='img'and('/'+item_id+'.png')in c.attrs.get('src','')for c in descendants(n))]
  # Select a leaf card, not an enclosing whole-page table.
  tables=[n for n in tables if not any(c.tag=='table'for c in descendants(n))]
  require(len(tables)==1,'Exact false-flag collection card is not unique: '+item_id)
  card=tables[0];require(item['name']in text(card)and '不可于【失与得】交换'in text(card),'False-flag card lacks actual notrade marker: '+item_id)
  cross.append({'item_id':item_id,'name':item['name'],'canSacrifice':False,'document_revision':re.findall(r'"wgRevisionId"\s*:\s*(\d+)',index_text)[0],
   'byte_start':len(index_text[:card.start].encode('utf8')),'byte_end':len(index_text[:card.end].encode('utf8')),'span_sha256':sha256(index_text[card.start:card.end].encode('utf8')).hexdigest(),'marker_direction':'offering_out_only'})
 main=load(root,MAIN,MAIN_SHA);md=Document(main.decode('utf8'));plain=text(md.stack[0])
 # The complete pinned document supplies these precise mechanics independently.
 main_phrases=('在点亮【生命游戏】的“声带”节点后，还可以交换零件。','在点亮【生命游戏】的“手掌”节点后，交换次数+1，但只能交换和首次交换相同类型的物品。','一部分收藏品','不可用于交换','该节点不会在第I，VI层出现。')
 require(all(p in plain for p in main_phrases),'Full exchange node source changed')
 docrules=[{'rule_id':'offering_semantics','title':'收藏品作为提供物','text':'可供出旗标只核对把收藏品交换出去；不能用它决定奖励会得到什么。','source_refs':[{'file':PACK+'/notrade-corner-433235.html','revision':'433235','meaning':'notrade'},{'file':PACK+'/relic-index-current.html','meaning':'legend_and21_exact_negative_cards'}]},
 {'rule_id':'palm_second_same_type','title':'第二次交换','text':'点亮生命游戏“手掌”后交换次数+1；第二次只能与首次同为收藏品或同为零件。账户实际科技与剩余次数未知。','source_refs':[{'file':MAIN,'text':main_phrases[1]}]},
 {'rule_id':'vocal_cords_scrap_only','title':'零件交换条件','text':'文献记载点亮“声带”后还能交换零件；不要把这个零件条件套给收藏品交换。原零件交换工具继续单独使用。','source_refs':[{'file':MAIN,'text':main_phrases[0]}]}]
 notices=['这里是回滚文明事件（失与得节点）的固定资料说明，不代表本局已进入或已经选择。',
 '固定本体原表覆盖272件收藏品，251项可供出旗标为真、21项为假；当前内容拓展与服务器完整目录不在本范围。',
 '收藏品与零件是两类交换物；零件的加工品、自然物、概念体子类不能代替这个分类。',
 '手掌增加的第二次交换须与首次同类；实际科技、持有、可选、消耗与剩余次数未知。',
 '只查“交出去”的原资料与声明；不列奖励候选池，不从稀有度推奖励档次、数量或概率。',
 '说明参考与社区导航不是已确认的游戏按钮；空后续也不能认定游戏已经结束。']
 choice_rows=[];unknown_target_keys={EVENT+':scene:3:choice:1':0,EVENT+':scene:7:choice:1':1}
 for scene in e['scenes']:
  for ch in scene['choices']:
   rules=[];supplement=None;candidates=[];results=[]
   for dest in ch['destination_keys']:
    target=next(s for s in e['scenes']if s['key']==dest)
    results.append({'scene_key':dest,'description':target['description'],'game_scene_ids':target['game_scene_ids'],'evidence':'existing_fixed_community_navigation','actual_reached':None})
   if ch['key']in unknown_target_keys:
    branch=unknown_target_keys[ch['key']];ri=suspicious[branch]
    supplement=result_text;candidates=[deepcopy(game['choiceScenes'][key])for key in scene_ids]
    rules=[{'rule_id':'documented_stop_after_exchange','title':'见好就收的资料结果','text':'另一份完整文献分别在藏品和零件分支写出同一结果；这不恢复原服务器入口，也不证明本局已经离开。',
     'source_refs':[{'file':BWIKI,'revision':'349818','choice_row':rows[ri],'result_row':rows[ri+1],'branch_label':'选项一分支'if branch==0 else'选项二分支'}]}]
   if ch['title']in('复原藏品','复原零件','继续赞助它','继续交换（需要能力加成）','到此为止'):
    rules+=deepcopy(docrules[1:])
   choice_rows.append({'event_id':EVENT,'scene_key':scene['key'],'choice_key':ch['key'],'reference_id':ch['key'],
    'choice_title':ch['title'],'choice_description':ch['description'],'condition_text':ch['conditional'],'presentation_role':ch['presentation_role'],
    'catalog_choice':deepcopy(ch),'documented_rules':rules,'documented_result_text':supplement,
    'original_scene_candidates':candidates,'documented_destinations':results,'related_stage_reference':None,'source_scene_link_verified':False,
    'original_choice_ids':deepcopy(ch['game_choice_ids']),'current_actual_original_candidate':None})
 catalogue=[{'item_id':k,'name':v['name'],'rarity':v['rarity'],'canSacrifice':v['canSacrifice'],'item':deepcopy(v)}for k,v in items.items()]
 source={'primary':{'file':PRIMARY,**pin(primary),'commit':COMMIT,'url':f'https://raw.githubusercontent.com/Kengxxiao/ArknightsGameData/{COMMIT}/zh_CN/gamedata/excel/roguelike_topic_table.json'},
  'catalog':{'file':CATALOG,**pin(catalog_raw),'revision':'427904'},'documents':[
  {'file':BWIKI,**pin(bwraw),'revision':'349818','url':'https://wiki.biligame.com/arknights/沉沦者的黑流树海/调查记录'},
  {'file':MAIN,**pin(main),'revision':'433770','url':'https://m.prts.wiki/w/沉沦者的黑流树海?oldid=433770'},
  {'file':PACK+'/notrade-corner-433235.html',**pin(corner),'revision':'433235','url':'https://m.prts.wiki/w/模板:收藏品/角标'},
  {'file':PACK+'/relic-index-current.html',**pin(collection),'revision':'441474','url':'https://m.prts.wiki/w/沉沦者的黑流树海/拟造物质编目'}]}
 authority={'schema':'relic_exchange_flow_selected_authority_v1','complete_event':deepcopy(e),'complete_items':items,'complete_catalogue':catalogue,
  'documented_choice_rows':choice_rows,'flow_notices':notices,'source':source,'full_bwiki_event_rows':rows,
  'complete_original_scene_candidates':{k:game['choiceScenes'][k]for k in scene_ids},
  'complete_original_destination_choices':{k.replace('scene_','choice_'):game['choices'][k.replace('scene_','choice_')]for k in scene_ids},
  'negative_flags21_independent_documentary_cards':cross,'can_sacrifice_false_count':21,
  'source_original_entry_restored':False,'server_behavior_recovered':False}
 unknowns={key:None for key in('actual_consumed','actual_reward_pool','actual_selectable','actual_eligible','actual_offered_consumed','actual_reward','actual_quantity','actual_choice','actual_scene','actual_transition','actual_inventory','quantity','reward_pool')}
 data={'schema':'relic_exchange_flow_v1','expected_event':e,'scenes':e['scenes'],'choices':choice_rows,'catalogue':catalogue,'flow_notices':notices,'source':source,
  'catalogue_scope':{'label':'固定本体272件收藏品原资料','total':272,'offer_true':251,'offer_false':21,'current_complete_catalogue':False,'game_commit':COMMIT},
  'notice':'只读交换提供物和完整文献流程，不作为奖励池或当前游戏可选性判断。',**unknowns,
  'inventory_updated':False,'calculation_applied':False,'run_state_updated':False,'current_server_verified':False,'original_entry_restored':False}
 outputs={DATA:jb(data),PACK+'/selected-authority-records.json':jb(authority)}
 runtime={name:pin(raw)for name,raw in outputs.items()};runtime[CATALOG]=pin(catalog_raw)
 manifest={'schema':'relic_exchange_flow_source_manifest_v1','data_file':DATA,'data_sha256':sha256(outputs[DATA]).hexdigest(),'runtime_files':runtime,
  'complete_primary_runtime_read':False,'complete_primary_build_pin':source['primary'],'build_source_documents':source['documents'],
  'all_runtime_members_required_for_each_target_query':True,'private_state_or_game_capture_used':False}
 outputs[PACK+'/source-manifest.json']=jb(manifest)
 template_path=pack/'backend-template.py';template=template_path.read_text(encoding='utf8')
 module=template.replace('__DATA_SHA__',sha256(outputs[DATA]).hexdigest()).replace('__MANIFEST_SHA__',sha256(outputs[PACK+'/source-manifest.json']).hexdigest()).replace('__ITEM_IDS__',' '.join(items)).replace('__CHOICE_KEYS__',' '.join(row['choice_key']for row in choice_rows))
 outputs['rouge/relic_exchange_flow.py']=module.encode('utf8')
 for name,raw in outputs.items():target=output/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
 result={'kind':'actual_source_build_not_product_acceptance','items':272,'true_flags':251,'false_flags':21,'negative_flags_crosschecked_in_complete_current_index':len(cross),'event_scenes':11,'choice_rows':19,'new_documented_results':2,'original_result_candidates_each':4,'source_original_entry_restored':False,'outputs':{name:pin(raw)for name,raw in outputs.items()}}
 (pack/'build-receipt.json').write_bytes(jb(result));return result
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);parser.add_argument('--output-root',type=Path,required=True);a=parser.parse_args();print(json.dumps(build(a.root,a.output_root),ensure_ascii=False))
