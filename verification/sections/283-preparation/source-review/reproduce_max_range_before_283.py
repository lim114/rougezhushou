"""Actual old-core counterexample; not a final implementation acceptance run."""
from pathlib import Path
import hashlib
import importlib.util
import json
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREP = ROOT / '.cache/section283-preparation'
path = PREP / 'rouge/panel_native_finalization.py'
raw = path.read_bytes()
assert hashlib.sha256(raw).hexdigest() == '3e331ca187d419521fa220a6c8698e745d19f79a2a425d60bddbf14a81415853'
sealed = HERE / 'core-original-3e331ca1.py'
assert not sealed.exists(); sealed.write_bytes(raw)
np = ROOT / '.cache/section283-numeric/rouge/panel_native_precision.py'
assert hashlib.sha256(np.read_bytes()).hexdigest() == '878347f7f5d69d09535f1bf0aec409068c68a3cdcf54812091c7deb96be838fc'
ns = HERE / 'numeric-original-878347f7.py'
assert not ns.exists(); ns.write_bytes(np.read_bytes())
sys.path.insert(0, str(ROOT))
import rouge
rouge.__path__.insert(0, str(PREP / 'rouge'))
spec = importlib.util.spec_from_file_location('rouge._283_range_original', path)
core = importlib.util.module_from_spec(spec); spec.loader.exec_module(core)
assert core.source_data() is not None
payload = {'fields': [{'id': 'ordinary_attack_at_signed64_max', 'field': 'attack', 'phase': 'normal',
    'model_value': None, 'basis_kind': 'nominal_fp', 'basis_single_bits': None,
    'basis_fp_raw': 9223372036854775807, 'addition_raw': 0, 'multiplier_delta_raw': 0,
    'final_addition_raw': 0, 'final_scaler_raw': 4294967296}]}
actual = core.panel_native_finalization(payload)
row = actual['fields'][0]
report = {'kind': 'ACTUAL_OLD_CORE283_FP_MAX_RANGE_COUNTEREXAMPLE',
    'core_sha256': hashlib.sha256(raw).hexdigest(),
    'numeric_sha256': hashlib.sha256(np.read_bytes()).hexdigest(),
    'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'input': payload, 'actual_output': actual,
    'expected_metadata_upper_raw': 9223372036854775806,
    'expected_conditional_getter_raw': 9223372036854775806,
    'actual_metadata_upper_raw': row['metadata_range']['upper_raw'],
    'actual_conditional_getter_raw': row['references']['getter_result_raw'],
    'counterexample_reproduced': row['metadata_range']['upper_raw'] == 9223372036854775807 and row['references']['getter_result_raw'] == 9223372036854775807,
    'evidence': 'source-gates-283.json default FP.MaxValue bounds;273 default ranges;mechanist_explosion_math MAX_RAW is width maximum, not FP.MaxValue',
    'game_dll_executed': False, 'process_memory_read': False, 'prototype_or_production_modified': False,
    'scope': 'One real public pure-function before repair counterexample. Not complete QA or final acceptance.'}
out = HERE / 'max-range-original-counterexample-283.json'
assert not out.exists(); out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'counterexample_reproduced':report['counterexample_reproduced'],'actual':row['references']['getter_result_raw'], 'expected':report['expected_conditional_getter_raw'],'receipt_sha256':hashlib.sha256(out.read_bytes()).hexdigest()},ensure_ascii=False))
assert report['counterexample_reproduced']
