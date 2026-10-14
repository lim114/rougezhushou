"""Source-bound FP packet multipliers over independent declared event inputs.

This does not schedule events, claim actual ordering or settle HP/EP/SP.
"""
from copy import deepcopy
from functools import lru_cache
from itertools import permutations
from pathlib import Path
import hashlib
import json
import struct

from .mechanist_explosion_math import ONE,MIN_RAW,MAX_RAW,multiply,mechanist_explosion_reference
from .shield_source_inventory import float32_signed_number_raw

SOURCE='rouge/data/modifier-packet-source.json'
SOURCE_SHA256='3a92394f4a5dddf51d9b926d5942e47213dc3c20d9fd8148ce178e9d494952d4'
EPSILON=42950
FAMILY_IDS={
 'physical':tuple('rogue_6_relic_legacy_'+str(i) for i in (5,6,7)),
 'magic':tuple('rogue_6_relic_legacy_'+str(i) for i in (8,9,10)),
 'true':('rogue_6_relic_legacy_11',),
 'healing':tuple('rogue_6_relic_legacy_'+str(i) for i in (81,82,83)),
 'elemental':('rogue_6_relic_legacy_104','rogue_6_relic_fight_21')}
TYPE={'physical':'PHYSICAL','magic':'MAGICAL','true':'PURE','healing':'HEAL','elemental':'ELEMENT'}
BASE_ONE=frozenset(('physical','magic','true'))


@lru_cache(maxsize=1)
def _source_data():
    root=Path(__file__).resolve().parents[1]
    try:
        raw=(root/SOURCE).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA256:return None
        data=json.loads(raw)
        for path,digest in data['source_artifacts_sha256'].items():
            if hashlib.sha256((root/path).read_bytes()).hexdigest()!=digest:return None
        return data
    except (OSError,ValueError,KeyError):return None


def source_data():
    return deepcopy(_source_data())


def _tri(value,name):
    if value is not None and type(value) is not bool:raise ValueError(name+'需要true、false或null。')


def _raw(value):
    if value is not None and (type(value) is not int or not MIN_RAW<=value<=MAX_RAW):
        raise ValueError('FP原值需要signed64整数或null，不能填布尔值/小数。')
    return value


def _bits(value):
    if value is not None and (type(value) is not int or not 0<=value<=0xffffffff):
        raise ValueError('float32_bits需要32位整数或null。')


def _and(*values):return False if False in values else None if None in values else True
def _not(value):return None if value is None else not value
def _equal(value,expected):return None if value is None else value==expected


def cancelled_reference(delta_type,value):
    if delta_type=='CANCELLED':return True
    zero=None if value is None else abs(value)<EPSILON
    if zero is True:return True
    return None if delta_type is None else zero


def is_damage_reference(damage_type,target_type):
    attack=None if damage_type is None else damage_type not in ('NONE','HEAL')
    return _and(attack,_equal(target_type,'HP'))


def module_ids(family,relic_ids):
    return ['damage:'+family] if family in BASE_ONE else [family+':'+rid for rid in relic_ids]


def _order(value,identities,name):
    if value is None:return list(permutations(identities))
    if type(value) is not list or any(type(v) is not str for v in value) or len(value)!=len(identities) or set(value)!=set(identities):
        raise ValueError(name+'需要包含各身份一次的完整排列或null。')
    return [tuple(value)]


def _input(packet_input):
    if type(packet_input) is not dict:raise ValueError('input需要独立入链FP或爆炸返回声明。')
    if packet_input.get('kind')=='entry_fp':
        if set(packet_input)!={'kind','raw'}:raise ValueError('entry_fp需要kind与raw。')
        return _raw(packet_input['raw']),None
    if packet_input.get('kind')!='explosion_return' or set(packet_input)!= {'kind','explosion','call_id','branch','value_unchanged_at_entry'}:
        raise ValueError('爆炸返回输入需要独立调用身份、分支与入链未变资格。')
    if type(packet_input['call_id']) is not str:raise ValueError('call_id需要实际声明调用身份。')
    if packet_input['branch'] not in ('scaled','baseline'):raise ValueError('爆炸分支需要scaled或baseline。')
    _tri(packet_input['value_unchanged_at_entry'],'入链值未变')
    report=mechanist_explosion_reference(packet_input['explosion'])
    row=next((r for r in report['rows'] if r['id']==packet_input['call_id']),None)
    if row is None:raise ValueError('声明爆炸中没有这个调用身份。')
    raw=row['branches'][packet_input['branch']]['calculate_damage_raw_reference']
    return raw if packet_input['value_unchanged_at_entry'] is True else None,report


