from pathlib import Path
import subprocess,json
from datetime import datetime,timezone,timedelta
ROOT=Path(__file__).resolve().parents[1]
parent=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
assert parent=='93ef6815b261d3b5f9ab58262f4825fd7b22d537'
path=ROOT/'DEVELOPMENT_CHECKPOINT.json'
cp=json.loads(path.read_bytes())
assert cp['completed_sections']==303 and cp['next_section']==304
scope={
 'section':304,'kind':'functional_section_scope_before_implementation',
 'at_Beijing':datetime.now(timezone(timedelta(hours=8))).isoformat(),
 'parent_commit':parent,'todo':'P3 探索节点动态状态与节点事件条件',
 'capability':'按好奇心与死/窥视箱中五个具体选项，阅读标记、同节点转换、暂离再访与作战节点效果限制；仅固定资料',
 'acceptance':['两事件五完整选项分别关联正确说明，不把一种选项结果加给另一种',
 '保留两份同名原选项与文献/原件脚本边界；不把第五层3节点/2比1作为当前地图断言或概率',
 '默认未选择；独立只读作战仅显式手动打开；同范围刷新保留阅读，换范围/坏源清旧资料',
 '实现必要行为检查和实际隔离原生窗口；本机测试窗口打开；不操作游戏、不聊天、不覆盖私人状态',
 '来源/验收/要求/索引同节提交并普通推送、核对真实远端'],
 'not_new_capability':['原event_battle_links已支持的混沌源阶理论入口不重算新增','不做路线建议或生成概率','不把资料说明当实际节点转换/消耗/效果/服务器验收'],
 'status':'implementation_preparation_not_completed',
 'next_full_validation_after':305,
}
out=ROOT/'verification/sections/304-preparation/scope.json'
out.parent.mkdir(parents=True,exist_ok=True)
assert not out.exists()
out.write_bytes((json.dumps(scope,ensure_ascii=False,indent=2)+'\n').encode())
cp['active_section']={'section':304,'scope':out.relative_to(ROOT).as_posix(),'status':'implementation_in_progress','functional_progress_claimed':False}
path.write_bytes((json.dumps(cp,ensure_ascii=False,indent=2)+'\n').encode())
print('304 scope recorded; completed remains303')
