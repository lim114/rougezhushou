"""Current fixed queue membership, never RNG decisions or actual occurrences."""
from collections import defaultdict
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

from . import current_battle_reference as battle

ROOT = Path(__file__).resolve().parents[1]
PACK = 'research/p3-current-spawn-candidates-355'
MANIFEST = PACK + '/runtime-manifest.json'
MANIFEST_SHA256 = 'f79e2541cb510934db8a3087ed58f34871e3c9c4276af5fd7d0ebb04517fff78'
KINDS = {'group': '候选组', 'package': '关联条目'}
FIELDS = {'group': 'randomSpawnGroupKey', 'package': 'randomSpawnGroupPackKey'}
NOTICE = ('这里只阅读固定关卡资料中的候选和关联条目；同组、同一关联标记不证明实际采用、'
          '同时出场、互斥次数或出现概率。空白记录与未指定目标的装置记录分开保留。')
UNAVAILABLE = '出怪候选资料无法核对；旧选择、成员、图片与跳转已清除，资料恢复后请手动重新选择。'


def _same(left, right):
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return left.keys() == right.keys() and all(_same(left[k], right[k]) for k in left)
    if type(left) is list:
        return len(left) == len(right) and all(_same(a, b) for a, b in zip(left, right))
    return left == right


def _packet():
    try:
        manifest_raw = battle.version._file(MANIFEST).read_bytes()
        if sha256(manifest_raw).hexdigest() != MANIFEST_SHA256:
            return None
        manifest = json.loads(manifest_raw)
        expected = {PACK + '/scope-inventory.json', PACK + '/source-notes.json',
                    'research/p3-current-rewards-315/selected-originals.json',
                    'research/p3-current-rewards-315/source-selection.json'}
        if (manifest['schema'] != 'current_spawn_candidates_355_manifest_v1'
                or manifest['game_commit'] != battle.version.NEW_COMMIT
                or set(manifest['files']) != expected):
            return None
        objects = {}
        for name, pin in manifest['files'].items():
            raw = battle.version._file(name).read_bytes()
            if type(pin['bytes']) is not int or len(raw) != pin['bytes'] or sha256(raw).hexdigest() != pin['sha256']:
                return None
            objects[name] = json.loads(raw)
        inventory = objects[PACK + '/scope-inventory.json']
        notes = objects[PACK + '/source-notes.json']
        characters = objects['research/p3-current-rewards-315/selected-originals.json']['characters']
        character_source = objects['research/p3-current-rewards-315/source-selection.json']
        if (inventory['schema'] != 'current_spawn_candidates_355_scope_v1'
                or inventory['game_commit'] != battle.version.NEW_COMMIT
                or character_source['commit'] != battle.version.NEW_COMMIT
                or notes['game_commit'] != battle.version.NEW_COMMIT):
            return None
        return {'inventory': inventory, 'notes': notes, 'characters': characters,
                'character_source': character_source, 'source_identity': MANIFEST_SHA256}
    except (OSError, ValueError, TypeError, KeyError, AttributeError, UnicodeError, RecursionError):
        return None


def _queue_name(queue):
    if queue['kind'] == 'main':
        return f"第{queue['wave']}波 · 第{queue['fragment']}组"
    return f"条件分支{queue['branch_index']} · 第{queue['phase']}段"


def _relation_key(stage_id, queue_selector, kind, raw_key):
    # Full structural identity, not an array position or a name heuristic.
    return json.dumps([stage_id, queue_selector, kind, raw_key], ensure_ascii=False, separators=(',', ':'))


def _member(action, characters):
    raw = action['raw']; typ = raw.get('actionType')
    refs = deepcopy(action['enemy_candidates'])
    predefined = deepcopy(action['predefined_candidates'])
    if typ == 'EMPTY':
        name, label = '空白候选记录', '空白记录'
    elif typ == 'ACTIVATE_PREDEFINED':
        label = '预置物件启用记录'
        if not raw.get('key'):
            name = '未指定启用目标'
        else:
            names = []
            for item in predefined:
                entity = (item['raw'].get('inst') or {}).get('characterKey')
                value = characters.get(entity, {}).get('name')
                if type(value) is str and value:
                    names.append(battle.plain(value))
            name = ' / '.join(dict.fromkeys(names)) if names else '预置物件（中文名称未取得）'
    elif typ == 'SPAWN':
        name = ' / '.join(dict.fromkeys(row['name'] for row in refs)) or '敌人名称未取得'
        label = '出怪记录'
    else:
        name = {'PREVIEW_CURSOR': '路线提示', 'PLAY_OPERA': '剧情演出',
                'DISPLAY_ENEMY_INFO': '敌人介绍提示'}.get(typ, '类型尚未核实的记录')
        label = '其它记录'
    return {'action_key': action['key'], 'source_selector': action['source_selector'],
            'name': name, 'type_label': label, 'action_type': typ,
            'declared_count': deepcopy(raw.get('count')), 'action': deepcopy(action),
            'enemy_candidates': refs, 'predefined_candidates': predefined,
            'can_open_action': True,
            'can_request_position': typ in ('SPAWN', 'ACTIVATE_PREDEFINED'),
            'actual_selection': None, 'actual_count': None, 'actual_time': None,
            'position_on_original': None}


