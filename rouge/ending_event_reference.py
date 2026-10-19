"""Declared event conditions, not live eligibility or route recommendations."""
from pathlib import Path,PurePosixPath
from hashlib import sha256
from copy import deepcopy
import json
from . import current_battle_reference as battle
ROOT=Path(__file__).resolve().parents[1];PACK='research/p3-ending-events-316';DATA='rouge/data/ending-events-reference.json';MANIFEST=PACK+'/runtime-manifest.json';MANIFEST_SHA256='bc8803e08c6983bd470460d9b0b13dd20444b311be4f252007895d61f5a58527'
BOOL_FIELDS=('post_update_clear','has_prayer','has_covenant','adventurer_alive','next_unmarked_after_first_down','rescue_used')
DEFAULT_CONTEXT={'scope':'current','floor':None,'region':'unknown','node_type':'unknown','gold':None,**{k:None for k in BOOL_FIELDS}}

def packet():
 try:
  raw=(ROOT/MANIFEST).read_bytes()
  if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
  manifest=json.loads(raw)
  if manifest['schema']!='ending_events_316_manifest_v1'or manifest['game_commit']!=battle.version.NEW_COMMIT:return None
  values={}
  for name,pin in manifest['files'].items():
   rel=PurePosixPath(name)
   if rel.is_absolute()or'..'in rel.parts or'\\'in name or':'in name:return None
   path=ROOT.joinpath(*rel.parts)
   if path.is_symlink()or not path.resolve().is_relative_to(ROOT.resolve()):return None
   content=path.read_bytes()
   if len(content)!=pin['bytes']or sha256(content).hexdigest()!=pin['sha256']:return None
   values[name]=content
  data=json.loads(values[DATA]);current=battle.packet()
  if current is None:return None
  originals=json.loads(values['research/p3-expansion-313/current-topic.json'])['details']
  for name in('choices','items','stages','scenes'):
   table='choiceScenes'if name=='scenes'else name
   for key,record in data['selected_originals'][name].items():
    if originals[table].get(key)!=record:return None
  return {'data':data,'current':current,'identity':MANIFEST_SHA256,'actual_eligible':None,'run_updated':False}
 except(OSError,ValueError,KeyError,TypeError,UnicodeError):return None

def context(values=None):
 if values is not None and type(values)is not dict:raise ValueError('条件需要对象。')
 result=deepcopy(DEFAULT_CONTEXT);values=values or{}
 if set(values)-set(result):raise ValueError('条件字段未支持。')
 result.update(values)
 if result['scope']not in('current','future','history')or result['region']not in('unknown','main','熄日余径','盲目者所见'):raise ValueError('查看范围或区域未支持。')
 if result['node_type']not in('unknown','险路尽头','命运所指','不期而遇','普通作战','紧急作战','险路恶敌'):raise ValueError('节点类型未支持。')
 if result['floor']is not None and(type(result['floor'])is not int or result['floor']not in range(1,7)):raise ValueError('主层应为1至6或未知。')
 if result['gold']is not None and(type(result['gold'])is not int or result['gold']<0):raise ValueError('源石锭应为非负整数或未知。')
 for key in BOOL_FIELDS:
  if result[key]is not None and type(result[key])is not bool:raise ValueError('状态应为是、否或未知。')
 return result

