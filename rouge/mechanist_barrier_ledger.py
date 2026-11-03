"""Ordered S2 barrier arithmetic over explicitly declared node conditions.

This is an offline reference, never an HP-damage or live-combat simulator.
Requests to create/finish a buff do not establish the next barrier instance.
"""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import hashlib
import json

from .ammo_counter import AmmoCounter, AmmoConsumption
from .catalog import catalog
from .barrier_blackboard import blackboard_storage_reference, ROUNDING_MODES, source_valid as blackboard_source_valid

ONE = 1 << 32
EPSILON = 42950
MAX_RAW = (1 << 63) - 1
SOURCE_SHA256 = 'bd8d4b11552c43de9d5a321aaa85a06442105e13ba442b865f95fdaa01dca8db'
SOURCE = 'rouge/data/mechanist-barrier-native-source.json'
RECIPIENTS = {'owner': '机械师本体', 'structure': '结构性原理'}


@lru_cache(maxsize=1)
def _source_valid():
    path = Path(__file__).resolve().parents[1] / SOURCE
    return path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == SOURCE_SHA256


def _integer(value, name, minimum=0, maximum=MAX_RAW):
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError(name + '需要范围内整数，不能使用布尔值或小数。')
    return value


def _boolean(value, name):
    if value is not None and type(value) is not bool:
        raise ValueError(name + '需要true、false或null（未知）。')
    return value


def _all(*values):
    return False if False in values else None if None in values else True


def _label(value):
    if type(value) is not str or not 1 <= len(value) <= 80 or any(ord(c) < 32 or 0xd800 <= ord(c) <= 0xdfff for c in value):
        raise ValueError('入伤标签需要1–80字且不能含控制字符。')
    return value


def _barrier(value):
    if type(value) is not dict or set(value) != {'available', 'dynamic_raw', 'cancel_all_raw'}:
        raise ValueError('屏障声明需要available、dynamic_raw和cancel_all_raw。')
    _boolean(value['available'], '屏障实例资格')
    for key in ('dynamic_raw', 'cancel_all_raw'):
        if value[key] is not None:
            _integer(value[key], key)
    return deepcopy(value)


def _filter(value):
    if type(value) is not dict or set(value) != {'source_available', 'total_raw'}:
        raise ValueError('来源屏障筛选声明需要source_available和total_raw。')
    _boolean(value['source_available'], '筛选来源有效性')
    if value['total_raw'] is not None:
        _integer(value['total_raw'], '此来源的屏障总原值', -(1 << 63), MAX_RAW)
    # The template passes a missing filter source, not a missing recipient.
    if value['source_available'] is False:
        return True
    if value['source_available'] is None or value['total_raw'] is None:
        return None
    return value['total_raw'] < EPSILON


PACKET_FLAGS = ('is_damage', 'cancelled', 'ignore_blocked',
    'no_intervening_barrier_changes', 'main_buff_for_explosion',
    'main_buff_for_replenish', 'ammunition_read_ok', 'manual_count_node_success', 'progress_source_available',
    'counting_is_affecting', 'counting_ignore_until_cast_end', 'counting_not_count_next')
PACKET_KEYS = {'id', 'recipient', 'value_raw', 'caster_shields',
    'recipient_shields', 'following_barrier', *PACKET_FLAGS}
INVENTORY_PACKET_KEYS = PACKET_KEYS - {'caster_shields', 'recipient_shields'} | {'source_shield_inventory'}


