"""Necessary cache preparation checks; reads original files, never native DLL code."""
import hashlib
import importlib.util
import json
import mmap
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CORE = ROOT / '.cache/section279-draft/rouge/skill_sp_increment_reference.py'
DATA = ROOT / '.cache/section279-draft/research/p2-skill-sp-increments-279'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
core_before = sha(CORE.read_bytes())
assert core_before == '7b72bb8c2428476bfdbf283f1f1b40c0969d7c11459594e3eca4bbb22b6a55ec'
checks = []


def check(name, condition):
    assert condition, name
    checks.append(name)


proof = json.loads((DATA / 'source-proof.json').read_bytes())
with Path(proof['source_game_dll']).open('rb') as handle, mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_READ) as native:
    metadata = Path(proof['source_metadata']).read_bytes()
    check('fresh complete DLL sha', sha(native) == proof['dll_sha256'])
    check('fresh complete metadata sha', sha(metadata) == proof['metadata_sha256'])
    for span in proof['byte_spans']:
        current = native if span['source'] == 'dll' else metadata
        raw = bytes.fromhex(span['raw_hex'])
        assert current[span['physical_offset']:span['physical_offset'] + len(raw)] == raw, span['label']
    check('all1670 proof spans equal fresh primary bytes', len(proof['byte_spans']) == 1670)
unique = {}
for method in proof['methods']:
    check('closed bounded CFG ' + method['method']['Name'], method['cfg_bounded_traversal_finished'] and not method['limits'])
    body = b''.join(bytes.fromhex(ins['bytes']) for ins in method['instructions'])
    assert sha(body) == method['reachable_bytes_sha256']
    for ins in method['instructions']:
        raw = bytes.fromhex(ins['bytes'])
        assert unique.setdefault(ins['address'], raw) == raw
check('938 independent instruction bytes count', len(unique) == 938)
by_index = {r['method'].get('metadata_method_index'): r for r in proof['methods'] if r['method'].get('metadata_method_index') is not None}
init = {i['address']: i for i in by_index[32852]['instructions']}
check('BB capture uses RBP from entry RDX', init['0x18252b311']['mnemonic'] == 'mov' and init['0x18252b311']['operands'] == 'rbp, rdx')
check('each loop tests captured RBP', init['0x18252b440']['mnemonic'] == 'test' and init['0x18252b440']['operands'] == 'rbp, rbp')
check('BB success stores mask before array reload', int('18252b498', 16) < int('18252b4ef', 16)
      and init['0x18252b498']['operands'] == 'dword ptr [rbx + 0x10], eax'
      and init['0x18252b4ef']['operands'] == 'rax, qword ptr [rbx + 0x78]')
single_ge = by_index[220359]['instructions']
check('Single GE opcode sequence inclusive ordered', [i['mnemonic'] for i in single_ge] == ['subss', 'comiss', 'setae', 'ret'])
helper = next(r for r in proof['methods'] if r['method']['Address'] == 0x1844dc660)
check('raw index helper literal two instructions', [(i['mnemonic'], i['operands']) for i in helper['instructions']] == [('mov', 'eax, ecx'), ('ret', '')])
single_fp = by_index[220498]['instructions']
check('Single FP uses MULSS then CVTTSS2SI', [i['mnemonic'] for i in single_fp] == ['mulss', 'cvttss2si', 'ret'])
check('OnTick has no direct Controller increments field', not any('+ 0x38]' in i['operands'] for i in by_index[66751]['instructions']))
meta = {r['index']: r for r in proof['method_metadata']}
check('BB Assign Single has void return', meta[30809]['return_type'] == 'System.Void' and meta[30809]['parameters'][1]['type'] == 'System.Single')
check('consumer methods return void', all(meta[index]['return_type'] == 'System.Void' for index in (66748, 66749, 66752)))

