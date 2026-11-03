"""Root assembles the actual five-section validation and progress report."""
import datetime
import hashlib
import json
from pathlib import Path

BASE=Path('/workspace/.continuation')
ROOT=Path('/workspace/rougezhushou')
OUT=BASE/'root-section105-save-spec-v2.json'
assert not OUT.exists()
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
load=lambda name:json.loads((BASE/name).read_bytes())
linux=load('full105-linux-v1.json');wine=load('full105-wine-v1.json')
gui=load('full105-window-actual-v2/wine-ui-100.json')
saved=load('root-full105-saved-audit-v1.json')
visual=load('full105-visual-audit-v1.json')
supervisor=load('full105-window-supervisor-v2.json')
guard=load('resume105-applied-source-v1.json')
assert linux['available_checks_passed'] is wine['available_checks_passed'] is True
assert gui['passed'] is True and gui['complete_ui_validation'] is True
assert saved['passed'] is saved['workflow_complete'] is True and saved['saved_states']==52
assert visual['passed'] is visual['workflow_complete'] is True and visual['actually_viewed_images']==4
assert supervisor['child_primary_exit']==supervisor['supervisor_exit']==0 and not supervisor['timed_out']
assert supervisor['owned_session_closure']['no_live_owned_execution_verified'] is True
assert len(guard['source_sha256'])==748
assert gui['after_section']==105 and gui['total_actual_checks']==4283
assert wine['environment_capability_skips']==3

