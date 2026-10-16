"""Player-facing, read-only summaries of the existing fixed node references.

This module changes presentation only. It neither determines server eligibility
nor applies resources, selects a route, or resolves an ambiguous scene instance.
The complete evidence remains available in the caller's existing detail page.
"""
from copy import deepcopy
from html import unescape
import re
import json

from . import event_planning
from . import expedition_results
from .documented_choice_items import event_item_references
from .stage_entry_reference import stage_entry_reference
from . import node_catalog as catalog
from .battle_reward_planning import stage_reward_sources
from .base_settlement_planning import stage_base_rewards, gold_reference_text


STATUS = {'matched': '已列条件相符', 'excluded': '已列条件不符', 'unknown': '条件尚未确认'}
RESOURCES = {'hp': '目标生命值', 'max_hp': '目标生命值上限', 'gold': '源石锭',
             'hope': '希望', 'shield': '护盾', 'ap': '行动力'}
CATEGORIES = {'MOVE': '加工品', 'GOODS': '自然物', 'PASSIVE': '概念体', None: '零件'}
BATTLE_KINDS = {'normal': '普通', 'emergency': '紧急', 'boss': '首领', 'pursuit': '追猎',
                'event': '事件内战斗', 'special': '特殊挑战', 'resident': '居民战斗'}


def _plain(value):
    text = unescape(value) if isinstance(value, str) else ''
    text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
    # Game conditions such as <保密等级·3+> are meaningful text, not tags.
    text = re.sub(r'</?[A-Za-z][^<>]*>|<[@$][^<>]*>|</>', '', text)
    return re.sub(r'https?://\S+', '', text).strip()


def _status(value):
    return STATUS.get(value, '条件尚未确认')


def _floors(values):
    return '、'.join(f'第{n}层' for n in values) if values else '层数尚未确认'


def _position(node):
    row, col = node.get('row'), node.get('col')
    return f'第{row + 1}行、第{col + 1}列' if type(row) is int and type(col) is int else '位置尚未确认'


def _budget(reference):
    coverage = reference.get('nominal_budget_covers')
    return ('已知资源够付这项费用' if coverage is True else '已知资源不足这项费用'
            if coverage is False else '能否付清这项费用：未知')


def _resource_lines(reference):
    kind = reference['kind']
    amount = reference.get('quantity_reference')
    if kind in ('nominal_cost', 'nominal_gain_or_recovery'):
        label = '费用' if kind == 'nominal_cost' else '获得或回复'
        lines = [f'{label}：{amount}{RESOURCES[reference["resource"]]}（原文明示数量）。']
        if kind == 'nominal_cost':
            lines.append(_budget(reference) + '；这不等于游戏按钮能否选择。')
            if reference.get('minimum_retained_hp_reference'):
                lines.append(f'原文注明至少保留{reference["minimum_retained_hp_reference"]}目标生命值；特殊扣除方式及实际扣除量未知。')
        return lines
    if kind == 'fraction_cost':
        amount = reference.get('fraction_arithmetic_reference')
        arithmetic = f'；按已知数量的一半为{amount}' if amount is not None else ''
        return [f'费用：一半{RESOURCES[reference["resource"]]}{arithmetic}。',
                '整数取整方式、实际扣除量和能否付清：未知。']
    if kind == 'category_item_cost':
        complete = '相关库存已声明完整' if reference['inventory_complete_declared'] else '相关库存尚未读全'
        return [f'物品费用：{amount}件{CATEGORIES[reference["scrap_category"]]}。',
                f'已知持有小计{reference["known_owned_subtotal"]}件；{complete}。',
                _budget(reference) + '；具体消耗哪些物品及实际扣除未知。']
    if kind == 'random_category_item_gain':
        return [f'随机奖励：{amount}件{CATEGORIES[reference["scrap_category"]]}；具体物品和完整候选池未知。']
    if kind == 'named_item_cost':
        return [f'物品费用：{_plain(reference["item_name"])} × {amount}。',
                _budget(reference) + '；实际是否消耗未知。']
    return ['这项资源变化尚未整理；请查看资料与依据。']


def _historical_context(entry, context):
    record = entry.get('record') or {}
    historical = bool(entry.get('history_read') or entry.get('history_context_reference')
                      or record.get('historical_read_reference'))
    copied = deepcopy(context or {})
    if historical:
        copied = {key: copied[key] for key in ('floor', 'difficulty', 'special_region', 'node_type') if key in copied}
        copied['entry_mode'] = 'content'
    return historical, copied


