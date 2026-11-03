"""Source-reviewed external Wine suite support; no project calls at import."""
import argparse
import ast
import ctypes
from ctypes import wintypes
import hashlib
import importlib
import json
import os
from pathlib import Path, PureWindowsPath
import platform
import re
import stat
import sys
import tempfile
import unittest
from datetime import datetime, timezone

PACKET = Path(__file__).resolve().parent
PACKET_NAMES = (
    'suite_common110.py', 'wine_capability_probe110.py', 'wine_full110.py',
    'wine_selected110.py', 'source-contract.json', 'README.md', 'manifest.json',
)
KERNELBASE_SHA = '30875e36572fff7b6eaee0798e807342fd99fff4a857799d11171e6617c116a5'
NTDLL_SHA = '5e3846b0c3cdcb4009a5837719cbc02f2635892ed788bc2e592e344cced6b0c2'
TEST_IDS = (
    'tests.test_account_cache_093.AccountCache093Tests.test_dangling_symlink_file_not_found_is_not_genuinely_absent',
    'tests.test_account_cache_093.AccountCache093Tests.test_symlink_to_damaged_file_retains_link_and_target_bytes',
    'tests.test_run_persistence_099.RunPersistenceTests.test_actual_dangling_symlink_is_not_missing_until_explicit_manual_reset',
)
SKIP_REASON = (
    'Declared installed-Wine environment capability skip: fresh independent and '
    'same-default-Temp probes on SHA-pinned Wine binaries reproduce the diagnosed '
    'CreateSymbolicLinkW success-only stub without a symbolic link. This original '
    'fixture body and its AccountCache or RunState preservation assertions were not run and '
    'are not counted as passed. Native Windows validation remains required.'
)
ADDITIONAL_ALLOWED = {
    'CORE_0.70_VERIFICATION.json', 'AGENTS.md', 'CLOUD_HANDOFF.md',
    'CLOUD_SOURCE_MANIFEST.json', 'DEVELOPMENT_CHECKPOINT.json', 'README.md',
    'PROJECT_PROGRESS.md', 'PROJECT_COMPLETED.md', 'WORK_IN_PROGRESS.md',
    'BATCH_CONTINUOUS_P2.md',
}
EXPECTED_CLASSIFIER_AST = {
    'AvailableResult': 'bed106a2ef5c7365f4d62429c4aa12da4e1b149ba16aad6dd812253db30ec9eb',
    'unmigrated_path': '9e5f185973f464c012eec0041b3d4bc1ccf1070d5abdb12ed2f7f2b8e5527334',
}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def reference(path):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), 'Regular nonsymlink input required: ' + str(path))
    data = path.read_bytes()
    return {'path': str(path.resolve()), 'bytes': len(data), 'sha256': digest(data)}


def packet_sources():
    return {name: reference(PACKET / name)['sha256'] for name in PACKET_NAMES}


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as out:
        json.dump(value, out, ensure_ascii=False, indent=2)
        out.write('\n')


def require_wine(explicit):
    require(explicit is True and os.name == 'nt' and platform.system() == 'Windows',
            'Explicit --wine and actual Windows Python are required; native adaptation is forbidden')
    require(platform.python_version() == '3.12.10', 'Diagnosed Windows Python version changed')


def active_module(module_name, expected_sha):
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    get_handle = kernel32.GetModuleHandleW
    get_handle.argtypes = (wintypes.LPCWSTR,)
    get_handle.restype = wintypes.HMODULE
    get_name = kernel32.GetModuleFileNameW
    get_name.argtypes = (wintypes.HMODULE, wintypes.LPWSTR, wintypes.DWORD)
    get_name.restype = wintypes.DWORD
    handle = get_handle(module_name)
    require(bool(handle), 'Cannot identify active module: ' + module_name)
    buffer = ctypes.create_unicode_buffer(32768)
    length = get_name(handle, buffer, len(buffer))
    require(0 < length < len(buffer), 'Cannot read active module path: ' + module_name)
    actual = reference(Path(buffer.value))
    require(actual['sha256'] == expected_sha, 'Active binary differs from the source-diagnosed Wine binary: ' + module_name)
    return actual


def wine_identity(explicit):
    require_wine(explicit)
    try:
        ntdll = ctypes.CDLL('ntdll')
        wine_version = ntdll.wine_get_version
    except (OSError, AttributeError) as exc:
        raise RuntimeError('Actual Wine-specific export absent; native Windows cannot use this adapter') from exc
    wine_version.argtypes = ()
    wine_version.restype = ctypes.c_char_p
    value = wine_version()
    require(bool(value), 'Wine identity export returned no version')
    return {
        'wine_specific_export': 'ntdll.wine_get_version',
        'actual_version': value.decode('ascii', errors='strict'),
        'active_kernelbase': active_module('kernelbase.dll', KERNELBASE_SHA),
        'active_ntdll': active_module('ntdll.dll', NTDLL_SHA),
        'python': platform.python_version(),
    }


