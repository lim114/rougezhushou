"""S2 shield initialization from declared recipient MAX_HP snapshots.

The owner's cultivation/relic subtotal is an optional numerical input reference,
never a claim about the actual Attributes.GetValue at ON_BUFF_START.
"""
from copy import deepcopy
import math
import struct

from .catalog import catalog
from .barrier_blackboard import (ONE, MAX_RAW, SOURCE, SOURCE_SHA256,
    ROUNDING_MODES, source_valid, float32_number_raw, shield_product_reference)
from .mechanist_barrier_ledger import _all, _boolean, _integer, _label, RECIPIENTS


SNAPSHOT_KEYS={'id','recipient','basis','max_hp_raw','target_attributes_available',
    'blackboard_available','ratio_numeric_readable','ratio_basis','ratio_float32_bits'}


def mechanist_shield_grants(scenario, snapshots, ordinary_native_path, float_rounding=None):
    from .calibration import _scenario, panel_layers
    s=_scenario(scenario)
    if s['operator']!='mechanist' or s['skill']!=2:
        raise ValueError('屏障初值参考只适用于机械师二技能。')
    if any(k in s for k in ('base_attack','base_hp','hp','base_defense')):
        raise ValueError('培养面板不能覆盖白值；请使用独立创建时FP快照声明。')
    rank=_integer(s['skill_rank'],'技能等级',1,10)
    _boolean(ordinary_native_path,'普通原生路径')
    if float_rounding is not None and float_rounding not in ROUNDING_MODES:
        raise ValueError('float_rounding需要明确单精度舍入环境，或null。')
    if type(snapshots) is not list or not 1<=len(snapshots)<=50:
        raise ValueError('初始化快照需要1–50份独立声明。')
    panel=panel_layers(s)
    hp=panel['panels']['已覆盖常态天赋与效果']['hp']
    model_raw=int(hp)*ONE if (type(hp) in (int,float) and math.isfinite(hp)
        and hp>=0 and float(hp).is_integer() and hp<=MAX_RAW//ONE) else None
    parameter=catalog()['operators']['mechanist']['skills'][1]['levels'][rank-1]['values']['hp_ratio']
    parameter_bits=struct.unpack('<I',struct.pack('<f',parameter))[0]
    rows=[];seen=set();valid=source_valid()
    for snapshot in snapshots:
        if type(snapshot) is not dict or set(snapshot)!=SNAPSHOT_KEYS:
            raise ValueError('每份创建快照需完整保留模板字段。')
        label=_label(snapshot['id'])
        if label in seen:raise ValueError('创建快照标签不能重复。')
        seen.add(label)
        recipient=snapshot['recipient']
        if type(recipient) is not str or recipient not in RECIPIENTS:
            raise ValueError('recipient需要owner或structure。')
        basis=snapshot['basis']
        if basis=='owner_model_known_subtotal':
            if recipient!='owner' or snapshot['max_hp_raw'] is not None:
                raise ValueError('模型小计仅适用本体，不能借本体生命替代结构性原理。')
            maximum=model_raw
        elif basis=='independent_fp_snapshot':
            maximum=snapshot['max_hp_raw']
            if maximum is not None:_integer(maximum,'创建节点MAX_HP快照原值')
        else:raise ValueError('basis需要本体模型小计或独立FP快照。')
        for field in ('target_attributes_available','blackboard_available','ratio_numeric_readable'):
            _boolean(snapshot[field],field)
        ratio_basis=snapshot['ratio_basis'];bits=snapshot['ratio_float32_bits']
        if ratio_basis=='fixed_skill_parameter':
            if bits is not None:raise ValueError('固定技能参数不得注入另一份bits。')
            bits=parameter_bits
        elif ratio_basis=='independent_float32_bits':
            if bits is not None:float32_number_raw(bits)
        else:raise ValueError('ratio_basis需要固定技能参数或独立单精度bits。')
        readable=snapshot['ratio_numeric_readable']
        ratio=ONE if readable is False else float32_number_raw(bits) if readable is True and bits is not None else None
        gate=None if not valid or ordinary_native_path is not True else _all(
            snapshot['target_attributes_available'],snapshot['blackboard_available'])
        reference=None
        if gate is True and maximum is not None and ratio is not None:
            reference=shield_product_reference(maximum,ratio,float_rounding)
        rows.append({'id':label,'recipient':recipient,'recipient_name':RECIPIENTS[recipient],
            'basis':basis,'max_hp_snapshot_raw_reference':maximum,
            'model_hp_known_subtotal':hp if basis=='owner_model_known_subtotal' else None,
            'ratio_numeric_readable':readable,'ratio_float32_bits_reference':bits,
            'ratio_raw_reference':ratio,'default_one_used_reference':_all(gate,None if readable is None else not readable),
            'initialization_gate':gate,'numeric_reference':reference,
            'shield_readback_raw_reference':reference['shield_readback_raw'] if reference else None,
            'actual_initial_shield':None,'actual_initialized_instance':None,'actual_creation_seconds':None,
            'snapshot_declaration':deepcopy(snapshot)})
    return {'operator':'机械师','skill':2,'skill_rank':rank,'scenario':deepcopy(s),
        'context_token':panel['context_token'],'rows':rows,'source':SOURCE,'source_sha256':SOURCE_SHA256,
        'source_valid':valid,'nominal_hp_ratio_parameter':parameter,
        'nominal_hp_ratio_float32_bits':parameter_bits,'float_rounding':float_rounding,
        'actual_initial_shield':None,'current_hotfix_equivalence_proven':False,
        'warnings':deepcopy(panel['warnings']),
        'notes':['创建节点读取屏障受益对象的MAX_HP；不是当前生命，也不借本体生命计算结构性原理。',
            '本体模型选项使用当前培养、模组、藏品等已覆盖生命小计作为整数输入参考；缺失加成与实际创建快照仍未知。',
            '先列FP即时乘积，再列单精度黑板写入与FP读回；不按普通十进制乘法或整数四舍五入替代。',
            '只有明确数字读取失败才用原生默认倍率1；未知保持未知，成功读取0仍为0。',
            '舍入模式为独立声明，不认证实际MXCSR；溢出路径不夹成最大值。',
            '实际创建、初始化完成、属性修正顺序与时刻、黑板来源/覆盖、实例标志和当前热更新仍未知。']}


def public_snapshots():
    common={'target_attributes_available':True,'blackboard_available':True,
        'ratio_numeric_readable':True,'ratio_basis':'fixed_skill_parameter','ratio_float32_bits':None}
    return [{'id':'本体模型生命小计','recipient':'owner','basis':'owner_model_known_subtotal','max_hp_raw':None,**common},
        {'id':'结构性原理独立3001快照','recipient':'structure','basis':'independent_fp_snapshot','max_hp_raw':3001*ONE,**common}]
