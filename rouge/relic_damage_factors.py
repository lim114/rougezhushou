"""Exact source groups: base-one merged boards differ from independent buffs."""
from math import prod

EVIDENCE='research/p2-relic-damage-composition-current/receipt.json'
BASE_ONE={
 'rogue_6_relic_legacy_5':('physical',1.15),'rogue_6_relic_legacy_6':('physical',1.25),
 'rogue_6_relic_legacy_7':('physical',1.35),'rogue_6_relic_legacy_8':('magic',1.2),
 'rogue_6_relic_legacy_9':('magic',1.3),'rogue_6_relic_legacy_10':('magic',1.4),
 'rogue_6_relic_legacy_11':('true',2.5)}
ELEMENTAL={'rogue_6_relic_legacy_104':(0,2),'rogue_6_relic_fight_21':(1,1.75)}


def verified_rule(rule,dtype):
    if not (rule.get('_verified_rule') and rule.get('kind')=='damage_taken' and rule.get('damage_type')==dtype
            and rule.get('composition_evidence')==EVIDENCE):return False
    if dtype=='elemental':
        source=ELEMENTAL.get(rule.get('relic_id'))
        return bool(source and rule.get('source_buff_key')=='global_buff_normal' and
            rule.get('source_buff_index')==source[0] and rule.get('value')==source[1]-1 and
            rule.get('group')=='enemy_take_element_damage_up[fix]')
    source=BASE_ONE.get(rule.get('relic_id'))
    group={'physical':'enemy_damage_scale[phy]','magic':'enemy_damage_scale[mag]','true':'enemy_damage_scale[pure]'}.get(dtype)
    return bool(source and source[0]==dtype and rule.get('source_buff_key')=='global_buff_stack_base_one' and
        rule.get('source_buff_index')==0 and rule.get('value')==source[1]-1 and rule.get('group')==group)


def source_factor(rules,dtype):
    """Return parameter arithmetic only for source-bound combinations."""
    selected=[r for r in rules if r.get('kind')=='damage_taken' and r.get('damage_type')==dtype]
    if not selected:return 1
    if len(selected)==1:return 1+selected[0]['value']
    if not all(verified_rule(r,dtype) for r in selected):return None
    distinct={r['relic_id']:r['value'] for r in selected}
    return prod(1+v for v in distinct.values()) if dtype=='elemental' else 1+sum(distinct.values())


def parameter_factor(effects,dtype):
    """Preserve existing manual-input convention outside the verified pair."""
    selected=[e for e in effects if e['kind']=='damage_taken' and e.get('damage_type')==dtype and float(e['value'])!=0]
    if dtype=='elemental' and len({r.get('relic_id') for r in selected})>1 and all(verified_rule(r,dtype) for r in selected):
        return source_factor(selected,dtype)
    return 1+sum(float(e['value']) for e in selected)


def finish_unresolved_composition(result,resolution):
    """Keep an explicit manual subtotal; never call the unbound mixture full."""
    if not resolution.get('damage_composition_unresolved'):return
    # This is an output-layer uncertainty; no elemental hits means no changed
    # damage reference. Zero remains known. Existing unknowns stay unknown.
    if not any(c.get('damage_type')=='elemental' and c.get('total',0)>0 for c in result.get('components',[])):return
    skill=result['estimate']['skill']
    keys=('total_damage','phase_damage','cycle_damage','cycle_dps','window_damage','window_dps')
    if 'known_damage_subtotals' not in result:
        result['known_damage_subtotals']={key:skill.get(key) for key in keys}
        result['known_damage_subtotals']['window_damage']=skill.get('window_damage',result.get('total_damage'))
    for key in keys:
        if skill.get(key)!=0:skill[key]=None
    if result.get('total_damage')!=0:result['total_damage']=None
    result['estimate']['notes'].append('双藏品与未绑定手动来源的组合层未知；保留未套用双藏品的明确参数小计，受影响完整伤害效率未知。零伤、基础属性与资源回转不由此清空。')


def note_verified_composition(result,scenario):
    rules=[e for e in scenario.get('effects',[])if verified_rule(e,'elemental')]
    if len({r['relic_id']for r in rules})>1:
        result['estimate']['notes'].append('阿猛与冰中火按两个独立承伤效果连乘，元素伤害参数倍率为3.5；冰中火的损伤积累倍率单独处理。不由此推定实际附着、触发时间或当前热更新。')
