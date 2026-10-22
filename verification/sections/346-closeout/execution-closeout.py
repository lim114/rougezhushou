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
parent='95de2e0fc5a722439b837b9251ed6acc0b2a10d8';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='被歌颂的影子逐圈代价、随机结果与犬植浆来源'
change='新增固定bee3国服被歌颂的影子完整文献阅读：28处完整对话位置及7组随机结果目录，共35处位置、33处主选项与16条结果参考。每圈代价按1/1/2/2/2/3/3/3生命分开显示，拒绝邀请、七处中途离开、逐圈领取及不同随机结果分别查阅，不合计互斥奖励。完整保留28段原对话和28份原项，56处准确原文入口加1处犬植浆取得入口均可打开；20份明确目的对话只读自身后续，不猜专属菜单，8份无明确后续的同文随机候选不按编号恢复圈次或父关系。第七圈虽文献只列三藏品后续，仍不把原项无next当已证服务器目的地。回复生命的文献复用叙述与原件安静叙述差异显式保留，第四/五/六圈同文原记录不强绑唯一。第八圈行动力领取返回继续跳舞处与犬植浆后离开分开，返回阅读仍提示每次加入消耗3生命，不推定无限收益或实际循环。犬植浆按原项明确物品指针显示准确名称、图片及其它干员迷彩/攻击力+10%可叠加说明，不按变动的社区序号套用鸭力板效果，不新增战斗模型。两组真实非零阅读/选区、选项和页签经父刷新保留；坏图回退文字，整源坏清旧及图片，恢复须手选；重复打开、父页失效及实际主窗关闭清理两入口窗口。旧20处目录上下文的21条对照仅20段唯一原文，不冒称覆盖28；全部38个固定旧目录组现可打开当前阅读，共36标题、20类阅读器，不等于当前游戏全部隐藏事件或条件完成。'
limits='复用321真实下载BWIKI352356完整交互图与固定bee3/baseline原件，重新查阅当前BWIKI及PRTS犬植浆条目。搜索读取10月17日社区错位效果反馈，直接反馈页两次超时，反馈仅作排查线索，效果以原项精确指针与固定游戏原件核对；不把社区反馈当游戏机制权威。没有新下载HTML或图片。文献结果目录不是游戏可选择的随机结果按钮或完整奖励池；同文与相邻编号不证明实际圈次/父关系。完整出现资格、各圈实际随机选择及具体池、生命不足/致命扣费处理、实际消费/回复/领取、真实重复与停止脚本、犬植浆独立领取件数/实际光环层数及其余来源仍未知。38目录组全有阅读入口不替代当前服务器全量覆盖；25旧场景/57旧选项未绑定快照不因本节对照自动减少。不操作游戏、不发聊天、不支付/领取、不改变本局记忆、地图或私人设置，不给路线建议/排序/概率。P3/P2/P1未完成，识别最后。'
validation='本机40项相关测试与Windows原生临时MainWindow54项唯一检查首轮通过，完整资料构建字节一致。56处准确原文和1处犬植浆取得入口均实际打开，20份明确后续与8份无后续原项逐项核对，49条文献选项/结果下一步全部实际操作；7组目录/16条结果参考非游戏按钮、八次加入各自代价、七处中途离开与最初拒绝、两次手动阅读行动力返回及3生命代价/不保证无限收益、犬植浆终段与准确图片/效果、回复生命文本差异及同文不强绑、两组真实非零阅读/选区与页签经父刷新保留、坏图文字回退与整源坏清旧/手选恢复、节点版本提示/旧目录文字保留及实际主窗关闭两入口均通过。7张最终实际PNG主代理逐张查看。初次准备构建将当前28原文误当旧目录链接数，被严格数量门拦下；保留原稿及退出1，独立核对旧20处上下文确为21链接/20唯一原文后更正统计口径，不修改旧目录或丢弃当前28原件。测试/原生首轮无失败重跑。七类真实外部操作零，临时本局/旧计算上下文不变；实际项目测试窗正常更新，可见响应且未最小化，正常重启全过程私人五路径不变，未确认前台。559旧维护选择器原序保留，现561。只跑本机必要及原生检查，云端不重复；335全量属历史，下次350。索引实现未改，复用历史25项单测，当前要求/断点/来源和索引实际校验。'
nname='verification/sections/346-necessary-attempt1/process.json';wname='verification/sections/346-native-attempt1/actual/window.json';pname='verification/sections/346-native-attempt1/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/346-main-window.json');a=read('verification/sections/346-source-audit.json');v=read('verification/sections/346-root-visual.json')
assert n['passed']and n['methods_ran']==40 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==54 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==7 and len(w['actual_readings'])==57 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==7 and a['ordered_previous559_preserved']and len(a['current_selectors'])==561
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section346-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':346,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':40,'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':54,'actual_Qt_exit':0,'original_scenes':28,'original_choices':28,'current_named_item':1,'exact_original_version_entries':56,'additional_relic_acquisition_entry':1,'document_contexts':35,'document_options_and_results':49,'catalogue_groups':38,'catalogue_titles':36,'reader_kinds':20,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/346-root-visual.json'),'source_audit':pin('verification/sections/346-source-audit.json'),'original_project_window':pin('verification/sections/346-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-335/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-335/summary.json'),'next_periodic_full_section':350,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/346.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=subprocess.check_output(['git','show',parent+':WORK_IN_PROGRESS.md'],cwd=ROOT);(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第346节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述346为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第346节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。335原失败与绑定维护/复验见verification/full-335/summary.json。'
doc('AGENTS.md','## 当前续接 · 第346节 + '+title+'\n\n'+details+'\n\n继续P3；347从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。完整文献、同文候选及具名参考不替代完整结果池、原项归属、领取或重复脚本核对。只跑本机必要检查；下一全量350，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第346节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');old='尚无旧目录条目的新增事件入口与其余未适配的完整阅读器';assert s.count(old)==1;s=s.replace(old,'行动奖励的实际出现与原入口、其余不在旧目录内的隐藏事件/条件链');anchor='安眠一隅两处数量注释与BWIKI/旧PRTS分组差异的实际解释';assert s.count(anchor)==1;s=s.replace(anchor,'被歌颂的影子当前服务器完整资格、随机原项实际父关系与生命不足处理、具体奖励池/实际结果、同文叙述实际选择及第八圈重复/停止脚本、犬植浆领取件数与实际生效；'+anchor);doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==345 and cp['next_section']==346
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before346_'+key]=cp.pop(key)
cp.update(completed_sections=346,latest_functional_section=346,next_section=347,batch_status='P3_SECTION346_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第346节 + '+title+'已本机必要验收；普通推送核对后347接续P3实际剩余缺口，未启动。下次350。',full_validation_due=False)
cp['sections'].append({'number':346,'completion_ref':'p3-section-346','topic':title,'verification':'verification/sections/346.json'});cp['functional_sections_since_latest_requirement'].append(346)
cp['current_section_save']={'section':346,'verification':'verification/sections/346.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':346,'receipt':'verification/sections/346.json','methods_run':40,'native_isolated_window_checks':54,'original_scenes':28,'original_choices':28,'current_named_item':1,'exact_original_version_entries':56,'additional_relic_acquisition_entry':1,'document_contexts':35,'document_options_and_results':49,'catalogue_groups':38,'catalogue_titles':36,'reader_kinds':20,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-335/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':346,'receipt':'verification/sections/346.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-335/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=346,next_section=347,next_section_started=False,receipt='verification/sections/346.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(current_shadow_game_commit='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',current_shadow_original_scenes=28,current_shadow_original_choices=28,current_shadow_original_entry_views=56,current_shadow_explicit_named_item=1,current_node_reader_groups=38,current_node_reader_titles=36,current_node_reader_kinds=20,current_shadow_actual_result_pool_or_server_verified=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section346-handoff:start -->\n## 第346节 + '+title+'\n\n'+details+'\n<!-- section346-handoff:end -->\n')
out=ROOT/'verification/sections/346-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_346.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':346,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next347_started':False,'at_Beijing':now}))
print(json.dumps({'section':346,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
