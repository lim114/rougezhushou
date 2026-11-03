"""Independent standard-library source/data inspection; no reviewed function execution."""
import ast
import base64
import collections
import gzip
import hashlib
import json
from pathlib import Path, PureWindowsPath

OUT = Path(__file__).resolve().parent
FINAL = Path('/workspace/.continuation/full095-ui-final-v1')
PENDING = Path('/workspace/.continuation/full095-ui-migration-pending-v3')
REPO = Path('/workspace/rougezhushou')
SHA = lambda b: hashlib.sha256(b).hexdigest()
REFS, CHECKS = {}, []

def check(name, value, detail=None):
    CHECKS.append({'id': name, 'passed': bool(value), 'detail': detail})
    if not value:
        raise AssertionError(name)

def path(value):
    if value.startswith('Z:'):
        w = PureWindowsPath(value)
        assert w.drive == 'Z:' and w.root == '\\' and '..' not in w.parts
        assert Path('/workspace/.compat/wine-prefix/dosdevices/z:').resolve() == Path('/')
        return Path('/').joinpath(*w.parts[1:])
    return Path(value)

def raw(p):
    p = path(str(p))
    assert p.is_file() and not p.is_symlink() and p.resolve() == p
    assert p.is_relative_to('/workspace/.continuation') or p.is_relative_to('/workspace/.compat') or p.is_relative_to(REPO)
    b = p.read_bytes()
    REFS[str(p)] = {'path': str(p), 'bytes': len(b), 'sha256': SHA(b)}
    return b

def doc(p):
    return json.loads(raw(p))

def bound(r):
    b = raw(r['path'])
    assert SHA(b) == r['sha256'] and ('bytes' not in r or len(b) == r['bytes'])
    return b

def ptr(d, p):
    for k in p[1:].split('/'):
        k = k.replace('~1', '/').replace('~0', '~')
        d = d[int(k)] if isinstance(d, list) else d[k]
    return d

def assignment(tree, name):
    found = [n for n in ast.walk(tree) if isinstance(n, ast.Assign) and any(isinstance(x, ast.Name) and x.id == name for x in n.targets)]
    assert len(found) == 1
    return found[0]

def function(tree, name):
    found = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == name]
    assert len(found) == 1
    return found[0]

def segment(source, tree, name):
    return ast.get_source_segment(source, function(tree, name))

