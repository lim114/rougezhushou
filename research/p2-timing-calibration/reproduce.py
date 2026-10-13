"""Read public formula ledgers; print a small result without loading run state."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from rouge.timing_calibration import compare_timing_observation


def main():
    examples = json.loads(Path(__file__).with_name('examples.json').read_text(encoding='utf-8'))
    results = []
    for example in examples['cases']:
        result = compare_timing_observation(**example['payload'])
        if result['native_verified'] or result['mismatching_conditional_clock_count']:
            raise ValueError('公式时钟参考不符；不能认证原生时钟。')
        if any(row['actual_native_reference_seconds'] is not None for row in result['comparisons']):
            raise ValueError('未证原生相位被错误补齐。')
        results.append({'id': example['id'], 'evidence_kind': result['evidence_kind'],
            'compared_conditional_clock_count': result['compared_conditional_clock_count'],
            'matching_conditional_clock_count': result['matching_conditional_clock_count'],
            'start_to_start_seconds': [row['observed_seconds'] for row in result['repeat_cycle_rows']],
            'manual_wait_seconds': [row['observed_seconds'] for row in result['comparisons'] if row['metric'] == 'activation_wait'],
            'native_verified': result['native_verified']})
    print(json.dumps({'scope': 'literal_formula_clock_not_game_events', 'cases': results}, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
