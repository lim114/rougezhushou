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
