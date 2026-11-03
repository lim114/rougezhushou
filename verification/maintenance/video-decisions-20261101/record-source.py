from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,subprocess,difflib,runpy
R=Path.cwd();B=R/'verification/maintenance/video-decisions-20261101';B.mkdir(exist_ok=False);decision='docs/decisions/2026-11-01-video-effects-decisions.md';BASE='bde603f9c6dc354d8964b1fff0d80f7ac1907782'
assert subprocess.check_output(['git','rev-parse','HEAD']).decode().strip()==BASE
def save(p,text):
 p=R/p;a=p.read_bytes().decode('utf8').splitlines(keepends=True);b=text.splitlines(keepends=True)
 for x,y,k in difflib.SequenceMatcher(None,[v.rstrip('\r\n')for v in a],[v.rstrip('\r\n')for v in b],autojunk=False).get_matching_blocks():b[y:y+k]=a[x:x+k]
 p.write_bytes(''.join(b).encode('utf8'))
summary='用户已确认：隐藏敌人提示先确认关卡身份，再核对局内实时歼灭总数；OBS动态展示不做；主要资料在一个主浮窗切换，目标旁保留少量临时卡片；接受合法适用的成熟网站页面/公开代码与本地状态、计算、缓存混合接入。个人数据不上传的边界不变。'
p='PROJECT_REQUIREMENTS.md';s=(R/p).read_text('utf8');s=s.replace('最终验收包含参考视频全部功能、交互及外观','最终验收包含参考视频中用户确认保留的功能、交互及外观（OBS动态展示已排除）',1);lines=s.splitlines(keepends=True);lines.insert(2,'\n当前确认的产品取舍：'+summary+' [完整决策摘要]('+decision+')。本次仅保存需求，开发保持450后暂停。\n\n');save(p,''.join(lines))
p='PROJECT_PROGRESS.md';s=(R/p).read_text('utf8');s=s.replace('## 待办','当前确认方向见[视频效果决策摘要]('+decision+')：采用单一主资料浮窗与临时卡片、接受成熟网站混合接入；OBS动态展示已排除，不列待办或验收缺口。\n\n## 待办',1);needle='| P3 | 视频效果对齐剩余交互 | ';assert needle in s;s=s.replace(needle,needle+'补齐单一主资料浮窗的页面切换、共享导航与阅读状态；核实并接入适用的成熟网页/代码及本地参数桥接；实现准确关卡身份与局内实时歼灭总数的只读核对、隐藏敌人提示及必要实机验证；',1);save(p,s)
p='VIDEO_PARITY.md';s=(R/p).read_text('utf8');s=s.replace('逐项对齐参考视频展示的布局、操作方式、资料联动与统计体验','按用户已确认取舍逐项对齐参考视频展示的布局、操作方式、资料联动与统计体验（OBS动态展示不纳入）',1)
lines=s.splitlines(keepends=True);found_hidden=found_obs=False;out=[]
for line in lines:
 if line.startswith('| 02:06–02:16 |'):
  found_hidden=True;out.append('| 02:06–02:16 | 关卡身份与局内实时歼灭总数核对后的隐藏敌人提示 | 用户已更正：先确认关卡身份，再核对局内实时歼灭总数。当前固定候选/机制资料不能代替这条实时计数对照链；计数字段、基准、动态分支及实际提示需恢复开发后核验。仅后台只读计数，不读取实时站位或操作战斗。 |\n')
 elif line.startswith('| 04:36–04:43 |'):found_obs=True
 else:out.append(line)
