"""Root-only explicit public archive plan; no project API invocation."""
import json, pathlib
B=pathlib.Path('/workspace/.continuation'); entries=[]
def add(source,destination):
 p=B/source;assert p.exists(),p
 entries.append({'source':str(p),'destination':destination})
for source in ['section109-empty-target-original-probe-source-v1','section109-permanent-release-original-probe-source-v1','section109-generic-instant-supplement-source-v1','section109-bounded-empty-candidate-source-v2','section109-window-source-v1','section109-window-source-v2','section109-window-source-v3','section109-window-source-v4']:
 add(source,'Source/'+source)
for phase in ['original','candidate']:
 for domain in ['focused','permanent','instant']:
  s=f'section109-{phase}-{domain}-actual-v1'
  add(s+'/native','actual/'+s+'/native')
  add(s+'/observations.json','actual/'+s+'/observations.json')
  for suffix in ['.log','.exit-code']:add(s+suffix,'actual/'+s+suffix)
for s in ['resume109-window-gold-v1','resume109-window-candidate-v1','resume109-window-candidate-v2']:
 add(s+'/records','actual/'+s+'/records');add(s+'/receipt.json','actual/'+s+'/receipt.json')
 for suffix in ['.log','.exit-code']:add(s+suffix,'actual/'+s+suffix)
 for leaf in sorted((B/s).glob('*.png')):add(s+'/'+leaf.name,'actual/'+s+'/'+leaf.name)
for s in ['resume109-baseline-selected-v1','resume109-focused-tests-linux-v1','resume109-focused-tests-linux-v2','resume109-focused-tests-wine-v1','resume109-selected-linux-v1','root-section109-apply-v1','resume109-candidate-apis-v1','root-section109-saved-paired-audit-v1','root-section109-saved-paired-audit-v2','root-section109-window-saved-audit-v1']:
 for suffix in ['.log','.exit-code']:add(s+suffix,'actual/'+s+suffix)
for s in ['resume109-original-source-v1.json','resume109-applied-source-v1.json','root-public-probe109-v1.py','root-section109-apply-v1.py','root-section109-saved-paired-audit-v1.py','root-section109-saved-paired-audit-v2.py','root-section109-saved-paired-audit-v2.json','root-section109-window-v3-source-check.json','root-section109-window-v4-source-check.json','root-section109-window-saved-audit-v1.py','root-section109-window-saved-audit-v1.json','root-section109-visual-readback-v1.json']:
 add(s,'root/'+s)