def _eq(value,expected):return None if value in(None,'unknown')else value==expected
def evaluate(identity,values=None):
 ref=packet()
 if ref is None:return None
 record=next((r for r in ref['data']['records']if r['id']==identity),None)
 if record is None:return None
 c=context(values);checks=[];options={};notes=[]
 def add(label,value,scope='event_reference'):checks.append({'label':label,'matches':value,'scope':scope})
 def option(cid,label,value):options.setdefault(cid,[]).append({'label':label,'matches':value,'scope':'choice_reference'})
 if identity=='entry':
  add('当前节点是险路尽头',_eq(c['node_type'],'险路尽头'));add('属于第一或第二主层',None if c['floor']is None else c['floor']in(1,2))
  option('choice_ro6_final1_8','更新后已完成一次结局，相关藏品解锁',c['post_update_clear']);option('choice_ro6_final1_8','足够支付10源石锭',None if c['gold']is None else c['gold']>=10)
  notes+=['钱不足影响消费选项，不据此判定整个事件不存在。']
 elif identity=='side_path':
  if c['scope']=='future'and c['region']=='main':
   add('持有谒日之祈',c['has_prayer'],'future_generation');add('主层从第三层起',None if c['floor']is None else c['floor']>=3,'future_generation');add('未持有停止后续余径出现的祭日之契',None if c['has_covenant']is None else not c['has_covenant'],'future_generation')
  else:notes+=['后续生成条件只核对“下一层生成条件＋主要区域”；不会删除当前或历史已出现的节点。']
 elif identity=='path_bonus':add('区域为熄日余径',_eq(c['region'],'熄日余径'));add('节点为普通作战',_eq(c['node_type'],'普通作战'))
 elif identity=='button':
  add('位于熄日余径',_eq(c['region'],'熄日余径'));add('当前节点为命运所指',_eq(c['node_type'],'命运所指'));option('choice_ro6_end4_1','探险家仍存活',c['adventurer_alive']);notes+=['存活条件只检查推进选项；拒绝选项及整个事件的实际资格不随之推定。']
 elif identity=='revive':
  add('当前为不期而遇',_eq(c['node_type'],'不期而遇'));add('是首次倒下后的下一个无标记不期而遇',c['next_unmarked_after_first_down']);add('本局救援机会尚未用过',None if c['rescue_used']is None else not c['rescue_used'])
 elif identity=='blueprint':notes+=['完整出现前置和节点类型没有明确依据；不在任意同类节点上自动判为可能出现。']
 elif identity=='hidden_region':add('查看盲目者所见区域',_eq(c['region'],'盲目者所见'));notes+=['这只是区域内关卡对应；进入隐藏层的完整执行条件仍未恢复。']
 contradictions=[]
 if c['post_update_clear']is False and(c['has_prayer']is True or c['has_covenant']is True):contradictions+=['持有结局关键藏品与“更新后未通关”的声明可能不一致；不会自动修正任一状态。']
 historical=c['scope']=='history'
 def status(rows):return 'reference_only'if historical else'not_matched'if any(x['matches']is False for x in rows)else'unknown'if not rows or any(x['matches']is None for x in rows)or contradictions else'listed_matched'
 result={'record':deepcopy(record),'context':c,'event_checks':checks,'listed_conditions_status':status(checks),'choice_checks':options,'choice_conditions_status':{k:status(v)for k,v in options.items()},'notes':notes,'contradictions':contradictions,'historical_reference_only':historical,
         'source_identity':ref['identity'],'source':ref['data']['source'],'originals':deepcopy(ref['data']['selected_originals']),'actual_event_eligible':None,'actual_choice_eligible':None,'actual_reward':None,'memory_updated':False,'probability':None}
 result['battle_choices']=[deepcopy(result['originals']['stages'][sid])for sid in record['stage_ids']]
 return result

def player_text(result):
 r=result['record'];labels={'listed_matched':'已列条件相符，其他前置仍待核对','not_matched':'有已列条件不符','unknown':'条件尚未读全或来源未明确','reference_only':'历史资料，仅供回看'}
 lines=[r['title'],'','【这项信息说明什么】',*r['facts'],'','【已列条件核对】',labels[result['listed_conditions_status']]]
 for check in result['event_checks']:lines+=[check['label']+'：'+('未知'if check['matches']is None else'相符'if check['matches']else'不符')]
 for cid in r['choice_ids']:
  choice=result['originals']['choices'][cid];lines+=['','【选项】'+choice['title'],battle.plain(choice['description'])]
  for check in result['choice_checks'].get(cid,[]):lines+=[check['label']+'：'+('未知'if check['matches']is None else'相符'if check['matches']else'不符')]
  target=choice.get('nextSceneId')
  if target:lines+=['原选项明确指向后续场景：'+result['originals']['scenes'][target]['title']+'。场景到选项的完整脚本仍未恢复。']
  item_id=(choice.get('displayData')or{}).get('itemId')
  if item_id in result['originals']['items']:lines+=['关联收藏品：'+result['originals']['items'][item_id]['name']]
 for iid in r['item_ids']:
  item=result['originals']['items'][iid];lines+=['','【相关收藏品】'+item['name'],battle.plain(item['usage'])]
 if result['battle_choices']:lines+=['','【相关作战】','可手动选择查看固定原图、敌人、出怪与奖励资料；同名配置保持分开，不代替判断当前实际版本。']
 lines+=['',*result['notes'],*result['contradictions'],'','【仍需分清】','条件相符不等于实际出现、可选、已领取或进入；未知不当作否。历史与当前节点不会因这里的核对被清空，也不计算生成概率。']
 return '\n'.join(lines)
