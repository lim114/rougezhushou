"""Manual account references joined to pinned squad conditions, without activation."""
from copy import deepcopy

from .run_config import config_data
from .squad_unlock_reference import squad_unlock_reference
from .technology_state import STATUS_LABELS


def squad_account_plan(account_state, grade):
    if type(grade) is not int or not 0 <= grade <= 15:
        raise ValueError('门槛对照等级需要0–15的整数。')
    rows = []
    for identity, record in config_data()['squads'].items():
        reference = squad_unlock_reference(identity)
        if reference is None:
            continue
        node = reference['technology_node_reference']
        manual = account_state.view(node['id']) if node else None
        gate = node['gate_reference'] if node else None
        rows.append({'squad_id': identity, 'name': record['name'],
                     'condition': reference['unlock_condition_reference'],
                     'technology_id': node['id'] if node else None,
                     'technology_name': node['name'] if node else None,
                     'manual_status': manual['status'] if manual else 'unknown',
                     'manual_source': manual['source'] if manual else None,
                     'manual_updated_at': manual['updated_at'] if manual else None,
                     'gate_grade_parameter': gate['enable_grade_parameter'] if gate else None,
                     'grade_parameter_met': grade >= gate['enable_grade_parameter'] if gate else None,
                     'account_unlocked': None, 'actual_activation': None,
                     'reference': deepcopy(reference)})
    return {'profile_id': account_state.selected_profile, 'profile_name': account_state.profile_name,
            'grade_reference': grade, 'rows': rows,
            'notes': ['科技状态来自当前资料档案的手动记录；解锁记录不证明条件已实际激活。',
                      '所选等级仅与原表3/6/9门槛参数对照，不切换本局难度或授权强化效果。',
                      '特勤分队需另核验相应游戏账户的机械师精英二；不借用计算预览或其他账户培养。',
                      '账户身份、分队实际解锁和实际激活仍未知。此清单不改写本局或伤害计算。']}


def format_squad_plan(plan):
    lines = [f"强化分队条件清单 · {plan['profile_name']} · 等级{plan['grade_reference']}参数对照"]
    for row in plan['rows']:
        state = STATUS_LABELS[row['manual_status']] if row['technology_id'] else '需另核验账户培养'
        gate = row['gate_grade_parameter']
        lines.append(row['name'] + '：' + row['condition'] + '；手动科技记录：' + state +
                     (f"；门槛{gate}，参数{'达到' if row['grade_parameter_met'] else '未达到'}" if gate is not None else ''))
    return '\n'.join([*lines, *plan['notes']])
