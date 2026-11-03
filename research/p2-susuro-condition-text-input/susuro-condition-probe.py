import copy
import hashlib
import json
import sys
from pathlib import Path

OUT = Path(__file__).parent
sys.path.insert(0, str(OUT / 'frozen'))
from rouge.catalog import catalog
from rouge.damage import calculate_damage
from rouge.estimate import format_estimate
from rouge.reporting import format_report

rows = []
cached = copy.deepcopy(catalog())
for mode in ('frames', 'continuous'):
    for value in (False, True, 'false', 'False', '0', ''):
        scenario = {'operator': 'char_298_susuro', 'skill': 1, 'elite': 2, 'level': 70,
                    'potential': 1, 'skill_rank': 10, 'base_attack': 1000,
                    'window_seconds': 10, 'timing_mode': mode,
                    'low_cost_healing_target': value}
        original = copy.deepcopy(scenario)
        try:
            result = calculate_damage(scenario)
            rows.append({'scenario': scenario, 'result': result,
                         'estimate_text': format_estimate(result), 'report_text': format_report(result),
                         'technical_report_text': format_report(result, technical=True)})
        except (ValueError, TypeError) as exc:
            rows.append({'scenario': scenario, 'error': {'type': type(exc).__name__, 'message': str(exc)}})
        assert scenario == original
        assert catalog() == cached
with (OUT / 'susuro-condition-public.json').open('x', encoding='utf-8') as f:
    json.dump(rows, f, ensure_ascii=False, indent=2, allow_nan=False)
    f.write('\n')
summary = []
for row in rows:
    r = row.get('result', {})
    summary.append({'mode': row['scenario']['timing_mode'],
                    'raw_condition': row['scenario']['low_cost_healing_target'],
                    'value_type': type(row['scenario']['low_cost_healing_target']).__name__,
                    'total_healing': r.get('total_healing'),
                    'selected_talents': r.get('talents'), 'error': row.get('error')})
receipt = {'status': 'readonly_condition_type_lead', 'baseline_commit': 'c950fbc800245f7f784d6070f7126890352ffcc9',
           'actual_calculate_damage_calls': len(rows), 'input_catalog_unchanged': True,
           'public_result_sha256': hashlib.sha256((OUT / 'susuro-condition-public.json').read_bytes()).hexdigest(),
           'summary': summary, 'product_changed': False, 'section_assigned': False,
           'gui_executed': False, 'wine_executed': False}
with (OUT / 'susuro-condition-probe-receipt.json').open('x', encoding='utf-8') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(json.dumps(receipt, ensure_ascii=False))
