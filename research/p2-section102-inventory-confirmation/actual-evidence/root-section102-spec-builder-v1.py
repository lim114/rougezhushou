"""Build102 archive from already completed actual evidence; no product execution."""
import json
from pathlib import Path

base=Path('/workspace/.continuation');n=102
full=json.loads((base/'resume102-full-linux-v1.json').read_bytes())
related=json.loads((base/'resume102-candidate-related-v3.json').read_bytes())
gold=json.loads((base/'resume102-window-gold-v1/receipt.json').read_bytes())
window=json.loads((base/'resume102-window-candidate-v1/receipt.json').read_bytes())
audit=json.loads((base/'root-resume102-saved-audit-v1.json').read_bytes())
assert full['available_checks_passed'] and related['available_checks_passed'] and audit['passed']
entries=[]
for name,destination in (
    ('section102-inventory-flag-consumption-source-v1','reviewed-inventory-source-v1'),
    ('section102-inventory-flag-scope-addendum-v1','historical-proof-scope-v1'),
    ('section102-inventory-flag-consumption-review-v1','independent-inventory-source-review-v1'),
    ('section102-registry-import-audit-v1','registry-import-source-audit-v1'),
    ('section102-registry-increment-source-v1','reviewed-registry-source-v1'),
    ('section102-registry-increment-review-v1','independent-registry-source-review-v1'),
    ('section102-window-source-v2','reviewed-window-source-v2'),
    ('resume102-window-gold-v1','actual-original-window-Gold-v1'),
    ('resume102-window-candidate-v1','actual-candidate-window-v1')):
    entries.append({'source':str(base/name),'destination':destination})
names=['section102-source-preparation-v1.json','window102-source-v1.py',
       'section101-original-inventory-flag-probe-v1.py','section101-original-inventory-flag-observations-v1.json',
       'section101-original-inventory-flag-actual-linux-v1.log','section101-original-inventory-flag-actual-linux-v1.exit-code',
       'root-section102-apply-v1.py','root-section102-apply-v1.log','root-section102-apply-v1.exit-code',
       'root-section102-apply-v1-INDEPENDENT_SOURCE_REVIEW.md','resume102-applied-source-v1.json',
       'root-resume102-api-v1.py','root-resume102-api-v2.py','root-resume102-api-v3.py',
       'root-resume102-full-v1.py','root-resume102-saved-audit-v1.py','root-resume102-saved-audit-v1.json',
       'root-resume102-saved-audit-v1.log','root-resume102-saved-audit-v1.exit-code','resume102-visual-audit-v1.json',
       'root-section102-spec-builder-v1.py','root-live-recovery-section102.json']
for prefix in ('resume102-original-registry-v1','resume102-candidate-related-v3','resume102-full-linux-v1'):
    names.extend(prefix+suffix for suffix in ('.json','.log','.stdout.log','.exit-code'))
names.extend(['resume102-full-linux-v1.child-exit-code','resume102-full-linux-guard-v1.json'])
for prefix in ('resume102-window-gold-v1','resume102-window-candidate-v1'):
    names.extend(prefix+suffix for suffix in ('.log','.exit-code'))
for name in names:
    assert (base/name).is_file(),name
    entries.append({'source':str(base/name),'destination':'actual-evidence/'+name})
entries.append({'source':str(base/'section101-publication-v1.json'),'destination':'prior-publication.json'})
summary=(f"15个新增库存确认方法已实际检验并纳入精选套件；52项原断言修改前全部通过，原full登记表精确增至217selectors。"
         f"相关222运行/219实际PASS/3缺样本case＋1缺样本setUpClass不可用/0失败0错误；Linux full {full['tests_run']}运行/{full['tests_passed']}实际PASS/84既有skip/126不可用记录87parents/0失败0错误。"
         "完整物理仓库未验证，10未登记模块与partial缺口仍待105收口。"
         "Wine实际6个Gold＋14候选窗口，保存42＋118native记录、135次原数学调用、六组成对完整原生结果及三全文、五个合法观察保存RunState重载阶段与四张实际查看PNG。"
         "原数字/None短路、浮点及原始坏flag/历史记录保留；新的完整bar和有效历史bar可核对，部分观察/已失效历史不能冒充确认。")
