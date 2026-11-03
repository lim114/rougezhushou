"""Exact, source-covered acquisition choices, never an exhaustive loot pool."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json
from . import expansion_reference as version
from . import current_memory_tree as memory, current_lone_dog as dog, current_vine_events as vine

ROOT = Path(__file__).resolve().parents[1]
DATA = 'rouge/data/current-reward-origins.json'
MANIFEST = 'research/p3-current-reward-origins-338/runtime-manifest.json'
MANIFEST_SHA256 = '2039483b9665ca4c025c96622a3b85d2b43d4f65e666580ae9ffb67fb6d21b8a'
NOTICE = '这里只列本版本已逐条核对的取得资料，不是完整获取池；不表示本局会遇到、能够选择或已经领取。'
UNAVAILABLE = '取得方式的来源暂时无法核对，旧清单与事件窗口已清除；恢复后请重新选择物品。'
PROVIDERS = {'memory': memory, 'dog': dog, 'vine': vine}
SELECTIONS = (
    ('memory', 'choice_ro6_normal5_1', 'rogue_6_relic_artifact_5'),
    ('memory', 'choice_ro6_normal5_2', 'rogue_6_relic_artifact_5'),
    ('memory', 'choice_ro6_normal5_3', 'rogue_6_relic_artifact_5'),
    ('dog', 'choice_ro6_task2_1', 'rogue_6_relic_cargo_10'),
    ('vine', 'document-choice:f43c004b6d9ea2e56f8c3963b11f18cc94117a293cfba9210de2e50c0a616c49', 'rogue_6_scrap_G_12'),
    ('vine', 'document-choice:a1184bbf2fce31dc7ed05aadb995ce4dc8d5a2dcbb7da65da46ac80a637dba90', 'rogue_6_scrap_G_12'),
)


def source_rows(packets):
    """Explicit reward fields only: held/consumed items and hint icons are excluded."""
    rows = []
    for reader, cid, item_id in SELECTIONS:
        d = packets[reader]['data']; c = d['choices'][cid]
        field = {'memory': 'reward_item_id', 'dog': 'item_id', 'vine': 'named_part_item_id'}[reader]
        if c[field] != item_id: raise ValueError('Named reward identity differs')
        event = d['event'] if 'event' in d else d['events'][c['event_id']]
        if cid not in event['choice_ids'] or c['scene_id'] not in event['scene_ids']:
            raise ValueError('Event membership differs')
        if cid not in d['scenes'][c['scene_id']]['choice_ids']: raise ValueError('Parent differs')
        item = d['originals']['items'][item_id]
        rows.append({'key': reader + ':' + cid, 'reader': reader, 'event_id': c['event_id'],
                     'event_title': event['title'], 'scene_id': c['scene_id'], 'choice_id': cid,
                     'item_id': item_id, 'item': deepcopy(item), 'choice': deepcopy(c)})
    return rows


def packet():
    try:
        raw = (ROOT / MANIFEST).read_bytes()
        if sha256(raw).hexdigest() != MANIFEST_SHA256: return None
        manifest = json.loads(raw)
        expected = {DATA, 'research/p3-current-reward-origins-338/source-notes.json'}
        expected.update(p.DATA for p in PROVIDERS.values())
        expected.update(p.MANIFEST for p in PROVIDERS.values())
        if manifest['schema'] != 'current_reward_origins_338_manifest_v1' or set(manifest['files']) != expected: return None
        for name, pin in manifest['files'].items():
            path = ROOT / name
            if path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()): return None
            if any(p.is_symlink() for p in path.parents if p != ROOT and ROOT in p.parents): return None
            content = path.read_bytes()
            if len(content) != pin['bytes'] or sha256(content).hexdigest() != pin['sha256']: return None
        d = json.loads((ROOT / DATA).read_bytes())
        packets = {k: p.packet() for k, p in PROVIDERS.items()}
        if any(v is None for v in packets.values()): return None
        if d['schema'] != 'current_reward_origins_338_v1' or d['game_commit'] != version.NEW_COMMIT: return None
        if d['rows'] != source_rows(packets) or d['complete_acquisition_pool'] is not False: return None
        return {'data': d, 'source_identity': (MANIFEST_SHA256, tuple((k, v['source_identity']) for k, v in packets.items())),
                'actual_received': None, 'actual_eligible': None, 'run_updated': False}
    except (OSError, ValueError, KeyError, TypeError, UnicodeError, AttributeError):
        return None


def reference(category, item_id):
    if type(category) is not str or type(item_id) is not str or category not in ('relics', 'scrap'): return None
    from . import current_critical_reward_origins as critical
    if item_id in critical.ITEM_IDS: return critical.reference(category, item_id)
    from . import current_named_reward_origins as named
    if item_id in named.ITEM_IDS: return named.reference(category, item_id)
    p = packet()
    if p is None: return None
    rows = [deepcopy(r) for r in p['data']['rows'] if r['item_id'] == item_id]
    if not rows: return None
    expected_kind = 'RELIC' if category == 'relics' else 'SCRAP'
    if any(r['item']['type'] != expected_kind for r in rows): return None
    detail = version.detail(category, item_id)
    if detail is None or any(detail['row']['value']['item'] != r['item'] for r in rows): return None
    return {**p, 'category': category, 'item_id': item_id, 'item': deepcopy(rows[0]['item']), 'rows': rows,
            'complete_acquisition_pool': False, 'actual_quantity': None}


def player_text(result, key=None):
    if result.get('kind') == 'critical_acquisition_349':
        from .current_critical_reward_origins import player_text as critical_text
        return critical_text(result, key)
    if result.get('kind') == 'named_acquisition_347':
        from .current_named_reward_origins import player_text as named_text
        return named_text(result, key)
    lines = ['【取得方式资料】' + result['item']['name'], NOTICE, '',
             '已核对 ' + str(len(result['rows'])) + ' 条选项；请逐条查看，互斥分支不会合并领取。']
    row = next((r for r in result['rows'] if r['key'] == key), None)
    if row:
        lines += ['', '【事件】' + row['event_title'], '【选项】' + row['choice']['title'],
                  '【代价与奖励原文】', version._plain(row['choice']['description']),
                  '', '【领取数量】原文未独立写明，不补成1件。',
                  '“查看这条选项”会打开对应事件和选项。所有条件默认尚未确认，不支付、不领取，也不写入本局。']
    else: lines += ['', '请选择一条取得方式，查看它自己的代价和奖励。']
    lines += ['', '【范围与未知】只覆盖愈创之心、独活、沉寂之屋中这三种具名奖励的已核对分支。',
              '持有笼控器、消耗源私钥、跟随或标记小狗，都不是这份清单里的额外领取方式。',
              '出现条件、当前服务器适用性、实际库存和完整获取池仍未知；没有列出不等于无法取得。']
    return '\n'.join(lines)
