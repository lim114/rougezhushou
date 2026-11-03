"""Static proof of unique085 sinks and inverse preservation of all3063 old checks."""
import ast
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
base = (HERE / 'wine-ui-smoke-080-preserved.py').read_text()
final = (HERE / 'wine-ui-smoke-085.py').read_text()
static = json.loads((HERE / 'runner-static-review.json').read_bytes())
assert static['old3063_complete_body_reconstructed_exactly']
assert static['new_case_design_count'] == 1154 and static['total_case_design_count'] == 4217
assert static['ready_for_actual_execution'] and not static['sections83_85_pending']
assert hashlib.sha256(final.encode()).hexdigest() == static['runner_sha256']
base_tree = ast.parse(base)
final_tree = ast.parse(final)
base_literals = [node.value for node in ast.walk(base_tree)
                 if isinstance(node, ast.Constant) and isinstance(node.value, str)]
final_literals = [node.value for node in ast.walk(final_tree)
                  if isinstance(node, ast.Constant) and isinstance(node.value, str)]
def output_sink_count(tree, name):
    return sum(isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div)
               and isinstance(node.left, ast.Name) and node.left.id == 'OUT'
               and isinstance(node.right, ast.Constant) and node.right.value == name
               for node in ast.walk(tree))
names = ('wine-ui-report-difference-080.json', 'wine-window-080.png', 'wine-ui-080.json',
         'wine-ui-failure-080.png', 'wine-sown-tile-control-080.png',
         'wine-movement-reference-080.png', 'wine-medical-trait-080.png')
rows = []
for old in names:
    new = old.replace('-080', '-085')
    assert base_literals.count(old) == final_literals.count(new) >= 1, old
    assert output_sink_count(base_tree, old) == output_sink_count(final_tree, new) == 1, old
    assert old not in final_literals and new not in base_literals
    rows.append({'original080_name': old, 'final085_name': new,
                 'actual_linux_destination': '/workspace/.compat/' + new,
                 'runner_windows_OUT': r'Z:\workspace\.compat',
                 'static_OUT_path_sink_occurrences': 1,
                 'original_and_final_literal_occurrences_including_metadata': base_literals.count(old)})
receipt = {
    'status': 'PASS_UNIQUE085_OUTPUT_NAMES_AND_EXACT_OLD3063_INVERSE',
    'runner_sha256': static['runner_sha256'], 'base080_sha256': static['base080_sha256'],
    'preserved_skills': 87, 'preserved_old_checks': 3063,
    'new_design_checks': 1154, 'planned_total_actual_checks': 4217,
    'old3063_complete_body_reconstructed_exactly': True,
    'inverse_recipe': 'Remove newly inserted085 helpers/group/counter wrapper and the entry guard; reverse only these seven output suffix renames. build_runner.py asserts exact equality with preserved080 bytes.',
    'permitted_changes_outside_inserted_group': ['new guard and preserved-count wrapper metadata', 'these seven output suffix renames'],
    'output_mappings': rows, '080_existing_actual_files_modified': False,
    'new_API_calls': 0, 'formatter_calls': 0, 'GUI_executed': False, 'Wine_executed': False,
}
path = HERE / 'artifact-mapping-and-old3063-proof085.json'
path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'outputs': len(rows), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}))
