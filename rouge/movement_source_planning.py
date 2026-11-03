"""Movement-part shopping lists reviewed against declared map source opportunities."""
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path
from . import duel_reward_planning as parts, event_planning

DATA = Path(__file__).with_name('data')
SOURCE_LABELS = {'explicit_source_flag': '条目明确来源标志', 'documented_shop_scope': '商店一般文档范围',
    'documented_not_sold': '文档明确不在两商店出售', 'seed_class_mismatch': '种子已列类别不符',
    'source_flag_absent_unknown': '本来源未列·资格待证'}
STATUS = {'matched': '已列条件相符', 'unknown': '条件待证', 'excluded': '已列条件不符', 'history_only': '历史类型参考'}


@lru_cache(maxsize=1)
def reference_data():
    return json.loads((DATA/'movement-source-reference.json').read_text(encoding='utf8'))


def _data():
    data = reference_data()
    for filename, key in (('duel-reward-reference.json', 'part_reference_sha256'), ('node-catalog.json', 'catalogue_sha256')):
        if sha256((DATA/filename).read_bytes()).hexdigest() != data[key]:
            raise ValueError('加工品原目录、来源卡片或独立事件目录变化，需重新绑定获取清单。')
    parts._data()
    return data


def _boolean(value, label):
    if value is not None and type(value) is not bool:
        raise ValueError(label + '需要布尔声明或未知。')


def _declaration(declaration, data):
    if declaration is None:
        return {}
    fields = {'access_declared', 'stock_item_ids', 'stock_complete', 'stock_presence', 'unmodified_price_scenario',
        'declared_prices', 'gold_declared', 'victory_declared', 'transition_completed', 'cultivation_completed', 'seed_presence'}
    if not isinstance(declaration, dict) or set(declaration) - fields:
        raise ValueError('来源情形声明含未支持字段。')
    for key in ('access_declared', 'stock_complete', 'unmodified_price_scenario', 'victory_declared',
            'transition_completed', 'cultivation_completed', 'seed_presence'):
        _boolean(declaration.get(key), key)
    ids = declaration.get('stock_item_ids', [])
    if not isinstance(ids, list) or any(not isinstance(k, str) or not k for k in ids) or len(ids) != len(set(ids)):
        raise ValueError('当前陈列ID声明需要不重复的非空文字列表。')
    presence = declaration.get('stock_presence', {})
    prices = declaration.get('declared_prices', {})
    if not isinstance(presence, dict) or any(k not in data['items'] or v is not None and type(v) is not bool for k, v in presence.items()):
        raise ValueError('目标加工品陈列状态需要明确原ID到布尔或未知。')
    if not isinstance(prices, dict) or any(k not in data['items'] or type(v) is not int or v < 0 for k, v in prices.items()):
        raise ValueError('目标报价声明需要明确原ID到非负整数。')
    gold = declaration.get('gold_declared')
    if gold is not None and (type(gold) is not int or gold < 0):
        raise ValueError('来源预算的金币声明需要非负整数或未知。')
    for key, value in presence.items():
        if key in ids and value is False or declaration.get('stock_complete') is True and key not in ids and value is True:
            raise ValueError('目标陈列状态与明确的陈列清单/完整度声明矛盾。')
    return deepcopy(declaration)


def _status(values):
    return 'excluded' if False in values else 'unknown' if None in values else 'matched'


def _membership(item, channel):
    rule = channel['membership_rule']
    flags = item['documented_source_flags']
    if rule == 'shop':
        return (False, 'documented_not_sold') if flags['nosell'] else (True, 'documented_shop_scope')
    if flags[rule]:
        return True, 'explicit_source_flag'
    if rule == 'seedreward' and item['documented_grade'] == 0 and item['item']['name'] != '小八界':
        return False, 'seed_class_mismatch'
    return None, 'source_flag_absent_unknown'


def movement_source(item_id, channel_id, context=None, declaration=None, *, historical=False):
    return _movement_source(_data(), item_id, channel_id, context, declaration, historical=historical)


