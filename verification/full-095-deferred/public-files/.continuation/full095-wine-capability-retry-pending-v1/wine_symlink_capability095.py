"""Exact installed Wine symlink-fixture admission; not product validation.

The original test bodies and filesystem APIs remain untouched. Only two loaded
cases can be replaced by declared skips, after independent public Temp fixtures
reproduce the source-proven success-only stub on the pinned active Wine binaries.
Native Windows, different binaries, and unrecognized probe results fail closed.
"""
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path, PureWindowsPath
import platform
import stat
import tempfile
import unittest

PACKET = Path(__file__).resolve().parent
TEST_IDS = (
    'tests.test_account_cache_093.AccountCache093Tests.test_dangling_symlink_file_not_found_is_not_genuinely_absent',
    'tests.test_account_cache_093.AccountCache093Tests.test_symlink_to_damaged_file_retains_link_and_target_bytes',
)
KERNELBASE_SHA = '30875e36572fff7b6eaee0798e807342fd99fff4a857799d11171e6617c116a5'
NTDLL_SHA = '5e3846b0c3cdcb4009a5837719cbc02f2635892ed788bc2e592e344cced6b0c2'
SKIP_REASON = (
    'Declared installed-Wine environment capability skip: the independently '
    'probed, SHA-pinned CreateSymbolicLinkW success-only stub creates no symbolic '
    'link in the same default Temp volume. This fixture body and its AccountCache '
    'preservation assertions were not run and are not counted as passed; genuine '
    'Windows validation remains required. See capability_records and capability_probe.'
)


def _windows_path(posix_path):
    if not posix_path.startswith('/workspace/'):
        raise ValueError('Only the bound public workspace evidence is readable')
    return Path(PureWindowsPath('Z:/' + posix_path.lstrip('/')))


