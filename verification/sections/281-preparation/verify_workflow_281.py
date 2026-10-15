"""Necessary workflow composition checks; public input only, no native source rerun."""
from copy import deepcopy
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CORE = HERE / 'rouge/skill_data_cost_consensus_reference.py'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
expected = 'e5942aad8ab13581d3bf519e9f93bc06a701af6a364552afcd6bc1d5c6b8b52b'
assert sha(CORE.read_bytes()) == expected
checks = []


def check(name, condition):
    assert condition, name
    checks.append(name)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


module = load('workflow281authorchecks', CORE)
legacy = load('original278authorchecks281', ROOT / 'rouge/skill_data_cost_reference.py')
original_legacy = sha((ROOT / 'rouge/skill_data_cost_reference.py').read_bytes())
original_consensus = sha((ROOT / 'rouge/skill_cost_rounding_consensus.py').read_bytes())
links = json.loads((HERE / 'research/p2-skill-data-cost-consensus-281/source-links.json').read_bytes())
check('new binding valid and no new native fresh count', module.source_data()['valid'] is True
      and links['fresh_native_method_count_this_preparation'] == 0 and links['fresh_native_span_count_this_preparation'] == 0)
check('9 existing methods subset, not counted41', module.source_data()['method_count'] == 32 and links['consensus9_methods_are_subset_of_legacy32'] is True)
old_payload = legacy.public_example()
baseline = json.dumps(legacy.skill_data_cost_reference(deepcopy(old_payload)), ensure_ascii=False, sort_keys=True)
payload = module.public_example()
saved = deepcopy(payload)
result = module.skill_data_cost_consensus_reference(payload)
check('caller payload unchanged', payload == saved and result['payload'] == saved)
check('all5 kind with11 source-supported public rows', len(result['rows']) == 11
      and {row['kind'] for row in result['rows']} == {'rune_add', 'rune_mul', 'relic_mul', 'scale_cost', 'replace_cost'})
check('actual outputs all unknown', all(result[k] is None and all(row[k] is None for row in result['rows']) for k in module.UNKNOWNS))
check('inexact consensus2 reachesopaque20bytecoststore', result['rows'][0]['normal'] is True
      and result['rows'][0]['encoder_argument_reference'] == 2
      and result['rows'][0]['stored_prefixes'] == [{'field': 'spCost', 'byte_count': 20,
            'payload_identity': 'public.consensus_two_to_store.opaque20', 'decoded_value': None}])
check('integer0or1 unknown stillindependentnormal encode/store', result['rows'][1]['normal'] is True
      and result['rows'][1]['consensus_reference']['integer_candidates'] == [0, 1]
      and result['rows'][1]['encoder_argument_reference'] is None and len(result['rows'][1]['stored_prefixes']) == 1)
check('opaque encoding doesnotfabricateargumentzero', result['rows'][1]['stages'][11]['reference'] ==
      {'argument': None, 'argument_known': False, 'argument_candidates': [0, 1], 'returned_payload': None})
check('relic1.05 conditional21 reachesstore', result['rows'][2]['encoder_argument_reference'] == 21 and len(result['rows'][2]['stored_prefixes']) == 1)
check('runeadd inexact10 reachesstore', result['rows'][3]['encoder_argument_reference'] == 10 and len(result['rows'][3]['stored_prefixes']) == 1)
check('both numerical operands unknown opaque normal store', result['rows'][4]['normal'] is True
      and result['rows'][4]['encoder_argument_reference'] is None and len(result['rows'][4]['stored_prefixes']) == 1)
check('next decoded101 notpreviousparameter reused', result['rows'][5]['consensus_reference']['cost_int32'] == 101
      and result['rows'][5]['encoder_argument_reference'] == 50)
check('roundnormal unknown noencode/store claim', result['rows'][6]['normal'] is None
      and result['rows'][6]['stored_prefixes'] == [] and result['rows'][6]['stages'][11]['called'] is None
      and result['rows'][6]['stages'][12]['called'] is None)
check('Single noownerUpdate appended', all(row['update_arguments'] is None and len(row['stages']) == 13 for row in result['rows'][:7]))
old_for_same = legacy.skill_data_cost_reference(deepcopy(payload))
for index in range(7, 11):
    actual = {key: value for key, value in result['rows'][index].items() if key not in ('calculation_route', 'consensus_reference')}
    check('nonSingle original rowfields identical ' + result['rows'][index]['id'], actual == old_for_same['rows'][index])
