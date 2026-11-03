"""Declared additional summons, currency and inventories; no deployment commands."""
from copy import deepcopy
from .token_module_comparison import compare_token_module
from .catalog import operator_attributes


def count(value, label, *, unknown=False, maximum=100):
    if unknown and value is None: return None
    if type(value) is not int or not 0 <= value <= maximum:
        raise ValueError(f'{label}需要0–{maximum}的整数。')
    return value


def token_budget(operator, training, requests, budget):
    count(budget, '费用预算', maximum=9999)
    # Validate the complete current equipment before consuming a reference.
    operator_attributes(operator, **{k:v for k,v in training.items() if k in
        ('elite','level','trust','potential','module_id','module_level')})
    comparison = compare_token_module(operator, training, training.get('module_id'))
    identities = {t['token_id'] for t in comparison['tokens']}
    if not isinstance(requests, dict) or set(requests) != identities:
        raise ValueError('请逐项提供当前干员全部召唤物的配额条件。')
    stage = training.get('module_level', 0) if training.get('module_id') else 0
    rows = []; subtotal = 0; all_costs_known = True
    for token in comparison['tokens']:
        request = requests[token['token_id']]
        if not isinstance(request, dict) or set(request) != {'additional', 'present', 'available_stock'}:
            raise ValueError('每项需要additional、present、available_stock。')
        additional = count(request['additional'], '新增数量')
        present = count(request['present'], '声明在场数量', unknown=True)
        stock = count(request['available_stock'], '声明剩余库存', unknown=True)
        values = token['stages'][stage]['values']
        count_reference=token['stages'][stage].get('count_reference')
        cost = values['deployment_cost']; cap = values['concurrent_limit']
        requested_cost = 0 if additional == 0 else cost * additional if cost is not None else None
        all_costs_known = all_costs_known and requested_cost is not None
        if requested_cost is not None: subtotal += requested_cost
        rows.append({'token_id': token['token_id'], 'name': token['name'], **deepcopy(request),
            'cost_reference': cost, 'requested_cost_reference': requested_cost,
            'held_limit_reference': values['held_limit'], 'concurrent_limit_reference': cap,
            'stock_within_reference': stock<=values['held_limit'] if stock is not None and values['held_limit'] is not None else None,
            'counted_present_scope':'ordinary_token_card_spawns' if count_reference else 'existing_verified_reference',
            'count_reference':deepcopy(count_reference),
            'stock_sufficient_declared': stock >= additional if stock is not None else None,
            'concurrent_within_reference': present + additional <= cap if present is not None and cap is not None else None,
            'source': deepcopy(token['stages'][stage]['source']), 'actual_deployable': None})
    total = subtotal if all_costs_known else None
    return {'operator': operator, 'operator_name': comparison['operator_name'], 'training': deepcopy(training),
        'budget': budget, 'rows': rows, 'known_cost_subtotal': subtotal, 'total_cost_reference': total,
        'budget_sufficient_reference': budget >= total if total is not None else None,
        'remaining_budget_reference': budget - total if total is not None else None,
        'notes': ['只按当前培养及已核验的独立实体费用计算一次新增；不推算退场返费、再部署涨费或技能免费创建。',
                  '在场和剩余库存由用户声明，未知可留空；库存上限不等于当前剩余库存。',
                  '每类在场限制仅使用已核验参考，不推算全局部署位、地块或单位实际在场。',
                  '库存越界仅表示超过默认培养参考；当前技能、热更新或自动生成的库存/数量仍须单独核验。',
                  '已计费用小计不包含未知费用；满足预算和数量参考仍不证明实际可部署。',
                  '所选模组未核验的字段保持未知；此表不改写账号、本局或原伤害。']+
                  (['望的声明在场只填写计入默认手动棋子限制的数量；自动额外棋子和技能期间修改未加入限额，不能与手动数量混算。']
                   if operator=='char_2027_wang' else [])}


def format_token_budget(result):
    def value(v): return '未知' if v is None else str(v)
    lines = [result['operator_name'] + ' · 召唤物局外配额', '培养：' + str(result['training']),
             f"预算{result['budget']}；已计费用{result['known_cost_subtotal']}；总费用{value(result['total_cost_reference'])}；余额{value(result['remaining_budget_reference'])}"]
    for row in result['rows']:
        lines.append(f"{row['name']}：新增{row['additional']}、声明在场{value(row['present'])}、剩余库存{value(row['available_stock'])}；"
                     f"每个费用{value(row['cost_reference'])}、本项费用{value(row['requested_cost_reference'])}、库存上限{value(row['held_limit_reference'])}、每类在场上限{value(row['concurrent_limit_reference'])}")
    return '\n'.join([*lines,*result['notes']])
