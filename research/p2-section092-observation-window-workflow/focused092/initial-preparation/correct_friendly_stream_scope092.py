"""Source-only correction: no project import, API, formatter, test, Qt or Wine."""
from pathlib import Path
import ast
import copy
import hashlib
import json

HERE = Path(__file__).resolve().parent
PENDING = HERE / 'wine-focused-window-092-pending.py'
PLAN = HERE / 'focused-window-plan092.json'
TIMING = Path('/workspace/rougezhushou/rouge/timing.py')
SEALER = HERE / 'seal_focused_window092.py'
PREPARATION = HERE
ORIGINAL_SHA256 = '54cec392f36e8bcb97b51dcc404ff8150f4c49a4011d3b3f63fc1fac72b2223b'
ORIGINAL_SEALER_SHA256 = 'ad5a120e5f5c3490add45774b800b5ac50ff3050d09ea0199fbb794729897cca'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def descriptor(path):
    data = path.read_bytes()
    return {'source_path': str(path), 'bytes': len(data), 'sha256': sha(data)}


def named_call(node, owner, method):
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and ast.unparse(node.func.value) == owner and node.func.attr == method)


original_bytes = PENDING.read_bytes()
assert sha(original_bytes) == ORIGINAL_SHA256
original = original_bytes.decode('utf-8')
tree = ast.parse(original)
friendly_nodes = [node for node in ast.walk(tree)
                  if isinstance(node, ast.If)
                  and ast.unparse(node.test) == "current.startswith('kaltsit-S3-friendly')"]
assert len(friendly_nodes) == 1
friendly = friendly_nodes[0]
assert len(friendly.body) == 4
stream_assert = friendly.body[1]
assert isinstance(stream_assert, ast.Assert)
assert ast.unparse(stream_assert.test) == "any((s['target_scope'] == 'friendly' for s in result['timing']['streams']))"
assert stream_assert.lineno == stream_assert.end_lineno
lines = original.splitlines(keepends=True)
old_line = lines[stream_assert.lineno - 1]
indent = old_line[:len(old_line) - len(old_line.lstrip())]
assert indent == ' ' * 20
assert old_line == indent + "assert any(s['target_scope']=='friendly' for s in result['timing']['streams'])\n"
new_lines = [indent + "if row['mode']=='frames':\n", '    ' + old_line]
lines[stream_assert.lineno - 1:stream_assert.lineno] = new_lines
corrected = ''.join(lines)
assert corrected.replace(''.join(new_lines), old_line, 1) == original
corrected_tree = ast.parse(corrected)
expected_tree = copy.deepcopy(tree)
expected_friendly = next(node for node in ast.walk(expected_tree)
                         if isinstance(node, ast.If)
                         and ast.unparse(node.test) == "current.startswith('kaltsit-S3-friendly')")
expected_friendly.body[1] = ast.If(
    test=ast.parse("row['mode']=='frames'", mode='eval').body,
    body=[expected_friendly.body[1]], orelse=[])
assert ast.dump(expected_tree, include_attributes=False) == ast.dump(corrected_tree, include_attributes=False)

timing_bytes = TIMING.read_bytes()
timing_source = timing_bytes.decode('utf-8')
timing_tree = ast.parse(timing_source)
attacks = [node for node in ast.walk(timing_tree)
           if isinstance(node, ast.FunctionDef) and node.name == 'attacks']
assert len(attacks) == 1
attacks = attacks[0]
continuous = [node for node in attacks.body
              if isinstance(node, ast.If) and ast.unparse(node.test) == "self.mode == 'continuous'"]
assert len(continuous) == 1
continuous = continuous[0]
assert isinstance(continuous.body[-1], ast.Return)
assert ast.unparse(continuous.body[-1].value) == 'stream'
append_nodes = [node for node in ast.walk(continuous)
                if named_call(node, 'self.streams', 'append')]
assert len(append_nodes) == 1
append_guards = [node for node in continuous.body if isinstance(node, ast.If)
                 and ast.unparse(node.test) == 'deployment_speed'
                 and append_nodes[0] in list(ast.walk(node))]
assert len(append_guards) == 1
stream_assignments = [node for node in continuous.body
                      if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'stream' for t in node.targets)]
assert len(stream_assignments) == 1
stream_assignment = stream_assignments[0]
assert isinstance(stream_assignment.value, ast.Dict)
assert 'target_scope' in [key.value for key in stream_assignment.value.keys if isinstance(key, ast.Constant)]
friendly_child = attacks.body[0]
assert isinstance(friendly_child, ast.If)
assert ast.unparse(friendly_child.test) == 'target_scope is not None and target_scope != self.target_scope'
extend_nodes = [node for node in ast.walk(friendly_child)
                if named_call(node, 'self.streams', 'extend')]
assert len(extend_nodes) == 1
assert ast.unparse(extend_nodes[0].args[0]) == 'child.streams'
assert isinstance(friendly_child.body[-1], ast.Return)
assert ast.unparse(friendly_child.body[-1].value) == 'stream'

plan_bytes = PLAN.read_bytes()
plan = json.loads(plan_bytes)
assert len(plan['rows']) == 19
assert sum('error' not in row for row in plan['rows']) == 15
assert sum('error' in row for row in plan['rows']) == 4
assert sum(row.get('button', False) for row in plan['rows']) == 2
assert sum('screenshot' in row for row in plan['rows']) == 2

