"""Root-only final aggregation from completed actual receipts, without project reexecution."""
import datetime
import hashlib
import json
from pathlib import Path

B = Path('/workspace/.continuation')
R = Path('/workspace/rougezhushou')


def read(name):
    return json.loads((B / name).read_text())


def pin(name):
    p = B / name
    assert p.is_file() and not p.is_symlink()
    raw = p.read_bytes()
    return {'path': name, 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def zero(name):
    assert (B / name).read_bytes() == b'0\n', name
    return pin(name)


def passed(name):
    value = read(name)
    assert value['passed'] is True and value['workflow_complete'] is True, name
    assert value.get('source_drift', []) == [], name
    return value


def source():
    guard = read('resume115-final-source-v1.json')
    actual = {p.relative_to(R).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
              for directory in ('rouge', 'tests', 'scripts')
              for p in (R / directory).rglob('*')
              if p.is_file() and p.suffix in ('.py', '.json') and '__pycache__' not in p.parts}
    assert actual == guard['source_sha256'] and len(actual) == 758
    for name, sha in guard['source_additional_sha256'].items():
        assert hashlib.sha256((R / name).read_bytes()).hexdigest() == sha
    return guard


def main():
    guard = source()
    names = ['full115-linux-actual-v1', 'full115-wine-actual-v1',
             'full115-selected-actual-v1', 'full115-capability-actual-v1',
             'full115-linux-pip-actual-v1', 'full115-wine-pip-actual-v1',
             'full115-window-owned-actual-v1', 'root-full115-saved-actual-v1',
             'section115-original-api-actual-v1', 'section115-candidate-api-actual-v1',
             'root-section115-api-accuracy-actual-v1', 'section115-window-actual-v1',
             'root-section115-window-saved-actual-v1', 'resume115-related-linux-v1',
             'resume115-related-wine-v1']
    exits = [zero(name + '.exit-code') for name in names]
    full = {}
    for platform in ('linux', 'wine'):
        value = read('full115-' + platform + '-actual-v1.json')
        assert value['available_checks_passed'] is True
        assert value['complete_repository_validation'] is False
        assert value['failures'] == value['errors'] == 0
        assert value['source_drift'] == []
        if platform == 'wine':
            assert value['source_additional_drift'] == value['adapter_source_drift'] == []
            assert value['environment_capability_skips'] == 3
        full[platform] = {key: value[key] for key in (
            'tests_run', 'tests_passed', 'historical_or_declared_skips',
            'unavailable_records', 'unavailable_parent_count', 'failures', 'errors')}
    selected = read('full115-selected-actual-v1.json')
    assert selected['passed'] is True and selected['failures'] == selected['errors'] == 0
    assert selected['source_drift'] == selected['source_additional_drift'] == selected['adapter_source_drift'] == []
    assert selected['passed_count_derived_from_run_minus_skipped'] is False
    saved = passed('root-full115-saved-actual-v1.json')
    assert saved['actual_gui_checks'] == 4283 and saved['saved_states'] == 52
    assert saved['selected_public_projections_equal_original_matrix_without_exceptions'] == 42
    assert saved['ten_admitted_projection_comparison_copies_equal_original_matrix'] == 10
    assert saved['no_live_owned_execution_verified'] is True
    assert saved['native_aliases_verified_by_this_audit'] is False
    assert saved['full_result_equality_to_old_gold_verified'] is False
    supervisor = read('full115-window-owned-actual-v1.json')
    assert supervisor['status'] == 'completed' and supervisor['timed_out'] is False
    assert type(supervisor['child_primary_exit']) is int and supervisor['child_primary_exit'] == supervisor['supervisor_exit'] == 0
    assert supervisor['owned_session_closure']['no_live_owned_execution_verified'] is True
    visual = passed('root-full115-visual-actual-v1.json')
    assert visual['Root_actually_viewed_all4_PNGs'] is True and len(visual['pngs']) == 4
    accuracy = passed('root-section115-api-accuracy-actual-v1/receipt.json')
    assert accuracy['original_cases_verified'] == accuracy['candidate_cases_verified'] == 19
    assert accuracy['native_records_decoded'] == 190 and accuracy['actual_calls_verified'] == 152
    assert accuracy['external_source_leaves_verified'] == 66 and len(accuracy['external_examples']) == 4
    assert [list(item['candidate_actual'].values())[0] for item in accuracy['external_examples']] == [25.0, 250.0, 400.0, 1.0]
    assert all(item['exact_nominal_value_agreement'] is True for item in accuracy['external_examples'])
    special = passed('root-section115-window-saved-actual-v1/receipt.json')
    assert special['actual_complete_states'] == 4 and special['actual_native_records_decoded'] == 66
    assert special['actual_independent_SP_pairs'] == 2
    assert type(special['actual_full_close_RunState_AccountCache_reload']) is int
    assert special['actual_full_close_RunState_AccountCache_reload'] == 1
    special_visual = passed('root-window115-specialized-visual-actual-v1.json')
    assert special_visual['Root_actually_viewed_both_PNGs'] is True
    for platform in ('linux', 'wine'):
        related = passed('resume115-related-' + platform + '-v1.json')
        assert related['tests_passed'] == related['tests_run'] == 72
        assert related['failures'] == related['errors'] == related['unavailable_records'] == 0
    publications = []
    for section in range(111, 115):
        publication = read(f'section{section}-publication-v1.json')
        assert publication['commit_primary_exit'] == publication['push_primary_exit'] == 0
        assert publication['local_HEAD'] == publication['remote_HEAD'] and publication['clean'] is True
        publications.append({'section': section, 'commit': publication['local_HEAD']})
    assert publications[-1]['commit'] == guard['root_prior_HEAD']
    source()
    receipt_names = ['resume115-final-source-v1.json', 'full115-linux-actual-v1.json',
        'full115-wine-actual-v1.json', 'full115-selected-actual-v1.json',
        'full115-capability-actual-v1.json', 'full115-window-owned-actual-v1.json',
        'root-full115-saved-actual-v1.json', 'root-full115-visual-actual-v1.json',
        'root-section115-api-accuracy-actual-v1/receipt.json',
        'root-section115-window-saved-actual-v1/receipt.json',
        'root-window115-specialized-visual-actual-v1.json',
        'full115-linux-pip-actual-v1.log', 'full115-wine-pip-actual-v1.log']
    result = {'kind': 'ROOT_ACTUAL_FULL115_AVAILABLE_SCOPE_CLOSURE',
        'recorded_at_UTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'passed': True, 'workflow_complete': True, 'source_drift': [],
        'after_section': 115, 'section_group': [111, 112, 113, 114, 115],
        'source_files': 758, 'CORE_unchanged': True,
        'complete_repository_validation': False,
        'native_windows_game_chat_verified': False,
        **full, 'wine_environment_capability_skips': 3,
        'wine_capability_skips_included_in_declared_skips_not_added_again': True,
        'selected': {key: selected[key] for key in ('tests_run', 'skipped', 'failures', 'errors')},
        'selected_passed_count_derived': False,
        'dependency_checks_raw_exit': {'linux': 0, 'wine': 0},
        'legacy_gui_checks': 4283, 'legacy_saved_states': 52,
        'legacy_projection_scope': {'unchanged_original_projections': 42, 'actual113_proved_window_metric_admissions': 10},
        'legacy_alias_or_cycle_identity_verified': False, 'old_full_result_GUI_Gold_equality_verified': False,
        'specialist_states': 4, 'specialist_native_decoded': 66, 'specialist_SP_pairs': 2,
        'API_original_candidate_cases_each': 19, 'API_native_decoded': 190,
        'API_actual_numeric_and_three_formatter_calls_verified': 152,
        'actual_external_examples_matched': 4, 'external_source_leaves_verified': 66,
        'external_actual_values': [25.0, 250.0, 400.0, 1.0],
        'external_fifth_conditions_not_matched_deferred': True,
        'actual_PNGs_Root_viewed': 6,
        'owned_no_live_execution': True,
        'owned_session_absence_verified': saved['owned_session_absence_verified'],
        'retained_zombies_reaped': False,
        'deferred095_and109_preserved': True,
        'prior_actual_publications': publications,
        'raw_exits': exits, 'actual_receipt_pins': [pin(name) for name in receipt_names],
        'batch_validation_closed': True, 'stop_after_section115': True, 'section116_started': False,
        'scope': 'Current maintained available full/selected tests plus actual bounded52-state legacy GUI and four-state115 GUI, saved audits and public worked-example comparisons. Missing migration evidence, historical/capability skips and native Windows/game/chat remain unverified.'}
    target = B / 'root-full115-actual-complete-v1.json'
    with target.open('x') as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2); handle.write('\n')
    text = f'''# 第111–115节进度与未完成项目

本批完成到第115节，五项实际功能改进及本批可用范围全量检验已经闭合；停止在此，不启动第116节。P2仍未全部完成，P3尚未开始。检验、网上算例、证据读回和归档是功能改进的附加工作。

| 节 | 已编入的实际成果 |
| --- | --- |
| 111 | 深海色触手完整施放保留已释放命中的延迟尾段；观察窗口与回转序列保持各自边界。 |
| 112 | 开始新局同步清理旧采样图片、摘要、预览、识别文字、状态与节点说明；账号档案保留。 |
| 113 | 有限弹药技能按明确观察窗口计算平均输出，避免平均分母提前截到弹药耗尽时刻。 |
| 114 | 实际消费的公共及条件数值参数拒绝布尔值，保留正常数值、文本数值、零值与已有错误顺序。 |
| 115 | 普通报告新增当前输出分项，区分伤害、潜在治疗、独立生命回复和损伤积累；展开已有结果，未知实际量继续未知。 |

## 本批实际检验结果

| 全量环境 | 运行 | 通过 | 历史/声明跳过 | 不可验证记录（父项） | 失败/错误 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Linux | {full['linux']['tests_run']} | {full['linux']['tests_passed']} | {full['linux']['historical_or_declared_skips']} | {full['linux']['unavailable_records']}（{full['linux']['unavailable_parent_count']}） | 0/0 |
| Wine | {full['wine']['tests_run']} | {full['wine']['tests_passed']} | {full['wine']['historical_or_declared_skips']} | {full['wine']['unavailable_records']}（{full['wine']['unavailable_parent_count']}） | 0/0 |

不可验证记录包含子项或初始化记录，不能用这些列反推通过数。Wine三项独立诊断的环境能力跳过已包含在声明跳过列，不再重复相加。缺失历史样本、迁移证据、依赖及跳过项均未计为通过。

精选Wine回归实际运行{selected['tests_run']}项、跳过{selected['skipped']}项、0失败/0错误，原始退出0；不从运行数减去跳过数推导独立通过数。Linux/Wine依赖检查均原始退出0。

完整窗口流程实际完成4283个检查、52个保存状态和每状态三份完整报告文本；退出码、受控子进程退出码及监督进程退出码均0。42份原始投影直接保持原值，10份按第113节已经实际测量的窗口秒数/平均输出差异核对，原始结果、调用输入和原始对照文字不改写。保存记录已独立读回，四张窗口/控件截图已实际查看。第115节专项另外完成4个窗口状态、66份原生记录、2对SP比较、关闭/重载及2张输出分项截图。

当前758个维护源码/JSON及额外CORE文件在检验前后保持冻结值。受控窗口进程完成且没有仍在执行的所属进程；已终止的僵尸条目若被保留，不等同于已经回收或所属会话完全消失。截图只证明实际可见部分，医疗说明在部分旧版截图中有裁剪。旧版保存格式没有容器别名/循环身份表示，也不宣称旧完整结果Gold全等或第95节原全量调用向量已恢复。

## 网上算例准确性核对

实际检索与下载的网页、版本、原文、参数及比较结果已封存；4个条件匹配的算例由实际项目调用得到以下一致结果。

| 公开算例与条件 | 公开结果 | 实际结果 |
| --- | ---: | ---: |
| ATK500、DEF800：物理伤害下限 | 25 | 25.0 |
| ATK500、RES50：法术单次伤害 | 250 | 250.0 |
| ATK1200、DEF800：物理单次伤害 | 400 | 400.0 |
| 阿米娅S1七级、基础间隔1.6秒、100+60攻速 | 1秒 | 1.0秒 |

前三例来源为[Terra Wiki Damage](https://arknights.wiki.gg/wiki/Damage#Tips)，下载观测版本[759599](https://arknights.wiki.gg/wiki/Damage?oldid=759599)。原文DEF/RES与低攻伤害带近似号；这里只比较其名义800/50输入，不将A等级换算或近似示例说成准确实战测量。攻速例来源为2021/06/19的[TapTap算例](https://www.taptap.cn/moment/152911449218355181)；原文一处技能序号笔误已与[阿米娅技能资料706848版](https://arknights.wiki.gg/wiki/Amiya?oldid=706848)及当前目录交叉核对，检验只覆盖攻速与间隔，不覆盖首击、命中数、SP或周期。

IS-Central另一个显示伤害算例涉及不同肉鸽模式、养成及取整条件，条件未对齐，保留为搁置候选，不计通过。19组原件/候选调用及三个完整格式化输出共190份原生证据已经读回，数值结果保留；第115节只增加已有分项的报告展示。

## 尚未完成

- P2时序与精度：其余条件天赋、模组、召唤物、获取目标、碰撞/命中、首跳、刷新、技能结束、阻回、伤转疗及动态事件的原生依据。深海色当前热更新与实际面板仍需独立核对。
- 藏品与本局强化：成长历史、多来源技力回复、动态弹药/补弹、资源事件顺序、重复获取、离队重入及库存真实规则；棋子数量、库存与实际在场上限映射仍有缺口。
- 本局环境：分队账号解锁/激活、长期科技实际属性层与模式适用性、动态关卡及其余敌人修正。
- 后续资料：第六层/特殊区域、路线与节点事件完整选择链、频次/权重/掉落池、地图校准、出怪与条件分支、敌人及首领脚本、图片分类缺口。
- 交付与集成：更多客户端/机器的聊天重连与协议、界面优化、原生Windows安装、升级保留、卸载及多机验收。
- 识别优化最后统一处理：持有页计数与变体、地图/连线覆盖、裁剪与低分辨率负例、连续页面完整读取和端到端OCR性能。第112节清理旧视图不等于识别准确率已提升。

不确定机制继续查资料并保留未知。研究线索、参数候选和测试通过不等同于这些未完成功能已经实现。详细剩余项以[PROJECT_PROGRESS.md](PROJECT_PROGRESS.md)为准。

第95节原窗口流程三次未完成，第三次取消退出143；第109节原完整候选窗口三次未完成（1、1、未取得最终退出码），最后窗口、关闭重载与第四图仍未闭合。两项保持搁置，不能由本批另一条窗口流程通过改写为成功；恢复须先有新诊断、有限计划和可靠执行条件，不自动重复第四次。

当前环境为Linux；Wine结果属于Windows兼容检验。原生Windows、真实游戏/聊天、私人布局及未迁移样本均未验证。

## 保存与断点

开发分支为`codex/p2-development`。第111–114节已实际逐节提交并推送，记录如下；第115节由包含本报告的本节提交保存，Root在实际commit/push后另行核对远端一致与工作区洁净。

''' + '\n'.join(f"- 第{row['section']}节：`{row['commit']}`" for row in publications) + '''

最终实际收据与公开证据归档在`research/p2-section115-current-output-breakdown`及`verification/full-115`；断点在`DEVELOPMENT_CHECKPOINT.json`。本批关闭，后续收到继续开发指令后从第116节恢复，保留所有未完成和搁置项目。
'''
    with (B / 'root-batch111-115-report-actual-v1.md').open('x') as handle:
        handle.write(text)
    print(json.dumps({'passed_available_scope': True, 'after_section': 115,
                      'linux': full['linux'], 'wine': full['wine'],
                      'selected_run': selected['tests_run'], 'GUI_checks': 4283,
                      'external_examples_matched': 4, 'section116_started': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
