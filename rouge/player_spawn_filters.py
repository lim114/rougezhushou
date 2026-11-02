"""Read-only grouping of original actions; never clocks or actual spawn counts."""
def group_key(action):
    queue=action.get('queue')or{};kind=queue.get('kind')
    names=('wave','fragment')if kind=='main'else('branch_index','phase')if kind=='branch'else()
    if not names or any(type(queue.get(k))is not int for k in names):return None
    return (kind,*(queue[k]for k in names))

def group_label(key):
    return f'第{key[1]}波 · 第{key[2]}组'if key[0]=='main'else f'条件分支{key[1]} · 第{key[2]}段'


def record_text(action,object_names):
    """Original per-record settings, with their occurrence conditions visible."""
    from .current_battle_reference import number,action_label
    title=action_label(action);predefined=action['predefined_candidates']
    if not action['enemy_candidates']and len(predefined)==1:
        name=object_names.get(predefined[0]['source_selector'])
        if name:title=title.rsplit(' · ',1)[0]+' · '+name
    raw=action['raw'];parts=[]
    if raw.get('actionType')in('SPAWN','ACTIVATE_PREDEFINED'):
        parts.extend(('配置数量：'+number(raw.get('count')), '间隔：'+number(raw.get('interval'))+'秒'))
    parts.append('本条等待：'+number(raw.get('preDelay'))+'秒')
    if action['queue']['kind']=='branch':parts.append('条件分支')
    if raw.get('hiddenGroup'):parts.append('隐藏候选')
    if raw.get('randomSpawnGroupKey')or raw.get('randomSpawnGroupPackKey'):parts.append('随机候选')
    if raw.get('blockFragment'):parts.append('需等待本组条件')
    return title+'\n'+' · '.join(parts)

def action_rows(actions,kind=None,group=None,focus=None,enemy_key=None):
    rows=[]
    if focus not in(None,'enemy','hidden','random','predefined'):return rows
    for action in actions:
        if kind is not None and(action.get('queue')or{}).get('kind')!=kind:continue
        if group is not None and group_key(action)!=group:continue
        raw=action.get('raw')or{}
        if focus=='enemy'and(enemy_key is None or not any(e.get('key')==enemy_key for e in action.get('enemy_candidates',[]))):continue
        if focus=='hidden'and not raw.get('hiddenGroup'):continue
        if focus=='random'and not(raw.get('randomSpawnGroupKey')or raw.get('randomSpawnGroupPackKey')):continue
        if focus=='predefined'and raw.get('actionType')!='ACTIVATE_PREDEFINED':continue
        rows.append(action)
    return rows
