"""Execute exactly the frozen three public cases in one isolated source tree."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys

OUT = Path(__file__).resolve().parent

def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)

def native(value):
    if value is None: return ['none']
    if type(value) is bool: return ['bool', value]
    if type(value) is int: return ['int', str(value)]
    if type(value) is float: return ['float', value.hex()]
    if type(value) is str: return ['str', value]
    if type(value) is list: return ['list', [native(v) for v in value]]
    if type(value) is tuple: return ['tuple', [native(v) for v in value]]
    if type(value) is dict: return ['dict', [[native(k), native(v)] for k, v in value.items()]]
    raise TypeError('Unsupported native public result type: ' + type(value).__name__)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def files(tree):
    return {p.relative_to(tree).as_posix(): sha(p.read_bytes())
            for p in sorted(tree.rglob('*')) if p.is_file() and p.suffix in ('.py', '.json')}

args = argparse.ArgumentParser()
args.add_argument('tree', choices=('baseline', 'draft'))
mode = args.parse_args().tree
tree = OUT / (mode + '-tree')
result_file = OUT / ('public-' + mode + '.json')
if result_file.exists():
    raise RuntimeError('Existing public run receipt; do not repeat passed entries')
freeze = json.loads((OUT / 'pre-execution-freeze.json').read_text())
for entry in freeze['artifacts']:
    raw = (OUT / entry['path']).read_bytes()
    if len(raw) != entry['bytes'] or sha(raw) != entry['sha256']:
        raise RuntimeError('Frozen input changed before public execution: ' + entry['path'])
before = files(tree)
plan = json.loads((OUT / 'validation-plan.json').read_text())
cases = plan['cases']
if len(cases) != 3:
    raise RuntimeError('Expected exactly three budgeted public cases')
sys.dont_write_bytecode = True
sys.path.insert(0, str(tree))
from rouge.damage import calculate_damage
import rouge.damage
if Path(rouge.damage.__file__).resolve() != tree / 'rouge/damage.py':
    raise RuntimeError('Public calculation imported the wrong isolated package')
if mode == 'draft':
    from rouge.reporting import format_report

receipt = {'status': 'RUNNING', 'tree': mode, 'source_before': before, 'records': [],
           'public_API_entries': 0, 'explicit_formatter_entries': 0,
           'explicit_project_helper_entries': 0, 'tests': 0, 'Qt': 0, 'Wine': 0,
           'old_count63_matrix_replays': 0, 'native_mechanism_certified': False}

def save():
    result_file.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')

save()
for index, case in enumerate(cases):
    scenario = copy.deepcopy(case['input'])
    before_json = canonical(scenario)
    before_native = native(scenario)
    record = {'id': case['id'], 'input': copy.deepcopy(scenario),
              'input_json_before': before_json, 'input_native_before': before_native,
              'public_API_entry': index + 1}
    receipt['public_API_entries'] += 1
    try:
        result = calculate_damage(scenario)
        record['status'] = 'returned'
        record['result_native'] = native(result)
        record['result_json'] = canonical(result)
        record['result'] = result
        if mode == 'draft':
            receipt['explicit_formatter_entries'] += 1
            formatted = format_report(result)
            record['formatted_native'] = native(formatted)
            record['formatted_text'] = formatted
            record['formatter_preserved_result_native'] = native(result) == record['result_native']
            record['formatter_preserved_result_json'] = canonical(result) == record['result_json']
            text_file = OUT / ('draft-text-' + str(index + 1) + '.txt')
            if text_file.exists():
                raise RuntimeError('Existing formatter text receipt')
            text_file.write_text(formatted + '\n', encoding='utf-8')
            record['formatted_text_archive_path'] = text_file.name
            record['formatted_text_file_sha256'] = sha(text_file.read_bytes())
    except Exception as error:
        record['status'] = 'raised'
        record['exception'] = {'type': type(error).__name__, 'message': str(error)}
    record['input_json_after'] = canonical(scenario)
    record['input_native_after'] = native(scenario)
    record['caller_json_unchanged'] = record['input_json_after'] == before_json
    record['caller_native_unchanged'] = record['input_native_after'] == before_native
    receipt['records'].append(record)
    receipt['source_after'] = files(tree)
    receipt['source_unchanged'] = receipt['source_after'] == before
    save()
    if record['status'] != 'returned' or not record['caller_json_unchanged'] or not record['caller_native_unchanged'] or not receipt['source_unchanged']:
        raise RuntimeError('Stop after genuine public-entry failure; preserve diagnostic: ' + case['id'])
    if mode == 'draft' and not (record['formatter_preserved_result_native'] and record['formatter_preserved_result_json']):
        raise RuntimeError('Formatter changed a public result; stop and preserve receipt')
receipt['status'] = 'THREE_PUBLIC_ENTRIES_COMPLETE'
save()
print(json.dumps({'status': receipt['status'], 'tree': mode,
                  'public_API_entries': receipt['public_API_entries'],
                  'formatter_entries': receipt['explicit_formatter_entries'],
                  'caller_and_source_unchanged': True, 'public_receipt_sha256': sha(result_file.read_bytes())}))
