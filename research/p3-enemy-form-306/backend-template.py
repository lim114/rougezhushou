"""Stage-specific documentary body/disguise links; never combat state or effects."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path,PurePosixPath

ROOT=Path(__file__).resolve().parents[1]
PACK='research/p3-enemy-form-306'
DATA='rouge/data/enemy-form-reference.json'
AUTHORITY=PACK+'/selected-authority-records.json'
MANIFEST=PACK+'/source-manifest.json'
BATTLE='rouge/data/battle-previews.json'
LEVEL='research/p3-spawn-candidates-299/levels/b68d3e2163e87d4b5da63004768f6cb3f8eaa5b5c66bcf56b72732c1a42f3dda.json'
DOC=PACK+'/community-complete-revisions.json'
GLOSSARY=PACK+'/abnormal-complete-440606.html'
DATA_SHA256='__DATA_SHA__'
MANIFEST_SHA256='__MANIFEST_SHA__'
STAGES=('ro6_n_2_3','ro6_e_2_3')
ALIASES=('enemy_2133_shdopl_lancer','enemy_2133_shdopl_mpmage','enemy_2133_shdopl_sword','enemy_2133_shdopl_demonk')
ACTUAL_FIELDS=('actual_form','actual_rank','actual_spawn_success','actual_disguise_enemy',
 'actual_disguise_level','actual_damage_event','actual_reveal_time','actual_position',
 'actual_remaining_route','actual_body_attributes','actual_disguise_abilities','actual_current_server_eligibility')

def _unknown():return{**{key:None for key in ACTUAL_FIELDS},'modifiers_changed':False,'maps_changed':False,'level_type_applied':False,'run_state_updated':False,'current_server_verified':False}
def _same(a,b):
 if type(a)is not type(b):return False
 if type(a)is dict:return a.keys()==b.keys()and all(type(k)is str and _same(a[k],b[k])for k in b)
 if type(a)is list:return len(a)==len(b)and all(_same(x,y)for x,y in zip(a,b))
 return a==b
def _file(name):
 if type(name)is not str:raise ValueError('Public source path required')
 p=PurePosixPath(name)
 if p.is_absolute()or'..'in p.parts or'\\'in name or':'in name or p.as_posix()!=name:raise ValueError('Unsafe public source path')
 f=ROOT.joinpath(*p.parts)
 if f.is_symlink()or not f.is_file()or not f.resolve().is_relative_to(ROOT.resolve()):raise ValueError('Regular public source required')
 for parent in f.parents:
  if parent==ROOT:break
  if parent.is_symlink():raise ValueError('Linked source parent refused')
 return f

def _packet():
 try:
  raw=_file(MANIFEST).read_bytes()
  if sha256(raw).hexdigest()!=MANIFEST_SHA256:return None
  m=json.loads(raw)
  if(m['schema']!='enemy_form_source_manifest_v1'or m['data_file']!=DATA or m['data_sha256']!=DATA_SHA256
   or m['all_members_required_for_each_target_query']is not True or m['actual_state_or_modifiers_applied']is not False):return None
  if set(m['runtime_files'])!={DATA,AUTHORITY,BATTLE,LEVEL,DOC,GLOSSARY}:return None
  blobs={}
  for name,pin in m['runtime_files'].items():
   content=_file(name).read_bytes()
   if type(pin['bytes'])is not int or len(content)!=pin['bytes']or sha256(content).hexdigest()!=pin['sha256']:return None
   blobs[name]=content
  d=json.loads(blobs[DATA]);a=json.loads(blobs[AUTHORITY]);battle=json.loads(blobs[BATTLE]);level=json.loads(blobs[LEVEL]);docs=json.loads(blobs[DOC])
  if(d['schema']!='enemy_form_reference_v1'or a['schema']!='enemy_form_selected_authority_v1'
   or not _same(d['rows'],a['rows'])or not _same(battle['source'],a['complete_battle_source'])or len(d['rows'])!=8):return None
  if any(d[key]is not False for key in('level_type_applied','modifiers_changed','maps_changed')):return None
  pages={p['title']:p for p in docs['query']['pages'].values()}
  if not _same(pages,a['complete_community_pages']):return None
  originals=[x for x in level['enemyDbRefs']if x['id']in ALIASES]
  if not _same(originals,a['complete_original_level_refs']):return None
  from .battle_preview import battle_data
  legacy=battle_data()
  if not _same(legacy['source'],battle['source']):return None
  for sid in STAGES:
   selected=a['complete_selected_stages'][sid]
   if not _same(selected,battle['stages'][sid])or not _same(selected,legacy['stages'][sid]):return None
  seen=[]
  for row in d['rows']:
   sid,eid,lv=row['stage_id'],row['enemy_id'],row['level'];seen.append((sid,eid,lv))
   if sid not in STAGES or eid not in ALIASES or type(lv)is not int or lv!=0:return None
   stage=battle['stages'][sid]
   body=next(x for x in stage['enemies']if x['id']==eid and x['level']==lv)
   target=next(x for x in stage['enemies']if x['id']==row['declared_summon_enemy_key'])
   original=next(x for x in originals if x['id']==eid and x['level']==lv)
   if(not _same(row['body_reference'],body)or not _same(row['disguise_enemy_reference'],target)
    or not _same(row['complete_original_reference'],original)or row['fixed_body_tier']is not None
    or row['declared_summon_level']is not None or row['current_server_verified']is not False
    or row['original_runtime_callback_verified']is not False):return None
  if seen!=[(sid,eid,0)for sid in STAGES for eid in ALIASES]:return None
  return deepcopy(d)
 except(OSError,ValueError,TypeError,KeyError,AttributeError,StopIteration,IndexError,RecursionError,UnicodeError):return None

def source_data():return _packet()
def _unavailable(stage_id,enemy_id,level):
 return{'target':True,'stage_id':stage_id,'enemy_id':enemy_id,'level':level,'source_valid':False,'status':'source_unavailable',
  'reference':None,'body_reference':None,'disguise_enemy_reference':None,'documented_lifecycle':[],
  'source_differences':[],'source':None,'source_identity':None,**_unknown(),
  'notice':'伪装与现身资料暂时无法核对，旧对应敌人与说明已清除；恢复后请重新选择。'}

def disguise_reference(stage_id,enemy_id,level):
 if(type(stage_id)is not str or stage_id not in STAGES or type(enemy_id)is not str or enemy_id not in ALIASES
  or type(level)is not int or level!=0):return None
 p=_packet()
 if p is None:return _unavailable(stage_id,enemy_id,level)
 row=next(x for x in p['rows']if(x['stage_id'],x['enemy_id'],x['level'])==(stage_id,enemy_id,level))
 return{'target':True,'status':'documented_reference','source_valid':True,'reference':row,**deepcopy(row),
  'source_identity':{'manifest_sha256':MANIFEST_SHA256,'data_sha256':DATA_SHA256},
  'scope_notice':p['scope_notice'],'notice':'只读固定对应关系和分阶段文献，不判断本局是否已经伪装或现身。',**_unknown()}

def reference_text(reference,technical=False):
 if reference is None:return ''
 if not reference['source_valid']:return '【伪装与现身】\n'+reference['notice']
 r=reference['reference'];target=r['disguise_enemy_reference']
 lines=['【伪装与现身】',r['documented_variant_name'],
  '本关原记录名：'+r['fixed_name']+'；图鉴和文献名称：'+r['community_base_name']+'。',
  '指定的伪装对象：'+target['name']+'；伪装退场后现身的是本体，二者资料分开。',
  '','【对应敌人的独立资料】',target['description']or target['handbook_description']or'未另列概述。']
 lines.extend('• '+x for x in target['abilities'])
 lines.append('这里引用本关对应敌人的独立资料；实际召唤等级、伪装的完整能力和数值未知，不覆盖本体面板。')
 for phase in r['documented_lifecycle']:
  lines+=['','【'+phase['title']+'】',phase['text']]
  lines.extend('• 条件：'+x for x in phase['conditions'])
 lines+=['','【来源差异与限制】']
 lines.extend('• '+x['text']for x in r['source_differences'])
 lines+=['','【本局仍待确认】','是否成功生成伪装、实际受伤或现身、实际等级与能力、发生时刻、当前位置及剩余路径均未确认。',
  '本资料不修改难度修正、敌人分类、固定地图或本局记录。',reference['scope_notice']]
 if technical:
  lines+=['','【技术详情】','当前固定引用：'+json.dumps({k:r[k]for k in('stage_id','enemy_id','level')},ensure_ascii=False),
   '原召唤声明：'+json.dumps(r['complete_original_reference']['overwrittenData']['talentBlackboard'],ensure_ascii=False),
   '本体完整资料：'+json.dumps(r['body_reference'],ensure_ascii=False),
   '对应敌人完整资料：'+json.dumps(target,ensure_ascii=False),
   '文献逐字表述：'+json.dumps([q for phase in r['documented_lifecycle']for q in phase['source_quotes']],ensure_ascii=False),
   '原件与版本：'+json.dumps(r['source'],ensure_ascii=False)]
 return '\n'.join(lines)
