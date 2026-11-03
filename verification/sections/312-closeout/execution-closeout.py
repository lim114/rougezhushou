from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone, timedelta
import json,runpy,subprocess
ROOT=Path(__file__).resolve().parents[1]
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def read(n):return json.loads((ROOT/n).read_bytes())
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
def pin(n):return{'receipt':n,'sha256':sha(n)}
def write_doc(n,s):
 # Existing document bytes use CRLF. Preserve that style without doubling carriage returns.
 p=ROOT/n;style='\r\n'if b'\r\n'in p.read_bytes()else'\n';p.write_bytes(s.replace('\r\n','\n').replace('\n',style).encode('utf8'))
title='德莱昂两个版本与赤金条的起飞、劫掠和退场条件'
change='光荣远征的德莱昂与赤金条、赤金厄运的“征服者”德莱昂新增三个精确资料入口。四组中文说明分开解释受伤起飞、降落、两版轰炸移速、劫掠增益、满载而归，以及赤金条触发成功后死亡和抵达终点后的自然物奖励条件。完整六张技能卡、三张能力卡及术语原件保留，不按参数名称或数组顺序猜测未绑定招式。三个对应原图、主题选择与技术详情可读；同来源刷新保留页签、滚动和选区，换身份或来源失效清空，恢复后手动重开。'
limits='本节为固定文献阅读，不是实际状态或数值预测。近地悬浮仍按文献采用地面寻路，具体地块中心判定保留存疑；10秒后尝试降落不等于恰好第10秒落地，起飞冷却不等于完整周期。赤金厄运固定引用未列赤金条不证明动态绝不出现；第0.1秒的历史检查不能由当前是否在场反推。赤金条攻击尝试、成功触发、首领退场、自身死亡、终点和战后奖励分别保留，不新增奖励数量或概率。未匹配的原始技能参数不当伤害公式。实际触发/面板/位置/时钟/奖励发放与当前服务器仍未知。两张高台图的首次边界测量均零候选，失败保留且地图能力未增加；81关59图完整校准及其余节点/掉落/首领缺口、P3/P2/P1均未完成。'
necessary='verification/sections/312-necessary-attempt2/process.json';native='verification/sections/312-native-attempt1/actual/window.json';native_process='verification/sections/312-native-attempt1/process.json';source='verification/sections/312-source-attempt1/process.json';visual='verification/sections/312-root-visual.json';main='verification/sections/312-main-window.json'
n,w,p,s,v,m=(read(x)for x in(necessary,native,native_process,source,visual,main))
assert n['passed']and n['exit_code']==0 and n['methods_ran']==84
assert w['passed']and w['unique_checks']==31 and w['qpa']=='windows'and w['qt_exit_code']==0 and w['verification_window_closed']
assert len(w['actual_entry_overviews'])==3 and len(w['actual_topic_readings'])==12 and len(w['same_identity_refresh_observations'])==6
assert all(value==0 for value in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(native)
assert s['passed']and s['exit_code']==0
for report in(n,w,s):
 assert report['source_sha256_before']==report['source_sha256_after']
 for name,digest in report['source_sha256_after'].items():assert sha(name)==digest,name
assert v['all_reviewed']and len(v['images'])==5
for image in v['images']:assert image['root_viewed']and sha(image['file'])==image['sha256']
assert m['passed']and m['window_visible_and_responsive']and m['private_entire_normal_close_and_start_interval_unchanged']
reg='verification/sections/312-preparation/maintained-registration.json';registry=read(reg)
assert registry['before_count']==484 and registry['after_count']==487 and registry['original_ordered_prefix_unchanged']
assert registry['source_sha256']==sha('scripts/verify_full_available.py')
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==311 and cp['next_section']==312
assert cp['policy']['new_functional_sections_paused']is False and cp['policy']['pause_after_active_section_requested']is False
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section312-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
manifest=read('research/p3-gold-boss-312/source-manifest.json')
r={'section':312,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development',
 'necessary_validation':{**pin(necessary),'methods_run':84,'actual_exit':0},
 'native_windows_validation':{**pin(native),'process':pin(native_process),'unique_checks':31,'actual_Qt_exit':0,'exact_entries':3,'actual_topic_readings':12,'actual_nonzero_refresh_reading_states':6,'eight_external_operation_attempts_zero':True},
 'root_visual_review':pin(visual),'original_project_window':pin(main),'source_build':pin(source),
 'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'maintained_registry':pin(reg),'source_manifest':pin('research/p3-gold-boss-312/source-manifest.json'),
 'source_scope':{'exact_targets':[['ro6_b_2','enemy_2140_shsgzd',0],['ro6_b_2','enemy_2142_shsggd',0],['ro6_b_2_b','enemy_2141_shsgz2',0]],'complete_public_revisions':[x['revision']for x in read('research/p3-gold-boss-312/http-source-records.json')],'skill_cards':6,'ability_cards':3,'conditional_reading_topics':4,'fresh_runtime_members':len(manifest['runtime_files']),'complete_current_stages':2,'complete_current_skill_definitions':3,'selected_current_bindings':3,'whole_database_and_levels_build_only':True,'current_server_or_actual_modes_verified':False,'no_named_engine_mapping_inferred':True},
 'earlier_necessary_validation':pin('verification/sections/312-necessary-attempt1/process.json'),'why_necessary_repeated':'Initial test execution passed; registration moved from NEW_MODULES to the end of ADDITIONAL_MODULES to preserve the entire original484 ordered selector prefix, then all84 necessary tests rerun on final bytes.',
 'map_attempt':{'first_observations':pin('research/p3-map-attempt-312/image-only-first-observations.json'),'geometric_candidates':0,'new_accepted_points':0,'map_functionality_delivered':False,'next_condition':'A distinct source-supported independent observation method or explicit original geometry transform; no retuning to chase agreement.'},
 'desktop_snapshot_transport':{'attempted':True,'result':'Windows-mcp Snapshot RPC server unavailable; PowerShell tool worked. Owned actual Qt HWND/PID and widget screenshots provide only the stated fixture/native/app-window scope, not a desktop screenshot or game validation.'},
 'full_suite_rerun':False,'last_full_receipt':'verification/full-305/summary.json','last_full_source_is_historical305':True,'next_periodic_full_section':320,'P3_complete':False,'P2_complete':False,'P1_complete':False,
 'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False}
(ROOT/'verification/sections/312.json').write_bytes(enc(r))
validation='实际84项必要检查、31项原生唯一检查通过，三个入口、12次主题阅读和6组非零阅读状态保留通过；来源副本真实损坏与手动恢复核对通过，五张实际截图均已查看。原项目窗口已正常更新并可见响应，整个关闭/启动期间私人五路径保持不变。原四类阅读入口共八方法AST保留，完整484检查选择器顺序不减，末尾新增三项至487；初次登记顺序调整后复验84项通过。未重跑全量，305仅历史范围，下次定期全量320；符号链接1314、历史私样本、Linux/Wine及游戏聊天不冒称通过。'
details=change+'\n\n'+validation+'\n\n'+limits+'\n\n用户已明确继续，311后暂停解除；本批不继承旧停止节数。严格低于15%时完整收尾规则保留。\n\n'+pending
for name in('PROJECT_COMPLETED.md','WORK_IN_PROGRESS.md'):
 text=(ROOT/name).read_text('utf8')
 if name=='WORK_IN_PROGRESS.md':
  marker='以下为已交付历史。\n\n';assert text.startswith('## 当前进行第312节')and text.count(marker)==1;text=text.split(marker,1)[1]
 write_doc(name,'## 第312节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述312为准。\n\n'+text)
text=(ROOT/'AGENTS.md').read_text('utf8');end=text.index('\n## ',3)
write_doc('AGENTS.md','## 当前续接 · 第312节 + '+title+'\n\n'+details+'\n\n继续P3，后续313；不继承311后暂停，识别最后，下一定期全量320。\n'+text[end:])
text=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');a=text.index('<!-- current-delivery:start -->');marker='<!-- current-delivery:end -->';b=text.index(marker)+len(marker)
write_doc('PROJECT_REQUIREMENTS.md',text[:a]+'<!-- current-delivery:start -->\n## 第312节 + '+title+'\n\n'+details+'\n'+marker+text[b:])
# Only remaining gaps stay in the todo list; the new completed documentary scope is elsewhere.
text=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');old='其余未覆盖首领及其关联敌人/装置的完整文献条件流程';assert text.count(old)==1
write_doc('PROJECT_PROGRESS.md',text.replace(old,'其余首领及关联敌人/装置尚未覆盖的完整文献条件流程；已支持首领流程的实际条件、执行与当前服务器核对',1))
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout','active_section'):
 if key in cp:cp['historical_before312_'+key]=cp.pop(key)
cp.update(completed_sections=312,latest_functional_section=312,next_section=313,batch_status='P3_SECTION312_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第312节 + '+title+'已本地验收，普通推送核对真实远端后继续P3；313未启动，下一定期全量320。')
assert not any(item['number']==312 for item in cp['sections'])
cp['sections'].append({'number':312,'completion_ref':'p3-section-312','topic':title,'verification':'verification/sections/312.json'})
cp['functional_sections_since_latest_requirement'].append(312)
cp['current_section_save']={'section':312,'verification':'verification/sections/312.json','scope':'current_functional_section','binding':'enclosing_commit'}
cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':312,'receipt':'verification/sections/312.json','necessary_methods_passed':84,'native_isolated_window_checks':31,'exact_entries':3,'actual_topic_readings':12,'actual_nonzero_refresh_states':6,'full_suite_rerun':False,'last_full_receipt':'verification/full-305/summary.json','full_source_is_historical305':True}
cp['latest_section_environment']={'section':312,'receipt':'verification/sections/312.json','native_windows':'84 necessary;31 unique native;3 entries/12 topics/6 nonzero refresh states; source damage/recovery; original app startup verified','native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-305/summary.json'}
cp['current_batch'].update(status=cp['batch_status'],completed_sections=312,next_section=313,next_section_started=False,receipt='verification/sections/312.json',batch_closed=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
text=(ROOT/'CLOUD_HANDOFF.md').read_text('utf8');write_doc('CLOUD_HANDOFF.md',text+'\n<!-- section312-handoff:start -->\n## 第312节 + '+title+'\n\n'+details+'\n<!-- section312-handoff:end -->\n')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
out=ROOT/'verification/sections/312-closeout';out.mkdir();(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes())
(out/'applied.json').write_bytes(enc({'section':312,'local_accepted':True,'ordinary_cloud_publication_verified':False,'at_Beijing':now,'next313_started':False,'section_label':read('CLOUD_INDEX.json')['current_section_label']}))
print(json.dumps({'completed_section_label':read('CLOUD_INDEX.json')['current_section_label'],'cloud_publication_pending':True},ensure_ascii=False))
