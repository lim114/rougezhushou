"""S2 explosion FP calculation over independent pre-event and late snapshots.

CalculateDamage references are not Modifier acceptance, hits or HP loss.
Both source ATK reads precede the first callback; later target reads are separate.
"""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import hashlib
import math
import struct

from .catalog import catalog
from .shield_source_inventory import float32_signed_number_raw

ONE = 1 << 32
MIN_RAW = -(1 << 63)
MAX_RAW = (1 << 63) - 1
EPSILON = 42950
PERCENT_RAW = 42949672
MINIMUM_RAW = 214748368
SOURCE = 'rouge/data/mechanist-explosion-source.json'
SOURCE_SHA256 = '116eda3956f41c5e662c8c93d0d38b66765629743c2383cd2279e9ded6364ab6'


@lru_cache(maxsize=1)
def source_valid():
    p=Path(__file__).resolve().parents[1]/SOURCE
    return p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==SOURCE_SHA256


def _raw(value,name):
    if value is not None and (type(value) is not int or not MIN_RAW<=value<=MAX_RAW):
        raise ValueError(name+'需要signed64 FP原值或null，不能用布尔值/小数。')
    return value


def _tri(value,name):
    if value is not None and type(value) is not bool:raise ValueError(name+'需要true、false或null。')
    return value


def _label(value):
    if type(value) is not str or not 1<=len(value)<=80 or any(ord(c)<32 or 0xd800<=ord(c)<=0xdfff for c in value):
        raise ValueError('调用标签需要1–80字，不能含控制字符。')
    return value


def _bits(value):
    if value is not None and (type(value) is not int or not 0<=value<=0xffffffff):
        raise ValueError('float32_bits需要32位整数或null。')
    return value


def wrap(raw):return (raw-MIN_RAW)%(1<<64)+MIN_RAW
def multiply(a,b):return None if a is None or b is None else wrap((a*b)>>32)
def add(a,b):return None if a is None or b is None else wrap(a+b)
def subtract(a,b):return None if a is None or b is None else wrap(a-b)
def nonnegative(a):return None if a is None else max(0,a)


INFO_KEYS={'damage_type','atk_raw','atk_scale_raw','atk_addition_raw'}


def _info(info):
    if type(info) is not dict or set(info)!=INFO_KEYS:
        raise ValueError('AttackInfo快照需要damage_type及atk/scale/addition三项原值。')
    if info['damage_type'] is not None and (type(info['damage_type']) is not str or info['damage_type'] not in ('MAGICAL','PHYSICAL','TRUE')):
        raise ValueError('伤害类型需要MAGICAL、PHYSICAL、TRUE或null；此计算仅核准MAGICAL。')
    for k in INFO_KEYS-{'damage_type'}:_raw(info[k],k)
    return deepcopy(info)


def final_attack_reference(info):
    info=_info(info);a,s,x=(info[k] for k in ('atk_raw','atk_scale_raw','atk_addition_raw'))
    if not source_valid():
        return {k:None for k in ('scale_addition_gate_reference','atk_product_raw_reference',
            'used_addition_raw_reference','atk_sum_raw_reference','final_atk_raw_reference')}
    gate=None if s is None else s>EPSILON
    used=None if gate is None else x if gate else 0
    product=multiply(a,s);combined=add(product,used)
    return {'scale_addition_gate_reference':gate,'atk_product_raw_reference':product,
        'used_addition_raw_reference':used,'atk_sum_raw_reference':combined,
        'final_atk_raw_reference':nonnegative(combined)}


def magical_damage_reference(info,magic_res_raw,penetrate_ratio_raw,penetrate_fixed_raw):
    """Ordinary CalculateDamageInternal MAGICAL branch, all signed64 operations."""
    info=_info(info)
    for name,value in (('magic_res_raw',magic_res_raw),('penetrate_ratio_raw',penetrate_ratio_raw),('penetrate_fixed_raw',penetrate_fixed_raw)):
        _raw(value,name)
    atk=final_attack_reference(info)
    result={**atk,'res_after_fixed_raw_reference':None,'penetration_remaining_ratio_raw_reference':None,
        'effective_res_raw_reference':None,'remaining_percent_raw_reference':None,
        'before_percent_factor_raw_reference':None,'resisted_damage_raw_reference':None,
        'minimum_damage_raw_reference':None,'calculate_damage_raw_reference':None,
        'source_valid':source_valid(),'status':'unknown'}
    if not result['source_valid']:result['status']='unknown_source';return result
    if info['damage_type']!='MAGICAL':result['status']='unqualified_damage_type';return result
    flat=nonnegative(subtract(magic_res_raw,penetrate_fixed_raw))
    ratio=subtract(ONE,penetrate_ratio_raw);effective=multiply(flat,ratio)
    remaining=nonnegative(subtract(100*ONE,effective))
    before=multiply(atk['final_atk_raw_reference'],remaining)
    resisted=multiply(before,PERCENT_RAW);floor=multiply(atk['final_atk_raw_reference'],MINIMUM_RAW)
    value=None if resisted is None or floor is None else max(resisted,floor)
    result.update(res_after_fixed_raw_reference=flat,penetration_remaining_ratio_raw_reference=ratio,
        effective_res_raw_reference=effective,remaining_percent_raw_reference=remaining,
        before_percent_factor_raw_reference=before,resisted_damage_raw_reference=resisted,
        minimum_damage_raw_reference=floor,calculate_damage_raw_reference=value,
        status='conditional_reference' if value is not None else 'unknown')
    return result


