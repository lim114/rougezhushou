"""Five source-bound investment thresholds; no account or inventory mutation."""
from copy import deepcopy
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
import json
import re

from . import expansion_reference as version

ROOT = Path(__file__).resolve().parents[1]
PACK = 'research/p3-current-bank-356'
DATA = 'rouge/data/current-bank-reference.json'
MANIFEST = PACK + '/runtime-manifest.json'
MANIFEST_SHA256 = '7f012f22dedc7d7dff2e894f01376f24f16517eaf433d14f0b3cc6a72a5fe641'
TOPIC = 'research/p3-expansion-313/current-topic.json'
DOCUMENT = 'research/p3-stage-context/community-main.html'
DOCUMENT_RECEIPT = 'research/p3-stage-context/source-receipt.json'
EXCERPT = PACK + '/investment-433770-excerpt.html'
NOTES = PACK + '/source-notes.json'
ITEM_ID = 'rogue_6_relic_legacy_60'
ICON = 'rouge/data/relic-icons/' + ITEM_ID + '.png'
REWARD_IDS = tuple('bank_reward_' + str(n) for n in range(1, 6))
THRESHOLDS = (15, 50, 125, 250, 500)
NOTICE = ('前瞻性投资：这里对照历史累计投资的资料门槛。'
          '本局源石锭、投资余额和历史累计投资是不同数值；本页不会读取或修改账户。')
UNAVAILABLE = '投资资料暂时无法核对，旧结果、物品图片和后续窗口已清除；恢复后请重新选择。'


def _same(actual, expected):
    if type(actual) is not type(expected):
        return False
    if type(expected) is dict:
        return actual.keys() == expected.keys() and all(_same(actual[k], v) for k, v in expected.items())
    if type(expected) is list:
        return len(actual) == len(expected) and all(_same(a, b) for a, b in zip(actual, expected))
    return actual == expected


def _file(relative):
    if type(relative) is not str:
        raise ValueError('A source path is required')
    rel = PurePosixPath(relative)
    if rel.is_absolute() or '..' in rel.parts or '\\' in relative or ':' in relative or rel.as_posix() != relative:
        raise ValueError('Unsafe source path')
    path = ROOT.joinpath(*rel.parts)
    if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('A regular public source is required')
    for parent in path.parents:
        if parent == ROOT:
            break
        if parent.is_symlink():
            raise ValueError('Linked source parent refused')
    return path


