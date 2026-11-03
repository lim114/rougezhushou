"""File-only bounded source review. Does not load or execute the 282 prototype."""
from pathlib import Path
import hashlib
import json
import mmap
import struct

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = HERE / 'source-candidate-original-547b8f2d.json'
EXPECTED = '547b8f2d149462ed21fb68a46d627ffa2e7e839ffbdead78620df71265914887'
OUT = HERE / 'source-design-review-282.json'
assert not OUT.exists(), 'Preserve the first source review.'
raw = INPUT.read_bytes()
assert hashlib.sha256(raw).hexdigest() == EXPECTED
source = json.loads(raw)
checks = []
def check(name, ok):
    checks.append({'name': name, 'passed': bool(ok)})

# This is a fresh read of files, not process memory. Existing source groups remain reused.
files = {
    'dll': Path(r'D:\Hypergryph Launcher\games\Arknights\GameAssembly.dll'),
    'metadata': Path(r'D:\Hypergryph Launcher\games\Arknights\Arknights_Data\il2cpp_data\Metadata\global-metadata.dat'),
}
expected = {'dll': '583b04ff4d1b1a4b35eaf09d77d936408c25447c9e345ef0463d814b6a123fc5',
            'metadata': 'd3fede171f92740a6f5dc053c58c7013d3c962db764ad1f05cbe977c074fcd1f'}
fresh = {}
failed_spans = []
for kind, path in files.items():
    with path.open('rb') as handle, mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_READ) as original:
        digest = hashlib.sha256(original).hexdigest()
        check(kind + '.complete_file_sha', digest == expected[kind])
        selected = [span for span in source['byte_spans'] if span['source'] == kind]
        for span in selected:
            offset = span['physical_offset']
            offset = int(offset, 0) if isinstance(offset, str) else offset
            value = bytes.fromhex(span['raw_hex'])
            if original[offset:offset + len(value)] != value:
                failed_spans.append({'source': kind, 'offset': offset, 'label': span['label']})
        fresh[kind] = {'sha256': digest, 'selected_span_count': len(selected),
                       'unique_exact_spans': len({(s['physical_offset'], s['raw_hex']) for s in selected})}
check('all_selected_file_spans_exact', not failed_spans)

methods = {m['method']['metadata_method_index']: m for m in source['methods']}
instructions = {i['address']: i for m in source['methods'] for i in m['instructions']}
def ins(address, mnemonic=None, operand=None):
    row = instructions[address]
    check('instruction.' + address, (mnemonic is None or row['mnemonic'] == mnemonic) and (operand is None or row['operands'] == operand))
    return row

# The computed jump is not generally closed. Only the exact 14 and direct 30 paths are claimed.
ins('0x1806f7440', 'lea', 'eax, [rbx - 7]')
ins('0x1806f7443', 'cmp', 'eax, 8')
ins('0x1806f7459', 'mov', 'eax, dword ptr [rdx + rcx*4 + 0x6f79bc]')
ins('0x1806f7463', 'jmp', 'rax')
table = next(t for t in source['entity_dirty_switch'] if t['attribute'] == 14)
target = hex(0x180000000 + struct.unpack('<I', bytes.fromhex(table['raw_hex']))[0])
check('attribute14_table_target', table['address'] == '0x1806f79d8' and target == '0x1806f7701')
ins('0x1806f71a7', 'lea', 'ecx, [rbx - 0x1c]')
ins('0x1806f71b2', 'sub', 'ecx, 1')
ins('0x1806f71bb', 'cmp', 'ecx, 1')
ins('0x1806f71be', 'je', '0x1806f7701')
check('attribute30_direct_same_target', 30 - 0x1c - 1 == 1)

