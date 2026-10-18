from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone, timedelta
import json, runpy

ROOT = Path(__file__).resolve().parents[1]
def read(name): return json.loads((ROOT / name).read_bytes())
def sha(name): return sha256((ROOT / name).read_bytes()).hexdigest()
def enc(value): return (json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf8')
def pin(name): return {'receipt': name, 'sha256': sha(name)}

title = '卡德霍、痛楚化身与猎犬的招式和退场条件'
change = '普通版永无安宁新增卡德霍、痛楚化身及猎犬proto三个精确资料入口；四组条件说明覆盖首次击倒与休整、痛吼的两种分支、位移及降攻速、化身退场增益、猎犬锁定撕咬和返回。完整保留8张技能卡、3张能力卡及术语原文，明确20秒/10秒、召唤摘要/关卡生成、旧图鉴/全场敌人增益和存疑波次的资料差异。痛苦将息的独立覆写与两种自定义化身另列依据，不借普通版技能。三个准确原图和中文主题阅读可用；同来源刷新保留阅读，换身份或坏源清旧、恢复手动重开。技术详情的特殊空格与分隔符用JSON转义保真，中文保持可读，严格读回原件的断言不放宽。'
limits = '固定文献不是本局状态：不从首次击倒、波次说明或冷却数值恢复实际触发时刻、出怪次数、伤害和通关结果；存疑波次仍存疑。技能的生成、召唤、退场、结束和持续攻击分别保留，不能互相替代；痛楚化身最多两层增益不等于当前层数。20秒/10秒及图鉴/社区修正版的当前服务器适用性仍未核对；扣30或10目标生命不推定所有对局必败。痛苦将息及其自定义化身未新增基础技能入口或完整机制预测，也不将旧内部pursuit名称当游戏分类。实际面板、命中、层数、路径、时钟、结算、当前热更新及其余首领/节点/掉落/完整地图校准仍待核验。没有修改数值模型、地图或本局记忆；P3/P2/P1均未全部完成。'
necessary = 'verification/sections/311-necessary-attempt2/process.json'
native = 'verification/sections/311-native-attempt1/actual/window.json'
process = 'verification/sections/311-native-attempt1/process.json'
visual = 'verification/sections/311-root-visual.json'
main = 'verification/sections/311-main-window.json'
build = 'verification/sections/311-source-attempt2/process.json'
n, w, p, v, m, b = (read(name) for name in (necessary, native, process, visual, main, build))
assert n['passed'] and n['exit_code'] == 0 and n['methods_ran'] == 94
assert w['passed'] and w['qpa'] == 'windows' and w['qt_exit_code'] == 0 and w['verification_window_closed']
assert w['unique_checks'] == 31 and len(w['checks']) == len(set(w['checks'])) == 31
assert len(w['actual_entry_overviews']) == 3 and len(w['actual_topic_readings']) == 12 and len(w['same_identity_refresh_observations']) == 6
assert all(value == 0 for value in w['external_operation_attempts'].values())
assert p['passed'] and p['exit_code'] == 0 and p['window_receipt_sha256'] == sha(native)
assert v['all_reviewed'] and len(v['images']) == len(w['screenshots']) == 5
for image in v['images']: assert image['root_viewed'] and sha(image['file']) == image['sha256']
assert m['passed'] and m['window_visible_and_responsive'] and m['private_state_five_paths_unchanged'] and m['private_entire_normal_close_and_start_interval_unchanged']
assert b['passed'] and b['exit_code'] == 0
for value in (n, w, b):
    assert value['source_sha256_before'] == value['source_sha256_after']
    for name, expected in value['source_sha256_after'].items(): assert sha(name) == expected, name
registration = 'verification/sections/311-preparation/maintained-registration.json'
reg = read(registration)
assert reg['after_count'] == 484 and reg['before_count'] == 481 and reg['original_ordered_prefix_unchanged'] and reg['source_sha256'] == sha('scripts/verify_full_available.py')
usage = read('verification/sections/311-preparation/usage-threshold.json')
assert usage['remaining_percent'] == 85 and usage['strict_below15_triggered'] is False
cp = read('DEVELOPMENT_CHECKPOINT.json')
assert cp['completed_sections'] == 310 and cp['next_section'] == 311 and cp['batch_start_section'] == 311
assert cp['policy']['wrap_up_below_usage_percent'] == 15 and cp['policy']['development_paused_by_latest_user_request'] is False
failure = read('verification/sections/311-necessary-attempt1/process.json')
assert failure['passed'] is False and failure['exit_code'] == 1 and failure['methods_ran'] == 93
assert sha('scripts/verify_boss_hunt_window_311.py') == '937e16f28d825646c9a89fc0097cb046b3ae1bd361f128ba836c6c2b05415d45'
now = datetime.now(timezone(timedelta(hours=8))).isoformat()
pending = '<!-- section311-publication-pending -->当前为本地验收完成，普通推送与真实远端核对尚待完成。'
r = {'section': 311, 'kind': 'functional_section', 'title': title, 'new_capability': change,
     'limitations': [limits], 'at_Beijing': now, 'branch': 'codex/p2-development',
     'necessary_validation': {**pin(necessary), 'methods_run': 94, 'actual_exit': 0},
     'native_windows_validation': {**pin(native), 'process': pin(process), 'unique_checks': 31,
         'actual_Qt_exit': 0, 'exact_entries': 3, 'actual_topic_readings': 12,
         'actual_nonzero_refresh_reading_states': 6, 'eight_external_operation_attempts_zero': True},
     'root_visual_review': pin(visual), 'original_project_window': pin(main), 'source_build': pin(build),
     'actual_canonical_rebuild': pin('verification/sections/311-preparation/root-source-rebuild/process.json'),
     'source_sha256': n['source_sha256_after'], 'validated_source_sha256': w['source_sha256_after'],
     'maintained_registry': pin(registration), 'source_manifest': pin('research/p3-boss-hunt-311/source-manifest.json'),
     'source_scope': {'exact_targets': [['ro6_b_4', 'enemy_2145_cadejo', 0], ['ro6_b_4', 'enemy_2146_cadesd', 0], ['ro6_b_4', 'enemy_2137_shsdgo', 0]],
         'complete_public_revisions': ['436092', '441718', '436178', '427937', '428754'],
         'skill_cards': 8, 'ability_cards': 3, 'conditional_reading_topics': 4,
         'per_target_fresh_public_runtime_members': 12, 'complete_selected_current_stages': 2,
         'complete_selected_current_skill_definitions': 5, 'selected_current_bindings': 8,
         'whole_database_and_levels_hashing_at_build_only': True,
         'explicit_whole_primary_location_overrides_verified': True,
         'current_server_or_actual_modes_verified': False, 'numerical_phase_model_added': False},
     'original_failure_history': [pin('verification/sections/311-necessary-attempt1/process.json')],
     'failure_scope': 'One view method failed in12 subject/topic subtests because Qt normalized source NBSP;94 final methods pass after display-only fix plus one added regression method. Original93 receipt retained.',
     'qt_display_repair': pin('verification/sections/311-preparation/qt-whitespace-repair/applied.json'),
     'independent_static_review_before_repair': pin('verification/sections/311-preparation/independent-static-review/REVIEW_FINAL.json'),
     'independent_static_review_after_repair': pin('verification/sections/311-preparation/qt-whitespace-repair/independent-review.json'),
     'historical_candidate_ui_handoff_is_before_qt_repair_not_current_source_map': True,
     'full_suite_rerun': False, 'last_full_receipt': 'verification/full-305/summary.json',
     'last_full_source_is_historical305': True, 'next_periodic_full_section': 320,
     'P3_complete': False, 'P2_complete': False,
     'private_state_contents_parsed_copied_or_restored': False,
     'private_state_hashed_locally_for_preservation_only': True, 'private_hashes_published': False,
     'game_operated': False, 'chat_sent': False, 'cloud_publication_binding': 'enclosing_commit', 'cloud_published': False}
(ROOT / 'verification/sections/311.json').write_bytes(enc(r))
details = change + '\n\n实际94项必要检查、31项原生唯一检查通过；三个入口、12次主题手动阅读及6组非零滚动/选区保持逐项完成，真实公开来源副本损坏/恢复及手动重开通过，根代理查看全部五张实际截图。正常关闭至重新启动的私人五路径不变，原测试窗口已更新可见响应。首轮93方法中一个方法的12个分项暴露Qt特殊空格转换；保留失败和前件，显示修复后严格读回断言保留，并新增实际Qt回归例。旧306/309/310六方法原AST保留；481维护选择器不减，现484。未重跑全量，305仅历史适用范围，下次定期全量320。真实符号链接1314、历史私样本、Linux/Wine及游戏聊天仍不计通过。\n\n' + limits + '\n\n' + pending
for name in ('PROJECT_COMPLETED.md', 'WORK_IN_PROGRESS.md'):
    path = ROOT / name
    text = path.read_text('utf8')
    if name == 'WORK_IN_PROGRESS.md':
        marker = '以下为已交付历史。\n\n'
        assert text.startswith('## 当前进行第311节') and text.count(marker) == 1
        text = text.split(marker, 1)[1]
    path.write_text('## 第311节 + ' + title + '\n\n' + now + '。' + details + '\n\n以下为历史记录；当前断点以上述311为准。\n\n' + text, encoding='utf8')
path = ROOT / 'PROJECT_PROGRESS.md'
text = path.read_text('utf8')
old = '未覆盖首领及其关联装置的完整文献条件流程'
assert text.count(old) == 1
path.write_text(text.replace(old, '其余未覆盖首领及其关联敌人/装置的完整文献条件流程', 1), encoding='utf8')
path = ROOT / 'AGENTS.md'
text = path.read_text('utf8')
end = text.index('\n## ', 3)
path.write_text('## 当前续接 · 第311节 + ' + title + '\n\n' + details + '\n\n继续P3，312未启动；编号仅配实际完成改动，严格低于15%规则保留。\n' + text[end:], encoding='utf8')
path = ROOT / 'PROJECT_REQUIREMENTS.md'
text = path.read_text('utf8')
start, end_marker = text.index('<!-- current-delivery:start -->'), '<!-- current-delivery:end -->'
end = text.index(end_marker) + len(end_marker)
path.write_text(text[:start] + '<!-- current-delivery:start -->\n## 第311节 + ' + title + '\n\n' + details + '\n' + end_marker + text[end:], encoding='utf8')
for key in ('current_section_validation', 'latest_section_environment', 'cloud_publication_closeout', 'active_section'):
    if key in cp: cp['historical_before311_' + key] = cp.pop(key)
cp.update(completed_sections=311, latest_functional_section=311, next_section=312,
          batch_status='P3_SECTION311_LOCAL_ACCEPTED_PUBLICATION_PENDING',
          next_action='第311节 + ' + title + '已本地验收，普通推送与真实远端核对后继续P3；本局实际与剩余缺口保留，下次定期全量320。')
assert not any(item['number'] == 311 for item in cp['sections'])
cp['sections'].append({'number': 311, 'completion_ref': 'p3-section-311', 'topic': title, 'verification': 'verification/sections/311.json'})
cp['functional_sections_since_latest_requirement'].append(311)
cp['current_section_save'] = {'section': 311, 'verification': 'verification/sections/311.json', 'scope': 'current_functional_section', 'binding': 'enclosing_commit'}
cp['last_verified_cloud_save']['scope'] = 'previous_functional_section'
cp['current_section_validation'] = {'section': 311, 'receipt': 'verification/sections/311.json', 'necessary_methods_passed': 94, 'native_isolated_window_checks': 31, 'exact_entries': 3, 'actual_topic_readings': 12, 'actual_nonzero_refresh_states': 6, 'full_suite_rerun': False, 'last_full_receipt': 'verification/full-305/summary.json', 'full_source_is_historical305': True}
cp['latest_section_environment'] = {'section': 311, 'receipt': 'verification/sections/311.json', 'native_windows': '94 necessary;31 unique native checks;3 entries/12 manual topics/6 real nonzero refresh states; source damage and manual recovery; original app startup separately verified', 'native_game_or_chat_verified': False, 'current_section_full_rerun': False, 'last_full_receipt': 'verification/full-305/summary.json'}
cp['current_batch'].update(status=cp['batch_status'], completed_sections=311, next_section=312, next_section_started=False, receipt='verification/sections/311.json', batch_closed=False)
cp['policy'].update(current_usage_remaining_percent=85, current_usage_receipt='verification/sections/311-preparation/usage-threshold.json')
(ROOT / 'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
path = ROOT / 'CLOUD_HANDOFF.md'
path.write_text(path.read_text('utf8') + '\n<!-- section311-handoff:start -->\n## 第311节 + ' + title + '\n\n' + details + '\n<!-- section311-handoff:end -->\n', encoding='utf8')
runpy.run_path(str(ROOT / 'scripts/update_cloud_index.py'))['update'](ROOT)
out = ROOT / 'verification/sections/311-closeout'
out.mkdir()
(out / 'execution-closeout.py').write_bytes(Path(__file__).read_bytes())
(out / 'applied.json').write_bytes(enc({'section': 311, 'local_accepted': True, 'ordinary_cloud_publication_verified': False, 'at_Beijing': now, 'next312_started': False, 'section_label': read('CLOUD_INDEX.json')['current_section_label']}))
(ROOT / 'verification/sections/311-preparation/execution-main-window.py').write_bytes((ROOT / '.cache/open_test_window_311.py').read_bytes())
print(json.dumps({'completed_section_label': read('CLOUD_INDEX.json')['current_section_label'], 'cloud_publication_pending': True}, ensure_ascii=False))
