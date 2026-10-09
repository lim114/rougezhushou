"""Build103 public archive specification after all actual validations."""
import json
from pathlib import Path

base=Path('/workspace/.continuation');audit=json.loads((base/'root-resume103-saved-audit-v1.json').read_bytes())
related=json.loads((base/'resume103-related-v1.json').read_bytes())
gold=json.loads((base/'resume103-window-gold-v2/receipt.json').read_bytes());window=json.loads((base/'resume103-window-candidate-v2/receipt.json').read_bytes())
assert audit['passed'] and related['available_checks_passed'] and gold['passed'] and window['passed']
entries=[]
for name,destination in (
    ('section103-cache-recovery-candidate-source-v2','reviewed-product-source-v2'),
    ('section103-window-source-v2','reviewed-window-source-v2'),
    ('section103-window-source-v1','inactive-window-source-v1'),
    ('section103-original-origin-actual-linux-v2','actual-original-origin-linux-v2'),
    ('section103-original-squad-actual-linux-v2','actual-original-squad-linux-v2'),
    ('section103-original-squad-linux-probe-source-v2','original-squad-probe-source-v2'),
    ('section103-nested-consumer-source-audit-v1','original-origin-source-audit-v1'),
    ('resume103-window-gold-v2','actual-healthy-window-Gold-v2'),
    ('resume103-window-candidate-v2','actual-candidate-window-v2')):
    assert (base/name).is_dir(),name
    entries.append({'source':str(base/name),'destination':destination})
names=['root-section103-apply-v1.py','root-section103-apply-v1-INDEPENDENT_SOURCE_REVIEW.md',
       'root-section103-apply-v1.log','root-section103-apply-v1.exit-code','resume103-applied-source-v1.json',
       'root-resume103-related-v1.py','root-resume103-saved-audit-v1.py','root-resume103-saved-audit-v1.json',
       'root-resume103-saved-audit-v1.log','root-resume103-saved-audit-v1.exit-code','resume103-visual-audit-v1.json',
       'original100-public-source743-proof-v1.json','root-live-recovery-section103.json','root-section103-spec-builder-v1.py']
for prefix,suffixes in (
    ('resume103-related-v1',('.json','.log','.stdout.log','.exit-code')),
    ('resume103-selected-v1',('.log','.exit-code')),
    ('resume103-window-gold-v2',('.log','.exit-code')),
    ('resume103-window-candidate-v2',('.log','.exit-code')),
    ('section103-original-origin-actual-linux-v2',('.log','.exit-code')),
    ('section103-original-squad-actual-linux-v2',('.log','.exit-code'))):
    names.extend(prefix+suffix for suffix in suffixes)
for name in names:
    assert (base/name).is_file(),name
    entries.append({'source':str(base/name),'destination':'actual-evidence/'+name})
entries.append({'source':str(base/'section102-publication-v1.json'),'destination':'prior-publication.json'})
summary=('34个新增真实API方法已编入；相关234运行/232实际PASS/2历史缓存或图像不可用/0失败0错误，精选1291运行/1既有skip/0失败0错误。'
         'Wine九个Gold＋十九个候选窗口，358个保存native记录（244原数学成功＋30明确ValueError＋84快照/观察/重载），'
         '健康九组初始及观察后完整原生/三全文均一致，候选18合法保存＋1陈旧不写，28个close/direct RunState重载，四图已实际查看。')
