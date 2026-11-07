"""Distinct current GUA-X recipient gates, only for fixed offline references."""
import math
from .susuro_healing import FP_ONE, FP_LARGE_EPS_RAW, matching_healing_trait

BINDINGS={
 'char_196_sunbr':('古米','uniequip_002_sunbr','sunbr','LT','set_heal_scale_by_hpratio'),
 'char_2025_shu':('黍','uniequip_002_shu','shu','LE','heal_scale_up[hpratio][LE]')}
FIELD='guardian_healing_target_hp_ratio'
EVIDENCE='research/p2-guardian-healing-gates-current/receipt.json'

def selected_trait(profile,scenario,*,cultivation=None):
    binding=BINDINGS.get(profile['id'])
    if binding is None or scenario.get('operator')!=profile['id']:return None
    name,identity,prefix,comparison,template=binding
    trait = matching_healing_trait(profile, scenario, cultivation, identity, prefix)
    if trait is None:
        return None
    return {'operator_id': profile['id'], 'operator_name': name, **trait,
            'comparison': comparison, 'template': template}


def reference(profile,scenario,*,cultivation=None):
    trait=selected_trait(profile,scenario,cultivation=cultivation)
    if trait is None:return None
    ratio=scenario.get(FIELD)
    if ratio is not None and (type(ratio) not in (int,float) or not 0<=ratio<=1):
        raise ValueError('受疗者生命比例需要0–1的有限数值；未指定时保持未知，不能使用自身生命或缺失生命代替。')
    raw=None if ratio is None else math.trunc(float(ratio)*FP_ONE)
    threshold_raw=math.trunc(trait['hp_ratio_threshold']*FP_ONE)
    boundary=threshold_raw+(FP_LARGE_EPS_RAW if trait['comparison']=='LE' else -FP_LARGE_EPS_RAW)
    qualified=None if raw is None else raw<boundary
    return {**trait,'scope':'fixed recipient ratio reference','recipient_hp_ratio':ratio,
        'recipient_hp_ratio_raw_reference':raw,'threshold_raw':threshold_raw,'comparison_boundary_raw':boundary,
        'fp_fractional_places':32,'epsilon_raw':FP_LARGE_EPS_RAW,'epsilon_ratio_reference':FP_LARGE_EPS_RAW/FP_ONE,
        'qualified':qualified,'factor':None if qualified is None else trait['heal_scale'] if qualified else 1,
        'evidence':EVIDENCE,'compiled_path_verified':True,'actual_recipient_ratio_verified':False,
        'actual_recipient_acquisition_verified':False,'actual_hp_trajectory_verified':False,
        'current_hotfix_equivalence_proven':False,'natural_regeneration_affected':False}

def attach_result(result,ref):
    if ref is None:return
    result['guardian_module_healing_reference']=dict(ref)
    notes=result['estimate']['notes']
    boundary='古米LT采用比例原值小于阈值减容差，恰好50%不符合。' if ref['comparison']=='LT' else '黍LE采用比例原值小于阈值加容差，恰好50%符合。'
    notes.append(ref['operator_name']+'GUA-X按受疗者固定比例计算直接治疗条件倍率；'+boundary+'不从自身生命、敌人血量或预算缺失生命推断受疗者血量；不推断实际友方获取、覆盖和治疗时钟，当前热更新未核验。')
    if ref['qualified'] is not None:return
    skill=result['estimate']['skill']
    fields=('total_healing','phase_healing','window_healing','cycle_healing','cycle_hps','window_hps')
    result['known_healing_subtotals']={key:skill[key] for key in fields}
    affected=False
    for key,value in result['known_healing_subtotals'].items():
        if value not in (None,0):
            skill[key]=None
            affected=True
    total=result['total_healing']
    if total not in (None,0):
        result['total_healing']=None
        affected=True
    if affected:result['complete']=result['estimate']['complete']=False
    notes.append('未指定受疗者生命比例；已证直接治疗小计不含该模组条件15%增强，受影响完整治疗总量与周期HPS未知。生命回复与播种地块回复不受该直接治疗倍率影响。')
