"""Independent declared Wang inventory, manual units and extra projectiles.

Only explicit receipts change a pool. Reference parameters do not schedule a
cast, manufacture an extra projectile, discard overflow or invent a refund.
"""
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path

from .catalog import catalog, operator_attributes
from .summons import token_attributes
from .token_counts import token_count_reference


OPERATOR = 'char_2027_wang'
TOKEN = 'token_10064_wang_stone1'
POOLS = ('stock', 'manual_active', 'extra_active', 'currency', 'sp')
POOL_LABELS = {'stock': '卡片库存', 'manual_active': '手动棋子',
               'extra_active': '活跃跟子弹道', 'currency': '费用', 'sp': '技力'}
LIMITS = {'stock': 100, 'manual_active': 100, 'extra_active': 100,
          'currency': 9999, 'sp': 9999}


@lru_cache(maxsize=1)
def source_data():
    return json.loads((Path(__file__).parent / 'data' / 'p2-wang-resource-source.json')
                      .read_text(encoding='utf-8'))


def _amount(value, label, maximum, *, unknown=True):
    if unknown and value is None:
        return None
    if type(value) is not int or not 0 <= value <= maximum:
        raise ValueError(f'{label}需要0–{maximum}整数，未知可用null。')
    return value


def _name(value, label):
    if (type(value) is not str or not 1 <= len(value) <= 60 or
            any(ord(c) < 32 or 0xd800 <= ord(c) <= 0xdfff for c in value)):
        raise ValueError(f'{label}需要1–60字符的名称。')
    return value


def _snapshot(value):
    if type(value) is not dict or set(value) != {'snapshot_id', *POOLS}:
        raise ValueError('独立快照需snapshot_id及stock/manual_active/extra_active/currency/sp。')
    return {'snapshot_id': _name(value['snapshot_id'], '快照名称'),
            **{key: _amount(value[key], POOL_LABELS[key], LIMITS[key]) for key in POOLS}}