def _movement_source(data, item_id, channel_id, context=None, declaration=None, *, historical=False):
    if not isinstance(item_id, str) or item_id not in data['items']:
        raise ValueError('获取目标需要12项固定加工品中的明确原ID；不能按名称或后缀猜来源。')
    if not isinstance(channel_id, str) or channel_id not in data['channels']:
        raise ValueError('获取渠道不在已核验的文档范围。')
    if type(historical) is not bool:
        raise ValueError('历史引用标志需要布尔值。')
    context = event_planning._context(context)
    declaration = _declaration(declaration, data)
    if historical:
        context = {key: deepcopy(value) for key, value in context.items()
            if key in ('floor', 'difficulty', 'special_region', 'node_type', 'original_node_type')}
        declaration = {}
    item = data['items'][item_id]
    channel = data['channels'][channel_id]
    membership, membership_source = _membership(item, channel)
    original_type = context.get('original_node_type')
    label = context.get('node_type')
    if original_type is not None and original_type not in data['node_types']:
        raise ValueError('节点原类型需要固定原枚举。')
    if original_type is not None and label is not None and data['node_types'][original_type]['name'] != label:
        raise ValueError('节点原枚举与显示类型声明矛盾，不能任选一个覆盖。')
    names = {data['node_types'][key]['name'] for key in channel['original_node_types']}
    type_match = original_type in channel['original_node_types'] if original_type is not None else None if label is None else label in names
    checks = [{'kind': 'source_membership', 'matches': membership,
        'text': SOURCE_LABELS[membership_source] + '；来源范围不等于当前实际随机池。'},
        {'kind': 'node_type', 'matches': type_match,
            'text': '核对独立原节点类型；目录类型不证明当前已经出现或可达。'},
        {'kind': 'access_declaration', 'matches': declaration.get('access_declared'),
            'text': '方案声明的入口可达状态；本功能不计算实际连接、占领、AP或最优路线。'}]
    stock = price = budget = None
    price_source = 'unknown'
    gold = declaration.get('gold_declared')
    if gold is None:
        gold = context.get('gold', context.get('resources', {}).get('gold'))
    if channel['membership_rule'] == 'shop':
        stock = declaration.get('stock_presence', {}).get(item_id)
        if stock is None and item_id in declaration.get('stock_item_ids', []):
            stock = True
        elif stock is None and declaration.get('stock_complete') is True:
            stock = False
        prices = declaration.get('declared_prices', {})
        if item_id in prices:
            price = prices[item_id]
            price_source = 'independent_declared_price'
            if declaration.get('unmodified_price_scenario') is True and item['documented_card_price'] != price:
                raise ValueError('无修正文档售价情形与独立报价声明矛盾。')
        elif declaration.get('unmodified_price_scenario') is True:
            price = item['documented_card_price']
            price_source = 'documented_unmodified_card_price' if price is not None else 'documented_price_absent'
        budget = None if gold is None or price is None else gold >= price
        checks += [{'kind': 'current_stock', 'matches': stock,
                'text': '当前加工品陈列按独立声明核对；未读到不当作不存在。'},
            {'kind': 'nominal_budget', 'matches': budget,
                'text': '只比较声明金币与独立报价/明确无修正文档售价；实际费用及购买资格未知。'}]
    elif channel['completion_field']:
        completion = declaration.get(channel['completion_field'])
        checks.append({'kind': channel['completion_field'], 'matches': completion,
            'text': '文档奖励需要对应的离层、培育完成或通关条件；这里只核对方案声明。'})
        if channel_id == 'seed':
            seed_presence = declaration.get('seed_presence')
            if seed_presence is None:
                seed_presence = event_planning._owned(context, data['seed_item_id'])
            checks.append({'kind': 'seed_owned', 'matches': seed_presence,
                'text': '培育需要种子持有参考；持有布尔不换算件数、不预扣。'})
    if historical:
        checks.append({'kind': 'historical_reference_only', 'matches': False,
            'text': '过去类型仅作历史来源参考，不当作当前可获取入口。'})
    return {'item_id': item_id, 'name': item['item']['name'], 'item': deepcopy(item),
        'channel_id': channel_id, 'channel': deepcopy(channel), 'historical_reference': historical,
        'source_membership_matches': membership, 'source_membership_reference': membership_source,
        'checks': checks, 'status': 'history_only' if historical else _status([c['matches'] for c in checks]),
        'context': deepcopy(context), 'declaration': declaration,
        'stock_presence_declared': stock, 'documented_card_price': item['documented_card_price'],
        'original_base_sell_price': item['original_base_sell_price'],
        'comparison_price_reference': price, 'comparison_price_source': price_source,
        'gold_declared': gold, 'nominal_budget_covers': budget,
        'quantity_reference': channel['quantity_reference'], 'actual_source_pool_member': None,
        'actual_current_stock': None, 'actual_price': None, 'actual_node_reachable': None,
        'actual_reward_quantity': None, 'actual_received': None, 'actual_server_eligible': None,
        'complete_server_reward_pool_known': False, 'inventory_updated': False,
        'source_origin_scene_verified': False, 'generation_probability': None,
        'sources': deepcopy(data['sources']), 'limits': list(data['limits'])}