assert found_hidden and found_obs;s=''.join(out);needle='## 视频中的计划与本项目边界';assert needle in s;s=s.replace(needle,needle+'\n\n用户确认取舍（2026-11-01）：'+summary+' 04:36–04:43的OBS动态展示仅保留视频历史参考，已从对齐目标表移除；普通个人统计卡和手动图片导出继续保留。[决策摘要]('+decision+')。\n',1);save(p,s)
p='IMPLEMENTATION_STRATEGY.md';s=(R/p).read_text('utf8');lines=s.splitlines(keepends=True);lines.insert(2,'\n当前用户已确认：'+summary+' [决定及边界]('+decision+')。本次只保存方向，不代表已接入网站或完成窗口重构；开发继续暂停。\n\n');s=''.join(lines);s=s.replace('不能为解决采样污染默认把用户要直播展示的统计卡一起隐藏','OBS动态展示已被用户排除；普通个人统计卡的捕获显示按现有要求单独处理');save(p,s)
entry='## 需求确认维护：视频效果与实现方向\n\n'+summary+'\n\n已保存[决策摘要]('+decision+')并同步需求、剩余事项、实现路线和视频对照。仅文档维护，功能仍450、未启动451；开发继续暂停，全量检查保持取消。决定已确认不代表功能已实现。\n\n'
for p in ('WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md'):save(p,entry+(R/p).read_text('utf8'))
cp=json.loads((R/'DEVELOPMENT_CHECKPOINT.json').read_bytes());assert cp['completed_sections']==450 and cp['next_section']==451 and cp['batch_status']=='PAUSED_AFTER450'and cp['policy']['new_functional_sections_paused']and cp['next_full_validation_after']is None
cp['current_maintenance_save']={'title':'保存用户确认的视频取舍与混合接入方向','receipt':'verification/maintenance/video-decisions-20261101/summary.json','binding':'enclosing_commit','functional_section_added':False}
cp['latest_video_decisions']={'path':decision,'sha256':sha256((R/decision).read_bytes()).hexdigest(),'user_confirmed':True,'OBS_dynamic_display_in_scope':False,'main_reference_window':'one_main_with_lightweight_hover_cards','mature_site_hybrid_accepted':True,'hidden_enemy_detection':'confirmed stage identity plus live in-run elimination total comparison','implementation_completed_by_this_document':False}
cp['next_action']='保持第450节后暂停，未获明确恢复不启动451。恢复时先读docs/decisions/2026-11-01-video-effects-decisions.md：单一主资料浮窗、成熟网站混合接入、关卡身份与局内实时歼灭总数核对；OBS动态展示不做。其余视频效果与识别缺口继续保留，全部预定全量检查仍取消。';save('DEVELOPMENT_CHECKPOINT.json',json.dumps(cp,ensure_ascii=False,indent=2)+'\n')
(B/'summary.json').write_text(json.dumps({'kind':'user_confirmed_requirements_documentation','section':450,'functional_section_added':False,'decisions':decision,'decisions_sha256':sha256((R/decision).read_bytes()).hexdigest(),'scope':summary,'goal_remains_paused':True,'product_implementation_changed':False,'full_check_executed':False,'test_window_restarted':False,'decisions_are_not_feature_acceptance':True,'at_UTC':datetime.now(timezone.utc).isoformat()},ensure_ascii=False,indent=2)+'\n','utf8')
idx=runpy.run_path(str(R/'scripts/update_cloud_index.py'));idx['update'](R);delivery=idx['validate_delivery'](R,cp);assert delivery['current_section']==450
index=json.loads((R/'CLOUD_INDEX.json').read_bytes());assert index['batch_status']=='PAUSED_AFTER450'and index['next_full_validation_after']is None and index['full_validation_mode']=='disabled_by_user'
assert sha256((R/'PROJECT_REQUIREMENTS.md').read_bytes()).hexdigest()==index['requirements']['sha256']
for p,h in index['public_pointers'].items():assert sha256((R/p).read_bytes()).hexdigest()==h
changed=subprocess.check_output(['git','diff','--name-only','-z']).split(b'\0');assert not any(p.decode('utf8').startswith(('rouge/','scripts/','tests/','third_party/'))for p in changed if p)
assert '| 04:36–04:43 |'not in(R/'VIDEO_PARITY.md').read_text('utf8')
(B/'record-source.py').write_bytes(Path(__file__).read_bytes());files=['AGENTS.md',decision,'PROJECT_REQUIREMENTS.md','PROJECT_PROGRESS.md','VIDEO_PARITY.md','IMPLEMENTATION_STRATEGY.md','WORK_IN_PROGRESS.md','PROJECT_COMPLETED.md','DEVELOPMENT_CHECKPOINT.json','CLOUD_INDEX.json','CLOUD_HANDOFF.md',*(p.relative_to(R).as_posix()for p in B.iterdir()if p.is_file())]
(B/'archive-manifest.json').write_text(json.dumps({'scope':'Explicit public documentation only;no private state or product code.','files':{p:{'sha256':sha256((R/p).read_bytes()).hexdigest(),'bytes':(R/p).stat().st_size}for p in files}},ensure_ascii=False,indent=2)+'\n','utf8');print({'saved':decision,'functional_section':450,'goal_remains_paused':True,'OBS_removed_from_targets':True,'index_valid':True})
