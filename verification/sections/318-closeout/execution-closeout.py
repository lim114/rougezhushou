from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone,timedelta
import json,runpy,sys,shutil
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
def read(n):return json.loads((ROOT/n).read_bytes())
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
def pin(n):return {'receipt':n,'sha256':sha(n)}
def doc(n,s):
 p=ROOT/n;style='\r\n'if b'\r\n'in p.read_bytes()else'\n';p.write_bytes(s.replace('\r\n','\n').replace('\n',style).encode('utf8'))
title='当前通关基础奖励、特殊入口与历史经验参考分开核对'
change='当前关卡预览新增“通关基础奖励”页，原前五页签不变。按固定441984原文解析六行区域与18条特殊入口奖励，分别显示可核对的当前基础源石锭、通常追猎零经验/一张招募券条款及明确标注的旧版经验参考；基础经验与满科技经验未分离的拼接文本不当当前经验计算，也不默认账号满科技。入口与区域独立对照，同名事件与通常追猎分项不相加，陌生旅伴2至3源石锭保留范围，不取中点。秘境仅沿用文献明确的普通/紧急原关卡分项，盲目者所见不借用同层源流表，余径基础结算保留未知并单列普通作战额外1件藏品条件。支持全部184配置的资料/未知状态；不支持的具名入口、空值不当零。刷新保留声明、页签和阅读状态，坏源清除当前/历史数值，单个来源失效不冒称其它关卡资料失败。玩家页使用普通中文，技术来源独立保存。'
limits='这是文献中的条件基础分项，不是完整结算或实际领取。当前非零指挥经验的两种显示模式仍未独立取得原始结构，旧修订433770由原HTML重建逐项核对后只作历史参考；不得把1013当1013经验，也不将旧值升级为当前数据。当前原始结构下载三次失败，保留curl Schannel/两种raw地址的失败和恢复条件，停止无新线索重试。固定当前纯文本441984复用实际316 Scrape，不冒称本批新下载HTML或当前服务器已验证。余径/隐藏第六层未列出的基础奖励、灰坑等未列入口奖励、所有难度/分队/科技/藏品/零件及无漏怪条件修正、完整收藏品/零件/招募券池与实际结算仍未知。通常追猎的零值不是其它入口或完整奖励零值；源石锭范围不提供概率。未改本局库存或旧模型，不操作游戏、不发送聊天。P3/P2/P1均未完成，原图完整映射与其它事件条件缺口保留，识别优化最后。'

necessary='verification/sections/318-necessary-attempt2/process.json';native='verification/sections/318-native-attempt2/actual/window.json';process='verification/sections/318-native-attempt2/process.json';source='verification/sections/318-source-attempt2/process.json';visual='verification/sections/318-root-visual.json';main='verification/sections/318-main-window.json';reg='verification/sections/318-preparation/maintained-registration.json'
n,w,p,s,v,m=(read(x)for x in(necessary,native,process,source,visual,main))
assert n['passed']and n['exit_code']==0 and n['methods_ran']==61
assert w['passed']and w['unique_checks']==28 and w['qpa']=='windows'and w['qt_exit_code']==0 and w['verification_window_closed']
assert len(w['actual_readings'])==8 and len(w['same_identity_refresh_observations'])==2
assert all(x==0 for x in w['external_operation_attempts'].values())and p['passed']and p['window_receipt_sha256']==sha(native)
assert s['passed']and s['exit_code']==0
for value in(n,w,s):
 assert value['source_sha256_before']==value['source_sha256_after']
 for name,digest in value['source_sha256_after'].items():assert sha(name)==digest,name
assert v['all_reviewed']and len(v['images'])==7
for image in v['images']:assert image['root_viewed']and sha(image['file'])==image['sha256']
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
rr=read(reg);assert rr['before_count']==501 and rr['after_count']==504 and rr['original_ordered_prefix_unchanged']and rr['source_sha256']==sha('scripts/verify_full_available.py')
from rouge import current_settlement_reference as model
ref=model.packet();assert ref is not None
scope={'game_commit':model.directory.version.NEW_COMMIT,'community_revision':'441984','historical_experience_revision':'433770','source_transport':'previous actual Windows-mcp Scrape selected current table and pursuit clause; old original HTML reconstructed for historical split only','supported_stage_refs_with_unknowns':184,'main_table_rows':6,'named_special_table_rows':18,'current_nonzero_experience_modes_verified':False,'historical_experience_auto_applied':False,'full_account_technology_assumed':False,'three_original_structure_downloads_failed_and_deferred':True,'complete_actual_settlement_verified':False,'actual_current_server_verified':False,'actual_run_memory_updated':False}
out=ROOT/'verification/sections/318-preparation';shutil.copyfile(ROOT/'.cache/open_test_window_318.py',out/'execution-main-window.py');(out/'source-scope.json').write_bytes(enc(scope))
usage=read('verification/sections/318-preparation/usage-final.json');assert usage['remainingPercent']>=15
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section318-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':318,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development',
 'necessary_validation':{**pin(necessary),'methods_run':61,'actual_exit':0},'native_windows_validation':{**pin(native),'process':pin(process),'unique_checks':28,'actual_Qt_exit':0,'actual_source_readings_and_jumps':8,'real_nonzero_refresh_states':2,'actual_MainWindow_compact_viewport':True,'actual_MainWindow_entry_exercised':True,'all_seven_real_external_operations_zero':True},
 'source_build':pin(source),'root_visual_review':pin(visual),'original_project_window':pin(main),'maintained_registry':pin(reg),'source_manifest':pin(model.MANIFEST),
 'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'source_scope':scope,
 'failed_product_validation_attempts':[],'source_failure_history':[pin('research/p3-current-settlement-318/original-download-failures.json')],
 'failure_explanation':'Necessary1/native1 passed before player-facing wording was simplified; both original passing receipts retained. Final necessary2/native2 bind the final source. Direct builder preparation first lacked project import path and was repaired before validation; three source download failures are separate unresolved evidence, not product-test passes.',
 'full_suite_rerun':False,'last_full_receipt':'verification/full-305/summary.json','last_full_source_is_historical305':True,'next_periodic_full_section':320,'P3_complete':False,'P2_complete':False,'P1_complete':False,
 'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False}
