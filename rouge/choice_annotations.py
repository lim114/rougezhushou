"""Source-bound annotation roles; never evaluate eligibility or call battle links."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path,PurePosixPath

ROOT=Path(__file__).resolve().parents[1]
DATA='rouge/data/choice-annotations.json'
AUTHORITY='research/p3-choice-annotations-307/selected-authority-records.json'
MANIFEST='research/p3-choice-annotations-307/source-manifest.json'
CATALOG='rouge/data/node-catalog.json'
DOCUMENTS=tuple(f'research/p3-future-region-effects-300/prts-events-{r}.html'for r in('427904','440271'))
DATA_SHA256='751217af2fc1374bcb901ca1ff6e208e3a20f33beb257980d6bb144d2cd46e53'
MANIFEST_SHA256='d6fef0cdc29e4509c5d1eb7a064a087ea37a43baeab30a82aea7c28d6354cd1e'
IDENTITIES=tuple((f'community_group_{g:03d}',f'community_group_{g:03d}:scene:{s}',
 f'community_group_{g:03d}:scene:{s}:choice:{c}')for g,s,c in
 ((8,0,0),(8,0,1),(14,2,0),(15,0,1),(15,2,0),(16,8,0),(17,6,0),(18,0,1),
  (19,1,0),(23,1,0),(23,6,0),(23,9,1),(23,11,0),(25,0,2),(30,0,0),(31,0,1)))
NEW_RESULT_IDENTITIES=tuple(IDENTITIES[i]for i in(1,2,4,5,6,9,10,11,12,15))

def _same(a,b):
 if type(a)is not type(b):return False
 if type(a)is dict:return a.keys()==b.keys()and all(type(k)is str and _same(a[k],b[k])for k in b)
 if type(a)is list:return len(a)==len(b)and all(_same(x,y)for x,y in zip(a,b))
 return a==b

def _file(name):
 if type(name)is not str:raise ValueError('Public relative path required')
 p=PurePosixPath(name)
 if p.is_absolute()or'..'in p.parts or'\\'in name or':'in name or p.as_posix()!=name:raise ValueError('Unsafe public path')
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
  if(m['schema']!='choice_annotation_source_manifest_v1'or m['all_runtime_members_required_each_target_query']is not True
   or m['qualification_or_state_changed']is not False or set(m['runtime_files'])!={DATA,AUTHORITY,CATALOG,*DOCUMENTS}):return None
  blobs={}
  for name,pin in m['runtime_files'].items():
   content=_file(name).read_bytes()
   if type(pin['bytes'])is not int or len(content)!=pin['bytes']or sha256(content).hexdigest()!=pin['sha256']:return None
   blobs[name]=content
  if sha256(blobs[DATA]).hexdigest()!=DATA_SHA256:return None
  d=json.loads(blobs[DATA]);a=json.loads(blobs[AUTHORITY]);catalog=json.loads(blobs[CATALOG])
  if(d['schema']!='choice_annotation_roles_v1'or a['schema']!='choice_annotation_selected_authority_v1'
   or not _same(d['rows'],a['rows'])or not _same(d['expected_events'],a['complete_expected_events'])):return None
  from . import node_catalog
  for eid,expected in d['expected_events'].items():
   current=next(e for e in catalog['events']if e['id']==eid)
   if not _same(expected,current)or not _same(expected,node_catalog._event(eid)):return None
  if tuple((r['event_id'],r['scene_key'],r['choice_key'])for r in d['rows'])!=IDENTITIES:return None
  if sum(r['role']=='preselection_requirement'for r in d['rows'])!=4:return None
  if sum(r['role']=='selection_result'for r in d['rows'])!=12:return None
  for row in d['rows']:
   e=d['expected_events'][row['event_id']];s=next(s for s in e['scenes']if s['key']==row['scene_key'])
   ch=next(c for c in s['choices']if c['key']==row['choice_key'])
   if not _same(row['catalog_choice'],ch)or row['text']!=ch['conditional']:return None
  return deepcopy(d)
 except(OSError,ValueError,KeyError,TypeError,StopIteration,AttributeError,IndexError,RecursionError,UnicodeError):return None

def source_data():return _packet()

def _choice(d,event_id,scene_key,choice_key,*,event=None,scene=None,choice=None):
 result={'target':True,'event_id':event_id,'scene_key':scene_key,'choice_key':choice_key,
  'status':'source_unavailable','source_valid':False,'role':None,'reference':None,'source_identity':None,
  'actual_selectable':None,'actual_result':None,'qualification_changed':False,'inventory_updated':False,
  'notice':'附注类型暂时无法核对；保留原文，不据此新增资格条件或确认实际结果。'}
 if d is None:return result
 expected=d['expected_events'][event_id];expected_scene=next(s for s in expected['scenes']if s['key']==scene_key)
 expected_choice=next(c for c in expected_scene['choices']if c['key']==choice_key)
 if any(given is not None and not _same(given,wanted)for given,wanted in
  ((event,expected),(scene,expected_scene),(choice,expected_choice))):return result
 row=next(r for r in d['rows']if(r['event_id'],r['scene_key'],r['choice_key'])==(event_id,scene_key,choice_key))
 result.update(status='documented_reference',source_valid=True,role=row['role'],reference=row,
  source_identity={'data_sha256':DATA_SHA256,'manifest_sha256':MANIFEST_SHA256},
  notice='这里只区分出现前条件和选择后结果；不改变资格判断或认定本局已经发生。')
 return result

def scene_references(event_id,scene_key,*,event=None,scene=None):
 """One fresh complete source check per target scene; unrelated scenes do no I/O."""
 if type(event_id)is not str or type(scene_key)is not str:return{}
 targets=[cid for eid,sid,cid in IDENTITIES if(eid,sid)==(event_id,scene_key)]
 if not targets:return{}
 d=_packet()
 return{cid:_choice(d,event_id,scene_key,cid,event=event,scene=scene)for cid in targets}

def choice_reference(event_id,scene_key,choice_key,*,event=None,scene=None,choice=None):
 if any(type(v)is not str for v in(event_id,scene_key,choice_key))or(event_id,scene_key,choice_key)not in IDENTITIES:return None
 return _choice(_packet(),event_id,scene_key,choice_key,event=event,scene=scene,choice=choice)

def _classify_rows(rows,event_id,scene_key,*,event=None,scene=None):
 from . import node_catalog
 if event is None:event=node_catalog._event(event_id)
 if scene is None:scene=node_catalog._scene(event_id,scene_key)
 annotations=scene_references(event_id,scene_key,event=event,scene=scene)
 output=deepcopy(rows)
 for row in output:
  annotation=annotations.get(row['choice_key'])
  if annotation is None:continue
  role=annotation['role']if annotation['source_valid']else None
  row.update(annotation_reference=annotation,annotation_role=role,annotation_source_valid=annotation['source_valid'])
  if role=='selection_result'and(event_id,scene_key,row['choice_key'])in NEW_RESULT_IDENTITIES:
   row['unparsed_condition_text']=None
 return output

def classified_choice_eligibility(event_id,scene_key,context=None,*,event=None,scene=None):
 """Full reading result atop untouched legacy checks/status and raw diagnostic API."""
 from . import event_planning
 result=deepcopy(event_planning.choice_eligibility(event_id,scene_key,context))
 result['rows']=_classify_rows(result['rows'],event_id,scene_key,event=event,scene=scene)
 return result

def classified_choice_resources(event_id,scene_key,context=None,*,event=None,scene=None):
 """Reuse existing resource results and classify their nested reading metadata once."""
 from . import event_planning
 result=deepcopy(event_planning.choice_resources(event_id,scene_key,context))
 rows=_classify_rows([r['choice_eligibility']for r in result['rows']],event_id,scene_key,event=event,scene=scene)
 for resource,qualified in zip(result['rows'],rows):resource['choice_eligibility']=qualified
 return result

def reading_lines(reference,text):
 """Keep literal text even if a source failed; an unknown role is never a condition."""
 if not text:return[]
 if(not reference or reference.get('source_valid')is not True
  or(reference.get('reference')or{}).get('text')!=text):
  return['附注原文（类型待核对）：'+text,
   '附注类型暂时无法核对；保留原文，不据此新增资格条件或确认实际结果。']
 row=reference['reference'];lines=[row['label']+'（原文）：'+text]
 if row['role']=='selection_result':lines.append('这是选择后的结果说明，不作为选项出现条件；实际结果仍未知。')
 lines.extend(row['limits'])
 return lines
