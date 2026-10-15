"""Apply the authorized function-only edit after actual equivalence checks."""
import ast
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
path=ROOT/'rouge/event_planning.py'
before=(HERE/'before-event-planning.py').read_bytes()
candidate=(HERE/'candidate-event-planning.py').read_bytes()
proof=json.loads((HERE/'public-equivalence-and-profile.json').read_text(encoding='utf-8'))
if proof['failed_checks'] or proof['matrix_queries_per_module']!=570 or proof['event_groups']!=38:
    raise ValueError('Actual public comparison did not pass its required scope.')
if path.read_bytes()!=before:raise ValueError('Live source changed since the reviewed baseline; do not overwrite.')
def outside(raw):
    tree=ast.parse(raw.decode('utf-8'))
    return [ast.dump(n) for n in tree.body if not isinstance(n,ast.FunctionDef) or n.name!='choice_resources']
if outside(before)!=outside(candidate):raise ValueError('Candidate changes code outside the authorized function.')
path.write_bytes(candidate)
actual=path.read_bytes()
if actual!=candidate:raise ValueError('Applied source does not equal the validated candidate bytes.')
receipt={'scope':'Authorized only-choice_resources production maintenance edit, not a new section.',
    'before_sha256':hashlib.sha256(before).hexdigest(),'after_sha256':hashlib.sha256(actual).hexdigest(),
    'only_function_changed':'choice_resources','outside_function_ast_unchanged':True,
    'actual_public_equivalence_queries_each':570,'invalid_input_cases':27,
    'source_guard_policy':'Fresh qualification per external query; no cross-query cache or hash/typed fallback weakening.',
    'no_other_production_tests_research_docs_private_modified':True,'no_gui_or_full_run':True}
with (HERE/'applied-maintenance.json').open('x',encoding='utf-8') as stream:json.dump(receipt,stream,ensure_ascii=False,indent=2)
print(json.dumps(receipt,ensure_ascii=False))
