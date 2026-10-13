"""Six explicit token table endpoints and their direct equipment additions.

No host-to-token level selection, interpolation, hidden talent or skill phase
is inferred. The caller selects the token's source phase and endpoint.
"""
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path

from .catalog import operator_attributes


FIELDS = {'hp': ('maxHp', 'max_hp'), 'attack': ('atk', 'atk'),
          'defense': ('def', 'def'), 'resistance': ('magicResistance', 'magic_resistance'),
          'deployment_cost': ('cost', 'cost'), 'attack_speed': ('attackSpeed', 'attack_speed'),
          'base_interval': ('baseAttackTime', 'base_attack_time'), 'block': ('blockCnt', 'block_cnt')}
LABELS = {'hp': '生命', 'attack': '攻击', 'defense': '防御', 'resistance': '法抗',
          'deployment_cost': '单次费用', 'attack_speed': '官方攻速数值',
          'base_interval': '基础间隔参数', 'block': '阻挡参数'}


@lru_cache(maxsize=1)
def source_data():
    return json.loads((Path(__file__).parent / 'data' / 'p2-supplemental-token-module-source.json')
                      .read_text(encoding='utf-8'))


def supported_operators():
    return {identity: source['owner_name'] for identity, source in source_data()['operators'].items()}


def compare_supplemental_token_modules(operator, training, selection):
    data = source_data()
    if type(operator) is not str or operator not in data['operators']:
        raise ValueError('当前补充召唤物模组范围仅含令与麦哲伦。')
    if type(training) is not dict or set(training) - {'elite', 'level', 'trust', 'potential', 'module_id', 'module_level'}:
        raise ValueError('宿主培养仅接受精英、等级、信赖、潜能和模组字段。')
    conditions = {'elite': 2, 'level': None, 'trust': 100, 'potential': 1,
                  'module_id': None, 'module_level': 0, **deepcopy(training)}
    if type(conditions['trust']) not in (int, float):
        raise ValueError('信赖需要数值。')
    if (type(conditions['module_level']) is not int or
            (conditions['module_id'] is None and conditions['module_level'] != 0)):
        raise ValueError('无模组须使用阶段0；模组阶段需要整数。')
    if conditions['module_id'] is not None and (type(conditions['module_id']) is not str or not conditions['module_id']):
        raise ValueError('宿主模组身份需要有效文字或null。')
    # This validates the captured host proposal; none of its stats enter a token.
    operator_attributes(operator, **conditions)
    source = data['operators'][operator]
    if conditions['level'] is None:
        conditions['level'] = source['owner_phases_raw'][conditions['elite']]['maxLevel']
    if type(selection) is not dict or set(selection) != {'token_elite', 'endpoint'}:
        raise ValueError('请显式选择独立实体token_elite资料阶段及endpoint端点。')
    token_elite = selection['token_elite']; endpoint = selection['endpoint']
    if type(token_elite) is not int or not 0 <= token_elite <= 2:
        raise ValueError('独立实体资料阶段需要0、1或2。')
    if endpoint not in ('first', 'last') or type(endpoint) is not str:
        raise ValueError('端点需first（1级）或last（该阶段满级）；不插值。')
    module = source['module_raw']; unlock_elite = int(module['unlockEvolvePhase'][-1])
    module_qualified = conditions['elite'] >= unlock_elite and conditions['level'] >= module['unlockLevel']
    variants = []
    for variant in source['variants']:
        identity = variant['token_id']; token = variant['token_raw']
        binding = variant['skill_binding_raw']
        if binding['overrideTokenKey'] != identity or source['display_token_dict_raw'].get(identity) is not True:
            raise ValueError('技能与独立实体来源绑定不完整。')
        skill_elite = int(binding['unlockCond']['phase'][-1])
        skill_qualified = (conditions['elite'] > skill_elite or
                           (conditions['elite'] == skill_elite and conditions['level'] >= binding['unlockCond']['level']))
        phase = token['phases'][token_elite]
        index = 0 if endpoint == 'first' else len(phase['attributesKeyFrames']) - 1
        frame = phase['attributesKeyFrames'][index]
        base = {field: frame['data'][raw_key] for field, (raw_key, _) in FIELDS.items()}
        stages = [{'module_level': 0, 'state': 'base_endpoint', 'values': deepcopy(base),
                   'direct_additions': {field: 0 for field in FIELDS},
                   'differences': {field: 0 for field in FIELDS}, 'stock_add_parameter': 0,
                   'source_selector': variant['token_selector'] + f'.phases[{token_elite}].attributesKeyFrames[{index}]',
                   'actual_values': dict.fromkeys(FIELDS), 'full_current_panel': None}]
        for number, record in enumerate(source['module_stage_records'], 1):
            pack = record['raw']['tokenAttributeBlackboard']
            if identity not in pack:
                raise ValueError('所列模组阶段缺少该独立实体直接属性记录。')
            additions = {row['key']: row['value'] for row in pack[identity]}
            direct = {field: additions.get(equip_key, 0) for field, (_, equip_key) in FIELDS.items()}
            qualified = module_qualified and skill_qualified
            # Only this complete direct ADD projection is calculated. Other
            # module parts may exist and never become a zero-effect claim.
            values = {field: base[field] + direct[field] if qualified else None for field in FIELDS}
            if qualified and values['deployment_cost'] < 0:
                raise ValueError('当前来源产生负费用，不能沿未核验的下限规则继续。')
            stages.append({'module_level': number, 'state': 'direct_addition_reference' if qualified else 'host_gate_unmet',
                           'values': values, 'direct_additions': direct,
                           'differences': deepcopy(direct) if qualified else dict.fromkeys(FIELDS),
                           'stock_add_parameter': additions.get('max_deck_stack_cnt'),
                           'source_selector': record['selector'] + '.tokenAttributeBlackboard.' + identity,
                           'actual_values': dict.fromkeys(FIELDS), 'full_current_panel': None})
        variants.append({'skill': variant['skill'], 'skill_id': binding['skillId'],
                         'skill_unlock_elite': skill_elite, 'skill_qualified': skill_qualified,
                         'token_id': identity, 'token_name': token['name'], 'position_parameter': token['position'],
                         'token_elite_declared': token_elite, 'token_level_endpoint': frame['level'],
                         'endpoint': endpoint, 'base_parameter_values': base, 'stages': stages,
                         'skill_source_selector': variant['skill_selector'],
                         'held_limit': None, 'concurrent_limit': None, 'actual_presence': None,
                         'actual_token_cultivation': None, 'actual_skill_boost': None,
                         'merged_token_values': None, 'full_damage': None, 'full_healing': None})
    return {'operator': operator, 'operator_name': source['owner_name'], 'host_training': conditions,
            'selection': deepcopy(selection), 'module_id': module['uniEquipId'], 'module_name': module['uniEquipName'],
            'module_unlock_elite': unlock_elite, 'module_unlock_level': module['unlockLevel'],
            'module_qualified': module_qualified, 'variants': variants,
            'scope': data['scope'], 'source_commit': data['source_commit'], 'sources': deepcopy(data['sources']),
            'generic_addition_evidence': deepcopy(data['generic_addition_evidence']),
            'public_documents': deepcopy(data['public_documents']),
            'notes': ['资料阶段与1级/满级端点由用户显式选择，不自动跟随宿主培养，不插值；端点是独立反事实参考。',
                      '宿主精英和等级只核技能及所列模组解锁门；本体信赖、潜能和装备白值不会流入独立实体。',
                      '模组列仅为原始培养端点加该实体的直接装备加值；未接入的技能、隐藏天赋或模组能力并非零效果。',
                      '单次费用、生命、攻击、防御与官方攻速加值分实体展示；基础间隔参数不等于当前实际攻击时钟。',
                      '库存原属性加值单列，完整库存和在场上限未知；不把原始基数或持有数量当实际部署数。',
                      '令S3只展示基础弦惊；合成大龙、技能强化、无人机生命周期和实际附着不外推。',
                      '当前完整实体面板、伤害和治疗保持未知；该窗口不操作游戏、不读取或写入本局。',
                      '沿用固定原始数据及已归档编译加法路径；当前热更新、真实实体培养和游戏面板尚未核验。']}