def _scene_outcome_lines(result):
    if not result.get('current_rule_applicable'):
        return []
    observation = event_planning.current_observation()
    lines = ['版本差异：这段流程的较新文档与旧资料不同。',
             '旧资料：' + _plain(observation['old_rule']),
             '较新文档：' + _plain(observation['current_rule']),
             '需要进入此事件之前的持有情况及犬植浆来源；现在持有不能替代。']
    for row in result['rows']:
        reward = f'{_plain(row["item_name"])} × {row["quantity"]}' if row['outcome'] == 'named_relic' else f'{row["quantity"]}行动力'
        lines.append(f'较新文档奖励：{reward}；{_status(row["status"])}；{_plain(row["source_condition"])}。')
    lines.append('当前游戏是否采用这段规则、实际领取：未知。')
    return lines


def _battle_choice_lines(row):
    lines = []
    for stage in row['preview_stage_candidates']:
        difficulty = {'NORMAL': '普通', 'FOUR_STAR': '紧急'}.get(stage['difficulty'], '难度未确认')
        lines.append(f'对应作战：{_plain(stage["name"])}（{difficulty}）；可用下方作战入口查看固定地图。')
    pool = row.get('generic_pool_requirement')
    if pool:
        candidates = pool['fixed_named_pool']
        if candidates:
            names = '、'.join(_plain(stage['title']) for stage in candidates)
            lines.append(f'下一主层固定作战候选：{names}；下方可逐个预览，完整候选池及实际选中关卡未知。')
        else:
            lines.append('将通向下一层普通作战中的一个；下一主层或对应关卡尚未确认，暂没有可绑定的地图入口。')
    return lines


