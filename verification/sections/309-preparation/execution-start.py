from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json, shutil, subprocess
ROOT=Path(__file__).resolve().parents[1]
def enc(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def read(p):return json.loads(p.read_bytes())
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()=='3bde3fa28159c9346d18e5d529e7e5620d3911fa'
assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT).strip()
out=ROOT/'verification/sections/309-preparation';out.mkdir()
source=ROOT/'research/p3-boss-phase-309';source.mkdir()
pins={}
for folder,sub in [('p3-309-boss-lifecycle-research',''),('p3-309-source-final-review','final-review')]:
    origin=ROOT/'.cache'/folder;handoff=read(origin/'HANDOFF.json')
    dest=source/sub;dest.mkdir(exist_ok=True)
    for name,pin in handoff['files'].items():
        original=(origin/name).read_bytes();assert sha256(original).hexdigest()==pin['sha256'] and len(original)==pin['bytes']
        (dest/name).write_bytes(original);pins[(dest/name).relative_to(ROOT).as_posix()]=pin
    shutil.copyfile(origin/'HANDOFF.json',dest/'HANDOFF.json')
cp_path=ROOT/'DEVELOPMENT_CHECKPOINT.json';cp=read(cp_path)
assert cp['completed_sections']==308 and cp['next_section']==309
cp['batch_start_section']=309;cp['batch_status']='P3_SECTION309_IN_PROGRESS'
cp['current_batch'].update(start=309,end=cp['batch_target_section'],status=cp['batch_status'],batch_closed=False,next_section_started=True)
cp['active_section']={'number':309,'remaining_todo':'P3敌人面板与机制：首领阶段资料','proposed_capability':'畸症首领按文献形态阅读招式、进入离开条件及第三形态循环/飞行返回关系；不是阶段数值模型','acceptance':['精确关卡/敌人/整数等级才出现独立入口，其他敌人隐藏','6文献名称条目、6技能卡和7转换条件由两份完整文献及固定原记录核对；保留来源差异','同来源刷新保留阅读选择，切换或坏源清旧内容；恢复手动重开','不改变预计数值/地图/实际本局状态；必要检查及原生窗口验证后方可销项'],'completed':False}
cp['next_action']='第309节进行中：补齐畸症首领的文献形态与转换阅读；完成与发布之前保持已交付308。'
cp_path.write_bytes(enc(cp))
now=datetime.now(timezone.utc).isoformat()
p=ROOT/'WORK_IN_PROGRESS.md';p.write_text('## 当前进行第309节（尚未验收、发布）\n\n'+now+'。拟交付：畸症首领按文献形态查看招式、进入离开条件、第三形态循环与飞行返回关系。精确引用外隐藏入口，同资料刷新保留阅读，切换或来源失效清空、恢复手动重开。数值口径不能直接对算的差异保留，不增加阶段面板或实况判断。当前已完成仍为308，P3/P2/P1均未全部完成。\n\n以下为已交付历史。\n\n'+p.read_text('utf8'),encoding='utf8')
(out/'source-promotion.json').write_bytes(enc({'section':309,'kind':'source_only_promoted_before_implementation_not_acceptance','at_utc':now,'source_pins':pins,'source_revision':['435612','420841'],'mode_header_extraction_error_fixed_in_build_not_original_freeze':True,'source_review_read_by_root':True,'no_numerical_contradiction_or_runtime_phase_proven':True,'private_game_chat_used':False}))
(out/'execution-start.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'started':309,'still_completed':308,'source_files':len(pins),'source_reviewed':True}))
