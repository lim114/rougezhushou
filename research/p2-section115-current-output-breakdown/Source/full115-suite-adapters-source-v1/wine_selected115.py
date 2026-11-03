"""Actual current selected MODULES via Wine, with explicit fixture capability."""
import json
import sys
import unittest
from suite_common115 import (admit_suite, bind_suite, common_receipt, drift_free,
                             parse_suite_args, require, validate_skips, write_json)


def main():
    args = parse_suite_args(__doc__)
    binding = bind_suite(args)
    modules = binding['cloud'].MODULES
    require(modules and all(isinstance(value, str) for value in modules), 'Nonempty current string MODULES required')
    suite, records = admit_suite(unittest.defaultTestLoader.loadTestsFromNames(modules), binding['capability_probe'])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.with_suffix('.log').open('x', encoding='utf-8') as log:
        result = unittest.TextTestRunner(stream=log, verbosity=1).run(suite)
    validate_skips(result, records)
    receipt = common_receipt(binding, args, records)
    receipt.update({
        'passed': result.wasSuccessful() and drift_free(receipt),
        'tests_run': result.testsRun, 'skipped': len(result.skipped),
        'failures': len(result.failures), 'errors': len(result.errors),
        'skips': [{'test': test.id(), 'reason': why} for test, why in result.skipped],
        'failed_cases': [{'test': test.id(), 'reason': why.splitlines()[-1]}
                         for test, why in result.failures + result.errors],
        'selectors': list(modules), 'complete_repository_validation': False,
        'scope': 'Current portable selected calculation regression; no Windows UI/capture, private state, game or chat actions',
        'passed_count_derived_from_run_minus_skipped': False,
    })
    write_json(args.out, receipt)
    print(json.dumps({key: receipt[key] for key in (
        'passed', 'platform', 'tests_run', 'skipped', 'failures', 'errors',
        'environment_capability_skips', 'source_drift', 'source_additional_drift', 'adapter_source_drift')}, ensure_ascii=False))
    return 0 if result.wasSuccessful() and drift_free(receipt) else 1


if __name__ == '__main__':
    sys.exit(main())
