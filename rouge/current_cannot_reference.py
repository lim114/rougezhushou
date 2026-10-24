"""Exact current shop boss/vault references, never combat or reward execution."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path, PurePosixPath
import json

from . import current_battle_reference as battle
from . import current_reward_reference as rewards

ROOT = Path(__file__).resolve().parents[1]
PACK = 'research/p3-current-cannot-367'
DATA = 'rouge/data/current-cannot-reference.json'
DOCS = PACK + '/complete-document-extract.json'
NOTES = PACK + '/source-notes.json'
MANIFEST = PACK + '/runtime-manifest.json'
MANIFEST_SHA256 = '3ad798ba90f371b468df85e0cbc52aa6c4a469233865752c7915296c5c73312d'
THEME = 'research/p3-current-recruit-tickets-354/topic-page.html'
THEME_RECEIPT = 'research/p3-current-recruit-tickets-354/source-download.json'
NODE_SOURCE = 'rouge/data/battle-node-pools.json'
STAGES = ('ro6_t_6', 'ro6_t_7')
BOSS = 'enemy_2153_shcan'
VAULT = 'trap_327_shchst'
TOPICS = (('entry', '商店挑战的入口与后果'), ('boss', '坎诺特：移动与回收'),
          ('vault', '保险柜：击破与干员拾取'), ('free', '两种免费栏位来源'),
          ('exit', '逃脱、投降与战后商品'), ('sources', '适用范围与差异'))
NOTICE = '只读当前固定关卡与文献。保险柜拾取、坎诺特回收和商店结算分开说明，不判断战斗状态，也不累计实际奖励。'
UNAVAILABLE = '坎诺特与保险柜资料无法核对，旧说明及关联入口已清除；资料恢复后请重新选择。'


def same(a, b):
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    if type(a) in (list, tuple):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


def _file(name):
    if type(name) is not str:
        raise ValueError('Public relative source required')
    rel = PurePosixPath(name)
    if rel.is_absolute() or '..' in rel.parts or '\\' in name or ':' in name or rel.as_posix() != name:
        raise ValueError('Unsafe public source')
    path = ROOT.joinpath(*rel.parts)
    if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('Regular public source required')
    for parent in path.parents:
        if parent == ROOT:
            break
        if parent.is_symlink():
            raise ValueError('Linked public source refused')
    return path


def selected_originals(current, selected):
    rows = {}
    for sid in STAGES:
        stage = current['version']['current']['details']['stages'][sid]
        key = 'levels/' + stage['levelId'].lower() + '.json'
        level = current['inputs']['levels'][key]
        rows[sid] = {'stage': deepcopy(stage), 'level_key': key, 'level': deepcopy(level)}
    return {'stages': rows, 'enemy_definitions': deepcopy(current['inputs']['enemy_definitions'][BOSS]),
            'handbook': deepcopy(current['inputs']['handbook'][BOSS]),
            'vault_character': deepcopy(selected['characters'][VAULT]),
            'vault_skill': deepcopy(selected['skills']['sktok_shchst'])}


def packet():
    try:
        raw = _file(MANIFEST).read_bytes()
        if sha256(raw).hexdigest() != MANIFEST_SHA256:
            return None
        manifest = json.loads(raw)
        names = {DATA, DOCS, NOTES, THEME, THEME_RECEIPT, NODE_SOURCE,
                 *(PACK + '/' + x for x in ('cannot.html', 'deadbox.html', 'livingwood.html', 'vault.html', 'http-sources.json'))}
        if manifest['schema'] != 'current_cannot_367_manifest_v1' or set(manifest['files']) != names:
            return None
        blobs = {}
        for name, pin in manifest['files'].items():
            body = _file(name).read_bytes()
            if type(pin['bytes']) is not int or len(body) != pin['bytes'] or sha256(body).hexdigest() != pin['sha256']:
                return None
            blobs[name] = body
        r = rewards.packet()
        if r is None:
            return None
        data = json.loads(blobs[DATA])
        if data['schema'] != 'current_cannot_367_v1' or not same(data['originals'], selected_originals(r['current'], r['selected'])):
            return None
        functions = json.loads(blobs[NODE_SOURCE])['node_functions']
        if [f for f in functions if f['node_type'] == '诡意行商'] != [data['shop_function_original']]:
            return None
        return {'data': data, 'documents': json.loads(blobs[DOCS]),
                'source_identity': (MANIFEST_SHA256, r['source_identity'], r['current']['identity'], r['current']['version']['source_identity']),
                'actual_boss_present': None, 'actual_recovered_vaults': None, 'actual_opened_vaults': None,
                'actual_free_slots': None, 'actual_goods': None, 'actual_gold_lost': None,
                'actual_shop_eligible': None, 'actual_outcome': None, 'actual_server_verified': False,
                'run_updated': False, 'numerical_combat_model_added': False}
    except (OSError, ValueError, TypeError, KeyError, UnicodeError, AttributeError, IndexError):
        return None


def shop_target(record):
    if type(record) is not dict:
        return None
    ref = packet()
    if ref is None:
        return None
    expected = ref['data']['shop_function_original']
    if any(k not in record or not same(record[k], value) for k, value in expected.items()):
        return None
    return {'kind': 'shop', 'stage_id': None, 'key': None}


def target_for_enemy(stage_id, enemy_key):
    if type(stage_id) is not str or stage_id not in STAGES or type(enemy_key) is not str:
        return None
    ref = packet()
    if ref is None or ref['data']['stages'][stage_id]['boss']['key'] != enemy_key:
        return None
    return {'kind': 'enemy', 'stage_id': stage_id, 'key': enemy_key}


def target_for_reward(stage_id, reward_id):
    if type(stage_id) is not str or stage_id not in STAGES or type(reward_id) is not str:
        return None
    ref = packet()
    if ref is None or reward_id not in {r['key'] for r in ref['data']['stages'][stage_id]['vaults']}:
        return None
    return {'kind': 'vault', 'stage_id': stage_id, 'key': reward_id}


def reference(target=None, *, floor=None):
    if floor is not None and (type(floor) is not int or not 1 <= floor <= 6):
        return None
    if target is None:
        target = {'kind': 'shop', 'stage_id': None, 'key': None}
    if type(target) is not dict or set(target) != {'kind', 'stage_id', 'key'}:
        return None
    ref = packet()
    if ref is None:
        return None
    kind, sid, key = target['kind'], target['stage_id'], target['key']
    selected = None
    if kind == 'shop':
        if sid is not None or key is not None:
            return None
    elif kind in ('stage', 'enemy', 'vault') and type(sid) is str and sid in STAGES and floor is None:
        stage = ref['data']['stages'][sid]
        if kind == 'stage' and key is not None:
            return None
        if kind == 'enemy':
            if type(key) is not str or key != stage['boss']['key']:
                return None
            selected = deepcopy(stage['boss'])
        if kind == 'vault':
            selected = next((deepcopy(r) for r in stage['vaults'] if r['key'] == key and type(key) is str), None)
            if selected is None:
                return None
    else:
        return None
    rows = [deepcopy(ref['data']['stages'][s]) for s in STAGES
            if (sid is None or sid == s) and (floor is None or s == ('ro6_t_6' if floor < 4 else 'ro6_t_7'))]
    return {**ref, 'target': deepcopy(target), 'stage_id': sid, 'selected': selected,
            'floor_declared': floor, 'stages': rows, 'actual_initial_entry': None}


def links(result):
    if type(result) is not dict or 'target' not in result:
        return []
    items = []
    if result['target']['kind'] != 'shop':
        items.append({'label': '返回诡意行商挑战的条件说明', 'target': {'kind': 'shop', 'stage_id': None, 'key': None}})
    for stage in result['stages']:
        sid = stage['id']
        if result['target']['kind'] == 'shop':
            items.append({'label': stage['name'] + ' · 坎诺特与保险柜', 'target': {'kind': 'stage', 'stage_id': sid, 'key': None}})
        items.append({'label': '打开' + stage['name'] + '固定作战预览', 'target': {'kind': 'battle', 'stage_id': sid, 'enemy_key': None, 'reward_id': None}})
        if result['target']['kind'] != 'shop':
            items.append({'label': '在敌人页查看这份坎诺特引用', 'target': {'kind': 'battle', 'stage_id': sid, 'enemy_key': stage['boss']['key'], 'reward_id': None}})
            for vault in stage['vaults']:
                items.append({'label': vault['label'] + ' · 查看对应奖励记录', 'target': {'kind': 'battle', 'stage_id': sid, 'enemy_key': None, 'reward_id': vault['key']}})
    return items


def qualify_link(result, target):
    if type(target) is not dict or type(result) is not dict or not {'target', 'floor_declared', 'source_identity'} <= result.keys():
        return None
    fresh = reference(result['target'], floor=result['floor_declared'])
    if fresh is None or not same(fresh['source_identity'], result['source_identity']):
        return None
    return deepcopy(target) if any(same(target, row['target']) for row in links(fresh)) else None


def player_text(result, topic=None):
    if topic is not None and (type(topic) is not str or topic not in dict(TOPICS)):
        return ''
    lines = ['坎诺特与保险柜 · 商店挑战', NOTICE]
    if result['stage_id'] is not None:
        stage = result['stages'][0]
        lines += ['', '【当前阅读的固定关卡】', stage['name'],
                  '本关资料列出' + str(len(stage['vaults'])) + '份保险柜记录；不等于实际出现或成功领取数量。',
                  '坎诺特与保险柜根据所选关卡分别核对；当前难度、加成和完整敌人面板尚未算全。']
        if stage['boss']['hp_override_only']:
            lines += ['本关的坎诺特有单独生命设定，不能把另一关的面板直接搬来。具体原值只放在来源页。']
        if result['target']['kind'] == 'vault':
            vault = result['selected']
            lines += ['所选：' + vault['label'], '在文献记载的干员成功拾取路径中，对应' + str(vault['pickup_free_slots_reference']) + '个零价格栏位；这不是实际已领取数量。']
    else:
        lines += ['', '文献层数对照：' + ('未知，保留两份条件候选' if result['floor_declared'] is None else '第' + str(result['floor_declared']) + '层；仅本页对照'),
                  '可查：' + '、'.join(s['name'] for s in result['stages']) + '。当前账户是否满足挑战条件仍未知。']
    for item in result['data']['reading']:
        if topic is None or item['id'] == topic:
            lines += ['', '【' + item['title'] + '】', *item['paragraphs']]
    lines += ['', '【不会据此给出的结果】',
              '实际箱数、实际回收数、实际免费栏位、具体商品及完整奖励总量均未知。不同路径、候选与说明不能相加为实收。',
              '不分析实时站位，不执行操作，不更新本局记忆，不推荐是否挑战。']
    return '\n'.join(lines)