def observe_operation(path, operation):
    try:
        value = getattr(path, operation)()
        if operation == 'lstat':
            value = {'mode': value.st_mode, 'is_link_mode': stat.S_ISLNK(value.st_mode),
                     'file_attributes': getattr(value, 'st_file_attributes', None),
                     'reparse_tag': getattr(value, 'st_reparse_tag', None)}
        elif operation == 'read_bytes':
            value = {'bytes_hex': value.hex()}
        else:
            value = str(value)
        return {'result': value}
    except OSError as exc:
        return {'error_type': type(exc).__name__, 'error': str(exc),
                'errno': getattr(exc, 'errno', None),
                'winerror': getattr(exc, 'winerror', None)}


def missing_operation(row, operation):
    value = row.get(operation, {})
    if (value.get('error_type') != 'FileNotFoundError'
            or type(value.get('errno')) is not int or value['errno'] != 2):
        return False
    if operation == 'read_bytes':
        # CPython FileIO uses the errno constructor, not a Windows error field.
        return 'winerror' in value and value['winerror'] is None
    if operation in ('lstat', 'readlink'):
        # These Windows path queries retain WinError2 as well as mapped ENOENT.
        return type(value.get('winerror')) is int and value['winerror'] == 2
    return False


def phantom(row, present):
    return (
        row.get('target_present') is present
        and row.get('creation') == {'returned_type': 'NoneType', 'returned_repr': 'None'}
        and row.get('is_symlink') is False and row.get('exists') is False
        and all(missing_operation(row, op) for op in ('lstat', 'readlink', 'read_bytes'))
        and row.get('target_bytes_unchanged') is True
        and row.get('actual_directory_entries') == ([Path(row['target']).name] if present else [])
    )


def genuine_link(row, present):
    expected_entries = sorted([Path(row['link']).name] + ([Path(row['target']).name] if present else []))
    readback = row.get('read_bytes', {})
    read_ready = (readback.get('result') == {'bytes_hex': b'{"public_bad_json":'.hex()}
                  if present else readback.get('error_type') == 'FileNotFoundError')
    return (
        row.get('target_present') is present
        and row.get('creation') == {'returned_type': 'NoneType', 'returned_repr': 'None'}
        and row.get('is_symlink') is True and row.get('exists') is present
        and row.get('lstat', {}).get('result', {}).get('is_link_mode') is True
        and isinstance(row.get('readlink', {}).get('result'), str)
        and bool(row['readlink']['result'])
        and row.get('resolved_link_matches_target') is True
        and read_ready and row.get('target_bytes_unchanged') is True
        and row.get('actual_directory_entries') == expected_entries
    )


def creation_exception(row, present):
    return (
        row.get('target_present') is present
        and row.get('creation', {}).get('exception_is_original_skip_type') is True
        and row.get('is_symlink') is False and row.get('exists') is False
        and row.get('target_bytes_unchanged') is True
        and all(missing_operation(row, op) for op in ('lstat', 'readlink', 'read_bytes'))
        and row.get('actual_directory_entries') == ([Path(row['target']).name] if present else [])
    )


def classify_observations(rows):
    require(isinstance(rows, list) and len(rows) == 2, 'Exactly two public capability controls required')
    for name, predicate in (
        ('genuine_links', genuine_link), ('diagnosed_phantom_success', phantom),
        ('original_creation_exceptions', creation_exception),
    ):
        if all(predicate(row, present) for row, present in zip(rows, (False, True), strict=True)):
            return name
    return 'unrecognized'


