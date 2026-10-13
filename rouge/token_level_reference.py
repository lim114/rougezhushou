"""Frozen token cultivation with both native interpolation branches retained.

The current installation candidate establishes the arithmetic, not the actual
KeepLowerValue instance, token cultivation or current-server table equivalence.
"""
from copy import deepcopy
from functools import lru_cache
import json
from itertools import product
import math
from pathlib import Path
import struct

from .p2_supplemental_token_modules import (compare_supplemental_token_modules,
    source_data, FIELDS, LABELS)

INTEGER_FIELDS = frozenset(('hp', 'attack', 'defense', 'deployment_cost', 'block'))


@lru_cache(maxsize=1)
def native_source():
    return json.loads((Path(__file__).parent / 'data/token-level-native-source.json')
                      .read_text(encoding='utf8'))


def single(value):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError('插值参数需要有限数值，不接受布尔值。')
    try:
        result = struct.unpack('<f', struct.pack('<f', value))[0]
    except (OverflowError, struct.error) as error:
        raise ValueError('插值参数超出单精度范围。') from error
    if not math.isfinite(result): raise ValueError('插值参数超出单精度有限范围。')
    return result


def interpolate_field(first, last, alpha, *, integer=False, keep_lower):
    if type(integer) is not bool or type(keep_lower) is not bool:
        raise ValueError('原生分支必须明确声明，不能用未知值推定false。')
    alpha = single(alpha)
    if not 0 <= alpha <= 1: raise ValueError('插值比例需要0–1。')
    first = single(first); last = single(last)
    difference = None if keep_lower else single(last - first)
    scaled = None if keep_lower else single(difference * alpha)
    numeric = first if keep_lower else single(first + scaled)
    if integer:
        if not -(2**31) <= numeric < 2**31: raise ValueError('整数属性超出声明支持范围。')
        value = int(round(numeric))
    else: value = numeric
    return {'value': value, 'first_single': first, 'last_single': last, 'alpha_single': alpha,
            'difference_single': difference, 'product_single': scaled,
            'before_typed_write': numeric, 'typed_write': 'nearest_even_int32' if integer else 'float32',
            'keep_lower_declared': keep_lower, 'actual_keep_lower': None}


