"""Limited independent review, not full QA or a native execution receipt."""
from __future__ import annotations
from copy import deepcopy
from pathlib import Path
import hashlib
import json
import sys
import traceback

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CORE = ROOT / '.cache/section280-draft/rouge/skill_cost_rounding_consensus.py'
EXPECTED = '86853e05e770e17d8cdbaabe14d4fb9f13e576efea378333b5470a39ec78aa77'
OUT = HERE / 'limited-implementation-review-280.json'
assert not OUT.exists(), 'Do not overwrite a first actual review.'
sys.path.insert(0, str(ROOT))
import rouge
rouge.__path__.insert(0, str(CORE.parent))
from rouge import skill_cost_rounding_consensus as core
from pypdf import PdfReader

checks = []
probes = []
def check(name, condition):
    checks.append({'name': name, 'passed': bool(condition)})
def scalar(name, operation, cost, bits, integer, candidates, status=None):
    actual = core.single_cost_consensus_reference(operation, cost, bits)
    probes.append({'name': name, 'input': {'operation': operation, 'cost': cost, 'modifier_bits': bits}, 'actual': actual})
    check(name + '.integer', actual['integer_consensus_reference'] == integer)
    check(name + '.candidates', actual['integer_candidates'] == candidates)
    if status is not None:
        check(name + '.status', actual['status'] == status)
    if actual['cases']:
        check(name + '.all16_once', [(c['conversion_rc'], c['operation_rc']) for c in actual['cases']] == [(a, b) for a in range(4) for b in range(4)])
    return actual
def action(name, **changes):
    a = {'id': name, 'kind': 'rune_mul', 'ordinary_native_path': True,
         'modifier_read': {'id': name + '.modifier', 'normal': True, 'bits': 0x3e4ccccd},
         'cost_decode': {'id': name + '.cost', 'normal': True, 'value': 10},
         'conversion_normally': True, 'operation_normally': True, 'round_normally': True}
    a.update(changes)
    return a
def rowprobe(name, a, receiver=True):
    p = {'receiver_exists': receiver, 'actions': [a]}
    before = deepcopy(p)
    result = core.skill_cost_rounding_consensus(p)
    probes.append({'name': name, 'input': p, 'actual': result})
    check(name + '.input_unmodified', p == before)
    check(name + '.actual_unknown', all(result[k] is None and result['rows'][0][k] is None for k in core.UNKNOWNS))
    return result['rows'][0]

report = {'kind': 'SECTION280_LIMITED_INDEPENDENT_IMPLEMENTATION_REVIEW',
          'scope': 'Fixed conditional ordinary-native numeric prefix; all16 conservative RC superset; not game observations, not full QA',
          'game_or_dll_execution': False, 'process_memory_read': False, 'game_or_chat_operation': False,
          'private_state_read_or_write': False, 'reviewer_findings': []}
