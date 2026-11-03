"""Rebuild a fixed, attributed marker reference from sealed public originals."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'research' / 'p3-fruit-marker-flow'
OUTPUT = ROOT / 'rouge' / 'data' / 'fruit-marker-reference.json'


def build():
    receipt = json.loads((EVIDENCE / 'source-receipt.json').read_text(encoding='utf-8'))
    for name, expected in receipt['required_raw_sha256'].items():
        if hashlib.sha256((EVIDENCE / name).read_bytes()).hexdigest() != expected:
            raise ValueError('冻结原件字节变化：' + name)
    items = json.loads((EVIDENCE / 'selected-original-items.json').read_text(encoding='utf-8'))
    marker = (EVIDENCE / 'marker-source-fragment.wiki').read_text(encoding='utf-8')
    parts = (EVIDENCE / 'parts-source-fragment.wiki').read_text(encoding='utf-8')
    relic_id = 'rogue_6_relic_cargo_4'
    ids = ['rogue_6_scrap_G_10', 'rogue_6_scrap_G_11', 'rogue_6_scrap_G_09']
    if items[relic_id]['name'] != '迷藏' or items[relic_id]['usage'] != '每次进入新区域时标记一个节点，探索该节点后获得一个较为稀有的随机自然物':
        raise ValueError('此构建器只适用于固定原版迷藏原文。')
    quotes = [
        '由收藏品【[[沉沦者的黑流树海/拟造物质编目#迷藏|迷藏]]】的效果生成',
        '若标记位于【曲折密道】，从另一端进入钻出后可以触发标记效果且不会消除标记',
        '可能生成于失与得并覆盖原本应生成的“文明之烬”标记的效果',
    ]
    if any(q not in marker for q in quotes):
        raise ValueError('固定标记来源缺少原句。')
    for identity, name in zip(ids, ['恋家果', '光彩松露', '板藤']):
        if items[identity]['name'] != name or '|名称=' + name not in parts or identity not in parts:
            raise ValueError('奖励原ID、名称与完整零件卡片不匹配。')
    return {
        'schema_version': 1,
        'scope': 'explicit_offline_marker_and_visit_declarations',
        'relic': items[relic_id],
        'documented_reward_candidates': [items[i] for i in ids],
        'original_reward_quantity_reference': 1,
        'original_quantity_quote': items[relic_id]['usage'],
        'marker_document_quotes': quotes,
        'original_reward_nature': '随机自然物；三个名称是固定公开文档的候选，不证明完整服务器池。',
        'sources': receipt,
        'unknowns': [
            '实际生成位置、游戏入口、触发、掉落成员、领取及当前服务器资格',
            '普通探索后的标记消除或保留；其它标记共存与覆盖顺序',
            '重复触发上限、随机独立性、总奖励及跳转后的真实库存',
            '实际曲折密道两端绑定；声明路线不是实际地图移动证据',
        ],
    }


if __name__ == '__main__':
    result = build()
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print('固定四原记录与完整标记/零件片段核对后重建。')