def _build(current, characters):
    relations = {'group': [], 'package': []}
    by_selector = {a['source_selector']: a for a in current['actions']}
    if len(by_selector) != len(current['actions']):
        raise ValueError('Duplicate action selectors')
    scopes = []; consumed = set()
    for raw_queue in battle.queues(current['level']):
        queue = {k: deepcopy(v) for k, v in raw_queue.items() if k != 'actions'}
        scope = {'key': queue['source_selector'], 'name': _queue_name(queue),
                 'kind': queue['kind'], 'queue': queue}
        scopes.append(scope)
        for kind, field in FIELDS.items():
            grouped = defaultdict(list)
            for index, raw in enumerate(raw_queue['actions']):
                selector = queue['source_selector'] + f'.actions[{index}]'
                action = by_selector.get(selector)
                if action is None or not _same(action['raw'], raw) or not _same(action['queue'], queue):
                    raise ValueError('Current action does not match original queue')
                consumed.add(selector)
                key = raw.get(field)
                if type(key) is str and key:
                    grouped[key].append(action)
                elif key not in (None, ''):
                    raise ValueError('Unexpected relation-key type')
            for ordinal, (key, members) in enumerate(grouped.items(), 1):
                relations[kind].append({
                    'key': _relation_key(current['id'], queue['source_selector'], kind, key),
                    'kind': kind, 'scope_key': scope['key'], 'queue': deepcopy(queue),
                    'name': scope['name'] + ' · ' + KINDS[kind] + str(ordinal),
                    'raw_relation_key': key, 'original_field': field,
                    'members': [_member(a, characters) for a in members],
                    'actual_selection': None, 'probability': None})
    if consumed != set(by_selector):
        raise ValueError('Action projection does not cover the exact original queues')
    return relations, scopes


def stage_reference(stage_id, origin_action_key=None):
    """All exact memberships, optionally only relations containing one action."""
    if type(stage_id) is not str or (origin_action_key is not None and type(origin_action_key) is not str):
        return None
    packet = _packet()
    if packet is None:
        return None
    selected = packet['inventory']['stages'].get(stage_id)
    if selected is None:
        return None
    current = battle.stage_reference(stage_id)
    if current is None:
        return None
    try:
        if (not _same(current['stage'], selected['complete_stage'])
                or current['level_key'] != selected['level_key']
                or not _same(current['source'], selected['original_level_source'])
                or sha256(json.dumps(current['level'], ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':'), allow_nan=False).encode('utf8')).hexdigest()
                   != selected['parsed_level_sha256']):
            return None
        relations, scopes = _build(current, packet['characters'])
        scope_rows = []
        for kind in ('group', 'package'):
            for row in relations[kind]:
                scope_rows.append({'kind': kind, 'queue_selector': row['scope_key'],
                    'raw_relation_key': row['raw_relation_key'],
                    'members': [m['source_selector'] for m in row['members']]})
        if not _same(scope_rows, selected['relations']):
            return None
        origin = next((a for a in current['actions'] if a['key'] == origin_action_key), None)
        if origin_action_key is not None and origin is None:
            return None
        if origin is not None:
            relations = {kind: [row for row in rows if any(
                m['action_key'] == origin_action_key for m in row['members'])]
                for kind, rows in relations.items()}
        return {'stage_id': stage_id, 'stage_name': current['name'],
                'origin_action_key': origin_action_key, 'origin_action': deepcopy(origin),
                'groups': relations['group'], 'packages': relations['package'],
                'scopes': scopes, 'source_identity': (MANIFEST_SHA256, current['source_identity'],
                                                     current['source']['sha256']),
                'battle_source_identity': current['source_identity'],
                'source': deepcopy(current['source']), 'level_key': current['level_key'],
                'actual_selection': None, 'actual_count': None, 'absolute_time': None,
                'actual_path': None, 'probabilities': None, 'run_updated': False}
    except (ValueError, TypeError, KeyError, AttributeError, IndexError, RecursionError):
        return None


