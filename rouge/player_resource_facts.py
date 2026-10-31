"""Player-facing counts: read quantities, qualified members and missing data differ."""
from .record_flags import active_record, unconfirmed_item_ids
from .player_resource_history import numeric_read
from .player_replay import observation_time


def count(value):
    return value if type(value) is int and numeric_read(value) else None


def inventory_summary(state):
    relics = sum(active_record(r, 'held') for r in state.get('relics', {}).values())
    tools = sum(active_record(r, 'held') for r in state.get('tactical_tools', {}).values())
    total = count(state.get('relic_count'))
    unknown = unconfirmed_item_ids(state)
    complete = (state.get('inventory_verified') is True and total is not None
                and relics + tools == total and not unknown)
    # The game badge includes tools. Subtract them only after a full match.
    expected_relics = total - tools if complete else total if tools == 0 and not unknown else None
    return {'relics': relics, 'tools': tools, 'total': total,
            'complete': complete, 'expected_relics': expected_relics}


def resource_rows(state):
    inventory = inventory_summary(state)
    known = inventory['relics'] + inventory['tools']
    total = inventory['total']
    visible = (str(total) if inventory['complete'] else '待核对' if total is not None and known > total
               else f'{known}/{total}' if total is not None
               else f'已读{known}' if known else '未读')
    status = '已核对完整' if inventory['complete'] else '清单尚未核对完整'
    rows = [{'key': 'items', 'name': '藏品/道具', 'value': visible,
        'note': f"已确认收藏品{inventory['relics']}件、战术道具{inventory['tools']}件；"
                + (f'游戏底部合计最近读到{total}件。' if total is not None else '游戏底部合计未读。')
                + status + '。点击查看收藏品。'}]
    resources = state.get('resources', {})
    parts = resources.get('parts_count') or {}
    amount = parts.get('value')
    capacity = count(parts.get('capacity'))
    value = f'{amount:g}' if numeric_read(amount) else '未读'
    if numeric_read(amount) and capacity is not None and capacity >= amount:
        value += '/' + str(capacity)
    rows.append({'key': 'parts', 'name': '零件箱', 'value': value,
        'note': '本局最近已读零件数量；容量只在已读且不小于数量时显示。'
                '具体成员和剩余次数未完整读取；点击查看零件资料。'})
    crew = sum(active_record(r, 'present') for r in state.get('operators', {}).values())
    crew_total = count(state.get('crew_count'))
    crew_value = ('待核对' if crew_total is not None and crew > crew_total
                  else str(crew_total) if crew == crew_total else f'{crew}/{crew_total}'
                  if crew_total is not None else f'已读{crew}' if crew else '未读')
    rows.append({'key': 'crew', 'name': '干员', 'value': crew_value,
        'note': f'已确认在队{crew}名；' + (f'已读队伍总数{crew_total}名。' if crew_total is not None else '队伍总数未读。')
                + '不是可携带或可部署人数；点击查看本局队伍。'})
    from .relic_counter_semantics import RESOURCE_LABELS
    for key in ('life', 'shield', 'command', 'hope', 'gold', 'action', 'valuation'):
        record = resources.get(key) or {}
        amount = record.get('value')
        value = f'{amount:g}' if numeric_read(amount) else '未读'
        capacity = count(record.get('capacity'))
        if key in ('life', 'hope') and numeric_read(amount) and capacity is not None and capacity >= amount:
            value += '/' + str(capacity)
        rows.append({'key': key, 'name': RESOURCE_LABELS[key], 'value': value,
            'note': '本局最近读到的数值。' + observation_time(record.get('captured_at'))
                    + '；未读不代表零，不使用分队或藏品推算，也不是所选历史层当时数值。'})
    return rows
