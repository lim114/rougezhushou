"""Fresh maintained-union full suite via diagnosed Wine; not discover/native."""
import json
import sys
import unittest
from suite_common105 import (admit_suite, bind_suite, common_receipt, drift_free,
                             parse_suite_args, require, validate_skips, write_json)


def main():
    args = parse_suite_args(__doc__, allow_require_complete=True)
    binding = bind_suite(args)
    historical = json.loads((binding['root'] / 'CORE_0.70_VERIFICATION.json').read_bytes())
    classifier = binding['classifier']
    modules = binding['cloud'].MODULES
    selectors = list(dict.fromkeys(historical['test_modules'] + list(classifier.NEW_MODULES) + list(modules)))
    require(selectors and all(isinstance(value, str) for value in selectors), 'Nonempty string selector union required')
    suite, records = admit_suite(unittest.defaultTestLoader.loadTestsFromNames(selectors), binding['capability_probe'])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.with_suffix('.log').open('x', encoding='utf-8') as log:
        # Use the exact current maintained AvailableResult; its original AST is guarded.
        result = unittest.TextTestRunner(stream=log, verbosity=1,
                                        resultclass=classifier.AvailableResult).run(suite)
    validate_skips(result, records)
    receipt = common_receipt(binding, args, records)
    receipt.update({
        'available_checks_passed': result.wasSuccessful() and drift_free(receipt),
        'complete_repository_validation': result.wasSuccessful() and drift_free(receipt)
                                          and not result.unavailable and not records,
        'tests_run': result.testsRun, 'tests_passed': result.passed_count,
        'historical_or_declared_skips': len(result.skipped),
        'failures': len(result.failures), 'errors': len(result.errors),
        'unavailable_records': len(result.unavailable),
        'unavailable_parent_count': len(result.unavailable_parents),
        'unavailable': result.unavailable,
        'failed_cases': [{'test': test.id(), 'reason': why.splitlines()[-1]}
                         for test, why in result.failures + result.errors],
        'skips': [{'test': test.id(), 'reason': why} for test, why in result.skipped],
        'selectors': selectors,
        'selector_inputs': {'historical': historical['test_modules'],
                            'new_modules': list(classifier.NEW_MODULES), 'cloud_modules': list(modules)},
        'scope': 'Actual current maintained offline selector union; absent migrated evidence is unavailable, not passed; no game or chat actions',
        'complete_field_scope': 'Maintained union only; historical declared skips remain; not all physical tests or native Windows',
    })
    write_json(args.out, receipt)
    print(json.dumps({key: receipt[key] for key in (
        'available_checks_passed', 'complete_repository_validation', 'tests_run', 'tests_passed',
        'historical_or_declared_skips', 'failures', 'errors', 'unavailable_records',
        'environment_capability_skips', 'source_drift', 'source_additional_drift', 'adapter_source_drift')}, ensure_ascii=False))
    return 1 if not receipt['available_checks_passed'] else (
        2 if args.require_complete and (result.unavailable or records) else 0)


if __name__ == '__main__':
    sys.exit(main())