def token_modules_by_host_level(operator, training, skill_rank=None):
    if type(training) is not dict or type(training.get('elite')) is not int or type(training.get('level')) is not int:
        raise ValueError('需要明确的宿主精英阶段和等级；未读取不能默认满级。')
    elite = training['elite']; level = training['level']
    if skill_rank is not None and (operator != 'char_2023_ling' or type(skill_rank) is not int or not 1 <= skill_rank <= 10):
        raise ValueError('形态技能等级仅适用于令，需要1–10整数。')
    first = compare_supplemental_token_modules(operator, training, {'token_elite': elite, 'endpoint': 'first'})
    last = compare_supplemental_token_modules(operator, training, {'token_elite': elite, 'endpoint': 'last'})
    source = source_data()['operators'][operator]
    variants = []; forms = []
    for left, right, raw in zip(first['variants'], last['variants'], source['variants']):
        if left['token_id'] != right['token_id'] or left['token_id'] != raw['token_id']:
            raise ValueError('独立实体身份不匹配。')
        frames = raw['token_raw']['phases'][elite]['attributesKeyFrames']
        lo = frames[0]['level']; hi = frames[-1]['level']
        if not lo <= level <= hi or hi == lo: raise ValueError('宿主等级没有同阶段实体的有界关键帧。')
        alpha = single(single(level - lo) / single(hi - lo))
        branches = []
        options = {key: {flag: interpolate_field(left['base_parameter_values'][key], right['base_parameter_values'][key],
                        alpha, integer=key in INTEGER_FIELDS, keep_lower=flag) for flag in (False, True)} for key in FIELDS}
        relevant = [key for key in FIELDS if options[key][False]['value'] != options[key][True]['value']]
        for flags in product((False, True), repeat=len(relevant)):
            declared = dict(zip(relevant, flags))
            branch = ('numeric_lerp' if not any(flags) else 'keep_lower_frame' if all(flags) else 'mixed_field_reference')
            traces = {key: deepcopy(options[key][declared.get(key, False)]) for key in FIELDS}
            base = {key: traces[key]['value'] for key in FIELDS}
            stages = []
            for old in left['stages']:
                qualified = left['skill_qualified'] and old['state'] != 'host_gate_unmet'
                values = dict.fromkeys(FIELDS)
                if qualified:
                    for key in FIELDS:
                        values[key] = base[key] + old['direct_additions'][key]
                    if values['deployment_cost'] < 0:
                        raise ValueError('来源产生负费用，不能沿未核验的下限规则继续。')
                stages.append({'module_level': old['module_level'], 'state': 'conditional_reference' if qualified else 'host_gate_unmet',
                               'values': values, 'source_selector': old['source_selector'],
                               'actual_current_values': dict.fromkeys(FIELDS)})
                if operator == 'char_2023_ling' and left['skill'] == 3 and skill_rank is not None:
                    from .ling_fusion_reference import documented_form_values
                    for form in ('basic', 'advanced'):
                        for active in (False, True):
                            values_form, trace = documented_form_values(values, skill_rank, form, active, qualified)
                            forms.append({'module_level': old['module_level'], 'form': form,
                                'skill_active_declared': active, 'skill_rank': skill_rank, 'cultivation_branch': branch,
                                'keep_lower_declared_for_varying_fields': declared,
                                'state': 'documented_formula_reference' if qualified else 'host_gate_unmet',
                                'values': values_form, 'attribute_trace': trace, 'actual_current_panel': None,
                                'actual_fusion_eligible': None, 'actual_presence': None, 'actual_skill_active': None,
                                'actual_fusion_or_mode_switch_seconds': None, 'full_skill_damage': None, 'cycle_dps': None})
            branches.append({'branch': branch, 'source_level': level,
                             'keep_lower_declared_for_varying_fields': declared, 'traces': traces, 'stages': stages})
        variants.append({'skill': left['skill'], 'token_id': left['token_id'], 'token_name': left['token_name'],
            'token_elite_reference': elite, 'token_level_reference': level, 'skill_qualified': left['skill_qualified'],
            'branches': branches, 'field_options': options, 'varying_fields': relevant,
            'combination_scope': 'independent_flag_conditional_output_bound_not_actual_distribution',
            'actual_keep_lower_flags': None, 'actual_cultivation': None})
    return {'operator': operator, 'operator_name': first['operator_name'], 'host_training': first['host_training'],
        'variants': variants, 'ling_forms': forms, 'skill_rank': skill_rank,
        'scope': 'documented_host_correspondence_and_both_native_lerp_branches',
        'native_source': deepcopy(native_source()), 'table_source_commit': first['source_commit'],
        'full_current_panel': None, 'complete_damage_or_cycle': None,
        'notes': ['培养资料按文档对应宿主精英和等级；不证明当前召唤物已创建、在场或实际培养。',
                  '每个属性的插值/保留下界独立列出；保留逐属性混合组合，合并相同数值，不默认实际标志false。',
                  '组合仅为独立标志假设下的条件输出边界，不证明所有组合可实际出现；无概率或默认推荐。',
                  '比例、减法、乘法及加法逐步单精度舍入；整数属性按已核对的最近偶数写回。',
                  '使用冻结的原始表及安装候选的默认算式；不证明当前服务器表或热更新与之等价。',
                  '只计本实体直接装备加值，本体信赖、潜能白值不流入；藏品、分队和其它修正未在此叠加。',
                  '完整当前面板、实际合成/模式、伤害、首击/结束时钟和周期仍未知。']}


def format_token_level_reference(result):
    training = result['host_training']
    lines = [result['operator_name'] + ' · 培养等级与原生插值分支对照',
             f"宿主声明：精英{training['elite']}、等级{training['level']}；实际实例/分支未知。"]
    for variant in result['variants']:
        lines.append(f"S{variant['skill']} · {variant['token_name']}")
        for branch in variant['branches']:
            caption = {'numeric_lerp': '数值插值分支', 'keep_lower_frame': '保留下界分支',
                       'mixed_field_reference': '逐属性混合条件'}[branch['branch']]
            kept = [LABELS[k] for k, v in branch['keep_lower_declared_for_varying_fields'].items() if v]
            if kept: caption += '（保留下界：' + '、'.join(kept) + '）'
            for stage in branch['stages']:
                values = '；'.join(LABELS[k] + ' ' + ('未知' if v is None else f'{v:g}') for k, v in stage['values'].items())
                lines.append(f"{caption} · 模组{stage['module_level']}：{values}")
    if result['ling_forms']:
        from .ling_fusion_reference import FORM_LABELS
        lines.append(f"令三技能形态参考：技能等级{result['skill_rank']}，仍按两条培养分支区分。")
        for row in result['ling_forms']:
            branch = {'numeric_lerp': '数值插值分支', 'keep_lower_frame': '保留下界分支',
                      'mixed_field_reference': '逐属性混合条件'}[row['cultivation_branch']]
            mode = '基础形态' if row['form'] == 'basic' else '高级形态'
            active = '技能开启' if row['skill_active_declared'] else '技能未开启'
            values = '；'.join(FORM_LABELS[k] + ' ' + ('未知' if v is None else v if isinstance(v, str) else f'{v:g}')
                              for k, v in row['values'].items())
            lines.append(f"{branch} · 模组{row['module_level']} · {mode} · {active}：{values}")
    lines.extend(result['notes'])
    return '\n'.join(lines)