def fresh_capability(explicit):
    identity = wine_identity(explicit)
    adapter_before = packet_sources()
    default_temp = str(Path(tempfile.gettempdir()).resolve())
    observations = []
    with tempfile.TemporaryDirectory(prefix='public-symlink-capability-100-') as folder:
        base = Path(folder)
        require(base.drive.casefold() == Path(default_temp).drive.casefold(),
                'Capability controls are not on default unittest Temp volume')
        for present in (False, True):
            target = base / ('present-target.json' if present else 'absent-target.json')
            original = b'{"public_bad_json":'
            if present:
                target.write_bytes(original)
            link = base / ('present-link.json' if present else 'absent-link.json')
            row = {'target_present': present, 'link': str(link), 'target': str(target)}
            try:
                value = os.symlink(target, link)
                row['creation'] = {'returned_type': type(value).__name__, 'returned_repr': repr(value)}
            except (OSError, NotImplementedError) as exc:
                row['creation'] = {'error_type': type(exc).__name__, 'error': str(exc),
                                   'winerror': getattr(exc, 'winerror', None),
                                   'exception_is_original_skip_type': True}
            row['is_symlink'] = link.is_symlink()
            row['exists'] = link.exists()
            for operation in ('lstat', 'readlink', 'read_bytes'):
                row[operation] = observe_operation(link, operation)
            try:
                row['resolved_link_matches_target'] = link.resolve(strict=False) == target.resolve(strict=False)
            except OSError as exc:
                row['resolved_link_matches_target'] = False
                row['resolve_error'] = str(exc)
            row['actual_directory_entries'] = sorted(p.name for p in base.iterdir())
            row['target_bytes_unchanged'] = target.read_bytes() == original if present else not target.exists()
            observations.append(row)
            # Controls share the same public default-Temp volume; remove only our real first link.
            if link.is_symlink():
                link.unlink()
            if present:
                target.unlink()
    mode = classify_observations(observations)
    adapter_after = packet_sources()
    require(adapter_before == adapter_after, 'Adapter Source changed during capability controls')
    return {'format_version': 1, 'checked_at': now(), 'platform': platform.system(),
            'wine_compatibility': True, 'native_windows_integration_verified': False,
            'identity': identity, 'default_temp': default_temp, 'observations': observations,
            'admission_mode': mode, 'passed': mode != 'unrecognized',
            'project_imports': 0, 'project_calls': 0, 'private_state_access': False,
            'source_sha256': adapter_before, 'source_drift': [],
            'actual_python_argv': list(sys.argv),
            'scope': 'Public temporary filesystem capability only; no product assertion or suite PASS'}


def regular_map(root):
    result = {}
    for folder in ('rouge', 'tests', 'scripts'):
        base = root / folder
        require(base.is_dir() and not base.is_symlink(), 'Maintained Source directory missing or symlinked: ' + folder)
        for path in sorted(base.rglob('*')):
            if path.suffix not in ('.py', '.json'):
                continue
            require(path.is_file() and not path.is_symlink(), 'Maintained Source entry is not a regular file: ' + str(path))
            result[path.relative_to(root).as_posix()] = digest(path.read_bytes())
    return result


def validate_hash_map(value, label):
    require(isinstance(value, dict) and bool(value), 'Nonempty hash map required: ' + label)
    for key, sha in value.items():
        require(isinstance(key, str) and isinstance(sha, str) and re.fullmatch('[0-9a-f]{64}', sha),
                'Invalid Source digest in ' + label)
    return value


def additional_map(root, expected):
    validate_hash_map(expected, 'source_additional_sha256')
    require('CORE_0.70_VERIFICATION.json' in expected, 'Root must bind historical selector registration')
    result = {}
    for relative in expected:
        require(relative in ADDITIONAL_ALLOWED, 'Additional Source is outside explicit public-root allowlist: ' + relative)
        result[relative] = reference(root / relative)['sha256']
    return result


def workspace_evidence_path(value):
    require(isinstance(value, str), 'Evidence reference path must be a string')
    if value.startswith('/workspace/'):
        value = str(PureWindowsPath('Z:/' + value.lstrip('/')))
    path = Path(value).resolve()
    parts = PureWindowsPath(str(path)).parts
    require(len(parts) >= 3 and parts[0].casefold() == 'z:\\' and parts[1].casefold() == 'workspace',
            'Only explicit public workspace evidence is admitted')
    return path


def checked_reference(expected, supplied):
    require(isinstance(expected, dict) and set(expected) == {'path', 'bytes', 'sha256'}, 'Exact file-reference schema required')
    expected_path = workspace_evidence_path(expected['path'])
    supplied = workspace_evidence_path(str(supplied))
    require(expected_path == supplied, 'CLI evidence path differs from Root guard reference')
    actual = reference(supplied)
    require(type(expected['bytes']) is int and actual['bytes'] == expected['bytes']
            and actual['sha256'] == expected['sha256'], 'Root-bound evidence bytes or SHA changed')
    return actual


def parse_suite_args(description, allow_require_complete=False):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--guard', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--probe', type=Path, required=True)
    parser.add_argument('--wine', action='store_true')
    if allow_require_complete:
        parser.add_argument('--require-complete', action='store_true')
    return parser.parse_args()


