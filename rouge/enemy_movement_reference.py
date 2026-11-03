"""Source-conditioned movement subtotal, never an actual movement/arrival clock."""
from copy import deepcopy
from functools import lru_cache
import json,math
from pathlib import Path
from .deployment import _single,_fp,_fp_product,_Q32

EVIDENCE='research/p3-enemy-native-movement-current/receipt.json'

@lru_cache(maxsize=1)
def movement_rules():
    return json.loads((Path(__file__).with_name('data')/'enemy-movement-source.json').read_text(encoding='utf-8'))

def _as_single(raw):
    return _single(_single(raw)*_single(1/_Q32))

def conditional_movement(base_speed,rune_factor,stage_multiplier):
    """Explicit lower-only metadata-range branch and no further modifiers.

    The published no-upper standard range and this native arithmetic branch
    agree; pointer/boolean allocation defaults are not inferred by this oracle.
    """
    if any(type(v) not in (int,float) or not math.isfinite(v) or v<0
           for v in (base_speed,rune_factor,stage_multiplier)):
        return {'state':'unavailable_parameters','conditional_speed_tiles_per_second':None}
    rules=movement_rules()
    try:
        base=_fp(base_speed);factor=_fp(rune_factor)
        product=_fp_product(base,factor)
        minimum=_fp(rules['minimum_parameter'])
        clamped=max(minimum,product)
        written=_as_single(clamped)
        # The reflection writer stores an ObscuredFloat; later attribute read
        # converts that float back to FP before the global movement multiplier.
        reread=_fp(written);multiplier=_fp(stage_multiplier)
        final=_fp_product(reread,multiplier)
        speed=_as_single(final)
    except (ValueError,OverflowError):
        return {'state':'unsupported_native_numeric_range','conditional_speed_tiles_per_second':None}
    return {'state':'conditional_source_reference_available',
        'input_field_fp_raw':base,'rune_fp_raw':factor,'product_fp_raw':product,
        'minimum_fp_raw':minimum,'clamped_fp_raw':clamped,
        'written_move_speed_attribute':written,'reread_field_fp_raw':reread,
        'movement_multiplier_fp_raw':multiplier,'speed_fp_raw':final,
        'conditional_speed_tiles_per_second':speed,
        'native_arithmetic_branch_bound':True,'native_field_writer_bound':True,
        'rune_execution_verified':False,'complete_effective_speed_verified':False,
        'complete_effective_speed':None,'native_unwritten_max_flag_baseline_verified':False,
        'native_unwritten_selector_pointer_baseline_verified':False,
        'conditions':['已列符文完成对该敌人移速字段的乘法写入，额外选择器或热更新不改变此路径。',
            '使用来源所列标准下限范围与无上限分支，不存在范围覆盖。',
            '属性读取期间没有其他移动属性加成、减速、阶段或特殊控制器覆盖。'],
        'native_evidence':EVIDENCE,'published_standard_range_source':deepcopy(rules['published_range_source']),
        'actual_position_or_arrival_time':None,'game_clock_speed_multiplier_assumed':False}

def stage_movement_component(stage,base_speed,rune_reference):
    """Only the exact unchanged pinned legacy record supplies this factor."""
    rules=movement_rules();source=stage.get('level_source')
    if (stage.get('id')!=rules['stage_id'] or stage.get('difficulty')!=rules['difficulty']
        or not isinstance(source,dict) or source.get('sha256')!=rules['stage_sha256']
        or rune_reference.get('parameter')!=rules['rune_factor']
        or stage.get('movement_multiplier')!=rules['stage_multiplier']
        or rune_reference.get('source_selector')!=rules['source_selector']):return None
    result=conditional_movement(base_speed,rules['rune_factor'],rules['stage_multiplier'])
    result.update(stage_id=rules['stage_id'],source=deepcopy(source),
        source_selector=rules['source_selector'],rune_key='enemy_attribute_mul',attribute_type='MOVE_SPEED',
        receiver_type='Torappu.LevelData+EnemyData.attributes',minimum_parameter=rules['minimum_parameter'])
    return result
