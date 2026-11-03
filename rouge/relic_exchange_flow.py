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
DATA_SHA256='30335cce9fd13f1a00e9fffde109ce813f48fa6537632a8913ed452ec1536929'
MANIFEST_SHA256='acd83e3d1d94b888bf5e9b0b8fb54771341b5bcc2c446e2906cbee57b90e661d'
EVENT_ID='community_group_025'
ITEM_IDS=tuple('rogue_6_relic_legacy_1 rogue_6_relic_legacy_2 rogue_6_relic_legacy_3 rogue_6_relic_legacy_4 rogue_6_relic_legacy_5 rogue_6_relic_legacy_6 rogue_6_relic_legacy_7 rogue_6_relic_legacy_8 rogue_6_relic_legacy_9 rogue_6_relic_legacy_10 rogue_6_relic_legacy_11 rogue_6_relic_legacy_12 rogue_6_relic_legacy_13 rogue_6_relic_legacy_14 rogue_6_relic_legacy_15 rogue_6_relic_legacy_16 rogue_6_relic_legacy_17 rogue_6_relic_legacy_18 rogue_6_relic_legacy_19 rogue_6_relic_legacy_20 rogue_6_relic_legacy_21 rogue_6_relic_legacy_22 rogue_6_relic_legacy_22_a rogue_6_relic_legacy_22_b rogue_6_relic_legacy_22_c rogue_6_relic_legacy_23 rogue_6_relic_legacy_23_a rogue_6_relic_legacy_23_b rogue_6_relic_legacy_23_c rogue_6_relic_legacy_24 rogue_6_relic_legacy_24_a rogue_6_relic_legacy_24_b rogue_6_relic_legacy_24_c rogue_6_relic_legacy_25 rogue_6_relic_legacy_25_a rogue_6_relic_legacy_25_b rogue_6_relic_legacy_25_c rogue_6_relic_legacy_26 rogue_6_relic_legacy_26_a rogue_6_relic_legacy_26_b rogue_6_relic_legacy_26_c rogue_6_relic_legacy_27 rogue_6_relic_legacy_27_a rogue_6_relic_legacy_27_b rogue_6_relic_legacy_27_c rogue_6_relic_legacy_28 rogue_6_relic_legacy_28_a rogue_6_relic_legacy_28_b rogue_6_relic_legacy_28_c rogue_6_relic_legacy_29 rogue_6_relic_legacy_29_a rogue_6_relic_legacy_29_b rogue_6_relic_legacy_29_c rogue_6_relic_legacy_30 rogue_6_relic_legacy_30_a rogue_6_relic_legacy_30_b rogue_6_relic_legacy_30_c rogue_6_relic_legacy_31 rogue_6_relic_legacy_31_a rogue_6_relic_legacy_31_b rogue_6_relic_legacy_31_c rogue_6_relic_legacy_32 rogue_6_relic_legacy_33 rogue_6_relic_legacy_34 rogue_6_relic_legacy_35 rogue_6_relic_legacy_36 rogue_6_relic_legacy_37 rogue_6_relic_legacy_38 rogue_6_relic_legacy_39 rogue_6_relic_legacy_40 rogue_6_relic_legacy_41 rogue_6_relic_legacy_42 rogue_6_relic_legacy_43 rogue_6_relic_legacy_44 rogue_6_relic_legacy_45 rogue_6_relic_legacy_45_a rogue_6_relic_legacy_45_b rogue_6_relic_legacy_45_c rogue_6_relic_legacy_46 rogue_6_relic_legacy_46_a rogue_6_relic_legacy_46_b rogue_6_relic_legacy_46_c rogue_6_relic_legacy_47 rogue_6_relic_legacy_47_a rogue_6_relic_legacy_47_b rogue_6_relic_legacy_47_c rogue_6_relic_legacy_48 rogue_6_relic_legacy_49 rogue_6_relic_legacy_50 rogue_6_relic_legacy_51 rogue_6_relic_legacy_52 rogue_6_relic_legacy_53 rogue_6_relic_legacy_54 rogue_6_relic_legacy_55 rogue_6_relic_legacy_56 rogue_6_relic_legacy_57 rogue_6_relic_legacy_58 rogue_6_relic_legacy_59 rogue_6_relic_legacy_60 rogue_6_relic_legacy_61 rogue_6_relic_legacy_62 rogue_6_relic_legacy_63 rogue_6_relic_legacy_64 rogue_6_relic_legacy_65 rogue_6_relic_legacy_66 rogue_6_relic_legacy_67 rogue_6_relic_legacy_68 rogue_6_relic_legacy_69 rogue_6_relic_legacy_70 rogue_6_relic_legacy_71 rogue_6_relic_legacy_72 rogue_6_relic_legacy_73 rogue_6_relic_legacy_74 rogue_6_relic_legacy_75 rogue_6_relic_legacy_76 rogue_6_relic_legacy_77 rogue_6_relic_legacy_78 rogue_6_relic_legacy_79 rogue_6_relic_legacy_80 rogue_6_relic_legacy_81 rogue_6_relic_legacy_82 rogue_6_relic_legacy_83 rogue_6_relic_legacy_84 rogue_6_relic_legacy_85 rogue_6_relic_legacy_86 rogue_6_relic_legacy_87 rogue_6_relic_legacy_88 rogue_6_relic_legacy_89 rogue_6_relic_legacy_90 rogue_6_relic_legacy_91 rogue_6_relic_legacy_92 rogue_6_relic_legacy_93 rogue_6_relic_legacy_94 rogue_6_relic_legacy_95 rogue_6_relic_legacy_96 rogue_6_relic_legacy_97 rogue_6_relic_legacy_98 rogue_6_relic_legacy_99 rogue_6_relic_legacy_100 rogue_6_relic_legacy_101 rogue_6_relic_legacy_102 rogue_6_relic_legacy_103 rogue_6_relic_legacy_104 rogue_6_relic_legacy_105 rogue_6_relic_legacy_106 rogue_6_relic_legacy_107 rogue_6_relic_legacy_108 rogue_6_relic_legacy_109 rogue_6_relic_legacy_110 rogue_6_relic_legacy_111 rogue_6_relic_legacy_113 rogue_6_relic_legacy_114 rogue_6_relic_legacy_115 rogue_6_relic_legacy_116 rogue_6_relic_legacy_117 rogue_6_relic_legacy_118 rogue_6_relic_legacy_119 rogue_6_relic_legacy_120 rogue_6_relic_legacy_121 rogue_6_relic_legacy_122 rogue_6_relic_legacy_123 rogue_6_relic_legacy_124 rogue_6_relic_legacy_125 rogue_6_relic_legacy_126 rogue_6_relic_legacy_127 rogue_6_relic_legacy_128 rogue_6_relic_legacy_129 rogue_6_relic_legacy_130 rogue_6_relic_legacy_131 rogue_6_relic_legacy_132 rogue_6_relic_legacy_133 rogue_6_relic_legacy_134 rogue_6_relic_legacy_135 rogue_6_relic_legacy_136 rogue_6_relic_legacy_137 rogue_6_relic_legacy_138 rogue_6_relic_legacy_139 rogue_6_relic_legacy_140 rogue_6_relic_legacy_141 rogue_6_relic_legacy_142 rogue_6_relic_cargo_1 rogue_6_relic_cargo_2 rogue_6_relic_cargo_3 rogue_6_relic_cargo_4 rogue_6_relic_cargo_5 rogue_6_relic_cargo_6 rogue_6_relic_cargo_7 rogue_6_relic_cargo_8 rogue_6_relic_cargo_9 rogue_6_relic_cargo_10 rogue_6_relic_cargo_11 rogue_6_relic_cargo_12 rogue_6_relic_cargo_13 rogue_6_relic_cargo_14 rogue_6_relic_fight_1 rogue_6_relic_fight_2 rogue_6_relic_fight_3 rogue_6_relic_fight_4 rogue_6_relic_fight_5 rogue_6_relic_fight_6 rogue_6_relic_fight_7 rogue_6_relic_fight_8 rogue_6_relic_fight_9 rogue_6_relic_fight_10 rogue_6_relic_fight_11 rogue_6_relic_fight_12 rogue_6_relic_fight_13 rogue_6_relic_fight_14 rogue_6_relic_fight_15 rogue_6_relic_fight_16 rogue_6_relic_fight_17 rogue_6_relic_fight_18 rogue_6_relic_fight_19 rogue_6_relic_fight_20 rogue_6_relic_fight_21 rogue_6_relic_fight_22 rogue_6_relic_fight_23 rogue_6_relic_fight_24 rogue_6_relic_fight_25 rogue_6_relic_fight_26 rogue_6_relic_fight_27 rogue_6_relic_fight_28 rogue_6_relic_fight_29 rogue_6_relic_fight_30 rogue_6_relic_hand_1 rogue_6_relic_hand_2 rogue_6_relic_hand_3 rogue_6_relic_hand_4 rogue_6_relic_hand_5 rogue_6_relic_hand_6 rogue_6_relic_hand_7 rogue_6_relic_book_1 rogue_6_relic_book_2 rogue_6_relic_book_3 rogue_6_relic_book_4 rogue_6_relic_book_5 rogue_6_relic_book_6 rogue_6_relic_book_7 rogue_6_relic_assign_1 rogue_6_relic_assign_2 rogue_6_relic_assign_3 rogue_6_relic_assign_4 rogue_6_relic_assign_5 rogue_6_relic_assign_6 rogue_6_relic_assign_7 rogue_6_relic_assign_8 rogue_6_relic_assign_9 rogue_6_relic_assign_10 rogue_6_relic_assign_11 rogue_6_relic_assign_12 rogue_6_relic_assign_13 rogue_6_relic_assign_14 rogue_6_relic_assign_15 rogue_6_relic_artifact_1 rogue_6_relic_artifact_2 rogue_6_relic_artifact_3 rogue_6_relic_artifact_4 rogue_6_relic_artifact_5 rogue_6_relic_artifact_6 rogue_6_relic_artifact_7 rogue_6_relic_final_1 rogue_6_relic_final_2 rogue_6_relic_final_3 rogue_6_relic_final_4 rogue_6_relic_final_5 rogue_6_relic_final_6 rogue_6_start_1 rogue_6_start_2 rogue_6_start_3 rogue_6_start_4 rogue_6_start_5 rogue_6_start_6'.split())
CHOICE_KEYS=tuple('community_group_025:scene:0:choice:0 community_group_025:scene:0:choice:1 community_group_025:scene:0:choice:2 community_group_025:scene:0:choice:3 community_group_025:scene:2:choice:0 community_group_025:scene:2:choice:1 community_group_025:scene:2:choice:2 community_group_025:scene:2:choice:3 community_group_025:scene:3:choice:0 community_group_025:scene:3:choice:1 community_group_025:scene:4:choice:0 community_group_025:scene:6:choice:0 community_group_025:scene:6:choice:1 community_group_025:scene:6:choice:2 community_group_025:scene:6:choice:3 community_group_025:scene:7:choice:0 community_group_025:scene:7:choice:1 community_group_025:scene:8:choice:0 community_group_025:scene:9:choice:0'.split())
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
