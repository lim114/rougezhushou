"""Supplement the newly clarified tiny-normal integer boundary, no suite rerun."""
from fractions import Fraction
from pathlib import Path
import hashlib
import importlib.util
import json

HERE = Path(__file__).resolve().parent
module = HERE / 'rouge/panel_native_precision.py'
spec = importlib.util.spec_from_file_location('numeric283_tiny', module)
subject = importlib.util.module_from_spec(spec)
spec.loader.exec_module(subject)
rows = []
for bits in (0x00800000, 0x80800000, 0x23800000, 0xa3800000):
    result = subject.single_integer_reference(bits)
    assert result['complete'] is True and result['integer_consensus'] == 0
    exponent = ((bits >> 23) & 255) - 127
    magnitude = Fraction(1, 1 << -exponent)
    assert 0 < magnitude < Fraction(1, 1 << 53)
    # The exact offset lies near +/-0.5 and all adjacent Double outcomes are
    # strictly between 0 and1 in magnitude. Floor/ceil cannot cross +/-1.
    assert Fraction(0) < Fraction(1, 2) - magnitude
    assert Fraction(1, 2) + magnitude < Fraction(1)
    rows.append({'input_bits': bits, 'magnitude_numerator': magnitude.numerator,
                 'magnitude_denominator': magnitude.denominator,
                 'expected_integer': 0, 'actual_reference': result,
                 'half_offset_is_claimed_exact': False})
output = HERE / 'tiny-normal-supplement-283.json'
assert not output.exists(), 'preserve first tiny-normal supplement'
data = {'kind': 'SECTION283_TINY_NORMAL_WRITER_INTEGER_BOUNDARY_SUPPLEMENT',
        'module_sha256': hashlib.sha256(module.read_bytes()).hexdigest(),
        'rows': rows, 'fixed_literal_count': 4,
        'normal_integer_result_not_arithmetic_exactness': True,
        'actual_rc_or_masks_proven': False, 'actual_game_observation': False}
output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps({'output': str(output), 'rows': len(rows),
                  'sha256': hashlib.sha256(output.read_bytes()).hexdigest()}, ensure_ascii=False))
