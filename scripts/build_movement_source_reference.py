"""Bind original MOVE identities to literal PRTS source flags, not server pools."""
import argparse
from hashlib import sha256
import html
import json
from pathlib import Path
import re
import runpy

ROOT = Path(__file__).resolve().parents[1]


def build(root=ROOT, research=None):
    research = research or root/'research/p3-event-continuation/movement-sources'
    common = root/'research/p3-event-continuation'
    source_receipt = json.loads((common/'source-receipt.json').read_text(encoding='utf8'))
    local_receipt = json.loads((research/'source-receipt.json').read_text(encoding='utf8'))
    selected_raw = (research/'selected-original.json').read_bytes()
    if sha256(selected_raw).hexdigest() != local_receipt['selected_original_sha256']:
        raise ValueError('固定加工品原件截取变化，需重新核验。')
    selected = json.loads(selected_raw)
    if selected['source'] != source_receipt['sources']['original']:
        raise ValueError('加工品原版本不符。')
    part_path = root/'rouge/data/duel-reward-reference.json'
    parts = json.loads(part_path.read_text(encoding='utf8'))
    raw = (common/'parts-source.wiki').read_text(encoding='utf8')
    if sha256(raw.encode()).hexdigest() != source_receipt['sources']['part_document']['raw_sha256']:
        raise ValueError('完整零件来源文档变化。')
    cards = runpy.run_path(str(root/'scripts/build_duel_reward_reference.py'))['cards'](raw)
    definitions = {
        'bossdrop': '有概率于“险路恶敌”类关卡通关后，或在通过“险路尽头”时掉落',
        'pathdrop': '有概率于通过“险路小径”时掉落',
        'seedreward': '有概率由种子培育得到',
        'nosell': '不在诡意行商和秘境行商中出售'}
    for key, statement in definitions.items():
        if '#vardefine: ' + key not in raw and '#vardefine:' + key not in raw:
            raise ValueError('来源旗标定义不存在。')
        if statement not in raw:
            raise ValueError('原旗标缺明确来源原句。')
    if '未注明获取方式的零件皆可在诡意行商/秘境行商、战斗掉落或随机事件中获得' not in raw:
        raise ValueError('商店一般来源范围缺完整原句。')
    if '加工品和概念体的估价恒为1源石锭' not in raw:
        raise ValueError('文档售价和基础估价缺独立定义。')
    fragments = {}
    for key, expected in local_receipt['main_fragment_sha256'].items():
        data = (research/(key+'-source.html')).read_bytes()
        if sha256(data).hexdigest() != expected:
            raise ValueError('获取入口的主页面片段变化。')
        fragments[key] = re.sub(r'\s+', '', html.unescape(re.sub('<[^>]+>', '', data.decode())))
    for phrase in ('获得1件加工品', '随后将剩余的行动力转化为等量希望后，进入下一层'):
        if phrase not in fragments['final_exit']:
            raise ValueError('尽头数量与转移文字不明。')
    if '会获得1件珍贵的加工品' not in fragments['path_exit']:
        raise ValueError('小径数量原文不明。')
    for key in ('battle_shop', 'scrap_shop'):
        if '源石锭' not in fragments[key] or '零件' not in fragments[key]:
            raise ValueError('两商店的具名节点购买来源不明。')
    items = {}
    movement_ids = {key for key, kind in selected['scrapItemToType'].items() if kind == 'MOVE'}
    if movement_ids != set(selected['moveScrapData']) or len(movement_ids) != 12:
        raise ValueError('加工品固定目录覆盖不完整。')
    for key in selected['moveScrapData']:
        item = selected['items'][key]
        reference = parts['items'][key]
        if reference['kind'] != 'MOVE' or reference['item'] != item or cards[key]['name'] != item['name']:
            raise ValueError('原加工品ID、名称和类型没有逐项闭合。')
        card = cards[key]['source_card']
        prices = re.findall(r'^\|售价=(\d+)$', card, re.M)
        if len(prices) > 1 or selected['moveScrapData'][key]['sellPrice'] != 1:
            raise ValueError('售价或原估价变化，需重新查证。')
        flags = {flag: '{{#var:' + flag + '}}' in card for flag in definitions}
        if flags['nosell'] is (bool(prices)):
            raise ValueError('文档禁售标志与条目售价应分别核对，不能补估价作售价。')
        items[key] = {**reference, 'original_move_record': selected['moveScrapData'][key],
            'documented_source_flags': flags, 'source_flags_are_game_data_flags': False,
            'documented_card_price': int(prices[0]) if prices else None,
            'original_base_sell_price': selected['moveScrapData'][key]['sellPrice'],
            'source_card_sha256': cards[key]['source_card_sha256'],
            'source_flag_definitions': definitions}
    if (sum(r['documented_source_flags']['bossdrop'] for r in items.values()),
            sum(r['documented_source_flags']['pathdrop'] for r in items.values()),
            sum(r['documented_source_flags']['seedreward'] for r in items.values()),
            sum(r['documented_source_flags']['nosell'] for r in items.values())) != (5, 5, 7, 2):
        raise ValueError('完整固定加工品旗标集合变化，需重新核验范围。')
    catalog_path = root/'rouge/data/node-catalog.json'
    catalog = json.loads(catalog_path.read_text(encoding='utf8'))
    channels = {
        'battle_shop': {'label': '诡意行商购买', 'original_node_types': ['BATTLE_SHOP'], 'membership_rule': 'shop',
            'completion_field': None, 'quantity_reference': None, 'catalogue_refs': []},
        'scrap_shop': {'label': '秘境行商购买', 'original_node_types': ['SCRAP_SHOP'], 'membership_rule': 'shop',
            'completion_field': None, 'quantity_reference': None, 'catalogue_refs': []},
        'seed': {'label': '秘境行商种子培育', 'original_node_types': ['SCRAP_SHOP'], 'membership_rule': 'seedreward',
            'completion_field': 'cultivation_completed', 'quantity_reference': 1, 'catalogue_refs': []},
        'final_exit': {'label': '险路尽头离层奖励', 'original_node_types': ['FINAL'], 'membership_rule': 'bossdrop',
            'completion_field': 'transition_completed', 'quantity_reference': 1, 'catalogue_refs': []},
        'path_exit': {'label': '险路小径离层奖励', 'original_node_types': ['EVACUATE'], 'membership_rule': 'pathdrop',
            'completion_field': 'transition_completed', 'quantity_reference': 1, 'catalogue_refs': []},
        'boss_clear': {'label': '险路恶敌通关来源', 'original_node_types': ['BATTLE_BOSS'], 'membership_rule': 'bossdrop',
            'completion_field': 'victory_declared', 'quantity_reference': None, 'catalogue_refs': []},
}
    for key, node_name in (('final_exit', '险路尽头'), ('path_exit', '险路小径')):
        channels[key]['catalogue_refs'] = [{'event_id': e['id'], 'title': e['title'],
            'entry_scene_keys': e['entry'], 'node_types': e['node_types'], 'source_origin_scene_verified': False}
            for e in catalog['events'] if node_name in e['node_types']]
    if len(channels['final_exit']['catalogue_refs']) != 1 or len(channels['path_exit']['catalogue_refs']) != 3:
        raise ValueError('尽头与三份同名小径目录组应独立保留。')
    entry_quotes = {
        'battle_shop': '可以消耗源石锭购买道具（包括招募券和战术道具）、收藏品和零件的坎诺特的商店。',
        'scrap_shop': '可以消耗源石锭购买零件，也可以出售不再需要的零件以换取源石锭的机械师的商店。',
        'seed': '在此可消耗种子进行种子培育，有概率获得当局零件或跨局增益。',
        'final_exit': '获得1件加工品，随后将剩余的行动力转化为等量希望后，进入下一层。',
        'path_exit': '相较于【险路尽头】，会获得1件珍贵的加工品，但不能使用留存的招募券进行招募。'}
    for key, channel in channels.items():
        fragment_key = 'scrap_shop' if key == 'seed' else key
        if key == 'boss_clear':
            channel['source_quote'] = definitions['bossdrop']
            channel['source_pinned_url'] = source_receipt['sources']['part_document']['pinned_url']
            channel['source_fragment_sha256'] = None
        else:
            if entry_quotes[key] not in fragments[fragment_key]:
                raise ValueError('渠道获取条件原句缺失。')
            channel['source_quote'] = entry_quotes[key]
            channel['source_pinned_url'] = source_receipt['sources']['duel_document']['pinned_url']
            channel['source_fragment_sha256'] = local_receipt['main_fragment_sha256'][fragment_key]
    seed_id = next(key for key, row in parts['items'].items() if row['item']['name'] == '种子')
    seed_card = cards[seed_id]['source_card']
    seed_quote = '培育成功后可能获得：1个任意'
    if not all(phrase in seed_card for phrase in (seed_quote, '小八界', '中稀有度', '高稀有度')):
        raise ValueError('种子数量和稀有度/具名例外范围缺明确卡片原句。')
    return {'schema_version': 1, 'items': items, 'channels': channels,
        'node_types': selected['nodeTypeData'], 'seed_item_id': seed_id,
        'seed_scope_source_card_sha256': cards[seed_id]['source_card_sha256'],
        'seed_scope_quote': seed_card,
        'part_reference_sha256': sha256(part_path.read_bytes()).hexdigest(),
        'catalogue_sha256': sha256(catalog_path.read_bytes()).hexdigest(),
        'sources': source_receipt['sources'], 'main_entry_fragments': local_receipt['main_fragment_sha256'],
        'coverage': {'original_MOVE_items': 12, 'boss_final_positive_flags': 5, 'path_positive_flags': 5,
            'seed_positive_flags': 7, 'shop_explicit_not_sold': 2, 'shop_documented_prices': 10,
            'literal_channel_kinds': 6, 'source_origin_gap_closed': False},
        'limits': ['来源旗标来自冻结PRTS卡片原文，不冒充原游戏获取flags或服务器脚本。',
            '旗标未列不等于不可能；出口/首领未标记成员仍保留待证，不能升级为完整实际池。',
            '文档售价与原估价1分开；只有明确的无修正情形或独立价格声明才比较金币。',
            '未见当前陈列不证明库存没有；只有明确完整加工品陈列声明才可排除当前缺项。',
            '离层、击败或培育完成是方案声明；数量是独立条件参考，实际领取未知。',
            '本图位置只定位已声明节点；历史类型不能当当前获取入口，实际可达性和路径未计算。',
            '同名三重身的3份目录组分开；具名渠道不关闭25原场景/57选项的入口关系缺口。',
            '不提供概率，不操作游戏，不写库存或本局状态。']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--research', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    output = args.output or args.root/'rouge/data/movement-source-reference.json'
    output.write_text(json.dumps(build(args.root, args.research), ensure_ascii=False, indent=2)+'\n', encoding='utf8')
