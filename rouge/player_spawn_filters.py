"""Read-only grouping of original actions; never clocks or actual spawn counts."""
def group_key(action):
    queue=action.get('queue')or{};kind=queue.get('kind')
    names=('wave','fragment')if kind=='main'else('branch_index','phase')if kind=='branch'else()
    if not names or any(type(queue.get(k))is not int for k in names):return None
    return (kind,*(queue[k]for k in names))

def group_label(key):
    return f'第{key[1]}波 · 第{key[2]}组'if key[0]=='main'else f'条件分支{key[1]} · 第{key[2]}段'

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