PASS_KEYS={'info_unchanged','post_event_info','target_attributes_available','magic_res_raw'}
FIRST_KEYS=PASS_KEYS|{'penetrate_ratio_raw','penetrate_fixed_raw'}


def _pass(value,first):
    if type(value) is not dict or set(value)!=(FIRST_KEYS if first else PASS_KEYS):
        raise ValueError('两次NoEvent输入须独立保留事件后信息、目标法抗及属性有效性；基准不使用来源穿透。')
    for k in ('info_unchanged','target_attributes_available'):_tri(value[k],k)
    if value['post_event_info'] is not None:_info(value['post_event_info'])
    if value['info_unchanged'] is True and value['post_event_info'] is not None:
        raise ValueError('无信息变化与独立事件后快照两模式互斥。')
    for k in (('magic_res_raw','penetrate_ratio_raw','penetrate_fixed_raw') if first else ('magic_res_raw',)):
        _raw(value[k],k)


def _prepared(initial,pass_value):
    if pass_value['info_unchanged'] is True:return deepcopy(initial),'declared_unchanged'
    if pass_value['post_event_info'] is not None:return _info(pass_value['post_event_info']),'independent_post_event_snapshot'
    return None,'unknown_post_event_info'


def mechanist_explosion_reference(payload):
    required={'operator','skill','skill_rank','ordinary_native_path','blackboard_available','scale_basis',
        'scale_number_readable','scale_float32_bits','radius_number_readable','radius_float32_bits','calls'}
    if type(payload) is not dict or set(payload)!=required:raise ValueError('请使用完整机械师S2爆炸数值声明。')
    if payload['operator']!='mechanist' or type(payload['skill']) is not int or payload['skill']!=2:
        raise ValueError('爆炸数值参考仅适用于机械师S2。')
    rank=payload['skill_rank']
    if type(rank) is not int or not 1<=rank<=10:raise ValueError('技能等级需要1–10。')
    for k in ('ordinary_native_path','blackboard_available','scale_number_readable','radius_number_readable'):_tri(payload[k],k)
    _bits(payload['scale_float32_bits']);_bits(payload['radius_float32_bits'])
    if payload['scale_basis'] not in ('nominal_skill_parameter','independent_blackboard_number'):
        raise ValueError('倍率依据需要名义技能参数或独立黑板数字。')
    if payload['scale_basis']=='nominal_skill_parameter' and payload['scale_float32_bits'] is not None:
        raise ValueError('名义倍率不允许另填bits覆盖。')
    calls=payload['calls']
    if type(calls) is not list or not 1<=len(calls)<=200:raise ValueError('每目标调用快照需要1–200项。')
    names=set()
    for c in calls:
        if type(c) is not dict or set(c)!={'id','target_enumerated','source_attributes_available','first_atk_raw',
                'baseline_atk_raw','first','baseline','late_first_info_unchanged','late_origin_info'}:
            raise ValueError('每调用须有两次独立攻击读取、两次NoEvent输入及晚期originAtk信息。')
        name=_label(c['id'])
        if name in names:raise ValueError('调用标签不能重复。')
        names.add(name)
        for k in ('target_enumerated','source_attributes_available','late_first_info_unchanged'):_tri(c[k],k)
        for k in ('first_atk_raw','baseline_atk_raw'):_raw(c[k],k)
        _pass(c['first'],True);_pass(c['baseline'],False)
        if c['late_origin_info'] is not None:_info(c['late_origin_info'])
        if c['late_first_info_unchanged'] is True and c['late_origin_info'] is not None:
            raise ValueError('晚期无变化与独立晚期快照两模式互斥。')
    valid=source_valid();context=valid and payload['ordinary_native_path'] is True and payload['blackboard_available'] is True
    values=catalog()['operators']['mechanist']['skills'][1]['levels'][rank-1]['values']
    nominal_bits=struct.unpack('<I',struct.pack('<f',values['atk_scale']))[0]
    scale_bits=nominal_bits if payload['scale_basis']=='nominal_skill_parameter' else payload['scale_float32_bits']
    scale=None;default=None;radius=None
    if context:
        if payload['scale_number_readable'] is False:scale,default=ONE,True
        elif payload['scale_number_readable'] is True:
            scale=None if scale_bits is None else float32_signed_number_raw(scale_bits);default=False
        if payload['radius_number_readable'] is False:radius=0.0
        elif payload['radius_number_readable'] is True and payload['radius_float32_bits'] is not None:
            r=struct.unpack('<f',struct.pack('<I',payload['radius_float32_bits']))[0]
            radius=r if math.isfinite(r) else None
    rows=[]
    for c in calls:
        initial={'damage_type':'MAGICAL','atk_raw':c['first_atk_raw'],'atk_scale_raw':scale,'atk_addition_raw':0}
        baseline={'damage_type':'MAGICAL','atk_raw':c['baseline_atk_raw'],'atk_scale_raw':ONE,'atk_addition_raw':0}
        first,first_basis=_prepared(initial,c['first']);second,second_basis=_prepared(baseline,c['baseline'])
        ready=context and c['target_enumerated'] is True and c['source_attributes_available'] is True
        branches={}
        for key,info,basis in (('scaled',first,first_basis),('baseline',second,second_basis)):
            p=c['first'] if key=='scaled' else c['baseline']
            numeric=None
            if ready and info is not None and p['target_attributes_available'] is True:
                numeric=magical_damage_reference(info,p['magic_res_raw'],p['penetrate_ratio_raw'] if key=='scaled' else 0,
                    p['penetrate_fixed_raw'] if key=='scaled' else 0)
            branches[key]={'prepared_attack_info':deepcopy(info),'basis':basis,'numeric_reference':numeric,
                'calculate_damage_raw_reference':None if numeric is None else numeric['calculate_damage_raw_reference'],
                'source_event_enabled':key=='scaled','target_event_enabled':True,
                'penetrate_ratio_raw_reference':p['penetrate_ratio_raw'] if key=='scaled' else 0,
                'penetrate_fixed_raw_reference':p['penetrate_fixed_raw'] if key=='scaled' else 0}
        late=first if c['late_first_info_unchanged'] is True else c['late_origin_info']
        origin=None if not ready or late is None else final_attack_reference(late)['final_atk_raw_reference']
        rows.append({'id':c['id'],'first_atk_read_raw_reference':c['first_atk_raw'],
            'baseline_atk_read_raw_reference':c['baseline_atk_raw'],'branches':branches,
            'origin_atk_raw_reference':origin,'actual_modifier_value':None,'actual_hit':None,'actual_hp_loss':None})
    primary=[r['branches']['scaled']['calculate_damage_raw_reference'] for r in rows]
    return {'operator':'机械师','skill':2,'skill_rank':rank,'rows':rows,'nominal_atk_scale':values['atk_scale'],
        'scale_raw_reference':scale,'default_one_used_reference':default,'radius_float32_reference':radius,
        'nominal_range_radius':values['range_radius'],'known_scaled_damage_raw_subtotal':sum(x for x in primary if x is not None),
        'declared_calls_scaled_damage_raw_total':sum(primary) if all(x is not None for x in primary) else None,
        'source_valid':valid,'source':SOURCE,'source_sha256':SOURCE_SHA256,
        'actual_target_count':None,'actual_total_damage':None,'actual_collision_seconds':None,
        'events_scheduled':False,'current_hotfix_equivalence_proven':False,
        'notes':['两次来源攻击读取均在首次伤害计算回调之前；目标前置事件仍分别触发，两次无事件计算输入须独立声明。',
            '进入无事件计算前的信息与晚期来源攻击读取不同；不能从前置快照默认推出后置回调没有变化。',
            '先FP乘攻击倍率，仅scale原值严格大于42950时加入加项，再Max(0)。FP乘法负值向下取整并signed64回绕。',
            '法抗先减固定穿透、Max(0)，再乘1−比例穿透；倍率已为FP比例，不再除100。基准分支source=null，两穿透值为0。',
            '基础法术值先乘剩余百分数，再乘0.01f；与0.05f最低值比较，不改成double百分比或另一种运算顺序。',
            '无事件计算直接返回基础公式值；外层伤害计算返回先前缓存值。晚期来源攻击须独立快照或明确无变化条件。',
            '范围半径数字明确失败采用节点字段默认0；成功0保持0，不借名义半径。半径不能证明实际目标枚举或命中。',
            '只有明确枚举到的目标及有效来源/目标属性快照才列计算参考；真实伤害修改器接受值、命中/生命损失、时钟及热更新未知。']}


def public_example():
    def branch(res,first):
        value={'info_unchanged':True,'post_event_info':None,'target_attributes_available':True,'magic_res_raw':res*ONE}
        if first:value.update(penetrate_ratio_raw=0,penetrate_fixed_raw=0)
        return value
    call={'id':'独立目标30法抗','target_enumerated':True,'source_attributes_available':True,
        'first_atk_raw':1000*ONE,'baseline_atk_raw':1000*ONE,'first':branch(30,True),'baseline':branch(30,False),
        'late_first_info_unchanged':None,'late_origin_info':None}
    return {'operator':'mechanist','skill':2,'skill_rank':10,'ordinary_native_path':True,'blackboard_available':True,
        'scale_basis':'nominal_skill_parameter','scale_number_readable':True,'scale_float32_bits':None,
        'radius_number_readable':True,'radius_float32_bits':0x3fc00000,'calls':[call]}