def resolve_member(result, relation_key, action_key):
    """Freshly resolve a manual choice; stale/mutated snapshots never authorize a jump."""
    if type(result) is not dict or type(relation_key) is not str or type(action_key) is not str:
        return None
    fresh = stage_reference(result.get('stage_id'), result.get('origin_action_key'))
    if fresh is None or not _same(fresh, result):
        return None
    row = next((r for r in fresh['groups'] + fresh['packages'] if r['key'] == relation_key), None)
    member = next((m for m in row['members'] if m['action_key'] == action_key), None) if row else None
    if member is None:
        return None
    return {'reference': fresh, 'relation': deepcopy(row), 'member': deepcopy(member)}


def position_reference(result, relation_key, action_key):
    selected = resolve_member(result, relation_key, action_key)
    if selected is None or not selected['member']['can_request_position']:
        return None
    from . import current_action_positions
    position = current_action_positions.reference(result['stage_id'], action_key)
    if (position is None or position['stage_id'] != result['stage_id']
            or position['action_key'] != action_key
            or position['battle_source_identity'] != result['battle_source_identity']
            or not _same(position['action'], selected['member']['action'])):
        return None
    return position


def player_text(result, relation=None, member=None):
    lines = [result['stage_name'], NOTICE, '', '【查阅范围】',
             ('本条记录相关的候选与关联条目。' if result['origin_action_key'] is not None
              else '本关完整固定资料目录；主波次与条件分支分开，不拼接同名标记。')]
    if relation is None:
        lines += [f"本关当前范围列有{len(result['groups'])}份候选组、{len(result['packages'])}份关联条目资料。",
                  '请手动选择一份关系资料，再选择成员；资料条数不是实际敌人数。']
        return '\n'.join(lines)
    lines += ['', '【' + KINDS[relation['kind']] + '】', relation['name'],
              f"这份资料列有{len(relation['members'])}条记录，包含空白与未具名项；不能累加为实际敌人数。"]
    if relation['kind'] == 'package':
        lines.append('关联条目指原件采用同一关联标记；尚未证明必定共同出现、互斥关系或实际采用次数。')
    if relation['queue']['kind'] == 'branch':
        lines.append('这是条件分支中的记录；分支是否触发、采用哪次记录以及发生时刻仍未知。')
    if member is None:
        return '\n'.join(lines + ['', '请手动选择一条成员记录。'])
    lines += ['', '【所选成员】', member['type_label'] + '：' + member['name']]
    count = member['declared_count']
    lines.append('本条配置数量：' + (str(count) if type(count) is int and count >= 0 else '未知')
                 + '；这是单条配置，不能当作实际生成数量。')
    if member['action_type'] == 'EMPTY':
        lines.append('空白记录没有指定要生成的敌人或启用的物件；不表示本局没有敌人。')
    elif member['action_type'] == 'ACTIVATE_PREDEFINED':
        matches = member['predefined_candidates']
        if not member['action']['raw'].get('key'):
            lines.append('本条未指定启用目标，与空白记录不同；不任意选择一个物件代替。')
        elif len(matches) == 1:
            lines.append('本关找到唯一预置别名声明；可查看已有位置参考，不表示已经启用、击破或领取。')
        elif len(matches) > 1:
            lines.append('这个别名对应多份预置声明；实际目标与位置未知，不任选其中一个。')
        else:
            lines.append('尚未找到准确预置声明；不借用出怪路线的编号代替装置位置。')
    elif member['action_type'] == 'SPAWN':
        n = len(member['enemy_candidates'])
        if n == 0:
            lines.append('本条尚未与本关敌人引用对应，不借同名敌人的面板或图片。')
        elif n > 1:
            lines.append('同一原标识对应多份敌人引用；不能任选一个等级当作本次出现配置。')
    if member['can_request_position']:
        lines += ['', '【怎样查看位置】',
                  '下方可打开本条已有地图参考。只有明确的名义格及已经核对的原图标志或中心才会显示；分支路线或位置缺失时保留未知。',
                  '不补坐标、不反推真实脚点、不连成实际路径；本页未给出开场后的准确出怪时间。']
    else:
        lines += ['', '本条不提供地图位置入口。']
    action_conditions = battle.action_text(member['action']).partition('\n\n【位置与入口】')[0]
    lines += ['', '【出现条件】', action_conditions,
              '', '【仍未确认】', '本局实际选择、触发与次数、当前服务器资格、完整绝对时钟和实际路径均未知；不改本局记录。']
    return '\n'.join(lines)
