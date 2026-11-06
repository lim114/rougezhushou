"""Offline public encounter observations; neither estimated weights nor run odds."""
from collections import Counter
from functools import lru_cache
from pathlib import Path
import json
from . import node_catalog
from .node_catalog_view import map_conditions

DEFAULT=Path(__file__).with_name('data')/'public-event-samples.json'


@lru_cache(maxsize=1)
def samples():
    data=json.loads(DEFAULT.read_text('utf8'))
    if data['schema']!='rouge-public-encounter-samples-v1':raise ValueError('事件统计口径未确认。')
    cohorts={};keys=set()
    for row in data['rows']:
        key=(row['floor'],row['treehole'],row['id']);count=row['observedCount']
        if (type(key[0])is not int or key[0]not in range(1,7)or type(key[1])is not bool
            or not isinstance(key[2],str)or not key[2].startswith('rogue_6:scene_ro6_')
            or type(count)is not int or count<0 or key in keys):raise ValueError('事件样本身份或计数未通过核对。')
        keys.add(key);cohorts.setdefault(key[:2],{})[key[2]]=count
    if sum(sum(rows.values())for rows in cohorts.values())!=data['metadata']['observations']:
        raise ValueError('事件观察总数与分项不一致。')
    return data['metadata'],cohorts


@lru_cache(maxsize=1)
def event_bindings():
    bindings={}
    for event in node_catalog._data()['events']:
        if '不期而遇'not in event['node_types']:continue
        ids={'rogue_6:'+scene_id.removesuffix('_enter')for scene in event['scenes']
             if scene['key']in event['entry']for scene_id in scene['game_scene_ids']
             if scene_id.endswith('_enter')}
        if len(ids)==1:bindings[event['id']]=next(iter(ids))
    owners=Counter(bindings.values())
    return {key:value for key,value in bindings.items()if owners[value]==1}


def references(graph):
    context=map_conditions(graph,{})
    # Hidden zones do not prove the entrance floor or the dataset's treehole cohort.
    if context['floor']is None or context['special_region']:return {}
    try:
        metadata,cohorts=samples()
    except(OSError,ValueError):return {}
    counts=cohorts.get((context['floor'],False),{})
    total=sum(counts.values())
    if not total:return {}
    return {key:{'event_id':identity,'count':counts[identity],'total':total,
                 'frequency':counts[identity]/total,'floor':context['floor'],
                 'model_version':metadata['version'],'difficulty_stratified':metadata['difficultyStratified']}
            for key,identity in event_bindings().items()if identity in counts}


def label(reference):
    return (f"历史 {reference['frequency']:.2%}"if reference['count']else'样本未观测')if reference else None


def explanation(reference):
    return (f"第{reference['floor']}层主地图历史观察：{reference['count']}/{reference['total']}次。"
            '分母包含该层原样本全部不期而遇事件，不随本页候选或搜索结果重分配；0次不表示不可能。'
            '样本混合保密等级；不是调整权重模型或本局生成概率，当前DLC适用性未核验。'
            f"来源：路标档案馆，资料模型版本{reference['model_version']}。")
