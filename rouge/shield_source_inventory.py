"""Source-qualified aggregation over an independently declared shield inventory.

This snapshot belongs to the two post-BlockDamage source filters. It is not
populated from live combat or from a create/finish request.
"""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import hashlib

ONE = 1 << 32
MIN_RAW = -(1 << 63)
MAX_RAW = (1 << 63) - 1
EPSILON = 42950
SOURCE = 'rouge/data/shield-source-inventory-source.json'
SOURCE_SHA256 = 'fe2bee9c8c83b68e494be440faca3b132ab1de9a7d8c4b13f9786a2492bfbfc5'
READ_POINT = 'post_block_damage_source_filters'


@lru_cache(maxsize=1)
def source_valid():
    path = Path(__file__).resolve().parents[1] / SOURCE
    return path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == SOURCE_SHA256


def _tri(value, name):
    if value is not None and type(value) is not bool:
        raise ValueError(name + '需要true、false或null（未知）。')
    return value


def _integer(value, name, minimum=MIN_RAW, maximum=MAX_RAW):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(name + '需要范围内整数，不能用布尔值或小数。')
    return value


def _identity(value, name, nullable=False):
    if nullable and value is None:
        return None
    if (type(value) is not str or not 1 <= len(value) <= 80
            or any(ord(c) < 32 or 0xd800 <= ord(c) <= 0xdfff for c in value)):
        raise ValueError(name + '需要1–80字身份声明，不能含控制字符。')
    return value


def _all(*values):
    return False if False in values else None if None in values else True


def _wrap(raw):
    return (raw - MIN_RAW) % (1 << 64) + MIN_RAW


def float32_signed_number_raw(bits):
    """Exact finite float32 -> signed FP, truncating toward zero.

    Out-of-range CVTT behavior is not emulated. Negative dynamic values are
    permitted here, without broadening the positive barrier-grant domain.
    """
    _integer(bits, '单精度bits', 0, 0xffffffff)
    exponent = (bits >> 23) & 255
    if exponent == 255:
        return None
    significand = (bits & 0x7fffff) + ((1 << 23) if exponent else 0)
    shift = exponent - 118 if exponent else -117
    magnitude = significand << shift if shift >= 0 else significand >> -shift
    raw = -magnitude if bits >> 31 else magnitude
    return raw if MIN_RAW <= raw <= MAX_RAW else None


def _value(value):
    if type(value) is not dict:
        raise ValueError('每项屏障需要独立数值声明。')
    if value.get('kind') == 'getter_fp_snapshot':
        if set(value) != {'kind', 'getter_returned', 'raw'}:
            raise ValueError('getter快照需要kind、getter_returned和raw。')
        returned = _tri(value['getter_returned'], 'getter返回资格')
        if value['raw'] is not None:
            _integer(value['raw'], 'getter FP原值')
        return {'raw_reference': value['raw'] if returned is True else None,
            'default_zero_used': None,
            'normal_return_reference': returned,
            'status': 'declared_getter_result' if returned is True and value['raw'] is not None else 'unknown_getter_result'}
    if value.get('kind') != 'blackboard_number' or set(value) != {
            'kind', 'ordinary_direct_data_path', 'blackboard_available', 'number_readable', 'float32_bits'}:
        raise ValueError('黑板数值需要普通直接分支、黑板对象、数值读取资格和float32_bits。')
    direct = _tri(value['ordinary_direct_data_path'], '普通直接读值分支')
    available = _tri(value['blackboard_available'], '黑板对象有效性')
    readable = _tri(value['number_readable'], '黑板数字读取资格')
    bits = value['float32_bits']
    if bits is not None:
        _integer(bits, '单精度bits', 0, 0xffffffff)
    result = {'raw_reference': None, 'default_zero_used': None, 'normal_return_reference': None, 'status': 'unknown_blackboard_read'}
    if direct is not True:
        result['status'] = 'unqualified_data_path'
    elif available is False:
        result['status'] = 'missing_blackboard_exception_path'
        result['normal_return_reference'] = False
    elif available is True and readable is False:
        result.update(raw_reference=0, default_zero_used=True, normal_return_reference=True, status='explicit_failed_numeric_lookup_default_zero')
    elif available is True and readable is True:
        raw = None if bits is None else float32_signed_number_raw(bits)
        result.update(raw_reference=raw, default_zero_used=False,
            normal_return_reference=True if raw is not None else None,
            status='numeric_reference' if raw is not None else 'unqualified_or_missing_float32_value')
    return result


