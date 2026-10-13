"""Reproduce literal experiments; candidate isolation never edits production."""
import json
from pathlib import Path
import sys

project = Path(__file__).resolve().parents[2]
if (project / 'dependency_snapshot').is_dir():
    sys.path.insert(0, str(project.parents[1]))
    import rouge
    rouge.__path__.insert(0, str(project / 'dependency_snapshot' / 'rouge'))
    rouge.__path__.insert(0, str(project / 'rouge'))
else:
    sys.path.insert(0, str(project))
from rouge.calibration_experiment import calibration_experiment


def main():
    examples = json.loads(Path(__file__).with_name('public-vectors.json').read_text(encoding='utf-8'))
    cases = []
    expected_states = {'compatible': 'compatible_on_declared_ranges', 'held_out_conflict': 'contradicted', 'control_drift': 'blocked'}
    for example in examples['cases']:
        result = calibration_experiment(**example['payload'])
        if result['overall_state'] != expected_states[example['variant']] or result['native_verified'] or result['engine_correction'] is not None:
            raise ValueError('公式实验状态不符或被错误升级为校正/认证。')
        cases.append({'id': example['id'], 'training_state': result['training_state'],
            'training_hypothesis_range': result['training_hypothesis_range'], 'overall_state': result['overall_state'],
            'blocked_record_ids': result['blocked_record_ids'], 'witness': result['overall_contradiction_witness'],
            'native_verified': result['native_verified'], 'engine_correction': result['engine_correction']})
    print(json.dumps({'scope': 'literal_formula_hypothesis_examples_not_game_samples', 'cases': cases}, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
