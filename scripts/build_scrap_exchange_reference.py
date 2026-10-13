"""Rebuild the finite exchange rules from complete frozen public statements."""
import argparse
from hashlib import sha256
import html
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def build(root=ROOT, research=None):
    research = research or root/'research/p3-event-continuation/exchange'
    common = root/'research/p3-event-continuation'
    part_path = root/'rouge/data/duel-reward-reference.json'
    parts = json.loads(part_path.read_text(encoding='utf8'))
    source_receipt = json.loads((common/'source-receipt.json').read_text(encoding='utf8'))
    rules = (research/'exchange-rules.wiki').read_text(encoding='utf8')
    required = ['一次性喷气背包、涂装黎博利、涂装佩洛、涂装阿戈尔',
        '零件仅能通过', '低稀有度', '中稀有度', '零件仅能交换获得相同稀有度的零件',
        '种子、枯苔藓球与笼控器无法在零件交换中获得', '以上前提下，所有零件均可能交换获得与自身相同的零件']
    for phrase in required:
        if phrase not in rules:
            raise ValueError('完整兑换条件原文缺失。')
    if rules not in (common/'parts-source.wiki').read_text(encoding='utf8'):
        raise ValueError('兑换规则不是冻结全目录原文的完整逐字片段。')
    fragment = (research/'exchange-node-fragment.html').read_text(encoding='utf8')
    text = re.sub(r'\s+', '', html.unescape(re.sub('<[^>]+>', '', fragment)))
    for phrase in ('在点亮【生命游戏】的“声带”节点后，还可以交换零件',
            '在点亮【生命游戏】的“手掌”节点后，交换次数+1，但只能交换和首次交换相同类型的物品',
            '该节点不会在第I，VI层出现'):
        if phrase not in text:
            raise ValueError('零件解锁、第2次交换或入口范围原文缺失。')
    def exact_ids(names):
        result = []
        for name in names:
            found = [key for key, row in parts['items'].items() if row['item']['name'] == name]
            if len(found) != 1:
                raise ValueError('具名池限制不能唯一对应原零件ID。')
            result += found
        return result
    exceptions = exact_ids(['一次性喷气背包', '涂装黎博利', '涂装佩洛', '涂装阿戈尔'])
    forbidden = exact_ids(['种子', '枯苔藓球', '笼控器'])
    if any(parts['items'][key]['documented_grade'] != 1 for key in exceptions):
        raise ValueError('四项具名高档兑换例外的原中档资料变化。')
    catalog_path = root/'rouge/data/node-catalog.json'
    catalog = json.loads(catalog_path.read_text(encoding='utf8'))
    events = [e for e in catalog['events'] if e['title'] == '回滚文明']
    if len(events) != 1:
        raise ValueError('完整结果数量来源分组没有唯一绑定。')
    event = events[0]
    refs = [{'event_id': event['id'], 'scene_key': scene['key'], 'choice_key': choice['key'],
        'description': choice['description'], 'original_choice_ids': choice['game_choice_ids'],
        'original_source_scene_chain_verified': False} for scene in event['scenes'] for choice in scene['choices']
        if choice['title'] == '接过零件' and choice['description'] == '获得1件零件']
    if len(refs) != 2:
        raise ValueError('两个独立零件结果场景的1件数量原文变化。')
    sources = {**source_receipt['sources'], 'exchange_node': {
        **source_receipt['sources']['duel_document'],
        'fragment_file': 'research/p3-event-continuation/exchange/exchange-node-fragment.html',
        'fragment_selector': 'main node table tr with exact node title 失与得',
        'fragment_sha256': sha256(fragment.encode()).hexdigest()},
        'exchange_rules': {'document': source_receipt['sources']['part_document']['pinned_url'],
            'sha256': sha256(rules.encode()).hexdigest(), 'scope': 'complete 零件交换规则 section before noinclude'},
        'quantity_catalogue': catalog['sources']['cached_community_catalog']}
    return {'schema_version': 1, 'sources': sources, 'part_reference_sha256': sha256(part_path.read_bytes()).hexdigest(),
        'item_ids': list(parts['items']), 'high_only_exception_ids': exceptions, 'forbidden_reward_ids': forbidden,
        'documented_quantity': 1, 'quantity_source': {'description': '获得1件零件', 'references': refs,
            'catalogue_sha256': sha256(catalog_path.read_bytes()).hexdigest()},
        'limits': ['文档候选完整覆盖固定30项；不宣称当前服务器完整池或真实陈列。',
            '声带、手掌与首次交换类型均为声明核对，账户实际科技与剩余交换次数未知。',
            '首次交换类型指收藏品或零件；不把加工品、自然物、概念体混作这个门。',
            '不能交换得到只限制结果候选，不证明此物不能提供；公开可交换标记也不证明实际按钮可用。',
            '相同零件可能出现受前面禁项及档次规则约束，不对提供物预扣或自动返还。',
            '固定427904的数量结果与434637的兑换规则分别保留；原来源场景链及实际执行未证。',
            '不提供概率，不操作游戏、不写本局或库存。']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--research', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    output = args.output or args.root/'rouge/data/scrap-exchange-reference.json'
    output.write_text(json.dumps(build(args.root, args.research), ensure_ascii=False, indent=2)+'\n', encoding='utf8')
