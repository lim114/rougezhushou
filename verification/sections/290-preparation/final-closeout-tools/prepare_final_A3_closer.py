"""Prepare a separate unexecuted v5 closeout; write cache UTF8 bytes only."""
import ast
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OLD_SHA = 'be1938afe5e1f0ea3877dd34af2467b3732be24c51e816754dbf0e20656cfc5e'


def main():
    old = ROOT / '.cache/close_section_290.py'
    target = ROOT / '.cache/close_section_290_final_A3.py'
    raw = old.read_bytes()
    if sha256(raw).hexdigest() != OLD_SHA or target.exists():
        raise ValueError('Preserved old helper and fresh final helper required')
    text = raw.decode('utf8')
    def replace(before, after):
        nonlocal text
        if text.count(before) != 1:
            raise ValueError('Unique original closer anchor required: ' + before[:90])
        text = text.replace(before, after, 1)
    replace('"""Prepared290 closeout.', '"""Prepared finalA3/new legacy4/A2 GUI composition290 closeout.')
    replace('import json\n', 'import json\nimport importlib.util\n')
    replace("TERM_SENTENCE = '初次招募时即处于已进阶状态'", """TERM_SENTENCE = '初次招募时即处于已进阶状态'
PROOF_PATH = 'verification/full-290/composite-admissibility.json'
FINAL_BUILDER_SHA = '__FINAL_BUILDER_SHA__'
FINAL_FREEZE_SHA = 'ad3842c95c4a4eadb6779611a337fbeb26c2682a25d6ed83945dcf7a0a8d65f7'
A2_FREEZE_SHA = '75cec266144a389b93aced04d150c4cf6e72a23403f250a9caab9915543e6ec0'""")
    gate = '''
def gate_final_composition(full, parent):
    require(full['actual_validation_attempt'] == 3
            and full['all_historical_source_maps_same_freeze'] is False
            and full['new_offline_and_legacy_share_one_final_freeze'] is True
            and full['A2_GUI_ran_final_complete_source'] is False,
            'new finalA3 offline/legacy4 and historical A2 current/P3 explicitly separate')
    proof = load(PROOF_PATH)
    require(full['composite_admissibility']['receipt'] == PROOF_PATH
            and full['composite_admissibility']['sha256'] == digest(ROOT / PROOF_PATH)
            and proof['kind'] == 'FULL290_FINAL_A3_COMPONENT_COMPOSITION_PROOF'
            and proof['complete_available_components_passed'] is True
            and proof['complete_repository_validation'] is False and proof['P2_complete'] is False
            and proof['all_historical_source_maps_same_freeze'] is False
            and proof['A2_GUI_ran_final_complete_source'] is False,
            'root-reviewed formal strict final composition proof')
    source = ROOT / '.cache/p3-full290-summary-prep/build_final_A3_summary_candidate.py'
    require(proof['builder_sha256'] == FINAL_BUILDER_SHA == digest(source), 'reviewed final builder actual bytes')
    module = importlib.util.module_from_spec(importlib.util.spec_from_file_location('_close290_final_reader', source))
    exec(compile(source.read_bytes(), str(source), 'exec'), module.__dict__)
    safe_helpers = module.fresh_module(ROOT / '.cache/p3-full290-summary-prep/build_summary_candidate.py',
            '_close290_preserved_read_helpers', module.OLD_HELPERS_SHA)
    frozen, old, metadata, activation = module.source_contract(safe_helpers)
    require(digest(ROOT / full['source_freeze']) == full['source_freeze_sha256'] == FINAL_FREEZE_SHA
            and frozen['parent_commit'] == parent and frozen['actual_validation_attempt'] == 3,
            'exact final tested parent/full/native/supplemental source maps and actual binding')
    require(full['exact_two_nonproduction_source_changes'] == proof['exact_two_nonproduction_source_changes'] == module.CHANGES
            and proof['unchanged_full_sources'] == 1219,
            'two exact test/terminal-metadata changes, all other1219 unchanged; not only-test')
    expected_components = {
        'offline3': {'path': full['source_freeze'], 'sha256': FINAL_FREEZE_SHA},
        'legacy4_and_original_typed': {'path': full['source_freeze'], 'sha256': FINAL_FREEZE_SHA},
        'A2_current_and_P3': {'path': 'verification/full-290/source-freeze-repair.json', 'sha256': A2_FREEZE_SHA}}
    require(full['component_freezes'] == proof['component_freezes'] == expected_components
            and proof['offline_actual_exit'] == proof['legacy4_actual_exit'] == proof['legacy_original_typed_actual_exit'] == 0,
            'all final actual successes plus explicitly historical A2 GUI component')
    require(proof['raw_archive_manifests_sha256'] == full['archive_manifests_sha256'], 'proof and summary bind same exact raw archives')
    expected_archives = {f'verification/full-290/{name}/archive-manifest.json' for name in (
        'execution-attempt1', 'p3-supplementary-attempt1', 'execution-attempt2', 'p3-supplementary-attempt2',
        'legacy-retry-attempt3-failed', 'legacy-retry-attempt3-failed-correction', 'offline-attempt3', 'legacy-retry-attempt4')}
    require(set(proof['raw_archive_manifests_sha256']) == expected_archives, 'all original failures/correction and two final archives retained')
    for name, expected in proof['raw_archive_manifests_sha256'].items():
        require(digest(ROOT / name) == expected, 'actual archived manifest identity')
        verify_manifest((ROOT / name).parent, load(name))
    require(full['legacy_window']['actual_legacy_execution_ordinal'] == 4
            and full['legacy_window']['component_source_freeze_sha256'] == FINAL_FREEZE_SHA
            and full['current_window']['actual_execution_attempt'] == 2
            and full['current_window']['component_source_freeze_sha256'] == A2_FREEZE_SHA
            and all(row['actual_execution_attempt'] == 2 and row['component_source_freeze_sha256'] == A2_FREEZE_SHA
                    for row in full['p3_supplementary_windows'].values()), 'actual legacy4 versus A2 current/P3 identities')
    fresh15 = frozen['necessary_module_check']
    require(proof['fresh_necessary15'] == full['fresh_necessary_module'] == fresh15
            and fresh15['actual_process_exit'] == 0 and fresh15['actual_tests_run'] == 15
            and digest(ROOT / fresh15['public_receipt_relative']) == fresh15['receipt_sha256'],
            'fresh final-source15 module original receipt, never added to old15')
    single = load(fresh15['public_receipt_relative'])
    require(single['exit_code'] == 0 and single['source_unchanged'] is True
            and single['source_sha256_before'] == single['source_sha256_after'], 'actual fresh necessary source stability')
    for name, expected in single['source_sha256_after'].items():
        require(digest(ROOT / name) == expected, 'fresh15 declared current source')
    for review in proof['root_visual_reviews']:
        require(digest(ROOT / review['path']) == review['sha256'], 'actual root component PNG review exact bytes')
    return frozen, proof, module.CHANGES, fresh15


'''
    replace('def main(apply):\n', gate + 'def main(apply):\n')
    replace("    frozen = load(full['source_freeze'])\n    require(digest(ROOT / full['source_freeze']) == full['source_freeze_sha256']\n            and frozen['actual_validation_attempt'] == 2, 'actual repaired attempt2 source freeze')",
            '    frozen, proof, approved_changes, fresh15 = gate_final_composition(full, parent)')
    replace("        require(necessary['source_sha256_before'][name] == expected and digest(ROOT / name) == expected,\n                'necessary46 own exact source: ' + name)",
        "        require(necessary['source_sha256_before'][name] == expected, 'historical necessary46 own unchanged source')\n"
        "        current_expected = approved_changes[name]['new_sha256'] if name in approved_changes and expected == approved_changes[name]['old_sha256'] else expected\n"
        "        require(digest(ROOT / name) == current_expected, 'necessary46 production source unchanged except declared two nonproduction inputs: ' + name)")
    replace("             'tests/test_choice_recruitment_integration_290.py', *migration_ready['live_test_files_sha256']]",
        "             'tests/test_choice_recruitment_integration_290.py', 'tests/test_enemy_sp_inheritance_reference.py', *migration_ready['live_test_files_sha256']]")
    replace("              'A1超时及诊断/准备失败保留；新修复仅按其真实源码与A2完整范围回执认定，不倒填原A1失败ID。',",
        "              'A1/A2离线超时、A2旧窗口内部1200超时、retry3原生崩溃与追加事实更正保留；新结果按finalA3与A2两处精确非生产差异组合，不倒填原失败。',")
    replace("            'counts_kept_separate_not_summed': True, 'author25_subset_not_added': True},",
        "            'fresh_final15_module': fresh15, 'old15_not_added_to_fresh15': True,\n            'counts_kept_separate_not_summed': True, 'author25_subset_not_added': True},")
    replace("            'actual_validation_attempt': 2, 'offline': full['offline_windows'],",
        "            'actual_validation_attempt': 3, 'actual_legacy_execution_ordinal': 4, 'offline': full['offline_windows'],\n"
        "            'component_freezes': full['component_freezes'], 'all_historical_source_maps_same_freeze': False,\n"
        "            'composite_proof': PROOF_PATH, 'composite_proof_sha256': digest(ROOT / PROOF_PATH),\n"
        "            'exact_two_nonproduction_source_changes': approved_changes,")
    replace("        'limits': limits, 'next_section': 291, 'cloud_publication_binding': 'enclosing_commit'}",
        "        'validation_maintenance': {'same_functional_section': True, 'production_numerical_change_for_runtime_repair': False,\n"
        "            'details': '计时工具与非WMI报告元数据维护；保留862/552原流程、选择器及实际范围，不证明原崩溃根因。'},\n"
        "        'limits': limits, 'next_section': 291, 'cloud_publication_binding': 'enclosing_commit'}")
    replace("        'unresolved_available_failures': False, 'original_failed_attempts_preserved': True}",
        "        'unresolved_available_failures': False, 'original_failed_attempts_preserved': True,\n"
        "        'component_freezes': full['component_freezes'], 'all_historical_source_maps_same_freeze': False,\n"
        "        'composite_proof': PROOF_PATH, 'actual_offline_attempt': 3, 'actual_legacy_ordinal': 4, 'reused_current_P3_attempt': 2}")
    replace("        'available_scope_passed': True, 'native_windows_game_chat_verified': False}",
        "        'available_scope_passed': True, 'native_windows_game_chat_verified': False, 'composite_proof': PROOF_PATH,\n"
        "        'actual_offline_attempt': 3, 'actual_legacy_ordinal': 4, 'reused_current_P3_attempt': 2}")
    replace("        'native_isolated_window_checks': window['unique_checks'], 'full_suite_rerun': True, 'full_receipt': FULL_PATH}",
        "        'native_isolated_window_checks': window['unique_checks'], 'full_suite_rerun': True, 'full_receipt': FULL_PATH,\n"
        "        'fresh_final_source_module_methods': 15, 'old15_not_added': True, 'composite_proof': PROOF_PATH}")
    replace("canonical290 {window['unique_checks']} checks; full complete available scope and original visible responsive window, private5 unchanged",
        "canonical290 A2 {window['unique_checks']} checks; finalA3 full offline + legacy4/typed plus A2 current/P3 exact two nonproduction-input equivalence, original visible responsive window, private5 unchanged")
    replace("        f\"最终真实Windows两页{window['unique_checks']}检查通过，原项目测试窗口正常重启、可见响应并置前，5私人路径未变。\"",
        "        f\"fresh finalA3源15项模块另行通过且不叠加旧15；最终真实Windows两页A2 {window['unique_checks']}检查保留，原项目测试窗口正常重启、可见响应并置前，5私人路径未变。\"")
    replace("        '原30项真实1314失败仍不可用，A1超时与原始失败保留。'",
        "        '新offline3与legacy4/原typed共享finalA3冻结；current/P3仍是A2，明确两处非生产输入差异，未声称同一次运行全部通过。原30项1314、A1/A2超时与retry3崩溃/事实更正保留。'")
    replace("        + f'完整可用范围{FULL_PATH}通过；实际符号链接1314、Linux/Wine/原Windows私样本及游戏聊天不计通过。'",
        "        + f'完整可用范围{FULL_PATH}以新finalA3 offline3+legacy4/typed及原A2 current/P3两处精确非生产输入差异组合通过，历史并非同freeze；实际符号链接1314、Linux/Wine/原Windows私样本及游戏聊天不计通过。'")
    replace("        + '25/57原入口、本次实际选择/费用/具体培养/领取仍待证；直升术语本身已查证，不列为未知。'",
        "        + 'finalA3新完整离线与legacy4/typed及A2 current/P3按两处精确非生产输入差异组合，原失败及事实更正保留。'\n"
        "        + '25/57原入口、本次实际选择/费用/具体培养/领取仍待证；直升术语本身已查证，不列为未知。'")
    replace("    tool_sources = ['.cache/close_section_290.py', '.cache/run_section_290_repair_necessary.py',",
        "    tool_sources = ['.cache/close_section_290.py', '.cache/close_section_290_final_A3.py',\n"
        "        '.cache/p3-full290-summary-prep/build_final_A3_summary_candidate.py',\n"
        "        '.cache/p3-full290-summary-prep/prepare_final_A3_closer.py',\n"
        "        '.cache/p3-full290-summary-prep/component_visual_reviews.py',\n"
        "        '.cache/p3-full290-summary-prep/FINAL_A3_CONTRACT.md',\n"
        "        '.cache/run_section_290_repair_necessary.py',")
    text = text.replace('__FINAL_BUILDER_SHA__', sha256((HERE / 'build_final_A3_summary_candidate.py').read_bytes()).hexdigest())
    ast.parse(text)
    target.write_bytes(text.encode('utf8'))
    if sha256(old.read_bytes()).hexdigest() != OLD_SHA:
        raise ValueError('Old closeout helper changed')
    print('UNEXECUTED_CACHE_FINAL_CLOSER', sha256(target.read_bytes()).hexdigest())


if __name__ == '__main__':
    main()
