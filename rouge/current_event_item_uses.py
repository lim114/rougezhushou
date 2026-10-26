"""Exact named item prerequisites and offerings, never automatic consumption."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
from . import current_event_directory as directory, expansion_reference as version
ROOT = Path(__file__).resolve().parents[1]
PACK = 'research/p3-current-event-item-uses-376'; DATA = 'rouge/data/current-event-item-uses.json'
NOTES = PACK + '/source-notes.json'; MANIFEST = PACK + '/runtime-manifest.json'; MANIFEST_SHA256 = '5f3d1281e3de8a77d0c26f717bca767d8e618c8ef9c29f3129bf60902927a5e9'
ROLES = (('held', '持有条件'), ('offered', '原文要求交出'), ('consumed', '原文明确消耗'))
NOTICE = '按准确物品查事件用途：持有、交出与消耗分别保留；查阅不表示已经持有、可以选择、已经消耗或已生效。'
UNAVAILABLE = '物品用途来源暂时无法核对，旧条目和所属资料窗口已清除；恢复后请重新选择。'


def derive(reference, current):
    items = {k: v for k, v in current['items'].items() if v['type'] in ('RELIC', 'SCRAP')}
    counts = {name: sum(v['name'] == name for v in items.values()) for name in {v['name'] for v in items.values()}}
    rows = []
    for event in reference['data']['rows']:
        for entry in event['entries']:
            for identity, item in items.items():
                if counts[item['name']] != 1: continue
                for role, verb in (('held', '持有'), ('offered', '交出'), ('consumed', '消耗')):
                    literal = verb + item['name']
                    if literal not in entry['description']: continue
                    rows.append({'id': entry['key'] + ':' + role + ':' + identity,
                                 'item_id': identity, 'item': deepcopy(item), 'category': 'relics' if item['type'] == 'RELIC' else 'scrap',
                                 'event_id': event['id'], 'event_title': event['title'], 'reader': event['reader'],
                                 'entry': deepcopy(entry), 'role': role, 'literal': literal,
                                 'binding_basis': 'unique_full_current_item_name_after_explicit_role_verb',
                                 'quantity_reference': None, 'actual_held': None, 'actual_consumed': None,
                                 'actual_eligible': None, 'actual_effect': None})
    return {'schema': 'current_event_item_uses_376_v1', 'rows': rows,
            'source_directory_identity': json.loads(json.dumps(reference['source_identity'])),
            'actual_complete_use_directory': None, 'actual_inventory': None, 'run_updated': False}


def packet():
    try:
        raw = (ROOT / MANIFEST).read_bytes()
        if sha256(raw).hexdigest() != MANIFEST_SHA256: return None
        manifest = json.loads(raw)
        expected = {DATA, NOTES, directory.DATA, directory.MANIFEST, 'rouge/current_event_directory.py', version.PACK + '/current-topic.json'}
        if manifest['schema'] != 'current_event_item_uses_376_manifest_v1' or set(manifest['files']) != expected: return None
        blobs = {}
        for name, pin in manifest['files'].items():
            rel = Path(name); path = ROOT / name
            if rel.is_absolute() or '..' in rel.parts or '\\' in name or ':' in name or path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()): return None
            if any(parent.is_symlink() for parent in path.parents if parent != ROOT and ROOT in parent.parents): return None
            data = path.read_bytes()
            if type(pin['bytes']) is not int or len(data) != pin['bytes'] or sha256(data).hexdigest() != pin['sha256']: return None
            blobs[name] = data
        base = directory.packet()
        if base is None: return None
        data = json.loads(blobs[DATA]); current = json.loads(blobs[version.PACK + '/current-topic.json'])['details']
        if not directory.same(data, derive(base, current)): return None
        return {'data': data, 'source_identity': (MANIFEST_SHA256, base['source_identity']),
                'version_source_identity': base['version_source_identity'], 'actual_inventory': None,
                'actual_eligible': None, 'run_updated': False}
    except (OSError, ValueError, KeyError, TypeError, AttributeError, UnicodeError, RecursionError): return None


def reference(identity=None, *, item_id=None, role=None, query=''):
    if identity is not None and type(identity) is not str: return None
    if item_id is not None and type(item_id) is not str: return None
    if role is not None and (type(role) is not str or role not in dict(ROLES)): return None
    if type(query) is not str or len(query) > 160: return None
    p = packet()
    if p is None: return None
    rows = []; needle = query.strip().casefold()
    for original in p['data']['rows']:
        if item_id is not None and original['item_id'] != item_id or role is not None and original['role'] != role: continue
        text = '\n'.join((original['item']['name'], original['event_title'], original['entry']['title'], original['entry']['description']))
        if needle and needle not in text.casefold(): continue
        rows.append(deepcopy(original))
    selected = next((r for r in rows if r['id'] == identity), None)
    if identity is not None and selected is None: return None
    return {**p, 'rows': rows, 'selected': selected, 'filters': {'item_id': item_id, 'role': role, 'query': query}}


def _fresh_selected(result):
    if type(result) is not dict or result.get('selected') is None: return None
    fresh = reference(result['selected']['id'], **result['filters'])
    return fresh['selected'] if fresh is not None and directory.same(fresh, result) else None


def destination(result):
    row = _fresh_selected(result)
    if row is None: return None
    base = directory.reference(row['event_id'])
    if base is None or not directory.same(json.loads(json.dumps(base['source_identity'])), result['data']['source_directory_identity']): return None
    return directory.resolve(base, row['entry']['key'])


def acquisition_target(result):
    row = _fresh_selected(result)
    if row is None: return None
    from . import current_reward_origins as origins
    fresh = origins.reference(row['category'], row['item_id'])
    return {'category': row['category'], 'item_id': row['item_id']} if fresh is not None else None


def player_text(result):
    lines = [NOTICE]
    row = result['selected']
    if row is None:
        lines += ['', '已核对7种具名物品在6份事件中的12条用途记录。先选择物品或用途，再点选准确对话。',
                  '笼控器的“持有”不会自动当成消耗；源私钥的不同交付位置也不会合并为一次可以完成全部效果。',
                  '这里只收录完整原文明确写出物品名的用途；泛指随机加工品、自然物、未明确件数和其它来源仍需另外核对。',
                  '目录未列不等于物品没有其它用途；完整服务器资格与本局库存未知。']
        return '\n'.join(lines)
    lines += ['', '【物品】' + row['item']['name'], '【这条用途】' + dict(ROLES)[row['role']],
              '【对应事件】' + row['event_title'], '【准确位置】' + row['entry']['scene_label'],
              '【查看的选项】' + row['entry']['title'], row['entry']['description']]
    if row['role'] == 'held':
        lines += ['', '【持有与消耗分开】原文只明确持有这一条件，没有据此扣除物品。',
                  '即使持有也只满足这一条文字条件，不保证完整资格或该选项一定出现。']
    else:
        lines += ['', '【交付或消耗数量】这条原文没有独立写出件数，保持未知，不默认每次1件。',
                  '本页不会实际交付、扣除或把效果套入本局。']
    if row['item']['name'] == '源私钥':
        lines += ['', '【源私钥的用途分别查看】当前具名目录列有愈创之心1处消耗、调谐仪式3处交付。',
                  '不同步骤是不同选项；不能据此说一把钥匙可完成三步，也不能先按3件扣除。']
    if row['event_title'] == '调谐仪式':
        lines += ['', '【仪式效果的边界】该选项的削弱说明和材料替代方式保留在完整原流程中；不等于已经附着到首领或取消全部能力。']
    lines += ['', '【物品作用原说明】', version._plain(row['item']['usage']),
              '作用说明不是本局已生效或拥有的证明。',
              '', '【继续核对】可打开本条准确对话；已有已证取得方式时另提供来源入口。',
              '没有来源入口仅表示当前具名索引尚未提供，不表示无法获得或来源只有一处。',
              '只作局外查阅，不操作游戏、不扣资源、不领奖、不改变本局或推荐路线。']
    return '\n'.join(lines)

