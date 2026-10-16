import json, subprocess
from pathlib import Path
from datetime import datetime, timezone
from hashlib import sha256
ROOT=Path(__file__).resolve().parents[1]
parent='5607cbc46c9cf17a841939a778a247e6e1a2a371'
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='codex/p2-development'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==parent
assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT)
cp=json.loads((ROOT/'DEVELOPMENT_CHECKPOINT.json').read_bytes())
assert cp['completed_sections']==300 and cp['next_section']==301
assert json.loads((ROOT/'verification/sections/300-publication.json').read_bytes())['passed']
base=ROOT/'verification/sections/301-preparation';assert not base.exists();base.mkdir(parents=True)
for name in ('DEVELOPMENT_CHECKPOINT.json','WORK_IN_PROGRESS.md','rouge/node_catalog_view.py'):
    out=base/'before'/name;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes((ROOT/name).read_bytes())
scope={'section':301,'kind':'functional_scope_before_implementation','parent_commit':parent,
 'started_utc':datetime.now(timezone.utc).isoformat(),
 'remaining_item':'P3节点事件与掉落：其余已绑定具名奖励的中文图文与精确选项对应',
 'new_capability':'从10个事件的16条精确选项手动查看13种具名奖励的原图标、用途、完整说明和解锁原文；多选项同物品仍分开，不误勾计算状态。',
 'source_research':'.cache/p3-301-named-reward-research/READY.json',
 'source_research_sha256':sha256((ROOT/'.cache/p3-301-named-reward-research/READY.json').read_bytes()).hexdigest(),
 'acceptance':['16完整event/scene/choice三元组唯一对应13种物品（12收藏品、1零件），原完整对象、精确iconId与图片SHA/blob核对。',
  '原17typed记录、38事件、190资源与既有295/297/300入口不变；未绑定choice_ro6_rest_4不补入口，数量、完整池、本局资格/领取/生效不伪造。',
  '仅有已绑定奖励的精确事件显示入口；默认不选，手动选完整选项即可阅读相应物品，资料页保留完整身份。',
  '同有效范围刷新保留选择、页签、选区与实际非零滚动；换范围或来源失效清旧图文，恢复后不自动选回。',
  '明确区分收藏品与零件、图鉴解锁文字与当前选项条件；不写本局状态、不勾计算藏品、不操作游戏或发送聊天。',
  '实际相关必要检查、真实Windows公开隔离窗口验收，更新并打开原项目测试窗口且私人5路径保持；源码、回执、要求和云端索引同节普通推送并核实际远端。'],
 'excluded':['新增掉落机制或池','原脚本入口补全','自动领取/勾选/计算藏品','路线建议','安眠及调谐仪式新机制','识别优化'],
 'last_full_section':290,'next_full_section':305,'full_suite_rerun_this_section':False,
 'numeric_endpoint':None,'P3_complete':False}
(base/'scope.json').write_text(json.dumps(scope,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
cp['active_section']={'section':301,'scope':'verification/sections/301-preparation/scope.json',
 'status':'implementation_not_yet_completed','functional_progress_claimed':False}
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_text(json.dumps(cp,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
old=(ROOT/'WORK_IN_PROGRESS.md').read_text(encoding='utf8')
(ROOT/'WORK_IN_PROGRESS.md').write_text('## 第301节进行中 · 精确选项对应的具名奖励图文\n\n范围为16精确选项/10事件/13物品的手动图文阅读，保留实际领取和资格未知。未完成功能或发布，见 verification/sections/301-preparation/scope.json。\n\n'+old,encoding='utf8')
print(json.dumps({'section':301,'scope_saved_before_implementation':True,'parent':parent,'next_full':305}))