def format_supplemental_token_modules(result):
    def show(value):
        return '未知' if value is None else f'{value:g}'
    training = result['host_training']
    lines = [result['operator_name'] + ' · 分技能召唤物培养端点与模组直接加值',
             f"宿主资格参考：精英{training['elite']} · 等级{training['level']}；所列模组{result['module_name']}："
             f"精英{result['module_unlock_elite']}等级{result['module_unlock_level']}解锁门",
             f"独立实体资料阶段：精英{result['selection']['token_elite']}；"
             + ('1级端点' if result['selection']['endpoint'] == 'first' else '该阶段满级端点')]
    for variant in result['variants']:
        lines.append(f"S{variant['skill']} · {variant['token_name']} · 独立资料等级{variant['token_level_endpoint']}；"
                     + ('宿主技能门符合' if variant['skill_qualified'] else '宿主技能门未符合'))
        for stage in variant['stages']:
            state = {'base_endpoint': '原始端点', 'direct_addition_reference': '直接装备分项',
                     'host_gate_unmet': '宿主技能/模组门未符合'}[stage['state']]
            summary = '；'.join(LABELS[key] + ' ' + show(value) for key, value in stage['values'].items())
            lines.append(f"模组{stage['module_level']}阶段（{state}）：{summary}；"
                         f"库存原属性加值{show(stage['stock_add_parameter'])}，完整上限未知")
    return '\n'.join([*lines, *result['notes']])