def main():
    mf = doc(FINAL / 'public-artifacts-manifest-final095.json')
    hand = doc(FINAL / 'handoff-final095.json')
    for name, row in mf['artifacts'].items():
        b = raw(FINAL / name)
        assert len(b) == row['bytes'] and SHA(b) == row['sha256']
    check('F01_actual_FINAL_whole_physical_packet_and_manifest', {p.name for p in FINAL.iterdir()} == set(mf['artifacts']) | {'public-artifacts-manifest-final095.json', 'handoff-final095.json'} and len(mf['artifacts']) == 3)
    final = raw(FINAL / 'wine-full-ui-095-final.py')
    check('F02_actual_FINAL_runner_pinned', SHA(final) == '83c412ce7e456109dc32a6415f7a61526955d48b01d25dbb72198870e6cf18ee' and len(final) == 1184276)
    binding = doc(FINAL / 'root-bound-input095.json')
    fs = final.decode(); ft = ast.parse(fs)
    flag = assignment(ft, 'PENDING095'); literal = assignment(ft, 'BINDING095')
    check('F03_literal_bindings_exact_saved_JSON', ast.literal_eval(flag.value) is False and ast.literal_eval(literal.value) == binding)
    pmf = doc(PENDING / 'public-artifacts-manifest-pending095.json')
    for name, row in pmf['artifacts'].items():
        b = raw(PENDING / name); assert len(b) == row['bytes'] and SHA(b) == row['sha256']
    ps = raw(PENDING / 'wine-full-ui-095-pending.py').decode(); pt = ast.parse(ps)
    old_literal = ast.get_source_segment(ps, assignment(pt, 'BINDING095'))
    new_literal = ast.get_source_segment(fs, literal)
    recovered = fs.replace(new_literal, old_literal, 1).replace('PENDING095 = False', 'PENDING095 = True', 1).encode()
    check('F04_two_only_FINAL_substitutions_whole_byte_inverse', fs.count(new_literal) == 1 and fs.count('PENDING095 = False') == 1 and recovered == ps.encode())
    ledger = doc(PENDING / 'exact-inverse-ledger095.json')
    for r in reversed(ledger['operations']):
        start, size = r['pending_byte_start'], r['pending_byte_count']
        assert SHA(recovered[start:start+size]) == r['pending_sha256']
        before = base64.b64decode(r['before_base64']); assert SHA(before) == r['original_sha256']
        recovered = recovered[:start] + before + recovered[start+size:]
    original = raw('/workspace/.continuation/ui-090-final-gate-revision/wine-ui-smoke-090-final-gate-revision.py')
    check('F05_all79_inverse_operations_original729181_byteexact', len(ledger['operations']) == 79 and recovered == original == raw(REPO / 'verification/full-090/wine-ui-runner.py') and len(original) == 729181)
    os = original.decode(); ot = ast.parse(os)
    prior = doc('/workspace/.continuation/full095-ui-pending-independent-review-v3/formal-source-review-full095-ui-v3.json')
    check('F06_prior_independent_SOURCE_gate_exact_pending_not_runtime', prior['source_gate_passed'] is True and prior['runtime_pass'] is False and prior['pending_runner_sha256'] == SHA(ps.encode()) and prior['pending_manifest_sha256'] == SHA(raw(PENDING / 'public-artifacts-manifest-pending095.json')))
    originals = sorted((n for n in ast.walk(ot) if isinstance(n, ast.Assert)), key=lambda n:n.lineno)
    classification = doc(PENDING / 'original-assertion-and-delta-classification095.json')
    assert len(originals) == len(classification['assertions']) == 826
    for n, r in zip(originals, classification['assertions']):
        assert n.lineno == r['original_line']
        assert SHA(ast.get_source_segment(os, n).encode()) == r['original_statement_sha256']
        assert SHA(ast.dump(n, include_attributes=False).encode()) == r['original_AST_sha256']
    actual_asserts = collections.Counter(ast.dump(n, include_attributes=False) for n in ast.walk(ft) if isinstance(n, ast.Assert))
    missing = [n.lineno for n in originals if not actual_asserts[ast.dump(n, include_attributes=False)]]
    check('F07_826_original_assertions822_AST_exact_four_preapproved', missing == [2365,2528,2687,3011], {'original':826,'unchanged':822,'preapproved_filename3_visibility1':missing})
    protected = prior['independent_source_checks']['protected_helpers']
    for r in protected:
        original_function = segment(os, ot, r['name']); final_function = segment(fs, ft, r['name'])
        assert SHA(original_function.encode()) == r['original_ast_source_sha256']
        assert SHA(final_function.encode()) == r['pending_ast_source_sha256']
        if r['name'] != 'train': assert original_function == final_function
    check('F08_14_protected_helpers_13exact_legal_train_id_only', len(protected) == 14)
    for r in prior['independent_source_checks']['protected_literal_assignments']:
        assert ast.get_source_segment(os, assignment(ot,r['name'])) == ast.get_source_segment(fs,assignment(ft,r['name']))
    check('F09_four_original_literal_assignments_wholebyte_preserved', True)
    for r in prior['independent_source_checks']['approved_codec_functions_source_only']:
        source = bound(r['approved_file']).decode(); tree = ast.parse(source)
        assert segment(fs, ft, r['name']) == segment(source,tree,r['name'])
        assert SHA(segment(fs,ft,r['name']).encode()) == r['function_sha256']
    check('F10_nine_approved_native_bytes_functions_sourceexact_unexecuted', len(prior['independent_source_checks']['approved_codec_functions_source_only']) == 9)
    guard = json.loads(bound(binding['source_guard']))
    actual = {p.relative_to(REPO).as_posix():SHA(raw(p)) for folder in ('rouge','tests','scripts') for p in sorted((REPO/folder).rglob('*')) if p.is_file() and p.suffix in ('.py','.json') and '__pycache__' not in p.parts}
    check('F11_actual735_fullselector_zero_drift_guard41b9', guard['passed'] is True and guard['candidate_bytes_exact'] is True and len(actual) == 735 and actual == guard['source_sha256_after'] and binding['source_guard']['sha256'] == '41b9f4662a31b0c8ade2cf51c019bda0a04f6569e92770249bcf2e7ebabe9eab')
    code = json.loads(bound(binding['candidate_manifest']))
    for r in code['files']:
        assert len(raw(REPO/r['destination_repo_path'])) == r['bytes'] and actual[r['destination_repo_path']] == r['sha256']; bound({'path':r['source_path'],'bytes':r['bytes'],'sha256':r['sha256']})
    check('F12_original_five_product_payloads_frozen_exact', len(code['files']) == 5 and binding['candidate_manifest']['sha256'] == '216d5c31a9bc89dbc51f0b875db073a4fe8ea8b85fb5c9b624f5d9d6f56a461a')
    supplements = binding['additional_formal_artifacts']; assert len(supplements) == 1
    supp = supplements[0]; json.loads(bound(supp)); sr = json.loads(bound(supp['formal_review']))
    target = supp['source_targets'][0]
    check('F13_single_oldtest_real_formal_6a580_8641_source_target', supp['sha256'] == '6a580bed1e8e60a1782fb53495996b4f841626a77eea9292f10952acdd194fcc' and supp['formal_review']['sha256'] == '86418bd3c790485b99d365cbf4cd6b0cf7da328aa51fe8364fcc0bca6d313e09' and ptr(sr,supp['formal_review_pass_pointer']) is True and sr['runtime_pass'] is False and target['destination_repo_path'] == 'tests/test_token_duration_reference.py' and actual[target['destination_repo_path']] == target['sha256'] and len(raw(REPO/target['destination_repo_path'])) == target['bytes'])
    for k in ('implementation_freeze','technical_tail_correction_artifact','actual94_receipt','actual94_guard','baseline_receipt','baseline_saved_verifier'):bound(binding[k])
    correction = json.loads(bound(binding['technical_tail_correction_artifact']))
    check('F14_corrected_doubleNL_tail_original_interface_bound', correction['actual_complete_append_tail_prefix'] == binding['report_contract']['technical_tail_prefix'] == '\n\n【所选模组原件追溯】\n' and correction['exact_code_product_manifest_sha256'] == binding['candidate_manifest']['sha256'])
    normalized = doc('/workspace/.continuation/root-full095-ui-binding-data-v1/normalized-fullui-binding095.json')
    expected = json.loads(json.dumps(normalized))
    for k in ('source_guard','candidate_manifest','implementation_freeze','technical_tail_correction_artifact','actual94_receipt','actual94_guard','baseline_receipt','baseline_saved_verifier'):
        expected[k]['path'] = 'Z:' + expected[k]['path'].replace('/','\\')
    for k in ('baseline_files','qualified_reference_provenance'):
        for r in expected[k]:r['path'] = 'Z:' + r['path'].replace('/','\\')
    for r in expected['additional_formal_artifacts']:
        r['path'] = 'Z:' + r['path'].replace('/','\\'); r['formal_review']['path'] = 'Z:' + r['formal_review']['path'].replace('/','\\')
    check('F15_actual_data_output_to_FINAL_only_declared_Z_path_normalization', binding == expected)
    build = doc('/workspace/.continuation/root-full095-ui-binding-data-v1/binding-data-build-receipt095.json')
    for r in build['input_bindings']:bound(r)
    buildmf = doc('/workspace/.continuation/root-full095-ui-binding-data-v1/public-artifacts-manifest-built-binding095.json')
    for r in buildmf['payload']:bound(r)
    bformal = doc('/workspace/.continuation/p2-full095-ui-binding-data-builder-formal-source-review-v1/formal-source-review-data-builder095-v1.json')
    check('F16_DATA_producer_independent_SOURCE_and_actual_saved_inputs', bformal['source_gate_passed'] is True and bformal['runtime_pass'] is False and build['passed'] is True and build['project_API_helper_codec_Qt_Wine_Git_network_calls'] == 0 and build['actual_focused113API_replayed'] is False and build['normalized_binding']['sha256'] == SHA(raw('/workspace/.continuation/root-full095-ui-binding-data-v1/normalized-fullui-binding095.json')))
    qualrow = binding['qualified_reference_provenance'][0]; qual = json.loads(bound(qualrow))
    saved = json.loads(bound(qual['actual_saved_only_review'])); receipt = json.loads(bound(qual['actual_runtime_receipt']))
    data = json.loads(gzip.decompress(bound(saved['actual_native_archive'])))
    baseline = json.loads(gzip.decompress(bound(binding['baseline_files'][0])))
    current_states = {r['id']:r for r in data['states']}
    saved_formal = doc('/workspace/.continuation/focused095-saved-validator-v4-formal-source-review/formal-source-review-saved-helper095-v4.json')
    check('F17_actual_focused_attempt2_primary0_savedv4_PASS_41', bound(saved['actual_primary_exit']) == b'0\n' and saved['passed'] is True and saved['runtime_attempt'] == 2 and saved['states_verified'] == receipt['states'] == len(current_states) == 41 and saved_formal['source_gate_passed'] is True and saved_formal['runtime_pass'] is False and saved_formal['helper_sha256'] == saved['verifier_source']['sha256'] and receipt['passed'] is receipt['workflow_complete'] is True)
    plan = doc(PENDING/'full095-subgroup-plan.json')
    assert len(binding['cases']) == len(plan['steps']) == 21
    assert [r['id'] for r in binding['cases']] == [r['id'] for r in plan['steps']]
    bridges, additions, strings = [], 0, 0
    for case, proposed in zip(binding['cases'],plan['steps']):
        assert case['step'] == proposed['step'] and case['comparison'] == proposed['comparison']
        if case['comparison'] == 'same_action_auto_manual':
            assert case['step']['action'] == 'numeric_callback' and case['step']['widget'] == 'defense' and case['step']['old_value'] == case['step']['restore_value'] == 0 and case['step']['value'] == 7
            continue
        old = ptr(baseline,case['baseline_pointer']); state = current_states[case['id']]
        assert old['id'] == case['id'] and old['passed'] is True and state['passed'] is True and state['planned']['JSON_projection'] == old['planned']['JSON_projection'] == case['step']
        delta = case['delta']; q = qual['cases'][case['id']]
        assert delta['has_addition'] == q['has_addition']
        if not delta['has_addition']:
            for mode in ('automatic','manual') if 'manual' in state else ('automatic',):
                assert state[mode]['damage_result']['native'] == old[mode]['damage_result']['native'] and state[mode]['three_texts'] == old[mode]['three_texts'] and state[mode]['visible_status'] == old[mode]['visible_status']
        else:
            additions += 1
            assert delta['reference_path'] == ['result','report','selected_module_source_reference'] and delta['sections_path'] == ['result','report','sections'] and delta['section_id'] == 'selected_module_source'
            assert ptr(qual,delta['provenance_pointer']) == q and delta['provenance_file'] == qualrow['name']
            for k in ('expected_reference_native','expected_section_native','text_insertions'):assert delta[k] == q[k]
            assert q['actual95_source_guard_sha256'] == binding['source_guard']['sha256'] and q['actual94_full_native_and_existing_report_exact'] is q['independent_raw_source_qualified'] is True
            for mode in ('automatic','manual') if 'manual' in state else ('automatic',):
                captured = state[mode]; proof = state['baseline_equivalence'][mode]
                assert captured['live_reference_alias_check']['independent_fresh_reference']['native'] == delta['expected_reference_native']
                assert captured['live_reference_alias_check']['independent_fresh_report_reference_detached_and_exact'] is True
                assert proof['full_native_except_exact_report_additions'] is True
                for key in ('raw_original_metadata_phase_owner_exact','existing_coverage_paths_valid','unknown_equipment_attachment_preserved'):assert proof['raw_original_source_checks'][key] is True
                for textmode in ('default','estimate','technical'):
                    before = old[mode]['three_texts']['strings'][textmode]; after = captured['three_texts']['strings'][textmode]
                    rows = delta['text_insertions'][textmode]; previous = len(before)+1; rebuilt = before
                    for r in sorted(rows,key=lambda r:r['offset'],reverse=True):
                        assert type(r['offset']) is int and 0 <= r['offset'] <= len(before) and r['offset'] < previous and SHA(r['text'].encode()) == r['sha256']
                        rebuilt = rebuilt[:r['offset']] + r['text'] + rebuilt[r['offset']:]; previous = r['offset']
                    assert rebuilt == after
                    assert any(r['text'].startswith('\n\n【所选模组 · 原件资料与覆盖边界】\n') for r in rows)
                    tails = [r for r in rows if r['text'].startswith(correction['actual_complete_append_tail_prefix'])]
                    assert len(tails) == (1 if textmode == 'technical' else 0)
                    if tails: assert tails[0]['offset'] == len(before) and after.endswith(tails[0]['text'])
                    strings += 1
        bridges.append(case['id'])
    check('F18_all21_steps_20_actual94_native_bridges_one_callback', len(bridges) == 20 and len(qual['cases']) == 20, {'paired_ids':bridges,'selected_additions':additions,'actual_texts_byteexact_reconstructed':strings})
    strict = segment(fs,ft,'_strict_baseline095')
    check('F19_runtime_exact_singlekey_uniquefinalsection_fullnative_three_texts', "matches[0]==len(section_list)-1" in strict and "removed['metrics']==[]" in strict and "flat_native(current)==baseline['damage_result']['native']" in strict and "capture['three_texts']['strings'][mode]==text" in strict and 'del parent[path[2]]' in strict and 'flat_native(reference)==delta_contract' in strict)
    profile = segment(fs,ft,'_profile095'); checkpoint = segment(fs,ft,'_checkpoint095'); finish = segment(fs,ft,'_finish095')
    check('F20_actual_API_prepared_originalcaller_retention_allphase_exception_trace', "_caller_objects095[id(frame)]=inputs" in profile and "_caller_objects095.pop(id(frame),None)" in profile and "record['caller_after']=snapshot(inputs)" in profile and "record['returned']=snapshot(arg)" in profile and "_phase_entries095.setdefault" in profile and "exception_events" in segment(fs,ft,'_trace_local095'))
    calls = sorted({ast.unparse(n.func) for n in ast.walk(function(ft,'_checkpoint095')) if isinstance(n,ast.Call)})
    check('F21_savepause_materialized_stdlib_only_hooks_finally_restore', not any(any(k in name for k in ('native_inverse','flat_native','snapshot','clone','calculate','format_report','processEvents')) for name in calls) and 'finally:' in checkpoint and 'sys.settrace(saved_trace);sys.setprofile(saved_profile)' in checkpoint, calls)
    check('F22_fresh_nativev3_absent_preimports_full_dynamic_physical_collection', "assert not _guard_native_out095.exists()" in fs and fs.index('_guard_native_out095.mkdir()') < fs.index('# END FULL095 PENDING ADMISSION') and "path.relative_to(_guard_out095).as_posix()" in checkpoint and "'full095-ui-native-v3/wine-ui-full-native-index-095.json'" in finish and "receipt['full_native095']['files']" in finish and 'rglob' in finish)
    check('F23_original4283_count_then_new21_total_real_receipt_fields', fs.index('assert len(checks)==4283,len(checks)') < fs.index("receipt['actual095_behavior_rows']=_new_subgroup095") and "receipt['legacy_original4283_actual_checks']=len(checks)" in fs and "receipt['legacy085_prefix4217_and090_additional66_preserved']=True" in fs and "receipt['actual_total_checks095']=len(checks)" in fs)
    own = segment(fs,ft,'source_hashes')
    check('F24_own_source_scope_original_rouge129_keys_not_full735', own == segment(os,ot,'source_hashes') and "for folder in (ROOT/'rouge',)" in own)
    keys = sorted(k for k in actual if k.startswith('rouge/'))
    check('F25_real_execution_contract_root_wrapper_absolute_Z_runner', len(keys) == 129 and hand['runner']['sha256'] == SHA(final) and hand['manifest']['sha256'] == SHA(raw(FINAL/'public-artifacts-manifest-final095.json')) and hand['fresh_native_directory'] == '/workspace/.compat/full095-ui-native-v3')
    section95 = doc(REPO/'verification/sections/095.json')
    check('F26_real95archive_distinct_SOURCE_admission_false_fullruntimepending', section95['passed'] is True and section95['workflow_complete'] is True and binding['actual95_section_completed'] is False and binding['section_completed'] is False and mf['actual095_completed'] is False and hand['section_completed'] is False)
    check('F27_all_source_input_hashes_unchanged_at_end', all(len(path(r['path']).read_bytes()) == r['bytes'] and SHA(path(r['path']).read_bytes()) == r['sha256'] for r in REFS.values()))
    result = {'format_version':1,'status':'PASS_SOURCE_AND_SAVED_DATA_INSPECTION_ONLY_NO_HARNESS_OR_CODEC_EXECUTION','passed':True,'checks':CHECKS,'source_keys':keys,'input_refs':list(REFS.values()),'all_reviewed_harness_helper_codec_project_Qt_Wine_Git_network_functions_executed':0,'tracked_repository_writes':0,'private_state_reads':0}
    output = OUT/'source-check-result095.json'; output.write_bytes(json.dumps(result,ensure_ascii=False,indent=2).encode()+b'\n')
    print(json.dumps({'passed':True,'checks':len(CHECKS),'input_refs':len(REFS),'source_keys':len(keys),'reviewed_functions_executed':0}))

if __name__ == '__main__':
    main()
