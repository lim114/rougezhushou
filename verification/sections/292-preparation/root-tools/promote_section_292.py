from pathlib import Path
from hashlib import sha256
import json,subprocess
ROOT=Path(__file__).resolve().parents[1]
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()=='63ec130238dfff0a65b8b648518328834f815725'
assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT)
base=ROOT/'.cache/p3-292-choice-preview-candidate/revision2'
names={'rouge/node_catalog_view.py':'c7398a4ae762c49bd19495f8a0692a917ee5e40a14db250915ca313f03c1506b',
 'tests/test_event_preview_filters_292.py':'e7bf4ac736b6a2c2851ab872f4d248df88480b9d274a2c9862622d7891998326'}
assert sha256((ROOT/'rouge/node_catalog_view.py').read_bytes()).hexdigest()=='ef1793eb70874fc4428ac8b8bab34a06c2cf02b69744a72c71b2b7b14632998f'
assert not (ROOT/'tests/test_event_preview_filters_292.py').exists()
for name,value in names.items():assert sha256((base/name).read_bytes()).hexdigest()==value
prep=ROOT/'verification/sections/292-preparation';prep.mkdir()
with (prep/'before-node_catalog_view.py').open('xb') as f:f.write((ROOT/'rouge/node_catalog_view.py').read_bytes())
for name in names:(ROOT/name).write_bytes((base/name).read_bytes())
copies={'CANDIDATE_HANDOFF.json':ROOT/'.cache/p3-292-choice-preview-candidate/CANDIDATE_HANDOFF.json',
 'independent-static-review.json':ROOT/'.cache/p3-292-independent-static-review/review.json',
 'filter-boundaries.md':ROOT/'.cache/p3-event-battle-entry-audit-after291/292-filter-boundaries.md',
 'existing-backend-capability-audit.json':ROOT/'.cache/p3-event-battle-entry-audit-after291/audit.json'}
for name,p in copies.items():
 with (prep/name).open('xb') as f:f.write(p.read_bytes())
cp_path=ROOT/'DEVELOPMENT_CHECKPOINT.json';cp=json.loads(cp_path.read_bytes())
assert cp['completed_sections']==291 and cp['next_section']==292
cp['active_section']={'section':292,'status':'in_progress','remaining_item':'P3节点事件与对应战斗资料的玩家阅读入口',
 'new_capability':'按完整流程场景/具体选项手动筛选现有固定作战资料，保持刷新阅读和精确来源，失效候选不沿用',
 'acceptance':'默认全集不减；同名/同关不同来源隔离；无战斗与未知下一层空入口；来源失败拒旧候选；刷新保筛选/完整token/文本滚动选区；实际隔离Windows预览；普通发布源码/要求/索引',
 'phase':'reviewed_candidate_promoted_required_tests_pending','backend_mechanics_or_data_changed':False}
cp['current_batch']['next_section_started']=True
cp['confirmed_next_stage_direction']['next_functional_section_started']=True
cp_path.write_bytes((json.dumps(cp,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
p=ROOT/'WORK_IN_PROGRESS.md';text=p.read_text(encoding='utf8')
intro=('## 第292节进行中 · 按流程和选项筛选作战预览\n\n'
 '新增玩家资料筛选入口，不重复计算已存在的五组后端连接、紧急过滤或下一层池。默认全部保留旧资料；用完整场景/选项/关卡来源恢复选择；无作战或过期来源不退回兄弟选项。'
 '验收覆盖同名选项、同关不同来源、旧普通/紧急/别名边界、阅读刷新和真实隔离窗口。不改变资格、实际触发、本局或资料引擎。候选已提升，实际测试待完成，未销项未发布。\n\n')
p.write_bytes((intro+text).encode('utf8'))
record={'section':292,'kind':'reviewed_candidate_promotion_not_completion','prior_commit':'63ec130238dfff0a65b8b648518328834f815725',
 'promoted_source_sha256':names,'new_test_methods_declared_not_executed':13,
 'backend_mechanics_or_data_changed':False,'private_state_read_or_written':False}
with (prep/'promotion.json').open('xb') as f:f.write((json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({'section':292,'promoted':True,'actual_tests_pending':True,'completed_sections':291}))
