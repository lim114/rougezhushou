"""UNEXECUTED source proposal. Root public lead reproduction, never section98 validation."""
import argparse
from collections import Counter
import hashlib
import importlib.abc
import importlib.machinery
import json
import os
from pathlib import Path
import sys
import tempfile
import traceback

HERE = Path(__file__).resolve().parent
REPO = Path('/workspace/rougezhushou')
GUARD_SHA = '41b9f4662a31b0c8ade2cf51c019bda0a04f6569e92770249bcf2e7ebabe9eab'
RUN_SHA = '20c6a00a72744017ebbc0fcb3b1009dddf8a6702aa01bf273b4b51c344692fd9'
FUTURE_GUARDS = {'section096': None, 'section097': None, 'future098baseline': None}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def raw_evidence(path):
    if not path.exists():
        return {'exists': False, 'raw_hex': None, 'bytes': None, 'sha256': None}
    raw = path.read_bytes()
    return {'exists': True, 'raw_hex': raw.hex(), 'bytes': len(raw), 'sha256': sha(raw)}


def native(value):
    """Small local graph recorder; no project/helper/fixture codec imported."""
    seen = {}

    def visit(item):
        kind = type(item)
        if kind in (dict, list, tuple):
            identity = id(item)
            if identity in seen:
                return {'ref': seen[identity], 'object_id': identity}
            label = len(seen)
            seen[identity] = label
            row = {'type': kind.__name__, 'node': label, 'object_id': identity}
            row['items'] = ([[visit(key), visit(child)] for key, child in item.items()]
                            if kind is dict else [visit(child) for child in item])
            return row
        if kind is float:
            return {'type': 'float', 'hex': item.hex(), 'repr': repr(item)}
        if kind in (str, int, bool) or item is None:
            return {'type': kind.__name__, 'value': item}
        if kind is bytes:
            return {'type': 'bytes', 'hex': item.hex()}
        return {'type': kind.__module__ + '.' + kind.__qualname__, 'repr': repr(item)}

    return visit(value)


def exception_record(error):
    return {'type': type(error).__module__ + '.' + type(error).__qualname__,
            'message': str(error), 'args_native': native(error.args),
            'traceback': ''.join(traceback.format_exception(type(error), error, error.__traceback__))}


def source_map():
    current = {}
    for folder in ('rouge', 'tests', 'scripts'):
        for path in sorted((REPO / folder).rglob('*')):
            if path.is_file() and path.suffix in ('.py', '.json') and '__pycache__' not in path.parts:
                current[path.relative_to(REPO).as_posix()] = sha(path.read_bytes())
    return current


class ExactSourceLoader(importlib.machinery.SourceFileLoader):
    def get_code(self, fullname):
        path = Path(self.path)
        relative = path.relative_to(REPO).as_posix()
        raw = path.read_bytes()
        if sha(raw) != EXPECTED.get(relative):
            raise RuntimeError('Imported project source differs from735 manifest: ' + relative)
        IMPORT_LOG.append({'module': fullname, 'path': str(path), 'sha256': sha(raw), 'bytes': len(raw)})
        # Execute the actual pinned .py bytes; do not reuse or write project .pyc.
        return self.source_to_code(raw, str(path))


class ExactSourceFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname != 'rouge' and not fullname.startswith('rouge.'):
            return None
        spec = importlib.machinery.PathFinder.find_spec(fullname, path)
        if spec is None or not isinstance(spec.loader, importlib.machinery.SourceFileLoader):
            raise RuntimeError('No pinned source-file spec for: ' + fullname)
        source_path = Path(spec.origin)
        if source_path.relative_to(REPO).as_posix() not in EXPECTED:
            raise RuntimeError('Project module outside735 source map: ' + str(source_path))
        spec.loader = ExactSourceLoader(fullname, str(source_path))
        return spec


def observe_call(name, call):
    try:
        return {'call': name, 'outcome': 'returned', 'returned_native': native(call())}
    except Exception as error:
        return {'call': name, 'outcome': 'raised', 'exception': exception_record(error)}


def state_evidence(run):
    if run is None:
        return None
    return {'state_native': native(run.state), 'preserve_unreadable': run.preserve_unreadable,
            'explicit_file': str(run.file)}


def consumer_evidence(run):
    # summary() is the exact consumer used by MainWindow startup at app.py199.
    return [observe_call(name, getattr(run, name)) for name in
            ('summary', 'inventory_status', 'held_relic_ids', 'held_tool_ids')]