def _validate(payload):
    keys={'family','relic_ids','acquisition_order','application_order','ordinary_native_path','no_intervening_changes',
        'groups_start_empty','float_rounding','packet','modules'}
    if type(payload) is not dict or set(payload)!=keys:raise ValueError('请使用完整藏品逐包修饰声明。')
    family=payload['family'];ids=payload['relic_ids']
    if type(family) is not str or family not in FAMILY_IDS:raise ValueError('family需要healing/physical/magic/true/elemental。')
    if type(ids) is not list or not 1<=len(ids)<=3 or any(type(i) is not str for i in ids) or len(set(ids))!=len(ids) or not set(ids)<=set(FAMILY_IDS[family]):
        raise ValueError('仅接受同族1–3件已绑定藏品，各来源只选一次。')
    acquisitions=_order(payload['acquisition_order'],ids,'预处理顺序')
    slots=module_ids(family,ids);applications=_order(payload['application_order'],slots,'修饰顺序')
    for k in ('ordinary_native_path','no_intervening_changes','groups_start_empty'):_tri(payload[k],k)
    if payload['float_rounding'] not in (None,'nearest_even'):raise ValueError('单精度舍入仅核准nearest_even或未知null。')
    p=payload['packet']
    if type(p) is not dict or set(p)!={'input','modifier_exists','damage_type','target_type','delta_type','value_immutable'}:
        raise ValueError('packet需要独立入链值、存在、类型/目标/方向及不可改值标记。')
    for k in ('modifier_exists','value_immutable'):_tri(p[k],k)
    for k,allowed in (('damage_type',('NONE','PHYSICAL','MAGICAL','PURE','HEAL','ELEMENT')),
                      ('target_type',('HP','SP','EP')),('delta_type',('CANCELLED','ADD','MINUS'))):
        if p[k] is not None and (type(p[k]) is not str or p[k] not in allowed):raise ValueError(k+'不在已核准类型内，未知请填null。')
    initial,explosion=_input(p['input'])
    modules=payload['modules']
    if type(modules) is not list or len(modules)!=len(slots):raise ValueError('每个合并后模块需要独立读取资格，不能按base_one藏品分别乘。')
    seen=set()
    for module in modules:
        if type(module) is not dict or set(module)!={'id','enabled','blackboard_available','number_readable','factor_basis','float32_bits'}:
            raise ValueError('模块需要身份、启用/黑板/数字资格、倍率依据及float32_bits。')
        if type(module['id']) is not str or module['id'] not in slots or module['id'] in seen:raise ValueError('模块身份缺失、重复或不属于本族。')
        seen.add(module['id'])
        for k in ('enabled','blackboard_available','number_readable'):_tri(module[k],k)
        _bits(module['float32_bits'])
        if module['factor_basis'] not in ('nominal_parameter','independent_number'):raise ValueError('倍率依据需要nominal_parameter或independent_number。')
        if module['factor_basis']=='nominal_parameter' and module['float32_bits'] is not None:
            raise ValueError('名义参数不能另填bits覆盖。')
    return family,ids,acquisitions,applications,slots,initial,explosion


def _f32(value):return struct.unpack('<f',struct.pack('<f',value))[0]
def _to_bits(value):return struct.unpack('<I',struct.pack('<f',value))[0]


def _same(values):
    first=values[0]
    return first if first is not None and all(v==first for v in values) else None


def _normal_conversion(bits):
    """No invalid/denormal/inexact conversion condition in the known domain.

    For other inputs the current MXCSR exception masks are not established;
    a retained setter value cannot prove that CVTT returned normally.
    """
    if bits is None:return None
    raw=float32_signed_number_raw(bits)
    if raw is None:return None
    exponent=(bits>>23)&255;fraction=bits&0x7fffff
    if exponent==0:return True if fraction==0 else None
    significand=fraction+(1<<23);shift=exponent-118
    return True if shift>=0 or significand%(1<<-shift)==0 else None


def _factor(state,bits):
    read=state['number_readable']
    chosen=bits if state['factor_basis']=='nominal_parameter' else state['float32_bits']
    if read is False:return [ONE],True,True
    normal=_normal_conversion(chosen)
    if normal is not True:return [],False if read is True else None,None
    raw=float32_signed_number_raw(chosen)
    return [raw] if read is True else sorted({ONE,raw}),False if read is True else None,True


