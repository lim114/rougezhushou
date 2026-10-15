"""Limited independent SP14/30 implementation review; public pure data only."""
from copy import deepcopy
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil
import sys
import traceback

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PACKAGE = ROOT / '.cache/section282-preparation'
CORE = PACKAGE / 'rouge/sp_recovery_attribute_reference.py'
SHA = 'c9cf4c2e86b42556cb2b7f0b26c2b1bc083d840a9bedc6990f343447b4f57073'
OUT = HERE / 'implementation-review-282.json'
assert not OUT.exists(), 'Do not overwrite the first actual review.'
sys.path.insert(0, str(ROOT))

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

core = load(CORE, 'rouge._independent_282_review')
Q = 4294967296
checks, probes = [], []
def check(name, ok):
    checks.append({'name': name, 'passed': bool(ok)})
def stage(row, name):
    return next(s for s in row['stages'] if s['name'] == name)
def full():
    return deepcopy(core.public_example())
def probe(name, payload, module=core):
    before = deepcopy(payload)
    result = module.sp_recovery_attribute_reference(payload)
    probes.append({'name': name, 'input': before, 'actual': result})
    check(name + '.input_preserved', payload == before)
    check(name + '.actual_unknown', all(result[k] is None and all(r[k] is None for r in result['rows']) for k in core.UNKNOWNS))
    check(name + '.not_events', result['events_scheduled'] is False and result['hotfix_equivalence_proven'] is False)
    return result
def standalone(reading):
    return {'readings': [reading], 'rate_reads': [], 'initializations': [], 'notifications': []}
def reading(label, attribute=14, raw=Q, dirty=True):
    r = deepcopy(core.public_example()['readings'][1])
    r['id'] = label; r['attribute'] = attribute; r['dirty'] = dirty
    r['decoded_cache']['raw'] = raw; r['calculation']['raw_read']['raw'] = raw
    return r
def modifier(label, ad=0, mul=0, finalad=0, scaler=Q):
    return {'id': label, 'registered': True, 'exists': True, 'get_value_normal': True,
            'included': True, 'basis': 'independent_cache', 'flower_load': None,
            'cache_values': {'addition': ad, 'multiplier_delta': mul,
                             'final_addition': finalad, 'final_scaler': scaler}}

report = {'kind': 'SECTION282_LIMITED_INDEPENDENT_IMPLEMENTATION_REVIEW',
          'scope': 'Generic14/30 cache and ordered buckets; raw14 overwrite prefix; identity-qualified independent-rate to fixed274',
          'new_native_fresh_methods_claimed': 0, 'new_native_fresh_spans_claimed': 0,
          'prior_source_review_receipt': 'source-design-review-282.json',
          'prior_source_review_sha256': '690b62d04a60b80d4b8b05f906947dcdc74a33b1821a521f820d3d4d0ac55419',
          'game_dll_executed': False, 'process_memory_read': False,
          'game_chat_or_private_operations': False, 'reviewer_findings': []}