def bind_suite(args):
    require_wine(args.wine)
    root = workspace_evidence_path(str(args.root))
    args.guard = workspace_evidence_path(str(args.guard))
    args.out = workspace_evidence_path(str(args.out))
    args.probe = workspace_evidence_path(str(args.probe))
    guard_ref = reference(args.guard)
    guard = json.loads(args.guard.read_bytes())
    require(guard.get('section') == 110 and type(guard.get('section')) is int,
            'An actual completed110 Root guard is required; historical095 or pending guards are forbidden')
    expected = validate_hash_map(guard.get('source_sha256'), 'source_sha256')
    source = regular_map(root)
    require(source == expected, 'Actual maintained rouge/tests/scripts .py/.json set or bytes differ from Root110 guard')
    additional = additional_map(root, guard.get('source_additional_sha256'))
    require(additional == guard['source_additional_sha256'], 'Additional selector/Root Source differs from guard')
    adapters = packet_sources()
    require(adapters == validate_hash_map(guard.get('adapter_source_sha256'), 'adapter_source_sha256'),
            'Exact sealed adapter Source differs from Root110 guard')
    probe_ref = checked_reference(guard.get('wine_capability_probe'), args.probe)
    exit_ref = guard.get('wine_capability_probe_primary_exit')
    probe_exit = checked_reference(exit_ref, workspace_evidence_path(exit_ref['path']))
    require(workspace_evidence_path(exit_ref['path']).read_bytes() == b'0\n',
            'Independent Root probe has no retained actual zero primary')
    prior = json.loads(args.probe.read_bytes())
    require(prior.get('passed') is True and prior.get('project_imports') == 0
            and prior.get('project_calls') == 0 and prior.get('private_state_access') is False
            and prior.get('native_windows_integration_verified') is False
            and prior.get('source_sha256') == adapters and prior.get('source_drift') == [],
            'Independent Root capability receipt has incompatible identity, Source or scope')
    fresh = fresh_capability(args.wine)
    require(fresh['passed'] is True and classify_observations(prior.get('observations')) == prior.get('admission_mode')
            and fresh['admission_mode'] == prior['admission_mode'],
            'Fresh suite controls differ from independently recorded capability; no cases admitted')
    require(prior.get('identity') == fresh['identity']
            and Path(prior['default_temp']).resolve() == Path(fresh['default_temp']).resolve(),
            'Independent and fresh controls differ in actual Wine identity or default Temp volume')
    require(datetime.fromisoformat(prior['checked_at']) <= datetime.fromisoformat(fresh['checked_at']),
            'Independent probe timestamp is after fresh suite controls')
    require(not args.out.exists() and not args.out.with_suffix('.log').exists(), 'Fresh exclusive output/log required')
    sys.path.insert(0, str(root))
    sys.path.insert(0, str(root / 'scripts'))
    classifier = importlib.import_module('verify_full_available')
    cloud = importlib.import_module('verify_cloud')
    require(Path(classifier.__file__).resolve() == root / 'scripts' / 'verify_full_available.py'
            and Path(cloud.__file__).resolve() == root / 'scripts' / 'verify_cloud.py'
            and classifier.ROOT.resolve() == root and cloud.ROOT.resolve() == root,
            'Loaded maintained selector/classifier module is outside the exact Root')
    tree = ast.parse((root / 'scripts/verify_full_available.py').read_bytes())
    actual_ast = {node.name: digest(ast.dump(node, include_attributes=False).encode('utf-8'))
                  for node in tree.body if isinstance(node, (ast.ClassDef, ast.FunctionDef))
                  and node.name in EXPECTED_CLASSIFIER_AST}
    require(actual_ast == EXPECTED_CLASSIFIER_AST, 'Maintained AvailableResult classification changed; new Source review required')
    return {'root': root, 'guard': guard, 'guard_reference': guard_ref,
            'source_sha256': source, 'source_additional_sha256': additional,
            'adapter_source_sha256': adapters, 'independent_capability_probe': probe_ref,
            'independent_capability_probe_primary_exit': probe_exit,
            'capability_probe': fresh, 'classifier': classifier, 'cloud': cloud}


def source_after(binding, args):
    source = regular_map(binding['root'])
    additional = additional_map(binding['root'], binding['guard']['source_additional_sha256'])
    adapters = packet_sources()
    require(reference(args.guard) == binding['guard_reference'], 'Root guard changed during suite')
    checked_reference(binding['guard']['wine_capability_probe'], args.probe)
    exit_ref = binding['guard']['wine_capability_probe_primary_exit']
    checked_reference(exit_ref, workspace_evidence_path(exit_ref['path']))
    return source, additional, adapters


