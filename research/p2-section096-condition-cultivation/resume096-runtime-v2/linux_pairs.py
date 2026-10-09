"""Root-run bounded 096 native API pairs. No whole-package profile/trace hooks."""
import argparse
import collections
import json
import os
from pathlib import Path
import signal
import sys
import time
import traceback

from native_evidence import assert_native_equal, freeze, read_record, sha256, source_map, write_record

PLAN_PATH = Path(__file__).with_name('plan.json')
PLAN_SHA256 = '55eab397b5bc908263d073318e610c7e23ddd33116759935b31e302144dc20fc'
GUARD_PATH = Path(__file__).with_name('gold-source.json')
GUARD_SHA256 = '41b9f4662a31b0c8ade2cf51c019bda0a04f6569e92770249bcf2e7ebabe9eab'
MANIFEST_PATH = Path(__file__).with_name('candidate-code.json')
MANIFEST_SHA256 = '255d95b7c7241ebc34bb85a01a543bac0f50f7d9b44ad9de7b178a4598c45c36'
DEADLINE_SECONDS = 600
RECEIPT_NAME = 'linux-pairs-receipt.json'


def bound_json(path, expected):
    raw = path.read_bytes()
    if sha256(raw) != expected:
        raise AssertionError('Bound Source hash differs: ' + str(path))
    return json.loads(raw)


