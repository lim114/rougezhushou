"""Declared duel rewards and complete fixed-catalogue membership comparisons."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import re
from . import event_planning
from .stage_context import stage_context

DATA = Path(__file__).with_name('data')
GRADE_NAMES = {0: '低稀有度', 1: '中稀有度', 2: '高稀有度'}
MEMBERSHIP_NAMES = {'documented_class_match': '已列档次条件相符',
    'named_exception': '文档具名例外', 'special_acquisition_unbound': '特殊来源资格待证',
    'documented_class_mismatch': '已列档次条件不符', 'relic_pool_unbound': '收藏品池成员待证'}
QUALIFICATIONS = {'matched': '已列条件相符', 'unknown': '资格未确认', 'excluded': '已列条件不符'}


@lru_cache(maxsize=1)
def reference_data():
    return json.loads((DATA/'duel-reward-reference.json').read_text(encoding='utf8'))


def _data():
    data = reference_data()
    for name, digest in data['runtime_source_sha256'].items():
        if sha256((DATA/name).read_bytes()).hexdigest() != digest:
            raise ValueError('狭路相逢原目录或入口来源已变化，需重新核验奖励绑定。')
    return data


def is_duel_stage(stage_id):
    return isinstance(stage_id, str) and stage_id in _data()['stages']


def _status(values):
    return 'excluded' if False in values else 'unknown' if None in values else 'matched'


def duel_rewards(stage_id=None, tier='left', context=None, success_declared=None):
    """Compare all source-covered IDs; a class match never proves pool membership.

    A declared timely victory is an offline scenario, not an observed game result.
    Special acquisition records stay unresolved even when their grade matches.
    """
    data = _data()
    if stage_id is not None and (not isinstance(stage_id, str) or stage_id not in data['stages']):
        raise ValueError('需要明确的固定狭路相逢关卡ID；不能按同名、后缀或其他战斗猜测。')
    if not isinstance(tier, str) or tier not in data['tiers']:
        raise ValueError('奖励档次需要left、middle或right。')
    if success_declared is not None and type(success_declared) is not bool:
        raise ValueError('限定时间内获胜声明需要布尔值或未知。')
    context = event_planning._context(context)
    identities = [stage_id] if stage_id else list(data['stages'])
    stages = []
    for identity in identities:
        entry = stage_context(identity, node_type=context.get('node_type'), floor=context.get('floor'),
            special_region=context.get('special_region', False), difficulty=context.get('difficulty'),
            entry_mode=context.get('entry_mode') if context.get('entry_mode') in ('natural', 'content') else None)
        if entry is None or entry['group'] != 'duel':
            raise ValueError('固定关卡与独立狭路相逢入口绑定不同。')
        stages.append({'stage_id': identity, 'name': data['stages'][identity]['original']['name'],
            'original': deepcopy(data['stages'][identity]['original']), 'entry_reference': entry,
            'actual_selected': None, 'actual_victory': None})
    entry_values = [False if s['entry_reference']['status'] == 'excluded' else
        True if s['entry_reference']['status'] == 'matched' else None for s in stages]
    entry_match = entry_values[0] if all(v is entry_values[0] for v in entry_values) else None
    rule = deepcopy(data['tiers'][tier])
    rows = []
    if rule['item_type'] == 'SCRAP':
        for key, reference in data['items'].items():
            row = deepcopy(reference)
            exception = key in rule['named_exception_ids']
            grade_match = reference['documented_grade'] in rule['allowed_documented_grades']
            matches = grade_match or exception
            special = bool(reference['special_acquisition_wikitext'])
            membership = ('documented_class_mismatch' if not matches else
                'special_acquisition_unbound' if special else
                'named_exception' if exception else 'documented_class_match')
            row.update(item_id=key, name=reference['item']['name'],
                documented_grade_matches=grade_match, named_exception=exception,
                documented_reward_class_matches=matches, membership_status=membership,
                actual_pool_membership=None, actual_reward_eligible=None, actual_received=None)
            rows.append(row)
    else:
        for key, item in data['relic_catalogue'].items():
            rows.append({'item_id': key, 'name': item['name'], 'item': deepcopy(item),
                'kind_name': '收藏品', 'documented_grade': None, 'original_rarity': item['rarity'],
                'membership_status': 'relic_pool_unbound', 'documented_reward_class_matches': None,
                'documented_grade_matches': None, 'named_exception': False,
                'actual_pool_membership': None, 'actual_reward_eligible': None, 'actual_received': None,
                'source_selector': '$.details.rogue_6.items.' + key})
    candidates = [r for r in rows if r['membership_status'] in ('documented_class_match', 'named_exception')]
    unresolved = [r for r in rows if r['membership_status'] in ('special_acquisition_unbound', 'relic_pool_unbound')]
    excluded = [r for r in rows if r['membership_status'] == 'documented_class_mismatch']
    return {'stage_id': stage_id, 'stage_candidates': stages, 'tier': tier, 'tier_rule': rule,
        'context': deepcopy(context), 'success_declared': success_declared,
        'documented_condition_status': _status([entry_match, success_declared]),
        'rows': rows, 'documented_class_candidates': candidates, 'unresolved_members': unresolved,
        'documented_class_excluded': excluded, 'catalogue_ids_covered_completely': True,
        'documented_quantity_reference': {'resource': 'scrap' if rule['item_type'] == 'SCRAP' else 'relic',
            'quantity': rule['quantity'], 'recruit_tickets': rule['recruit_tickets']},
        'quantity_condition': 'limited_time_victory_against_declared_documented_opponent',
        'actual_reward': None, 'actual_reward_quantity': None, 'actual_server_eligible': None,
        'actual_opponent_selected': None, 'actual_timely_victory': None,
        'complete_server_reward_pool_known': False, 'recruit_ticket_profession_pool_known': False,
        'generation_probability': None, 'inventory_updated': False, 'map_binding_created': False,
        'sources': deepcopy(data['sources']), 'coverage': deepcopy(data['coverage']), 'limits': list(data['limits'])}


def reward_text(result, item_id=None, technical=False):
    if type(technical) is not bool:
        raise ValueError('来源字段开关需要布尔值。')
    selected = next((r for r in result['rows'] if r['item_id'] == item_id), None) if item_id else None
    if item_id is not None and selected is None:
        raise ValueError('所选奖励引用不在当前档次的完整固定目录中。')
    rule = result['tier_rule']
    quantity = result['documented_quantity_reference']
    kind = '零件' if quantity['resource'] == 'scrap' else '收藏品'
    lines = ['【狭路相逢 · 条件奖励】', rule['label'] + '：' + rule['source_text'],
        f"限定时间内获胜后的文档数量：{quantity['quantity']}件{kind} + {quantity['recruit_tickets']}张招募券。",
        '数量是单次对应档次参考；左、中、右三档不相加，实际掉落与领取未知。',
        '声明情形：' + ('限定时间内获胜' if result['success_declared'] is True else
            '未在限定时间内获胜' if result['success_declared'] is False else '限时获胜状态未声明'),
        '已列入口及获胜条件：' + QUALIFICATIONS[result['documented_condition_status']] + '；实际服务器资格未知。']
    for stage in result['stage_candidates']:
        entry = stage['entry_reference']
        lines.append(stage['name'] + ' · 固定关卡参考：' + QUALIFICATIONS[entry['status']])
        for check in entry['checks']:
            state = '相符' if check['matches'] is True else '不符' if check['matches'] is False else '未知'
            lines.append('  ' + check['description'] + ' 核对：' + state)
    if rule['item_type'] == 'SCRAP':
        lines += ['', f"已覆盖固定零件目录：{len(result['rows'])}项；已列档次条件相符{len(result['documented_class_candidates'])}项，"
            f"特殊来源待证{len(result['unresolved_members'])}项，档次不符{len(result['documented_class_excluded'])}项。",
            '这是一份完整固定目录的类别比较；相符项尚未证明属于当前实际随机池。']
        if rule['named_exception_ids']:
            lines.append('中档文档额外具名候选：浪花、雾滚草、小八界；它们保留各自低稀有度，不改写原档次。')
    else:
        lines += ['', f"原收藏品目录：{len(result['rows'])}项，仅供检索；完整掉落池与每项资格未知。",
            '不把原目录全集当作最右对手可掉落全集，也不补造招募券职业池。']
    if selected:
        item = selected['item']
        lines += ['', selected['name'] + ' · ' + MEMBERSHIP_NAMES[selected['membership_status']],
            '类型：' + selected['kind_name']]
        if selected['documented_grade'] is not None:
            lines.append('文档稀有度：' + GRADE_NAMES[selected['documented_grade']])
        if selected.get('special_acquisition_wikitext'):
            lines.append('此物品有独立获取方式记载；狭路相逢的掉落资格尚未证实，保留待证引用。')
        lines += ['用途参考：' + re.sub(r'<[^>]+>', '', item.get('usage') or '未知'),
            '解锁说明：' + (item.get('unlockCondDesc') or '未列明；不视为已解锁'),
            '实际池成员、领取数量及本局持有变化：未知。']
    sources = result['sources']
    lines += ['', '档次数量来源：PRTS 修订' + str(sources['duel_document']['revision']) + '；' + sources['duel_document']['pinned_url'],
        '逐项零件及稀有度来源：PRTS 修订' + str(sources['part_document']['revision']) + '；' + sources['part_document']['pinned_url'],
        *result['limits']]
    if technical:
        lines += ['', '原目录来源：' + sources['original']['url'],
            '原关卡ID：' + '、'.join(s['stage_id'] for s in result['stage_candidates']),
            '完整目录覆盖：' + json.dumps(result['coverage'], ensure_ascii=False)]
        if selected:
            lines += ['原物品ID：' + selected['item_id'], '原稀有度：' + selected['original_rarity'],
                '原表字段：' + selected['source_selector']]
            if selected.get('special_acquisition_wikitext'):
                lines.append('独立获取方式原文：' + selected['special_acquisition_wikitext'])
    return '\n'.join(lines)
