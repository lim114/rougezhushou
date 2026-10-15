"""Necessary source/contract checks for cache prototype, not section completion."""
from copy import deepcopy
import hashlib
import importlib.util
import json
import mmap
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CORE = ROOT / '.cache/section280-draft/rouge/skill_cost_rounding_consensus.py'
DATA = ROOT / '.cache/section280-draft/research/p2-cost-rounding-consensus-280'
LEGACY = ROOT / 'rouge/skill_data_cost_reference.py'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
before = sha(CORE.read_bytes())
legacy_before = sha(LEGACY.read_bytes())
assert before == '86853e05e770e17d8cdbaabe14d4fb9f13e576efea378333b5470a39ec78aa77'
assert legacy_before == '7cd8eee14c217c46419b5ac70bbcfe14f63e67a5687b7974d8718ae60618077a'
checks = []


def check(name, condition):
    assert condition, name
    checks.append(name)


proof = json.loads((DATA / 'source-proof.json').read_bytes())
with Path(proof['source_game_dll']).open('rb') as handle, mmap.mmap(handle.fileno(), 0, access=mmap.ACCESS_READ) as native:
    metadata = Path(proof['source_metadata']).read_bytes()
    check('fresh whole DLL SHA', sha(native) == proof['dll_sha256'])
    check('fresh whole metadata SHA', sha(metadata) == proof['metadata_sha256'])
    for span in proof['byte_spans']:
        source = native if span['source'] == 'dll' else metadata
        raw = bytes.fromhex(span['raw_hex'])
        assert source[span['physical_offset']:span['physical_offset'] + len(raw)] == raw, span['label']
    check('all759 original byte spans fresh equal', len(proof['byte_spans']) == 759)
for method in proof['methods']:
    check('bounded source CFG ' + method['method']['Name'], method['cfg_bounded_traversal_finished'] and not method['limits'])
    body = b''.join(bytes.fromhex(i['bytes']) for i in method['instructions'])
    assert sha(body) == method['reachable_bytes_sha256']
instructions = {i['address']: i for m in proof['methods'] for i in m['instructions']}
check('546 independent instructions count', len(instructions) == 546)
for conv, op, mnemonic in (('0x180cf70c6', '0x180cf70c9', 'mulss'),
                           ('0x180cf6e95', '0x180cf6e98', 'addss'),
                           ('0x180d0f2a6', '0x180d0f2a9', 'mulss')):
    check('source ordered pair ' + conv, instructions[conv]['mnemonic'] == 'cvtdq2ps'
          and instructions[op]['mnemonic'] == mnemonic and int(conv, 16) < int(op, 16))
check('explicit floor ROUNDSD imm9', instructions['0x1804eefb0']['mnemonic'] == 'roundsd'
      and instructions['0x1804eefb0']['operands'].endswith(', 9'))
check('explicit ceil ROUNDSD imm10', instructions['0x1804eefd0']['mnemonic'] == 'roundsd'
      and instructions['0x1804eefd0']['operands'].endswith(', 0xa'))
cpu1, cpu2 = proof['official_cpu_sources']
check('official Volume1 file SHA', sha((HERE.parent / 'p2-skill-data-modifiers-278/intel-sdm-vol1-dec2024.pdf').read_bytes()) == cpu1['sha256'])
check('official Volume2abcd file SHA', sha((HERE / 'intel-sdm-volume2abcd-280.pdf').read_bytes()) == cpu2['file_sha256'])
check('four precise CPU bookmarks only', [b['title'].split('—')[0].strip() for b in cpu2['bookmarks']] == ['ADDSS', 'CVTDQ2PS', 'MULSS', 'ROUNDSD'])


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


module = load('consensus280authorchecks', CORE)
old = load('legacy278authorcomparison', LEGACY)
check('both public source gates valid', module.source_data()['valid'] and old.source_data()['valid'])
example = module.public_example()
original = deepcopy(example)
output = module.skill_cost_rounding_consensus(example)
check('payload and caller example unchanged', output['payload'] == original and example == original)
check('all3 kind with10 public rows', len(output['rows']) == 10 and {r['kind'] for r in output['rows']} == {'rune_add', 'rune_mul', 'relic_mul'})
check('actual cost/SP/cycle all unknown', all(output[k] is None and all(r[k] is None for r in output['rows']) for k in module.UNKNOWNS))
check('public complete16 candidate pairs', all(len(r['consensus_reference']['cases']) == 16 for r in output['rows'][:9]))
two = output['rows'][0]['consensus_reference']
check('inexact0.2 all16 agree2 while legacy is unknown', two['integer_consensus_reference'] == 2
      and two['expanded_beyond_exact_only'] is True and old.single_cost_reference('mul', 10, 0x3e4ccccd)['rounded_int32_reference'] is None)
