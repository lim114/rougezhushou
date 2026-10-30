"""Compare like archived read contexts, keeping unread difficulty/squad separate."""
from .run_config import config_data, confirmed_config
from .player_personal_statistics import unique_archives

UNREAD = '__unread__'

def cohort(record):
    state = record.get('state', {})
    observed = confirmed_config({'run_id': state.get('id'), 'config': state.get('config', {})})
    difficulty = observed.get('difficulty', {}).get('value', UNREAD)
    squad = observed.get('squad', {}).get('id')
    data = config_data()['squads']
    known = data.get(squad, {})
    family = known.get('normalBandId', UNREAD)
    base = data.get(family, {})
    return {'difficulty': difficulty, 'squad': family,
            'squad_name': base.get('name') or '分队未读到'}

def cohort_options(records):
    grades, squads = {}, {}
    for record in unique_archives(records):
        group = cohort(record)
        value = group['difficulty']
        grades[value] = '保密等级未读到' if value == UNREAD else f'保密等级{value}'
        squads[group['squad']] = group['squad_name']
    return {'difficulty': list(grades.items()), 'squad': list(squads.items())}

def select_cohort(records, *, difficulty=None, squad=None):
    if difficulty is not None and type(difficulty) is not int and difficulty != UNREAD:
        return []
    if squad is not None and not isinstance(squad, str):
        return []
    result = []
    for record in unique_archives(records):
        group = cohort(record)
        if difficulty is not None and group['difficulty'] != difficulty:
            continue
        if squad is not None and group['squad'] != squad:
            continue
        result.append(record)
    return result

def cohort_note(difficulty, squad):
    return ('筛选的是归档中已读保密等级与分队类型；未读项目单独保留。'
            '同一分队的基础、强化阶段合并为一种类型，不表示效果完全相同。'
            '筛选不改变原记录、样本缺失处理或收藏品完整性分母。'
            '这不是不同分队的强度结论；版本、个人选择和读取缺失仍可能影响样本。')
