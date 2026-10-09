"""Root-only actual107 closure/spec builder; Source preparation is not a PASS.

No project/helper/codec/test/Qt/Wine/Git imports or calls. Actual future runner,
Saved Source/bindings and applier primary are required inputs, never invented.
Only external report/spec files are written after all real terminal gates.
"""
import argparse
import ast
import datetime
import hashlib
import json
from pathlib import Path

BASE = Path('/workspace/.continuation')
ROOT = Path('/workspace/rougezhushou')
ORIGINAL_SHA = '0a38276dda0ee3e6640f203cc61397686b6e83c365656578b6896dc461563d00'
FIRST_GOLD_SHA = 'f786cba8c64d66f47d4c11d9b08074114702321281b75ba65587620df8f9c038'
DIAGNOSIS_SHA = '3b94cf623b58e8100f793a722bc8d5ea18ff4eab0954056da75fc44f7be089cf'
RELATED_SOURCE_SHA = '2f1c302f89ba122f73fadd0e15d5de2b020e7dae56cce6bcdc311944e5367f13'
SELECTOR = 'tests.test_aglna_gravity_weight_107'
TEST_PATH = 'tests/test_aglna_gravity_weight_107.py'
OLD_TEST_SHA = '62766f1d8cae2b4ef4618ae4f90dddb0c1e9ce8d165f272f1d0fc9caa3b87e8c'
NEW_TEST_SHA = '2c5eab4be5f484ca3eaf45d19eeb1f1067661a36c42ea41297a5ad1ec22ecc51'
OLD_APPLIED_SHA = '9f06db822007088a569ab571abb1b950bdc9701ad3eaa366603b713c80f9d897'
FAILED_RELATED_SHA = '6f407da19b0899d77331bd23a9eb3abab92edb8fd4413aab5fa7e8042147ae82'
EMPTY_DIAGNOSIS_SHA = 'a4748413342aab7a5ee896beabadafd74553c82fdcc045bd68c8f942b777172b'
GOLD_RUNNER_SHA = '9762693bc8088837122758f4c3893ac17b47414ced0c484942cb0754e31472e8'
CANDIDATE_RUNNER_SHA = '9ab0acdc117ab545386261006e341aabc1763ee679dcf3be36eae3eb032e6207'
GOLD_RECEIPT_SHA = 'f543d873cbc9ab3c629e8d0815df3438a82c15fe459e463870f757bef9396634'
TEST_REPAIR_SOURCE_SHA = 'f8ae7e02566624bce6c8e160aaa507596e3446d78b322521ccad07bbff01fca2'
TEST_REPAIR_REVIEW_SHA = '13c8b59a0c7797620c9bd57dfbdf41982bf4669fe7f87f75d9b6494b09a95bc2'
PHASES = ('plain','gravity-base','gravity-manual100',
          'manual-light-original-oracle','restored-plain','actual-fresh-save-view')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(name):
    return json.loads((BASE / name).read_bytes())


def pin(path):
    path = Path(path).resolve()
    raw = path.read_bytes()
    return {'path': str(path), 'bytes': len(raw), 'sha256': sha(raw)}


def validate_pin(value, expected=None):
    assert type(value) is dict
    path = Path(value['path']).resolve()
    assert not Path(value['path']).is_symlink()
    raw = path.read_bytes()
    assert len(raw) == value['bytes'] and sha(raw) == value['sha256'], str(path)
    if expected is not None:
        assert path == Path(expected).resolve(), (path,expected)
    return raw


def source_map():
    return {p.relative_to(ROOT).as_posix(): sha(p.read_bytes())
            for folder in ('rouge','tests','scripts') for p in sorted((ROOT/folder).rglob('*'))
            if p.is_file() and p.suffix in ('.py','.json') and '__pycache__' not in p.parts}


def assignment(raw, name):
    rows = [n for n in ast.parse(raw).body if isinstance(n,ast.Assign)
            and any(isinstance(t,ast.Name) and t.id == name for t in n.targets)]
    assert len(rows) == 1
    return ast.literal_eval(rows[0].value)


def summary(value):
    names = ('tests_run','tests_passed','skipped','unavailable_parent_count','failures','errors')
    out = {key:value[key] for key in names}
    out['unavailable_records'] = len(value['unavailable'])
    return out