def wang_resource_reference(training, skill=1, rank=1):
    if type(training) is not dict:
        raise ValueError('培养条件需要对象。')
    allowed = {'elite', 'level', 'trust', 'potential', 'module_id', 'module_level'}
    if set(training) - allowed:
        raise ValueError('仅接受精英、等级、信赖、潜能及模组培养条件。')
    conditions = {'elite': 2, 'level': None, 'trust': 100, 'potential': 1,
                  'module_id': None, 'module_level': 0, **deepcopy(training)}
    if (type(conditions['module_level']) is not int or
            (conditions['module_id'] is None and conditions['module_level'] != 0)):
        raise ValueError('无模组须使用module_level=0；模组阶段需要整数。')
    if conditions['module_id'] is not None and (type(conditions['module_id']) is not str
                                               or not conditions['module_id']):
        raise ValueError('模组身份需要非空字符串或null。')
    if type(conditions['trust']) not in (int, float):
        raise ValueError('信赖需要0–100的数值。')
    operator_attributes(OPERATOR, **conditions)
    profile = catalog()['operators'][OPERATOR]
    if conditions['level'] is None:
        conditions['level'] = profile['phases'][conditions['elite']]['max_level']
    if type(skill) is not int or skill not in (1, 2):
        raise ValueError('当前账本仅支持S1/S2；S3弹药和返还尚未闭合。')
    _amount(rank, '技能等级', 10, unknown=False)
    if rank == 0:
        raise ValueError('技能等级需要1–10。')
    if profile['skills'][skill - 1]['unlock_elite'] > conditions['elite']:
        raise ValueError('当前精英阶段尚未开放该技能。')
    if rank > 7 and conditions['elite'] < 2:
        raise ValueError('当前精英阶段不能采用专精参考。')
    data = source_data()
    eligible = [entry for entry in data['talent_candidates']
                if int(entry['raw']['unlockCondition']['phase'][-1]) <= conditions['elite']
                and (int(entry['raw']['unlockCondition']['phase'][-1]) < conditions['elite']
                     or entry['raw']['unlockCondition']['level'] <= conditions['level'])
                and entry['raw']['requiredPotentialRank'] <= conditions['potential'] - 1]
    talent = eligible[-1]
    extra_parameter = int(next(item['value'] for item in talent['raw']['blackboard']
                               if item['key'] == 'attack@max_spawn_cnt'))
    selected = data['skills'][skill - 1]
    if selected['skill_id'] != profile['skills'][skill - 1]['id']:
        raise ValueError('当前技能身份与固定来源不一致。')
    level = selected['levels'][rank - 1]
    grant = int(next(item['value'] for item in level['raw']['blackboard'] if item['key'] == 'cnt'))
    scenario = {'operator': OPERATOR, **conditions}
    counts = token_count_reference(profile, scenario, TOKEN)
    attributes = token_attributes(profile, scenario, TOKEN)
    # Existing compiled proof covers token-card counts. A module parameter
    # elsewhere never proves the complete projectile pool's modified cap.
    extra_limit = None if counts['module_applied'] else extra_parameter
    return {'training': conditions, 'skill': skill, 'rank': rank,
            'skill_name': level['raw']['name'], 'nominal_stock_grant': grant,
            'sp_cost_parameter': level['raw']['spData']['spCost'],
            'manual_limit_reference': counts['concurrent_limit'],
            'stock_limit_reference': counts['held_limit'],
            'base_extra_limit_parameter': extra_parameter,
            'extra_limit_reference': extra_limit,
            'manual_cost_reference': attributes['deployment_cost'],
            'module_applied': counts['module_applied'],
            'count_reference': deepcopy(counts),
            'talent_source': deepcopy(talent), 'skill_source': deepcopy(level),
            'source_commit': data['source_commit'], 'sources': deepcopy(data['sources']),
            'separate_entity_evidence': deepcopy(data['separate_entity_evidence']),
            'actual_presence': None, 'actual_stock': None, 'actual_creation_seconds': None,
            'current_hotfix_verified': False}


def _checks(state, reference):
    limits = {'stock': reference['stock_limit_reference'],
              'manual_active': reference['manual_limit_reference'],
              'extra_active': reference['extra_limit_reference']}
    return {key: state[key] <= maximum if state[key] is not None and maximum is not None else None
            for key, maximum in limits.items()}


def _receipt(step, reference):
    kind = step['kind']
    if kind == 'manual_receipt':
        expected = {'id', 'kind', 'stock_spent', 'manual_created', 'extra_created',
                    'currency_spent', 'sp_spent'}
        mapping = {'stock': ('stock_spent', -1), 'manual_active': ('manual_created', 1),
                   'extra_active': ('extra_created', 1), 'currency': ('currency_spent', -1),
                   'sp': ('sp_spent', -1)}
        maxima = {'manual_created': 1, 'extra_created': 1}
    elif kind == 'skill_receipt':
        expected = {'id', 'kind', 'accepted_stock', 'sp_spent'}
        mapping = {'stock': ('accepted_stock', 1), 'sp': ('sp_spent', -1)}
        maxima = {'accepted_stock': reference['nominal_stock_grant']}
    elif kind == 'loss_receipt':
        expected = {'id', 'kind', 'manual_lost', 'extra_lost', 'stock_returned',
                    'currency_returned', 'sp_returned'}
        mapping = {'stock': ('stock_returned', 1), 'manual_active': ('manual_lost', -1),
                   'extra_active': ('extra_lost', -1), 'currency': ('currency_returned', 1),
                   'sp': ('sp_returned', 1)}
        maxima = {}
    else:
        raise ValueError('步骤kind需manual_receipt/skill_receipt/loss_receipt/snapshot。')
    if set(step) != expected:
        raise ValueError(f'{kind}字段不完整或含未支持字段。')
    values = {key: _amount(step[key], key, maxima.get(key, 9999)) for key in expected - {'id', 'kind'}}
    return {pool: (None if values[key] is None else sign * values[key])
            for pool, (key, sign) in mapping.items()}


