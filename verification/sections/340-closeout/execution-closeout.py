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
parent='d4f9b0609456de074f05afa60065c6a041e8ccf6';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='临时中介所完整事件、四组职业图标与独立临时招募'
change='新增固定国服临时中介所完整事件阅读，保留4段对话、6份完整原选项、10处准确版本入口。可靠中介四组分别用中文与两枚职业图标显示先锋/近卫、重装/辅助、医疗/狙击、术师/特种，明确每组2希望、招募1名5星及以下直升干员；或不变成各一名，四组不累计成8希望/4干员。“直升”解释为首次招募即已进阶，具体培养仍未知。随机6星临时招募和离开各有独立结果及后续，不继承可靠分支职业组/2希望，不把临时招募当只打一场的应急雇佣。职业组仅本页对照、默认未知，不自动认定本次随机结果；只有可靠分支显示该控件及图标，其它分支和终段完全隐藏并清旧图。本页四组对照只阻断不符组合的后续阅读，不代表服务器资格。图标缺失显示中文占位并保留已核对正文及另一枚图标；整个来源失效则清旧资料与图标，恢复须手选。实际父页刷新保留两组真实非零滚动与选区、选项、页签及本页职业组；重复打开、父源或实际主窗关闭清理所属窗口。节点新增1个当前版本入口及4份完整旧/新情景对照，共32目录组、30事件、14类阅读器。'
limits='复用321真实下载的BWIKI352356完整HTTP中的临时中介所整表，四组随机标记、6选项和4对话均逐项匹配固定bee3国服原记录，并保留全部baseline比较结果和完整旧/新正文；只准许明确的省略号写法转换，不按相似名称猜前情景。独立复读BWIKI与PRTS集成战略/主题资料，直升含义、通用临时招募希望规则及应急雇佣区别单独说明；不冒称新下载HTML、当前服务器验证或已恢复事件实际发放/费用脚本。复用已归档8职业图标及准确哈希，失败只回退文字；不新下载或借用干员头像充图标。第290节仅有旧可靠选项的四组补充，本节新增完整当前事件及准确入口，不重写旧290边界、不把未知旧入口计作当前实机通过。本次实际职业组、完整资格、具体候选和费用、培养、六星实际人选/发放时点及本局希望/领取仍未知，不能把文字来源当实际结果。只局外查阅，不操作游戏、发聊天或改本局/地图/计算与私人配置，不给路线建议/排序/概率。P3/P2/P1未完成，识别最后。'
validation='本机44项相关必要检查首轮通过，完整资料构建字节一致且所选源码前后不变。Windows原生临时MainWindow共48项唯一检查通过，10处实际版本入口准确打开对话/选项，四职业组全部8图标及无双人数/无四组相加、直升解释与不假免费招募，4乘4共16组对照边界、六星不继承职业与2希望/不混应急、离开及各终段不反复招募逐项核对。两组真实非零阅读与选区、页签/选项/职业对照经实际父刷新保留；实际损坏图标保留正文及另一图标，恢复只还原合格图片，整个源坏清旧图/控件/正文及手动恢复、重复打开、节点默认未知/版本提示、坏源保留旧目录与实际主窗同时关闭版本和节点子窗通过。8张实际PNG主代理逐张查看。七类真实外部操作计数零，临时本局与旧计算上下文不变；原项目测试窗正常更新，可见响应且未最小化，未确认置前台，正常关闭到启动私人五路径一致。547旧维护选择器原序保留，现549。只跑本机必要及原生检查，未云端重复运行；335完整可用范围仍是历史，不冒称本节全量，下次350。未改索引实现，25单测依既有证据复用，但当前要求、断点、来源和索引仍实际校验。'
nname='verification/sections/340-necessary-attempt1/process.json';wname='verification/sections/340-native-attempt1/actual/window.json';pname='verification/sections/340-native-attempt1/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/340-main-window.json');a=read('verification/sections/340-source-audit.json');v=read('verification/sections/340-root-visual.json')
assert n['passed']and n['methods_ran']==44 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==48 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==8 and len(w['actual_readings'])==10 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==8 and a['ordered_previous547_preserved']and len(a['current_selectors'])==549
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section340-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':340,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':44,'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':48,'actual_Qt_exit':0,'original_scenes':4,'original_choices':6,'profession_pairs':4,'verified_profession_icons':8,'exact_original_version_entries':10,'catalogue_groups':32,'catalogue_titles':30,'reader_kinds':14,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/340-root-visual.json'),'source_audit':pin('verification/sections/340-source-audit.json'),'original_project_window':pin('verification/sections/340-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-335/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-335/summary.json'),'next_periodic_full_section':350,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/340.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=subprocess.check_output(['git','show',parent+':WORK_IN_PROGRESS.md'],cwd=ROOT);(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第340节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述340为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第340节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。335原失败与绑定维护/复验见verification/full-335/summary.json。'
doc('AGENTS.md','## 当前续接 · 第340节 + '+title+'\n\n'+details+'\n\n继续P3；341从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。完整事件阅读不替代本次职业抽取、实际招募或服务器资格。只跑本机必要检查；下一全量350，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第340节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');assert s.count('临时中介所本次职业组合与实际选择、招募费用、具体培养数值、领取状态及原入口')==1;s=s.replace('临时中介所本次职业组合与实际选择、招募费用、具体培养数值、领取状态及原入口','临时中介所本次职业组抽取与实际选择、可靠分支实际费用/名单及全部具体培养数值、六星发放过程、领取状态与原入口完整服务器资格');doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==339 and cp['next_section']==340
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before340_'+key]=cp.pop(key)
cp.update(completed_sections=340,latest_functional_section=340,next_section=341,batch_status='P3_SECTION340_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第340节 + '+title+'已本机必要验收；普通推送核对后341接续P3实际剩余缺口，未启动。下次350。',full_validation_due=False)
cp['sections'].append({'number':340,'completion_ref':'p3-section-340','topic':title,'verification':'verification/sections/340.json'});cp['functional_sections_since_latest_requirement'].append(340)
cp['current_section_save']={'section':340,'verification':'verification/sections/340.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':340,'receipt':'verification/sections/340.json','methods_run':44,'native_isolated_window_checks':48,'original_scenes':4,'original_choices':6,'profession_pairs':4,'verified_profession_icons':8,'exact_original_version_entries':10,'catalogue_groups':32,'catalogue_titles':30,'reader_kinds':14,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-335/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':340,'receipt':'verification/sections/340.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-335/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=340,next_section=341,next_section_started=False,receipt='verification/sections/340.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(current_agency_game_commit='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',current_agency_original_scenes=4,current_agency_original_choices=6,current_agency_profession_pairs=4,current_agency_verified_profession_icons=8,current_agency_original_entries=10,current_node_reader_groups=32,current_node_reader_titles=30,current_node_reader_kinds=14,current_agency_actual_server_offer_or_recruitment_verified=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section340-handoff:start -->\n## 第340节 + '+title+'\n\n'+details+'\n<!-- section340-handoff:end -->\n')
out=ROOT/'verification/sections/340-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_340.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':340,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next341_started':False,'at_Beijing':now}))
print(json.dumps({'section':340,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