def _validate(inventory):
    required = {'operator', 'skill', 'recipient_role', 'snapshot_id', 'read_point',
        'ordinary_native_path', 'no_changes_between_filters', 'recipient', 'caster',
        'recipient_container_available', 'inventory_complete', 'shields'}
    if type(inventory) is not dict or set(inventory) != required:
        raise ValueError('请使用完整的机械师二技能来源屏障库存声明。')
    if inventory['operator'] != 'mechanist' or type(inventory['skill']) is not int or inventory['skill'] != 2:
        raise ValueError('来源屏障库存只适用于机械师二技能。')
    if type(inventory['recipient_role']) is not str or inventory['recipient_role'] not in ('owner', 'structure'):
        raise ValueError('受击角色需要owner或structure。')
    _identity(inventory['snapshot_id'], '快照标签')
    if inventory['read_point'] != READ_POINT:
        raise ValueError('库存须独立声明在BlockDamage之后的来源筛选读取点，不能沿用受击前库存。')
    for key in ('ordinary_native_path', 'no_changes_between_filters', 'recipient_container_available', 'inventory_complete'):
        _tri(inventory[key], key)
    for role in ('caster', 'recipient'):
        target = inventory[role]
        if type(target) is not dict or set(target) != {'identity', 'available'}:
            raise ValueError('来源和受击对象需要identity与available。')
        _tri(target['available'], role + '有效性')
        _identity(target['identity'], role + '身份', nullable=target['available'] is not True)
    if inventory['recipient_role'] == 'owner' and inventory['caster'] != inventory['recipient']:
        raise ValueError('本体受击的两个来源筛选对应同一身份和资格，不能声明成不同对象。')
    shields = inventory['shields']
    if type(shields) is not list or len(shields) > 1000:
        raise ValueError('库存需要0–1000个独立实例；是否读全须另行声明。')
    ids = set()
    for item in shields:
        if type(item) is not dict or set(item) != {'id', 'buff_reference_present', 'finished_or_disabled',
                'source_reference_present', 'source_identity', 'has_shield', 'damage_mask_bits', 'value'}:
            raise ValueError('每个实例需要身份、存在/结束/来源/hasShield资格、mask及独立值声明。')
        name = _identity(item['id'], '屏障实例标签')
        if name in ids:
            raise ValueError('屏障实例标签不能重复；同一实例不能累加两次。')
        ids.add(name)
        for key in ('buff_reference_present', 'finished_or_disabled', 'source_reference_present', 'has_shield'):
            _tri(item[key], key)
        _identity(item['source_identity'], '实例来源身份', nullable=item['source_reference_present'] is not True)
        if item['damage_mask_bits'] is not None:
            _integer(item['damage_mask_bits'], 'mask原bits', 0, 0xffffffff)
        _value(item['value'])


def _aggregate(inventory, role, qualified):
    target, source = inventory['recipient'], inventory[role]
    context = _all(target['available'], source['available'], inventory['recipient_container_available'])
    rows, known_math, unknown_count, normal_returns = [], 0, 0, []
    for item in inventory['shields']:
        same = None
        if source['available'] is True:
            if item['source_reference_present'] is False:
                same = False
            elif item['source_reference_present'] is True:
                same = item['source_identity'] == source['identity']
        eligibility = _all(item['buff_reference_present'],
            None if item['finished_or_disabled'] is None else not item['finished_or_disabled'], same, item['has_shield'])
        if not qualified or context is not True:
            eligibility = None
        value = _value(item['value'])
        contribution = 0 if eligibility is False else value['raw_reference'] if eligibility is True else None
        normal = (True if eligibility is False else value['normal_return_reference'] if eligibility is True
            else True if value['normal_return_reference'] is True else None)
        normal_returns.append(normal)
        if contribution is None:
            unknown_count += 1
        else:
            known_math += contribution
        rows.append({'id': item['id'], 'source_identity': item['source_identity'],
            'buff_reference_present': item['buff_reference_present'], 'finished_or_disabled': item['finished_or_disabled'],
            'has_shield': item['has_shield'],
            'source_matches': same, 'eligible_reference': eligibility,
            'value_reference': value, 'contribution_raw_reference': contribution,
            'normal_return_reference': normal,
            'damage_mask_bits': item['damage_mask_bits'], 'mask_used_for_filtering': False})
    total = (_wrap(known_math) if qualified and context is True
        and inventory['inventory_complete'] is True and unknown_count == 0 else None)
    predicate, normal = None, None
    if qualified:
        if target['available'] is False:
            predicate, normal = False, True
        elif target['available'] is True:
            if source['available'] is False:
                predicate, normal = True, True
            elif source['available'] is True:
                if inventory['recipient_container_available'] is False:
                    normal = False
                elif inventory['recipient_container_available'] is True:
                    normal = _all(*normal_returns)
                    if normal is not False and inventory['inventory_complete'] is not True:
                        # Omitted qualifying instances may throw too, so a
                        # partial subtotal establishes no successful return.
                        normal = None
                if normal is True and total is not None:
                    predicate = total < EPSILON
    return {'role': role, 'source_identity': source['identity'], 'source_available': source['available'],
        'rows': rows, 'known_contribution_count': len(rows) - unknown_count,
        'unknown_contribution_count': unknown_count, 'known_math_raw_subtotal': known_math,
        'known_wrapped_raw_subtotal': _wrap(known_math), 'subtotal_is_lower_bound': False,
        'total_raw_reference': total, 'signed_wrap_occurred': None if total is None else total != known_math,
        'filter_le_zero_reference': predicate, 'normal_return_reference': normal}


