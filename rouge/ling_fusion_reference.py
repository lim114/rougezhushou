"""Ling S3 documented form arithmetic, separate from actual fusion/cast clocks."""
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path

from .p2_supplemental_token_modules import compare_supplemental_token_modules, LABELS

FORM_FIELDS = ('hp', 'attack', 'defense', 'resistance', 'attack_speed',
               'base_interval', 'block', 'deployment_slots', 'damage_type')
FORM_LABELS = {**LABELS, 'deployment_slots': '文档部署位占用', 'damage_type': '普攻伤害类型'}


@lru_cache(maxsize=1)
def fusion_source():
    return json.loads((Path(__file__).parent / 'data' / 'ling-fusion-source.json')
                      .read_text(encoding='utf-8'))


def documented_form_values(base, skill_rank, form, active, qualified):
    """Same documented form layer for endpoints and explicit native branches."""
    if type(skill_rank) is not int or not 1 <= skill_rank <= 10:
        raise ValueError('令三技能等级需要1–10整数。')
    if form not in ('basic', 'advanced') or type(active) is not bool or type(qualified) is not bool:
        raise ValueError('形态与技能状态需要明确声明。')
    values = dict.fromkeys(FORM_FIELDS); trace = {}
    if not qualified: return values, trace
    source = fusion_source(); skill = source['owner_skill_levels'][skill_rank - 1]
    buff = source['merged_additions'] if form == 'advanced' else {}
    for key in ('hp', 'attack', 'defense', 'resistance'):
        bonus = buff.get(key, 0) + (skill.get(key, 0) if active else 0)
        values[key] = base[key] * (1 + bonus)
        trace[key] = {'cultivation_and_direct_equipment': base[key],
                      'form_additive_percent': buff.get(key, 0),
                      'skill_additive_percent': skill.get(key, 0) if active else 0, 'factor': 1 + bonus}
    values['attack_speed'] = base['attack_speed']
    values['base_interval'] = base['base_interval'] + buff.get('base_interval', 0)
    values['block'] = base['block'] + buff.get('block', 0)
    values['deployment_slots'] = 2 if form == 'advanced' else 1
    values['damage_type'] = '法术' if form == 'advanced' else '物理'
    return values, trace


def ling_fusion_reference(training, selection, skill_rank=10):
    if type(skill_rank) is not int or not 1 <= skill_rank <= 10:
        raise ValueError('令三技能等级需要1–10整数；8–10对应专精一至三。')
    endpoints = compare_supplemental_token_modules('char_2023_ling', training, selection)
    variant = next(v for v in endpoints['variants'] if v['skill'] == 3)
    source = fusion_source()
    if variant['token_id'] != source['token_id'] or variant['skill_id'] != source['owner_skill_id']:
        raise ValueError('令三技能与弦惊原始身份不匹配。')
    rows = []
    for stage in variant['stages']:
        qualified = variant['skill_qualified'] and stage['state'] != 'host_gate_unmet'
        for form in ('basic', 'advanced'):
            for active in (False, True):
                values, trace = documented_form_values(stage['values'], skill_rank, form, active, qualified)
                rows.append({'module_level': stage['module_level'], 'form': form,
                             'skill_active_declared': active, 'skill_rank': skill_rank,
                             'state': 'documented_formula_reference' if qualified else 'host_gate_unmet',
                             'values': values, 'attribute_trace': trace,
                             'equipment_source_selector': stage['source_selector'],
                             'actual_current_panel': None, 'actual_fusion_eligible': None,
                             'actual_presence': None, 'actual_skill_active': None,
                             'actual_fusion_or_mode_switch_seconds': None,
                             'full_skill_damage': None, 'cycle_dps': None})
    return {'operator': 'char_2023_ling', 'operator_name': '令', 'token_id': source['token_id'],
            'token_name': variant['token_name'], 'host_training': endpoints['host_training'],
            'selection': deepcopy(selection), 'skill_rank': skill_rank,
            'rows': rows, 'scope': 'documented_ling_s3_form_and_skill_formula_reference',
            'sources': deepcopy(source['sources']), 'source_commit': source['source_commit'],
            'notes': [
                '各行是明确培养端点、直接装备加值和所选形态/技能状态的文档算式参考；并非当前实际面板。',
                '高级形态与技能的攻击/防御百分比在同一层相加，不把两者倍率叠乘。',
                '未自动判断合成对象、部署先后、位置、技能切换或附着；不采集战斗信息。',
                '部署位是文档占用参数，不代表当前空余位、部署资格或在场数量。',
                '间隔是基础参数，不证明首击、前后摇、命中/持续伤害首跳和完整技能时钟。',
                '藏品、分队、其它属性修正及当前热更新未在本表叠加；完整当前面板、伤害与周期未知。']}


def format_ling_fusion_reference(result):
    lines = ['令 · 弦惊基础/高级形态与宁作吾状态对照（文档算式）',
             f"技能等级：{result['skill_rank']}；独立实体精英资料{result['selection']['token_elite']} · "
             + ('1级端点' if result['selection']['endpoint'] == 'first' else '满级端点')]
    for row in result['rows']:
        mode = '基础形态' if row['form'] == 'basic' else '高级形态'
        active = '技能开启声明' if row['skill_active_declared'] else '技能未开启声明'
        values = '；'.join(FORM_LABELS[k] + ' ' +
                          ('未知' if row['values'][k] is None else
                           row['values'][k] if isinstance(row['values'][k], str) else f"{row['values'][k]:g}")
                          for k in FORM_FIELDS)
        lines.append(f"模组{row['module_level']} · {mode} · {active}：{values}")
    lines.extend(result['notes'])
    return '\n'.join(lines)
