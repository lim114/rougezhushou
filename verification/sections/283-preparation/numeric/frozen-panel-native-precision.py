"""Conditional signed64 FP-to-Single and pre-encoder Int32 references.

No host floating point, actual MXCSR, codec equality or runtime observation is
used. The parent workflow must freshly bind this module and its source proof.
The unnamed half-even helper is qualified only in the writer's signed32 domain.
"""
from fractions import Fraction

_Q = 1 << 32


def _integer(value, bits, unsigned=False):
    if value is None:
        return
    lo, hi = (0, 1 << bits) if unsigned else (-(1 << (bits - 1)), 1 << (bits - 1))
    if type(value) is not int or not lo <= value < hi:
        raise ValueError('strict integer width required')


def _power2(exponent):
    return Fraction(1 << exponent) if exponent >= 0 else Fraction(1, 1 << -exponent)


def _normal_fraction(bits):
    exponent, significand = (bits >> 23) & 255, bits & 0x7fffff
    if exponent == 255:
        return None, 'nonfinite_environment_unknown'
    if exponent == 0:
        return (Fraction(0), None) if significand == 0 else (None, 'subnormal_environment_unknown')
    value = Fraction((1 << 23) + significand) * _power2(exponent - 150)
    return (-value if bits >> 31 else value), None


def _integer_to_single_bits(value, rc):
    """All signed64 inputs are finite normal or canonical positive zero."""
    if value == 0:
        return 0
    negative, magnitude = value < 0, abs(value)
    exponent = magnitude.bit_length() - 1
    if exponent <= 23:
        significand = magnitude << (23 - exponent)
    else:
        step = 1 << (exponent - 23)
        significand, remainder = divmod(magnitude, step)
        if rc == 0:
            up = remainder * 2 > step or (remainder * 2 == step and significand & 1)
        elif rc == 1:
            up = negative and remainder != 0
        elif rc == 2:
            up = not negative and remainder != 0
        else:
            up = False
        significand += int(bool(up))
        if significand == 1 << 24:
            exponent += 1
            significand >>= 1
    return (0x80000000 if negative else 0) | ((exponent + 127) << 23) | (significand - (1 << 23))


def fp_single_reference(raw):
    """Enumerate signed64 CVTSI2SS RC0..3, then exact Single MULSS 2^-32.

    Complete means all normal-result branches are covered, not unique bits.
    Every nonzero result has magnitude at least 2^-32; no subnormal branch or
    actual exception-mask/RC setting is inferred.
    """
    _integer(raw, 64)
    result = {'input_raw': raw, 'complete': False, 'single_bits_candidates': [],
              'candidates': [], 'reason': 'unknown_input' if raw is None else None}
    if raw is None:
        return result
    for rc in range(4):
        converted = _integer_to_single_bits(raw, rc)
        # Multiplication by 2^-32 only changes the normal exponent. Signed64
        # integer conversion has exponent0..63; scaled exponent is -32..31.
        bits = 0 if converted == 0 else converted - (32 << 23)
        result['candidates'].append({'conversion_rc': rc, 'bits': bits})
    result['single_bits_candidates'] = sorted({c['bits'] for c in result['candidates']})
    result['complete'] = True
    if len(result['single_bits_candidates']) != 1:
        result['reason'] = 'multiple_single_candidates'
    return result


def _half_even(value):
    lower, remainder = divmod(value.numerator, value.denominator)
    return lower + int(remainder * 2 > value.denominator or
                       (remainder * 2 == value.denominator and lower & 1))


def single_integer_reference(bits):
    """Independent normal/zero Single -> conditional half-even Int32 argument.

    Out-of-domain conversion is not reinterpreted as an ordinary indefinite
    Int32 value. Normality of calls, protected encoding and future decode remain
    independent in the parent workflow.
    """
    _integer(bits, 32, unsigned=True)
    result = {'input_bits': bits, 'complete': False, 'integer_candidates': [],
              'integer_consensus': None, 'reason': 'unknown_input' if bits is None else None}
    if bits is None:
        return result
    value, reason = _normal_fraction(bits)
    if reason:
        return {**result, 'reason': reason}
    # Only the safe writer domain is claimed for the anonymous Double helper.
    # All Single values outside this envelope round outside signed32. Avoid
    # extending the helper proof to huge finite Single values (>2^53).
    if value < -(1 << 31) - 1 or value > (1 << 31):
        return {**result, 'reason': 'int32_out_of_domain'}
    rounded = _half_even(value)
    if not -(1 << 31) <= rounded < (1 << 31):
        return {**result, 'reason': 'int32_out_of_domain'}
    return {**result, 'complete': True, 'integer_candidates': [rounded],
            'integer_consensus': rounded, 'reason': None}


def writer_integer_reference(raw):
    """FP overload -> Single -> half-even -> signed32 pre-encoder consensus."""
    fp = fp_single_reference(raw)
    result = {'input_raw': raw, 'complete': False, 'integer_candidates': [],
              'integer_consensus': None,
              'single_bits_candidates': fp['single_bits_candidates'], 'reason': fp['reason']}
    if not fp['complete']:
        return result
    candidates = [single_integer_reference(c['bits']) for c in fp['candidates']]
    result['integer_candidates'] = sorted({integer for candidate in candidates
                                           for integer in candidate['integer_candidates']})
    if not all(c['complete'] for c in candidates):
        return {**result, 'reason': 'int32_out_of_domain'}
    result['complete'] = True
    if len(result['integer_candidates']) == 1:
        result['integer_consensus'] = result['integer_candidates'][0]
        result['reason'] = None
    else:
        result['reason'] = 'multiple_integer_candidates'
    return result
