"""Fixed-body relic offering and complete documentary exchange flow; no grant API."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path, PurePosixPath

ROOT=Path(__file__).resolve().parents[1]
PACK='research/p3-relic-exchange-305'
DATA='rouge/data/relic-exchange-flow.json'
MANIFEST=PACK+'/source-manifest.json'
AUTHORITY=PACK+'/selected-authority-records.json'
DATA_SHA256='__DATA_SHA__'
MANIFEST_SHA256='__MANIFEST_SHA__'
EVENT_ID='community_group_025'
ITEM_IDS=tuple('__ITEM_IDS__'.split())
CHOICE_KEYS=tuple('__CHOICE_KEYS__'.split())
RARITY_LABELS={'NORMAL':'低稀有度','RARE':'中稀有度','SUPER_RARE':'高稀有度'}
ACTUAL_FIELDS=('actual_consumed','actual_reward_pool','actual_selectable','actual_eligible','actual_offered_consumed','actual_reward',
 'actual_quantity','actual_choice','actual_scene','actual_transition','actual_inventory','quantity','reward_pool')


def _unknown():return {**{key:None for key in ACTUAL_FIELDS},'inventory_updated':False,'calculation_applied':False,'run_state_updated':False}
def _same(a,b):
 if type(a)is not type(b):return False
 if type(b)is dict:return a.keys()==b.keys()and all(type(k)is str and _same(a[k],b[k])for k in b)
 if type(b)is list:return len(a)==len(b)and all(_same(x,y)for x,y in zip(a,b))
 return a==b

def _file(name):
 p=PurePosixPath(name)
 if type(name)is not str or p.is_absolute()or'..'in p.parts or'\\'in name or':'in name:raise ValueError('Invalid public source path')
 target=ROOT.joinpath(*p.parts)
 if target.is_symlink()or not target.is_file()or not target.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Regular source inside project required')
 return target

def _packet():
 try:
  raw=_file(MANIFEST).read_bytes()
  if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
  manifest=json.loads(raw)
  if(manifest['schema']!='relic_exchange_flow_source_manifest_v1'or manifest['data_file']!=DATA
   or manifest['data_sha256']!=DATA_SHA256 or manifest['complete_primary_runtime_read']is not False):return None
  blobs={}
  for name,pin in manifest['runtime_files'].items():
   raw=_file(name).read_bytes()
   if type(pin['bytes'])is not int or len(raw)!=pin['bytes']or sha256(raw).hexdigest()!=pin['sha256']:return None
   blobs[name]=raw
  if set(blobs)!={DATA,AUTHORITY,'rouge/data/node-catalog.json'}:return None
  d=json.loads(blobs[DATA]);a=json.loads(blobs[AUTHORITY]);c=json.loads(blobs['rouge/data/node-catalog.json'])
  e=next(x for x in c['events']if x['id']==EVENT_ID)
  if(d['schema']!='relic_exchange_flow_v1'or not _same(d['expected_event'],e)or not _same(a['complete_event'],e)
   or not _same(d['choices'],a['documented_choice_rows'])or not _same(d['catalogue'],a['complete_catalogue'])
   or len(d['scenes'])!=11 or not _same(d['scenes'],e['scenes'])or len(d['choices'])!=19
   or tuple(x['choice_key']for x in d['choices'])!=CHOICE_KEYS or tuple(x['item_id']for x in d['catalogue'])!=ITEM_IDS
   or len(ITEM_IDS)!=272 or sum(x['canSacrifice']is False for x in d['catalogue'])!=21):return None
  if not _same(d['flow_notices'],a['flow_notices'])or not _same(d['source'],a['source']):return None
  for row in d['catalogue']:
   item=a['complete_items'][row['item_id']]
   if(type(row['canSacrifice'])is not bool or item['type']!='RELIC'or not _same(row['item'],item)
    or not _same([row['name'],row['rarity'],row['canSacrifice']],[item['name'],item['rarity'],item['canSacrifice']])):return None
  for row in d['choices']:
   scene=next(x for x in e['scenes']if x['key']==row['scene_key'])
   choice=next(x for x in scene['choices']if x['key']==row['choice_key'])
   if(row['event_id']!=EVENT_ID or row['reference_id']!=row['choice_key']or not _same(row['catalog_choice'],choice)
    or row['related_stage_reference']is not None or row['source_scene_link_verified']is not False):return None
  if any(d.get(k)is not None for k in ACTUAL_FIELDS)or any(d.get(k)is not False for k in('inventory_updated','calculation_applied','run_state_updated','current_server_verified','original_entry_restored')):return None
  # Recheck the complete public target object against legacy mutable cache too.
  from . import node_catalog
  if not _same(node_catalog._event(EVENT_ID),e):return None
  return deepcopy(d)
 except(OSError,ValueError,TypeError,KeyError,AttributeError,StopIteration,IndexError,RecursionError,UnicodeError):return None

def _unavailable(**extra):
 return{'target':True,'status':'source_unavailable','source_valid':False,'event_id':EVENT_ID,
  'event_title':None,'scope_key':None,'catalogue':[],'scenes':[],'choices':[],'flow_notices':[],
  'reference':None,'source':None,'source_reference':None,'source_identity':None,'item':None,'can_offer_reference':None,
  'checks':[],'documented_condition_status':'unknown',**_unknown(),**extra,
  'notice':'交换资料暂时无法核对；旧物品、流程与结果已清除，恢复后请重新选择。'}

def source_data():return _packet()

def _common(packet):
 return{'target':True,'status':'documented_reference','source_valid':True,'event_id':EVENT_ID,
  'event_title':'回滚文明','rarity_labels':deepcopy(RARITY_LABELS),'scope_key':EVENT_ID+':'+DATA_SHA256+':'+MANIFEST_SHA256,
  'catalogue_scope':deepcopy(packet['catalogue_scope']),'flow_notices':deepcopy(packet['flow_notices']),
  'source_identity':{'manifest_sha256':MANIFEST_SHA256,'data_sha256':DATA_SHA256},
  'source':deepcopy(packet['source']),'source_reference':{'manifest_sha256':MANIFEST_SHA256,'data_sha256':DATA_SHA256},
  'current_server_verified':False,'original_entry_restored':False,**_unknown(),
  'notice':packet['notice']}

def event_reference(event_id):
 if type(event_id)is not str or event_id!=EVENT_ID:return None
 p=_packet()
 if p is None:return _unavailable()
 return{**_common(p),'scenes':p['scenes'],'choices':p['choices'],'catalogue':p['catalogue']}

def choice_details(event_id,scene_key,choice_key):
 if(type(event_id)is not str or event_id!=EVENT_ID or type(scene_key)is not str or type(choice_key)is not str
  or choice_key not in CHOICE_KEYS or scene_key!=choice_key.rsplit(':choice:',1)[0]):return None
 p=_packet()
 if p is None:return _unavailable()
 row=next(x for x in p['choices']if x['choice_key']==choice_key)
 return{**_common(p),'reference':row,'related_stage_reference':None}

def relic_offer_reference(item_id,*,exchange_index=1,first_exchange_item_type=None,palm_unlocked=None,owned=None):
 if type(item_id)is not str or item_id not in ITEM_IDS:return None
 if type(exchange_index)is not int or exchange_index not in(1,2):raise ValueError('交换次数只能是整数1或2，不能把布尔值当次数。')
 if first_exchange_item_type not in(None,'RELIC','SCRAP')or (first_exchange_item_type is not None and type(first_exchange_item_type)is not str):raise ValueError('首次类型只能是收藏品、零件或未知。')
 if exchange_index==1 and first_exchange_item_type is not None:raise ValueError('首次交换尚无先前类型；不能同时声明已发生首次交换。')
 if any(v is not None and type(v)is not bool for v in(palm_unlocked,owned)):raise ValueError('持有及手掌声明只能是真、假或未知。')
 p=_packet()
 if p is None:return _unavailable(item_id=item_id,exchange_index=exchange_index)
 item=next(x for x in p['catalogue']if x['item_id']==item_id)
 checks=[{'key':'offering_flag','matches':item['canSacrifice'],'title':'原资料可否作为提供物','text':'原表可供出旗标只用于交换出去；不代表能否作为奖励得到。'},
  {'key':'owned_declaration','matches':owned,'title':'声明持有','text':'持有仅是本次离线声明；没有读取实际库存或预扣物品。'}]
 if exchange_index==2:
  checks.extend([{'key':'palm_declaration','matches':palm_unlocked,'title':'第二次交换的手掌条件','text':'文献记载点亮手掌后交换次数+1；实际剩余交换次数未知。'},
   {'key':'same_first_type','matches':None if first_exchange_item_type is None else first_exchange_item_type=='RELIC','title':'与首次同为收藏品','text':'第二次应与首次同属收藏品；零件子类、物品稀有度不能代替这个类型。'}])
 values=[x['matches']for x in checks]
 state='excluded'if False in values else'unknown'if None in values else'matched'
 return{**_common(p),'item_id':item_id,'name':item['name'],'rarity':item['rarity'],'item':item['item'],
  'can_offer_reference':item['canSacrifice'],'canSacrifice':item['canSacrifice'],'checks':checks,
  'documented_condition_status':state,'exchange_index':exchange_index,'first_exchange_item_type_declared':first_exchange_item_type,
  'palm_unlocked_declared':palm_unlocked,'owned_declared':owned,
  'documented_conditions_are_actual_selectability':False,'complete_reward_pool_known':False,
  'reward_rarity_inferred':False,'offering_flag_used_for_reward_side':False,
  'condition_notice':'只核对已列资料与声明；条件相符仍不代表游戏中此刻可选、实际消耗或当前服务器完整资格。'}