def file_reference(path):
    path = Path(path)
    data = path.read_bytes()
    return {'path': str(path), 'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest()}


def _read_bound_inputs():
    contract = json.loads((PACKET / 'source-contract-wine-capability095.json').read_text(encoding='utf-8'))
    references = contract['runtime_evidence_references']
    for name, reference in references.items():
        actual = file_reference(_windows_path(reference['path']))
        if actual['bytes'] != reference['bytes'] or actual['sha256'] != reference['sha256']:
            raise RuntimeError('Bound SOURCE/evidence changed: ' + name)
    failed = json.loads(_windows_path(references['old_failed_full_receipt']['path']).read_text(encoding='utf-8'))
    if (failed['available_checks_passed'] is not False or failed['failures'] != 1 or failed['errors'] != 1
            or tuple(row['test'] for row in failed['failed_cases']) != TEST_IDS
            or failed['source_drift'] != [] or len(failed['source_sha256']) != 342):
        raise RuntimeError('Original failed full095 receipt does not match the two prerequisite failures')
    if _windows_path(references['old_failed_primary_exit']['path']).read_bytes() != b'1\n':
        raise RuntimeError('Original full095 failure status was not retained')
    if _windows_path(references['root_capability_probe_exit']['path']).read_bytes() != b'0\n':
        raise RuntimeError('Independent root capability probe has no observed zero status')
    prior_text = _windows_path(references['root_capability_probe_log']['path']).read_text(encoding='utf-8')
    prior, trailing = json.JSONDecoder().raw_decode(prior_text.lstrip())
    if (prior.get('platform') != 'Windows' or prior.get('python') != '3.12.10'
            or prior.get('project_imports') != 0 or prior.get('private_state_access') is not False):
        raise RuntimeError('Independent root probe identity or scope does not match')
    for row, present in zip(prior['observations'], (False, True), strict=True):
        if not _phantom_success(row, present):
            raise RuntimeError('Independent root probe did not observe the exact phantom-success state')
    return contract, failed, prior


def _active_module_reference(module_name, expected_sha):
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    get_handle = kernel32.GetModuleHandleW
    get_handle.argtypes = (wintypes.LPCWSTR,)
    get_handle.restype = wintypes.HMODULE
    get_name = kernel32.GetModuleFileNameW
    get_name.argtypes = (wintypes.HMODULE, wintypes.LPWSTR, wintypes.DWORD)
    get_name.restype = wintypes.DWORD
    handle = get_handle(module_name)
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    buffer = ctypes.create_unicode_buffer(32768)
    length = get_name(handle, buffer, len(buffer))
    if not length or length >= len(buffer):
        raise RuntimeError('Cannot identify the active module: ' + module_name)
    actual = file_reference(Path(buffer.value))
    if actual['sha256'] != expected_sha:
        raise RuntimeError('The active module is not the diagnosed installed Wine binary: ' + module_name)
    return actual


def _observe_operation(link, operation):
    try:
        value = getattr(link, operation)()
        if operation == 'lstat':
            info = value
            value = {'mode': info.st_mode, 'is_link_mode': stat.S_ISLNK(info.st_mode),
                     'file_attributes': getattr(info, 'st_file_attributes', None),
                     'reparse_tag': getattr(info, 'st_reparse_tag', None)}
        elif operation == 'read_bytes':
            value = {'bytes_hex': value.hex()}
        else:
            value = str(value)
        return {'result': value}
    except OSError as exc:
        return {'error_type': type(exc).__name__, 'error': str(exc),
                'winerror': getattr(exc, 'winerror', None)}


def _phantom_success(row, present):
    creation = row.get('creation', {})
    return (
        row.get('target_present') is present
        and creation == {'returned_type': 'NoneType', 'returned_repr': 'None'}
        and row.get('is_symlink') is False and row.get('exists') is False
        and row.get('lstat', {}).get('error_type') == 'FileNotFoundError'
        and row['lstat'].get('winerror') == 2
        and row.get('readlink', {}).get('error_type') == 'FileNotFoundError'
        and row['readlink'].get('winerror') == 2
        and row.get('target_bytes_unchanged') is True
        and row.get('actual_directory_entries') == ([Path(row['target']).name] if present else [])
    )


def admit_installed_wine(wine):
    if wine is not True or os.name != 'nt' or platform.system() != 'Windows':
        raise RuntimeError('This external fixture admission requires explicit --wine and actual Windows Python')
    if platform.python_version() != '3.12.10':
        raise RuntimeError('The diagnosed Windows Python version changed')
    # This Wine-specific export is required, not WINEPREFIX or a platform label.
    try:
        ntdll = ctypes.CDLL('ntdll')
        wine_version = ntdll.wine_get_version
    except (OSError, AttributeError) as exc:
        raise RuntimeError('Actual Wine identity is absent; native Windows cannot use this skip') from exc
    wine_version.argtypes = ()
    wine_version.restype = ctypes.c_char_p
    returned = wine_version()
    if not returned:
        raise RuntimeError('Wine identity export returned no version')
    actual_version = returned.decode('ascii', errors='strict')
    identity = {'wine_specific_export': 'ntdll.wine_get_version', 'actual_version': actual_version,
                'active_kernelbase': _active_module_reference('kernelbase.dll', KERNELBASE_SHA),
                'active_ntdll': _active_module_reference('ntdll.dll', NTDLL_SHA)}
    contract, failed, prior = _read_bound_inputs()
    observations = []
    default_temp = str(Path(tempfile.gettempdir()))
    with tempfile.TemporaryDirectory(prefix='public-symlink-capability-retry095-') as folder:
        base = Path(folder)
        if base.drive.casefold() != Path(default_temp).drive.casefold():
            raise RuntimeError('Capability fixture is not in the default unittest Temp volume')
        for present in (False, True):
            target = base / ('present-target.json' if present else 'absent-target.json')
            original = b'{"public_bad_json":'
            if present:
                target.write_bytes(original)
            link = base / ('present-link.json' if present else 'absent-link.json')
            row = {'target_present': present, 'link': str(link), 'target': str(target)}
            try:
                returned = os.symlink(target, link)
                row['creation'] = {'returned_type': type(returned).__name__, 'returned_repr': repr(returned)}
            except (OSError, NotImplementedError) as exc:
                row['creation'] = {'error_type': type(exc).__name__, 'error': str(exc),
                                   'winerror': getattr(exc, 'winerror', None)}
            row['is_symlink'] = link.is_symlink()
            row['exists'] = link.exists()
            for operation in ('lstat', 'readlink', 'read_bytes'):
                row[operation] = _observe_operation(link, operation)
            row['actual_directory_entries'] = sorted(p.name for p in base.iterdir())
            row['target_bytes_unchanged'] = target.read_bytes() == original if present else not target.exists()
            observations.append(row)
    if not all(_phantom_success(row, present)
               for row, present in zip(observations, (False, True), strict=True)):
        raise RuntimeError('Fresh fixture capability does not match the exact diagnosed Wine phantom-success stub; no tests skipped')
    if Path(prior['observations'][0]['link']).drive.casefold() != Path(default_temp).drive.casefold():
        raise RuntimeError('Fresh default Temp volume differs from the independent root probe')
    return {'identity': identity, 'default_temp': default_temp, 'observations': observations,
            'runtime_evidence_references': contract['runtime_evidence_references'],
            'old_failed_full_primary_exit': 1, 'old_failed_full_receipt_preserved': True,
            'prior_failed_source_sha256': failed['source_sha256'],
            'native_windows_integration_verified': False,
            'project_calls_during_capability_probe': 0}


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
    """Keep original suite order and loader result; replace two exact leaf IDs."""
    if (capability.get('identity', {}).get('active_kernelbase', {}).get('sha256') != KERNELBASE_SHA
            or capability.get('identity', {}).get('active_ntdll', {}).get('sha256') != NTDLL_SHA
            or capability.get('old_failed_full_primary_exit') != 1
            or not all(_phantom_success(row, present) for row, present in
                       zip(capability['observations'], (False, True), strict=True))):
        raise RuntimeError('The loaded suite has no exact installed-Wine capability admission')
    admitted = []

    def walk(current):
        if isinstance(current, unittest.TestSuite):
            return unittest.TestSuite(walk(child) for child in current)
        if current.id() in TEST_IDS:
            if current.id() in admitted:
                raise RuntimeError('Repeated prerequisite case in original loader output')
            admitted.append(current.id())
            return FixtureCapabilitySkip(current.id())
        return current

    filtered = walk(suite)
    if set(admitted) != set(TEST_IDS) or len(admitted) != 2:
        raise RuntimeError('Exactly the two original prerequisite cases must be present')
    records = [{'test': test_id, 'kind': 'environment_capability', 'classification': 'declared_skip',
                'reason': SKIP_REASON, 'pre_product_fixture_admission': True,
                'actually_executed': False, 'fixture_body_run': False,
                'product_assertions_passed': False,
                'capability_probe_pointer': '/capability_probe',
                'original_failure_preserved': True} for test_id in admitted]
    return filtered, records


def adapter_sources():
    return {name: file_reference(PACKET / name) for name in (
        'wine_full095_capability_retry.py', 'wine_selected095_capability.py',
        'wine_symlink_capability095.py', 'source-contract-wine-capability095.json')}


def validate_result_capability_skips(result, records):
    actual = [(test.id(), reason) for test, reason in result.skipped if test.id() in TEST_IDS]
    expected = [(row['test'], SKIP_REASON) for row in records]
    if actual != expected:
        raise RuntimeError('The two admitted prerequisite cases were not reported as honest declared skips')
