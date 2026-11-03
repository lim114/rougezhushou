"""Exact documented ownership clauses, independent of source-scene recovery."""
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path
from . import node_catalog as catalog

@lru_cache(maxsize=1)
def reference_data():
    return json.loads((Path(__file__).with_name('data')/'choice-held-reference.json').read_text(encoding='utf8'))

def _data():
    data=reference_data()
    if data['sources']['fixed_event_catalog']['sha256']!=catalog._data()['sources']['cached_community_catalog']['sha256']:
        raise ValueError('持有门参考的固定事件目录已变化，须重新绑定完整选择文字。')
    if data['sources']['original_game']['sha256']!=catalog._original()['source']['game_data']['sha256']:
        raise ValueError('持有门参考的原件版本已变化，须重新核验原物品ID与原选择。')
    return data

def choice_reference(event_id,choice):
    data=_data();row=data['community_choices'].get(choice['key'])
    if row is None:return None
    if (row['event_id']!=event_id or row['choice_title']!=choice['title'] or row['description']!=choice['description']):
        raise ValueError('持有门参考与所选原目录条目不相符，不能仅按组编号复用。')
    return {**deepcopy(row),'sources':deepcopy(data['sources'])}

def original_reference(record_id):
    data=_data();row=data['original_choices'].get(record_id)
    if row is None:return None
    original=catalog._original()['choices'].get(record_id)
    if original is None or any(original[k]!=v for k,v in row['raw_record'].items() if k in original):
        raise ValueError('原选择持有门已变化，不能仅按ID复用。')
    return {**deepcopy(row),'sources':deepcopy(data['sources'])}
