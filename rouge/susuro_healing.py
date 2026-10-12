"""Source-bound physician trait, using a declared recipient ratio only."""
import math

OPERATOR='char_298_susuro'
MODULE='uniequip_002_susuro'
FP_ONE=1<<32
FP_LARGE_EPS_RAW=42950
EVIDENCE='research/p2-susuro-healing-composition-current/receipt.json'


def selected_trait(profile,scenario):
    if profile['id']!=OPERATOR or scenario.get('operator')!=OPERATOR:return None
    module=next((m for m in profile['modules'] if m['id']==scenario.get('module_id')==MODULE),None)
    elite=scenario.get('elite',2)
    level=scenario.get('level') or profile['phases'][elite]['max_level']
    stage=scenario.get('module_level',0)
    if not module or elite<module['unlock_elite'] or level<module['unlock_level'] or stage not in (1,2,3):return None
    expected='susuro_equip_1_'+str(stage)+'_p1'
    for part in module['levels'][stage-1]['parts']:
        if part.get('isToken') or part.get('target')!='TRAIT' or part.get('resKey')!=expected:continue
        for candidate in (part.get('overrideTraitDataBundle') or {}).get('candidates') or []:
            gate=candidate.get('unlockCondition') or {'phase':'PHASE_0','level':1}
            phase=int(gate['phase'][-1])
            if phase>elite or phase==elite and gate['level']>level or candidate.get('requiredPotentialRank',0)>scenario.get('potential',1)-1:continue
            board={x['key']:x['value'] for x in candidate.get('blackboard') or []}
            if board.get('heal_scale')==1.15 and board.get('hp_ratio')==.5:
                return {'module_id':MODULE,'module_level':stage,'res_key':expected,
                    'heal_scale':board['heal_scale'],'hp_ratio_threshold':board['hp_ratio']}
    return None


def reference(profile,scenario):
    trait=selected_trait(profile,scenario)
    if trait is None:return None
    ratio=scenario.get('healing_target_hp_ratio')
    if ratio is not None and (type(ratio) not in (int,float) or not 0<=ratio<=1 or not math.isfinite(ratio)):
        raise ValueError('受疗者生命比例需要0–1的有限数值；未指定时保持未知，不能使用自身生命或缺失生命代替。')
    # Explicit ratio reference uses the native double->Q32.32 conversion:
    # multiply by2**32, then truncation toward zero. Actual hp/maxHp uses
    # native FP division and is not reconstructed from a displayed percentage.
    raw=None if ratio is None else math.trunc(float(ratio)*FP_ONE)
    threshold_raw=math.trunc(trait['hp_ratio_threshold']*FP_ONE)
    qualified=None if raw is None else raw<threshold_raw+FP_LARGE_EPS_RAW
    return {**trait,'scope':'fixed recipient ratio reference',
        'recipient_hp_ratio':ratio,'recipient_hp_ratio_raw_reference':raw,
        'threshold_raw':threshold_raw,'fp_fractional_places':32,'comparison':'LE with native tolerance',
        'epsilon_raw':FP_LARGE_EPS_RAW,'epsilon_ratio_reference':FP_LARGE_EPS_RAW/FP_ONE,
        'qualified':qualified,'factor':None if qualified is None else trait['heal_scale'] if qualified else 1,
        'evidence':EVIDENCE,'compiled_path_verified':True,'actual_recipient_ratio_verified':False,
        'actual_recipient_acquisition_verified':False,'actual_hp_trajectory_verified':False,
        'current_hotfix_equivalence_proven':False,'natural_regeneration_affected':False}


def attach_result(result,ref):
    if ref is None:return
    result['susuro_module_healing_reference']=dict(ref)
    notes=result['estimate']['notes']
    notes.append('苏苏洛PHY-X按受疗者的固定生命比例情景计算；当前基包LE带Q32.32容差，恰好50%也符合条件。比例不是苏苏洛自身生命或缺失生命，不推断真实血量变化、友方覆盖和治疗时刻；当前热更新未核验。')
    if ref['qualified'] is not None:return
    skill=result['estimate']['skill']
    fields=('total_healing','phase_healing','window_healing','cycle_healing','cycle_hps','window_hps')
    result['known_healing_subtotals']={key:skill.get(key) for key in fields}
    affected=any(skill.get(key) not in (None,0) for key in fields) or result.get('total_healing') not in (None,0)
    for key in fields:
        if skill.get(key) not in (None,0):skill[key]=None
    if result.get('total_healing') not in (None,0):result['total_healing']=None
    if affected:result['complete']=result['estimate']['complete']=False
    notes.append('未指定受疗者生命比例；已证治疗小计不含该模组的条件15%增强，完整治疗总量与周期HPS保持未知。自然生命回复沿独立属性路径，未乘该治疗倍率。')
