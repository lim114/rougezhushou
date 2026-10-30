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
    for key, name in (('life', '目标生命'), ('shield', '护盾'),
                      ('command', '指挥等级'), ('hope', '希望')):
        rows.append({'key': key, 'name': name, 'value': '未读',
            'note': '当前自动读取尚未覆盖此项，不从分队、保密等级或旧层记录推算。'})
    gold = resources.get('gold') or {}
    amount = gold.get('value')
    rows.append({'key': 'gold', 'name': '源石锭',
        'value': f'{amount:g}' if numeric_read(amount) else '未读',
        'note': '本局最近读到的数量。' + observation_time(gold.get('captured_at'))
                + '；不是所选历史层当时数量，也不代表结算收益。'})
    for key, name in (('action', '行动力'), ('valuation', '总估价')):
        rows.append({'key': key, 'name': name, 'value': '未读',
            'note': '当前自动读取尚未覆盖此项，不根据地图步数、藏品或旧记录推算。'})
    return rows
