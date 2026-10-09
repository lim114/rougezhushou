"""Root builds a concrete104 archive spec from actual completed receipts."""
import json
from pathlib import Path

BASE = Path('/workspace/.continuation')
OUT = BASE/'root-section104-save-spec-v1.json'
assert not OUT.exists()
audit_path = BASE/'root-resume104-saved-audit-v1.json'
audit = json.loads(audit_path.read_bytes())
assert audit['passed'] is True and audit['workflow_complete'] is True
gold = json.loads((BASE/'resume104-window-gold-v1/receipt.json').read_bytes())
candidate = json.loads((BASE/'resume104-window-candidate-v1/receipt.json').read_bytes())
related = json.loads((BASE/'resume104-related-v1.json').read_bytes())
assert gold['passed'] is candidate['passed'] is True
assert len(gold['rows']) == 9 and len(candidate['rows']) == 18
assert len(gold['records']) == 117 and len(candidate['records']) == 238
entries = []
for p in sorted(BASE.iterdir()):
    if p.name.startswith(('section104-', 'root-section104-applier-independent-source-review')):
        assert not p.is_symlink()
        entries.append({'source':str(p),'destination':'public-source-and-original/'+p.name})
for p in sorted(BASE.iterdir()):
    if p.name.startswith(('root-section104-apply-', 'root-resume104-', 'resume104-',
                          'root-live-recovery-section104', 'root-section104-spec-builder-')):
        entries.append({'source':str(p),'destination':'actual-root-evidence/'+p.name})
entries.append({'source':str(BASE/'section103-publication-v1.json'),'destination':'prior-publication.json'})
paragraph = ('已编入资源读取准入：无效容器、无效记录或缺少value的字段按未读处理，保留旧事实和原时间；'
             '完整零值与原有float/None/bool/text保存语义、合法同页字段及配置更新、未知计数器资格和原IO失败策略不变。'
             '15个新增真实API方法，相关221运行/220PASS/1既有skip/0失败0错误；精选1306运行/1既有skip/0失败0错误。'
             'Wine九个健康Gold及十八候选实际窗口均raw0，355份native记录、273个原计算成功；'
             '九健康组初始与观察后完整原生结果、三全文、原状态和磁盘均与实际Gold一致。'
             '四图已实际查看；27次关闭后直接RunState重载，真实非空.tmp目录写盘失败保留内存提示并恢复较早磁盘，'
             '窗口未测手动reset，不宣称全部MainWindow重新打开。')
readme = ('# 第104节资源读取准入与保存边界\n\n'+paragraph+'\n\n'
          '44组实际原API观察基于已完成102的746+CORE源码；观察workflow0但productFalse，保留原异常、磁盘和native证据。'
          '现在修复基于已实际push103的747到748，仅run_state.apply局部、15方法测试及精选登记，保留101–103全部改动。'
          '旧完整资源metadata循环仍按原JSON政策产生ValueError；未进行全局schema清洗/回滚，也不拒绝此前已接纳完整值。'
          '坏读数是公开构造API输入，不声称自然OCR曾产生这些问题。\n\n'
          'Root apply-v1仅Source；v2补齐原件manifest7文件pin及断点不存在前置，Root实际运行一次0。'
          'v2非作者Source复核晚于Root实际执行，原件按真实时间保留。'
          'JSON重载使用实际磁盘完整JSON oracle；live native另存类型/浮点位/顺序/双向alias，JSON不保内存alias。\n\n'
          'P2机制、旧095三次未完成及原生Windows/游戏/客户端聊天边界继续保留，18未完成项目组不因这节销项。'
          '每节commit/push，105后五节全量和进度总结，再依序继续。')
spec = {'section':104,'topic':'资源读取准入与保存边界','archive':'research/p2-section104-resource-admission',
        'source_guard':str(BASE/'resume104-applied-source-v1.json'),
        'exit_files':[str(BASE/n) for n in ('root-section104-apply-v2.exit-code','resume104-related-v1.exit-code',
            'resume104-selected-v1.exit-code','resume104-window-gold-v1.exit-code',
            'resume104-window-candidate-v1.exit-code','root-resume104-saved-audit-v1.exit-code')],
        'pass_receipts':[str(BASE/'resume104-window-gold-v1/receipt.json'),
            str(BASE/'resume104-window-candidate-v1/receipt.json'),str(audit_path)],
        'public_evidence':entries,'previous_publication':str(BASE/'section103-publication-v1.json'),
        'next_action':'104真实commit/push后，105完成原测试登记遗漏及真实字体fixture，运行本组全部可用Linux/Wine/实际窗口检查并展示总结，然后继续下一组；旧095/native边界保持。',
        'archive_readme':readme,
        'section_receipt':{'implemented_scope':['Incomplete resource admission retains old fact/time',
            'Wellformed peers/config and original complete-value/save-error policies preserved'],
            'new_test_methods':15,'related':{k:related[k] for k in ('tests_run','tests_passed','skipped','failures','errors','unavailable_parent_count')},
            'selected':{'tests_run':1306,'skipped':1,'failures':0,'errors':0},'saved_readback':audit,
            'gold_windows':9,'candidate_windows':18,'native_records':355,'original_numeric_successes':273,
            'gold_elapsed_seconds':gold['elapsed_seconds'],'candidate_elapsed_seconds':candidate['elapsed_seconds'],
            'actual_original_cases':44,'actual_original_product_pass':False,
            'full_batch_next_after':105,'remaining_project_groups':18,'natural_OCR_verified':False},
        'completed_paragraph':paragraph+' 归档research/p2-section104-resource-admission；P2机制未确认部分继续保留。',
        'work_paragraph':'104真实回归、九Gold/十八候选窗口、完整saved读回和四图检验通过，正在真正commit/push；依序105原测试登记收口、真实字体fixture、五节可用全量与总结，再自动下一组。'}
with OUT.open('x') as stream:
    json.dump(spec,stream,ensure_ascii=False,indent=2);stream.write('\n')
print(json.dumps({'spec':str(OUT),'public_entries':len(entries)}))
