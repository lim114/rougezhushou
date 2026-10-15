"""Conditional panel layers, typed writer arguments and independent flow facts.

Nominal snapshots are not protected decoder reads or observed game state.
The ordinary recomputation and manager finalizer are distinct source pipelines.
"""
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import math
import struct
from .mechanist_explosion_math import ONE, MIN_RAW, MAX_RAW, add, multiply
from .panel_native_precision import fp_single_reference, writer_integer_reference, single_integer_reference

SOURCE = 'research/p2-panel-native-finalization-283/source-manifest.json'
SOURCE_SHA256 = '09039f7dabf680b76e57b827d960e3a793609a7b592294700c8acbe553dea08a'
FIELDS = {
    'hp': (0, 'ObscuredInt', ONE, MAX_RAW),
    'attack': (1, 'ObscuredInt', 0, MAX_RAW),
    'defense': (2, 'ObscuredInt', 0, MAX_RAW),
    'resistance': (3, 'ObscuredFloat', 0, 100 * ONE),
    'attack_speed': (7, 'ObscuredFloat', 20 * ONE, MAX_RAW),
}
REFERENCE_KEYS = ('input_fp_raw', 'after_add_raw', 'multiplier_raw', 'after_multiplier_raw',
                  'after_final_add_raw', 'after_final_scaler_raw', 'clamped_raw',
                  'getter_result_raw', 'as_float', 'writer')
LIMITATIONS = [
    '输入是名义模型快照及已选数值分项，不是实际保护字段读取。',
    '实际修饰器激活、完整库存、热更新、RC与正常执行资格未证。',
    '写入参数不等于保护编码后的下一次解码值；后续层仅使用独立名义快照。',
    '普通属性参考仅限默认范围下的条件重算，不断言缓存已脏或无运行时范围覆盖。',
]


def source_data():
    """Fresh file guards, including dependencies whose own loaders may cache."""
    root = Path(__file__).resolve().parents[1]
    try:
        raw = (root / SOURCE).read_bytes()
        if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
            return None
        data = json.loads(raw)
        for name, expected in data['files'].items():
            if hashlib.sha256((root / name).read_bytes()).hexdigest() != expected:
                return None
        return deepcopy(data)
    except (OSError, ValueError, TypeError, KeyError):
        return None


def _object(v, keys):
    if type(v) is not dict or set(v) != set(keys):
        raise ValueError('请使用完整固定字段，不能注入来源或计算器。')


def _int(v, bits, unsigned=False):
    if v is None:
        return
    lo, hi = (0, 1 << bits) if unsigned else (-(1 << (bits - 1)), 1 << (bits - 1))
    if type(v) is not int or not lo <= v < hi:
        raise ValueError('需要指定宽度整数或null。')


def _tri(v):
    if v is not None and type(v) is not bool:
        raise ValueError('资格需要true、false或null。')


def _id(v):
    if type(v) is not str or not 1 <= len(v) <= 80 or any(ord(c) < 32 or 0xd800 <= ord(c) <= 0xdfff for c in v):
        raise ValueError('身份需要1–80字符，不能含控制字符。')


def _single_fp(bits):
    if bits is None:
        return None
    exponent, significand = (bits >> 23) & 255, bits & 0x7fffff
    if exponent == 255 or (exponent == 0 and significand):
        return None
    if exponent == 0:
        return 0
    value = Fraction((1 << 23) + significand)
    power = exponent - 150 + 32
    value = value * (1 << power) if power >= 0 else value / (1 << -power)
    if bits >> 31:
        value = -value
    if not MIN_RAW <= value < (1 << 63):
        return None
    return int(value)  # CVTTSS2SI64 toward zero, including valid MIN64.


def _mul(a, b):
    return 0 if a == 0 or b == 0 else multiply(a, b)


def _clamp(v, lo, hi):
    if lo is not None and hi is not None and lo >= hi:
        return lo
    if v is not None and lo is not None and v <= lo:
        return lo
    first = None if v is None or hi is None else min(v, hi)
    return None if first is None or lo is None else max(first, lo)


