from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone,timedelta
import json,runpy,subprocess,shutil
ROOT=Path(__file__).resolve().parents[1]
def read(n):return json.loads((ROOT/n).read_bytes())
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+chr(10)).encode('utf8')
def sha(n):return sha256((ROOT/n).read_bytes()).hexdigest()
def pin(n):return{'receipt':n,'sha256':sha(n)}
def doc(n,s):
 p=ROOT/n;style='\r\n'if b'\r\n'in p.read_bytes()else'\n';p.write_bytes(s.replace('\r\n','\n').replace('\n',style).encode('utf8'))
parent='fa9d061f0c30c2aaa98ccf6ba825a37c148c1bce';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='险路尽头完整事件、难度16奖励差异与独立后续'
change='新增险路尽头完整事件阅读，保留5段原情景、8份完整原选项、6处文献选项和8个查阅位置。说服同伴、留存券招募、离开及10源石锭援助分别查阅；谒日之祈具名提示与用途原件可从事件或藏品说明打开。保密等级、结算前行动力及源石锭仅本页对照，默认未知。明确常规模式16不再取得加工品，旧文案保留且不按其预测1件；等量希望独立对照，不把取得加工品和后续确认相加两次，不造本局最终希望/上限。两份未写加工品的原选项单列为前置未知，仅保留明确后续，不按难度挑原件；重复文献对话分成不同阅读位置，末处终止，不循环领奖。14个准确原始入口保留来源请求；同一原件对应多处文献时不默认选阶段。节点目录新增1个准入及4处完整旧/新正文对照，共31目录组、29事件、13类阅读器。实际父页刷新保留两个真实非零阅读位置、选区/页签、选项、三项条件和原入口；坏源清旧、手动恢复、重复打开与父源/主窗关闭均清理所属事件窗口。'
limits='复用321实际下载的BWIKI352356完整HTTP中的险路尽头标题段，保留调查中及完整表；本轮独立复读BWIKI和PRTS主题页，常规等级16例外另核对bee3完整difficulty原记录，不冒称新下载HTML或核对当前服务器。表中缺失的选项三不补造。八原选项完整保留，提示生命上限的字段不当额外数值奖励；同文案原件不凭ID/难度消歧，两份无加工品原件只按明确nextSceneId关联后续、前置仍未知。实际原菜单/变体、服务器资格、招募费用/库存/随机结果与培养、完整加工品池、希望结算执行阶段/上限修正、谒日之祈发放件数及余径/探险家/首领脚本仍待依据。等量希望是固定规则对照而非实际资源结算；文献流程不执行换层、招募或选择。仅局外查阅，不操作游戏、不发送聊天、不改本局/地图/数值或私人配置，不提供路线建议/排序/概率。P3/P2/P1未完成，识别最后。'
validation='本机45项相关必要检查首轮全部通过，完整资料构建可重复且字节一致，所选源码前后不变。Windows原生临时MainWindow共47项唯一检查通过，14处实际版本入口准确保留源请求，歧义原件不自动选文献位置；常规等级15/16加工品边界、行动力7的独立等量规则、无加工品原件仅明确后续、招募不假免费/固定随机、确认不造地图、重复文献对话终止、援助源石锭9/10边界及谒日之祈未知件数逐项核对。两个真实非零滚动和选区/页签、选项/三条件/来源经实际父页刷新保留；坏源清旧/手动恢复、重复开窗、节点默认未知和版本提示、坏源保留旧目录、实际主窗关闭同时清理版本页和节点页子窗。9张实际PNG由主代理直接查看。七类真实外部操作计数零，临时本局与旧计算上下文不变。原项目测试窗正常更新，可见响应且未最小化，正常关闭到启动私人五路径一致；未确认置前台。545旧维护选择器原序保留，现547。准备时资料解析器构造参数纠正后才实施构建，不冒称测试失败/通过；误开无关物品页和谒日之祈PRTS不可达已记来源边界，无关页不作依据。只跑本机必要与原生检查，无云端重复运行；335完整可用范围保留为历史，不冒称本节全量，下次350。索引实现未变，25单测复用已有证据，但当前要求、状态、来源和索引实际校验。'
nname='verification/sections/339-necessary-attempt1/process.json';wname='verification/sections/339-native-attempt1/actual/window.json';pname='verification/sections/339-native-attempt1/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/339-main-window.json');a=read('verification/sections/339-source-audit.json');v=read('verification/sections/339-root-visual.json')
assert n['passed']and n['methods_ran']==45 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==47 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==9 and len(w['actual_readings'])==14 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==9 and a['ordered_previous545_preserved']and len(a['current_selectors'])==547
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section339-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':339,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':45,'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':47,'actual_Qt_exit':0,'original_scenes':5,'original_choices':8,'document_choice_occurrences':6,'reading_contexts':8,'exact_original_version_entries':14,'catalogue_groups':31,'catalogue_titles':29,'reader_kinds':13,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/339-root-visual.json'),'source_audit':pin('verification/sections/339-source-audit.json'),'original_project_window':pin('verification/sections/339-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-335/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-335/summary.json'),'next_periodic_full_section':350,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/339.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=subprocess.check_output(['git','show',parent+':WORK_IN_PROGRESS.md'],cwd=ROOT);(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第339节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述339为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第339节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。335原失败与绑定维护/复验见verification/full-335/summary.json。'
doc('AGENTS.md','## 当前续接 · 第339节 + '+title+'\n\n'+details+'\n\n继续P3；340从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。完整事件表与原件对照不替代服务器资格或实际结算。只跑本机必要检查；下一全量350，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第339节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');assert s.count('其余未覆盖完整事件表及其奖励条件')==1;s=s.replace('其余未覆盖完整事件表及其奖励条件','险路尽头完整出现资格、八原选项实际选择与两份无加工品原件前置、留存券库存/费用/实际结果、加工品池及行动力换希望实际阶段和谒日之祈发放/余径脚本，其余未覆盖完整事件表及其奖励条件');s=s.replace('更新：2026-10-21。','更新：2026-10-22。');doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==338 and cp['next_section']==339
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before339_'+key]=cp.pop(key)
cp.update(completed_sections=339,latest_functional_section=339,next_section=340,batch_status='P3_SECTION339_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第339节 + '+title+'已本机必要验收；普通推送核对后340接续P3实际剩余缺口，未启动。下次350。',full_validation_due=False)
cp['sections'].append({'number':339,'completion_ref':'p3-section-339','topic':title,'verification':'verification/sections/339.json'});cp['functional_sections_since_latest_requirement'].append(339)
cp['current_section_save']={'section':339,'verification':'verification/sections/339.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':339,'receipt':'verification/sections/339.json','methods_run':45,'native_isolated_window_checks':47,'original_scenes':5,'original_choices':8,'document_choice_occurrences':6,'reading_contexts':8,'exact_original_version_entries':14,'catalogue_groups':31,'catalogue_titles':29,'reader_kinds':13,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-335/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':339,'receipt':'verification/sections/339.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-335/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=339,next_section=340,next_section_started=False,receipt='verification/sections/339.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(current_exit_game_commit='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',current_exit_original_scenes=5,current_exit_original_choices=8,current_exit_document_choice_occurrences=6,current_exit_reading_contexts=8,current_exit_original_entries=14,current_node_reader_groups=31,current_node_reader_titles=29,current_node_reader_kinds=13,current_exit_actual_server_eligibility_verified=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section339-handoff:start -->\n## 第339节 + '+title+'\n\n'+details+'\n<!-- section339-handoff:end -->\n')
out=ROOT/'verification/sections/339-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_339.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':339,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next340_started':False,'at_Beijing':now}))
print(json.dumps({'section':339,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
