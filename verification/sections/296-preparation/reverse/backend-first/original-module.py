"""Exact fixed-battle to documented event-choice reading, never actual entry."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from . import event_planning

ROOT=Path(__file__).resolve().parents[1]
DATA='rouge/data/battle-event-references.json'
MANIFEST='research/p3-battle-event-references-296/source-manifest.json'
MANIFEST_SHA256='c6a7d1294e48b6fec896f736d56baa0c09f25f3365de471cc11c88d74705de21'
STAGE_IDS=('ro6_t_1','ro6_t_2','ro6_t_3','ro6_t_4','ro6_t_5','ro6_e_t_3','ro6_e_t_4','ro6_e_t_5')
EVENT_IDS=('community_group_012','community_group_013','community_group_014','community_group_015','community_group_016')
_CACHE={}
NOTICE='这是资料中与固定战斗对应的事件选项，不代表本局发生、可选或已进入；所列主层仅属于该事件资料，不是作战全部入口。'

def _sha(raw):return hashlib.sha256(raw).hexdigest()
def _same(value,expected):
 if type(value)is not type(expected):return False
 if type(expected)is dict:
  return(value.keys()==expected.keys()and all(type(key)is str for key in value)
   and all(type(key)is str and _same(value[key],expected[key])for key in expected))
 if type(expected)is list:return len(value)==len(expected)and all(_same(a,b)for a,b in zip(value,expected))
 return value==expected

def _reference_id(edge):
 identity={key:edge[key]for key in('stage_id','event_id','scene_key','choice_key','stage_record','stage_page','level_source')}
 return'battle-event:'+_sha(json.dumps(identity,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())

def _packet():
 """Every call hashes current bytes; only immutable parsed snapshots are cached."""
 try:
  raw=(ROOT/MANIFEST).read_bytes()
  if _sha(raw)!=MANIFEST_SHA256:return None
  manifest=json.loads(raw);blobs={}
  for name,pin in manifest['files'].items():
   if type(name)is not str or Path(name).is_absolute()or'..'in Path(name).parts or'\\'in name:return None
   path=ROOT/name
   if path.is_symlink()or not path.is_file()or not path.resolve().is_relative_to(ROOT.resolve()):return None
   data=path.read_bytes()
   if len(data)!=pin['bytes']or _sha(data)!=pin['sha256']:return None
   blobs[name]=data
  key=(MANIFEST_SHA256,tuple((name,pin['sha256'])for name,pin in sorted(manifest['files'].items())))
  if key not in _CACHE:
   selected=json.loads(blobs[DATA])
   if (type(selected)is not dict or type(selected.get('schema_version'))is not int or selected['schema_version']!=1
     or selected['reference_kind']!='fixed_battle_documented_event_choices'
     or selected['stage_ids']!=list(STAGE_IDS)or selected['event_ids']!=list(EVENT_IDS)
     or selected['counts']!={'raw_edges':14,'admitted_edges':11,'explicit_exclusions':3,'events':5,'choices':8,'stage_ids':8}
     or len(selected['edges'])!=14
     or len({r['reference_id']for r in selected['edges']})!=14
     or any(r['reference_id']!=_reference_id(r)for r in selected['edges'])):return None
   parsed={'data':selected,'catalog':json.loads(blobs['rouge/data/node-catalog.json']),
    'planning':json.loads(blobs['rouge/data/event-planning-reference.json']),
    'battle':json.loads(blobs['rouge/data/battle-previews.json']),'manifest':manifest}
   _CACHE.clear();_CACHE[key]=parsed
  return _CACHE[key]
 except (OSError,ValueError,KeyError,TypeError,AttributeError,IndexError):return None

def _source_identity(packet):
 return{'manifest_sha256':MANIFEST_SHA256,'reference_data_sha256':packet['manifest']['files'][DATA]['sha256'],
  'node_catalog_sha256':packet['manifest']['files']['rouge/data/node-catalog.json']['sha256'],
  'event_planning_data_sha256':packet['manifest']['files']['rouge/data/event-planning-reference.json']['sha256'],
  'battle_previews_sha256':packet['manifest']['files']['rouge/data/battle-previews.json']['sha256'],
  'game_commit':packet['data']['sources']['original_game']['commit'],
  'documents':[{'revision':row['revision'],'sha256':row['sha256']}for row in packet['data']['sources']['documents']]}

def source_data():
 """Fresh source validity plus a small defensive copy; no override parameter."""
 packet=_packet()
 if packet is None:return None
 return{**deepcopy(packet['data']),'source_identity':deepcopy(_source_identity(packet))}

def _validated_forward(packet,event_id):
 """Cross-check the existing forward API against separately parsed current bytes.

 No floor, inventory, memory or other current-run declaration is supplied. A
 warm/polluted legacy lru cache cannot create a reverse link merely because the
 disk still hashes correctly.
 """
 event=next(e for e in packet['catalog']['events']if e['id']==event_id)
 references=[r for r in packet['planning']['battle_links']if r['event_id']==event_id]
 live=event_planning.event_battle_links(event_id)
 summary={key:deepcopy(event[key])for key in('id','title','node_types','floors','natural','natural_reason','entry')}
 if not _same(live['event'],summary)or len(live['rows'])!=len(references):return None
 for current,raw in zip(live['rows'],references):
  for key,value in raw.items():
   if key=='stage_page_links':continue
   if key not in current or not _same(current[key],value):return None
  scene=next(s for s in event['scenes']if s['key']==raw['scene_key'])
  choice=next(c for c in scene['choices']if c['key']==raw['choice_key'])
  if not _same([choice['title'],choice['description'],choice['conditional']],
    [raw['choice_title'],raw['description'],raw['conditional_text']]):return None
  expected=[];excluded=[];emergency=raw['conditional_text']=='升级为紧急作战'
  if len(current['stage_page_links'])!=len(raw['stage_page_links']):return None
  for live_page,raw_page in zip(current['stage_page_links'],raw['stage_page_links']):
   if any(key not in live_page or not _same(live_page[key],value)for key,value in raw_page.items()):return None
   for stage in raw_page['stage_records']:
    candidate={**deepcopy(stage),'source_difficulty_matches':None if not emergency else stage['difficulty']=='FOUR_STAR',
     'actual_stage_instance':None}
    (excluded if candidate['source_difficulty_matches']is False else expected).append(candidate)
  if not _same(current['preview_stage_candidates'],expected)or not _same(current['excluded_stage_candidates'],excluded):return None
 return live

def _unknown(stage_id):
 return{'status':'unknown','reference_kind':'fixed_battle_documented_event_choices','stage_id':stage_id,
  'source_valid':False,'stage_reference':None,'rows':[],'excluded_rows':[],'source_identity':None,
  'stage_global_floors':None,'full_stage_origin_floors_known':False,'actual_stage_id':None,
  'actual_choice_eligible':None,'actual_entered':None,'current_server_verified':False,
  'notice':'对应事件资料暂时无法核对；旧入口与选择已清除。实际入口、资格和作战全部层数仍未知。'}

def _row(packet,edge):
 event=next(e for e in packet['catalog']['events']if e['id']==edge['event_id'])
 scene_number,scene=next((i,s)for i,s in enumerate(event['scenes'],1)if s['key']==edge['scene_key'])
 choice_number=next(i for i,c in enumerate(scene['choices'],1)if c['key']==edge['choice_key'])
 stage={**deepcopy(edge['stage_record']),'level_source':deepcopy(edge['level_source'])}
 result={key:deepcopy(edge[key])for key in('reference_id','event_id','event_title','event_documented_main_floors',
  'event_node_types','scene_key','choice_key','choice_title','choice_description','conditional_text',
  'stage_page','source_difficulty_matches','excluded_by_explicit_difficulty')}
 result.update(stage_id=edge['stage_id'],stage_reference=stage,scene_number=scene_number,choice_number=choice_number,
  event_floor_scope='event_documented_main_floors_only',
  stage_global_floors=None,full_stage_origin_floors_known=False,source_scene_link_verified=False,
  actual_stage_id=None,actual_choice_eligible=None,actual_entered=None,token=None)
 if not edge['excluded_by_explicit_difficulty']:
  result['token']={'reference_kind':'fixed_battle_to_documented_event_choice','reference_id':edge['reference_id'],
   'stage_id':edge['stage_id'],'event_id':edge['event_id'],'scene_key':edge['scene_key'],'choice_key':edge['choice_key'],
   'scene_number':scene_number,'choice_number':choice_number,
   'stage_record':deepcopy(edge['stage_record']),'stage_page':deepcopy(edge['stage_page']),
   'level_source':deepcopy(edge['level_source']),'source_identity':deepcopy(_source_identity(packet))}
 return result

def stage_event_references(stage_id):
 """Return only exact source-admitted event links for the eight supported IDs."""
 if type(stage_id)is not str or stage_id not in STAGE_IDS:return None
 packet=_packet();result=_unknown(stage_id)
 if packet is None:return result
 try:
  edges=[row for row in packet['data']['edges']if row['stage_id']==stage_id]
  if not edges:return result
  for event_id in dict.fromkeys(row['event_id']for row in edges):
   if _validated_forward(packet,event_id)is None:return result
  rows=[];excluded=[]
  for edge in edges:
   preview=packet['battle']['stages'][stage_id];record=edge['stage_record'];level=preview['level_source']
   if (not _same([preview['id'],preview['name'],preview['difficulty']],[stage_id,record['name'],record['difficulty']])
     or not _same(level,edge['level_source'])or not level['url'].endswith(record['level_id'].lower()+'.json')):return result
   current=_row(packet,edge)
   (excluded if edge['excluded_by_explicit_difficulty']else rows).append(current)
  result.update(status='documented_reference',source_valid=True,stage_reference=deepcopy(rows[0]['stage_reference']),
   rows=rows,excluded_rows=excluded,source_identity=deepcopy(_source_identity(packet)),
   scope_counts=deepcopy(packet['data']['counts']),raw_edge_count=len(edges),notice=NOTICE)
  return result
 except (OSError,ValueError,KeyError,TypeError,AttributeError,IndexError,StopIteration):return result

def resolve_stage_event_reference(stage_id,token):
 """Freshly rebuild and compare all token keys/types before manual navigation."""
 if type(stage_id)is not str or stage_id not in STAGE_IDS or type(token)is not dict:return None
 result=stage_event_references(stage_id)
 if not result or result['status']!='documented_reference':return None
 return next((deepcopy(row)for row in result['rows']if _same(token,row['token'])),None)