check('type Update originalonlycostfalse retained', result['rows'][9]['update_arguments']['only_update_sp_cost'] is False)
check('replacement nullSpData retainsencode beforefailure', result['rows'][10]['normal'] is False
      and result['rows'][10]['stages'][2]['called'] is True and result['rows'][10]['stages'][2]['normal'] is True
      and result['rows'][10]['stages'][4]['called'] is False)


def one():
    p = deepcopy(payload)
    p['actions'] = p['actions'][:1]
    return p


absent = one()
absent['actions'][0]['modifier_read']['found'] = False
r = module.skill_data_cost_consensus_reference(absent)['rows'][0]
check('Rune key missing normalearlyreturn noCostDecode', r['normal'] is True and r['stored_prefixes'] == [] and r['stages'][7]['called'] is False)
main_missing = one()
main_missing['actions'][0]['skill_data_read']['exists'] = False
r = module.skill_data_cost_consensus_reference(main_missing)['rows'][0]
check('mainSkill absent normalreturn no numeric tail', r['normal'] is True and r['stages'][8]['called'] is False)
failed = one()
failed['actions'][0]['cost_copy_normally'] = False
r = module.skill_data_cost_consensus_reference(failed)['rows'][0]
check('copyfailure neverreachesnewtail', r['normal'] is False and r['stages'][7]['called'] is False and r['consensus_reference'] is None)
unknown = one()
unknown['actions'][0]['sp_data_read']['exists'] = None
r = module.skill_data_cost_consensus_reference(unknown)['rows'][0]
check('pointerunknown future remainsNone', r['normal'] is None and r['stages'][7]['called'] is None and r['stored_prefixes'] == [])
encode_failed = one()
encode_failed['actions'][0]['encode_normally'] = False
r = module.skill_data_cost_consensus_reference(encode_failed)['rows'][0]
check('encoderfail retainsknownargument butnostore', r['normal'] is False and r['encoder_argument_reference'] == 2
      and r['stages'][12]['called'] is False and not r['stored_prefixes'])
store_failed = one()
store_failed['actions'][0]['store_normally'] = False
r = module.skill_data_cost_consensus_reference(store_failed)['rows'][0]
check('storefailed noopaque writeprefix', r['normal'] is False and not r['stored_prefixes'])
try:
    module.skill_data_cost_consensus_reference(one(), data={})
except TypeError:
    check('publicdata override rejected', True)
else:
    raise AssertionError('publicdata override accepted')
bad = one()
bad['actions'][0]['evaluator'] = 'arbitrary'
try:
    module.skill_data_cost_consensus_reference(bad)
except ValueError:
    check('publicevaluator key rejected', True)
else:
    raise AssertionError('evaluator accepted')
check('legacy defaultpublic resultbyteidentical aftercomposition', baseline == json.dumps(legacy.skill_data_cost_reference(deepcopy(old_payload)), ensure_ascii=False, sort_keys=True))
check('oldcore production bytes unchanged', sha((ROOT / 'rouge/skill_data_cost_reference.py').read_bytes()) == original_legacy)
check('280 production bytes unchanged', sha((ROOT / 'rouge/skill_cost_rounding_consensus.py').read_bytes()) == original_consensus)
check('281draft frozen bytes unchanged', sha(CORE.read_bytes()) == expected)
receipt = {'kind': 'SECTION281_CACHE_NECESSARY_WORKFLOW_CHECKS_NOT_COMPLETION', 'actual_exit_code': 0,
           'check_count': len(checks), 'checks': checks, 'core_sha256': expected,
           'legacy_default_core_sha256_unchanged': original_legacy, 'consensus280_core_sha256_unchanged': original_consensus,
           'source_links_sha256': module.source_data()['proof_sha256'], 'native_source_reused_not_new_fresh': True,
           'native_fresh_methods_this_check': 0, 'native_fresh_spans_this_check': 0,
           'production_or_private_state_modified': False, 'game_or_chat_operated': False,
           'script_sha256': sha(Path(__file__).read_bytes())}
target = HERE / 'necessary-workflow-checks-281.json'
assert not target.exists(), 'preserve earlier actual receipt'
target.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps({'receipt_sha256': sha(target.read_bytes()), 'actual_exit_code': 0, 'checks': len(checks)}, ensure_ascii=False))
