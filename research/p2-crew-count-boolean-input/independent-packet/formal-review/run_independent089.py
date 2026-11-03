"""Authorized once-only state proof:3 persisted-seed pairs and frozen7 tests."""
from collections import Counter
import copy
import gzip
import hashlib
import importlib.util
import importlib.machinery
import json
from pathlib import Path
import sys
import tempfile
import unittest

OUT = Path(__file__).resolve().parent
REPO = Path('/workspace/rougezhushou')
SOURCE = OUT.parent / 'source-preparation-snapshots'
FROZEN = OUT / 'frozen-draft-snapshots'
mode = sys.argv[1]
assert mode in ('baseline', 'draft', 'tests')
output = OUT / ('fresh-' + mode + '089')
output.mkdir(exist_ok=False)
runtime = output / 'runtime'
runtime.mkdir()
sys.dont_write_bytecode = True
tempfile.tempdir = str(runtime)

def native(value):
    kind = type(value)
    if kind is dict:
        return {'type': 'dict', 'items': [[native(key), native(item)] for key, item in value.items()]}
    if kind in (tuple, list):
        return {'type': kind.__name__, 'items': [native(item) for item in value]}
    if kind is float:
        return {'type': 'float', 'hex': value.hex()}
    assert kind in (str, int, bool, type(None)), kind
    return {'type': kind.__name__, 'value': value}

def digest(data):
    return hashlib.sha256(data).hexdigest()

def disk(path):
    if not path.exists():
        return None
    raw = path.read_bytes()
    decoded = json.loads(raw)
    return {'bytes': len(raw), 'sha256': digest(raw), 'UTF8_raw_bytes': raw.decode(),
            'JSON': decoded, 'JSON_typed': native(decoded)}

freeze = json.loads((FROZEN / 'draft-freeze089.json').read_bytes())
assert digest((FROZEN / 'draft-freeze089.json').read_bytes()) == '04c9567954f2b7bcd34c2abe1b2b616988400d4193943e94ec4e46e32a8cc248'
product = FROZEN / ('baseline/rouge/run_state.py' if mode == 'baseline' else 'draft/rouge/run_state.py')
expected_product_hash = freeze['source_run_state_old_sha256'] if mode == 'baseline' else freeze['files'][0]['sha256']
assert digest(product.read_bytes()) == expected_product_hash
proof = json.loads((SOURCE / 'fixed-public-source-bindings089.json').read_bytes())
project_reads = {}
audit_busy = False

def audit(event, args):
    global audit_busy
    if audit_busy or event != 'open' or not args or not isinstance(args[0], (str, bytes)):
        return
    path = Path(args[0].decode() if isinstance(args[0], bytes) else args[0]).resolve()
    assert '.local' not in path.parts, ('real .local forbidden', path)
    if not path.is_relative_to(REPO / 'rouge') or not path.is_file():
        return
    relative = path.relative_to(REPO).as_posix()
    assert relative in proof['files'], ('unexpected public project input', relative)
    audit_busy = True
    try:
        raw = path.read_bytes()
    finally:
        audit_busy = False
    expected = proof['files'][relative]
    actual = {'bytes': len(raw), 'sha256': digest(raw)}
    assert actual == expected, (relative, actual, expected)
    project_reads[relative] = actual

sys.addaudithook(audit)
sys.path.insert(0, str(REPO))

class FixedPublicSourceLoader(importlib.machinery.SourceFileLoader):
    """Use verified public .py bytes; never read or mutate existing .pyc."""
    def get_code(self, fullname):
        source_path = Path(self.path).resolve()
        raw = source_path.read_bytes()
        relative = source_path.relative_to(REPO).as_posix()
        expected = proof['files'][relative]
        assert {'bytes': len(raw), 'sha256': digest(raw)} == expected
        return self.source_to_code(raw, str(source_path))

class FixedPublicSourceFinder:
    def find_spec(self, fullname, path=None, target=None):
        if fullname != 'rouge' and not fullname.startswith('rouge.'):
            return None
        found = importlib.machinery.PathFinder.find_spec(fullname, path)
        assert found is not None and found.origin.endswith('.py'), fullname
        found.loader = FixedPublicSourceLoader(fullname, found.origin)
        return found

sys.meta_path.insert(0, FixedPublicSourceFinder())
import rouge
spec = importlib.util.spec_from_file_location('rouge.run_state', product)
module = importlib.util.module_from_spec(spec)
sys.modules['rouge.run_state'] = module
spec.loader.exec_module(module)
roles, entries, records, pending = Counter(), Counter(), [], {}
ctor_limit, apply_limit = (14, 24) if mode == 'tests' else (3, 3)

