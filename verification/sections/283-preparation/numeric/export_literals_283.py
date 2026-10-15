"""Archive fixed expected literals and actual per-RC numeric classifications."""
from pathlib import Path
import hashlib
import importlib.util
import json

HERE = Path(__file__).resolve().parent
test_path = HERE / 'verify_numeric_283.py'
core_path = HERE / 'rouge/panel_native_precision.py'
spec = importlib.util.spec_from_file_location('numeric283_literal_inputs', test_path)
tests = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tests)
rows = []
for raw, bits, integers, complete, consensus in tests.LITERALS:
    fp = tests.subject.fp_single_reference(raw)
    integer = tests.subject.writer_integer_reference(raw)
    assert fp['single_bits_candidates'] == bits
    assert integer['integer_candidates'] == integers
    assert integer['complete'] is complete
    assert integer['integer_consensus'] == consensus
    rows.append({'input_raw': raw,
                 'fixed_expected': {'single_bits_candidates': bits, 'integer_candidates': integers,
                                    'complete': complete, 'integer_consensus': consensus},
                 'actual_fp_reference': fp, 'actual_writer_reference': integer,
                 'actual_per_rc_integer': [
                     {'conversion_rc': c['conversion_rc'], **tests.subject.single_integer_reference(c['bits'])}
                     for c in fp['candidates']]})
result = {'kind': 'SECTION283_FIXED_LITERAL_AND_ACTUAL_NUMERIC_PREPARATION_READBACK',
          'core_sha256': hashlib.sha256(core_path.read_bytes()).hexdigest(),
          'literal_test_sha256': hashlib.sha256(test_path.read_bytes()).hexdigest(),
          'fixed_literal_count': len(rows), 'rows': rows,
          'candidate_is_actual_game_observation': False,
          'actual_RC_or_exception_masks_proven': False,
          'is_final_independent_acceptance': False,
          'encoding_decode_equality_assumed': False}
output = HERE / 'fixed-literal-readback-283.json'
assert not output.exists(), 'preserve first actual literal export'
output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps({'output': str(output), 'literal_count': len(rows),
                  'sha256': hashlib.sha256(output.read_bytes()).hexdigest()}, ensure_ascii=False))
