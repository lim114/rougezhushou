"""Explicit fixed-stage targets and grades, using the existing environment engine."""
import json
from copy import deepcopy
from .catalog import catalog,stage_previews
from .damage import calculate_damage
from .reporting import has_damage,has_healing


def compare_enemies(scenario, preview):
    if set(preview) != {'stage_id','enemies','grades','orb_mode'}: raise ValueError('需要stage_id、enemies、grades、orb_mode。')
    sid = preview['stage_id']
    if type(sid) is not str or sid not in stage_previews(): raise ValueError('需要有固定敌人档案的关卡。')
    selections = preview['enemies']; grades = preview['grades']; orb_mode = preview['orb_mode']
    if (not isinstance(grades,list) or not 1 <= len(grades) <= 6 or
            any(type(g) is not int or not 0 <= g <= 15 for g in grades) or len(set(grades)) != len(grades)):
        raise ValueError('grades需要1–6个不重复的0–15整数。')
    if type(orb_mode) is not str or orb_mode not in ('unknown','active_same_column','active_other_column'):
        raise ValueError('源阶方情景需要未知、行动同列或行动异列。')
    if not isinstance(selections,list) or not 1 <= len(selections) <= 20: raise ValueError('需选择1–20个关卡敌人。')
    records = []; seen = set()
    for selection in selections:
        if (not isinstance(selection,dict) or set(selection) != {'enemy_id','level'} or
                type(selection['enemy_id']) is not str or type(selection['level']) is not int):
            raise ValueError('每个敌人需要原表enemy_id和整数level。')
        key = (selection['enemy_id'],selection['level'])
        matches = [e for e in stage_previews()[sid]['possible_enemies'] if (e['id'],e['level']) == key]
        if len(matches) != 1 or key in seen: raise ValueError('敌人身份与等级需唯一匹配当前关卡，不能重复。')
        seen.add(key); records.append(matches[0])
    # Reject unusable starting conditions before turning individual cells into errors.
    calculate_damage(deepcopy(scenario))
    rows = []
    for record in records:
        for grade in grades:
            proposed = deepcopy(scenario)
            target = {'stage_id':sid,'enemy_id':record['id'],'level':record['level']}
            if record['id'] == 'enemy_2148_shorbb': target['orb_mode'] = orb_mode
            proposed['target_enemy'] = target
            proposed.setdefault('run_config',{})
            difficulty = deepcopy(proposed['run_config'].get('difficulty') or {})
            difficulty.update(value=grade,source='手动局外难度对照'); difficulty.pop('captured_at',None)
            proposed['run_config']['difficulty'] = difficulty
            row = {'enemy_name':record['name'],'enemy_id':record['id'],'level':record['level'],'grade':grade,
                'status':'待测算','error':None,'max_hp':None,'attack':None,'defense':None,'resistance':None,
                'window_damage':None,'window_healing':None,'window_damage_applicable':has_damage(scenario['operator'],scenario['skill']),
                'window_healing_applicable':has_healing(scenario['operator'],scenario['skill']),
                'enemy':None,'pending':[],'scenario':proposed,'calculation_notes':[]}
            try: modeled = calculate_damage(proposed)
            except ValueError as error:
                row.update(status='不可测算',error=str(error)); rows.append(row); continue
            enemy = modeled['run_resolution']['enemy']; stats = enemy['stats']; metrics = modeled['estimate']['skill']
            row.update(status='已计参考' if modeled['complete'] else '部分参考',max_hp=stats['maxHp'],attack=stats['atk'],
                defense=stats['def'],resistance=stats['magicResistance'],window_damage=metrics.get('window_damage'),
                window_healing=metrics.get('window_healing'),enemy=deepcopy(enemy),
                pending=deepcopy(modeled['run_resolution']['pending']),calculation_notes=deepcopy(modeled['estimate']['notes']))
            rows.append(row)
    return {'scenario':deepcopy(scenario),'preview':deepcopy(preview),'stage_name':catalog()['stages'][sid]['name'],'rows':rows,
        'notes':['目标均为固定关卡的候选引用，不保证出场，不据此推算概率、敌人数量或实际死亡时间。',
                 '每行替换目标与保密等级，其他培养、分队、区域、藏品及时序沿用打开时条件；不改写本局难度或目标。',
                 '面板与输出只包含现有已核验的修正；原生脚本、敌人阶段和动态环境缺口逐行保留。',
                 '源阶方只使用明确选择的统一来源列情景；未知模式不自动补齐减伤，混合来源列仍待核验。',
                 '生命面板不被转换为击杀时间；未知输出保留未知，不用它排序方案。']}


def format_enemy_comparison(result):
    def value(row,key):
        if row.get(key+'_applicable') is False: return '不适用'
        return '未知' if row[key] is None else str(row[key])
    lines = [result['stage_name']+' · 固定敌人与难度对照',
             '打开时条件：'+json.dumps(result['scenario'],ensure_ascii=False,sort_keys=True),
             '用户对照选择：'+json.dumps(result['preview'],ensure_ascii=False)]
    for row in result['rows']:
        lines.append(f"{row['enemy_name']}（引用{row['level']}、等级{row['grade']}、{row['status']}）：生命{value(row,'max_hp')}、攻击{value(row,'attack')}、防御{value(row,'defense')}、法抗{value(row,'resistance')}；窗口伤害{value(row,'window_damage')}、治疗{value(row,'window_healing')}")
        if row['error']: lines.append(row['error'])
        if row['enemy']:
            lines.append('来源与已计修正：'+json.dumps(row['enemy'],ensure_ascii=False,sort_keys=True))
        lines.extend(row['pending']); lines.extend(row['calculation_notes'])
    return '\n'.join([*lines,*result['notes']])