def _writer_math(raw, storage):
    floating = fp_single_reference(raw)
    bits = floating['single_bits_candidates']
    integer = writer_integer_reference(raw) if storage == 'ObscuredInt' else None
    consensus = integer['integer_consensus'] if integer is not None and integer['complete'] else None
    unique_bits = bits[0] if floating['complete'] and len(bits) == 1 else None
    value = consensus if integer is not None else None if unique_bits is None else struct.unpack('<f', struct.pack('<I', unique_bits))[0]
    return floating, {
        'storage_type': storage, 'integer_reference': integer,
        'single_bits_candidates': bits,
        'encoder_argument_reference': value,
        'encoder_argument_bits_reference': None if integer is not None else unique_bits,
        'copied_byte_count_reference': 20 if integer is not None else 24,
    }


def _validate_fields(payload):
    _object(payload, {'fields'})
    rows = payload['fields']
    if type(rows) is not list or len(rows) > 80:
        raise ValueError('需要0–80条面板参考。')
    seen = set()
    keys = {'id', 'field', 'phase', 'model_value', 'basis_kind', 'basis_single_bits', 'basis_fp_raw',
            'addition_raw', 'multiplier_delta_raw', 'final_addition_raw', 'final_scaler_raw'}
    for row in rows:
        _object(row, keys)
        _id(row['id'])
        if row['id'] in seen:
            raise ValueError('参考身份不能重复。')
        seen.add(row['id'])
        if row['field'] not in FIELDS or row['phase'] not in ('cultivation', 'rune', 'normal', 'skill'):
            raise ValueError('需要固定五属性和培养/藏品/常态/技能阶段。')
        if row['phase'] == 'skill' and row['field'] not in ('attack', 'attack_speed'):
            raise ValueError('既有技能面板仅有攻击与攻速；不能虚构其它技能面板。')
        model = row['model_value']
        if model is not None and (type(model) not in (int, float) or not math.isfinite(model)):
            raise ValueError('名义模型值需要有限数字或null，不能用布尔值。')
        if row['basis_kind'] not in ('nominal_single', 'nominal_fp'):
            raise ValueError('基值必须显式为独立名义Single或FP快照。')
        _int(row['basis_single_bits'], 32, True)
        _int(row['basis_fp_raw'], 64)
        unused = 'basis_fp_raw' if row['basis_kind'] == 'nominal_single' else 'basis_single_bits'
        if row[unused] is not None:
            raise ValueError('未选中的基值必须是null，不能暗接编码回环。')
        for key in ('addition_raw', 'multiplier_delta_raw', 'final_addition_raw', 'final_scaler_raw'):
            _int(row[key], 64)
        if row['phase'] == 'cultivation' and [row[k] for k in ('addition_raw', 'multiplier_delta_raw', 'final_addition_raw', 'final_scaler_raw')] != [0, 0, 0, ONE]:
            raise ValueError('培养层只解释名义基值，不添加修饰或写回流程。')
        if row['phase'] == 'rune' and row['final_addition_raw'] != 0:
            raise ValueError('藏品manager没有final addition桶。')


