"""Fixed public source queries, never server eligibility or game operations."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import json,re

NOTICE='固定资料候选与原文引用；未知资格仍保留，不表示必然出现，不提供生成概率。'
@lru_cache(maxsize=1)
def _data():
    return json.loads((Path(__file__).with_name('data')/'node-catalog.json').read_text(encoding='utf-8'))
@lru_cache(maxsize=1)
def _original():
    return json.loads((Path(__file__).with_name('data')/'node-events.json').read_text(encoding='utf-8'))
def _text(value,label,optional=False):
    if optional and value is None:return
    if not isinstance(value,str) or not value.strip():raise ValueError(label+'需要非空文字。')
def _floor(floor,special_region=False):
    if floor is not None and (type(floor) is not int or floor not in range(1,7)):raise ValueError('主层需要1–6的整数。')
    if type(special_region) is not bool:raise ValueError('special_region需要布尔值。')
def _event(event_id):
    _text(event_id,'事件引用')
    e=next((e for e in _data()['events'] if e['id']==event_id),None)
    if e is None:raise ValueError('事件引用不存在；同名事件需要选择各自资料分组。')
    return e
def _scene(event_id,scene_key):
    _text(scene_key,'场景引用')
    s=next((s for s in _event(event_id)['scenes'] if s['key']==scene_key),None)
    if s is None:raise ValueError('场景不属于所选事件。')
    return s
def _result(rows,**extra):
    return {'rows':rows,'sources':deepcopy(_data()['sources']),
            'scope':deepcopy(_data()['completeness']),'notice':NOTICE,**extra}
def _summary(e):
    return {k:deepcopy(e[k]) for k in ('id','title','node_types','floors','natural','natural_reason','entry')}
def _all_node_types():
    return list(dict.fromkeys([v['name'] for v in _data()['node_types'].values()]+
                             [t for e in _data()['events'] for t in e['node_types']]))
def all_events(node_type=None,include_indirect=False):
    _text(node_type,'节点类型',True)
    if type(include_indirect) is not bool:raise ValueError('include_indirect需要布尔值。')
    rows=[_summary(e) for e in _data()['events'] if (include_indirect or e['natural'] is not False)
          and (node_type is None or node_type in e['node_types'])]
    return _result(rows,node_type=node_type,indirect_included=include_indirect,
                   original_uncataloged=deepcopy(_data()['uncataloged_original_titles']),
                   known_node_types=_all_node_types())
COMMANDS={'events':all_events}
def event_candidates(node_type=None,floor=None,special_region=False,include_indirect=False):
    _floor(floor,special_region)
    rows=[];excluded=[]
    for e in all_events(node_type,include_indirect)['rows']:
        natural_context=e['natural'] is not False
        if floor is not None and not special_region and natural_context and e['floors'] and floor not in e['floors']:
            excluded.append({**e,'reason':'固定社区目录的主层范围不包含所选层'});continue
        e['floor_status']='目录主层条件相符' if floor is not None and not special_region and natural_context and e['floors'] else '层数或特殊区域资格未知'
        e['server_eligibility']='未知';rows.append(e)
    return _result(rows,excluded=excluded,floor=floor,special_region=special_region,
                   indirect_included=include_indirect)
COMMANDS['candidates']=event_candidates
def _validate_node(node):
    if not isinstance(node,dict):raise ValueError('节点需要对象。')
    for key in ('observed_type','remembered_type'):_text(node.get(key),key,True)
    prediction=node.get('prediction')
    if prediction is not None and not isinstance(prediction,dict):raise ValueError('类型预测需要对象。')
    types=(prediction or {}).get('candidates')
    if types is not None and (not isinstance(types,list) or any(not isinstance(t,str) or not t for t in types)):
        raise ValueError('类型候选需要非空文字列表。')
    for key in ('content','remembered_content'):
        value=node.get(key)
        if value is not None and not isinstance(value,dict):raise ValueError(key+'需要对象。')
    history=node.get('content_history')
    if history is not None and (not isinstance(history,list) or any(not isinstance(v,dict) for v in history)):
        raise ValueError('历史内容需要对象列表。')
def node_events(node,floor=None,special_region=False):
    _validate_node(node);_floor(floor,special_region)
    observed=node.get('observed_type');remembered=node.get('remembered_type')
    # A current floor filter cannot discard the identity of an earlier read.
    history=all_events(remembered,include_indirect=True)['rows'] if remembered and remembered!=observed else []
    if observed in ('林间空地','曲折密道'):
        return _result([],history_candidates=history,type_candidates=[observed],node_id=node.get('id'),
                       state='当前通行节点；历史内容仅作过去参考')
    if observed and not observed.startswith('未知'):
        types=[observed];basis='当前已读类型'
    else:
        types=(node.get('prediction') or {}).get('candidates') or []
        if not types:types=_all_node_types()
        basis='模板类型候选' if (node.get('prediction') or {}).get('candidates') else '类型未确认，全部已证节点类别联合'
    by_id={}
    for t in types:
        for e in event_candidates(t,floor,special_region)['rows']:by_id[e['id']]=e
    return _result(list(by_id.values()),history_candidates=history,type_candidates=deepcopy(types),
                   remembered_type=remembered,node_id=node.get('id'),type_basis=basis)
COMMANDS['node']=node_events
def original_references(query='',title=None,record_type='all',record_id=None):
    if not isinstance(query,str) or len(query)>120:raise ValueError('检索词需要0–120字。')
    _text(title,'标题',True);_text(record_id,'原表引用',True)
    if record_type not in ('all','scene','choice'):raise ValueError('原表类别需要all、scene或choice。')
    rows=[];needle=query.strip().casefold()
    for kind,field,idkey in (('scene','unmapped_original_scenes','scene_id'),('choice','unmapped_original_choices','choice_id')):
        if record_type not in ('all',kind):continue
        for raw in _data()[field]:
            if record_id is not None and raw[idkey]!=record_id:continue
            if title is not None and raw['title']!=title:continue
            text=json.dumps(raw,ensure_ascii=False).casefold()
            if needle and needle not in text:continue
            rows.append({'record_type':kind,'record_id':raw[idkey],**deepcopy(raw),
                         'source_scene_link_verified':False,'reachable_from_entry':None})
    if record_id is not None and not rows:raise ValueError('引用不在未分类原表记录中。')
    return _result(rows,query=query,title=title,record_type=record_type,
                   next_scene_is_destination_reference_only=True,
                   natural_node_entry_verified=False)
def event_details(event_id):
    e=deepcopy(_event(event_id));represented={i for s in e['scenes'] for i in s['game_scene_ids']}
    unlinked=[{'id':i,**deepcopy(s),'reachable_from_entry':None} for i,s in _original()['scenes'].items()
              if s['title']==e['title'] and i not in represented]
    return _result(e['scenes'],event=_summary(e),unlinked_original_scenes=unlinked,
                   unclassified_original_query={'command':'original','input':{'query':e['title']}},
                   server_scene_reachability_verified=False)
COMMANDS.update(detail=event_details,original=original_references)
