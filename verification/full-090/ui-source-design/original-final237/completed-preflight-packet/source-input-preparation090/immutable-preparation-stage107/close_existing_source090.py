"""Read existing saved085 shape and derive source spans, without product calls."""
import ast
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
source = Path('/workspace/.continuation/ui-085-draft/public-schema-final-085.json.gz')
raw = source.read_bytes()
saved = json.loads(gzip.decompress(raw))
rows = [row for row in saved['records'] if row['input']['operator'] == 'char_1048_orchd2'
        and row.get('result') is not None]
row = rows[0]
result = row['result']
keys = ['attack', 'total_damage', 'total_healing', 'components', 'estimate', 'report']
assert all(key in result for key in keys)
references = {key: value for key, value in result.items() if key.endswith('_reference')}
receipt = {
    'scope': 'Read-only actual085 preflight saved shape for Orchid; no new calls or fresh86 evidence',
    'root085_source_commit': saved['root_commit'],
    'source_file': str(source), 'source_file_sha256': hashlib.sha256(raw).hexdigest(),
    'saved_case_section': row['section'], 'saved_case_input': row['input'],
    'required_result_key_types': {key: type(result[key]).__name__ for key in keys},
    'estimate_skill_key_types': {key: type(value).__name__ for key, value in result['estimate']['skill'].items()},
    'actual_saved_unknown_references': references,
    'application_API_calls': 0, 'production_helper_calls': 0, 'formatter_calls': 0,
    'Qt_calls': 0, 'Wine_calls': 0,
}
(HERE / 'existing085-orchid-shape-reference090.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n')

contract_path = HERE / 'source-producer-contracts090.json'
contracts = json.loads(contract_path.read_bytes())
spans = {}
for name, functions in [('rouge/operator_engine.py', ['selected_talents']),
                        ('rouge/app.py', ['training_conditions', 'update_operator', 'update_skill_options'])]:
    tree = ast.parse((HERE / 'source085' / name).read_bytes())
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in functions:
            spans[node.name] = {'path': name, 'first_line': node.lineno, 'last_line': node.end_lineno}
assert len(spans) == 4
contracts['exact_function_source_spans'] = spans
contracts['shared_producer_source_ranges']['skill_and_module_gates'] = spans['selected_talents']
contract_path.write_text(json.dumps(contracts, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'saved085_orchid_reference_written': True, 'exact_AST_source_spans': 4,
                  'new_API_helper_formatter_Qt_Wine_calls': 0}))
