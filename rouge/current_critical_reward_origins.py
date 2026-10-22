"""Three explicit current ending-item grants with separately checked conditions."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path, PurePosixPath
import json
from . import expansion_reference as version
from . import ending_event_reference as conditions
from . import documented_event_flows as flows
from . import current_exit as exit_flow

ROOT = Path(__file__).resolve().parents[1]
PACK = 'research/p3-critical-reward-origins-349'
DATA = 'rouge/data/current-critical-reward-origins.json'
MANIFEST = PACK + '/runtime-manifest.json'
MANIFEST_SHA256 = 'b90c3d04d05438777cb4aadcb4d6b537276fa9988b8c3faa48c58925fb2c3832'
SELECTIONS = (
    ('entry', 'choice_ro6_final1_8', 'rogue_6_relic_final_7'),
    ('revive', 'choice_ro6_revive_1', 'rogue_6_relic_final_9'),
    ('blueprint', 'choice_ro6_end5_3', 'rogue_6_relic_final_10'),
)
ITEM_IDS = frozenset(v[2] for v in SELECTIONS)
PROVIDERS = (conditions, flows, exit_flow)
UNAVAILABLE = '取得条件的资料暂时无法核对，旧内容和后续窗口已清除；恢复后请重新选择物品。'


def source_rows(current, condition_packet, flow_packet, exit_packet):
    rows = []
    for event_id, cid, iid in SELECTIONS:
        original = current['choices'][cid]
        item = current['items'][iid]
        record = next(r for r in condition_packet['data']['records'] if r['id'] == event_id)
        declared = condition_packet['data']['selected_originals']
        if (cid not in record['choice_ids'] or original != declared['choices'][cid]
                or item != declared['items'][iid] or item['type'] != 'RELIC'
                or original['displayData']['itemId'] != iid
                or not version._plain(original['description']).endswith('获得收藏品')):
            raise ValueError('Exact original grant pointer, text and condition record required')
        if event_id == 'entry':
            if exit_packet['data']['originals']['choices'][cid] != original:
                raise ValueError('Exact exit grant required')
            target = exit_flow.locate('choices', cid)
            if target != {'event_id': 'exit', 'source_request': {'category': 'choices', 'key': cid}}:
                raise ValueError('Exact exit source entry required')
            linked = exit_flow.reference('exit', source_request=target['source_request'])
            if linked is None or len(linked['source_targets']) != 1:
                raise ValueError('Unique existing document target required')
            sid, doc_cid = linked['source_targets'][0]
            doc_choice = linked['choices'][doc_cid]
            if (doc_choice['variant_ids'] != [cid] or doc_choice['title'] != original['title']
                    or doc_choice['description'] != original['description']):
                raise ValueError('Full original variant and document grant must agree')
            reader_target = {'scene_id': sid, 'choice_id': doc_cid}
        else:
            data = flow_packet['data']; choice = data['choices'][cid]
            scene = data['scenes'][choice['scene_id']]
            if (data['originals']['choices'][cid] != original or choice['item_id'] != iid
                    or choice['event_id'] != event_id or cid not in scene['choice_ids']):
                raise ValueError('Exact documented parent and grant required')
            target = {'event_id': event_id, 'scene_id': choice['scene_id'], 'choice_id': cid}
            reader_target = {'scene_id': choice['scene_id'], 'choice_id': cid}
        rows.append({'key': 'critical349:' + cid, 'reader': 'critical349',
                     'event_id': event_id, 'event_title': record['title'],
                     'choice_id': cid, 'item_id': iid, 'item': deepcopy(item),
                     'choice': deepcopy(original), 'target': deepcopy(target), 'reader_target': reader_target,
                     'condition_record': deepcopy(record),
                     'binding_basis': 'explicit_original_grant_item_pointer_no_literal_item_name',
                     'actual_quantity': None, 'actual_received': None, 'actual_eligible': None})
    return rows


def packet():
    try:
        raw = (ROOT / MANIFEST).read_bytes()
        if sha256(raw).hexdigest() != MANIFEST_SHA256: return None
        manifest = json.loads(raw)
        expected = {DATA, PACK + '/source-notes.json'} | {p.DATA for p in PROVIDERS} | {p.MANIFEST for p in PROVIDERS}
        if (manifest['schema'] != 'critical_reward_origins_349_manifest_v1'
                or manifest['game_commit'] != version.NEW_COMMIT or set(manifest['files']) != expected): return None
        for name, pin in manifest['files'].items():
            rel = PurePosixPath(name)
            if rel.is_absolute() or '..' in rel.parts or '\\' in name or ':' in name: return None
            path = ROOT.joinpath(*rel.parts)
            if path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()): return None
            if any(p.is_symlink() for p in path.parents if p != ROOT and ROOT in p.parents): return None
            content = path.read_bytes()
            if len(content) != pin['bytes'] or sha256(content).hexdigest() != pin['sha256']: return None
        upstream = [p.packet() for p in PROVIDERS]; current = version.packet()
        if current is None or any(p is None for p in upstream): return None
        data = json.loads((ROOT / DATA).read_bytes())
        if (data['schema'] != 'critical_reward_origins_349_v1' or data['game_commit'] != version.NEW_COMMIT
                or data['complete_acquisition_pool'] is not False
                or data['rows'] != source_rows(current['current']['details'], *upstream)): return None
        return {'data': data, 'source_identity': (MANIFEST_SHA256, current['source_identity']),
                'actual_received': None, 'actual_eligible': None, 'run_updated': False}
    except (OSError, ValueError, KeyError, TypeError, UnicodeError, AttributeError, StopIteration):
        return None


def reference(category, item_id, values=None):
    if type(category) is not str or type(item_id) is not str or category != 'relics' or item_id not in ITEM_IDS:
        return None
    packet_value = packet()
    if packet_value is None: return None
    rows = [deepcopy(r) for r in packet_value['data']['rows'] if r['item_id'] == item_id]
    detail = version.detail(category, item_id)
    if len(rows) != 1 or detail is None or detail['row']['value']['item'] != rows[0]['item']: return None
    checked = conditions.evaluate(rows[0]['event_id'], values)
    if checked is None or checked['record'] != rows[0]['condition_record']: return None
    return {**packet_value, 'kind': 'critical_acquisition_349', 'category': category,
            'item_id': item_id, 'item': deepcopy(rows[0]['item']), 'rows': rows,
            'condition_reference': checked, 'complete_acquisition_pool': False, 'actual_quantity': None}


def player_text(result, key=None):
    row = result['rows'][0]
    lines = ['【取得方式资料】' + result['item']['name'],
             '只列已核对的这一条取得记录，不是全部掉落方式；不表示本局已经满足条件或已经领取。', '',
             '【相关事件】' + row['event_title'], '【领取选项】' + row['choice']['title'],
             '【代价与奖励原文】', version._plain(row['choice']['description']),
             '【物品对应】原文没有写藏品名，但该条原记录明确指向本页藏品；不是按图标或相似名称猜测。', '',
             '【领取数量】没有独立写明件数，仍为未知，不补成1件。']
    if row['event_id'] == 'entry':
        lines += ['', '【需要核对】第Ⅰ或第Ⅱ层的险路尽头、更新后已完成一次结局并解锁相关藏品，以及10源石锭。',
                  '钱不足只影响这条消费选项，不能据此说整个事件不会出现。持有后的余径规则与本项领取分开查阅。']
    elif row['event_id'] == 'revive':
        lines += ['', '【需要核对】探险家首次倒下后的下个无标记不期而遇，且本局救援机会尚未使用。',
                  '代价是一半目标生命上限，不是当前生命值；整数如何处理尚未核验，不替你计算或扣除。']
    else:
        lines += ['', '【出现条件】制图桌的完整前置和节点类型仍未知，不能把每个不期而遇都列为能获得。',
                  '这是文献中可选的强化项；查看资料不表示必须取得或本局已经生效。']
    lines += ['', '【继续查阅】取得方式页可打开本物品的条件面板；面板底部的“查看准确领取选项的流程原文”可打开对应选项。',
              '已列条件全部相符仍不等于完整资格已核验。完整获取池、服务器执行、实际件数与本局领取仍未知。',
              '仅局外查阅，不扣资源、不领取、不改本局记忆或计算；不推荐路线或给生成概率。']
    return '\n'.join(lines)