class FixtureCapabilitySkip(unittest.TestCase):
    def __init__(self, original_id):
        super().__init__('runTest')
        self.original_id = original_id

    def id(self):
        return self.original_id

    def __str__(self):
        return self.original_id

    def runTest(self):
        self.skipTest(SKIP_REASON)


def admit_suite(suite, capability):
    require(capability.get('platform') == 'Windows' and capability.get('wine_compatibility') is True
            and capability.get('native_windows_integration_verified') is False
            and capability.get('identity', {}).get('active_kernelbase', {}).get('sha256') == KERNELBASE_SHA
            and capability.get('identity', {}).get('active_ntdll', {}).get('sha256') == NTDLL_SHA,
            'Suite capability is not the exact diagnosed actual Wine identity')
    mode = capability['admission_mode']
    require(mode in ('genuine_links', 'diagnosed_phantom_success', 'original_creation_exceptions'),
            'Unrecognized capability may not modify the suite')
    found = []

    def walk(current):
        if isinstance(current, unittest.TestSuite):
            return unittest.TestSuite(walk(child) for child in current)
        if current.id() in TEST_IDS:
            require(current.id() not in found, 'Duplicate allowlisted fixture in original loader')
            found.append(current.id())
            if mode == 'diagnosed_phantom_success':
                return FixtureCapabilitySkip(current.id())
        return current

    adapted = walk(suite)
    require(set(found) == set(TEST_IDS) and len(found) == 3, 'All three original fixture cases must exist exactly once')
    if mode != 'diagnosed_phantom_success':
        return adapted, []
    require(all(phantom(row, present) for row, present in zip(capability['observations'], (False, True), strict=True)),
            'Phantom admission lacks exact two-control shape')
    records = [{'test': test_id, 'kind': 'environment_capability', 'classification': 'declared_skip',
                'reason': SKIP_REASON, 'pre_product_fixture_admission': True,
                'actually_executed': False, 'fixture_body_run': False,
                'product_assertions_passed': False, 'capability_probe_pointer': '/capability_probe',
                'historical_full095_failure_reference_only': True} for test_id in found]
    return adapted, records


def validate_skips(result, records):
    if records:
        actual = [(test.id(), reason) for test, reason in result.skipped if test.id() in TEST_IDS]
        require(actual == [(row['test'], SKIP_REASON) for row in records],
                'Three admitted fixture leaves were not recorded as their exact ordinary skips')


def common_receipt(binding, args, records):
    source, additional, adapters = source_after(binding, args)
    drift = [name for name in sorted(set(source) | set(binding['source_sha256']))
             if source.get(name) != binding['source_sha256'].get(name)]
    additional_drift = [name for name in sorted(set(additional) | set(binding['source_additional_sha256']))
                        if additional.get(name) != binding['source_additional_sha256'].get(name)]
    adapter_drift = [name for name in sorted(set(adapters) | set(binding['adapter_source_sha256']))
                     if adapters.get(name) != binding['adapter_source_sha256'].get(name)]
    return {'format_version': 1, 'section': 110, 'checked_at': now(),
            'platform': platform.system(), 'wine_compatibility': True,
            'native_windows_integration_verified': False,
            'root_guard': binding['guard_reference'],
            'source_sha256': binding['source_sha256'], 'source_sha256_after': source, 'source_drift': drift,
            'source_additional_sha256': binding['source_additional_sha256'],
            'source_additional_sha256_after': additional, 'source_additional_drift': additional_drift,
            'adapter_source_sha256': binding['adapter_source_sha256'],
            'adapter_source_sha256_after': adapters, 'adapter_source_drift': adapter_drift,
            'capability_probe': binding['capability_probe'],
            'independent_capability_probe': binding['independent_capability_probe'],
            'independent_capability_probe_primary_exit': binding['independent_capability_probe_primary_exit'],
            'capability_records': records, 'environment_capability_skips': len(records),
            'capability_skips_counted_passed': 0,
            'capability_rows_overlap_ordinary_skips': True,
            'historical_full095_reused_as_current_gate': False,
            'historical_full095_evidence_written_by_adapter': False,
            'full095_ui_retried_by_adapter': False,
            'actual_python_argv': list(sys.argv), 'actual_cwd': str(Path.cwd()),
            'is_unittest_discover': False}


def drift_free(receipt):
    return not (receipt['source_drift'] or receipt['source_additional_drift'] or receipt['adapter_source_drift'])
