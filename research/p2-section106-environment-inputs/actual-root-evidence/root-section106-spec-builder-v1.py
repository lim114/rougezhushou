"""Root real106 closure and explicit public archive specification."""
import ast
import datetime
import hashlib
import json
from pathlib import Path

BASE = Path('/workspace/.continuation')
ROOT = Path('/workspace/rougezhushou')

def load(name):
    return json.loads((BASE / name).read_bytes())

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def main():
    spec_path = BASE / 'root-section106-save-spec-v1.json'
    assert not spec_path.exists()
    guard = load('resume106-applied-source-v1.json')
    assert guard['source_count'] == len(guard['source_sha256']) == 749
    for name, want in {**guard['source_sha256'], **guard['source_additional_sha256']}.items():
        assert sha((ROOT / name).read_bytes()) == want, name
    related = load('resume106-related-v1.json')
    assert related['available_checks_passed'] is True and related['failures'] == related['errors'] == 0
    assert related['source_sha256'] == guard['source_sha256'] and not related['source_drift']
    lines = (BASE / 'resume106-selected-v1.log').read_text().splitlines()
    selected = json.loads(next(line for line in reversed(lines) if line.startswith('{"passed"')))
    assert selected['passed'] is True and selected['failures'] == selected['errors'] == 0
    gold = load('resume106-window-gold-v1/receipt.json')
    candidate = load('resume106-window-candidate-v1/receipt.json')
    for phase, value, count in (('gold', gold, 9), ('candidate', candidate, 23)):
        assert value['phase'] == phase and value['passed'] is value['workflow_complete'] is True
        assert len(value['rows']) == count and not value['Qt_errors'] and not value['source_drift']
        assert value['runner_sha256'] == 'd4076884a45a8044778a6d358e1a4e54921edde7f6baeb545a3a4c35ed65d520'
        assert value['source_before'] == value['source_after']
    assert candidate['source_after'] == guard['source_sha256']
    assert candidate['actual_gold_receipt_sha256'] == sha((BASE / 'resume106-window-gold-v1/receipt.json').read_bytes())
    saved = load('root-resume106-saved-audit-v1.json')
    visual = load('resume106-visual-audit-v1.json')
    assert saved['passed'] is saved['workflow_complete'] is True and not saved['source_drift']
    assert saved['decoded_record_count'] == 836 and saved['healthy_Gold_points_checked'] == 18
    assert saved['source_after'] == guard['source_sha256']
    assert visual['passed'] is visual['workflow_complete'] is True and visual['actually_viewed_images'] == 4
    assert visual['candidate_receipt_sha256'] == sha((BASE / 'resume106-window-candidate-v1/receipt.json').read_bytes())
    assert len(candidate['pngs']) == len(visual['pngs']) == 4
    for png, viewed in zip(candidate['pngs'], visual['pngs']):
        assert all(viewed[key] == value for key, value in png.items()) and viewed['actually_viewed'] is True
    exit_names = ['root-section106-apply-v2.exit-code', 'resume106-related-v1.exit-code',
        'resume106-selected-v1.exit-code', 'resume106-window-gold-v1.exit-code',
        'resume106-window-candidate-v1.exit-code', 'root-resume106-saved-audit-v1.exit-code']
    for name in exit_names:
        assert (BASE / name).read_bytes() == b'0\n', name
    publication = load('section105-publication-v1.json')
    assert publication['local_HEAD'] == publication['remote_HEAD'] == guard['baseline_HEAD']
    assert publication['push_primary_exit'] == 0 and publication['clean'] is True
    original = load('section106-original-environment-actual-linux-v1/observations.json')
    assert original['observation_complete'] is True and original['product_pass'] is False
    assert sha((BASE / 'section106-original-environment-actual-linux-v1/observations.json').read_bytes()) == 'c09e542f3d1cee720c31daa638663a133bd1894268eb7bb20abc062ccfb92b25'
    test_tree = ast.parse((ROOT / 'tests/test_environment_input_106.py').read_bytes())
    assert sum(isinstance(n, ast.FunctionDef) and n.name.startswith('test_') for n in ast.walk(test_tree)) == 23
    stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
    report = f'''# 第106节环境适用资格与原始来源报告

{stamp}（北京时间）。当前749维护Source及CORE前后匹配；本节验收后实际提交推送，未来自身commit hash不在准备阶段虚构。

共同修复三个原有问题：难度缓存只看modeDifficulty而忽略mode，导致不支持模式被本局上下文复用和UI锁定；固定敌人引用等级bool被数值API按0/1误接受，而预览原本已拒绝；合法难度的非文本source在build_report拼接时TypeError，数值API不能返回结果。原实现33组/284调用/350native观察及19 ValueError、5 TypeError完整保留，不将原观察算修复PASS。

五处产品局部变动：difficulty_value资格同时检查原数值入口已经要求的两个模式字段；只有active固定enemy bool引用增加既有身份ValueError，原数值float兼容和预览严格错误不变；来源只在报告呈现时显示未确认，保留原raw；UI/本局摘要沿共同资格决定确认/可用分析预设。分析预设仍不能替换原本局配置或绕过原ValueError。真实合法新NORMAL观察、原培养记录及实际保存恢复保持。

实际23新API方法；相关20选择项 {related['tests_run']}运行/{related['tests_passed']}通过/{related['skipped']}原skip/{related['unavailable_parent_count']}不可用父项/0失败0错误；精选117登记 {selected['tests_run']}运行/{selected['skipped']}原skip/0失败0错误。相关不可用保持原AvailableResult分类，不伪装PASS。本节未重复105全量，下一五节全量为110。

实际Gold9窗口/143native/90.1303秒；候选23窗口/343native/222.7760秒、原direct API各11，无Qt错误。四候选PNG已实际查看；坏来源图当前视口没有滚到来源段，只证明可返回计算的界面，具体未确认文字由完整报告Saved原件核实。

Root实际Saved: {saved['decoded_record_count']}条受限原件解码，{saved['original_combined_pure_records_checked']}原API联合caller/state/disk守恒，{saved['actual_calculator_caller_records_checked']}窗口/直接API caller守恒，{saved['saved_snapshots_checked']}快照，{saved['healthy_Gold_points_checked']}健康初始/新观察完整Gold配对（全部结果、三全文、状态/原盘），{saved['direct_API_contracts_checked']}直接合同，{saved['actual_close_direct_RunState_records_checked']}实际close后RunState加载保存JSON整图。Rootbindings绑定真正Gold CLI使用的resume105-applied guard，不误借模板full105-suite guard字节。

窗口没有保存每一个UI/formatter的联合prepost；这些沿冻结runner原runtime断言，独立Saved不补造。window_per_UI_step_prepost_saved_verified、individual_formatter_prepost_saved_verified、cross_separate_freeze_live_alias_verified均False。JSON不保live别名，未二次MainWindow重开/自然OCR/原生Windows/游戏/聊天。没有添加新模式数值、账户科技buff或动态关卡假设，18组P2/P3等待办仍按PROJECT_PROGRESS保留；旧95三次未完成继续搁置。

下一节107的原实现准备证据另列：Root已做14公开caller、74显式消费者/1catalog getter/89native/0原API错误，已确认重力蔑视机关最终面板减重但安洁重量天赋仍用原重量。该原观察与冻结Source准备不是107候选应用或完成；106发布后按资料证实范围处理。
'''
    report_path = BASE / 'section106-actual-report-v1.md'
    with report_path.open('x') as f:
        f.write(report)
    entries = []
    for path in sorted(BASE.iterdir()):
        if path.name.startswith('section106-'):
            entries.append({'source': str(path), 'destination': 'public106/' + path.name})
        if path.name.startswith('resume106-'):
            entries.append({'source': str(path), 'destination': 'actual106/' + path.name})
    root_names = ['root-section106-apply-v1.py', 'root-section106-apply-v2.py',
        'root-section106-apply-v2.log', 'root-section106-apply-v2.exit-code',
        'root-section106-applier-independent-source-v1', 'root-section106-applier-independent-source-v2',
        'root-resume106-related-v1.py', 'root-resume106-saved-bindings-v1.json',
        'root-resume106-saved-audit-v1.json', 'root-resume106-saved-audit-v1.log',
        'root-resume106-saved-audit-v1.exit-code', 'resume106-applied-source-v1.json',
        'root-live-recovery-section106.json', 'root-section106-spec-builder-v1.py']
    for name in root_names:
        entries.append({'source': str(BASE / name), 'destination': 'actual-root-evidence/' + name})
    for name in ['section107-enemy-weight-original-probe-source-v1',
        'section107-enemy-weight-original-probe-independent-source-v1',
        'section107-original-weight-actual-linux-v1', 'section107-original-weight-actual-linux-v1.log',
        'section107-original-weight-actual-linux-v1.exit-code',
        'section107-technology-consumer-independent-source-v1']:
        entries.append({'source': str(BASE / name), 'destination': 'preparation-only-next107/' + name})
    entries.extend([{'source': str(BASE / 'section105-publication-v1.json'), 'destination': 'prior-publication.json'},
                    {'source': str(report_path), 'destination': 'REPORT_ZH.md'}])
    topic = '环境适用资格与来源报告'
    paragraph = (f'模式两字段统一确认资格、active敌人bool引用拒绝、非文本来源安全报告及原信息保留/合法新观察恢复共同完成。23新方法；相关{related["tests_run"]}/{related["tests_passed"]}PASS/{related["skipped"]}skip/U{related["unavailable_parent_count"]}父项、精选{selected["tests_run"]}/skip{selected["skipped"]}，0失败0错误。真实9Gold/23候选窗口，836Saved/73快照/18完整Gold点/32close后JSON加载及四图通过。未存逐UI/formatter共同prepost与跨分freeze alias仍未验证；无原生Windows/游戏/聊天。107仅原证据，待本节推送后修复。')
    spec = {'section': 106, 'topic': topic, 'archive': 'research/p2-section106-environment-inputs',
        'source_guard': str(BASE / 'resume106-applied-source-v1.json'),
        'exit_files': [str(BASE / name) for name in exit_names],
        'pass_receipts': [str(BASE / 'root-resume106-saved-audit-v1.json'), str(BASE / 'resume106-visual-audit-v1.json')],
        'public_evidence': entries, 'previous_publication': str(BASE / 'section105-publication-v1.json'),
        'next_action': '106实际commit/push后，107减重来源与重量天赋共享同一派生参考，完整手填/固定身份、培养、低重、报告及窗口边界；每节检验保存，110后全量及总结。P2未知资料和95搁置不变。',
        'archive_readme': '# 第106节环境适用资格与来源报告\n\n实际范围、边界和未完成事项见REPORT_ZH.md；Source-only材料不计Runtime/小节。preparation-only-next107仅下一节公开原证据，未应用候选。所有原件由manifest逐项SHA核对，原失效/skip/不可用保留。',
        'section_receipt': {'implemented_scope': ['Difficulty mode alias eligibility', 'Active bool enemy reference rejection',
            'Safe non-text provenance report', 'Shared UI/summary qualification', 'Actual legal fresh observation persistence'],
            'new_test_methods': 23, 'related_tests': {k: related[k] for k in ('tests_run', 'tests_passed', 'skipped', 'unavailable_parent_count', 'failures', 'errors')},
            'selected_tests': selected, 'Gold_windows': 9, 'candidate_windows': 23, 'Gold_native': 143, 'candidate_native': 343,
            'Saved_decoded_records': 836, 'healthy_complete_Gold_points': 18, 'actual_close_direct_RunState_records': 32,
            'four_pngs_actually_viewed': True, 'next_full_validation_after': 110, 'new_source_files': 1,
            'window_per_UI_step_prepost_saved_verified': False, 'individual_formatter_prepost_saved_verified': False,
            'cross_separate_freeze_live_alias_verified': False, 'full095_deferred_preserved': True},
        'completed_paragraph': paragraph,
        'work_paragraph': paragraph + ' 当前验收归档，正在真实提交推送，随后依序107；下次110全量和进度总结。'}
    with spec_path.open('x') as f:
        json.dump(spec, f, ensure_ascii=False, indent=2); f.write('\n')
    print(json.dumps({'spec': str(spec_path), 'public_entries': len(entries), 'source_files': 749}))

if __name__ == '__main__':
    main()
