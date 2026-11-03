"""Source-bound positive FP and single-precision barrier blackboard reference.

Rounding mode is a declaration, not a measurement of the game's MXCSR.
Integer arithmetic avoids the int64 -> double -> float double-rounding trap.
"""
from functools import lru_cache
from pathlib import Path
import hashlib
import json
import struct

ONE = 1 << 32
MAX_RAW = (1 << 63) - 1
SOURCE = 'rouge/data/barrier-blackboard-source.json'
SOURCE_SHA256 = '420d761a6364e5d840b5965aa751c0f76a39016d298cc17ae6b1989fdc35347e'
ROUNDING_MODES = ('nearest_even', 'toward_zero', 'toward_positive', 'toward_negative')


@lru_cache(maxsize=1)
def source_valid():
    path=Path(__file__).resolve().parents[1]/SOURCE
    return path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==SOURCE_SHA256


def _raw(value):
    if type(value) is not int or not 0 <= value <= MAX_RAW:
        raise ValueError('屏障数值参考需要非负signed64 FP原值。')
    return value


def float32_number_raw(bits):
    """FP(float): single float * 2^32, then signed truncate toward zero."""
    if type(bits) is not int or not 0 <= bits <= 0xffffffff:
        raise ValueError('单精度数值需要32位无符号bits。')
    exponent=(bits >> 23) & 255;fraction=bits & 0x7fffff
    if bits >> 31 or exponent==255:
        raise ValueError('只支持有限非负单精度值，不接受负值/NaN/Infinity。')
    significand=fraction if exponent==0 else fraction+(1<<23)
    shift=-117 if exponent==0 else exponent-118
    raw=significand << shift if shift>=0 else significand >> -shift
    return raw if raw<=MAX_RAW else None


def blackboard_storage_reference(raw, rounding_mode):
    """Assign(FP) -> AsFloat -> Assign(float) -> GetFpOrDefault trace."""
    _raw(raw)
    if rounding_mode is not None and rounding_mode not in ROUNDING_MODES:
        raise ValueError('舍入环境需要四种明确模式之一，或null（未知）。')
    result={'math_raw':raw,'rounding_mode':rounding_mode,'stored_float32_bits':None,
        'stored_float32':None,'readback_raw':None,'readback_minus_math_raw':None,
        'source_valid':source_valid(),'status':'unknown'}
    if not result['source_valid'] or rounding_mode is None:
        return result
    shift=max(0,raw.bit_length()-24)
    quotient,remainder=divmod(raw,1<<shift)
    if shift:
        halfway=1<<(shift-1)
        upward=(rounding_mode=='toward_positive' and remainder!=0) or (
            rounding_mode=='nearest_even' and (remainder>halfway or remainder==halfway and quotient%2==1))
        quotient+=int(upward)
    stored_raw=quotient << shift
    # A rounded 2^63 reaches CVTT's overflow path. Do not cap or simulate it.
    if stored_raw>MAX_RAW:
        result['status']='unqualified_signed64_overflow';return result
    bits=struct.unpack('<I',struct.pack('<f',stored_raw/ONE))[0]
    value=struct.unpack('<f',struct.pack('<I',bits))[0]
    readback=float32_number_raw(bits)
    assert readback==stored_raw
    result.update(stored_float32_bits=bits,stored_float32=value,readback_raw=readback,
        readback_minus_math_raw=readback-raw,status='conditional_reference')
    return result


def shield_product_reference(max_hp_raw, ratio_raw, rounding_mode):
    _raw(max_hp_raw);_raw(ratio_raw)
    if not source_valid():
        return {'max_hp_raw':max_hp_raw,'ratio_raw':ratio_raw,'product_raw':None,
            'storage':None,'shield_readback_raw':None,'status':'unknown_source'}
    product=(max_hp_raw*ratio_raw) >> 32
    if product>MAX_RAW:
        return {'max_hp_raw':max_hp_raw,'ratio_raw':ratio_raw,'product_raw':None,
            'storage':None,'shield_readback_raw':None,'status':'unqualified_product_overflow'}
    storage=blackboard_storage_reference(product,rounding_mode)
    return {'max_hp_raw':max_hp_raw,'ratio_raw':ratio_raw,'product_raw':product,
        'storage':storage,'shield_readback_raw':storage['readback_raw'],'status':storage['status']}