spec = importlib.util.spec_from_file_location('increment279authorchecks', CORE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
check('pinned public source gate valid', module.source_data()['valid'] is True)
example = module.public_example()
result = module.skill_sp_increment_reference(example)
check('public payload preserved without mutation', result['payload'] == example)
check('all4 action kinds with10 public rows', len(result['rows']) == 10 and {r['kind'] for r in result['rows']} == {'sp_data_init', 'skill_data_init', 'attack_gain', 'damage_gain'})
check('all actual array/SP/cycle outputs unknown', all(result[n] is None and all(r[n] is None for r in result['rows']) for n in module.UNKNOWNS))
check('absent BB yields4 default_one without mask write',
      [r['value_bits'] for r in result['rows'][0]['slot_references']] == [1065353216] * 4
      and not any(p['field'] == 'spType' for p in result['rows'][0]['stored_prefixes'])
      and all(r['mask_reference'] is None for r in result['rows'][0]['slot_references']))
check('unknown direct bits/mask write retains null prefix', result['rows'][1]['stored_prefixes'][4]['field'] == 'spType'
      and result['rows'][1]['stored_prefixes'][4]['value'] is None
      and result['rows'][1]['stored_prefixes'][5]['bits'] is None)
check('mask survives short array failure', result['rows'][2]['normal'] is False
      and result['rows'][2]['stored_prefixes'][-1] == {'field': 'spType', 'value': 1, 'known_set_bit': 1})
check('negative Single epsilon GE inclusive and second duration independent',
      result['rows'][3]['duration_ge_reference']['ge_boolean_reference'] is True
      and result['rows'][3]['assign_arguments']['duration_bits'] == 3212836864
      and result['rows'][3]['sp_init_arguments']['blackboard_identity'] == 'secondBB')
check('unknown GE retains already written flag and unknown future', result['rows'][4]['normal'] is None
      and result['rows'][4]['stored_prefixes'] == [{'field': 'm_inited', 'value': True}]
      and next(s for s in result['rows'][4]['stages'] if s['name'] == 'first_blackboard_read')['called'] is None)
check('positive and negative public request amounts', result['rows'][5]['recover_arguments']['amount_raw'] == 4294967296
      and result['rows'][6]['recover_arguments']['amount_raw'] == -4294967296)
check('cancelled damage skips amount and request', all(s['called'] is False for s in result['rows'][7]['stages'] if s['name'] in ('array_read', 'amount_read', 'recover_request')))
check('unknown conversion normal calls keep opaque request', result['rows'][8]['normal'] is True
      and result['rows'][8]['recover_arguments'] == {'amount_raw': None, 'force': False})
check('default_one does not enable consumer bit', all(s['called'] is False for s in result['rows'][9]['stages'][1:]))
check('zero Single comparison qualified', module.single_ge_zero_reference(0)['ge_boolean_reference'] is True)
check('Single EPS and MIN64 literal conversion', module.single_increment_reference(925353388)['raw_reference'] == 42949
      and module.single_increment_reference(3472883712)['raw_reference'] == -9223372036854775808)
check('mask OR preserves signed32 literal', module.mask_bit_reference(-2147483648, 0)['result_int32_reference'] == -2147483647)
check('frozen prototype bytes unchanged', sha(CORE.read_bytes()) == core_before)
receipt = {'kind': 'SECTION279_CACHE_PREPARATION_NECESSARY_CHECKS_NOT_SECTION_COMPLETION',
           'actual_exit_code': 0, 'check_count': len(checks), 'checks': checks, 'byte_span_count_rechecked': 1670,
           'source_game_dll_sha256': proof['dll_sha256'], 'source_metadata_sha256': proof['metadata_sha256'],
           'core_sha256_before': core_before, 'core_sha256_after': sha(CORE.read_bytes()),
           'proof_sha256': sha((DATA / 'source-proof.json').read_bytes()),
           'manifest_sha256': sha((DATA / 'source_manifest.json').read_bytes()),
           'script_sha256': sha(Path(__file__).read_bytes()),
           'production_or_tests_modified': False, 'native_dll_executed': False, 'process_memory_read': False,
           'current_hotfix_or_actual_array_sp_cycle_proven': False}
target = HERE / 'preparation-increment-check-279.json'
assert not target.exists(), 'preserve an earlier actual receipt'
target.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps({'path': str(target.relative_to(ROOT)), 'sha256': sha(target.read_bytes()),
                  'actual_exit_code': 0, 'check_count': len(checks), 'spans_rechecked': 1670}, ensure_ascii=False))
