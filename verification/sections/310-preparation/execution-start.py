from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,subprocess
ROOT=Path(__file__).resolve().parents[1]
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
assert git('branch','--show-current').decode().strip()=='codex/p2-development'
assert git('rev-parse','HEAD').decode().strip()=='6e3ffdc262e0934f4203994a9634efb1320f4f05'
assert not git('status','--porcelain').strip()
out=ROOT/'verification/sections/310-preparation';out.mkdir();source=ROOT/'research/p3-boss-cycle-310';source.mkdir()
pins={}
for folder,sub,handoff_name,handoff_sha in [('p3-310-boss-research','','HANDOFF.json','6252d3ef3cee23aab3854ae01e3c1a389a555f7ceb8129da91b74dac805a2bd6'),('p3-310-source-final-review','final-review','HANDOFF_FINAL.json','6fc6753177478b9867a96733dc87a6a291f96890794b07e5faa1972642dc6003')]:
    origin=ROOT/'.cache'/folder;raw=(origin/handoff_name).read_bytes();assert sha256(raw).hexdigest()==handoff_sha
    h=json.loads(raw);dest=source/sub;dest.mkdir(exist_ok=True)
    for name,pin in h['files'].items():
        content=(origin/name).read_bytes();assert sha256(content).hexdigest()==pin['sha256'] and len(content)==pin['bytes']
        (dest/name).write_bytes(content);pins[(dest/name).relative_to(ROOT).as_posix()]=pin
    (dest/handoff_name).write_bytes(raw)
cp_path=ROOT/'DEVELOPMENT_CHECKPOINT.json';cp=json.loads(cp_path.read_bytes());assert cp['completed_sections']==309 and cp['next_section']==310
cp['batch_start_section']=310;cp['batch_status']='P3_SECTION310_IN_PROGRESS';cp['current_batch'].update(start=310,end=cp['batch_target_section'],status=cp['batch_status'],batch_closed=False,next_section_started=True)
cp['active_section']={'number':310,'completed':False,'remaining_todo':'P3敌人面板与机制：其余首领的完整文献流程','proposed_capability':'混沌源阶理论中洛伦茨/源阶方的交替激活与模块条件阅读；按主体与条件分组，含原先漏抽的装置技能表','acceptance':['仅两个精确首领引用显示入口，模块与源阶粒素不借用敌人身份','完整文献7条流程按主循环/首次半血/终点退场/模块两类结果分组，不成为必然时间轴','保留7技能、2能力与独立装置技能/机制完整原件，模块白值仅技术，零字段不当本局预测','同来源刷新保留阅读，两身份切换或来源失效清空，恢复手动重开','不修改任何数值模型/地图/本局；必要检查、实际Windows阅读、项目要求与云端发布核对后才计完成']}
cp['next_action']='第310节进行中：补齐洛伦茨—源阶方与模块的有条件资料流程。完成与发布之前已交付仍309。';cp_path.write_bytes(enc(cp))
now=datetime.now(timezone.utc).isoformat();p=ROOT/'WORK_IN_PROGRESS.md';p.write_text('## 当前进行第310节（尚未验收、发布）\n\n'+now+'。拟交付：混沌源阶理论的交替激活、首次半血、终点退场与模块两类结果资料。两个精确首领入口、四类阅读主题、原先遗漏的装置技能与机制；不推当前模式/数量/阶段数值/倒计时，不把七流程当线性时序。切换或坏源清旧、同源刷新保留，完成前已交付仍309。\n\n以下为已交付历史。\n\n'+p.read_text('utf8'),encoding='utf8')
(out/'source-promotion.json').write_bytes(enc({'section':310,'kind':'source_only_before_implementation_not_acceptance','at_utc':now,'source_pins':pins,'complete_public_revisions':['441767','436997','440218','427939'],'root_read_complete_source_effects_and_final_review':True,'missing_module_skill_table_recovered_from_original_full_HTML':True,'source_counting':'7 boss skills +2 ability cards +1 independent module skill table','runtime_game_or_stage_values_verified':False,'private_game_or_chat_used':False}))
(out/'execution-start.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'started':310,'still_completed':309,'frozen_public_files':len(pins),'current_game_state_not_inferred':True}))
