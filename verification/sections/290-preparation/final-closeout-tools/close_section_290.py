"""Prepared290 closeout. Do not execute before root approves final actual gates.

Default is preview AFTER all evidence gates, with no writes. --apply explicitly
writes only public section/CP/docs and an allowlisted public-tools archive.
This script never runs tests, restarts a window, publishes Git, reads private
configuration/state, or invents an unavailable validation result.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone, timedelta
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
FULL_PATH = 'verification/full-290/summary.json'
SECTION = 290
PREP = ROOT / 'verification/sections/290-preparation'
EVIDENCE = PREP / 'supplementary-public-evidence'
TITLE = '临时中介所四种招募结果、出现条件区分与完整可用范围复验'
TERM_SENTENCE = '初次招募时即处于已进阶状态'


def require(value, description):
    if value is not True:
        raise ValueError('290 closeout prerequisite: ' + description)


def regular(path):
    require(path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(ROOT), 'public regular file: ' + str(path))
    return path


def load(name):
    return json.loads(regular(ROOT / name).read_bytes())


def digest(path):
    return sha256(regular(path).read_bytes()).hexdigest()


def encode(data):
    return (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf8')


def verify_manifest(folder, manifest):
    for name, entry in manifest['files'].items():
        rel = Path(name)
        require(not rel.is_absolute() and '..' not in rel.parts and '\\' not in name, 'safe public manifest member')
        path = regular(folder / rel)
        require(path.resolve().is_relative_to(folder.resolve()) and digest(path) == entry['sha256']
                and path.stat().st_size == entry['bytes'], 'public archived exact bytes: ' + name)


def main(apply):
    branch = subprocess.check_output(['git', 'branch', '--show-current'], cwd=ROOT, text=True).strip()
    parent = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    require(branch == 'codex/p2-development', 'authorized development branch')
    require(not (ROOT / 'verification/sections/290.json').exists(), 'never overwrite a completed section receipt')
    full = load(FULL_PATH)
    require(full['after_section'] == SECTION and full['available_checks_passed'] is True
            and full['scope_not_reduced'] is True and full['complete_repository_validation'] is False
            and full['P2_complete'] is False and not full.get('candidate_only_not_publicly_published', False),
            'root-reviewed public full summary, not cache candidate')
    require(full['source_files'] == 1221 and full['maintained_selectors'] == 430
            and full['supplemental_public_input_files'] == 42 and full['source_drift'] == []
            and full['tested_worktree_parent_commit'] == parent, 'actual1221/430/42 complete current frozen scope')
    frozen = load(full['source_freeze'])
    require(digest(ROOT / full['source_freeze']) == full['source_freeze_sha256']
            and frozen['actual_validation_attempt'] == 2, 'actual repaired attempt2 source freeze')
    for name, expected in {**frozen['source_sha256'], **frozen['supplemental_public_inputs_sha256']}.items():
        require(digest(ROOT / name) == expected, 'current exact full-validated source: ' + name)
    legacy = full['legacy_window']
    require(legacy['passed'] is True and legacy['typed_readback_verified'] is True
            and legacy['formal_typed_readback_actual_exit'] == 0 and legacy['saved_states'] == 52
            and legacy['runtime_check_records'] == 4283 and legacy['current_assertion_AST_and_order'] == 862
            and legacy['original_maintry_checks'] == 552, 'complete actual legacy52/typed/862/552')
    p3 = full['p3_supplementary_windows']
    require(set(p3) == {'286', '287', '288', '289', '290'}
            and all(row['passed'] is True and row['actual_child_and_supervisor_exit'] == 0 for row in p3.values())
            and p3['290']['unique_check_labels'] == 70, 'all five actual supplementary windows, final29070')
    window = load(p3['290']['receipt'])
    require(window['passed'] is True and window['unique_checks'] == 70 and window['qpa'] == 'windows'
            and window['verification_window_closed'] is True, 'canonical final actual290 window')
    native = load('verification/sections/290-main-window.json')
    require(native['passed'] is True and native['private_file_hash_comparison_count'] == 5
            and native['private_hashes_equal'] is True and native['changed_private_paths'] == []
            and native['no_private_restoration'] is True and native['private_contents_parsed_copied_or_restored'] is False,
            'actual original project normal restart with private5 unchanged')
    require(len(native['visible_windows']) == 1 and native['visible_windows'][0]['visible'] is True
            and native['visible_windows'][0]['responding'] is True
            and native['visible_windows'][0]['minimized'] is False, 'one responsive visible original project window')
    focus = load('verification/sections/290-main-window-focus.json')
    require(focus['visible'] is True and focus['actual_foreground'] == focus['hwnd'] == native['visible_windows'][0]['hwnd'],
            'actual original test window foreground receipt')
    necessary = load('verification/sections/290-necessary-repair/process.json')
    log = regular(ROOT / 'verification/sections/290-necessary-repair/stderr.txt').read_text(encoding='utf8')
    ran = re.search(r'Ran (\d+) tests in', log)
    require(necessary['exit_code'] == 0 and necessary['source_unchanged'] is True and ran is not None
            and int(ran[1]) == 46 and log.rstrip().endswith('OK'), 'actual repaired46 necessary checks')
    for name, expected in necessary['source_sha256_after'].items():
        require(necessary['source_sha256_before'][name] == expected and digest(ROOT / name) == expected,
                'necessary46 own exact source: ' + name)
    migration_dir = EVIDENCE / 'presentation-migration'
    migration = json.loads(regular(migration_dir / 'attempt2/first-run.json').read_bytes())
    migration_ready = json.loads(regular(migration_dir / 'READY.json').read_bytes())
    migration_controller = json.loads(regular(migration_dir / 'attempt2/first-controller.json').read_bytes())
    require(migration['actual_successful'] is True and migration['actual_tests_run'] == migration['actual_passed_count'] == 69
            and migration['actual_failures'] == migration['actual_errors'] == migration['actual_unavailable'] == []
            and migration['source_unchanged_during_run'] is True and migration['safety_events'] == [],
            'actual69 display migration checks with original scope')
    require(migration_controller['actual_child_exit'] == migration_controller['controller_exit'] == 0
            and migration_controller['timed_out'] is False and migration_controller['owned_job_no_live_execution_verified'] is True
            and migration['source_sha256'] == migration_controller['worker_source_sha256']
                == digest(migration_dir / 'attempt2/verify_migration.py')
            and migration_controller['source_sha256'] == digest(migration_dir / 'attempt2/run_bounded.py'),
            '69 actual worker/controller source identity, not46 or full counts')
    for name, expected in migration_ready['live_test_files_sha256'].items():
        require(digest(ROOT / name) == expected, 'five migrated current test sources: ' + name)
    integrity = json.loads(regular(EVIDENCE / 'INTEGRITY_CHECK.json').read_bytes())
    require(integrity['hash_or_inventory_mismatches'] == [] and integrity['tests_gui_full_game_chat_private_run'] is False,
            'supplementary archive exact public evidence only')
    verify_manifest(EVIDENCE, integrity)
    for group in integrity['groups']:
        folder = EVIDENCE / group['group']
        require(digest(folder / 'ARCHIVE_MANIFEST.json') == group['manifest_sha256'], 'public group manifest identity')
        verify_manifest(folder, json.loads(regular(folder / 'ARCHIVE_MANIFEST.json').read_bytes()))

    # All public result gates have passed. Construct every document in memory
    # before any write/copy; preserve current semantics rather than numeric edits.
    checkpoint = load('DEVELOPMENT_CHECKPOINT.json')
    require(checkpoint['completed_sections'] == 289 and checkpoint['next_section'] == 290
            and checkpoint['latest_functional_section'] == 289, 'close only actual289→290 continuation')
    require(checkpoint['policy']['full_validation_anchor_section'] == 125
            and checkpoint['policy']['full_validation_interval'] == 15, 'current125 anchor and15 cadence')
    next_full = 125 + ((SECTION - 125) // 15 + 1) * 15
    require(next_full == 305 and (SECTION - 125) % 15 == 0, '290 due full then305, not a continuous stopping target')
    now = datetime.now(timezone(timedelta(hours=8))).isoformat()
    files = ['rouge/choice_recruitment_results.py', 'rouge/data/choice-recruitment-results.json',
             'rouge/event_planning.py', 'rouge/player_node_information.py', 'rouge/node_catalog_view.py',
             'scripts/build_choice_recruitment_results_290.py', 'scripts/verify_recruitment_results_window_290.py',
             'scripts/verify_full_available.py', 'tests/test_choice_recruitment_results_290.py',
             'tests/test_choice_recruitment_integration_290.py', *migration_ready['live_test_files_sha256']]
    scope = ('临时中介所“可靠的中介值得信任”按完整原选项和独立全文列出先锋/近卫、重装/辅助、医疗/狙击、术师/特种四种替代招募结果；'
             '每种资料参考为2希望与1名5星及以下直升干员，直升已查证为初招即已进阶。'
             '仅精确这一条职业说明归入选择后结果，不更改出现资格、原目录或本局状态；四种结果不相加。')
    limits = ['当前实际职业组/选择、具体招募费用、具体培养数值、领取者与领取事实及原入口仍需各自依据。',
              '25个原场景、57个原选项的原入口缺口不减少；来源全文一致不证明当前服务器或实际生成。',
              'P3/P2/P1未完成，识别最后；不提供路线推荐或自动选路。',
              'A1超时及诊断/准备失败保留；新修复仅按其真实源码与A2完整范围回执认定，不倒填原A1失败ID。',
              '实际符号链接1314、Linux/Wine/原Windows私样本及游戏聊天不计通过。']
    receipt = {'section': SECTION, 'kind': 'functional_section', 'title': TITLE, 'at_Beijing': now,
        'branch': branch, 'prior_commit': parent, 'remaining_item': 'P3节点事件的具体招募结果与结果条件说明',
        'new_capability': scope, 'files': files, 'source_sha256': {name: digest(ROOT / name) for name in files},
        'source_evidence': {'packet': 'research/p3-choice-recruitment-290',
            'manifest_sha256': digest(ROOT / 'research/p3-choice-recruitment-290/source-manifest.json'),
            'exact_choice': 'community_group_018:scene:0:choice:1',
            'original_profession_result_records': ['choice_ro6_hire1_1', 'choice_ro6_hire1_4', 'choice_ro6_hire1_5', 'choice_ro6_hire1_6'],
            'independent_document_revision': '349818', 'community_revisions': ['427904', '440271'],
            'remaining_original_scenes': 25, 'remaining_original_choices': 57,
            'original_catalog_and_run_state_changed': False, 'actual_recruitment_or_grants_certified': False,
            'terminology_known': {'直升': '初次招募时即处于已进阶状态'}},
        'necessary_validation': {'receipt': 'verification/sections/290-necessary-repair/process.json',
            'methods_run': int(ran[1]), 'source_unchanged': True,
            'display_migration_receipt': str((migration_dir / 'attempt2/first-run.json').relative_to(ROOT)).replace('\\', '/'),
            'display_methods_run': migration['actual_tests_run'], 'display_methods_passed': migration['actual_passed_count'],
            'counts_kept_separate_not_summed': True, 'author25_subset_not_added': True},
        'native_windows_validation': {'receipt': p3['290']['receipt'], 'unique_checks': window['unique_checks'],
            'original_project_window': 'verification/sections/290-main-window.json',
            'original_window_focus': 'verification/sections/290-main-window-focus.json',
            'normal_restart_private_paths_compared': native['private_file_hash_comparison_count'],
            'normal_restart_private_paths_changed': len(native['changed_private_paths']), 'game_or_chat_verified': False},
        'full_validation': {'receipt': FULL_PATH, 'sha256': digest(ROOT / FULL_PATH),
            'available_checks_passed': full['available_checks_passed'],
            'complete_repository_validation': full['complete_repository_validation'], 'scope_not_reduced': True,
            'actual_validation_attempt': 2, 'offline': full['offline_windows'],
            'legacy_typed_states': legacy['saved_states'], 'p3_supplementary_windows': full['p3_supplementary_windows'],
            'next_periodic_section': next_full, 'cadence_anchor': 125, 'interval': 15},
        'public_supporting_archive': 'verification/sections/290-preparation/supplementary-public-evidence/INTEGRITY_CHECK.json',
        'limits': limits, 'next_section': 291, 'cloud_publication_binding': 'enclosing_commit'}
    historical_keys = ('current_section_save', 'current_section_validation', 'latest_section_environment',
        'latest_functional_section', 'last_full_validation', 'current_available_full_validation',
        'cloud_publication_closeout', 'active_section', 'next_periodic_full_validation_only_if_resumed',
        'current_batch', 'current_batch_commit_policy', 'confirmed_next_stage_direction', 'next_full_validation_after')
    history_key = 'historical_before290_current_pointers'
    require(history_key not in checkpoint, 'never overwrite previous closeout history')
    checkpoint[history_key] = {key: deepcopy(checkpoint[key]) for key in historical_keys if key in checkpoint}
    for key in ('cloud_publication_closeout', 'active_section', 'next_periodic_full_validation_only_if_resumed'):
        checkpoint.pop(key, None)
    checkpoint.update(completed_sections=SECTION, next_section=291, latest_functional_section=SECTION,
        batch_status='P3_SECTION290_VALIDATED_AWAITING_PUBLICATION', next_full_validation_after=next_full,
        next_action='从291继续P3剩余地图/事件/掉落工作，先核证据；当前无连续数字终点，下一定期完整可用全量305。')
    checkpoint['policy']['next_full_validation_after'] = next_full
    checkpoint['current_batch_commit_policy']['next_full_validation_after'] = next_full
    checkpoint['current_batch'].update(status=checkpoint['batch_status'], next_section=291, next_section_started=False,
        receipt='verification/sections/290.json', next_full_validation_after=next_full, batch_closed=False)
    checkpoint['confirmed_next_stage_direction'].update(last_completed_functional_section=SECTION, next_functional_section_started=False)
    checkpoint['sections'].append({'number': SECTION, 'completion_ref': 'p3-section-290', 'topic': TITLE, 'verification': 'verification/sections/290.json'})
    checkpoint['current_section_save'] = {'section': SECTION, 'verification': 'verification/sections/290.json',
        'scope': 'current_functional_section', 'binding': 'enclosing_commit',
        'commit_reference': 'commit containing290 source, full/necessary receipts, requirements and cloud index'}
    checkpoint['last_verified_cloud_save']['scope'] = 'previous_functional_section'
    checkpoint['last_full_validation'] = {'after_section': SECTION, 'receipt': FULL_PATH,
        'available_checks_passed': True, 'complete_repository_validation': False, 'scope_not_reduced': True,
        'native_current_windows_gui_verified': True, 'native_windows_game_chat_verified': False,
        'unresolved_available_failures': False, 'original_failed_attempts_preserved': True}
    checkpoint['current_available_full_validation'] = {'section': SECTION, 'receipt': FULL_PATH,
        'available_scope_passed': True, 'native_windows_game_chat_verified': False}
    checkpoint['current_section_validation'] = {'section': SECTION, 'receipt': 'verification/sections/290.json',
        'necessary_methods_passed': int(ran[1]), 'display_migration_methods_passed': migration['actual_passed_count'],
        'native_isolated_window_checks': window['unique_checks'], 'full_suite_rerun': True, 'full_receipt': FULL_PATH}
    checkpoint['latest_section_environment'] = {'section': SECTION,
        'native_windows': f"{int(ran[1])} necessary and {migration['actual_passed_count']} display checks separately; canonical290 {window['unique_checks']} checks; full complete available scope and original visible responsive window, private5 unchanged",
        'native_game_or_chat_verified': False, 'new_Linux_Wine_full_run': False,
        'current_section_full_rerun': True, 'full_receipt': FULL_PATH, 'receipt': 'verification/sections/290.json'}
    checkpoint['functional_sections_since_latest_requirement'] = list(dict.fromkeys([*checkpoint['functional_sections_since_latest_requirement'], SECTION]))

    completed = (f'## 功能第290节 · {TITLE}\n\n{now}。{scope}\n\n'
        f"修后{int(ran[1])}必要检查与展示迁移{migration['actual_passed_count']}检查分别保留真实源码与退出，互不叠加；"
        f"最终真实Windows两页{window['unique_checks']}检查通过，原项目测试窗口正常重启、可见响应并置前，5私人路径未变。"
        f"完整可用复验见{FULL_PATH}：离线实际{full['offline_windows']['tests_run']}项，旧52状态及typed读回、当前29项与五补充窗口完成；"
        '原30项真实1314失败仍不可用，A1超时与原始失败保留。'
        '源资料、资格、目录和本局均不借结果卡改写；25/57原入口缺口不减少，直升术语已核而具体招募/培养/领取需本局依据。'
        '本节本机功能与验收完成，云端发布尚待普通推送核对。后续291，下一定期全量305（125锚点每15节），无连续数字终点；P3/P2/P1仍未完成。\n\n')
    mutations = {ROOT / 'verification/sections/290.json': encode(receipt), ROOT / 'DEVELOPMENT_CHECKPOINT.json': encode(checkpoint)}
    old_wip = regular(ROOT / 'WORK_IN_PROGRESS.md').read_text(encoding='utf8')
    require('## 功能第289节' in old_wip, 'keep historical289 onward work log')
    mutations[ROOT / 'WORK_IN_PROGRESS.md'] = (completed + old_wip[old_wip.index('## 功能第289节'):]).encode('utf8')
    mutations[ROOT / 'PROJECT_COMPLETED.md'] = (completed + regular(ROOT / 'PROJECT_COMPLETED.md').read_text(encoding='utf8')).encode('utf8')
    progress = regular(ROOT / 'PROJECT_PROGRESS.md').read_text(encoding='utf8')
    anchor = '25个未绑定来源原场景、57个原选项的入口与条件链；'
    require(progress.count(anchor) == 1, 'exact remaining-only event todo anchor')
    mutations[ROOT / 'PROJECT_PROGRESS.md'] = progress.replace(anchor, anchor + '临时中介所本次职业组合与实际选择、招募费用、具体培养数值、领取状态及原入口；', 1).encode('utf8')
    requirements = regular(ROOT / 'PROJECT_REQUIREMENTS.md').read_text(encoding='utf8')
    start, end = requirements.index('<!-- current-delivery:start -->'), requirements.index('<!-- current-delivery:end -->')
    block = ('<!-- current-delivery:start -->\n## 当前交付与续接 · 第290节\n\n'
        + '2026-10-16继续P3，无数字终点。' + scope
        + f'修后{int(ran[1])}必要、{migration["actual_passed_count"]}展示与最终Windows两页{window["unique_checks"]}检查分别通过，原窗口更新且私人5路径不变。'
        + f'完整可用范围{FULL_PATH}通过；实际符号链接1314、Linux/Wine/原Windows私样本及游戏聊天不计通过。'
        + '25场景/57原选项入口不减；当前实际选择、费用、具体培养与领取仍待证。下一节291，下一定期全量305（125锚点每15节）；'
        + '本节保存绑定enclosing_commit，尚未冒称云端发布，普通推送后须核对真实开发分支。P3/P2/P1未完成，识别最后。\n')
    new_requirements = requirements[:start] + block + requirements[end:]
    require(TERM_SENTENCE in requirements and TERM_SENTENCE in new_requirements, 'preserve20261016 terminology-first known直升 rule')
    mutations[ROOT / 'PROJECT_REQUIREMENTS.md'] = new_requirements.encode('utf8')
    agents = regular(ROOT / 'AGENTS.md').read_text(encoding='utf8')
    start, end = agents.index('## 当前续接 · 第289节'), agents.index('## 当前优先顺序与输出可读性')
    new_agents = (agents[:start] + '## 当前续接 · 第290节已完成功能与完整可用验收\n\n'
        + '2026-10-16继续P3，无数字终点。' + scope
        + f'本机验证见verification/sections/290.json和{FULL_PATH}；原测试窗口更新打开，私人5路径不变。'
        + '25/57原入口、本次实际选择/费用/具体培养/领取仍待证；直升术语本身已查证，不列为未知。'
        + '后续291，下一定期完整可用全量305（125锚点每15节）。P3优先，P2/P1保留、识别最后；'
        + '当前可用通过不含真实符号链接1314、Linux/Wine/原Windows私样本或游戏聊天。'
        + '本节尚待普通推送并核对真实远端；源码/要求/验收/索引同提交。\n\n' + agents[end:])
    require('初次招募即处于已进阶状态' in agents and '初次招募即处于已进阶状态' in new_agents,
            'preserve exact AGENTS terminology rule outside current block')
    mutations[ROOT / 'AGENTS.md'] = new_agents.encode('utf8')
    tool_sources = ['.cache/close_section_290.py', '.cache/run_section_290_repair_necessary.py',
        '.cache/restart_window_290.py', '.cache/focus_window_290.py',
        '.cache/p3-full290-summary-prep/build_summary_candidate.py',
        '.cache/p3-full290-summary-prep/controller-review.json',
        '.cache/p3-full290-summary-prep/controller-review-corrected.process.exit',
        '.cache/p3-full290-summary-prep/controller-review-corrected.stdout.log',
        '.cache/p3-full290-summary-prep/controller-review-corrected.stderr.log',
        '.cache/p3-full290-summary-prep/review_controller_differences-first.py',
        '.cache/p3-full290-summary-prep/controller-review.process.exit',
        '.cache/p3-full290-summary-prep/controller-review.stderr.log',
        '.cache/p3-full290-summary-prep/ROOT_VISUAL_REVIEW_SCHEMA.md']
    archive = PREP / 'final-closeout-tools'
    require(not archive.exists(), 'new public reviewed-tools archive, no overwrite')
    copies = {Path(name).name: regular(ROOT / name).read_bytes() for name in tool_sources}
    copies['before-WORK_IN_PROGRESS.md'] = old_wip.encode('utf8')
    tool_manifest = {'kind': '290_PUBLIC_CLOSEOUT_TOOLS_ONLY_NOT_PRIVATE_STATE',
        'files': {name: {'bytes': len(raw), 'sha256': sha256(raw).hexdigest()} for name, raw in copies.items()},
        'private_state_contents_or_hash_snapshots_copied': False,
        'archive_of_existing_public_69_workers': 'verification/sections/290-preparation/supplementary-public-evidence/presentation-migration/ARCHIVE_MANIFEST.json',
        'no_tests_GUI_restart_game_chat_or_git_push_executed_by_this_script': True}
    require(all(not path.resolve().is_relative_to(ROOT / '.local') for path in mutations), 'no private mutation paths')
    print(json.dumps({'gates_passed': True, 'apply_requested': apply, 'planned_public_files': [str(path.relative_to(ROOT)) for path in mutations],
        'next_full_validation_after': next_full, 'continuous_numeric_target': None, 'no_publication_claim': True}, ensure_ascii=False))
    if not apply:
        return
    archive.mkdir(parents=True)
    for name, raw in copies.items():
        with (archive / name).open('xb') as file:
            file.write(raw)
    with (archive / 'archive-manifest.json').open('xb') as file:
        file.write(encode(tool_manifest))
    for path, raw in mutations.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb' if path.name == '290.json' else 'wb') as file:
            file.write(raw)
    print(json.dumps({'section': SECTION, 'local_closeout_written': True, 'cloud_published': False,
        'next_section': 291, 'next_full_validation_after': next_full}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true', help='Root only: apply after actual full/original-window review. Default preview writes nothing.')
    main(parser.parse_args().apply)
