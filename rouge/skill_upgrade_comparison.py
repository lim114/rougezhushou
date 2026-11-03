"""Same-scenario rank proposals, gated by existing model and source references."""
import json
from copy import deepcopy
from .catalog import catalog
from .damage import calculate_damage
from .skill_cultivation import explanation, format_explanation
from .reporting import has_damage, has_healing


def compare_skill_upgrades(scenario, preview):
    if set(preview) != {'ranks'}: raise ValueError('需要ranks等级列表。')
    ranks = preview['ranks']
    if (not isinstance(ranks,list) or not 1 <= len(ranks) <= 10 or
            any(type(r) is not int or not 1 <= r <= 10 for r in ranks) or len(set(ranks)) != len(ranks)):
        raise ValueError('ranks需要1–10个不重复的1–10整数等级。')
    baseline = calculate_damage(deepcopy(scenario))
    profile = catalog()['operators'][scenario['operator']]; skill = scenario['skill']; elite = scenario.get('elite',2)
    base_metrics = baseline['estimate']['skill']; rows = []
    for rank in ranks:
        proposed = deepcopy(scenario); proposed['skill_rank'] = rank
        source = explanation(scenario['operator'],profile,skill,elite,
            {'rank':rank,'source':'preview_unconfirmed','manual_reference_applied':False})
        parameter = profile['skills'][skill-1]['levels'][rank-1]
        row = {'rank':rank,'label':f'等级{rank}' if rank<=7 else f'专精{rank-7}',
            'status':'待测算','error':None,'original_training_reference':deepcopy(source),
            'duration_parameter':parameter['duration'] if parameter['duration'] >= 0 else None,
            'raw_duration_parameter':parameter['duration'],'sp_cost_parameter':parameter['sp_cost'],
            'window_damage':None,'window_healing':None,'delta_window_damage':None,'delta_window_healing':None,
            'known_window_damage':None,'known_window_healing':None,'cycle_damage':None,'cycle_healing':None,
            'warnings':[],'calculation_notes':[]}
        for field in ('window_damage','delta_window_damage'):
            row[field+'_applicable'] = has_damage(scenario['operator'],skill)
        for field in ('window_healing','delta_window_healing'):
            row[field+'_applicable'] = has_healing(scenario['operator'],skill)
        try: modeled = calculate_damage(proposed)
        except ValueError as error:
            row.update(status='不可测算',error=str(error)); rows.append(row); continue
        metrics = modeled['estimate']['skill']; row['status'] = '已计参考' if modeled['complete'] else '部分参考'
        for key in ('window_damage','window_healing','cycle_damage','cycle_healing'): row[key] = metrics.get(key)
        for key in ('window_damage','window_healing'):
            value = metrics.get(key); original = base_metrics.get(key)
            row['delta_'+key] = value-original if value is not None and original is not None else None
        row['known_window_damage'] = modeled.get('known_damage_subtotals',{}).get('window_damage')
        row['known_window_healing'] = modeled.get('known_healing_subtotals',{}).get('window_healing')
        row['warnings'] = deepcopy(modeled['warnings']); row['calculation_notes'] = deepcopy(modeled['estimate']['notes'])
        rows.append(row)
    return {'scenario':deepcopy(scenario),'baseline_rank':scenario.get('skill_rank',10),'rows':rows,
        'baseline_metrics':deepcopy(base_metrics),
        'notes':['每行仅替换技能等级，培养、模组、目标、藏品及观察条件使用打开时的同一情景。',
                 '原训练条件只作升级门参考，不确认账户已培养或肉鸽受限形态的使用资格；不可测算的等级明确保留原因。',
                 '差值以打开时等级为基准；未知整体输出不当零，已计小计与完整输出分开。',
                 '持续时间和技力消耗列是技能表参数，不自动确认实际结束、充能消费或原生回转。',
                 '结果仅供局外升级比较，不改写账号、本局技能或原计算。']}


def format_skill_upgrades(result):
    def value(row,key):
        if row.get(key+'_applicable') is False: return '不适用'
        return '未知' if row[key] is None else str(row[key])
    lines = [f"技能等级对照 · 基准等级{result['baseline_rank']}",
             '同一计算条件：'+json.dumps(result['scenario'],ensure_ascii=False,sort_keys=True)]
    for row in result['rows']:
        lines.append(f"{row['label']}（{row['status']}）：窗口伤害{value(row,'window_damage')}，治疗{value(row,'window_healing')}；伤害差值{value(row,'delta_window_damage')}，治疗差值{value(row,'delta_window_healing')}；持续参数{row['duration_parameter']}，技力参数{row['sp_cost_parameter']}")
        if row['error']: lines.append(row['error'])
        lines.append(format_explanation(row['original_training_reference']))
        lines.extend(row['warnings']); lines.extend(row['calculation_notes'])
    return '\n'.join([*lines,*result['notes']])
