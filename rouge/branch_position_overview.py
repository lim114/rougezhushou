"""Grouped fixed-source branch positions; no inferred routes or activation."""
from copy import deepcopy
from .branch_reference import branch_reference


def branch_position_overview(stage_id, branch_id=None, phase=None):
    result = branch_reference(stage_id, branch_id, phase)
    groups = {}
    for branch in result['rows']:
        for reference in branch['map_references']:
            cell = reference['cell']
            key = (cell['row'], cell['col'])
            group = groups.setdefault(key, {'cell': deepcopy(cell), 'references': []})
            # References retain distinct identities even when positions coincide.
            group['references'].append(deepcopy(reference))
    rows = []
    for ordinal, key in enumerate(sorted(groups), 1):
        rows.append({'ordinal': ordinal, **groups[key]})
    return {'stage_id': stage_id, 'stage_name': result['stage_name'],
        'level_sha256': result['source']['sha256'], 'branch_id': branch_id, 'phase': phase,
        'rows': rows, 'reference_count': sum(len(r['references']) for r in rows),
        'cell_count': len(rows), 'actual_activation': None, 'actual_spawn_positions': None,
        'all_branch_routes_bound': False,
        'notes': ['P编号对应当前所选分支/阶段的资料格；同格引用分开保留，不等于同时出现或敌人数。',
            '总览保留所有来源预置声明；阶段筛选仅限制阶段动作，不把来源声明变成该阶段产生的位置。',
            '只使用已明确具名的来源及唯一alias激活对象；没有从routeIndex借基础路线，也没有连接点形成分支路线。',
            '逻辑格图可显示全部资料格；固定原图仅显示已有投影支持的地面参考，未支持位置保持未知。']}


def overview_text(result):
    lines = [f"分支资料位置：{result['reference_count']}条独立引用，合并为{result['cell_count']}个资料格。"]
    for row in result['rows']:
        cell = row['cell']
        names = ' / '.join(dict.fromkeys(r['name'] for r in row['references']))
        lines.append(f"P{row['ordinal']} · 第{cell['row']+1}行、第{cell['col']+1}列 · {names} · {len(row['references'])}条引用")
    return '\n'.join([*lines, *result['notes']])