def main():
    global EXPECTED, IMPORT_LOG, ACTIVE, LAST_SELF
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    continuation = Path('/workspace/.continuation')
    if continuation not in output.parents or output == HERE or HERE in output.parents or output.exists():
        raise RuntimeError('Require a fresh Root output directory under.continuation, outside sealed source package.')
    if os.environ.get('PYTHONDONTWRITEBYTECODE') != '1':
        raise RuntimeError('Root must launch with PYTHONDONTWRITEBYTECODE=1.')
    sys.dont_write_bytecode = True
    if sys.getprofile() is not None or any(name == 'rouge' or name.startswith('rouge.') for name in sys.modules):
        raise RuntimeError('Require a fresh unprofiled interpreter with no project modules already imported.')
    guard_raw = (HERE / 'source-expected-current095.json').read_bytes()
    if len(guard_raw) != 84227 or sha(guard_raw) != GUARD_SHA:
        raise RuntimeError('Pinned current095 guard reference mismatch.')
    guard = json.loads(guard_raw)
    EXPECTED = guard['source_sha256_after']
    if len(EXPECTED) != 735 or EXPECTED.get('rouge/run_state.py') != RUN_SHA:
        raise RuntimeError('Expected735/currentRunState source layout mismatch.')
    manifest = json.loads((HERE / 'public-artifacts-manifest.json').read_text())
    for row in manifest['artifacts']:
        path = HERE / row['relative_path']
        raw = path.read_bytes()
        if len(raw) != row['bytes'] or sha(raw) != row['sha256']:
            raise RuntimeError('Sealed probe source/fixture mismatch: ' + row['relative_path'])
    before_source = source_map()
    if before_source != EXPECTED:
        raise RuntimeError('Current735 source map mismatch BEFORE project import; no probe may run.')
    output.mkdir()
    IMPORT_LOG, ENTRY_LOG, cases = [], [], []
    ACTIVE, LAST_SELF = {'case': 'bootstrap', 'phase': 'import'}, None
    finder = ExactSourceFinder()
    sys.meta_path.insert(0, finder)
    sys.path.insert(0, str(REPO))
    source_file = str(REPO / 'rouge/run_state.py')

    def profile(frame, event, arg):
        global LAST_SELF
        if event == 'call' and frame.f_code.co_filename == source_file:
            ENTRY_LOG.append({'index': len(ENTRY_LOG), **ACTIVE,
                              'function': frame.f_code.co_qualname, 'line': frame.f_code.co_firstlineno})
            if frame.f_code.co_name == '__init__':
                LAST_SELF = frame.f_locals.get('self')

    collection_error = None
    sys.setprofile(profile)
    try:
        from rouge.run_state import RunState
        recipes = json.loads((HERE / 'fixture-recipes.json').read_text())
        with tempfile.TemporaryDirectory(prefix='root-public-runstate-leads-') as temporary:
            scratch = Path(temporary)
            for recipe in recipes['startup']:
                ACTIVE = {'case': recipe['id'], 'phase': 'constructor'}
                LAST_SELF = None
                path = scratch / (recipe['id'] + '.json')
                original = (HERE / recipe['fixture']).read_bytes()
                path.write_bytes(original)
                row = {'id': recipe['id'], 'kind': 'startup_loaded_public_fixture',
                       'observed': native(json.loads(original)), 'fixture_original_raw': raw_evidence(path),
                       'raw_before': raw_evidence(path), 'temporary_before': raw_evidence(path.with_suffix('.tmp')),
                       'Product_PASS': None}
                try:
                    run = RunState(file=path)  # Actual signature is file, never unsupported path=.
                except Exception as error:
                    row['constructor'] = {'outcome': 'raised', 'exception': exception_record(error)}
                    row['after_constructor'] = state_evidence(LAST_SELF)
                    row['consumers'] = {'outcome': 'not_called', 'reason': 'Constructor raised; no product success inferred.'}
                else:
                    row['constructor'] = {'outcome': 'returned'}
                    row['after_constructor'] = state_evidence(run)
                    ACTIVE = {'case': recipe['id'], 'phase': 'visible_consumers'}
                    row['consumers'] = consumer_evidence(run)
                row['raw_after'] = raw_evidence(path)
                row['temporary_after'] = raw_evidence(path.with_suffix('.tmp'))
                row['original_raw_retained'] = row['raw_before'] == row['raw_after']
                cases.append(row)

            seed_path = scratch / 'public-inventory-seed.json'
            seed_observation = json.loads((HERE / recipes['inventory_seed_fixture']).read_bytes())
            ACTIVE = {'case': 'public_inventory_seed', 'phase': 'constructor'}
            LAST_SELF = None
            seed_row = {'id': 'public_inventory_seed', 'kind': 'public_repository_fixture_seed',
                        'observed': native(seed_observation), 'caller_before': native(seed_observation),
                        'raw_before': raw_evidence(seed_path), 'Product_PASS': None}
            try:
                seed_run = RunState(file=seed_path)
            except Exception as error:
                seed_row['constructor'] = {'outcome': 'raised', 'exception': exception_record(error)}
                seed_row['state_after'] = state_evidence(LAST_SELF)
                seed_row['raw_after'] = raw_evidence(seed_path)
                seed_row['apply'] = {'outcome': 'not_called', 'reason': 'Seed constructor raised.'}
                cases.append(seed_row)
                raise RuntimeError('Actual public seed constructor raised; no subject baseline invented.') from error
            seed_row['constructor'] = {'outcome': 'returned'}
            seed_at = seed_run.state['started_at'] + 1
            ACTIVE = {'case': 'public_inventory_seed', 'phase': 'apply'}
            seed_row['apply'] = observe_call('apply', lambda: seed_run.apply(seed_observation, seed_at))
            seed_row['caller_after'] = native(seed_observation)
            seed_row['caller_native_unchanged'] = seed_row['caller_before'] == seed_row['caller_after']
            seed_row['state_after'] = state_evidence(seed_run)
            seed_row['raw_after'] = raw_evidence(seed_path)
            ACTIVE = {'case': 'public_inventory_seed', 'phase': 'visible_consumers'}
            seed_row['consumers'] = consumer_evidence(seed_run)
            cases.append(seed_row)
            if seed_row['apply']['outcome'] != 'returned' or not seed_path.is_file():
                raise RuntimeError('Actual public seed could not produce a persisted baseline; subject cases not invented.')
            seed_raw = seed_path.read_bytes()

            for recipe in recipes['inventory_subjects']:
                path = scratch / (recipe['id'] + '.json')
                path.write_bytes(seed_raw)  # Every subject begins with the same complete actual seed bytes.
                observed = json.loads((HERE / recipe['fixture']).read_bytes())
                ACTIVE = {'case': recipe['id'], 'phase': 'constructor'}
                LAST_SELF = None
                row = {'id': recipe['id'], 'kind': 'inventory_count_direct_observed_input',
                       'observed': native(observed), 'caller_before': native(observed),
                       'raw_before': raw_evidence(path), 'Product_PASS': None}
                try:
                    run = RunState(file=path)
                except Exception as error:
                    row['constructor'] = {'outcome': 'raised', 'exception': exception_record(error)}
                    row['state_after'] = state_evidence(LAST_SELF)
                    row['apply'] = {'outcome': 'not_called', 'reason': 'Constructor raised.'}
                    row['consumers'] = {'outcome': 'not_called', 'reason': 'Constructor raised.'}
                else:
                    row['constructor'] = {'outcome': 'returned'}
                    row['state_before'] = state_evidence(run)
                    ACTIVE = {'case': recipe['id'], 'phase': 'apply'}
                    at = seed_at + 1
                    row['captured_at_native'] = native(at)
                    row['apply'] = observe_call('apply', lambda: run.apply(observed, at))
                    row['state_after'] = state_evidence(run)
                    ACTIVE = {'case': recipe['id'], 'phase': 'visible_consumers'}
                    row['consumers'] = consumer_evidence(run)
                row['caller_after'] = native(observed)
                row['caller_native_unchanged'] = row['caller_before'] == row['caller_after']
                row['raw_after'] = raw_evidence(path)
                row['raw_before_after_equal'] = row['raw_before'] == row['raw_after']
                row['raw_before_matches_actual_seed'] = row['raw_before']['exists'] and row['raw_before']['raw_hex'] == seed_raw.hex()
                row['temporary_after'] = raw_evidence(path.with_suffix('.tmp'))
                cases.append(row)
    except Exception as error:
        collection_error = exception_record(error)
    finally:
        sys.setprofile(None)
        sys.meta_path.remove(finder)
    after_source = source_map()
    source_unchanged = before_source == after_source == EXPECTED
    counts = Counter(row['function'] for row in ENTRY_LOG)
    result = {'status': 'ACTUAL_LEAD_OBSERVATIONS_COLLECTED' if collection_error is None and source_unchanged
                       else 'ACTUAL_LEAD_COLLECTION_INFRASTRUCTURE_FAILED',
              'purpose': 'Current095 public lead reproduction only; not98 implementation or validation.',
              'Product_PASS': None, 'completed_section_increment': 0, 'future_guards': FUTURE_GUARDS,
              'source_before': before_source, 'source_after': after_source,
              'source_before_after_equal735': source_unchanged, 'expected_guard_sha256': GUARD_SHA,
              'actual_imported_source_log': IMPORT_LOG, 'RunState_method_entry_log': ENTRY_LOG,
              'RunState_method_entry_counts_derived_from_actual_log': dict(counts),
              'other_project_helper_entries': 'Not instrumented; no inferred whole-project call totals.',
              'cases': cases, 'collection_error': collection_error,
              'no_actual_game_observation_semantics_claim': True,
              'no_actual_MainWindow_or_native_Windows_validation': True,
              'exit0_meaning': 'Collection completed and maintained source unchanged; no Product_PASS or fixed-bug claim.'}
    (output / 'actual-lead-observations.json').write_text(json.dumps(result, ensure_ascii=True, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'output': str(output), 'status': result['status'], 'Product_PASS': None,
                      'actual_case_records': len(cases), 'actual_method_entries': len(ENTRY_LOG),
                      'source_before_after_equal735': source_unchanged}))
    return 0 if collection_error is None and source_unchanged else 2


if __name__ == '__main__':
    raise SystemExit(main())
