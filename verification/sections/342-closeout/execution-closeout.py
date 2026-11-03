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
parent='247c8f8536f29a8cb5f83b38a40108216d8f0998';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
title='未涉足之树完整事件、解锁前置与派出归来分项'
change='新增固定bee3国服未涉足之树完整事件阅读：4段原对话、4个实际原选项及8处准确版本入口。探索内部、探索源头、休息三支分别阅读；源头后续的会合确认与归来说明分开，说明不作为第五个按钮。明确休息当场2希望、源头归来2希望及怦然信标，不跨分支累加；内部完整回报不借用源头。归来提示及收藏品指针/完整物品已与当前原件核对，源头和确认才显示已核对信标图片及效果，内部/休息/无选择/无效源完全隐藏图片而非禁用。确认不再派人或即时领取，目标生命提示字段不冒充回血，无原件后续或地图就不补跳转。显示文献第II-IV层及源头相关选项先通关强制重启前置，不认定账户已经解锁或同次全部可选。长期科技喙的通用加工品规则与源头仅获得的关系未知，不额外加算。本页无资源/人选输入，实际派出、归来和库存全未知。刷新保留两组真实非零阅读/选区、选项和页签；图坏只回退文字，整源坏清旧、手选恢复、重复打开/父页及主窗关闭清理所属窗口。节点新增当前阅读器与4条准确旧新情景对照，共34目录组、32标题、16类阅读器。'
limits='复用321真实下载的BWIKI352356完整未涉足之树表、297实际归档PRTS完整文献及固定当前bee3/baseline原件，并再次读取当前BWIKI和PRTS相关段落。现有297旧目录派出归来说明保持不变；本节新增的是完整当前事件、确认项及准确入口，非重新计旧说明。4个当前gameConst字段、完整怦然信标物品与旧文献关联逐项核对，但文本相同不证明服务器实际执行。完整出现资格、账户解锁/实际可选、派出人选、特殊区域是否等同下一层、实际时刻/是否返回、内部完整奖励池/数量/培养、喙与源头叠加及实际领取件数未知。不新下载HTML或图片、不借同名恢复脚本/地图，不改本局、计算、队伍或私人状态，不操作游戏或发聊天，不给路线建议/排序/概率。P3/P2/P1未完成，识别最后。'
validation='本机最终37项相关检查通过，完整资料构建字节一致。Windows原生临时MainWindow42项唯一检查通过：8处准确版本入口、三支互不借奖励、源头真实确认而非归来解释按钮、文献层数/解锁不等同账户资格、确认不造地图/回血或再次领奖、已核对图片及坏图文字回退、两组真实非零阅读/选区与选项/页签经实际父刷新保留、坏源清旧/手选恢复、重复打开和父页清理、节点版本提示及实际主窗同时关闭两种入口子窗。6张最终实际PNG主代理直接逐张查看。七类真实外部操作计数零，临时本局及旧计算上下文不变；实际原项目测试窗正常更新，可见响应未最小化，重启全过程私人五路径不变，未确认前台。初轮36测试与41窗口检查已通过，随后补上文献已知层数/解锁条件并按最终源码完整复验；初始源码/回执均保留，不伪称原测试失败。审计准备误用不存在的test_modules函数，在审计运行前改用真实maintained_selectors，不计验收。551旧维护选择器原序保留，现553。仅本机必要及原生检查，云端不重复；335全量是历史，下次350。索引实现未改，25单测复用历史，但当前源码/要求/断点和索引实际校验。'
nname='verification/sections/342-necessary-attempt2/process.json';wname='verification/sections/342-native-attempt2/actual/window.json';pname='verification/sections/342-native-attempt2/process.json'
n,w,p=map(read,(nname,wname,pname));m=read('verification/sections/342-main-window.json');a=read('verification/sections/342-source-audit.json');v=read('verification/sections/342-root-visual.json')
assert n['passed']and n['methods_ran']==37 and w['passed']and w['qpa']=='windows'and w['qt_exit_code']==0 and w['unique_checks']==42 and w['verification_window_closed']
assert len(w['same_identity_refresh_observations'])==2 and len(w['screenshots'])==6 and len(w['actual_readings'])==8 and all(x==0 for x in w['external_operation_attempts'].values())
assert p['passed']and p['window_receipt_sha256']==sha(wname)
for result in(n,w):
 assert result['source_sha256_before']==result['source_sha256_after']
 for name,h in result['source_sha256_after'].items():assert sha(name)==h,name