def _packet_multiply(value,factor):
    # A valid signedFP unknown is annihilated by0 only after the conversion
    # and active body have been qualified; skip branches are merged separately.
    return 0 if value==0 or factor==0 else multiply(value,factor)


def _execute(value,p,state,bits):
    bb=state['blackboard_available']
    result={'factor_raw_reference':None,'default_one_used_reference':None,'attempted_raw_reference':None,
        'stored_raw_reference':value,'setter_called_reference':False,'node_return_reference':None,
        'normal_return_reference':True,'status':'skipped','factor_candidate_raws':[]}
    if bb is False:
        result.update(status='missing_blackboard_exception',normal_return_reference=False);return result
    if bb is not True:
        result.update(status='unknown_execution_or_blackboard',normal_return_reference=None,
            stored_raw_reference=value if p['value_immutable'] is True else None,setter_called_reference=None);return result
    candidates,default,normal=_factor(state,bits)
    result.update(default_one_used_reference=default,factor_candidate_raws=candidates)
    if normal is not True:
        result.update(status='unqualified_float_conversion',normal_return_reference=None,
            stored_raw_reference=value if p['value_immutable'] is True else None,setter_called_reference=None);return result
    factor=_same(candidates);attempted=_same([_packet_multiply(value,c) for c in candidates])
    immutable=p['value_immutable']
    stored=value if immutable is True else attempted if immutable is False else _same([value,attempted])
    result.update(factor_raw_reference=factor,attempted_raw_reference=attempted,
        stored_raw_reference=stored,setter_called_reference=True,node_return_reference=True,
        status='conditional_reference' if stored is not None else 'unknown_numeric_or_setter')
    return result


def _boards(family,order,records,payload):
    if not records or payload['float_rounding']!='nearest_even':return {i:None for i in module_ids(family,list(order))}
    if family in BASE_ONE:
        if payload['groups_start_empty'] is not True:return {'damage:'+family:None}
        value=None
        for identity in order:
            incoming=_f32(records[identity]['parameter'])
            value=incoming if value is None else _f32(_f32(value+incoming)-1.0)
        return {'damage:'+family:_to_bits(value)}
    return {family+':'+identity:records[identity]['parameter_float32_bits'] for identity in order}


def _step(value,p,definition,state,bits):
    cancelled=cancelled_reference(p['delta_type'],value)
    damage=is_damage_reference(p['damage_type'],p['target_type'])
    type_pass=_equal(p['damage_type'],definition['type'])
    early_stop=cancelled if definition['family']=='healing' else _and(cancelled,damage)
    # For the selected nonNONE/nonHEAL masks, type_pass implies the same
    # damageType part of isDamage. Do not treat those two tests as independent.
    composite_stop=cancelled if definition['family']=='healing' else _and(cancelled,_equal(p['target_type'],'HP'))
    allowed=_and(type_pass,_not(composite_stop));active=_and(state['enabled'],allowed)
    result={'module_id':state['id'],'name':definition['name'],'input_raw_reference':value,
        'cancelled_reference':cancelled,'is_damage_reference':damage,'type_pass_reference':type_pass,
        'early_stop_reference':early_stop,'body_active_reference':active,
        'number_key':definition['number_key'],'nominal_float32_bits':bits,
        'factor_raw_reference':None,'default_one_used_reference':None,'attempted_raw_reference':None,
        'stored_raw_reference':value,'setter_called_reference':False,'node_return_reference':None,
        'normal_return_reference':True,'status':'skipped'}
    if active is False:
        if state['enabled'] is True:result['node_return_reference']=False
        return result
    executed=_execute(value,p,state,bits)
    if active is True:result.update(executed);return result
    # Unknown activation merges the skipped and executed alternatives. Equal
    # values/normal returns remain known, without claiming a setter was called.
    result.update(stored_raw_reference=_same([value,executed['stored_raw_reference']]),
        normal_return_reference=_same([True,executed['normal_return_reference']]),
        setter_called_reference=_same([False,executed['setter_called_reference']]),
        status='unknown_execution_or_blackboard')
    return result


