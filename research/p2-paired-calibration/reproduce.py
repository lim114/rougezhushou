"""Read public declared examples and print a small reproducible summary only."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from rouge.paired_calibration import compare_paired_panels


def main():
    examples = json.loads(Path(__file__).with_name('examples.json').read_text(encoding='utf-8'))
    rows = []
    for example in examples['cases']:
        result = compare_paired_panels(**example['payload'])
        if not result['all_paired_absolute_values_match'] or result['native_verified']:
            raise ValueError('公开公式样例不符；不能升级为实机验收。')
        rows.append({'id': example['id'], 'evidence_kind': result['evidence_kind'],
            'rows': [{key: row[key] for key in ('field', 'observed_after_minus_before',
                      'model_after_minus_before', 'delta_residual')} for row in result['rows']],
            'native_verified': result['native_verified']})
    print(json.dumps({'scope': 'literal_public_formula_examples', 'cases': rows}, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