(ROOT/'verification/sections/318.json').write_bytes(enc(r))
validation='实际61项必要检查、28项Windows原生唯一检查通过；实际MainWindow打开对应当前关卡并进入新增基础奖励页，8组入口/区域阅读涵盖通常作战、秘境、同名事件/追猎、范围、隐藏第六层、余径和灰坑；两组非零滚动选区保持及真实公开文件损坏清旧/手动重验通过。七张最终实际截图均已查看；七类游戏采样/聊天/凭证调用零次，临时本局与旧计算上下文不变。501维护选择器原序保持，现504；原项目窗口正常更新并可见响应，关闭至启动的私人五路径不变。首轮已通过回执保留，简化玩家措辞后重新验证并绑定最终源码。未重跑全量，305仅历史范围，下次定期全量320；符号链接1314、历史私样本、Linux/Wine及游戏聊天未计通过。'
details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
for name in('PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md'):
 text=(ROOT/name).read_text('utf8')
 if name=='WORK_IN_PROGRESS.md':assert text.startswith('## 正在进行第318节');text=text[text.index('## 第317节'):]
 doc(name,'## 第318节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述318为准。\n\n'+text)
text=(ROOT/'AGENTS.md').read_text('utf8');end=text.index('\n## ',3);doc('AGENTS.md','## 当前续接 · 第318节 + '+title+'\n\n'+details+'\n\n继续P3，后续319优先新事件前置/作战与地图入口、完整奖励池和原图映射的剩余缺口。严格低于15%才开始完整收尾，下次定期全量320。\n'+text[end:])
text=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');a=text.index('<!-- current-delivery:start -->');marker='<!-- current-delivery:end -->';b=text.index(marker)+len(marker)
doc('PROJECT_REQUIREMENTS.md',text[:a]+'<!-- current-delivery:start -->\n## 第318节 + '+title+'\n\n'+details+'\n'+marker+text[b:])
text=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');text=text.replace('完整奖励池与发放条件（含','当前非零经验两种显示模式的原始依据、隐藏第六层/余径与未列具名入口基础结算、所有额外奖励修正及完整奖励池与发放条件（含',1);doc('PROJECT_PROGRESS.md',text)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==317 and cp['next_section']==318
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout','active_section'):
 if key in cp:cp['historical_before318_'+key]=cp.pop(key)
cp.update(completed_sections=318,latest_functional_section=318,next_section=319,batch_status='P3_SECTION318_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第318节 + '+title+'已本地验收。普通推送核对后接续事件前置/作战入口、完整奖励池和原图映射；319未启动，下一定期全量320。')
cp['sections'].append({'number':318,'completion_ref':'p3-section-318','topic':title,'verification':'verification/sections/318.json'});cp['functional_sections_since_latest_requirement'].append(318)
cp['current_section_save']={'section':318,'verification':'verification/sections/318.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':318,'receipt':'verification/sections/318.json','necessary_methods_passed':61,'native_isolated_window_checks':28,'actual_source_readings_and_jumps':8,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-305/summary.json','full_source_is_historical305':True}
cp['latest_section_environment']={'section':318,'receipt':'verification/sections/318.json','native_windows':'61 necessary;28 native actual MainWindow/current base reward checks;8 readings and2 nonzero states;original app/private5 preservation verified','native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-305/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=318,next_section=319,next_section_started=False,receipt='verification/sections/318.json',batch_closed=False)
cp['policy'].update(current_usage_remaining_percent=usage['remainingPercent'],current_usage_receipt='verification/sections/318-preparation/usage-final.json')
cp['current_data_versions'].update(current_settlement_game_commit=model.directory.version.NEW_COMMIT,current_settlement_source_manifest=model.MANIFEST,current_settlement_community_revision='441984',historical_experience_reference_revision='433770',current_settlement_nonzero_experience_verified=False,current_settlement_complete_rewards_verified=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section318-handoff:start -->\n## 第318节 + '+title+'\n\n'+details+'\n<!-- section318-handoff:end -->\n')
import subprocess
p=ROOT/'WORK_IN_PROGRESS.md';current=p.read_bytes();old=subprocess.check_output(['git','show','1175e2f02c8a887a25a98c0e11441f109284f8de:WORK_IN_PROGRESS.md'],cwd=ROOT);marker='## 第317节'.encode();at=current.index(marker);assert current[at:].decode().replace('\r\n','\n')==old.decode().replace('\r\n','\n');prefix=current[:at].decode().replace('\r\n','\n').replace('\n','\r\n');p.write_bytes(prefix.encode()+old)
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/318-closeout';out.mkdir();(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':318,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next319_started':False,'at_Beijing':now}))
print(json.dumps({'section_label':read('CLOUD_INDEX.json')['current_section_label'],'scope':scope,'publication_pending':True},ensure_ascii=False))
