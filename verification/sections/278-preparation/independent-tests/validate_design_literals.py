"""Check manually listed preparation literals without importing the candidate core."""
from fractions import Fraction
from pathlib import Path
import hashlib
import json
import struct


BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]


def exact_single(bits):
    return Fraction.from_float(struct.unpack('>f', bytes.fromhex(bits))[0])


def nearest_even(value):
    sign = -1 if value < 0 else 1
    num, den = abs(value).as_integer_ratio()
    whole, remainder = divmod(num, den)
    if 2 * remainder > den or (2 * remainder == den and whole % 2):
        whole += 1
    return sign * whole


def main():
    literals_file = BASE / 'literal-boundaries.json'
    value = json.loads(literals_file.read_text(encoding='utf-8'))
    checks = []
    for row in value['single_transform_cases']:
        if 'exact_Single' in row:
            cost = Fraction(row['cost_int32'])
            operand = exact_single(row['operand_bits'])
            result = cost * operand if row['operation'] == 'multiply' else cost + operand
            assert result == Fraction(row['exact_Single']), row['id']
            packed = struct.pack('>f', float(result))
            assert Fraction.from_float(struct.unpack('>f', packed)[0]) == result, row['id']
            assert nearest_even(result) == row['encoder_argument_int32'], row['id']
            checks.append({'id': row['id'], 'exact_rational_Single_and_round_checked': True})
        elif 'allowed_neighbor_Singles' in row:
            exact = Fraction(row['cost_int32']) * exact_single(row['operand_bits'])
            left, right = map(Fraction, row['allowed_neighbor_Singles'])
            assert left < exact < right, row['id']
            left_bits = struct.unpack('>I', struct.pack('>f', float(left)))[0]
            right_bits = struct.unpack('>I', struct.pack('>f', float(right)))[0]
            assert abs(left_bits - right_bits) == 1, row['id']
            actual_rounds = [nearest_even(left), nearest_even(right)]
            assert actual_rounds == row['allowed_round_integers'], row['id']
            resolved = actual_rounds[0] if actual_rounds[0] == actual_rounds[1] else None
            assert resolved == row['encoder_argument_int32'], row['id']
            checks.append({'id': row['id'], 'rational_bracket_adjacent_Singles_checked': True})
        else:
            # Rejection/unknown controls are design requirements, not a running core result.
            checks.append({'id': row['id'], 'design_unknown_only': True})
    for row in value['signed32_scale_cases']:
        low = row['cost_int32'] * row['scale_int32'] % 4294967296
        signed = low if low < 2147483648 else low - 4294967296
        assert signed == row['encoder_argument_int32'], row['id']
        checks.append({'id': row['id'], 'low32_literal_checked': True})
    inputs = {
        str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [
            literals_file,
            BASE / 'ACCEPTANCE_DESIGN.md',
            ROOT / '.cache/research/p2-skill-data-modifiers-278/SOURCE_GATE.md',
            ROOT / '.cache/section278-independent-cost-source/cost-source-review.json',
        ]
    }
    receipt = {
        'kind': 'INDEPENDENT278_DESIGN_LITERAL_SELF_CHECK',
        'preparation_only': True,
        'core_imported': False,
        'native_game_execution': False,
        'MXCSR_assumed': False,
        'schema_stable': False,
        'single_design_rows': len(value['single_transform_cases']),
        'signed32_scale_design_rows': len(value['signed32_scale_cases']),
        'numeric_design_rows': len(checks),
        'checks': checks,
        'input_sha256': inputs,
        'independent_future_decoded_cost_or_live_SP': None,
    }
    path = BASE / 'design-literal-self-check.json'
    path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'design_rows': len(checks), 'single_rows': len(value['single_transform_cases']),
                      'scale_rows': len(value['signed32_scale_cases']), 'receipt': str(path),
                      'core_imported': False, 'schema_stable': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