readme=("# 第102节库存确认消费资格与遗漏测试登记\n\n"
        "文字/列表/映射的旧确认标记保留原件，三处消费只使用原兼容数字/bool/None资格，不把坏标记视为证明；生产端bool写入和历史图标等级恢复逻辑保持原行为。\n\n"+summary+
        "\n\nhealthy六个原生完整snapshot（数值结果/三文本/摘要/库存/原状态/原disk）和输入调用类型、浮点位、dict次序、双向容器别名均已Root读取比对。5action阶段有真实RunState重载；三个坏标记无action窗口只构造/计算/关闭守盘，没有声称全部MainWindow重开。所有临时账户、本局、设置、DesktopBackend均公开隔离，auto/timer/请求关闭。\n\n"
        "相关219实际PASS是维护计数；setUpClass不可用不包含在222 testsRun内，因此不拿run数简单相减。Linux full353个Source文件哈希是原脚本范围；Root另绑定全部746维护Source＋CORE，前后无变。不替换断言/放宽分类器/制造样本。\n\n"
        "Source v1 runner未执行，其metadata wrapper比较问题在freshv2实际开跑前已更正；api-v2坏猜模块名也在候选执行前更正为真实_relic_recognition_022文件。原件保留。每节commit/push，105后五节全量和总结。Wine兼容验证不是原生Windows/游戏/客户端聊天验收，P2未知机制仍须查证。")
spec={'section':102,'source_guard':str(base/'resume102-applied-source-v1.json'),
      'exit_files':[str(base/name) for name in ('root-section102-apply-v1.exit-code','resume102-original-registry-v1.exit-code',
          'resume102-candidate-related-v3.exit-code','resume102-full-linux-v1.exit-code','resume102-full-linux-v1.child-exit-code',
          'resume102-window-gold-v1.exit-code','resume102-window-candidate-v1.exit-code','root-resume102-saved-audit-v1.exit-code')],
      'pass_receipts':[str(base/name) for name in ('resume102-window-gold-v1/receipt.json','resume102-window-candidate-v1/receipt.json','root-resume102-saved-audit-v1.json')],
      'public_evidence':entries,'archive':'research/p2-section102-inventory-confirmation','topic':'库存确认资格和52项原回归登记',
      'previous_publication':str(base/'section101-publication-v1.json'),
      'next_action':'102真正commit/push后依序103来源证据与分队缓存合法恢复，104资源观察保存契约；105物理测试登记收口、五节Linux/Wine/window全量和进度总结。未确认机制不写入数值。',
      'archive_readme':readme,'section_receipt':{'implemented_scope':['inline inventory flag qualification and three consumers','15 new real-API methods','52 unchanged original assertions restored into full registry'],
          'new_test_methods':15,'restored_original_methods':52,'full_selector_union':217,'original_restored_methods_actual_PASS':52,
          'related':{key:related[key] for key in ('tests_run','tests_passed','unavailable_parent_count','skipped','failures','errors')},
          'related_unavailable_scope':'3 test cases plus1 setUpClass not counted in testsRun; four unmigrated image prerequisites',
          'linux_full':{key:full[key] for key in ('tests_run','tests_passed','historical_or_declared_skips','unavailable_records','unavailable_parent_count','failures','errors','complete_repository_validation')},
          'window':{'actual_Gold_windows':6,'actual_candidate_windows':14,'saved_native_records':160,'actual_original_numeric_calls':135,
              'full_healthy_Gold_pairs':6,'three_full_texts_compared':True,'authorized_save_RunState_reload_phases':5,'all_MainWindow_reopened':False,'actually_viewed_pngs':4,
              'gold_primary_exit':0,'candidate_primary_exit':0,'gold_elapsed_seconds':gold['elapsed_seconds'],'candidate_elapsed_seconds':window['elapsed_seconds']},
          'full_batch_next_after':105,'remaining_project_groups':18,'unresolved_mechanics_still_unknown':True},
      'completed_paragraph':summary+' 本节归档research/p2-section102-inventory-confirmation；P2三组真实机制与原生Windows/游戏链未完成。',
      'work_paragraph':'102专项与扩登记后的Linux full可用检查、实际窗口、Saved/视觉读回均已通过并归档，正在真正commit/push，随后103→104→105全量和总结。每节保存，原095三次未完成继续搁置。'}
with (base/'root-section102-save-spec-v1.json').open('x') as stream:json.dump(spec,stream,ensure_ascii=False,indent=2);stream.write('\n')
print(json.dumps({'spec_written':True,'public_evidence_entries':len(entries),'section':102}))
