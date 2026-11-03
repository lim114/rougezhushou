"""Necessary author check for cache prototype; not a completed section receipt."""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DRAFT = ROOT / '.cache/section278-draft'
CORE = DRAFT / 'rouge/skill_data_cost_reference.py'
DATA = DRAFT / 'research/p2-skill-data-cost-278'
checks = []


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check(name, condition):
    assert condition, name
    checks.append(name)


module = load(CORE, 'cost278_draft_author_check')
check('strict SHA source packet accepted', module.source_data()['valid'] is True)
for name, operation, cost, bits, expected in [
    ('25half even12', 'mul', 25, 0x3f000000, 12),
    ('23half even12', 'mul', 23, 0x3f000000, 12),
    ('negative23half retainsnegative12', 'mul', -23, 0x3f000000, -12),
    ('add half to101 rounds102', 'add', 101, 0x3f000000, 102),
    ('exact large even Int32 allowed', 'mul', 16777218, 0x3f800000, 16777218),
    ('zero result Int32 zero regardless zero-sign', 'mul', 0, 0xbf800000, 0),
]:
    check(name, module.single_cost_reference(operation, cost, bits)['rounded_int32_reference'] == expected)
check('Single inexact RC not assumed', module.single_cost_reference('mul', 10, 0x3d4ccccd)['rounded_int32_reference'] is None)
check('Int32 inexact conversion not assumed', module.single_cost_reference('mul', 16777217, 0x3f800000)['rounded_int32_reference'] is None)
check('Single subnormal input remainsunknown', module.single_cost_reference('mul', 1, 1)['rounded_int32_reference'] is None)
check('nonfinite operand remainsunknown', module.single_cost_reference('mul', 1, 0x7f800000)['rounded_int32_reference'] is None)
check('positive2power31 Int32 conversion domain not assumed', module.single_cost_reference('mul', -2147483648, 0xbf800000)['rounded_int32_reference'] is None)
check('MIN32 timesnegative1 low32 staysMIN32', module.signed_scale_reference(-2147483648, -1)['product_int32_reference'] == -2147483648)
check('MAX32 times2 low32 negative2', module.signed_scale_reference(2147483647, 2)['product_int32_reference'] == -2)
example = module.public_example()
out = module.skill_data_cost_reference(example)
rows = {row['id']: row for row in out['rows']}
check('public10 rows andall5kind', len(out['rows']) == 10 and set(row['kind'] for row in out['rows']) == set(module.STAGES))
check('independent nextdecode101 not inherited from previous12', rows['public.independent_next_decode']['encoder_argument_reference'] == 102)
check('onlycost updateTrue', rows['public.onlycost']['update_arguments']['only_update_sp_cost'] is True)
check('modifytype updateFalse', rows['public.type_update']['update_arguments']['only_update_sp_cost'] is False)
failure = rows['public.null_sp_after_encode']
check('encoding precedes firstsp nullguard', failure['stages'][2]['normal'] is True
      and failure['stages'][3]['normal'] is True and failure['stages'][3]['reference']['exists'] is False
      and failure['stages'][4]['called'] is False and failure['normal'] is False)
check('inexact domain futurecalledNone', all(stage['called'] is None for stage in rows['public.RC_unknown']['stages'][10:]))
for row in out['rows']:
    check(row['id'] + ' actualcost/SP/cycle alwaysunknown', all(row[key] is None for key in module.UNKNOWNS))
probe = deepcopy(example)
probe['actions'] = [deepcopy(example['actions'][6])]
probe['actions'][0]['owner_read']['exists'] = False
null_owner = module.skill_data_cost_reference(probe)['rows'][0]
check('scale nullowner stillreadsdata2', null_owner['stages'][9]['normal'] is True and null_owner['stages'][10]['called'] is False)
probe['actions'] = [deepcopy(example['actions'][8])]
probe['actions'][0]['second_owner_read']['exists'] = False
null_second_owner = module.skill_data_cost_reference(probe)['rows'][0]
check('replacement nullowner2 stillreadsdata3', null_second_owner['stages'][13]['normal'] is True and null_second_owner['stages'][14]['called'] is False)
probe['actions'][0]['second_owner_read']['exists'] = True
probe['actions'][0]['type_value_read']['value'] = None
unknown_type = module.skill_data_cost_reference(probe)['rows'][0]
check('normal directunknownInt32 typewrite proceedswithouttypeassumption', unknown_type['stored_prefixes'][-1] == {'field': 'spType', 'value': None}
      and unknown_type['update_arguments']['only_update_sp_cost'] is False and unknown_type['normal'] is True)
