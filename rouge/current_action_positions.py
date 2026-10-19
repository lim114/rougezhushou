"""Explicit current action cells; no runtime branch route selection or path guess."""
from copy import deepcopy
from . import current_battle_reference as battle, current_map_position as positions
from .battle_preview import display_cell

SPATIAL = {'MOVE': '移动目标格', 'APPEAR_AT_POS': '再出现的目标格'}
WAIT = {'WAIT_FOR_SECONDS': '到达后等待', 'WAIT_CURRENT_FRAGMENT_TIME': '等待本组计时'}
UNAVAILABLE = '当前条目与地图位置无法核对，旧内容已清除；恢复后请重新选择。'


def reference(stage_id, action_key):
    current = battle.stage_reference(stage_id)
    grid = positions.stage_reference(stage_id)
    if current is None or grid is None or type(action_key) is not str:
        return None
    return _reference(current, grid, action_key)


def _reference(current, grid, action_key):
    stage_id = current['id']
    action = next((a for a in current['actions'] if a['key'] == action_key), None)
    if action is None:
        return None
    level = current['level']; raw = action['raw']; entries = []; notes = []

    def add(label, position, selector, *, offset=None, random_range=None):
        # Source positions use bottom-up rows; mapData/landmark rows are top-down.
        cell = display_cell(position, grid['rows'], grid['cols'])
        point = positions.cell_reference(grid, **cell) if cell else None
        entries.append({'key': str(len(entries)), 'label': label, 'source_selector': selector,
                        'raw_position': deepcopy(position), 'cell': cell,
                        'center': deepcopy(point['point']) if point else None,
                        'offset': deepcopy(offset), 'random_range': deepcopy(random_range),
                        'actual_position': None, 'actual_time': None})

    kind = raw.get('actionType')
    if kind == 'SPAWN' and action['queue']['kind'] == 'main':
        index = raw.get('routeIndex'); routes = level['routes']
        if type(index) is not int or not 0 <= index < len(routes):
            notes.append('本条基础路线缺失或编号越界，没有选择其它路线代替。')
        else:
            route = routes[index]; prefix = f'$.routes[{index}]'
            if route.get('motionMode') not in ('WALK', 'FLY'):
                notes.append('本条路线的移动方式未定义，占位格不能当作出生位置。')
            else:
                add('出生参考格', route.get('startPosition'), prefix + '.startPosition',
                    offset=route.get('spawnOffset'), random_range=route.get('spawnRandomRange'))
                for i, checkpoint in enumerate(route.get('checkpoints') or []):
                    typ = checkpoint.get('type'); source = prefix + f'.checkpoints[{i}]'
                    if typ in SPATIAL:
                        add(f'第{i + 1}处：' + SPATIAL[typ], checkpoint.get('position'), source + '.position',
                            offset=checkpoint.get('reachOffset'))
                    elif typ in WAIT:
                        notes.append(f'第{i + 1}处：{WAIT[typ]}，配置值{battle.number(checkpoint.get("time"))}秒；不是开场后的准确时刻，等待占位格不标到地图。')
                    elif typ == 'DISAPPEAR':
                        notes.append(f'第{i + 1}处：消失；不从此记录的位置字段猜格子，也不连接到再出现位置。')
                    else:
                        notes.append(f'第{i + 1}处：记录类型尚未核实，位置与耗时保留未知。')
                add('终点参考格', route.get('endPosition'), prefix + '.endPosition')
    elif kind == 'ACTIVATE_PREDEFINED':
        matches = action['predefined_candidates'] if raw.get('key') else []
        if len(matches) == 1:
            match = matches[0]
            add('预置装置或单位的声明格', match['raw'].get('position'), match['source_selector'] + '.position')
            notes.append('这只是唯一别名对应的预置声明；没有确认实际激活、打开、击破或领取。')
        elif len(matches) > 1:
            notes.append('同一别名有多份预置声明，实际选择尚未确认，不任选其中一个位置。')
        else:
            notes.append('没有找到唯一的具名预置声明；激活动作的路线编号不能代替装置位置。')
    elif kind == 'SPAWN':
        notes.append('这是条件分支。基础路线与额外路线的实际选择尚未确认，没有按相同编号借用位置。')
    else:
        notes.append('此条不是已支持的出怪或具名装置激活记录，没有从它的路线编号推断位置。')
    return {'stage_id': stage_id, 'action_key': action_key, 'action': deepcopy(action),
            'label': battle.action_label(action), 'entries': entries, 'notes': notes,
            'grid': grid, 'battle_source_identity': current['source_identity'],
            'source_identity': (current['source_identity'], grid['source_identity']),
            'actual_occurrence': None, 'absolute_time': None, 'actual_path': None,
            'run_updated': False}


def entry_label(entry):
    cell = entry['cell']
    return entry['label'] + (f' · 第{cell["row"] + 1}行第{cell["col"] + 1}列' if cell else ' · 地图内位置未知')


def player_text(result, entry=None):
    lines = [result['label'], '', '【位置参考】',
             '从列表选择一处，左侧标出对应格子；右侧只有已经核对过的近似中心才画标记。',
             '出生和移动位置是关卡资料中的名义格，不是实际脚点；偏移、随机范围和敌人寻路没有推算。']
    if entry:
        lines += [entry_label(entry), '原图近似中心：' + ('有已核对参考。' if entry['center'] else '尚未核对，不猜位置。')]
        if any(type(v) in (int, float) and v != 0 for d in (entry['offset'], entry['random_range']) if isinstance(d, dict) for v in d.values()):
            lines += ['本条包含位置偏移参数；这里仍只标名义格中心，不表示偏移后的出生或到达点。']
    if not result['entries']:
        lines += ['本条尚无能够绑定的位置。']
    lines += ['', '【条件和等待】', *result['notes'],
              '随机候选、隐藏组和条件分支均不等于一定出现；这里不计算生成概率或全局出怪时刻。',
              '只逐个查看明确引用的格子，不连成敌人实际路线，不读取或操作战斗。']
    return '\n'.join(lines)
