import copy
import gzip
import hashlib
import json
import sys
from pathlib import Path
from review76_common import canonical, locked_positive, normalized_locked_result

sys.dont_write_bytecode = True
own = Path(__file__).parent
side = sys.argv[1]
source = own / ('baseline153' if side == 'baseline' else 'draft')
sys.path.insert(0, str(source))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.reporting import format_report

cases = json.loads((own / 'final-focused-cases76.json').read_text())
catalog_before = canonical(catalog())
calls = 0
def invoke(scenario):
    global calls
    before = canonical(scenario)
    calls += 1
    try:
        outcome = {'result': calculate_damage(scenario)}
    except Exception as error:
        outcome = {'error_type': type(error).__name__, 'error': str(error)}
    assert canonical(scenario) == before
    return outcome

def texts(result):
    before = canonical(result)
    value = {'default': format_report(result), 'technical': format_report(result, technical=True),
             'estimate_entry_point': format_estimate(result)}
    assert canonical(result) == before
    return value

records = []
for case in cases:
    scenario = copy.deepcopy(case['scenario'])
    outcome = invoke(scenario)
    row = {**case, 'outcome': outcome}
    if 'result' in outcome:
        row['formatted_reports'] = texts(outcome['result'])
    if locked_positive(scenario, outcome):
        zero = dict(scenario, bubble_bursts=0)
        control = invoke(zero)
        row['zero_count_control'] = {'scenario': zero, 'outcome': control}
        row['zero_control_formatted_reports'] = texts(control['result'])
        if side == 'draft':
            row['normalized_formatted_reports'] = texts(normalized_locked_result(outcome['result'], scenario['bubble_bursts']))
    records.append(row)
assert canonical(catalog()) == catalog_before
raw = json.dumps(records, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode()
packed = gzip.compress(raw, mtime=0)
destination = own / ('final-focused-' + side + '76.json.gz')
destination.write_bytes(packed)
receipt = {'side': side, 'source_tree': str(source), 'case_records': len(records),
           'actual_public_calls': calls, 'accepted': sum('result' in x['outcome'] for x in records),
           'errors': sum('error_type' in x['outcome'] for x in records),
           'zero_controls': sum('zero_count_control' in x for x in records),
           'gzip_sha256': hashlib.sha256(packed).hexdigest(), 'gzip_bytes': len(packed),
           'decompressed_sha256': hashlib.sha256(raw).hexdigest(), 'decompressed_bytes': len(raw),
           'inputs_catalog_results_not_mutated': True, 'dont_write_bytecode': True}
(own / ('final-focused-' + side + '76-receipt.json')).write_text(json.dumps(receipt, indent=2) + '\n')
print(json.dumps(receipt))
