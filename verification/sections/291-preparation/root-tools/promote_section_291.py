from pathlib import Path
from hashlib import sha256
from datetime import datetime,timezone,timedelta
import json,subprocess
ROOT=Path(__file__).resolve().parents[1]
def sha(raw):return sha256(raw).hexdigest()
def load(p):return json.loads((ROOT/p).read_bytes())
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()=='2f264428bdc8dffaa16fdcc842649b441e94ba5a'
assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT).decode().strip()=='codex/p2-development'
assert not subprocess.check_output(['git','status','--porcelain'],cwd=ROOT)
manifest_path=ROOT/'.cache/p3-291-promotion-readiness/PROMOTION_FILES.json'
assert sha(manifest_path.read_bytes())=='84731fd97eb9b77b8b1529a9879dc494ff6620ed94b3696da16df6a7ac95f337'
plan=json.loads(manifest_path.read_bytes());assert len(plan['files'])==32
files={};before={}
for row in plan['files']:
    name=row['destination'];path=ROOT/name;src=ROOT/row['candidate_source']
    assert not name.startswith(('.cache/','.local/')) and name!='local-settings.json'
    assert path.resolve().is_relative_to(ROOT) and src.is_file() and not src.is_symlink()
    raw=src.read_bytes();assert sha(raw)==row['candidate']['sha256'] and len(raw)==row['candidate']['bytes']
    assert path.exists()==row['live_exists_before_promotion']
    if path.exists():
        old=path.read_bytes();assert sha(old)==row['live_before']['sha256'] and len(old)==row['live_before']['bytes']
        before[name]=old
    files[name]=raw
prep=ROOT/'verification/sections/291-preparation'
prep.mkdir(parents=True,exist_ok=True)
for name,raw in before.items():
    path=prep/'before-291'/name;path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as f:f.write(raw)
for name,raw in files.items():
    path=ROOT/name;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(raw)
    assert path.read_bytes()==raw
cp=load('DEVELOPMENT_CHECKPOINT.json')
assert cp['completed_sections']==290 and cp['next_section']==291
cp['active_section']={'section':291,'status':'in_progress','remaining_item':'P3和平守卫者节点条件、地图对应与固定作战入口',
 'new_capability':'单向移动例外说明；独立已读据点位置入口与枯枝/败叶固定资料；保留事件阅读并在显式查看时切换',
 'acceptance':'来源精确核对/不反推实际目标或完成；旧资格费用不变；当前历史位置与过期守卫；刷新阅读保留；必要检查和真实Windows三尺寸、两关入口；普通发布并更新要求索引',
 'promotion_manifest':'.cache/p3-291-promotion-readiness/PROMOTION_FILES.json','phase':'candidate_promoted_required_checks_pending'}
cp['current_batch']['next_section_started']=True
cp['confirmed_next_stage_direction']['next_functional_section_started']=True
(ROOT/'DEVELOPMENT_CHECKPOINT.json').write_bytes((json.dumps(cp,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
p=ROOT/'WORK_IN_PROGRESS.md';text=p.read_text(encoding='utf8')
intro=('## 第291节进行中 · 和平守卫者资料与地图、作战入口\n\n'
 '对应P3节点事件条件/地图对应/固定作战资料待办。本节新增单向移动例外的玩家说明、独立已读或记忆据点位置参考、两关固定资料入口，保留原事件阅读；没有实际目标、完成、移动或结算证据不赋值。'
 '验收：来源失效回退和旧资格/费用保持；当前/历史和过期位置校验；地图刷新/技术开关保留阅读，显式查看才切换；必要检查与真实Windows三尺寸、两关预览。'
 '已从32项核过前置SHA的缓存提升正式源，尚未通过实际测试，未完成、未发布。\n\n')
p.write_bytes((intro+text).encode('utf8'))
record={'section':291,'status':'promoted_not_verified_or_complete','at_Beijing':datetime.now(timezone(timedelta(hours=8))).isoformat(),
 'prior_commit':'2f264428bdc8dffaa16fdcc842649b441e94ba5a','promotion_manifest_sha256':sha(manifest_path.read_bytes()),
 'source_sha256':{name:sha(raw) for name,raw in files.items()},'preexisting_files_archived':{name:sha(raw) for name,raw in before.items()},
 'actual_tests_or_GUI_executed_by_promotion':False,'private_state_read_or_written':False,'completed_sections':290}
with (prep/'promotion.json').open('xb') as f:f.write((json.dumps(record,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
print(json.dumps({'promoted_files':len(files),'preexisting_saved':len(before),'section':291,'completed':False,'tests_pending':True}))
