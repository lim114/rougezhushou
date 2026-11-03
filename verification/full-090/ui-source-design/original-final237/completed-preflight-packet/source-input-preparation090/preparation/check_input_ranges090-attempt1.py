"""Bind the approved eight inputs to the real widget constructors, without Qt."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
APP = HERE / 'source-production-boundary87/app.py'
PLAN = HERE / 'additional8-input-plan090.json'

def describe(path):
    raw = path.read_bytes()
    return {'source_path': str(path), 'bytes': len(raw),
            'sha256': hashlib.sha256(raw).hexdigest()}

assert not (HERE / 'input-range-proof090.json').exists()
app = APP.read_text()
tree = ast.parse(app)
number = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'number')
assert [a.arg for a in number.args.args] == ['value', 'maximum', 'decimals']
assert 'control.setRange(0, maximum)' in ast.get_source_segment(app, number)
assert 'control.setDecimals(decimals)' in ast.get_source_segment(app, number)
assert 'self.window_seconds = number(40,3600,2)' in app
assert 'self.deployment_elapsed=number(0,3600,2)' in app
assert 'self.defense = number(0,100000,0)' in app
assert 'self.resistance = number(0,100,1)' in app
assert 'self.healing_targets.setRange(0,100);self.healing_targets.setValue(1)' in app
assert 'self.timing_scenario=QPlainTextEdit()' in app
assert "form.addRow('战斗时序情景（测试，可留空）', self.timing_scenario)" in app
assert "scenario['timing']=json.loads(self.timing_scenario.toPlainText())" in app
assert "if not isinstance(scenario['timing'],dict)" in app
plan = json.loads(PLAN.read_bytes())
assert len(plan['cases']) == 8
for row in plan['cases']:
    value = row['input']
    assert type(value['continuous_attacks']) is bool
    assert type(value['window_seconds']) is float and value['window_seconds'] == 12.75
    assert 0 <= value['window_seconds'] <= 3600 and round(value['window_seconds'], 2) == value['window_seconds']
    assert value['deployment_elapsed_seconds'] == 0.0
    assert value['enemy_defense'] == 0.0 and value['enemy_resistance'] == 0.0
    assert value['healing_targets'] == 1
    assert 'base_attack' not in value
empty = [r['input']['timing'] for r in plan['cases']
         if r['pair_id'] == '088-hidden-checkbox-amiya-E0-S1-empty-target-reference']
assert len(empty) == 2 and empty == [{'target_windows': []}, {'target_windows': []}]
receipt = {
    'status': 'PASS_REAL_WIDGET_INPUT_RANGE_AND_TIMING_EDITOR_SOURCE_ONLY',
    'actual_producer_commit': '6191cc76ecf2a907493dd8347dcecb7b0d6bc4d0',
    'plan': describe(PLAN), 'actual_app_snapshot': describe(APP),
    'number_factory': {'default_value_not_minimum': True, 'minimum': 0,
        'window_maximum': 3600, 'window_decimals': 2,
        'window_initial_value': 40, 'requested_value': 12.75},
    'real_QPlainTextEdit_JSON_empty_target_object_is_expressible': True,
    'empty_target_actual_widget_execution_pending': True,
    'readonly_auto_base_attack_preserved_no_manual_control': True,
    'eight_typed_bool_inputs': True,
    'application_API_helpers_formatter_RunState_constructor_apply_Qt_Wine_tests_calls': 0,
    'actual088_source_transport_still_required_before_new8_API': True,
}
(HERE / 'input-range-proof090.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(describe(HERE / 'input-range-proof090.json'), ensure_ascii=False))