class _InvestmentTable(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.row = None
        self.cell = None

    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            self.row = []
        elif tag in ('th', 'td'):
            self.cell = []

    def handle_data(self, text):
        if self.cell is not None:
            self.cell.append(text)

    def handle_endtag(self, tag):
        if tag in ('th', 'td') and self.cell is not None:
            self.row.append(' '.join(''.join(self.cell).split()))
            self.cell = None
        elif tag == 'tr' and self.row is not None:
            self.rows.append(self.row)
            self.row = None


def document_fragment(html):
    """Select a contiguous original fragment, not reconstructed HTML."""
    start_text = '<ul><li>投资计算方式更新：'
    if html.count(start_text) != 1:
        raise ValueError('Unique investment section required')
    start = html.index(start_text)
    end = html.index('</tbody></table>', start) + len('</tbody></table>')
    return html[start:end]


def derive_data(details, fragment, receipt):
    """Pure source projection used by the builder and checked at runtime."""
    parser = _InvestmentTable()
    parser.feed(fragment)
    if parser.rows[0] != ['历史累计投资额', '投资奖赏'] or len(parser.rows) != 6:
        raise ValueError('Complete five-row document table required')
    if '不再需要投资系统的余额达到标准' not in fragment or '历史累计投资额' not in fragment:
        raise ValueError('Counter distinction must remain in the original document')
    document_rows = {int(v[0]): v[1] for v in parser.rows[1:] if len(v) == 2}
    if tuple(document_rows) != THRESHOLDS:
        raise ValueError('Document thresholds changed')
    records = sorted(details['bankRewards'], key=lambda v: v['unlockGoldCnt'])
    if tuple(r['rewardId'] for r in records) != REWARD_IDS or tuple(r['unlockGoldCnt'] for r in records) != THRESHOLDS:
        raise ValueError('Exact five current reward records required')
    if details['gameConst']['bankRewardCountType'] != 'TOTAL_SUM':
        raise ValueError('Current counter source changed')
    match = re.fullmatch('解锁收藏品【(.+)】', records[3]['desc'])
    if match is None or records[3]['rewardType'] != 'UNLOCK_ITEM':
        raise ValueError('Explicit item name required')
    items = [(key, value) for key, value in details['items'].items()
             if value.get('type') == 'RELIC' and value.get('name') == match[1]]
    if len(items) != 1 or items[0][0] != ITEM_ID:
        raise ValueError('Unique exact named collectible required')
    item = items[0][1]
    if item['unlockCondDesc'] != '在“前瞻性投资系统”中的投资储备余额最高达到过250':
        raise ValueError('Conflicting original item description must remain explicit')
    if receipt['community_revision'] != 433770 or receipt['community_file'] != DOCUMENT:
        raise ValueError('Pinned document provenance required')
    types = ('UNLOCK_WITHDRAW', 'UNLOCK_SHOP_BATTLE', 'ADD_SHOP_POS', 'UNLOCK_ITEM', 'ADD_SHOP_POS')
    if tuple(r['rewardType'] for r in records) != types:
        raise ValueError('Reward types changed')
    # Independent source phrasings stay intact; only the two identical shop rows
    # and the exact named item are cross-matched as text.
    if any(document_rows[n] != records[i]['desc'] for i, n in ((1, 50), (2, 125), (4, 500))):
        raise ValueError('Current reward and document row disagree')
    if match[1] not in document_rows[250] or '取款' not in document_rows[15]:
        raise ValueError('Document reward identity changed')
    return {
        'schema': 'current_bank_reference_356_v1', 'game_commit': version.NEW_COMMIT,
        'bank_records': deepcopy(records), 'counter_original': 'TOTAL_SUM',
        'counter_interpretation_basis': 'pinned_document_explicit_history_total_not_english_enum_only',
        'item': deepcopy(item),
        'item_binding': {'reward_id': 'bank_reward_4', 'item_id': ITEM_ID,
                         'basis': 'explicit_exact_name_and_unique_current_relic_not_original_item_id_pointer'},
        'document': {'file': DOCUMENT, 'revision': 433770,
                     'url': receipt['community_pinned_url'],
                     'rows': [{'threshold': n, 'description': document_rows[n]} for n in THRESHOLDS]},
        'conflict': {'reward_id': 'bank_reward_4', 'document_counter': '历史累计投资额',
                     'item_counter_original': item['unlockCondDesc'],
                     'current_server_resolution_verified': False},
        'actual_unlocked': None, 'actual_received': None, 'account_updated': False,
        'run_updated': False, 'complete_acquisition_pool': False,
    }


def packet():
    try:
        raw = _file(MANIFEST).read_bytes()
        if sha256(raw).hexdigest() != MANIFEST_SHA256:
            return None
        manifest = json.loads(raw)
        expected = {DATA, TOPIC, DOCUMENT, DOCUMENT_RECEIPT, EXCERPT, NOTES, ICON}
        if (manifest['schema'] != 'current_bank_356_manifest_v1'
                or manifest['game_commit'] != version.NEW_COMMIT or set(manifest['files']) != expected):
            return None
        blobs = {}
        for name, pin in manifest['files'].items():
            content = _file(name).read_bytes()
            if type(pin['bytes']) is not int or len(content) != pin['bytes'] or sha256(content).hexdigest() != pin['sha256']:
                return None
            blobs[name] = content
        current = version.packet()
        if current is None:
            return None
        current_source = json.loads(blobs[TOPIC])
        if not _same(current_source, current['current']):
            return None
        receipt = json.loads(blobs[DOCUMENT_RECEIPT])
        if (receipt['community_bytes'] != len(blobs[DOCUMENT])
                or receipt['community_sha256'] != sha256(blobs[DOCUMENT]).hexdigest()):
            return None
        fragment = document_fragment(blobs[DOCUMENT].decode('utf8'))
        if blobs[EXCERPT] != fragment.encode('utf8'):
            return None
        expected_data = derive_data(current_source['details'], fragment, receipt)
        data = json.loads(blobs[DATA])
        if not _same(data, expected_data):
            return None
        return {'data': data, 'source_identity': (MANIFEST_SHA256, current['source_identity']),
                'actual_unlocked': None, 'actual_received': None, 'account_updated': False,
                'run_updated': False}
    except (OSError, ValueError, KeyError, TypeError, UnicodeError, AttributeError, IndexError):
        return None


def _number(value):
    return value is None or (type(value) is int and 0 <= value <= 2147483647)


def reference(cumulative=None, peak_balance=None):
    if not _number(cumulative) or not _number(peak_balance):
        return None
    source = packet()
    if source is None:
        return None
    rows = []
    for original in source['data']['bank_records']:
        threshold = original['unlockGoldCnt']
        conflict = original['rewardId'] == 'bank_reward_4'
        rows.append({'id': original['rewardId'], 'threshold': threshold,
                     'original': deepcopy(original),
                     'document_description': next(r['description'] for r in source['data']['document']['rows'] if r['threshold'] == threshold),
                     'cumulative_condition_matches': None if cumulative is None else cumulative >= threshold,
                     'cumulative_difference': None if cumulative is None else max(0, threshold - cumulative),
                     'has_counter_conflict': conflict,
                     'legacy_peak_condition_matches': None if not conflict or peak_balance is None else peak_balance >= threshold,
                     'item_target': {'category': 'relics', 'key': ITEM_ID} if conflict else None,
                     'actual_unlocked': None, 'actual_received': None})
    return {**source, 'rows': rows, 'declared': {'cumulative': cumulative, 'peak_balance': peak_balance},
            'automatic_account_read': False, 'actual_shop_slots': None, 'actual_unlock_total': None}


def locate(category, key):
    if type(category) is not str or type(key) is not str or category != 'relics' or key != ITEM_ID:
        return None
    return {'reward_id': 'bank_reward_4'} if packet() is not None else None


def item_reference(reward_id):
    if type(reward_id) is not str or reward_id != 'bank_reward_4':
        return None
    source = packet()
    if source is None:
        return None
    detail = version.detail('relics', ITEM_ID)
    if (detail is None or not _same(detail['row']['value']['item'], source['data']['item'])
            or detail['source_identity'] != source['source_identity'][1]):
        return None
    return {**source, 'reward_id': reward_id, 'target': {'category': 'relics', 'key': ITEM_ID},
            'item': deepcopy(source['data']['item']), 'detail': detail,
            'unlock_not_acquisition': True}


def icon_bytes():
    source = packet()
    if source is None:
        return None
    try:
        manifest = json.loads(_file(MANIFEST).read_bytes())
        raw = _file(ICON).read_bytes()
        pin = manifest['files'][ICON]
        return raw if len(raw) == pin['bytes'] and sha256(raw).hexdigest() == pin['sha256'] else None
    except (OSError, ValueError, KeyError, TypeError):
        return None


def _condition(value):
    return '未提供，暂不能对照' if value is None else '已达到这条资料门槛' if value else '尚未达到这条资料门槛'


def player_text(result, reward_id=None):
    row = next((r for r in result['rows'] if r['id'] == reward_id), None)
    if reward_id is not None and row is None:
        return '请选择资料中列出的投资奖赏。'
    lines = ['【前瞻性投资 · 五档奖赏】', NOTICE,
             '按历史累计投资核对门槛，并不表示账户已解锁、商店已增加栏位或已经获得收藏品。', '',
             '【重要：原资料的两种说法】',
             '主题文献明确按历史累计投资计算；当前资料表的计数方式与此相符。',
             '但金酒之杯的原解锁文案仍写“投资储备余额最高达到过250”。两种说法都保留，当前服务器实际采用哪种尚未实测。']
    if row is None:
        lines += ['', '【资料目录】']
        for value in result['rows']:
            lines.append(str(value['threshold']) + ' 源石锭：' + value['original']['desc'])
        lines += ['', '选择一档可对照差额与限制。125和500分别列为两档记录，不推算当前商店的最终商品数量。']
    else:
        lines += ['', '【本档奖赏】', str(row['threshold']) + ' 源石锭：' + row['original']['desc'], '',
                  '【按文献的累计投资口径对照】', _condition(row['cumulative_condition_matches'])]
        if row['cumulative_difference'] is not None:
            lines.append('与这一档的差额：' + str(row['cumulative_difference']) + ' 源石锭。')
        if row['has_counter_conflict']:
            lines += ['', '【金酒之杯原解锁文案】', result['data']['item']['unlockCondDesc'],
                      '若单独按这条最高余额文案对照：' + _condition(row['legacy_peak_condition_matches']),
                      '两个输入彼此独立，缺失的一项不会从另一项补算。达标表示文案条件相符，不表示实际解锁。',
                      '本档只是解锁收藏品，不能直接记为领取1件；完整取得方式与掉落池仍未知。',
                      '可打开金酒之杯的准确当前资料，查看效果及保留的原解锁文字。']
        elif row['id'] == 'bank_reward_2':
            lines += ['这条记录没有给出实际挑战资格和关卡指针；这里不自动跳到某场战斗。']
        elif row['id'] in ('bank_reward_3', 'bank_reward_5'):
            lines += ['这是一档额外商品的解锁记录；当前栏位还可能受其它效果影响，不能据此给出商店总数。']
        else:
            lines += ['这是取款功能的解锁说明；具体取款消耗、可取次数和实际可操作状态不在本页判断。']
    lines += ['', '【来源与范围】',
              '当前原表：国服2026年10月16日固定资料；文献使用已保存的PRTS修订433770，未冒充新网页或服务器执行证明。',
              '文献：' + result['data']['document']['url'],
              '仅局外查阅。不操作游戏、不发起投资或取款，也不更新本局记忆、账户或收藏品。']
    return '\n'.join(lines)


def item_player_text(result):
    item = result['item']
    return '\n'.join(['【投资解锁对应的收藏品】' + item['name'],
                      '【效果】' + version._plain(item['usage']),
                      '【原解锁说明】' + item['unlockCondDesc'], '',
                      '本入口由五档投资表中明确写出的收藏品名，对应到当前资料中唯一同名收藏品。原投资记录没有直接物品编号。',
                      '主题文献按历史累计投资；上面的物品原文按最高余额。冲突保留，实际解锁和领取仍未知。',
                      '这里只提供说明，未将攻速效果代入计算；解锁不是本局获得，也不是完整取得来源。'])