def _graph_nodes(graph, data):
    if not isinstance(graph, dict) or not isinstance(graph.get('nodes'), list) or len(graph['nodes']) > 200:
        raise ValueError('获取清单地图需要最多200项的声明节点列表。')
    nodes = {}
    positions = set()
    for node in graph['nodes']:
        if not isinstance(node, dict) or not isinstance(node.get('id'), str) or not node['id']:
            raise ValueError('来源节点需要非空文字ID。')
        if any(type(node.get(key)) is not int or node[key] < 0 for key in ('row', 'col')):
            raise ValueError('来源节点行列需要非负整数。')
        position = node['row'], node['col']
        if node['id'] in nodes or position in positions:
            raise ValueError('来源节点ID或位置重复。')
        for key in ('base_node_type', 'node_type_raw'):
            if node.get(key) is not None and (not isinstance(node[key], str) or node[key] not in data['node_types']):
                raise ValueError('原节点类型不在固定原枚举中。')
        if node.get('base_node_type') and node.get('node_type_raw') and node['base_node_type'] != node['node_type_raw']:
            raise ValueError('两个原类型声明矛盾。')
        for key in ('observed_type', 'remembered_type'):
            if node.get(key) is not None and (not isinstance(node[key], str) or not node[key]):
                raise ValueError('当前/过去类型需要非空文字或未知。')
        _declaration(node.get('acquisition_declaration'), data)
        nodes[node['id']] = deepcopy(node)
        positions.add(position)
    return nodes


def source_review(target_item_ids, graph=None, context=None, declarations_by_node=None, *, epoch=None):
    """Review every selected item at all declared source nodes without ranking rates."""
    data = _data()
    if not isinstance(target_item_ids, list) or any(not isinstance(k, str) or k not in data['items'] for k in target_item_ids) or len(target_item_ids) != len(set(target_item_ids)):
        raise ValueError('获取清单需要不重复的固定加工品原ID列表。')
    context = event_planning._context(context)
    nodes = None if graph is None else _graph_nodes(graph, data)
    allowed = set(nodes) if nodes is not None else {'directory:' + key for key in data['channels']}
    declarations_by_node = {} if declarations_by_node is None else declarations_by_node
    if not isinstance(declarations_by_node, dict) or set(declarations_by_node) - allowed:
        raise ValueError('来源情形声明必须绑定当前声明图节点或对应独立目录渠道。')
    for declaration in declarations_by_node.values():
        _declaration(declaration, data)
    rows = []
    channels = data['channels']
    labels = {row['name'] for row in data['node_types'].values()}
    opportunities = []
    if nodes is None:
        for channel in channels:
            opportunities.append({'channel_id': channel, 'source_key': 'directory:' + channel,
                'node': None, 'historical': False, 'original_type': None, 'label': None})
    else:
        for key, node in nodes.items():
            current = node.get('observed_type')
            raw = node.get('base_node_type') or node.get('node_type_raw')
            if current in labels:
                types = [kind for kind, row in data['node_types'].items() if row['name'] == current]
                original = types[0] if len(types) == 1 else None
                basis = 'declared_current_display_type'
            elif raw:
                types, original = [raw], raw
                current = data['node_types'][raw]['name']
                basis = 'declared_original_type_only'
            else:
                types, original, current = [], None, None
                basis = 'current_type_unknown'
            for channel, definition in channels.items():
                if not types or set(types).intersection(definition['original_node_types']):
                    opportunities.append({'channel_id': channel, 'source_key': key, 'node': node,
                        'historical': False, 'original_type': original, 'label': current, 'type_basis': basis})
            previous = node.get('remembered_type')
            if previous and previous != current:
                historical_types = {kind for kind, row in data['node_types'].items() if row['name'] == previous}
                for channel, definition in channels.items():
                    if historical_types.intersection(definition['original_node_types']):
                        opportunities.append({'channel_id': channel, 'source_key': key, 'node': node,
                            'historical': True, 'original_type': next(iter(historical_types)) if len(historical_types) == 1 else None,
                            'label': previous, 'type_basis': 'historical_type_reference'})
    for item_id in target_item_ids:
        for opportunity in opportunities:
            node = opportunity['node']
            row_context = ({key: deepcopy(context[key]) for key in ('floor', 'difficulty', 'special_region')
                if key in context} if opportunity['historical'] else deepcopy(context))
            if node is not None:
                row_context.update(node_type=opportunity['label'], original_node_type=opportunity['original_type'])
            declaration = {} if opportunity['historical'] else {**((node or {}).get('acquisition_declaration') or {}),
                **declarations_by_node.get(opportunity['source_key'], {})}
            result = _movement_source(data, item_id, opportunity['channel_id'], row_context, declaration,
                historical=opportunity['historical'])
            binding = {'node_id': node['id'], 'row': node['row'], 'col': node['col'],
                'zone_id': graph.get('zone_id'), 'template_id': graph.get('template_id'), 'epoch': epoch} if node else None
            result.update(source_key=opportunity['source_key'], node_id=node['id'] if node else None,
                position=binding, identity_basis=opportunity.get('type_basis', 'independent_directory_source_reference'),
                review_key=[item_id, opportunity['source_key'], opportunity['channel_id'], opportunity['historical']])
            rows.append(result)
    targets = []
    for item_id in target_item_ids:
        matches = [row for row in rows if row['item_id'] == item_id]
        targets.append({'item_id': item_id, 'name': data['items'][item_id]['item']['name'],
            'owned_quantity_declared': context.get('item_quantities', {}).get(item_id),
            'owned_presence_declared': event_planning._owned(context, item_id),
            'matched_source_rows': sum(r['status'] == 'matched' for r in matches),
            'unknown_source_rows': sum(r['status'] == 'unknown' for r in matches),
            'excluded_source_rows': sum(r['status'] == 'excluded' for r in matches),
            'historical_source_rows': sum(r['status'] == 'history_only' for r in matches),
            'actual_acquisition_plan_complete': False, 'current_holdings_do_not_cancel_target': True})
    return {'rows': rows, 'targets': targets, 'target_item_ids': list(target_item_ids),
        'graph_bound': graph is not None, 'epoch': epoch, 'context': deepcopy(context),
        'actual_node_reachability_known': False, 'source_totals_known': False,
        'actual_route_selected': None, 'actual_reward_total': None, 'complete_server_reward_pool_known': False,
        'generation_probability': None, 'inventory_updated': False, 'run_state_updated': False,
        'source_origin_gap_closed': False, 'coverage': deepcopy(data['coverage']),
        'sources': deepcopy(data['sources']), 'limits': list(data['limits'])}


