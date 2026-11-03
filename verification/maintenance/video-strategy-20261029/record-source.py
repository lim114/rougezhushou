from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json, runpy, subprocess, sys

R=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(R),str(R/'scripts')]
from player_ui_verification import source_hashes

assert subprocess.check_output(['git','branch','--show-current'],cwd=R).decode().strip()=='codex/p2-development'
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R).decode().strip()
assert head=='a6bbf3e7b0e6850d5128e35140a910aa17500e91'
before=source_hashes()
assert before==json.loads((R/'verification/sections/410-source-audit.json').read_bytes())['source_sha256']

def save(name,data):
    (R/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8',newline='\n')

cp=json.loads((R/'DEVELOPMENT_CHECKPOINT.json').read_bytes())
assert cp['completed_sections']==410 and cp['next_section']==411
cp['historical_batch_before_video_strategy_20261029']={k:cp[k]for k in('current_batch','batch_status','batch_start_section','batch_target_section','next_action')}
cp.update(batch_start_section=411,batch_target_section=None,batch_status='RESUMED_VIDEO_STRATEGY_RECORDED',
    next_action='按IMPLEMENTATION_STRATEGY.md从411衔接P3；优先打通已确认场景、准确资料与笔记的小窗使用流程。411尚未实施，不将方案维护计成功能节；新数字终点未指定。下一到期全量425。')
cp['current_batch']={'start':411,'end':None,'next_full_validation_after':425,
    'status':cp['batch_status'],'completed_sections':410,'next_section':411,'next_section_started':False,
    'batch_closed':False,'receipt':'verification/sections/410.json'}
cp['policy'].update(development_paused_by_latest_user_request=False,new_functional_sections_paused=False,
    stop_after_section=None,current_user_batch_target_section=None,batch_target_section=None,
    current_user_batch_completed=False,video_effects_final_target=True,
    independently_choose_simpler_implementation=True,current_usage_remaining_percent=62,
    usage_wrap_up_triggered=False,usage_percent_available=True,
    current_usage_receipt='verification/maintenance/video-strategy-20261029/review.json')
cp['policy'].pop('paused_after_completed_section',None)
cp['cloud_publication_closeout']['development_paused']=False
cp['implementation_strategy']={'path':'IMPLEMENTATION_STRATEGY.md',
    'sha256':sha256((R/'IMPLEMENTATION_STRATEGY.md').read_bytes()).hexdigest(),
    'status':'plan_only_not_implemented_or_acceptance_passed',
    'last_functional_section':410,'next_functional_section_started':False}
save('DEVELOPMENT_CHECKPOINT.json',cp)

start='<!-- player-batch-current:start -->';end='<!-- player-batch-current:end -->'
body='''## 当前续接 · 第410节已发布，按新要求优化视频效果的实现路线

2026-10-29（北京时间），用户明确继续，要求最终达到参考录像全部功能与交互效果，并授权独立判断更方便、快捷的实现方式。410之后暂停已经解除；未指定新的数字终点。功能仍完成至410，411尚未实施，方案维护不增加功能节数。

当前方案见 [IMPLEMENTATION_STRATEGY.md](IMPLEMENTATION_STRATEGY.md)：保留已有Python/Qt能力，先打通场景、准确资料、笔记的小窗流程；复用同局快照与本机资料，减少重复查询与切窗；覆盖提示与交互面板分开；识别优化仍最后统一处理。不把换技术栈或增加栏目当作达成视频效果。

明确产品边界保持：只读后台采样和局外参考，不操作游戏、不推荐或自动选路、不上传个人数据、不使用Codex分析后端替代普通ChatGPT聊天。公开历史频率、抽取权重和本局条件概率分开；缺当前版本依据时继续查证，不能宣称整项已完成。

最后功能提交b600b1d00a53af72e0b885084682e52aac4250e4及410发布元数据已核对远端；本次方案维护另外提交，不冒充411。410完整可用验收保留原有适用范围，本次未修改实现，不重跑全量；下一到期425。P3/P2/P1仍未全部完成。'''
for name in('AGENTS.md','WORK_IN_PROGRESS.md','PROJECT_REQUIREMENTS.md'):
    p=R/name;text=p.read_text('utf8');assert text.count(start)==text.count(end)==1
    left,rest=text.split(start);_,right=rest.split(end,1)
    p.write_text(left+start+'\n'+body+'\n'+end+right,encoding='utf8',newline='\n')

p=R/'VIDEO_PARITY.md';text=p.read_text('utf8')
text=text.replace('## 当前证据与后续顺序','## 实现路线调整 · 2026-10-29\n\n最终仍需达到上表全部演示功能与交互效果，不能只对齐外观或部分入口。先按 [实现路线](IMPLEMENTATION_STRATEGY.md) 整合现有Qt能力和场景关联流程，复用一次读取结果与本机资料；再补完整数据和覆盖层，最后统一识别验收。技术思路可独立取舍，隐私、只读和不自动选路边界不变。本文各项未完成标记保持，方案本身不算交付。\n\n## 当前证据与后续顺序')
p.write_text(text,encoding='utf8',newline='\n')

index=runpy.run_path(str(R/'scripts/update_cloud_index.py'));index['update'](R)
validation=index['validate_delivery'](R,cp)
after=source_hashes();assert before==after
out=R/'verification/maintenance/video-strategy-20261029';out.mkdir(parents=True,exist_ok=False)
receipt={'kind':'requirements_and_design_maintenance','functional_section_incremented':False,
    'completed_sections':410,'next_section':411,'next_section_started':False,
    'user_continue_revoked_previous_pause':True,'new_numeric_target_specified':False,
    'parent_verified_remote_commit':head,'independent_design_review_completed':True,
    'implementation_changed':False,'new_feature_acceptance_claimed':False,
    'source_count':len(before),'source_before_equals_410_audit_and_after':before==after,
    'full_suite_rerun':False,'full410_scope_reused_without_new_execution':True,
    'next_periodic_full':425,'index_validation':validation,
    'strategy_sha256':cp['implementation_strategy']['sha256'],
    'required_strategy_summary_in_hashed_requirements':True,
    'usage':{'remaining_percent':62,'window_minutes':10080,'secondary_unavailable':True,
        'source':'actual account usage tool usedPercent38','triggered':False},
    'remaining_percent':62,'triggered':False,
    'new_continuous_video_playback_claimed':False,'private_contents_included':False,
    'game_operated':False,'chat_sent':False,'recorded_UTC':datetime.now(timezone.utc).isoformat()}
(out/'review.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n','utf8')
(out/'record-source.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'maintenance_recorded':True,'completed_sections':410,'next_section_started':False,
    'source_count_unchanged':len(after),'index_valid':True},ensure_ascii=False))