# Important ordering: capture raw array before encoding, guard it only afterward.
for address, mnemonic, operand in [
    ('0x18064a139', 'mov', 'rbp, qword ptr [rsi + 0x58]'),
    ('0x18064a150', 'call', '0x1866fe6e0'),
    ('0x18064a155', 'test', 'rbp, rbp'),
    ('0x18064a15a', 'cmp', 'r14d, dword ptr [rbp + 0x18]'),
    ('0x18064a16c', 'movups', 'xmmword ptr [rbp + rcx*8 + 0x20], xmm0'),
    ('0x18064a175', 'movups', 'xmmword ptr [rbp + rcx*8 + 0x30], xmm1'),
    ('0x18064a17f', 'movsd', 'qword ptr [rbp + rcx*8 + 0x40], xmm0'),
    ('0x18064a188', 'call', '0x180649a90'),
    ('0x18064a18d', 'test', 'r15b, r15b'),
    ('0x18064a19a', 'call', '0x1806499a0')]:
    ins(address, mnemonic, operand)

# The first delegate existence read precedes committing the dirty mask.
for address, mnemonic, operand in [
    ('0x180649ad5', 'bts', 'rbx, rax'),
    ('0x180649ad9', 'cmp', 'qword ptr [rdi + 0x80], 0'),
    ('0x180649ae1', 'mov', 'qword ptr [rdi + 0x78], rbx'),
    ('0x180649af9', 'mov', 'rbp, qword ptr [rdi + 0x80]'),
    ('0x180649b3c', 'call', '0x1866fe710'),
    ('0x180649b41', 'mov', 'r10, qword ptr [rbp + 0x18]'),
    ('0x180649b52', 'call', 'r10'),
    ('0x180649c0b', 'call', '0x1866fe710'),
    ('0x180649c10', 'test', 'rdi, rdi'),
    ('0x180649c2f', 'cmp', 'ebx, 0x26')]:
    ins(address, mnemonic, operand)

# Independent Init attributes reads: Reset, overwrite target, and subscribe target.
for address, target_call in [('0x1806f532d', '0x180701e20'), ('0x1806f534e', '0x180701e20'),
                             ('0x1806f537d', '0x1844dc660'), ('0x1806f53b6', '0x1866fdad0'),
                             ('0x1806f53d7', '0x18064a0f0'), ('0x1806f53e1', '0x180701e20'),
                             ('0x1806f5435', '0x185880ed0'), ('0x1806f5443', '0x185f16130')]:
    ins(address, 'call', target_call)
ins('0x1806f5378', 'xor', 'ecx, ecx')
ins('0x1806f53c4', 'mov', 'r9b, 1')
ins('0x1806f53cf', 'mov', 'edx, 0xe')
ins('0x1806f542e', 'mov', 'r8, qword ptr [r8 + 0x928]')
ins('0x1806f53f9', 'mov', 'r15, qword ptr [rax + 0x80]')

# 14/30 are an inline controller-rate update, with the same explicit 274 branches.
for address, mnemonic, operand in [
    ('0x1806f7701', 'mov', 'r14, qword ptr [rsi + 0xf8]'),
    ('0x1806f770d', 'call', '0x180708750'),
    ('0x1806f7715', 'test', 'r14, r14'),
    ('0x1806f7770', 'call', '0x181e04d40'),
    ('0x1806f77a4', 'call', '0x18070a1c0'),
    ('0x1806f77a9', 'mov', 'rcx, qword ptr [r14 + 0x18]'),
    ('0x1806f77b8', 'call', '0x180702490'),
    ('0x1806f77c6', 'call', '0x180709f20'),
    ('0x1806f7801', 'jmp', '0x1806f76ce'),
    ('0x1806f76e5', 'call', '0x181e044e0'),
    ('0x1806f784a', 'call', '0x181e04750')]:
    ins(address, mnemonic, operand)
for address, operand in [('0x1807087da', '0x1806499a0'), ('0x18070884a', '0x1806499a0'),
                         ('0x180702509', '0x180708750'), ('0x18070255a', '0x1866e4c60')]:
    ins(address, None, operand)
ins('0x1807087d2', 'mov', 'edx, 0xe')
ins('0x180708842', 'mov', 'edx, 0x1e')
check('no_call_to_rate_update_callee_in_selected_branch', not any(i.get('target') == '0x18070a670' for i in methods[66699]['instructions']))