def panel_native_finalization(payload):
    _validate_fields(payload)
    valid = source_data() is not None
    result = {'source_valid': valid, 'fields': [], 'complete_native_panel': False,
              'actual_panel': None, 'limitations': list(LIMITATIONS)}
    for item in payload['fields']:
        _, storage, lo, hi = FIELDS[item['field']]
        row = {key: item[key] for key in ('id', 'field', 'phase', 'model_value')}
        row.update(basis='nominal_model_snapshot', storage_type=storage if valid else None,
                   metadata_range={'lower_raw': lo, 'upper_raw': hi} if valid else None,
                   references={key: None for key in REFERENCE_KEYS}, conditional_complete=False,
                   actual_decoded_value=None, actual_getter_raw=None, complete_native_value=False,
                   limitations=list(LIMITATIONS))
        if valid:
            ref = row['references']
            raw = _single_fp(item['basis_single_bits']) if item['basis_kind'] == 'nominal_single' else item['basis_fp_raw']
            ref['input_fp_raw'] = raw
            if item['phase'] == 'cultivation':
                row['conditional_complete'] = raw is not None
            else:
                added = add(raw, item['addition_raw'])
                multiplier = add(ONE, item['multiplier_delta_raw'])
                if item['phase'] != 'rune' and multiplier is not None:
                    multiplier = max(0, multiplier)
                multiplied = _mul(added, multiplier)
                final_added = multiplied if item['phase'] == 'rune' else add(multiplied, item['final_addition_raw'])
                scaled = _mul(final_added, item['final_scaler_raw'])
                clamped = _clamp(scaled, lo, hi)
                ref.update(after_add_raw=added, multiplier_raw=multiplier, after_multiplier_raw=multiplied,
                           after_final_add_raw=final_added, after_final_scaler_raw=scaled, clamped_raw=clamped)
                if item['phase'] == 'rune':
                    ref['as_float'], ref['writer'] = _writer_math(clamped, storage)
                    row['conditional_complete'] = ref['writer']['encoder_argument_reference'] is not None
                else:
                    ref['getter_result_raw'] = clamped
                    row['conditional_complete'] = clamped is not None
        result['fields'].append(row)
    return result


def public_example():
    rows = []
    for phase in ('cultivation', 'rune', 'normal', 'skill'):
        for field in FIELDS:
            if phase == 'skill' and field not in ('attack', 'attack_speed'):
                continue
            value = {'hp': 1000, 'attack': 100, 'defense': 90, 'resistance': 10, 'attack_speed': 100}[field]
            rows.append({'id': phase + '-' + field, 'field': field, 'phase': phase, 'model_value': value,
                         'basis_kind': 'nominal_fp', 'basis_single_bits': None, 'basis_fp_raw': value * ONE,
                         'addition_raw': 0, 'multiplier_delta_raw': 0, 'final_addition_raw': 0,
                         'final_scaler_raw': ONE})
    return {'fields': rows}


class _Flow:
    def __init__(self, names, initial=True):
        self.active = initial
        self.terminal_normal = None
        self.stages = {name: {'name': name, 'called': False if initial is not None else None,
                              'normal': None, 'reference': None} for name in names}

    def step(self, name, normal, reference=None):
        called = self.active
        self.stages[name] = {'name': name, 'called': called,
                             'normal': normal if called is True else None,
                             'reference': deepcopy(reference) if called is True else None}
        if called is True and normal is not True:
            self.active = normal
            self.terminal_normal = normal
        if self.active is None:
            for stage in self.stages.values():
                if stage['called'] is False:
                    stage['called'] = None

    def control(self, condition):
        if self.active is True and condition is None:
            self.active = None
            self.terminal_normal = None
            for stage in self.stages.values():
                if stage['called'] is False:
                    stage['called'] = None

    def finish(self, normal):
        if self.active is True:
            self.active = False
            self.terminal_normal = normal

    def normal(self):
        return True if self.active is True else self.terminal_normal


def _read_bool(v):
    _object(v, {'normal', 'value'})
    _tri(v['normal'])
    _tri(v['value'])


READ_NAMES = ('argument_null_check', 'object_type', 'int_target_type', 'int_assignability',
              'float_target_type', 'float_assignability', 'unbox_and_copy', 'decode', 'fallback_convert')
READ_KEYS = {'value_exists', 'object_type_normal', 'int_type_normal', 'int_assignable',
             'float_type_normal', 'float_assignable', 'unbox_normal', 'decode_normal',
             'decoded_int32', 'decoded_single_bits', 'fallback_normal', 'fallback_bits'}


def _validate_read(v):
    _object(v, READ_KEYS)
    for key in ('value_exists', 'object_type_normal', 'int_type_normal', 'float_type_normal',
                'unbox_normal', 'decode_normal', 'fallback_normal'):
        _tri(v[key])
    _read_bool(v['int_assignable'])
    _read_bool(v['float_assignable'])
    _int(v['decoded_int32'], 32)
    _int(v['decoded_single_bits'], 32, True)
    _int(v['fallback_bits'], 32, True)