readme=('# 第103节首次招募来源证据与分队缓存恢复\n\n'
        '只在消费旧金色来源证明前要求映射；坏来源叶子保原并能接受真实新观察，真实招募变化仍清除不再适用强化，合法旧金色修正仍保已有事实。'
        'confirmed_config只以字符串ID查询公共档案；只有已知ID、匹配名称和真正True可阻止更弱同名分队覆盖。坏ID的旧True不阻碍后续合法False-badge恢复；健康强化贸易分队仍保留。\n\n'+summary+
        '\n\n实际旧原API来源14cases与分队17cases都为观察workflow0/productFalse。分队是在真实full100 e839公共Git blobs重构的743+CORE树上运行；证据单独保留完整源码map，不能冒称当前102/103版本。Root现在实编自已push102的746到747，保留101/102修改、full21注册表和CORE，仅四个局部运输。\n\n'
        '原数字API对坏分队仍明确拒绝，30次原ValueError及输入原件保留；合法新观察后的19个数学结果可正常格式化。所有真实数值caller和live snapshot保留类型、浮点位、dict顺序与双向alias。'
        'JSON重载正确使用完整实际磁盘JSON类型/位/顺序oracle，JSON不保跨字段内存alias；live native独立保留。没有声称全部MainWindow重开、自然OCR产生坏状态、全局schema或原生Windows/游戏/客户端聊天通过。\n\n'
        '旧window Source10da v1未执行，因将JSON重载与live alias严格比较会误报而由独立Source审阅拦下；freshc2eafe v2在Root开跑前修齐、独审并实际一次通过。不得将未执行Source阻断计产品失败，也不抹旧原件。'
        '坏来源恢复截图只展示真实摘要，来源字段恢复由native证据证明；坏分队的原拒绝文本、恢复后有效名称和强化贸易保留均实际可见。\n\n'
        '每节commit/push，105后五节全量与进度总结。P2三组机制及原生连续采样证据仍待查证，18待办组未销为完成。')
spec={'section':103,'source_guard':str(base/'resume103-applied-source-v1.json'),
      'exit_files':[str(base/name) for name in ('root-section103-apply-v1.exit-code','resume103-related-v1.exit-code',
           'resume103-selected-v1.exit-code','resume103-window-gold-v2.exit-code','resume103-window-candidate-v2.exit-code','root-resume103-saved-audit-v1.exit-code')],
      'pass_receipts':[str(base/name) for name in ('resume103-window-gold-v2/receipt.json','resume103-window-candidate-v2/receipt.json','root-resume103-saved-audit-v1.json')],
      'public_evidence':entries,'archive':'research/p2-section103-cache-recovery','topic':'来源证据消费和分队缓存合法恢复',
      'previous_publication':str(base/'section102-publication-v1.json'),
      'next_action':'103真实commit/push后继续104资源观察完整值保存资格与安全恢复；随后105物理测试登记收口和真实字体fixture、五节Linux/Wine/window全量和总结，再自动下一组。',
      'archive_readme':readme,'section_receipt':{'implemented_scope':['Legacy source proof mapping qualification before correction check','String squad ID before confirmed-config lookup','Known matched true squad proof preserves original stronger facts without blocking bad-cache repair'],
          'new_test_methods':34,'related':{key:related[key] for key in ('tests_run','tests_passed','unavailable_parent_count','skipped','failures','errors')},
          'selected':{'tests_run':1291,'skipped':1,'failures':0,'errors':0},'window':audit,
          'gold_elapsed_seconds':gold['elapsed_seconds'],'candidate_elapsed_seconds':window['elapsed_seconds'],
          'original_origin_cases':14,'original_squad_cases':17,'original_product_pass':False,'live_alias_preserved_by_JSON_claimed':False,
          'full_batch_next_after':105,'remaining_project_groups':18},
      'completed_paragraph':summary+' 已应用来源证据资格、分队ID资格及旧强事实保护的三处修复，四份局部运输。归档research/p2-section103-cache-recovery；P2实际机制待办仍保留。',
      'work_paragraph':'103专项真实回归、九Gold/十九候选窗口、原件与视觉读回通过，正在真正commit/push；依序104资源观察准入（44原API实际观察已封存但未修复），105登记收口及可用全量/总结。每节保存，原095搁置/native边界不变。'}
with (base/'root-section103-save-spec-v1.json').open('x') as stream:json.dump(spec,stream,ensure_ascii=False,indent=2);stream.write('\n')
print(json.dumps({'section':103,'spec_written':True,'public_evidence_entries':len(entries)}))
