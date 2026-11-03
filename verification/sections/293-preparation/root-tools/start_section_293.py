from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json,subprocess
root=Path(__file__).resolve().parents[1]
assert subprocess.check_output(['git','branch','--show-current'],cwd=root,text=True).strip()=='codex/p2-development'
assert not subprocess.check_output(['git','status','--porcelain'],cwd=root)
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
assert head=='78b43ec3c4f69f410f7f290eb1048b755ad57b0e'
remote=subprocess.check_output(['git','ls-remote','origin','refs/heads/codex/p2-development'],cwd=root,text=True).split()[0]
assert remote==head
cp_path=root/'DEVELOPMENT_CHECKPOINT.json';cp=json.loads(cp_path.read_bytes())
assert cp['completed_sections']==292 and cp['next_section']==293 and 'active_section' not in cp
dest=root/'verification/sections/293-preparation';dest.mkdir(exist_ok=False)
sources={'before-node_catalog_view.py':root/'rouge/node_catalog_view.py',
 'DESIGN.md':root/'.cache/p3-resting-result-card-design/DESIGN.md',
 'source-readback.json':root/'.cache/p3-resting-result-card-design/source-readback.json',
 'independent-design-review.json':root/'.cache/p3-293-independent-design-review/review.json'}
files={}
for name,path in sources.items():
    raw=path.read_bytes();(dest/name).write_bytes(raw)
    files[name]={'sha256':sha256(raw).hexdigest(),'bytes':len(raw)}
row={'section':293,'status':'scope_defined_before_functional_changes','at_utc':datetime.now(timezone.utc).isoformat(),
 'parent':head,'actual_remote_parent':remote,'files':files,
 'remaining_item':'P3 node events and future reward information',
 'new_capability':'A source-bound one-hop results reader for four resting-corner choices, with manual exact scene text navigation.',
 'acceptance':['Four exact choices and nine source branches; six destination buttons; count conflicts preserved.',
 'Future quantities never current grants; 99 gold unresolved original entry retained.',
 'Fresh source validation, deep copies, non-target isolation and no eligibility/data/state mutation.',
 'Manual isolated UI, source invalidation, refresh reading retention and no game/chat operations.'],
 'full_validation_due':305,'functional_complete':False}
(dest/'scope.json').write_bytes((json.dumps(row,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
cp['active_section']={'section':293,'status':'source_bound_results_reader_in_preparation',
 'remaining_item':row['remaining_item'],'new_capability':row['new_capability'],'acceptance':row['acceptance'],
 'preparation_receipt':'verification/sections/293-preparation/scope.json'}
cp_path.write_bytes((json.dumps(cp,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
wip=root/'WORK_IN_PROGRESS.md';raw=wip.read_bytes()
header=('## 第293节进行中 · 安眠一隅后续资料集中阅读\n\n'
 '集中列出四条具体随机选择的一跳来源后续及未来按钮数量，手动打开精确场景原文；保留两处数量冲突与99锭原入口错配。'
 '不重复计算已有全文或九条子边，不改资格、目录、本局、完整池或实际领取；10附注/25与57原入口缺口保留。'
 '功能与必要/真实窗口待验证，未销项、未发布；下一定期全量305。\n\n')
wip.write_bytes(header.encode('utf8')+raw)
print(json.dumps({'section':293,'scope_started':True,'parent_remote_equal':True,'complete':False}))