def _event_lines(entry, context):
    record = entry['record']
    event_id = record['id']
    result = catalog.event_details(event_id)
    event = result['event']
    historical, context = _historical_context(entry, context)
    qualification = event_planning.event_eligibility(event_id, context)
    lines = [_plain(event['title']), '节点类型：' + ('、'.join(event['node_types']) or '特殊入口'),
             '资料层数：' + _floors(event['floors']), '出现条件：' + _status(qualification['status']) + '；当前游戏能否出现、进入：未知。']
    namesakes = [row['id'] for row in catalog.all_events(include_indirect=True)['rows'] if row['title'] == event['title']]
    if len(namesakes) > 1:
        lines.insert(1, f'同名资料：第{namesakes.index(event_id) + 1}组，共{len(namesakes)}组；以下只列本组选项，不按标题合并。')
    if historical:
        lines.append(('这是历史节点的资料参考；' if entry.get('history_context_reference') and not
                      (entry.get('history_read') or record.get('historical_read_reference')) else '这是历史已读内容；')
                     + '不使用当前持有和资源推定当时条件或费用。')
    if event['natural'] is False:
        lines.append('这项事件不是普通自然出现的候选；需要另行满足特殊入口。')
    for check in qualification['checks']:
        if check['kind'] != 'catalog_scope':
            state = '符合' if check['matches'] is True else '不符' if check['matches'] is False else '未知'
            lines.append(f'前置条件（{state}）：{_plain(check["source_text"])}')
    scenes = result['rows']
    if context.get('entry_mode') in ('natural','content','processed_item'):
        reading=deepcopy(catalog._event(event_id));reading['scenes']=deepcopy(scenes)
        reference=catalog.natural_event_requirements(reading,floor=context.get('floor'),
            entry_mode=context['entry_mode'],special_region=context.get('special_region',False),
            historical=historical or context.get('reference_context_scope')=='historical_title_reference_only')
        if reference:
            lines+=['','【自然出现的已知条件】']
            if not reference['source_valid']:
                lines.append('节点主层资料暂时无法核对；不沿用旧限制，保留原文与资格未知。')
            else:
                floors='、'.join('第'+str(n)+'层' for n in reference['documented_excluded_main_floors'])
                lines.append('资料记载：'+reference['node_type']+'不会自然出现在'+floors+'。')
                match=reference['documented_floor_match']
                lines.append('当前主层不在上述自然出现范围内；下方仍可查阅完整事件资料。' if match is False else
                    '当前主层未被这条限制排除；其它出现条件和实际生成仍未知。' if match is True else
                    '本次为已读、历史、特殊区域或条件未齐的参考；不据此删除内容或判定不能进入。')
                tech=reference['technology_enabling_reference']
                if tech:
                    lines.append('已知开启途径：生命游戏中的“'+tech['name']+'”。')
                    lines.append('这是一条已知开启途径；本账号是否点亮尚未确认，不能据未点亮就认定绝不出现。')
                lines.append('以上为固定版本的资料范围，未证明当前服务器的全部出现条件。')
    numbers = {scene['key']: number for number, scene in enumerate(scenes, 1)}
    expedition=expedition_results.event_reference(event_id)
    if expedition and expedition.get('source_valid'):
        # Bind the actual reading graph as well as the fresh on-disk source.
        original=json.dumps(expedition['expected_event']['scenes'],sort_keys=True,ensure_ascii=False,allow_nan=False)
        current=json.dumps(scenes,sort_keys=True,ensure_ascii=False,allow_nan=False)
        if current!=original:expedition={'source_valid':False}
    expedition_rows={(r['scene_key'],r['choice_key']):r for r in expedition['rows']} if expedition and expedition.get('source_valid') else {}
    expedition_note=expedition.get('return_explanatory_reference') if expedition and expedition.get('source_valid') else None
    if expedition and not expedition.get("source_valid"):
        lines.append('派出与归来资料暂时无法核对；保留原文，奖励时点和实际领取仍待确认。')
    reward_options = catalog.event_reward_options(event_id)
    rewards = {row['choice_id']: row for row in reward_options['rows']}
    documented_items = event_item_references(event_id)
    item_references = (documented_items or {}).get('items', [])
    if documented_items and documented_items.get('status') == 'unknown':
        lines.append('补充物品资料暂时无法核对；可继续阅读选项原文，不表示该选项没有物品。')
    if reward_options.get('supplemental_reward_reference', {}).get('status') == 'unknown':
        lines.append('补充奖励资料暂时无法核对；可继续查看选项原文，奖励数量与实际领取仍未确认。')
    battle_rows = event_planning.event_battle_links(event_id, context=context)['rows']
    for number, scene in enumerate(scenes, 1):
        lines.extend(['', f'【场景 {number}】', _plain(scene['description'])])
        lines.extend(_plain(note) for note in scene.get('edesc_texts', []))
        lines.extend(_scene_outcome_lines(event_planning.scene_outcomes(event_id, scene['key'], context)))
        resources = {row['choice_key']: row for row in event_planning.choice_resources(event_id, scene['key'], context)['rows']}
        for index, choice in enumerate(scene['choices'], 1):
            row = resources[choice['key']]
            expedition_row=expedition_rows.get((scene['key'],choice['key']))
            if expedition_note and (scene['key'],choice['key'])==(expedition_note['scene_key'],expedition_note['choice_key']):
                lines+=['','【探索源头的归来说明】',_plain(choice.get('description')),
                        '归来时（资料）：2希望和怦然信标；该干员不会进阶。',
                        '这段是归来结果说明，不是另一个可点击的选择，也不是派出时的即时收益。']
                continue
            condition = row['choice_eligibility']
            recruitment = condition.get('recruitment_result_reference')
            known_recruitment = bool(recruitment and recruitment['status'] == 'documented_reference'
                                     and recruitment['annotation_role'] == 'selection_result')
            movement = condition.get('movement_result_reference')
            known_movement = bool(movement and movement['status'] == 'documented_reference'
                                  and movement['annotation_role'] == 'selection_result')
            label = '选项' if choice['presentation_role'] == 'display_option_reference' else '说明参考（是否为实际按钮未确认）'
            lines.extend(['', f'{label} {index}：{_plain(choice["title"])}',
                          '效果说明：' + ('可招募的职业组合见下方；实际结果尚未确认。' if known_recruitment
                                      else '前往最近据点的资料说明见下方；实际移动尚未确认。' if known_movement
                                      else _plain(choice.get('description')) or '未知'),
                          '选项条件：' + _status(row['choice_eligibility']['status']) + '；实际可选仍未知。'])
            if choice.get('conditional') and not known_recruitment and not known_movement:
                lines.append('条件原文：' + _plain(choice['conditional']))
            if known_recruitment:
                lines.append('选择后可能的招募结果：')
                for variant_index, variant in enumerate(recruitment['variants'], 1):
                    lines.append(f'职业组合 {variant_index}：' + '或'.join(_plain(name) for name in variant['profession_pair']) + '。')
                lines.append(f'每种结果的资料参考：获得{recruitment["hope_gain_reference"]}希望，'
                             f'招募{recruitment["recruit_count_reference"]}名{recruitment["rarity_ceiling_reference"]}星及以下的'
                             f'{_plain(recruitment["upgrade_reference_text"])}干员。')
                if recruitment.get('upgrade_reference_text') == '直升':
                    lines.append('直升：首次招募即已进阶。本次干员的实际等级、技能及模组等培养信息仍待读取确认。')
                lines.append('本次职业组合、实际招募、招募费用和直升后的等级/精英阶段：尚未确认。')
                lines.append('这些是资料列出的不同可能结果，不相加；职业组合说明不作为选项出现条件。')
            elif recruitment is not None:
                lines.append('补充招募资料暂时无法核对；保留选项原文，具体职业结果仍未确认。')
            if known_movement:
                lines.append('选择后的移动说明（原文）：' + _plain(movement['base_action_reference']['description']))
                lines.append('资料记载：' + _plain(movement['completion_exception_reference']['condition_text']) + '。')
                lines.append('本层是否已完成、实际目的地和是否移动：尚未确认。')
                lines.append('这是单向说明：已完成则不移动；未完成不代表一定移动。过去位置不证明据点作战已完成。')
                lines.append('下方可查看本图已读据点位置和据点固定作战资料；均不代表本次移动结果。')
            elif movement is not None:
                lines.append('补充移动资料暂时无法核对；保留原文，本层完成情况和实际移动仍未确认。')
            for check in condition['parsed_special_requirements']:
                state = '符合' if check['matches'] is True else '不符' if check['matches'] is False else '未知'
                lines.append(f'条件核对（{state}）：{_plain(check["source_text"])}')
                if check.get('holding_is_consumption') is False:
                    lines.append('这里要求持有；不据此认定会消耗该物品。')
            if condition.get('unparsed_condition_text'):
                lines.append('这段附加条件尚未完整解析；保留原文，不当作已满足。')
            if any(check.get('key') == 'hidden_option_unlock' for check in condition['checks']):
                lines.append('这可能是隐藏选项；解锁条件尚未确认。')
            if expedition_row:
                lines.extend(_expedition_choice_lines(expedition_row))
            else:
                for reference in row['resource_references']:
                    lines.extend(_resource_lines(reference))
            if not row['resource_references'] and not expedition_row:
                lines.append('未整理出明确的即时资源数量；不等于零费用或没有收益。')
            for reference in rewards.get(choice['key'], {}).get('rewards', []):
                reward = reference.get('reward') or {}
                name = reward.get('name') or reference.get('description') or '名称未确认'
                quantity = reward.get('quantity')
                label = '具名奖励（零件）：' if reward.get('type') == 'SCRAP' else '具名奖励：'
                lines.append(label + _plain(name) + (f' × {quantity}' if quantity is not None else '；数量未确认') + '；实际领取未知。')
            for reference in item_references:
                if (reference.get('event_id') == event_id and reference.get('scene_key') == scene['key']
                        and reference.get('choice_key') == choice['key']):
                    lines.append('资料写明的物品：' + _plain(reference['name']) + '（收藏品）；数量与本局实际领取尚未确认。')
                    lines.append('可通过下方“查看选项中的物品说明”入口阅读图标与用途；这不会选择游戏中的选项。')
            conversion = row.get('ap_conversion_reference')
            if conversion:
                amount = conversion['hope_gain_reference']
                lines.append('转换参考：每1剩余行动力对应1希望；' + (f'按已知余量为{amount}希望。' if amount is not None else '剩余行动力未确认，数量未知。') + '实际领取未知。')
            targets = [f'场景 {numbers[key]}' for key in choice.get('destination_keys', []) if key in numbers]
            lines.append('后续：' + ('、'.join(targets) if targets else '资料未明确；不能认定已结束。'))
            for sub in choice.get('subchoices', []):
                name = (sub.get('parts') or ['名称未确认'])[0]
                target = numbers.get(sub.get('community_destination_scene_id'))
                lines.append('子选项：' + _plain(name) + ' → ' + (f'场景 {target}' if target is not None else '后续未知'))
            for battle in battle_rows:
                if battle['scene_key'] == scene['key'] and battle['choice_key'] == choice['key']:
                    lines.extend(_battle_choice_lines(battle))
    if result.get('unlinked_original_scenes'):
        lines.append('\n另有同名原文尚未找到完整入口关系；不能当作本次一定可到达的流程，详见资料与依据。')
    lines.append('\n以上按资料原顺序列出，不代选选项。完整奖励池、实际领取及本局变化未知；括号内藏品效果未当作节点即时增减。')
    return lines


