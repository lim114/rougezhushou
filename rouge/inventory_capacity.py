"""Explicit occupancy declarations, hypothetical disposal and overload gate.

The source establishes overload prevents action, including pursuit. Individual
occupancy weights and actual inventory/capacity are NEVER inferred here.
"""
from copy import deepcopy
from itertools import combinations
import hashlib,json
from pathlib import Path

SOURCE_FILE=Path(__file__).with_name('data')/'inventory-capacity-source.json'
SOURCE_SHA256='1f0af46425324b6ffd05005540af149e108fdf2b1d43b44e94babd921b3ebdae'

def capacity_source():
    raw=SOURCE_FILE.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA256:
        raise ValueError('容量规则来源摘要已变化，不能继续应用原来源资格。')
    return json.loads(raw)


def _text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(field + '需要非空文字声明。')
    return value


def _natural(value, field, optional=True):
    if value is None and optional:
        return None
    if type(value) is not int or not 0 <= value <= 1000000:
        raise ValueError(field + '需要非负整数；未知填null。')
    return value


def _items(rows):
    if not isinstance(rows, list) or len(rows) > 60:
        raise ValueError('逐件清单需要至多60个独立实例。')
    identities = set()
    result = []
    for row in rows:
        if type(row) is not dict:
            raise ValueError('每个实例需要对象。')
        item = deepcopy(row)
        key = _text(item.get('instance_id'), '库存实例ID')
        if key in identities:
            raise ValueError('库存实例ID必须唯一；同名物品可以有不同实例。')
        identities.add(key)
        _text(item.get('item_id'), '物品来源ID')
        _text(item.get('source'), '实例与占用声明来源')
        item['slot_units'] = _natural(item.get('slot_units'), '独立占用单位')
        result.append(item)
    return result


def _state(items, capacity, complete):
    known = sum(row['slot_units'] or 0 for row in items)
    closed = complete is True and all(row['slot_units'] is not None for row in items)
    occupied = known if closed else None
    overloaded = None
    if capacity is not None:
        if known > capacity:
            overloaded = True
        elif closed:
            overloaded = False
    return {'known_occupied_lower_bound': known, 'declared_occupied': occupied,
        'capacity': capacity, 'complete_occupancy_known': closed,
        'declared_overloaded': overloaded,
        'free_units': capacity-occupied if occupied is not None and capacity is not None else None,
        'minimum_release_units': max(0, occupied-capacity) if occupied is not None and capacity is not None else None,
        'documented_action_gate': 'blocked_by_declared_overload' if overloaded is True else
            'overload_condition_not_blocking' if overloaded is False else 'unknown',
        'actual_game_action_allowed': None,
        'pursuit_exempt_from_overload': False}


def _minimal_release(items, state, protected, limit, search_limit):
    needed = state['minimum_release_units']
    result = {'minimum_discarded_instances': None, 'candidate_discard_sets': [],
        'complete_candidate_enumeration': False, 'search_visits': 0,
        'item_value_or_utility_ranked': False, 'source': 'finite mathematics on explicit slot declarations only'}
    if needed is None:
        result['status'] = 'unknown_occupancy_or_capacity'
        return result
    if needed == 0:
        result.update(status='no_release_required', minimum_discarded_instances=0,
            candidate_discard_sets=[{'instance_ids': [], 'released_units': 0}], complete_candidate_enumeration=True)
        return result
    allowed = sorted((row for row in items if row['instance_id'] not in protected),
        key=lambda row: (-row['slot_units'], row['instance_id']))
    running = 0
    count = None
    for index, row in enumerate(allowed, 1):
        running += row['slot_units']
        if running >= needed:
            count = index
            break
    if count is None:
        result.update(status='protected_instances_prevent_sufficient_release', complete_candidate_enumeration=True)
        return result
    result.update(status='minimal_instance_count_proved', minimum_discarded_instances=count)
    # The descending sum proves k-1 cannot suffice. Enumeration is separately
    # bounded: stopping does not pretend all minimal sets were shown.
    for chosen in combinations(allowed, count):
        if result['search_visits'] >= search_limit:
            result['truncated_reason'] = 'search_visit_limit'
            return result
        result['search_visits'] += 1
        units = sum(row['slot_units'] for row in chosen)
        if units >= needed:
            if len(result['candidate_discard_sets']) >= limit:
                result['truncated_reason'] = 'candidate_limit'
                return result
            result['candidate_discard_sets'].append({'instance_ids': sorted(row['instance_id'] for row in chosen),
                'released_units': units})
    result['complete_candidate_enumeration'] = True
    return result