def _read_reference(v, initial):
    f = _Flow(READ_NAMES, initial)
    result = {'normal': None, 'stages': [], 'single_bits_candidates': [], 'route': None,
              'actual_decoded_value': None}
    f.step('argument_null_check', True, {'exists': v['value_exists']})
    f.control(v['value_exists'])
    if f.active is True and v['value_exists'] is False:
        result.update(single_bits_candidates=[0], route='null_zero')
        f.finish(True)
    elif f.active is True:
        f.step('object_type', v['object_type_normal'])
        f.step('int_target_type', v['int_type_normal'])
        f.step('int_assignability', v['int_assignable']['normal'], v['int_assignable']['value'])
        if f.active is True:
            f.control(v['int_assignable']['value'])
        route = 'ObscuredInt' if f.active is True and v['int_assignable']['value'] is True else None
        if f.active is True and v['int_assignable']['value'] is False:
            f.step('float_target_type', v['float_type_normal'])
            f.step('float_assignability', v['float_assignable']['normal'], v['float_assignable']['value'])
            if f.active is True:
                f.control(v['float_assignable']['value'])
            route = 'ObscuredFloat' if f.active is True and v['float_assignable']['value'] is True else None
            if f.active is True and v['float_assignable']['value'] is False:
                route = 'Convert.ToSingle'
                f.step('fallback_convert', v['fallback_normal'], {'independent_bits': v['fallback_bits']})
                if f.active is True:
                    result['single_bits_candidates'] = [] if v['fallback_bits'] is None else [v['fallback_bits']]
        if route in ('ObscuredInt', 'ObscuredFloat'):
            f.step('unbox_and_copy', v['unbox_normal'], {'byte_count': 20 if route == 'ObscuredInt' else 24})
            f.step('decode', v['decode_normal'], {'independent_value': v['decoded_int32'] if route == 'ObscuredInt' else v['decoded_single_bits']})
            if f.active is True:
                if route == 'ObscuredInt':
                    raw = None if v['decoded_int32'] is None else v['decoded_int32'] * ONE
                    result['single_bits_candidates'] = fp_single_reference(raw)['single_bits_candidates']
                else:
                    result['single_bits_candidates'] = [] if v['decoded_single_bits'] is None else [v['decoded_single_bits']]
        result['route'] = route
    result.update(normal=f.normal(), stages=list(f.stages.values()))
    return result


def read_field_reference(payload):
    _validate_read(payload)
    valid = source_data() is not None
    return {'source_valid': valid, **_read_reference(payload, True if valid else None)}


WRITE_NAMES = ('as_float', 'field_null_check', 'field_type_read', 'type_route',
               'round', 'encode', 'struct_copy', 'box', 'set_value')
WRITE_KEYS = {'fp_raw', 'field_exists', 'as_float_normal', 'field_type_read', 'type_route_normal', 'round_normal',
              'encode_normal', 'copy_normal', 'box_normal', 'set_value_normal'}
TYPES = ('ObscuredInt', 'ObscuredFloat', 'Int32', 'Single', 'unsupported')


def _validate_write(v):
    _object(v, WRITE_KEYS)
    _int(v['fp_raw'], 64)
    for key in ('field_exists', 'as_float_normal', 'type_route_normal', 'round_normal', 'encode_normal',
                'copy_normal', 'box_normal', 'set_value_normal'):
        _tri(v[key])
    _object(v['field_type_read'], {'normal', 'value'})
    _tri(v['field_type_read']['normal'])
    if v['field_type_read']['value'] is not None and v['field_type_read']['value'] not in TYPES:
        raise ValueError('需要固定已证类型、unsupported或null。')


