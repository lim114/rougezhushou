"""Current documented event catalogue, separate from live node eligibility."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path, PurePosixPath
import importlib, json, re

ROOT = Path(__file__).resolve().parents[1]
PACK = 'research/p3-current-event-directory-372'
DATA = 'rouge/data/current-event-directory.json'
NOTES = PACK + '/source-notes.json'
MANIFEST = PACK + '/runtime-manifest.json'
MANIFEST_SHA256 = '1700a08414f07e55ea560a3e8a404dbb308cb44a07be2fd49893c26207834de1'
UNAVAILABLE = '事件目录的来源暂时无法核对，旧目录、阅读内容和所属窗口已清除；恢复后请重新选择。'
NOTICE = ('按已经核对的当前固定资料查找事件。这里的分类只帮助查资料，'
          '不是本局可能出现的完整清单，也不判断现在能否选择。')
TOPICS = (('gold', '提到源石锭代价'), ('life', '提到生命代价'), ('held', '提到持有物品'),
          ('offered', '提到交付或消耗物品'), ('action', '提到行动力代价'),
          ('battle', '有具名固定作战资料'), ('random', '提到随机或珍贵奖励'),
          ('operator', '提到招募、进阶或派遣'))
PROVIDERS = {
    'resources': 'current_resource_events', 'vine333': 'current_vine_events',
    'encounters': 'current_encounters', 'shadow346': 'current_shadow',
    'memory336': 'current_memory_tree', 'lake': 'current_lake', 'cave334': 'current_cave',
    'agency340': 'current_agency', 'peace343': 'current_peace', 'dog335': 'current_lone_dog',
    'sand': 'current_sand_reference', 'resting345': 'current_resting',
    'scout342': 'current_scout', 'reconstruction344': 'current_reconstruction',
    'shop': 'current_unattended_shop', 'portal341': 'current_portal',
    'box': 'box_event_reference', 'ritual': 'current_ritual_reference',
    'exit339': 'current_exit', 'rest': 'current_rest_travel', 'flows321': 'documented_event_flows'}


def providers():
    return {key: importlib.import_module('.' + value, __package__) for key, value in PROVIDERS.items()}


def same(a, b):
    if type(a) is not type(b): return False
    if type(a) is dict: return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if type(a) in (list, tuple): return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


def _file(name):
    rel = PurePosixPath(name)
    if type(name) is not str or rel.is_absolute() or '..' in rel.parts or '\\' in name or ':' in name or rel.as_posix() != name:
        raise ValueError('Regular public source required')
    path = ROOT.joinpath(*rel.parts)
    if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('Regular public source required')
    for parent in path.parents:
        if parent == ROOT: break
        if parent.is_symlink(): raise ValueError('Linked source parent refused')
    return path


def _event(data, event_id):
    if 'event' in data:
        row = data['event']; return row if row['id'] == event_id else None
    events = data['events']
    return events.get(event_id) if type(events) is dict else next((e for e in events if e['id'] == event_id), None)


def _snapshot(data, event_id):
    event = _event(data, event_id)
    if event is None: raise ValueError('Exact current event required')
    return {'event': deepcopy(event),
            'scenes': {sid: deepcopy(data['scenes'][sid]) for sid in event['scene_ids']},
            'choices': {cid: deepcopy(data['choices'][cid]) for cid in event['choice_ids']}}


def topic_ids(text, has_battle):
    """Classify cited words only; absence never proves eligibility or no cost."""
    rules = (
        ('gold', r'(?:消耗|失去|扣除)[^，。\n]{0,14}源石锭'),
        ('life', r'(?:消耗|失去|扣除)[^，。\n]{0,14}目标生命'),
        ('held', r'持有'),
        ('offered', r'交出|消耗[^，。\n]{0,18}(?:加工品|自然物|源私钥|零件)|种下'),
        ('action', r'消耗[^，。\n]{0,12}行动力'),
        ('random', r'随机|珍贵'), ('operator', r'招募|进阶|派一名|同伴进入|同伴探索'))
    matches = {key for key, pattern in rules if re.search(pattern, text)}
    if has_battle: matches.add('battle')
    return [key for key, _ in TOPICS if key in matches]


def derive(catalogue, bindings, modules):
    from . import expansion_reference as version
    rows = []; by_pair = {}
    for summary in catalogue:
        binding = bindings[summary['id']]
        if binding is None: raise ValueError('Every existing catalogue group must retain its exact current reader')
        pair = (binding['reader'], binding['current_event_id'])
        if pair in by_pair:
            row = by_pair[pair]; row['catalogue_groups'].append(deepcopy(summary)); continue
        ref = modules[pair[0]].reference(pair[1])
        if ref is None: raise ValueError('Current event source unavailable')
        snapshot = _snapshot(ref['data'], pair[1])
        row = {'id': pair[0] + ':' + pair[1], 'reader': pair[0], 'event_id': pair[1],
               'title': ref['event']['title'], 'catalogue_groups': [deepcopy(summary)],
               'reader_source_identity': json.loads(json.dumps(ref['source_identity'])), **snapshot}
        rows.append(row); by_pair[pair] = row
    for event_id in ('button', 'blueprint', 'revive'):
        ref = modules['flows321'].reference(event_id)
        if ref is None: raise ValueError('Current extra event source unavailable')
        rows.append({'id': 'flows321:' + event_id, 'reader': 'flows321', 'event_id': event_id,
                     'title': ref['event']['title'], 'catalogue_groups': [],
                     'reader_source_identity': json.loads(json.dumps(ref['source_identity'])),
                     **_snapshot(ref['data'], event_id)})
    for row in rows:
        ref = modules[row['reader']].reference(row['event_id']); entries = []
        for sid in row['event']['scene_ids']:
            for cid in row['scenes'][sid]['choice_ids']:
                choice = row['choices'][cid]
                original = ref['data'].get('originals', {}).get('choices', {}).get(cid, {})
                title = choice.get('title', original.get('title', ''))
                description = choice.get('description', original.get('description', ''))
                ids = [choice.get(key) for key in ('item_id', 'reward_item_id', 'offered_item_id', 'effect_item_id', 'required_item_id', 'named_reward_item_id', 'named_part_item_id')]
                ids.append((original.get('displayData') or {}).get('itemId'))
                items = ref['data'].get('originals', {}).get('items', {})
                names = list(dict.fromkeys(items[i]['name'] for i in ids if i in items))
                has_battle = bool(choice.get('stage_ids') or choice.get('has_documented_battle_link'))
                text = version._plain(title + '\n' + description)
                entries.append({'key': row['id'] + ':' + sid + ':' + cid, 'scene_id': sid,
                                'choice_id': cid, 'scene_label': modules[row['reader']].scene_label(ref, sid),
                                'title': version._plain(title), 'description': version._plain(description),
                                'related_item_names': names,
                                'topics': topic_ids(text, has_battle),
                                'presentation': choice.get('presentation', 'documented_choice'),
                                'actual_game_button': choice.get('actual_game_button'),
                                'actual_eligible': None})
        row['entries'] = entries
        row['node_types'] = list(dict.fromkeys(t for group in row['catalogue_groups'] for t in group['node_types']))
        row['topics'] = [topic for topic, _ in TOPICS if any(topic in e['topics'] for e in entries)]
        row['actual_eligible'] = None; row['actual_node'] = None
    if len(rows) != 39 or sum(len(r['catalogue_groups']) for r in rows) != 38:
        raise ValueError('Keep 36 distinct current catalogue readers, three additional events and 38 source groups')
    return {'schema': 'current_event_directory_372_v1', 'rows': rows,
            'actual_complete_generation_pool': None, 'actual_eligible': None, 'run_updated': False}


def packet():
    try:
        from . import expansion_reference as version
        raw = _file(MANIFEST).read_bytes()
        if sha256(raw).hexdigest() != MANIFEST_SHA256: return None
        manifest = json.loads(raw); notes_raw = _file(NOTES).read_bytes()
        notes_pin = manifest['files'][NOTES]
        if len(notes_raw) != notes_pin['bytes'] or sha256(notes_raw).hexdigest() != notes_pin['sha256']: return None
        notes = json.loads(notes_raw)
        expected = {DATA, NOTES, 'rouge/data/node-catalog.json', *notes['original_sources']}
        if (manifest['schema'] != 'current_event_directory_372_manifest_v1'
                or manifest['game_commit'] != version.NEW_COMMIT or set(manifest['files']) != expected): return None
        blobs = {}
        for name, pin in manifest['files'].items():
            content = _file(name).read_bytes()
            if type(pin['bytes']) is not int or len(content) != pin['bytes'] or sha256(content).hexdigest() != pin['sha256']: return None
            blobs[name] = content
        d = json.loads(blobs[DATA]); source_data = {key: json.loads(blobs[path]) for key, path in notes['provider_data_files'].items()}
        if (d['schema'] != 'current_event_directory_372_v1' or set(source_data) != set(PROVIDERS)
                or set(notes['provider_source_identities']) != set(PROVIDERS)): return None
        catalogue = json.loads(blobs['rouge/data/node-catalog.json'])['events']
        ids = set()
        for row in d['rows']:
            if row['id'] in ids: return None
            ids.add(row['id'])
            if not same(row['reader_source_identity'], notes['provider_source_identities'][row['reader']]): return None
            snap = _snapshot(source_data[row['reader']], row['event_id'])
            if any(not same(row[key], value) for key, value in snap.items()): return None
            for group in row['catalogue_groups']:
                old = next((e for e in catalogue if e['id'] == group['id']), None)
                if old is None or any(not same(group[k], old[k]) for k in group): return None
        if len(d['rows']) != 39 or sum(len(r['catalogue_groups']) for r in d['rows']) != 38: return None
        return {'data': d, 'source_identity': (MANIFEST_SHA256, tuple((k, identity) for k, identity in notes['provider_source_identities'].items())),
                'version_source_identity': notes['version_source_identity'],
                'actual_eligible': None, 'actual_node': None, 'run_updated': False}
    except (OSError, ValueError, KeyError, TypeError, UnicodeError, AttributeError, StopIteration, RecursionError):
        return None


def reference(event_id=None, *, query='', node_type=None, topic=None):
    if type(query) is not str or len(query) > 160: return None
    if event_id is not None and type(event_id) is not str: return None
    if node_type is not None and type(node_type) is not str: return None
    if topic is not None and (type(topic) is not str or topic not in dict(TOPICS)): return None
    p = packet()
    if p is None: return None
    needle = query.strip().casefold(); rows = []
    for original in p['data']['rows']:
        if node_type == 'unclassified' and original['node_types']: continue
        if node_type not in (None, 'unclassified') and node_type not in original['node_types']: continue
        if topic is not None and topic not in original['topics']: continue
        text = '\n'.join([original['title'], *[e['title']+'\n'+e['description']+'\n'+'\n'.join(e['related_item_names']) for e in original['entries']]])
        if needle and needle not in text.casefold(): continue
        rows.append(deepcopy(original))
    selected = next((r for r in rows if r['id'] == event_id), None)
    if event_id is not None and selected is None: return None
    return {**p, 'rows': rows, 'selected': selected,
            'filters': {'query': query, 'node_type': node_type, 'topic': topic}}


def resolve(result, entry_key=None):
    if type(result) is not dict or result.get('selected') is None: return None
    fresh = reference(result['selected']['id'], **result['filters'])
    if fresh is None or not same(fresh, result): return None
    row = fresh['selected']; entry = None
    if entry_key is not None:
        if type(entry_key) is not str: return None
        entry = next((e for e in row['entries'] if e['key'] == entry_key), None)
        if entry is None: return None
    return {'event': deepcopy(row), 'entry_key': entry_key,
            'scene_id': entry['scene_id'] if entry else row['event']['entry_scene_id'],
            'choice_id': entry['choice_id'] if entry else None, 'actual_eligible': None, 'run_updated': False}


def player_text(result, entry_key=None):
    row = result['selected']; lines = [NOTICE]
    if row is None:
        return '\n'.join([*lines, '', '已核对39份当前事件资料，另保留它们对应的38个旧目录分组。',
                          '可搜事件名、选项原文或奖励文字，再按资料类别和已提到的条件缩小范围。',
                          '同名情景、重复结果和三重身的三张来源图仍在对应事件内分别保留。',
                          '没有列出不等于不会出现；完整隐藏事件表、服务器资格与实际结果仍未知。'])
    lines += ['', '【事件】' + row['title'], '【资料中的分类】' + ('、'.join(row['node_types']) or '尚未明确；保留在未分类资料中'),
              '这是固定目录的查阅分类，不是当前节点类型或完整出现条件。',
              '【有记录的内容】' + ('、'.join(dict(TOPICS)[key] for key in row['topics']) or '暂未提取到这些文字分类；不代表没有代价或条件。'),
              '对话资料：' + str(len(row['event']['scene_ids'])) + '段；逐段选项或结果记录：' + str(len(row['entries'])) + '条。']
    entry = next((e for e in row['entries'] if e['key'] == entry_key), None)
    if entry:
        lines += ['', '【查阅位置】' + entry['scene_label'], '【选项或结果原文】' + entry['title'], entry['description']]
        if entry['related_item_names']:
            lines += ['关联物品提示：' + '、'.join(entry['related_item_names']), '关联提示不单独当作获得、消耗或已经持有的证明。']
        if entry['presentation'] == 'outcome_reference' or entry['actual_game_button'] is False:
            lines += ['这条是文献中的结果参考，不能当成可以自行选择的游戏按钮。']
        lines += ['可打开这一段准确的原流程；只继续查资料，不在游戏中选择。']
    else:
        lines += ['', '选择下方一条记录可直接定位到对应对话与选项；也可打开事件起始资料。']
    if len(row['catalogue_groups']) > 1:
        lines += ['', '【同名来源保留】' + str(len(row['catalogue_groups'])) + '个旧目录分组对应同一份当前完整文献。',
                  '这里只合并查阅入口，没有判定本局的背景图、原始变体或实际选项。']
    lines += ['', '【仍需核对】完整出现前置、实际阶段、隐藏选项、当前服务器资格和奖励发放。',
              '条件分类不是资格判断；已列条件相符也不能证明本局一定可选。',
              '只作局外查阅，不推荐路线、不提供概率、不扣资源、不领取或改变本局。']
    return '\n'.join(lines)