def wang_resource_ledger(training, preview, *, skill=1, rank=1):
    """Validate independent receipts and keep unknown pools until a new snapshot."""
    reference = wang_resource_reference(training, skill, rank)
    if type(preview) is not dict or set(preview) != {'initial', 'steps'}:
        raise ValueError('需要initial独立快照和steps声明序列。')
    initial = _snapshot(preview['initial'])
    if type(preview['steps']) is not list or len(preview['steps']) > 60:
        raise ValueError('声明序列需0–60项。')
    state = {key: initial[key] for key in POOLS}
    segment = initial['snapshot_id']
    snapshot_names = {segment}; step_names = set(); rows = []; stopped = False
    for ordinal, step in enumerate(preview['steps'], 1):
        if type(step) is not dict or 'id' not in step or 'kind' not in step:
            raise ValueError('每步需对象、id和kind。')
        identity = _name(step['id'], '步骤名称')
        if identity in step_names:
            raise ValueError('步骤名称不能重复。')
        step_names.add(identity)
        if step['kind'] == 'snapshot':
            if set(step) != {'id', 'kind', 'state'}:
                raise ValueError('snapshot需id/kind/state。')
            observation = _snapshot(step['state'])
            if observation['snapshot_id'] in snapshot_names:
                raise ValueError('恢复链必须提供新的、唯一命名独立快照。')
            snapshot_names.add(observation['snapshot_id'])
            segment = observation['snapshot_id']
            state = {key: observation[key] for key in POOLS}; stopped = False
            rows.append({'ordinal': ordinal, 'id': identity, 'kind': 'snapshot',
                         'segment_id': segment, 'before': None, 'deltas': None,
                         'after': deepcopy(state), 'status': 'independent_snapshot',
                         'contradictions': [], 'within_reference': _checks(state, reference),
                         'declaration': deepcopy(step), 'actual_clock': None})
            continue
        deltas = _receipt(step, reference)
        before = deepcopy(state)
        candidate = {key: (None if state[key] is None or deltas.get(key, 0) is None
                           else state[key] + deltas.get(key, 0)) for key in POOLS}
        contradictions = [key for key in POOLS if candidate[key] is not None and candidate[key] < 0]
        if stopped:
            after = {key: None for key in POOLS}; status = 'blocked_after_contradiction'
            contradictions = []
        elif contradictions:
            after = {key: None for key in POOLS}; status = 'contradicted_declaration'; stopped = True
        else:
            after = candidate
            status = 'partial_unknown' if any(value is None for value in after.values()) else 'declared_balance'
        state = after
        row = {'ordinal': ordinal, 'id': identity, 'kind': step['kind'],
               'segment_id': segment, 'before': before, 'deltas': deltas,
               'after': deepcopy(state), 'status': status, 'contradictions': contradictions,
               'within_reference': _checks(state, reference),
               'declaration': deepcopy(step), 'actual_clock': None}
        if step['kind'] == 'skill_receipt':
            row['nominal_stock_grant'] = reference['nominal_stock_grant']
            row['accepted_stock_declared'] = step['accepted_stock']
            row['nominal_sp_cost'] = reference['sp_cost_parameter']
            row['sp_spent_matches_parameter'] = (step['sp_spent'] == reference['sp_cost_parameter']
                                                  if step['sp_spent'] is not None else None)
        rows.append(row)
    return {'operator': OPERATOR, 'scope': 'offline_declared_receipts_separate_projectile_pool',
            'reference': reference, 'initial': initial,
            'initial_within_reference': _checks(initial, reference),
            'preview': deepcopy(preview), 'rows': rows, 'final': deepcopy(state),
            'final_segment_id': segment, 'chain_blocked': stopped,
            'actual_final': {key: None for key in POOLS},
            'notes': ['每步只是独立声明结果；顺序是账本顺序，没有实际创建、触发、消失或技力时钟。',
                      '卡片手动棋子与跟子弹道分池；两者总数不等于召唤物数量、角色占位或关卡部署位。',
                      '手动成功数、库存消耗、费用和技力支出各自声明；失败创建不自动推出退款或消耗。',
                      'S1/S2名义取得2枚，实际入库量需另行声明；满库不自动推出丢弃或接受数量。',
                      '损失和明确退款各自声明；未声明的返还保持未知，不能从离场推出库存恢复。',
                      '任一池未知只沿该池传播；负余额矛盾阻断整链，只有唯一命名的独立快照能恢复。',
                      '来源上限越界只表示超过所列普通培养参考；不否定尚未核验的技能、热更新或其它修改。',
                      '启用合法模组时完整跟子池上限未知，保留基础天赋参数；S3弹药和返还未接入。',
                      '费用与技力不会随时间自动增加；本工具不读取或写入本局、账号或游戏。']}