def _write_reference(v, initial):
    f = _Flow(WRITE_NAMES, initial)
    floating = fp_single_reference(v['fp_raw']) if initial is True else None
    result = {'normal': None, 'stages': [], 'return_boolean': None,
              'as_float_reference': floating, 'encoder_argument_reference': None,
              'encoder_argument_bits_reference': None, 'boxed_type_reference': None,
              'stored_prefix': None, 'actual_decoded_value': None}
    f.step('as_float', v['as_float_normal'], floating)
    f.step('field_null_check', v['field_exists'], {'exists': v['field_exists']})
    f.step('field_type_read', v['field_type_read']['normal'], v['field_type_read']['value'])
    kind = v['field_type_read']['value']
    f.step('type_route', v['type_route_normal'], kind)
    if f.active is True and kind is None:
        f.control(None)
    if f.active is True and kind == 'unsupported':
        result['return_boolean'] = False
        f.finish(True)
    if f.active is True and kind in ('ObscuredInt', 'Int32'):
        integer = writer_integer_reference(v['fp_raw'])
        argument = integer['integer_consensus'] if integer['complete'] else None
        f.step('round', v['round_normal'], integer)
        if f.active is True and kind == 'ObscuredInt':
            result['encoder_argument_reference'] = argument
            f.step('encode', v['encode_normal'], {'int32_argument': argument})
            f.step('struct_copy', v['copy_normal'], {'byte_count': 20, 'encoder_argument_reference': argument})
            if f.active is True:
                result['stored_prefix'] = {'kind': 'protected_struct_copy', 'byte_count': 20,
                                           'encoder_argument_reference': argument}
        if f.active is True:
            result['boxed_type_reference'] = 'ObscuredInt' if kind == 'ObscuredInt' else 'Double'
            f.step('box', v['box_normal'], {'boxed_type': result['boxed_type_reference'],
                                          'pre_encoder_integer_reference': argument})
    elif f.active is True and kind in ('ObscuredFloat', 'Single'):
        bits = floating['single_bits_candidates']
        argument = bits[0] if floating['complete'] and len(bits) == 1 else None
        if kind == 'ObscuredFloat':
            result['encoder_argument_bits_reference'] = argument
            f.step('encode', v['encode_normal'], {'single_bits_argument': argument})
            f.step('struct_copy', v['copy_normal'], {'byte_count': 24, 'encoder_argument_bits_reference': argument})
            if f.active is True:
                result['stored_prefix'] = {'kind': 'protected_struct_copy', 'byte_count': 24,
                                           'encoder_argument_bits_reference': argument}
        if f.active is True:
            result['boxed_type_reference'] = 'ObscuredFloat' if kind == 'ObscuredFloat' else 'Single'
            f.step('box', v['box_normal'], {'boxed_type': result['boxed_type_reference'],
                                          'single_bits_reference': argument})
    if f.active is True:
        f.step('set_value', v['set_value_normal'], {'actual_future_decode': None})
        if f.active is True:
            result['return_boolean'] = True
    result.update(normal=f.normal(), stages=list(f.stages.values()))
    return result


def write_field_reference(payload):
    _validate_write(payload)
    valid = source_data() is not None
    return {'source_valid': valid, **_write_reference(payload, True if valid else None)}


MANAGER_NAMES = ('first_metas_get', 'first_metas_check', 'first_item_get', 'first_item_check',
                 'field_read', 'second_metas_get', 'second_metas_check', 'second_item_get',
                 'second_item_check', 'range_meta_read', 'range_meta_check', 'attribute_read',
                 'field_null_check', 'reflection_get', 'read_attributes_field', 'single_to_fp',
                 'addition_array_read', 'addition_array_check', 'addition_bounds', 'addition_element',
                 'multiplier_array_read', 'multiplier_array_check', 'multiplier_bounds', 'multiplier_element',
                 'scaler_array_read', 'scaler_array_check', 'scaler_bounds', 'scaler_element',
                 'range_get', 'write_attributes_field', 'loop_increment')
FIRST_META_KEYS = {'get_normal', 'exists', 'item_normal', 'item_exists', 'field_read_normal', 'field_exists'}
SECOND_META_KEYS = {'get_normal', 'exists', 'item_normal', 'item_exists', 'range_read_normal',
                    'range_exists', 'attribute_read_normal', 'attribute'}
