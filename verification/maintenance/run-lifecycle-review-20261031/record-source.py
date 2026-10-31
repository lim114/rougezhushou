from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import difflib,json,runpy,subprocess,sys
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts')];BASE='23030ec53a21fc7c47253c7e65d30d0dfbb27581';B=R/'verification/maintenance/run-lifecycle-review-20261031';prefix=B.relative_to(R).as_posix()+'/'
def read(n):return json.loads((R/n).read_bytes())
def pin(n):
 p=R/n;raw=p.read_bytes();return {'path':p.relative_to(R).as_posix(),'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
def write(n,v):(R/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def text(n,value):
 p=R/n
 if not p.exists():p.parent.mkdir(parents=True,exist_ok=True);p.write_text(value,'utf8');return
 old=p.read_bytes().decode('utf8').splitlines(keepends=True);new=value.splitlines(keepends=True);out=list(new)
 for a,b,num in difflib.SequenceMatcher(None,[s.rstrip('\r\n')for s in old],[s.rstrip('\r\n')for s in new],autojunk=False).get_matching_blocks():
  for i in range(num):out[b+i]=old[a+i]
 p.write_bytes(''.join(out).encode('utf8'))
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==BASE
assert not subprocess.check_output(['git','diff','--name-only',BASE,'--','rouge']).strip()
source=['rouge/run_state.py','rouge/recipient_state.py','rouge/record_flags.py','rouge/training_view.py','rouge/player_team.py','rouge/app.py','rouge/account_cache.py','rouge/run_recognition.py','PROJECT_REQUIREMENTS.md']
for n in source:assert subprocess.check_output(['git','show',BASE+':'+n])==(R/n).read_bytes(),n
suite=read(prefix+'tests/results.json');process=read(prefix+'tests/process.json');transitions=read(prefix+'tests/comparisons.json')['comparisons'];assert suite['passed']and suite['tests_run']==89 and not suite['skipped']and not suite['forbidden_external_calls']and process['actual_observed_exit']==0 and len(transitions)==17
write(prefix+'source-review.json',{'baseline_commit':BASE,'source_files_unchanged':[pin(n)for n in source],'test_source':pin('tests/test_run_lifecycle_review.py'),'reviewed_chain':'RunState.apply/restore_origin_discovery_buffs, recipient_state merge/invalidation, presence and metadata projection, training_view selected inputs, MainWindow apply/sync/calculate and manual reset, TeamPanel roster qualification; inspected recognition marker source contract.','verified_transitions':transitions,'confirmed_scope':'Continuous E1 recruitment -> empty full popup -> targeted relic discovery -> promotion -> partial/full recipient popup -> E2/S3 training -> ordinary pages -> reload -> full-roster departure -> re-recruit; unknown origin discovery, partial roster, parent-relic loss, stale observation and old-run context after explicit temporary UI reset.','meaning':'State and calculation-input preservation, not independently calibrated game formulas or actual image recognition. Initial E1 max80/E2 max90 values use current pinned mechanist profile and are not a new model.','review_result':'No product defect reproduced in the covered transitions. Kept current source unchanged; did not manufacture a numerical or state change to count progress.','guards_retained':'Do not remove current-run identity/stale-input, unknown presence, positive/negative recipient evidence, source qualification or unreadable-file/non-overwrite protections solely because rare. Existing actual game and persistence permission gaps remain.','REA_scope':'Complete Python source directly reviewed per REA skill; no new REA invocation and no invented whole-program claim.','whole_program_complete':False})
title='本局招募、强化与重启连续链路回顾'
write(prefix+'summary.json',{'kind':'implementation_review_evidence_maintenance','title':title,'baseline_commit':BASE,'completed_sections':440,'functional_section_added':False,'production_source_changed':False,'reviewed_scope_passed':True,'related_unique_tests':89,'new_continuous_tests':3,'recorded_public_transition_rows':17,'test_receipt':pin(prefix+'tests/results.json'),'source_review':pin(prefix+'source-review.json'),'native_window_new_run':False,'reason_no_new_window_run':'Only tests and review documentation changed. Actual MainWindow methods execute with Windows QPA and temporary paths, but no new visible native/game/chat validation claimed. Existing unchanged test application remains open.','whole_program_complete':False,'whole_video_parity_complete':False,'P3_complete':False,'P2_complete':False,'P1_complete':False,'full_validation_rerun':False,'private_data_included':False,'game_operated':False,'chat_sent':False,'publication_binding':'enclosing maintenance commit; ordinary push and actual remote/blob equality required'})
text('research/run-lifecycle-review-20261031/README.md','''# 本局招募、进阶、定向强化与恢复的连续回顾

按REA技能直接阅读完整Python源码，本轮无新REA调用。沿RunState合并/历史修复、领取者正负证据、在队/未知资格投影、培养来源选择、MainWindow同步/计算、手动新局与队伍列表检查。识别来源只核对招募标记的字段契约，没有读取游戏或优化识别。完整Python源码不通过机械扫描PYC冒充逆向完成。

新增三条连续集成检查，调用实际MainWindow.apply_run_observation、培养选择、计算和临时手动重置；复用既有隔离设置，不另造计算器。第一条覆盖精一招募、完整未领取页、两件定向藏品、进阶、部分与完整领取页、补齐精二/三技能、本局页面复用、RunState重载、完整名单离队及重新招募。另两条覆盖首次来源确认不清强化、局部名单不确认离队、母藏品离开不抹已证强化、旧时间/旧局上下文拒绝和明确手动新局。保存17条公开输入后的实际计算输入与队伍投影；不是17个独立实机案例。机械师E1上限80/E2上限90来自当前固定培养资料，本轮不增加或修改机制。

实际89项不同相关检查退出0，无失败/错误/跳过；包含新3项、原状态同步、定向强化生命周期、来源发现修复、培养资格与只读队伍。验证临时路径、Windows QPA、输入不被修改、每次接受后计算一次最终输入、已证正向强化保留/不凭未读确认领取、晋升不猜模组与专精、再招募旧培养失效、历史前缀与同局身份保留。临时手动新局不接触用户本局；真实游戏、画面识别、机制准确性、跨系统文件权限和聊天未验收。

上述范围未复现产品缺陷，因此不改运行代码、不靠虚构缺陷或新增防御凑进度。当前按资格分离的来源、过期输入、未知在场、正负强化和不可读文件保护涉及真实记忆/准确性，不能仅因触发较少删除。其余本局地图/物品/资源连续输入、实际应急离队事件与持久化不可用范围仍需分开核对，不能由本次代替。完整程序与视频仍未完成，P3/P2/P1保留，识别最后。

本轮仅测试和审阅维护，不增加功能节数，仍440/未开441；原full440只对应旧冻结源码，完整选择器追加到711项。运行产品源码和项目要求整字节未变，保留上轮已打开的实际项目小窗，不为纯审阅重复重启。没有游戏操作、真实聊天、个人状态读取/复制/重置或上传。
''')
n='PROGRAM_REVIEW.md';t=(R/n).read_text('utf8');t+='\n[本局连续状态回顾](research/run-lifecycle-review-20261031/README.md)沿实际MainWindow重放招募、进阶、定向强化、重启、离队/再招募及明确临时新局，89项相关检查通过；未复现产品缺陷，未改运行源码。本局其它物品/地图/资源连续场景及实机、独立机制和全程序仍未完成。\n';text(n,t)
n='PROJECT_PROGRESS.md';t=(R/n).read_text('utf8');assert '补齐其余招募/强化/异常恢复的连续场景与独立机制依据'in t;t=t.replace('补齐其余招募/强化/异常恢复的连续场景与独立机制依据','补齐其它物品/地图/资源与异常恢复的连续场景、实际应急离队及独立机制依据');text(n,t)
entry=f'''<!-- run-lifecycle-review-20261031:start -->
## 实现回顾维护 · {title}

实际MainWindow到计算输入、队伍资格连续重放招募/进阶/部分与完整领取页/普通页复用/重启/完整名单离队/重新招募，以及来源首次确认、局部名单、母藏品移除和明确临时手动新局；保存17条实际输入投影，不当作独立实机案例。89项相关检查真实退出0，无跳过；未复现产品缺陷，运行源码和要求未改，不制造功能或防御改动凑节数。回执：`{prefix}summary.json`。

纯审阅保留已打开的原项目小窗，不重复重启/声称新原生验收；没有游戏、聊天或用户记录操作。其它物品/地图/资源/异常连续场景、实机应急事件与全程序/全视频仍未完成。功能440/未开441，P3/P2/P1未完成，识别最后。
<!-- run-lifecycle-review-20261031:end -->

'''
for n in ['WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md']:text(n,entry+(R/n).read_text('utf8'))
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']={'kind':'implementation_review_evidence_maintenance','title':title,'receipt':prefix+'summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_program_review_continuous_run_lifecycle','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False};cp['current_batch']['receipt']=prefix+'summary.json';cp['next_action']='继续完整程序回顾：其它物品移除/资源快照/跨层地图历史及异常恢复连续输入，核对可复用实现；完整数值/机制证据、其余窗口及全片外观/交互保持未完成。招募/强化到实际计算输入的已覆盖连续链路不重复计推进，实机应急离队仍需真实证据；识别最后。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');module=runpy.run_path(str(R/'scripts/update_cloud_index.py'));module['update'](R);assert module['validate_delivery'](R,cp)['current_section']==440
from scripts.verify_full_available import maintained_selectors
selectors=maintained_selectors();assert len(selectors)==711 and selectors[-1]=='tests.test_run_lifecycle_review';assert read('CLOUD_INDEX.json')['requirements']['sha256']==pin('PROJECT_REQUIREMENTS.md')['sha256']
write(prefix+'final-audit.json',{'passed':True,'baseline_commit':BASE,'source_review':pin(prefix+'source-review.json'),'summary':pin(prefix+'summary.json'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'cloud_index':pin('CLOUD_INDEX.json'),'ordered_selectors':711,'production_source_changed':False,'related_tests':89,'whole_program_complete':False,'whole_video_parity_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes());archive={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'};write(prefix+'archive-manifest.json',{'kind':'explicit_public_archive','files':archive})
print(json.dumps({'passed':True,'related_tests':89,'archive_files':len(archive),'goal_complete':False}))
