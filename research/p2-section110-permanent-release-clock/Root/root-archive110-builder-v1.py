"""Root serial final archive preparation; requires actual completed full110 receipts."""
import json,hashlib,datetime
from pathlib import Path
B=Path('/workspace/.continuation');R=Path('/workspace/rougezhushou')
def read(p):return json.loads(p.read_bytes())
def ref(p):
 b=p.read_bytes();return {'path':str(p),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
g=read(B/'resume110-applied-source-v2.json');assert g['section']==110 and len(g['source_sha256'])==753
for n,s in g['source_sha256'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==s
for n,s in g['source_additional_sha256'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==s
linux=read(B/'full110-linux-actual-v1.json');wine=read(B/'full110-wine-actual-v2.json');selected=read(B/'full110-wine-selected-actual-v1.json');ui=read(B/'full110-window-actual-v1/wine-ui-100.json');small=read(B/'resume110-window-specialized-v1/receipt.json');saved=read(B/'root-window110-saved-actual-v1/receipt.json');fullsaved=read(B/'root-full110-saved-audit-v1.json');visual=read(B/'root-full110-visual-actual-v1.json');sup=read(B/'full110-window-actual-v1.supervisor.json')
for d in (linux,wine):assert d['available_checks_passed'] is True and d['failures']==d['errors']==0 and not d['source_drift']
assert selected['passed'] and not selected['source_drift'];assert ui['passed'] and ui['complete_ui_validation'] and ui['total_actual_checks']==4283
assert small['passed'] and small['workflow_complete'] and saved['passed'] and saved['workflow_checks_passed']
assert fullsaved['passed'] and fullsaved['workflow_complete'] and visual['passed'] and visual['workflow_complete']
assert sup['child_primary_exit']==sup['supervisor_exit']==0 and not sup['timed_out'] and sup['owned_session_closure']['no_live_owned_execution_verified']
exits=[B/name for name in ['section110-original-permanent-actual-v2.exit-code','section110-original-supplement-actual-v1.exit-code','section110-candidate-permanent-actual-v1.exit-code','section110-candidate-supplement-actual-v1.exit-code','root-section110-apply-v1.exit-code','root-section110-api-saved-audit-v1.exit-code','full110-linux-actual-v1.exit-code','full110-wine-actual-v2.exit-code','full110-wine-selected-actual-v1.exit-code','resume110-window-specialized-v1.exit-code','root-window110-saved-actual-v1.exit-code','full110-window-actual-v1.exit-code','root-full110-saved-audit-v1.exit-code','full110-linux-pip-actual-v1.exit-code','full110-wine-pip-actual-v1.exit-code']]
assert all(p.read_bytes()==b'0\n' for p in exits)
closure={'kind':'ROOT_ACTUAL_FULL110_AVAILABLE_SCOPE_CLOSURE','passed':True,'workflow_complete':True,'source_drift':[],'after_section':110,'source_files':753,'complete_repository_validation':False,'native_windows_game_chat_verified':False,'linux':{k:linux[k]for k in ['tests_run','tests_passed','historical_or_declared_skips','unavailable_records','unavailable_parent_count','failures','errors']},'wine':{k:wine[k]for k in ['tests_run','tests_passed','historical_or_declared_skips','unavailable_records','unavailable_parent_count','failures','errors']},'wine_selected_run':selected['tests_run'],'legacy_gui_checks':4283,'legacy_saved_states':52,'specialist_gui_states':12,'specialist_current_SP_pairs':6,'specialist_native_records':116,'specialist_three_full_texts':36,'actual_PNGs_viewed':6,'deferred095_and109_preserved':True,'scope':'Current maintained available selectors + unchanged bounded legacy functional matrix + specialized permanent-skill 12states. Missing migration evidence, historical skips and3 diagnosed Wine capability bodies are not PASS. Original88 APIs compare1numeric+2formatters; specialist Window separately has3wholeformattertexts. No old095 complete vector or original full GUI Gold claim.'}
cp=B/'root-full110-closure-v1.json';assert not cp.exists();cp.write_text(json.dumps(closure,ensure_ascii=False,indent=2)+'\n')
entries=[]
def add(p,d):
 assert p.is_file() and not p.is_symlink();entries.append({'source':str(p),'destination':d})
def public_dir(name,destination,allowed=None):
 p=B/name
 for f in sorted(p.rglob('*')):
  if f.is_file() and '__pycache__' not in f.parts and 'public-state' not in f.parts:
   rel=f.relative_to(p)
   if allowed is None or rel.parts[0] in allowed:add(f,destination+'/'+rel.as_posix())
for name in ['section109-permanent-release-original-probe-source-v1','section110-permanent-release-candidate-source-v1','section110-permanent-release-candidate-source-v2','section110-tests-contract-correction-source-v1','section110-window-source-v1','section110-window-saved-readback-source-v1','full110-suite-adapters-source-v1','full110-bounded-window-source-draft-v1','full110-bounded-window-source-active-v1']:
 public_dir(name,'Source/'+name)
for name in ['section110-original-permanent-actual-v2','section110-original-supplement-actual-v1','section110-candidate-permanent-actual-v1','section110-candidate-supplement-actual-v1']:
 public_dir(name,'API/'+name);add(B/(name+'.log'),'API/'+name+'.log');add(B/(name+'.exit-code'),'API/'+name+'.exit-code')
public_dir('resume110-window-specialized-v1','Window/specialized');public_dir('root-window110-saved-actual-v1','Window/specialized-saved')
# Synthetic private runtime folders are not inferred; legacy public retained evidence only.
legacy=B/'full110-window-actual-v1'
allowed={'wine-ui-100.json','source100-guard-input.json','full110-progress.json',ui['new_state_archive090']['file'],*(x['file']for x in ui['screenshots100'])}
for name in sorted(allowed):add(legacy/name,'Window/full/'+name)
for p in sorted(B.iterdir()):
 if p.is_file() and (p.name.startswith(('resume110-','root-section110-','full110-','root-full110-','root-window110-')) or p.name in ['root-public-probe109-v1.py','root-apply-local-transport-v1.py','section110-permanent-release-independent-source-v1.json','section110-tests-contract-correction-independent-source-v1.json','root-archive110-builder-v1.py']):
  add(p,'Root/'+p.name)
add(B/'section109-publication-v1.json','prior-publication.json')
assert len({e['destination']for e in entries})==len(entries)
summary='第106–110节已完成实际功能修复：环境适用资格与来源报告、派生重量与天赋共同消费、本局区域输入资格、敌方空供靶与独立来源归属，以及永久技能释放/SP时钟分离；逐节均按实际检验保存。110闭合后继续111召唤物施放尾段、112新局采样视图、113弹药观察窗口、114数值输入资格、115普通报告分项。115全量和公开算例实际核对后结束此批次。'
archive='research/p2-section110-permanent-release-clock'
spec={'section':110,'source_guard':str(B/'resume110-applied-source-v2.json'),'archive':archive,'topic':'永久技能空供靶释放与技力时钟分离','public_evidence':entries,'exit_files':list(map(str,exits)),'pass_receipts':[str(cp),str(B/'root-section110-api-saved-audit-v1.json'),str(B/'root-window110-visual-actual-v1.json'),str(B/'root-full110-saved-audit-v1.json'),str(B/'root-full110-visual-actual-v1.json')],'previous_publication':str(B/'section109-publication-v1.json'),'section_receipt':{'functional_changes':['永久技能连续模式空供靶保留原释放时钟且不计敌方命中','充能与SP事件使用已释放攻击而非空命中流','保持S1独立未定位音符、S2未知切换/回转、培养与其他时钟原行为'],'original_candidate_API_cases':88,'API_full_SP_pairs':88,'API_native_records_read':704,'API_formatter_count_per_case':2,'final_new_test_methods':23,'full_available_validation':closure,'failures_retained':['原probe错误filename raw1','首次related F2/E8：7合同错误+1不存在模块，原件保留','修正related缺两份迁移样本 raw1','首次Winefull cwd/font raw1；已修启动配置，重跑实际raw0'],'native_windows_verified':False},'archive_readme':summary+'\n\n所有退出码、源码候选/修正、原观察和实际Saved证据公开保留。可用范围PASS不代表缺失样本、本机Windows/游戏/聊天或旧95/109完整窗口已通过。','next_action':'依序开始111–115实质功能；115全量+实际外网算例核对完成后结束批次','completed_paragraph':summary+'具体实际检查见verification/full-110和本节归档；原source guard753+CORE前后一致。','work_paragraph':'第110节实际功能及本批可用范围检验已闭合，准备本节真实commit/push。下一节111先记录实际原公开API再应用局部修复。已搁置的95/109窗口不作通过，客户端与未迁移数据仍待其真实条件。'}
p=B/'root-section110-save-spec-v1.json';assert not p.exists();p.write_text(json.dumps(spec,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'section':110,'explicit_public_leaves':len(entries),'archive_preparation_only':True}))