def profile(frame, event, argument):
    if frame.f_code.co_filename != str(product):
        return
    name = frame.f_code.co_name
    if event == 'call':
        if name == '__init__':
            assert entries[name] < ctor_limit, ('constructor hard budget', mode)
        if name == 'apply':
            assert entries[name] < apply_limit, ('apply hard budget', mode)
        entries[name] += 1
    if name not in ('__init__', 'apply'):
        return
    if event == 'call':
        instance = frame.f_locals['self']
        path = Path(frame.f_locals['file']) if name == '__init__' else instance.file
        assert path.resolve().is_relative_to(runtime)
        caller = frame.f_back.f_code.co_name
        if name == '__init__':
            role = 'constructor_reload' if path.exists() else 'constructor_new'
        else:
            role = 'seed_apply' if mode == 'tests' and caller == 'seed_run' else 'subject_apply'
        roles[role] += 1
        record = {'entry_sequence': len(records) + len(pending) + 1,
            'method': name, 'role': role, 'caller': caller, 'file_path': str(path),
            'state_before': copy.deepcopy(getattr(instance, 'state', None)),
            'state_before_typed': native(getattr(instance, 'state', None)),
            'disk_before': disk(path)}
        with (output / 'actual-entry-ledger.jsonl').open('a', encoding='utf-8') as stream:
            json.dump({'entry_sequence': record['entry_sequence'], 'method': name,
                'role': role, 'file_path': str(path), 'product_sha256': expected_product_hash}, stream)
            stream.write('\n')
        if name == 'apply':
            observed = frame.f_locals['observed']
            record.update(observed_before=copy.deepcopy(observed), observed_before_typed=native(observed),
                captured_at=frame.f_locals['captured_at'], captured_at_typed=native(frame.f_locals['captured_at']))
        pending[id(frame)] = record
    elif event == 'return':
        instance = frame.f_locals['self']
        record = pending.pop(id(frame))
        record.update(return_value=argument, return_value_typed=native(argument),
            state_after=copy.deepcopy(instance.state), state_after_typed=native(instance.state),
            disk_after=disk(instance.file))
        if name == 'apply':
            observed = frame.f_locals['observed']
            record.update(observed_after=copy.deepcopy(observed), observed_after_typed=native(observed))
            assert record['observed_before_typed'] == record['observed_after_typed']
        records.append(record)
        with (output / 'incremental-completed-native-records.jsonl').open('a', encoding='utf-8') as stream:
            json.dump(record, stream, ensure_ascii=False, allow_nan=False)
            stream.write('\n')

cases = []
test_result = None
previous_profile = sys.getprofile()
sys.setprofile(profile)
try:
    if mode == 'tests':
        tests_path = FROZEN / 'draft/tests/test_run_crew_count_boolean_input.py'
        assert digest(tests_path.read_bytes()) == freeze['files'][1]['sha256']
        test_spec = importlib.util.spec_from_file_location('independent_original_new_tests089', tests_path)
        tests = importlib.util.module_from_spec(test_spec)
        test_spec.loader.exec_module(tests)
        assert tests.RunState is module.RunState
        suite = unittest.defaultTestLoader.loadTestsFromModule(tests)
        assert suite.countTestCases() == 7
        with (output / 'original7-tests.log').open('x', encoding='utf-8') as stream:
            result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
        test_result = {'run': result.testsRun, 'errors': len(result.errors),
            'failures': len(result.failures), 'skips': len(result.skipped), 'success': result.wasSuccessful()}
    else:
        plans = [
            ('true-two-distinct-no-alias', 'one-True',
             {'operators': [
                 {'id': 'mechanist', 'scope': 'run', 'fields': {'level': 8}, 'skill_ranks': {'1': 2}},
                 {'id': 'char_151_myrtle', 'scope': 'run', 'fields': {'trust': 22}, 'skill_ranks': {}}],
              'selected_operator': 'mechanist', 'crew_count': True}),
            ('false-positive-fields-resource', 'empty-None',
             {'operators': [{'id': 'mechanist', 'scope': 'run', 'fields': {'trust': 73}, 'skill_ranks': {}}],
              'selected_operator': 'mechanist', 'crew_count': False,
              'resources': {'gold': {'value': 37, 'source': 'public isolated observation'}}}),
            ('prior-personal-buff-typeerror', 'empty-False',
             {'operators': [{'id': 'mechanist', 'scope': 'run', 'fields': {'level': 3},
                'skill_ranks': {}, 'char_buffs_complete': 1, 'char_buff_ids': []}],
              'crew_count': False})]
        for case_id, saved_case, observed in plans:
            public_seed = SOURCE / 'runtime' / saved_case / 'seed-persisted.json'
            seed_bytes = public_seed.read_bytes()
            case_dir = runtime / case_id
            case_dir.mkdir()
            target = case_dir / 'run.json'
            target.write_bytes(seed_bytes)
            (case_dir / 'initial-persisted.json').write_bytes(seed_bytes)
            before_constructor = disk(target)
            run = module.RunState(target)
            assert disk(target) == before_constructor
            state_before = copy.deepcopy(run.state)
            caller_before = native(observed)
            captured_at = run.state['started_at'] + 2
            caught, returned = None, None
            try:
                returned = run.apply(observed, captured_at)
            except Exception as exception:
                caught = {'type': type(exception).__name__, 'message': str(exception)}
            cases.append({'case_id': case_id, 'public_seed_path': str(public_seed),
                'initial_persisted_bytes': len(seed_bytes), 'initial_persisted_sha256': digest(seed_bytes),
                'initial_persisted_UTF8': seed_bytes.decode(), 'file_path': str(target),
                'actual_run_id': run.state['id'], 'started_at': run.state['started_at'],
                'started_at_hex': run.state['started_at'].hex(), 'captured_at': captured_at,
                'captured_at_hex': captured_at.hex(), 'state_before': state_before,
                'state_before_typed': native(state_before), 'state_after': copy.deepcopy(run.state),
                'state_after_typed': native(run.state), 'disk_before': before_constructor, 'disk_after': disk(target),
                'observed_before_typed': caller_before, 'observed_after_typed': native(observed),
                'returned': returned, 'exception': caught})
            assert native(observed) == caller_before
