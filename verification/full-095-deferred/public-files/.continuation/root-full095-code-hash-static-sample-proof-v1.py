import hashlib
import json
import struct
from pathlib import Path

BASE = Path('/workspace/.continuation')
PACKAGE = Path('/workspace/.compat/python-windows/package/tools')
def ref(path):
    path = Path(path)
    raw = path.read_bytes()
    return {'path': str(path), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}

binary = PACKAGE / 'python312.dll'
b = binary.read_bytes()
assert ref(binary)['sha256'] == '9a0e3435aaa680d868150f87ab3e388ad2eebc22f87e036155c7b4eda8cd2120'
pe = struct.unpack_from('<I', b, 0x3c)[0]
assert b[:2] == b'MZ' and b[pe:pe + 4] == b'PE\0\0'
machine, count = struct.unpack_from('<HH', b, pe + 4)
opt = pe + 24
osize = struct.unpack_from('<H', b, pe + 20)[0]
assert machine == 0x8664 and struct.unpack_from('<H', b, opt)[0] == 0x20b
image_base = struct.unpack_from('<Q', b, opt + 24)[0]
sections = []
for number in range(count):
    virtual_size, va, raw_size, raw_pointer = struct.unpack_from('<IIII', b, opt + osize + 40 * number + 8)
    sections.append((va, max(virtual_size, raw_size), raw_pointer, raw_size))
def offset(rva):
    for va, size, raw_pointer, raw_size in sections:
        if va <= rva < va + size:
            assert rva - va < raw_size
            return raw_pointer + rva - va
    raise ValueError('Unmapped RVA')
def cstring(rva):
    start = offset(rva)
    return b[start:b.index(b'\0', start)]

export_rva, export_size = struct.unpack_from('<II', b, opt + 112)
export = offset(export_rva)
names_count = struct.unpack_from('<I', b, export + 24)[0]
functions_rva, names_rva, ordinals_rva = struct.unpack_from('<III', b, export + 28)
for number in range(names_count):
    name_rva = struct.unpack_from('<I', b, offset(names_rva) + 4 * number)[0]
    if cstring(name_rva) == b'PyCode_Type':
        ordinal = struct.unpack_from('<H', b, offset(ordinals_rva) + 2 * number)[0]
        type_rva = struct.unpack_from('<I', b, offset(functions_rva) + 4 * ordinal)[0]
        break
else:
    raise ValueError('PyCode_Type export absent')
# Installed release x64 headers: PyVarObject is 24 bytes; name plus 11
# pointer/Py_ssize_t fields precede tp_hash. These are the same package headers.
header = (PACKAGE / 'include/cpython/object.h').read_text()
assert 'struct _typeobject {' in header and 'hashfunc tp_hash;' in header
assert cstring(struct.unpack_from('<Q', b, offset(type_rva) + 24)[0] - image_base) == b'code'
hash_rva = struct.unpack_from('<Q', b, offset(type_rva) + 120)[0] - image_base
pdata_rva, pdata_size = struct.unpack_from('<II', b, opt + 112 + 3 * 8)
assert pdata_size % 12 == 0
matches = []
for number in range(pdata_size // 12):
    start, end, unwind = struct.unpack_from('<III', b, offset(pdata_rva) + 12 * number)
    if start == hash_rva:
        matches.append((start, end, unwind))
assert len(matches) == 1
start, end, unwind = matches[0]
source = BASE / 'full095-cpython-lineno-source-diagnosis-v1/Objects-codeobject.c'
source_text = source.read_text()
assert '(hashfunc)code_hash,                /* tp_hash */' in source_text
classified = []
for version in ('v1', 'v2'):
    log = BASE / ('root-full095-ui-cache-readonly-native-location-' + version + '.log')
    raw_exit = BASE / ('root-full095-ui-cache-readonly-native-location-' + version + '.exit-code')
    assert raw_exit.read_bytes() == b'0\n'
    report = json.loads(log.read_bytes())
    assert report['process_not_left_traced'] is True and report['UI_PASS_claimed'] is False
    assert report['memory_or_register_writes'] == report['project_calls'] == report['new_wine_executions'] == 0
    rows = []
    for sample in report['samples']:
        hashes = [item for item in sample['matching_PE_images'] if item['sha256'] == ref(binary)['sha256']]
        assert len(hashes) <= 1
        rva = int(hashes[0]['relative_virtual_address'], 16) if hashes else None
        rows.append({'sample': sample['sample'], 'python312_RVA': hex(rva) if rva is not None else None,
                     'within_actual_CodeType_tp_hash_PE_function': rva is not None and start <= rva < end})
    classified.append({'probe': version, 'actual_probe_log': ref(log), 'actual_probe_exit': ref(raw_exit),
                       'sample_count': len(rows), 'samples_within_actual_hash_function': sum(row['within_actual_CodeType_tp_hash_PE_function'] for row in rows),
                       'rows': rows})
result = {'status': 'ACTUAL_BOUNDED_NATIVE_SAMPLES_CORRELATED_WITH_STATIC_PUBLIC_BINARY_AND_SOURCE',
          'binary_reference_only_not_archive_selection': ref(binary),
          'installed_release_x64_header_refs': [ref(PACKAGE / 'include/object.h'), ref(PACKAGE / 'include/cpython/object.h')],
          'official_pinned_CPython_source': ref(source), 'code_hash_source_lines': [1862, 1898],
          'PyCode_Type_tp_hash_initializer_source_line': 2156,
          'PyCode_Type_export_RVA': hex(type_rva), 'tp_hash_field_offset': 120,
          'actual_PE_unwind_function_range_RVAs': [hex(start), hex(end)],
          'actual_samples': classified, 'runtime_time_percentage': None, 'exact_code_object_at_sample': None,
          'complete_performance_root_cause_established': False, 'future_cache_improvement_measured': False,
          'UI_primary_exit_observed': False, 'UI_PASS_claimed': False,
          'project_calls': 0, 'new_Wine_executions': 0, 'active_process_changes_by_this_static_correlator': 0}
out = BASE / 'root-full095-code-hash-static-sample-proof-v1.json'
with out.open('x', encoding='utf-8') as handle:
    json.dump(result, handle, indent=2)
    handle.write('\n')
print(json.dumps({'proof': ref(out), 'actual_function_range': [hex(start), hex(end)],
                  'actual_probe_sample_counts': [(item['sample_count'], item['samples_within_actual_hash_function']) for item in classified],
                  'UI_PASS_claimed': False}))