try:
    module.skill_data_cost_reference(example, data={'valid': True})
    raise AssertionError('public source override accepted')
except TypeError:
    checks.append('public API rejects data/source override')

# Real modified owned public packet, never production/user state.
INVALID = HERE / 'invalid-cost-source-packet'
(INVALID / 'rouge').mkdir(parents=True, exist_ok=True)
(INVALID / 'research/p2-skill-data-cost-278').mkdir(parents=True, exist_ok=True)
shutil.copyfile(CORE, INVALID / 'rouge/skill_data_cost_reference.py')
for name in ('source_manifest.json', 'source-proof.json'):
    shutil.copyfile(DATA / name, INVALID / 'research/p2-skill-data-cost-278' / name)
packet_proof = INVALID / 'research/p2-skill-data-cost-278/source-proof.json'
packet_proof.write_bytes(packet_proof.read_bytes() + b' ')
invalid = load(INVALID / 'rouge/skill_data_cost_reference.py', 'cost278_invalid_source_author_check')
check('actual changed proof bytes rejected', invalid.source_data()['status'] == 'proof_sha_mismatch')
invalid_out = invalid.skill_data_cost_reference(example)
check('invalidsource no numeric/encoder/store/update references', all(
    row['arithmetic_reference'] is None and row['encoder_argument_reference'] is None
    and row['stored_prefixes'] == [] and row['update_arguments'] is None for row in invalid_out['rows']))
check('invalidsource both scalarhelpersNone', invalid.single_cost_reference('mul', 25, 0x3f000000) is None
      and invalid.signed_scale_reference(20, 2) is None)

proof = json.loads((DATA / 'source-proof.json').read_bytes())
dll = Path(proof['source_game_dll']).read_bytes()
metadata = Path(proof['source_metadata']).read_bytes()
check('fresh original DLL SHA', hashlib.sha256(dll).hexdigest() == proof['dll_sha256'])
check('fresh original metadata SHA', hashlib.sha256(metadata).hexdigest() == proof['metadata_sha256'])
for span in proof['byte_spans']:
    raw = bytes.fromhex(span['raw_hex'])
    source = dll if span['source'] == 'dll' else metadata
    position = span['physical_offset']
    assert source[position:position + len(raw)] == raw, span['label']
check('all4034 original physical spans fresh', len(proof['byte_spans']) == 4034)
check('32 retained selected source records', len(proof['methods']) == 32)
cpu = json.loads((HERE / 'intel-arithmetic-source.json').read_bytes())
check('official CPU PDF original SHA', hashlib.sha256((HERE / 'intel-sdm-vol1-dec2024.pdf').read_bytes()).hexdigest() == cpu['sha256'])
receipt = {'kind': 'SECTION278_COST_CACHE_PREPARATION_CHECK_NOT_ACTUAL_COMPLETION',
           'checks_passed': len(checks), 'checks': checks,
           'core_sha256': hashlib.sha256(CORE.read_bytes()).hexdigest(),
           'proof_sha256': hashlib.sha256((DATA / 'source-proof.json').read_bytes()).hexdigest(),
           'primary_files_fresh': True, 'spans_rechecked': len(proof['byte_spans']),
           'dll_executed': False, 'process_memory_read': False, 'production_or_tests_modified': False,
           'actual_cost_or_sp_or_cycle_proven': False, 'four_slot_initialization_implemented': False}
(HERE / 'preparation-cost-check-278.json').write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps({key: value for key, value in receipt.items() if key != 'checks'}, ensure_ascii=False))