finally:
    sys.setprofile(previous_profile)

assert not pending
expected_roles = {'constructor_new': 12, 'constructor_reload': 2, 'seed_apply': 12, 'subject_apply': 12} if mode == 'tests' else {'constructor_reload': 3, 'subject_apply': 3}
assert roles == expected_roles
assert entries['__init__'] == ctor_limit and entries['apply'] == apply_limit
assert digest(product.read_bytes()) == expected_product_hash
loaded = []
for name, loaded_module in sorted(sys.modules.items()):
    source = getattr(loaded_module, '__file__', None)
    if not name.startswith('rouge') or not source:
        continue
    path = Path(source).resolve()
    data = path.read_bytes()
    expected_hash = expected_product_hash if name == 'rouge.run_state' else proof['files'][path.relative_to(REPO).as_posix()]['sha256']
    assert digest(data) == expected_hash
    loaded.append({'name': name, 'source_path': str(path), 'bytes': len(data), 'sha256': digest(data)})
for relative, before in project_reads.items():
    data = (REPO / relative).read_bytes()
    assert {'bytes': len(data), 'sha256': digest(data)} == before

summary = {'status': 'COLLECTED' if mode != 'tests' else ('PASS' if test_result['success'] else 'FAILED_PRESERVED'),
    'mode': mode, 'actual_roles': dict(roles), 'RunState_source_actual_entries': dict(entries),
    'constructor_entries': entries['__init__'], 'apply_entries': entries['apply'],
    'records': len(records), 'test_result': test_result, 'product_sha256': expected_product_hash,
    'loaded_project_sources_bound': loaded, 'actual_read_public_source_bindings': project_reads,
    'public_seed_scope': 'Exact original scratch persisted bytes cloned; actual UUID/time retained; no crosscase normalization.',
    'no_real_local': True, 'damage_app_API': 0, 'public_recognition_API': 0,
    'formatter': 0, 'Qt': 0, 'Wine': 0, 'network': 0, 'tracked_mutations': 0,
    'other_internal_helpers': 'Only this RunState source body entries instrumented; no whole-project helper count inferred.'}
raw = json.dumps({'summary': summary, 'records': records, 'cases': cases}, ensure_ascii=False, allow_nan=False).encode()
compressed = gzip.compress(raw, mtime=0)
(output / 'complete-native-records.json.gz').write_bytes(compressed)
summary.update(gzip_bytes=len(compressed), gzip_sha256=digest(compressed),
               decoded_bytes=len(raw), decoded_sha256=digest(raw))
with (output / 'summary.json').open('x', encoding='utf-8') as stream:
    json.dump(summary, stream, ensure_ascii=False, indent=2)
    stream.write('\n')
print(json.dumps({'mode': mode, 'status': summary['status'], 'constructors': entries['__init__'],
    'apply': entries['apply'], 'roles': dict(roles), 'tests': test_result,
    'damage_app_API': 0, 'formatter': 0}))
assert mode != 'tests' or test_result['success']
