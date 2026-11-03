import copy
import hashlib
import json
import os
import sys
from pathlib import Path

OUT = Path(__file__).parent
tree, seed = sys.argv[1:3]
assert os.environ.get('PYTHONHASHSEED') == seed
sys.path.insert(0, str(OUT / tree))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.reporting import format_report

cases = json.loads((OUT / 'public-cases.json').read_text())
original_catalog = copy.deepcopy(catalog())
rows = []
for index, case in enumerate(cases):
    scenario = copy.deepcopy(case['scenario'])
    original = copy.deepcopy(scenario)
    candidate_references = []

    def trace(frame, event, arg):
        if (event == 'line' and frame.f_code.co_name == 'prepare' and
                frame.f_code.co_filename.endswith('/rouge/relics.py') and
                'candidates' in frame.f_locals and not candidate_references):
            candidate_references.append({key: copy.deepcopy(frame.f_locals[key])
                                         for key in ('rules', 'effects', 'token_effects', 'candidates')})
        return trace

    try:
        sys.settrace(trace)
        result = calculate_damage(scenario)
        sys.settrace(None)
        row = {'index': index, 'label': case['label'], 'scenario': scenario,
               'result': result, 'estimate_text': format_estimate(result),
               'report_text': format_report(result),
               'technical_report_text': format_report(result, technical=True)}
    except (ValueError, TypeError) as exc:
        sys.settrace(None)
        row = {'index': index, 'label': case['label'], 'scenario': scenario,
               'error': {'type': type(exc).__name__, 'message': str(exc)}}
    assert scenario == original, ('input mutation', index)
    assert catalog() == original_catalog, ('catalog mutation', index)
    row['candidate_references'] = candidate_references
    rows.append(row)

destination = OUT / f'public-{tree}-seed-{seed}.json'
with destination.open('x', encoding='utf-8') as f:
    json.dump(rows, f, ensure_ascii=False, indent=2, allow_nan=False)
    f.write('\n')
print(json.dumps({'passed': True, 'tree': tree, 'seed': seed, 'calls': len(rows),
                  'accepted': sum('result' in r for r in rows),
                  'errors': sum('error' in r for r in rows),
                  'sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
                  'input_catalog_unchanged': True}))
