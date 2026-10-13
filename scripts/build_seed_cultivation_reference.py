"""Keep explicit yellow cradle IDs separate from groups and blue support relics."""
import argparse
from hashlib import sha256
import html
import json
from pathlib import Path
import re
import runpy
from copy import deepcopy

ROOT = Path(__file__).resolve().parents[1]


def build(root=ROOT, research=None):
    research = research or root/'research/p3-event-continuation/seed'
    common = root/'research/p3-event-continuation'
    primary = json.loads((research/'selected-seed-original.json').read_text(encoding='utf8'))
    sources = json.loads((common/'source-receipt.json').read_text(encoding='utf8'))['sources']
    new_source = json.loads((research/'source-receipt.json').read_text(encoding='utf8'))['blackflow_database']
    new_source = {**new_source, 'fragment_file': 'research/p3-event-continuation/seed/cradle-source.wiki'}
    if primary['source'] != sources['original']:
        raise ValueError('黄色襁褓原表版本不同。')
    cradle_path = research/'cradle-source.wiki'
    raw = cradle_path.read_bytes()
    if sha256(raw).hexdigest() != new_source['fragment_sha256']:
        raise ValueError('完整襁褓培育室原文摘要变化。')
    text = raw.decode()
    for phrase in ('黄色', '蓝色', '秘境行商培育种子获得的生灵', '下次探索开始时被收获',
            '所有襁褓生灵仅在<常规探索>模式生效', '以其它模式开始探索时，不会培育或是收获襁褓生灵'):
        if phrase not in text:
            raise ValueError('黄色/蓝色或模式、跨局边界缺明确原文。')
    yellow = text.split('黄色襁褓生灵=', 1)[1].split('|-|', 1)[0]
    groups = {}
    for match in re.finditer(r'\{\{集成战略道具\n\|([^\n]+)\n\|ID=([^\n]+)', yellow):
        name, key = match.groups()
        item = primary['items'][key]
        if item['name'] != name or item['type'] != 'LEGACY' or primary['legacyItems'][key]['legacyGroupId'] != key:
            raise ValueError('文档黄色原ID与独立原组不一致。')
        groups[key] = {'name': name, 'documented_item_id': key}
    if len(groups) != 4:
        raise ValueError('完整黄色文档段不应包含蓝色藏品或隐藏助力。')
    part_path = root/'rouge/data/duel-reward-reference.json'
    parts = json.loads(part_path.read_text(encoding='utf8'))
    # Same explicit card fields already verified by the first feature.
    cards = runpy.run_path(str(root/'scripts/build_duel_reward_reference.py'))['cards']
    parsed = cards((common/'parts-source.wiki').read_text(encoding='utf8'))
    seed_ids = [k for k, v in parsed.items() if v['name'] == '种子']
    if len(seed_ids) != 1:
        raise ValueError('种子不能唯一对应原零件。')
    seed = parsed[seed_ids[0]]['source_card']
    for phrase in ('培育成功后可能获得：1个任意', '襁褓生灵', '浪花，雾滚草，小八界', '中稀有度', '高稀有度'):
        if phrase not in seed:
            raise ValueError('种子的类条件及具名例外缺完整原文。')
    named = [k for k, r in parts['items'].items() if r['item']['name'] in ('浪花', '雾滚草', '小八界')]
    if len(named) != 3:
        raise ValueError('三个种子具名例外未完全对应。')
    markers = [k for k, card in parsed.items() if '{{#var:seedreward}}' in card['source_card']]
    initial = json.loads((root/'rouge/data/original-entry-reference.json').read_text(encoding='utf8'))
    direct_choices = {r['legacy_id']: r for r in initial['startup']['legacy_choices']}
    legacy_rows = {}
    unbound = []
    for key, membership in primary['legacyItems'].items():
        group = membership['legacyGroupId']
        if group not in groups:
            unbound.append(key)
            continue
        item = primary['items'][key]
        if item['name'] != groups[group]['name'] or item['type'] != 'LEGACY':
            raise ValueError('原组成员不应从同名推断，必须明确同组且名称字段匹配。')
        buffs = primary['relics'][key]['buffs']
        if len(buffs) != 1:
            raise ValueError('原下一局效果来源数量变化，需重新查证。')
        buff = buffs[0]
        board = {r['key']: r for r in buff['blackboard']}
        direct = deepcopy(direct_choices.get(key)) if key in direct_choices else None
        if buff['key'] == 'init_gift':
            resource_id, quantity = board['id']['valueStr'], board['count']['value']
            if (resource_id, quantity) not in (('rogue_6_gold', 5.0), ('rogue_6_population', 1.0)):
                raise ValueError('原黄色襁褓资源参数变化。')
            future = {'kind': 'next_initial_resource', 'resource': 'gold' if resource_id == 'rogue_6_gold' else 'hope',
                'quantity': int(quantity), 'minimum_completed_regions': None}
        elif buff['key'] == 'init_support_multi_chance':
            if board['add']['value'] != 1.0 or '至少两个区域' not in item['usage']:
                raise ValueError('支援额外机会的原数量或条件不同。')
            future = {'kind': 'next_support_selection_chance', 'quantity': 1, 'minimum_completed_regions': 2}
        elif buff['key'] == 'force_add_choice':
            if direct is None or direct['force_add_choice_buff'] != buff or direct['legacy_item'] != item:
                raise ValueError('黄色原ID与后续原支援缺直接字段绑定。')
            if board['choice_id']['valueStr'] != direct['choice']['id'] or board['scene_ids']['valueStr'] != direct['scene_id']:
                raise ValueError('不允许用名称或ID后缀反推蓝色支援。')
            if '至少两个区域' not in item['usage']:
                raise ValueError('原黄色襁褓跨局门不明。')
            future = {'kind': 'next_extra_blue_support', 'quantity': 1, 'minimum_completed_regions': 2}
        else:
            raise ValueError('黄色襁褓出现未支持原buff，不猜效果。')
        legacy_rows[key] = {'item_id': key, 'item': item, 'legacy_group_id': group,
            'documented_source_id': key == group, 'documented_group': groups[group],
            'original_buff': buff, 'next_effect': future, 'direct_blue_support_reference': direct,
            'source_selector': '$.details.rogue_6.items.' + key,
            'membership_selector': '$.details.rogue_6.legacyItems.' + key,
            'buff_selector': '$.details.rogue_6.relics.' + key + '.buffs[0]'}
    if len(legacy_rows) != 13 or len(unbound) != 1:
        raise ValueError('保留原明确组别及未列助力；不能静默丢弃或按前缀纳入。')
    fragment = (research/'seed-source-fragment.html').read_bytes()
    plain = re.sub(r'\s+', '', html.unescape(re.sub('<[^>]+>', '', fragment.decode())))
    for phrase in ('秘境行商', '一个非种子的随机零件', '下次<常规探索>', '襁褓生灵'):
        if phrase not in plain:
            raise ValueError('培育入口、当前/下局的独立数量文字缺失。')
    return {'schema_version': 1, 'sources': {**sources, 'cradle_document': new_source},
        'part_reference_sha256': sha256(part_path.read_bytes()).hexdigest(),
        'original_entry_reference_sha256': sha256((root/'rouge/data/original-entry-reference.json').read_bytes()).hexdigest(),
        'seed_item_id': seed_ids[0], 'seed_item_source_card_sha256': parsed[seed_ids[0]]['source_card_sha256'],
        'seed_documented_named_ids': named, 'explicit_seed_marker_ids': markers,
        'legacy_rows': legacy_rows, 'yellow_documented_groups': groups, 'unlisted_original_legacy_ids': unbound,
        'original_legacy_total': len(primary['legacyItems']), 'current_scrap_quantity_reference': 1,
        'yellow_legacy_quantity_reference': 1, 'documented_seed_cost_quantity': None,
        'limits': ['文档四种黄色襁褓明确原ID与9个原同组变体分开；同组不证明种子会给每个变体。',
            '蓝色襁褓是后续支援收藏品；不能当种子立即奖励或当局属性。',
            '30零件类别比较与明确培育来源标志分别保留，不宣称完整服务器随机池。',
            '本局通过区域数量不同于到达最高层、当前层及当前库存；跨局门不得借用那些数值。',
            '实际消耗种子数量、成功、收到的原变体和下局支援展示均未知。',
            '各候选不能相加为实际奖励总量；只提供独立条件参考。',
            '不提供概率，不操作游戏，不写本局、账户档案或库存。']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--research', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    output = args.output or args.root/'rouge/data/seed-cultivation-reference.json'
    output.write_text(json.dumps(build(args.root, args.research), ensure_ascii=False, indent=2)+'\n', encoding='utf8')
