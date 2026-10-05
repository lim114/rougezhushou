"""Recheck static installation bytes and the attribute-boundary evidence chain."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / '.cache/research/attribute-boundaries-065'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    paths = [DIR / n for n in ('attribute-range-cfg.json', 'sp-speed-cfg.json',
        'metadata-ranges.json', 'read_attribute_ranges.py', 'parser-source-receipt.json',
        'parser-source-addendum.json', 'CustomAttributeDataReader.cs', 'MetadataClass.cs',
        'Il2CppExecutor.cs', 'BinaryReaderExtensions.cs', 'LICENSE')]
    paths += [ROOT / '.cache/research/p1-native-runtime-054/metadata-native-fields.json',
        ROOT / '.cache/research/p1-native-runtime-054/read_metadata_static.py',
        ROOT / '.cache/research/p1-native-cost-054/extract_cfg.py', Path(__file__)]
    ranges, getters, metadata = [json.loads((DIR / name).read_text(encoding='utf-8'))
        for name in ('attribute-range-cfg.json', 'sp-speed-cfg.json', 'metadata-ranges.json')]
    dll = Path(ranges['source_game_dll'])
    meta = dll.parent / 'Arknights_Data/il2cpp_data/Metadata/global-metadata.dat'
    assert sha(dll) == ranges['dll_sha256'] == metadata['dll_sha256'] == getters['dll_sha256']
    assert sha(meta) == ranges['metadata_sha256'] == metadata['metadata_sha256']
    methods = ranges['methods'] + getters['methods']
    with dll.open('rb') as stream:
        for method in methods:
            assert method['cfg_bounded_traversal_finished'] and not method['limits']
            for row in method['instructions']:
                stream.seek(int(row['physical_offset'], 16))
                assert stream.read(len(bytes.fromhex(row['bytes']))).hex() == row['bytes']
    instructions = {row['address']: row for m in methods for row in m['instructions']}
    checks = {
        '0x18230abba': ('mov', 'ebx, edx'),
        '0x18230abca': ('movaps', 'xmm6, xmm2'),
        '0x18230abdc': ('movss', 'dword ptr [rdi + 0x18], xmm6'),
        '0x18230abe6': ('mov', 'dword ptr [rdi + 0x10], ebx'),
        '0x18230abee': ('mov', 'byte ptr [rdi + 0x20], 1'),
        '0x18070eb39': ('mov', 'edx, 7'),
        '0x18070eb46': ('jmp', '0x180655b30'),
        '0x180cce3f5': ('call', '0x18230aa00'),
        '0x180cce427': ('call', '0x186316210'),
        '0x180cce438': ('call', '0x18230c200'),
        '0x1806567c5': ('call', '0x18230aa00'),
        '0x18065688b': ('call', '0x186316210'),
        '0x180657534': ('call', '0x186316210'),
    }
    for addr, expected in checks.items():
        row = instructions[addr]
        assert (row['mnemonic'], row['operands']) == expected
    fields = json.loads(paths[-4].read_text(encoding='utf-8'))
    attribute = next(t for t in fields['selected'] if t['name'] == 'Torappu.AttributeMetaAttribute')
    offsets = {f['name']: f['offset'] for f in attribute['fields']}
    assert offsets['m_min'] == 24 and offsets['m_hasMin'] == 32 and offsets['m_hasMax'] == 33
    with meta.open('rb') as stream:
        for field, expected in zip(metadata['fields'], [(7, 20.0), (14, 0.0), (30, 0.0)]):
            assert field['fully_consumed']
            stream.seek(field['physical_offset'])
            assert stream.read(len(bytes.fromhex(field['raw_hex']))).hex() == field['raw_hex']
            attr = field['attributes'][0]
            assert attr['constructor_address'] == '0x18230abb0'
            assert tuple(a['value'] for a in attr['arguments']) == expected
    result = {'passed': True, 'dll_sha256': sha(dll), 'metadata_sha256': sha(meta),
        'methods_checked': len(methods), 'instruction_bytes_checked': sum(m['instruction_count'] for m in methods),
        'default_attack_speed_minimum': 20, 'attribute_has_upper_bound': False,
        'rune_range_before_attribute_writer': True, 'ordinary_range_after_all_modifiers': True,
        'metadata_decoder': 'Il2CppDumper v6.7.46 v29 custom-attribute serialization',
        'source_sha256': {p.relative_to(ROOT).as_posix(): sha(p) for p in paths},
        'file_only': True, 'dll_executed': False, 'process_memory_read': False,
        'current_hotfix_equivalence_proven': False, 'explicit_runtime_range_override_supported': False,
        'sp_boundaries_researched_but_numeric_model_unchanged': True}
    (DIR / 'native-proof.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k != 'source_sha256'}))


if __name__ == '__main__': main()