def modifier_packet_reference(payload):
    family,ids,acquisitions,applications,slots,initial,explosion=_validate(payload)
    source=_source_data();valid=source is not None
    records={r['relic_id']:r for r in source['sources']} if valid else {}
    definitions={}
    for slot in slots:
        members=[records[i] for i in ids if i in records and (family in BASE_ONE or slot==family+':'+i)]
        definitions[slot]={'family':family,'type':TYPE[family],'number_key':'heal_scale' if family=='healing' else 'damage_scale',
            'name':' / '.join(r['name'] for r in members) or slot,'source_ids':[r['relic_id'] for r in members]}
    ready=valid and payload['ordinary_native_path'] is True and payload['no_intervening_changes'] is True and payload['packet']['modifier_exists'] is True
    states={m['id']:m for m in payload['modules']};cases=[]
    for acquisition in acquisitions:
        boards=_boards(family,acquisition,records,payload)
        for application in applications:
            value=initial if ready else None;normal=True if ready else None;steps=[]
            for slot in application:
                if normal is not True:
                    steps.append({'module_id':slot,'name':definitions[slot]['name'],'status':'not_called_after_unqualified_chain',
                        'normal_return_reference':None,'stored_raw_reference':None,'attempted_raw_reference':None});continue
                step=_step(value,payload['packet'],definitions[slot],states[slot],boards[slot]);steps.append(step)
                value=step['stored_raw_reference'];normal=step['normal_return_reference']
            final=value if normal is True else None
            cases.append({'preprocessing_order':list(acquisition),'application_order':list(application),
                'nominal_blackboard_bits':boards,'steps':steps,'normal_return_reference':normal,
                'last_stored_raw_reference':value,'declared_chain_raw_reference':final})
    known=sorted({c['declared_chain_raw_reference'] for c in cases if c['declared_chain_raw_reference'] is not None})
    complete=all(c['declared_chain_raw_reference'] is not None for c in cases)
    return {'family':family,'relic_ids':list(ids),'selected_sources':[deepcopy(records[i]) for i in ids if i in records],
        'module_definitions':definitions,'declared_entry_raw':initial,'explosion_base_reference':explosion,
        'cases':cases,'declared_order_combination_count':len(cases),'known_discrete_raw_references':known,
        'all_declared_cases_numeric':complete,'single_declared_chain_raw_reference':known[0] if complete and len(known)==1 else None,
        'source_valid':valid,'source':SOURCE,'source_sha256':SOURCE_SHA256,'actual_modifier_value':None,
        'actual_hp_loss':None,'actual_healing':None,'actual_complete_total':None,'actual_order':None,
        'order_counts_are_probabilities':False,'actual_probability_by_order':None,'events_scheduled':False,
        'current_hotfix_equivalence_proven':False,'notes':[
            '同类base_one来源先逐次单精度old+new−1合并，再形成一个修饰模块；normal来源各自乘当前FP包，治疗生命回复通道不重复计入。',
            '列举的是独立声明顺序组合，不证明实际可达、获取顺序与事件容器顺序的对应关系，也不赋概率或均值。',
            '名义单精度参考须声明nearest_even；未知舍入/非空背景组不能默认补成名义参数。独立黑板数字与名义参数互斥。',
            '取消为delta取消或Abs(FP值)<42950，负大值不先夹正。治疗取消直接停止；伤害早门仅在取消且isDamage时停止，再按实际伤害类型过滤。',
            '不可改值标记只抑制setter写入；黑板读取和FP乘法仍先执行，缺失对象仍可能异常。尝试值与保留值分列。',
            '未知启用/读取的分支只在数值或正常返回相同时闭合；取消与类型共享字段，不当作互不相关的未知。',
            'NaN、超域、非整定点转换等可能触发SIMD异常；当前异常掩码未证，保留原存储值不代表转换正常或后续已执行。',
            '明确数字读取失败才默认ONE，成功0/负值保持原值；缺对象、未确认读取及超出已核准数字转换域保持未知。',
            '爆炸基础返回只有修饰器已创建且到本次入口值未变时才能接入；不能借构造时默认标记证明后续仍可改值。',
            '数值只覆盖所选来源与声明无间插变化的普通原生链；实际库存、前后事件、命中、HP/EP/SP结算、完整总量和热更新未知。']}


def public_example(family='healing'):
    ids=list(FAMILY_IDS[family]);slots=module_ids(family,ids)
    return {'family':family,'relic_ids':ids,'acquisition_order':None,'application_order':None,
        'ordinary_native_path':True,'no_intervening_changes':True,'groups_start_empty':True,'float_rounding':'nearest_even',
        'packet':{'input':{'kind':'entry_fp','raw':1000*ONE},'modifier_exists':True,'damage_type':TYPE[family],
            'target_type':'HP','delta_type':'ADD' if family=='healing' else 'MINUS','value_immutable':False},
        'modules':[{'id':slot,'enabled':True,'blackboard_available':True,'number_readable':True,
                    'factor_basis':'nominal_parameter','float32_bits':None} for slot in slots]}