def mechanist_shield_inventory(inventory):
    _validate(inventory)
    valid = source_valid()
    qualified = valid and inventory['ordinary_native_path'] is True and inventory['no_changes_between_filters'] is True
    filters = {role: _aggregate(inventory, role, qualified) for role in ('caster', 'recipient')}
    first, second = filters['caster'], filters['recipient']
    called, normal, passed = None, first['normal_return_reference'], None
    if normal is True:
        if first['filter_le_zero_reference'] is False:
            called, passed = False, False
        elif first['filter_le_zero_reference'] is True:
            called, normal = True, second['normal_return_reference']
            if normal is True:
                passed = second['filter_le_zero_reference']
        else:
            normal = True if second['normal_return_reference'] is True else None
            if normal is True:
                passed = _all(first['filter_le_zero_reference'], second['filter_le_zero_reference'])
    elif normal is False:
        called = False
    return {'operator': '机械师', 'skill': 2, 'recipient_role': inventory['recipient_role'],
        'snapshot_id': inventory['snapshot_id'], 'read_point': READ_POINT,
        'source_filters': filters, 'inventory_complete_declaration': inventory['inventory_complete'],
        'both_filters_pass_reference': passed, 'recipient_filter_called_reference': called,
        'ordered_filters_returned_reference': normal,
        'source_valid': valid, 'source': SOURCE, 'source_sha256': SOURCE_SHA256,
        'actual_inventory_complete': None, 'actual_overflow_cancelled': None,
        'events_scheduled': False, 'current_hotfix_equivalence_proven': False,
        'notes': ['库存和身份仅为局外独立声明；读取点须在BlockDamage后，并明确两筛选间无变化。',
            '先排除空实例、结束/禁用、来源不同及hasShield关闭项，再累计FP值；mask不参与此来源筛选。',
            '黑板对象缺失是异常路径，不能作0；数字读取明确失败才默认0。接口/XLua路径不推断数值。',
            '总原值按signed64回绕相加，再判断是否严格小于42950；不逐盾判断后合取，也不夹成0或最大值。',
            '读全或贡献资格未知则完整总量未知；已证分项可能含负值及回绕，不能称下界。',
            '缺筛选来源可通过，但缺受击对象失败；补盾/结束请求不会自动插入或移除库存。',
            '先执行机械师来源筛选，false时不调用受击者自身来源筛选；正常返回false仍可进入后续节点，异常/未证明返回则后续请求未知。',
            '实际实例、读取完整性、创建/移除与回调时钟及当前热更新仍未知；不写入本局记忆。']}


def public_example(recipient_role='structure'):
    if recipient_role not in ('owner', 'structure'):
        raise ValueError('受击角色需要owner或structure。')
    owner_id = '机械师本体·声明'
    recipient_id = owner_id if recipient_role == 'owner' else '结构性原理·声明'
    def item(name, source, raw):
        return {'id': name, 'buff_reference_present': True, 'finished_or_disabled': False,
            'source_reference_present': True, 'source_identity': source, 'has_shield': True,
            'damage_mask_bits': 0, 'value': {'kind': 'getter_fp_snapshot', 'getter_returned': True, 'raw': raw}}
    return {'operator': 'mechanist', 'skill': 2, 'recipient_role': recipient_role,
        'snapshot_id': '公开受击后库存', 'read_point': READ_POINT,
        'ordinary_native_path': True, 'no_changes_between_filters': True,
        'caster': {'identity': owner_id, 'available': True},
        'recipient': {'identity': recipient_id, 'available': True},
        'recipient_container_available': True, 'inventory_complete': True,
        'shields': [item('刚耗尽的本技能盾', owner_id, 0),
            item('同来源另一块20盾', owner_id, 20 * ONE),
            item('受击者自身来源0盾', recipient_id, 0), item('第三方100盾', '第三方·声明', 100 * ONE)]}