try:
    check('frozen_core_before', hashlib.sha256(CORE.read_bytes()).hexdigest() == EXPECTED)
    check('sealed_original_same_bytes', (HERE / 'core-before-86853e05.py').read_bytes() == CORE.read_bytes())
    source = core.source_data()
    report['source'] = source
    check('bound_source_valid_9_759', source['valid'] is True and source['method_count'] == 9 and source['byte_span_count'] == 759)

    # Targeted official source reread: exact legacy mnemonics/opcodes, no fused-operation substitution.
    cpu_path = ROOT / '.cache/research/p2-cost-rounding-consensus-280/intel-sdm-volume2abcd-280.pdf'
    cpu_sha = hashlib.sha256(cpu_path.read_bytes()).hexdigest()
    check('official_cpu_pdf_sha', cpu_sha == 'bc4348020f5d5a27b0207c61e3c88d4e610eaf428658dc5d08a1cc84f98a719b')
    pdf = PdfReader(cpu_path)
    cpu_rows = []
    for name, first, required in [
        ('ADDSS', 151, ('F3 0F 58 /r', 'ADDSS DEST, SRC (128-bit Legacy SSE Version)', 'DEST[31:0] := DEST[31:0] + SRC[31:0]')),
        ('CVTDQ2PS', 378, ('NP 0F 5B /r', 'CVTDQ2PS (128-bit Legacy SSE Version)', 'Convert_Integer_To_Single_Precision_Floating_Point')),
        ('MULSS', 889, ('F3 0F 59 /r', 'MULSS (128-bit Legacy SSE Version)', 'DEST[31:0] := DEST[31:0] * SRC[31:0]')),
        ('ROUNDSD', 1311, ('IF (imm[2]', 'MXCSR.RC', 'IMM8.RC', 'ROUNDSD (128-bit Legacy SSE Version)')),
    ]:
        texts = [pdf.pages[i].extract_text() for i in range(first, first + 3)]
        combined = '\n'.join(texts)
        facts = {word: word in combined for word in required}
        check('official_legacy_' + name, all(facts.values()))
        cpu_rows.append({'instruction': name, 'pages_zero_based': list(range(first, first + 3)),
                         'page_text_sha256': [hashlib.sha256(t.encode()).hexdigest() for t in texts],
                         'legacy_form_verified': all(facts.values()), 'facts_archived_as_paraphrase_only': True})
    report['official_cpu_source_reread'] = {'file_sha256': cpu_sha, 'pages': cpu_rows,
        'v4fmaddss_used_as_addss': False, 'game_MXCSR_known': False,
        'first_inspection_correction_retained': (ROOT / '.cache/research/p2-cost-rounding-consensus-280/SOURCE_INSPECTION_CORRECTION.md').exists()}

    # Independently derived literal boundaries, rather than reproducing the rounding implementation.
    x = scalar('inexact_product_integer_closed', 'mul', 10, 0x3e4ccccd, 2, [2])
    check('inexact_product_expands_exact_domain', x['expanded_beyond_exact_only'] and x['all_operations_exact'] is False)
    scalar('positive_half_boundary', 'mul', 10, 0x3d4ccccd, None, [0, 1], 'RC_integer_outcomes_disagree')
    scalar('negative_half_boundary', 'mul', -10, 0x3d4ccccd, None, [-1, 0], 'RC_integer_outcomes_disagree')
    x = scalar('two_step_int32_conversion', 'mul', 16777217, 0x3f800000, None, [16777216, 16777218])
    check('two_step_conversion_literal_bits', [r['cost_single_bits'] for r in x['cost_conversion_candidates']] == [0x4b800000, 0x4b800000, 0x4b800001, 0x4b800000])
    # This is a conservative-superset contract guard, not proof of physical RC switching.
    x = scalar('same_rc_diagnostic_not_full_domain', 'mul', 16777217, 0xb2ffffff, None, [-1, 0])
    check('same_rc_alone_zero', x['same_rc_integer_candidates'] == [0])
    check('mixed_pair_reference_literal', next(c for c in x['cases'] if c['conversion_rc'] == 2 and c['operation_rc'] == 1)['result_bits_candidates'] == [0xbf000001])
    x = scalar('partial_safe_subset_not_consensus', 'mul', 2147483647, 0x3f800000, None, [2147483520], 'incomplete_numeric_domain_consensus_unknown')
    check('max_int32_unsafe_branch_retained', any(c['status'] == 'rounded_int32_conversion_domain_unknown' and c['rounded_int32_reference'] is None for c in x['cases']))
    scalar('minimum_signed32_exact', 'mul', -2147483648, 0x3f800000, -2147483648, [-2147483648])
    scalar('positive_half_even_tie', 'mul', 3, 0x3fc00000, 4, [4])
    scalar('negative_half_even_tie', 'mul', -3, 0x3fc00000, -4, [-4])
    x = scalar('exact_cancellation_zero_sign_superset', 'add', -1, 0x3f800000, 0, [0])
    check('both_zero_signs_conservative', x['possible_operation_bits'] == [0, 0x80000000])
    scalar('minimum_normal_rounds_integer_zero', 'mul', 1, 0x00800000, 0, [0])
    scalar('nonfinite_input_unknown', 'mul', 1, 0x7f800000, None, [], 'modifier_nonfinite_environment_unknown')
    scalar('subnormal_input_unknown', 'add', 0, 1, None, [], 'modifier_subnormal_environment_unknown')
    scalar('operation_overflow_no_number', 'mul', 2, 0x7f7fffff, None, [], 'incomplete_numeric_domain_consensus_unknown')

    a = action('decode_failed'); a['cost_decode']['normal'] = False
    r = rowprobe('proved_failure_blocks_future', a)
    check('decode_failure_prefix', r['normal'] is False and r['stages'][0]['normal'] is True and r['stages'][1]['called'] is True and all(s['called'] is False for s in r['stages'][2:]))
    r = rowprobe('unknown_conversion_future_unknown', action('conversion_unknown', conversion_normally=None))
    check('conversion_unknown_prefix', r['normal'] is None and r['stages'][2]['called'] is True and all(s['called'] is None for s in r['stages'][3:]) and r['encoder_argument_reference'] is None)
    r = rowprobe('known_operation_failed', action('operation_failed', operation_normally=False))
    check('operation_failed_round_not_called', r['normal'] is False and r['stages'][4]['called'] is False and r['encoder_argument_reference'] is None)
    a = action('unknown_numbers'); a['modifier_read']['bits'] = None; a['cost_decode']['value'] = None
    r = rowprobe('opaque_known_normal_prefix', a)
    check('opaque_normal_not_numeric', r['normal'] is True and all(s['normal'] is True for s in r['stages']) and r['encoder_argument_reference'] is None)
    r = rowprobe('receiver_missing_no_call', action('missing'), receiver=False)
    check('missing_receiver_false', r['called'] is False and r['normal'] is False and all(s['called'] is False for s in r['stages']))
    r = rowprobe('ordinary_path_unknown', action('unknown_path', ordinary_native_path=None))
    check('unknown_path_no_false_future', r['called'] is None and all(s['called'] is None for s in r['stages']))

    p = core.public_example()
    expected_input = deepcopy(p)
    result = core.skill_cost_rounding_consensus(p)
    check('independent_next_decode_not_previous_output', result['rows'][8]['encoder_argument_reference'] == 50 and result['rows'][8]['stages'][1]['reference']['value'] == 101)
    check('all_three_numeric_prefix_kinds', {r['kind'] for r in result['rows']} == set(core.KINDS))
    result['payload']['actions'][0]['cost_decode']['value'] = 99
    check('returned_payload_copy', p == expected_input)
    rejected = False
    try:
        forged = deepcopy(p); forged['source_data'] = {'valid': True}
        core.skill_cost_rounding_consensus(forged)
    except ValueError:
        rejected = True
    check('source_injection_rejected', rejected)
    report['public_example_actual'] = core.skill_cost_rounding_consensus(p)
    check('frozen_core_after', hashlib.sha256(CORE.read_bytes()).hexdigest() == EXPECTED)
    check('legacy278_exact_interface_untouched', hashlib.sha256((ROOT / 'rouge/skill_data_cost_reference.py').read_bytes()).hexdigest() == '7cd8eee14c217c46419b5ac70bbcfe14f63e67a5687b7974d8718ae60618077a')
except Exception:
    report['review_tool_exception'] = traceback.format_exc()

report.update({'core_sha256': hashlib.sha256(CORE.read_bytes()).hexdigest(),
               'review_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'probe_count': len(probes), 'checks': checks, 'check_count': len(checks),
               'probes': probes,
               'passed': bool(checks) and all(c['passed'] for c in checks) and 'review_tool_exception' not in report,
               'remaining_unknowns': ['actual MXCSR/masks/handler operands and results', 'physical reachability of mixed RC pairs',
                                     'encoder/store continuation and roundtrip', 'actual cost/SP/complete cycle'],
               'review_scope_not_full_source_rescan_or_QA': True})
OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps({'passed': report['passed'], 'probes': len(probes), 'checks': len(checks),
                  'receipt_sha256': hashlib.sha256(OUT.read_bytes()).hexdigest(),
                  'failed_checks': [c['name'] for c in checks if not c['passed']],
                  'tool_exception': report.get('review_tool_exception')}, ensure_ascii=False))
raise SystemExit(0 if report['passed'] else 1)