try:
    check('frozen_core_before', hashlib.sha256(CORE.read_bytes()).hexdigest() == SHA)
    check('sealed_before_core', (HERE / 'core-before-c9cf4c2e.py').read_bytes() == CORE.read_bytes())
    check('bound_source', core.source_data()['valid'] is True)
    normalized = json.loads((PACKAGE / 'research/p2-sp-recovery-attributes-282/source-proof.json').read_bytes())
    init = next(m for m in normalized['methods'] if m['method']['metadata_method_index'] == 66624)
    check('normalized_init_selected_metrics', init['instruction_count'] == 92 and init['reachable_instruction_bytes'] == 384 and len(init['instructions']) == 92)
    check('preserved_inherited_init_metrics', init['original_full_method_metrics']['instruction_count'] == 719)
    manifest = json.loads((PACKAGE / 'research/p2-sp-recovery-attributes-282/source_manifest.json').read_bytes())
    check('fresh_outer_guard_29_files', len(manifest['files_sha256']) == 29)

    r = probe('public_composition', full())
    check('ratio_default_not_upper_one', next(v for v in r['readings'] if v['id'] == 'ratio-over-one')['getter_raw_reference'] == 3 * Q)
    check('negative_default_clamped_zero', next(v for v in r['readings'] if v['id'] == 'negative14')['getter_raw_reference'] == 0)
    initial, notice = r['rows']
    check('slot_conversion_not_refresh_decode', initial['slot0_fp_argument_raw_reference'] == 6442450944 and initial['refresh_reference']['getter_raw_reference'] == 7 * Q)
    check('raw_opaque40_not_actual', initial['stored_prefix'] == [{'field': 'rawData[14]', 'byte_count': 40, 'payload_identity': None, 'decoded_value': None}] and initial['raw_value_after'] is None and initial['cache_value_after'] is None)
    check('independent_new_and_can_rates', notice['clock_request']['actions'][0]['rate_input_raw'] == 2 * Q and notice['can_recover_snapshot_reference']['attr14_raw'] == Q)
    check('qualified_keep_past_literal', notice['clock_reference']['final_period_raw_reference'] == Q // 2 and notice['clock_reference']['final_remaining_raw_reference'] == Q // 4)
    check('inline_body_label', stage(notice, 'controller_update')['reference']['source_body'] == 'inline_UpdateSpRecoveryPerSec')

    a = reading('four-bucket-literal', raw=5 * Q // 4)
    a['calculation']['modifiers'] = [modifier('first', 2 * Q, Q // 2, Q, 2 * Q), modifier('second', -Q, -Q // 4, -Q // 2, 3 * Q)]
    r = probe('ordered_four_buckets_literal', standalone(a))['readings'][0]
    check('four_bucket_literal_result', r['getter_raw_reference'] == 85362475008)
    check('four_bucket_literal_aggregation', r['buckets_reference'] == {'addition': Q, 'multiplier_delta': 5 * Q // 4, 'final_addition': Q // 2, 'final_scaler': 6 * Q})
    for name, scalers, expected in [('order_a', [Q + 1, Q + 1, Q // 2], Q // 2 + 1), ('order_b', [Q + 1, Q // 2, Q + 1], Q // 2)]:
        a = reading(name); a['calculation']['modifiers'] = [modifier(name + str(i), scaler=v) for i, v in enumerate(scalers)]
        r = probe('fixedpoint_association.' + name, standalone(a))['readings'][0]
        check(name + '.literal_low_bit_result', r['getter_raw_reference'] == expected)
    a = reading('clean-cache', raw=-Q, dirty=False); a['calculation']['raw_read']['raw'] = 10 * Q
    r = probe('clean_decoded_cache_independent', standalone(a))['readings'][0]
    check('clean_negative_not_reclamped', r['getter_raw_reference'] == -Q and r['dirty_cleared_reference'] is False)
    a = reading('incomplete-range'); a['calculation']['inventory_complete'] = False
    a['calculation']['range_read'].update(override=True, lower_raw=5 * Q, upper_raw=2 * Q)
    r = probe('incomplete_inventory_reversed_range', standalone(a))['readings'][0]
    check('reversed_range_native_order_closes', r['getter_raw_reference'] == 5 * Q and all(v is None for v in r['buckets_reference'].values()))
    a = reading('negative-multiplier', raw=None); a['calculation']['modifiers'] = [modifier('negative_delta', mul=-2 * Q)]
    r = probe('zero_factor_closes_unknown_raw', standalone(a))['readings'][0]
    check('max0_multiplier_absorbs_unknown', r['getter_raw_reference'] == 0 and r['normal_return_reference'] is True)
    a = reading('failed-raw'); a['calculation']['raw_read']['normal'] = False
    r = probe('early_dirty_clear_preserved_on_failure', standalone(a))['readings'][0]
    check('early_clear_not_successful_getter', r['dirty_cleared_reference'] is True and r['normal_return_reference'] is False and r['getter_raw_reference'] is None)

    p = full(); p['initializations'][0]['attributes_read']['exists'] = False
    r = probe('initial_captured_attributes_null', p)['rows'][0]
    check('conversion_before_attributes_null_guard', r['slot0_fp_argument_raw_reference'] == 6442450944 and stage(r, 'single_conversion')['normal'] is True and stage(r, 'attributes_guard')['normal'] is False and stage(r, 'raw_encode')['called'] is False)
    p = full(); p['initializations'][0]['increments_read']['length'] = 1; p['initializations'][0]['raw_array_read']['exists'] = False
    r = probe('slot0_only_length_one_and_raw_null', p)['rows'][0]
    check('no_four_slot_requirement', stage(r, 'slot0_read')['called'] is True and r['slot0_fp_argument_raw_reference'] == 6442450944)
    check('encoder_precedes_raw_array_null', stage(r, 'raw_encode')['normal'] is True and stage(r, 'raw_array_guard')['normal'] is False and stage(r, 'raw_store')['called'] is False)
    for flag in (False, None):
        p = full(); p['initializations'][0]['mark_dirty_returns_normally'] = flag
        r = probe('opaque_mark_dirty.' + str(flag), p)['rows'][0]
        check('mark_dirty_prefix.' + str(flag), len(r['stored_prefix']) == 1 and r['normal'] is flag and stage(r, 'refresh')['called'] is (False if flag is False else None))
        check('no_simulated_dirty_state.' + str(flag), stage(r, 'mark_dirty')['reference']['partial_mask_state'] is None and stage(r, 'mark_dirty')['reference']['callback_target'] is None)
    p = full(); p['readings'][0]['calculation']['raw_read']['normal'] = False
    r = probe('independent_refresh_failure_keeps_raw_store', p)['rows'][0]
    check('refresh_failure_retains_prefix', r['normal'] is False and len(r['stored_prefix']) == 1 and r['refresh_reference']['dirty_cleared_reference'] is True and r['refresh_reference']['getter_raw_reference'] is None)
    p = full(); p['initializations'][0]['slot0_read']['bits'] = None
    r = probe('unknown_single_value_opaque_store', p)['rows'][0]
    check('unknown_conversion_not_call_failure', r['normal'] is True and r['slot0_fp_argument_raw_reference'] is None and stage(r, 'raw_encode')['reference']['argument_raw'] is None and len(r['stored_prefix']) == 1 and r['refresh_reference']['getter_raw_reference'] == 7 * Q)

    p = full(); p['notifications'][0]['controller_read']['exists'] = False
    r = probe('new_rate_before_controller_null', p)['rows'][1]
    check('rate_still_called_before_guard_failure', stage(r, 'new_rate')['normal'] is True and r['new_rate_reference']['rate_raw_reference'] == 2 * Q and stage(r, 'controller_guard')['normal'] is False and stage(r, 'controller_update')['called'] is False and r['clock_request'] is None)
    p = full(); p['readings'][3]['decoded_cache']['raw'] = 0
    r = probe('positive_new_rate_separate_can_recover_false', p)['rows'][1]
    check('new_rate_does_not_replace_can_getter', r['clock_request']['actions'][0]['rate_input_raw'] == 2 * Q and r['can_recover_snapshot_reference']['attr14_raw'] == 0 and r['clock_reference']['final_period_raw_reference'] == -Q and r['clock_reference']['final_remaining_raw_reference'] == -Q)
    p = full(); p['notifications'][0]['timer'].update(period_raw=0, remaining_raw=0); p['rate_reads'][1]['first_attributes_getter_normal'] = False
    r = probe('invalid_timer_does_not_consume_can_getter', p)['rows'][1]
    check('invalid_timer_restart_normal_despite_unused_bad_can', r['normal'] is True and r['clock_reference']['final_period_raw_reference'] == Q // 2 and r['clock_reference']['final_remaining_raw_reference'] == Q // 2)
    p = full(); p['rate_reads'][0]['second_attributes_getter_normal'] = False
    r = probe('second_attributes_failure_does_not_reach_controller_guard', p)['rows'][1]
    check('new_rate_failure_future_false', r['normal'] is False and stage(r, 'controller_guard')['called'] is False and stage(r, 'controller_update')['called'] is False and r['clock_request'] is None)
    p = full(); p['notifications'][0]['controller_matches_clock'] = False
    r = probe('no_assumed_controller_identity', p)['rows'][1]
    check('identity_unqualified_no_clock', r['new_rate_reference']['rate_raw_reference'] == 2 * Q and r['normal'] is None and r['clock_request'] is None and r['clock_reference'] is None)

    rejected = {}
    for field in ('source_data', 'evaluator'):
        p = full(); p[field] = True
        try: core.sp_recovery_attribute_reference(p); rejected[field] = False
        except ValueError: rejected[field] = True
        check('public_injection_rejected.' + field, rejected[field])
    p = full(); p['readings'][0]['attribute'] = 13
    try: core.sp_recovery_attribute_reference(p); reject_hp = False
    except ValueError: reject_hp = True
    check('hp_attribute_not_admitted', reject_hp)
    p = full(); p['readings'][1]['calculation']['modifiers'] = [modifier('not-a-flower')]
    p['readings'][1]['calculation']['modifiers'][0]['basis'] = 'flower'
    try: core.sp_recovery_attribute_reference(p); reject_flower = False
    except ValueError: reject_flower = True
    check('hp_flower_recipe_not_transferred', reject_flower)
    from rouge import recovery_attributes as old273
    p = old273.public_example(); p['readings'][0]['attribute'] = 14
    try: old273.recovery_attribute_reference(p); old_rejected = False
    except ValueError: old_rejected = True
    check('old273_public_scope_unchanged', old_rejected)

    # Warm each isolated clone first; changing a pinned file afterward defeats any inner LRU.
    for name, target in [('cached_attribute_source', 'rouge/data/recovery-attribute-source.json'),
                         ('fixedpoint_helper', 'rouge/mechanist_explosion_math.py')]:
        dest = HERE / ('implementation-clone-' + name)
        assert not dest.exists()
        paths = set(manifest['files_sha256']) | {'rouge/sp_recovery_attribute_reference.py',
                'research/p2-sp-recovery-attributes-282/source_manifest.json',
                'research/p2-sp-recovery-attributes-282/source-proof.json'}
        for rel in sorted(paths):
            out = dest / rel; out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(PACKAGE / rel, out)
        cloned = load(dest / 'rouge/sp_recovery_attribute_reference.py', 'rouge._282_clone_' + name)
        warm = cloned.sp_recovery_attribute_reference(cloned.public_example())
        check('clone_valid_warm.' + name, warm['source_valid'] is True and warm['rows'][1]['clock_reference']['final_period_raw_reference'] == Q // 2)
        file = dest / target; file.write_bytes(file.read_bytes() + b'\n')
        result = probe('uncached_source_guard.' + name, cloned.public_example(), cloned)
        check('all_derived_suppressed.' + name, result['source_valid'] is False and all(v['getter_raw_reference'] is None for v in result['readings']) and all(v['rate_raw_reference'] is None for v in result['rate_reads']) and all(not row['stored_prefix'] and row['clock_reference'] is None and all(s['called'] is None for s in row['stages']) for row in result['rows']))

    check('frozen_core_after', hashlib.sha256(CORE.read_bytes()).hexdigest() == SHA)
    check('273_core_not_changed', hashlib.sha256((ROOT / 'rouge/recovery_attributes.py').read_bytes()).hexdigest() == manifest['files_sha256']['rouge/recovery_attributes.py'])
    check('274_core_not_changed', hashlib.sha256((ROOT / 'rouge/sp_recovery_clock.py').read_bytes()).hexdigest() == manifest['files_sha256']['rouge/sp_recovery_clock.py'])
except Exception:
    report['review_tool_exception'] = traceback.format_exc()

report.update({'core_sha256': hashlib.sha256(CORE.read_bytes()).hexdigest(),
               'review_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'probe_count': len(probes), 'check_count': len(checks), 'checks': checks, 'probes': probes,
               'passed': bool(checks) and all(c['passed'] for c in checks) and 'review_tool_exception' not in report,
               'remaining_unknowns': ['actual attribute/cache/dirty/timer/SP/cycle', 'delegate/attachment identity and callback effects', 'protected encode/decode equality', 'current hotfix/runtime source'],
               'scope_not_full_QA_or_native_window': True})
OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
print(json.dumps({'passed': report['passed'], 'probes': len(probes), 'checks': len(checks),
                  'receipt_sha256': hashlib.sha256(OUT.read_bytes()).hexdigest(),
                  'failed_checks': [c['name'] for c in checks if not c['passed']],
                  'tool_exception': report.get('review_tool_exception')}, ensure_ascii=False))
raise SystemExit(0 if report['passed'] else 1)