ARRAY_KEYS = {'read_normal', 'exists', 'length', 'element_normal', 'raw'}


def _validate_manager(v):
    _object(v, {'ordinary_native_path', 'initial_metas', 'iterations'})
    _tri(v['ordinary_native_path'])
    init = v['initial_metas']
    _object(init, {'get_normal', 'exists', 'count_normal', 'count'})
    for key in ('get_normal', 'exists', 'count_normal'):
        _tri(init[key])
    _int(init['count'], 32)
    if init['count'] is not None and init['count'] > 40:
        raise ValueError('独立流程参考最多40次迭代。')
    if type(v['iterations']) is not list or len(v['iterations']) > 40:
        raise ValueError('独立流程参考最多40次迭代。')
    if init['count'] is not None and len(v['iterations']) != max(0, init['count']):
        raise ValueError('迭代声明必须覆盖初始固定count，不能以部分列表冒充全量循环。')
    seen = set()
    for row in v['iterations']:
        _object(row, {'id', 'first_meta', 'second_meta', 'reflection_get_normal', 'read_field',
                      'single_to_fp_normal', 'arrays', 'range_read', 'writer'})
        _id(row['id'])
        if row['id'] in seen:
            raise ValueError('迭代身份不能重复。')
        seen.add(row['id'])
        _object(row['first_meta'], FIRST_META_KEYS)
        for value in row['first_meta'].values():
            _tri(value)
        _object(row['second_meta'], SECOND_META_KEYS)
        for key in SECOND_META_KEYS - {'attribute'}:
            _tri(row['second_meta'][key])
        _int(row['second_meta']['attribute'], 32)
        _tri(row['reflection_get_normal'])
        _tri(row['single_to_fp_normal'])
        _validate_read(row['read_field'])
        _object(row['arrays'], {'addition', 'multiplier', 'scaler'})
        for array in row['arrays'].values():
            _object(array, ARRAY_KEYS)
            for key in ('read_normal', 'exists', 'element_normal'):
                _tri(array[key])
            _int(array['length'], 32, True)
            _int(array['raw'], 64)
        _object(row['range_read'], {'normal', 'lower_raw', 'upper_raw'})
        _tri(row['range_read']['normal'])
        _int(row['range_read']['lower_raw'], 64)
        _int(row['range_read']['upper_raw'], 64)
        # The writer receives the captured FieldInfo and calculated FP argument;
        # those two keys cannot be separately supplied to manufacture identity.
        _object(row['writer'], WRITE_KEYS - {'fp_raw', 'field_exists'})
        _validate_write({'fp_raw': None, 'field_exists': row['first_meta']['field_exists'], **row['writer']})


def _array_read(f, name, point, attribute):
    f.step(name + '_array_read', point['read_normal'], {'exists': point['exists']})
    f.step(name + '_array_check', point['exists'], {'exists': point['exists']})
    index = None if attribute is None else attribute & 0xffffffff
    bounds = None if index is None or point['length'] is None else index < point['length']
    f.step(name + '_bounds', bounds, {'attribute': attribute, 'unsigned_index': index, 'length': point['length']})
    f.step(name + '_element', point['element_normal'], {'raw': point['raw']})
    return point['raw'] if f.active is True else None