# Standard inheritance forwards first, then ignores 14/30 in later non-SP cases.
ins('0x180a2c8c9', 'call', '0x180ac9c50')
ins('0x180ac9cb8', 'call', '0x1806f7100')
ins('0x180ac9cbd', 'cmp', 'esi, 0xf')
for index in (66699, 76035, 77706):
    entry = next(m for m in source['method_metadata'] if m['index'] == index)
    check('source_virtual_slot126.' + str(index), entry['slot'] == 126)

init = methods[66624]
counts = [{'method_index': index, 'selected_instructions': len(m['instructions']),
           'selected_instruction_bytes': sum(len(bytes.fromhex(i['bytes'])) for i in m['instructions']),
           'candidate_reported_instruction_count': m.get('instruction_count'),
           'whole_method_claim': m.get('whole_method_claim', 'bounded artifact; no dynamic target closure claimed')}
          for index, m in methods.items()]
unique_instructions = {i['address']: i['bytes'] for m in methods.values() for i in m['instructions']}
check('candidate_selected_instruction_count', len(unique_instructions) == 1647)
check('candidate_selected_spans_count', len(source['byte_spans']) == 1833)
check('init_prefix_only', init['whole_method_claim'] is False and len(init['instructions']) == 92)

facts = [
    {'id': 'attribute_reference', 'fact': 'The generic GetValue/_CalculateAttributeValue index/range machinery can be qualified separately for14/30; clean cached decode and dirty recomputation are different observed reads. Existing273 source is reused; its public13/19 validator is not silently broadened.',
     'requirements': ['complete ordered registered-modifier observations', 'all required member normal/include facts', 'independent four cached buckets', 'raw decoded value and raw normal independent', 'dynamic min/max reads independent', 'early dirty clear before raw read', 'cache encoder/store normal independent from returned reference']},
    {'id': 'formula', 'fact': 'Existing generic formula remains ((raw + ADD) * Max(0, MULTIP) + FINALADD) * FINALSCALER, then native Clamp. Bucket seeds are0/ONE/0/ONE;14 and30 metadata lower bound0 and default upper FP.MaxValue are reused under their normal default-range construction, not forced over dynamic overrides.'},
    {'id': 'overwrite', 'fact': 'Overwrite captures raw array, resolves index and encodes before testing the captured array or bounds; writes16+16+8 bytes; calls MarkAttributeDirty; only after its normal return does refresh=true call GetValue. Encoder argument is not a later decoded raw/cache observation.'},
    {'id': 'dirty_callback', 'fact': 'Local BTS precedes first callback-presence CMP, which precedes the dirty-mask write and branch. The delegate pointer is captured again only on the first-presence true path. Cached protected value decode precedes dereferencing/invoking that captured delegate. It is the old cached observation, not the newly encoded raw value.'},
    {'id': 'bulk_dirty_distinct', 'fact': 'MarkAttributesDirty ORs the whole mask first, has its own initial presence check, and considers selected positive bits in indices0..37. Each selected iteration captures a delegate and decodes cache before an explicit delegate NULL guard. Do not reuse the single-dirty ordering unchanged.'},
    {'id': 'init', 'fact': 'Init reads attributes for Reset, independently reads overwrite target, reads increment slot0 with native array guards, converts Single to FP, calls OverwriteRawData14 with refresh=true, then independently reads subscription target and its existing delegate; constructs virtual handler, Combine and subscription writes follow. Neither old delegate absence nor equality of the three attributes targets is proved.'},
    {'id': 'notification', 'fact': 'Selected native Character→Unit→Entity inheritance forwards14/30 to Entity. Case14 computed-jump table and case30 direct tests reach7701; this region captures controller, gets new rate, then checks controller NULL. It inlines controller update logic rather than calling66750.'},
    {'id': 'rate', 'fact': 'New-rate getter reads attribute14 then attribute30 via two independently qualified attributes getter calls and FP-multiplies them. Valid timer update drainsOnTick0, then separately calls canRecover on controller owner, whose normal native path reads rate again and applies strict signed GT against0. That boolean cannot be inferred from the earlier new-rate argument.'},
]
required_cases = [
    'raw-array NULL: encode may be a known completed prefix before the guard failure; no MarkDirty/refresh',
    'first callback absent: dirty write may complete; no old-cache decode/invoke, then explicit refresh may continue',
    'first callback present + second delegate NULL: single-dirty cache decode precedes its dereference failure',
    'callback normal=false: preceding raw40 and dirty-write prefixes persist; refresh is not called',
    'callback normal=unknown: completed prefixes persist; refresh called status remains unknown',
    'initialization overwrite failure or unknown normality: do not claim later handler construction/Combine/subscription',
    'preexisting delegate may run during initial overwrite before this subscription; later state reads cannot be synthesized',
    'captured controller NULL: the new-rate getter is still called before the NULL failure',
    'valid timer plus canRecover=false invalidates after drain even if earlier new-rate argument is positive',
    'earlier new-rate and later canRecover rate may differ; no same-owner/same-attributes assumption',
    'dirty-clear followed by failed raw read/cache encode/store retains early clear prefix, not a successful getter',
]
notes = [
    {'severity': 'source_contract_precision', 'detail': 'Correct prose/order placing the first callback-presence read after dirty write. Its CMP is649ad9, before MOV649ae1; actual callback invocation remains after dirty write.'},
    {'severity': 'source_receipt_precision', 'detail': 'Candidate Init still carries inherited719-instruction/3127-byte/full hash fields beside selected92-instruction/384-byte prefix. Preserve original provenance separately and label/recompute selected-prefix counts/hash before publication; this review counts only the selected92 and claims no full Init closure.'},
]
unknowns = [
    'Actual runtime attributes/controller/delegate identity or equality, preexisting delegate list and dispatch targets',
    'Combine result, accepted subscription/write-barrier completion and effects of any callback/reentrancy',
    'Encode/decode roundtrip or decoded cache/raw equality without independent observed qualification',
    'Dynamic registrations/modified range/hotfix and actual current timer/SP/complete skill cycle',
    'Whole Entity.OnAttributeDirty computed-jump and all of Entity.Init remain outside selected closure',
]
report = {'kind': 'SECTION282_LIMITED_INDEPENDENT_SOURCE_DESIGN_REVIEW',
          'source_candidate_sha256': EXPECTED, 'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'originals': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in HERE.glob('*.json') if p != OUT},
          'fresh_file_readback': fresh, 'all_selected_spans_match': not failed_spans, 'failed_spans': failed_spans,
          'selected_artifact_method_entries': len(methods), 'selected_unique_instructions': len(unique_instructions),
          'selected_byte_span_count': len(source['byte_spans']), 'per_entry_selected_counts': counts,
          'new_whole_native_methods_claimed': 0, 'new_full_audit_of_inherited273_274_279_proofs': False,
          'prototype_loaded_or_executed': False, 'production_or_author_files_changed': False,
          'game_dll_executed': False, 'process_memory_read': False, 'game_or_chat_operation': False,
          'mechanism_source_facts': facts, 'source_contract_corrections': notes,
          'implementation_acceptance_cases_not_executed': required_cases,
          'remaining_unknowns': unknowns, 'checks': checks, 'check_count': len(checks),
          'selected_source_checks_passed': all(c['passed'] for c in checks),
          'conclusion': 'Source supports a conditional14/30 reference group with separate initialization, overwrite/dirty notification and timer-update observations, subject to the noted order/count precision corrections. This is not section completion or implementation QA.'}
OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps({'source_checks_passed': report['selected_source_checks_passed'], 'checks': len(checks),
                  'selected_entries': len(methods), 'selected_unique_instructions': len(unique_instructions),
                  'selected_byte_spans': len(source['byte_spans']),
                  'receipt_sha256': hashlib.sha256(OUT.read_bytes()).hexdigest(),
                  'failed_checks': [c['name'] for c in checks if not c['passed']]}, ensure_ascii=False))
raise SystemExit(0 if report['selected_source_checks_passed'] else 1)