add('section108-publication-v1.json','prior-publication.json')
add('resume109-window-candidate-v3.log','actual/resume109-window-candidate-v3.log')
add('root-section109-window-complete-plan-source-v1.py','Source/root-section109-window-complete-plan-source-v1.py')
for script in ['root-section-publish-v3.py',pathlib.Path(__file__).name]:add(script,'root/'+script)
window=json.loads((B/'resume109-window-candidate-v2/receipt.json').read_text());assert not window['passed'] and len(window['rows'])==15 and len(window['pngs'])==3
proof=json.loads((B/'root-section109-window-saved-audit-v1.json').read_text());assert proof['passed'];visual=json.loads((B/'root-section109-visual-readback-v1.json').read_text());assert visual['passed'] and len(visual['images'])==3
spec={'section':109,'source_guard':str(B/'resume109-applied-source-v1.json'),'archive':'research/p2-section109-empty-owner-acquisition','topic':'敌方空供靶与独立来源归属修复','public_evidence':entries,'previous_publication':str(B/'section108-publication-v1.json'),'exit_files':[str(B/(s+'.exit-code')) for s in ['resume109-baseline-selected-v1','resume109-focused-tests-linux-v2','resume109-focused-tests-wine-v1','resume109-selected-linux-v1','root-section109-apply-v1','resume109-candidate-apis-v1','resume109-window-gold-v1','root-section109-saved-paired-audit-v2','root-section109-window-saved-audit-v1']], 'pass_receipts':[str(B/'root-section109-saved-paired-audit-v2.json'),str(B/'root-section109-window-saved-audit-v1.json')],
'archive_readme':'第109节实际功能：普通敌方continuous空供靶、独立单位自己的空范围、无窗弹药与友方治疗回退、手填屏障持续时间、泛用与灵知瞬发入口。原82与候选82公开API全返回值/原始caller及格式化文本保存；40永久释放/SP全返回值保持原版，留110修复。仅公开合成输入，临时账号/本局目录不归档。真实Wine窗口非原生Windows。原错误module选择、Saved配对formatter输入误判、两次窗口断言失败与第三次环境中断全部保留；完整候选窗口三次后搁置，缺尾两快照/close/第四图，不宣称18PASS。',
'section_receipt':{'functional_progress':['敌方空供靶排除普通连续攻击，独立单位只消费自身范围','弹药完整声明不覆盖空实际stream，友方回退按明确受疗人数保留','手填屏障持续时间实际普通伤害消费空供靶而独立爆炸/结束仍未知','两条泛用开启瞬发及灵知S2统一空供靶'], 'new_test_methods':22,'linux_related':{'run':118,'failures':0,'errors':0},'wine_related':{'run':118,'failures':0,'errors':0},'linux_selected':{'run':1379,'skipped':1,'failures':0,'errors':0},'original_selected':{'run':1357,'skipped':1},'public_API':{'original_cases':82,'candidate_cases':82,'candidate_consumer_calls':246,'full_numeric_callers_paired':82,'saved_records_decoded':656,'permanent_whole_returned_values_identical':120},'real_MainWindow':{'gold_rows':18,'candidate_completed_prefix_rows':15,'full_candidate_workflow_passed':False,'healthy_whole_Gold':5,'completed_intentional_change_snapshot_contracts':10,'gold_windows':1,'candidate_completed_close_reload_windows':0,'candidate_numeric_calls':window['actual_numeric_calls'],'actual_candidate_attempts':3,'initial_failures':['visual anchor absent; functional rows6; raw1 retained','UI snow_entries0 differs from API entries2; exact known total0 and unknown phase/cycle/recharge preserved; raw1 retained'],'source_and_CORE_unchanged':True},'root_window_saved_audit':proof,'actual_visual_images':visual['images'],'command_failure_history':['Linux initial three nonexistent selectors raw1; corrected118PASS','Saved v1 compared changed formatter inputs between versions; pure v2 corrected numericcaller pairing','candidate window first raw1 absent visual title; second raw1 wrong zero-entry snow total expectation; third interrupted by exec-server transport disconnect/X termination/Wine page fault; primary NULL; deferred after3'], 'unknown_boundaries':['永久continuous空目标与释放/SP分离留110','正continuous范围保持原参考，不补原生时钟','开启后独立机制/完整尾段不完整保持None','逐formatter独立purity未做','nativeWindows/game/chat未验']},
'next_action':'继续第110节永久技能连续释放/SP与敌方命中分离实际功能，完成本组全量Linux/Wine/window和进度总结。此批至115功能＋全量及外部算例核对后结束。',
'completed_paragraph':'敌方空供靶/独立来源归属功能共同完成；新增22方法，Linux/Wine定向各118、Linux精选1379/skip1，原候选各82API通过；真实18Gold与候选15完成前缀已读回，完整候选窗口三次后搁置。40永久参照完整保持原，未知友方/后续时钟不填。原失败记录保留，实际已存Saved全部读回和三图查看（数字在下缘，未称全图数值验收）；正在真实提交推送。',
'work_paragraph':'109验收完成并存档，继续110永久释放/SP分离后执行五节可用全量与总结；再推进111触手完整技能弹道尾段及后续有依据的P2状态功能。115全量加入公开网上算例准确性检验后结束本批。每节需功能实绩、检验、保存和推送；P2未完成、旧95搁置及native边界保持。'}
out=B/'root-section109-save-spec-v1.json'
with out.open('x') as f:json.dump(spec,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'section':109,'public_evidence_entries':len(entries)}))
