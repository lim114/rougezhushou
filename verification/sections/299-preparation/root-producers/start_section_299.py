from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,subprocess
ROOT=Path(__file__).resolve().parents[1];PARENT='b56cbf352cf5d171f52ba05839312950df462e8c'
def encode(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
assert git('branch','--show-current')=='codex/p2-development' and git('rev-parse','HEAD')==PARENT
assert not git('status','--porcelain')
remote=git('ls-remote','origin','refs/heads/codex/p2-development').split()[0];assert remote==PARENT
DEST=ROOT/'verification/sections/299-preparation';DEST.mkdir(exist_ok=False)
before={}
for name in ('rouge/battle_view.py','PROJECT_PROGRESS.md'):
 p=ROOT/name;q=DEST/'before'/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
 before[name]={'sha256':sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
scope={'section':299,'status':'scope_defined_before_functional_changes','at_utc':datetime.now(timezone.utc).isoformat(),'parent':PARENT,'actual_remote_parent':remote,
 'remaining_item':'P3固定出怪条件、分组关系及地图与敌人资料对应',
 'new_capability':'普通战斗预览可从当前出怪条目查看同组完整固定候选，并手动浏览本关主队列的其它候选组与关联包；中文列明敌人、场景物件和空动作，手动跳转已支持的固定格图/敌人资料。',
 'not_new_mechanism':'第163节已有后端分组和局外工具原键表，本节新增的是普通玩家在具体出怪预览中可操作的完整阅读及资料对应入口。',
 'before_existing_sources':before,
 'acceptance':['精确主队列+原组/包键+原action身份，不跨片段合并复用组键，不按同名敌人去重。','本关完整手动目录覆盖来源已绑定组和包，不能仅覆盖含SPAWN的组却宣称全覆盖；包中无group成员也保留。','SPAWN保留具体敌人及完整等级候选，ACTIVATE_PREDEFINED只按exactalias绑定物件，空key与EMPTY保持区别；不借其他头像或坐标。','不推实际选择、互斥次数、概率、同时出现、实际总数或绝对时间；分支不借主队列同名组。','新阅读默认未选；同范围刷新保留组/条目/页签/实际滚动选区；换关或来源失效清空旧资料和跳转，恢复不自动选择。','手动格图/敌人入口由父页重新核对精确原关卡与条目；过期/篡改身份拒绝，刷新不自动切换父筛选、地图选点或当前敌人。','必要功能与真实隔离MainWindow验证；原项目窗口更新、私人5不变；源码/要求/验收/索引逐节普通推送核对远端。'],
 'functional_complete':False,'full_validation_due':305,'other_P3_P2_P1_gaps_not_retired':True}
(DEST/'scope.json').write_bytes(encode(scope))
p=ROOT/'DEVELOPMENT_CHECKPOINT.json';cp=json.loads(p.read_bytes())
cp['active_section']={k:scope[k]for k in ('section','status','remaining_item','new_capability','acceptance')}
cp['active_section']['preparation_receipt']='verification/sections/299-preparation/scope.json';p.write_bytes(encode(cp))
p=ROOT/'WORK_IN_PROGRESS.md';p.write_bytes(('## 第299节进行中 · 当前出怪条目的同组固定候选\n\n新增普通战斗预览中的条目级中文阅读与手动格图/敌人入口，并可手动浏览本关主队列全部已绑定组与关联包。已有163分组机制不重复记功，原组/包成员关系不当作实际选择、概率或同时出场。本节尚未完成/发布，范围与验收见 verification/sections/299-preparation/scope.json。\n\n').encode()+p.read_bytes())
print(json.dumps({'section':299,'scope_defined':True,'parent':PARENT,'production_changes':0}))
