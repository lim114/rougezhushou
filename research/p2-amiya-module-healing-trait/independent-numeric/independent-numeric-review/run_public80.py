"""One actual public call per scenario, with full JSON and three reports."""
import copy
import hashlib
import json
import os
from pathlib import Path
import sys

OUT = Path(__file__).resolve().parent
kind = sys.argv[1]
assert kind in ('baseline', 'draft')
assert os.environ.get('PYTHONHASHSEED') == '0'
root = Path('/workspace/.continuation/p2-amiya-trait-scale-080') / kind
sys.path.insert(0, str(root))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.reporting import format_report

freeze = json.loads((OUT / 'freeze080.json').read_text())
for rel, entry in freeze['sources'].items():
    assert hashlib.sha256((root / rel).read_bytes()).hexdigest() == entry[kind + '_sha256'], rel
original_catalog = copy.deepcopy(catalog())
rows = []
for case in json.loads((OUT / 'cases080.json').read_text()):
    scenario = copy.deepcopy(case['scenario'])
    before = copy.deepcopy(scenario)
    row = {'label': case['label'], 'scenario': scenario}
    try:
        result = calculate_damage(scenario)
        row.update(result=result, estimate_text=format_estimate(result),
                   report_text=format_report(result), technical_report_text=format_report(result, technical=True))
    except (ValueError, TypeError) as exc:
        row['error'] = {'type': type(exc).__name__, 'message': str(exc)}
    assert scenario == before, case['label']
    rows.append(row)
assert catalog() == original_catalog
for rel, entry in freeze['sources'].items():
    assert hashlib.sha256((root / rel).read_bytes()).hexdigest() == entry[kind + '_sha256'], rel
target = OUT / (kind + '-public080.json')
with target.open('x', encoding='utf-8') as stream:
    json.dump(rows, stream, ensure_ascii=False, indent=2, allow_nan=False)
    stream.write('\n')
print(json.dumps({'status': 'completed_actual_public_calls', 'kind': kind, 'public_calls': len(rows),
                  'accepted': sum('result' in row for row in rows), 'errors': sum('error' in row for row in rows),
                  'input_catalog_source_unchanged': True, 'hash_seed': '0'}))