def mechanist_barrier_ledger(payload):
    required = {'operator', 'skill', 'skill_rank', 'ordinary_native_path',
        'no_external_ammunition_changes', 'maximum_ammunition',
        'consumed_ammunition', 'initial_barriers', 'packets'}
    if type(payload) is not dict or not required <= set(payload) or set(payload)-required-{'float_rounding'}:
        raise ValueError('请使用完整的机械师二技能屏障账本声明模板。')
    rounding = payload.get('float_rounding')
    if rounding is not None and rounding not in ROUNDING_MODES:
        raise ValueError('float_rounding需要明确单精度舍入环境，或null（未知）。')
    if payload['operator'] != 'mechanist' or type(payload['skill']) is not int or payload['skill'] != 2:
        raise ValueError('入伤屏障账本只适用于机械师二技能。')
    rank = _integer(payload['skill_rank'], '技能等级', 1, 10)
    ordinary = _boolean(payload['ordinary_native_path'], '普通原生路径条件')
    no_external = _boolean(payload['no_external_ammunition_changes'], '无外部弹药变更条件')
    maximum = _integer(payload['maximum_ammunition'], '声明共享弹匣上限', 1, 1000)
    consumed = _integer(payload['consumed_ammunition'], '已耗弹声明', 0, 10000)
    initial = payload['initial_barriers']
    if type(initial) is not dict or set(initial) != set(RECIPIENTS):
        raise ValueError('请分别声明owner（本体）和structure（结构性原理）的屏障。')
    barriers = {key: _barrier(value) for key, value in initial.items()}
    packets = payload['packets']
    if type(packets) is not list or not 1 <= len(packets) <= 200:
        raise ValueError('有序入伤需要1–200项。顺序为调用方声明，不推断同帧先后。')
    names = set()
    inventory_reports = {}
    explosion_reports = {}
    for packet in packets:
        if type(packet) is not dict or set(packet)-{'explosion_math'} not in (PACKET_KEYS, INVENTORY_PACKET_KEYS):
            raise ValueError('每项入伤须保留完整声明字段；null代表未知。')
        name = _label(packet['id'])
        if name in names:
            raise ValueError('入伤标签不能重复。')
        names.add(name)
        if type(packet['recipient']) is not str or packet['recipient'] not in RECIPIENTS:
            raise ValueError('受击对象需要owner或structure。')
        _integer(packet['value_raw'], '入伤FP原值', -MAX_RAW, MAX_RAW)
        for flag in PACKET_FLAGS:
            _boolean(packet[flag], flag)
        if 'explosion_math' in packet:
            from .mechanist_explosion_math import mechanist_explosion_reference
            explosion_reports[name] = mechanist_explosion_reference(packet['explosion_math'])
            if packet['explosion_math']['skill_rank'] != rank:
                raise ValueError('爆炸计算的技能等级须与该账本一致。')
        if 'source_shield_inventory' in packet:
            from .shield_source_inventory import mechanist_shield_inventory
            inventory = packet['source_shield_inventory']
            inventory_reports[name] = mechanist_shield_inventory(inventory)
            if inventory['recipient_role'] != packet['recipient']:
                raise ValueError('筛选库存的受击角色须与本项入伤一致。')
        else:
            for key in ('caster_shields', 'recipient_shields'):
                _filter(packet[key])
        if packet['following_barrier'] is not None:
            _barrier(packet['following_barrier'])
        if ('source_shield_inventory' not in packet and packet['recipient'] == 'owner' and packet['no_intervening_barrier_changes'] is True
                and packet['caster_shields'] != packet['recipient_shields']):
            raise ValueError('本体两个来源筛选是同一身份；无中间变更声明下不能给出不同快照。')
    source_valid = _source_valid()
    counter = AmmoCounter(maximum, consumed=consumed)
    consumption = AmmoConsumption(counter, 7, 1, ignore_trigger_once=True)
    count_known = source_valid and ordinary is True and no_external is True
    rows = []
    for ordinal, packet in enumerate(packets, 1):
        recipient = packet['recipient']; barrier = barriers[recipient]
        value = packet['value_raw']
        near_zero = abs(value) < EPSILON
        cancelled = True if near_zero else packet['cancelled']
        entry = None if not source_valid or ordinary is not True else _all(barrier['available'],
            None if cancelled is None else not cancelled, packet['is_damage'],
            None if packet['ignore_blocked'] is None else not packet['ignore_blocked'])
        row = {'ordinal': ordinal, 'id': packet['id'], 'recipient': recipient,
            'recipient_name': RECIPIENTS[recipient], 'input_raw': value,
            'entry_gate': entry, 'near_zero_modifier_cancelled': near_zero,
            'barrier_before_raw': barrier['dynamic_raw'], 'absorbed_raw': None,
            'barrier_after_subtraction_raw': None, 'barrier_storage_reference': None,
            'barrier_after_block_raw': None, 'modifier_after_subtraction_raw': None,
            'modifier_after_block_raw': None, 'block_cancel_requested': None,
            'depletion_gate': None, 'overflow_cancel_requested': None,
            'explosion_requested': None, 'manual_count_requested': None,
            'ammunition_consumed_reference': None,
            'replenishment_requested': None, 'finish_old_barrier_requested': None,
            'actual_hp_loss': None, 'actual_explosion_hits': None,
            'actual_replenishment_created': None, 'actual_finish_seconds': None,
            'independent_following_barrier': deepcopy(packet['following_barrier']),
            'source_shield_inventory_reference': deepcopy(inventory_reports.get(packet['id']))}
        if entry is False:
            row.update(status='filtered', absorbed_raw=0,
                barrier_after_subtraction_raw=barrier['dynamic_raw'], barrier_after_block_raw=barrier['dynamic_raw'],
                modifier_after_subtraction_raw=value, modifier_after_block_raw=value,
                block_cancel_requested=False, depletion_gate=False,
                overflow_cancel_requested=False, explosion_requested=False,
                manual_count_requested=False, ammunition_consumed_reference=0,
                replenishment_requested=False, finish_old_barrier_requested=False)
        elif entry is None or barrier['dynamic_raw'] is None:
            row['status'] = 'unknown'
            barriers[recipient] = {'available': None, 'dynamic_raw': None, 'cancel_all_raw': None}
            count_known = False
        else:
            absorbed = min(max(0, value), barrier['dynamic_raw'])
            after = barrier['dynamic_raw'] - absorbed
            storage = blackboard_storage_reference(after, rounding)
            readback = storage['readback_raw']
            intermediate = value - absorbed
            block_cancel = intermediate < EPSILON
            row.update(status='conditional_reference', absorbed_raw=absorbed,
                barrier_after_subtraction_raw=after, barrier_storage_reference=storage,
                barrier_after_block_raw=readback, modifier_after_subtraction_raw=intermediate,
                modifier_after_block_raw=0 if block_cancel else intermediate,
                block_cancel_requested=block_cancel)
            unchanged = packet['no_intervening_barrier_changes'] is True
            if not unchanged:
                # The storage arithmetic is a reference before intervening
                # callbacks; it cannot stand in for their later BB read.
                row['barrier_after_block_raw'] = None
            cancel_all = barrier['cancel_all_raw']
            branch = None if not unchanged or cancel_all is None else cancel_all < EPSILON
            dynamic_gate = None if not unchanged or readback is None else readback < EPSILON
            depleted = _all(branch, dynamic_gate)
            row['depletion_gate'] = depleted
            if not unchanged:
                barriers[recipient] = {'available': None, 'dynamic_raw': None, 'cancel_all_raw': None}
                count_known = False
            elif branch is False:
                row.update(overflow_cancel_requested=True, explosion_requested=False,
                    manual_count_requested=False, ammunition_consumed_reference=0,
                    replenishment_requested=False, finish_old_barrier_requested=False)
                # Outer fail branch cancels the modifier and leaves this barrier.
                barriers[recipient]['dynamic_raw'] = readback
            elif branch is None and dynamic_gate is False:
                # Neither possible cancel_all branch explodes or counts here,
                # but only the outer-fail path cancels the modifier.
                row.update(overflow_cancel_requested=None, explosion_requested=False,
                    manual_count_requested=False, ammunition_consumed_reference=0,
                    replenishment_requested=False, finish_old_barrier_requested=False)
                barriers[recipient]['dynamic_raw'] = readback
            elif depleted is False:
                row.update(overflow_cancel_requested=False, explosion_requested=False,
                    manual_count_requested=False, ammunition_consumed_reference=0,
                    replenishment_requested=False, finish_old_barrier_requested=False)
                barriers[recipient]['dynamic_raw'] = readback
            elif depleted is None:
                barriers[recipient] = {'available': None, 'dynamic_raw': None, 'cancel_all_raw': None}
                count_known = False
            else:
                row['overflow_cancel_requested'] = (inventory_reports[packet['id']]['both_filters_pass_reference']
                    if packet['id'] in inventory_reports else _all(_filter(packet['caster_shields']), _filter(packet['recipient_shields'])))
                filters_returned = (inventory_reports[packet['id']]['ordered_filters_returned_reference']
                    if packet['id'] in inventory_reports else True)
                if filters_returned is not True:
                    row['status'] = 'unknown_after_source_filter'
                    count_known = False
                else:
                    row['explosion_requested'] = packet['main_buff_for_explosion']
                    read_ok = packet['ammunition_read_ok']
                    positive = counter.raw_remaining > 0 if count_known else None
                    request = _all(read_ok, positive, packet['main_buff_for_replenish'])
                    row['manual_count_requested'] = request
                    row['replenishment_requested'] = _all(request, packet['manual_count_node_success'])
                    row['finish_old_barrier_requested'] = read_ok
                    if request is False:
                        row['ammunition_consumed_reference'] = 0
                    else:
                        count_gate = _all(request, packet['manual_count_node_success'], packet['progress_source_available'], packet['counting_is_affecting'],
                            None if packet['counting_ignore_until_cast_end'] is None else not packet['counting_ignore_until_cast_end'])
                        if count_gate is False or packet['counting_not_count_next'] is True:
                            row['ammunition_consumed_reference'] = 0
                        elif count_gate is True and packet['counting_not_count_next'] is False and count_known:
                            row['ammunition_consumed_reference'] = consumption.on_event(7)
                        else:
                            count_known = False
                # MarkFinish/AddBuff requests prove no instance for the next packet.
                barriers[recipient] = {'available': None, 'dynamic_raw': None, 'cancel_all_raw': None}
        following = packet['following_barrier']
        if following is not None:
            barriers[recipient] = _barrier(following)
        row['following_barrier_state'] = deepcopy(barriers[recipient])
        row['ammunition_remaining_reference'] = counter.raw_remaining if count_known else None
        row['explosion_fp_reference'] = deepcopy(explosion_reports.get(packet['id'])) if row['explosion_requested'] is True else None
        row['declared_explosion_base_raw_reference'] = (0 if row['explosion_requested'] is False else
            row['explosion_fp_reference']['declared_calls_scaled_damage_raw_total'] if row['explosion_fp_reference'] is not None else None)
        rows.append(row)
    parameters = catalog()['operators']['mechanist']['skills'][1]['levels'][rank-1]['values']
    known = [row for row in rows if row['absorbed_raw'] is not None]
    return {'operator': '机械师', 'skill': 2, 'skill_rank': rank, 'rows': rows,
        'known_absorbed_raw_subtotal': sum(row['absorbed_raw'] for row in known),
        'absorbed_raw_total': sum(row['absorbed_raw'] for row in rows) if len(known) == len(rows) else None,
        'known_packets': len(known), 'packet_count': len(rows), 'final_barriers': deepcopy(barriers),
        'known_declared_explosion_base_raw_subtotal': sum(r['declared_explosion_base_raw_reference'] for r in rows if r['declared_explosion_base_raw_reference'] is not None),
        'declared_explosion_base_raw_total': sum(r['declared_explosion_base_raw_reference'] for r in rows) if all(r['declared_explosion_base_raw_reference'] is not None for r in rows) else None,
        'maximum_ammunition_reference': maximum,
        'ammunition_consumed_reference': counter.consumed - consumed if count_known else None,
        'ammunition_remaining_reference': counter.raw_remaining if count_known else None,
        'nominal_maximum_parameter': int(parameters['trigger_time']),
        'source_valid': source_valid and blackboard_source_valid() and all(r['source_valid'] for r in inventory_reports.values())
            and all(r['source_valid'] for r in explosion_reports.values()),
        'entry_math_source_valid': source_valid, 'blackboard_source_valid': blackboard_source_valid(),
        'source': SOURCE, 'source_sha256': SOURCE_SHA256,
        'actual_hp_loss': None, 'actual_end_seconds': None, 'actual_total_damage': None,
        'events_scheduled': False, 'current_hotfix_equivalence_proven': False,
        'notes': ['顺序及所有节点条件为独立声明；FP原值单位为2^32，不读取或修改本局状态。',
            '本工具仅支持非负屏障黑板原值；负值声明直接拒绝，不静默夹成0。',
            '扣盾即时差与单精度写入/FP读回分列；后续耗尽门及下一包使用读回值。舍入环境未声明则读回与相关依赖未知，不假定当前游戏MXCSR。',
            '未声明中间屏障无变化时，只保留即时吸收算式，后续破屏门未知。',
            '屏障筛选只计受击者身上来自机械师与自身的盾，不包含第三方来源；缺筛选来源可通过，缺受击实例不可通过。',
            '可用source_shield_inventory替代两个手填总量；两模式互斥。库存只在受击后独立读取点计算，不从创建/结束请求自动更新。来源总量允许signed64负值及回绕，不扩大非负吸收屏障的支持域。',
            '库存模式另列筛选正常返回资格：异常/未证明返回不会推定后续爆炸/计数/结束节点执行。旧手填总量模式是筛选正常返回下的独立数值条件参考。',
            '可选explosion_math逐目标保留两次攻击/事件后/法抗及晚期originAtk快照；只有爆炸请求明确true才接入FP参考，计算返回不等于实际命中或生命损失。',
            '取消伤害修改器不会抹去它的数值；中间剩余值不是实际生命损失。',
            '爆炸前与补盾前主buff门分别声明；补盾请求与计数成功分开，计数门关闭仍可能请求补盾。',
            'manual_count_node_success声明计数节点的外层返回；progress_source_available单独声明计数源存在。计数源缺失可使耗弹0，而不阻止补盾请求。',
            '旧盾结束和新盾创建仅为请求；下一包需要独立新屏障声明，不能由请求自动重置屏障。',
            '实际命中、最大生命创建快照、碰撞、补盾与结束时刻、实例附着、XLua及当前热更新仍未知。']}


def public_example():
    barrier = {'available': True, 'dynamic_raw': 100 * ONE, 'cancel_all_raw': 0}
    def packet(name, value, recipient='owner'):
        return {'id': name, 'recipient': recipient, 'value_raw': value * ONE,
            **{key: True for key in PACKET_FLAGS}, 'cancelled': False, 'ignore_blocked': False,
            'counting_ignore_until_cast_end': False, 'counting_not_count_next': False,
            'caster_shields': {'source_available': True, 'total_raw': 0},
            'recipient_shields': {'source_available': True, 'total_raw': 0}, 'following_barrier': None}
    first, second, third = packet('本体首次40', 40), packet('本体随后70', 70), packet('结构性原理110', 110, 'structure')
    second['following_barrier'] = deepcopy(barrier)
    return {'operator': 'mechanist', 'skill': 2, 'skill_rank': 10,
        'ordinary_native_path': True, 'no_external_ammunition_changes': True,
        'float_rounding': 'nearest_even',
        'maximum_ammunition': 8, 'consumed_ammunition': 0,
        'initial_barriers': {'owner': deepcopy(barrier), 'structure': deepcopy(barrier)},
        'packets': [first, second, third]}