# This fresh builder is Root-executed only after actual retry2 + Saved + visual.
# No output is written until every terminal gate below succeeds.
assert not (BASE/'full105-actual-closure-v2.json').exists()
assert not (BASE/'full105-progress-report-v2.md').exists()
def fingerprint(path):
    path=Path(path);raw=path.read_bytes()
    return {'source':str(path),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
def actual_exit(name):
    raw=(BASE/name).read_bytes()
    assert raw==b'0\n', (name,raw)
    return fingerprint(BASE/name)
for name in ('root-section105-apply-v1.exit-code','root-full105-guard-builder-v1.exit-code',
             'section105-portable-node-font-actual-wine-v1.exit-code',
             'full105-wine-capability-probe-v1.exit-code','full105-linux-v1.exit-code',
             'full105-wine-v1.exit-code','full105-window-primary-v2.exit-code',
             'root-full105-saved-audit-v1.exit-code'):
    actual_exit(name)

suite_guard_path=BASE/'full105-source-suite-guard-v1.json'
suite_guard_raw=suite_guard_path.read_bytes();suite_guard=json.loads(suite_guard_raw)
assert suite_guard['source_sha256']==guard['source_sha256']
assert suite_guard['source_additional_sha256']==guard['source_additional_sha256']
assert set(guard['source_additional_sha256'])=={'CORE_0.70_VERIFICATION.json'}
for field in ('source_sha256','source_additional_sha256'):
    for relative,expected in guard[field].items():
        assert hashlib.sha256((ROOT/relative).read_bytes()).hexdigest()==expected, relative
    assert gui[field]==gui[field+'_after']==guard[field]
    assert wine[field]==wine[field+'_after']==guard[field]
assert gui['source_drift']==gui['source_additional_drift']==[]
assert wine['source_drift']==wine['source_additional_drift']==wine['adapter_source_drift']==[]
assert linux['source_drift']==[]
# Linux receipt itself owns its 355-source subset, not the complete748 map.
assert len(linux['source_sha256'])==355
assert all(guard['source_sha256'].get(k)==v for k,v in linux['source_sha256'].items())
linux_all=load('full105-linux-root-source-audit-v1.json')
assert linux_all['passed'] is linux_all['workflow_complete'] is True
assert linux_all['source_count']==748 and linux_all['source_drift']==[]
assert linux_all['source_guard_sha256']==hashlib.sha256(suite_guard_raw).hexdigest()
assert linux_all['native_windows_verified'] is False
assert linux['complete_repository_validation'] is wine['complete_repository_validation'] is False
assert linux['failures']==linux['errors']==wine['failures']==wine['errors']==0

runner_path=BASE/'full105-progress-bounded-window-source-v2/window.py'
supervisor_source=BASE/'full105-progress-bounded-window-source-v2/supervisor105.py'
runner_pin='0004f90b316ec6bc576ac893ce67f52e09e9db4508edd8708f431676b36695a1'
supervisor_pin='477cf622f56e77a87850790f99c37dbdef3d6466b74697e9783417e83cf3efc3'
assert fingerprint(runner_path)['sha256']==runner_pin==gui['runner_sha256']
assert fingerprint(supervisor_source)['sha256']==supervisor_pin==supervisor['supervisor_sha256']
assert gui['source100_guard_sha256']==hashlib.sha256(suite_guard_raw).hexdigest()
assert gui['full105_attempt']==supervisor['full105_attempt']==2
assert gui['deadline_seconds']==supervisor['deadline_seconds']==1200
assert supervisor['after_section']==105 and supervisor['status']=='completed'
assert supervisor['timed_out'] is False
assert supervisor['native_windows_verified'] is supervisor['global_wineserver_terminated'] is False
expected_argv=['/workspace/.compat/run-wine-python.sh',
               'Z:\\workspace\\.continuation\\full105-progress-bounded-window-source-v2\\window.py',
               '--root','Z:\\workspace\\rougezhushou',
               '--guard','Z:\\workspace\\.continuation\\full105-source-suite-guard-v1.json',
               '--out','Z:\\workspace\\.continuation\\full105-window-actual-v2']
assert supervisor['argv']==expected_argv and supervisor['cwd']==str(ROOT)
assert gui['total_actual_checks']==len(gui['checks'])==4283
assert gui['new_state_archive090']['records']==52
assert gui['global_profile_or_trace_used'] is gui['old095_complete_function_vector_measured'] is False
assert gui['specialist101_104_validation_in_this_runner'] is False
progress_path=BASE/'full105-window-actual-v2/full105-progress.json'
progress=json.loads(progress_path.read_bytes())
assert progress['kind']=='FULL105_ATTEMPT2_APPENDED_CHECK_PROGRESS'
assert progress['after_section']==105 and progress['attempt']==2
assert progress['passed'] is progress['workflow_complete'] is progress['complete_function_vector_measured'] is False
assert progress['checkpoint_every_appended_checks']==32
assert type(progress['appended_checks']) is int and 0<=progress['appended_checks']<=len(gui['checks'])
assert progress['appended_checks']%32==0
assert saved['actual_gui_checks']==4283 and saved['main_source_files']==748
assert saved['primary_exit']==0 and saved['source_drift']==[]
assert saved['no_live_owned_execution_verified'] is True
assert saved['saved_archive_sha256']==gui['new_state_archive090']['sha256']
assert saved['png_hashes_checked']==gui['screenshots100']
assert saved['native_aliases_verified_by_this_audit'] is saved['full_result_equality_to_old_gold_verified'] is False
assert saved['old095_complete_function_vector_measured'] is saved['native_windows_game_chat_verified'] is False

first_path=BASE/'full105-window-supervisor-v1.json'
first=fingerprint(first_path)
assert first['sha256']=='b49a2771bea0121cc2a84c6c4e0c6a113d7fb020ffc5b2aed9db81de8103cbb6'
first_supervisor=json.loads(first_path.read_bytes())
assert (BASE/'full105-window-primary-v1.exit-code').read_bytes()==b'124\n'
assert first_supervisor['child_primary_exit']==-9 and first_supervisor['supervisor_exit']==124
assert first_supervisor['timed_out'] is True and first_supervisor['deadline_seconds']==600
assert first_supervisor['elapsed_seconds']==600.1465337909904
assert not (BASE/'full105-window-actual-v1/wine-ui-100.json').exists()
partial_visual=load('full105-visual-partial-ledger-v1.json')
assert partial_visual['actually_viewed_images']==3 and partial_visual['passed_claimed'] is False
assert len(partial_visual['pngs'])==3 and all(row['actually_viewed'] is True for row in partial_visual['pngs'])
attempts=[{'attempt':1,'status':'TIMED_OUT_INCOMPLETE_NOT_PASS','primary_exit':124,
           'child_primary_exit':-9,'supervisor_exit':124,'timed_out':True,'deadline_seconds':600,
           'elapsed_seconds':first_supervisor['elapsed_seconds'],'partial_pngs_actually_viewed':3,
           'final_gui_receipt_present':False,'supervisor':first,
           'primary':fingerprint(BASE/'full105-window-primary-v1.exit-code'),
           'partial_visual_ledger':fingerprint(BASE/'full105-visual-partial-ledger-v1.json')},
          {'attempt':2,'status':'ACTUAL_COMPLETE_BOUNDED_GUI_PASS','primary_exit':0,
           'child_primary_exit':supervisor['child_primary_exit'],'supervisor_exit':supervisor['supervisor_exit'],
           'timed_out':supervisor['timed_out'],'deadline_seconds':supervisor['deadline_seconds'],
           'elapsed_seconds':supervisor['elapsed_seconds'],'actual_checks':gui['total_actual_checks'],
           'saved_states':gui['new_state_archive090']['records'],
           'argv':supervisor['argv'],'runner':fingerprint(runner_path),
           'supervisor_source':fingerprint(supervisor_source),
           'supervisor':fingerprint(BASE/'full105-window-supervisor-v2.json'),
           'primary':fingerprint(BASE/'full105-window-primary-v2.exit-code'),
           'final_gui_receipt':fingerprint(BASE/'full105-window-actual-v2/wine-ui-100.json'),
           'progress_partial_only':fingerprint(progress_path),
           'saved_readback':fingerprint(BASE/'root-full105-saved-audit-v1.json'),
           'actual_visual_ledger':fingerprint(BASE/'full105-visual-audit-v1.json'),
           'no_live_owned_execution_verified':True,
           'owned_session_absence_verified':supervisor['owned_session_closure']['owned_session_absence_verified']}]
def summary(result):
    names=('tests_run','tests_passed','historical_or_declared_skips','unavailable_records',
           'unavailable_parent_count','failures','errors')
    return {key:result[key] for key in names}
closure={'after_section':105,'section_group':[101,102,103,104,105],
    'status':'PASSED_AVAILABLE_MAINTAINED_AND_BOUNDED_GUI_SCOPE',
    'validated_at_Beijing':stamp,'available_checks_passed':True,'batch_validation_closed':True,
    'complete_repository_validation':False,'native_windows_game_chat_verified':False,
    'archive':'verification/full-105','linux':summary(linux),'wine':summary(wine),
    'environment_capability_skips':3,'source_files':748,'additional_CORE_verified':True,
    'current_physical_test_modules':221,'full_actual_union_selectors':239,
    'gui_passed':True,'actual_gui_attempts':2,'gui_attempts':attempts,'actual_gui_checks':4283,'saved_states':52,
    'four_pngs_actually_viewed':True,'saved_legacy_codec_aliases_verified':False,
    'old_complete_fullGold_equality_verified':False,'old095_complete_function_vector_measured':False,
    'full095_deferred_preserved':True,'scope':'Current239 maintained available selector union plus inherited bounded healthy functional MainWindow suite. Specialist101–104 receipts separately archived. Missing evidence, original skips and3 actual Wine capability bodies are not PASS.'}
closure_path=BASE/'full105-actual-closure-v2.json'
with closure_path.open('x') as f:json.dump(closure,f,ensure_ascii=False,indent=2);f.write('\n')
commits={n:load(f'section{n:03d}-publication-v1.json')['local_HEAD'] for n in range(101,105)}
report=f'''# 第101–105节进度与未完成项目

{stamp}（北京时间）。本组五节已完成实际检验；本报告与闭合断点随105归档提交。101–104各有真实commit/push；105本报告随该节提交。所有改动在codex/p2-development。

| 小节 | 完成范围 | 保存 |
| --- | --- | --- |
| 101 | 培养、计数和未知强化资料的安全消费；保留原输入与明确拒绝 | [{commits[101][:7]}](https://github.com/lim114/rougezhushou/commit/{commits[101]}) |
| 102 | 坏库存完成标记不冒充完整确认；有效当前页和同条件历史仍可确认 | [{commits[102][:7]}](https://github.com/lim114/rougezhushou/commit/{commits[102]}) |
| 103 | 首次招募来源与分队缓存合法恢复；原强事实保护不阻挡坏ID修复 | [{commits[103][:7]}](https://github.com/lim114/rougezhushou/commit/{commits[103]}) |
| 104 | 缺value或坏形状资源按未读保旧事实/时间，合法同页信息更新；真实写盘失败边界 | [{commits[104][:7]}](https://github.com/lim114/rougezhushou/commit/{commits[104]}) |
| 105 | 恢复20遗漏选择项（69既有方法），真实中文字体OCR测试，五节全量可用检验 | 本节实际commit/push证明另存，不能在提交前虚构自身hash |

本组新增90个真实API测试方法；102另恢复52个原方法的登记，105恢复69个原方法。Source方法数不是本次实际通过数。当前221物理测试模块、116精选登记、239全量选择项。

| 本轮实际检验 | 运行 | 实际通过 | 跳过 | 不可用父项／记录 | 失败／错误 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Linux | {linux['tests_run']} | {linux['tests_passed']} | {linux['historical_or_declared_skips']} | {linux['unavailable_parent_count']}／{linux['unavailable_records']} | 0／0 |
| Wine Windows二进制 | {wine['tests_run']} | {wine['tests_passed']} | {wine['historical_or_declared_skips']} | {wine['unavailable_parent_count']}／{wine['unavailable_records']} | 0／0 |

不可用记录含子例与setUpClass，不能用这些列做简单加减。Wine87跳过包含3个实际诊断的符号链接能力限制，三个原fixture主体未执行，不计PASS；其余为原声明跳过。私人历史图片/缓存与缺少环境依赖按原分类器公开记录。未放宽分类器、断言或图像阈值，未伪造资料。

当前Source748+CORE全图前后匹配。字体单项真实OCR原七断言通过，保留原缺msyh字体探测raw1、原测试raw9和修正后raw0；使用真实Noto Sans CJK SC，无字体伪装/跳过。复现命令须设置ROUGE_TEST_CJK_FONT到可加载的真实字体文件，Wine本环境为Z:\\usr\\share\\fonts\\opentype\\noto\\NotoSansCJK-Regular.ttc。

实际窗口第2次运行完成4283检查、52保存状态，四图实际查看，最终primary/child/supervisor均0。第1次600秒预算超时，原primary124、child-9、实际600.1465337909904秒、三张已查看PNG且无终稿均完整保留；第一次不计PASS。第2次预算1200秒，简短progress只记录已追加checks下界，不能替代完整终稿或声明全向量测量完成。52个旧Gold对比只证明原显式public projection；当前完整结果与三全文另存，未证明整个旧FullGold相等。旧native090 codec不表达alias，五组旧合成状态×两显示模式为十个内存消费者回放，不是十次真实constructor/apply或自然OCR。101–104专项实际窗口、真实观察、完整native和关闭/直接RunState重载证据各自保留。Supervisor证明无仍执行的owned进程；保留的Z进程不代表已reap或owned-session不存在。

## 未完成项目

[PROJECT_PROGRESS.md](../../PROJECT_PROGRESS.md)仍有18组实际待办。当前P2主要缺口为技能真实时序与精度、召唤物模组的原生附着/数量/时钟、本局环境的账户解锁与buff层/动态关卡脚本依据。这些机制缺口不能由缓存健壮性或Wine测试销项。P2完成后进入P3；P1保留原断点；识别优化仍放最后。

路线与事件/掉落、固定地图坐标与出怪时间轴/条件分支、敌人原生机制及图片分类资料、更多客户端聊天兼容、Windows安装/升级/卸载/多机器验收亦保留原待办。原生Windows、实际游戏连续采样与客户端聊天未验证。第95节完整窗口三次未完成仍搁置，不进行第四次无诊断重放，不记全量PASS。

下一节106合并处理环境信息的适用模式、敌人等级bool身份和非文本来源报告三个相关问题。已做原API实际观察33组/284调用/350native，原问题及19 ValueError/5 TypeError保留；仅代表原实现观察。所有22合法新观察恢复和重载已按实际记录核对。106候选尚未编入/未验收，不计为完成；完成105实际保存后依序推进。
'''
report_path=BASE/'full105-progress-report-v2.md'
with report_path.open('x') as f:f.write(report)
entries=[]
for p in sorted(BASE.iterdir()):
    if p.name.startswith(('section105-', 'full105-')):
        entries.append({'source':str(p),'destination':'public-current105/'+p.name})
for name in ('root-section105-apply-v1.py','root-section105-apply-v1.log','root-section105-apply-v1.exit-code',
    'root-section105-scripts-INDEPENDENT_SOURCE_REVIEW-v1.md','resume105-applied-source-v1.json',
    'root-full105-guard-builder-v1.py','root-full105-guard-builder-v1.log','root-full105-guard-builder-v1.exit-code',
    'root-full105-saved-audit-v1.py','root-full105-saved-audit-v1.json','root-full105-saved-audit-v1.log',
    'root-full105-saved-audit-v1.exit-code','root-live-recovery-section105.json','root-section105-spec-builder-v1.py'):
    entries.append({'source':str(BASE/name),'destination':'actual-root-evidence/'+name})
entries.append({'source':str(Path(__file__).resolve()),'destination':'actual-root-evidence/root-section105-spec-builder-v2.py'})
entries.extend([{'source':str(BASE/'section104-publication-v1.json'),'destination':'prior-publication.json'},
    {'source':str(BASE/'section104-saved-readback-independent-source-review-v1'),'destination':'post104-supplementary-source-review'},
    {'source':str(report_path),'destination':'REPORT_ZH.md'},
    {'source':str(closure_path),'destination':'closure.json'}])
for n in range(101,105):
    entries.append({'source':str(BASE/f'section{n:03d}-publication-v1.json'),
                    'destination':f'actual101-104-publications/section{n:03d}.json'})
text=('20个遗漏选择项恢复69个既有方法，中文字体真实OCR原七断言通过。'
      '本组Linux2240运行/2018PASS/84skip/U191records150parents/0失败0错误；'
      'Wine2307运行/2094PASS/87skip（含3已诊断能力限制）/U186records145parents/0失败0错误。'
      '当前748+CORE全图未漂移。实际窗口第二次4283检查/52状态/四图/保存读回及无live-owned执行检查通过，保留第一次600秒超时primary124/child-9；'
      '原生Windows/游戏/聊天及原095完整向量未验证，旧codec无alias与旧Gold全图比较限度保留。')
spec={'section':105,'topic':'测试登记与五节全量检验','archive':'verification/full-105',
    'source_guard':str(BASE/'resume105-applied-source-v1.json'),
    'exit_files':[str(BASE/name) for name in ('root-section105-apply-v1.exit-code',
        'root-full105-guard-builder-v1.exit-code','section105-portable-node-font-actual-wine-v1.exit-code',
        'full105-wine-capability-probe-v1.exit-code','full105-linux-v1.exit-code','full105-wine-v1.exit-code',
        'full105-window-primary-v2.exit-code','root-full105-saved-audit-v1.exit-code')],
    'pass_receipts':[str(BASE/'full105-linux-root-source-audit-v1.json'),str(BASE/'root-full105-saved-audit-v1.json'),
                     str(BASE/'full105-visual-audit-v1.json')],
    'public_evidence':entries,'previous_publication':str(BASE/'section104-publication-v1.json'),
    'next_action':'105真实commit/push并展示101–105总结后继续106环境适用模式/敌人bool身份/来源报告组合；每节真实保存，下一次五节全量110；P2未知机制及095/native边界保留。',
    'archive_readme':'# 第101–105节全量可用检查\n\n实际范围与未完成事项见REPORT_ZH.md、closure.json；所有公开原件由manifest.json逐项SHA核对。当前仍非原生Windows或完整仓库PASS。Source-only材料不计为运行或进度，原失败/不可用/跳过未删除。',
    'section_receipt':{'implemented_scope':['20 original selector registrations recovered','Explicit real portable CJK font fixture',
        'Actual five-section Linux/Wine/bounded MainWindow validation'],
        'recovered_original_test_methods':69,'original_font_assertions':7,'full_validation':closure,
        'remaining_project_groups':18,'next_full_validation_after':110,'new_source_files':0},
    'completed_paragraph':text+' 完成项归档verification/full-105；106仍未编入，不冒充P2机制销项。',
    'work_paragraph':'105全量可用Linux/Wine/实际窗口及saved/四图验收通过，正在真正commit/push本节及总结。完成后依序106组合推进；每节commit/push，110后再全量和总结。'}
with OUT.open('x') as f:json.dump(spec,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'spec':str(OUT),'public_entries':len(entries)}))