def _expedition_choice_lines(reference):
    """Show known phases without applying a resource or a run action."""
    dispatch=reference.get('dispatch_reference')
    if not dispatch:
        return ['选择时（资料）：获得2希望；不派出干员。']
    lines=[f'派出期间：{dispatch["operator_count_reference"]}名干员暂时不能编入队伍。',
           '归来时点：原文为本区域结束、进入新区域；社区资料称下一层开始。特殊区域是否相同仍未确认。']
    item=reference.get('documented_return_item')
    if item:
        amounts='、'.join(str(r['quantity_reference'])+RESOURCES[r['resource']]
                         for r in reference['return_resource_references'])
        lines+=['归来时（资料）：'+amounts+'和'+_plain(item['name'])+'；不是派出时立即获得。',
                '进阶结果：这种源头探索不会使派出的干员进阶。',
                '可在下方派出结果入口中手动查看归来藏品的图标、用途与完整说明。',
                '科技“喙”与源头“仅获得”的关系尚未核验，不额外加算随机加工品。']
    else:
        lines+=['归来物资的具体内容、数量，以及是否进阶：尚未确认。']
    return lines


def _function_lines(record, context):
    lines = [_plain(record.get('node_type')) or '功能节点', '【作用与条件】']
    lines.extend(_plain(row.get('description_text')) for row in record.get('references', []))
    for row in record.get('extra_condition_references', []):
        text = row.get('description_text') or row.get('text')
        if text:
            lines.append(_plain(text))
    checks = dict(record.get('known_requirement_checks') or {})
    if record.get('node_type') and any(key in context for key in ('floor', 'difficulty', 'special_region')):
        current = catalog.function_nodes(record['node_type'], floor=context.get('floor'),
            difficulty=context.get('difficulty'), special_region=context.get('special_region', False))['rows']
        if current:
            incoming = current[0].get('known_requirement_checks') or {}
            for field, keys in (('known_floor_requirement_matches', ('floor', 'special_region')),
                                ('known_difficulty_requirement_matches', ('difficulty',))):
                if any(key in context for key in keys):
                    checks[field] = incoming.get(field)
    for field, label in (('known_floor_requirement_matches', '已列层数条件'),
                         ('known_difficulty_requirement_matches', '已列保密等级条件')):
        if checks.get(field) is not None:
            lines.append(label + '：' + ('相符' if checks[field] else '不符') + '；不能据此确认游戏实际状态。')
    lines.append('这些是固定资料说明；本局是否解锁、已生效或可再次使用：未知。')
    if record.get('node_type') == '林间空地':
        lines.append('没有已确认的当前事件；通过前的类型与内容仍可在本局历史中查看。')
    return lines


