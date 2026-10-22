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
parent='a41b006f0c8fa8a986629d6f9b072bad38fef9a9';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='安眠一隅完整分支、资料差异与99源石锭后续对照'
change='新增固定bee3国服安眠一隅完整文献阅读：25处对话/结果位置、24处选项与结果参考，七条路径分别查阅首次小狗/捕梦网/松鼠及后续果园、豹子竞速、动物泥偶等结果。12段完整原对话和12份原选项共24处准确版本入口全部可打开，其中8份原项有明确目的对话，4份仅是同文随机候选而无明确后续或父关系。19处BWIKI对话、4处结果参考目录与2处旧资料归属未证位置分开，结果目录不当游戏可选菜单。保留旧293两处数量注释冲突；捕梦网的安静观察独立领取不拿来凑随机项，松鼠后的旧动物泥偶不当当前已证结果。99源石锭文献离开与原项返回病床并列，提供准确原项对照入口，只读明确后续而不补菜单、重复领取或真实离开。源私钥按完整名称唯一对应当前藏品资料及准确图片，原项没有物品指针这一限制明确显示；其说明99与事件领取99关系未证，不合计198。刷新保留两组真实非零阅读/选区、选项和页签及子原文位置；重复打开/父页失效/实际主窗关闭清理所属整树。坏图回退文字，整源坏清旧及对照入口，恢复须手选。节点接入18条上下文对照但仅12段唯一原对话，共37目录组、35标题、19类阅读器。'
limits='复用321真实下载BWIKI352356完整安眠一隅表、293已归档PRTS两版完整原文及固定bee3与baseline原件，再针对当前BWIKI/PRTS与数量分组差异查阅；未找到足够证据解决实际结果数量/归属，不补缺项、不猜概率。没有新下载HTML或图片。旧293保留，本节新增完整当前阅读和准确原文入口，不重新登记旧数量问题为已解决。具名源私钥是全文唯一同名当前RELIC参考，原选项itemId为空，不伪称有明确物品指针。两处99是否同次发放、实际父情景、返回/离开/重复脚本、完整结果范围与归属、当前服务器全部资格及本局实际领取仍未知。原文8个明确目的地不证明实际可达，4个同文随机候选不证明服务器父关系；旧25场景/57选项未绑定快照不因本节对照而自动减少。不操作游戏、不发聊天、不支付/领取、不改变本局记忆、地图、计算数值或私人设置，不给路线建议/排序/概率。P3/P2/P1未完成，识别最后。'
validation='本机44项相关测试与Windows原生临时MainWindow58项唯一检查首轮通过；完整资料构建字节一致。24处准确版本入口全部实际打开、8个明确后续和4个无后续候选逐项核对；七条文献路径、结果参考非游戏菜单、两处数量冲突/旧额外结果保留、原项缺物品指针及99不相加、准确99原项与病床后续/不递归补菜单、两组非零阅读/选区及页签经真实父刷新保留、子原文位置保持、坏图文字回退与坏源清旧/手选恢复、节点版本提示及实际主窗同时关闭两入口整树通过。8张最终实际PNG主代理逐张查看。初次准备构建误假定原项有物品指针而KeyError，保留初稿和实际失败，改为完整名称唯一对照并保留缺指针限制；测试和原生均无失败重跑。七类真实外部操作零，临时本局及旧计算上下文不变。实际项目测试窗正常更新，可见响应且未最小化，私人五路径整个正常重启不变，未确认前台。557旧维护选择器原序保留，现559。只跑本机必要及原生检查，云端不重复；335全量属历史，下次350。索引实现未变，复用历史25项单测，当前要求/断点/来源及索引实际校验。'
nname='verification/sections/345-necessary-attempt1/process.json';wname='verification/sections/345-native-attempt1/actual/window.json';pname='verification/sections/345-native-attempt1/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/345-main-window.json');a=read('verification/sections/345-source-audit.json');v=read('verification/sections/345-root-visual.json')
assert n['passed']and n['methods_ran']==44 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==58 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==8 and len(w['actual_readings'])==24 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==8 and a['ordered_previous557_preserved']and len(a['current_selectors'])==559
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section345-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':345,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':44,'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':58,'actual_Qt_exit':0,'original_scenes':12,'original_choices':12,'current_named_item':1,'exact_original_version_entries':24,'catalogue_groups':37,'catalogue_titles':35,'reader_kinds':19,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/345-root-visual.json'),'source_audit':pin('verification/sections/345-source-audit.json'),'original_project_window':pin('verification/sections/345-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-335/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-335/summary.json'),'next_periodic_full_section':350,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/345.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=subprocess.check_output(['git','show',parent+':WORK_IN_PROGRESS.md'],cwd=ROOT);(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第345节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述345为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第345节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。335原失败与绑定维护/复验见verification/full-335/summary.json。'
doc('AGENTS.md','## 当前续接 · 第345节 + '+title+'\n\n'+details+'\n\n继续P3；346从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。完整文献、同文候选及具名参考不替代完整结果池、原项归属、领取或重复脚本核对。只跑本机必要检查；下一全量350，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第345节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');old='安眠一隅两处原注数量冲突、完整候选范围与99源石锭原入口及本局实际结果';assert s.count(old)==1;s=s.replace(old,'安眠一隅两处数量注释与BWIKI/旧PRTS分组差异的实际解释、完整结果范围/归属、99原项实际父情景及病床返回/离开/重复脚本、源私钥99与事件99的同次发放关系和实际领取');doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==344 and cp['next_section']==345
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before345_'+key]=cp.pop(key)
cp.update(completed_sections=345,latest_functional_section=345,next_section=346,batch_status='P3_SECTION345_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第345节 + '+title+'已本机必要验收；普通推送核对后346接续P3实际剩余缺口，未启动。下次350。',full_validation_due=False)
cp['sections'].append({'number':345,'completion_ref':'p3-section-345','topic':title,'verification':'verification/sections/345.json'});cp['functional_sections_since_latest_requirement'].append(345)
cp['current_section_save']={'section':345,'verification':'verification/sections/345.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':345,'receipt':'verification/sections/345.json','methods_run':44,'native_isolated_window_checks':58,'original_scenes':12,'original_choices':12,'current_named_item':1,'exact_original_version_entries':24,'catalogue_groups':37,'catalogue_titles':35,'reader_kinds':19,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-335/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':345,'receipt':'verification/sections/345.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-335/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=345,next_section=346,next_section_started=False,receipt='verification/sections/345.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(current_resting_game_commit='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',current_resting_original_scenes=12,current_resting_original_choices=12,current_resting_original_entry_views=24,current_resting_named_item_reference=1,current_node_reader_groups=37,current_node_reader_titles=35,current_node_reader_kinds=19,current_resting_actual_result_pool_or_server_verified=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section345-handoff:start -->\n## 第345节 + '+title+'\n\n'+details+'\n<!-- section345-handoff:end -->\n')
out=ROOT/'verification/sections/345-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_345.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':345,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next346_started':False,'at_Beijing':now}))
print(json.dumps({'section':345,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