check('0.2 operation neighbors exact literal', two['possible_operation_bits'] == [1073741824, 1073741825])
check('all4 conversion modes retained', [c['rc'] for c in two['cost_conversion_candidates']] == [0, 1, 2, 3])
check('all16 pairs retained without probability or defaultRC', [(c['conversion_rc'], c['operation_rc']) for c in two['cases']] == [(a, b) for a in range(4) for b in range(4)])
check('0.05 boundary0/1 not collapsed', output['rows'][1]['consensus_reference']['integer_candidates'] == [0, 1]
      and output['rows'][1]['encoder_argument_reference'] is None)
check('1.05 cost20 closes21 oldexact remainsunknown', output['rows'][2]['encoder_argument_reference'] == 21
      and old.single_cost_reference('mul', 20, 0x3f866666)['rounded_int32_reference'] is None)
check('1.05 cost30 still31/32', output['rows'][3]['consensus_reference']['integer_candidates'] == [31, 32]
      and output['rows'][3]['encoder_argument_reference'] is None)
check('Int32 inexact conversion literal16777216/18', [c['cost_single_bits'] for c in output['rows'][4]['consensus_reference']['cost_conversion_candidates']]
      == [1266679808, 1266679808, 1266679809, 1266679808])
check('inexact conversion timeszero closeszero', output['rows'][4]['encoder_argument_reference'] == 0
      and output['rows'][4]['consensus_reference']['possible_operation_bits'] == [0, 2147483648])
check('inexact conversion timesone doesnotpretendoriginalcost', output['rows'][5]['consensus_reference']['integer_candidates'] == [16777216, 16777218]
      and output['rows'][5]['encoder_argument_reference'] is None)
check('negative inexact cost not clampedzero', output['rows'][6]['encoder_argument_reference'] == -2)
check('ADDSS inexact common integer', output['rows'][7]['encoder_argument_reference'] == 10)
check('independent next decoded101 useshalf-even50', output['rows'][8]['consensus_reference']['cost_int32'] == 101
      and output['rows'][8]['encoder_argument_reference'] == 50)
check('nonfinite coefficient keepsunknown', output['rows'][9]['encoder_argument_reference'] is None
      and output['rows'][9]['consensus_reference']['cases'] == [])
check('MIN32×negativeone Int32 domain unknown', module.single_cost_consensus_reference('mul', -2147483648, 0xbf800000)['integer_consensus_reference'] is None)
check('MAX32×zero closeszero across conversion differences', module.single_cost_consensus_reference('mul', 2147483647, 0)['integer_consensus_reference'] == 0)
check('subnormal coefficient remainsenvironmentunknown', module.single_cost_consensus_reference('mul', 20, 1)['integer_consensus_reference'] is None)
unknown = deepcopy(example)
unknown['actions'] = unknown['actions'][:1]
unknown['actions'][0]['round_normally'] = None
row = module.skill_cost_rounding_consensus(unknown)['rows'][0]
check('round unknown doesnotqualifyinteger output', row['normal'] is None and row['consensus_reference'] is None and row['encoder_argument_reference'] is None)
check('preceding arithmetic stage has no future integer reference', all('rounded_int32_reference' not in c
      for c in row['stages'][3]['reference']['cases']))
check('newcore frozen bytes unchanged', sha(CORE.read_bytes()) == before)
check('legacy core frozen bytes unchanged', sha(LEGACY.read_bytes()) == legacy_before)
receipt = {'kind': 'SECTION280_CACHE_PREPARATION_NECESSARY_CHECKS_NOT_SECTION_COMPLETION',
           'actual_exit_code': 0, 'check_count': len(checks), 'checks': checks, 'byte_span_count_rechecked': 759,
           'dll_sha256': proof['dll_sha256'], 'metadata_sha256': proof['metadata_sha256'],
           'core_sha256_before': before, 'core_sha256_after': sha(CORE.read_bytes()),
           'legacy_exact_core_sha256_before': legacy_before, 'legacy_exact_core_sha256_after': sha(LEGACY.read_bytes()),
           'proof_sha256': sha((DATA / 'source-proof.json').read_bytes()),
           'manifest_sha256': sha((DATA / 'source_manifest.json').read_bytes()), 'script_sha256': sha(Path(__file__).read_bytes()),
           'production_or_tests_modified': False, 'native_dll_executed': False, 'process_memory_read': False,
           'actual_rc_masks_handlers_or_actual_cost_sp_cycle_proven': False}
target = HERE / 'preparation-consensus-check-280.json'
assert not target.exists(), 'preserve actual earlier receipt'
target.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps({'path': str(target.relative_to(ROOT)), 'sha256': sha(target.read_bytes()),
                  'actual_exit_code': 0, 'check_count': len(checks), 'spans_rechecked': 759}, ensure_ascii=False))