def dump_json(path, value):
    temporary = path.with_name(path.name + '.tmp')
    with temporary.open('w', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, allow_nan=False, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--mode', required=True, choices=('gold', 'candidate'))
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--baseline', type=Path)
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    out = args.out.absolute()
    if out.exists() or out.is_symlink():
        raise AssertionError('Output must be fresh absent; retain previous attempts')
    if out == root or root in out.parents:
        raise AssertionError('Evidence output must be outside the project Source root')
    if (args.mode == 'candidate') != (args.baseline is not None):
        raise AssertionError('Only candidate consumes a Root-created gold output directory')
    plan = bound_json(PLAN_PATH, PLAN_SHA256)
    guard = bound_json(GUARD_PATH, GUARD_SHA256)
    manifest = bound_json(MANIFEST_PATH, MANIFEST_SHA256)
    cases = plan['Linux_cases']
    if len(cases) != 1132 or plan['counts']['Linux_API_cases_planned'] != 1132:
        raise AssertionError('All 1132 cases of the bound plan are required')
    if len({case['id'] for case in cases}) != 1132:
        raise AssertionError('Planned case IDs must be unique')
    gold_sources = {relative: sha for relative, sha in guard['source_sha256_after'].items()
                    if relative.startswith('rouge/')}
    if guard['passed'] is not True or len(guard['source_sha256_after']) != 735:
        raise AssertionError('Actual gold Source guard must describe 735 maintained paths')
    expected_sources = dict(gold_sources)
    if len(manifest['files']) != 5:
        raise AssertionError('The exact five-file 096 candidate manifest is required')
    if args.mode == 'candidate':
        for row in manifest['files']:
            relative = row['destination_repo_path']
            if not relative.startswith('rouge/'):
                continue
            old = row['expected_old']
            if old is None:
                if relative in expected_sources:
                    raise AssertionError('New candidate path already exists in gold: ' + relative)
            elif expected_sources.get(relative) != old['sha256']:
                raise AssertionError('Candidate old coordinate differs: ' + relative)
            expected_sources[relative] = row['sha256']
    before_sources = source_map(root, ('rouge',))
    if before_sources != dict(sorted(expected_sources.items())):
        raise AssertionError('Physical rouge Source set/hash differs from admitted gold/candidate')
    own_sources = {str(Path(__file__).resolve()): sha256(Path(__file__).read_bytes()),
                   str(Path(__file__).with_name('native_evidence.py').resolve()):
                   sha256(Path(__file__).with_name('native_evidence.py').read_bytes())}
    baseline = None
    baseline_receipt = None
    baseline_receipt_sha = None
    if args.baseline is not None:
        baseline = args.baseline.resolve(strict=True)
        raw = (baseline / RECEIPT_NAME).read_bytes()
        baseline_receipt_sha = sha256(raw)
        baseline_receipt = json.loads(raw)
        if not (baseline_receipt['mode'] == 'gold' and baseline_receipt['passed'] is True
                and baseline_receipt['workflow_complete'] is True
                and baseline_receipt['plan_sha256'] == PLAN_SHA256
                and baseline_receipt['source_sha256_before'] == gold_sources
                and baseline_receipt['source_sha256_after'] == gold_sources
                and baseline_receipt['source_drift'] == []
                and baseline_receipt['runner_source_sha256'] == own_sources
                and [row['id'] for row in baseline_receipt['records']] == [case['id'] for case in cases]):
            raise AssertionError('Saved gold must be the complete actual matching Source/plan/runner run')

    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    receipt = {'format_version': 1, 'kind': 'CONDITION096_ISOLATED_LINUX_API_PAIRS',
               'mode': args.mode, 'root': str(root), 'passed': False, 'workflow_complete': False,
               'completed_section_increment': 0, 'plan_sha256': PLAN_SHA256,
               'guard_sha256': GUARD_SHA256, 'candidate_manifest_sha256': MANIFEST_SHA256,
               'runner_source_sha256': own_sources, 'source_sha256_before': before_sources,
               'source_guard_scope': 'Complete physical rouge .py/.json set; Root separately guards all maintained trees',
               'deadline_seconds': DEADLINE_SECONDS, 'records': [], 'paired_records': 0,
               'baseline_directory': str(baseline) if baseline is not None else None,
               'baseline_receipt_sha256': baseline_receipt_sha, 'private_state_used': False,
               'project_app_imports': 0, 'whole_package_profile_or_trace_used': False,
               'written_boundary_tests_executed_by_worker': False,
               'independent_boundary_unittest_primary_required': True}
    counts = collections.Counter()
    events = []
    active = 'before-project-import'
    scenario = None
    caller_before = None
    outcome = None
    damage_module = None
    original_prepare = None
    previous_alarm = signal.getsignal(signal.SIGALRM)
    sys.dont_write_bytecode = True

    class DeadlineExceeded(BaseException):
        pass

    def check_deadline():
        if time.monotonic() - started >= DEADLINE_SECONDS:
            raise DeadlineExceeded('Actual Linux pairs deadline exceeded')

    def alarm_handler(signum, frame):
        raise DeadlineExceeded('Actual Linux pairs SIGALRM deadline exceeded')

    def error_info(error):
        return {'type': type(error).__name__, 'module': type(error).__module__,
                'message': str(error), 'args': freeze(error.args)}

    def observe(target, real_function, call_args, call_kwargs):
        """Transparent actual call; no numerical implementation, mock, or substituted return."""
        counts[target] += 1
        caller = {'args': call_args, 'kwargs': call_kwargs}
        event = {'target': target, 'case': active, 'caller_before': freeze(caller), 'outcome': 'pending'}
        events.append(event)
        try:
            result = real_function(*call_args, **call_kwargs)
        except BaseException as error:
            event['outcome'] = 'raised'
            event['error'] = error_info(error)
            raise
        else:
            event['outcome'] = 'returned'
            event['returned'] = freeze(result)
            event['caller_and_returned_graph'] = freeze({'caller': caller, 'returned': result})
            if target == '_prepare_damage':
                # The pinned actual function returns (prepared_scenario, attributes, resolutions...).
                event['actual_prepared_scenario_returned'] = freeze(result[0])
            return result
        finally:
            event['caller_after'] = freeze(caller)
            assert_native_equal(event['caller_after'], event['caller_before'], 'Actual target caller unchanged: ' + target)
            event['caller_unchanged'] = True

    try:
        signal.signal(signal.SIGALRM, alarm_handler)
        signal.setitimer(signal.ITIMER_REAL, DEADLINE_SECONDS)
        sys.path.insert(0, str(root))
        import rouge.damage as damage_module
        from rouge.estimate import format_estimate
        from rouge.reporting import format_report
        original_calculate = damage_module.calculate_damage
        original_prepare = damage_module._prepare_damage
        for function, relative in ((original_calculate, 'rouge/damage.py'), (original_prepare, 'rouge/damage.py'),
                                   (format_estimate, 'rouge/estimate.py'), (format_report, 'rouge/reporting.py')):
            if Path(function.__code__.co_filename).resolve() != root / relative:
                raise AssertionError('Actual target does not come from the Root-provided guarded Source')

        def observed_prepare(*call_args, **call_kwargs):
            return observe('_prepare_damage', original_prepare, call_args, call_kwargs)

        damage_module._prepare_damage = observed_prepare
        for sequence, case in enumerate(cases, 1):
            check_deadline()
            active = case['id']
            events.clear()
            count_start = dict(counts)
            scenario = freeze(case['scenario'])
            caller_before = freeze(scenario)
            outcome = None
            try:
                value = observe('calculate_damage', original_calculate, (scenario,), {})
                outcome = {'kind': 'returned', 'value': freeze(value),
                           'caller_and_result': freeze({'caller': scenario, 'result': value})}
            except Exception as error:
                outcome = {'kind': 'raised', **error_info(error)}
                value = None
            assert_native_equal(scenario, caller_before, 'Original scenario unchanged: ' + active)
            texts = None
            if outcome['kind'] == 'returned':
                result_before = freeze(value)
                texts = {'estimate': observe('format_estimate', format_estimate, (value,), {}),
                         'default': observe('format_report_default', format_report, (value,), {}),
                         'technical': observe('format_report_technical', format_report, (value,), {'technical': True})}
                assert_native_equal(value, result_before, 'Actual three formatters leave result unchanged: ' + active)
                if any(type(text) is not str for text in texts.values()):
                    raise AssertionError('Actual report formatters must return three strings')
            vector = {key: counts[key] - count_start.get(key, 0) for key in sorted(counts)
                      if counts[key] != count_start.get(key, 0)}
            if vector.get('calculate_damage') != 1 or vector.get('_prepare_damage') != 1:
                raise AssertionError('One actual API and preparation call is required for each case')
            if any(event['outcome'] == 'pending' or event['caller_unchanged'] is not True for event in events):
                raise AssertionError('Incomplete actual call evidence')
            row = {'id': active, 'planned': freeze(case), 'caller_before': caller_before,
                   'caller_after': freeze(scenario), 'outcome': outcome,
                   'actual_target_calls': freeze(events), 'actual_target_function_vector': vector,
                   'all_three_texts': texts, 'local_invariants_passed': True}
            stored = write_record(out, sequence, row)
            stored['id'] = active
            receipt['records'].append(stored)
            with (out / 'records.jsonl').open('a', encoding='utf-8') as stream:
                stream.write(json.dumps(stored, ensure_ascii=False, allow_nan=False) + '\n')
                stream.flush()
                os.fsync(stream.fileno())
            dump_json(out / 'progress.json', {'status': 'RUNNING_NOT_PASS', 'mode': args.mode,
                'records_completed': sequence, 'case': active, 'paired_records': receipt['paired_records'],
                'elapsed_seconds': time.monotonic() - started, 'deadline_seconds': DEADLINE_SECONDS})
            if baseline_receipt is not None:
                original = read_record(baseline, baseline_receipt['records'][sequence - 1])
                assert_native_equal(row, original, 'Complete original native/errors/three texts: ' + active)
                receipt['paired_records'] += 1
            print(json.dumps({'records_completed': sequence, 'case': active,
                              'paired_records': receipt['paired_records']}, ensure_ascii=False), flush=True)
        if (len(receipt['records']) != 1132 or counts['calculate_damage'] != 1132
                or counts['_prepare_damage'] != 1132
                or (args.mode == 'candidate' and receipt['paired_records'] != 1132)):
            raise AssertionError('Every planned real API record and candidate pair must complete')
        if 'rouge.app' in sys.modules or 'rouge.condition_cultivation' in sys.modules:
            raise AssertionError('Numeric worker must never import app or presentation helper')
        for name, module in tuple(sys.modules.items()):
            if name == 'rouge' or name.startswith('rouge.'):
                filename = getattr(module, '__file__', None)
                if filename is not None and not Path(filename).resolve().is_relative_to(root):
                    raise AssertionError('Project import escaped the actual guarded Source: ' + name)
        check_deadline()
        receipt['passed'] = True
        receipt['workflow_complete'] = True
    except BaseException as error:
        receipt['failure'] = {'type': type(error).__name__, 'message': str(error),
                              'case': active, 'traceback': traceback.format_exc()}
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous_alarm)
        if damage_module is not None and original_prepare is not None:
            damage_module._prepare_damage = original_prepare
        receipt['elapsed_seconds'] = time.monotonic() - started
        receipt['actual_target_function_entries'] = dict(counts)
        receipt['actual_API_entries'] = counts['calculate_damage']
        receipt['case_group_counts'] = dict(collections.Counter(case['group'] for case in cases[:len(receipt['records'])]))
        if receipt.get('failure'):
            try:
                failure_directory = out / 'failure-native'
                failure_directory.mkdir(exist_ok=False)
                receipt['failure_native'] = write_record(failure_directory, 1,
                    {'case': active, 'actual_caller': scenario, 'caller_before': caller_before,
                     'outcome': outcome, 'actual_target_calls': events, 'actual_target_function_entries': dict(counts)})
                receipt['failure_native']['directory'] = 'failure-native'
            except BaseException as error:
                receipt['failure_native_capture_error'] = {'type': type(error).__name__, 'message': str(error)}
        try:
            after_sources = source_map(root, ('rouge',))
            receipt['source_sha256_after'] = after_sources
            receipt['source_drift'] = [relative for relative in sorted(set(before_sources) | set(after_sources))
                                     if before_sources.get(relative) != after_sources.get(relative)]
            receipt['runner_source_sha256_after'] = {path: sha256(Path(path).read_bytes()) for path in own_sources}
            receipt['runner_source_drift'] = receipt['runner_source_sha256_after'] != own_sources
            receipt['bound_metadata_sha256_after'] = {
                'plan': sha256(PLAN_PATH.read_bytes()), 'gold_source': sha256(GUARD_PATH.read_bytes()),
                'candidate_code': sha256(MANIFEST_PATH.read_bytes())}
            if receipt['bound_metadata_sha256_after'] != {
                    'plan': PLAN_SHA256, 'gold_source': GUARD_SHA256, 'candidate_code': MANIFEST_SHA256}:
                raise AssertionError('Bound plan/guard/manifest changed during actual execution')
            if baseline is not None and sha256((baseline / RECEIPT_NAME).read_bytes()) != baseline_receipt_sha:
                raise AssertionError('Saved actual gold receipt changed during candidate execution')
            if receipt['source_drift'] or receipt['runner_source_drift']:
                raise AssertionError('Actual project or runner Source changed during execution')
        except BaseException as error:
            receipt['passed'] = False
            receipt['workflow_complete'] = False
            receipt['final_guard_failure'] = {'type': type(error).__name__, 'message': str(error)}
        dump_json(out / RECEIPT_NAME, receipt)
        dump_json(out / 'progress.json', {'status': 'ACTUAL_PASS' if receipt['passed'] else 'ACTUAL_INCOMPLETE_OR_FAILED',
                  'records_completed': len(receipt['records']), 'paired_records': receipt['paired_records'],
                  'elapsed_seconds': receipt['elapsed_seconds'], 'case': active})
        print(json.dumps({'passed': receipt['passed'], 'records': len(receipt['records']),
                          'paired_records': receipt['paired_records'], 'failure': receipt.get('failure'),
                          'final_guard_failure': receipt.get('final_guard_failure')}, ensure_ascii=False), flush=True)
    return 0 if receipt['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
