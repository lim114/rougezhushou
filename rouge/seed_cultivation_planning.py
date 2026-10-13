"""Seed candidates preserve immediate scraps, future yellow gifts and original aliases."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
import re
from . import duel_reward_planning as parts, event_planning

DATA = Path(__file__).with_name('data')
MEMBERSHIP = {'explicit_seed_marker': '明确种子来源标志', 'documented_class_match': '文档类别候选',
    'special_acquisition_unbound': '特殊来源资格待证', 'documented_class_mismatch': '已列类别不符',
    'documented_yellow_id': '文档明确黄色襁褓', 'original_yellow_group_variant': '原同组变体·种子资格待证'}


@lru_cache(maxsize=1)
def reference_data():
    return json.loads((DATA/'seed-cultivation-reference.json').read_text(encoding='utf8'))


def _data():
    data = reference_data()
    for filename, key in (('duel-reward-reference.json', 'part_reference_sha256'),
            ('original-entry-reference.json', 'original_entry_reference_sha256')):
        if sha256((DATA/filename).read_bytes()).hexdigest() != data[key]:
            raise ValueError('零件或黄色襁褓的直接后续原件变化，需重新核验培育引用。')
    return data, parts._data()


def _boolean(value, label):
    if value is not None and type(value) is not bool:
        raise ValueError(label + '需要布尔值或未知。')


def _status(values):
    return 'excluded' if False in values else 'unknown' if None in values else 'matched'


def seed_cultivation_reference(context=None, *, seed_quantity=None, cultivation_completed=None,
        current_normal_exploration=None, next_normal_exploration=None, completed_regions=None):
    data, original = _data()
    context = event_planning._context(context)
    for value, label in ((cultivation_completed, '培育完成声明'),
            (current_normal_exploration, '本局常规探索声明'), (next_normal_exploration, '下局常规探索声明')):
        _boolean(value, label)
    for value, label in ((seed_quantity, '种子件数'), (completed_regions, '本局通过区域数量')):
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError(label + '需要非负整数或未知，不借用当前层或最高层。')
    mode = context.get('exploration_mode')
    if mode not in (None, 'NORMAL', 'MONTH_TEAM'):
        raise ValueError('现有模式声明需要NORMAL、MONTH_TEAM或未知。')
    contextual_normal = None if mode is None else mode == 'NORMAL'
    if current_normal_exploration is not None and contextual_normal is not None and current_normal_exploration is not contextual_normal:
        raise ValueError('本局模式声明与上下文不符，不能任选一个覆盖。')
    normal = contextual_normal if current_normal_exploration is None else current_normal_exploration
    seed_id = data['seed_item_id']
    quantity = context.get('item_quantities', {}).get(seed_id) if seed_quantity is None else seed_quantity
    presence = context.get('item_presence', {}).get(seed_id)
    if quantity is not None and presence is not None and presence is not (quantity > 0):
        raise ValueError('种子件数与持有状态声明矛盾。')
    ownership = quantity > 0 if quantity is not None else presence
    node_type = context.get('node_type')
    source_matches = None if node_type is None else node_type == '秘境行商'
    yellow_mode_check = {'kind': 'normal_exploration', 'matches': normal,
        'scope': 'yellow_legacy_only', 'text': '黄色襁褓培育与收获仅在常规探索模式生效；不把该门推广到普通零件奖励。'}
    checks = [
        {'kind': 'shop_entry', 'matches': source_matches, 'text': '在秘境行商的机械师园圃培育；其它行商不借用这个入口。'},
        {'kind': 'seed_owned', 'matches': ownership, 'text': '需要携带种子；实际一次消耗件数未列明，不能预扣。'},
        {'kind': 'cultivation_completed', 'matches': cultivation_completed, 'text': '候选是培育完成后的资料参考；声明情形不证明实际完成或结果。'}]
    rows = []
    for key, reference in original['items'].items():
        class_match = reference['documented_grade'] in (1, 2) or key in data['seed_documented_named_ids']
        marker = key in data['explicit_seed_marker_ids']
        membership = ('documented_class_mismatch' if not class_match else
            'special_acquisition_unbound' if reference['special_acquisition_wikitext'] else
            'explicit_seed_marker' if marker else 'documented_class_match')
        row = deepcopy(reference)
        row.update(item_id=key, name=row['item']['name'], kind='current_scrap',
            reward_scope='current_exploration_scrap_reference', membership_status=membership,
            documented_class_matches=class_match, explicit_seed_source_marker=marker,
            quantity_reference=1, actual_pool_membership=None, actual_received=None,
            actual_current_quantity=None, actual_future_grant=None)
        rows.append(row)
    common_status = _status([c['matches'] for c in checks])
    yellow_status = _status([c['matches'] for c in checks] + [normal])
    for row in rows:
        row['cultivation_condition_status'] = common_status
    for key, reference in data['legacy_rows'].items():
        row = deepcopy(reference)
        effect = row['next_effect']
        minimum = effect['minimum_completed_regions']
        regions = True if minimum is None else None if completed_regions is None else completed_regions >= minimum
        future_checks = [
            {'kind': 'next_normal_exploration', 'matches': next_normal_exploration,
                'text': '所列效果属于下次常规探索，不计入本局资源。'},
            {'kind': 'completed_regions', 'matches': regions,
                'text': '本局至少通过两个区域才有此额外支援参考。' if minimum else '此物品原说明没有两区域门；不借用其他襁褓条件。'}]
        row.update(name=row['item']['name'], kind='future_yellow_legacy', kind_name='黄色襁褓',
            reward_scope='next_normal_exploration_reference', documented_grade=None,
            membership_status='documented_yellow_id' if row['documented_source_id'] else 'original_yellow_group_variant',
            cultivation_condition_status=yellow_status,
            quantity_reference=1, actual_pool_membership=None, actual_received=None, actual_current_quantity=None,
            future_checks=future_checks, next_effect_condition_status=_status([c['matches'] for c in future_checks]),
            actual_future_grant=None, actual_next_blue_choice_displayed=None,
            inherited_legacy_created=False, buff_applied_to_current_run=False)
        rows.append(row)
    return {'rows': rows, 'seed_item_id': seed_id, 'seed_quantity_declared': quantity,
        'seed_presence_declared': presence, 'context': deepcopy(context), 'checks': checks,
        'documented_condition_status': common_status, 'yellow_mode_check': yellow_mode_check,
        'yellow_cultivation_condition_status': yellow_status,
        'cultivation_completed_declared': cultivation_completed,
        'current_normal_exploration_declared': normal, 'next_normal_exploration_declared': next_normal_exploration,
        'completed_regions_declared': completed_regions,
        'documented_candidates': [r for r in rows if r['membership_status'] in
            ('explicit_seed_marker', 'documented_class_match', 'documented_yellow_id')],
        'unresolved_members': [r for r in rows if r['membership_status'] in
            ('special_acquisition_unbound', 'original_yellow_group_variant')],
        'documented_excluded': [r for r in rows if r['membership_status'] == 'documented_class_mismatch'],
        'fixed_scrap_catalogue_complete': True, 'complete_server_reward_pool_known': False,
        'yellow_documented_source_ids': list(data['yellow_documented_groups']),
        'original_legacy_total': data['original_legacy_total'],
        'unlisted_original_legacy_ids': list(data['unlisted_original_legacy_ids']),
        'documented_seed_cost_quantity': None, 'actual_seed_consumed': None, 'actual_cultivation_success': None,
        'actual_result_item_id': None, 'actual_reward_quantity': None,
        'actual_current_resource_total': None, 'actual_next_resource_total': None,
        'actual_server_eligible': None, 'generation_probability': None,
        'inventory_updated': False, 'run_memory_updated': False, 'next_run_state_created': False,
        'sources': deepcopy(data['sources']), 'limits': list(data['limits'])}


def cultivation_text(result, item_id=None, technical=False):
    if type(technical) is not bool:
        raise ValueError('来源开关需要布尔值。')
    selected = next((r for r in result['rows'] if r['item_id'] == item_id), None) if item_id else None
    if item_id is not None and selected is None:
        raise ValueError('引用不属于固定种子资料及明确原组目录。')
    lines = ['【秘境行商 · 种子培育】',
        '本局零件与下次探索黄色襁褓分别列出；蓝色襁褓属于后续支援收藏品。',
        '已列入口及完成条件：' + parts.QUALIFICATIONS[result['documented_condition_status']],
        '黄色襁褓的额外模式条件：' + parts.QUALIFICATIONS[result['yellow_cultivation_condition_status']],
        '种子件数声明：' + (str(result['seed_quantity_declared']) if result['seed_quantity_declared'] is not None else '未知；持有布尔不编成件数')]
    for check in result['checks']:
        state = '相符' if check['matches'] is True else '不符' if check['matches'] is False else '未知'
        lines.append(state + '：' + check['text'])
    mode_check = result['yellow_mode_check']
    state = '相符' if mode_check['matches'] is True else '不符' if mode_check['matches'] is False else '未知'
    lines.append(state + '：' + mode_check['text'])
    lines += ['', f"已覆盖固定零件30项与黄色襁褓原记录13项；文档候选{len(result['documented_candidates'])}项，"
        f"变体/特殊来源待证{len(result['unresolved_members'])}项，类别不符{len(result['documented_excluded'])}项。",
        '黄色文档明确4原ID，其余9个同组原变体未证明种子会给出；不按同名或后缀合并。',
        '获得1件零件或1个黄色襁褓是各类单独数量参考；候选不相加为实际奖励总量。']
    if selected:
        lines += ['', selected['name'] + ' · ' + MEMBERSHIP[selected['membership_status']]]
        lines.append('该类别的已列培育条件：' + parts.QUALIFICATIONS[selected['cultivation_condition_status']] + '；完整服务器资格未知。')
        if selected['kind'] == 'current_scrap':
            lines += ['类别：' + selected['kind_name'] + ' · ' + parts.GRADE_NAMES[selected['documented_grade']],
                '奖励范围：本次探索的零件资料；实际获得和库存变化未知。']
            if selected['explicit_seed_source_marker']:
                lines.append('本条零件卡片明确标记“有概率由种子培育得到”；只证明来源，不能换算掉率。')
            elif selected['membership_status'] == 'documented_class_match':
                lines.append('按种子原文中/高稀有度类别保留；本条没有独立种子来源标志。')
        else:
            effect = selected['next_effect']
            names = {'next_initial_resource': '下次初始资源', 'next_support_selection_chance': '下次支援额外选择机会',
                'next_extra_blue_support': '下次额外蓝色支援选项'}
            resource = {'gold': '源石锭', 'hope': '希望'}.get(effect.get('resource'), '次')
            lines += ['奖励范围：下次常规探索；本局不加资源、不加蓝色收藏品。',
                '若获得此原候选：' + names[effect['kind']] + f" +{effect['quantity']}{resource}参考；" +
                parts.QUALIFICATIONS[selected['next_effect_condition_status']]]
            for check in selected['future_checks']:
                state = '相符' if check['matches'] is True else '不符' if check['matches'] is False else '未知'
                lines.append(state + '：' + check['text'])
            direct = selected.get('direct_blue_support_reference')
            if direct:
                lines += ['本原记录的独立后续支援指针：' + direct['choice']['title'],
                    '该指针不证明本次种子给了此原变体、下次已经展示或已选择这个支援。']
            if not selected['documented_source_id']:
                lines.append('原组关系可核验，种子对该变体的资格未知；不能从同名羽蛇推定实际原ID。')
        lines += ['用途原文：' + re.sub(r'<[^>]+>', '', selected['item'].get('usage') or '未知'),
            '实际池成员、结果数量及领取：未知。']
    lines += ['', '种子零件来源：' + result['sources']['part_document']['pinned_url'],
        '黄色/蓝色及跨局边界：' + result['sources']['cradle_document']['pinned_url'], *result['limits']]
    if technical:
        lines += ['原目录来源：' + result['sources']['original']['url']]
        if selected:
            lines += ['原物品ID：' + selected['item_id'], '原字段：' + selected['source_selector']]
            if selected['kind'] == 'future_yellow_legacy':
                lines += ['原legacyGroupId：' + selected['legacy_group_id'], '原buff：' + json.dumps(selected['original_buff'], ensure_ascii=False)]
    return '\n'.join(lines)
