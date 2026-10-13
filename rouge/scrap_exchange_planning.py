"""Finite documented zero-part exchange pools over explicit offline declarations."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
from . import duel_reward_planning as parts, event_planning, node_catalog

DATA = Path(__file__).with_name('data')
MEMBERSHIP = {'same_grade': '文档同档候选', 'high_only_exception': '高档交换具名例外',
    'forbidden_reward': '文档不可交换得到', 'grade_mismatch': '文档档次不符'}


@lru_cache(maxsize=1)
def reference_data():
    return json.loads((DATA/'scrap-exchange-reference.json').read_text(encoding='utf8'))


def _data():
    data = reference_data()
    if sha256((DATA/'duel-reward-reference.json').read_bytes()).hexdigest() != data['part_reference_sha256']:
        raise ValueError('零件逐项来源变化，需重新核验兑换池。')
    original = parts._data()
    if set(data['item_ids']) != set(original['items']):
        raise ValueError('零件固定目录覆盖变化，不能复用旧兑换池。')
    for reference in data['quantity_source']['references']:
        scene = node_catalog._scene(reference['event_id'], reference['scene_key'])
        choice = next((c for c in scene['choices'] if c['key'] == reference['choice_key']), None)
        if choice is None or choice['description'] != reference['description'] or choice['game_choice_ids'] != reference['original_choice_ids']:
            raise ValueError('零件结果的独立数量来源变化，拒绝补造1件奖励。')
    return data, original


def _boolean(value, label):
    if value is not None and type(value) is not bool:
        raise ValueError(label + '需要布尔值或未知。')


def exchange_candidates(offered_item_id, context=None, *, exchange_index=1,
        vocal_cords_unlocked=None, palm_unlocked=None, first_exchange_item_type=None,
        owned_quantity=None):
    data, original = _data()
    if not isinstance(offered_item_id, str) or offered_item_id not in original['items']:
        raise ValueError('需要明确的固定原零件ID，不能按名称或后缀猜兑换档次。')
    if type(exchange_index) is not int or exchange_index not in (1, 2):
        raise ValueError('交换次数需要第1或第2次。')
    for value, label in ((vocal_cords_unlocked, '声带解锁声明'), (palm_unlocked, '手掌解锁声明')):
        _boolean(value, label)
    if first_exchange_item_type not in (None, 'SCRAP', 'RELIC'):
        raise ValueError('首次交换类型需要SCRAP、RELIC或未知，不能用加工品/自然物/概念体替代。')
    if owned_quantity is not None and (type(owned_quantity) is not int or owned_quantity < 0):
        raise ValueError('持有件数需要非负整数或未知，持有布尔不能编成件数。')
    context = event_planning._context(context)
    quantity = context.get('item_quantities', {}).get(offered_item_id) if owned_quantity is None else owned_quantity
    presence = context.get('item_presence', {}).get(offered_item_id)
    if quantity is not None and presence is not None and presence is not (quantity > 0):
        raise ValueError('持有件数与当前持有声明矛盾。')
    ownership = quantity >= 1 if quantity is not None else presence
    offered = original['items'][offered_item_id]
    natural = context.get('entry_mode') == 'natural' and context.get('node_type') == '失与得'
    floor = context.get('floor')
    floor_match = floor in (2, 3, 4, 5) if natural and floor is not None and not context.get('special_region') else None
    checks = [
        {'kind': 'vocal_cords', 'matches': vocal_cords_unlocked,
            'text': '点亮生命游戏“声带”后可交换零件；账户实际解锁未自动取得。'},
        {'kind': 'ownership', 'matches': ownership,
            'text': '此次需要持有所声明零件；件数与持有状态分别保留。'},
        {'kind': 'natural_main_floor', 'matches': floor_match,
            'text': '仅自然失与得入口：不会在第I、VI主层出现；特殊区域口径未证。'}]
    if exchange_index == 2:
        checks += [
            {'kind': 'palm', 'matches': palm_unlocked,
                'text': '第2次交换需点亮生命游戏“手掌”；实际剩余交换次数未取得。'},
            {'kind': 'same_exchange_item_type', 'matches': None if first_exchange_item_type is None else first_exchange_item_type == 'SCRAP',
                'text': '第2次需与首次交换同为零件；收藏品/零件类型不等于零件的三种子类。'}]
    values = [c['matches'] for c in checks]
    status = 'excluded' if False in values else 'unknown' if None in values else 'matched'
    rows = []
    grade = offered['documented_grade']
    for key, reference in original['items'].items():
        forbidden = key in data['forbidden_reward_ids']
        restricted = key in data['high_only_exception_ids']
        same_grade = reference['documented_grade'] == grade
        if forbidden:
            member, matches = 'forbidden_reward', False
        elif restricted:
            member, matches = ('high_only_exception', True) if grade == 2 else ('grade_mismatch', False)
        else:
            member, matches = ('same_grade', True) if same_grade else ('grade_mismatch', False)
        row = deepcopy(reference)
        row.update(item_id=key, name=reference['item']['name'], membership_status=member,
            documented_pool_membership=matches, same_as_offered_item=key == offered_item_id,
            actual_pool_membership=None, actual_displayed=None, actual_received=None)
        rows.append(row)
    return {'offered_item_id': offered_item_id, 'offered': deepcopy(offered), 'offered_documented_grade': grade,
        'context': deepcopy(context), 'exchange_index': exchange_index, 'checks': checks,
        'documented_condition_status': status, 'owned_quantity_declared': quantity, 'item_presence_declared': presence,
        'first_exchange_item_type_declared': first_exchange_item_type,
        'rows': rows, 'documented_candidates': [r for r in rows if r['documented_pool_membership']],
        'documented_excluded': [r for r in rows if not r['documented_pool_membership']],
        'complete_documented_fixed_catalogue_pool_known': True, 'complete_current_server_pool_known': False,
        'documented_reward_quantity': 1, 'quantity_source': deepcopy(data['quantity_source']),
        'same_item_return_documented': any(r['same_as_offered_item'] and r['documented_pool_membership'] for r in rows),
        'actual_option_count': None, 'actual_offered_consumed': None, 'actual_reward_quantity': None,
        'actual_server_eligible': None, 'actual_selection': None, 'inventory_updated': False,
        'map_binding_created': False, 'generation_probability': None, 'sources': deepcopy(data['sources']),
        'limits': list(data['limits'])}


def exchange_text(result, item_id=None, technical=False):
    if type(technical) is not bool:
        raise ValueError('来源开关需要布尔值。')
    selected = next((r for r in result['rows'] if r['item_id'] == item_id), None) if item_id else None
    if item_id is not None and selected is None:
        raise ValueError('候选引用不属于完整固定零件目录。')
    lines = ['【失与得 · 零件交换】',
        '声明提供：' + result['offered']['item']['name'] + ' · ' + parts.GRADE_NAMES[result['offered_documented_grade']],
        f"第{result['exchange_index']}次交换；已列条件：{parts.QUALIFICATIONS[result['documented_condition_status']]}。",
        '获得1件零件是文档结果参考；实际消耗、陈列数、领取与当前服务器资格未知。']
    quantity = result['owned_quantity_declared']
    lines.append('声明件数：' + (str(quantity) if quantity is not None else '未知；持有布尔不换算件数'))
    for check in result['checks']:
        state = '相符' if check['matches'] is True else '不符' if check['matches'] is False else '未知'
        lines.append(state + '：' + check['text'])
    lines += ['', f"完整固定文档比较：{len(result['rows'])}项，文档候选{len(result['documented_candidates'])}项，已列不符{len(result['documented_excluded'])}项。",
        '低/中档交换限于相同档次；高档可得高档及一次性喷气背包、涂装黎博利、涂装佩洛、涂装阿戈尔。',
        '种子、枯苔藓球、笼控器在文档中不能交换得到；该规则不证明它们不能作为提供物。',
        '相同零件可再次出现以文档前提为准；不预扣提供物，不把可能返回当作已返还。']
    if selected:
        lines += ['', selected['name'] + ' · ' + MEMBERSHIP[selected['membership_status']],
            '类别：' + selected['kind_name'] + ' · ' + parts.GRADE_NAMES[selected['documented_grade']],
            '与提供物相同：' + ('是' if selected['same_as_offered_item'] else '否'),
            '当前实际随机池成员与领取：未知。']
    lines += ['', '完整文档池来源：' + result['sources']['part_document']['pinned_url'],
        '入口能力门来源：' + result['sources']['exchange_node']['pinned_url'], *result['limits']]
    if technical:
        lines += ['提供原ID：' + result['offered_item_id'], '原目录来源：' + result['sources']['original']['url']]
        if selected:
            lines += ['候选原ID：' + selected['item_id'], '原字段：' + selected['source_selector']]
    return '\n'.join(lines)
