"""Run the full maintained selector set and disclose migration prerequisites.

Missing .cache evidence is unavailable, never passed. Product assets and
calculation failures remain errors. --require-complete also fails for unavailable
checks. Native Windows integration is outside this offline suite.
"""
import argparse
import hashlib
import json
import platform
import re
import sys
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
NEW_MODULES = (
    'tests.test_s1_neural_boundary', 'tests.test_neural_incoming_clock',
    'tests.test_charge_reference', 'tests.test_gnosis_attack_clock',
    'tests.test_gnosis_s1_reference', 'tests.test_gnosis_target_lifetime',
)


def source_hashes():
    files = [*ROOT.glob('rouge/**/*.py'), *ROOT.glob('rouge/data/**/*.json'),
             *ROOT.glob('tests/test_*.py'), Path(__file__)]
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(set(files))}


def unmigrated_path(path):
    resolved = Path(path).resolve()
    return any(resolved.is_relative_to((ROOT / folder).resolve())
               for folder in ('.cache', 'samples/native-client'))


class AvailableResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.unavailable = []
        self.passed_count = 0
        self.unavailable_parents = set()

    def addSuccess(self, test):
        if test.id() not in self.unavailable_parents:
            self.passed_count += 1
            super().addSuccess(test)

    def addError(self, test, err):
        exc = err[1]
        missing = getattr(exc, 'filename', None)
        if isinstance(exc, FileNotFoundError) and missing and unmigrated_path(missing):
            self.unavailable_parents.add(test.id())
            self.unavailable.append({'test': test.id(), 'kind': 'unmigrated_cache',
                                     'reason': str(exc)})
            if self.dots:
                self.stream.write('U'); self.stream.flush()
            return
        wrapped = re.search(r"ModuleNotFoundError: No module named '([^']+)'", str(exc)) if type(test).__name__ == '_FailedTest' else None
        module_name = exc.name if isinstance(exc, ModuleNotFoundError) else (wrapped.group(1) if wrapped else None)
        if module_name and module_name.split('.')[0] in (
                'PySide6', 'PIL', 'rapidocr_onnxruntime', 'win32gui', 'win32process',
                'win32api', 'windows_capture'):
            self.unavailable_parents.add(test.id())
            self.unavailable.append({'test': test.id(), 'kind': 'environment_dependency',
                                     'reason': str(exc)})
            if self.dots:
                self.stream.write('U'); self.stream.flush()
            return
        super().addError(test, err)

    def addSubTest(self, test, subtest, err):
        if err is not None and isinstance(err[1], FileNotFoundError):
            missing = getattr(err[1], 'filename', None)
            if missing and unmigrated_path(missing):
                self.unavailable_parents.add(test.id())
                self.unavailable.append({'test': subtest.id(), 'kind': 'unmigrated_cache',
                                         'reason': str(err[1])})
                # The parent remains unavailable even when other subtests pass.
                if self.dots:
                    self.stream.write('U'); self.stream.flush()
                return
        super().addSubTest(test, subtest, err)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--wine', action='store_true', help='Label Windows binaries run via Wine')
    parser.add_argument('--require-complete', action='store_true')
    args = parser.parse_args()
    before = source_hashes()
    historical = json.loads((ROOT / 'CORE_0.70_VERIFICATION.json').read_text(encoding='utf-8'))
    # Pick up future cloud selectors automatically as the project advances.
    from verify_cloud import MODULES
    selectors = list(dict.fromkeys(historical['test_modules'] + list(NEW_MODULES) + list(MODULES)))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.with_suffix('.log').open('x', encoding='utf-8') as log:
        result = unittest.TextTestRunner(stream=log, verbosity=1,
            resultclass=AvailableResult).run(unittest.defaultTestLoader.loadTestsFromNames(selectors))
    after = source_hashes()
    drift = [name for name in sorted(set(before) | set(after)) if before.get(name) != after.get(name)]
    unavailable_parents = result.unavailable_parents
    receipt = {
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'platform': platform.system(), 'wine_compatibility': args.wine,
        'native_windows_integration_verified': False,
        'available_checks_passed': result.wasSuccessful() and not drift,
        'complete_repository_validation': result.wasSuccessful() and not drift and not result.unavailable,
        'tests_run': result.testsRun, 'tests_passed': result.passed_count,
        'historical_or_declared_skips': len(result.skipped),
        'failures': len(result.failures), 'errors': len(result.errors),
        'unavailable_records': len(result.unavailable),
        'unavailable_parent_count': len(unavailable_parents),
        'unavailable': result.unavailable,
        'failed_cases': [{'test': t.id(), 'reason': e.splitlines()[-1]}
                         for t, e in result.failures + result.errors],
        'skips': [{'test': t.id(), 'reason': why} for t, why in result.skipped],
        'selectors': selectors, 'source_sha256': before, 'source_drift': drift,
        'scope': 'All maintained offline selectors; absent migrated evidence is unavailable, not passed; no game or chat actions',
    }
    with args.output.open('x', encoding='utf-8') as out:
        json.dump(receipt, out, ensure_ascii=False, indent=2); out.write('\n')
    print(json.dumps({key: receipt[key] for key in (
        'available_checks_passed', 'complete_repository_validation', 'tests_run',
        'tests_passed', 'historical_or_declared_skips', 'failures',
        'errors', 'unavailable_records', 'source_drift')}, ensure_ascii=False))
    return 1 if not receipt['available_checks_passed'] else (2 if args.require_complete and result.unavailable else 0)


if __name__ == '__main__':
    sys.exit(main())