assert v['passed']and len(v['final_screenshot_reviews'])==6 and a['ordered_previous551_preserved']and len(a['current_selectors'])==553
assert m['passed']and m['private_entire_normal_close_and_start_interval_unchanged']and m['window_visible_and_responsive']
now=datetime.now(timezone(timedelta(hours=8))).isoformat();pending='<!-- section342-publication-pending -->本地验收完成，普通推送及真实远端核对待完成。'
r={'section':342,'kind':'functional_section','title':title,'new_capability':change,'limitations':[limits],'at_Beijing':now,'branch':'codex/p2-development','necessary_validation':{**pin(nname),'methods_run':37,'actual_exit':0},'native_windows_validation':{**pin(wname),'process':pin(pname),'unique_checks':42,'actual_Qt_exit':0,'original_scenes':4,'original_choices':4,'current_game_const_fields':4,'current_return_item':1,'exact_original_version_entries':8,'catalogue_groups':34,'catalogue_titles':32,'reader_kinds':16,'real_nonzero_refresh_states':2,'actual_MainWindow_entry_and_close_exercised':True,'all_seven_real_external_operations_zero':True},'root_visual_review':pin('verification/sections/342-root-visual.json'),'source_audit':pin('verification/sections/342-source-audit.json'),'original_project_window':pin('verification/sections/342-main-window.json'),'source_sha256':n['source_sha256_after'],'validated_source_sha256':w['source_sha256_after'],'full_suite_rerun':False,'last_full_receipt':'verification/full-335/summary.json','last_full_receipt_is_historical_for_this_changed_source':True,'last_full_validation_sha256':sha('verification/full-335/summary.json'),'next_periodic_full_section':350,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_state_contents_parsed_copied_or_restored':False,'private_state_hashed_locally_for_preservation_only':True,'private_hashes_published':False,'game_operated':False,'chat_sent':False,'cloud_publication_binding':'enclosing_commit','cloud_published':False,'execution_environment':'local_original_windows_project_venv','local_source_parity_required_for_cloud_publication':True}
(ROOT/'verification/sections/342.json').write_bytes(enc(r));details=change+'\n\n'+validation+'\n\n'+limits+'\n\n'+pending
old_wip=subprocess.check_output(['git','show',parent+':WORK_IN_PROGRESS.md'],cwd=ROOT);(ROOT/'WORK_IN_PROGRESS.md').write_bytes(('## 第342节 + '+title+'\n\n'+now+'。'+details+'\n\n以下为历史记录；当前断点以上述342为准。\n\n').replace('\n','\r\n').encode()+old_wip)
doc('PROJECT_COMPLETED.md','## 第342节 + '+title+'\n\n'+now+'。'+details+'\n\n'+(ROOT/'PROJECT_COMPLETED.md').read_text('utf8'))
s=(ROOT/'AGENTS.md').read_text('utf8');end=s.index('\n## 项目级最高优先要求');note='下一到期完整检查须给304/305两份full320验证脚本显式传入--source-freeze及当轮根声明冻结文件；默认320仅供历史绑定。335原失败与绑定维护/复验见verification/full-335/summary.json。'
doc('AGENTS.md','## 当前续接 · 第342节 + '+title+'\n\n'+details+'\n\n继续P3；343从实际剩余节点/事件条件、掉落和固定地图缺口接续，未启动。文献前置与派出归来参考不替代账户实际解锁、服务器资格或实际领取。只跑本机必要检查；下一全量350，严格低于15%才开始当前完整小节收尾。\n\n'+note+'\n'+s[end:])
s=(ROOT/'PROJECT_REQUIREMENTS.md').read_text('utf8');start=s.index('<!-- current-delivery:start -->');end=s.index('<!-- current-delivery:end -->')+len('<!-- current-delivery:end -->');doc('PROJECT_REQUIREMENTS.md',s[:start]+'<!-- current-delivery:start -->\n## 第342节 + '+title+'\n\n'+details+'\n<!-- current-delivery:end -->'+s[end:])
s=(ROOT/'PROJECT_PROGRESS.md').read_text('utf8');assert s.count('其余未覆盖完整事件表及其奖励条件')==1;s=s.replace('其余未覆盖完整事件表及其奖励条件','未涉足之树完整服务器资格与账户实际解锁/可选、特殊区域返回判定及实际时刻、内部完整奖励/数量/培养、喙与源头关系及实际领取，其余未覆盖完整事件表及其奖励条件');doc('PROJECT_PROGRESS.md',s)
cp=read('DEVELOPMENT_CHECKPOINT.json');assert cp['completed_sections']==341 and cp['next_section']==342
for key in('current_section_validation','latest_section_environment','cloud_publication_closeout'):
 if key in cp:cp['historical_before342_'+key]=cp.pop(key)
cp.update(completed_sections=342,latest_functional_section=342,next_section=343,batch_status='P3_SECTION342_LOCAL_ACCEPTED_PUBLICATION_PENDING',next_action='第342节 + '+title+'已本机必要验收；普通推送核对后343接续P3实际剩余缺口，未启动。下次350。',full_validation_due=False)
cp['sections'].append({'number':342,'completion_ref':'p3-section-342','topic':title,'verification':'verification/sections/342.json'});cp['functional_sections_since_latest_requirement'].append(342)
cp['current_section_save']={'section':342,'verification':'verification/sections/342.json','scope':'current_functional_section','binding':'enclosing_commit'};cp['last_verified_cloud_save']['scope']='previous_functional_section'
cp['current_section_validation']={'section':342,'receipt':'verification/sections/342.json','methods_run':37,'native_isolated_window_checks':42,'original_scenes':4,'original_choices':4,'current_game_const_fields':4,'current_return_item':1,'exact_original_version_entries':8,'catalogue_groups':34,'catalogue_titles':32,'reader_kinds':16,'real_nonzero_refresh_states':2,'full_suite_rerun':False,'last_full_receipt':'verification/full-335/summary.json','last_full_receipt_is_historical_for_current_changes':True}
cp['latest_section_environment']={'section':342,'receipt':'verification/sections/342.json','native_windows':validation,'native_game_or_chat_verified':False,'current_section_full_rerun':False,'last_full_receipt':'verification/full-335/summary.json'}
cp['windows_native_validation']=validation;cp['current_batch'].update(status=cp['batch_status'],completed_sections=342,next_section=343,next_section_started=False,receipt='verification/sections/342.json',batch_closed=False)
cp['policy'].update(verification_execution_preference='local_project_environment',avoid_duplicate_cloud_tests=True)
cp['current_data_versions'].update(current_scout_game_commit='bee3f83c5d60590b5e1cd42b8d09d00ce32ab10d',current_scout_original_scenes=4,current_scout_original_choices=4,current_scout_game_const_fields=4,current_scout_original_entry_views=8,current_node_reader_groups=34,current_node_reader_titles=32,current_node_reader_kinds=16,current_scout_actual_dispatch_return_or_server_verified=False)
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes(enc(cp))
doc('CLOUD_HANDOFF.md',(ROOT/'CLOUD_HANDOFF.md').read_text('utf8')+'\n<!-- section342-handoff:start -->\n## 第342节 + '+title+'\n\n'+details+'\n<!-- section342-handoff:end -->\n')
out=ROOT/'verification/sections/342-closeout';out.mkdir();shutil.copyfile(ROOT/'.cache/open_test_window_342.py',out/'execution-main-window.py')
runpy.run_path(str(ROOT/'scripts/update_cloud_index.py'))['update'](ROOT)
(out/'execution-closeout.py').write_bytes(Path(__file__).read_bytes());(out/'applied.json').write_bytes(enc({'section':342,'local_accepted':True,'ordinary_cloud_publication_verified':False,'next343_started':False,'at_Beijing':now}))
print(json.dumps({'section':342,'local_accepted':True,'ordinary_publication_pending':True},ensure_ascii=False))
