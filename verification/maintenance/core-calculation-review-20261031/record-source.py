from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import ast,ctypes,difflib,json,re,runpy,subprocess,sys,time
R=Path.cwd();sys.path[:0]=[str(R),str(R/'scripts'),str(R/'.cache/305-window-tooldeps')]
BASE='c23e8fb618932d6999c412feedb3c40b46c831b1';B=R/'verification/maintenance/core-calculation-review-20261031';prefix=B.relative_to(R).as_posix()+'/'
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
def old(n):return subprocess.check_output(['git','show',BASE+':'+n])
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==BASE
changed=['rouge/damage.py'];before='research/core-calculation-review-20261031/before-damage.py';assert old(changed[0])==(R/before).read_bytes()
old_tree=ast.parse(old(changed[0]));new_tree=ast.parse((R/changed[0]).read_bytes())
def functions(tree):return{n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
a=functions(old_tree);b=functions(new_tree);assert a.keys()==b.keys()and all(ast.dump(a[n],include_attributes=False)==ast.dump(b[n],include_attributes=False)for n in a if n!='_skill_damage_base')
drop={3,4,5,6,16,18,19,21};expected=[ast.dump(n,include_attributes=False)for i,n in enumerate(a['_skill_damage_base'].body)if i not in drop];actual=[ast.dump(n,include_attributes=False)for n in b['_skill_damage_base'].body[1:]];assert expected==actual
classes=lambda t:{n.name:ast.dump(n,include_attributes=False)for n in t.body if isinstance(n,ast.ClassDef)};assert classes(old_tree)==classes(new_tree)
unchanged=['rouge/estimate.py','rouge/relics.py','rouge/relic_attributes.py','rouge/operator_engine.py','rouge/run_modifiers.py','rouge/timing.py','rouge/reporting.py','rouge/app.py','PROJECT_REQUIREMENTS.md']
for n in unchanged:assert old(n)==(R/n).read_bytes(),n
assert not subprocess.check_output(['git','diff','--name-only',BASE,'--','rouge/data','research/runtime-reference-loaders-20261031']).strip()
sites=[]
for p in sorted((R/'rouge').glob('*.py')):
 for node in ast.walk(ast.parse(p.read_bytes())):
  if isinstance(node,ast.Name)and isinstance(node.ctx,ast.Load)and node.id in('_skill_damage','_skill_damage_base'):
   sites.append({'file':p.relative_to(R).as_posix(),'line':node.lineno,'name':node.id})
assert len(sites)==3 and all(r['file']=='rouge/damage.py'for r in sites)
suite=read(prefix+'tests-current/results.json');assert suite['passed']and suite['tests_run']==80 and suite['failed']==0 and suite['errors']==0 and not suite['forbidden_external_calls']
assert len(suite['skipped'])==1 and '0.30用户缩减计算范围'in suite['skipped'][0]['reason']
ids=re.findall(r'^test_\w+ \(([^)]+)\)',(R/(prefix+'tests-current/stderr.txt')).read_text('utf8'),re.M);assert len(ids)==len(set(ids))==80
for folder in ['tests','tests-current']:assert read(prefix+folder+'/process.json')['actual_observed_exit']==0
comparisons=read(prefix+'tests-current/comparisons.json')['comparisons'];assert len(comparisons)==75 and all(c['complete_result_equal']for c in comparisons)
net=len(old(changed[0]).splitlines())-len((R/changed[0]).read_bytes().splitlines());assert net==9
write(prefix+'source-review.json',{'baseline_commit':BASE,'changed_source':[pin(n)for n in changed],'own_prior_source':pin(before),'all_other_functions_and_phase_bounds_class_AST_unchanged':True,'removed_private_statements':[ast.unparse(a['_skill_damage_base'].body[i])for i in sorted(drop)],'remaining_internal_body_AST_exactly_equal_after_added_docstring':True,'removed_assignments':3,'removed_if_guards':5,'physical_lines_net_removed':net,'actual_static_internal_name_load_sites':sites,'unchanged_models_state_UI_and_requirements':[pin(n)for n in unchanged],'boundary':'Public calculate_damage/_calculate_damage always call unchanged _prepare_damage. Only the three original operators use _skill_damage; full-window callback keeps the same prepared operator/skill/rank. Private helper is not a separate advertised input API. Numeric/count/active-skill gates remain, including companion boolean and original normalizations.','comparison_scope':'75 valid public scenarios over all9 initial-operator skills; 54 invalid skill/rank scenarios and8 numeric/active-condition scenarios keep original exception type/message. Tests compare complete result/report/unknowns, not only totals.','measured_workload_change':{'scope':'catalog lookup calls through damage module binding for mechanist S1, complete result identical','before':5,'after':3,'runtime_speed_claimed':False},'not_proven':'No new independent mechanics/calibration, actual game clock, complete87-skill correctness, whole-program completion or video parity.','REA_scope':'Complete Python source directly reviewed per REA skill. No new REA invocation; previous actual toolbar/bridge evidence separate.'})
live=read(prefix+'live-window/window.json');assert live['passed']and live['private_six_paths_unchanged']
import win32gui,win32process
for w in live['owned_windows']:assert win32gui.IsWindowVisible(w['hwnd'])and win32process.GetWindowThreadProcessId(w['hwnd'])[1]==w['pid']and not ctypes.windll.user32.IsHungAppWindow(w['hwnd'])
a_status=read('.cache/core-calculation-review-live-status.json');time.sleep(2.2);b_status=read('.cache/core-calculation-review-live-status.json');assert b_status['toolbar_visible']and b_status['elapsed_since_launch']>a_status['elapsed_since_launch']
for n in changed:assert live['source_sha256_after'][n]==pin(n)['sha256']
write(prefix+'live-window/desktop-review.json',{'actual_windows_mcp_snapshot_called':True,'actual_image_viewed':True,'region':[1716,1164,2130,1218],'owned_window_visible_and_responding':True,'Qt_timer_advanced':True,'private_six_paths_unchanged_during_startup':True,'private_contents_or_hashes_published':False,'game_operated':False,'chat_sent':False,'new_UI_layout_validation_claimed':False})
title='首批三名技能计算删除内部重复校验，保留统一输入入口'
write(prefix+'summary.json',{'kind':'implementation_review_maintenance','title':title,'baseline_commit':BASE,'completed_sections':440,'functional_section_added':False,'implemented_scope_passed':True,'test_executions_and_unique_test_ids':80,'passed_tests':79,'historical_skipped':suite['skipped'],'new_tests':4,'full_valid_scenarios_compared':75,'invalid_selection_scenarios_compared':54,'numeric_and_active_condition_errors_compared':8,'source_review':pin(prefix+'source-review.json'),'test_receipt':pin(prefix+'tests-current/results.json'),'live_window':pin(prefix+'live-window/desktop-review.json'),'production_physical_lines_net_removed':9,'native_UI_layout_changed':False,'full_validation_rerun':False,'full440_only_original_frozen_source':True,'whole_program_complete':False,'whole_video_parity_complete':False,'P3_complete':False,'P2_complete':False,'P1_complete':False,'private_data_included':False,'game_operated':False,'chat_sent':False,'publication_binding':'enclosing maintenance commit; ordinary push and actual remote/blob equality required'})
text('research/core-calculation-review-20261031/README.md','''# 首批三名技能计算的输入边界与重复代码回顾

按REA技能直接审查完整Python源码，追踪damage._prepare_damage、内部技能计算/全技能窗口回调、藏品准备/属性符文、周期估计、完成器和报告；本轮未新调用REA，不机械扫描字节码。核对真实调用点：内部_skill_damage_base只由_skill_damage调用；_skill_damage只在三个原干员的已准备路径运行，并作为同一技能的完整窗口回调。build_estimate仅调整窗口，保持原operator/skill/rank。其它29人扩展引擎不改。

统一_prepare_damage已经拒绝无效技能/等级、未开放技能/专精，并计算培养和藏品前置；内部又重复五个条件检查、三个局部赋值，其中第二次基础攻击检查还重复了同函数上方的数值循环。移除这些内部冗余，保留公开入口和原数值/计数/当前技能条件检查、转换及错误顺序，增加内部契约说明。其余函数和PhaseBounds类AST完全不变；内部函数剩余运算语句AST保持，原数据/机制/时序/完成器/报告和界面源码未变。净减少9物理行（计入新增说明），不是性能倍数。私有helper不作为独立对外输入API。

实际执行自有原damage与当前代码，对照首批三人全部9技能、75种公开有效情景：默认、低精英/等级、不同潜能与信赖、修饰效果、酒类与静态藏品、无目标、前后摇和窗口、冲锋/部署/破屏选项。完整结果、报告和未知字段逐项相同，不仅比较总伤。另54种非法技能/等级和8种数值/当前条件保持原异常类型与文字。机械师S1中本模块的catalog引用查询由5次减至3次，完整结果相同；这是单函数查找工作量，不是实际延迟或识别速度。

最终80个不同测试身份：79通过，1项原战斗专属旧断言按用户缩减范围历史跳过，不计通过；覆盖新4项、原伤害、酒类、藏品和Qt状态同步。第一轮79次（78通过/1历史跳过）保留，新增查找次数检查后复跑实际80；不相加凑覆盖。没有改变原跳过规则或数值断言，也没有声称87技能独立校准。所有游戏/网络/聊天/凭据实际调用为零，状态目录隔离。

实际项目测试小窗更新并打开，可见响应、Qt计时推进；启动六处私人路径保持，仅公开布尔结果。界面布局和数据未改，未另跑宽范围界面验收或拿旧图冒充新数值实测。功能仍440/未开441，原full440只对应其旧冻结源码，完整选择器追加到713；全程序、独立机制与视频效果、P3/P2/P1仍未完成，识别最后。后续继续审未核对的条件/完成器/报告链路，不重复计入本次已移除的校验。
''')
n='PROGRAM_REVIEW.md';t=(R/n).read_text('utf8');t+='\n[技能计算内部校验回顾](research/core-calculation-review-20261031/README.md)核对首批三名完整调用路径，统一入口保留、删除私有内部五个重复条件和三个赋值，净减9物理行。75有效情景完整结果/报告一致，54选择错误与8数值条件错误保持；80项中79通过/1历史跳过。未证明机制独立准确、完整87技能或全程序/视频完成。\n';text(n,t)
n='IMPLEMENTATION_STRATEGY.md';text(n,(R/n).read_text('utf8')+'\n[首批技能计算边界回顾](research/core-calculation-review-20261031/README.md)通过实际调用链确定只在统一_prepare_damage校验选择，内部同一选择不重复验证；保留数值/条件与未知边界，删除8条冗余语句并说明内部契约，净减9行。75完整输出对照和公开错误比较保持，不引入新框架或猜机制；查找5→3不当作端到端提速。\n')
entry=f'''<!-- core-calculation-review-20261031:start -->
## 实现回顾维护 · {title}

统一_prepare_damage入口不变，首批三名技能的私有内部删除五个重复条件和三个赋值，剩余运算AST不变，净减9物理行；不改机制、时序、资料与界面。75有效情景完整结果/报告一致，54非法选择及8数值/当前条件错误保持；80个不同测试中79通过、1原战斗专属历史跳过不计通过。单例本模块catalog查询5→3，不称实测延迟改善。

原测试小窗更新响应，启动六处私人路径保持，无游戏/聊天/个人上传。回执：`{prefix}summary.json`。功能440/未开441，完整独立机制/87技能、全程序/全视频及P3/P2/P1未完成，识别最后。
<!-- core-calculation-review-20261031:end -->

'''
for n in ['WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md']:text(n,entry+(R/n).read_text('utf8'))
cp=read('DEVELOPMENT_CHECKPOINT.json');cp['current_maintenance_save']={'kind':'implementation_review_maintenance','title':title,'receipt':prefix+'summary.json','binding':'enclosing_commit','functional_section_added':False,'status':'partial_program_review_core_calculation_boundary','review_checklist':'PROGRAM_REVIEW.md','review_checklist_sha256':pin('PROGRAM_REVIEW.md')['sha256'],'application_review_complete':False};cp['current_batch']['receipt']=prefix+'summary.json';cp['next_action']='继续完整计算链路回顾：条件藏品/属性层、完成器和报告中的数值与未知传播，先查既有机制来源再改模型；独立算例、当前数据、未审模块与视频外观/交互仍保留。首批内部重复校验已删除，公开入口/错误保持，不重复计推进；识别最后。'
text('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n');module=runpy.run_path(str(R/'scripts/update_cloud_index.py'));module['update'](R);assert module['validate_delivery'](R,cp)['current_section']==440
from scripts.verify_full_available import maintained_selectors
selectors=maintained_selectors();assert len(selectors)==713 and selectors[-1]=='tests.test_core_calculation_review';assert read('CLOUD_INDEX.json')['requirements']['sha256']==pin('PROJECT_REQUIREMENTS.md')['sha256']
write(prefix+'final-audit.json',{'passed':True,'baseline_commit':BASE,'summary':pin(prefix+'summary.json'),'requirements':pin('PROJECT_REQUIREMENTS.md'),'cloud_index':pin('CLOUD_INDEX.json'),'ordered_selectors':713,'test_unique_ids':80,'tests_passed':79,'historical_skipped':1,'physical_source_lines_net_removed':9,'whole_program_complete':False,'whole_video_parity_complete':False,'at_UTC':datetime.now(timezone.utc).isoformat()})
(B/'record-source.py').write_bytes(Path(__file__).read_bytes());archive={p.relative_to(R).as_posix():{k:v for k,v in pin(p.relative_to(R)).items()if k!='path'}for p in sorted(B.rglob('*'))if p.is_file()and p.name!='archive-manifest.json'};write(prefix+'archive-manifest.json',{'kind':'explicit_public_archive','files':archive})
print(json.dumps({'passed':True,'tests_passed':79,'historical_skipped':1,'full_result_scenarios':75,'net_removed':9,'archive_files':len(archive),'goal_complete':False}))
