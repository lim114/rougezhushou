"""Attach conditional native arithmetic to existing model snapshots.

No model output is used as evidence of a protected decode, actual inventory,
normal native call or current game state. Each phase has a fresh nominal basis.
"""
from copy import deepcopy
import math
import struct

Q = 1 << 32
FIELDS = ('hp', 'attack', 'defense', 'resistance', 'attack_speed')
PHASE_NAMES = {'cultivation':'培养与模组', 'rune':'藏品与分队符文写回',
               'normal':'已覆盖常态天赋与效果', 'skill':'技能期间参考'}
LABELS = {'hp':'生命值', 'attack':'攻击力', 'defense':'防御力',
          'resistance':'法术抗性', 'attack_speed':'攻速属性'}


def _number(value):
    return value if type(value) in (int, float) and math.isfinite(value) else None


def _bits(value):
    value = _number(value)
    if value is None:
        return None
    try:
        bits = struct.unpack('<I', struct.pack('<f', value))[0]
        return bits if bits & 0x7f800000 != 0x7f800000 else None
    except (OverflowError, struct.error):
        return None


def _raw(value):
    # This conversion specifies the legacy model's nominal Single input. It
    # does not identify runtime Blackboard bits or the actual rounding mode.
    from .deployment import _fp
    try:
        return _fp(value) if _number(value) is not None else None
    except (ValueError, OverflowError):
        return None


def _sum_raw(values):
    from .mechanist_explosion_math import add
    out = 0
    for value in values:
        out = add(out, value)
    return out


def _product(left, right):
    from .mechanist_explosion_math import multiply
    return 0 if left == 0 or right == 0 else multiply(left, right)


def _term(basis, *, addition=0, multiplier=0, final_addition=0, final_scaler=1):
    return {'basis':basis, 'addition':[addition], 'multiplier':[multiplier],
            'final_addition':[final_addition], 'final_scaler':[final_scaler]}


def _record(phase, field, value, term=None):
    from .mechanist_explosion_math import multiply
    term = term or _term(None)
    scaler = Q
    for value_factor in term['final_scaler']:
        scaler = _product(scaler, _raw(value_factor))
    return {'id':phase+'.'+field, 'field':field, 'phase':phase, 'model_value':_number(value),
            'basis_kind':'nominal_single', 'basis_single_bits':_bits(term['basis']), 'basis_fp_raw':None,
            'addition_raw':_sum_raw([_raw(v) for v in term['addition']]),
            'multiplier_delta_raw':_sum_raw([_raw(v) for v in term['multiplier']]),
            'final_addition_raw':_sum_raw([_raw(v) for v in term['final_addition']]),
            'final_scaler_raw':scaler}


def prepare(scenario, cultivated, rune_attributes, runes):
    """Consume the same resolved rune objects used by the main calculation."""
    from .relic_attributes import FIELDS as RUNE_FIELDS
    from .mechanist_explosion_math import add, multiply
    rows=[]
    for field in FIELDS:
        if field not in cultivated:
            continue
        rows.append(_record('cultivation',field,cultivated[field],_term(cultivated[field])))
        row=_record('rune',field,rune_attributes[field],_term(cultivated[field]))
        selected=[e for e in runes if RUNE_FIELDS[e['kind']]==field]
        def term_value(effect):
            if effect.get('native_count_scale')=='float32_before_fp':
                from .deployment import _single
                try:
                    return _raw(_single(_single(effect['native_rune_base'])*_single(effect['native_rune_factor'])))
                except (ValueError, OverflowError):
                    return None
            return _raw(effect['value'])
        row['addition_raw']=_sum_raw([term_value(e) for e in selected if e['formula_item']=='ADDITION'])
        row['multiplier_delta_raw']=_sum_raw([term_value(e) for e in selected if e['formula_item']=='MULTIPLIER'])
        scaler=Q
        for effect in selected:
            if effect['formula_item']=='FINAL_SCALER':
                factor=term_value(effect)
                if factor is not None and factor<0:
                    factor=add(factor,Q)
                scaler=_product(scaler,factor)
        row['final_scaler_raw']=scaler
        rows.append(row)
    scenario['_panel_native_prepared']={'fields':rows,'rune_sources':deepcopy(runes),
        'scope':'Same resolved current-operator sources; primitive Single/FP interpretation is nominal, not runtime evidence.'}