def _battle_lines(record):
    stage_id = record.get('id') or record.get('stage_id')
    result = stage_reward_sources(stage_id)
    lines = [_plain(result['stage_name']), '类别：' + ('、'.join(BATTLE_KINDS.get(kind, '类别未确认') for kind in record.get('categories', [])) or '未确认'),
             '资料层数：' + _floors(record.get('floors')), '可用下方入口查看固定战斗地图、敌人和出场资料。',
             '【战后基础奖励】', '以下需要战斗胜利，按资料中的入口分别列出；不含额外加成，不代表本局已领取。']
    entry_reference = stage_entry_reference(stage_id)
    if entry_reference is not None:
        reward_heading = lines[-2:]; lines = lines[:-2]
        if entry_reference.get('status') == 'documented_reference':
            floors = '、'.join(str(r['main_floor_reference']) for r in entry_reference['rows'] if type(r['main_floor_reference']) is int)
            lines.extend(['', '【资料记录的关联入口】', '原始资料列出第' + floors + '层普通作战上的关联标记，另有原资料称为“假层”的单独记录。',
                '可在战斗预览中点击“查看对应节点与进入方式资料”，阅读完整标记及相关藏品说明。',
                '这不保证本局出现；假层不归到某个主层或秘境，实际标记位置和全部进入方式仍未确认。'])
        else:
            lines.append('补充进入方式资料暂时无法核对；保留关卡原说明，不把资料失效当作没有入口。')
        lines.extend(['', *reward_heading])
    base = stage_base_rewards(stage_id)
    for reference in base['rows']:
        if reference['status'] == 'excluded':
            continue
        region = ('追猎' if reference['rule_kind'].endswith('pursuit') else
                  '秘境' if reference.get('region_scope') == 'portal' else
                  '特殊事件作战' if reference['rule_kind'] == 'named_special_battle' else '主层作战')
        floor = reference.get('source_battle_floor')
        origin = region + (f'、第{floor}层' if floor is not None else '')
        xp = reference['base_experience_reference']
        lines.append(f'条件：{origin}；基础指挥经验：{xp if xp is not None else "未知"}；'
                     f'源石锭：{gold_reference_text(reference["base_gold_reference"])}。')
        lines.append('本局是否属于此入口、实际领取：未知；不同入口的候选奖励不能相加。')
    if not base['rows']:
        lines.append('基础结算资料尚未绑定；不等于奖励为零。')
    lines.extend(['', '【可能获得的额外奖励】'])
    reward_entities = {row['entity_id'] for row in result['rows']}
    if {'trap_323_shsbox', 'enemy_2152_shezlc'} <= reward_entities:
        lines.append('箱型装置与它召出的移动恶笼草是关联资料；同一移动敌人的奖励只能算一次，不能各加10源石锭。')
    if record.get('entry_condition_excluded_reference'):
        lines.append('这项资料不符合当前已列入口条件，仍可查看原图；不当作当前可进入的作战。')
    for row in result['rows']:
        lines.append(_plain(row['name']))
        if row.get('display_cell'):
            lines.append('固定资料位置：' + _position(row['display_cell']) + '；不表示当前已出现。')
        group = row.get('candidate_group_reference')
        if group:
            names = [member.get('name') or ('不生成对象' if member.get('is_empty_key') else '名称未确认') for member in group['members']]
            lines.append('同组候选：' + '、'.join(_plain(name) for name in names) + '；不能相加成实际奖励。')
        for outcome in row['rule']['outcomes']:
            resource = {'gold': '源石锭', 'random_scrap': '随机零件', 'random_relic': '收藏品'}.get(outcome['resource'], '奖励')
            quantity = outcome.get('quantity')
            amount = f'{quantity}{resource}' if quantity is not None else f'{resource}数量未知'
            lines.append(f'条件：{_plain(outcome["condition_label"])}；数量参考：{amount}。')
            if outcome.get('cost_quantity') is not None:
                lines.append(f'开启费用参考：{outcome["cost_quantity"]}点部署费用；不是源石锭或行动力。')
        if row.get('kind') == 'moving_enemy_action':
            lines.append('击倒收益和漏过损失是两种不同结果，不能同时相加，也不能用记录条数代替出现数量。')
        if row['rule'].get('quantity_scope_notice'):
            lines.append(_plain(row['rule']['quantity_scope_notice']))
    if not result['rows']:
        lines.append('当前固定资料未列出已支持的奖励对象；不等于没有奖励。')
    lines.append('完整结算奖励、随机物品池、实际出现及领取总量：未知。各条件奖励不能直接相加。')
    return lines