def manager_flow_reference(payload):
    """Independent ordinary snapshots, not actual reflection/game execution."""
    _validate_manager(payload)
    valid = source_data() is not None
    start = payload['ordinary_native_path'] if valid else None
    outer = _Flow(('initial_metas_get', 'initial_metas_check', 'initial_count'), start)
    init = payload['initial_metas']
    outer.step('initial_metas_get', init['get_normal'])
    outer.step('initial_metas_check', init['exists'], {'exists': init['exists']})
    outer.step('initial_count', init['count_normal'], {'count': init['count']})
    if outer.active is True and init['count'] is None:
        outer.control(None)
    rows = []
    for item in payload['iterations']:
        f = _Flow(MANAGER_NAMES, outer.active)
        row = {'id': item['id'], 'normal': None, 'stages': [], 'read_reference': None,
               'writer_reference': None, 'arithmetic_reference': None,
               'loop_continues_reference': None, 'actual_attributes': None}
        first, second = item['first_meta'], item['second_meta']
        f.step('first_metas_get', first['get_normal'])
        f.step('first_metas_check', first['exists'])
        f.step('first_item_get', first['item_normal'])
        f.step('first_item_check', first['item_exists'])
        f.step('field_read', first['field_read_normal'], {'exists': first['field_exists']})
        f.step('second_metas_get', second['get_normal'])
        f.step('second_metas_check', second['exists'])
        f.step('second_item_get', second['item_normal'])
        f.step('second_item_check', second['item_exists'])
        f.step('range_meta_read', second['range_read_normal'], {'exists': second['range_exists']})
        # This comparison is normal for either Boolean result. Its false branch
        # is a normal skip; it is not the later FieldInfo-null throwing guard.
        f.step('range_meta_check', True, {'exists': second['range_exists']})
        if f.active is True:
            f.control(second['range_exists'])
        skipped = f.active is True and second['range_exists'] is False
        if skipped:
            f.step('loop_increment', True, {'writer_boolean_tested': False, 'skipped_missing_range': True})
            row['loop_continues_reference'] = True
            f.finish(True)
        else:
            f.step('attribute_read', second['attribute_read_normal'], {'attribute': second['attribute']})
            f.step('field_null_check', first['field_exists'], {'exists': first['field_exists']})
            f.step('reflection_get', item['reflection_get_normal'])
            read = _read_reference(item['read_field'], f.active)
            row['read_reference'] = read
            f.step('read_attributes_field', read['normal'], {'single_bits_candidates': read['single_bits_candidates']})
            candidates = [_single_fp(bits) for bits in read['single_bits_candidates']] if f.active is True else []
            basis = candidates[0] if candidates and candidates[0] is not None and all(value == candidates[0] for value in candidates) else None
            f.step('single_to_fp', item['single_to_fp_normal'], {'fp_argument_reference': basis})
            attribute = second['attribute']
            addition = _array_read(f, 'addition', item['arrays']['addition'], attribute)
            after_add = add(basis, addition) if f.active is True else None
            delta = _array_read(f, 'multiplier', item['arrays']['multiplier'], attribute)
            multiplier = add(ONE, delta) if f.active is True else None
            product = _mul(after_add, multiplier) if f.active is True else None
            scaler = _array_read(f, 'scaler', item['arrays']['scaler'], attribute)
            scaled = _mul(product, scaler) if f.active is True else None
            f.step('range_get', item['range_read']['normal'], item['range_read'])
            clamped = _clamp(scaled, item['range_read']['lower_raw'], item['range_read']['upper_raw']) if f.active is True else None
            row['arithmetic_reference'] = {'basis_raw': basis, 'after_add_raw': after_add,
                                           'multiplier_raw': multiplier, 'after_multiplier_raw': product,
                                           'after_scaler_raw': scaled, 'clamped_raw': clamped} if valid else None
            writer = _write_reference({'fp_raw': clamped, 'field_exists': first['field_exists'], **item['writer']}, f.active)
            row['writer_reference'] = writer
            f.step('write_attributes_field', writer['normal'], {'returned_boolean': writer['return_boolean']})
            # Actual source increments without inspecting the normal writer's AL.
            f.step('loop_increment', True, {'writer_boolean_tested': False,
                                          'writer_boolean': writer['return_boolean']})
            if f.active is True:
                row['loop_continues_reference'] = True
        row.update(normal=f.normal(), stages=list(f.stages.values()))
        rows.append(row)
        if outer.active is True and row['normal'] is not True:
            outer.active = row['normal']
            outer.terminal_normal = row['normal']
    return {'source_valid': valid, 'normal': outer.normal(), 'stages': list(outer.stages.values()),
            'rows': rows, 'actual_attributes': None, 'complete_native_panel': False}