def format_wang_resource_ledger(result):
    def show(value):
        return '未知' if value is None else str(value)
    def pools(state):
        return '；'.join(POOL_LABELS[key] + ' ' + show(state[key]) for key in POOLS)
    reference = result['reference']
    lines = [f"望 · {reference['skill_name']} · 等级{reference['rank']} · 分池声明资源账本",
             '培养参考：' + format_wang_training(reference),
             '初始快照：' + result['initial']['snapshot_id'] + '；' + pools(result['initial']),
             f"普通库存上限{reference['stock_limit_reference']}；手动棋子上限{reference['manual_limit_reference']}；"
             f"跟子基础上限参数{reference['base_extra_limit_parameter']}；当前完整上限参考{show(reference['extra_limit_reference'])}",
             f"技能名义取得{reference['nominal_stock_grant']}枚；名义技力消耗{reference['sp_cost_parameter']}；"
             f"单枚手动棋子费用参考{reference['manual_cost_reference']}（不自动扣款）"]
    initial_outside = [POOL_LABELS[key] for key, value in result['initial_within_reference'].items() if value is False]
    if initial_outside:
        lines.append('初始快照超过普通来源参考：' + '、'.join(initial_outside))
    for row in result['rows']:
        labels = {'independent_snapshot': '新的独立快照', 'declared_balance': '声明余额',
                  'partial_unknown': '部分池未知', 'contradicted_declaration': '声明出现负余额，链已阻断',
                  'blocked_after_contradiction': '前链矛盾，等待独立快照'}
        lines.append(f"{row['ordinal']}. {row['id']} [{row['segment_id']}] {labels[row['status']]}：" + pools(row['after']))
        if row['contradictions']:
            lines.append('矛盾池：' + '、'.join(POOL_LABELS[key] for key in row['contradictions']))
        outside = [POOL_LABELS[key] for key, value in row['within_reference'].items() if value is False]
        if outside:
            lines.append('超过普通来源参考：' + '、'.join(outside))
        if row['kind'] == 'skill_receipt':
            lines.append(f"名义取得{row['nominal_stock_grant']}；声明实际入库{show(row['accepted_stock_declared'])}；"
                         f"声明技力支出{show(row['declaration']['sp_spent'])}。")
    lines.append('最终独立快照段：' + result['final_segment_id'] + '；' + pools(result['final']))
    lines.extend(result['notes'])
    return '\n'.join(lines)


def format_wang_training(reference):
    training = reference['training']
    module = next((entry for entry in catalog()['operators'][OPERATOR]['modules']
                   if entry['id'] == training['module_id']), None)
    equipment = (f"{module['name']} {training['module_level']}阶段"
                 + ('（已满足解锁门）' if reference['module_applied'] else '（未满足解锁门）')
                 if module else '无模组')
    return (f"精英{training['elite']} · 等级{training['level']} · 潜能{training['potential']} · "
            f"信赖加成进度{training['trust']}% · {equipment}")
