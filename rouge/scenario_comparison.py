"""Recalculate saved proposals with current data, retaining unknown scope."""
import json
from copy import deepcopy
from .catalog import catalog
from .damage import calculate_damage
from .reporting import has_damage,has_healing
from .scenario_library import model_signature


def scenario_differences(before,after,path=''):
    changes = []
    if isinstance(before,dict) and isinstance(after,dict):
        for key in sorted(set(before)|set(after)):
            pointer = path+'/'+key.replace('~','~0').replace('/','~1')
            if key not in before: changes.append({'path':pointer,'kind':'added','after':deepcopy(after[key])})
            elif key not in after: changes.append({'path':pointer,'kind':'removed','before':deepcopy(before[key])})
            else: changes.extend(scenario_differences(before[key],after[key],pointer))
    elif type(before) is not type(after) or before != after:
        changes.append({'path':path or '/','kind':'changed','before':deepcopy(before),'after':deepcopy(after)})
    return changes


def compare_saved_scenarios(baseline,records):
    if not isinstance(records,list) or len(records)>6: raise ValueError('每次最多比较6个已保存情景。')
    current_signature = model_signature(); rows = []; base_window = None; baseline_metrics = None
    proposals = [{'name':'当前编辑条件（基准）','scenario':deepcopy(baseline),'model_signature':current_signature},*deepcopy(records)]
    for index,proposal in enumerate(proposals):
        if not isinstance(proposal,dict) or type(proposal.get('name')) is not str or not isinstance(proposal.get('scenario'),dict):
            raise ValueError('比较项需要名称与情景。')
        scenario = proposal['scenario']
        row = {'name':proposal['name'],'operator_name':'未知','skill':scenario.get('skill'),'status':'待测算',
               'window_seconds':None,'window_damage':None,'window_healing':None,'delta_window_damage':None,'delta_window_healing':None,
               'scenario':deepcopy(scenario),'differences':scenario_differences(baseline,scenario),'error':None,
               'saved_model_matches_current':proposal.get('model_signature')==current_signature,
               'saved_at':proposal.get('saved_at'),'warnings':[],'calculation_notes':[]}
        try: modeled = calculate_damage(deepcopy(scenario))
        except (ValueError,KeyError,TypeError) as error:
            if index==0: raise ValueError('基准情景不可测算：'+str(error)) from None
            row.update(status='当前不可测算',error=str(error)); rows.append(row); continue
        metrics = modeled['estimate']['skill']; window = metrics.get('window_seconds')
        row.update(operator_name=catalog()['operators'][scenario['operator']]['name'],
            status='已计参考' if modeled['complete'] else '部分参考',window_seconds=window,
            window_damage=metrics.get('window_damage'),window_healing=metrics.get('window_healing'),
            warnings=deepcopy(modeled['warnings']),calculation_notes=deepcopy(modeled['estimate']['notes']))
        if index==0: base_window = window; baseline_metrics = metrics
        for key in ('window_damage','window_healing'):
            applicable = has_damage(scenario['operator'],scenario['skill']) if key=='window_damage' else has_healing(scenario['operator'],scenario['skill'])
            row[key+'_applicable'] = applicable; row['delta_'+key+'_applicable'] = applicable
            original = baseline_metrics.get(key); value = metrics.get(key)
            if window is not None and window==base_window and original is not None and value is not None:
                row['delta_'+key] = value-original
        row['same_window_as_baseline'] = window is not None and window==base_window
        training_notice = scenario.get('unconfirmed_training')
        if isinstance(training_notice,list) and all(type(v) is str for v in training_notice) and training_notice:
            row['warnings'].append('培养条件未确认：'+'、'.join(training_notice))
        rows.append(row)
    return {'baseline':deepcopy(baseline),'rows':rows,'current_model_signature':current_signature,
        'notes':['保存的是局外条件；每次对照使用当前代码与资料重新计算，不复用历史结果。',
                 '保存条件中的读取与本局来源只代表原条件快照，不代表当前游戏或当前本局的新观察。',
                 '保存时计算资料变化会提示；这不确认当前游戏热更新、账户状态或实际机制。',
                 '仅在相同的已知观察窗口且双方输出为数值时显示差值；窗口不同或未知输出保留未知。',
                 '条件差异逐项列出，不自动认定单一变化造成全部收益，不据未知输出排序。',
                 '载入只进入局外编辑器；不会覆盖主计算条件、账号、本局记录或当前游戏。']}


def format_scenario_comparison(result):
    def value(row,key):
        if row.get(key+'_applicable') is False:return '不适用'
        return '未知' if row[key] is None else str(row[key])
    lines = ['局外情景库 · 当前资料重新对照']
    for row in result['rows']:
        lines.append(f"{row['name']}：{row['operator_name']} S{row['skill']}，{row['status']}；窗口{value(row,'window_seconds')}秒；伤害{value(row,'window_damage')}、治疗{value(row,'window_healing')}；伤害差值{value(row,'delta_window_damage')}、治疗差值{value(row,'delta_window_healing')}")
        lines.append('保存时计算资料：'+('与当前一致' if row['saved_model_matches_current'] else '不同或未记录，以上为当前重新测算'))
        lines.append('局外条件：'+json.dumps(row['scenario'],ensure_ascii=False,sort_keys=True))
        lines.append('相对基准的字段差异：'+json.dumps(row['differences'],ensure_ascii=False))
        if row['error']:lines.append(row['error'])
        lines.extend(row['warnings']);lines.extend(row['calculation_notes'])
    return '\n'.join([*lines,*result['notes']])