def inventory_capacity_plan(snapshot, proposals=None, protected_ids=None, *, max_candidates=20, max_search_visits=50000):
    if type(snapshot) is not dict:
        raise ValueError('独立库存快照需要对象。')
    _text(snapshot.get('snapshot_id'), '独立快照名称')
    _text(snapshot.get('source'), '快照来源')
    complete = snapshot.get('inventory_complete')
    if complete is not None and type(complete) is not bool:
        raise ValueError('库存完整性需要true/false/null。')
    capacity = _natural(snapshot.get('capacity'), '独立总容量')
    items = _items(snapshot.get('items'))
    by_id = {row['instance_id']: row for row in items}
    protected = [] if protected_ids is None else protected_ids
    if not isinstance(protected, list) or any(type(value) is not str for value in protected) or len(set(protected)) != len(protected):
        raise ValueError('保留实例需要不重复ID列表。')
    if set(protected)-by_id.keys():
        raise ValueError('保留实例必须在本快照中明确存在。')
    for value, field in [(max_candidates, '候选上限'), (max_search_visits, '遍历上限')]:
        if type(value) is not int or not 1 <= value <= 100000:
            raise ValueError(field+'需要1至100000整数。')
    if proposals is None:
        proposals = []
    if not isinstance(proposals, list) or len(proposals) > 30:
        raise ValueError('整理/领取方案需要至多30项列表。')
    reference=capacity_source()
    state = _state(items, capacity, complete)
    rows = []
    seen = set()
    for proposal in proposals:
        if type(proposal) is not dict:
            raise ValueError('方案需要对象。')
        key = _text(proposal.get('id'), '方案ID')
        if key in seen:
            raise ValueError('方案ID不能重复。')
        seen.add(key)
        _text(proposal.get('source'), '方案声明来源')
        discard = proposal.get('discard_ids', [])
        if not isinstance(discard, list) or any(type(value) is not str for value in discard) or len(set(discard)) != len(discard):
            raise ValueError('丢弃实例需要不重复ID列表。')
        if set(discard)-by_id.keys():
            raise ValueError('不得丢弃未声明实例。')
        if set(discard)&set(protected):
            raise ValueError('方案与保留实例偏好冲突。')
        received = _items(proposal.get('received_items', []))
        if {row['instance_id'] for row in received}&by_id.keys():
            raise ValueError('领取声明实例不能重用原库存ID，即使计划先丢弃。')
        remaining = [row for row in items if row['instance_id'] not in discard]
        if len(remaining)+len(received) > 60:
            raise ValueError('方案完成后的声明清单超过60实例。')
        after_discard = _state(remaining, capacity, complete)
        after_receive = _state(remaining+received, capacity, complete)
        rows.append({'id': key, 'source': proposal['source'], 'discard_ids': deepcopy(discard),
            'received_items': received, 'after_discard': after_discard, 'after_receive': after_receive,
            'actual_discard_performed': None, 'actual_rewards_received': None,
            'actual_reward_interface_allows_discard': None,
            'minimum_release': _minimal_release(remaining+received, after_receive, protected, max_candidates, max_search_visits)})
    return {'snapshot': deepcopy(snapshot), 'protected_ids': deepcopy(protected), 'initial': state,
        'minimum_release': _minimal_release(items, state, protected, max_candidates, max_search_visits), 'proposals': rows,
        'native_inventory_or_capacity_verified': False, 'inventory_updated': False,
        'source_rule': 'PRTS固定433770：'+reference['rule_text'], 'source_reference': reference,
        'notes': ['每实例占用单位由用户独立声明；没有默认为每件1格。',
            '容量条件不阻断不证明其它行动资格成立；实际游戏行动仍未知。',
            '方案为独立假设，不触发领取/丢弃/出售或改写本局。']}


def public_capacity_payload():
    item = lambda identity, units: {'instance_id': identity, 'item_id': 'rogue_6_scrap_M_01',
        'slot_units': units, 'source': '字面量算术演示的独立占用声明，非游戏测量'}
    return {'snapshot': {'snapshot_id': '占用算术演示', 'source': '合成声明，非本局',
        'capacity': 5, 'inventory_complete': True, 'items': [item('a', 3), item('b', 2), item('c', 2)]},
        'protected_ids': ['a'], 'proposals': [{'id': '保留a丢弃b', 'source': '局外假设方案',
            'discard_ids': ['b'], 'received_items': []}, {'id': '丢弃bc并声明领取d', 'source': '局外假设方案',
            'discard_ids': ['b','c'], 'received_items': [item('d', 1)]}]}
