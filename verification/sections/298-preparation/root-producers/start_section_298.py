from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import json,subprocess
ROOT=Path(__file__).resolve().parents[1]
PARENT='bb4927a2a2760d48882f3945b750053d7a5617fc'
DEST=ROOT/'verification/sections/298-preparation'
def encode(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
def digest(p):return sha256(p.read_bytes()).hexdigest()
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==PARENT
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='codex/p2-development'
assert subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)==''
remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/codex/p2-development'],cwd=ROOT,text=True).split()[0]
assert remote==PARENT
DEST.mkdir(exist_ok=False)
names=['rouge/node_catalog.py','rouge/event_planning.py','rouge/node_catalog_view.py','rouge/player_node_information.py','tests/test_node_catalog.py','PROJECT_PROGRESS.md']
before={}
for name in names:
 p=ROOT/name;q=DEST/'before'/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
 before[name]={'sha256':digest(p),'bytes':p.stat().st_size}
scope={'section':298,'status':'scope_defined_before_functional_changes','at_utc':datetime.now(timezone.utc).isoformat(),'parent':PARENT,'actual_remote_parent':remote,
 'before_existing_sources':before,'remaining_item':'P3难度、层数及前置对具体节点/事件资格的影响',
 'new_capability':'5类节点、6组精确事件接入资料明确的自然主层禁区；目录和地图候选说明原因，已读/历史与手动资料入口保留；两项科技仅说明已知开启途径。',
 'acceptance':['6事件×6主层完整矩阵；只对明确自然主层应用新禁区，允许层不等于必生成。','特殊区域、未知入口、加工品、已读内容、历史不借新禁区删除；本局与原目录不改。','完整来源与029继承类型声明核对，热缓存来源或实际目录对象变更不借旧限制。','默认190资源、38玩家输出不变；显式上下文只改变本组六事件，17typed/25场景57选项/10附注/15关卡层数不冒称补完。','真实隔离MainWindow可查看排除理由，手动读已排除项/历史；刷新保持选择、页签、实际滚动及选区；来源失效清旧限制回未知。','不采游戏、不发聊天、不覆盖私人5路径；必要验证及原窗口更新后逐字节普通推送要求、索引和源码。'],
 'functional_complete':False,'full_validation_due':305}
(DEST/'scope.json').write_bytes(encode(scope))
cp=ROOT/'DEVELOPMENT_CHECKPOINT.json';d=json.loads(cp.read_bytes())
d['active_section']={k:scope[k]for k in ('section','status','remaining_item','new_capability','acceptance')}
d['active_section']['preparation_receipt']='verification/sections/298-preparation/scope.json'
cp.write_bytes(encode(d))
wp=ROOT/'WORK_IN_PROGRESS.md';wp.write_bytes(('## 第298节进行中 · 自然主层条件与节点资料保留\n\n六组事件接入五类节点已有文献禁区，来源和适用范围先核后算；普通目录仍可查阅，实际已读和历史内容不被自然池条件擦除。两项科技只列已证开启途径，不建立未点亮的反向硬门。验收标准见 verification/sections/298-preparation/scope.json；尚未计为完成或云端已发布。\n\n').encode()+wp.read_bytes())
candidate=ROOT/'.cache/p3-298-event-requirements-candidate'
h=candidate/'HANDOFF.json';assert digest(h)=='3a49cab299d40a5852fb59da53ef6535deae3d781ae48a3c0fbfc3a4076aa657'
packet=json.loads(h.read_bytes());base=ROOT/packet['candidate_root']
for name,pin in packet['promotion_allowlist'].items():
 p=base/name;assert digest(p)==pin['sha256'] and p.stat().st_size==pin['bytes'];assert not (ROOT/name).exists()
for name,pin in packet['existing_live_dependencies_not_promotion'].items():assert digest(ROOT/name)==pin['sha256']
for name in packet['promotion_allowlist']:
 p=ROOT/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((base/name).read_bytes())
(DEST/'promotion.json').write_bytes(encode({'section':298,'handoff_sha256':digest(h),'source_root':str(base.relative_to(ROOT)),'promoted':packet['promotion_allowlist'],'root_integration_pending':True,'author_API_tests_are_subset_not_feature_acceptance':True}))
print(json.dumps({'scope_defined_before_promotion':True,'promoted':len(packet['promotion_allowlist']),'parent':PARENT}))
