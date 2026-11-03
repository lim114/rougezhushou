from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone
import subprocess,json,sys
ROOT=Path(__file__).resolve().parents[1]
def enc(v):return(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode('utf8')
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()=='cc0b53683b37dae5273065986c989e5f783105d2'
base=ROOT/'.cache/p3-313-dlc2-research/prepared'
for source in base.rglob('*'):
 if source.is_file():
  dest=ROOT/source.relative_to(base);assert not dest.exists(),str(dest);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(source.read_bytes())
sys.path.insert(0,str(ROOT));from scripts.build_expansion_reference_313 import build
raw=build(ROOT);p=ROOT/'research/p3-expansion-313/runtime-manifest.json';p.write_bytes(raw)
p=ROOT/'rouge/expansion_reference.py';s=p.read_text('utf8');assert s.count('PREPARATION_NOT_YET_PINNED')==1;p.write_bytes(s.replace('PREPARATION_NOT_YET_PINNED',sha256(raw).hexdigest()).encode('utf8'))
p=ROOT/'rouge/app.py';s=p.read_text('utf8');anchor="        tabs.addTab(self.node_catalog,'节点事件')";assert s.count(anchor)==1
s=s.replace(anchor,anchor+"\n        from .expansion_view import ExpansionUpdatePanel\n        self.expansion_update=ExpansionUpdatePanel()\n        tabs.addTab(self.expansion_update,'版本与更新')")
p.write_bytes(s.encode('utf8'))
p=ROOT/'rouge/battle_view.py';s=p.read_text('utf8');anchor='class BattlePreviewPanel(QWidget):';assert s.count(anchor)==1
# Put the version boundary before the existing selectors; do not alter their numerical behavior.
start=s.index(anchor);at=s.index('layout=QVBoxLayout(self)',start);end=at+len('layout=QVBoxLayout(self)')
s=s[:end]+"\n        from .expansion_reference import LEGACY_NOTICE\n        self.version_notice=QLabel(LEGACY_NOTICE);self.version_notice.setWordWrap(True);layout.addWidget(self.version_notice)"+s[end:];p.write_bytes(s.encode('utf8'))
out=ROOT/'verification/sections/313-preparation';out.mkdir()
scope={'section':313,'human_steering':'黒流树海dlc2已经更新，注意同步最新情况','official_name_difference':'Verified official wording is 内容拓展·一; DLC2 official name not established. Supporting sources distinguished, TapTap AI repost not an official original.','remaining_todo':'P3当前国服资料同步、事件后续与具名物品提示、更新关卡固定原图','new_capability':'独立版本目录提供当前完整资料与全部新增/改动筛选，选项明确后续场景可跳转，80变更关卡的精确固定原图可读，旧计算显示版本边界','acceptance':['旧计算与历史来源保留；更新未全量迁移必须明确提示','全量新旧主题选片与原文件匹配；所有类别的增删改和同名条目不混并','只依据明确nextSceneId跳转，不拼接前置场景，不把item提示当领取','固定原图80引用、41不同blob严格校验，不添加未核对的位置标记','同资料刷新保留搜索、筛选和阅读，坏源清旧、恢复手动重选','必要验证与真实Windows窗口、要求索引同提交普通推送核对'],'at_utc':datetime.now(timezone.utc).isoformat(),'game_chat_private_used':False}
(out/'scope.json').write_bytes(enc(scope))
(out/'usage-threshold.json').write_bytes(enc({'section':313,'source':'actual usage tool at start of this goal continuation','used_percent':20,'remaining_percent':80,'window_duration_minutes':10080,'strict_below15_triggered':False,'secondary_unavailable_not_inferred':True,'account_identifiers_saved':False}))
p=ROOT/'DEVELOPMENT_CHECKPOINT.json';cp=json.loads(p.read_bytes());assert cp['completed_sections']==312 and cp['next_section']==313
cp['batch_status']='P3_SECTION313_IN_PROGRESS';cp['batch_start_section']=313;cp['current_batch'].update(start=313,status=cp['batch_status'],batch_closed=False,next_section_started=True)
cp['active_section']={**scope,'completed':False};cp['next_action']='第313节进行中，优先接入10月16日内容拓展一的版本隔离目录与明确后续资料；未验收发布前已交付仍312。'
p.write_bytes(enc(cp))
p=ROOT/'WORK_IN_PROGRESS.md';raw=p.read_bytes();prefix='## 当前进行第313节（尚未验收发布）\n\n已收到更新提醒，按核实的国服“内容拓展·一”处理。同步新旧资料与固定地图，明确旧计算尚未完整迁移，不把条目存在当本局可用或已获得。范围与验收见verification/sections/313-preparation/scope.json。\n\n以下为已交付历史。\n\n';p.write_bytes(prefix.replace('\n','\r\n').encode('utf8')+raw)
(out/'execution-start.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'section_started':313,'still_completed':312,'manifest_sha256':sha256(raw).hexdigest(),'new_runtime_manifest':sha256((ROOT/'research/p3-expansion-313/runtime-manifest.json').read_bytes()).hexdigest()},ensure_ascii=False))