sealer_bytes = SEALER.read_bytes()
assert sha(sealer_bytes) == ORIGINAL_SEALER_SHA256
sealer_original = sealer_bytes.decode('utf-8')
role_replacements = [
    ('Sole independent source-only formal; root actual Wine once, then view actual two PNGs and archive receipt/native checkpoint. Preserve successful prefix if failure, same issue third failure deferred.',
     'Root-appointed final source-only reviewer pending; root actual Wine once after PASS, then view actual two PNGs and archive receipt/native checkpoint. Preserve successful prefix if failure, same issue third failure deferred.'),
    ('source080 source-only,0project calls; root executes one Wine acceptance after PASS',
     'root-appointed final source-only reviewer pending,0project calls; root executes one Wine acceptance after PASS'),
]
sealer_corrected = sealer_original
for old_role, new_role in role_replacements:
    assert sealer_corrected.count(old_role) == 1
    assert new_role not in sealer_corrected
    sealer_corrected = sealer_corrected.replace(old_role, new_role, 1)
reverse_sealer = sealer_corrected
for old_role, new_role in reversed(role_replacements):
    reverse_sealer = reverse_sealer.replace(new_role, old_role, 1)
assert reverse_sealer == sealer_original
ast.parse(sealer_corrected)

PREPARATION.mkdir(mode=0o700, exist_ok=True)
backup = PREPARATION / 'wine-focused-window-092-before-friendly-stream-scope-correction.py'
sealer_backup = PREPARATION / 'seal_focused_window092-before-reviewer-role-metadata-correction.py'
diagnostic = PREPARATION / 'friendly-stream-source-correction-diagnostic092.json'
assert not backup.exists() and not sealer_backup.exists() and not diagnostic.exists()
backup.write_bytes(original_bytes)
sealer_backup.write_bytes(sealer_bytes)
PENDING.write_text(corrected, encoding='utf-8')
SEALER.write_text(sealer_corrected, encoding='utf-8')
assert backup.read_bytes() == original_bytes
assert sealer_backup.read_bytes() == sealer_bytes
assert PLAN.read_bytes() == plan_bytes
proof = {
    'format_version': 1,
    'status': 'SOURCE_ONLY_FRIENDLY_STREAM_ASSERTION_FRAMES_SCOPE_CORRECTED_RUNTIME_UNRUN',
    'passed': True,
    'original_pending': descriptor(backup),
    'corrected_pending': descriptor(PENDING),
    'original_sealer': descriptor(sealer_backup),
    'corrected_sealer': descriptor(SEALER),
    'unchanged_plan': descriptor(PLAN),
    'source': descriptor(TIMING),
    'source_evidence': [
        {'boundary': 'friendly child extends actual child.streams and returns actual stream',
         'lines': [friendly_child.lineno, friendly_child.end_lineno],
         'text': ast.get_source_segment(timing_source, friendly_child)},
        {'boundary': 'continuous stream is returned; append only inside deployment_speed condition',
         'lines': [continuous.lineno, continuous.end_lineno],
         'text': ast.get_source_segment(timing_source, continuous)},
    ],
    'correction': {
        'original_line': stream_assert.lineno,
        'old': old_line,
        'new': ''.join(new_lines),
        'exact_reverse_recovers_original_body': True,
        'AST_only_one_conditional_wrapper_changed': True,
        'stream_presence_required_only_for_frames': True,
        'positive_healing_total_damage_zero_and_unknown_friendly_clock_retained_in_both_modes': True,
        'continuous_stream_not_fabricated': True,
        'all_19_inputs_unchanged': True,
    },
    'reviewer_role_metadata_correction': {
        'authorization': 'root explicitly approved preserving original sealer and correcting stale source080 formal attribution',
        'replacement_count': len(role_replacements),
        'replacements': [{'old': old_role, 'new': new_role} for old_role, new_role in role_replacements],
        'exact_reverse_recovers_original_sealer': True,
        'no_runtime_or_source730_pendingstage_change': True,
        'old_source080_preliminary_boundary_preserved': 'Parent identifies old source080 as one preliminary source boundary only; no independent final review.',
    },
    'previous_attempt': {
        'provenance': 'parent-carried continuation context; not a new observed product run',
        'tool_boundary': 'CreateProcess 409 environment_offline',
        'process_created': False,
        'correction_written': False,
        'new_project_API_calls': 0,
        'product_failure': False,
    },
    'project_imports': 0,
    'project_API_calls': 0,
    'project_helper_calls': 0,
    'formatter_calls': 0,
    'test_calls': 0,
    'Qt_calls': 0,
    'Wine_calls': 0,
    'runtime_validation': 'root only, after actual source guard and independent final source review',
}
diagnostic.write_text(json.dumps(proof, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')
print(json.dumps({'pending': descriptor(PENDING), 'original_backup': descriptor(backup),
                  'sealer': descriptor(SEALER), 'original_sealer_backup': descriptor(sealer_backup),
                  'diagnostic': descriptor(diagnostic), 'plan': descriptor(PLAN),
                  'source_only_AST_proof_passed': True, 'project_calls': 0}))
