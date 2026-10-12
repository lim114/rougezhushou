"""First-arrival LIGHT references admitted only by explicit temporary declarations."""
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path


@lru_cache(maxsize=1)
def arrival_data():
    return json.loads((Path(__file__).with_name('data')/'node-arrival-reference.json').read_text(encoding='utf8'))


def arrival_source():return arrival_data()['source']


def validate_arrival_state(node):
    state=node.get('light_arrival_declaration')
    if state is None:state={}
    if not isinstance(state,dict) or set(state)-{'first_entry','reward_received'}:
        raise ValueError('羽瞰点到达声明只接受first_entry和reward_received。')
    for field in ('first_entry','reward_received'):
        if state.get(field) is not None and type(state[field]) is not bool:
            raise ValueError('羽瞰点首次/已领取状态需要布尔声明或留空。')
    return state


def arrival_reference(node,types,*,difficulty=None,split_unlocked=None):
    if difficulty is not None and (type(difficulty) is not int or difficulty not in range(16)):
        raise ValueError('保密等级需要0–15整数或留空。')
    if split_unlocked is not None and type(split_unlocked) is not bool:
        raise ValueError('分裂科技需要布尔声明或留空。')
    state=validate_arrival_state(node)
    matches=None if not types else True if all(t=='LIGHT' for t in types) else False if 'LIGHT' not in types else None
    first,received=state.get('first_entry'),state.get('reward_received')
    data=arrival_data();quantity=data['first_arrival_admission']['source_quantity']
    vision=data['visibility_count_parameters']
    conflict=first is True and received is True
    component=None;ap=None;qualified=None;reason='当前原节点类型或首次/领取状态未明确。'
    if matches is False:
        component=ap=0;qualified=False;reason='当前明确原类型不是羽瞰点；本项首次到达组件不适用。'
    elif matches is True and not conflict:
        if first is True and received is False:
            component=ap=quantity;qualified=True;reason='本次方案明确为首次且尚未领取；仅条件参考，不是实际领取。'
        elif received is True:
            component=0;reason='首次组件已声明领取；重复到达是否另有AP未证，不能再次计入+1。'
    if conflict:reason='首次到达与已领取声明冲突；未据此求AP。'
    high=None if difficulty is None else difficulty>=vision['minimum_difficulty']
    boost=False if high is False or split_unlocked is False else True if high is True and split_unlocked is True else None
    spawn=[vision['upgraded']['spawn']] if boost is True else [vision['base']['spawn']] if boost is False else [vision['base']['spawn'],vision['upgraded']['spawn']]
    arrived=[vision['upgraded']['arrival']] if boost is True else [vision['base']['arrival']] if boost is False else [vision['base']['arrival'],vision['upgraded']['arrival']]
    return {'node_id':node['id'],'original_type_matches_light':matches,
            'first_entry_declared':first,'reward_received_declared':received,'declaration_conflict':conflict,
            'first_component_condition_matches':qualified,'source_stated_arrival_ap':quantity,
            'first_component_remaining_ap_reference':component,'node_arrival_ap_reference':ap,'reason':reason,
            'occupied_declared':node.get('occupied_declared'),'occupied_light_source_exception':matches is True,
            'vision_boost_condition_matches':boost,'difficulty_declared':difficulty,'split_unlocked_declared':split_unlocked,
            'spawn_surrounding_count_candidates':spawn,'arrival_surrounding_count_candidates':arrived,
            'range_geometry':None,'actual_revealed_nodes':None,'actual_ap_received':None,
            'source':deepcopy(arrival_source())}


def arrival_lines(reference):
    if reference['original_type_matches_light'] is False:return []
    number=lambda value:'未知' if value is None else str(value)
    truth=lambda value:'未知' if value is None else '是' if value else '否'
    return ['羽瞰点首次到达AP参考：'+number(reference['node_arrival_ap_reference'])+'；原说明到达+1AP，模型只接首次未领情境。',
            '本次首次声明：'+truth(reference['first_entry_declared'])+'；已领取声明：'+truth(reference['reward_received_declared'])+'。',
            reference['reason'],
            '被居民占领的羽瞰点到达仍有+1资料；当前原类型和首次资格仍需独立确认。',
            '出现周围格数参数候选：'+str(reference['spawn_surrounding_count_candidates'])+'；到达后参数候选：'+str(reference['arrival_surrounding_count_candidates'])+'。',
            '4/12/24只是已列数量；范围几何、实际揭示节点和领取均未知。']