def normal_terms(attributes, base_attack, *, hp_multiplier=0, attack_multiplier=0,
                 defense_multiplier=0, defense_flat=0, resistance_addition=0,
                 attack_speed_addition=0, attack_flat=0):
    return {'hp':_term(attributes['hp'],multiplier=hp_multiplier),
            'attack':_term(base_attack,multiplier=attack_multiplier,final_addition=attack_flat),
            'defense':_term(attributes['defense'],multiplier=defense_multiplier,final_addition=defense_flat),
            'resistance':_term(attributes['resistance'],addition=resistance_addition),
            'attack_speed':_term(attributes['attack_speed'],addition=attack_speed_addition)}


def first_three_skill_terms(scenario, attributes, effects):
    from .catalog import catalog
    level=catalog()['operators'][scenario['operator']]['skills'][scenario['skill']-1]['levels'][scenario.get('skill_rank',10)-1]
    bb=level['values']
    return {'attack':_term(scenario['base_attack'],multiplier=bb.get('atk',0)+sum(e['value'] for e in effects if e['kind']=='attack_pct')),
            'attack_speed':_term(attributes['attack_speed'],addition=bb.get('attack_speed',0)+sum(e['value'] for e in effects if e['kind']=='attack_speed'))}


def install(estimate, normal, skill):
    estimate['_panel_native_terms']={'normal':normal,'skill':skill}


def unknown_skill_terms():
    return {'attack':_term(None),'attack_speed':_term(None)}


def add_final_term(estimate, phase, field, bucket, value):
    terms=estimate.get('_panel_native_terms',{}).get(phase,{})
    if field in terms:
        terms[field][bucket].append(value)


def finish(scenario, result):
    """Evaluate once; calibration and report consume this exact main result."""
    from .panel_native_finalization import panel_native_finalization
    estimate=result['estimate'];terms=estimate.pop('_panel_native_terms',{})
    prepared=scenario.get('_panel_native_prepared',{'fields':[],'rune_sources':[]})
    rows=deepcopy(prepared['fields'])
    for phase, field_terms in terms.items():
        for field,term in field_terms.items():
            if phase=='normal':
                stats=estimate['base_stats']
                value=stats.get('attack_speed_reference',stats['attack_speed']) if field=='attack_speed' else stats.get(field)
            else:
                stats=estimate['skill']
                value=stats.get('skill_attack_speed_reference') if field=='attack_speed' else stats.get('skill_attack')
            rows.append(_record(phase,field,value,term))
    evaluated=panel_native_finalization({'fields':rows})
    evaluated['phase_ids']={phase:[row['id'] for row in evaluated['fields'] if row['phase']==phase] for phase in PHASE_NAMES}
    evaluated['input_provenance']={'rune_sources':deepcopy(prepared['rune_sources']),
        'basis':'independent_nominal_model_snapshots',
        'bucket_values':'nominal interpretations of existing model primitives, not observed modifier cache values',
        'protected_parent_result_propagated':False,'normal_native_calls_inferred':False,
        'extended_skill_input_scope':'Only first-three skill primitives closed here; other skill phases keep unknown native bases.'}
    result['panel_native_finalization']=evaluated
    estimate['native_panel_reference_key']='panel_native_finalization'


def conditional_value(row):
    """Presentation reference only, never a replacement for model stats."""
    if not row['conditional_complete']:
        return None
    ref=row['references']
    if row['phase'] in ('normal','skill'):
        return None if ref['getter_result_raw'] is None else ref['getter_result_raw']/Q
    if row['phase']=='cultivation':
        return None if ref['input_fp_raw'] is None else ref['input_fp_raw']/Q
    writer=ref['writer']
    if not writer:
        return None
    if writer['encoder_argument_reference'] is not None:
        return writer['encoder_argument_reference']
    bits=writer['encoder_argument_bits_reference']
    return None if bits is None else struct.unpack('<f',struct.pack('<I',bits))[0]


def report_section(result):
    from .reporting import section,metric
    data=result.get('panel_native_finalization')
    if data is None:
        return None
    metrics=[metric(row['id'],('常态' if row['phase']=='normal' else '技能期间')+' · '+LABELS[row['field']]+'算式参考',conditional_value(row))
             for row in data['fields'] if row['phase'] in ('normal','skill')]
    metrics.append(metric('complete_native_panel','完整原生面板',None))
    return section('panel_native_finalization','面板算式与精度核验',metrics,[
        '保留原有模型值；这里使用已选模型参数的名义位型，按已核验原生公式给条件参考，不是实机读值。',
        '各层基础值分别取名义快照；不把编码参数当作下一层解码结果，也不证明真实修饰器、范围覆盖或当前热更新。',
        '藏品符文写回与常态/技能重算的公式和存储步骤分开；详情与四层对应见局外工具的面板查询。',
        '来源核验：'+('通过' if data['source_valid'] else '未通过，条件参考已隐藏')+'；完整原生面板与实际读值仍未知。'])
