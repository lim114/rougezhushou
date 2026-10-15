"""Independent bounded composition review; no game/native execution or broad QA."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
import sys
import traceback

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DRAFT = ROOT / '.cache/section281-preparation'
CORE = DRAFT / 'rouge/skill_data_cost_consensus_reference.py'
EXPECTED = 'e5942aad8ab13581d3bf519e9f93bc06a701af6a364552afcd6bc1d5c6b8b52b'
OUT = HERE / 'limited-implementation-review-281.json'
assert not OUT.exists(), 'Preserve the first actual review.'

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

core = load(CORE, '_281_independent_fixed')
legacy = load(DRAFT / 'rouge/skill_data_cost_reference.py', '_281_independent_old')
checks, probes = [], []
def check(name, value):
    checks.append({'name': name, 'passed': bool(value)})
def stage(row, name):
    return next(s for s in row['stages'] if s['name'] == name)
def action(label):
    a = deepcopy(core.public_example()['actions'][0])
    a['id'] = label
    for name, value in a.items():
        if isinstance(value, dict) and 'id' in value:
            value['id'] = label + '.' + name
    return a
def probe(name, a, receiver=True):
    p = {'receiver_exists': receiver, 'actions': [a]}
    before = deepcopy(p)
    actual = core.skill_data_cost_consensus_reference(p)
    probes.append({'name': name, 'input': before, 'actual': actual})
    check(name + '.input_preserved', p == before)
    check(name + '.actual_unknown', all(actual[k] is None and actual['rows'][0][k] is None for k in core.UNKNOWNS))
    return actual['rows'][0]

report = {'kind': 'SECTION281_LIMITED_INDEPENDENT_COMPOSITION_REVIEW',
          'scope': 'Complete Single prelude to consensus/opaque encode/store; unchanged scale/replace owner/update; source clone guards',
          'native_fresh_methods_this_review': 0, 'native_fresh_spans_this_review': 0,
          'source_reused_from_prior_sections': True, 'game_dll_executed': False,
          'process_memory_read': False, 'game_chat_or_private_operations': False,
          'reviewer_findings': []}
try:
    check('frozen_core_before', hashlib.sha256(CORE.read_bytes()).hexdigest() == EXPECTED)
    check('original_core_sealed', (HERE / 'core-before-e5942aad.py').read_bytes() == CORE.read_bytes())
    source = core.source_data()
    report['source'] = source
    check('bound_32_not_sum41', source['valid'] is True and source['method_count'] == 32 and source['byte_span_count'] == 4034)

    links_path = DRAFT / 'research/p2-skill-data-cost-consensus-281/source-links.json'
    links = json.loads(links_path.read_bytes())
    proof = json.loads((DRAFT / 'research/p2-skill-data-cost-278/source-proof.json').read_bytes())
    mappings = []
    for kind, mapping in links['source_method_mapping'].items():
        m = next(m for m in proof['methods'] if m['method']['metadata_method_index'] == mapping['metadata_method_index'])
        check('source_method_sha.' + kind, m['reachable_bytes_sha256'] == mapping['reachable_bytes_sha256'])
        if kind not in core.SINGLE_KINDS:
            check('unchanged_non_single_source.' + kind, mapping['new_numeric_evaluator_used'] is False)
            continue
        rows = {i['address']: i for i in m['instructions']}
        matched = {}
        for name, address in mapping['stage_instruction_addresses'].items():
            ins = rows[address]
            check('mapped_bytes.' + kind + '.' + name, ins['bytes'] == mapping['stage_instruction_bytes'][name])
            matched[name] = {'address': address, 'bytes': ins['bytes'], 'mnemonic': ins['mnemonic'], 'operands': ins['operands']}
        # Source anchors identify a stage region, not all reads/copies in a single instruction.
        ordered = sorted(m['instructions'], key=lambda i: int(i['address'], 16))
        pos = next(i for i, ins in enumerate(ordered) if ins['address'] == mapping['stage_instruction_addresses']['store'])
        following = ordered[pos:pos + 12]
        check('native_16plus4_and_return.' + kind, any(i['mnemonic'] == 'mov' and i['operands'].startswith('dword ptr [rdi + 0x44]') for i in following) and any(i['mnemonic'] == 'ret' for i in following))
        mappings.append({'kind': kind, 'anchors': matched, 'only_anchor_bytes_not_new_fresh_audit': True})
    check('source_declares_new_fresh_zero', links['fresh_native_method_count_this_preparation'] == 0 and links['fresh_native_span_count_this_preparation'] == 0)
    report['source_mapping_review'] = mappings
    report['mapping_precision_note'] = 'Rune owner_read anchors a qualified incoming-owner null test; relic round anchors the inline Double conversion. The complete regions, not one anchor instruction, establish each multi-instruction stage.'

    p = core.public_example()
    original_input = deepcopy(p)
    actual = core.skill_data_cost_consensus_reference(p)
    old = legacy.skill_data_cost_reference(p)
    probes.append({'name': 'all_public_kinds_legacy_comparison', 'input': p, 'actual': actual, 'legacy_actual': old})
    check('public_input_unchanged', p == original_input)
    for a, r, before in zip(p['actions'], actual['rows'], old['rows']):
        if a['kind'] not in core.SINGLE_KINDS:
            check('old_fields_identical.' + a['id'], {k: v for k, v in r.items() if k not in ('calculation_route', 'consensus_reference')} == before)
        else:
            check('single_no_extra_owner_update.' + a['id'], [s['name'] for s in r['stages']] == list(core.SINGLE_STAGES) and r['update_arguments'] is None)
    r = actual['rows'][0]
    check('known_integer_encodes_and_stores', r['encoder_argument_reference'] == 2 and stage(r, 'encode')['reference']['argument_known'] is True and r['stored_prefixes'][0]['decoded_value'] is None and r['stored_prefixes'][0]['byte_count'] == 20)
    r = actual['rows'][1]
    check('disagree_opaque_normal_store', r['normal'] is True and r['encoder_argument_reference'] is None and stage(r, 'encode')['reference']['argument_candidates'] == [0, 1] and len(r['stored_prefixes']) == 1)
    r = actual['rows'][4]
    check('unknown_operands_opaque_normal_store', r['normal'] is True and r['encoder_argument_reference'] is None and stage(r, 'encode')['reference']['argument_known'] is False and len(r['stored_prefixes']) == 1)
    check('next_decode_independent101', actual['rows'][5]['encoder_argument_reference'] == 50 and stage(actual['rows'][5], 'cost_decode')['reference']['value'] == 101)

    a = action('missing_skill'); a['skill_data_read']['exists'] = False
    r = probe('normal_early_skill_return', a)
    check('missing_skill_no_decode_or_tail', r['normal'] is True and all(s['called'] is False for s in r['stages'][3:]) and not r['stored_prefixes'])
    a = action('absent_rune'); a['modifier_read']['found'] = False
    r = probe('normal_early_key_absent', a)
    check('absent_key_no_tail', r['normal'] is True and all(s['called'] is False for s in r['stages'][5:]) and r['consensus_reference'] is None)
    a = action('unknown_rune'); a['modifier_read']['found'] = None
    r = probe('presence_unknown_no_skip_claim', a)
    check('unknown_presence_future_unknown', r['normal'] is None and all(s['called'] is None for s in r['stages'][5:]))
    a = action('owner_failed'); a['owner_read']['normal'] = False
    r = probe('proved_prelude_failure', a)
    check('failed_prelude_not_rebuilt', r['normal'] is False and all(s['called'] is False for s in r['stages'][1:]) and not r['stored_prefixes'])
    a = action('decode_unknown'); a['cost_decode']['normal'] = None
    r = probe('decode_normal_unknown_no_rebuild', a)
    check('decode_unknown_future_unknown', stage(r, 'cost_decode')['called'] is True and all(s['called'] is None for s in r['stages'][8:]) and r['consensus_reference'] is None)

    for field, stage_name in [('single_conversion_normally', 'single_conversion'), ('round_normally', 'round'), ('encode_normally', 'encode'), ('store_normally', 'store')]:
        for flag in (False, None):
            a = action(field + ('_failed' if flag is False else '_unknown')); a[field] = flag
            r = probe(field + '.' + str(flag), a)
            pos = core.SINGLE_STAGES.index(stage_name)
            check(field + '.' + str(flag) + '.own_call', stage(r, stage_name)['called'] is True and stage(r, stage_name)['normal'] is flag and r['normal'] is flag)
            check(field + '.' + str(flag) + '.future', all(s['called'] is (False if flag is False else None) for s in r['stages'][pos + 1:]) and not r['stored_prefixes'])
    a = action('partial_domain'); a['cost_decode']['value'] = 2147483647; a['modifier_read']['bits'] = 0x3f800000
    r = probe('one_safe_subset_opaque_store', a)
    check('unsafe_other_candidates_not_parameter', r['normal'] is True and r['encoder_argument_reference'] is None and stage(r, 'encode')['reference']['argument_candidates'] == [2147483520] and len(r['stored_prefixes']) == 1)
    a = action('fresh_after'); r = probe('returned_copy', a)
    r['stages'][0]['reference']['identity'] = 'changed-copy'
    check('returned_read_copy', a['owner_read']['identity'] != 'changed-copy')

    rejected = {}
    for extra in ('source_data', 'evaluator', 'RC', 'mode'):
        forged = {'receiver_exists': True, 'actions': [action('reject_' + extra)], extra: True}
        try:
            core.skill_data_cost_consensus_reference(forged)
            rejected[extra] = False
        except ValueError:
            rejected[extra] = True
        check('public_injection_reject.' + extra, rejected[extra])
    report['public_injection_rejections'] = rejected

    # Own isolated public clones only; corrupt bytes fail before executing a dependency.
    clone_cases = [
        ('legacy_core', 'rouge/skill_data_cost_reference.py', b'\nraise RuntimeError("unexpected cloned dependency execution")\n'),
        ('consensus_core', 'rouge/skill_cost_rounding_consensus.py', b'\nraise RuntimeError("unexpected cloned dependency execution")\n'),
        ('legacy_packet', 'research/p2-skill-data-cost-278/SCHEMA.md', b'\nindependent guard corruption\n'),
        ('wrapper_links', 'research/p2-skill-data-cost-consensus-281/source-links.json', b'\n '),
    ]
    for label, relative, suffix in clone_cases:
        dest = HERE / ('clone-' + label)
        assert not dest.exists()
        (dest / 'rouge').mkdir(parents=True)
        for name in ('skill_data_cost_consensus_reference.py', 'skill_data_cost_reference.py', 'skill_cost_rounding_consensus.py'):
            shutil.copyfile(DRAFT / 'rouge' / name, dest / 'rouge' / name)
        for directory in ('p2-skill-data-cost-consensus-281', 'p2-skill-data-cost-278', 'p2-cost-rounding-consensus-280'):
            shutil.copytree(DRAFT / 'research' / directory, dest / 'research' / directory)
        cloned = load(dest / 'rouge/skill_data_cost_consensus_reference.py', '_281_clone_' + label)
        check('clone_valid_before.' + label, cloned.source_data()['valid'] is True)
        target = dest / relative
        target.write_bytes(target.read_bytes() + suffix)
        payload = {'receiver_exists': True, 'actions': [action('clone_' + label)]}
        result = cloned.skill_data_cost_consensus_reference(payload)
        probes.append({'name': 'source_clone_guard.' + label, 'input': payload, 'altered_public_path': relative, 'actual': result})
        r = result['rows'][0]
        check('clone_invalid_after.' + label, result['source']['valid'] is False and r['arithmetic_reference'] is None and r['consensus_reference'] is None and r['stored_prefixes'] == [] and all(s['called'] is None for s in r['stages']))

    check('frozen_core_after', hashlib.sha256(CORE.read_bytes()).hexdigest() == EXPECTED)
    check('legacy278_unchanged', hashlib.sha256((ROOT / 'rouge/skill_data_cost_reference.py').read_bytes()).hexdigest() == '7cd8eee14c217c46419b5ac70bbcfe14f63e67a5687b7974d8718ae60618077a')
    check('consensus280_unchanged', hashlib.sha256((ROOT / 'rouge/skill_cost_rounding_consensus.py').read_bytes()).hexdigest() == '86853e05e770e17d8cdbaabe14d4fb9f13e576efea378333b5470a39ec78aa77')
except Exception:
    report['review_tool_exception'] = traceback.format_exc()

report.update({'core_sha256': hashlib.sha256(CORE.read_bytes()).hexdigest(),
               'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'probe_count': len(probes), 'check_count': len(checks), 'checks': checks, 'probes': probes,
               'passed': bool(checks) and all(c['passed'] for c in checks) and 'review_tool_exception' not in report,
               'remaining_unknowns': ['actual cost/SP/complete cycle', 'protected roundtrip', 'real RC/masks/hotfix/current invocation qualification'],
               'scope_not_full_QA_or_new_native_fresh_source_audit': True})
OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps({'passed': report['passed'], 'probes': len(probes), 'checks': len(checks),
                  'receipt_sha256': hashlib.sha256(OUT.read_bytes()).hexdigest(),
                  'failed_checks': [c['name'] for c in checks if not c['passed']],
                  'tool_exception': report.get('review_tool_exception')}, ensure_ascii=False))
raise SystemExit(0 if report['passed'] else 1)