def source_text(row, technical=False):
    if type(technical) is not bool:
        raise ValueError('来源字段开关需要布尔值。')
    lines = ['【加工品获取来源审查】', row['name'] + ' · ' + row['channel']['label'],
        '来源范围：' + SOURCE_LABELS[row['source_membership_reference']],
        '情形条件：' + STATUS[row['status']] + '；实际池成员、可达与领取未知。']
    position = row.get('position')
    if position:
        basis = '历史类型来源。' if row['historical_reference'] else '原类型声明参考，当前读取未证。' if row.get('identity_basis') == 'declared_original_type_only' else '当前类型声明参考。'
        lines.append(f"声明图位置：第{position['row']+1}行、第{position['col']+1}列；" + basis)
    else:
        lines.append('独立渠道目录参考，尚未绑定具体地图节点。')
    for check in row['checks']:
        state = '相符' if check['matches'] is True else '不符' if check['matches'] is False else '未知'
        lines.append(state + '：' + check['text'])
    if row['channel']['membership_rule'] == 'shop':
        lines += ['文档条目售价：' + (str(row['documented_card_price']) if row['documented_card_price'] is not None else '未列；不拿估价代替'),
            '原基础估价：' + str(row['original_base_sell_price']) + '源石锭；与条目售价分开。',
            '预算比较采用：' + (str(row['comparison_price_reference']) if row['comparison_price_reference'] is not None else '报价未确认') +
                '；声明金币：' + (str(row['gold_declared']) if row['gold_declared'] is not None else '未知'),
            '当前加工品陈列：' + ('声明有此项' if row['stock_presence_declared'] is True else '声明无此项' if row['stock_presence_declared'] is False else '未知；未见不视为不存在')]
    lines += ['入口获取原句：' + row['channel']['source_quote'],
        '入口文档：' + row['channel']['source_pinned_url']]
    amount = row['quantity_reference']
    lines.append('独立奖励数量参考：' + (str(amount) + '件加工品；需对应完成条件。' if amount is not None else '未列明；不按来源条目数或生成引用数凑实际数量。'))
    for reference in row['channel']['catalogue_refs']:
        lines.append('独立目录组：' + reference['title'] + '；同名入口分别保留，来源原场景链与当前实例仍未知。')
    rule = row['channel']['membership_rule']
    if rule != 'shop':
        lines.append('文档来源原句：' + row['item']['source_flag_definitions'][rule])
    elif row['item']['documented_source_flags']['nosell']:
        lines.append('文档排除原句：' + row['item']['source_flag_definitions']['nosell'])
    lines += ['来源标志：冻结PRTS卡片的明确标志；不是原游戏获取flags。',
        '来源文档：' + row['sources']['part_document']['pinned_url'], *row['limits']]
    if technical:
        lines += ['原目标ID：' + row['item_id'], '原节点类型：' + str(row['context'].get('original_node_type')),
            'PRTS原旗标：' + json.dumps(row['item']['documented_source_flags'], ensure_ascii=False),
            '原估价字段：$.modules.rogue_6.scrap.moveScrapData.' + row['item_id'] + '.sellPrice',
            '独立目录事件ID：' + '、'.join(r['event_id'] for r in row['channel']['catalogue_refs'])]
    return '\n'.join(lines)