def distinct_runner_compatibility(gold_source,candidate_source,gold_raw,gold_guard_raw,primary):
    """Read-only exact metadata inverse; no execution or rewritten old Gold."""
    assert len(gold_source) == 39470 and sha(gold_source) == GOLD_RUNNER_SHA
    assert len(candidate_source) == 43210 and sha(candidate_source) == CANDIDATE_RUNNER_SHA
    recovered = candidate_source
    for tag,indent in (('01',''),('02','    '),('03','        '),('04','    ')):
        begin = (indent+'# BEGIN107_META_'+tag+'\n').encode()
        end = (indent+'# END107_META_'+tag+'\n').encode()
        assert recovered.count(begin) == recovered.count(end) == 1
        first = recovered.index(begin)
        last = recovered.index(end,first)+len(end)
        recovered = recovered[:first]+recovered[last:]
    for newer,older in [
        (("TEST_SHA='"+NEW_TEST_SHA+"'\n").encode(),("TEST_SHA='"+OLD_TEST_SHA+"'\n").encode()),
        (b"gold['runner_sha256']==GOLD_RUNNER_SHA and gold['original_receipt_sha256']==ORIGINAL_SHA",
         b"gold['runner_sha256']==sha(Path(__file__).read_bytes()) and gold['original_receipt_sha256']==ORIGINAL_SHA")]:
        assert recovered.count(newer) == 1
        recovered = recovered.replace(newer,older,1)
    assert recovered == gold_source and sha(recovered) == GOLD_RUNNER_SHA
    assert primary == b'0\n' and sha(gold_raw) == GOLD_RECEIPT_SHA
    return {'kind':'ROOT107_METADATA_ONLY_GOLD_ADMISSION_V1',
            'Gold_runner_sha256':GOLD_RUNNER_SHA,'candidate_runner_sha256':CANDIDATE_RUNNER_SHA,
            'legacy_Gold_receipt_sha256':sha(gold_raw),
            'legacy_Gold_source_guard_sha256':sha(gold_guard_raw),
            'legacy_Gold_primary_sha256':sha(primary),
            'functional_source_inverse_sha256':sha(recovered),'candidate_test_sha256':NEW_TEST_SHA,
            'legacy_Gold_source_count':749,'candidate_source_count':750,
            'legacy_Gold_contains_107_test':False,'Window_imports_107_test':False,
            'old_and_new_runners_are_identical':False,'legacy_Gold_values_rewritten':False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    required = ('runner','gold-runner','saved-source','saved-bindings','apply-exit',
                'test-repair-exit','source-guard','related-linux','related-linux-exit',
                'related-wine','related-wine-exit','candidate-api-dir','candidate-api-exit')
    for name in required:
        parser.add_argument('--'+name,required=True)
    args = parser.parse_args()
    runner_path = Path(args.runner).resolve()
    gold_runner_path = Path(args.gold_runner).resolve()
    saved_source = Path(args.saved_source).resolve()
    bindings_path = Path(args.saved_bindings).resolve()
    apply_exit = Path(args.apply_exit).resolve()
    repair_exit = Path(args.test_repair_exit).resolve()
    guard_path = Path(args.source_guard).resolve()
    candidate_API_dir = Path(args.candidate_api_dir).resolve()
    candidate_API_exit = Path(args.candidate_api_exit).resolve()
    related_paths = {environment:Path(getattr(args,'related_'+environment)).resolve()
                     for environment in ('linux','wine')}
    related_exits = {environment:Path(getattr(args,'related_'+environment+'_exit')).resolve()
                     for environment in ('linux','wine')}
    spec_path = BASE/'root-section107-save-spec-v2.json'
    report_path = BASE/'section107-actual-report-v2.md'
    assert not spec_path.exists() and not report_path.exists()
    supplied_files = [runner_path,gold_runner_path,saved_source,bindings_path,apply_exit,
                      repair_exit,guard_path,candidate_API_exit]+list(related_paths.values())+list(related_exits.values())
    for path in supplied_files:
        assert path.is_file() and not path.is_symlink() and path != ROOT and ROOT not in path.parents
    assert candidate_API_dir.parent == BASE and candidate_API_dir.name.startswith('section107-candidate-weight-actual-')
    assert candidate_API_dir.is_dir() and not candidate_API_dir.is_symlink()
    assert candidate_API_exit == BASE/(candidate_API_dir.name+'.exit-code')
    for environment in ('linux','wine'):
        assert related_paths[environment].parent == BASE
        assert related_paths[environment].name.startswith('resume107-related-'+environment+'-')
        assert related_exits[environment] == related_paths[environment].with_suffix('.exit-code')
    guard_raw = guard_path.read_bytes()
    guard = json.loads(guard_raw)
    assert guard['section'] == 107 and guard['source_count'] == len(guard['source_sha256']) == 750
    assert source_map() == guard['source_sha256']
    assert guard_path == BASE/'resume107-applied-source-v2.json'
    assert guard['status'] == 'ACTUALLY_REPAIRED_TEST_CONTRACT_RUNTIME_PENDING'
    assert guard['test_source_sha256'] == NEW_TEST_SHA
    assert guard['test_repair_prior_guard_sha256'] == OLD_APPLIED_SHA
    assert guard['test_repair_applier_source_sha256'] == TEST_REPAIR_SOURCE_SHA
    assert guard['test_repair_independent_source_review_sha256'] == TEST_REPAIR_REVIEW_SHA
    assert guard['test_repair_method_delta']['old_methods'] == 11
    assert guard['test_repair_method_delta']['new_methods'] == 12
    old_applied_raw = (BASE/'resume107-applied-source-v1.json').read_bytes()
    assert sha(old_applied_raw) == OLD_APPLIED_SHA
    old_applied = json.loads(old_applied_raw)
    assert set(old_applied['source_sha256']) == set(guard['source_sha256'])
    assert {p for p in guard['source_sha256']
            if guard['source_sha256'][p] != old_applied['source_sha256'][p]} == {TEST_PATH}
    assert old_applied['source_sha256'][TEST_PATH] == OLD_TEST_SHA
    assert old_applied['source_additional_sha256'] == guard['source_additional_sha256']
    assert set(guard['source_additional_sha256']) == {'CORE_0.70_VERIFICATION.json'}
    core_raw = (ROOT/'CORE_0.70_VERIFICATION.json').read_bytes()
    assert sha(core_raw) == guard['source_additional_sha256']['CORE_0.70_VERIFICATION.json']
    publication = load('section106-publication-v1.json')
    assert publication['local_HEAD'] == publication['remote_HEAD'] == guard['baseline_HEAD']
    assert publication['local_HEAD'] == '78c982e5f185246e55dca3d73624e23767a40d76'
    assert publication['section'] == 106 and publication['commit_primary_exit'] == publication['push_primary_exit'] == 0
    assert publication['clean'] is True and publication['source_files'] == 749
    checkpoint = json.loads((ROOT/'DEVELOPMENT_CHECKPOINT.json').read_bytes())
    assert checkpoint['completed_sections'] == 106 and checkpoint['next_section'] == 107
    assert checkpoint['full_validation_due'] is False
    closure = json.loads((ROOT/'verification/full-105/closure.json').read_bytes())
    assert checkpoint['last_full_validation'] == checkpoint['current_full105_checkpoint'] == closure
    assert closure['after_section'] == 105 and closure['batch_validation_closed'] is True
    assert checkpoint['next_full_validation_after'] == checkpoint['current_batch_commit_policy']['next_full_validation_after'] == 110
    gold_guard_raw = (BASE/'resume106-applied-source-v1.json').read_bytes()
    old_guard = json.loads(gold_guard_raw)
    assert len(old_guard['source_sha256']) == 749
    assert old_guard['source_additional_sha256'] == guard['source_additional_sha256']
    assert set(guard['source_sha256']) - set(old_guard['source_sha256']) == {TEST_PATH}
    assert not set(old_guard['source_sha256']) - set(guard['source_sha256'])
    assert {key for key in old_guard['source_sha256'] if old_guard['source_sha256'][key] != guard['source_sha256'][key]} == {'rouge/operator_engine.py','scripts/verify_cloud.py'}
    assert set(guard['changed_paths']) == {'rouge/operator_engine.py','scripts/verify_cloud.py',TEST_PATH}
    modules = assignment((ROOT/'scripts/verify_cloud.py').read_bytes(),'MODULES')
    full_raw = (ROOT/'scripts/verify_full_available.py').read_bytes()
    extra = assignment(full_raw,'NEW_MODULES')
    assert len(modules) == 118 and modules.count(SELECTOR) == 1 and len(extra) == 41
    assert sha(full_raw) == old_guard['source_sha256']['scripts/verify_full_available.py']
    selectors = list(dict.fromkeys(json.loads(core_raw)['test_modules']+list(extra)+list(modules)))
    assert len(selectors) == 241 and selectors.count(SELECTOR) == 1
    assert guard['full_NEW_MODULES_unchanged'] is True and guard['cloud_selectors_after'] == 118
    assert guard['full_selector_union_after'] == 241
    test_raw = (ROOT/TEST_PATH).read_bytes()
    assert sum(isinstance(n,ast.FunctionDef) and n.name.startswith('test_') for n in ast.walk(ast.parse(test_raw))) == 12
    assert sha(test_raw) == guard['test_source_sha256']

    names = ('resume107-selected-v1.exit-code','resume107-window-gold-v2.exit-code',
             'resume107-window-candidate-v1.exit-code',
             'section107-original-weight-actual-linux-v1.exit-code',
             'root-resume107-saved-audit-v1.exit-code',
             'root-section107-fixture-schema-diagnostic-v1.exit-code',
             'root-section107-empty-diagnostic-v1.exit-code')
    exit_files = [BASE/name for name in names]+[apply_exit,repair_exit,candidate_API_exit]+list(related_exits.values())
    for path in exit_files:
        assert path.read_bytes() == b'0\n', str(path)
    assert sha((BASE/'root-section107-related-v1.py').read_bytes()) == RELATED_SOURCE_SHA
    related = {}
    for environment in ('linux','wine'):
        assert related_paths[environment] != BASE/'resume107-related-linux-v1.json'
        value = json.loads(related_paths[environment].read_bytes())
        assert value['section'] == 107 and value['available_checks_passed'] is True
        assert value['failures'] == value['errors'] == 0 and value['source_drift'] == []
        assert value['source_sha256'] == value['source_after'] == guard['source_sha256']
        assert value['source_additional_sha256'] == value['source_additional_after'] == guard['source_additional_sha256']
        assert value['original_assertions_and_classifier_unchanged'] is True
        assert value['wine_compatibility'] is (environment == 'wine')
        assert value['native_windows_game_chat_verified'] is False and SELECTOR in value['selectors']
        related[environment] = value
    failed_related_raw = (BASE/'resume107-related-linux-v1.json').read_bytes()
    assert sha(failed_related_raw) == FAILED_RELATED_SHA
    assert (BASE/'resume107-related-linux-v1.exit-code').read_bytes() == b'1\n'
    failed_related = json.loads(failed_related_raw)
    assert failed_related['tests_run'] == 222 and failed_related['tests_passed'] == 219
    assert failed_related['available_checks_passed'] is False
    assert failed_related['failures'] == 1 and failed_related['errors'] == 0
    assert failed_related['skipped'] == 1 and failed_related['unavailable_parent_count'] == 1
    assert failed_related['source_sha256'] == failed_related['source_after'] == old_applied['source_sha256']
    assert failed_related['source_drift'] == []
    empty_diagnosis_raw = (BASE/'root-section107-empty-diagnostic-v1.json').read_bytes()
    assert sha(empty_diagnosis_raw) == EMPTY_DIAGNOSIS_SHA
    empty_diagnosis = json.loads(empty_diagnosis_raw)
    assert empty_diagnosis['kind'] == 'ROOT_ACTUAL_107_EMPTY_BOUNDARY_DIAGNOSIS'
    assert len(empty_diagnosis['rows']) == 12
    assert empty_diagnosis['Source_750_CORE_unchanged'] is empty_diagnosis['new_test_failure_preserved'] is True
    assert empty_diagnosis['product_modified'] is False
    lines = (BASE/'resume107-selected-v1.log').read_text().splitlines()
    selected = json.loads(next(line for line in reversed(lines) if line.startswith('{"passed"')))
    assert selected['passed'] is True and selected['failures'] == selected['errors'] == 0

    original_raw = (BASE/'section107-original-weight-actual-linux-v1/observations.json').read_bytes()
    original = json.loads(original_raw)
    assert sha(original_raw) == ORIGINAL_SHA
    candidate_API_raw = (candidate_API_dir/'observations.json').read_bytes()
    candidate_API = json.loads(candidate_API_raw)
    for value, count in ((original,748),(candidate_API,750)):
        assert value['observation_only'] is True and value['product_pass'] is False
        assert value['observation_complete'] is value['source_and_CORE_unchanged'] is True
        assert value['source_before'] == value['source_after'] and len(value['source_before']) == count
        assert value['CORE_before'] == value['CORE_after'] == sha(core_raw)
        assert value['planned_calculation_cases'] == 14 and value['planned_previews'] == 2
        assert value['actual_explicit_consumer_calls'] == 74 and value['actual_explicit_public_loader_calls'] == 1
        assert value['actual_native_records'] == len(value['native_records']) == 89
        assert value['consumer_error_count'] == value['blocked_phase_count'] == 0
    assert candidate_API['source_before'] == guard['source_sha256']
    assert candidate_API['source_guard_sha256'] == sha(guard_raw)

    gold_dir = BASE/'resume107-window-gold-v2'
    candidate_dir = BASE/'resume107-window-candidate-v1'
    gold_raw = (gold_dir/'receipt.json').read_bytes()
    candidate_raw = (candidate_dir/'receipt.json').read_bytes()
    gold,candidate = json.loads(gold_raw),json.loads(candidate_raw)
    runner_raw = runner_path.read_bytes()
    gold_runner_raw = gold_runner_path.read_bytes()
    compile(runner_raw,str(runner_path),'exec')
    compile(gold_runner_raw,str(gold_runner_path),'exec')
    assert sha(gold_runner_raw) == GOLD_RUNNER_SHA and sha(runner_raw) == CANDIDATE_RUNNER_SHA
    assert sha(gold_raw) == GOLD_RECEIPT_SHA
    compatibility = distinct_runner_compatibility(gold_runner_raw,runner_raw,gold_raw,gold_guard_raw,
                                                (BASE/'resume107-window-gold-v2.exit-code').read_bytes())
    assert assignment(runner_raw,'COUNT') == 13
    assert assignment(runner_raw,'ORIGINAL_SHA') == ORIGINAL_SHA
    for phase,value,map_,raw_guard in (('gold',gold,old_guard['source_sha256'],gold_guard_raw),
                                       ('candidate',candidate,guard['source_sha256'],guard_raw)):
        assert value['kind'] == 'ROOT_ACTUAL_107_REAL_MAINWINDOW' and value['phase'] == phase
        assert value['passed'] is value['workflow_complete'] is True
        assert len(value['rows']) == 13 and value['Qt_errors'] == value['source_drift'] == []
        assert value['source_before'] == value['source_after'] == map_
        assert value['source_additional_before'] == value['source_additional_after'] == guard['source_additional_sha256']
        assert value['runner_sha256'] == (GOLD_RUNNER_SHA if phase == 'gold' else CANDIDATE_RUNNER_SHA)
        assert value['source_guard_sha256'] == sha(raw_guard)
        assert value['original_receipt_sha256'] == ORIGINAL_SHA
        assert value['native_windows_verified'] is value['game_chat_sampling_executed'] is value['private_state_access'] is False
        assert all(list(row['snapshots']) == list(PHASES) for row in value['rows'])
    assert guard['window_source_sha256'] == GOLD_RUNNER_SHA  # historical actual Gold, not new candidate
    assert candidate['Gold_runner_compatibility'] == compatibility
    assert 'Gold_runner_compatibility' not in gold
    assert candidate['actual_gold_receipt_sha256'] == sha(gold_raw)
    assert len(gold['pngs']) == 0 and len(candidate['pngs']) == 4

    saved_raw = (BASE/'root-resume107-saved-audit-v1.json').read_bytes()
    saved = json.loads(saved_raw)
    saved_source_raw = saved_source.read_bytes()
    compile(saved_source_raw,str(saved_source),'exec')
    assert saved['kind'] == 'ROOT_ACTUAL_107_PURE_SAVED_READBACK'
    assert saved['passed'] is saved['workflow_complete'] is True
    assert saved['audit_Source_sha256'] == sha(saved_source_raw)
    assert assignment(saved_source_raw,'GOLD_WINDOW') == GOLD_RUNNER_SHA
    assert assignment(saved_source_raw,'CANDIDATE_WINDOW') == CANDIDATE_RUNNER_SHA
    assert assignment(saved_source_raw,'TEST') == NEW_TEST_SHA
    assert saved['Gold_runner_compatibility'] == compatibility
    bindings_raw = bindings_path.read_bytes()
    bindings = json.loads(bindings_raw)
    assert saved['bindings_sha256'] == sha(bindings_raw) and saved['bindings'] == bindings
    assert bindings['kind'] == 'ROOT_ACTUAL107_SAVED_ARTIFACT_BINDINGS_V2' and bindings['actual_runtime_ready'] is True
    expected_bindings = {
        'gold_guard':BASE/'resume106-applied-source-v1.json',
        'candidate_guard':guard_path,
        'gold_receipt':gold_dir/'receipt.json','candidate_receipt':candidate_dir/'receipt.json',
        'gold_primary':BASE/'resume107-window-gold-v2.exit-code',
        'candidate_primary':BASE/'resume107-window-candidate-v1.exit-code',
        'original_receipt':BASE/'section107-original-weight-actual-linux-v1/observations.json',
        'candidate_API_receipt':candidate_API_dir/'observations.json',
        'original_primary':BASE/'section107-original-weight-actual-linux-v1.exit-code',
        'candidate_API_primary':candidate_API_exit,
        'gold_window_runner':gold_runner_path,'candidate_window_runner':runner_path,
        'audit_Source':saved_source,'visual':BASE/'resume107-visual-audit-v1.json',
    }
    for key,path in expected_bindings.items():
        validate_pin(bindings[key],path)
    for value in bindings.values():
        if type(value) is dict and {'path','bytes','sha256'} <= set(value):
            validate_pin(value)
    assert saved['source_before'] == saved['source_after'] == guard['source_sha256'] and saved['source_drift'] == []
    assert saved['source_additional_before'] == saved['source_additional_after'] == guard['source_additional_sha256']
    assert saved['complete_same_input_UI_Gold_points'] == 62 and saved['intended_changed_UI_points'] == 16
    assert len(saved['Gold_points']) == 78 and saved['saved_UI_snapshot_count'] == len(saved['snapshot_checks']) == 156
    assert saved['API_original_and_current_records_checked'] == 178 and saved['API_output_pairs_checked'] == len(saved['API_pair_checks']) == 74
    assert saved['decoded_record_count'] == len(saved['decoded_records']) == 178+len(gold['records'])+len(candidate['records'])
    assert saved['phase_record_counts'] == {'gold':len(gold['records']),'candidate':len(candidate['records'])}
    assert saved['saved_actual_normal_plan_count'] == len(saved['normal_plan_checks']) == gold['actual_captured_normal_plans']+candidate['actual_captured_normal_plans']
    assert saved['actual_close_direct_RunState_count'] == len(saved['restart_checks']) == 26
    assert saved['window_per_UI_step_prepost_saved_verified'] is saved['common_three_formatter_group_prepost_saved_verified'] is True
    assert saved['individual_formatter_prepost_saved_verified'] is saved['cross_separate_freeze_live_alias_verified'] is False
    assert saved['second_MainWindow_reopen_verified'] is saved['natural_OCR_producer_verified'] is saved['native_windows_verified'] is False
    visual = load('resume107-visual-audit-v1.json')
    assert visual['passed'] is visual['workflow_complete'] is True and visual['actually_viewed_images'] == 4
    assert visual['native_windows_game_chat_verified'] is False
    assert len(visual['pngs']) == len(saved['PNG_checks']) == 4
    for png,viewed in zip(candidate['pngs'],visual['pngs']):
        assert all(viewed[key] == value for key,value in png.items()) and viewed['actually_viewed'] is True
        raw = (candidate_dir/png['file']).read_bytes()
        assert raw.startswith(b'\x89PNG\r\n\x1a\n') and len(raw) == png['bytes'] and sha(raw) == png['sha256']

    first_raw = (BASE/'resume107-window-gold-v1/receipt.json').read_bytes()
    first = json.loads(first_raw)
    assert sha(first_raw) == FIRST_GOLD_SHA and (BASE/'resume107-window-gold-v1.exit-code').read_bytes() == b'1\n'
    assert first['passed'] is first['workflow_complete'] is False and len(first['rows']) == 0 and len(first['records']) == 4
    assert first['source_before'] == first['source_after'] == old_guard['source_sha256'] and first['source_drift'] == []
    diagnosis_raw = (BASE/'root-section107-fixture-schema-diagnostic-v1.json').read_bytes()
    diagnosis = json.loads(diagnosis_raw)
    assert sha(diagnosis_raw) == DIAGNOSIS_SHA and diagnosis['passed'] is diagnosis['workflow_complete'] is True
    assert diagnosis['actual_original_validator_calls'] == 26 and diagnosis['actual_old_expected_rejections'] == diagnosis['actual_corrected_qualifications'] == 13
    assert diagnosis['source_sha256'] == old_guard['source_sha256'] and diagnosis['source_drift'] == []
    assert source_map() == guard['source_sha256'] and (ROOT/'CORE_0.70_VERIFICATION.json').read_bytes() == core_raw
    # ALL terminal raw, actual Source/receipt/Saved/view and retained-failure gates
    # precede the first report/spec write. Nothing here writes tracked files.
    stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
    attempts = [
        {'attempt':1,'status':'FAILED_PUBLIC_FIXTURE_NOT_PRODUCT_PASS','primary':1,
         'receipt':pin(BASE/'resume107-window-gold-v1/receipt.json'),'completed_windows':0,
         'native_records':4,'failure':first['failure'],'elapsed_seconds':first['elapsed_seconds']},
        {'attempt':2,'status':'ACTUAL_COMPLETE_GOLD','primary':0,
         'receipt':pin(gold_dir/'receipt.json'),'completed_windows':len(gold['rows']),
         'native_records':len(gold['records']),'elapsed_seconds':gold['elapsed_seconds']},
    ]
    text = (f'既有重力减重派生值与安洁重量天赋共同消费；保留原base校验、signed参考、固定身份、培养、低重和报告边界。12个新增API测试方法（初版11方法中的1个边界预期按真实旧连续行为局部修正并新增独立控制）；'
            f'Linux相关{related["linux"]["tests_run"]}/{related["linux"]["tests_passed"]}PASS/skip{related["linux"]["skipped"]}/U{related["linux"]["unavailable_parent_count"]}父项；'
            f'Wine相关{related["wine"]["tests_run"]}/{related["wine"]["tests_passed"]}PASS/skip{related["wine"]["skipped"]}/U{related["wine"]["unavailable_parent_count"]}父项；'
            f'精选118登记{selected["tests_run"]}运行/skip{selected["skipped"]}，均0失败0错误。'
            f'两次Gold尝试（首次fixture失败原raw1保留），最终13Gold/13候选×6完整快照；62同输入完整Gold点、16有意变化按原manual完整components/estimate.skill及旧fixedmetadata核对；'
            f'{saved["decoded_record_count"]}Saved原件、26实际close后JSON加载、四图已看；Source750+CORE不漂移。'
            'S1/S2无实际normal调用，仅S3实际原plan；未验证新floor/stacking/绝对gamephase、逐formatter独立prepost、跨分freeze alias、二次MainWindow、自然OCR或原生Windows/游戏/聊天。')
    report = f'''# 第107节派生重量与天赋共同消费

{stamp}（北京时间）。本报告只在全部实际raw0、完整Source守恒、Saved读回和Root四图查看成功后生成；随本节真实提交推送，自身未来commit hash不虚构。

{ text }

原公开API观察仍是748 Source、14caller+2preview、74显式消费者/1原catalog getter/89native。候选750 Source的同组观察原件也保留89native、0消费者错误/blocked；两份都标observation-only/product_passFalse，是否修复由独立Saved原/候选74调用配对证明，不能把观察运行本身计产品PASS。

新增测试初次Linux相关实际222运行/219PASS/skip1/U1父项/1失败0错误/raw1，失败原件完整封存。Root随后实际12调用诊断确认连续参考并不消费空target_windows，而frames空范围及两类零边界保持0。仅该新增测试从11至12方法：10旧方法字节保留、1方法保所有合法零边界和四个原断言、1独立连续参考方法完整比较返回值（只在先断言False/True之后对齐既有timing.scenario_provided输入标记）。产品timing/计算/registry没有改动；修正独审及test-only applier、前后750 guard、失败与原诊断都存档。报告的最终相关成功来自fresh实际receipt，不将首次失败覆盖或计PASS。

只有engine原base option校验之后、既有天赋阈值之前，对局部weight加原relics.prepare已生成的signed weight_delta一次。原caller/场景baseweight、固定身份优先、原低重量与负参考、培养资格、其他干员输出、报告/preview producer均保持原合同。没有增加游戏下限、不同物品叠加法则、位移模型或新起飞/结束时钟。

第一次Gold真实失败：{first['elapsed_seconds']}秒，raw1、0完成窗口/4native，原保存资格正确拒绝缺config.zone.name的fixture。Root原validator对13旧fixture+13仅补publicname版本实际26次诊断：13原拒绝、13修正合格且输入守恒。Source v1/v2/v3与独审、首次失败全部封存；当前是第二次真实Gold最终成功，Source v3不是第三次实际尝试，未放宽产品validator或原断言。

原真实健康Gold runner976保持不变，候选runner9ab独立SHA明确不同；四个元数据块和两处精确替换剥离后全字节恢复976。只放行这组已通过Source749、无107test导入的原Gold；旧Gold值和失败证据未重写，不能称新旧runner同SHA。

最终Gold：{len(gold['rows'])}窗口/{len(gold['records'])}native/{gold['actual_numeric_calls']}实际原numeric调用/{gold['actual_captured_normal_plans']}实际原normal调用/{gold['elapsed_seconds']}秒。候选：{len(candidate['rows'])}窗口/{len(candidate['records'])}native/{candidate['actual_numeric_calls']}实际numeric/{candidate['actual_captured_normal_plans']}实际normal/{candidate['elapsed_seconds']}秒。每窗口六个最终快照；S1/S2原调用路径捕获0 normal，只有S3可达原plan被记录，不把空normal列表冒称执行或完整gamephase。正常分支与changed oracle均用真实原调用返回，无伪计算。

Saved实际解码{saved['decoded_record_count']}原件：API原/候选178条、74完整消费者配对，其中{saved['API_intended_changed_consumer_pairs']}项有意变化/{saved['API_complete_unchanged_consumer_pairs']}项原输出完整保持；窗口{saved['saved_UI_snapshot_count']}快照、{saved['saved_UI_group_count']}共同UI prepost、{saved['saved_common_formatter_group_count']}共同三formatter组prepost、{saved['saved_actual_normal_plan_count']}真实normal原件、62完整同输入Gold/16原manual oracle变化点、26 close后直接RunState加载实际保存JSON整图。变化点保原fixed metadata和全盘，不把旧缺陷fixed结果作必须相等的oracle。

四候选PNG由Root实际打开并绑定该candidate receipt和Saved。窗口每步共同state/disks和共同三formatter组已保存可读回；每一个formatter独立prepost、跨分freeze live alias没有证明。JSON不保证原内存别名；没有第二MainWindow重开、自然OCR、原生Windows、游戏或聊天验收。

精选仅prepend107至118；原full helper和NEW41全字节保留，真实full main自动union cloud后241。相关Linux/Wine仍原AvailableResult分类，原skip/不可用父项与记录保留、不计PASS。精选原断言未改；本节不重复105全量，last_full105和旧95三次deferred保持，下一五节全量110。

其余P2/P3项目继续依据PROJECT_PROGRESS原待办和已证实公开资料推进；本节没有替未知机制补公式。归档后真正commit/push，CP更新107/next108、dueFalse、nextfull110；108区域输入工作仍需先真实原API观察、Source审阅和独立实际验收，不提前计完成。
'''
    entries = []
    for path in sorted(BASE.iterdir()):
        if path.name.startswith('section107-'):
            entries.append({'source':str(path),'destination':'public107/'+path.name})
        elif path.name.startswith('resume107-'):
            entries.append({'source':str(path),'destination':'actual107/'+path.name})
        elif path.name.startswith(('root-section107-','root-resume107-')):
            entries.append({'source':str(path),'destination':'actual-root-evidence/'+path.name})
    entries.extend([
        {'source':str(BASE/'root-live-recovery-section107.json'),'destination':'actual-root-evidence/root-live-recovery-section107.json'},
        {'source':str(BASE/'section106-publication-v1.json'),'destination':'prior-publication.json'},
        {'source':str(runner_path),'destination':'actual-final-window-Source/window107.py'},
        {'source':str(gold_runner_path),'destination':'actual-final-window-Source/legacy-gold-window107.py'},
        {'source':str(saved_source),'destination':'actual-final-Saved-Source/audit107.py'},
        {'source':str(bindings_path),'destination':'actual-root-evidence/final-saved-bindings.json'},
        {'source':str(apply_exit),'destination':'actual-root-evidence/actual-apply.exit-code'},
        {'source':str(repair_exit),'destination':'actual-root-evidence/actual-testrepair.exit-code'},
        {'source':str(guard_path),'destination':'actual-root-evidence/final-source-guard.json'},
        {'source':str(candidate_API_dir),'destination':'actual107/final-candidate-API'},
        {'source':str(candidate_API_exit),'destination':'actual-root-evidence/final-candidate-API.exit-code'},
        *({'source':str(related_paths[env]),'destination':'actual-root-evidence/final-related-'+env+'.json'} for env in ('linux','wine')),
        *({'source':str(related_exits[env]),'destination':'actual-root-evidence/final-related-'+env+'.exit-code'} for env in ('linux','wine')),
        {'source':str(Path(__file__).resolve()),'destination':'actual-root-evidence/root-section107-spec-builder-v1.py'},
        {'source':str(report_path),'destination':'REPORT_ZH.md'},
    ])
    receipt = {
        'implemented_scope':['Same prepared signed weight delta consumed by existing qualified AG talent','Original base validation and producer/report scope preserved','Actual original manual-light oracle and saved-state validation'],
        'new_test_methods':12,'related_linux':summary(related['linux']),'related_wine':summary(related['wine']),
        'preserved_failed_related_linux':summary(failed_related),
        'preserved_failed_related_linux_primary':1,'test_contract_repair_actual_diagnosis_calls':12,
        'test_repair_product_or_timing_changed':False,
        'actual_distinct_window_runner_compatibility':compatibility,
        'selected_tests':selected,'Gold_attempts':attempts,'Gold_windows':len(gold['rows']),
        'candidate_windows':len(candidate['rows']),'Gold_native':len(gold['records']),
        'candidate_native':len(candidate['records']),'API_original_native':89,'API_candidate_native':89,
        'Gold_actual_numeric_calls':gold['actual_numeric_calls'],'candidate_actual_numeric_calls':candidate['actual_numeric_calls'],
        'Gold_actual_normal_plan_calls':gold['actual_captured_normal_plans'],
        'candidate_actual_normal_plan_calls':candidate['actual_captured_normal_plans'],
        'Saved_decoded_records':saved['decoded_record_count'],'Saved_UI_snapshots':saved['saved_UI_snapshot_count'],
        'complete_same_input_UI_Gold_points':62,'intended_changed_UI_points':16,
        'actual_close_direct_RunState_records':saved['actual_close_direct_RunState_count'],
        'four_pngs_actually_viewed':True,'new_source_files':1,'source_count':750,
        'cloud_selectors':118,'full_NEW_MODULES_unchanged':True,'full_union_selectors':241,
        'window_per_UI_step_prepost_saved_verified':True,'common_three_formatter_group_prepost_saved_verified':True,
        'individual_formatter_prepost_saved_verified':False,'cross_separate_freeze_live_alias_verified':False,
        'new_game_floor_stacking_phase_verified':False,'native_windows_game_chat_verified':False,
        'full095_deferred_preserved':True,'last_full_validation_preserved_after_section':105,
        'next_full_validation_after':110,'actual_final_window_runner':pin(runner_path),'actual_historical_Gold_runner':pin(gold_runner_path),
        'actual_final_Saved_Source':pin(saved_source),'actual_Saved_receipt':pin(BASE/'root-resume107-saved-audit-v1.json'),
        'actual_Saved_bindings':pin(bindings_path),
    }
    spec = {'section':107,'topic':'派生重量与天赋共同消费',
        'archive':'research/p2-section107-effective-enemy-weight',
        'source_guard':str(guard_path),
        'exit_files':[str(path) for path in exit_files],
        'pass_receipts':[str(BASE/'root-resume107-saved-audit-v1.json'),str(BASE/'resume107-visual-audit-v1.json')],
        'public_evidence':entries,'previous_publication':str(BASE/'section106-publication-v1.json'),
        'next_action':'107实际commit/push后依序108已证实区域输入工作；每节真实检验/保存，110后全量和进度总结；lastfull105及95deferred保留，未知floor/stacking/gamephase不编造。',
        'archive_readme':'# 第107节派生重量与天赋共同消费\n\n实际范围与局限见REPORT_ZH.md。首次Gold raw1/4native、首次相关Linux raw1/222运行/1失败、Source v1/v2/v3/v4与两组Root诊断原件保留；后续真实原件由manifest逐项SHA核对。Source-only准备不计Runtime/小节、原观察product_passFalse不冒称PASS。',
        'section_receipt':receipt,'completed_paragraph':text,
        'work_paragraph':text+' 当前归档后真实commit/push，随后依序108；下次110全量和进度总结。'}
    # No tracked writes or publish calls. Root's separate saver/publisher owns them.
    with report_path.open('x',encoding='utf-8') as stream:
        stream.write(report)
    with spec_path.open('x',encoding='utf-8') as stream:
        json.dump(spec,stream,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps({'spec':str(spec_path),'public_entries':len(entries),'source_files':750}))


if __name__ == '__main__':
    main()