def _map_lines(entry, dossier, map_context, context):
    node = entry['record']
    if dossier is None and map_context:
        graph, conditions = map_context[:2]
        dossier = catalog.node_dossier(graph, node['id'], **conditions)
    historical = bool(map_context and len(map_context) > 3 and map_context[3])
    lines = [_position(node), ('当时类型：' if historical else '当前类型：') + _plain(node.get('observed_type') or '未确认')]
    if node.get('template_type'):
        lines.append('模板固定类型：' + _plain(node['template_type']))
    if node.get('remembered_type'):
        lines.append('过去类型：' + _plain(node['remembered_type']))
    for key, label in (('content', '当时读取' if historical else '当前读取'), ('remembered_content', '过去读取')):
        if node.get(key):
            lines.append(label + '：' + _plain(node[key].get('title') or '内容身份未确认'))
    for content in node.get('content_history') or []:
        lines.append('历史读取：' + _plain(content.get('title') or '内容身份未确认'))
    if node.get('observed_type') in ('林间空地', '曲折密道'):
        lines.append(('这是当时的通行节点；不代表现在的状态。' if historical else '这是当前通行节点；')
                     + '过去事件不当作现在仍可发生的事件。')
    if dossier:
        lines.extend(['', '【该节点的固定资料候选】'])
        for key, label in (('rows', '事件'), ('battle_rows', '作战'), ('function_rows', '功能')):
            for row in dossier.get(key, []):
                text = label + '：' + _plain(row.get('title') or row.get('node_type') or '名称未确认')
                if key == 'rows':
                    event_context = deepcopy(context)
                    if map_context:
                        event_context.update(map_context[1])
                    kind = node.get('observed_type')
                    event_context.update(node_type=kind if kind and not kind.startswith(('未知', '类型未确认')) else None,
                        entry_mode='content' if (node.get('content') or {}).get('kind') == 'event'
                        and (node.get('content') or {}).get('title') == row.get('title') else 'natural')
                    text += '；' + _status(event_planning.event_eligibility(row['id'], event_context)['status'])
                lines.append(text)
        for row in dossier.get('history_observed_event_rows', []):
            lines.append('过去已读事件：' + _plain(row['title']))
    lines.append('可用下方入口定位到地图并查看节点内容。候选不是当前可发生全集；条件与实际通行情况仍需核对，不自动选路。')
    return lines


