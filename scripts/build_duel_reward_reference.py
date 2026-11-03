"""Pin exact public part IDs/grades and declared duel tiers, without drop rates."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / 'research/p3-event-continuation'
GRADES = {'0': 'NORMAL', '1': 'RARE', '2': 'SUPER_RARE'}


def fingerprint(value):
    return sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(',', ':')).encode()).hexdigest()


def cards(text):
    """Read the three atomic fields; do not parse nested effect templates."""
    result = {}
    for start in re.finditer(r'\{\{:沉沦者的黑流树海/零件\n', text):
        depth = 0
        end = None
        for token in re.finditer(r'\{\{|\}\}', text[start.start():]):
            depth += 1 if token.group() == '{{' else -1
            if depth == 0:
                end = start.start() + token.end()
                break
        if end is None:
            raise ValueError('零件模板边界不完整。')
        raw = text[start.start():end]
        fields = dict(re.findall(r'^\|([^=\n|]+)=([^\n]*)$', raw, re.M))
        key = fields['ID']
        if key in result or fields['稀有度'] not in GRADES:
            raise ValueError('零件原ID重复或文档稀有度未列明。')
        result[key] = {'name': fields['名称'], 'grade': int(fields['稀有度']),
            'original_rarity': GRADES[fields['稀有度']], 'kind_name': fields['类型'],
            'special_acquisition_wikitext': fields.get('获取'),
            'source_card_sha256': sha256(raw.encode()).hexdigest(),
            'source_card': raw}
    return result


def build(root=ROOT):
    research = root / 'research/p3-event-continuation'
    receipt = json.loads((research/'source-receipt.json').read_text(encoding='utf8'))
    sources = receipt['sources']
    for key in ('part_document', 'part_template'):
        raw = (root/sources[key]['raw_file']).read_bytes()
        if sha256(raw).hexdigest() != sources[key]['raw_sha256']:
            raise ValueError('冻结文档原文变化，需重新核验。')
    primary = json.loads((research/'selected-original.json').read_text(encoding='utf8'))
    if primary['source'] != sources['original']:
        raise ValueError('固定原表版本不符。')
    template = (research/'part-template-source.wiki').read_text(encoding='utf8')
    # The template expressly accepts both the original enum and the card grade.
    if '|稀有|RARE|1=1f999c|超稀有|SUPER_RARE|2=7d0022|313131' not in template:
        raise ValueError('文档等级与原稀有度枚举的明确同值定义缺失。')
    parsed = cards((research/'parts-source.wiki').read_text(encoding='utf8'))
    module = primary['scrap_module']
    if set(parsed) != set(module['scrapItemToType']) or len(parsed) != 30:
        raise ValueError('零件目录未与完整固定原模块双向对应。')
    kind_names = {k: v['typeName'] for k, v in module['scrapTypeData'].items()}
    items = {}
    for key, card in parsed.items():
        original = primary['items'][key]
        kind = module['scrapItemToType'][key]
        if (card['name'] != original['name'] or card['original_rarity'] != original['rarity']
                or card['kind_name'] != kind_names[kind] or original['type'] != 'SCRAP'):
            raise ValueError('具名零件与原ID、类别或稀有度不符。')
        items[key] = {'item': original, 'kind': kind, 'kind_name': kind_names[kind],
            'documented_grade': card['grade'], 'original_rarity': card['original_rarity'],
            'special_acquisition_wikitext': card['special_acquisition_wikitext'],
            'source_card_sha256': card['source_card_sha256'],
            'source_selector': '$.details.rogue_6.items.' + key,
            'module_selector': '$.modules.rogue_6.scrap.scrapItemToType.' + key}
    fragment = (root/sources['duel_document']['fragment_file']).read_bytes()
    if sha256(fragment).hexdigest() != sources['duel_document']['fragment_sha256']:
        raise ValueError('狭路相逢数量原文变化。')
    import html
    text = re.sub(r'\s+', '', html.unescape(re.sub('<[^>]+>', '', fragment.decode())))
    for phrase in ('最左敌人奖励1低稀有度或中稀有度零件+2招募券',
            '中间敌人奖励1中稀有度/高稀有度零件/浪花/雾滚草/小八界+2招募券',
            '最右敌人奖励1收藏品+2招募券', '在限定时间内击败更难的对手将会获得更好的奖励'):
        if phrase not in text:
            raise ValueError('独立档次、数量或限时条件原文缺失。')
    exceptions = []
    for name in ('浪花', '雾滚草', '小八界'):
        ids = [k for k, v in items.items() if v['item']['name'] == name]
        if len(ids) != 1 or items[ids[0]]['documented_grade'] != 0:
            raise ValueError('中档具名例外没有唯一直接原ID对应。')
        exceptions += ids
    pool = json.loads((root/'rouge/data/battle-node-pools.json').read_text(encoding='utf8'))
    stages = {}
    for key, original in primary['stages'].items():
        row = pool['stages'][key]
        if row['name'] != original['name'] or not any(
                r['source_membership'] == 'duel_event_named_pool' for r in row['source_references']):
            raise ValueError('固定狭路相逢关卡缺原具名来源绑定。')
        if '在限定时间内击败越难的对手将会获得更好的奖励' not in original['description']:
            raise ValueError('原关卡限时条件文字缺失。')
        stages[key] = {'original': original, 'source_pool_references': row['source_references'],
            'source_selector': '$.details.rogue_6.stages.' + key}
    relics = {k: v for k, v in primary['items'].items() if v['type'] == 'RELIC'}
    return {'schema_version': 1, 'sources': sources,
        'runtime_source_sha256': {name: sha256((root/'rouge/data'/name).read_bytes()).hexdigest()
            for name in ('node-events.json', 'exploration-reference.json',
                         'stage-context-reference.json', 'battle-node-pools.json')},
        'items': items, 'relic_catalogue': relics, 'stages': stages,
        'tiers': {
            'left': {'label': '最左敌人', 'allowed_documented_grades': [0, 1],
                'named_exception_ids': [], 'item_type': 'SCRAP', 'quantity': 1, 'recruit_tickets': 2,
                'source_text': '最左敌人奖励1低稀有度或中稀有度零件+2招募券'},
            'middle': {'label': '中间敌人', 'allowed_documented_grades': [1, 2],
                'named_exception_ids': exceptions, 'item_type': 'SCRAP', 'quantity': 1, 'recruit_tickets': 2,
                'source_text': '中间敌人奖励1中稀有度/高稀有度零件/浪花/雾滚草/小八界+2招募券'},
            'right': {'label': '最右敌人', 'allowed_documented_grades': [],
                'named_exception_ids': [], 'item_type': 'RELIC', 'quantity': 1, 'recruit_tickets': 2,
                'source_text': '最右敌人奖励1收藏品+2招募券'}},
        'coverage': {'original_scrap_count': len(items), 'documented_scrap_count': len(parsed),
            'all_original_scraps_matched_bidirectionally': True, 'fixed_duel_stages': len(stages),
            'original_relic_catalogue_count': len(relics), 'tier_rules': 3,
            'middle_named_low_grade_exceptions': 3, 'complete_current_server_pool_known': False},
        'limits': ['档次与数量是限时获胜后的文档条件参考；声明获胜不证明实际结果或领取。',
            '全部零件仅指固定原目录与冻结文档的30项双向覆盖，不是完整服务器随机池。',
            '特殊获取方式另列待证；不能仅凭高稀有度把笼控器或光彩松露加入常规掉落。',
            '收藏品原目录仅作检索；其掉落池成员、解锁、去重、招募券职业及实际资格未知。',
            '档次是文档中的左/中/右对手参考；不推断关卡中的按钮、敌人ID、坐标或选择。',
            '不提供掉落概率，不改动库存、本局记忆、地图绑定或游戏。']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default=str(ROOT/'rouge/data/duel-reward-reference.json'))
    args = parser.parse_args()
    Path(args.output).write_text(json.dumps(build(), ensure_ascii=False, indent=2)+'\n', encoding='utf8')