def _original_lines(entry):
    record = entry['record'].get('record', entry['record'])
    lines = [_plain(record.get('title')) or '未归类原文', '【已知内容】',
             _plain(record.get('description')) or '内容说明尚未确认。']
    if record.get('lockedCoverDesc'):
        lines.append('条件文字：' + _plain(record['lockedCoverDesc']))
    reference = record.get('special_entry_reference')
    if reference:
        lines.append('这份原文已有部分特殊入口资料；当前能否出现或进入仍未知。')
        if reference.get('label'):
            lines.append(_plain(reference['label']))
    else:
        lines.append('尚未找到完整来源入口；不能把它列为普通节点必然可发生的事件。')
    target_id = record.get('nextSceneId')
    if target_id:
        target = catalog._original()['scenes'].get(target_id)
        lines.append('原文注明的后续：' + (_plain(target.get('title')) if target else '名称未确认'))
        lines.append('明确后续不证明从哪里进入、实际能到达，或必定发生战斗。可用下方入口查看已绑定的后续资料。')
    lines.append('奖励、完整条件及实际选择结果：未知。完整原文和来源可在资料与依据中查看。')
    return lines


def node_information_text(entry, *, context=None, dossier=None, map_context=None):
    """Summarize one entry without changing any source or caller-owned state."""
    if not isinstance(entry, dict) or not isinstance(entry.get('record'), dict):
        return '尚未选择有足够资料的节点。可先选择事件、功能节点、作战或本图位置；资料不足不等于不可能出现。'
    historical, safe_context = _historical_context(entry, context)
    kind = entry.get('kind')
    if kind == 'map' and map_context and len(map_context) > 3 and map_context[3]:
        historical = True
        safe_context = {key: safe_context[key] for key in ('floor', 'difficulty', 'special_region', 'node_type') if key in safe_context}
    try:
        if kind == 'event':
            lines = _event_lines(entry, safe_context)
        elif kind == 'function':
            lines = _function_lines(entry['record'], safe_context)
        elif kind == 'battle':
            lines = _battle_lines(entry['record'])
        elif kind == 'map':
            lines = _map_lines(entry, dossier, map_context, safe_context)
        elif kind == 'original':
            lines = _original_lines(entry)
        else:
            lines = ['这类内容的玩家说明尚未整理；请查看资料与依据，不能据此判断没有事件或奖励。']
    except (ValueError, TypeError, KeyError):
        lines = ['资料暂时无法整理；当前条件、奖励和后续均不能据此确认。请查看资料与依据中的具体原因。']
    if historical and kind != 'event':
        lines.insert(0, '历史资料；不代表当前节点状态，也不使用当前资源推定当时结果。')
    return '\n'.join(line for line in lines if line is not None)
